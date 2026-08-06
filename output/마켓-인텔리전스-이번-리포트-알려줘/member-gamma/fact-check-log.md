Creator: member-gamma
Created: 2026-08-05 12:07
Version: 1.0

# 검증 요약

- `2026-W32` 마켓 인텔리전스 리포트는 실제로 게시돼 있으며 `isLatest=true`, `generatedAt=2026-08-03T13:30:00+09:00`, `articleCount=15`로 확인됐다.
- 직전 기준선 `2026-W31` 리포트도 게시본으로 확인됐으며 `generatedAt=2026-07-27T13:30:00+09:00`, `articleCount=16`이다.
- `api/keywords?locale=kr` 기준 키워드 체계에는 `platform_labor_law`, `rider_rights`, `ai_optimization`, `ma_acquisition`, `fair_trade_delivery` 등이 포함돼 있어 이번 주 핵심 이슈 분류와 정합하다.
- `api/archive/search?weekFrom=2026-W29&weekTo=2026-W32&locale=kr` 는 결과가 비어 있었다. 이번 산출물은 `api/report` 원문 두 건과 기존 최종본 재사용 근거를 중심으로 작성해야 한다.

# 항목별 검증 결과

| 원문 주장 | 검증 상태 | 출처 | 비고 |
|---|---|---|---|
| `2026-W32` 주간 리포트가 존재하고 최신 게시본이다 | 확인됨 | `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr` | `isLatest=true`, `alreadyConfirmed=true` |
| `2026-W32` 리포트 생성 시점은 2026-08-03이고 기사 수는 15건이다 | 확인됨 | 동일 API 응답 | 보고서 본문 첫머리와 JSON 필드가 일치 |
| 이번 주 최상위 이슈 중 하나는 서울고법 라이더 근로자성 판결 최종 확정이다 | 확인됨 | 동일 API 응답 | W32 1위 이슈로 직접 명시 |
| 이번 주 최상위 이슈 중 하나는 배민-배달대행 6개사 위치추적 표준연동 완료다 | 확인됨 | 동일 API 응답 | W32 2위 이슈에 바로고 포함 6개사 명시 |
| 우버의 딜리버리히어로 148억달러 인수 공식 확정이 이번 주 핵심 이슈다 | 확인됨 | 동일 API 응답 | W32 3위 이슈에 148억달러, 2027년 하반기 종결 전망 명시 |
| 부릉 AI 배차로 이동시간 30% 단축은 경쟁사 효율화 벤치마크로 제시된다 | 확인됨 | 동일 API 응답 | W32 4위 이슈에 `12.7분→9.2분`, `30% 단축` 명시 |
| 배달대행비는 40% 감소했고 배달앱 이용료는 40.9~59% 증가했다 | 확인됨 | 동일 API 응답 | W32 5위 이슈에 업종별 수치 명시 |
| 직전 주차 W31의 핵심 프레임은 `배달앱 규제 안전지대`였다 | 확인됨 | `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr` | W31 1위 이슈와 한 줄 요약에서 직접 확인 |
| W32는 W31 대비 `규제 기회`에서 `직접 법무 리스크` 쪽으로 무게중심이 이동했다 | 부분 일치 | W31/W32 API 응답 비교 | 사실 자체는 각 주차 원문에 있으나, `이동` 표현은 분석 문장으로 써야 함 |
| 이전 재사용 산출물은 W30 기반 인사이트 요약이었다 | 확인됨 | `output/마켓-대시보드에서-이번주-인사이트-요약해줘/final/final-artifact.md` | 재사용 참고본의 메타데이터와 본문 확인 |

원문 발췌:

1. 출처: 마켓 인텔리전스 API
   날짜: 2026-08-03
   원문 URL: `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr`
   원문 발췌: `서울고법 라이더 근로자성 판결이 업체측 상고 포기로 최종 확정됐다` / `배민은 바로고를 포함한 배달대행 6개사와 라이더 위치추적 표준연동을 완료` / `우버의 딜리버리히어로 148억달러 인수도 공식 확정`

2. 출처: 마켓 인텔리전스 API
   날짜: 2026-07-27
   원문 URL: `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr`
   원문 발췌: `규제 폭풍의 중심은 배달앱이다. 배달대행 사업자인 바로고는 오히려 규제 외 안전지대에 있다`

3. 출처: 마켓 인텔리전스 API
   날짜: 2026-08-05 조회
   원문 URL: `https://barogo-intel.vercel.app/api/keywords?locale=kr`
   원문 발췌: `platform_labor_law`, `rider_rights`, `ai_optimization`, `ma_acquisition`, `fair_trade_delivery`

# 수정 권고

- `이번 주 리포트`라는 표현은 `2026-W32`, 생성일 `2026-08-03`, 기사 수 `15건`으로 구체화한다.
- W31 대비 변화는 `원문 비교에 따른 해석`으로 명시하고, 원문 사실처럼 단정하지 않는다.
- `규제 안전지대`라는 W31 프레임을 그대로 반복하지 말고, W32에서는 `배달대행사 직접 리스크 + 표준연동 기회`로 초점을 옮겨야 한다.
