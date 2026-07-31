# Dept Dashboard Reader Skill

## Purpose
member-alpha가 **사내 여러 부서의 손익/실적 대시보드 API**(ERP·현장·인사·AX·브랜드·법무 등)를
조회하는 데 필요한 대시보드 레지스트리와 민감정보 취급 원칙을 제공한다. 부서마다 별도 시스템이지만
같은 스크립트(`scripts/dashboard_fetch.py`)로 호출한다 — base URL·경로·인증 키만 다르다.

## When to Use
Team Lead가 특정 부서 대시보드 조회가 필요한 assignment를 줄 때만 사용한다.

## 공통 호출 방식
```bash
python scripts/dashboard_fetch.py \
  --base-url <레지스트리의 base_url> \
  --path <레지스트리의 엔드포인트 경로, 선행 슬래시 없이> \
  --key-env <레지스트리의 key_env> \
  --query ym=2026-07 \  # 필요한 경우, 여러 번 지정 가능
  --ca-cert certs/ax_server.pem   # 레지스트리에 ca_cert 가 명시된 대시보드만 추가 (자가서명 인증서 핀 고정)
```
인증은 `X-API-Key` 헤더로 고정되어 있다(`dashboard_fetch.py`가 강제). 401 응답을 받으면 키가
잘못됐거나 만료된 것이다 — 재시도하지 말고 Team Lead에 보고한다. 403 응답은 이 키에 해당
엔드포인트의 scope 권한이 없는 것이다 — 레지스트리에서 scope 요구사항을 확인한다.

**주의 (Git Bash/MSYS)**: `--path` 값 앞에 `/`를 붙이면 Git Bash가 유닉스 절대경로로 오인해 Windows
경로로 자동 변환해버려 요청이 깨진다. `--path`는 항상 **선행 슬래시 없이** 쓴다
(`api/external/board`, `/api/external/board` ❌).

## 대시보드 레지스트리
새 부서 대시보드의 스펙(base URL·인증 방식·엔드포인트)을 받으면 **이 표에 행을 추가**하고
`team-config.yaml`의 `external_data_sources.dashboards`에 `enabled: true` 항목을 추가한다.
스크립트 코드는 수정할 필요 없다.

| 대시보드 | 상태 | base_url | key_env | 엔드포인트 | 민감도/주의사항 |
|---|---|---|---|---|---|
| ERP (손익/실적) | ✅ 사용 가능 | `http://10.10.190.25:8000` | `ERP_API_KEY` | `api/external/board`(전사 손익, `ym` 파라미터), `api/external/b2b`(B2B 실손익), `api/external/loadshop`(로드샵 실손익), `api/external/input`(수익상세 입력폼, 가장 상세·복잡) | 전사 손익·조직별 마진 등 민감 재무 데이터. Phase 5 외부 배포 전 Team Lead가 민감도 재확인 |
| AX | ✅ 사용 가능 | `https://10.10.70.81:8011` (자가서명 인증서 — `--ca-cert certs/ax_server.pem` 필수) | `AX_API_KEY` | `api/v1/export/cases`(AX 사례 데이터), `api/v1/export/reports`(부서 보고서/KPI 스냅샷). 공통 선택 파라미터 `dept`(부서 ID — **한글 부서명**, 예: `채널비즈니스팀`. `finance` 같은 영문 코드 아님) | 키는 scope(`cases`/`reports`)별 권한 분리 — 해당 scope 없으면 403. reports에는 부서 보고서 본문(HTML)이 포함될 수 있음, 외부 배포 전 내용 확인 |
| 현장 | ⏳ 스펙 확인 필요 | - | - | - | - |
| 인사 | ⏳ 스펙 확인 필요 | - | - | - | 개인정보(급여·평가 등) 포함 가능성이 높음 — 스펙 확인 시 접근 범위·마스킹 필요 여부를 반드시 함께 확인 |
| 마켓 인텔리전스 | ✅ 사용 가능 | `https://barogo-intel.vercel.app` | `MARKET_API_KEY` | `api/report`(주차 리포트 본문, `week` 필수 예: `2026-W30`, `locale` 선택 `global`/`kr`/`tech`), `api/archive/search`(아카이브 검색, `weekFrom`/`weekTo`/`company`/`keyword`/`q`/`locale` 모두 선택), `api/keywords`(키워드 목록, `locale` 선택) | 공개 Vercel 호스팅 — **현재 서버측 인증 미구현**(누구나 접근 가능). 추후 X-API-Key 추가 예정이며 우리는 이미 헤더를 보내므로 그때 가서 클라이언트 변경 불필요. 인증서는 표준 CA 발급이라 `--ca-cert` 불필요 |
| 브랜드 | ⏳ 스펙 확인 필요 | - | - | - | - |
| 법무 | ⏳ 스펙 확인 필요 | - | - | - | 소송·계약 등 기밀 정보 포함 가능성 — 스펙 확인 시 접근 승인 절차가 별도로 필요한지 반드시 확인 |

