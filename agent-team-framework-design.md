# Agent Team Framework 설계서

> **Claude Code 구현 참조용 통합 설계 문서**
> 작성일: 2026-04-17 | 버전: v1.1 (2026-05-24: dev task type · member-epsilon · Priority Queue 추가)

---

## Executive Summary

**핵심 주장:** 본 문서는 Claude Code 환경에서 **다수의 에이전트가 팀으로 협업하여 분업 완성형 업무를 수행하는 범용 프레임워크**를 설계한다. 기존 오케스트레이터-서브에이전트 위계 구조와 달리, **팀장 중재형 협업 모델**을 채택하여 팀장이 작업 분배·의존성 분석·산출물 통합·품질 판단을 동적으로 수행한다.

**핵심 설계 결정:**
- 팀 구성을 YAML config로 정의하여 업무별 교체 가능 (config-driven)
- 팀장이 산출물 교차 참조 필요 여부와 수정 규모를 상황 판단하여 직접수정/재지시를 결정
- 종료 조건은 품질 기준 + 최대 반복 횟수 + 사람 승인의 3중 레이어

**결론:** 이 프레임워크를 기반으로 특정 업무(산업 인텔리전스, 업무 과제 분석 등)에 config만 교체하여 팀을 즉시 구성할 수 있다.

---

## 1. 작업 컨텍스트 문서

> 이 섹션은 프레임워크의 배경, 목적, 범위, 제약조건을 정의한다.

### 1.1 배경 및 목적

#### 배경
[사실] Claude Code의 기존 멀티에이전트 패턴은 CLAUDE.md(오케스트레이터) → AGENT.md(서브에이전트)의 단방향 위계 구조로, 호출-실행-반환의 1회성 상호작용에 최적화되어 있다.

[분석] 그러나 실무에서는 "시장조사 결과를 참고해 재무분석을 수행하고, 통합 리포트를 작성한 뒤 품질을 검토하여 재작업"하는 식의 **반복적 조율이 필요한 분업 협업**이 빈번하다. 기존 구조로는 이 패턴을 자연스럽게 구현하기 어렵다.

#### 목적
- 다수의 에이전트가 **팀**으로 협업하는 범용 프레임워크를 설계한다
- 업무가 바뀌어도 **config 교체만으로 팀 재구성**이 가능한 구조를 만든다
- 팀장 에이전트가 작업 분배·통합·품질 관리를 **동적으로 판단**하는 중재 프로토콜을 정의한다

### 1.2 범위

#### 포함 (In Scope)
- 팀 구성 config 스키마 정의
- 팀장 중재 프로토콜 (작업 분배, 의존성 분석, 산출물 통합, 품질 판단)
- 팀원 에이전트 실행 프로토콜
- 복합 종료 조건 메커니즘
- 폴더 구조 및 파일 역할 정의

#### 제외 (Out of Scope)
- 특정 업무에 종속된 도메인 로직 (추후 config로 매핑)
- CLAUDE.md, AGENT.md, SKILL.md의 상세 프롬프트 내용 (구현 시 작성)
- 외부 API 연동 상세 (업무별로 스킬에서 처리)

### 1.3 용어 정의

| 용어 | 정의 |
|------|------|
| **Team** | 하나의 업무를 협업 수행하는 에이전트 그룹. 반드시 1명의 Team Lead + 1명 이상의 Member로 구성 |
| **Team Lead** | 팀의 오케스트레이터. 작업 분배, 의존성 분석, 산출물 통합, 품질 판단, 종료 결정을 수행 |
| **Member** | 특정 역할을 맡아 독립 산출물을 생성하는 에이전트 |
| **Task** | 팀이 수행하는 전체 업무 단위. config에 정의됨 |
| **Assignment** | Team Lead가 Member에게 분배하는 개별 작업 단위 |
| **Artifact** | 각 에이전트가 생성하는 산출물 파일 |
| **Review Cycle** | Team Lead가 산출물을 검토하고 승인/재지시하는 1회 순환 |
| **Handoff** | 에이전트 간 산출물과 컨텍스트가 전달되는 행위 (항상 Team Lead 경유) |
| **Config** | 팀 구성·역할·종료조건을 정의하는 YAML 파일 |

