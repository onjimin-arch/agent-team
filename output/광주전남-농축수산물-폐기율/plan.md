# Plan: 광주전남 농축수산물 폐기율 분석 보고서

## Task 요약
광주광역시 및 전라남도 지역의 농산물·축산물·수산물 폐기율 현황을 분석하고,
주요 원인·구조적 문제·개선 방향을 도출하는 리서치 보고서를 작성한다.

## 선택된 Task Type
- **Type**: `research-report` (default)
- **근거**: 폐기율 "현황" 분석이 핵심 과제이며, 명시적 태그 없음 → default 적용

## 활성 멤버 목록
| 멤버 | 역할 | 비고 |
|---|---|---|
| member-alpha | 시장 조사·데이터 분석 | 폐기율 데이터 수집 및 구조 분석 |
| member-gamma | 팩트체커 | 수치·출처·정책명 검증 |
| member-delta | 시각화 | Mermaid 다이어그램·테이블 작성 |
| member-beta | 보고서 초안 작성 | 분석 결과 → 최종 보고서 |

## 할당 작업

### member-alpha
- 광주·전남 농산물/축산물/수산물 폐기율 데이터 조사 및 분석
- 품목별·지역별·연도별 폐기율 현황 파악
- 주요 폐기 원인(유통 구조, 수요-공급 불균형, 저장시설 등) 분석
- 타 지역 및 전국 평균과의 비교
- 출력: `output/광주전남-농축수산물-폐기율/member-alpha/analysis-report.md`

### member-gamma
- member-alpha의 수치·정책명·출처 검증
- 폐기율 통계치가 공신력 있는 출처(농림축산식품부, 해양수산부, 통계청 등)에서 확인 가능한지 검토
- 출력: `output/광주전남-농축수산물-폐기율/member-gamma/fact-check-log.md`

### member-delta
- member-alpha 분석 결과를 Mermaid 다이어그램 및 테이블로 시각화
- 품목별 폐기율 비교 테이블, 원인 구조 흐름도, 지역별 비교 차트 스펙
- 출력: `output/광주전남-농축수산물-폐기율/member-delta/visuals.md`

### member-beta
- member-alpha·gamma·delta 산출물을 종합하여 최종 보고서 초안 작성
- 요약, 핵심 인사이트, 추천 사항 포함
- 출력: `output/광주전남-농축수산물-폐기율/member-beta/draft-report.md`

## 실행 순서 및 의존성
```
member-alpha → member-gamma (alpha 산출물 검증)
member-alpha → member-delta (alpha 산출물 시각화)
member-gamma + member-delta → member-beta (통합 보고서 작성)
member-beta → 팀장 통합 → final-artifact.md
```

## 의존성 맵
- member-gamma depends on: member-alpha
- member-delta depends on: member-alpha
- member-beta depends on: member-alpha, member-gamma, member-delta

## 기대 산출물
- 광주·전남 농축수산물 폐기율 현황 분석 (품목별/연도별)
- 폐기 원인 구조 분석
- 개선 정책 및 추천 사항
- 시각화 자료 (다이어그램·테이블)
- 최종 통합 보고서: `output/광주전남-농축수산물-폐기율/final/final-artifact.md`
