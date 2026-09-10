"""Slack Bolt Socket Mode 봇 — DM/스레드 대화, 슬러그 확인, 승인 UI, 완료 알림.

흐름 요약:
- '신규 주제 <설명>' → 슬러그 제안 → 확인 버튼 → 팀장 프로토콜 실행
- 스레드(또는 DM)에 기존 태스크가 있으면: 실행 중인 경우 중단(cancel_event)
  후 같은 슬러그로 follow-up 재시작, 이미 끝난 경우 바로 follow-up 시작.
- '슬러그 수정' 버튼: 다음 메시지를 슬러그 재지정으로 해석.

실행 전 `.env` 설정 필요 (README 참조).
"""
from __future__ import annotations

import atexit
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import yaml
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agent_runner import run_team_lead
from slug import slugify
from state import (
    find_latest_task_for_channel,
    find_task_by_thread,
    get_cancel_event,
    get_slug_wait,
    get_task_thread,
    pop_pending,
    pop_slug_wait,
    put_approval_answer,
    put_pending,
    put_slug_wait,
    put_task,
    register_cancel,
    unregister_task,
    update_task,
)

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logging.getLogger("slack_bolt").setLevel(logging.WARNING)
logging.getLogger("slack_sdk").setLevel(logging.WARNING)
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


def _load_task_types() -> list[dict]:
    """team-config.yaml 의 task.types 를 그대로 읽는다 — 이 봇의 라벨링이 팀장의
    Phase 1-0 판별과 별개의 하드코딩된 키워드셋으로 드리프트하지 않도록, 여기서
    별도 목록을 유지하지 않고 항상 이 config 를 단일 소스로 삼는다."""
    config_path = Path(__file__).parent.parent / ".claude" / "configs" / "team-config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("task", {}).get("types", [])
    except Exception:
        return []

def _load_quick_query_triggers() -> list[str]:
    """team-config.yaml 의 task.quick_query.triggers — '새 작업' 없이도 이 메시지에 반응할지를
    싸게 1차 필터링하는 용도다. quick_query 인지 풀 리포트(task.types)인지의 최종 판단은 opencode
    안에서 팀장이 CLAUDE.md Phase 0 로 내린다 — 이 목록은 어디까지나 "무시하지 않고 실행은 한다"
    수준의 프리필터다."""
    config_path = Path(__file__).parent.parent / ".claude" / "configs" / "team-config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        qq = cfg.get("task", {}).get("quick_query", {})
        if not qq.get("enabled", False):
            return []
        return [str(t) for t in qq.get("triggers", [])]
    except Exception:
        return []


def _load_include_download_link() -> bool:
    """team-config.yaml 의 distribution.slack.include_download_link — 기본 False(다운로드 링크
    제외). Team Lead(LLM)가 slack-notification.json 에 이 규칙을 무시하고 다운로드 링크를 반복해서
    넣는 사례가 여러 워크스페이스에서 확인돼(예: output/이번-전사-경영-실적-손익,
    output/배달대행사-pg사-이슈 등), 텍스트 지시만으로는 신뢰할 수 없어 봇 쪽에서 최종 발송 직전에
    결정론적으로 한 번 더 걸러낸다(아래 _strip_download_link_blocks)."""
    config_path = Path(__file__).parent.parent / ".claude" / "configs" / "team-config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return bool(cfg.get("distribution", {}).get("slack", {}).get("include_download_link", False))
    except Exception:
        return False


