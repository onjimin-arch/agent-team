#!/usr/bin/env python3
"""(미실행 — 준비만 된 스크립트) 경영전략실_지식베이스의 9개 큐레이션 파일을 `## ` 헤더 단위로 쪼개
`00_Inbox`에 raw 노트로 넣는다. 그 뒤로는 새 지식 수집과 동일하게 note-structurer 배치가 분류·
태깅·에스컬레이션을 처리한다 — 마이그레이션 전용 분류 로직을 새로 만들지 않는다(재사용).

지식수집_구조화_에이전트_설계서.md에서 "(C) 구조만 먼저 설계하고 이관은 나중에"로 결정됨
(2026-08-12) — 이 스크립트는 그 "나중"을 위해 준비만 해두는 것이다. **기본값은 --dry-run이며,
원본 9개 파일은 절대 수정·삭제하지 않는다**(Inbox에 새 노트만 만든다) — 그래도 실제 실행은 지민님이
결과를 검토한 뒤 명시적으로 --execute를 줘야 한다.

사용:
    # 1. 먼저 무엇이 만들어질지만 확인 (아무것도 쓰지 않음)
    python migrate_existing_kb.py --vault "<vault>" --kb-dir "<vault>/경영전략실_지식베이스"

    # 2. 검토 후 실제 실행
    python migrate_existing_kb.py --vault "<vault>" --kb-dir "<vault>/경영전략실_지식베이스" --execute

셀프테스트: python migrate_existing_kb.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[1]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
import kb_lib  # noqa: E402


def split_by_headers(text: str) -> list[tuple[str, str]]:
    """"# 제목\\n\\n## 섹션 A\\n...\\n## 섹션 B\\n..." → [("섹션 A", "..."), ("섹션 B", "...")].
    최상위 "# 제목" 은 문서 제목이라 별도 섹션으로 취급하지 않는다(원문 관례상 본문 없이 제목만)."""
    lines = text.split("\n")
    sections: list[tuple[str, list[str]]] = []
    current_heading, current_body = None, []
    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((current_heading, current_body))
            current_heading = line[3:].strip()
            current_body = []
        elif line.startswith("# ") and current_heading is None:
            continue  # 문서 최상위 제목 줄은 스킵
        else:
            if current_heading is not None:
                current_body.append(line)
    if current_heading is not None:
        sections.append((current_heading, current_body))
    return [(h, "\n".join(b).strip()) for h, b in sections if "\n".join(b).strip()]


def plan_migration(kb_dir: Path) -> list[dict]:
    plan = []
    for md_file in sorted(kb_dir.glob("*.md")):
        for heading, body in split_by_headers(md_file.read_text(encoding="utf-8")):
            source_id = f"legacy:{md_file.stem}:{hashlib.sha1(heading.encode()).hexdigest()[:10]}"
            plan.append({"file": md_file.name, "heading": heading, "body": body, "source_id": source_id})
    return plan


def write_inbox_note(vault: Path, item: dict) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_heading = "".join(c if c.isalnum() or c in " _-" else "_" for c in item["heading"])[:60].strip()
    # source_id 전체(파일명+제목 해시 조합)를 다시 해시해 파일명에 넣는다 — 같은 초(second)에 여러
    # 섹션을 쓸 때 제목이 같으면(예: 여러 파일에 공통인 "관련 문서" 섹션) ts+제목만으로는 파일명이
    # 충돌해 먼저 쓴 게 덮어써진다. source_id의 마지막 세그먼트(제목 해시)만 쓰면 서로 다른 파일의
    # 같은 제목 섹션끼리 또 충돌하므로(1차 수정에서 놓쳤던 부분), source_id 전체를 해시해야 한다
    # (2026-08-13 실제 마이그레이션 1차 실행에서 48개 중 9개가 이렇게 유실된 것을 확인하고 수정함).
    digest = hashlib.sha1(item["source_id"].encode()).hexdigest()[:10]
    path = vault / "00_Inbox" / f"{ts}_legacy_{digest}_{safe_heading}.md"
    fm = {
        "source": "legacy_kb",
        "source_id": item["source_id"],
        "date": datetime.now(timezone.utc).isoformat(),
        "raw": True,
        "status": "pending",
    }
    kb_lib.write_note(path, fm, f"# {item['heading']}\n\n(출처: 경영전략실_지식베이스/{item['file']})\n\n{item['body']}")
    return path


def _selftest() -> None:
    import tempfile

    sample = "# 문서 제목\n\n소개 문단\n\n## 섹션 A\n섹션 A 내용\n두번째 줄\n\n## 섹션 B\n섹션 B 내용\n"
    sections = split_by_headers(sample)
    assert [h for h, _ in sections] == ["섹션 A", "섹션 B"], sections
    assert sections[0][1] == "섹션 A 내용\n두번째 줄"
    assert sections[1][1] == "섹션 B 내용"

    with tempfile.TemporaryDirectory() as td:
        kb_dir = Path(td) / "kb"
        kb_dir.mkdir()
        (kb_dir / "01_예시.md").write_text(sample, encoding="utf-8")
        plan = plan_migration(kb_dir)
        assert len(plan) == 2, plan
        assert plan[0]["source_id"].startswith("legacy:01_예시:")

        vault = Path(td) / "vault"
        (vault / "00_Inbox").mkdir(parents=True)
        path = write_inbox_note(vault, plan[0])
        fm, body = kb_lib.read_note(path)
        assert fm["source"] == "legacy_kb" and fm["status"] == "pending"
        assert "섹션 A 내용" in body

        # 회귀 테스트: 서로 다른 파일의 같은 제목("관련 문서" 등) 섹션이 같은 초에 처리돼도
        # 파일명이 충돌해 덮어써지면 안 된다(2026-08-13 실제 마이그레이션에서 48개 중 9개 유실됨).
        (kb_dir / "02_예시.md").write_text(sample, encoding="utf-8")
        plan2 = plan_migration(kb_dir)
        same_heading_items = [p for p in plan2 if p["heading"] == "섹션 A"]
        assert len(same_heading_items) == 2  # 01_예시.md, 02_예시.md 둘 다 "섹션 A"를 가짐
        paths = {str(write_inbox_note(vault, item)) for item in same_heading_items}
        assert len(paths) == 2, f"파일명 충돌 발생: {paths}"

    print("OK: migrate_existing_kb selftest passed (원본 파일은 이 테스트에서도 건드리지 않음)")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault")
    parser.add_argument("--kb-dir")
    parser.add_argument("--execute", action="store_true", help="실제로 Inbox에 쓴다. 없으면 dry-run(계획만 출력)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not args.vault or not args.kb_dir:
        parser.error("--vault 와 --kb-dir 는 --selftest 가 아닐 때 필수")

    plan = plan_migration(Path(args.kb_dir))
    print(f"계획: {len(plan)}개 섹션을 00_Inbox에 raw 노트로 생성 예정 (원본 파일은 수정하지 않음)")
    for item in plan:
        print(f"  - [{item['file']}] {item['heading']} ({len(item['body'])}자)")

    if not args.execute:
        print("\n--execute 없이 실행됨 → 아무것도 쓰지 않았습니다(dry-run). 검토 후 --execute로 재실행하세요.")
        return 0

    vault = Path(args.vault)
    written = [str(write_inbox_note(vault, item)) for item in plan]
    print(f"\n{len(written)}개 Inbox 노트 생성 완료. 다음 note-structurer 배치가 분류를 진행합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
