#!/usr/bin/env python3
"""URL 하나를 md로 변환해 00_Inbox에 저장. robots.txt 최소 확인(차단 사이트는 자동 배제).

stdlib만 사용: robots.txt 파싱은 `urllib.robotparser`, HTML→텍스트는 `html.parser` 기반 손수
태그 스트리퍼(외부 파서 라이브러리 도입 안 함 — ponytail 3단: stdlib면 충분).

호출 경로(설계서 3-5-1 결정): `knowledge-research`가 리서치 중 찾은 URL, 또는 file-watcher가
`urls.txt`에서 감지한 URL. 별도의 "URL 직접 제출" 기능은 없다.

사용:
    python web_clip.py --url https://example.com --vault "<vault 절대경로>"

셀프테스트(네트워크 없이 HTML→텍스트 변환만): python web_clip.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[4]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
import kb_lib  # noqa: E402

_UA = "knowledge-agent-web-clipper/1.0 (개인 지식베이스 수집용; 지민님 개인 사용)"


class _TextExtractor(HTMLParser):
    """<script>/<style> 제외 텍스트만 모으는 최소 구현 — 레이아웃/서식은 버린다."""

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.chunks: list[str] = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._skip_depth == 0 and data.strip():
            self.chunks.append(data.strip())


def html_to_text(html: str) -> tuple[str, str]:
    """(title, body_text) 반환."""
    extractor = _TextExtractor()
    extractor.feed(html)
    return extractor.title.strip(), "\n".join(extractor.chunks)


def check_robots_allowed(url: str, user_agent: str = _UA) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except (urllib.error.URLError, OSError):
        return True  # robots.txt 자체를 못 읽으면 차단 근거가 없으므로 허용(최소 확인 원칙)
    return rp.can_fetch(user_agent, url)


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def write_inbox_note(vault: Path, url: str, title: str, body: str) -> Path:
    source_id = f"web:{url}"
    digest = hashlib.sha1(source_id.encode()).hexdigest()[:10]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:60].strip()
    # digest를 항상 파일명에 넣는다 — 같은 초에 제목이 같은 두 URL을 클립하면 안 그러면 충돌한다.
    path = vault / "00_Inbox" / f"{ts}_web_{digest}_{safe_title}.md"
    fm = {
        "source": "web",
        "source_id": source_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "raw": True,
        "status": "pending",
    }
    kb_lib.write_note(path, fm, f"# {title or url}\n\n원본: {url}\n\n{body}")
    return path


def clip_url(url: str, vault: Path) -> dict:
    if not check_robots_allowed(url):
        return {"ok": False, "url": url, "error": "robots_disallowed"}
    try:
        html = fetch_url(url)
    except (urllib.error.URLError, OSError) as e:
        return {"ok": False, "url": url, "error": str(e)}
    title, body = html_to_text(html)
    if not body.strip():
        return {"ok": False, "url": url, "error": "empty_body_after_extraction"}
    path = write_inbox_note(vault, url, title, body)
    return {"ok": True, "url": url, "path": str(path)}


def _selftest() -> None:
    import tempfile

    sample_html = "<html><head><title>테스트 제목</title><style>.x{}</style></head>" \
                   "<body><script>var x=1;</script><h1>본문 헤더</h1><p>본문 내용입니다.</p></body></html>"
    title, body = html_to_text(sample_html)
    assert title == "테스트 제목", title
    assert "본문 헤더" in body and "본문 내용입니다." in body
    assert "var x=1" not in body and ".x{}" not in body  # script/style 제외 확인

    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        (vault / "00_Inbox").mkdir()
        path = write_inbox_note(vault, "https://example.com/a", "테스트 제목", "본문 내용입니다.")
        fm, saved_body = kb_lib.read_note(path)
        assert fm["source"] == "web" and fm["source_id"] == "web:https://example.com/a"
        assert "본문 내용입니다." in saved_body

    print("OK: web_clip selftest passed (network 호출 없이 파싱/저장 로직만 검증)")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--vault")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not args.url or not args.vault:
        parser.error("--url 과 --vault 는 --selftest 가 아닐 때 필수")

    import json
    result = clip_url(args.url, Path(args.vault))
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
