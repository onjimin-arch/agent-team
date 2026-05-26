# Plan: GPU 지원 받는 방법

## 태스크 요약
한국에서 스타트업/기업/연구자가 GPU 자원을 지원받을 수 있는 방법을 조사·분석하고, 실행 가능한 가이드를 제공한다.

## Task Type 판별
- **선택된 type**: `research-report` (default)
- **근거**: 트리거 키워드 미매칭 → default type 적용
- **활성 멤버**: member-alpha · member-gamma · member-delta · member-beta (전원)

## 멤버 배정

| 멤버 | 역할 | 산출물 |
|---|---|---|
| member-alpha | GPU 지원 프로그램 조사·분석 (정부/공공/민간/해외) | `member-alpha/analysis-report.md` |
| member-gamma | alpha 보고서의 수치·프로그램명·기관명·조건 팩트체크 | `member-gamma/fact-check-log.md` |
| member-delta | 지원 프로세스 흐름도, 프로그램 비교 테이블 시각화 | `member-delta/visuals.md` |
| member-beta | 최종 보고서 초안 (요약·핵심 인사이트·추천 사항) | `member-beta/draft-report.md` |

## 실행 순서 & 의존성

```
member-alpha
    ↓
member-gamma (alpha 결과 참조)
    ↓
member-delta (alpha + gamma 결과 참조)
    ↓
member-beta (alpha + gamma + delta 모두 참조)
```

## 기대 산출물 상세

### member-alpha
- 국내 GPU 지원 채널 분류: 정부/공공기관, 민간 클라우드 크레딧, 학술/연구기관, 스타트업 전용 프로그램
- 각 프로그램의 지원 대상, 규모, 신청 방법, URL

### member-gamma
- alpha 보고서 내 수치(지원 규모, 크레딧 금액 등) 및 프로그램명 정확성 검증
- 출처 불명 또는 최신 정보 갱신 필요 항목 플래그

### member-delta
- GPU 지원 신청 프로세스 플로우차트 (Mermaid)
- 주요 프로그램 비교 테이블 (지원 대상 / 규모 / 신청 방법)

### member-beta
- 독자 타겟별(스타트업, 연구자, 기업) 맞춤 추천 경로 정리
- 핵심 인사이트: 놓치기 쉬운 팁, 신청 시기, 주의사항

## 종료 조건
- max_cycles: 3
- quality_criteria: 필수 섹션 포함, 논리적 정합성, 스키마 준수
- human_approval: false