### 1.4 제약조건

| 제약 | 내용 | 영향 |
|------|------|------|
| **Claude Code 환경** | 에이전트 간 통신은 파일 시스템과 프롬프트 기반으로만 가능 | 실시간 메시징 불가, 파일 기반 Handoff 필수 |
| **컨텍스트 윈도우** | 각 에이전트(서브에이전트 호출)마다 별도 컨텍스트 | 팀원 에이전트는 자기 역할 지침 + 할당된 작업 정보만 로드 |
| **순차 실행** | Claude Code는 서브에이전트를 병렬 실행할 수 없음 | 의존성이 없어도 팀원은 순차 호출됨. 단, 독립 작업은 순서 무관 |
| **비용 효율** | 반복 루프가 많을수록 토큰 소모 증가 | 최대 반복 횟수 제한 필수 |

---

## 2. 워크플로우 정의

> 이 섹션은 팀의 전체 실행 흐름, 분기 조건, 각 단계의 성공 기준과 실패 처리를 정의한다.

### 2.1 전체 실행 흐름

```
[시작] 사용자가 Task 입력
  │
  ▼
┌─────────────────────────────────────────────┐
│ Phase 1: PLAN (Team Lead)                   │
│  1-1. Config 로드 → 팀 구성 확인            │
│  1-2. Task 분석 → Assignment 목록 생성       │
│  1-3. 의존성 분석 → 실행 순서 결정           │
│  1-4. 실행 계획서 작성 → /output/plan.md     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Phase 2: EXECUTE (Team Lead → Members)      │
│  반복: 각 Assignment에 대해                  │
│  2-1. Team Lead가 Member 호출 + 지시 전달    │
│  2-2. Member가 산출물 생성 → /output/        │
│  2-3. (선행 산출물 참조 필요 시) 경로 전달    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Phase 3: REVIEW (Team Lead)                 │
│  3-1. 각 산출물 품질 검증                    │
│  3-2. 판단 분기:                             │
│       ├─ 승인 → Phase 4로                    │
│       ├─ 경미한 수정 → Team Lead 직접 수정   │
│       └─ 중대한 수정 → 해당 Member에 재지시  │
│          (Review Cycle +1, 최대 N회)         │
│  3-3. 모든 산출물 승인 시 Phase 4로          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Phase 4: INTEGRATE (Team Lead)              │
│  4-1. 개별 산출물을 최종 결과물로 통합       │
│  4-2. 통합 산출물 자기 검증                  │
│  4-3. 종료 조건 체크                         │
│       ├─ 품질 기준 충족 + 반복 제한 이내     │
│       │   ├─ 사람 승인 필요 → 대기            │
│       │   └─ 불필요 → 완료                    │
│       └─ 미충족 → Phase 2로 (전체 재실행)    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
[종료] 최종 산출물 → /output/final/
```

### 2.2 Phase별 상세 정의

#### Phase 1: PLAN

> Team Lead가 Task를 분석하고, 팀원별 Assignment을 생성하며, 실행 순서를 결정하는 단계.

| 항목 | 내용 |
|------|------|
| **수행 주체** | Team Lead (LLM 판단) |
| **입력** | 사용자 Task 설명 + team-config.yaml |
| **LLM 판단 영역** | Task 분해, 각 Member에 대한 Assignment 범위 결정, 의존성 분석 (병렬 가능 vs 순차 필요), 선행 산출물 참조 여부 결정 |
| **산출물** | `/output/plan.md` — Assignment 목록, 실행 순서, 의존성 맵, 각 Assignment의 기대 산출물 |
| **성공 기준** | 모든 Member에게 최소 1개 Assignment 배정, 순환 의존성 없음, 기대 산출물 형식 명시 |
| **검증 방법** | 규칙 기반 (Assignment 수 ≥ Member 수, 의존성 DAG 검증) + LLM 자기 검증 (Assignment 범위가 Member 역할에 부합하는지) |
| **실패 시 처리** | 자동 재시도 (최대 2회). 2회 실패 시 에스컬레이션 (사용자에게 Task 분해 방식 확인 요청) |

