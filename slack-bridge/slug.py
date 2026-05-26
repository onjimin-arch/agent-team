"""kebab-case slug 생성 — 한글·영문 혼재 업무 설명에서 간단한 슬러그 후보 만들기."""
from __future__ import annotations

import re
from datetime import datetime


_STOPWORDS = {
    # 위치/주체
    "관련", "대한", "통한", "위한", "대해", "대하여",
    "한국", "국내", "국외", "해외",
    # 시간 표현
    "이후", "이전", "당시", "당해", "동안", "최근",
    # 업무 동사/명사
    "작성", "보고서", "리서치", "분석", "조사", "검토",
    "수립", "수행", "진행", "실시", "도출", "정리",
    # 영어 stop words
    "the", "a", "an", "and", "or", "for", "to", "of", "in",
    "on", "by", "with", "from", "as", "at", "is", "be",
}

# 숫자+한글 접미사 → 숫자만 추출 (예: 2026년 → 2026)
_NUM_SUFFIX = re.compile(r"^(\d+)(년|월|일|분|초|회|차|주|호|분기|시간|세기)$")


def _normalize(token: str) -> str:
    m = _NUM_SUFFIX.match(token)
    return m.group(1) if m else token


def slugify(text: str, max_tokens: int = 5) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^0-9a-z가-힣\s-]", " ", text)
    raw = [t for t in re.split(r"\s+", text) if t]

    tokens: list[str] = []
    for t in raw:
        if t in _STOPWORDS:
            continue
        t = _normalize(t)
        # 단일 한글 1글자는 대부분 조사/의존명사 (후, 중, 전, 등)
        if len(t) == 1 and re.match(r"[가-힣]", t):
            continue
        tokens.append(t)

    tokens = tokens[:max_tokens] or [datetime.now().strftime("%Y%m%d-%H%M")]
    slug = re.sub(r"-+", "-", "-".join(tokens)).strip("-")
    return slug or datetime.now().strftime("topic-%Y%m%d-%H%M")


if __name__ == "__main__":
    # 간단 점검용
    for sample in [
        "2026년 국내 전기차 시장 리서치 후 보고서 작성",
        "LLM 에이전트 성능 개선 분석",
        "2025 Q3 매출 리포트 작성",
        "AI 팀 주간 회고 정리",
    ]:
        print(f"{sample!r:60s} -> {slugify(sample)}")
