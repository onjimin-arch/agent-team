"""SDK 최소 smoke test — Slack/봇 없이 Claude Agent SDK 만 검증.

사용법: `python smoke_test.py`
"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


async def main():
    from claude_agent_sdk import ClaudeAgentOptions, query

    print(f"ANTHROPIC_API_KEY set: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
    print(f"Model: {os.environ.get('AGENT_MODEL', 'default')}")

    def on_stderr(line: str):
        print(f"[stderr] {line}")

    options = ClaudeAgentOptions(
        model=os.environ.get("AGENT_MODEL", "claude-sonnet-4-6"),
        max_turns=3,
        stderr=on_stderr,
    )

    print("--- Running simple query ---")
    try:
        async for msg in query(prompt="Say 'hello from SDK' in Korean.", options=options):
            t = type(msg).__name__
            if t == "AssistantMessage":
                for block in getattr(msg, "content", []):
                    text = getattr(block, "text", None)
                    if text:
                        print(f"[assistant] {text}")
            elif t == "ResultMessage":
                print(f"[result] cost={getattr(msg, 'total_cost_usd', 0)} turns={getattr(msg, 'num_turns', 0)}")
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
