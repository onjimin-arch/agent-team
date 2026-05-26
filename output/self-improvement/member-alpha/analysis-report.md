# Analysis Report — BUG-01 역할 중복 분석 및 PATCH-01·02 초안

생성자: member-alpha | 생성시각: 2026-05-26 | 버전: v1

---

## 개요

현재 alpha·gamma의 역할 정의에서 웹 검색이 중복 수행되는 구간을 정확히 식별하고,
중복을 제거하는 AGENT.md 수정 패치 초안을 작성한다.

---

## 분석 결과

### 중복 구간 식별

**member-alpha (현재)**
- Assignment Protocol: "market and competitor research synthesis" — 리서치 명시
- Skills Reference: `shared/data-parser` — 외부 데이터 파싱 암시
- Constraints: "Stay within the market research and analysis domain" — 리서치 도메인 포함
- **웹 검색을 명시적으로 금지하는 조항 없음**

**member-gamma (현재)**
- Assignment Protocol: "Use WebSearch and WebFetch tools when a claim requires external verification"
- Skills & Tools: `web-research` — WebSearch·WebFetch 명시
- Execution Rules: "cross-checking numeric claims against public sources" — 수집 행위 포함

**중복 발생 지점**: research-report 타입에서 alpha가 리서치(=웹 검색)하고,
gamma가 그 결과를 재검색으로 검증 → 동일 소스를 두 번 방문하는 구조.

### 실행 순서 변경 필요

현재: alpha(조사) → gamma(팩트체크) → delta → beta
수정: gamma(수집) → alpha(분석) → delta → beta

gamma를 alpha보다 먼저 실행해야 alpha가 gamma 산출물을 입력으로 쓸 수 있음.
단, code-review 타입에서는 기존 순서 유지 (alpha 코드 스캔 → gamma 검증).

---

## 결론

PATCH-01은 alpha Execution Rules에 research-report 타입 전용 제약을 추가하는 방향,
PATCH-02는 gamma Assignment Protocol에 research-report 전용 수집 역할을 추가하는 방향이
기존 섹션 구조를 파괴하지 않으면서 역할을 분리하는 최소 침습적 방법이다.

---

## PATCH-01 초안: member-alpha/AGENT.md

### 수정 섹션: Execution Rules (하단 추가)

**추가할 내용:**
```markdown
### research-report 타입 전용 제약
- **직접 웹 검색 금지**: 정보 수집을 위한 WebSearch·WebFetch 사용 금지.
- **gamma 산출물 의존**: `WS/member-gamma/` 산출물을 유일한 원천 데이터로 사용한다.
  gamma 산출물이 존재하지 않으면 Team Lead에 에스컬레이션하고 대기한다.
- 역할: 수집된 원문 데이터의 **분석·종합·인사이트 도출** 전담.
```

---

## PATCH-02 초안: member-gamma/AGENT.md

### 수정 섹션 1: Assignment Protocol (code-review 전용 역할 섹션 직후 추가)

**추가할 내용:**
```markdown
### research-report 전용 역할
`research-report` task type 으로 실행 시 팩트체크 대신 아래 역할을 수행한다:
- **alpha보다 먼저 실행**된다 (alpha의 분석 원천 데이터 제공 역할).
- WebSearch·WebFetch 로 주제 관련 원문 데이터를 수집한다.
- 수집한 데이터를 **정제·해석 없이 원문 그대로** 저장한다.
- 각 항목에 출처·날짜·원문 URL 을 반드시 포함한다.
- 분석·인사이트 도출은 alpha 영역 — gamma 는 수집만 수행한다.
```

### 수정 섹션 2: Execution Rules (하단 추가)

**추가할 내용:**
```markdown
### research-report 타입 산출물 형식
수집 항목마다 아래 필드를 필수 포함한다:

| 필드 | 내용 |
|------|------|
| 출처 | 기관명 / 미디어명 |
| 날짜 | YYYY-MM-DD |
| 원문 URL | 직접 링크 |
| 원문 발췌 | 번역·해석 없이 원문 그대로 |
```
