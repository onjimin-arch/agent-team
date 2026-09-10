#!/usr/bin/env python3
"""knowledge-research의 결정론적 부분 — quota 하드캡, 초안 저장, vault 반영.

실제 웹 리서치·관련성 판단·요약 작성은 임시 서브에이전트(Agent 도구, "방법 B")가 한다
(SKILL.md 참고). 이 스크립트는 그 결과를 받아 quota를 체크하고 vault에 최종 반영한다.

CLI:
    check-quota  --daily-limit N            → quota 남았으면 카운트 증가 후 allowed:true
    finalize     --vault V --draft-file D.json  → 초안을 vault 03_Resources에 정식 노트로 반영

draft JSON 형식:
{
  "topic": "...", "body": "[사실] ...", "sources": ["https://..."],
  "has_conflicting_sources": false
}

셀프테스트: python knowledge_research.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[4]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
import kb_lib  # noqa: E402

KB_OUTPUT = _AGENT_TEAM_ROOT / "output" / "knowledge-agent"
DEFAULT_DESTINATION = "03_Resources"  # 리서치 결과는 정의상 참고자료 — [3-6] 결정


def check_quota(daily_limit: int) -> dict:
    allowed = kb_lib.check_and_increment_quota(KB_OUTPUT, "knowledge-research", daily_limit)
    if not allowed:
        return {"allowed": False, "error": "quota_exceeded", "daily_limit": daily_limit}
    return {"allowed": True}


def save_draft(topic: str, body: str, sources: list[str], has_conflicting_sources: bool = False) -> Path:
    today = date.today().isoformat()
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:60].strip() or "topic"
    draft_path = KB_OUTPUT / "research_drafts" / f"{safe_topic}_{today}.md"
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    source_lines = "\n".join(f"- {s}" for s in sources)
    conflict_note = "\n\n**출처 간 상충 있음** — 신뢰도 판단은 하지 않고 상충 사실만 기록함([3-6] 결정).\n" if has_conflicting_sources else ""
    draft_path.write_text(f"# {topic}\n\n{body}{conflict_note}\n\n## 출처\n{source_lines}\n", encoding="utf-8")
    return draft_path


def promote_to_vault(vault: Path, topic: str, body: str, sources: list[str], has_conflicting_sources: bool = False, destination: str = DEFAULT_DESTINATION) -> Path:
    source_id = f"research:{hashlib.sha1(topic.encode()).hexdigest()[:10]}-{date.today().isoformat()}"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:60].strip() or "topic"
    note_path = vault / destination / f"{ts}_research_{safe_topic}.md"
    fm = {
        "source": "research",
        "source_id": source_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "raw": False,
        "status": "done",
        "tags": ["research"],
    }
    source_lines = "\n".join(f"- {s}" for s in sources)
    conflict_note = "\n\n**출처 간 상충 있음**\n" if has_conflicting_sources else ""
    body_full = f"# {topic}\n\n{body}{conflict_note}\n\n## 출처\n{source_lines}\n"
    kb_lib.write_note(note_path, fm, body_full)
    return note_path


def finalize(vault: Path, draft: dict) -> dict:
    topic, body = draft["topic"], draft["body"]
    sources = draft.get("sources", [])
    has_conflicting = draft.get("has_conflicting_sources", False)
    save_draft(topic, body, sources, has_conflicting)  # 3-8절: 초안도 별도 보관
    note_path = promote_to_vault(vault, topic, body, sources, has_conflicting)
    return {"ok": True, "path": str(note_path), "summary": body[:200]}


def _selftest() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td_kb:
        kb_output = Path(td_kb)
        assert kb_lib.check_and_increment_quota(kb_output, "knowledge-research", 2) is True
        assert kb_lib.check_and_increment_quota(kb_output, "knowledge-research", 2) is True
        assert kb_lib.check_and_increment_quota(kb_output, "knowledge-research", 2) is False  # 하드캡

    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        (vault / "03_Resources").mkdir(parents=True)
        result = finalize(vault, {
            "topic": "경쟁사 X 동향",
            "body": "[사실] 경쟁사 X가 신규 서비스를 출시했다.",
            "sources": ["https://example.com/a", "https://example.com/b"],
            "has_conflicting_sources": True,
        })
        assert result["ok"]
        fm, body = kb_lib.read_note(Path(result["path"]))
        assert fm["source"] == "research" and fm["status"] == "done"
        assert "상충 있음" in body and "example.com/a" in body

    print("OK: knowledge_research selftest passed")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="command")

    p_q = sub.add_parser("check-quota")
    p_q.add_argument("--daily-limit", type=int, required=True)

    p_f = sub.add_parser("finalize")
    p_f.add_argument("--vault", required=True)
    p_f.add_argument("--draft-file", required=True)

    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if args.command == "check-quota":
        print(json.dumps(check_quota(args.daily_limit), ensure_ascii=False))
    elif args.command == "finalize":
        draft = json.loads(Path(args.draft_file).read_text(encoding="utf-8"))
        print(json.dumps(finalize(Path(args.vault), draft), ensure_ascii=False))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
