# 팩트체크 로그 — 일반 업무·프로젝트 관리 시스템 기능 검증 (2025~2026)

작성: member-gamma (팩트체커)
검증 기간: 2026-06-18 기준 / 출처는 모두 2025~2026 공식 문서·헬프센터·릴리스 노트 우선
대상: Notion, Asana, Jira, ClickUp, Monday.com, Linear, Trello

---

## 검증 요약

**시스템별 한 줄 특징**
- **Notion**: 문서·DB 통합형. 2025년 Notion 3.0 "AI Agents"(자율 20분 작업)·Custom Agents(트리거/스케줄)·AI Meeting Notes로 AI 전면화. 승인 워크플로우는 **네이티브 approval 객체가 없고** 버튼+상태 속성+자동화로 구성. [1][12][13]
- **Asana**: 워크 매니지먼트 + 2025 "AI Studio"(노코드 AI 워크플로우 빌더)·AI Teammates. **네이티브 Approval(승인) 태스크 타입 보유**. [2][3]
- **Jira**: 이슈 트래킹/ITSM 강자. 2025년 "Rovo" AI 에이전트 도입(Premium/Enterprise 4~7월, Standard 10월). 승인은 **Jira Service Management의 네이티브 워크플로우 approval step**(단, 커스텀 필드 기반 설정 필요). [4][14]
- **ClickUp**: "올인원" 15종+ 뷰·AI 커스텀 필드·"Brain²" AI. 승인은 타임시트/상태(예: Awaiting Approval) 기반이 중심. [5]
- **Monday.com**: Work OS 플랫폼. 2025 "AI Blocks"(컬럼·자동화·워크플로우 빌더 공통)·"Digital Workforce"(일부 coming soon). [6]
- **Linear**: 제품 개발 특화 이슈 트래커. List/Board/Timeline 3종 뷰 중심(**캘린더·간트 네이티브 미제공**), 2026년 Linear Agent(Claude Code/Codex로 코드 작성). [7][8][15]
- **Trello**: 칸반 중심 경량 도구. Premium에서 Timeline/Calendar/Dashboard, Butler 자동화, Custom Fields/AI는 **Power-Up·Atlassian Intelligence 형태**. [9][16]

**전체 핵심 사실 요약**
1. **AI 기능은 전 제품이 2025~2026에 "에이전트(agent)" 단계로 진입**했다. 단순 요약/생성을 넘어 자율 실행·스케줄 트리거가 표준 마케팅 포인트가 됨(Notion Agents, Asana AI Studio/Teammates, Jira Rovo, Monday Digital Workforce, Linear Agent, ClickUp Brain²).
2. **네이티브 "승인(approval)" 기능은 제품별로 성격이 크게 다르다.** Asana(태스크 approval)·Jira Service Management(워크플로우 approval step)는 비교적 명확한 네이티브 승인을 가진다. 반면 Notion·Linear·Trello는 별도 approval 객체 없이 상태/버튼/Power-Up으로 구현한다 — 비교표 작성 시 가장 흔히 틀리는 지점.
3. **커스텀 필드의 깊이가 제품 정체성을 가른다.** Notion(관계형 relation·롤업 rollup 네이티브), ClickUp(통화·AI 필드 등 풍부), Monday(컬럼 타입 다양). 반면 Trello는 Custom Fields가 **Power-Up**으로 제공.
4. **Slack 연동은 7개 모두 지원**하나 깊이가 다르다. Linear는 양방향(@Linear 멘션으로 Slack 내 액션·프로젝트별 채널 자동 생성)으로 특히 강함.
5. **RI(총투입시간×반복성가중치) 식의 자동화 우선순위 정량 산정 + 가치사슬 시각화는 일반 PM 도구의 네이티브 기능이 아니다.** 이는 별도 카테고리인 **프로세스 마이닝(IBM Process Mining 등)** 영역으로, 평가 대상 앱의 차별점으로 강조 가능. [10][11]

---

## 항목별 검증 결과

범례: O=네이티브 지원 / △=부분·플러그인·애드온·유료 한정 / X=미지원(확인) / ?=공식 확인 불충분

### 1. 뷰 종류 (테이블·리스트 / 칸반 / 타임라인·간트 / 캘린더 / 갤러리·카드)

