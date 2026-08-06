#!/usr/bin/env python3
"""Git pre-commit 리마인더(비차단): task-type ↔ 담당 member 매핑 동기화 알림.

task-type 별 담당 member 는 세 군데 이상에 흩어져 선언된다:
  1) .claude/configs/team-config.yaml 의 task.types[].triggers/members (인라인 배열)
  2) 각 .claude/agents/member-*/AGENT.md 의 "### {type} 전용 역할" 섹션
  3) CLAUDE.md 의 "사용 가능한 기본 type" 목록 + "Team Members Quick Reference" 표

이 매핑이 "정확히" 맞게 갱신됐는지는 기계적으로 검증할 수 없으므로(어느 AGENT.md 섹션이
"맞는" 곳인지, CLAUDE.md의 어느 줄이 관련 항목인지는 의미 판단이 필요) 이 스크립트는
check_dashboard_registry_sync.py와 달리 커밋을 막지 않는다 — 이번 커밋에서 위 세 지점 중
하나라도 건드렸으면 나머지 지점의 현재 줄 번호를 참고용으로 출력만 한다.

줄 번호는 하드코딩하지 않고 스테이징된 blob(git show :path)에서 매번 다시 계산한다 —
파일이 자라도 포인터가 낡지 않도록.

종료 코드: 항상 0 (비차단).
"""
from __future__ import annotations

import glob
import re
import subprocess
import sys

YAML_PATH = ".claude/configs/team-config.yaml"
CLAUDE_PATH = "CLAUDE.md"
AGENT_GLOB = ".claude/agents/member-*/AGENT.md"

_YAML_TYPES_RE = re.compile(r"(triggers|members)\s*:\s*\[")
_AGENT_HEADING_RE = re.compile(r"^###\s.*전용\s*역할")
_CLAUDE_TYPE_LIST_RE = re.compile(r"^-\s*`[a-z-]+`")
_CLAUDE_QUICKREF_ROW_RE = re.compile(r"^\|\s*member-")


def _run(args: list[str]) -> tuple[str, int]:
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout, result.returncode


def staged_files() -> list[str]:
    out, _ = _run(["git", "diff", "--cached", "--name-only"])
    return out.splitlines()


def changed_lines(path: str) -> list[str]:
    out, _ = _run(["git", "diff", "--cached", "-U0", "--", path])
    lines = []
    for line in out.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+") or line.startswith("-"):
            lines.append(line[1:])
    return lines


def staged_content_lines(path: str) -> list[str]:
    """이번 커밋에 반영될(스테이징된) 파일 전체 내용 — 최신 줄 번호 계산용."""
    out, code = _run(["git", "show", f":{path}"])
    return out.splitlines() if code == 0 else []


def find_lines(path: str, pattern: re.Pattern) -> list[int]:
    return [i + 1 for i, l in enumerate(staged_content_lines(path)) if pattern.search(l)]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    files = staged_files()
    touched: list[str] = []

    if YAML_PATH in files and any(_YAML_TYPES_RE.search(l) for l in changed_lines(YAML_PATH)):
        touched.append(YAML_PATH)

    agent_files = [f for f in files if re.match(r"\.claude/agents/member-.*/AGENT\.md$", f)]
    agent_hit = [f for f in agent_files if any(_AGENT_HEADING_RE.search(l) for l in changed_lines(f))]
    touched += agent_hit

    if CLAUDE_PATH in files and any(
        _CLAUDE_TYPE_LIST_RE.search(l) or _CLAUDE_QUICKREF_ROW_RE.search(l) for l in changed_lines(CLAUDE_PATH)
    ):
        touched.append(CLAUDE_PATH)

    if not touched:
        return 0

    print("[pre-commit] 참고: task-type ↔ member 매핑은 여러 곳에서 각각 선언됩니다 (자동 검증 아님):")
    print(f"  - {YAML_PATH}: {find_lines(YAML_PATH, _YAML_TYPES_RE)} (task.types[].triggers/members)")
    for f in sorted(glob.glob(AGENT_GLOB)):
        lines = find_lines(f, _AGENT_HEADING_RE)
        if lines:
            print(f"  - {f}: {lines} (### {{type}} 전용 역할)")
    print(
        f"  - {CLAUDE_PATH}: {find_lines(CLAUDE_PATH, _CLAUDE_TYPE_LIST_RE)} (기본 type 목록), "
        f"{find_lines(CLAUDE_PATH, _CLAUDE_QUICKREF_ROW_RE)} (Team Members Quick Reference)"
    )
    print(f"  이번 커밋에서 변경됨: {touched}")
    print("  다른 지점도 함께 갱신해야 하는지 확인하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