NEW_TOPIC_TRIGGER = _load_new_topic_trigger()
TASK_TYPES = _load_task_types()
QUICK_QUERY_TRIGGERS = _load_quick_query_triggers()
INCLUDE_DOWNLOAD_LINK = _load_include_download_link()
_DOWNLOAD_LINK_LABEL_RE = re.compile(r"다운로드|download", re.IGNORECASE)
_MENTION_RE = re.compile(r"<@[UW][A-Z0-9]+(\|[^>]+)?>")
_BRACKET_TAG_RE = re.compile(r"\[([^\[\]]{1,30})\]")
_SLUG_LINE_RE = re.compile(r"^\s*슬러그\s*[:：]\s*([a-z0-9][a-z0-9\-]*)\s*$", re.IGNORECASE)
_BARE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,64}$")
_CANCEL_WAIT_TIMEOUT = 45.0  # 중단 신호 후 스레드 join 대기 최대 초
_FOLLOWUP_GUESS_WINDOW_SEC = 900  # 15분 — 이보다 오래된 마지막 작업은 후속 확인 대상에서 제외

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

    # 1. 슬러그 대기 소비 (슬러그 수정 대기 중이면 소비)
    if _consume_slug_wait(user, text, channel, client):
        return

    # 2. 스레드 follow-up (기존 태스크 계속)
    if _route_thread_followup(event, client, text, channel, thread_ts, user):
        return

    # 3. DM 폴백 — 스레드 매칭 실패 시, 최근 작업이 있으면 후속인지 새 작업인지 "묻는다"
    #    (추측하지 않는다). "마켓 인텔리전스 알려줘" 다음 "ERP 손익 분석해서 알려줘"처럼 짧은
    #    시간 안에 서로 무관한 요청을 연달아 보내는데, 뒤 문장에 "분석"처럼 task.types 트리거
    #    키워드가 우연히 겹치면 조용히 앞 작업의 후속으로 이어붙는 오작동이 실사용에서 반복
    #    확인됐다(quick-query는 이미 제외했지만 report-type 키워드 겹침까진 못 막았다). 이제는
    #    같은 채널에 "최근"(아래 윈도우 이내) 작업이 있을 때만 버튼으로 직접 확인한다 — 오래된
    #    작업이면 애초에 후보에서 제외하고 그냥 새 작업으로 시작한다(질문 피로 최소화).
    if NEW_TOPIC_TRIGGER not in text and text:
        is_cmd, matched_type = _is_command(text)
        if is_cmd and matched_type != "quick-query":
            latest = find_latest_task_for_channel(channel)
            if latest and latest.get("slug"):
                age_sec = time.time() - latest.get("created_at", 0)
                if age_sec <= _FOLLOWUP_GUESS_WINDOW_SEC:
                    approval_id = uuid.uuid4().hex[:10]
                    put_pending(approval_id, {
                        "kind": "followup_confirm",
                        "slug": latest["slug"], "task": text, "user": user,
                        "channel": channel, "thread_ts": thread_ts,
                    })
                    _post(client, channel, thread_ts,
                          blocks=_followup_confirm_blocks(approval_id, latest["slug"], text),
                          text=f"직전 작업(`{latest['slug']}`)에 이어서 처리할까요, 새 작업으로 시작할까요?")
                    return

    # 4. 새로운 명령어 처리
    _handle_trigger(text, channel, thread_ts, user, client)


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

    _handle_trigger(text, channel, thread_ts, user, client)


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

def _match_tag_to_type(tag: str, task_types: list[dict]) -> str | None:
    """대괄호 태그(`[dev]`, `[설계]` 등) 내용을 task.types 의 name 또는 triggers 와 대조한다.
    CLAUDE.md Phase 1-0 의 "태그가 명시된 경우 → 태그 우선 (score 무시)" 규칙과 동일한 우선순위를
    Slack 단계에서도 미리 반영 — 별도 별칭 표를 두지 않고 team-config.yaml 자체를 그대로 참조한다."""
    tag_norm = tag.strip().lower()
    if not tag_norm:
        return None
    for t in task_types:
        name = str(t.get("name", "")).lower()
        if tag_norm == name:
            return t["name"]
        for trig in t.get("triggers", []):
            trig_norm = str(trig).lower()
            if tag_norm == trig_norm or tag_norm in trig_norm or trig_norm in tag_norm:
                return t["name"]
    return None


def _score_task_types(text_lower: str, task_types: list[dict]) -> list[tuple[str, float]]:
    """CLAUDE.md Phase 1-0 과 동일한 공식: score = 매칭 keyword 수 / 해당 type 의 전체 trigger 수."""
    scores = []
    for t in task_types:
        triggers = t.get("triggers") or []
        if not triggers:
            continue
        matched = sum(1 for trig in triggers if str(trig).lower() in text_lower)
        if matched:
            scores.append((t["name"], matched / len(triggers)))
    return scores


