---
Creator: member-delta
Created: 2026-05-26
Version: 1.0
---

# 시각자료: Claude Code Agent Team 멀티에이전트 시스템

---

## 시각자료 개요

| 자료 번호 | 유형 | 제목 | 출처 데이터 |
|---|---|---|---|
| V-01 | Mermaid flowchart | 전체 파이프라인 Phase 흐름 | alpha analysis-report §2 |
| V-02 | Mermaid graph | 멤버 의존성 맵 (research-report 타입) | alpha analysis-report §1.3 |
| V-03 | Mermaid mindmap | Task Type별 활성 멤버 구조 | alpha analysis-report §1.2 |
| V-04 | 비교 테이블 | Task Type 요약 | alpha analysis-report §1.2 |
| V-05 | 비교 테이블 | 강점 vs 개선 영역 | alpha analysis-report §3~4 |

---

## Mermaid 다이어그램

### V-01: 전체 파이프라인 Phase 흐름

팀장이 수행하는 5개 Phase와 각 단계 산출물의 흐름을 나타낸다.

```mermaid
flowchart TD
    U[사용자 요청] --> P1

    subgraph P1["Phase 1: Planning"]
        direction TB
        P1a[Task Type 판별] --> P1b[멤버 배정]
        P1b --> P1c[plan.md 생성]
    end

    subgraph P2["Phase 2: Execution"]
        direction TB
        M_G[member-gamma\n원천 데이터 수집] --> M_A[member-alpha\n분석·인사이트]
        M_A --> M_D[member-delta\n시각화]
        M_A --> M_B[member-beta\n보고서 초안]
    end

    subgraph P3["Phase 3: Review"]
        direction TB
        R[member-reviewer\n독립 리뷰] --> |APPROVE| APR[승인]
        R --> |EDIT| EDT[직접 수정\n≤30%]
        R --> |REASSIGN| RAS[재배정\n>30%]
    end

    subgraph P4["Phase 4: Integration"]
        direction TB
        INT[팀장 통합] --> FA[final-artifact.md]
    end

    subgraph P5["Phase 5: Distribution"]
        direction TB
        NOT[Notion 저장] --> LOG[review-log.md\nDistribution 기록]
    end

    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
```

### V-02: 멤버 의존성 맵 (research-report 타입)

research-report 타입에서 멤버 간 데이터 흐름과 의존 관계를 나타낸다.

```mermaid
graph LR
    GMA[member-gamma\nfact-check-log.md] -->|원천 데이터| ALP[member-alpha\nanalysis-report.md]
    ALP -->|분석 결과| DLT[member-delta\nvisuals.md]
    ALP -->|분석 결과| BTA[member-beta\ndraft-report.md]
    DLT -->|시각자료| INT[팀장 통합\nfinal-artifact.md]
    BTA -->|보고서 초안| INT
```

### V-03: Task Type별 활성 멤버 구조

6개 task type 각각의 활성 멤버 조합을 나타낸다.

```mermaid
mindmap
  root((Agent Team\nTask Types))
    research-report
      alpha
      beta
      gamma
      delta
    code-review
      alpha
      gamma
      beta
    multilingual-brief
      alpha
      beta
      delta
    dev
      alpha
      epsilon
    design
      alpha
      zeta
    github-plan
      eta
      alpha
      beta
```

---

## 핵심 수치 테이블

### T-01: Task Type 요약

| Task Type | 활성 멤버 수 | 핵심 산출물 | Default |
|---|---|---|---|
| research-report | 4명 (alpha·beta·gamma·delta) | analysis-report + draft-report + visuals | ✅ |
| code-review | 3명 (alpha·gamma·beta) | analysis-report + fact-check-log + draft-report | ✗ |
| multilingual-brief | 3명 (alpha·beta·delta) | analysis-report + draft-report + visuals | ✗ |
| dev | 2명 (alpha·epsilon) | analysis-report + dev-log + diff-summary | ✗ |
| design | 2명 (alpha·zeta) | analysis-report + design-spec | ✗ |
| github-plan | 3명 (eta·alpha·beta) | github-research-report + analysis-report + draft-report | ✗ |

### T-02: Termination 파라미터

| 파라미터 | 값 | 의미 |
|---|---|---|
| max_cycles | 3 | 최대 실행 사이클 수 |
| max_review_per_member | 2 | 멤버당 최대 리뷰 횟수 |
| human_approval | false | 자동 승인 (사용자 확인 불필요) |
| auto_proceed_on_escalation | true | 에스컬레이션 시 자동 계속 진행 |
| review_direct_edit_threshold | 30% | 직접 수정 가능 최대 변경량 |

### T-03: Distribution 엔드포인트 현황

| 엔드포인트 | 상태 | 비고 |
|---|---|---|
| Notion | ✅ 활성 | data_source_id: 348363ae-... |
| Gmail | ❌ 비활성 | 인증 후 활성화 예정 |
| Google Drive | ❌ 비활성 | 인증 후 활성화 예정 |
| Google Calendar | ❌ 비활성 | 인증 후 활성화 예정 |

### T-04: 강점 vs 개선 영역 요약

| 구분 | 항목 | 영향도 |
|---|---|---|
| 강점 | 역할 격리 원칙 | 높음 |
| 강점 | 파일 기반 핸드오프 | 높음 |
| 강점 | AUTO 모드 완전 무인화 | 높음 |
| 강점 | Task Type 동적 팀 구성 | 중간 |
| 강점 | 품질 3단계 검증 | 중간 |
| 개선 | alpha 단일 의존도 | 높음 |
| 개선 | direct_edit_threshold 불일치 | 낮음 |
| 개선 | WebSearch 환경 의존성 | 중간 |
| 개선 | AGENT.md 정기 감사 부재 | 낮음 |
