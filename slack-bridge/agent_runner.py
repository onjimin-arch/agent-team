"""팀장 프로토콜(CLAUDE.md) 실행 러너 — Claude Agent SDK 기반.

Slack 봇이 백그라운드 스레드에서 `run_team_lead()` 를 호출한다.
SDK 의 `query()` 를 이용해 CLAUDE.md 팀장 지침을 따르게 하고,
Phase 1~4 의 진행 상황을 `notify` 콜백으로 Slack 에 중계한다.

B 플로우(중단+재시작) 지원:
- `cancel_event` 가 set 되면 async 루프를 빠져나와 generator 를 정리한다.
- 같은 슬러그에 대해 `follow_up=True` 로 재호출하면 기존 산출물을
  읽고 후속 지시를 처리하는 프롬프트가 전달된다.
"""
from __future__ import annotations

import asyncio
import os
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
- Phase 5 Slack payload: `output/{slug}/slack-notification.json` (아래 Phase 5 규칙 참조)

진행 규칙:
- CLAUDE.md 의 팀장 프로토콜 및 `.claude/configs/team-config.yaml` 의 멤버 정의를 그대로 따릅니다.
- 멤버 역할을 수행할 때는 해당 멤버의 AGENT.md 를 먼저 읽습니다.
- Phase 전환 시점마다 `Phase {{N}} 시작:` 으로 시작하는 짧은 한 줄 로그를 출력합니다.
- 허용 도구: `Read/Write/Edit/Glob/Grep` + `Bash` (curl 용) + Notion MCP (`notion-search`/`notion-fetch`/`notion-create-pages`/`notion-update-page`). WebFetch/WebSearch 는 이 환경에서 비허용.

Phase 5 전체 실행:
- **5-1 Notion**: `notion-create-pages` 로 team-config.yaml 의 `data_source_id` 에 페이지 생성 (CLAUDE.md 규칙 준수). 반환된 Notion URL 을 메모.
- **5-2 Slack**:
  - `output/{slug}/slack-notification.json` 을 CLAUDE.md Phase 5-2 Block Kit 템플릿에 맞춰 작성 (context 비고: `· 최초 실행`). Notion URL 이 있으면 링크 블록 포함.
  - `Bash` 로 `webhook_file` 을 읽어 `curl -s -X POST -H "Content-Type: application/json; charset=utf-8" --data-binary @output/{slug}/slack-notification.json <webhook_url>` 전송. 절대 인라인 `--data` 금지.
- slack-bridge 는 위 JSON 을 읽어 **지시받은 DM/스레드에도** 같은 Block Kit 을 포스팅합니다 — 즉 webhook 채널 + 지시 스레드 양쪽에 뜹니다.
- `review-log.md` 의 "Distribution" 섹션에 각 엔드포인트 성공/실패/URL/시각 기록.
"""

_WORKSPACE_HINT_FOLLOWUP = """
## 활성 워크스페이스 (런타임 주입 · 후속 지시 모드)
현재 활성 워크스페이스 슬러그: `{slug}`
**기존 산출물이 이미 존재하는 워크스페이스입니다.**

아래 순서로 진행하세요:
1. `output/{slug}/plan.md`, `output/{slug}/review-log.md`, 그리고 `output/{slug}/` 하위 멤버별 폴더 및 `final/` 을 먼저 읽어 현재 상태를 파악합니다.
2. 사용자의 후속 지시(아래 프롬프트에 명시됨)가 기존 계획의 어느 부분에 해당하는지 판단합니다 — 특정 멤버 재작업, 새 관점 추가, 최종 보고서 수정 등.
3. 필요한 범위만 수정합니다. 기존 파일은 가능하면 덮어쓰기보다 **보강** 하고, 부득이한 경우에도 관련 섹션만 교체합니다.
4. 변경 내역을 `output/{slug}/review-log.md` 하단에 "Follow-up ({timestamp})" 섹션으로 추가 기록합니다.
5. 최종 산출물에 반영이 필요하면 `output/{slug}/final/final-artifact.md` 를 업데이트합니다.
6. **Phase 5 재실행** — 최신 상태 기준으로 배포 결과물을 갱신.
   - Notion: `notion-search` 로 기존 페이지(제목에 슬러그/주제 포함)를 찾아 `notion-update-page` 로 본문을 최신화. 찾지 못한 경우에만 `notion-create-pages`.
   - Slack payload: `output/{slug}/slack-notification.json` 을 재작성 (CLAUDE.md Phase 5-2 Block Kit 템플릿, context 비고 = `· 후속 지시 반영 ({timestamp})`). Notion 링크가 바뀌지 않았으면 동일 URL 유지.
   - webhook 재전송: `Bash` + `curl --data-binary @...` 로 위 JSON 재전송.
