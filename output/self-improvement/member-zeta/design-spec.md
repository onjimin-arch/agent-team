# Design Spec — CLAUDE.md PATCH-03·04·05

생성자: member-zeta | 생성시각: 2026-05-26 | 버전: v1

---

## 1. 작업 컨텍스트

- 대상 파일: `CLAUDE.md`
- 수정 섹션: 3곳 (Workspace Protocol / Phase 1 선행 체크 / Phase 1-0)
- 제약: 섹션 단위 패치만 허용. 전체 파일 교체 금지.
- 패치 간 충돌 리스크: PATCH-04가 1-0 앞에 삽입되므로, PATCH-05(1-0 내용 교체)와
  삽입 위치가 인접함 → 적용 순서 명시 필요 (03 → 04 → 05 순서).

---

## 2. 워크플로우 정의

```
PATCH-03 적용 (Workspace Protocol 섹션 수정)
  ↓
PATCH-04 적용 (Phase 1 앞에 새 섹션 삽입)
  ↓
PATCH-05 적용 (Phase 1-0 내용 교체)
```

---

## 3. 구현 스펙

### PATCH-03 — Workspace Protocol 새 작업 트리거

**수정 위치**: `### 새 작업 트리거` 섹션, 기존 2번 항목 교체

**변경 전:**
```
2. 사용자에게 슬러그를 제시하고 확인/수정 요청.
```

**변경 후:**
```
2. `team-config.yaml` 의 `termination.human_approval` 값에 따라 분기:
   - `human_approval: false` → 슬러그 자동 확정. 사용자 확인 생략.
     `WS/plan.md` 상단에 "자동 확정된 slug: {slug}" 기록.
   - `human_approval: true` → 사용자에게 슬러그를 제시하고 확인/수정 요청.
```

---

### PATCH-04 — Phase 1 선행 체크 삽입

**수정 위치**: `## Phase 1: Planning Protocol` 섹션의 `### 1-0.` 앞에 삽입

**삽입할 내용:**
```
### 1-선행. 유사 워크스페이스 재사용 체크
`task.types` 판별 전에 실행한다.

1. `output/` 하위 디렉터리 목록을 확인한다.
2. 현재 task 키워드와 기존 slug를 단순 문자열 비교한다.
3. 유사 slug 발견 시:
   - 해당 `WS/final/final-artifact.md` 존재 여부 확인.
   - 존재하면:
     - 생성일이 **30일 이내** AND task 범위가 **80% 이상** 겹친다고 판단되면:
       → 사용자에게 재사용 여부 제안:
         "기존 리서치({slug}, {날짜})를 참조하겠습니까? [Y/N]"
       → Y: 해당 산출물을 alpha 입력으로 전달, gamma 탐색 범위 축소.
       → N: 신규 탐색 진행.
     - 위 조건 미충족 시 → 신규 탐색 진행.
4. 유사 slug 없으면 → 기존 Phase 1 프로세스 그대로 진행.
```

---

### PATCH-05 — Phase 1-0 Scoring 방식 교체

**수정 위치**: `### 1-0. Task Type 자동 판별` 섹션 전체 내용 교체

**변경 전 (현재 전체):**
```
`team-config.yaml` 의 `task.types` 를 순회하며, 사용자 요청 문장에 각 type 의
`triggers` 키워드가 하나라도 포함되면 해당 type 으로 분기합니다. 매칭이 없으면
`default: true` 인 type 을 사용합니다. 선택된 type 의 `members` 목록만 가동하고
나머지 멤버는 비활성화합니다.

- 사용자가 `"새 작업 [code-review] ..."` 처럼 **대괄호 태그**를 앞에 붙이면
  trigger 키워드보다 우선합니다.
- 선택 결과(type · 근거 · 활성 멤버)는 `WS/plan.md` 에 명시합니다.
```

**변경 후:**
```
`task.types` 를 scoring 방식으로 판별한다:

1. 모든 task type 의 triggers 를 순회한다.
2. 사용자 요청 문장에서 각 type 의 매칭 keyword 수를 카운트한다.
3. `score = 매칭 keyword 수 / 해당 type 의 전체 trigger 수` (비율 기준)
4. 가장 높은 score 의 type 을 선택한다.

동점 처리:
- 대괄호 태그(`[code-review]` 등)가 명시된 경우 → 태그 우선 (score 무시).
- 동점이며 태그 없음 → 동점 type 목록을 사용자에게 제시하고 선택 요청.
- 모든 type score = 0 → `default: true` 인 type 사용.

결과를 `WS/plan.md` 에 기록:
- 선택된 type
- 각 type 별 score (예: `research-report: 2/8, code-review: 1/4`)
- 선택 근거 (최고 score / 태그 / 동점 처리)
- 활성 멤버 목록
```

---

## 적용 순서 및 충돌 분석

| 순서 | 패치 | 위치 | 충돌 위험 |
|------|------|------|---------|
| 1 | PATCH-03 | Workspace Protocol § 새 작업 트리거 | 없음 |
| 2 | PATCH-04 | Phase 1 § 1-0 앞 삽입 | PATCH-05와 인접 — 반드시 04 먼저 |
| 3 | PATCH-05 | Phase 1-0 내용 교체 | PATCH-04 삽입 후 1-0 위치 변경 없음 |

PATCH-04 삽입 후 `### 1-0.` 헤더는 그대로 유지되므로 PATCH-05 적용에 문제 없음.
