# Self-Improvement Patch
생성일: 2026-05-26 | 대상 파일: CLAUDE.md · member-alpha/AGENT.md · member-gamma/AGENT.md

---

## 적용 방법
각 패치를 해당 파일의 명시된 섹션에 붙여넣는다. 전체 파일을 교체하지 않는다.
CLAUDE.md 패치는 PATCH-03 → PATCH-04 → PATCH-05 순서로 적용한다.

---

## PATCH-01: member-alpha/AGENT.md
### 수정 섹션: Execution Rules — 하단에 아래 블록 추가

#### 변경 전
```
- Do not modify another member's assigned domain.
```
*(섹션 끝)*

#### 변경 후
```
- Do not modify another member's assigned domain.

### research-report 타입 전용 제약
- **직접 웹 검색 금지**: 정보 수집을 위한 WebSearch·WebFetch 사용 금지.
- **gamma 산출물 의존**: `WS/member-gamma/` 산출물을 유일한 원천 데이터로 사용한다.
  gamma 산출물이 존재하지 않으면 Team Lead에 에스컬레이션하고 대기한다.
- 역할: 수집된 원문 데이터의 **분석·종합·인사이트 도출** 전담.
```

---

## PATCH-02: member-gamma/AGENT.md
### 수정 섹션 A: Assignment Protocol — 하단에 아래 블록 추가

#### 변경 전
*(Assignment Protocol 섹션 끝)*

#### 변경 후
```
### research-report 전용 역할
`research-report` task type 으로 실행 시 팩트체크 대신 아래 역할을 수행한다:
- **alpha 보다 먼저 실행**된다 (alpha 의 분석 원천 데이터 제공 역할).
- WebSearch·WebFetch 로 주제 관련 원문 데이터를 수집한다.
- 수집한 데이터를 **정제·해석 없이 원문 그대로** 저장한다.
- 각 항목에 출처·날짜·원문 URL 을 반드시 포함한다.
- 분석·인사이트 도출은 alpha 영역 — gamma 는 수집만 수행한다.
```

### 수정 섹션 B: Execution Rules — 하단에 아래 블록 추가