| 시스템 | 테이블·리스트 | 칸반 보드 | 타임라인·간트 | 캘린더 | 갤러리·카드 | 출처 |
|---|---|---|---|---|---|---|
| Notion | O | O | O(타임라인) | O | O | [1][12] |
| Asana | O | O | O(타임라인/간트) | O | △(보드 카드) | [17] |
| Jira | O | O | O(타임라인/로드맵) | O | △ | [4][14] |
| ClickUp | O | O | O(Timeline·Gantt) | O | △ | [5] |
| Monday | O | O | O(간트) | O | O | [6] |
| Linear | O(List) | O(Board) | O(Timeline=로드맵) | **X(네이티브 캘린더 없음)** | X | [8][15] |
| Trello | △(리스트=보드 컬럼) | O(핵심) | △(Premium Timeline) | △(Premium/Calendar Power-Up) | O(카드) | [9][16] |

주: Linear는 **캘린더·간트 뷰 네이티브 미제공**, Timeline(로드맵)만 제공 — 비교 시 명확히 구분 필요. [15]

### 2. 저장된 뷰(saved views) / 뷰별 필터·정렬·그룹핑 유지

| 시스템 | 지원 | 비고 | 출처 |
|---|---|---|---|
| Notion | O | DB별 다중 뷰, 뷰마다 필터/정렬/그룹 저장 | [1] |
| Asana | O | 저장된 뷰·필터·정렬 | [17] |
| Jira | O | 필터(JQL)·저장된 검색·보드 | [4] |
| ClickUp | O | 15+ 뷰 저장, 필터/그룹 | [5] |
| Monday | O | 보드 뷰 저장·필터 | [6] |
| Linear | O | "Custom Views" — 필터링된 보드/리스트를 뷰로 저장(Opt/Alt+V), 그룹핑(Status/Project/Priority/Cycle/Label 등) | [8] |
| Trello | △ | 필터링 가능하나 "저장된 뷰" 개념은 Premium 뷰/Power-Up 의존 | [9] |

### 3. 커스텀 필드 종류 (텍스트/숫자/선택/날짜/사람/관계형/수식·롤업)

| 시스템 | 텍스트·숫자·선택·날짜·사람 | 관계형 연결 | 수식·롤업 | 출처 |
|---|---|---|---|---|
| Notion | O | O(Relation 네이티브) | O(Formula·Rollup 네이티브) | [1] |
| Asana | O | △(Reference 커스텀 필드로 태스크/프로젝트/포트폴리오/목표 연결) | △(공식 일부, 롤업 제한적) | [2] |
| Jira | O | △(이슈 링크·Assets) | △(애드온/스크립트 의존 많음) | [4] |
| ClickUp | O | O(Relationship 필드) | O(Formula·AI 커스텀 필드: 요약/번역/액션아이템 자동생성) | [5] |
| Monday | O(컬럼 타입 다양) | O(Connect boards/Mirror) | △(Formula 컬럼·Mirror 롤업 형태) | [6] |
| Linear | O(Issue properties) | △ | △ | [8] |
| Trello | △(Custom Fields는 **Power-Up**: 드롭다운/체크박스/날짜/숫자/텍스트) | X | X | [9][16] |

주: Trello 커스텀 필드는 **네이티브가 아니라 Power-Up**(흔한 오해 지점). [9]

### 4. 자동화 룰 (no-code, 트리거-액션)

| 시스템 | 지원 | 명칭/특징 | 출처 |
|---|---|---|---|
| Notion | O | DB 자동화 + 버튼 + 2025.12 webhook 액션(Zapier/Make 연계) | [1][13] |
| Asana | O | Rules + 2025 AI Studio(노코드 AI 워크플로우, 6월 룰 빌더 재설계) | [2][3] |
| Jira | O | Jira Automation(트리거-조건-액션), Rovo 에이전트를 룰에 포함 가능 | [4] |
| ClickUp | O | Automations(스케줄·다중 프로젝트·복합 로직) | [5] |
| Monday | O | Automations + AI Blocks(컬럼/자동화/워크플로우 빌더) | [6] |
| Linear | O | Automations(Business/Enterprise), Product Intelligence(담당자 추천·중복 탐지·라벨 제안) | [7] |
| Trello | O | **Butler** 노코드 자동화(카드 이동/담당자/마감 설정) | [9] |

### 5. 협업: 코멘트 · @멘션 · 인앱 알림

