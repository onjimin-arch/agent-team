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
스크립트 코드는 수정할 필요 없다. `담당(owner)`/`최종 확인일(last_verified)`은 이 대시보드의
스펙을 확인해 준 부서 담당자(문의처)와 그 시점을 기록한다 — Phase 6-1이 90일 이상 지난 항목을
재확인 대상으로 플래그하는 데 쓰인다.

| 대시보드 | 상태 | base_url | key_env | 엔드포인트 | 담당(owner) | 최종 확인일 | 민감도/주의사항 |
|---|---|---|---|---|---|---|---|
| ERP (손익/실적) | ✅ 사용 가능 | `http://10.10.190.25:8000` | `ERP_API_KEY` | `api/external/board`(전사 손익, `ym` 파라미터), `api/external/b2b`(B2B 실손익), `api/external/loadshop`(로드샵 실손익), `api/external/input`(월별 손익 입력/추정 폼 — **`manual_saved:false`인 미래월은 "목표"가 아니라 전월 캐리포워드 예측치**, 목표로 오인 금지), `api/external/business-performance`(✅ 배포 확인됨 2026-08-14 — 분기/월/년 사업 실적: `revenue`/`cost`/`profit`/`ebitda` + 수행건수 `total_cnt`/`b2b_cnt`/`ls_cnt`, `period=month\|quarter\|year` 기본 quarter. **`from`/`to` 모두 생략(2023년~현재 전체)은 30초 타임아웃** — 1년 단위(4개 분기)로는 확인됨, 여러 해가 필요하면 연도별로 나눠 호출) | - | 2026-08-14 | 전사 손익·조직별 마진 등 민감 재무 데이터. Phase 5 외부 배포 전 Team Lead가 민감도 재확인. **`business-performance`의 `revenue`/`cost`/`profit`/`ebitda`는 사업 실적(실제)이며 "26년 사업계획" 목표치와는 다른 데이터** — 목표 대비 질문에는 아직 쓸 수 없음(별도 엔드포인트 미확보) |
| AX | ✅ 사용 가능 | `https://10.10.70.81:8011` (자가서명 인증서 — `--ca-cert certs/ax_server.pem` 필수) | `AX_API_KEY` | `api/v1/export/cases`(AX 사례 데이터 — 업무별 리소스(빈도·인력·투입시간)·절감률 + `dept_name`/`created_at`/`updated_at`, 선택 파라미터 `unanalyzed=true`시 AI 미분석 업무만), `api/v1/export/reports`(부서 보고서/KPI 스냅샷), `api/v1/export/departments`(부서명(`name`)·현재 구성원 수(`headcount`)·최초조사 구성원 수(`survey_headcount`)·월별 인원 변동 이력(`monthly_headcount`) — 부서별 리소스 기준선 산출). 공통 선택 파라미터 `dept`(부서 ID — **한글 부서명**, 예: `채널비즈니스팀`. `finance` 같은 영문 코드 아님) | - | 2026-08-19 | 키는 scope(`cases`/`reports`/`departments`)별 권한 분리 — 해당 scope 없으면 403. `cases`/`reports`/`departments` 세 엔드포인트 모두 현재 키로 200 확인됨(2026-08-19). reports에는 부서 보고서 본문(HTML)이 포함될 수 있음, 외부 배포 전 내용 확인 |
| 현장 | ✅ 사용 가능 | `https://crm.ax.barogo.io` | `FIELD_API_KEY` | `api/external/dashboard`(바로고·모아라인·딜버 배송 실적 종합 — "바모딜". `ym`만 주면 월간, `date`만 주면 해당 일자만(`period.mode`가 `monthly`/`daily`로 바뀜 — 둘 다 주면 `ym` 우선), `sido` 선택(지역 필터)) | - | 2026-08-14 | 배송 건수(전체/C2C/B2B)·수행 라이더 수. 응답 `sensitivity` 필드가 `general`로 확인됨(브랜드별·지역별 집계 — 개인정보 없음). **`rider`(수행 라이더 수) 필드는 사람 단위 중복제거가 안 된 것으로 강하게 추정됨(2026-08-14 검증: 7월 서울 일별 6일 평균×31일 ≈ 월간 총합, 4%밖에 안 차이 남 — 진짜 유니크 인원이면 훨씬 작아야 함) — "N명"을 "고유 인원수"로 단정하지 말고 "라이더-일 합산으로 추정"이라고 명시. 정확한 유니크 인원이 필요하면 현장 API 담당자에게 별도 확인 필요. 표준 CA 인증서라 `--ca-cert` 불필요 |
| 인사 | ⏳ 스펙 확인 필요 | - | - | - | - | - | 개인정보(급여·평가 등) 포함 가능성이 높음 — 스펙 확인 시 접근 범위·마스킹 필요 여부를 반드시 함께 확인 |
| 마켓 인텔리전스 | ✅ 사용 가능 | `https://barogo-intel.vercel.app` | `MARKET_API_KEY` | `api/report`(주차 리포트 본문, `week` 필수 예: `2026-W30`, `locale` 선택 `global`/`kr`/`tech`), `api/archive/search`(아카이브 검색, `weekFrom`/`weekTo`/`company`/`keyword`/`q`/`locale` 모두 선택), `api/keywords`(키워드 목록, `locale` 선택) | - | - | 공개 Vercel 호스팅 — **현재 서버측 인증 미구현**(누구나 접근 가능). 추후 X-API-Key 추가 예정이며 우리는 이미 헤더를 보내므로 그때 가서 클라이언트 변경 불필요. 인증서는 표준 CA 발급이라 `--ca-cert` 불필요 |
| 브랜드물류 (요기·땡배달) | ✅ 사용 가능 | `http://10.10.190.25:8080` | `B2B_API_KEY` | `api/external/pnl`(화주사×월 손익, `ym` 또는 `from`+`to`, `brand` 선택), `api/external/pnl_region`(화주사×시도×월 손익, 위 파라미터 + `brand` 선택), `api/external/quality`(화주사×월 수행품질, 위 파라미터), `api/external/meta`(브랜드·기간 커버리지·리소스 목록, 파라미터 없음) | - | 2026-08-14 | `pnl`/`pnl_region`/`quality` = 민감(내부·상업 — 화주사별 마진 구조 노출). **외부(투자자/언론/정부) 반출 전 데이터오너 승인 필수**(데이터오너 요청사항). `meta`만 일반. 개인정보·상점 식별자 없음(화주사=브랜드 단위 집계, `brand`는 `요기배달`/`땡배달`). 데이터 커버리지 2025-12-01~전일, 픽업(출발지) 기준. 표준 CA 인증서라 `--ca-cert` 불필요 |
| 법무 | ⏳ 스펙 확인 필요 | - | - | - | - | - | 소송·계약 등 기밀 정보 포함 가능성 — 스펙 확인 시 접근 승인 절차가 별도로 필요한지 반드시 확인 |
| 커넥트운영팀 | ✅ 사용 가능 | `http://10.10.50.31:5000` | `BEMIN_API_KEY` | `api/external/summary`(금주 핵심 수치), `api/external/daily`/`weekly`/`monthly`(일·주·월별 실적, 전체 기간 반환, 파라미터 없음), `api/external/revenue`/`revenue-daily`(주별/일별 매출), `api/external/churn`(이탈 위험 협력사, `week` 선택 예: `week=117`), `api/external/management-fee`(관리비 수령률, `week` 선택) + `/weeks`(주차 목록), `api/external/baemin-fee`(배민 관리비 수령률, `week` 선택) + `/weeks`, `api/external/partners`(협력사 리스트+주차별 완료건수, `weeks` 선택 기본 12 또는 `all`) | - | 2026-08-14 | 협력사ID/명 + 내부 담당자 이름 포함. 사업자번호·대표자명·핸드폰번호·입금계좌번호·은행명·이메일 6개 필드는 승인 전까지 응답에서 제외됨(추후 포함 결정 시 민감으로 재분류 필요) — 현재는 일반. 표준 CA 인증서라 `--ca-cert` 불필요 |

