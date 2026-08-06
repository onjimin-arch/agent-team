자동 확정된 slug: erp-손익-분석해서-알려줘

# ERP 손익 분석 계획

Phase 0 판별: task_pipeline - 요청문에 Quick Query 신호(`ERP`, `손익`, `알려줘`)가 있으나 report_signal(`분석`)이 함께 있어 풀 파이프라인으로 진행.

## 작업 요약
- ERP 대시보드의 전사 손익 데이터를 조회해 최신 월 손익을 분석하고 핵심 원인과 대응 포인트를 정리한다.
- 기존 유사 워크스페이스 `output/이번-전사-경영-실적-손익/`(작성일 2026-07-31, 범위 80% 이상 중첩)을 AUTO 모드 규칙에 따라 재사용한다.

## Task Type 판별
- 선택된 type: `research-report`
- score:
  - `research-report`: 1/7 (`분석`)
  - `code-review`: 0/5
  - `multilingual-brief`: 0/6
  - `dev`: 0/10
  - `design`: 0/8
  - `github-plan`: 0/7
  - `ir-relations`: 0/9
  - `gr-policy`: 0/9
  - `pr-crisis`: 0/9
  - `mgmt-planning`: 0/8
  - `strategy-newbiz`: 0/8
- 선택 근거: 최고 score(`research-report`) 자동 선택.

## 활성 멤버
- alpha(조사)
- gamma(팩트체크)
- delta(시각화)
- beta(보고서)

## 고위험 플래그
- 고위험(사내 대시보드 데이터 사용): `scripts/dashboard_fetch.py`로 ERP 민감 재무 데이터를 조회한다.
- `termination.high_risk_override_enabled=false` 이므로 Notion/Slack 배포는 자동 진행하되, 문서에는 민감 데이터 사용 사실을 명시한다.

## Assignments
- `member-alpha(조사)`
  - ERP 대시보드 `api/external/board?ym=2026-08`와 비교 기준 `ym=2026-07`을 조회한다.
  - 기존 최종 산출물 `output/이번-전사-경영-실적-손익/final/final-artifact.md`를 참고해 비교 맥락을 재사용한다.
  - 최신 손익, 사업부별 증감, 비용 구조 변화를 분석해 `member-alpha/analysis-report.md`를 작성한다.
- `member-gamma(팩트체크)`
  - alpha 산출물의 핵심 수치와 증감 계산이 ERP 응답 원문과 일치하는지 검증한다.
  - 8월 수치가 `예상`이며 `elapsed=4/31` 기반이라는 해석상 주의사항을 명시한다.
- `member-delta(시각화)`
  - alpha 산출물의 핵심 수치만 사용해 전사 손익 흐름과 사업부별 증감을 Mermaid/테이블로 구조화한다.
- `member-beta(보고서)`
  - alpha, gamma, delta 산출물을 종합해 경영진이 바로 읽을 수 있는 요약과 추천 사항을 작성한다.

## 실행 순서
1. `member-alpha`
2. `member-gamma` + `member-delta`
3. `member-beta`

## Dependency Map
- `member-alpha`: ERP 대시보드 응답, 기존 워크스페이스 최종본
- `member-gamma`: `member-alpha/analysis-report.md`
- `member-delta`: `member-alpha/analysis-report.md`
- `member-beta`: `member-alpha/analysis-report.md`, `member-gamma/fact-check-log.md`, `member-delta/visuals.md`

## Expected Outputs
- `output/erp-손익-분석해서-알려줘/member-alpha/analysis-report.md`
- `output/erp-손익-분석해서-알려줘/member-gamma/fact-check-log.md`
- `output/erp-손익-분석해서-알려줘/member-delta/visuals.md`
- `output/erp-손익-분석해서-알려줘/member-beta/draft-report.md`

자동 확정 후 Phase 2 진입 - 2026-08-05 12:35 KST