#### Phase 2: EXECUTE

> Team Lead가 실행 순서에 따라 각 Member를 호출하고, Member는 독립적으로 산출물을 생성하는 단계.

| 항목 | 내용 |
|------|------|
| **수행 주체** | Team Lead (호출/지시) + 각 Member (실행) |
| **입력** | plan.md의 해당 Assignment + (의존성이 있는 경우) 선행 산출물 파일 경로 |
| **LLM 판단 영역 (Team Lead)** | 선행 산출물을 Member에게 어느 범위까지 전달할지 결정, 지시문 작성 |
| **LLM 판단 영역 (Member)** | 할당된 영역에 대한 분석·생성·판단 (역할에 따라 다름) |
| **코드/스크립트 처리** | 파일 I/O, 데이터 파싱, API 호출, 정형 데이터 처리 → 각 Member의 스킬 스크립트 |
| **산출물** | `/output/{member-name}/{artifact-file}` — Member별 디렉토리에 산출물 저장 |
| **성공 기준** | 산출물 파일 존재 + 기대 형식 준수 + 필수 섹션/필드 포함 |
| **검증 방법** | 스키마 검증 (파일 존재, 형식 체크) + 규칙 기반 (필수 섹션 포함 여부) |
| **실패 시 처리** | 스킵 불가 (분업 완성형이므로 각 산출물이 필수). 자동 재시도 1회 → 실패 시 Team Lead가 오류 원인 분석 후 지시문 수정하여 재호출 |

#### Phase 3: REVIEW

> Team Lead가 모든 Member의 산출물을 검토하고, 승인·직접수정·재지시를 판단하는 단계.

| 항목 | 내용 |
|------|------|
| **수행 주체** | Team Lead (LLM 판단) |
| **입력** | `/output/{member-name}/` 하위 전체 산출물 |
| **LLM 판단 영역** | 품질 평가 (역할 적합성, 완성도, 정합성), 수정 규모 판단, 직접수정/재지시 분기 결정 |
| **분기 조건 (핵심)** | 아래 "수정 규모 판단 기준" 참조 |
| **산출물** | `/output/review-log.md` — 각 Member별 검토 결과, 판단 사유, 액션 |
| **성공 기준** | 모든 산출물이 "승인" 또는 "직접수정 완료" 상태 |
| **검증 방법** | LLM 자기 검증 (검토 근거의 일관성) |
| **실패 시 처리** | 재지시 → Member 재실행 (Review Cycle +1). 최대 반복 횟수 도달 시 현재 최선 버전으로 Phase 4 진행 + 미해결 이슈를 review-log.md에 기록 |

**수정 규모 판단 기준 (Team Lead의 의사결정 프로토콜):**

```
수정이 필요한 산출물 발견 시:

IF 수정 범위가 아래 모두에 해당:
  - 전체 산출물의 20% 미만 영향
  - 사실관계 변경 없음 (표현/구조/형식 수준)
  - Member의 추가 도메인 판단 불필요
THEN → Team Lead 직접 수정

ELSE → 해당 Member에 수정 지시서와 함께 재지시
  수정 지시서에 포함할 내용:
  - 수정 필요 위치
  - 현재 문제점
  - 기대하는 수정 방향
  - 참고할 다른 산출물 (있는 경우)
```

#### Phase 4: INTEGRATE

> Team Lead가 승인된 개별 산출물을 최종 결과물로 통합하는 단계.

| 항목 | 내용 |
|------|------|
| **수행 주체** | Team Lead (LLM 판단 + 통합 작업) |
| **입력** | 모든 Member의 승인된 산출물 + plan.md |
| **LLM 판단 영역** | 산출물 간 정합성 확인, 중복/모순 해소, 통합 구조 결정, 전체 품질 자기 검증 |
| **코드/스크립트 처리** | 파일 병합, 포맷 변환 → 통합 스킬 스크립트 |
| **산출물** | `/output/final/{final-artifact}` — 최종 통합 결과물 |
| **성공 기준** | config에 정의된 최종 품질 기준 충족 |
| **검증 방법** | LLM 자기 검증 (통합 품질 체크리스트) + 스키마 검증 (최종 산출물 형식) |
| **실패 시 처리** | 품질 미충족 + 반복 가능 → Phase 2로 전체 재실행. 최대 반복 도달 → 현재 최선 버전 + 품질 보고서 함께 출력 |

