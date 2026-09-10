#!/usr/bin/env python3
"""vault 파일시스템을 직접 검색한다 — Obsidian 실행 여부와 무관 (설계서 3-1/3-7절 결정).

지금은 키워드/태그 필터 단계만 동작한다. "하이브리드: 필터 → 임베딩 재순위"의 임베딩 재순위 단계는
아직 붙어있지 않다 — Smart Connections 같은 로컬 임베딩 플러그인을 설치한 뒤 그 인덱스 포맷을 보고
`rerank_by_embedding()`을 채울 예정이다(설계서 5절 가정 4, 미해소). 그때까지는 키워드 검색만으로도
"관련 노트 없음"보다는 유용하므로 이 상태로 둔다 — 가짜 임베딩 유사도를 지어내지 않는다.

사용:
    python knowledge_query.py --vault "<vault 절대경로>" --query "n8n 워크플로우" --max-results 5

배치(note-structurer)가 락을 쥐고 있으면 최대 30초 폴링 대기 후, 그래도 안 풀리면 "vault_busy"를
반환한다(호출한 멤버가 나중에 재시도) — [2-3] 락 판정 참고.

셀프테스트: python knowledge_query.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[4]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
import kb_lib  # noqa: E402

KB_OUTPUT = _AGENT_TEAM_ROOT / "output" / "knowledge-agent"
SEARCH_FOLDERS = ["01_Projects", "02_Areas", "03_Resources", "04_Permanent"]
_EXCERPT_RADIUS = 120


def _score_and_excerpt(query_terms: list[str], title: str, tags: list[str], body: str) -> tuple[int, str]:
    haystack = f"{title}\n{' '.join(tags)}\n{body}".lower()
    score = sum(haystack.count(t.lower()) for t in query_terms)
    if score == 0:
        return 0, ""
    first_term = next((t for t in query_terms if t.lower() in body.lower()), None)
    if first_term is None:
        return score, body[:_EXCERPT_RADIUS]
    idx = body.lower().find(first_term.lower())
    start, end = max(0, idx - _EXCERPT_RADIUS), min(len(body), idx + _EXCERPT_RADIUS)
    return score, ("…" if start > 0 else "") + body[start:end].strip() + ("…" if end < len(body) else "")


def search(vault: Path, query: str, folders: list[str] = SEARCH_FOLDERS, max_results: int = 5) -> list[dict]:
    query_terms = [t for t in re.split(r"\s+", query.strip()) if t]
    if not query_terms:
        return []

    candidates = []
    for folder in folders:
        base = vault / folder
        if not base.exists():
            continue
        for md in base.glob("**/*.md"):
            fm, body = kb_lib.read_note(md)
            title = md.stem
            score, excerpt = _score_and_excerpt(query_terms, title, fm.get("tags", []) or [], body)
            if score > 0:
                candidates.append({"path": str(md), "title": title, "score": score, "excerpt": excerpt, "tags": fm.get("tags", [])})

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return rerank_by_embedding(candidates, query)[:max_results]


def rerank_by_embedding(candidates: list[dict], query: str) -> list[dict]:
    """TODO: Smart Connections(또는 자체 호스팅) 임베딩 인덱스가 준비되면 여기서 코사인 유사도로
    재순위한다. 지금은 키워드 스코어 순서를 그대로 통과시킨다(가짜 유사도 지어내지 않음)."""
    return candidates


def query_with_lock_check(vault: Path, query: str, max_results: int = 5) -> dict:
    if not kb_lib.wait_for_lock(KB_OUTPUT, max_wait_sec=30, poll_sec=2, stale_after_sec=300):
        return {"success": False, "error": "vault_busy", "hint": "note-structurer 배치가 진행 중입니다. 잠시 후 다시 시도하세요."}
    results = search(vault, query, max_results=max_results)
    if not results:
        return {"success": True, "results": [], "message": "관련 노트 없음"}
    return {"success": True, "results": results}


def _selftest() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        (vault / "01_Projects").mkdir(parents=True)
        (vault / "03_Resources").mkdir(parents=True)

        kb_lib.write_note(
            vault / "01_Projects" / "a.md",
            {"source": "notion", "source_id": "x", "date": "2026-08-12T00:00:00Z", "raw": False, "status": "done", "tags": ["ax"]},
            "n8n 워크플로우 자동화에 대한 정리 내용입니다.",
        )
        kb_lib.write_note(
            vault / "03_Resources" / "b.md",
            {"source": "web", "source_id": "y", "date": "2026-08-12T00:00:00Z", "raw": False, "status": "done", "tags": []},
            "전혀 관계없는 다른 주제입니다.",
        )

        results = search(vault, "n8n 워크플로우")
        assert len(results) == 1, results
        assert results[0]["title"] == "a", results
        assert "n8n" in results[0]["excerpt"]

        empty = search(vault, "존재하지않는검색어xyz")
        assert empty == []

    print("OK: knowledge_query selftest passed")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault")
    parser.add_argument("--query")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not args.vault or not args.query:
        parser.error("--vault 와 --query 는 --selftest 가 아닐 때 필수")

    result = query_with_lock_check(Path(args.vault), args.query, args.max_results)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