7. `review-log.md` 의 "Distribution" 섹션에 "Follow-up ({timestamp}) — Notion 갱신 / Slack 재전송 / bridge 포스팅" 한 줄 append.

제약:
- 새 워크스페이스를 만들지 않습니다. 슬러그는 위와 동일하게 유지. Notion 도 **같은 페이지**를 업데이트.
- 전체 재실행이 필요할 만큼 지시가 크면, 변경 범위를 먼저 사용자에게 보고하는 한 줄을 출력한 뒤 진행합니다.
- 허용 도구: `Read/Write/Edit/Glob/Grep` + `Bash` + Notion MCP (`notion-search`/`notion-fetch`/`notion-create-pages`/`notion-update-page`). WebFetch/WebSearch 는 비허용.
"""

_NOTIFY_COOLDOWN = 2.5  # 텍스트 블록 알림 최소 간격(초)
_CANCEL_POLL_INTERVAL = 0.5


class _Cancelled(Exception):
    """cancel_event 가 set 되어 내부적으로 루프를 빠져나갈 때 쓰는 센티넬."""


def run_team_lead(
    topic_slug: str,
    task_description: str,
    *,
    notify: Callable[[str], None],
    request_approval: Callable[[str, dict], str] | None = None,
    cancel_event: threading.Event | None = None,
    follow_up: bool = False,
) -> dict[str, Any]:
    """팀장 프로토콜 실행 (동기 wrapper).

    follow_up=True 면 기존 워크스페이스에 대한 후속 지시 처리 모드로 동작.
    cancel_event 가 set 되면 진행 중 asyncio generator 를 종료하고
    status="cancelled" 로 반환.
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

    result = asyncio.run(
        _run_async(topic_slug, task_description, team_root, notify, cancel_event, follow_up)
    )

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


