#!/usr/bin/env python3
"""Windows 작업 스케줄러가 호출하는 단일 진입점. Claude Code 내장 cron 대신 OS 스케줄러를 쓰기로 한
결정(2026-08-13)의 구현 — `config/knowledge_pipeline.json`과 `.env`를 읽어 각 지식수집 스킬
스크립트를 실행한다.

작업 스케줄러 "프로그램/스크립트" 칸에는 python.exe가 아니라 **pythonw.exe**(창 없는 버전)로
등록한다 — 콘솔 창이 깜빡이는 걸 막기 위함(2026-08-13, docs/task_scheduler_setup.md 참고):
    pythonw C:\\...\\agent-team\\scripts\\run_scheduled.py --task notion-sync
    pythonw C:\\...\\agent-team\\scripts\\run_scheduled.py --task slack-sync
    pythonw C:\\...\\agent-team\\scripts\\run_scheduled.py --task file-watcher
    pythonw C:\\...\\agent-team\\scripts\\run_scheduled.py --task note-structurer

notion-sync/slack-sync/file-watcher는 LLM 없이 순수 스크립트라 여기서 바로 실행한다.
note-structurer는 분류 판단에 LLM이 필요하므로 `claude -p`(헤드리스)를 통해 Claude Code가
`.claude/skills/note-structurer/SKILL.md` 절차를 직접 수행하게 한다.

pythonw.exe는 콘솔이 없어 print()가 기록될 곳이 없으므로, 이 스크립트는 print 대신 로그 파일
(`output/knowledge-agent/scheduler_logs/YYYYMMDD.log`)에 결과를 남긴다. 자식 프로세스(notion_pull.py
등, 그리고 claude CLI)도 `CREATE_NO_WINDOW`로 띄워 콘솔 창이 전혀 뜨지 않게 한다.

등록 방법은 `docs/task_scheduler_setup.md` 참고. 이 스크립트 자체는 실행만 하고 작업을 새로 만들지는
않는다(`schtasks /create`는 별도).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[1]  # .../agent-team
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # 자식 프로세스도 콘솔 창 없이


def log(message: str) -> None:
    log_dir = _AGENT_TEAM_ROOT / "output" / "knowledge-agent" / "scheduler_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{date.today().isoformat()}.log"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def load_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and value:  # 빈 값(아직 안 채운 토큰)은 주입하지 않음 — 명확한 _missing 에러가 나게
            os.environ[key] = value


def load_config() -> dict:
    return json.loads((_AGENT_TEAM_ROOT / "config" / "knowledge_pipeline.json").read_text(encoding="utf-8"))


def _find_claude_cli() -> str:
    """Task Scheduler가 띄우는 pythonw.exe는 대화형 셸과 PATH가 달라 `claude`(확장자 없음)를
    CreateProcess로 못 찾는다(WinError 2) — npm 전역 설치 경로를 직접 뒤져 `.cmd`까지 확인한다."""
    found = shutil.which("claude") or shutil.which("claude.cmd")
    if found:
        return found
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        candidate = Path(appdata) / "npm" / "claude.cmd"
        if candidate.exists():
            return str(candidate)
    return "claude"  # 못 찾아도 이전 동작(PATH 의존) 유지 — 에러 메시지로 원인 파악 가능


def run(cmd: list[str], cwd: str | None = None) -> int:
    log("실행: " + " ".join(cmd))
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        creationflags=_CREATE_NO_WINDOW,
    )
    if result.stdout.strip():
        log("stdout: " + result.stdout.strip())
    if result.stderr.strip():
        log("stderr: " + result.stderr.strip())
    log(f"종료 코드: {result.returncode}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=["notion-sync", "slack-sync", "file-watcher", "note-structurer"])
    args = parser.parse_args()

    load_env(_AGENT_TEAM_ROOT / ".env")
    config = load_config()
    vault = config["vault_path"]
    skills = _AGENT_TEAM_ROOT / ".claude" / "skills"

    if args.task == "notion-sync":
        return run([sys.executable, str(skills / "notion-sync/scripts/notion_pull.py"),
                    "--vault", vault, "--whitelist", str(skills / "notion-sync/scripts/whitelist.json")])

    if args.task == "slack-sync":
        return run([sys.executable, str(skills / "slack-sync/scripts/slack_pull.py"),
                    "--vault", vault, "--config", str(skills / "slack-sync/scripts/filter_config.json")])

    if args.task == "file-watcher":
        drop_folder = Path(config["drop_folder"])
        drop_folder.mkdir(parents=True, exist_ok=True)
        return run([sys.executable, str(skills / "file-watcher/scripts/watch_inbox.py"),
                    "--watch-dir", str(drop_folder), "--vault", vault])

    if args.task == "note-structurer":
        prompt = (
            f"agent-team/.claude/skills/note-structurer/SKILL.md 절차를 그대로 따라 vault(경로: {vault})의 "
            f"00_Inbox에서 status:pending인 노트를 전부 처리하라(락 획득 -> 목록 조회 -> 각 노트 판단 -> "
            f"finalize -> 락 해제). pending 노트가 없으면 아무 것도 하지 않고 종료하라."
        )
        return run([_find_claude_cli(), "-p", prompt], cwd=str(_AGENT_TEAM_ROOT))

    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # pythonw는 콘솔이 없어 처리 안 된 예외가 그냥 사라진다 — 반드시 로그에 남긴다
        log(f"예외 발생: {type(e).__name__}: {e}")
        sys.exit(1)
