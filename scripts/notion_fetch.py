#!/usr/bin/env python3
"""다른 부서 Notion 워크스페이스 읽기 전용 조회 (member-alpha 용).

`scripts/notion_publish.py`(우리 조직 Notion 쓰기)와 별개다 — 이 스크립트는 다른 부서가 만든
별도 Notion 워크스페이스를 **조회 전용**으로 읽는다. 토큰도 별도 환경변수
(`DEPT_NOTION_API_TOKEN`)를 사용하며, 절대 `NOTION_API_TOKEN`(쓰기용)과 혼용하지 않는다.

외부 의존성 없이(stdlib `urllib`만 사용) 동작한다. `notion_publish.py`와 동일한 API 버전·요청
헬퍼·에러 출력 관례를 따른다.

사용 예:
    export DEPT_NOTION_API_TOKEN=secret_xxx
    python scripts/notion_fetch.py --search "화물 운임"
    python scripts/notion_fetch.py --page-id 1a2b3c4d5e6f...
    python scripts/notion_fetch.py --data-source-id 1a2b... --filter '{"property":"상태","status":{"equals":"완료"}}'

출력: JSON {"success": bool, "source_url": ..., "fetched_at": "<ISO8601>", "content": ...} (stdout).
실패해도 exit code 1(또는 설정 오류는 2)로 비치명적 종료.

한계 (의도적 단순화 — 자세한 내용은 .claude/skills/dept-notion-reader/SKILL.md 참조):
- 표(table) 블록은 셀 텍스트를 "|"로 이어붙인 plain text로만 변환한다.
- 이미지·임베드·synced block 등 텍스트가 아닌 블록은 건너뛰고 표시만 남긴다.
- 블록 자식은 1단계까지만 재귀 조회한다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_VERSION = "2025-09-03"
API_BASE = "https://api.notion.com/v1"
_MAX_PAGES = 5  # search/query 페이지네이션 상한 (폭주 방지)
_MAX_CHILD_DEPTH = 1  # 블록 자식 재귀 깊이 (0-indexed 상대 깊이)


def _request(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, dict]:
    url = f"{API_BASE}/{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Notion-Version", API_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = {"message": str(e)}
        return e.code, payload
    except urllib.error.URLError as e:
        return 0, {"message": f"network_error: {e.reason}"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain_text(rich_text: list[dict]) -> str:
    return "".join(run.get("plain_text", "") for run in (rich_text or []))


def _title_of(obj: dict) -> str:
    """search 결과(페이지/데이터베이스 공용)에서 제목을 최선 노력으로 추출한다."""
    if obj.get("object") == "database":
        return _plain_text(obj.get("title", []))
    props = obj.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            return _plain_text(prop.get("title", []))
    return ""


def _simplify_property(prop: dict):
    t = prop.get("type")
    if t in ("title", "rich_text"):
        return _plain_text(prop.get(t, []))
    if t == "number":
        return prop.get("number")
    if t == "select":
        sel = prop.get("select")
        return sel.get("name") if sel else None
    if t == "status":
        st = prop.get("status")
        return st.get("name") if st else None
    if t == "multi_select":
        return [o.get("name") for o in prop.get("multi_select", [])]
    if t == "date":
        d = prop.get("date")
        if not d:
            return None
        return d.get("start") if not d.get("end") else f"{d.get('start')} ~ {d.get('end')}"
    if t == "checkbox":
        return prop.get("checkbox")
    if t in ("url", "email", "phone_number"):
        return prop.get(t)
    if t == "people":
        return [p.get("name") or p.get("id") for p in prop.get("people", [])]
    if t == "formula":
        f = prop.get("formula", {})
        return f.get(f.get("type"))
    return f"[지원되지 않는 property 타입: {t}]"


def _simplify_properties(properties: dict) -> dict:
    return {name: _simplify_property(prop) for name, prop in properties.items()}


def _fetch_children(block_id: str, token: str, depth: int = 0) -> list[dict]:
    blocks: list[dict] = []
    cursor = None
    pages = 0
    while pages < _MAX_PAGES:
        path = f"blocks/{block_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        status, resp = _request("GET", path, token)
        if status != 200:
            break
        results = resp.get("results", [])
        for b in results:
            if b.get("has_children") and depth < _MAX_CHILD_DEPTH:
                b["_children"] = _fetch_children(b["id"], token, depth + 1)
        blocks.extend(results)
        pages += 1
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return blocks


_TEXT_BLOCK_TYPES = {
    "paragraph": "",
    "heading_1": "# ",
    "heading_2": "## ",
    "heading_3": "### ",
    "quote": "> ",
    "bulleted_list_item": "- ",
    "numbered_list_item": "1. ",
    "to_do": "- [ ] ",
}


def _block_to_lines(block: dict, indent: str = "") -> list[str]:
    t = block.get("type", "")
    lines: list[str] = []
    if t in _TEXT_BLOCK_TYPES:
        text = _plain_text(block.get(t, {}).get("rich_text", []))
        lines.append(f"{indent}{_TEXT_BLOCK_TYPES[t]}{text}")
    elif t == "code":
        code_obj = block.get("code", {})
        text = _plain_text(code_obj.get("rich_text", []))
        lang = code_obj.get("language", "")
        lines.append(f"{indent}```{lang}")
        lines.extend(f"{indent}{ln}" for ln in text.split("\n"))
        lines.append(f"{indent}```")
    elif t == "divider":
        lines.append(f"{indent}---")
    elif t == "table_row":
        cells = block.get("table_row", {}).get("cells", [])
        lines.append(f"{indent}| " + " | ".join(_plain_text(c) for c in cells) + " |")
    else:
        lines.append(f"{indent}[지원되지 않는 블록: {t}]")

    for child in block.get("_children", []):
        lines.extend(_block_to_lines(child, indent + "  "))
    return lines


def blocks_to_text(blocks: list[dict]) -> str:
    lines: list[str] = []
    for b in blocks:
        lines.extend(_block_to_lines(b))
    return "\n".join(lines)


def cmd_search(query: str, token: str) -> dict:
    results: list[dict] = []
    cursor = None
    pages = 0
    while pages < _MAX_PAGES:
        body = {"query": query, "page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        status, resp = _request("POST", "search", token, body)
        if status != 200:
            return {"success": False, "error": "search_failed", "status": status, "detail": resp}
        for r in resp.get("results", []):
            results.append({
                "id": r.get("id"),
                "object": r.get("object"),
                "url": r.get("url"),
                "title": _title_of(r),
            })
        pages += 1
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return {
        "success": True,
        "source_url": f"{API_BASE}/search",
        "fetched_at": _now_iso(),
        "content": {"query": query, "results": results},
    }


def cmd_page(page_id: str, token: str) -> dict:
    status, page = _request("GET", f"pages/{page_id}", token)
    if status != 200:
        return {"success": False, "error": "page_not_found", "status": status, "detail": page}

    blocks = _fetch_children(page_id, token)
    text = blocks_to_text(blocks)
    return {
        "success": True,
        "source_url": page.get("url", ""),
        "fetched_at": _now_iso(),
        "content": {
            "title": _title_of(page),
            "properties": _simplify_properties(page.get("properties", {})),
            "body": text,
        },
    }


def cmd_data_source(data_source_id: str, token: str, filter_json: str | None) -> dict:
    body: dict = {"page_size": 100}
    if filter_json:
        try:
            body["filter"] = json.loads(filter_json)
        except json.JSONDecodeError as e:
            return {"success": False, "error": "invalid_filter_json", "detail": str(e)}

    rows: list[dict] = []
    cursor = None
    pages = 0
    while pages < _MAX_PAGES:
        if cursor:
            body["start_cursor"] = cursor
        status, resp = _request("POST", f"data_sources/{data_source_id}/query", token, body)
        if status != 200:
            return {"success": False, "error": "query_failed", "status": status, "detail": resp}
        for r in resp.get("results", []):
            rows.append({
                "id": r.get("id"),
                "url": r.get("url"),
                "properties": _simplify_properties(r.get("properties", {})),
            })
        pages += 1
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")

    return {
        "success": True,
        "source_url": f"{API_BASE}/data_sources/{data_source_id}/query",
        "fetched_at": _now_iso(),
        "content": {"row_count": len(rows), "rows": rows},
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--search", help="키워드로 페이지/데이터베이스 검색")
    group.add_argument("--page-id", help="특정 페이지 내용 조회")
    group.add_argument("--data-source-id", help="데이터소스(데이터베이스) 조회")
    parser.add_argument("--filter", default=None, help="--data-source-id 와 함께 사용할 Notion filter 객체(JSON)")
    args = parser.parse_args()

    token = os.environ.get("DEPT_NOTION_API_TOKEN", "").strip()
    if not token:
        print(json.dumps({
            "success": False,
            "error": "DEPT_NOTION_API_TOKEN_missing",
            "hint": "https://www.notion.so/my-integrations 에서 (다른 부서 워크스페이스 관리자가) "
                    "Integration 토큰을 발급하고 대상 페이지/데이터소스에 Connect 한 뒤 "
                    "DEPT_NOTION_API_TOKEN 환경변수로 설정하세요. NOTION_API_TOKEN(우리 조직, 쓰기용)과는 "
                    "다른 값입니다.",
        }, ensure_ascii=False))
        return 2

    if args.filter and not args.data_source_id:
        print(json.dumps({"success": False, "error": "filter_without_data_source_id"}, ensure_ascii=False))
        return 2

    if args.search is not None:
        result = cmd_search(args.search, token)
    elif args.page_id is not None:
        result = cmd_page(args.page_id, token)
    else:
        result = cmd_data_source(args.data_source_id, token, args.filter)

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
