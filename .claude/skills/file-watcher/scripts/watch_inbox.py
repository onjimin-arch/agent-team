#!/usr/bin/env python3
"""로컬 드롭 폴더를 폴링해 새 파일을 감지 → 00_Inbox에 반영.

- 일반 텍스트류(.txt/.md/.csv/.log/.json): 내용을 그대로 읽어 Inbox 노트로 저장.
- `urls.txt`(또는 파일명에 "urls" 포함된 .txt): 줄 단위 URL 목록으로 보고 web-clipper에 위임
  (설계서 3-5-1 "URL 유입 경로" 결정 — 별도 URL 제출 기능을 새로 만들지 않고 이 경로를 재사용).
- pdf/docx/이미지 OCR 등은 범위 밖이다(설계서 5절 가정 7, 미해소) — 만나면 skipped로 로그만 남기고
  건너뛴다.

OS 파일시스템 이벤트(inotify 등)를 쓰는 새 의존성(watchdog 패키지 등) 대신, 처리한 파일의
경로+mtime을 상태 파일에 기록해두고 폴링마다 비교하는 방식으로 stdlib만으로 구현한다.

사용:
    python watch_inbox.py --watch-dir "<드롭 폴더>" --vault "<vault 절대경로>"

셀프테스트(네트워크/실제 폴더 감시 없이 로직만): python watch_inbox.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_AGENT_TEAM_ROOT = Path(__file__).resolve().parents[4]  # .../agent-team
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "shared" / "knowledge-lib" / "scripts"))
sys.path.insert(0, str(_AGENT_TEAM_ROOT / ".claude" / "skills" / "web-clipper" / "scripts"))
import kb_lib  # noqa: E402
import web_clip  # noqa: E402

KB_OUTPUT = _AGENT_TEAM_ROOT / "output" / "knowledge-agent"
_TEXT_EXTS = {".txt", ".md", ".csv", ".log", ".json"}


def is_url_list_file(path: Path) -> bool:
    return path.suffix.lower() == ".txt" and "url" in path.stem.lower()


def extract_text(path: Path) -> str | None:
    if path.suffix.lower() not in _TEXT_EXTS:
        return None  # pdf/docx/이미지 등은 범위 밖 — None 반환으로 상위에서 skipped 처리
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def write_inbox_note(vault: Path, file_path: Path) -> Path:
    text = extract_text(file_path)
    digest = hashlib.sha1(str(file_path.resolve()).encode()).hexdigest()[:10]
    source_id = f"file:{digest}"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in file_path.stem)[:60]
    # digest를 파일명에도 넣는다 — 같은 초에 이름이 같은 두 파일을 처리하면 안 그러면 충돌한다.
    out_path = vault / "00_Inbox" / f"{ts}_file_{digest}_{safe_name}.md"
    fm = {
        "source": "file",
        "source_id": source_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "raw": True,
        "status": "pending",
    }
    kb_lib.write_note(out_path, fm, f"# {file_path.name}\n\n원본 경로: {file_path}\n\n{text}")
    return out_path


def _load_seen(watch_dir: Path) -> dict:
    raw = kb_lib.get_cursor(KB_OUTPUT, f"file-watcher:{hashlib.sha1(str(watch_dir).encode()).hexdigest()[:8]}")
    return json.loads(raw) if raw else {}


def _save_seen(watch_dir: Path, seen: dict) -> None:
    kb_lib.set_cursor(KB_OUTPUT, f"file-watcher:{hashlib.sha1(str(watch_dir).encode()).hexdigest()[:8]}", json.dumps(seen))


def scan_once(watch_dir: Path, vault: Path) -> dict:
    seen = _load_seen(watch_dir)
    written, skipped, failed = [], [], []

    for path in sorted(watch_dir.iterdir()):
        if not path.is_file():
            continue
        mtime = str(path.stat().st_mtime)
        key = path.name
        if seen.get(key) == mtime:
            continue  # 이미 처리했고 그 뒤로 안 바뀜

        if is_url_list_file(path):
            urls = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
            for url in urls:
                result = web_clip.clip_url(url, vault)
                (written if result.get("ok") else failed).append(result)
            seen[key] = mtime  # 목록 파일 자체를 성공 처리로 간주(개별 URL 실패는 failed에 남음)
            continue

        text = extract_text(path)
        if text is None:
            skipped.append({"file": str(path), "reason": "unsupported_format"})
            continue  # cursor(seen)에 기록하지 않음 — 지원 포맷이 추가되면 다음 스캔에 재시도

        out_path = write_inbox_note(vault, path)
        written.append(str(out_path))
        seen[key] = mtime  # 쓰기 성공분만 전진 ([2-3] 결정과 동일 원칙)

    _save_seen(watch_dir, seen)
    return {"success": True, "written": written, "skipped": skipped, "failed": failed}


def _selftest() -> None:
    import tempfile

    assert is_url_list_file(Path("urls.txt")) is True
    assert is_url_list_file(Path("my_urls_list.txt")) is True
    assert is_url_list_file(Path("report.txt")) is False
    assert is_url_list_file(Path("report.pdf")) is False

    with tempfile.TemporaryDirectory() as td:
        watch_dir = Path(td) / "drop"
        watch_dir.mkdir()
        vault = Path(td) / "vault"
        (vault / "00_Inbox").mkdir(parents=True)

        (watch_dir / "note.txt").write_text("텍스트 파일 내용", encoding="utf-8")
        (watch_dir / "image.png").write_bytes(b"\x89PNG fake")

        result = scan_once(watch_dir, vault)
        assert len(result["written"]) == 1, result
        assert len(result["skipped"]) == 1 and result["skipped"][0]["reason"] == "unsupported_format", result

        # 재스캔 시 이미 처리한 텍스트 파일은 다시 쓰지 않는다 (cursor 동작 확인)
        result2 = scan_once(watch_dir, vault)
        assert result2["written"] == [], result2
        # 지원 안 되는 포맷은 cursor에 남기지 않으므로 매번 다시 skipped로 잡힌다(추후 포맷 지원 대비)
        assert len(result2["skipped"]) == 1, result2

    print("OK: watch_inbox selftest passed")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch-dir")
    parser.add_argument("--vault")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not args.watch_dir or not args.vault:
        parser.error("--watch-dir 와 --vault 는 --selftest 가 아닐 때 필수")

    result = scan_once(Path(args.watch_dir), Path(args.vault))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