| 시스템 | 코멘트 | @멘션 | 인앱 알림 | 출처 |
|---|---|---|---|---|
| Notion | O | O | O | [1] |
| Asana | O | O | O | [17] |
| Jira | O | O | O | [4] |
| ClickUp | O | O | O | [5] |
| Monday | O | O | O | [6] |
| Linear | O | O(@Linear 포함) | O | [7] |
| Trello | O | O | O | [9] |

주: 7개 모두 기본 지원(보편 기능). 차이는 깊이보다 알림 채널 연동(아래 9번)에서 발생.

### 6. 승인/검토 워크플로우 (네이티브 approval) — **정밀 검증**

| 시스템 | 네이티브 approval | 구현 방식 | 출처 |
|---|---|---|---|
| Asana | **O** | 태스크를 "Approval" 타입으로 지정, 승인/거절(모바일 in-app 포함) | [2][3] |
| Jira | **O(JSM)** | Jira Service Management **워크플로우 approval step** — 단, 사용자 picker 커스텀 필드(Approvers/Approver groups)를 만들어 연결해야 함 | [14] |
| ClickUp | △ | 전용 approval 객체보다 **상태 기반**(In Review/Awaiting Approval) + 타임시트 승인이 중심 | [5] |
| Monday | △ | 상태 컬럼 + 자동화로 승인 흐름 구성(전용 approval 위젯은 앱/템플릿 의존) | [6] |
| Notion | **X(전용 없음)** | **버튼 속성 + 상태 속성 + 자동화**로 승인 흐름 구성(네이티브 approval 객체 아님) | [12][13] |
| Linear | **X(전용 없음)** | 상태/워크플로우 + (코드)리뷰 흐름으로 대체, 일반 결재형 approval 미제공 | [8] |
| Trello | **X(전용 없음)** | 리스트 이동/Butler 규칙으로 의사 승인, 전용 approval 없음 | [9] |

**핵심**: "승인 기능"을 단일 축으로 비교하면 오류 발생. **Asana·Jira(JSM)만 네이티브 결재형 승인**에 가깝고, 나머지는 상태/버튼/자동화 조합. Jira조차 사전에 커스텀 필드 설정이 필요함. [14]

### 7. 대시보드 · 리포팅 (위젯 · 차트 빌더)

| 시스템 | 지원 | 특징 | 출처 |
|---|---|---|---|
| Notion | △ | 차트 블록·DB 집계 있으나 전용 위젯형 대시보드 빌더는 제한적 | [1] |
| Asana | O | Dashboards·Reporting·Universal Reporting(위젯/차트) | [17] |
| Jira | O | Dashboards(가젯), JSM/Advanced Roadmaps 리포트 | [4] |
| ClickUp | O | Dashboards(위젯·차트), Goals·Rollups | [5] |
| Monday | O | Dashboards(위젯 50+), 차트 위젯 | [6] |
| Linear | △ | Analytics/Insights(이슈·사이클 기반), 자유 차트 빌더는 제한적 | [8] |
| Trello | △ | **Dashboard 뷰(Premium)** — 카드 수/마감/멤버별 기본 차트 | [9] |

### 8. 권한 · 역할 모델 (RBAC · 게스트 · 부서/스페이스 스코프)

| 시스템 | RBAC | 게스트 | 스코프(스페이스/팀) | 출처 |
|---|---|---|---|---|
| Notion | O | O(게스트) | O(Teamspace) | [1] |
| Asana | O | O | O(팀/프로젝트/포트폴리오 권한) | [17] |
| Jira | O(세밀한 권한 스킴) | O | O(프로젝트 단위) | [4] |
| ClickUp | O | O | O(Workspace/Space/Folder 계층) | [5] |
| Monday | O | O | O(Workspace/보드 권한) | [6] |
| Linear | O(Administration) | O(게스트) | O(Team) | [8] |
| Trello | O | O | O(Workspace/보드) | [9] |

### 9. API / 외부 연동(특히 Slack) / 임포트(엑셀·CSV)

