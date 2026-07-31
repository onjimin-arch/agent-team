# SQL Reader Skill

## Purpose
member-alpha가 다른 부서가 제공하는 SQL DB(REST 게이트웨이 경유 예정)를 **조회 전용(SELECT-only)**으로
사용하는 데 필요한 안전 규칙을 제공한다.

## When to Use
Team Lead가 SQL 데이터 조회가 필요한 assignment를 줄 때만 사용한다.

## 현재 상태 (중요 업데이트)
애초 "다른 부서 SQL DB"로 요청됐던 실제 데이터소스는 자유 SQL 쿼리 게이트웨이가 아니라 **고정된
4개 GET 엔드포인트를 가진 사내 ERP REST API**로 확인됐다 — 그 데이터소스는 이제
`.claude/skills/erp-reader/SKILL.md` + `scripts/erp_fetch.py`를 사용한다. 이 스킬(sql-reader)과
`scripts/sql_guard.py`는 이후 정말로 **자유 SELECT 쿼리를 허용하는 별도 DB 게이트웨이**가 생길
경우를 위해 남겨둔 것이며, 현재는 실제 사용처가 없다.

## 실제 조회 스크립트(`scripts/sql_read.py`)는 아직 없다
`team-config.yaml`의 `external_data_sources.sql_gateway.enabled`가 `false`인 동안은 실제 게이트웨이
호출부가 구현되지 않은 상태다 — 부서가 엔드포인트 URL·인증 헤더 형식·요청/응답 스키마를 아직 확정하지
않았기 때문이다. 이 기간 동안 SQL 조회가 필요한 assignment를 받으면:
1. 데이터를 임의로 지어내거나 추측하지 않는다.
2. `WS/member-alpha/analysis-report.md`에 "SQL 게이트웨이 미구현 — 조회 불가"로 명시한다.
3. Team Lead에 에스컬레이션한다.

`sql_gateway.enabled`가 `true`로 바뀌고 `scripts/sql_read.py`가 존재하면, 이 스킬 문서의 명령
레퍼런스 섹션이 실제 사용법으로 갱신되어 있을 것이다.

## SELECT-only 안전 검증 규칙 (지금도 유효 — `scripts/sql_guard.py`)
`scripts/sql_read.py`가 구현된 뒤에도, **모든 쿼리는 실행 전에 반드시 `sql_guard.py`의
`validate_select_only()` 검증을 통과해야 한다**:

```bash
# 독립적으로 쿼리 하나를 미리 검증해볼 수 있다
python scripts/sql_guard.py --query "SELECT * FROM orders WHERE created_at > '2026-01-01'"
```

검증 규칙:
- 앞뒤 공백·SQL 주석(`--`, `/* */`)을 제거한 뒤 `SELECT`로 시작해야 한다.
- 세미콜론(`;`)으로 이어지는 두 번째 statement가 있으면 차단한다(단일 SELECT문만 허용).
- `INSERT / UPDATE / DELETE / DROP / ALTER / TRUNCATE / CREATE / GRANT / REVOKE / EXEC / MERGE` 등
  변경성 키워드가 포함되어 있으면(문자열 리터럴 내부가 아닌 SQL 키워드 위치에서) 차단한다.

**중요 — 이 검증은 최선 노력(best-effort) 문자열 검사이지 진짜 보안 경계가 아니다.** 실제 안전장치는
게이트웨이 쪽 계정에 read-only 권한만 부여하는 것이며, 이 스킬의 검증은 그 위에 얹는 추가 방어선일
뿐이다 — 게이트웨이 계정 권한 설정 여부를 Team Lead가 부서 쪽에 반드시 확인해야 한다.

## 인용 원칙
조회 결과를 사용할 때는 사용한 쿼리 원문, 조회 시각, (알 수 있다면) 대상 테이블/뷰 이름을 분석
결과에 함께 인용한다.
