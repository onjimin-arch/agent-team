자동 확정된 slug: 이번-바로고-현장-배송-실적이랑

Phase 0 판별: task_pipeline - quick_query 신호(`현장`, `실적`, `알려줘`)는 강하지만, 런타임 지시가 Phase 1-5 전체 수행을 명시했고 `최근 배달 플랫폼 업계 동향 뉴스`까지 함께 종합해야 하므로 정식 리포트 파이프라인으로 진행

# 이번 바로고 현장 배송 실적과 업계 동향 계획

## Task Summary
- 업무 설명: 이번 주 바로고 현장 배송 실적이랑, 최근 배달 플랫폼 업계 동향 뉴스도 같이 찾아서 알려줘
- 워크스페이스: `output/이번-바로고-현장-배송-실적이랑`
- 실행 모드: AUTO

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
- 선택 근거: 모든 type score 가 0이므로 `default: true` 인 `research-report` 선택

## 활성 멤버 목록
- alpha(조사)
- gamma(팩트체크)
- delta(시각화)
- beta(보고서)

## Assignments
- `member-gamma`: 최근 배달 플랫폼 업계 동향의 원문 데이터를 수집한다. `2026-W31`, `2026-W32` 마켓 인텔리전스 리포트와 아카이브/키워드 조회 결과를 바탕으로 규제, 표준연동, 경쟁사 효율화, 수수료 구조 변화 신호를 날짜·출처·URL과 함께 정리한다.
- `member-alpha`: `member-gamma` 원문 수집 로그와 현장 대시보드 원문을 바탕으로 이번 주 기준 배송 실적을 분석한다. 현장 대시보드는 `2026-08` 누적 스냅샷과 `2026-07` 기준선을 조회하고, 일평균/비중/라이더 생산성으로 정규화해 해석한다.
- `member-delta`: `member-alpha` 분석 결과를 시각자료로 재구성한다. 현장 실적 진단 흐름과 업계 뉴스가 바로고 의사결정으로 이어지는 흐름을 Mermaid 다이어그램 2개와 핵심 수치 표로 정리한다.
- `member-beta`: `member-alpha`, `member-gamma`, `member-delta` 산출물을 종합해 경영진 공유용 보고서 초안을 작성한다. 현장 실적 요약과 업계 뉴스 함의를 한 문서에 결합하고 즉시 실행 항목을 우선순위별로 정리한다.

## Execution Order
1. `member-gamma`
2. `member-alpha`
3. `member-delta`
4. `member-beta`

## Dependency Map
- `member-gamma`: 선행 의존성 없음
- `member-alpha`: `output/이번-바로고-현장-배송-실적이랑/member-gamma/fact-check-log.md`
- `member-delta`: `output/이번-바로고-현장-배송-실적이랑/member-alpha/analysis-report.md`
- `member-beta`: `output/이번-바로고-현장-배송-실적이랑/member-alpha/analysis-report.md`, `output/이번-바로고-현장-배송-실적이랑/member-gamma/fact-check-log.md`, `output/이번-바로고-현장-배송-실적이랑/member-delta/visuals.md`

## Expected Outputs
- `member-gamma/fact-check-log.md`: 최근 업계 동향 원문 수집 및 검증 로그
- `member-alpha/analysis-report.md`: 현장 배송 실적과 업계 함의를 결합한 분석 보고서
- `member-delta/visuals.md`: Mermaid 다이어그램 및 핵심 수치 테이블
- `member-beta/draft-report.md`: 최종 공유용 보고서 초안

## Risk Flags
- 고위험(사내 대시보드 데이터 사용): `member-alpha` 에게 `scripts/dashboard_fetch.py` 기반 현장 대시보드 조회를 배정
- 적용 메모: `termination.high_risk_override_enabled: false` 이므로 AUTO 모드에서 Notion/Slack 배포는 계속 진행

자동 확정 후 Phase 2 진입 - 2026-08-05 14:05