def _is_command(text: str) -> tuple[bool, str]:
    """
    명령어인지 판별하고, 예상 task type 을 라벨링한다.

    **중요**: 여기서 반환하는 type 은 어디까지나 Slack 안내 메시지용 미리보기다.
    최종 판별은 opencode 서브프로세스 안에서 팀장이 CLAUDE.md Phase 1-0 로 다시 수행하며,
    거기서 실제로 참조하는 것도 이 함수와 동일한 team-config.yaml 의 task.types 다 — 그래서
    이 함수는 별도 키워드셋을 하드코딩하지 않고 항상 TASK_TYPES(같은 config)를 그대로 사용한다.
    이전 버전은 이 둘이 서로 다른 키워드셋을 써서 라벨과 실제 실행이 어긋날 수 있었다.

    반환: (명령어여부, task.types[].name 중 하나 또는 'auto')
    """
    if '[AUTO:' in text:
        return True, 'auto'

    task_types = TASK_TYPES

    # 대괄호 태그 우선 (예: "[dev] 로그인 버그 수정")
    tag_match = _BRACKET_TAG_RE.search(text)
    if tag_match:
        matched_type = _match_tag_to_type(tag_match.group(1), task_types)
        if matched_type:
            return True, matched_type

    text_lower = text.lower()
    scores = _score_task_types(text_lower, task_types)
    if not scores:
        # task.types 어느 것도 안 걸리면 quick_query 프리필터로 한 번 더 본다 — "ERP 이번달 손익
        # 얼마야?" 처럼 조회성 문장은 report_signal_triggers(분석/보고서/리서치 등)가 없어 원래
        # task.types 에 안 걸린다. 여기서 True 로 반환해도 실제로 quick_query 로 처리할지 풀
        # 파이프라인이 필요한지는 opencode 안 팀장이 CLAUDE.md Phase 0 에서 최종 판단한다.
        if any(trig.lower() in text_lower for trig in QUICK_QUERY_TRIGGERS):
            return True, 'quick-query'
        return False, ''

    best_score = max(s for _, s in scores)
    tied = [name for name, s in scores if s == best_score]
    if len(tied) > 1:
        # 동점 처리: team-config.yaml 나열 순서 기준 자동 선택
        # (CLAUDE.md AUTO 모드 인터럽트 규칙 ③과 동일 — Slack 트리거는 항상 AUTO 모드로 실행되므로)
        order = [t["name"] for t in task_types]
        tied.sort(key=lambda n: order.index(n) if n in order else len(order))
    return True, tied[0]

