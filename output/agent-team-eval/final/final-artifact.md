# Agent Team Framework 오픈소스 비교 평가 보고서

생성: Team Lead 통합 | 일시: 2026-05-26 | 비교 대상: 5개 GitHub 오픈소스 프레임워크

---

## 요약

**결론: 현재 프레임워크는 오픈소스 최상위와 동급. 도메인 범용성·배포 통합·Config-driven 설계에서 차별적 강점. 병렬 실행 구조 부재가 가장 큰 개선 기회.**

---

## 비교 대상 프레임워크

| 레포 | 라이선스 | 핵심 특징 |
|------|---------|---------|
| [wshobson/agents](https://github.com/wshobson/agents) | MIT | 191 agent, 155 skill, 83 plugin. 멀티하네스(5종) |
| [ciscoittech/claude-agent-framework](https://github.com/ciscoittech/claude-agent-framework) | MIT | 병렬 실행, 97% context reduction, 에이전트 자동 생성 |
| [lucasbrandao4770/claude-agent-teams](https://github.com/lucasbrandao4770/claude-agent-teams) | MIT | 파일 오너십 강제, 8개 팀 템플릿, dry-run |
| [Gentleman-Programming/agent-teams-lite](https://github.com/Gentleman-Programming/agent-teams-lite) | MIT | Spec-driven, orchestrator + 9 sub-agents, 순수 Markdown |
| [aws-samples/sample-claude-code-agent-team](https://github.com/aws-samples/sample-claude-code-agent-team) | Apache 2.0 | AWS 공식 샘플, 부모-자식 에이전트, Spec-driven |

---

## 강점 (오픈소스 대비 우위)

### 1. 도메인 범용성 — 오픈소스와 가장 큰 차별점

비교 대상 5개 레포 중 4개는 소프트웨어 개발 도메인 전용이다. 우리 프레임워크는 task type으로 6개 도메인을 수평 확장한다:

| Task Type | 도메인 | 활성 멤버 |
|-----------|-------|---------|
| `research-report` | 리서치·분석 | alpha·gamma·delta·beta |
| `code-review` | 코드 리뷰 | alpha·gamma·beta |
| `multilingual-brief` | 번역·다국어 | alpha·beta·delta |
| `dev` | 개발·배포 | alpha·epsilon |
| `design` | 에이전트 설계 | alpha·zeta |
| `github-plan` | 오픈소스 탐색 | eta·alpha·beta |

### 2. Config-driven 설계

`team-config.yaml` 한 파일로 멤버·task type·배포 엔드포인트를 전체 정의. 오늘 member-eta 추가가 config 병합만으로 완결된 것이 실증. 대부분의 오픈소스는 AGENT.md 직접 편집 필요.

### 3. Distribution 단계 내장 (Phase 5)

Notion 자동 저장, Gmail/Drive/Calendar 연동이 워크플로우에 통합. 비교 대상 레포 중 배포까지 포함한 사례 없음.

### 4. Slack 연동 + 자동 모드

Socket Mode 봇 + `[AUTO: slug]` 프롬프트로 외부 트리거 → 무인 실행 가능. 이 조합을 내장한 오픈소스 프레임워크 미발견.

### 5. Workspace 격리

주제별 slug 폴더로 결과 격리. 멀티 프로젝트 병행 시 결과 혼합 없음.

---

## 약점 (개선 기회)

### 1. 🔴 순차 실행 — 가장 큰 구조적 갭

`ciscoittech`는 탐색 3~6개 + 빌드 8개 + 리뷰 5개를 병렬로 실행해 3~6× 속도를 달성한다. 현재 프레임워크는 plan.md에 병렬 가능성을 명시해도 실제 실행은 직렬이다.

**영향**: 처리 시간. 멤버가 늘수록 누적 지연 증가.

### 2. 🟡 파일 오너십 — 텍스트 규칙의 한계

`lucasbrandao4770`는 에이전트별 편집 가능 파일 목록을 테이블로 관리하고 위반을 차단한다. 우리의 "절대 금지" 조항은 LLM 판단에 의존한다.

**영향**: 팀 확장 시 멤버 간 파일 충돌 리스크.

### 3. 🟢 에이전트 자동 생성, Dry-run, 멀티하네스

낮은 우선순위. 현재 운영 규모에서 임팩트 제한적.

---

## 종합 평가

| 평가 항목 | 우리 | 오픈소스 최상위 |
|---------|------|--------------|
| 도메인 범용성 | ★★★★★ | ★★★☆☆ |
| Config-driven 설계 | ★★★★★ | ★★★☆☆ |
| 배포 통합 | ★★★★★ | ★★☆☆☆ |
| 외부 트리거 연동 | ★★★★☆ | ★★☆☆☆ |
| 병렬 실행 | ★★☆☆☆ | ★★★★★ |
| 파일 오너십 강제 | ★★☆☆☆ | ★★★★☆ |
| 에이전트 자동 생성 | ★★☆☆☆ | ★★★★☆ |
| **종합** | **★★★★☆** | **★★★★☆** |

**오픈소스 최상위와 종합 동급. 방향은 올바르며 실행 속도 개선이 다음 과제.**

---

## 권고 액션 (우선순위 순)

| 순위 | 액션 | 난이도 | 참고 레포 |
|------|------|-------|---------|
| 1 | 파일 오너십 테이블을 CLAUDE.md에 추가 | 낮음 | `claude-agent-teams` |
| 2 | plan.md에 `parallel_group` 표준 필드 추가 | 낮음 | `ciscoittech` |
| 3 | 병렬 실행 구조 설계 (`team-config.yaml`에 `parallel_groups` 필드) | 중간 | `ciscoittech` |
| 4 | Dry-run 모드 (실행 전 팀 구성 미리보기) | 낮음 | `claude-agent-teams` |
