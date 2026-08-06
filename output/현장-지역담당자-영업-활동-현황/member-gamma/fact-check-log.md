Creator: member-gamma
Created: 2026-08-05 13:16
Version: 1.0

# 검증 요약

- 이번 `research-report` 사이클에서 gamma는 팩트체크보다 원천 데이터 수집 역할로 실행했다.
- 수집 범위는 `2026-08` 현재월 누적 전국 스냅샷, `2026-07` 전국 월간 기준선, `경남` 지역 spot-check 1건이다.
- 아래 수치는 해석 없이 현장 대시보드 원문을 그대로 옮긴 것이다.

# 항목별 검증 결과

| 원문 주장 | 검증 상태 | 출처 | 비고 |
|---|---|---|---|
| `2026-08` 전국 최근 누적 스냅샷을 확보했다. | 확인됨 | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-08-05&ym=2026-08` | 기간 `2026-08-01`~`2026-08-04`, 전체 `1,099,163`, B2B `164,351`, 라이더 `43,630` |
| `2026-07` 전국 월간 기준선을 확보했다. | 확인됨 | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07` | 기간 `2026-07-01`~`2026-07-31`, 전체 `7,820,669`, B2B `1,112,534`, 라이더 `354,060` |
| `경남`의 `2026-07` 지역 spot-check가 전국 응답의 `bySido.경남`과 일치한다. | 확인됨 | `https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07&sido=%EA%B2%BD%EB%82%A8` | 전체 `1,113,326`, B2B `103,620`, 라이더 `48,281` |

## 수집 원문 1

- 출처: 바로고 현장 종합 대시보드
- 날짜: 2026-08-05
- 원문 URL: `https://crm.ax.barogo.io/api/external/dashboard?date=2026-08-05&ym=2026-08`
- 원문 발췌: `period=2026-08-01~2026-08-04`, `totals.total=1099163`, `totals.c2c=934812`, `totals.b2b=164351`, `totals.rider=43630`, `bySido.경기.total=269019`, `bySido.서울.total=102451`, `bySido.전남.total=89923`, `sensitivity=general`

## 수집 원문 2

- 출처: 바로고 현장 종합 대시보드
- 날짜: 2026-08-05
- 원문 URL: `https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07`
- 원문 발췌: `period=2026-07-01~2026-07-31`, `totals.total=7820669`, `totals.c2c=6708135`, `totals.b2b=1112534`, `totals.rider=354060`, `bySido.경기.total=1911645`, `bySido.서울.total=729366`, `bySido.전남.total=639679`, `sensitivity=general`

## 수집 원문 3

- 출처: 바로고 현장 종합 대시보드
- 날짜: 2026-08-05
- 원문 URL: `https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07&sido=%EA%B2%BD%EB%82%A8`
- 원문 발췌: `period=2026-07-01~2026-07-31`, `filter_sido=경남`, `totals.total=1113326`, `totals.b2b=103620`, `totals.rider=48281`

# 수정 권고

- alpha는 `지역담당자 활동 현황`을 개인별 영업 로그가 아니라 `권역 관할 성과 프록시`로 해석해야 한다.
- alpha는 `2026-08` 4일 누적치와 `2026-07` 전체월 총량을 직접 비교하지 말고 일평균, B2B 비중, 라이더당 처리량으로 정규화해 비교해야 한다.
- beta는 최종 보고서에 내부 현장 대시보드 출처와 집계 기간(`2026-08-01`~`2026-08-04`)을 명시해야 한다.