def _handle_trigger(text: str, channel: str, thread_ts: str | None, user: str, client) -> None:
    """새 작업(또는 명령어로 인식된 메시지)을 새 워크스페이스로 시작한다.

    `event`/`say`(Bolt 콜백) 를 받지 않는다 — 함수 내부는 `channel`/`thread_ts`/`client`만으로
    충분하고(`_post` 헬퍼로 대체), 이렇게 해야 on_message/on_app_mention 뿐 아니라 버튼 클릭
    핸들러(on_followup_new)에서도 동일하게 재사용할 수 있다."""
    has_trigger = NEW_TOPIC_TRIGGER in text
    if has_trigger:
        task_desc = text.replace(NEW_TOPIC_TRIGGER, "", 1).strip(" -:·")
    else:
        task_desc = text

    is_cmd, task_type = _is_command(task_desc)

    # 업무 키워드가 없는 일반 대화는 작업 시작하지 않음
    if not has_trigger and not is_cmd:
        _post(client, channel, thread_ts, text="안녕하세요! 업무 요청을 입력해 주세요.\n예) `2026년 배달 시장 분석해줘`")
        return

    if not task_desc:
        _post(client, channel, thread_ts, text="업무 내용을 입력해 주세요. 예) `바로고 배달 시장 분석해줘`")
        return

    slug = slugify(task_desc)
    
    # 타입별 아이콘 및 라벨
    # team-config.yaml 의 task.types 이름과 1:1 대응 (더 이상 별도 키워드셋을 쓰지 않으므로
    # _is_command 가 반환할 수 있는 값과 항상 일치한다).
    type_config = {
        'research-report': ('📊', '리서치·분석 보고서', 'alpha 조사 → gamma 팩트체크 → delta 시각화 → beta 보고서 작성'),
        'code-review': ('🔎', '코드 리뷰', 'alpha 코드 스캔 → gamma 논리·보안 검증 → beta 리뷰 요약'),
        'multilingual-brief': ('🌐', '다국어 브리프', 'alpha 조사 → beta 다국어 요약·번역 → delta 시각자료'),
        'dev': ('💻', '개발', 'eta 오픈소스 선행 리서치 → alpha 구현 방향 분석 → epsilon 코드 수정·검증·배포'),
        'design': ('🧩', '설계', 'alpha 사전 리서치 → zeta 설계서(design-spec.md) 작성'),
        'github-plan': ('🔍', '오픈소스 리서치·구현 계획', 'eta 레포 탐색·라이선스 감사 → alpha 방향 분석 → beta 계획 보고서'),
        'quick-query': ('🔍', '빠른 조회', 'Team Lead가 연동 데이터소스를 직접 조회해 즉시 답변 (풀 파이프라인 생략)'),
        'auto': ('🤖', '오토', '자동 모드 — Phase 1~5 중단 없이 실행'),
    }
    emoji, label, note = type_config.get(
        task_type, ('❓', task_type or '알 수 없음', '')
    )

    _post(
        client, channel, thread_ts,
        text=(
            f"{emoji} {label} 작업 시작: `{slug}`\n> {task_desc}\n\n"
            f"📋 **예상 처리 방식**: {note}\n"
            f"_(최종 유형은 팀장이 Phase 1-0에서 다시 판별합니다 — 위 라벨과 다를 수 있어요)_\n"
            f"저장 경로: `output/{slug}/`"
        ),
    )
    _start_new_task(slug, task_desc, channel, thread_ts, user, client)


def _followup_confirm_blocks(approval_id: str, slug: str, task: str) -> list[dict]:
    return [
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"직전 작업(`{slug}`)과 이어지는 내용인지 확실치 않습니다.\n> {task}"}},
        {
            "type": "actions",
            "block_id": f"followup_confirm:{approval_id}",
            "elements": [
                {"type": "button", "style": "primary", "text": {"type": "plain_text", "text": "이어서 처리"}, "action_id": "followup_continue", "value": approval_id},
                {"type": "button", "text": {"type": "plain_text", "text": "새 작업으로 시작"}, "action_id": "followup_new", "value": approval_id},
            ],
        },
    ]


@app.action("followup_continue")
def on_followup_continue(ack, body, client):
    ack()
    approval_id = body["actions"][0]["value"]
    pending = pop_pending(approval_id)
    if not pending:
        return
    slug, task, channel, user = pending["slug"], pending["task"], pending["channel"], pending["user"]
    thread_ts = pending.get("thread_ts")
    text = f"🔁 후속 지시로 처리: `{slug}`\n> {task}"
    client.chat_update(channel=body["channel"]["id"], ts=body["message"]["ts"], text=text,
                        blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}])
    _start_followup_task(slug, task, channel, thread_ts, user, client)


