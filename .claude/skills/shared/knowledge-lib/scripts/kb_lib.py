#!/usr/bin/env python3
"""지식수집 스킬 공용 유틸 — frontmatter, cursor, 락 판정, quota, 태그 유사도.

전부 stdlib만 사용한다(pyyaml 등 신규 의존성 없음). 손수 작성한 frontmatter 파서는
이 프로젝트가 실제로 쓰는 필드(문자열/문자열 리스트/불리언)만 다루는 의도적 단순화다 —
자세한 한계는 SKILL.md 참고.

셀프테스트: python kb_lib.py --selftest
"""
from __future__ import annotations

import argparse
import difflib
import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

FRONTMATTER_DELIM = "---"


# ---------------------------------------------------------------- frontmatter

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """"---\\nkey: val\\n---\\nbody" 를 (dict, body) 로 분리한다."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            end = i
            break
    if end is None:
        return {}, text
    fm: dict = {}
    for line in lines[1:end]:
        if not line.strip() or ":" not in line:
            continue
        key, _, raw_val = line.partition(":")
        key = key.strip()
        raw_val = raw_val.strip()
        if raw_val.startswith("[") and raw_val.endswith("]"):
            inner = raw_val[1:-1].strip()
            fm[key] = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()] if inner else []
        elif raw_val.lower() in ("true", "false"):
            fm[key] = raw_val.lower() == "true"
        else:
            fm[key] = raw_val.strip('"').strip("'")
    body = "\n".join(lines[end + 1:])
    if body.startswith("\n"):
        body = body[1:]
    return fm, body


def _format_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return "[" + ", ".join(f'"{x}"' for x in v) + "]"
    return str(v)


def write_frontmatter(fm: dict, body: str) -> str:
    lines = [FRONTMATTER_DELIM]
    for k, v in fm.items():
        lines.append(f"{k}: {_format_value(v)}")
    lines.append(FRONTMATTER_DELIM)
    return "\n".join(lines) + "\n\n" + body.lstrip("\n")


def read_note(path: Path) -> tuple[dict, str]:
    return parse_frontmatter(Path(path).read_text(encoding="utf-8"))


def write_note(path: Path, fm: dict, body: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(write_frontmatter(fm, body), encoding="utf-8")


# --------------------------------------------------------------------- cursor

def _cursor_dir(kb_output_root: Path) -> Path:
    d = Path(kb_output_root) / "cursors"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_cursor(kb_output_root: Path, source_name: str) -> str | None:
    f = _cursor_dir(kb_output_root) / f"{source_name}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8")).get("cursor")


def set_cursor(kb_output_root: Path, source_name: str, cursor_value: str) -> None:
    """쓰기까지 성공한 항목만큼만 호출한다 — 실패분은 cursor에 반영하지 않는다([2-3] 결정)."""
    f = _cursor_dir(kb_output_root) / f"{source_name}.json"
    f.write_text(
        json.dumps({"cursor": cursor_value, "updated_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False),
        encoding="utf-8",
    )


# ----------------------------------------------------------------------- lock

def lock_path(kb_output_root: Path) -> Path:
    return Path(kb_output_root) / "batch.lock"


def acquire_batch_lock(kb_output_root: Path) -> None:
    """note-structurer 배치 시작 시 호출. 끝나면 release_batch_lock으로 반드시 해제한다."""
    lock_path(kb_output_root).write_text(
        json.dumps({"acquired_at": datetime.now(timezone.utc).isoformat()}), encoding="utf-8"
    )


def release_batch_lock(kb_output_root: Path) -> None:
    lp = lock_path(kb_output_root)
    if lp.exists():
        lp.unlink()


def check_lock(kb_output_root: Path, stale_after_sec: int = 300) -> bool:
    """knowledge-query/knowledge-research가 시작 전 호출. True=지금 진행해도 됨, False=배치가 살아있으니 대기/재시도 안내.

    워치독 프로세스 없이 요청 측이 스스로 타임스탬프로 판정한다([2-3] 결정) — 5~10분 지나면
    배치가 죽은 것으로 간주하고 무시하고 진행한다.
    """
    lp = lock_path(kb_output_root)
    if not lp.exists():
        return True
    try:
        acquired_at = datetime.fromisoformat(json.loads(lp.read_text(encoding="utf-8"))["acquired_at"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return True  # 락 파일이 깨져 있으면 판단 불가 상태로 두지 않고 진행
    age = (datetime.now(timezone.utc) - acquired_at).total_seconds()
    return age > stale_after_sec


def wait_for_lock(kb_output_root: Path, max_wait_sec: int = 30, poll_sec: int = 2, stale_after_sec: int = 300) -> bool:
    """최대 max_wait_sec 동안 짧게 폴링. True=진행 가능, False=아직 배치 중(호출자에게 '나중에 재시도' 응답)."""
    deadline = time.monotonic() + max_wait_sec
    while True:
        if check_lock(kb_output_root, stale_after_sec=stale_after_sec):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(poll_sec)


# ---------------------------------------------------------------------- quota

def _quota_file(kb_output_root: Path, name: str, day: date) -> Path:
    d = Path(kb_output_root) / "quota"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{name}_{day.isoformat()}.json"


def check_and_increment_quota(kb_output_root: Path, name: str, daily_limit: int) -> bool:
    """True=허용(카운트 증가시킴), False=quota 초과(하드 캡 — [2-3] 결정, 호출 거부)."""
    today = date.today()
    f = _quota_file(kb_output_root, name, today)
    count = json.loads(f.read_text(encoding="utf-8"))["count"] if f.exists() else 0
    if count >= daily_limit:
        return False
    f.write_text(json.dumps({"count": count + 1, "date": today.isoformat()}), encoding="utf-8")
    return True


# --------------------------------------------------------------- tag 유사도

def suggest_existing_tag(new_tag: str, existing_tags: list[str], threshold: float = 0.84) -> str | None:
    """difflib 문자열 유사도 기반 — 오탈자/표기 차이는 잡지만 동의어는 못 잡는 임시 구현(SKILL.md 한계 참고)."""
    best, best_score = None, 0.0
    for existing in existing_tags:
        score = difflib.SequenceMatcher(None, new_tag.lower(), existing.lower()).ratio()
        if score > best_score:
            best, best_score = existing, score
    return best if best_score >= threshold else None


def collect_existing_tags(vault_root: Path, folders: list[str]) -> list[str]:
    tags: set[str] = set()
    for folder in folders:
        for md in (Path(vault_root) / folder).glob("**/*.md"):
            fm, _ = read_note(md)
            for t in fm.get("tags", []) or []:
                tags.add(t)
    return sorted(tags)


# --------------------------------------------------------------- source_id

def find_note_by_source_id(vault_root: Path, folders: list[str], source_id: str) -> Path | None:
    for folder in folders:
        base = Path(vault_root) / folder
        if not base.exists():
            continue
        for md in base.glob("**/*.md"):
            fm, _ = read_note(md)
            if fm.get("source_id") == source_id:
                return md
    return None


# ------------------------------------------------------------------- selftest

def _selftest() -> None:
    fm, body = parse_frontmatter(
        '---\nsource: notion\nsource_id: notion:abc123\ntags: ["ax", "리서치"]\nstatus: pending\n---\n\n본문 내용'
    )
    assert fm == {"source": "notion", "source_id": "notion:abc123", "tags": ["ax", "리서치"], "status": "pending"}, fm
    assert body == "본문 내용", repr(body)

    out = write_frontmatter({"tags": ["a", "b"], "done": True}, "본문")
    fm2, body2 = parse_frontmatter(out)
    assert fm2 == {"tags": ["a", "b"], "done": True}, fm2
    assert body2 == "본문", repr(body2)

    assert suggest_existing_tag("AX", ["ax", "리서치"], threshold=0.8) == "ax"
    assert suggest_existing_tag("완전히다른개념", ["ax", "리서치"], threshold=0.8) is None

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        assert get_cursor(root, "notion") is None
        set_cursor(root, "notion", "2026-08-12T00:00:00Z")
        assert get_cursor(root, "notion") == "2026-08-12T00:00:00Z"

        assert check_lock(root) is True  # 락 없음 → 진행 가능
        acquire_batch_lock(root)
        assert check_lock(root, stale_after_sec=300) is False  # 방금 건 락 → 대기
        release_batch_lock(root)
        assert check_lock(root) is True

        assert check_and_increment_quota(root, "knowledge-research", daily_limit=2) is True
        assert check_and_increment_quota(root, "knowledge-research", daily_limit=2) is True
        assert check_and_increment_quota(root, "knowledge-research", daily_limit=2) is False  # 하드 캡

    print("OK: all kb_lib selftests passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        _selftest()
    else:
        parser.print_help()
        sys.exit(1)
