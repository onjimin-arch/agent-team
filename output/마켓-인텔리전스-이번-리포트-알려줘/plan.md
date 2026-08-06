자동 확정된 slug: 마켓-인텔리전스-이번-리포트-알려줘

# 마켓 인텔리전스 이번 주 리포트 계획

## Task Summary
- 업무 설명: 마켓 인텔리전스 이번 주 리포트 알려줘
- 워크스페이스: `output/마켓-인텔리전스-이번-리포트-알려줘`
- 실행 모드: AUTO
- 기준 주차: `2026-W32`
- Phase 0 판별: `task_pipeline`
- 판별 근거: `알려줘`, `마켓 인텔리전스`로 quick query 신호가 있으나, 런타임 지시에서 Phase 1~5 전체 수행이 명시돼 있어 풀 파이프라인으로 고정
- 선행 재사용 판단: `output/마켓-대시보드에서-이번주-인사이트-요약해줘/final/final-artifact.md`를 참조 입력으로 재사용
- 재사용 근거: 2026-07-31 생성본으로 30일 이내이며, 동일한 주간 마켓 인텔리전스 브리핑 요약 범주라 범위 중첩이 높음

## Task Type 판별
- 선택된 type: `research-report`
- score:
  - `research-report`: 0/7
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
- 선택 근거: 직접 매칭된 type trigger는 없으나 default type 이 `research-report`이고, 요청 내용이 주간 시장 브리핑 요약에 해당함

## 활성 멤버 목록
- alpha(조사)
- gamma(팩트체크)
- delta(시각화)
- beta(보고서)

## 위험 플래그
- 고위험(사내 대시보드 데이터 사용): `member-alpha` 에게 `scripts/dashboard_fetch.py` 기반 `market` 대시보드 조회를 배정
- 처리 규칙: `termination.high_risk_override_enabled=false` 이므로 AUTO 모드에서 Notion/Slack 배포를 포함해 자동 진행

## Assignments
- `member-gamma`: `2026-W32` 마켓 인텔리전스 원문과 직전 참고 산출물을 대조해 핵심 주장, 수치, 시점 표현의 검증 로그를 작성한다.
- `member-alpha`: `market` 대시보드 `api/report` 와 `api/keywords` 원문을 조회해 이번 주 핵심 인사이트, 반복 트렌드, 실행 우선순위를 분석한다. source URL 과 fetched_at 을 명시한다.
- `member-delta`: alpha 분석을 바탕으로 이번 주 핵심 이슈의 영향 흐름을 Mermaid 다이어그램으로 정리하고 실행 우선순위 표를 만든다.
- `member-beta`: gamma, alpha, delta 산출물을 종합해 경영진이 바로 읽을 수 있는 주간 리포트 초안을 작성한다.

## Execution Order
1. `member-gamma`
2. `member-alpha`
3. `member-delta`
4. `member-beta`

## Dependency Map
- `member-gamma`: `output/마켓-대시보드에서-이번주-인사이트-요약해줘/final/final-artifact.md`
- `member-alpha`: `output/마켓-대시보드에서-이번주-인사이트-요약해줘/final/final-artifact.md`
- `member-delta`: `output/마켓-인텔리전스-이번-리포트-알려줘/member-alpha/analysis-report.md`
- `member-beta`: `output/마켓-인텔리전스-이번-리포트-알려줘/member-gamma/fact-check-log.md`, `output/마켓-인텔리전스-이번-리포트-알려줘/member-alpha/analysis-report.md`, `output/마켓-인텔리전스-이번-리포트-알려줘/member-delta/visuals.md`

## Expected Outputs
- `member-gamma/fact-check-log.md`: 핵심 주장 및 시점 표현 검증 로그
- `member-alpha/analysis-report.md`: 주간 인사이트 분석 보고서
- `member-delta/visuals.md`: 이슈 구조도와 우선순위 표
- `member-beta/draft-report.md`: 최종 리포트 초안

자동 확정 후 Phase 2 진입 - 2026-08-05 12:06
