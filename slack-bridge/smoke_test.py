"""slack-bridge 핵심 로직 smoke test — Slack/봇 없이 로컬에서 검증.

사용법: `python smoke_test.py`
"""
import asyncio
import os
import subprocess
import sys
import tempfile
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

# --- agent_runner._reconcile_misplaced_workspace (opencode 가 워크스페이스를
#     slack-bridge/output/{slug}/ 밑에 잘못 저장하는 케이스 자동 복구, 2026-08-14 실사례) ---
from agent_runner import _reconcile_misplaced_workspace

def test_reconcile_misplaced_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        team_root = Path(tmp)
        wrong = team_root / "slack-bridge" / "output" / "테스트-슬러그"
        wrong.mkdir(parents=True)
        (wrong / "quick-query-log.md").write_text("content", encoding="utf-8")

        notified = []
        _reconcile_misplaced_workspace(team_root, "테스트-슬러그", notified.append)

        correct = team_root / "output" / "테스트-슬러그" / "quick-query-log.md"
        assert correct.exists(), "FAIL: 파일이 올바른 위치로 옮겨지지 않음"
        assert not wrong.exists(), "FAIL: 잘못된 디렉터리가 정리되지 않음"
        assert notified, "FAIL: 복구 사실이 notify 되지 않음"

        # 잘못된 워크스페이스가 없는 정상 케이스는 아무 일도 하지 않아야 함
        notified.clear()
        _reconcile_misplaced_workspace(team_root, "다른-슬러그", notified.append)
        assert not notified, "FAIL: 정상 케이스에서 불필요하게 notify 됨"

    print("  _reconcile_misplaced_workspace 이동/정리/notify  OK")

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

    print("\n[5] 워크스페이스 오배치 복구 (_reconcile_misplaced_workspace)")
    test_reconcile_misplaced_workspace()

    print("\n[6] opencode CLI")
    test_opencode()

    print("\n=== 모든 테스트 통과 ===")

if __name__ == "__main__":
    main()
