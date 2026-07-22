#!/usr/bin/env python3
"""결정론적 산출물 검증기 (Phase 3/4 품질 게이트).

LLM 판단 없이 필수 섹션 존재 여부만 기계적으로 확인한다. team-config.yaml 의
`expected_files.required_sections` 을 그대로 반영하되, YAML 파싱은 호출자(팀장 LLM)가
이미 team-config.yaml 을 읽어 알고 있는 값을 인자로 넘겨주는 방식으로 분리했다
(이 스크립트는 외부 의존성 없이 어떤 Python 3 환경에서도 동작해야 하므로 PyYAML 등을
 요구하지 않는다).

사용 예:
    python scripts/validate_artifact.py \\
        --file output/slug/member-alpha/analysis-report.md \\
        --sections "개요,분석 결과,결론"

    # 여러 파일을 한 번에 (Phase 4 통합 검증용)
    python scripts/validate_artifact.py --manifest manifest.json

manifest.json 형식:
    [
      {"file": "output/slug/member-alpha/analysis-report.md",
       "sections": ["개요", "분석 결과", "결론"]},
      {"file": "output/slug/final/final-artifact.md",
       "sections": ["요약", "핵심 인사이트"]}
    ]

출력: JSON (stdout). 종료 코드: 전부 통과 0 / 하나라도 실패 1 / 실행 오류 2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$", re.MULTILINE)
# 헤딩 앞의 번호("1. ", "1) ")나 이모지·장식 문자를 제거하고 비교한다.
_NUM_PREFIX_RE = re.compile(r"^\s*(?:\d+[\.\)]\s*|[-*]\s*)+")


def _normalize(text: str) -> str:
    text = _NUM_PREFIX_RE.sub("", text)
    text = re.sub(r"[*_`]", "", text)
    return text.strip().casefold()


def extract_headings(content: str) -> list[str]:
    return [m.group(2) for m in _HEADING_RE.finditer(content)]


def check_file(path: Path, required_sections: list[str]) -> dict:
    if not path.exists():
        return {
            "file": str(path),
            "pass": False,
            "error": "file_not_found",
            "missing_sections": required_sections,
            "found_headings": [],
        }
    content = path.read_text(encoding="utf-8", errors="replace")
    headings = extract_headings(content)
    normalized_headings = [_normalize(h) for h in headings]

    missing: list[str] = []
    for section in required_sections:
        target = _normalize(section)
        if not any(target == h or target in h or h in target for h in normalized_headings):
            missing.append(section)

    empty_sections = _find_empty_sections(content, required_sections)

    return {
        "file": str(path),
        "pass": not missing and not empty_sections,
        "missing_sections": missing,
        "empty_sections": empty_sections,
        "found_headings": headings,
    }


def _section_body(content: str, matches: list[re.Match], i: int) -> str:
    """i번째 헤딩의 본문을 반환한다. 같은/더 얕은 레벨의 다음 헤딩 전까지가 본문이며,
    하위(더 깊은) 헤딩은 본문의 일부로 취급한다 — 예: '## 분석 결과' 바로 다음에
    '### 1. ...' 하위 섹션이 와도 그건 빈 섹션이 아니라 정상적인 구조다."""
    level = len(matches[i].group(1))
    start = matches[i].end()
    end = len(content)
    for j in range(i + 1, len(matches)):
        if len(matches[j].group(1)) <= level:
            end = matches[j].start()
            break
    return content[start:end].strip()


def _find_empty_sections(content: str, required_sections: list[str]) -> list[str]:
    """섹션 헤딩은 있지만 본문이 비어있거나 플레이스홀더만 있는 경우를 감지."""
    matches = list(_HEADING_RE.finditer(content))
    empty: list[str] = []
    placeholder_re = re.compile(r"^(tbd|todo|n/a|없음|작성\s*중|\.\.\.)$", re.IGNORECASE)

    for i, m in enumerate(matches):
        heading_norm = _normalize(m.group(2))
        target_hit = next(
            (s for s in required_sections if _normalize(s) == heading_norm or _normalize(s) in heading_norm),
            None,
        )
        if target_hit is None:
            continue
        body = _section_body(content, matches, i)
        if not body or placeholder_re.match(body):
            empty.append(target_hit)
    return empty


def main() -> int:
    # Windows 콘솔의 기본 cp949 인코딩에서도 한글 JSON 출력이 깨지지 않도록 강제.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="검증할 단일 파일 경로")
    parser.add_argument("--sections", help="콤마 구분 필수 섹션명 (예: '개요,분석 결과,결론')")
    parser.add_argument("--manifest", help="여러 파일을 한 번에 검증할 JSON 매니페스트 경로")
    args = parser.parse_args()

    tasks: list[dict] = []
    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            print(json.dumps({"error": f"manifest_not_found: {args.manifest}"}, ensure_ascii=False))
            return 2
        tasks = json.loads(manifest_path.read_text(encoding="utf-8"))
    elif args.file and args.sections:
        tasks = [{"file": args.file, "sections": [s.strip() for s in args.sections.split(",") if s.strip()]}]
    else:
        parser.print_help()
        return 2

    results = [check_file(Path(t["file"]), t.get("sections", [])) for t in tasks]
    all_pass = all(r["pass"] for r in results)

    print(json.dumps({"all_pass": all_pass, "results": results}, ensure_ascii=False, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
