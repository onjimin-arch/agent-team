#!/usr/bin/env python3
"""Notion 화이트리스트(DB/페이지)에서 cursor 이후 변경분만 pull → md 변환 → 00_Inbox 기록.

`agent-team/scripts/notion_fetch.py`(다른 부서 워크스페이스 조회용)의 요청/블록→텍스트 변환
헬퍼를 재사용한다 — 여기서는 같은 조직 Notion을 `NOTION_API_TOKEN`(읽기 전용 재사용, 지민님 확인
완료 2026-08-12)으로 조회한다는 점만 다르다.

화이트리스트 형식은 scripts/whitelist.example.json 참고 — 실제 파일은 scripts/whitelist.json으로
직접 만들어야 한다(설계서 3-5-1 "Notion 수집 범위는 화이트리스트" 결정).

사용:
    export NOTION_API_TOKEN=secret_xxx
    python notion_pull.py --vault "<vault 절대경로>" --whitelist scripts/whitelist.json

exit: 0=정상(0건 포함) / 1=설정 오류(토큰·화이트리스트 없음)

셀프테스트(네트워크 없이 순수 로직만): python notion_pull.py --selftest
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
import notion_fetch  # noqa: E402  (agent-team/scripts, 헬퍼 재사용)
import kb_lib  # noqa: E402

KB_OUTPUT = _AGENT_TEAM_ROOT / "output" / "knowledge-agent"


def _iso_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _pull_page(page_id: str, token: str, cursors: dict) -> dict | None:
    status, page = notion_fetch._request("GET", f"pages/{page_id}", token)
    if status != 200:
        return {"ok": False, "id": page_id, "error": page}
    last_edited = page.get("last_edited_time")
    if cursors.get(page_id) and last_edited and _iso_to_dt(last_edited) <= _iso_to_dt(cursors[page_id]):
        return None  # cursor 이후 변경 없음 → 스킵(증분 수집, 3-5-1 결정)
    blocks = notion_fetch._fetch_children(page_id, token)
    return {
        "ok": True,
        "id": page_id,
        "cursor_key": page_id,
        "title": notion_fetch._title_of(page),
        "body": notion_fetch.blocks_to_text(blocks),
        "last_edited_time": last_edited,
        "url": page.get("url", ""),
    }


def _pull_data_source(ds_id: str, token: str, cursors: dict) -> list[dict]:
    status, resp = notion_fetch._request("POST", f"data_sources/{ds_id}/query", token, {"page_size": 100})
    if status != 200:
        return [{"ok": False, "id": ds_id, "error": resp}]
    out = []
    for row in resp.get("results", []):
        page_id = row.get("id")
        last_edited = row.get("last_edited_time")
        cursor_key = f"{ds_id}:{page_id}"
        if cursors.get(cursor_key) and last_edited and _iso_to_dt(last_edited) <= _iso_to_dt(cursors[cursor_key]):
            continue
        blocks = notion_fetch._fetch_children(page_id, token)
        out.append({
            "ok": True,
            "id": page_id,
            "cursor_key": cursor_key,
            "title": notion_fetch._title_of(row),
            "body": notion_fetch.blocks_to_text(blocks),
            "last_edited_time": last_edited,
            "url": row.get("url", ""),
        })
    return out


def write_inbox_note(vault: Path, source_id: str, title: str, body: str, url: str) -> Path:
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:60].strip()
    # source_id 해시를 항상 파일명에 넣는다 — 같은 초에 제목이 같은 두 페이지를 처리하면 해시 없이는
    # 파일명이 충돌해 먼저 쓴 노트가 덮어써진다(migrate_existing_kb.py에서 실제로 겪은 버그와 동일 클래스).
    digest = hashlib.sha1(source_id.encode()).hexdigest()[:10]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    path = vault / "00_Inbox" / f"{ts}_{digest}_{safe_title}.md"
    fm = {
        "source": "notion",
        "source_id": source_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "raw": True,
        "status": "pending",
    }
    kb_lib.write_note(path, fm, f"# {title}\n\n원본: {url}\n\n{body}")
    return path


def run(vault: Path, whitelist: dict, token: str) -> dict:
    cursors_raw = kb_lib.get_cursor(KB_OUTPUT, "notion")
    cursors = json.loads(cursors_raw) if cursors_raw else {}

    written, failed = [], []
    for entry in whitelist.get("items", []):
        results = []
        if entry["type"] == "page":
            r = _pull_page(entry["id"], token, cursors)
            if r is not None:
                results = [r]
        elif entry["type"] == "data_source":
            results = _pull_data_source(entry["id"], token, cursors)

        for result in results:
            if not result.get("ok"):
                failed.append(result)
                continue
            path = write_inbox_note(vault, f"notion:page-{result['id']}", result["title"], result["body"], result["url"])
            written.append(str(path))
            cursors[result["cursor_key"]] = result["last_edited_time"]  # 쓰기 성공분만 전진 ([2-3] 결정)

    kb_lib.set_cursor(KB_OUTPUT, "notion", json.dumps(cursors, ensure_ascii=False))
    return {"success": True, "written": written, "failed": failed}


def _selftest() -> None:
    import tempfile

    assert _iso_to_dt("2026-08-12T00:00:00.000Z") < _iso_to_dt("2026-08-12T01:00:00.000Z")

    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        (vault / "00_Inbox").mkdir()
        path = write_inbox_note(vault, "notion:page-abc123", "테스트 페이지", "본문 내용", "https://notion.so/abc123")
        fm, body = kb_lib.read_note(path)
        assert fm["source"] == "notion" and fm["source_id"] == "notion:page-abc123" and fm["status"] == "pending"
        assert "본문 내용" in body

        # 네트워크 함수(_pull_page 등)는 호출하지 않고, cursor 비교 로직만 단위 검증
        cursors: dict = {"p1": "2026-08-12T00:00:00.000Z"}
        assert _iso_to_dt("2026-08-12T00:00:00.000Z") <= _iso_to_dt(cursors["p1"])  # 변경 없음 판정 재현
        assert _iso_to_dt("2026-08-12T01:00:00.000Z") > _iso_to_dt(cursors["p1"])  # 변경 있음 판정 재현

    print("OK: notion_pull selftest passed (network 호출 없이 로직만 검증)")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault")
    parser.add_argument("--whitelist")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not args.vault or not args.whitelist:
        parser.error("--vault 와 --whitelist 는 --selftest 가 아닐 때 필수")

    token = os.environ.get("NOTION_API_TOKEN", "").strip()
    if not token:
        print(json.dumps({"success": False, "error": "NOTION_API_TOKEN_missing"}, ensure_ascii=False))
        return 1

    whitelist_path = Path(args.whitelist)
    if not whitelist_path.exists():
        print(json.dumps({"success": False, "error": "whitelist_not_found", "path": str(whitelist_path)}, ensure_ascii=False))
        return 1

    result = run(Path(args.vault), json.loads(whitelist_path.read_text(encoding="utf-8")), token)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