### 2.3 종료 조건 상세

> 3중 레이어 종료 조건은 아래 순서로 체크한다.

```
[체크 1] 최대 반복 횟수 (비용 보호)
  현재 전체 루프 횟수 ≥ config.termination.max_cycles?
  ├─ YES → 강제 종료. 현재 최선 버전 + 미해결 이슈 보고서 출력
  └─ NO  → 체크 2로

[체크 2] 품질 기준 (품질 보장)
  config.termination.quality_criteria의 모든 항목 충족?
  ├─ NO  → Phase 2로 복귀 (재실행)
  └─ YES → 체크 3으로

[체크 3] 사람 승인 (고위험 게이트)
  config.termination.human_approval == true?
  ├─ YES → 사용자에게 최종 산출물 제시 + 승인 요청
  │        ├─ 승인    → 완료
  │        └─ 수정 요청 → 피드백 반영 후 Phase 2로 (루프 카운트 +1)
  └─ NO  → 완료
```

### 2.4 상태 전이 다이어그램

```
                    ┌──────────┐
                    │  START   │
                    └────┬─────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Phase 1     │
                  │  PLAN        │──── 실패(2회) ──→ [에스컬레이션]
                  └──────┬───────┘
                         │ 성공
                         ▼
              ┌──────────────────┐
          ┌──▶│  Phase 2         │
          │   │  EXECUTE         │──── Member 실패 ──→ [재호출(1회)]
          │   └──────┬───────────┘                      │
          │          │ 완료                             실패
          │          ▼                                   │
          │   ┌──────────────┐                    [Team Lead 분석
          │   │  Phase 3     │                     + 지시 수정 후
          │   │  REVIEW      │                     재호출]
          │   └──┬───┬───┬───┘
          │      │   │   │
          │   승인  경미  중대
          │      │   │   │
          │      │   │   └──→ Member 재지시 ──→ Phase 2 (해당 Member만)
          │      │   └──→ Team Lead 직접 수정
          │      ▼
          │   ┌──────────────┐
          │   │  Phase 4     │
          │   │  INTEGRATE   │
          │   └──┬───────────┘
          │      │
          │   종료조건 체크
          │      │
          │   미충족 + 반복 가능
          └──────┘
                 │
              충족 │
                 ▼
          ┌──────────────┐
          │  COMPLETE    │
          └──────────────┘
```

---

## 3. 구현 스펙

> 이 섹션은 폴더 구조, config 스키마, 에이전트 구조, 파일 목록 등 구조와 역할 정의 수준의 구현 가이드를 제공한다. 상세 프롬프트 내용은 포함하지 않는다.

### 3.1 폴더 구조

```
/project-root
├── CLAUDE.md                              # 메인 에이전트 (Team Lead) 지침
├── queue_server.py                        # Priority Queue 서버 (Flask + heapq)
├── /.claude
│   ├── /configs
│   │   ├── team-config.yaml               # 팀 구성 정의 (config-driven)
│   │   └── queue-config.yaml              # Priority Queue 설정 (Slack 포트, 모델, 우선순위)
│   ├── /skills
│   │   ├── /task-planner
│   │   │   ├── SKILL.md                   # Task 분해 + 의존성 분석 스킬
│   │   │   └── /scripts
│   │   │       └── validate-plan.py       # plan.md 구조 검증 (DAG, Assignment 수)
│   │   ├── /artifact-reviewer
│   │   │   ├── SKILL.md                   # 산출물 품질 검토 스킬
│   │   │   └── /scripts
│   │   │       └── check-artifact.py      # 산출물 형식/필수항목 검증
│   │   ├── /integrator
│   │   │   ├── SKILL.md                   # 산출물 통합 스킬
│   │   │   └── /scripts
│   │   │       └── merge-artifacts.py     # 파일 병합 유틸리티
│   │   └── /shared                        # 모든 에이전트가 공유하는 스킬
│   │       ├── /file-io
│   │       │   ├── SKILL.md
│   │       │   └── /scripts
│   │       │       ├── read-file.py
│   │       │       └── write-file.py
│   │       └── /data-parser
│   │           ├── SKILL.md
│   │           └── /scripts
│   │               └── parse-data.py
│   └── /agents
│       ├── /member-template
│       │   └── AGENT.md                   # Member 에이전트 기본 템플릿
│       ├── /member-alpha … /member-delta  # 각 Member AGENT.md
│       └── /member-epsilon
│           └── AGENT.md                   # Dev Agent (OpenCode headless 실행 전담)
├── /output
│   ├── .active-workspace                  # 현재 활성 워크스페이스 슬러그
│   └── /{topic-slug}/                     # 주제별 워크스페이스
│       ├── plan.md                        # Phase 1 산출물
│       ├── review-log.md                  # Phase 3 산출물
│       ├── slack-notification.json        # Phase 5 Slack Block Kit 페이로드
│       ├── /{member-name}/                # 각 Member의 개별 산출물
│       └── /final/                        # Phase 4 최종 통합 산출물
└── agent-team-framework-design.md         # 본 설계서 (참고용)
```

