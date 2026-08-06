자동 확정된 slug: 현장-지역담당자-영업활동-분석해줘

Phase 0 판별: task_pipeline - quick_query 신호 `현장`이 있으나 report_signal `분석`이 명시돼 정식 리포트 경로로 진행

# 현장 지역담당자 최근 영업활동 분석 계획

## Task Summary
- 업무 설명: 현장 지역담당자 최근 영업활동 분석
- 워크스페이스: `output/현장-지역담당자-영업활동-분석해줘`
- 실행 모드: AUTO
- 기준 스냅샷: `2026-08-01`부터 `2026-08-04`까지의 현장 대시보드 월간 누적 집계
- 데이터 접근 전략: 현장 대시보드 전국 집계를 우선 확보하고, 전월 비교는 재조회 성공 범위 내에서만 제한적으로 반영한다.

## Task Type 판별
- 선택된 type: `research-report`
- score:
  - `research-report`: 1/7 (`분석` 매칭)
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
- 선택 근거: 요청문에서 명시적으로 매칭된 trigger 는 `분석`뿐이며, 코드/설계/정책 대응이 아닌 운영 활동 해석 요청이므로 `research-report`를 적용한다.

## 활성 멤버 목록
- alpha(조사)
- gamma(팩트체크)
- delta(시각화)
- beta(보고서)

## 위험 플래그
- 고위험(사내 대시보드 데이터 사용): `member-alpha` 에게 `scripts/dashboard_fetch.py` 기반 현장 대시보드 조회를 배정
- 처리 규칙: `termination.high_risk_override_enabled=false` 이므로 AUTO 모드에서 Phase 5 Notion/Slack 배포를 그대로 수행한다.

## Assignments
- `member-alpha`: `scripts/dashboard_fetch.py` 로 현장 대시보드 전국 집계(`date=2026-08-05`, `ym=2026-08`)를 조회하고, 지역별 활동 규모, B2B 비중, 라이더당 처리량 관점에서 영업활동 구조를 분석한다. 전월 비교는 조회 성공 범위만 사용하고 실패한 비교 재조회도 한계로 기록한다.
- `member-gamma`: alpha 가 사용한 원문 수치와 파생 지표를 검증한다. 전국 합계 일치 여부, 브랜드 합계 차이, 전월 비교 성공/실패 범위를 확인하고 수정 권고를 남긴다.
- `member-delta`: alpha·gamma 산출물을 바탕으로 지역 집중도, 활동 구조, 우선 액션 포인트를 빠르게 읽을 수 있는 Mermaid 다이어그램과 핵심 수치 테이블로 구조화한다.
- `member-beta`: alpha·gamma·delta 산출물을 종합해 지역담당자용 운영 해석과 즉시 실행 권고가 담긴 보고서 초안을 작성한다.

## Execution Order
1. `member-alpha`
2. `member-gamma`
3. `member-delta`
4. `member-beta`

## Dependency Map
- `member-alpha`: 선행 의존성 없음
- `member-gamma`: `output/현장-지역담당자-영업활동-분석해줘/member-alpha/analysis-report.md`
- `member-delta`: `output/현장-지역담당자-영업활동-분석해줘/member-alpha/analysis-report.md`, `output/현장-지역담당자-영업활동-분석해줘/member-gamma/fact-check-log.md`
- `member-beta`: `output/현장-지역담당자-영업활동-분석해줘/member-alpha/analysis-report.md`, `output/현장-지역담당자-영업활동-분석해줘/member-gamma/fact-check-log.md`, `output/현장-지역담당자-영업활동-분석해줘/member-delta/visuals.md`

## Expected Outputs
- `member-alpha/analysis-report.md`: 최근 현장 영업활동 구조 분석 보고서
- `member-gamma/fact-check-log.md`: 수치 검증 로그와 데이터 한계
- `member-delta/visuals.md`: 지역 집중도와 활동 구조 시각자료
- `member-beta/draft-report.md`: 지역담당자 실행용 보고서 초안

자동 확정 후 Phase 2 진입 - 2026-08-05 12:55