@app.action("followup_new")
def on_followup_new(ack, body, client):
    ack()
    approval_id = body["actions"][0]["value"]
    pending = pop_pending(approval_id)
    if not pending:
        return
    task, channel, user = pending["task"], pending["channel"], pending["user"]
    thread_ts = pending.get("thread_ts")
    client.chat_update(channel=body["channel"]["id"], ts=body["message"]["ts"], text="🆕 새 작업으로 시작합니다.",
                        blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": "🆕 새 작업으로 시작합니다."}}])
    _handle_trigger(task, channel, thread_ts, user, client)


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


@app.action("interactive_approval")
def on_interactive_approval(ack, body, client):
    """scripts/slack_approval.py 가 게시한 승인/질문 버튼 클릭 처리.

    value 형식: "{approval_id}:{선택지}". 클릭 결과는 state.put_approval_answer 로
    interactive-approvals.json 에 기록되고, opencode 서브프로세스에서 실행 중인
    scripts/slack_approval.py 가 그 파일을 폴링해 응답을 이어받는다 — 이 핸들러와 그 스크립트는
    서로 다른 프로세스이므로 파일이 유일한 연결고리다."""
    ack()
    value = body["actions"][0]["value"]
    if ":" not in value:
        return
    approval_id, choice = value.split(":", 1)
    user = body.get("user", {}).get("id", "")
    channel_id = body["channel"]["id"]
    message_ts = body["message"]["ts"]

    recorded = put_approval_answer(approval_id, choice, user)
    if not recorded:
        # 이미 다른 클릭으로 응답됨 — 중복 클릭 무시, 현재 상태만 안내.
        client.chat_postEphemeral(
            channel=channel_id, user=user,
            text="이미 다른 응답으로 처리된 요청입니다.",
        )
        return

    original_blocks = body["message"].get("blocks", [])
    kept = [b for b in original_blocks if b.get("type") != "actions"]
    kept.append({"type": "context", "elements": [
        {"type": "mrkdwn", "text": f"✅ 선택됨: *{choice}* (by <@{user}>)"}
    ]})
    client.chat_update(channel=channel_id, ts=message_ts, text=f"✅ 선택됨: {choice}", blocks=kept)


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


_NOTION_URL_RE = re.compile(r"https://(?:www\.)?notion\.so/\S+|https://app\.notion\.com/\S+")


def _extract_notion_url(review_log_path: Path) -> str | None:
    """review-log.md 에서 가장 최근에 기록된 Notion 페이지 URL을 찾는다.

    CLAUDE.md Phase 5가 Notion 저장에 성공해도, slack-notification.json 을 만드는 시점(예전엔
    Notion보다 먼저 실행되던 5-1)에 그 URL을 몰라서 Slack 알림에 전혀 안 실리는 문제가 실제로
    있었다(2026-07-29, 소화물-인증-등록제 워크스페이스). CLAUDE.md 는 순서를 바꿔 고쳤지만, 이
    bridge 합성 폴백도 review-log.md 를 직접 뒤져 같은 문제를 겪지 않도록 보강한다."""
    if not review_log_path.exists():
        return None
    try:
        text = review_log_path.read_text(encoding="utf-8")
    except OSError:
        return None
    matches = _NOTION_URL_RE.findall(text)
    if not matches:
        return None
    return matches[-1].rstrip(").,\"'")


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
    report_grade = _grab_meta(final_text, "보고서 등급")
    active = _grab_meta(final_text, "활성 멤버") or "alpha(조사) · beta(보고서)"
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

    fields = [
        {"type": "mrkdwn", "text": f"*주제*\n{topic_short}"},
        {"type": "mrkdwn", "text": f"*작성일*\n{written}"},
        {"type": "mrkdwn", "text": f"*Task Type*\n{task_type}"},
    ]
    if report_grade:
        # dev/code-review 등 등급 미적용 type 은 final-artifact.md 에 이 줄이 없어 report_grade == "" 임
        fields.append({"type": "mrkdwn", "text": f"*보고서 등급*\n{report_grade}"})
    fields += [
        {"type": "mrkdwn", "text": f"*활성 멤버*\n{active}"},
        {"type": "mrkdwn", "text": f"*사이클*\n{cycle}"},
        {"type": "mrkdwn", "text": f"*승인*\n{approval}"},
    ]

    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "✅ 에이전트 팀 보고서 완료", "emoji": True}},
        {"type": "section", "fields": fields},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": "*핵심 결과*\n" + "\n".join(f"• {x}" for x in insights[:5])}},
    ]
    if fact_summary:
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": f"*팩트체크 결과*\n{fact_summary}"}})
    notion_url = _extract_notion_url(ws / "review-log.md")
    if notion_url:
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": f"*Notion*: {notion_url}"}})
    blocks.append({"type": "context", "elements": [
        {"type": "mrkdwn", "text": f"로컬 경로: `output/{slug}/final/final-artifact.md` · bridge 자동 합성"}
    ]})

    return {
        "text": f"✅ [에이전트 팀] {topic_short} 완료",
        "blocks": blocks,
    }


