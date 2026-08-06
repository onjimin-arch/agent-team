#!/usr/bin/env python3
"""Git pre-commit 게이트: 대시보드 레지스트리 이중 관리 파일 동기화 검증.

`.claude/configs/team-config.yaml` (external_data_sources.dashboards.*) 와
`.claude/skills/dept-dashboard-reader/SKILL.md` (레지스트리 표) 는 사내 부서 대시보드의
base_url/key_env/ca_cert 등 동일한 인프라 정보를 중복 보유한다. 한쪽만 바뀐 채 커밋되면
두 파일이 서로 다른 사실을 가리키게 되어 조용히 낡는다 — 이 스크립트는 그 상태를 막는다.

YAML/Markdown 파서를 쓰지 않는다. `base_url|key_env|ca_cert|note` 토큰은 team-config.yaml
전체에서 external_data_sources.dashboards.* 블록에만 등장하고(grep으로 확인됨), 레지스트리
표는 SKILL.md 안의 유일한 마크다운 표라서 `|`로 시작하는 줄만 봐도 충분하다.
`scripts/validate_artifact.py`와 동일하게 정규식 기반, 외부 의존성 없음(Python stdlib만 사용).

종료 코드: 동기화 문제 없음(또는 검사 대상 아님) 0 / 한쪽만 변경됨 1.
우회: `git commit --no-verify` (git 기본 기능 — 이 스크립트가 별도 플래그를 두지 않는다).
"""
from __future__ import annotations

import re
import subprocess
import sys

YAML_PATH = ".claude/configs/team-config.yaml"
SKILL_PATH = ".claude/skills/dept-dashboard-reader/SKILL.md"

_YAML_SIGNAL_RE = re.compile(r"\b(base_url|key_env|ca_cert|note)\s*:")


def _run(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout


def staged_files() -> set[str]:
    out = _run(["git", "diff", "--cached", "--name-only"])
    return set(out.splitlines())


def changed_lines(path: str) -> list[str]:
    """스테이징된 diff의 +/- 본문 줄만 반환 (헤더 줄 제외)."""
    out = _run(["git", "diff", "--cached", "-U0", "--", path])
    lines = []
    for line in out.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+") or line.startswith("-"):
            lines.append(line[1:])
    return lines


def yaml_touched_registry() -> bool:
    return any(_YAML_SIGNAL_RE.search(l) for l in changed_lines(YAML_PATH))


def skill_touched_registry() -> bool:
    return any(l.strip().startswith("|") for l in changed_lines(SKILL_PATH))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    files = staged_files()
    yaml_hit = YAML_PATH in files and yaml_touched_registry()
    skill_hit = SKILL_PATH in files and skill_touched_registry()

    if yaml_hit != skill_hit:
        touched, other = (YAML_PATH, SKILL_PATH) if yaml_hit else (SKILL_PATH, YAML_PATH)
        print(
            f"""
[pre-commit] 대시보드 레지스트리 동기화 확인 필요
  변경됨:     {touched}
  변경 안 됨: {other}

두 파일은 사내 대시보드(base_url/key_env/ca_cert/note)를 함께 관리합니다.
한쪽만 바뀌면 서로 다른 사실을 가리키게 됩니다 — 같은 커밋에 두 파일을 함께 반영하세요.

정말로 한쪽만 바꾸는 게 맞다면(오타 수정, 서식 변경 등 사실관계와 무관한 변경):
  git commit --no-verify
""".strip(),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
