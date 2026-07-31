#!/usr/bin/env python3
"""사내 부서별 손익/실적 대시보드 API 읽기 전용 조회 (member-alpha 용) — 범용 버전.

ERP뿐 아니라 현장·인사·AX·브랜드·법무 등 여러 부서가 각자 유사한 구조(X-API-Key 헤더 인증, 고정
GET 엔드포인트)의 대시보드 API를 운영한다. 이 스크립트는 특정 부서에 종속되지 않고 base URL·경로·
인증 키 환경변수를 모두 인자로 받는다 — 각 대시보드의 실제 값(base URL, 키 환경변수명, 알려진
엔드포인트 목록, 민감도)은 이 스크립트가 아니라 `.claude/skills/dept-dashboard-reader/SKILL.md`의
레지스트리 표에 문서화되어 있다. **새 부서 대시보드가 추가돼도 이 스크립트는 수정할 필요가 없다** —
스킬 문서 표에 행만 추가하면 된다.

인증: `X-API-Key` 헤더만 사용한다 (쿼리스트링 `?api_key=` 방식은 URL 노출 위험 때문에 의도적으로
지원하지 않는다). 이 방식이 ERP 대시보드에서는 확인됐지만, 다른 부서 대시보드도 동일한 인증
방식을 쓰는지는 시스템별로 실제 확인이 필요하다 — 다르다면 이 스크립트로 호출할 수 없고 별도 처리가
필요하다(SKILL.md에 예외로 기록할 것).

외부 의존성 없이(stdlib `urllib`만 사용) 동작한다.

사용 예 (ERP):
    export ERP_API_KEY=erp_xxx
    python scripts/dashboard_fetch.py --base-url http://10.10.190.25:8000 \\
        --path api/external/board --key-env ERP_API_KEY --query ym=2026-07

주의 (Git Bash/MSYS 환경, 예: 이 프로젝트의 Windows 개발 환경): `--path` 값 앞에 `/`를 붙이면
("/api/external/board") MSYS 가 이를 유닉스 절대경로로 오인해 Windows 경로로 자동 변환해버려
요청이 깨진다(`InvalidURL: URL can't contain control characters` 등으로 실패). `--path` 는 항상
**선행 슬래시 없이** 쓴다("api/external/board") — 스크립트가 base URL과 합칠 때 슬래시를 알아서
정규화한다.

출력: JSON {"success": bool, "source_url": ..., "fetched_at": "<ISO8601>", "content": ...} (stdout).
실패해도 exit code 1(또는 설정 오류는 2)로 비치명적 종료.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _request(url: str, api_key: str, ca_cert: str | None) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET")
    req.add_header("X-API-Key", api_key)
    context = ssl.create_default_context(cafile=ca_cert) if ca_cert else None
    try:
        with urllib.request.urlopen(req, timeout=30, context=context) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = {"message": str(e)}
        return e.code, payload
    except urllib.error.URLError as e:
        return 0, {"message": f"network_error: {e.reason}"}


def _parse_query(pairs: list[str]) -> dict:
    query: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        query[key] = value
    return query


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="대시보드 API의 base URL (예: http://10.10.190.25:8000)")
    parser.add_argument("--path", required=True, help="엔드포인트 경로 (예: /api/external/board)")
    parser.add_argument("--key-env", required=True, help="API 키가 담긴 환경변수 이름 (예: ERP_API_KEY)")
    parser.add_argument("--query", action="append", default=[], metavar="KEY=VALUE",
                         help="쿼리 파라미터, 여러 번 지정 가능 (예: --query ym=2026-07)")
    parser.add_argument("--ca-cert", default=None,
                         help="자가서명 인증서를 쓰는 대시보드용 CA 파일 경로 (예: certs/ax_server.pem). "
                              "레지스트리에 명시된 대시보드만 지정한다 — 임의로 검증을 우회하지 않는다.")
    args = parser.parse_args()

    api_key = os.environ.get(args.key_env, "").strip()
    if not api_key:
        print(json.dumps({
            "success": False,
            "error": f"{args.key_env}_missing",
            "hint": f"{args.key_env} 환경변수가 설정되어 있지 않습니다. 해당 대시보드의 키 발급 페이지에서 "
                    f"API 키를 발급받아 slack-bridge/.env 에 {args.key_env}=... 형태로 추가하세요. "
                    f"(.claude/skills/dept-dashboard-reader/SKILL.md 의 대시보드 레지스트리 표 참조)",
        }, ensure_ascii=False))
        return 2

    query = _parse_query(args.query)
    url = args.base_url.rstrip("/") + "/" + args.path.lstrip("/")
    if query:
        url += "?" + urllib.parse.urlencode(query)

    status, payload = _request(url, api_key, args.ca_cert)

    if status == 401:
        print(json.dumps({
            "success": False, "error": "unauthorized", "status": status, "detail": payload,
            "hint": f"{args.key_env} 값이 잘못됐거나 만료됐을 수 있습니다. 재발급이 필요합니다.",
        }, ensure_ascii=False))
        return 1
    if status == 403:
        print(json.dumps({
            "success": False, "error": "forbidden", "status": status, "detail": payload,
            "hint": f"{args.key_env} 키에 이 엔드포인트에 필요한 scope 권한이 없을 수 있습니다. "
                    f"레지스트리에서 이 대시보드의 scope 요구사항을 확인하세요.",
        }, ensure_ascii=False))
        return 1
    if status != 200:
        print(json.dumps({
            "success": False, "error": "request_failed", "status": status, "detail": payload,
        }, ensure_ascii=False))
        return 1

    print(json.dumps({
        "success": True, "source_url": url, "fetched_at": _now_iso(), "content": payload,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
