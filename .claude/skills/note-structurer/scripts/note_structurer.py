#!/usr/bin/env python3
"""note-structurer의 결정론적(코드) 부분 — 분류/태깅 자체(LLM 판단)는 이 스크립트가 하지 않는다.

역할 분담(설계서 3-4절 "에이전트 판단 vs 스크립트"):
- 이 스크립트: pending 노트 나열, 락 획득/해제, 태그 유사도 치환, 에스컬레이션 규칙 판정,
  source_id 중복 병합, 폴더 이동, 배치 로그 기록 — 전부 결정론적.
- 메인 에이전트(LLM): 각 pending 노트를 읽고 목적지 폴더·태그·링크 후보·판단 근거 텍스트·민감정보
  의심 여부를 결정한다. 그 결과를 이 스크립트의 `finalize` 서브커맨드에 JSON으로 넘긴다.

CLI 서브커맨드:
    list-pending   --vault V                          → pending 노트 목록(JSON)
    acquire-lock   --vault V
    release-lock   --vault V
    finalize       --vault V --decision-file D.json    → 노트 1건 완료 처리
    log-summary    --vault V                           → 오늘자 배치 로그 기록(list-pending 재계산 기반)

decision JSON 형식(예):
{
  "inbox_path": "00_Inbox/xxx.md",
  "destination_candidates": ["01_Projects"],   // 2개 이상이면 동률로 에스컬레이션
  "tags": ["ax", "n8n"],
  "related": ["[[01_AX_인프라_자동화]]"],
  "reasoning": "...",                           // review_needed 시 그대로 frontmatter에 기록됨
  "sensitive_flag": false,
  "body": "[사실] ...최종 본문(마킹 완료)..."
}

셀프테스트(파일시스템만, LLM/네트워크 없이): python note_structurer.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[4]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
import kb_lib  # noqa: E402

KB_OUTPUT = _AGENT_TEAM_ROOT / "output" / "knowledge-agent"
DESTINATION_FOLDERS = ["01_Projects", "02_Areas", "03_Resources", "04_Permanent"]
_MIN_BODY_LEN = 30  # 이보다 짧은 원문은 "모호"로 보고 에스컬레이션 (규칙 기반 필터, 2-2절)


def list_pending(vault: Path) -> list[dict]:
    items = []
    for md in sorted((vault / "00_Inbox").glob("*.md")):
        fm, body = kb_lib.read_note(md)
        if fm.get("status") == "pending":
            items.append({"path": str(md), "frontmatter": fm, "body": body})
    return items


def decide_escalation(destination_candidates: list[str], tags: list[str], body_len: int, sensitive_flag: bool) -> tuple[bool, str | None]:
    """LLM이 낸 후보/판단 뒤에 돌리는 규칙 기반 필터([2-2] 결정) — 확신도를 숫자로 묻지 않는다."""
    if len(destination_candidates) != 1:
        return True, f"목적지 폴더 후보 {len(destination_candidates)}개(동률 또는 0개)"
    if destination_candidates[0] not in DESTINATION_FOLDERS:
        return True, f"알 수 없는 목적지 폴더: {destination_candidates[0]}"
    if not tags:
        return True, "태그 후보 없음"
    if body_len < _MIN_BODY_LEN:
        return True, f"원문이 짧음({body_len}자 < {_MIN_BODY_LEN}자)"
    if sensitive_flag:
        return True, "민감정보 의심"
    return False, None


def _apply_tag_similarity(vault: Path, proposed_tags: list[str]) -> list[str]:
    existing = kb_lib.collect_existing_tags(vault, DESTINATION_FOLDERS)
    final_tags = []
    for tag in proposed_tags:
        matched = kb_lib.suggest_existing_tag(tag, existing)
        final_tags.append(matched or tag)
    return sorted(set(final_tags))


def finalize(vault: Path, decision: dict) -> dict:
    inbox_path = Path(decision["inbox_path"])
    if not inbox_path.is_absolute():
        inbox_path = vault / inbox_path
    if not inbox_path.exists():
        return {"ok": False, "error": "inbox_note_not_found", "path": str(inbox_path)}

    fm, _old_body = kb_lib.read_note(inbox_path)
    source_id = fm.get("source_id")
    candidates = decision.get("destination_candidates", [])
    tags = _apply_tag_similarity(vault, decision.get("tags", []))
    # "원문이 짧거나 모호"는 LLM이 새로 쓴 최종 본문이 아니라 Inbox의 원본 원자료 길이로 판단한다
    escalate, reason = decide_escalation(candidates, tags, len(_old_body), decision.get("sensitive_flag", False))

    if escalate:
        fm["review_needed"] = True
        fm["review_reason"] = reason
        # status는 pending 그대로 둔다 — 사람이 review_needed만 지우면 다음 배치가 자동 재인식([2-3] 결정)
        kb_lib.write_note(inbox_path, fm, decision.get("body", _old_body))
        return {"ok": True, "action": "escalated", "path": str(inbox_path), "reason": reason}

    destination_folder = candidates[0]
    existing = kb_lib.find_note_by_source_id(vault, DESTINATION_FOLDERS, source_id) if source_id else None

    new_fm = {
        "source": fm.get("source"),
        "source_id": source_id,
        "date": fm.get("date"),
        "raw": False,
        "status": "done",
        "project": decision.get("project", ""),
        "tags": tags,
        "related": decision.get("related", []),
    }
    if not new_fm["project"]:
        del new_fm["project"]
    if not new_fm["related"]:
        del new_fm["related"]

    if existing is not None:
        # source_id 중복 → 새 노트를 만들지 않고 기존 노트를 갱신([2-3] "소스 문서 업데이트/중복 방지" 결정)
        kb_lib.write_note(existing, new_fm, decision.get("body", ""))
        inbox_path.unlink()
        return {"ok": True, "action": "updated_existing", "path": str(existing)}

    dest_path = vault / destination_folder / inbox_path.name
    kb_lib.write_note(dest_path, new_fm, decision.get("body", ""))
    inbox_path.unlink()
    return {"ok": True, "action": "created", "path": str(dest_path)}


def log_summary(vault: Path, results: list[dict]) -> Path:
    today = date.today().isoformat().replace("-", "")
    log_path = KB_OUTPUT / "batch_logs" / f"{today}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "created": sum(1 for r in results if r.get("action") == "created"),
        "updated_existing": sum(1 for r in results if r.get("action") == "updated_existing"),
        "escalated": sum(1 for r in results if r.get("action") == "escalated"),
        "failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }
    log_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return log_path


def _selftest() -> None:
    import tempfile

    assert decide_escalation(["01_Projects"], ["ax"], 100, False) == (False, None)
    ok, reason = decide_escalation(["01_Projects", "02_Areas"], ["ax"], 100, False)
    assert ok and "동률" in reason, reason
    ok, reason = decide_escalation(["01_Projects"], [], 100, False)
    assert ok and "태그" in reason, reason
    ok, reason = decide_escalation(["01_Projects"], ["ax"], 5, False)
    assert ok and "짧음" in reason, reason
    ok, reason = decide_escalation(["01_Projects"], ["ax"], 100, True)
    assert ok and "민감정보" in reason, reason

    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        for folder in ["00_Inbox"] + DESTINATION_FOLDERS:
            (vault / folder).mkdir(parents=True)

        inbox_note = vault / "00_Inbox" / "test.md"
        kb_lib.write_note(inbox_note, {
            "source": "notion", "source_id": "notion:page-1", "date": "2026-08-12T00:00:00Z",
            "raw": True, "status": "pending",
        }, "충분히 긴 원본 텍스트입니다 — 30자 넘는 원자료라 모호함 규칙에 안 걸려야 합니다.")

        pending = list_pending(vault)
        assert len(pending) == 1, pending

        # 정상 분류 → 신규 생성
        result = finalize(vault, {
            "inbox_path": str(inbox_note),
            "destination_candidates": ["01_Projects"],
            "tags": ["ax"],
            "reasoning": "명확함",
            "sensitive_flag": False,
            "body": "[사실] 정리된 본문",
        })
        assert result["ok"] and result["action"] == "created", result
        assert not inbox_note.exists()  # Inbox에서 사라짐
        assert Path(result["path"]).parent.name == "01_Projects"

        # 같은 source_id 재수집 → 기존 노트 갱신(신규 생성 아님)
        inbox_note2 = vault / "00_Inbox" / "test2.md"
        kb_lib.write_note(inbox_note2, {
            "source": "notion", "source_id": "notion:page-1", "date": "2026-08-12T01:00:00Z",
            "raw": True, "status": "pending",
        }, "갱신된 원본 텍스트입니다 — 이것도 30자 넘겨서 모호함 규칙에 안 걸리게 합니다.")
        result2 = finalize(vault, {
            "inbox_path": str(inbox_note2),
            "destination_candidates": ["01_Projects"],
            "tags": ["ax"],
            "sensitive_flag": False,
            "body": "[사실] 갱신된 본문",
        })
        assert result2["ok"] and result2["action"] == "updated_existing", result2
        assert result2["path"] == result["path"]  # 같은 파일이 갱신됨, 새 파일 안 생김

        # 목적지 후보 2개 → 에스컬레이션, Inbox에 남고 status는 pending 유지
        inbox_note3 = vault / "00_Inbox" / "test3.md"
        kb_lib.write_note(inbox_note3, {
            "source": "file", "source_id": "file:xyz", "date": "2026-08-12T02:00:00Z",
            "raw": True, "status": "pending",
        }, "모호한 원본")
        result3 = finalize(vault, {
            "inbox_path": str(inbox_note3),
            "destination_candidates": ["01_Projects", "02_Areas"],
            "tags": ["ax"],
            "sensitive_flag": False,
            "body": "본문",
        })
        assert result3["ok"] and result3["action"] == "escalated", result3
        fm3, _ = kb_lib.read_note(inbox_note3)
        assert fm3.get("review_needed") is True and fm3.get("status") == "pending", fm3

        log_path = log_summary(vault, [result, result2, result3])
        logged = json.loads(log_path.read_text(encoding="utf-8"))
        assert logged["created"] == 1 and logged["updated_existing"] == 1 and logged["escalated"] == 1, logged

    print("OK: note_structurer selftest passed")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list-pending")
    p_list.add_argument("--vault", required=True)

    p_acq = sub.add_parser("acquire-lock")
    p_acq.add_argument("--vault", required=True)

    p_rel = sub.add_parser("release-lock")
    p_rel.add_argument("--vault", required=True)

    p_fin = sub.add_parser("finalize")
    p_fin.add_argument("--vault", required=True)
    p_fin.add_argument("--decision-file", required=True)

    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if args.command == "list-pending":
        print(json.dumps(list_pending(Path(args.vault)), ensure_ascii=False))
    elif args.command == "acquire-lock":
        kb_lib.acquire_batch_lock(KB_OUTPUT)
        print(json.dumps({"ok": True}))
    elif args.command == "release-lock":
        kb_lib.release_batch_lock(KB_OUTPUT)
        print(json.dumps({"ok": True}))
    elif args.command == "finalize":
        decision = json.loads(Path(args.decision_file).read_text(encoding="utf-8"))
        print(json.dumps(finalize(Path(args.vault), decision), ensure_ascii=False))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
