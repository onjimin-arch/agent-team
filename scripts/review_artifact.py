#!/usr/bin/env python3
"""격리된 member-reviewer 실행기 (Phase 3 리뷰 격리 보장).

기존 문제: CLAUDE.md 는 "Agent 도구로 member-reviewer 서브에이전트를 실행하라"고 지시했지만
- Claude Code 세션에는 `member-reviewer` 라는 subagent_type 이 등록되어 있지 않고
- 실제 프로덕션 실행 경로(slack-bridge/agent_runner.py)는 `opencode run` 단일 프로세스이므로
같은 컨텍스트 안에서 팀장이 "리뷰어인 척" 자기 검토를 하고 있을 위험이 있었다.

이 스크립트는 리뷰를 **완전히 별도의 OS 프로세스**로 분리해 진짜 격리를 보장한다:
1. 임시 디렉터리를 만들어 그 안에서만 서브프로세스를 실행한다 (cwd 격리 —
   리뷰어가 실수로라도 plan.md·다른 멤버 산출물을 탐색할 수 없다).
2. 프롬프트에는 member-reviewer/AGENT.md 전문 + 대상 아티팩트 본문 + 스펙 +
   task_type + 한 줄 요약만 인라인으로 포함한다 (그 외 컨텍스트 전달 안 함).
3. 서브프로세스 종료 후 stdout 에서 "### Verdict: APPROVE|EDIT|REASSIGN" 를 파싱한다.

사용 예:
    python scripts/review_artifact.py \\
        --artifact output/slug/member-alpha/analysis-report.md \\
        --sections "개요,분석 결과,결론" \\
        --task-type research-report \\
        --task-summary "2026년 국내 전기차 시장 리서치" \\
        --out output/slug/member-alpha/.review-verdict.md

종료 코드: APPROVE=0 / EDIT=2 / REASSIGN=3 / 파싱실패·실행오류=1
환경변수:
    REVIEWER_CLI    (기본 "opencode") — 서브프로세스로 실행할 CLI 바이너리
    REVIEWER_MODEL  (기본 $AGENT_MODEL 또는 "claude-sonnet-4-6")
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ANSI_RE = re.compile(r"\x1b(?:\[[0-9;]*[mGKHFJ]|\][^\x07]*\x07|[^\[])")
_VERDICT_RE = re.compile(r"###\s*Verdict:\s*(APPROVE|EDIT|REASSIGN)", re.IGNORECASE)
_TIMEOUT_MARKER = "###REVIEW_TIMEOUT###"

_EXIT_CODE = {"APPROVE": 0, "EDIT": 2, "REASSIGN": 3}

_REPO_ROOT = Path(__file__).resolve().parent.parent
_REVIEWER_AGENT_MD = _REPO_ROOT / ".claude" / "agents" / "member-reviewer" / "AGENT.md"


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def build_prompt(reviewer_spec: str, artifact_content: str, artifact_name: str,
                  sections: list[str], task_type: str, task_summary: str) -> str:
    sections_block = "\n".join(f"- {s}" for s in sections) if sections else "(지정된 필수 섹션 없음)"
    return f"""{reviewer_spec}

---

## 리뷰 대상

**Artifact 파일명**: {artifact_name}
**Task Type**: {task_type}
**Task Summary**: {task_summary}

**필수 섹션 (required_sections)**:
{sections_block}

## Artifact 전문

{artifact_content}

---

위 Review Criteria 와 Output Format 을 그대로 따라 판정을 반환하세요.
지금 이 프롬프트에 없는 정보(작성 지시, plan.md, 다른 멤버 산출물)는 존재하지 않는다고 가정하고,
파일을 새로 찾아 읽으려 하지 마세요."""


def run_isolated(prompt: str, cli: str, model: str, timeout_sec: int = 600) -> str:
    """격리된 임시 디렉터리(cwd)에서 리뷰 서브프로세스를 실행하고 stdout 전체를 반환.

    타임아웃 시 이전엔 TimeoutExpired 가 그대로 전파되어 스크립트 전체가 크래시했다
    (`.review-verdict.md` 도 못 만들고, exit 1 로 정리되지도 못함). 여기서 잡아서
    지금까지 나온 부분 출력(있다면)을 살리고 _TIMEOUT_MARKER 로 표시해 반환한다."""
    tmp_dir = tempfile.mkdtemp(prefix="review-artifact-")
    try:
        cmd = [cli, "run", "--dangerously-skip-permissions", "--model", model, prompt]
        try:
            proc = subprocess.run(
                cmd,
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_sec,
            )
        except subprocess.TimeoutExpired as e:
            partial = (e.stdout or "") + ("\n" + e.stderr if e.stderr else "")
            return _TIMEOUT_MARKER + "\n" + _strip_ansi(partial)
        return _strip_ansi(proc.stdout + ("\n" + proc.stderr if proc.returncode != 0 else ""))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True, help="리뷰할 아티팩트 파일 경로")
    parser.add_argument("--sections", default="", help="콤마 구분 필수 섹션명")
    parser.add_argument("--task-type", default="", help="task type (예: research-report)")
    parser.add_argument("--task-summary", default="", help="한 줄 task 요약")
    parser.add_argument("--out", default="", help="전체 리뷰 텍스트를 저장할 파일 경로 (선택)")
    parser.add_argument("--cli", default=os.environ.get("REVIEWER_CLI", "opencode"))
    parser.add_argument(
        "--model",
        default=os.environ.get("REVIEWER_MODEL") or os.environ.get("AGENT_MODEL", "claude-sonnet-4-6"),
    )
    parser.add_argument(
        "--timeout-sec", type=int, default=int(os.environ.get("REVIEWER_TIMEOUT_SEC", "600")),
    )
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    if not artifact_path.exists():
        print(f'{{"error": "artifact_not_found", "path": "{args.artifact}"}}')
        return 1
    if not _REVIEWER_AGENT_MD.exists():
        print(f'{{"error": "reviewer_agent_md_not_found", "path": "{_REVIEWER_AGENT_MD}"}}')
        return 1

    reviewer_spec = _REVIEWER_AGENT_MD.read_text(encoding="utf-8")
    artifact_content = artifact_path.read_text(encoding="utf-8", errors="replace")
    sections = [s.strip() for s in args.sections.split(",") if s.strip()]

    model = args.model if "/" in args.model else f"anthropic/{args.model}"
    prompt = build_prompt(reviewer_spec, artifact_content, artifact_path.name, sections,
                          args.task_type, args.task_summary)

    output = run_isolated(prompt, args.cli, model, timeout_sec=args.timeout_sec)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")

    if output.startswith(_TIMEOUT_MARKER):
        print(
            f'{{"verdict": null, "error": "review_timeout", "timeout_sec": {args.timeout_sec}, '
            f'"out_saved": {str(bool(args.out)).lower()}}}'
        )
        return 1

    match = _VERDICT_RE.search(output)
    if not match:
        print(f'{{"verdict": null, "error": "no_verdict_parsed", "out_saved": {str(bool(args.out)).lower()}}}')
        return 1

    verdict = match.group(1).upper()
    print(f'{{"verdict": "{verdict}", "artifact": "{artifact_path.as_posix()}", "out_saved": {str(bool(args.out)).lower()}}}')
    return _EXIT_CODE[verdict]


if __name__ == "__main__":
    sys.exit(main())