| 시스템 | REST/공개 API | Slack 연동 | CSV/엑셀 임포트 | 출처 |
|---|---|---|---|---|
| Notion | O | O | O(CSV→DB) | [1] |
| Asana | O | O | O(CSV) | [17] |
| Jira | O | O | O(CSV/JSON) | [4] |
| ClickUp | O | O | O(엑셀/CSV) | [5] |
| Monday | O(GraphQL) | O | O(엑셀/CSV) | [6] |
| Linear | O(GraphQL) | **O(양방향: @Linear 멘션 액션, 프로젝트별 Slack 채널 자동 생성·업데이트 게시)** | O(Import Issues, CSV/타사 이전) | [7][8] |
| Trello | O | O(Slack Power-Up) | △(CSV는 Power-Up/Enterprise 의존) | [9] |

주: Linear/Monday는 GraphQL API. 나머지는 REST 중심. Linear의 **Slack 양방향 통합 깊이**가 차별점. [7]

### 10. 모바일 앱 / 반응형 / 접근성(a11y)

| 시스템 | 모바일 앱 | 모바일 특화 기능 | 접근성(a11y) 공식 정보 | 출처 |
|---|---|---|---|---|
| Notion | O(iOS/Android) | 2026.01 Notion 3.2 "Mobile AI" | 공식 a11y 등급 명시 자료 부족(?) | [1] |
| Asana | O | **모바일에서 승인/거절 in-app** | a11y 일부 문서화(?) | [3] |
| Jira | O | 모바일 보드·알림 | VPAT 등 별도 확인 필요(?) | [4] |
| ClickUp | O | 모바일 앱 | ? | [5] |
| Monday | O | 모바일 앱 | ? | [6] |
| Linear | O(데스크톱/모바일) | 모바일에서 Agent 챗 | ? | [7] |
| Trello | O | 경량 모바일 친화 | ? | [9] |

주: **접근성(WCAG/VPAT) 등급은 7개 모두 공개 1차 자료가 충분치 않아 단정 금지(?)**. 비교 보고서에서 a11y는 "확인 필요" 또는 각 사 VPAT 직접 인용 권장.

### 11. AI 기능 (2025~2026 도입 현황) — **정밀 검증**

| 시스템 | AI 브랜드/기능 | 2025~2026 핵심 도입 | 출처 |
|---|---|---|---|
| Notion | Notion AI / Agents | **2025.09 Notion 3.0 AI Agents**(자율 ~20분, 수백 페이지), Custom Agents(트리거/스케줄), AI Meeting Notes(Zoom/Meet/Teams 봇 없이 전사·요약), Q&A/Enterprise Search, relation-aware autofill, Workers for Agents(JS/Python 실행). Business/Enterprise 포함 | [1][12] |
| Asana | Asana AI / AI Studio | **AI Studio**(노코드 AI 워크플로우), Smart Workflow Gallery, **AI Teammates(2025 Fall)**, AI 룰(요약·트리아지·리네임), 2025.06 룰빌더 재설계 | [2][3] |
| Jira | Atlassian **Rovo** | Rovo 에이전트(기본/Studio 커스텀/마켓플레이스), 백로그 그루밍·요약, 채팅·자동화·편집(/Rovo, /ai). **롤아웃: Premium/Ent 2025.04~07, Standard 2025.10**. **주의: Rovo가 Jira 커스텀 필드를 처리 못하는 제약 보고됨** | [4] |
| ClickUp | **ClickUp Brain² / AI Fields** | Brain²($9/user~)에 프리미엄 모델(ChatGPT/Claude/Gemini), 워크스페이스 전체 컨텍스트(태스크/문서/커스텀필드/시간추적), **AI Custom Fields**(요약/번역/액션아이템/상태리포트 자동생성) | [5] |
| Monday | **monday AI**(AI Blocks/Digital Workforce) | AI Blocks(컬럼·자동화·워크플로우 빌더 공통), Product Power-ups(워크로드/마감 예측), **Digital Workforce(일부 coming soon)** | [6] |
| Linear | **Linear Agent / Skills** | **2026.03 Linear Agent 공개 베타**(전 플랜), Skills(재사용 워크플로우), **Claude Code·Codex로 코드 작성**(triage→plan→review→ship), Product Intelligence(담당자 추천·중복 탐지·라벨 제안). Automations/Code Intelligence는 Business/Enterprise | [7][15] |
| Trello | **Atlassian Intelligence** | 카드 요약·보드 컨텍스트 기반 설명 자동생성. 별도 강력 AI 에이전트보다 경량 | [16] |

