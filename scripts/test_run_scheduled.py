"""run_scheduled.py 핵심 로직 self-check. 사용법: python scripts/test_run_scheduled.py"""
from run_scheduled import _find_claude_cli


def main() -> None:
    found = _find_claude_cli()
    assert found, "FAIL: _find_claude_cli()가 빈 값을 반환함"
    print(f"  _find_claude_cli() -> {found}  OK")


if __name__ == "__main__":
    main()
