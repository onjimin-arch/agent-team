자동 확정된 slug: 현장-지역담당자-영업-활동-현황

# 현장 지역담당자 영업 활동 현황 분석 계획

Phase 0 판별: task_pipeline - quick_query 신호(`현장`)가 있었지만 report_signal(`분석`)가 명확해 정식 리포트 파이프라인으로 진행

## 선행 체크

- 유사 워크스페이스 재사용: `output/현장-지역담당자-영업활동-분석해줘/final/final-artifact.md` 재사용
- 재사용 근거: 작성일 `2026-08-05`, 현재 요청과 주제 중복도 80% 이상, 동일한 현장 지역담당자 영업활동 현황 범위
- 처리 방식: 기존 산출물은 범위 설정 참고자료로만 사용하고, 이번 사이클의 원천 데이터는 현장 대시보드 재조회 결과로 갱신

## 작업 요약

- 최근 현장 대시보드 기준으로 지역담당자 관할 권역의 영업 활동 구조를 분석한다.
- 개인별 영업 로그가 아닌 권역별 배송 실적, B2B 믹스, 라이더 생산성을 지역담당자 활동의 프록시 지표로 해석한다.
- `scripts/dashboard_fetch.py`로 현장 대시보드를 조회하므로 고위험(사내 대시보드 데이터 사용) 플래그를 기록한다. 단 `termination.high_risk_override_enabled: false` 이므로 AUTO 모드 배포는 계속 진행한다.

## Task Type 판별

- 선택된 type: `research-report`
- 선택 근거: 최고 score
- score 상세:
  - `research-report`: 2/7 (`분석`, `현황`)
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

## 활성 멤버

- alpha(조사) · gamma(팩트체크) · delta(시각화) · beta(보고서)

## Assignments

- `member-gamma(팩트체크)`
  - 현장 대시보드 원문 데이터를 수집한다.
  - 최소 수집 범위: `2026-08` 현재월 누적 전국 스냅샷, `2026-07` 전국 월간 기준선, 필요 시 지역 spot-check.
  - 출력: `member-gamma/fact-check-log.md`
- `member-alpha(조사)`
  - gamma가 수집한 원문만 사용해 최근 영업활동 현황을 분석한다.
  - 핵심 관점: 전국 속도 변화, 지역 집중도, B2B 복잡도, 권역별 생산성 차이, 해석 한계.
  - 출력: `member-alpha/analysis-report.md`
- `member-delta(시각화)`
  - alpha 분석을 시각 요약으로 재구성한다.
  - 최소 산출: 변화 요약 다이어그램 1개, 권역 관리 유형 다이어그램 1개, 핵심 비교표 2개.
  - 출력: `member-delta/visuals.md`
- `member-beta(보고서)`
  - alpha와 delta 승인본을 바탕으로 의사결정용 보고서 초안을 작성한다.
  - 핵심 구조: 요약, 핵심 인사이트, 추천 사항.
  - 출력: `member-beta/draft-report.md`

## 실행 순서

1. gamma(팩트체크) - 원천 데이터 수집
2. alpha(조사) - 현황 분석
3. delta(시각화) - 시각 자료 구성
4. beta(보고서) - 보고서 초안 작성

## 의존성 맵

- gamma -> 없음
- alpha -> gamma
- delta -> alpha
- beta -> alpha, delta

## 예상 결과물

- 지역담당자 활동을 권역 성과 프록시로 읽은 분석 보고서
- 전국 대비 권역별 우선순위를 빠르게 볼 수 있는 시각화
- 다음 확인 KPI와 액션이 포함된 최종 보고서

자동 확정 후 Phase 2 진입 - 2026-08-05 13:16