### 3.2 팀 구성 Config 스키마

> Config는 업무가 바뀔 때 교체하는 유일한 파일이다. 팀 구성, 종료 조건, 산출물 형식을 모두 여기서 정의한다.

```yaml
# team-config.yaml

task:
  name: "업무명"
  description: "업무에 대한 상세 설명"
  input_description: "입력 데이터/지시 형태"
  final_output:
    format: "md | docx | xlsx | json"        # 최종 산출물 형식
    description: "최종 산출물에 대한 설명"

team:
  lead:
    name: "team-lead"
    role: "팀장의 역할 한 줄 요약"
    direct_edit_threshold: "20%"               # 직접 수정 허용 기준 (산출물 영향 범위)
    skills:                                    # Team Lead 전용 스킬
      - task-planner
      - artifact-reviewer
      - integrator

  members:
    - name: "member-alpha"
      role: "이 Member의 역할 한 줄 요약"
      domain: "담당 도메인/영역"
      agent_md: ".claude/agents/member-alpha/AGENT.md"
      skills:                                  # 이 Member가 사용하는 스킬
        - shared/file-io
        - shared/data-parser
      output:
        directory: "output/member-alpha"
        expected_files:
          - name: "analysis-report.md"
            format: "md"
            required_sections:                 # 검증용 필수 섹션
              - "개요"
              - "분석 결과"
              - "결론"

    - name: "member-beta"
      role: "이 Member의 역할 한 줄 요약"
      domain: "담당 도메인/영역"
      agent_md: ".claude/agents/member-beta/AGENT.md"
      skills:
        - shared/file-io
      output:
        directory: "output/member-beta"
        expected_files:
          - name: "data-summary.json"
            format: "json"
            schema_file: "schemas/data-summary.schema.json"  # (선택) JSON 스키마

termination:
  max_cycles: 3                                # Phase 2-4 전체 루프 최대 횟수
  max_review_per_member: 2                     # 개별 Member 재지시 최대 횟수
  quality_criteria:                            # 품질 기준 (모두 충족 시 통과)
    - type: "rule"
      description: "모든 Member 산출물의 필수 섹션 포함"
    - type: "llm_self_check"
      description: "통합 산출물의 논리적 정합성 및 중복/모순 없음"
    - type: "schema"
      description: "최종 산출물이 기대 형식을 준수"
  human_approval: true                         # true면 최종 산출물에 사람 승인 필요

execution:
  dependency_strategy: "lead_decides"          # lead_decides | all_parallel | all_sequential
  data_passing: "file_based"                   # file_based | inline
  intermediate_output_dir: "output"
```

### 3.3 에이전트 구조

#### 에이전트 역할 맵

| 에이전트 | 유형 | 역할 | 소속 Phase |
|----------|------|------|-----------|
| **Team Lead** | 메인 (CLAUDE.md) | 계획·분배·검토·통합·종료 판단 | 전 Phase |
| **Member (동적)** | 서브에이전트 (AGENT.md) | 할당된 영역의 산출물 생성 | Phase 2 |

