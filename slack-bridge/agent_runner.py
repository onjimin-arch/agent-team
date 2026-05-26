"""팀장 프로토콜(CLAUDE.md) 실행 러너 — opencode CLI 기반.

Slack 봇이 백그라운드 스레드에서 `run_team_lead()` 를 호출한다.
`opencode run` 을 subprocess 로 실행하고, stdout 을 실시간으로
읽어 `notify` 콜백으로 Slack 에 중계한다.

B 플로우(중단+재시작) 지원:
- `cancel_event` 가 set 되면 subprocess 를 terminate 한다.
- 같은 슬러그에 대해 `follow_up=True` 로 재호출하면 기존 산출물을
  읽고 후속 지시를 처리하는 프롬프트가 전달된다.
"""
from __future__ import annotations

import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable


_WORKSPACE_HINT_INITIAL = """
## 활성 워크스페이스 (런타임 주입)
현재 활성 워크스페이스 슬러그: `{slug}`
모든 산출물은 `output/{slug}/` 하위에만 저장합니다.

- Phase 1 계획: `output/{slug}/plan.md`
- Phase 2 멤버 산출물: `output/{slug}/{{member-name}}/`
- Phase 3 리뷰 로그: `output/{slug}/review-log.md`
- Phase 4 최종 산출물: `output/{slug}/final/final-artifact.md`
- Phase 5 Slack payload: `output/{slug}/slack-notification.json`

진행 규칙:
- CLAUDE.md 의 팀장 프로토콜 및 `.claude/configs/team-config.yaml` 의 멤버 정의를 그대로 따릅니다.
- Phase 전환 시점마다 `Phase {{N}} 시작:` 으로 시작하는 짧은 한 줄 로그를 출력합니다.
"""

_WORKSPACE_HINT_FOLLOWUP = """
## 활성 워크스페이스 (런타임 주입 · 후속 지시 모드)
현재 활성 워크스페이스 슬러그: `{slug}`
**기존 산출물이 이미 존재하는 워크스페이스입니다.**

아래 순서로 진행하세요:
1. `output/{slug}/plan.md`, `output/{slug}/review-log.md`, 하위 멤버 폴더 및 `final/` 을 먼저 읽어 현재 상태를 파악합니다.
2. 후속 지시가 기존 계획의 어느 부분에 해당하는지 판단합니다.
3. 필요한 범위만 수정합니다. 기존 파일은 가능하면 보강하고 관련 섹션만 교체합니다.
4. 변경 내역을 `output/{slug}/review-log.md` 하단에 "Follow-up ({timestamp})" 섹션으로 추가 기록합니다.
5. 최종 산출물에 반영이 필요하면 `output/{slug}/final/final-artifact.md` 를 업데이트합니다.
"""

_NOTIFY_COOLDOWN = 2.5


def run_team_lead(
    topic_slug: str,
    task_description: str,
    *,
    notify: Callable[[str], None],
    request_approval: Callable[[str, dict], str] | None = None,
    cancel_event: threading.Event | None = None,
    follow_up: bool = False,
) -> dict[str, Any]:
    """팀장 프로토콜 실행.

    follow_up=True 면 기존 워크스페이스에 대한 후속 지시 처리 모드로 동작.
    cancel_event 가 set 되면 subprocess 를 terminate 하고 status="cancelled" 로 반환.
    """
    team_root = Path(os.environ["TEAM_ROOT"])
    workspace = team_root / "output" / topic_slug
    workspace.mkdir(parents=True, exist_ok=True)
    (team_root / "output" / ".active-workspace").write_text(topic_slug, encoding="utf-8")

    if follow_up:
        notify(f"🔁 후속 지시 처리 시작 — 워크스페이스 `output/{topic_slug}/` 이어서 진행.")
    else:
        notify(f"📂 워크스페이스: `output/{topic_slug}/`")
        notify("🤖 팀장 에이전트 실행 — Phase 1~4 시작.")

    result = _run_subprocess(topic_slug, task_description, team_root, notify, cancel_event, follow_up)

    cancelled = bool(cancel_event and cancel_event.is_set())
    final_path = workspace / "final" / "final-artifact.md"

    if cancelled:
        status = "cancelled"
    elif final_path.exists():
        status = "completed"
    else:
        status = "partial"

    return {
        "status": status,
        "final_path": str(final_path) if final_path.exists() else None,
        "follow_up": follow_up,
        **result,
    }


def _run_subprocess(
    topic_slug: str,
    task_description: str,
    team_root: Path,
    notify: Callable[[str], None],
    cancel_event: threading.Event | None,
    follow_up: bool,
) -> dict[str, Any]:
    model = os.environ.get("AGENT_MODEL", "anthropic/claude-sonnet-4-6")
    # opencode 모델 형식: "anthropic/..." — claude CLI 형식이면 변환
    if "/" not in model:
        model = f"anthropic/{model}"

    hint_template = _WORKSPACE_HINT_FOLLOWUP if follow_up else _WORKSPACE_HINT_INITIAL
    hint = hint_template.format(
        slug=topic_slug,
        timestamp=time.strftime("%Y-%m-%d %H:%M"),
    )

    if follow_up:
        prompt = (
            f"{hint}\n\n"
            f"기존 워크스페이스에 후속 지시가 접수되었습니다.\n\n"
            f"**워크스페이스 슬러그**: `{topic_slug}`\n"
            f"**후속 지시**: {task_description}\n\n"
            f"위 후속 지시 모드 절차를 따르세요. 먼저 기존 산출물을 읽고, "
            f"변경 범위를 판단한 뒤 필요한 파일만 수정합니다."
        )
    else:
        prompt = (
            f"{hint}\n\n"
            f"업무 요청이 접수되었습니다.\n\n"
            f"**업무 설명**: {task_description}\n"
            f"**워크스페이스 슬러그**: `{topic_slug}`\n\n"
            f"CLAUDE.md 의 팀장 프로토콜에 따라 Phase 1(기획) → 2(실행) → 3(리뷰) → 4(통합) 를 "
            f"순서대로 수행하세요. 최종 산출물은 `output/{topic_slug}/final/final-artifact.md` 로 저장합니다."
        )

    cmd = ["opencode", "run", "--dangerously-skip-permissions", "--model", model, prompt]

    artifacts: list[str] = []
    last_notify = 0.0

    proc = subprocess.Popen(
        cmd,
        cwd=str(team_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        for line in proc.stdout:
            line = line.rstrip()
            if not line:
                continue

            if cancel_event and cancel_event.is_set():
                proc.terminate()
                notify("⏹️ 현재 실행을 중단했습니다. 후속 지시를 준비합니다…")
                break

            # 파일 생성 감지
            if "output/" in line and any(x in line for x in ["Writing", "Created", "✓", "write"]):
                artifacts.append(line[:120])

            # 진행 상황 Slack 중계 (쿨다운 적용)
            now = time.monotonic()
            if now - last_notify >= _NOTIFY_COOLDOWN:
                first_line = line.strip().splitlines()[0][:240]
                if first_line and not first_line.startswith("```"):
                    notify(f"💭 {first_line}")
                    last_notify = now

        proc.wait()
    except Exception:
        proc.terminate()
        raise

    return {
        "cost_usd": 0.0,
        "turns": 0,
        "artifacts": artifacts,
        "cancelled": bool(cancel_event and cancel_event.is_set()),
    }
