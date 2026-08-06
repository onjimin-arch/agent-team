Creator: member-gamma
Created: 2026-08-05 12:53
Version: 1.0

# 검증 요약

- 수집 범위: `2026-W21`부터 `2026-W32`까지 최근 약 3개월의 국내 배달 시장 시그널 중, 직접 조회 가능한 `W29~W32` 주간 리포트와 `W21~W26` 아카이브 검색 결과를 원문 기반으로 정리했다.
- 검증된 3대 흐름: `라이더/규제 리스크의 직접화`, `플랫폼 수직통합과 표준연동 강화`, `효율·비용 프레임 경쟁 심화`.
- 직접 조회 URL:
  - `https://barogo-intel.vercel.app/api/report?week=2026-W29&locale=kr` (`fetched_at=2026-08-05T03:52:20.681886+00:00`)
  - `https://barogo-intel.vercel.app/api/report?week=2026-W30&locale=kr` (`fetched_at=2026-08-05T03:51:40.723010+00:00`)
  - `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr` (`fetched_at=2026-08-05T03:51:40.759546+00:00`)
  - `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr` (`fetched_at=2026-08-05T03:51:40.732418+00:00`)
  - `https://barogo-intel.vercel.app/api/archive/search?weekFrom=2026-W20&weekTo=2026-W32&locale=kr` (`fetched_at=2026-08-05T03:51:27.659052+00:00`)
  - `https://barogo-intel.vercel.app/api/keywords?locale=kr` (`fetched_at=2026-08-05T03:51:27.579620+00:00`)
- 데이터 공백: `api/archive/search`는 이번 조회에서 `matchedWeeks=['2026-W26','2026-W25','2026-W24','2026-W23','2026-W22','2026-W21']`만 반환했다. 따라서 `W27~W28`는 별도 아카이브 원문 대신 `W29`, `W30` 리포트의 catch-up 문구를 참고해야 한다.

# 항목별 검증 결과

| 원문 주장 | 검증 상태 | 출처 | 비고 |
|---|---|---|---|
| `W32` 리포트는 최신 게시본이며 기사 15건 기준이다 | 확인됨 | `api/report?week=2026-W32&locale=kr` | `isLatest=true`, `articleCount=15` |
| `W31`은 배달앱 규제 집행 국면과 바로고의 B2B 안전지대 포지셔닝을 강조한다 | 확인됨 | `api/report?week=2026-W31&locale=kr` | 공정위 과징금 심의, 우버-DH 심사 전략 포함 |
| `W30`은 쿠팡나우와 퀵커머스 전선 확대를 핵심 변화로 본다 | 확인됨 | `api/report?week=2026-W30&locale=kr` | `쿠팡나우`, `배민 B마트`, 퀵커머스 직접 언급 |
| `W29`은 대행사 라이더 근로자성 판결을 바로고 직접 리스크로 해석한다 | 확인됨 | `api/report?week=2026-W29&locale=kr` | `배달 대행사 라이더도 근로자 첫 판결` 명시 |
| 5월 후반 아카이브는 배민 매각/우버-DH M&A를 다수 기사로 다룬다 | 확인됨 | `api/archive/search?weekFrom=2026-W20&weekTo=2026-W32&locale=kr` | `W21~W23` 대표 기사 다수 |
| 6월 중순 아카이브는 공정위 심의 재개와 동의의결 기각을 집중적으로 다룬다 | 확인됨 | 동일 | `W26` 기사 15건 중 대표 기사 3건이 동일 축 |
| 시장 키워드 사전에는 `quick_commerce`, `ai_optimization`, `rider_rights`, `delivery_fee_cap`, `platform_labor_law`가 포함된다 | 확인됨 | `api/keywords?locale=kr` | 이후 분석 축 분류 근거로 사용 가능 |

### W29 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-07-13 |
| 원문 URL | `https://barogo-intel.vercel.app/api/report?week=2026-W29&locale=kr` |
| 원문 발췌 | `배달 대행사 라이더도 근로자 첫 판결 (7/8)... 바로고를 포함한 배달대행 모델 전체에 파급.` |

### W30 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-07-20 |
| 원문 URL | `https://barogo-intel.vercel.app/api/report?week=2026-W30&locale=kr` |
| 원문 발췌 | `쿠팡이츠가 '쿠팡나우' 상표권을 출원하며... 퀵커머스 직매입 모델이 확대되면 배달대행 의존도가 줄고 플랫폼 자체 라이더·인프라가 강화된다.` |

### W31 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-07-27 |
| 원문 URL | `https://barogo-intel.vercel.app/api/report?week=2026-W31&locale=kr` |
| 원문 발췌 | `공정위가 배민에 최대 5,100억원 과징금 심의를 시작했고... 바로고는 '규제 안전지대의 독립 B2B 배달대행'이라는 포지셔닝을 적극 활용해야 한다.` |

### W32 원문 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-08-03 |
| 원문 URL | `https://barogo-intel.vercel.app/api/report?week=2026-W32&locale=kr` |
| 원문 발췌 | `서울고법 라이더 근로자성 판결이 업체 상고 포기로 최종 확정됐다... 배민은 바로고를 포함한 배달대행 6개사와 라이더 위치추적 표준연동을 완료했다.` |

### W21~W26 아카이브 대표 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API archive |
| 날짜 | 2026-05-13 ~ 2026-06-20 |
| 원문 URL | `https://barogo-intel.vercel.app/api/archive/search?weekFrom=2026-W20&weekTo=2026-W32&locale=kr` |
| 원문 발췌 | `2026-W21: 우버 '배민' 인수 검토`, `2026-W24: 쿠팡 정보유출 6,246억 충격`, `2026-W26: 배민·쿠팡 동의의결 기각` |

### 키워드 사전 기록

| 필드 | 내용 |
|---|---|
| 출처 | Barogo Intelligence API |
| 날짜 | 2026-08-05 조회 |
| 원문 URL | `https://barogo-intel.vercel.app/api/keywords?locale=kr` |
| 원문 발췌 | `quick_commerce`, `ai_optimization`, `rider_rights`, `delivery_fee_cap`, `platform_labor_law`, `local_commerce` |

# 수정 권고

1. action theme 1: alpha는 `W29`와 `W32` 근거를 묶어 `라이더/노무 리스크 정량화`를 최우선 액션으로 제시해야 한다.
2. action theme 2: `W30~W32`의 `쿠팡나우`, `표준연동`, `효율 경쟁` 근거를 묶어 `표준연동 + SLA 상품화` 액션으로 연결해야 한다.
3. action theme 3: `W31~W32`의 규제 집행 및 비용 구조 기사 근거를 사용해 `가맹점 비용 방어 영업` 액션으로 명시해야 한다.
4. `W27~W28` 직접 아카이브가 비어 있음을 문서에 명시하고, `W29`와 `W30`의 catch-up 문구로만 연결해야 한다.
5. 수치 인용은 원문에 나온 값만 사용하고, 감마 로그 안에 근거가 이미 기록된 항목만 후속 문서에 올려야 한다.
