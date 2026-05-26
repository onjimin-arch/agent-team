# Plan: 배달시장 MS 분석

## Task 요약
국내 배달 시장의 주요 플랫폼(배달의민족·쿠팡이츠·요기요)별 시장점유율(Market Share)을 분석하고, 경쟁 구도·성장 추이·주요 변수를 정리한 리서치 보고서를 작성한다.

## Task Type 판별
- **선택된 type**: `research-report`
- **근거**: 요청 문장에 "분석"(trigger) 및 "시장"(trigger) 포함
- **활성 멤버**: member-alpha, member-beta, member-gamma, member-delta

## 멤버별 과업 할당

| 멤버 | 과업 | 산출물 |
|---|---|---|
| member-alpha | 배달 시장 MS 데이터 수집·구조화 분석 | `member-alpha/analysis-report.md` |
| member-gamma | alpha 산출물 내 수치·출처 팩트체크 | `member-gamma/fact-check-log.md` |
| member-delta | alpha 분석 기반 Mermaid 다이어그램·비교 테이블 작성 | `member-delta/visuals.md` |
| member-beta | alpha·gamma·delta 산출물 종합 → 보고서 초안 작성 | `member-beta/draft-report.md` |

## 실행 순서 및 의존성

```
member-alpha  →  member-gamma  →  member-delta
                                         ↓
                                  member-beta
```

1. **Step 1** (독립): member-alpha — 시장 분석 보고서
2. **Step 2** (alpha 완료 후): member-gamma — 팩트체크
3. **Step 3** (alpha 완료 후, gamma 병행 가능): member-delta — 시각화
4. **Step 4** (gamma + delta 완료 후): member-beta — 보고서 초안

## 의존성 맵
- member-gamma → `member-alpha/analysis-report.md`
- member-delta → `member-alpha/analysis-report.md`
- member-beta → `member-alpha/analysis-report.md` + `member-gamma/fact-check-log.md` + `member-delta/visuals.md`

## 기대 최종 산출물
- 경로: `output/배달시장-ms/final/final-artifact.md`
- 형식: 마크다운 통합 보고서
- 포함 내용: 시장 개요, 플랫폼별 MS, 경쟁 구도, 트렌드, 시각화, 추천 사항
