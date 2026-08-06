#!/usr/bin/env python3
"""Slack 인터랙티브 버튼 승인/질문 — 게시 후 클릭 응답을 실제로 기다린다.

CLAUDE.md 의 "인터랙티브 승인(Slack 버튼)" 절에서 사용하는 공통 프리미티브. AUTO 모드의
human_approval 게이트, Phase 1-2 plan 확정, Phase 6-3 신규 에이전트 제안, Quick Query 의 민감
데이터 공유 승인 등 여러 지점에서 동일하게 재사용한다.

동작 원리:
1. 버튼(각 옵션당 하나, action_id="interactive_approval", value="{approval_id}:{option}")이 달린
   메시지를 Slack 채널/스레드에 게시한다.
2. slack-bridge/app.py 의 `@app.action("interactive_approval")` 핸들러가 클릭을 받으면
   `slack-bridge/state/interactive-approvals.json` 에 응답을 기록한다 — 이 스크립트는 그 프로세스와
   완전히 별도(opencode 서브프로세스)로 실행되므로, 공유 파일시스템의 이 JSON 파일을 폴링해 응답을
   확인한다 (app.py 의 state.py 와 동일한 스키마를 쓰지만, 이 스크립트는 slack-bridge 패키지를
   import 하지 않고 자체적으로 파일을 읽고 쓴다 — scripts/ 의 다른 도구들처럼 실행 환경에 독립적으로
   동작하기 위함).
3. `--timeout-sec` 안에 응답이 오면 그 선택지를, 안 오면 `answered: false` 를 반환한다(비치명적,
   exit 0) — 호출자(Team Lead)가 CLAUDE.md 의 "타임아웃 시 보류" 규칙에 따라 처리한다.

외부 의존성 없음 (stdlib `urllib`만 사용) — slack-bridge 의 .venv 가 아니어도 동작한다.

사용 예:
    export SLACK_BOT_TOKEN=xoxb-...
    python scripts/slack_approval.py --channel "#oc-agent-log" \\
        --question "이 조회 결과(ERP 손익)를 공유해도 될까요?" \\
        --options "승인,거부" --timeout-sec 900

종료 코드: 0 성공(응답 또는 타임아웃 모두 포함) / 1 발송 실패(비치명적) / 2 설정 오류(토큰 없음 등)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

API_BASE = "https://slack.com/api"

# app.py 의 state.py 와 동일한 경로/스키마를 공유한다. scripts/ 는 team_root 기준 cwd 로 호출되는
# 것이 기본이지만, cwd 에 의존하지 않도록 이 파일 위치 기준 상대경로로 고정한다.
_STATE_FILE = Path(__file__).resolve().parent.parent / "slack-bridge" / "state" / "interactive-approvals.json"

_DEFAULT_TIMEOUT_SEC = 1800
_POLL_INTERVAL_SEC = 3
_DENY_WORDS = {"거부", "반려", "취소", "reject", "no", "deny", "cancel"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _call(method: str, token: str, **params) -> dict:
    url = f"{API_BASE}/{method}"
    data = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"http_{e.code}"}
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"network_error: {e.reason}"}


def _call_get(method: str, token: str, **params) -> dict:
    url = f"{API_BASE}/{method}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"http_{e.code}"}
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"network_error: {e.reason}"}


def resolve_channel_id(token: str, channel: str) -> tuple[str | None, str | None]:
    """채널명(#foo) 또는 ID(C0123)를 채널 ID로 해석. (채널ID, 에러) 튜플 반환.

    scripts/slack_publish.py 와 동일한 탐색 로직 — 두 스크립트는 각자 독립 실행 가능해야 하므로
    (공유 import 없이) 의도적으로 중복시킨다.
    """
    name = channel.lstrip("#").strip()
    if name.upper().startswith("C") and name.isalnum():
        return name, None

    cursor = ""
    for _ in range(20):
        resp = _call(
            "conversations.list", token,
            types="public_channel,private_channel", limit=200,
            **({"cursor": cursor} if cursor else {}),
        )
        if not resp.get("ok"):
            return None, resp.get("error", "conversations_list_failed")
        for ch in resp.get("channels", []):
            if ch.get("name") == name:
                return ch["id"], None
        cursor = resp.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            break
    return None, "channel_search_exhausted"


def ensure_member(token: str, channel_id: str) -> tuple[bool, str | None]:
    info = _call_get("conversations.info", token, channel=channel_id)
    if info.get("ok") and info.get("channel", {}).get("is_member"):
        return True, None
    join = _call("conversations.join", token, channel=channel_id)
    if join.get("ok"):
        return True, None
    return False, join.get("error", "join_failed")


def _button_style(option: str) -> str | None:
    return "danger" if option.strip().lower() in _DENY_WORDS else None


def _build_blocks(approval_id: str, question: str, context: str, options: list[str]) -> list[dict]:
    blocks: list[dict] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"❓ *승인 요청*\n{question}"}},
    ]
    if context:
        blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": context}]})
    elements = []
    for i, opt in enumerate(options):
        btn = {
            "type": "button",
            "text": {"type": "plain_text", "text": opt},
            "action_id": "interactive_approval",
            "value": f"{approval_id}:{opt}",
        }
        style = _button_style(opt) or ("primary" if i == 0 else None)
        if style:
            btn["style"] = style
        elements.append(btn)
    blocks.append({"type": "actions", "block_id": f"interactive_approval:{approval_id}", "elements": elements})
    return blocks


def _load_state() -> dict:
    if not _STATE_FILE.exists():
        return {}
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", required=True, help="채널명(#oc-agent-log) 또는 채널 ID")
    parser.add_argument("--question", required=True, help="사용자에게 물어볼 질문")
    parser.add_argument("--context", default="", help="추가 설명(선택) — context 블록으로 표시")
    parser.add_argument("--options", default="승인,거부", help="쉼표로 구분한 선택지 (기본: 승인,거부)")
    parser.add_argument("--thread-ts", default=None, help="스레드 안에 게시할 경우의 thread_ts")
    parser.add_argument("--timeout-sec", type=int, default=_DEFAULT_TIMEOUT_SEC)
    args = parser.parse_args()

    token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print(json.dumps({"success": False, "error": "SLACK_BOT_TOKEN_missing"}, ensure_ascii=False))
        return 2

    options = [o.strip() for o in args.options.split(",") if o.strip()]
    if not options:
        print(json.dumps({"success": False, "error": "no_options"}, ensure_ascii=False))
        return 2

    channel_id, err = resolve_channel_id(token, args.channel)
    if err:
        print(json.dumps({
            "success": False, "error": err, "channel": args.channel,
            "hint": "채널을 찾을 수 없습니다. 채널명 또는 채널 ID를 확인하세요.",
        }, ensure_ascii=False))
        return 1

    ok, join_err = ensure_member(token, channel_id)
    if not ok:
        print(json.dumps({
            "success": False, "error": "not_in_channel", "channel": args.channel, "join_error": join_err,
            "hint": f"봇이 비공개 채널이거나 자동 참여 권한이 없습니다. `/invite @agent-team-bot` 를 "
                    f"{args.channel} 채널에 직접 실행해 초대해 주세요.",
        }, ensure_ascii=False))
        return 1

    approval_id = uuid.uuid4().hex[:10]
    blocks = _build_blocks(approval_id, args.question, args.context, options)
    kwargs = {"channel": channel_id, "blocks": blocks, "text": f"❓ 승인 요청: {args.question}"}
    if args.thread_ts:
        kwargs["thread_ts"] = args.thread_ts
    resp = _call("chat.postMessage", token, **kwargs)
    if not resp.get("ok"):
        print(json.dumps({"success": False, "error": resp.get("error", "post_failed")}, ensure_ascii=False))
        return 1

    message_ts = resp.get("ts")
    deadline = time.monotonic() + max(args.timeout_sec, 1)
    while time.monotonic() < deadline:
        state = _load_state()
        entry = state.get(approval_id)
        if entry and entry.get("status") == "answered":
            print(json.dumps({
                "success": True, "answered": True, "approval_id": approval_id,
                "choice": entry.get("choice"), "responder": entry.get("user"),
                "answered_at": entry.get("answered_at"),
            }, ensure_ascii=False))
            return 0
        time.sleep(_POLL_INTERVAL_SEC)

    # 타임아웃 — 버튼을 비활성화하고(재클릭 방지) 안내만 남긴다. 실패로 취급하지 않는다(exit 0):
    # 호출자가 CLAUDE.md 의 "타임아웃 시 보류" 규칙에 따라 계속 진행 여부를 판단한다.
    _call(
        "chat.update", token, channel=channel_id, ts=message_ts,
        text=f"⏳ 시간 초과 — 응답 없음: {args.question}",
        blocks=[{"type": "section", "text": {"type": "mrkdwn",
            "text": f"⏳ *시간 초과 — 응답 없음*\n{args.question}"}}],
    )
    print(json.dumps({
        "success": True, "answered": False, "timeout": True, "approval_id": approval_id,
        "hint": "제한 시간 내 응답이 없었습니다. 승인이 꼭 필요한 작업이면 사람이 이 대화를 열어 "
                "직접 진행 여부를 확인해야 합니다 — 임의로 진행하지 마세요.",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