#### Team Lead (CLAUDE.md) 핵심 섹션 목록

| 섹션 | 역할 |
|------|------|
| **Identity & Role** | 팀장 정체성, 권한 범위, 판단 원칙 |
| **Config Loading** | team-config.yaml 로드 및 파싱 방법 |
| **Phase 1: Planning Protocol** | Task 분해, 의존성 분석, plan.md 작성 지침 |
| **Phase 2: Execution Protocol** | Member 호출 방식, 지시문 템플릿, 선행 산출물 전달 규칙 |
| **Phase 3: Review Protocol** | 품질 검토 기준, 수정 규모 판단 로직, 직접수정/재지시 분기 |
| **Phase 4: Integration Protocol** | 산출물 통합 방법, 정합성 체크리스트, 최종 품질 검증 |
| **Termination Protocol** | 3중 종료 조건 체크 순서, 에스컬레이션 조건 |
| **Handoff Rules** | 데이터 전달 형식, 파일 경로 규칙, 컨텍스트 전달 범위 |
| **Skills Reference** | 사용 가능한 스킬 목록과 트리거 조건 |

#### Member Template (AGENT.md) 핵심 섹션 목록

| 섹션 | 역할 |
|------|------|
| **Identity & Role** | config에서 주입되는 역할·도메인 정의 |
| **Assignment Protocol** | Team Lead로부터 받는 지시 형식, 선행 산출물 참조 방법 |
| **Execution Rules** | 산출물 생성 규칙, 파일 저장 위치, 형식 준수 |
| **Revision Protocol** | 재지시 수신 시 수정 프로세스 |
| **Skills Reference** | 사용 가능한 스킬 목록 |
| **Constraints** | 역할 범위 제한 (다른 Member 영역 침범 금지) |

### 3.4 스킬/스크립트 파일 목록

| 스킬 | 역할 | 트리거 조건 | 주요 스크립트 |
|------|------|------------|--------------|
| **task-planner** | Task를 Assignment으로 분해, 의존성 DAG 생성 | Phase 1에서 Team Lead가 호출 | `validate-plan.py`: plan.md 구조 검증 (순환 의존성, Assignment 수, 형식) |
| **artifact-reviewer** | 산출물 품질 검토 지원 | Phase 3에서 Team Lead가 호출 | `check-artifact.py`: 파일 존재, 필수 섹션, 형식 검증 |
| **integrator** | 개별 산출물을 최종 결과물로 병합 | Phase 4에서 Team Lead가 호출 | `merge-artifacts.py`: 파일 병합, 포맷 변환 |
| **shared/file-io** | 파일 읽기/쓰기 유틸리티 | 모든 에이전트가 필요 시 호출 | `read-file.py`, `write-file.py` |
| **shared/data-parser** | 다양한 형식(xlsx, csv, json, md) 데이터 파싱 | 입력 데이터 처리 시 | `parse-data.py` |

### 3.5 데이터 전달 상세

#### Handoff 프로토콜

```
[Team Lead → Member 호출 시 전달 내용]

1. Assignment 지시서 (프롬프트 인라인)
   - 작업 범위
   - 기대 산출물 형식
   - 참조해야 할 선행 산출물 경로 (있는 경우)

2. 컨텍스트 파일 경로 (파일 기반)
   - /output/plan.md (전체 계획 참조용)
   - /output/{preceding-member}/*.* (선행 산출물, Team Lead 판단에 의해 선택적 전달)

[Member → Team Lead 반환]

1. 산출물 파일 (파일 기반)
   - /output/{member-name}/{artifact-file}

2. 실행 메타데이터 (프롬프트 인라인)
   - 완료 상태
   - 특이사항/불확실성 보고
```

#### 중간 산출물 파일 규칙

| 규칙 | 내용 |
|------|------|
| **저장 위치** | 모든 중간 산출물은 `/output/` 하위에 저장 |
| **네이밍** | `{member-name}/{descriptive-name}.{ext}` |
| **메타데이터** | 각 산출물 첫 줄에 생성자, 생성 시각, 버전 기록 |
| **버전 관리** | 재작업 시 기존 파일 덮어쓰기 (review-log.md에 변경 이력 기록) |
| **최종 산출물** | `/output/final/` 에만 저장. Phase 4 완료 후에만 생성 |

