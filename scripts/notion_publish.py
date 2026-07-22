#!/usr/bin/env python3
"""Notion REST API 직접 호출 기반 Phase 5 배포 폴백.

기존 문제: CLAUDE.md Phase 5 는 `notion-create-pages` MCP 도구 호출만 전제하는데,
실제 프로덕션 실행 경로(opencode 서브프로세스, slack-bridge/agent_runner.py)에는
claude.ai MCP 커넥터가 연결되어 있지 않다. 그 결과 실제 운영 로그
(`output/방식-영어-퀴즈-게임-개발/auto-log.md`)에서 "NOTION_API_TOKEN 환경변수 미설정"으로
Notion 배포가 반복 실패했다.

이 스크립트는 MCP 없이도 동작하는 독립 경로다 — Notion Integration 토큰
(`NOTION_API_TOKEN`, https://www.notion.so/my-integrations 에서 발급) 하나만 있으면
opencode/Claude Code 어느 실행 환경에서도 Bash 로 직접 호출 가능하다.
외부 의존성 없이(stdlib `urllib`만 사용) 동작하도록 작성했다.

주의: 대상 Notion 데이터소스에 이 Integration 이 "연결(connect)"되어 있어야 한다
(데이터베이스 페이지 우측 상단 ... → Connections → Integration 추가).

사용 예:
    export NOTION_API_TOKEN=secret_xxx
    python scripts/notion_publish.py \\
        --file output/slug/final/final-artifact.md \\
        --data-source-id 348363ae-08db-80aa-ba4a-000b3160d6ed \\
        --title-property 이름 \\
        --icon "🖥️" \\
        --title "2026년 전기차 시장 리서치 (2026-07-22)"

출력: JSON {"success": bool, "url": str, ...} (stdout). 실패해도 exit code 1로
비치명적 종료 — 호출자가 이미 완성된 final-artifact.md 는 그대로 두고 계속 진행할 수 있다.

한계 (의도적 단순화 — MCP 커넥터 없이 최소 신뢰성 확보가 목적이지 완벽한 렌더링이 목적이 아님):
- 마크다운 테이블은 Notion 테이블 블록이 아니라 코드 블록(plain text)으로 보존한다.
- 인라인 서식은 **bold** 만 인식하고 나머지(이탤릭·링크 등)는 원문 그대로 텍스트로 남는다.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_VERSION = "2025-09-03"
API_BASE = "https://api.notion.com/v1"
_RICH_TEXT_LIMIT = 2000
_CHUNK_TARGET = 1800  # rich text 분할 기준 (여유를 둔 안전 마진)


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


def _rich_text(text: str) -> list[dict]:
    """**bold** 만 인식하는 단순 인라인 파서. 그 외 서식은 원문 그대로 둔다."""
    runs = []
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            content = part[2:-2]
            bold = True
        else:
            content = part
            bold = False
        for i in range(0, len(content), _RICH_TEXT_LIMIT):
            chunk = content[i:i + _RICH_TEXT_LIMIT]
            run = {"type": "text", "text": {"content": chunk}}
            if bold:
                run["annotations"] = {"bold": True}
            runs.append(run)
    return runs or [{"type": "text", "text": {"content": ""}}]


def _chunk_text(text: str, target: int = _CHUNK_TARGET) -> list[str]:
    if len(text) <= target:
        return [text]
    chunks = []
    while text:
        if len(text) <= target:
            chunks.append(text)
            break
        cut = text.rfind(" ", 0, target)
        cut = cut if cut > 0 else target
        chunks.append(text[:cut])
        text = text[cut:].lstrip()
    return chunks


def _paragraph_blocks(text: str) -> list[dict]:
    return [
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _rich_text(c)}}
        for c in _chunk_text(text)
    ]


def _heading_block(level: int, text: str) -> dict:
    key = f"heading_{min(level, 3)}"
    return {"object": "block", "type": key, key: {"rich_text": _rich_text(text[:_RICH_TEXT_LIMIT])}}


def _list_item_block(text: str, numbered: bool) -> dict:
    key = "numbered_list_item" if numbered else "bulleted_list_item"
    return {"object": "block", "type": key, key: {"rich_text": _rich_text(text[:_RICH_TEXT_LIMIT])}}


def _code_block(text: str, language: str) -> dict:
    lang = language if language else "plain text"
    chunks = _chunk_text(text, target=1900) or [""]
    return {
        "object": "block", "type": "code",
        "code": {"rich_text": [{"type": "text", "text": {"content": chunks[0]}}], "language": lang},
    }


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_DIVIDER_RE = re.compile(r"^\s*(?:---+|\*\*\*+|___+)\s*$")


def md_to_blocks(markdown_text: str) -> list[dict]:
    lines = markdown_text.split("\n")
    blocks: list[dict] = []
    para_buffer: list[str] = []
    i = 0

    def flush_para():
        nonlocal para_buffer
        if para_buffer:
            text = "\n".join(para_buffer).strip()
            if text:
                blocks.extend(_paragraph_blocks(text))
            para_buffer = []

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            flush_para()
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append(_code_block("\n".join(code_lines), lang))
            i += 1
            continue

        m = _HEADING_RE.match(line)
        if m:
            flush_para()
            blocks.append(_heading_block(len(m.group(1)), m.group(2).strip()))
            i += 1
            continue

        m = _TABLE_ROW_RE.match(line)
        if m:
            flush_para()
            table_lines = []
            while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
                table_lines.append(lines[i])
                i += 1
            blocks.append(_code_block("\n".join(table_lines), "plain text"))
            continue

        if _DIVIDER_RE.match(line):
            flush_para()
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        m = _BULLET_RE.match(line)
        if m:
            flush_para()
            blocks.append(_list_item_block(m.group(1), numbered=False))
            i += 1
            continue

        m = _NUMBERED_RE.match(line)
        if m:
            flush_para()
            blocks.append(_list_item_block(m.group(1), numbered=True))
            i += 1
            continue

        if not line.strip():
            flush_para()
            i += 1
            continue

        para_buffer.append(line)
        i += 1

    flush_para()
    return blocks


def strip_h1(markdown_text: str) -> tuple[str, str | None]:
    """최상위 H1 제목 줄을 제거하고 (본문, 추출된 제목) 을 반환."""
    lines = markdown_text.split("\n")
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^#\s+(.+?)\s*$", stripped)
        if m:
            return "\n".join(lines[:idx] + lines[idx + 1:]), m.group(1)
        break  # 첫 비어있지 않은 줄이 H1 이 아니면 본문 그대로 유지
    return markdown_text, None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Notion 에 올릴 마크다운 파일 (보통 final-artifact.md)")
    parser.add_argument("--data-source-id", required=True)
    parser.add_argument("--title-property", default="이름")
    parser.add_argument("--icon", default="")
    parser.add_argument("--title", default="", help="지정하지 않으면 파일의 H1 제목을 사용")
    args = parser.parse_args()

    token = os.environ.get("NOTION_API_TOKEN", "").strip()
    if not token:
        print(json.dumps({
            "success": False,
            "error": "NOTION_API_TOKEN_missing",
            "hint": "https://www.notion.so/my-integrations 에서 Integration 토큰을 발급하고 "
                    "대상 데이터소스에 Connect 한 뒤 NOTION_API_TOKEN 환경변수로 설정하세요.",
        }, ensure_ascii=False))
        return 2

    file_path = Path(args.file)
    if not file_path.exists():
        print(json.dumps({"success": False, "error": "file_not_found", "path": args.file}, ensure_ascii=False))
        return 2

    content = file_path.read_text(encoding="utf-8", errors="replace")
    body_text, extracted_title = strip_h1(content)
    title = args.title or extracted_title or file_path.stem

    blocks = md_to_blocks(body_text)
    first_batch, rest = blocks[:100], blocks[100:]

    page_payload: dict = {
        "parent": {"type": "data_source_id", "data_source_id": args.data_source_id},
        "properties": {
            args.title_property: {"title": [{"text": {"content": title[:2000]}}]}
        },
        "children": first_batch,
    }
    if args.icon:
        page_payload["icon"] = {"type": "emoji", "emoji": args.icon}

    status, resp = _request("POST", "pages", token, page_payload)
    if status not in (200, 201):
        print(json.dumps({"success": False, "error": "create_page_failed", "status": status, "detail": resp},
                          ensure_ascii=False))
        return 1

    page_id = resp.get("id", "")
    page_url = resp.get("url", "")

    for start in range(0, len(rest), 100):
        batch = rest[start:start + 100]
        status, append_resp = _request("PATCH", f"blocks/{page_id}/children", token, {"children": batch})
        if status not in (200, 201):
            print(json.dumps({
                "success": True, "partial": True, "url": page_url, "page_id": page_id,
                "warning": "일부 블록 추가 실패 (페이지는 생성됨)", "detail": append_resp,
            }, ensure_ascii=False))
            return 0

    print(json.dumps({"success": True, "url": page_url, "page_id": page_id}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