**AI 정밀 주의**: (a) Monday "Digital Workforce"는 일부 **coming soon** 표기 — 전면 출시로 단정 금지. (b) Jira Rovo는 **롤아웃 시점(플랜별 차등)**과 **커스텀 필드 미처리 제약**을 명시할 것. (c) ClickUp/Notion은 외부 LLM(Claude 등) 모델을 옵션으로 노출. (d) Linear Agent는 2026.03 **베타** 단계.

### 인접 영역 — 프로세스 개선/리소스 정량화(RI·자동화 우선순위·프로세스 마이닝)

| 항목 | 일반 PM 도구에서의 취급 | 출처 |
|---|---|---|
| 업무 시간 추적(time tracking) | ClickUp/Monday/Wrike는 시간추적 오버레이 네이티브 제공, 그 외는 애드온/통합 多 | [10][11] |
| 자동화 ROI·우선순위 산정 | **PM 도구 네이티브 기능 아님.** 별도 영역(프로세스 마이닝)에서 what-if·우선순위 산정 제공(IBM Process Mining 등) | [10][11] |
| 프로세스 마이닝(이벤트 로그→프로세스 재구성·병목 발견) | **별도 카테고리 솔루션**(IBM Process Mining 등). 일반 PM 도구에 네이티브 부재 | [10] |
| 가치사슬 시각화 | 일반 PM 도구 표준 기능 아님 | [10][11] |

**결론(평가 대상 앱 차별점 검증)**: 평가 대상 앱의 **RI=총투입시간×반복성가중치 기반 자동화 우선순위 자동 산정 + 가치사슬 시각화**는 위 7개 일반 PM 도구의 네이티브 기능에 **해당하지 않음**(흔치 않음 — 확인됨). 가장 가까운 영역은 별도 카테고리인 **프로세스 마이닝**이며, 일반 PM 도구는 기껏해야 시간추적 데이터 + 대시보드 수준에 그친다. 따라서 비교 보고서에서 이 기능을 평가 대상 앱의 **명확한 차별점(white space)**으로 제시 가능. [10][11]

---

## 수정 권고 (비교 보고서 작성 시 흔한 오해/부정확 표현 주의점)

1. **"승인 기능 있음"으로 7개를 동일선상에 두지 말 것.** 네이티브 결재형 approval은 **Asana(태스크 approval)·Jira Service Management(워크플로우 approval step)** 정도. Notion·Linear·Trello는 **버튼/상태/Power-Up 조합**일 뿐 전용 approval 객체가 아니다. Jira조차 **사용자 picker 커스텀 필드 사전 설정**이 필요. [12][14]

2. **Trello의 커스텀 필드·캘린더·타임라인·대시보드는 "네이티브"가 아니다.** Custom Fields는 **Power-Up**, Timeline/Calendar/Dashboard는 **Premium 유료 뷰** 또는 Power-Up. "Trello가 간트를 지원한다"는 단정은 부정확. [9][16]

3. **Linear는 캘린더·간트(Gantt) 뷰를 네이티브로 제공하지 않는다.** List/Board(Kanban)/Timeline(로드맵)만. "Linear에 캘린더 뷰가 있다"는 서술은 오류. [8][15]

4. **Jira Rovo의 가용성과 제약을 정확히.** 플랜별 롤아웃 차등(Premium/Ent 2025.04~07, Standard 2025.10), 그리고 **"Rovo가 Jira 커스텀 필드를 처리하지 못한다"**는 제약을 반드시 병기. "Jira는 AI가 모든 필드를 자동 처리한다"는 과장 금지. [4]

5. **Monday "Digital Workforce"는 일부 coming soon.** 출시 완료 기능과 예고 기능을 구분해 표기할 것. [6]

6. **Notion AI Meeting Notes는 "봇이 회의에 참석하지 않고" 캡처/요약**한다는 점이 차별점(타사 봇 참석형과 다름). 잘못 비교하지 말 것. [1]

7. **AI 모델 출처 표기.** ClickUp Brain²/Linear Agent 등은 외부 LLM(Claude·ChatGPT·Gemini, Codex)을 사용/노출 — "자체 모델"로 단정 금지. [5][7]

8. **접근성(a11y)은 7개 모두 1차 공개자료가 빈약**하므로 등급을 임의 부여하지 말고 "각 사 VPAT/WCAG 문서 확인 필요"로 처리. (이 로그에서 미검증 = ?)

