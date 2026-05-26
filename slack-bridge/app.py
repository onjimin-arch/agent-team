"""Slack Bolt Socket Mode 봇 — DM/스레드 대화, 슬러그 확인, 승인 UI, 완료 알림.

흐름 요약:
- '신규 주제 <설명>' → 슬러그 제안 → 확인 버튼 → 팀장 프로토콜 실행
- 스레드(또는 DM)에 기존 태스크가 있으면: 실행 중인 경우 중단(cancel_event)
  후 같은 슬러그로 follow-up 재시작, 이미 끝난 경우 바로 follow-up 시작.
- '슬러그 수정' 버튼: 다음 메시지를 슬러그 재지정으로 해석.

실행 전 `.env` 설정 필요 (README 참조).
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

import yaml
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agent_runner import run_team_lead
from slug import slugify
from state import (
    find_task_by_thread,
    get_cancel_event,
    get_slug_wait,
    get_task_thread,
    pop_pending,
    pop_slug_wait,
    put_pending,
    put_slug_wait,
    put_task,
    register_cancel,
    unregister_task,
    update_task,
)

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("slack-bridge")

_allowed_raw = (
    os.environ.get("SLACK_ALLOWED_USER_IDS", "")
    + ","
    + os.environ.get("SLACK_ALLOWED_USER_ID", "")
)
ALLOWED_USERS = {u.strip() for u in _allowed_raw.split(",") if u.strip()}

def _load_new_topic_trigger() -> str:
    config_path = Path(__file__).parent.parent / ".claude" / "configs" / "team-config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("execution", {}).get("workspace", {}).get("new_topic_trigger", "새 작업")
    except Exception:
        return "새 작업"

NEW_TOPIC_TRIGGER = _load_new_topic_trigger()
_MENTION_RE = re.compile(r"<@[UW][A-Z0-9]+(\|[^>]+)?>")
_SLUG_LINE_RE = re.compile(r"^\s*슬러그\s*[:：]\s*([a-z0-9][a-z0-9\-]*)\s*$", re.IGNORECASE)
_BARE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,64}$")
_CANCEL_WAIT_TIMEOUT = 45.0  # 중단 신호 후 스레드 join 대기 최대 초

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def _is_allowed(user_id: str) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


def _strip_mentions(text: str) -> str:
    return _MENTION_RE.sub("", text).strip()


def _post(client, channel: str, thread_ts: str | None, **kwargs):
    if thread_ts:
        kwargs.setdefault("thread_ts", thread_ts)
    return client.chat_postMessage(channel=channel, **kwargs)


# ---------- 메시지 진입점 ----------

@app.event("message")
def on_message(event, say, client):
    """DM 메시지 — 슬러그 대기 소비 → 스레드 follow-up → '신규 주제' 트리거 순으로 판별."""
    log.info("on_message 수신: channel_type=%s subtype=%s bot_id=%s text=%r",
             event.get("channel_type"), event.get("subtype"), event.get("bot_id"),
             (event.get("text") or "")[:80])
    if event.get("channel_type") != "im" or event.get("subtype") or event.get("bot_id"):
        log.info("on_message 필터 통과 실패 — 무시")
        return
    user = event.get("user", "")
    if not _is_allowed(user):
        return

    text = (event.get("text") or "").strip()
    channel = event["channel"]
    # DM 도 봇 답장은 스레드화해서 맥락을 붙잡는다 (사용자 원 메시지 ts = 스레드 root)
    thread_ts = event.get("thread_ts") or event.get("ts")

    if _consume_slug_wait(user, text, channel, client):
        return

    if _route_thread_followup(event, client, text, channel, thread_ts, user):
        return

    _handle_trigger(event, say, text, channel, thread_ts, user, client)


@app.event("app_mention")
def on_app_mention(event, say, client):
    """채널 스레드 멘션 — 스레드에 기존 태스크 있으면 follow-up, 없으면 트리거."""
    if event.get("subtype") or event.get("bot_id"):
        return
    user = event.get("user", "")
    if not _is_allowed(user):
        return

    text = _strip_mentions(event.get("text") or "")
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event.get("ts")

    if _route_thread_followup(event, client, text, channel, thread_ts, user):
        return

    _handle_trigger(event, say, text, channel, thread_ts, user, client)


# ---------- 라우팅 헬퍼 ----------

def _route_thread_followup(event, client, text: str, channel: str, thread_ts: str, user: str) -> bool:
    """스레드에 기존 태스크가 있으면 follow-up 으로 처리. 처리했으면 True 반환.

    '신규 주제' 키워드가 있으면 기존 태스크와 무관하게 새 워크스페이스로 분기
    (기존 실행 중이면 먼저 중단 → 새 주제 시작).
    """
    existing = find_task_by_thread(channel, thread_ts)
    if not existing:
        return False

    if NEW_TOPIC_TRIGGER in text:
        # 새 주제 — 기존 실행 중이면 중단만 먼저, 이후 기존 트리거 플로우로 넘김
        if existing.get("status") == "running":
            if not _cancel_and_wait(existing["task_id"], client, channel, thread_ts, reason="새 주제 수신"):
                return True  # 중단 실패 — 새 주제 생성 보류
        return False  # 상위에서 _handle_trigger 계속 진행

    if not text.strip():
        _post(client, channel, thread_ts, text="후속 지시 내용을 함께 입력해 주세요.")
        return True

    status = existing.get("status")
    slug = existing.get("slug")
    if not slug:
        return False  # 이상 상태 — 트리거로 폴백

    if status == "running":
        _post(client, channel, thread_ts,
              text=f"🔁 후속 지시 접수 — 현재 실행을 중단하고 `{slug}` 에서 이어 처리합니다.")
        if not _cancel_and_wait(existing["task_id"], client, channel, thread_ts, reason="후속 지시"):
            return True  # 중단 실패 — follow-up 시작하지 않음
    else:
        _post(client, channel, thread_ts,
              text=f"🔁 후속 지시 접수 — `{slug}` 이어서 처리합니다.")

    _start_followup_task(slug, text, channel, thread_ts, user, client)
    return True


def _cancel_and_wait(task_id: str, client, channel: str, thread_ts: str | None, *, reason: str) -> bool:
    """실행 중인 태스크에 cancel 신호 후 스레드 종료 대기. True 면 정상 종료."""
    evt = get_cancel_event(task_id)
    thr = get_task_thread(task_id)
    if not evt or not thr:
        # 인메모리 레코드가 없음 — 봇 재시작 등으로 이미 유효하지 않음
        update_task(task_id, status="stale")
        return True
    evt.set()
    _post(client, channel, thread_ts, text=f"⏹️ 중단 중… ({reason})")
    thr.join(timeout=_CANCEL_WAIT_TIMEOUT)
    alive = thr.is_alive()
    if alive:
        _post(client, channel, thread_ts,
              text=f"⚠️ {int(_CANCEL_WAIT_TIMEOUT)}초 내 중단 확인 실패. 파일 경쟁을 피하기 위해 후속 지시를 보류합니다 — 잠시 뒤 다시 시도해 주세요.")
    else:
        unregister_task(task_id)
    return not alive


# ---------- '신규 주제' 트리거 ----------

def _handle_trigger(event, say, text: str, channel: str, thread_ts: str | None, user: str, client) -> None:
    say_kwargs = {"thread_ts": thread_ts} if thread_ts else {}

    if NEW_TOPIC_TRIGGER in text:
        task_desc = text.replace(NEW_TOPIC_TRIGGER, "", 1).strip(" -:·")
    else:
        task_desc = text

    if not task_desc:
        say("업무 내용을 입력해 주세요. 예) `바로고 배달 시장 분석해줘`", **say_kwargs)
        return

    slug = slugify(task_desc)
    say(
        text=f"✅ 시작: `{slug}`\n> {task_desc}\n저장 경로: `output/{slug}/`",
        **say_kwargs,
    )
    _start_new_task(slug, task_desc, channel, thread_ts, user, client)


def _slug_confirm_blocks(approval_id: str, slug: str, task: str) -> list[dict]:
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*업무 접수*\n> {task}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"제안 슬러그: `{slug}`\n저장 경로: `output/{slug}/`"}},
        {
            "type": "actions",
            "block_id": f"slug_confirm:{approval_id}",
            "elements": [
                {"type": "button", "style": "primary", "text": {"type": "plain_text", "text": "이 슬러그로 시작"}, "action_id": "slug_ok", "value": approval_id},
                {"type": "button", "text": {"type": "plain_text", "text": "슬러그 수정"}, "action_id": "slug_edit", "value": approval_id},
                {"type": "button", "style": "danger", "text": {"type": "plain_text", "text": "취소"}, "action_id": "slug_cancel", "value": approval_id},
            ],
        },
    ]


# ---------- 슬러그 확인/수정/취소 버튼 ----------

@app.action("slug_ok")
def on_slug_ok(ack, body, client):
    ack()
    approval_id = body["actions"][0]["value"]
    pending = pop_pending(approval_id)
    if not pending:
        return
    slug, task, channel, user = pending["slug"], pending["task"], pending["channel"], pending["user"]
    thread_ts = pending.get("thread_ts")
    _start_new_task(slug, task, channel, thread_ts, user, client,
                    update_message=(body["message"]["ts"], f"✅ 시작: `{slug}`\n> {task}"))


@app.action("slug_edit")
def on_slug_edit(ack, body, client):
    """슬러그 수정 대기 상태 진입 — 사용자의 다음 메시지를 슬러그 재지정으로 해석."""
    ack()
    approval_id = body["actions"][0]["value"]
    pending = pop_pending(approval_id)
    if not pending:
        return
    user = pending["user"]
    put_slug_wait(user, {
        "task": pending["task"],
        "channel": pending["channel"],
        "thread_ts": pending.get("thread_ts"),
        "previous_slug": pending["slug"],
    })
    kwargs = {
        "channel": pending["channel"],
        "text": (
            f"원하는 슬러그를 회신해 주세요. 형태: `슬러그: <kebab-case>` 또는 슬러그만 단독 입력.\n"
            f"(원래 업무: {pending['task']} · 이전 제안: `{pending['slug']}`)"
        ),
    }
    if pending.get("thread_ts"):
        kwargs["thread_ts"] = pending["thread_ts"]
    client.chat_postMessage(**kwargs)


@app.action("slug_cancel")
def on_slug_cancel(ack, body, client):
    ack()
    pop_pending(body["actions"][0]["value"])
    client.chat_update(channel=body["channel"]["id"], ts=body["message"]["ts"], text="❌ 취소됨", blocks=[])


def _consume_slug_wait(user: str, text: str, channel: str, client) -> bool:
    """사용자가 슬러그 수정 대기 중이면 이 메시지를 슬러그 입력으로 소비."""
    waiting = get_slug_wait(user)
    if not waiting:
        return False

    # '신규 주제' 가 먼저 오면 대기 해제하고 기존 경로로 처리하도록 양보
    if NEW_TOPIC_TRIGGER in text:
        pop_slug_wait(user)
        return False

    m = _SLUG_LINE_RE.match(text)
    candidate = m.group(1) if m else (text.strip() if _BARE_SLUG_RE.match(text.strip()) else None)
    if not candidate:
        _post(client, channel, waiting.get("thread_ts"),
              text="슬러그 형식이 맞지 않습니다. 예: `슬러그: 2026-ev-market` 또는 `2026-ev-market`")
        return True

    pop_slug_wait(user)
    approval_id = uuid.uuid4().hex[:10]
    put_pending(approval_id, {
        "kind": "slug_confirm",
        "slug": candidate,
        "task": waiting["task"],
        "user": user,
        "channel": waiting["channel"],
        "thread_ts": waiting.get("thread_ts"),
    })
    _post(
        client, waiting["channel"], waiting.get("thread_ts"),
        blocks=_slug_confirm_blocks(approval_id, candidate, waiting["task"]),
        text=f"워크스페이스 슬러그: {candidate}",
    )
    return True


# ---------- 멤버 산출물 승인 (현재는 UI 전용 — 러너 Event 연결은 별도 단계) ----------

@app.action("approve_yes")
@app.action("approve_no")
def on_approval(ack, body, client):
    ack()
    approval_id = body["actions"][0]["value"]
    decision = "approved" if body["actions"][0]["action_id"] == "approve_yes" else "rejected"
    pending = pop_pending(approval_id)
    if not pending:
        return
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"{'✅ 승인' if decision == 'approved' else '❌ 반려'}: {pending.get('label', '')}",
        blocks=[],
    )


# ---------- 태스크 시작 ----------

def _start_new_task(slug: str, task: str, channel: str, thread_ts: str | None, user: str, client,
                    *, update_message: tuple[str, str] | None = None) -> None:
    """신규 워크스페이스 태스크 시작."""
    if update_message:
        ts, text = update_message
        client.chat_update(channel=channel, ts=ts, text=text,
                           blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}])
    task_id = uuid.uuid4().hex[:12]
    put_task(task_id, {
        "slug": slug, "task": task, "user": user, "channel": channel,
        "thread_ts": thread_ts, "status": "running", "follow_up": False,
    })
    _spawn_runner(task_id, slug, task, channel, thread_ts, client, follow_up=False)


def _start_followup_task(slug: str, instruction: str, channel: str, thread_ts: str, user: str, client) -> None:
    """같은 슬러그에 대한 후속 지시 태스크 시작."""
    task_id = uuid.uuid4().hex[:12]
    put_task(task_id, {
        "slug": slug, "task": instruction, "user": user, "channel": channel,
        "thread_ts": thread_ts, "status": "running", "follow_up": True,
    })
    _spawn_runner(task_id, slug, instruction, channel, thread_ts, client, follow_up=True)


def _spawn_runner(task_id: str, slug: str, task: str, channel: str, thread_ts: str | None,
                  client, *, follow_up: bool) -> None:
    cancel_event = threading.Event()
    t = threading.Thread(
        target=_run_task,
        args=(task_id, slug, task, channel, thread_ts, client, cancel_event, follow_up),
        daemon=True,
    )
    register_cancel(task_id, cancel_event, t)
    t.start()


_DEFAULT_WEBHOOK_FILE = Path(r"C:\Users\이지민\.claude-secrets\slack-webhook.txt")
# `**작성일**: 2026-04-30` (개별 줄) 또는
# `> **작성일**: 2026-04-24 | **Task Type**: ...` (한 줄 인라인) 둘 다 매칭.
# 줄 prefix 의 `> ` blockquote 와 ` | ` 구분자를 허용, 라벨 이후 다음 `|` 또는 줄끝까지 캡처.
_META_RE = lambda label: re.compile(
    rf"\*\*{re.escape(label)}\*\*\s*[:：]?\s*([^|\n\r]+?)\s*(?=\||$)", re.MULTILINE
)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# 핵심 인사이트(우선) > 핵심 요약 > 요약 순서로 매칭. 우선순위가 높은 헤더가 있으면 그걸 사용.
_INSIGHT_HEADER_PATTERNS = (
    re.compile(r"^##\s+(?:\d+\.\s+)?핵심\s*인사이트\s*$", re.MULTILINE),
    re.compile(r"^##\s+(?:\d+\.\s+)?핵심\s*요약\s*$", re.MULTILINE),
    re.compile(r"^##\s+(?:\d+\.\s+)?요약\s*$", re.MULTILINE),
)
_NEXT_H2_RE = re.compile(r"^##\s+", re.MULTILINE)
# bullet (`- `, `* `), 번호 (`1. `), 또는 H3 헤딩(`### 인사이트 1: ...`) 형태 모두 인사이트 한 항목.
# H3 의 경우 `인사이트 N:` 또는 `N.` 같은 prefix 를 떼고 헤딩 본문만 캡처.
# VERBOSE 모드를 쓰지 않는다 — 패턴 안에 `#` 가 들어가는데 VERBOSE 에서는 `#` 가 주석 시작이라
# H3 분기가 통째로 주석 처리되어 어떤 줄이든 매치하는 버그가 발생.
_INSIGHT_ITEM_RE = re.compile(
    r"^\s*(?:###\s+(?:인사이트\s*\d+\s*[:：]\s*|\d+[\.\)]\s*)?(?P<h3>.+?)"
    r"|(?:[-*]|\d+\.)\s+(?:\*\*(?P<bold>[^*\n]+)\*\*|(?P<plain>.+?)))\s*$",
    re.MULTILINE,
)


def _grab_meta(text: str, label: str) -> str:
    m = _META_RE(label).search(text)
    return m.group(1).strip() if m else ""


def _extract_insights(final_text: str, max_items: int = 5) -> list[str]:
    """final-artifact.md 의 '핵심 인사이트'/'요약' 섹션에서 bullet 항목을 추출.

    우선순위: 핵심 인사이트 > 핵심 요약 > 요약. 핵심 인사이트가 본 보고서의 결론이므로
    Slack 알림에는 그게 가장 적합하다.
    """
    m = None
    for pattern in _INSIGHT_HEADER_PATTERNS:
        m = pattern.search(final_text)
        if m:
            break
    if not m:
        return []
    rest = final_text[m.end():]
    end = _NEXT_H2_RE.search(rest)
    section = rest[: end.start()] if end else rest

    items: list[str] = []
    for line_m in _INSIGHT_ITEM_RE.finditer(section):
        text = (
            line_m.group("h3")
            or line_m.group("bold")
            or line_m.group("plain")
            or ""
        ).strip().rstrip(":：").strip()
        if not text or text.startswith("```"):
            continue
        # 너무 긴 본문은 첫 문장만 잘라 사용
        if len(text) > 140:
            cut = re.split(r"(?<=[\.。!?])\s", text, maxsplit=1)[0]
            text = cut[:140].rstrip() + "…" if len(cut) > 140 else cut
        items.append(text)
        if len(items) >= max_items:
            break
    return items


def _extract_fact_check_summary(gamma_path: Path) -> str | None:
    if not gamma_path.exists():
        return None
    try:
        text = gamma_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"##\s*검증\s*요약\s*\n", text)
    if not m:
        return None
    rest = text[m.end():]
    end = _NEXT_H2_RE.search(rest)
    section = rest[: end.start()] if end else rest

    counts: dict[str, int] = {}
    # gamma 산출물은 두 포맷이 혼용된다:
    #   (1) bullet: `- **확인됨**: 11개`
    #   (2) table : `| 확인됨 | 6 |`
    # 둘 다 매칭하기 위해 라벨 좌우의 마크다운 장식(`**`, `|`, ws) 을 허용.
    for label in ["총 검증 항목", "확인됨", "부분 일치", "출처 불명", "불일치", "최신 정보로 갱신 필요"]:
        cm = re.search(
            rf"(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*[\|:：]\s*[^\d|]*?(\d+)",
            section,
        )
        if cm:
            counts[label] = int(cm.group(1))
    if not counts:
        return None

    parts: list[str] = []
    if "총 검증 항목" in counts:
        parts.append(f"검증 {counts['총 검증 항목']}건")
    for label in ["확인됨", "부분 일치", "출처 불명", "불일치", "최신 정보로 갱신 필요"]:
        if label in counts:
            short = "갱신 필요" if label == "최신 정보로 갱신 필요" else label
            parts.append(f"{short} {counts[label]}건")
    return " · ".join(parts)


def _synthesize_block_kit_payload(team_root: Path, slug: str) -> dict | None:
    """slack-notification.json 이 없을 때 워크스페이스 산출물로 Block Kit 합성."""
    ws = team_root / "output" / slug
    final_path = ws / "final" / "final-artifact.md"
    if not final_path.exists():
        return None
    try:
        final_text = final_path.read_text(encoding="utf-8")
    except OSError:
        return None

    h1 = _H1_RE.search(final_text)
    topic = h1.group(1).strip() if h1 else slug
    topic_short = re.sub(r"\s*보고서\s*$", "", topic).strip()

    written = _grab_meta(final_text, "작성일") or time.strftime("%Y-%m-%d")
    task_type = _grab_meta(final_text, "Task Type") or "research-report"
    active = _grab_meta(final_text, "활성 멤버") or "alpha · beta"
    active = re.sub(r"member-", "", active).strip()
    cycle = _grab_meta(final_text, "사이클") or "1 / 3"
    approval = _grab_meta(final_text, "승인") or "human_approval=false (자동 완료)"

    insights = _extract_insights(final_text, max_items=5)
    if not insights:
        insights = ["(요약 자동 추출 실패 — 보고서 본문 확인 필요)"]

    has_gamma = "gamma" in active
    fact_summary = (
        _extract_fact_check_summary(ws / "member-gamma" / "fact-check-log.md")
        if has_gamma else None
    )

    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "✅ 에이전트 팀 보고서 완료", "emoji": True}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*주제*\n{topic_short}"},
            {"type": "mrkdwn", "text": f"*작성일*\n{written}"},
            {"type": "mrkdwn", "text": f"*Task Type*\n{task_type}"},
            {"type": "mrkdwn", "text": f"*활성 멤버*\n{active}"},
            {"type": "mrkdwn", "text": f"*사이클*\n{cycle}"},
            {"type": "mrkdwn", "text": f"*승인*\n{approval}"},
        ]},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": "*핵심 결과*\n" + "\n".join(f"• {x}" for x in insights[:5])}},
    ]
    if fact_summary:
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": f"*팩트체크 결과*\n{fact_summary}"}})
    blocks.append({"type": "context", "elements": [
        {"type": "mrkdwn", "text": f"로컬 경로: `output/{slug}/final/final-artifact.md` · bridge 자동 합성"}
    ]})

    return {
        "text": f"✅ [에이전트 팀] {topic_short} 완료",
        "blocks": blocks,
    }


def _read_webhook_url() -> str | None:
    path = Path(os.environ.get("SLACK_WEBHOOK_FILE", str(_DEFAULT_WEBHOOK_FILE)))
    try:
        url = path.read_text(encoding="utf-8").strip()
        return url or None
    except OSError:
        return None


def _post_to_webhook(payload: dict) -> bool:
    url = _read_webhook_url()
    if not url:
        return False
    try:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        log.warning("webhook 전송 실패: %s", e)
        return False


def _load_block_kit_payload(slug: str) -> tuple[dict | None, bool]:
    """Block Kit payload 확보. Returns (payload, was_synthesized).

    1) `output/{slug}/slack-notification.json` 이 있으면 그걸 사용 (Phase 5 정상 경로).
    2) 없으면 워크스페이스 산출물에서 합성하고 디스크에 저장(다음 follow-up 재사용).
    `was_synthesized=True` 면 webhook 도 bridge 가 직접 쏴 줘야 한다(agent 가 Phase 5 를 못 했으므로).
    """
    team_root_str = os.environ.get("TEAM_ROOT")
    if not team_root_str:
        return None, False
    team_root = Path(team_root_str)
    path = team_root / "output" / slug / "slack-notification.json"

    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8")), False
        except (json.JSONDecodeError, OSError) as e:
            log.warning("slack-notification.json 읽기 실패 (%s): %s — 합성 fallback", slug, e)

    payload = _synthesize_block_kit_payload(team_root, slug)
    if not payload:
        return None, False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("slack-notification.json 자동 합성 저장: %s", path)
    except OSError as e:
        log.warning("자동 합성 JSON 저장 실패 (%s): %s", slug, e)
    return payload, True


def _run_task(task_id: str, slug: str, task: str, channel: str, thread_ts: str | None,
              client, cancel_event: threading.Event, follow_up: bool) -> None:
    def notify(msg: str):
        _post(client, channel, thread_ts, text=msg)

    def request_approval(label: str, preview: dict) -> str:
        approval_id = uuid.uuid4().hex[:10]
        put_pending(approval_id, {
            "kind": "artifact", "label": label, "task_id": task_id,
            "channel": channel, "thread_ts": thread_ts,
        })
        _post(client, channel, thread_ts, blocks=[
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*승인 요청*: {label}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"```{preview.get('summary', '')[:600]}```"}},
            {"type": "actions", "elements": [
                {"type": "button", "style": "primary", "text": {"type": "plain_text", "text": "승인"}, "action_id": "approve_yes", "value": approval_id},
                {"type": "button", "style": "danger", "text": {"type": "plain_text", "text": "반려"}, "action_id": "approve_no", "value": approval_id},
            ]},
        ], text=f"승인 요청: {label}")
        return approval_id

    try:
        result = run_team_lead(
            slug, task,
            notify=notify,
            request_approval=request_approval,
            cancel_event=cancel_event,
            follow_up=follow_up,
        )
        update_task(task_id, status=result.get("status", "completed"), result=result)
        _notify_completion(client, channel, thread_ts, notify, slug, result)
    except Exception as e:
        log.exception("task failed")
        update_task(task_id, status="failed", error=str(e))
        notify(f"❌ 실패: {e}")
    finally:
        unregister_task(task_id)


def _notify_completion(client, channel: str, thread_ts: str | None, notify, slug: str, result: dict):
    """완료 알림. `completed` 상태에서는 Phase 5 의 Block Kit payload 를 읽어
    지시받은 스레드에 그대로 재포스팅한다. 없으면 텍스트로 fallback."""
    status = result.get("status", "unknown")
    cost = result.get("cost_usd", 0.0)
    turns = result.get("turns", 0)
    artifacts = result.get("artifacts") or []
    final = result.get("final_path")
    follow_up = result.get("follow_up", False)

    if status == "completed" and final:
        payload, synthesized = _load_block_kit_payload(slug)
        if payload and payload.get("blocks"):
            try:
                kwargs = {
                    "channel": channel,
                    "blocks": payload["blocks"],
                    "text": payload.get("text") or f"에이전트 팀 보고서 완료: {slug}",
                }
                if thread_ts:
                    kwargs["thread_ts"] = thread_ts
                client.chat_postMessage(**kwargs)
                if synthesized:
                    # Phase 5 가 안 돌아간 케이스 — webhook 채널도 bridge 가 직접 발송
                    if _post_to_webhook(payload):
                        notify("📣 webhook 채널에도 동일한 알림을 발송했습니다 (Phase 5 자동 보강).")
                    else:
                        notify("⚠️ webhook 채널 발송 실패 — 이 스레드 알림만 게시되었습니다.")
                if follow_up:
                    notify("🔁 후속 지시 반영 완료 — 위 블록의 수치·멤버 목록이 최신 상태입니다.")
                return
            except Exception as e:
                log.warning("Block Kit 재포스팅 실패, 텍스트로 fallback: %s", e)
        # payload 없음/실패 — 텍스트 fallback
        header = "🔁 후속 지시 반영 완료" if follow_up else "🎉 완료"
        lines = [f"{header}: `output/{slug}/final/final-artifact.md`"]
    elif status == "cancelled":
        lines = [f"⏹️ 중단됨: `{slug}` — 다음 지시를 기다립니다."]
    else:
        lines = [f"⚠️ 부분 완료 — 최종 산출물 미생성. `output/{slug}/` 내부 확인 필요."]

    if artifacts:
        lines.append(f"📎 생성/수정 파일 {len(artifacts)}개: " + ", ".join(f"`{a}`" for a in artifacts[:5]))
    if cost:
        lines.append(f"💰 비용 ${cost} · 턴 {turns}")
    notify("\n".join(lines))


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    log.info("slack-bridge starting (Socket Mode)")
    handler.start()
