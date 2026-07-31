자동 확정된 slug: 이번-전사-경영-실적-손익

# 이번 전사 경영 실적(손익) 요약 계획

## Task Summary
- 업무 설명: 이번 달 전사 경영 실적(손익) 현황을 ERP 대시보드에서 조회해서 요약
- 워크스페이스: `output/이번-전사-경영-실적-손익`
- 실행 모드: AUTO
- 조회 대상 월: `2026-07`

## Task Type 판별
- 선택된 type: `mgmt-planning`
- score:
  - `research-report`: 1/7 (`현황` 매칭)
  - `code-review`: 0/5
  - `multilingual-brief`: 0/6
  - `dev`: 0/10
  - `design`: 0/8
  - `github-plan`: 0/7
  - `ir-relations`: 0/9
  - `gr-policy`: 0/9
  - `pr-crisis`: 0/9
  - `mgmt-planning`: 1/8 (`경영 실적` 매칭)
  - `strategy-newbiz`: 0/8
- 선택 근거: 요청의 핵심 명사가 `경영 실적`이며 ERP 대시보드 기반 손익 요약이라는 업무 성격이 `mgmt-planning` 전용 역할과 직접 일치하므로 이를 우선 적용

## 활성 멤버 목록
- alpha
- delta
- beta

## 위험 플래그
- 고위험(사내 대시보드 데이터 사용): `member-alpha` 에게 `scripts/dashboard_fetch.py` 기반 ERP 대시보드 조회를 배정
- 처리 규칙: AUTO 모드에서는 Phase 1~4 자동 진행, Phase 5 외부 배포는 보류하고 승인 대기 알림만 발송

## Assignments
- `member-alpha`: ERP 대시보드(`api/external/board`, `ym=2026-07`) 조회를 시도하고, 원문 응답 또는 실패 사유를 기반으로 전사 손익 현황 분석 보고서 작성. 수치와 해석을 구분하고 source URL, fetched_at, 조회 한계를 함께 기록.
- `member-delta`: alpha 산출물을 바탕으로 경영진 보고용 시각자료 작성. 손익 요약 흐름도, 리스크/조치 플로우, 핵심 수치 테이블을 구성.
- `member-beta`: alpha·delta 산출물을 종합해 경영 요약 보고서 초안 작성. 확보된 사실, 조회 실패 원인, 즉시 필요한 조치와 후속 보고 권고를 정리.

## Execution Order
1. `member-alpha`
2. `member-delta`
3. `member-beta`

## Dependency Map
- `member-alpha`: 선행 의존성 없음
- `member-delta`: `output/이번-전사-경영-실적-손익/member-alpha/analysis-report.md`
- `member-beta`: `output/이번-전사-경영-실적-손익/member-alpha/analysis-report.md`, `output/이번-전사-경영-실적-손익/member-delta/visuals.md`

## Expected Outputs
- `member-alpha/analysis-report.md`: ERP 조회 결과 또는 실패 사유를 반영한 경영 실적 분석 보고서
- `member-delta/visuals.md`: 경영진 보고용 Mermaid 다이어그램과 핵심 수치 테이블
- `member-beta/draft-report.md`: 전사 손익 현황 요약 초안

자동 확정 후 Phase 2 진입 - 2026-07-30 16:08

## Cycle 3 Update (2026-07-31 13:44)
- 재사용 판단: 기존 동일 슬러그의 최종 산출물이 30일 이내에 존재하고 업무 범위가 동일하므로 AUTO 규칙에 따라 기존 워크스페이스를 재사용한다.
- 실행 전략: 기존 `mgmt-planning` 계획과 활성 멤버(`alpha`, `delta`, `beta`)는 유지하고, ERP 대시보드를 `2026-07` 기준으로 재조회해 수치만 최신화한다.
- 위험 플래그 유지: `scripts/dashboard_fetch.py` 실제 사용으로 인해 고위험(사내 대시보드 데이터 사용) override가 계속 적용된다.
- 현재 사이클 목표:
  1. `member-alpha` 가 ERP 재조회 결과(`data_date=2026-07-30`, `calc_at=2026-07-31 11:25:10`)를 반영해 분석 보고서를 갱신한다.
  2. `member-delta` 가 최신 수치 기준 시각자료를 갱신한다.
  3. `member-beta` 가 최신 수치와 승인 조건을 반영해 경영 요약 초안을 갱신한다.
  4. Team Lead가 Phase 3~5를 다시 수행한다.
