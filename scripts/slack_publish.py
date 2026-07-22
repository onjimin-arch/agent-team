#!/usr/bin/env python3
"""Slack 채널 배포 — 채널 join 선점검 포함 (Phase 5 안정화).

기존 문제: 실제 운영 로그에서 `distribution.slack.channel`(`#agent-log`) 발송이
"not_in_channel" 오류로 반복 실패했다 (`output/방식-영어-퀴즈-게임-개발/auto-log.md`,
`output/회의-녹음-텍스트-변환을-회의록/review-log.md`). 원인은 봇이 해당 채널에
초대되지 않은 상태에서 chat.postMessage 를 바로 호출했기 때문이다.

이 스크립트는:
1. 채널명을 채널 ID로 해석한다 (conversations.list 조회).
2. 발송 전 봇이 채널 멤버인지 확인하고, 아니면 conversations.join 을 먼저 시도한다
   (공개 채널이면 `channels:join` 스코프만으로 자동 해결된다).
3. join 도 실패하면(비공개 채널 등) 원인과 함께 "봇을 초대해 주세요" 같은
   실행 가능한 안내 메시지를 반환한다 — 무한 재시도나 프로세스 중단 없이
   호출자가 그대로 다음 단계를 진행할 수 있게 한다 (기존 프로토콜의
   "하나라도 실패하면 에러 메시지를 기록... 전체 프로세스는 종료하지 않음" 원칙 유지).

외부 의존성 없음 (stdlib `urllib`만 사용) — slack-bridge 의 .venv 가 아니어도 동작한다.

사용 예:
    export SLACK_BOT_TOKEN=xoxb-...
    python scripts/slack_publish.py --channel "#agent-log" --text "완료: ..." \\
        --blocks-file output/slug/slack-notification.json

종료 코드: 0 성공 / 1 발송 실패(비치명적) / 2 설정 오류(토큰 없음 등)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://slack.com/api"


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


def resolve_channel_id(token: str, channel: str) -> tuple[str | None, str | None]:
    """채널명(#foo) 또는 ID(C0123)를 채널 ID로 해석. (채널ID, 에러) 튜플 반환."""
    name = channel.lstrip("#").strip()
    if name.upper().startswith("C") and name.isalnum():
        return name, None  # 이미 ID 형태로 보임

    cursor = ""
    for _ in range(20):  # 최대 20페이지 (2000개 채널) 까지만 탐색
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
    return None, "channel_not_found"


def ensure_member(token: str, channel_id: str) -> tuple[bool, str | None]:
    """채널 멤버인지 확인 후 아니면 join 시도. (성공여부, 에러) 반환."""
    info = _call("conversations.info", token, channel=channel_id)
    if info.get("ok") and info.get("channel", {}).get("is_member"):
        return True, None

    join = _call("conversations.join", token, channel=channel_id)
    if join.get("ok"):
        return True, None
    return False, join.get("error", "join_failed")


def post_message(token: str, channel_id: str, text: str, blocks: list | None) -> dict:
    kwargs = {"channel": channel_id, "text": text or " "}
    if blocks:
        kwargs["blocks"] = blocks
    return _call("chat.postMessage", token, **kwargs)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", required=True, help="채널명(#agent-log) 또는 채널 ID")
    parser.add_argument("--text", default="", help="fallback/알림 텍스트")
    parser.add_argument("--blocks-file", default="", help="Block Kit JSON 파일 경로 (선택)")
    args = parser.parse_args()

    token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print(json.dumps({"success": False, "error": "SLACK_BOT_TOKEN_missing"}, ensure_ascii=False))
        return 2

    blocks = None
    if args.blocks_file:
        try:
            payload = json.loads(open(args.blocks_file, encoding="utf-8").read())
            blocks = payload.get("blocks", payload if isinstance(payload, list) else None)
            if not args.text:
                args.text = payload.get("text", "")
        except (OSError, json.JSONDecodeError) as e:
            print(json.dumps({"success": False, "error": "blocks_file_read_failed", "detail": str(e)},
                              ensure_ascii=False))
            return 2

    channel_id, err = resolve_channel_id(token, args.channel)
    if err:
        print(json.dumps({
            "success": False, "error": err, "channel": args.channel,
            "hint": f"채널을 찾을 수 없습니다. 채널명이 맞는지, 봇이 워크스페이스에 설치되어 있는지 확인하세요.",
        }, ensure_ascii=False))
        return 1

    ok, join_err = ensure_member(token, channel_id)
    if not ok:
        print(json.dumps({
            "success": False, "error": "not_in_channel", "channel": args.channel, "join_error": join_err,
            "hint": f"봇이 비공개 채널이거나 자동 참여 권한이 없습니다. Slack에서 "
                    f"`/invite @agent-team-bot` 를 {args.channel} 채널에 직접 실행해 초대해 주세요.",
        }, ensure_ascii=False))
        return 1

    resp = post_message(token, channel_id, args.text, blocks)
    if not resp.get("ok"):
        print(json.dumps({"success": False, "error": resp.get("error", "post_failed"), "channel": args.channel},
                          ensure_ascii=False))
        return 1

    print(json.dumps({
        "success": True, "channel": args.channel, "ts": resp.get("ts"),
        "permalink_hint": "chat.getPermalink 미호출 — ts/channel 로 워크스페이스에서 확인 가능",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
