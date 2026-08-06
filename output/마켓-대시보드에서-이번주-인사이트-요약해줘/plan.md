자동 확정된 slug: 마켓-대시보드에서-이번주-인사이트-요약해줘

# 마켓 대시보드 이번주 인사이트 요약 계획

## Task Summary
- 업무 설명: 마켓 대시보드에서 이번주 인사이트 요약
- 워크스페이스: `output/마켓-대시보드에서-이번주-인사이트-요약해줘`
- 실행 모드: AUTO
- 기준 주차: `2026-W31` 요청분
- 데이터 접근 전략: `2026-W31` 리포트 부재 시 최신 게시 주차(`2026-W30`)를 근거 데이터로 사용하고, 이번 주 미게시 상태 자체를 리스크로 함께 보고

## Task Type 판별
- 선택된 type: `research-report`
- score:
  - `research-report`: 1/7 (`시장` 매칭)
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
- 선택 근거: `시장` 키워드가 유일하게 매칭됐고, 요청 목적이 코드/설계/정책 대응이 아닌 시장 인텔리전스 요약이므로 `research-report`를 적용

## 활성 멤버 목록
- alpha(조사)
- gamma(팩트체크)
- delta(시각화)
- beta(보고서)

## 위험 플래그
- 고위험(사내 대시보드 데이터 사용): `member-alpha` 에게 `scripts/dashboard_fetch.py` 기반 `market` 대시보드 조회를 배정
- 처리 규칙: AUTO 모드에서는 Phase 1~4 자동 진행, Phase 5에서 Notion 저장은 즉시 실행하고 Slack 등 나머지 외부 배포는 승인 대기 알림만 발송

## Assignments
- `member-gamma`: 마켓 인텔리전스의 최신 공개 리포트와 직전 주차 리포트를 원문 기준으로 정리하고, 이번 주(`2026-W31`) 리포트 미게시 사실을 raw source 로그에 남긴다.
- `member-alpha`: `market` 대시보드 `api/report` 및 `api/keywords`를 조회해 최신 게시 주차의 핵심 변화와 이번 주 미게시 리스크를 분석한다. 대시보드 원문과 해석을 분리하고 source URL, fetched_at을 명시한다.
- `member-delta`: alpha 분석을 바탕으로 이번 주 인사이트 스캔용 Mermaid 다이어그램과 핵심 수치/트렌드 표를 작성한다.
- `member-beta`: gamma·alpha·delta 산출물을 종합해 경영진/실무진이 바로 읽을 수 있는 인사이트 요약 초안을 작성한다.

## Execution Order
1. `member-gamma`
2. `member-alpha`
3. `member-delta`
4. `member-beta`

## Dependency Map
- `member-gamma`: 선행 의존성 없음
- `member-alpha`: `output/마켓-대시보드에서-이번주-인사이트-요약해줘/member-gamma/fact-check-log.md`
- `member-delta`: `output/마켓-대시보드에서-이번주-인사이트-요약해줘/member-alpha/analysis-report.md`
- `member-beta`: `output/마켓-대시보드에서-이번주-인사이트-요약해줘/member-gamma/fact-check-log.md`, `output/마켓-대시보드에서-이번주-인사이트-요약해줘/member-alpha/analysis-report.md`, `output/마켓-대시보드에서-이번주-인사이트-요약해줘/member-delta/visuals.md`

## Expected Outputs
- `member-gamma/fact-check-log.md`: 마켓 대시보드 최신/직전 주차 raw source 및 미게시 상태 기록
- `member-alpha/analysis-report.md`: 이번 주 인사이트 분석 보고서
- `member-delta/visuals.md`: 인사이트 구조도와 핵심 수치 테이블
- `member-beta/draft-report.md`: 최종 요약 초안

자동 확정 후 Phase 2 진입 - 2026-07-31 15:49