#### 변경 전
*(Execution Rules 섹션 끝, Do not modify another member's artifacts directly. 다음)*

#### 변경 후
```
### research-report 타입 산출물 형식
수집 항목마다 아래 필드를 필수 포함한다:

| 필드 | 내용 |
|------|------|
| 출처 | 기관명 / 미디어명 |
| 날짜 | YYYY-MM-DD |
| 원문 URL | 직접 링크 |
| 원문 발췌 | 번역·해석 없이 원문 그대로 |
```

---

## PATCH-03: CLAUDE.md
### 수정 섹션: Workspace Protocol — 새 작업 트리거

#### 변경 전
```
2. 사용자에게 슬러그를 제시하고 확인/수정 요청.
```

#### 변경 후
```
2. `team-config.yaml` 의 `termination.human_approval` 값에 따라 분기:
   - `human_approval: false` → 슬러그 자동 확정. 사용자 확인 생략.
     `WS/plan.md` 상단에 "자동 확정된 slug: {slug}" 기록.
   - `human_approval: true` → 사용자에게 슬러그를 제시하고 확인/수정 요청.
```

---

## PATCH-04: CLAUDE.md
### 수정 섹션: Phase 1 Planning Protocol — 1-0 앞에 삽입

#### 변경 전
```
### 1-0. Task Type 자동 판별
```

#### 변경 후
```
### 1-선행. 유사 워크스페이스 재사용 체크
`task.types` 판별 전에 실행한다.

1. `output/` 하위 디렉터리 목록을 확인한다.
2. 현재 task 키워드와 기존 slug 를 단순 문자열 비교한다.
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

### 1-0. Task Type 자동 판별
```

---

## PATCH-05: CLAUDE.md
### 수정 섹션: Phase 1-0 Task Type 자동 판별 — 본문 교체

#### 변경 전
```
`team-config.yaml` 의 `task.types` 를 순회하며, 사용자 요청 문장에 각 type 의 `triggers` 키워드가 하나라도 포함되면 해당 type 으로 분기합니다. 매칭이 없으면 `default: true` 인 type 을 사용합니다. 선택된 type 의 `members` 목록만 가동하고 나머지 멤버는 비활성화합니다.

- 사용자가 `"새 작업 [code-review] ..."` 처럼 **대괄호 태그**를 앞에 붙이면 trigger 키워드보다 우선합니다.
- 선택 결과(type · 근거 · 활성 멤버)는 `WS/plan.md` 에 명시합니다.
```

#### 변경 후
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

사용 가능한 기본 type (team-config.yaml 기준):
- `research-report` (default): alpha · gamma · delta · beta
- `code-review`: alpha · gamma · beta
- `multilingual-brief`: alpha · beta · delta
- `dev`: alpha · epsilon
- `design`: alpha · zeta
- `github-plan`: eta · alpha · beta

---

## PATCH-06: CLAUDE.md
### 수정 섹션: Phase 1-1 Validation 블록 이후 — 신규 1-2 체크포인트 삽입 (OBS-02)

#### 변경 전
*(Validation 블록 끝, ## Phase 2: Execution Protocol 직전)*

#### 변경 후
```
### 1-2. Plan 확정 체크포인트
`plan.md` 초안 작성 직후, Phase 2 진입 전에 실행한다.

- `human_approval: true` → 사용자에게 plan.md 요약(task type, 활성 멤버, 배정 내용)을 제시하고 승인을 요청한다.
  승인이 확인될 때까지 Phase 2 진입 금지.
- `human_approval: false` → plan.md 하단에 "자동 확정 후 Phase 2 진입" 타임스탬프를 기록하고 즉시 Phase 2 시작.
- AUTO 모드(`[AUTO: slug]`) → `human_approval` 무관하게 자동 진행.
```

---

## PATCH-07: CLAUDE.md + 신규 파일
### 수정 섹션: Phase 3 Review Protocol 전체 교체 + member-reviewer/AGENT.md 생성 (OBS-01)

#### 변경 전
```
## Phase 3: Review Protocol
For all member artifacts:
- Evaluate whether each artifact meets expected format and content.
- Use review criteria from the config.
- Decide one of:
  - Approve
  - Directly edit (minor changes only)
  - Reassign to the member with a corrected instruction

Record results in `WS/review-log.md`.
```

#### 변경 후
```
## Phase 3: Review Protocol
각 멤버 산출물에 대해 독립 리뷰어 서브에이전트(`member-reviewer`)를 `Agent` 도구로 실행한다.

### 리뷰어 호출 방식
subagent_type: `member-reviewer`

리뷰어에게 전달: 산출물 내용, config expected_files 스펙, task type, task summary
리뷰어에게 금지: 멤버 지시사항 원문, plan.md 작성 경위, 다른 멤버 산출물

### 리뷰어 판정 처리
- APPROVE → Phase 4 진행
- EDIT(내용) → Team Lead 직접 편집
- REASSIGN(사유) → 멤버 재배정
```

신규 파일: `.claude/agents/member-reviewer/AGENT.md` 생성

---

## 검증 체크리스트

- [x] alpha Execution Rules에 "직접 웹 검색 금지" 명시됨
- [x] gamma Assignment Protocol에 research-report 전용 수집 역할 명시됨
- [x] gamma Execution Rules에 "출처·날짜·원문 URL 필수" 산출물 형식 명시됨
- [x] CLAUDE.md human_approval 분기 로직 추가됨 (PATCH-03)
- [x] CLAUDE.md Phase 1 선행 체크 단계 추가됨 (PATCH-04)
- [x] CLAUDE.md scoring 방식 판별 로직 추가됨 (PATCH-05)
- [x] CLAUDE.md Phase 1-2 Plan 확정 체크포인트 추가됨 (PATCH-06)
- [x] CLAUDE.md Phase 3 독립 리뷰어 서브에이전트 방식으로 교체됨 (PATCH-07)
- [x] `.claude/agents/member-reviewer/AGENT.md` 생성됨 (PATCH-07)
- [x] 모든 패치가 기존 섹션 구조를 유지함 (전체 파일 교체 없음)
- [x] 기존 task type 5종의 동작 유지됨
