# Quick Query Log

**요청**: 26년 7월 기준 서울 지역에 1건 이상 배달한 라이더 알려줘
**판별**: quick_query (quick query 신호 `알려줘` 매칭, report_signal 미충족)
**사용 소스**: 현장 대시보드 `api/external/dashboard` 서울 필터 월별 집계
**source_url**: https://crm.ax.barogo.io/api/external/dashboard?date=2026-07-31&ym=2026-07&sido=%EC%84%9C%EC%9A%B8
**fetched_at**: 2026-08-14T05:31:24.215642+00:00

## 답변
- `2026-07` 기준 서울 지역에서 1건 이상 배달한 `수행 라이더 수`는 `34,832명`이다.
- 근거: 현장 대시보드 응답의 `bySido.서울.rider = 34832`.
- 이 데이터소스는 라이더 개인 식별정보나 명단은 제공하지 않아 `어떤 라이더인지`까지는 조회할 수 없다.