def _ensure_notion_link(payload: dict, ws: Path) -> bool:
    """이미 존재하는 slack-notification.json 에 Notion 링크가 빠져 있으면 review-log.md 에서
    찾아 blocks 에 보강한다(payload 를 in-place 로 수정). 보강했으면 True 반환.

    실사례(2026-07-29, 소화물-인증-등록제): Phase 5가 Notion을 성공시켰는데도
    slack-notification.json 생성 시점 순서 문제로 링크가 아예 안 실렸고, 파일이 이미 존재하니
    _synthesize_block_kit_payload 의 보강 로직도 트리거될 기회가 없었다 — 그래서 기존 파일
    자체를 이 함수로 직접 보강한다."""
    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        return False
    already = any(
        "notion.so" in json.dumps(b, ensure_ascii=False) or "notion.com" in json.dumps(b, ensure_ascii=False)
        for b in blocks
    )
    if already:
        return False
    notion_url = _extract_notion_url(ws / "review-log.md")
    if not notion_url:
        return False
    insert_at = len(blocks)
    for i, b in enumerate(blocks):
        if b.get("type") == "context":
            insert_at = i
            break
    blocks.insert(insert_at, {"type": "section", "text": {"type": "mrkdwn", "text": f"*Notion*: {notion_url}"}})
    return True


def _is_download_link_block(block: dict) -> bool:
    """"다운로드/Download" 라벨과 최종 산출물 링크(final-artifact.md)가 함께 있는 블록만 정확히
    매칭한다 — "Markdown 다운로드 기능" 처럼 본문 내용상 무관하게 "다운로드"를 언급하는 블록까지
    같이 지우지 않기 위해 두 조건을 함께 요구한다."""
    text = json.dumps(block, ensure_ascii=False)
    return bool(_DOWNLOAD_LINK_LABEL_RE.search(text)) and "final-artifact.md" in text


def _strip_download_link_blocks(payload: dict) -> bool:
    """`distribution.slack.include_download_link: false`(기본값)면 다운로드 링크 블록을 제거한다.
    제거했으면 True 반환."""
    if INCLUDE_DOWNLOAD_LINK:
        return False
    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        return False
    filtered = [b for b in blocks if not _is_download_link_block(b)]
    if len(filtered) == len(blocks):
        return False
    payload["blocks"] = filtered
    return True