### 3.6 Config 확장 가이드

> 새로운 업무에 팀을 구성할 때 아래 절차를 따른다.

```
1. team-config.yaml 작성
   - task 섹션: 업무명, 설명, 입출력 정의
   - team.members 섹션: 필요한 Member 수만큼 추가
   - termination 섹션: 업무 위험도에 따라 조정

2. Member별 AGENT.md 작성
   - /.claude/agents/{member-name}/AGENT.md
   - Member Template 기반으로 역할·도메인만 교체

3. (필요 시) 업무 전용 스킬 추가
   - /.claude/skills/{skill-name}/SKILL.md + /scripts/
   - config의 해당 Member skills에 등록

4. 실행
   - Task 입력 → Team Lead(CLAUDE.md)가 config 로드 → 자동 실행
```

---

## 4. 검증 매트릭스

> 전체 Phase에 걸친 검증 항목을 한눈에 정리한다.

| Phase | 단계 | 성공 기준 | 검증 유형 | 실패 처리 |
|-------|------|----------|----------|----------|
| 1 | PLAN | 모든 Member에 Assignment 배정, DAG 유효 | 규칙 기반 + LLM 자기검증 | 자동 재시도 2회 → 에스컬레이션 |
| 2 | EXECUTE (개별) | 산출물 파일 존재 + 형식 준수 + 필수 항목 포함 | 스키마 검증 + 규칙 기반 | 자동 재시도 1회 → Team Lead 분석 후 재호출 |
| 3 | REVIEW | 모든 산출물 승인 또는 직접수정 완료 | LLM 자기검증 | 재지시 (최대 N회) → 최선 버전 진행 |
| 4 | INTEGRATE | 통합 산출물 품질 기준 충족 | LLM 자기검증 + 스키마 검증 | 전체 재실행 (최대 M회) → 강제 종료 + 보고서 |
| 종료 | 사람 승인 | 사용자 승인 | 사람 검토 | 피드백 반영 후 재실행 |

---

## 5. 설계 결정 근거 (ADR)

> 주요 설계 결정의 배경과 대안 비교를 기록한다.

### ADR-1: 팀장 중재형 vs 자유 발언형

| 항목 | 팀장 중재형 (채택) | 자유 발언형 (기각) |
|------|-------------------|-------------------|
| **장점** | 예측 가능, 비용 통제, 디버깅 용이 | 유연, 창발적 결과 가능 |
| **단점** | 팀장 병목 가능 | 무한 루프 위험, 토큰 폭발, 추적 어려움 |
| **채택 이유** | [분석] Claude Code 환경에서 에이전트 간 직접 통신이 불가하므로 중재자가 필수. 또한 범용 프레임워크에서는 예측 가능성이 유연성보다 중요함 |

### ADR-2: Config-driven vs Template-based 팀 구성

| 항목 | Config-driven (채택) | Template-based (기각) |
|------|---------------------|---------------------|
| **장점** | 무한 확장, 업무별 자유 구성 | 빠른 시작, 검증된 조합 |
| **단점** | 초기 config 작성 비용 | 새로운 조합에 대응 어려움 |
| **채택 이유** | [분석] 범용 프레임워크의 핵심 가치는 재사용성. Config-driven이 장기적으로 더 적은 유지보수 비용. 자주 쓰는 조합은 /configs/ 하위에 프리셋으로 축적 가능 |

### ADR-3: 수정 규모 기반 직접수정/재지시 분기

| 항목 | 상황 판단형 (채택) | 항상 재지시 (기각) | 항상 직접수정 (기각) |
|------|------------------|-------------------|-------------------|
| **장점** | 효율 + 품질 균형 | 역할 분리 명확 | 빠른 처리 |
| **단점** | 판단 기준의 모호성 | 사소한 수정에도 재호출 비용 | 팀장 과부하, 도메인 오류 |
| **채택 이유** | [분석] 20% 미만 + 사실관계 변경 없음 + 추가 판단 불필요의 3중 조건으로 명확한 분기 기준을 제시하여 모호성을 최소화함 |

