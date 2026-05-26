"""
agent-team 을 claude CLI 로 실행하고 결과를 반환한다.

사용 예시 (직접 테스트):
  python runner.py 2026년 전기차 시장 분석해줘
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AGENT_DIR = str(Path(__file__).parent.parent)
TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "600"))
MODEL = os.environ.get("AGENT_MODEL", "anthropic/claude-sonnet-4-6")
if "/" not in MODEL:
    MODEL = f"anthropic/{MODEL}"


def run_agent_task(task: str) -> str:
    slug = f"slack-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # [AUTO: slug] 접두사로 자동 모드 진입 (CLAUDE.md 자동 모드 규칙 적용)
    prompt = f"[AUTO: {slug}]\n새 작업\n\n{task}"

    try:
        proc = subprocess.run(
            ["opencode", "run", "--dangerously-skip-permissions", "--model", MODEL, prompt],
            cwd=AGENT_DIR,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        return f"⏰ 작업 시간 초과 ({TIMEOUT // 60}분). 복잡한 작업은 직접 실행해 주세요."
    except FileNotFoundError:
        return "❌ `claude` CLI 를 찾을 수 없습니다. PATH 설정을 확인해 주세요."
    except Exception as e:
        return f"❌ 실행 오류: {e}"

    # final-artifact.md 우선 반환
    final_path = Path(AGENT_DIR) / "output" / slug / "final" / "final-artifact.md"
    if final_path.exists():
        content = final_path.read_text(encoding="utf-8")
        truncated = content[:2800]
        suffix = "\n...(전체 결과는 output 폴더 참조)" if len(content) > 2800 else ""
        return f"✅ 작업 완료!\n\n```\n{truncated}{suffix}\n```"

    # 폴백: stdout 요약
    out = (proc.stdout or "").strip()
    if out:
        return f"✅ 완료\n\n{out[:2500]}"

    return "✅ 작업이 완료되었습니다. `output/" + slug + "/` 폴더에서 결과를 확인하세요."


if __name__ == "__main__":
    test_task = " ".join(sys.argv[1:]) or "테스트: 간단한 안녕하세요 인사말 작성"
    print(run_agent_task(test_task))