def _load_block_kit_payload(slug: str) -> tuple[dict | None, bool]:
    """Block Kit payload 확보. Returns (payload, was_synthesized).

    1) `output/{slug}/slack-notification.json` 이 있으면 그걸 사용 (Phase 5 정상 경로).
    2) 없으면 워크스페이스 산출물에서 합성하고 디스크에 저장(다음 follow-up 재사용).

    이전엔 `was_synthesized=True` 인 경우(팀장이 Phase 5 를 스킵/실패한 케이스) 별도의
    Incoming Webhook("Claude Agent Team" 이름으로 표시)에도 중복 발송했는데, 이 경로는
    scripts/slack_publish.py 를 통한 정식 Phase 5 배포와 별개로 팀장의 스코프 판단(예: "Phase 1-4까지만
    수행")을 무시하고 다른 채널·다른 봇 이름으로 알림을 흘려보내 혼란을 줬다 — 제거함.
    이제 `was_synthesized=True` 는 "Phase 5 가 실행되지 않았다"는 사실을 그대로 기록만 하고,
    이 스레드 알림 하나로 끝낸다.
    """
    team_root_str = os.environ.get("TEAM_ROOT")
    if not team_root_str:
        return None, False
    team_root = Path(team_root_str)
    path = team_root / "output" / slug / "slack-notification.json"

    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log.warning("slack-notification.json 읽기 실패 (%s): %s — 합성 fallback", slug, e)
        else:
            notion_added = _ensure_notion_link(payload, path.parent)
            link_stripped = _strip_download_link_blocks(payload)
            if notion_added or link_stripped:
                try:
                    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                    log.info("slack-notification.json 보강 저장 (%s): notion=%s, download_link_stripped=%s",
                              slug, notion_added, link_stripped)
                except OSError as e:
                    log.warning("slack-notification.json 보강 저장 실패 (%s): %s", slug, e)
            return payload, False

    payload = _synthesize_block_kit_payload(team_root, slug)
    if not payload:
        return None, False
    _strip_download_link_blocks(payload)
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

    # 진행 로그(💭 ...)는 스레드에 매번 새 메시지로 쌓지 않고, 메시지 하나를 계속
    # 갱신한다 — opencode 가 몇 초마다 라인을 쏟아내면 스레드가 도배되는 문제 완화.
    _progress_ts: list[str | None] = [None]

    def notify_progress(msg: str):
        if _progress_ts[0] is None:
            resp = _post(client, channel, thread_ts, text=msg)
            _progress_ts[0] = resp["ts"]
            return
        try:
            client.chat_update(channel=channel, ts=_progress_ts[0], text=msg)
        except Exception as e:
            log.warning("progress 메시지 갱신 실패, 새 메시지로 폴백: %s", e)
            resp = _post(client, channel, thread_ts, text=msg)
            _progress_ts[0] = resp["ts"]

    try:
        result = run_team_lead(
            slug, task,
            notify=notify,
            notify_progress=notify_progress,
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

    if status == "completed":
        # `final`(final-artifact.md)이 없어도 quick-query 완료일 수 있다 — 그 경로는
        # slack-notification.json 만 쓰고 final-artifact.md 는 만들지 않는다(풀 파이프라인 생략).
        # `_load_block_kit_payload` 는 final_path 유무와 무관하게 slack-notification.json 존재
        # 여부만으로 동작하므로 이 조건 완화만으로 충분하다.
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
                    notify("ℹ️ 이번 실행은 Phase 5(배포)를 수행하지 않아, 워크스페이스 산출물에서 알림을 자동 합성했습니다.")
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
    elif status == "failed":
        rc = result.get("returncode")
        lines = [
            f"❌ 실행 실패 — opencode 프로세스가 비정상 종료되었습니다 (exit code {rc}). "
            f"바로 위 오류 로그를 확인해 주세요. `output/{slug}/` 는 그대로 보존되어 있어 다시 시도할 수 있습니다."
        ]
    else:
        lines = [f"⚠️ 부분 완료 — 최종 산출물 미생성. `output/{slug}/` 내부 확인 필요."]

    if artifacts:
        lines.append(f"📎 생성/수정 파일 {len(artifacts)}개: " + ", ".join(f"`{a}`" for a in artifacts[:5]))
    if cost:
        lines.append(f"💰 비용 ${cost} · 턴 {turns}")
    notify("\n".join(lines))


_LOCK_FILE = Path(__file__).parent / "state" / "app.lock"


def _pid_alive(pid: int) -> bool:
    if os.name == "nt":
        try:
            out = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True, timeout=5,
            )
            return str(pid) in out.stdout
        except OSError:
            return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _acquire_single_instance_lock() -> None:
    """중복 실행 방지 — 같은 봇 토큰으로 app.py 두 프로세스가 동시에 Socket Mode 에
    붙으면 이벤트를 어느 쪽이 받을지 불확실해지고, state/*.json 을 서로 다른 프로세스가
    동시에 읽고 써서 꼬인다(2026-07-29 실사례: 후속 지시에 아무 응답도 없었음).
    PID 파일로 이미 살아있는 인스턴스가 있으면 즉시 종료하고, 없으면(또는 이전 프로세스가
    비정상 종료해 PID 파일만 남은 경우) 현재 PID 로 새로 기록한다."""
    _LOCK_FILE.parent.mkdir(exist_ok=True)
    if _LOCK_FILE.exists():
        try:
            old_pid = int(_LOCK_FILE.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            old_pid = None
        if old_pid and old_pid != os.getpid() and _pid_alive(old_pid):
            log.error(
                "이미 실행 중인 app.py 인스턴스가 있습니다 (PID %d). 중복 실행은 이벤트 중복 "
                "수신과 state 파일 경합을 유발하므로 시작하지 않습니다. 기존 프로세스를 먼저 "
                "종료한 뒤 다시 실행하세요.", old_pid,
            )
            sys.exit(1)
    _LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")
    atexit.register(lambda: _LOCK_FILE.unlink(missing_ok=True))


if __name__ == "__main__":
    _acquire_single_instance_lock()
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    log.info("slack-bridge starting (Socket Mode)")
    handler.start()
