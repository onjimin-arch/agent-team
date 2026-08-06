# Quick Query Skill

## Purpose
"새 작업" 없이 들어온 단순 정보 조회 요청을 alpha·beta·gamma 등 멤버 fan-out 없이 **Team Lead가
직접** 처리하는 경량 경로. `dept-dashboard-reader`/`dept-notion-reader`/`sql-reader`/
`shared/web-research`가 이미 제공하는 조회 스크립트를 그대로 호출하고, Phase 1~6(계획→실행→리뷰→
통합→배포→회고)을 전부 생략한다.

## When to Use
CLAUDE.md Phase 0 에서 Team Lead가 이번 요청을 "quick_query"로 판별했을 때만 이 스킬을 따른다.
판별 기준(`team-config.yaml`의 `task.quick_query`)은 다음과 같다:

- 요청에 `task.quick_query.triggers`(조회/확인해줘/얼마/몇 건/언제/알려줘, 또는 ERP·현장·AX·마켓
  인텔리전스·노션 같은 데이터소스 이름)가 있다.
- 동시에 `task.quick_query.report_signal_triggers`(분석/보고서/리서치/전략/계획/설계/타당성 등)가
  **없거나 약하다** — 즉 "이 숫자/사실 하나만 알려줘" 수준이지 "정리된 산출물"을 원하는 게 아니다.
- 애매하면(두 신호가 비슷하게 매칭되면) 추측하지 말고 인터랙티브 승인 버튼으로 사용자에게 직접
  묻는다: "이 요청을 [빠른 조회]로 처리할까요, 아니면 [정식 리포트]로 처리할까요?" (아래 "인터랙티브
  승인" 절차, `scripts/slack_approval.py --options "빠른 조회,정식 리포트"`). 응답에 따라 분기한다.

## 실행 절차
1. **데이터소스 식별**: 요청 문장에서 어떤 소스가 필요한지 판단한다.
   - 사내 부서 대시보드(ERP/현장/AX/마켓 인텔리전스 등) → `dept-dashboard-reader` 스킬 →
     `scripts/dashboard_fetch.py`
   - 타 부서 Notion → `dept-notion-reader` 스킬 → `scripts/notion_fetch.py`
   - 자유 SELECT 쿼리 게이트웨이가 실제로 열려 있다면 → `sql-reader` 스킬 → `scripts/sql_guard.py`
   - 사내 데이터가 아니라 외부 사실 확인이 필요하면 → `shared/web-research` 스킬 (WebSearch/WebFetch)
   - 필요한 소스가 여러 개면 순차로 호출한다. 어느 스킬도 요청을 커버하지 못하면(예: "⏳ 스펙 확인
     필요" 상태의 대시보드) 데이터를 지어내지 말고 "{소스명} 조회 불가 — 스펙 미확인"으로 명시한 뒤
     그대로 사용자에게 답한다.
2. **직접 호출**: 멤버를 거치지 않고 Team Lead가 해당 스킬의 지침대로 Bash 로 스크립트를 실행한다.
3. **감사 로그 작성 (필수)**: `output/{slug}/quick-query-log.md` 에 아래 형식으로 기록한다.
   ```md
   # Quick Query Log

   **요청**: {사용자 원문}
   **판별**: quick_query (report_signal 미충족 / 사용자 확인 결과: {빠른 조회|정식 리포트})
   **사용 소스**: {예: ERP 대시보드 api/external/board}
   **source_url**: {스크립트가 반환한 source_url}
   **fetched_at**: {스크립트가 반환한 fetched_at}

   ## 답변
   {최종적으로 사용자에게 전달한 요약}
   ```
   이 파일의 존재 자체가 slack-bridge(`agent_runner.py`)에게 "quick-query 경로로 정상 완료됨"을
   알리는 신호다 — 반드시 작성해야 Slack 쪽 완료 처리가 올바르게 동작한다.
4. **민감 데이터 승인 게이트**: 이번 조회에 `scripts/dashboard_fetch.py`를 사용했다면
   (`team-config.yaml`의 `termination.high_risk_if_dashboard_used: true` 규칙과 동일한 대상),
   `high_risk_override_enabled: true` 인 동안은 답변을 보내기 전에 인터랙티브 승인을 받는다:
   ```
   python scripts/slack_approval.py --channel "{슬랙 채널}" \
     --question "이 조회 결과({대시보드명})를 공유해도 될까요?" \
     --options "승인,거부" --timeout-sec 900
   ```
   - `answered: true, choice: "승인"` → 5번으로 진행.
   - `answered: true, choice: "거부"` → 답변을 보내지 않고 quick-query-log.md에 "거부됨"으로 기록,
     사용자에게는 "승인이 거부되어 결과를 공유하지 않습니다"로만 답한다.
   - `answered: false`(타임아웃) → 기존 CLAUDE.md 규칙과 동일하게 **보류** — 결과를 자동으로 보내지
     않고, quick-query-log.md에 "승인 대기 중 타임아웃 — 사람이 직접 확인 필요"로 기록한다.
   `high_risk_override_enabled: false` 인 동안은 이 게이트를 건너뛰고 바로 5번으로 진행한다
   (CLAUDE.md "사내 대시보드 데이터 사용 시 승인 규칙"과 동일한 마스터 스위치를 공유).
5. **응답 전달**: `output/{slug}/slack-notification.json` 을 Phase 5 와 동일한 Block Kit 스키마로
   작성한다(간단한 section 블록 1~2개면 충분 — 풀 리포트처럼 메타데이터 헤더 전체를 채울 필요 없음).
   `slack-bridge/app.py`가 이 파일을 그대로 읽어 스레드에 재포스팅한다. 별도로
   `scripts/slack_publish.py`를 호출할 필요는 없다(중복 발송 방지 — Phase 5 배포 규약과 동일하게
   파일만 남기면 bridge가 발송을 책임진다).

## 하지 않는 것
- 워크스페이스 하위에 `member-*/` 폴더나 `plan.md`/`review-log.md`(Phase 3 리뷰 로그)를 만들지 않는다.
- Phase 3(격리 리뷰)·Phase 5(배포 다중 엔드포인트)·Phase 6(팀 역량 회고)를 실행하지 않는다 — 이 경로
  자체가 그 무게를 줄이기 위한 것이다.
- `final/final-artifact.md`를 만들지 않는다(만들면 오히려 풀 리포트로 오인된다).

## 관련 스킬
- `.claude/skills/dept-dashboard-reader/SKILL.md`
- `.claude/skills/dept-notion-reader/SKILL.md`
- `.claude/skills/sql-reader/SKILL.md`
- `.claude/skills/shared/web-research/SKILL.md`