9. **RI·자동화 우선순위·가치사슬 시각화는 일반 PM 도구의 기능이 아니다.** 이를 "경쟁 도구도 한다"고 쓰면 부정확. 가장 가까운 건 별도 카테고리(프로세스 마이닝). 평가 대상 앱의 차별점으로 명확히 포지셔닝. [10][11]

10. **GraphQL vs REST 구분.** Linear·Monday는 GraphQL API. "모두 REST API"라는 표현은 부정확. [6][7]

---

## 출처 목록

(모든 URL 확인일: 2026-06-18)

1. Notion — AI/제품·릴리스 종합. https://www.notion.com/product/ai , https://www.notion.com/releases , https://www.notion.com/releases/2026-01-20
2. Asana — AI Studio 제품 페이지. https://asana.com/product/ai/ai-studio , https://help.asana.com/s/article/ai-studio-smart-workflows
3. Asana — 2025 릴리스(Spring/Summer/Fall). https://asana.com/inside-asana/spring-release-2025 , https://asana.com/inside-asana/fall-release-2025 , https://forum.asana.com/t/spring-2025-release-unlock-speed-and-scale-for-your-teams-with-ai-workflows/1065607
4. Jira — Rovo AI 기능. https://www.atlassian.com/software/jira/ai , https://support.atlassian.com/rovo/docs/agents/
5. ClickUp — 제품 기능·Brain·AI Fields. https://clickup.com/features , https://clickup.com/brain , https://help.clickup.com/hc/en-us/articles/18450100382871-What-are-AI-Fields
6. Monday.com — AI Blocks/AI Feature Catalog/AI Workflows. https://support.monday.com/hc/en-us/articles/18433811274386-AI-blocks , https://support.monday.com/hc/en-us/articles/24047211522194-AI-Feature-Catalog , https://support.monday.com/hc/en-us/articles/20598895919122-AI-Workflows-features-and-capabilities
7. Linear — Linear Agent 체인지로그·Slack 통합. https://linear.app/changelog/2026-03-24-introducing-linear-agent , https://linear.app/integrations/slack , https://linear.app/docs/slack
8. Linear — Docs(Custom Views/Board layout/Issue properties/Import). https://linear.app/docs , https://linear.app/docs/custom-views , https://linear.app/docs/board-layout
9. Trello — 기능/Butler/Power-Ups 가이드. https://trello.com/butler-automation , https://support.atlassian.com/trello/docs/using-the-calendar-power-up/ , https://blogs.zoftwarehub.com/trello-guide-2025-features-benefits-pricing-analysis/
10. 프로세스 마이닝/자동화 우선순위. https://www.kickidler.com/info/top-process-mining-software.html (IBM Process Mining 등 what-if·우선순위 산정)
11. PM 도구 시간추적·ROI. https://www.tempo.io/blog/project-management-and-time-tracking , https://www.celoxis.com/article/roi-project-management-software-numbers-results
12. Notion — 승인 워크플로우·DB 버튼. https://www.notion.com/help/database-buttons , https://www.notion.com/help/guides/make-work-more-efficient-database-button-property
13. Notion — Automations/Webhook(2025.12). https://www.notion.com/help/guides/category/automations , https://www.gend.co/blog/discover-latest-features-notion-dec-2025
14. Jira Service Management — 워크플로우 approval step 추가. https://support.atlassian.com/jira-service-management-cloud/docs/add-an-approval-to-a-workflow/ , https://support.atlassian.com/jira-service-management-cloud/docs/set-up-approvals/
15. Linear — 뷰/로드맵 타임라인(캘린더·간트 미제공 확인). https://linear.app/changelog/2021-05-27-linear-preview-roadmap-timeline , https://toolstackpm.com/tools/linear/features/kanban-boards
16. Trello — Atlassian Intelligence·Power-Ups 2026. https://workmanagementhub.com/trello-power-ups-guide-2026/
17. Asana — 프로젝트 뷰(캘린더/칸반/간트/타임라인). https://asana.com/features/project-management/project-views

---
검증 완료. 1차 출처(공식 문서·헬프센터·릴리스 노트) 우선 적용. 미확인 항목은 표에 `?`로 표기하여 비교 보고서에서 임의 단정을 방지함.
