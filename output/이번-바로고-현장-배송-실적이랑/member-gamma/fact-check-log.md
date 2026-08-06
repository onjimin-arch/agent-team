Creator: member-gamma
Created: 2026-08-05 14:06
Version: 1.0

# 검증 요약

- 이번 `research-report` 사이클에서 gamma는 팩트체크보다 원천 데이터 수집 역할로 실행했다.
- 수집 범위는 `2026-W31`, `2026-W32` 마켓 인텔리전스 리포트와 아카이브/키워드 조회 결과, 그리고 이번 주 기준 현장 대시보드 원문 수치다.
- 이번 주 뉴스 프레임은 `배달앱 규제 안전지대`에서 `배달대행사 직접 리스크 + 표준연동 기회`로 이동했다.
- 아래 항목은 해석이 아니라 원문 근거 정리이며, 현장 실적은 원문 수치만 검증하고 해석은 alpha가 수행한다.

# 항목별 검증 결과

| 원문 주장 | 검증 상태 | 출처 | 비고 |
|---|---|---|---|
| `2026-W32` 리포트는 최신 게시본이며 기사 15건 기준이다 | 확인됨 | `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr` | `isLatest=true`, `generatedAt=2026-08-03T13:30:00+09:00`, `articleCount=15` |
| `2026-W31` 리포트는 직전 주차 기준선으로 비교 가능하다 | 확인됨 | `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr` | `generatedAt=2026-07-27T13:30:00+09:00`, `articleCount=16` |
| 이번 주 기준 현장 스냅샷은 `2026-08-01~2026-08-04` 누적 전체 `1,099,163건`, B2B `164,351건`, 라이더 `43,630명`이다 | 확인됨 | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-08-05&ym=2026-08` | `sensitivity=general`, 전국 집계 |
| 비교 기준선인 `2026-07` 전체월 실적은 전체 `7,820,669건`, B2B `1,112,534건`, 라이더 `354,060명`이다 | 확인됨 | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07` | 전국 월간 기준선 |
| 이번 주 최상위 리스크는 `배달대행 플랫폼업체` 대상 라이더 근로자성 판결 최종 확정이다 | 확인됨 | `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr` | 바로고와 동일 사업구조 직접 언급 |
| 이번 주 기회 신호는 배민-배달대행 6개사 위치추적 표준연동 완료다 | 확인됨 | 동일 | 바로고 포함 6개사 명시 |
| 우버의 딜리버리히어로 148억달러 인수 공식 확정이 구조 변화 신호다 | 확인됨 | 동일 | `2027년 하반기 종결` 전망 포함 |
| 부릉 AI 배차의 이동시간 30% 단축은 경쟁사 효율화 벤치마크다 | 확인됨 | 동일 | `12.7분 -> 9.2분`, `30% 단축` |
| 배달대행비 하락과 배달앱 이용료 상승의 비용 분화가 기사화됐다 | 확인됨 | 동일 | 피자/햄버거/샌드위치 업종 `-40%` vs `+40.9%` |
| 직전 주차 `W31`의 핵심 프레임은 배달앱 규제 강화와 바로고의 상대적 안전지대였다 | 확인됨 | `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr` | `규제 안전지대의 독립 B2B 배달대행` 문구 확인 |
| `api/archive/search?weekFrom=2026-W29&weekTo=2026-W32&locale=kr`는 결과가 비어 있다 | 확인됨 | `https://barogo-intel.vercel.app/api/archive/search?weekFrom=2026-W29&weekTo=2026-W32&locale=kr` | 최근 4주 아카이브 직접 매칭 없음 |
| 넓은 범위 아카이브에서는 배달앱 규제/과징금 관련 기사 묶음이 확인된다 | 확인됨 | `https://barogo-intel.vercel.app/api/archive/search?weekFrom=2026-W20&weekTo=2026-W32&locale=kr` | `2026-W26` 기사 다수 반환 |
| 키워드 사전에는 `ai_optimization`, `rider_rights`, `platform_labor_law`, `fair_trade_delivery`가 포함된다 | 확인됨 | `https://barogo-intel.vercel.app/api/keywords?locale=kr` | 이번 주 핵심 축 분류 근거 |

## 현장 실적 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | 바로고 현장 종합 대시보드 |
| 날짜 | 2026-08-05 조회 |
| 원문 URL | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-08-05&ym=2026-08` |
| 원문 발췌 | `period=2026-08-01~2026-08-04`, `totals.total=1099163`, `totals.c2c=934812`, `totals.b2b=164351`, `totals.rider=43630`, `sensitivity=general` |

| 필드 | 내용 |
|---|---|
| 출처 | 바로고 현장 종합 대시보드 |
| 날짜 | 2026-08-05 조회 |
| 원문 URL | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07` |
| 원문 발췌 | `period=2026-07-01~2026-07-31`, `totals.total=7820669`, `totals.c2c=6708135`, `totals.b2b=1112534`, `totals.rider=354060`, `sensitivity=general` |

## W32 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-08-03 |
| 원문 URL | `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr` |
| 원문 발췌 | `서울고법 라이더 근로자성 판결이 업체측 상고 포기로 최종 확정됐다` / `배민은 바로고를 포함한 배달대행 6개사와 라이더 위치추적 표준연동을 완료` / `우버의 딜리버리히어로 148억달러 인수도 공식 확정` / `부릉, AI 배차로 라이더 이동시간 30% 단축` |

## W31 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-07-27 |
| 원문 URL | `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr` |
| 원문 발췌 | `규제 폭풍의 중심은 배달앱이다. 배달대행 사업자인 바로고는 오히려 규제 외 안전지대에 있다` / `배민 최대 5,100억 과징금 심의` / `우버-DH 심사 쟁점은 멤버십·데이터·결제 연계` |

## 보강 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API archive |
| 날짜 | 2026-08-05 조회 |
| 원문 URL | `https://barogo-intel.vercel.app/api/archive/search?weekFrom=2026-W20&weekTo=2026-W32&locale=kr` |
| 원문 발췌 | `배민·쿠팡 '3600억' 상생안 퇴짜…수천억 과징금 위기` / `공정위, 배민·쿠팡 동의의결 '기각'…'배달앱 갑질' 제재 착수` / `'최혜대우 요구' 배민·쿠팡이츠, 공정위 심판대로` |

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-08-05 조회 |
| 원문 URL | `https://barogo-intel.vercel.app/api/keywords?locale=kr` |
| 원문 발췌 | `quick_commerce`, `ai_optimization`, `rider_rights`, `platform_labor_law`, `fair_trade_delivery`, `ma_acquisition` |

# 수정 권고

- alpha는 `이번 주 업계 뉴스`를 `직접 리스크(노무/법무)`, `기회(표준연동 영업)`, `경쟁 벤치마크(AI 배차)`, `비용 프레임(수수료 중립 메시지)`의 4축으로 정리하는 것이 적절하다.
- alpha는 현장 실적 비교에서 `8월 4일 누적치`와 `7월 전체월 기준선`의 기간 차이를 명시하고, 총량이 아니라 정규화 지표로 비교해야 한다.
- alpha는 `W31 -> W32` 변화가 원문 비교에 따른 해석임을 명시하고, `안전지대`라는 표현을 이번 주 사실처럼 반복하지 않아야 한다.
- beta는 최종 문서에서 `최근 뉴스`의 기준선을 `W31`, `W32` 두 주차와 8월 5일 조회 시점으로 구체화해야 한다.