"⏳ 스펙 확인 필요" 대시보드는 아직 호출할 수 없다 — Team Lead가 assignment로 줘도 alpha는 데이터를
지어내지 말고 "{부서명} 대시보드 스펙 미확인 — 조회 불가"로 명시한 뒤 에스컬레이션한다.

## ERP 호출 예시
```bash
export ERP_API_KEY=erp_xxx
python scripts/dashboard_fetch.py --base-url http://10.10.190.25:8000 \
  --path api/external/board --key-env ERP_API_KEY --query ym=2026-07
```
사업 실적(분기별 매출/비용/영업이익/EBITDA + 수행건수)은 `board`가 아니라 `business-performance`를 쓴다:
```bash
python scripts/dashboard_fetch.py --base-url http://10.10.190.25:8000 \
  --path api/external/business-performance --key-env ERP_API_KEY \
  --query period=quarter --query from=2023-Q1
```
`period`는 `month`/`quarter`/`year`(기본 `quarter`), `from`/`to`는 `period`와 같은 형식(월 `2024-06`,
분기 `2024-Q2`, 년 `2024`) — 둘 다 생략하면 2023년~현재 전체를 반환한다. 건수 데이터가 해당 기간에
없으면 `0`이 아니라 `null`로 온다(실제 0건과 구분) — `null`을 0으로 임의 치환하지 않는다.

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

부서 인원 현황이 필요하면 `departments`를 쓴다(응답 필드: `name`/`headcount`/`survey_headcount`/
`monthly_headcount`):
```bash
python scripts/dashboard_fetch.py --base-url https://10.10.70.81:8011 \
  --path api/v1/export/departments --key-env AX_API_KEY \
  --ca-cert certs/ax_server.pem --query dept=채널비즈니스팀
```
`departments`는 `cases`/`reports`와 별도 scope다 — scope 권한이 없는 키로 호출하면 401이 아니라
403이 온다(키 자체는 유효하지만 이 scope 권한이 없다는 뜻). 403이 나면 재시도하지 말고 "AX 관리
탭에서 `cases`/`reports`/`departments` 세 scope로 키 재발급 필요"로 Team Lead에 보고한다.