"⏳ 스펙 확인 필요" 대시보드는 아직 호출할 수 없다 — Team Lead가 assignment로 줘도 alpha는 데이터를
지어내지 말고 "{부서명} 대시보드 스펙 미확인 — 조회 불가"로 명시한 뒤 에스컬레이션한다.

## ERP 호출 예시
```bash
export ERP_API_KEY=erp_xxx
python scripts/dashboard_fetch.py --base-url http://10.10.190.25:8000 \
  --path api/external/board --key-env ERP_API_KEY --query ym=2026-07
```

## AX 호출 예시 (자가서명 인증서 — `--ca-cert` 필수)
```bash
export AX_API_KEY=ax_xxx
python scripts/dashboard_fetch.py --base-url https://10.10.70.81:8011 \
  --path api/v1/export/reports --key-env AX_API_KEY \
  --ca-cert certs/ax_server.pem --query dept=채널비즈니스팀
```
`certs/ax_server.pem`은 AX 서버(`10.10.70.81:8011`)가 실제로 제시하는 인증서를 그대로 저장해 둔
것이다(`openssl s_client -connect 10.10.70.81:8011 -showcerts`로 취득, 2028-09-24 만료). `--ca-cert`
없이 호출하면 `SSL: CERTIFICATE_VERIFY_FAILED`로 실패한다 — 인증서 검증을 끄는(curl -k류) 방식
대신 이 인증서를 신뢰 루트로 명시적으로 고정하는 방식을 쓴다.

## 마켓 인텔리전스 호출 예시
```bash
export MARKET_API_KEY=mkt_xxx   # 서버가 아직 검증하지 않지만 스크립트 요구사항상 값은 채워야 함
python scripts/dashboard_fetch.py --base-url https://barogo-intel.vercel.app \
  --path api/report --key-env MARKET_API_KEY --query week=2026-W30 --query locale=kr
```

## 인용 원칙
조회 결과를 분석 결과에 사용할 때는 `source_url`(호출한 엔드포인트 전체 URL)과 `fetched_at`을
반드시 함께 인용한다. 원문 수치와 alpha 자신의 해석·분석을 명확히 구분해서 기술한다.

## 승인 필요 (강제 규칙)
`dashboard_fetch.py`를 한 번이라도 사용한 사이클은 task type과 무관하게 Phase 5(외부 배포) 전
**사람 승인이 강제**된다 (`team-config.yaml` `termination.high_risk_if_dashboard_used: true`,
CLAUDE.md "사내 대시보드 데이터 사용 시 승인 규칙" 참조). alpha는 이 스킬을 사용하는 assignment를
받으면 Team Lead가 plan.md에 "고위험(사내 대시보드 데이터 사용)" 플래그를 기록했는지 신경 쓸 필요는
없다 — Team Lead의 책임이다. alpha는 그저 원문·해석을 정확히 구분해 기록하기만 하면 된다.

## 인증 방식이 다를 경우
이 스킬과 `dashboard_fetch.py`는 `X-API-Key` 헤더 방식을 전제로 한다. 새 부서 대시보드가 다른
인증 방식(OAuth, 세션 쿠키 등)을 쓴다면 이 스크립트로 호출할 수 없다 — Team Lead에 보고하고
별도 처리 방법을 결정한다.

자가서명 인증서(HTTPS)를 쓰는 대시보드는 인증 방식과 별개 문제다 — `--ca-cert`로 지원된다
(AX 참고). 새 대시보드가 자가서명 인증서를 쓴다면, 검증을 끄지 말고 그 서버가 제시하는 인증서를
받아 `certs/{부서}_server.pem`으로 저장한 뒤 레지스트리의 `ca_cert`에 경로를 기록한다.

## sql-reader 스킬과의 관계
이 대시보드들은 모두 고정된 GET 엔드포인트만 제공한다 — 자유 SQL 쿼리가 아니다. 만약 정말로 자유
SELECT 쿼리를 허용하는 DB 게이트웨이가 별도로 필요해지면 `.claude/skills/sql-reader/SKILL.md` +
`scripts/sql_guard.py`(SELECT-only 검증기)를 사용한다 — 현재는 미사용.
