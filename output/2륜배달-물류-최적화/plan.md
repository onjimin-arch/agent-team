자동 확정된 slug: 2륜배달-물류-최적화 (human_approval: false, "새 작업" 취지의 요청으로 판단)

# Plan: 2륜(이륜차) 라스트마일 배송 물류 최적화 프로젝트

## Task 요약
바로고 2륜 배달 물류 최적화 프로젝트(배차·경로·묶음배송·ETA·라이더 수급 5개 축) 지원.
이 워크스페이스는 Claude Desktop Projects + Notion(https://app.notion.com/p/barogohq/3c3363ae08db804e9e16f179cd53bf80)에서
이미 진행 중인 프로젝트를 이 agent-team 파이프라인에서 보조/병행하기 위한 것.
Custom instructions(프로젝트 지침) 전문은 사용자가 대화 중 제공 — 역할/도메인/포맷/제약/KPI 프레임워크는
아래 "프로젝트 지침 요약" 참조.

## Phase 0 판별
- quick_query 신호("확인해줘" 등) 약함, report_signal("분석","전략","계획") 존재 → task_pipeline(풀 파이프라인)으로 진행.

## Phase 1-0. Task Type 판별
- research-report: 매칭 3/7 (분석, 시장, 현황) = 0.43 — **최고 점수 & default**
- design: 매칭 2/8 (설계, 아키텍처) = 0.25
- mgmt-planning / strategy-newbiz / product-planning: 0/8~10
→ **선택: research-report** (alpha 조사 → gamma 팩트체크 → delta 시각화 → beta 보고서, 단 research-report
타입 특유 규칙상 실제 실행 순서는 gamma(원천수집) 선행 → alpha(분석) → delta(시각화) → beta(보고서))

## Notion 현황 조사 결과 (Team Lead가 Notion MCP로 직접 조회, 2026-08-24)
프로젝트 워크스페이스: "물류 최적화 프로젝트" (경영전략실 › 프로젝트 리스트)
- 트랙 4개(전략 프레임워크 / 5단계 게이트 / 데이터 파이프라인 / 비용 효율화) 동시 진행 중
- **Gate 1 — 정의·프레임워크 확정 (승인상태: 승인)**
  필요 산출물: ① 시장 변화·바로고 현황 정리 / ② AS-IS 정량 분석 / ③ 국내외 벤치마크(부릉·Meituan) /
  ④ 물류최적화 정의 문서 / ⑤ 라이더·상점 인터뷰 설계
  - ①의 "시장 변화" 부분: "배달 시장 흐름 정리(2017~2025+2026월별)"[확정], "배달 시장 종합 보고"[확정],
    "경쟁사 실적 통계(배달앱4사·배달대행3사 매출/점유율)"[내용 완성, 상태 미지정] — **이미 상세히 커버됨**
  - ①의 "바로고 현황" 부분: 전용 단독 문서는 아직 없음. 관련 내용은 Gate2 문서
    "바로고 2륜배달 물류 최적화 — 진행현황"(상태: 리뷰중)에 일부 존재 — Redash/Athena SQL 기반
    AS-IS 진단(Input-Decision-Output 8요소 프레임워크, B2B 자동취소율 ~15% vs 로드샵 ~0.8% 등).
    단 이 문서의 Section2(현황진단)는 Athena GROUP BY 오류로 미완, Section3(개발영역·순서)은 미착수.
- Gate 2 (팩터 우선순위·목표수준 합의): 검토중 (게이트키퍼 홍년·윤한)
- Gate 3~5: 대기

## 활성 멤버
alpha(조사) · gamma(팩트체크/원천수집) · delta(시각화) · beta(보고서)

## 환경 제약 확인
- 이 대화형 세션에는 MARKET_API_KEY/AX_API_KEY/NOTION_API_TOKEN 등 사내 대시보드·Notion 폴백 토큰 미설정
  → alpha의 dept-dashboard-reader(market/ax 대시보드) 직접 조회는 이 세션에서 불가.
  → Notion 조회는 MCP 커넥터로 가능(대화형 세션이므로 notion-fetch/notion-query-data-sources 직접 사용 가능,
    scripts/notion_fetch.py 폴백 불필요).
  → 내부 Redash/Athena(실제 배달 원장 SQL) 접근 권한 없음 — 이미 Notion에 있는 SQL 분석 결과보다 깊은
    내부 데이터 분석은 이 세션에서 재현 불가.

## 미결정 사항 (사용자 확인 필요 — 아래 대화에서 질문)
Gate1 산출물①의 "바로고 현황" 파트를 이 세션에서 무엇을 만들지가 불분명함:
1) 이미 있는 Notion 조각(경쟁사 실적 통계의 바로고 섹션 + 진행현황 문서의 AS-IS 요약)을 모아
   "바로고 현황(포지션)" 단독 문서로 통합·정리(신규 조사 없음, 통합 작업 위주)
2) 위 통합 + 외부 웹서치로 보강할 수 있는 부분만 gamma가 추가 조사(바로고 관련 최근 언론 보도,
   공개 IR/투자 자료 등 — 내부 SQL 데이터는 대체 불가)
3) 다른 범위 (사용자 지정)

## Phase 1-2 체크포인트
human_approval: false 이지만, 위 "미결정 사항"으로 인해 Phase 2(멤버 실행) 착수 전 사용자에게
직접 질문 후 진행 (에스컬레이션이 아니라 범위 확인).
