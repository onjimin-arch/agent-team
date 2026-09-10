#!/usr/bin/env python3
"""지정 채널에서 "결정됨"/"공유됨" 리액션이 달린 메시지만, cursor 이후로 REST 폴링해 원문 그대로
`00_Inbox`에 기록한다 (요약 안 함 — 요약은 note-structurer 배치가 한다, 2-2/2-3절 결정).

`agent-team/scripts/slack_publish.py`의 Slack Web API 호출 헬퍼(`_call_get`, `resolve_channel_id`)를
재사용한다. 토큰은 agent-team과 동일한 `SLACK_BOT_TOKEN`을 재사용한다(지민님 확인 완료 2026-08-12).

필터 기준(리액션 이모지 이름)은 scripts/filter_config.example.json 참고 — **이 리액션 기반 필터는
가정이며 실제 팀 사용 패턴과 맞는지 확인이 필요하다**(설계서 5절 가정 3, 아직 미해소).

사용:
    export SLACK_BOT_TOKEN=xoxb-...
    python slack_pull.py --vault "<vault 절대경로>" --config scripts/filter_config.json

셀프테스트(네트워크 없이 필터 로직만): python slack_pull.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[4]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / "scripts"))
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
import slack_publish  # noqa: E402  (agent-team/scripts, 헬퍼 재사용)
import kb_lib  # noqa: E402

KB_OUTPUT = _AGENT_TEAM_ROOT / "output" / "knowledge-agent"


def message_matches_tags(message: dict, reaction_tags: list[str]) -> bool:
    reactions = message.get("reactions", [])
    return any(r.get("name") in reaction_tags for r in reactions)


def _fetch_channel_messages(token: str, channel_id: str, oldest_ts: str | None) -> list[dict]:
    params = {"channel": channel_id, "limit": 200}
    if oldest_ts:
        params["oldest"] = oldest_ts
    resp = slack_publish._call_get("conversations.history", token, **params)
    if not resp.get("ok"):
        return []
    # Slack은 최신순으로 반환 — cursor 갱신을 위해 오래된 순으로 뒤집는다
    return list(reversed(resp.get("messages", [])))


def write_inbox_note(vault: Path, channel_name: str, message: dict) -> Path:
    ts = message["ts"]
    text = message.get("text", "")
    source_id = f"slack:{channel_name}:{ts}"
    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
    fname_ts = dt.strftime("%Y%m%d%H%M%S")
    digest = hashlib.sha1(source_id.encode()).hexdigest()[:8]
    path = vault / "00_Inbox" / f"{fname_ts}_slack_{channel_name}_{digest}.md"
    fm = {
        "source": "slack",
        "source_id": source_id,
        "date": dt.isoformat(),
        "raw": True,
        "status": "pending",
    }
    kb_lib.write_note(path, fm, f"# Slack #{channel_name}\n\n{text}")
    return path


def run(vault: Path, config: dict, token: str) -> dict:
    reaction_tags = config.get("reaction_tags", ["결정", "공유"])
    cursors_raw = kb_lib.get_cursor(KB_OUTPUT, "slack")
    cursors = json.loads(cursors_raw) if cursors_raw else {}

    written, failed = [], []
    for channel in config.get("channels", []):
        channel_id, err = slack_publish.resolve_channel_id(token, channel)
        if err:
            failed.append({"channel": channel, "error": err})
            continue
        oldest = cursors.get(channel_id)
        messages = _fetch_channel_messages(token, channel_id, oldest)
        latest_ts = oldest
        for message in messages:
            if not message_matches_tags(message, reaction_tags):
                latest_ts = message["ts"]  # 태그 안 붙어도 훑은 시점은 전진(같은 메시지 재검사 방지)
                continue
            path = write_inbox_note(vault, channel.lstrip("#"), message)
            written.append(str(path))
            latest_ts = message["ts"]  # 쓰기 성공분 기준으로만 전진 ([2-3] 결정)
        if latest_ts:
            cursors[channel_id] = latest_ts

    kb_lib.set_cursor(KB_OUTPUT, "slack", json.dumps(cursors, ensure_ascii=False))
    return {"success": True, "written": written, "failed": failed}


def _selftest() -> None:
    import tempfile

    msg_tagged = {"ts": "1699999999.000100", "text": "결정: A안으로 간다", "reactions": [{"name": "결정", "count": 1}]}
    msg_plain = {"ts": "1700000000.000100", "text": "그냥 잡담", "reactions": []}
    assert message_matches_tags(msg_tagged, ["결정", "공유"]) is True
    assert message_matches_tags(msg_plain, ["결정", "공유"]) is False

    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        (vault / "00_Inbox").mkdir()
        path = write_inbox_note(vault, "일반", msg_tagged)
        fm, body = kb_lib.read_note(path)
        assert fm["source"] == "slack" and fm["source_id"] == "slack:일반:1699999999.000100"
        assert "A안으로 간다" in body

    print("OK: slack_pull selftest passed (network 호출 없이 로직만 검증)")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault")
    parser.add_argument("--config")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not args.vault or not args.config:
        parser.error("--vault 와 --config 는 --selftest 가 아닐 때 필수")

    token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print(json.dumps({"success": False, "error": "SLACK_BOT_TOKEN_missing"}, ensure_ascii=False))
        return 1

    config_path = Path(args.config)
    if not config_path.exists():
        print(json.dumps({"success": False, "error": "config_not_found", "path": str(config_path)}, ensure_ascii=False))
        return 1

    result = run(Path(args.vault), json.loads(config_path.read_text(encoding="utf-8")), token)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
