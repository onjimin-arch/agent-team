자동 확정된 slug: 부서별-ax-진척율

# Plan

Phase 0 판별: task_pipeline - 요청문에 quick query 신호(`AX`)와 report signal(`분석`)이 함께 있어 애매했으나, `scripts/slack_approval.py` 호출이 `invalid_blocks`로 실패해 AUTO 모드 에스컬레이션 규칙에 따라 안전 기본값인 풀 파이프라인으로 진행.

## Task Summary
- 업무 설명: 부서별 AX 진척율 분석
- 워크스페이스: `output/부서별-ax-진척율/`
- 데이터 상태: `2026-08-19 09:54` 기준 AX 대시보드 재조회(`cases`/`reports`/`departments`)가 모두 `401 unauthorized`로 실패해, 30일 이내 유사 워크스페이스 `output/ax-대시보드에서-전사-ax-현황/`의 검증본(`2026-07-31`)을 재사용한다.
- 고위험 플래그: 사내 대시보드 데이터 사용. 단 `termination.high_risk_override_enabled=false` 이므로 Phase 5 배포는 자동 진행.

## Task Type
- 선택된 type: `research-report`
- score:
  - `research-report`: `1/7` (`분석` 매칭)
  - `code-review`: `0/5`
  - `multilingual-brief`: `0/6`
  - `dev`: `0/10`
  - `design`: `0/8`
  - `github-plan`: `0/7`
  - `ir-relations`: `0/9`
  - `gr-policy`: `0/9`
  - `pr-crisis`: `0/9`
  - `mgmt-planning`: `0/8`
  - `strategy-newbiz`: `0/8`
  - `product-planning`: `0/10`
- 선택 근거: 최고 score.
- 활성 멤버: alpha(조사) · gamma(팩트체크) · delta(시각화) · beta(보고서)

## Reuse Check
- 유사 워크스페이스: `output/ax-대시보드에서-전사-ax-현황/`
- 최종 산출물 존재: 예 (`final/final-artifact.md`)
- 생성일: `2026-07-31`
- 재사용 판단: 30일 이내이며 AX 진행 현황 분석과 부서별 진척률 분석의 범위가 80% 이상 겹친다고 판단.
- AUTO 모드 판단: 기존 검증본 재사용, 단 오늘 재조회 실패 사실을 모든 산출물에 병기.

## Assignments
- `member-gamma(팩트체크)`: 재사용 대상 산출물의 원문 수치와 출처 범위를 검증하고, 오늘 재조회 실패 사실과 데이터 시점 제한을 정리한 `fact-check-log.md` 작성.
- `member-alpha(조사)`: 기존 AX 집계표를 부서별 진척률 중심으로 재해석하고, 진척률과 시간 영향도의 괴리를 설명한 `analysis-report.md` 작성.
- `member-delta(시각화)`: 부서별 진척률 순위표와 우선순위 구조를 `visuals.md`로 정리.
- `member-beta(보고서)`: 위 산출물을 바탕으로 경영진이 바로 읽을 수 있는 `draft-report.md` 작성.

## Execution Order
1. `member-gamma(팩트체크)`
2. `member-alpha(조사)`
3. `member-delta(시각화)`
4. `member-beta(보고서)`

## Dependency Map
- `member-gamma` -> 없음
- `member-alpha` -> `member-gamma/fact-check-log.md`
- `member-delta` -> `member-alpha/analysis-report.md`
- `member-beta` -> `member-alpha/analysis-report.md`, `member-delta/visuals.md`, `member-gamma/fact-check-log.md`

자동 확정 후 Phase 2 진입 - 2026-08-19 09:54

## Follow-up Update (2026-08-19 10:11)
- 후속 지시: `다시 조회해서 작성해줘.`
- 판단: 기존 `2026-07-31` 재사용 스냅샷 보강이 아니라 AX 원문 `cases` / `reports` / `departments` 재조회 후 재작성 범위로 분류.
- 수행 범위: `member-gamma/fact-check-log.md`, `member-alpha/analysis-report.md`, `member-delta/visuals.md`, `member-beta/draft-report.md`, `final/final-artifact.md`, `slack-notification.json`, `review-log.md` 갱신.
- 배포 방침: 최종 산출물 내용이 바뀌므로 Phase 5 Notion / Slack을 모두 재실행.