async def _run_async(
    topic_slug: str,
    task_description: str,
    team_root: Path,
    notify: Callable[[str], None],
    cancel_event: threading.Event | None,
    follow_up: bool,
) -> dict[str, Any]:
    from claude_agent_sdk import ClaudeAgentOptions, query

    model = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")

    stderr_log: list[str] = []

    def _capture_stderr(line: str) -> None:
        stderr_log.append(line)
        print(f"[sdk-stderr] {line}", flush=True)

    hint_template = _WORKSPACE_HINT_FOLLOWUP if follow_up else _WORKSPACE_HINT_INITIAL
    hint = hint_template.format(
        slug=topic_slug,
        timestamp=time.strftime("%Y-%m-%d %H:%M"),
    )

    options = ClaudeAgentOptions(
        cwd=str(team_root),
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": hint,
        },
        allowed_tools=[
            "Read", "Write", "Edit", "Glob", "Grep",
            # Phase 5-2 Slack webhook 용 curl
            "Bash",
            # Phase 5-1 Notion 저장/갱신 (claude.ai 커넥터)
            "mcp__claude_ai_Notion__notion-search",
            "mcp__claude_ai_Notion__notion-fetch",
            "mcp__claude_ai_Notion__notion-create-pages",
            "mcp__claude_ai_Notion__notion-update-page",
        ],
        permission_mode="bypassPermissions",
        model=model,
        max_turns=60,
        setting_sources=["user", "project"],
        stderr=_capture_stderr,
    )

    if follow_up:
        prompt = (
            f"기존 워크스페이스에 후속 지시가 접수되었습니다.\n\n"
            f"**워크스페이스 슬러그**: `{topic_slug}`\n"
            f"**후속 지시**: {task_description}\n\n"
            f"시스템 프롬프트의 '후속 지시 모드' 절차를 따르세요. "
            f"먼저 기존 산출물을 읽고, 변경 범위를 판단한 뒤 필요한 파일만 수정합니다."
        )
    else:
        prompt = (
            f"업무 요청이 접수되었습니다.\n\n"
            f"**업무 설명**: {task_description}\n"
            f"**워크스페이스 슬러그**: `{topic_slug}`\n\n"
            f"CLAUDE.md 의 팀장 프로토콜에 따라 Phase 1(기획) → 2(실행) → 3(리뷰) → 4(통합) 를 순서대로 수행하세요. "
            f"최종 산출물은 `output/{topic_slug}/final/final-artifact.md` 로 저장합니다."
        )

    state = {"last_notify": 0.0, "cost": 0.0, "turns": 0}
    artifacts: list[str] = []

    async def _cancel_watcher() -> None:
        """cancel_event 를 주기적으로 폴링 — set 되면 task 를 취소한다."""
        if not cancel_event:
            return
        while not cancel_event.is_set():
            await asyncio.sleep(_CANCEL_POLL_INTERVAL)
        raise _Cancelled()

    try:
        async def _drive() -> None:
            async for message in query(prompt=prompt, options=options):
                _handle_message(message, team_root, artifacts, state, notify)
                if cancel_event and cancel_event.is_set():
                    raise _Cancelled()

        drive_task = asyncio.create_task(_drive())
        watch_task = asyncio.create_task(_cancel_watcher())

        done, pending = await asyncio.wait(
            {drive_task, watch_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        for p in pending:
            p.cancel()
        # 취소 전파가 완료될 때까지 정리
        for p in pending:
            try:
                await p
            except (asyncio.CancelledError, _Cancelled):
                pass
        for d in done:
            exc = d.exception()
            if isinstance(exc, _Cancelled):
                notify("⏹️ 현재 실행을 중단했습니다. 후속 지시를 준비합니다…")
                return {
                    "cost_usd": round(state["cost"], 4),
                    "turns": state["turns"],
                    "artifacts": artifacts,
                    "cancelled": True,
                }
            if exc:
                raise exc
    except _Cancelled:
        notify("⏹️ 현재 실행을 중단했습니다.")
        return {
            "cost_usd": round(state["cost"], 4),
            "turns": state["turns"],
            "artifacts": artifacts,
            "cancelled": True,
        }
    except Exception as e:
        tail = "\n".join(stderr_log[-30:]) if stderr_log else "(stderr 비어 있음)"
        raise RuntimeError(f"{type(e).__name__}: {e}\n--- CLI stderr ---\n{tail}") from e

    return {
        "cost_usd": round(state["cost"], 4),
        "turns": state["turns"],
        "artifacts": artifacts,
        "cancelled": False,
    }


def _handle_message(message, team_root: Path, artifacts: list[str], state: dict, notify: Callable[[str], None]) -> None:
    msg_type = type(message).__name__

    if msg_type == "ResultMessage":
        state["cost"] = float(getattr(message, "total_cost_usd", 0.0) or 0.0)
        state["turns"] = int(getattr(message, "num_turns", 0) or 0)
        return

    if msg_type != "AssistantMessage":
        return

    for block in getattr(message, "content", []):
        if getattr(block, "name", None) == "Write":
            inp = getattr(block, "input", {}) or {}
            path = str(inp.get("file_path", "")).replace("\\", "/")
            root_str = str(team_root).replace("\\", "/")
            rel = path[len(root_str):].lstrip("/") if path.startswith(root_str) else path
            if rel:
                artifacts.append(rel)
                notify(f"📝 파일 생성: `{rel}`")
            continue

        text = getattr(block, "text", None)
        if not text:
            continue
        now = time.monotonic()
        if now - state["last_notify"] < _NOTIFY_COOLDOWN:
            continue
        first_line = text.strip().splitlines()[0].strip()
        if not first_line or first_line.startswith("```"):
            continue
        notify(f"💭 {first_line[:240]}")
        state["last_notify"] = now
