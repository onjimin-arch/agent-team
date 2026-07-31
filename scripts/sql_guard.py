#!/usr/bin/env python3
"""SQL 쿼리가 SELECT-only 인지 검증하는 최선 노력(best-effort) 안전 가드.

member-alpha 가 부서 SQL 게이트웨이(구현 예정: `scripts/sql_read.py`)를 호출하기 전, 모든 쿼리는
이 스크립트의 `validate_select_only()` 검증을 통과해야 한다. 자세한 배경은
`.claude/skills/sql-reader/SKILL.md` 참조.

**중요 — 이 검증은 문자열 기반 최선 노력 검사이지 진짜 보안 경계가 아니다.** 실제 안전장치는
게이트웨이 쪽 DB 계정에 read-only 권한만 부여하는 것이다. 이 가드는 그 위에 얹는 추가 방어선으로,
실수로/의도치 않게 변경성 쿼리가 전송되는 것을 막는 용도다 — 우회 가능한 정교한 공격을 막는 용도로
설계되지 않았다.

외부 의존성 없음(stdlib `re`만 사용).

사용 예:
    python scripts/sql_guard.py --query "SELECT * FROM orders WHERE created_at > '2026-01-01'"
    # {"valid": true, "reason": "ok"}

    python scripts/sql_guard.py --query "DROP TABLE orders"
    # {"valid": false, "reason": "not_a_select_statement"}

출력: JSON {"valid": bool, "reason": str} (stdout). exit code: valid=0, invalid=1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

_COMMENT_LINE_RE = re.compile(r"--[^\n]*")
_COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_STRING_LITERAL_RE = re.compile(r"'(?:[^']|'')*'")

_FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE", "REPLACE", "CALL",
    "ATTACH", "DETACH", "VACUUM", "PRAGMA",
]


def _strip_comments(query: str) -> str:
    stripped = _COMMENT_BLOCK_RE.sub(" ", query)
    stripped = _COMMENT_LINE_RE.sub(" ", stripped)
    return stripped


def validate_select_only(query: str) -> tuple[bool, str]:
    """쿼리 문자열이 단일 SELECT 문인지 검증한다. (ok, reason) 튜플을 반환한다."""
    if not query or not query.strip():
        return False, "empty_query"

    cleaned = _strip_comments(query).strip()
    if not cleaned:
        return False, "empty_after_comment_strip"

    # 끝의 세미콜론 하나는 허용하되, 그 뒤/앞에 추가 statement 가 있으면 차단한다.
    body = cleaned
    if body.rstrip().endswith(";"):
        body = body.rstrip()[:-1]
    if ";" in body:
        return False, "multiple_statements"

    if not re.match(r"(?is)^\s*SELECT\b", body):
        return False, "not_a_select_statement"

    # 문자열 리터럴 내부 값은 제거한 뒤 금지 키워드를 검사한다 (값에 우연히 포함된 단어로 인한
    # 오탐을 방지 — 예: WHERE name = 'DROP TABLE THEATER' 같은 값 자체는 통과시켜야 함).
    scan_target = _STRING_LITERAL_RE.sub("''", body)
    for keyword in _FORBIDDEN_KEYWORDS:
        if re.search(rf"(?i)\b{keyword}\b", scan_target):
            return False, f"forbidden_keyword:{keyword}"

    return True, "ok"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="검증할 SQL 쿼리 문자열")
    args = parser.parse_args()

    ok, reason = validate_select_only(args.query)
    print(json.dumps({"valid": ok, "reason": reason}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
