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
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://slack.com/api"

# team-config.yaml 의 distribution.slack.include_download_link 는 기본 false(다운로드 링크 제외)인데,
# Team Lead(LLM)가 이 규칙을 반복해서 무시하고 slack-notification.json 에 다운로드 링크를 넣는 사례가
# 여러 워크스페이스에서 확인됐다(텍스트 지시만으로는 신뢰할 수 없음). 그래서 이 스크립트가 발송 직전에
# 한 번 더 결정론적으로 걸러낸다 — "다운로드/download" 라벨과 최종 산출물 링크(final-artifact.md)가
# 함께 있는 블록만 정확히 매칭해 제거하고, 무관한 본문 언급(예: "Markdown 다운로드 기능")은 건드리지
# 않는다. 정말로 다운로드 링크를 보내야 하면(include_download_link: true) --allow-download-link 를
# 명시적으로 넘긴다 — 기본값은 항상 "제거"다.
_DOWNLOAD_LINK_LABEL_RE = re.compile(r"다운로드|download", re.IGNORECASE)


def _is_download_link_block(block: dict) -> bool:
    text = json.dumps(block, ensure_ascii=False)
    return bool(_DOWNLOAD_LINK_LABEL_RE.search(text)) and "final-artifact.md" in text


def _strip_download_link_blocks(blocks: list) -> list:
    return [b for b in blocks if not _is_download_link_block(b)]


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
    """일부 조회성 메서드(예: conversations.info)는 JSON POST 바디를 받지 않고
    `invalid_arguments` 로 실패한다 — GET + 쿼리스트링으로 호출해야 하는 전용 헬퍼."""
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
    """채널명(#foo) 또는 ID(C0123)를 채널 ID로 해석. (채널ID, 에러) 튜플 반환."""
    name = channel.lstrip("#").strip()
    if name.upper().startswith("C") and name.isalnum():
        return name, None  # 이미 ID 형태로 보임

    cursor = ""
    for _ in range(20):  # 최대 20페이지 (workspace 규모에 따라 부족할 수 있음 — 아래 참고)
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
    # 채널이 많은(Enterprise Grid 등) 워크스페이스에서는 이름 검색이 페이지 한도 내에
    # 못 찾고 끝날 수 있다 — 채널 ID(C로 시작)를 --channel 에 직접 넘기면 이 탐색을
    # 완전히 건너뛰므로(위 fast-path), 그 경우 channel_not_found 대신 이 안내를 반환한다.
    return None, "channel_search_exhausted"


def ensure_member(token: str, channel_id: str) -> tuple[bool, str | None]:
    """채널 멤버인지 확인 후 아니면 join 시도. (성공여부, 에러) 반환."""
    info = _call_get("conversations.info", token, channel=channel_id)
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
    parser.add_argument("--allow-download-link", action="store_true",
                         help="team-config.yaml 의 distribution.slack.include_download_link: true 일 때만 "
                              "명시적으로 넘긴다. 기본값(생략)은 다운로드 링크 블록을 강제로 제거한다.")
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
            if blocks and not args.allow_download_link:
                blocks = _strip_download_link_blocks(blocks)
        except (OSError, json.JSONDecodeError) as e:
            print(json.dumps({"success": False, "error": "blocks_file_read_failed", "detail": str(e)},
                              ensure_ascii=False))
            return 2

    channel_id, err = resolve_channel_id(token, args.channel)
    if err:
        hint = "채널을 찾을 수 없습니다. 채널명이 맞는지, 봇이 워크스페이스에 설치되어 있는지 확인하세요."
        if err == "channel_search_exhausted":
            hint = (
                "채널이 매우 많은 워크스페이스라 이름 검색이 탐색 한도 내에 채널을 못 찾았습니다. "
                "Slack에서 해당 채널의 '채널 ID'(C로 시작하는 값)를 복사해 --channel 인자에 "
                "이름 대신 직접 넘기면 이 검색을 건너뛰고 바로 동작합니다."
            )
        print(json.dumps({
            "success": False, "error": err, "channel": args.channel, "hint": hint,
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