---

## 6. 기존 프로젝트 매핑 가이드

> 현재 설계 완료된 에이전트 프로젝트를 본 프레임워크에 매핑하는 방향을 제시한다.

### 6.1 산업 인텔리전스 모니터링 에이전트

| 기존 구조 | 팀 프레임워크 매핑 |
|----------|------------------|
| content-collector (서브에이전트) | Member: content-collector — 뉴스/RSS/YouTube 수집 |
| intelligence-analyst (서브에이전트) | Member: intelligence-analyst — 수집 데이터 분석·인사이트 추출 |
| report-dispatcher (서브에이전트) | Member: report-dispatcher — 리포트 포맷팅·배포 |
| 메인 오케스트레이터 | Team Lead — 수집 범위 지시, 분석 품질 검토, 리포트 통합 검토 |

[제언] 기존 3-서브에이전트 구조가 팀 프레임워크와 자연스럽게 매핑됨. 추가 이점은 Team Lead가 분석 품질을 검토하고 재작업을 지시할 수 있다는 점.

### 6.2 업무 과제 분석 AI 에이전트

| 기존 구조 | 팀 프레임워크 매핑 |
|----------|------------------|
| resource-analyst (서브에이전트) | Member: resource-analyst — xlsx 업무 데이터 분석 |
| ai-solution-designer (서브에이전트) | Member: ai-solution-designer — AI 도입 권고안 작성 |
| 메인 오케스트레이터 | Team Lead — 분석 결과 기반으로 권고안 방향 지시, 정합성 검토 |

[제언] 기존에는 resource-analyst 결과를 ai-solution-designer에 직접 전달했으나, 팀 프레임워크에서는 Team Lead가 분석 결과를 검토한 뒤 필요한 부분만 선별하여 전달함으로써 품질 게이트가 추가됨.

---

## 부록 A: Config 프리셋 예시

> 자주 사용될 것으로 예상되는 팀 구성 프리셋 목록.

| 프리셋명 | 팀원 구성 | 적합한 업무 유형 |
|---------|----------|----------------|
| `research-report` | alpha · gamma · delta · beta | 조사 → 팩트체크 → 시각화 → 보고서 작성 |
| `code-review` | alpha · gamma · beta | 코드 스캔 → 논리·보안 검증 → 리뷰 요약 |
| `multilingual-brief` | alpha · beta · delta | 조사 → 요약 → 다국어 시각자료 |
| `dev` | alpha · epsilon | 구현 방향 분석 → OpenCode 코드 수정 → 배포 |
| `data-pipeline` | data-collector + data-processor + reporter | 데이터 수집 → 가공 → 리포트 |
| `strategy-brief` | market-scanner + competitor-analyst + strategist | 시장조사 → 경쟁사 분석 → 전략 제언 |
| `document-review` | drafter + reviewer + finalizer | 초안 작성 → 검토 → 최종 편집 |

---

## 부록 B: 로그 파일 구조

### plan.md 구조

```markdown
# Execution Plan

## Task
- Name: {task name}
- Description: {description}

## Assignments

### Assignment 1: {member-name}
- 범위: ...
- 기대 산출물: /output/{member-name}/{file}
- 의존성: 없음 | Assignment N 완료 후

### Assignment 2: {member-name}
- 범위: ...
- 기대 산출물: ...
- 의존성: Assignment 1 (/output/{member-name}/{file})

## Execution Order
1. Assignment 1 (독립)
2. Assignment 2 (Assignment 1 의존)

## Dependency Map
Assignment 1 → Assignment 2
```

### review-log.md 구조

```markdown
# Review Log

## Cycle 1

### {member-name} — {artifact-file}
- 상태: 승인 | 직접수정 | 재지시
- 검토 결과: ...
- (직접수정인 경우) 수정 내용: ...
- (재지시인 경우) 수정 지시서: ...

## Cycle 2 (재지시 이후)
...

## Summary
- 총 Review Cycles: N
- 미해결 이슈: ...
```

---

*문서 끝*
