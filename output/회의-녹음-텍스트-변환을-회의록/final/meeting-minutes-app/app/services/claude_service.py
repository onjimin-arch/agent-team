import os
import anthropic

_client: anthropic.Anthropic | None = None

SYSTEM_PROMPT = """당신은 전문 회의록 작성 도우미입니다. 회의 전사 텍스트를 분석하여 구조화된 회의록을 작성합니다.
반드시 한국어로 작성하며, 마크다운 형식을 사용합니다."""

USER_PROMPT_TEMPLATE = """다음 회의 전사 텍스트를 분석하여 아래 형식의 회의록을 작성해주세요.
정보가 명확하지 않은 항목은 "확인 필요"로 표시하세요.

## 회의 요약
(2-3문장으로 핵심 내용 요약)

## 참석자
(언급된 이름이나 역할 목록, 없으면 "미확인"으로 표시)

## 주요 논의사항
(항목별 정리, 번호 매기기)

## 결정사항
(확정된 사항 목록, 없으면 "없음")

## 액션아이템
| 담당자 | 내용 | 기한 |
|-------|------|------|
(항목 나열, 없으면 행 생략)

---
전사 텍스트:
{transcript}"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def generate_minutes(transcript: str) -> str:
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(transcript=transcript),
            }
        ],
    )
    return message.content[0].text
