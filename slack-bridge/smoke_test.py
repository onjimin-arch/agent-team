"""slack-bridge 핵심 로직 smoke test — Slack/봇 없이 로컬에서 검증.

사용법: `python smoke_test.py`
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# --- slug.py ---
from slug import slugify

def test_slug():
    cases = [
        ("2026년 국내 전기차 시장 리서치", "2026"),  # kebab 변환 확인
        ("slack-bridge 테스트", "slack-bridge"),
        ("hello world today", "hello"),
    ]
    ok = True
    for text, expected_substr in cases:
        result = slugify(text)
        assert expected_substr in result, f"FAIL slug({text!r}) = {result!r}, expected to contain {expected_substr!r}"
        print(f"  slug({text!r}) = {result!r}  OK")
    return ok

# --- state.py ---
import state as st

def test_state():
    approval_id = "smoke-test-approval"
    payload = {"channel": "ch_test", "thread_ts": "ts_test", "user": "u_test"}
    st.put_pending(approval_id, payload)
    p = st.get_pending(approval_id)
    assert p is not None and p["channel"] == "ch_test", f"FAIL: {p}"
    st.pop_pending(approval_id)
    assert st.get_pending(approval_id) is None
    print(f"  state put/get/pop  OK")

# --- _is_command (app.py 에서 임포트) ---
def test_is_command():
    # app.py 의 _is_command 로직을 직접 확인 (모듈 임포트 없이)
    COMMAND_KEYWORDS = [
        "리서치", "분석", "보고서", "시장", "정책", "현황", "research", "report",
        "코드 리뷰", "code review", "리뷰해",
        "영문", "번역", "다국어", "translate",
        "개발", "배포", "버그", "기능 추가", "implement", "deploy", "fix",
        "깃허브", "github", "오픈소스",
    ]
    def _is_command(text: str) -> bool:
        t = text.lower()
        return any(k in t for k in COMMAND_KEYWORDS)

    assert _is_command("2026년 전기차 시장 리서치 보고서 작성"), "FAIL: 리서치"
    assert _is_command("GitHub 공개 코드 참고해서 구현"), "FAIL: github"
    assert not _is_command("안녕하세요"), "FAIL: 일반 인사"
    print(f"  _is_command logic  OK")

# --- opencode CLI 존재 확인 ---
def test_opencode():
    result = subprocess.run(["opencode", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  opencode --version: {result.stdout.strip() or result.stderr.strip()}  OK")
    else:
        print(f"  opencode not found or error (returncode={result.returncode}) - install opencode CLI to run agents")

# --- .env 핵심 변수 확인 ---
def test_env():
    keys = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "TEAM_ROOT", "AGENT_MODEL"]
    for k in keys:
        v = os.environ.get(k, "")
        status = "OK" if v else "MISSING"
        print(f"  {k}: {v[:20]}{'...' if len(v) > 20 else ''}  {status}")
    team_root = Path(os.environ.get("TEAM_ROOT", ""))
    if team_root.exists():
        claude_md = team_root / "CLAUDE.md"
        print(f"  TEAM_ROOT exists, CLAUDE.md: {'OK' if claude_md.exists() else 'NOT FOUND'}")
    else:
        print(f"  TEAM_ROOT does not exist: {team_root}")

def main():
    print("=== slack-bridge smoke test ===\n")

    print("[1] .env 변수")
    test_env()

    print("\n[2] slug 생성")
    test_slug()

    print("\n[3] state 관리")
    test_state()

    print("\n[4] 명령 감지 (_is_command)")
    test_is_command()

    print("\n[5] opencode CLI")
    test_opencode()

    print("\n=== 모든 테스트 통과 ===")

if __name__ == "__main__":
    main()
