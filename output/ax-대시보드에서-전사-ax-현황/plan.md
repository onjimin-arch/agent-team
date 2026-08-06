자동 확정된 slug: ax-대시보드에서-전사-ax-현황

# AX 대시보드 전사 AX 현황 요약 계획

## Task Summary
- 업무 설명: AX 대시보드에서 전사 AX 진행 현황 확인하고 요약
- 워크스페이스: `output/ax-대시보드에서-전사-ax-현황`
- 실행 모드: AUTO
- 데이터 소스: AX 대시보드 `api/v1/export/cases`, `api/v1/export/reports`
- 분석 초점: 전사 AX 파이프라인 규모, 부서별 집중도, 진행 단계 불균형, 최신 보고서 기반 정성 시사점

## Task Type 판별
- 선택된 type: `research-report`
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
  - `mgmt-planning`: 0/8
  - `strategy-newbiz`: 0/8
- 선택 근거: 요청문에서 직접 매칭된 trigger는 `현황`뿐이고, 목적도 코드 수정이나 설계가 아니라 AX 현황을 데이터 기반으로 요약하는 리서치 성격이므로 `research-report`를 적용한다.

## 활성 멤버 목록
- alpha(조사)
- gamma(팩트체크)
- delta(시각화)
- beta(보고서)

## 위험 플래그
- 고위험(사내 대시보드 데이터 사용): `member-alpha` 에게 `scripts/dashboard_fetch.py` 기반 AX 대시보드 조회를 배정
- 처리 규칙: AUTO 모드에서는 Phase 1~4 자동 진행, Phase 5에서 Notion 저장은 즉시 실행하고 Slack은 최종 배포 대신 승인 대기 알림만 발송

## Assignments
- `member-gamma`: AX `cases`/`reports` 원문에서 전사 현황 요약에 필요한 raw source를 정리하고, 최신 보고서 작성 시점과 누락 부서를 기록한다.
- `member-alpha`: `scripts/dashboard_fetch.py` 로 AX `cases`/`reports`를 조회해 전사 AX 파이프라인의 규모, 부서별 집중도, 진행률 불일치, 정성 시사점을 분석한다. 원문 수치와 해석을 분리하고 `source_url`, `fetched_at`을 명시한다.
- `member-delta`: alpha 분석을 바탕으로 전사 AX 단계 흐름도와 부서별 집중도 표를 작성한다.
- `member-beta`: gamma·alpha·delta 산출물을 종합해 경영진이 바로 읽을 수 있는 AX 현황 요약 초안을 작성한다.

## Execution Order
1. `member-gamma`
2. `member-alpha`
3. `member-delta`
4. `member-beta`

## Dependency Map
- `member-gamma`: 선행 의존성 없음
- `member-alpha`: `output/ax-대시보드에서-전사-ax-현황/member-gamma/fact-check-log.md`
- `member-delta`: `output/ax-대시보드에서-전사-ax-현황/member-alpha/analysis-report.md`
- `member-beta`: `output/ax-대시보드에서-전사-ax-현황/member-gamma/fact-check-log.md`, `output/ax-대시보드에서-전사-ax-현황/member-alpha/analysis-report.md`, `output/ax-대시보드에서-전사-ax-현황/member-delta/visuals.md`

## Expected Outputs
- `member-gamma/fact-check-log.md`: AX 원문 데이터와 최신 보고서 스냅샷 정리
- `member-alpha/analysis-report.md`: 전사 AX 진행 현황 분석 보고서
- `member-delta/visuals.md`: 단계 흐름도와 핵심 수치 표
- `member-beta/draft-report.md`: 최종 요약 초안

자동 확정 후 Phase 2 진입 - 2026-07-31 16:13
