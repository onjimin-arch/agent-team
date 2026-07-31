자동 확정된 slug: 바로고가-정부-정책-기관-대응하기

# 바로고의 정부 정책·기관 대응 모니터링 채널 조사 계획

## Task Summary
- 업무 설명: 바로고가 정부 정책 및 기관 대응을 위해 모니터링해야 하는 외부 채널(사이트)을 조사한다.
- 목표 산출물: 정책 변화 조기 탐지에 필요한 채널 목록, 기관별 확인 포인트, 모니터링 운영 권고안을 담은 최종 보고서.

## Task Type Selection
- 선택된 type: research-report
- score:
  - research-report: 1/8 (`정책` 매칭)
  - code-review: 0/4
  - multilingual-brief: 0/6
  - dev: 0/10
  - design: 0/8
  - github-plan: 0/6
- 선택 근거: 최고 score 인 `research-report` 선택
- 활성 멤버 목록: member-alpha, member-beta, member-gamma, member-delta

## Assignments
- member-gamma: 정부 정책 및 기관 대응과 직접 관련된 원문 채널을 수집하고, 기관명·날짜·URL·원문 발췌를 정리한다.
- member-alpha: gamma 산출물을 기반으로 바로고 관점의 모니터링 우선순위, 채널 분류, 활용 목적을 분석한다.
- member-delta: alpha 분석 결과를 시각자료와 표로 구조화한다.
- member-beta: alpha 분석과 delta 시각자료를 바탕으로 실행 가능한 보고서 초안을 작성한다.

## Execution Order
1. member-gamma
2. member-alpha
3. member-delta
4. member-beta

## Dependency Map
- member-gamma: 선행 의존성 없음
- member-alpha: `output/바로고가-정부-정책-기관-대응하기/member-gamma/fact-check-log.md` 필요
- member-delta: `output/바로고가-정부-정책-기관-대응하기/member-alpha/analysis-report.md` 필요
- member-beta: `output/바로고가-정부-정책-기관-대응하기/member-alpha/analysis-report.md`, `output/바로고가-정부-정책-기관-대응하기/member-delta/visuals.md` 필요

## Expected Outputs
- member-gamma: 정책 모니터링용 원문 채널 로그
- member-alpha: 기관군별 모니터링 전략 분석 보고서
- member-delta: 모니터링 체계 다이어그램 및 우선순위 테이블
- member-beta: 핵심 인사이트와 추천 사항을 담은 보고서 초안

## Validation Notes
- 모든 활성 멤버에 작업 배정 완료
- 의존성 사이클 없음
- AUTO 모드이므로 사용자 승인 없이 진행

자동 확정 후 Phase 2 진입: 2026-07-29 18:44