## 현장 호출 예시
```bash
export FIELD_API_KEY=barogo_xxx
# 월간(2026-07 전체): ym만 지정 — date를 같이 줘도 무시되고 ym 기준 월간으로 응답됨(2026-08-14 검증)
python scripts/dashboard_fetch.py --base-url https://crm.ax.barogo.io \
  --path api/external/dashboard --key-env FIELD_API_KEY \
  --query ym=2026-07 --query sido=서울
# 특정 하루만: ym을 빼고 date만 지정하면 period.mode가 daily로 바뀜
python scripts/dashboard_fetch.py --base-url https://crm.ax.barogo.io \
  --path api/external/dashboard --key-env FIELD_API_KEY \
  --query date=2026-07-01 --query sido=서울
```
`sido`는 선택 파라미터(생략 시 전국 집계로 추정 — 실제 생략 동작은 미확인이므로 전국 데이터가
필요하면 우선 생략 없이 확인 후 사용, 전국 조회는 Redash 부하로 타임아웃 잦음). `rider` 필드는
중복제거 안 된 것으로 추정되니 위 레지스트리 표 주의사항을 반드시 참고. 이 API는 반복 호출에
불안정(Redash 백엔드 타임아웃 빈발) — 짧은 시간에 여러 날짜를 연속 조회하지 않는다.

## 마켓 인텔리전스 호출 예시
```bash
export MARKET_API_KEY=mkt_xxx   # 서버가 아직 검증하지 않지만 스크립트 요구사항상 값은 채워야 함
python scripts/dashboard_fetch.py --base-url https://barogo-intel.vercel.app \
  --path api/report --key-env MARKET_API_KEY --query week=2026-W30 --query locale=kr
```

## 브랜드물류 호출 예시
```bash
export B2B_API_KEY=b2b_xxx
python scripts/dashboard_fetch.py --base-url http://10.10.190.25:8080 \
  --path api/external/pnl --key-env B2B_API_KEY --query ym=2026-07
```
`brand` 파라미터로 `요기배달`/`땡배달` 중 하나만 필터할 수 있다(생략 시 둘 다). 구간 조회는
`ym` 대신 `--query from=2026-07-01 --query to=2026-07-15`. `pnl`/`pnl_region`/`quality`는
민감(내부·상업) 데이터이므로, 조회 결과를 외부로 반출하는 산출물에 쓸 때는 데이터오너 승인이
먼저 필요하다는 점을 assignment에 명시한다.

## 커넥트운영팀 호출 예시
```bash
export BEMIN_API_KEY=bemin_xxx
python scripts/dashboard_fetch.py --base-url http://10.10.50.31:5000 \
  --path api/external/summary --key-env BEMIN_API_KEY
```
`daily`/`weekly`/`monthly`는 파라미터 없이 전체 기간을 반환한다. `churn`/`management-fee`/`baemin-fee`는
`--query week=117`로 주차를 지정한다(생략 시 최신 주차). `partners`는 `--query weeks=1`(또는 `all`).

## 인용 원칙
조회 결과를 분석 결과에 사용할 때는 `source_url`(호출한 엔드포인트 전체 URL)과 `fetched_at`을
반드시 함께 인용한다. 원문 수치와 alpha 자신의 해석·분석을 명확히 구분해서 기술한다.
조회된 수치가 부분 조회거나 시점이 오래된 경우 "추정"으로 명시하고, 조회되지 않은 항목을 알고 있는
배경지식으로 채우지 않는다.

**필드 매칭 검증(중요)**: 질문에 답하기 전에, 가져온 필드가 실제로 질문 조건에 부합하는지 먼저
확인한다 — "그럴듯하게 가까운 숫자"를 그냥 가져다 쓰지 않는다. 예:
- 응답에 `manual_saved`/`tag`/`editable` 같은 상태 플래그가 있으면 반드시 확인한다.
  `manual_saved: false`나 `tag: "전월"`(전월 캐리포워드) 값을 실제 확정치·목표치인 것처럼
  제시하면 안 된다 — "이 값은 아직 미확정 추정치(전월 캐리포워드)"라고 명시한다
  (2026-08-14 ERP `input` 오답 사례: 8~12월 미입력 예측치를 "사업계획 목표"로 잘못 제시함 — 진짜
  목표 데이터는 `input`이 아니라 별도 엔드포인트에 있었음).
- 질문이 특정 조건(기간 단위, 지역, 최소 건수 등)을 명시하면, 가져온 필드의 정의가 정확히 그
  조건과 일치하는지 파라미터·응답 메타(`period.mode`/`period.label` 등)로 재확인한다. 예를 들어
  "7월 한 달 기준"인지 "특정 하루 기준"인지 애매하면, 파라미터를 바꿔 실제로 값이 달라지는지
  테스트해서 그 API가 무엇을 집계하는지 확인한다 — 짐작하지 않는다.
- 딱 맞는 필드가 없으면 "이 조건에 정확히 맞는 데이터는 없고, 가장 가까운 {필드명}은 {값}이다"라고
  차이를 명시한다. 조건에 안 맞는 걸 알면서 그대로 답으로 제시하지 않는다.

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
