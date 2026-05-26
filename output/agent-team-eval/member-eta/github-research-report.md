# GitHub Research Report
생성자: member-eta | 생성시각: 2026-05-26 | 버전: v1

---

## 탐색 조건

| 항목 | 값 |
|------|-----|
| 탐색 키워드 | "multi-agent framework claude code", "claude agent team", "multi-agent LLM orchestration" |
| 평가 대상 | Claude Code 기반 또는 비교 가능한 멀티에이전트 프레임워크 |
| 품질 필터 | Stars 100+, 라이선스 MIT/Apache 우선 |

---

## 탐색 결과 요약

| 레포 | Stars(추정) | 라이선스 | 선정 이유 |
|------|-----------|---------|---------|
| `wshobson/agents` | 高 | MIT | 가장 대규모. 191 agent, 155 skill, 83 plugin. 멀티하네스 지원 |
| `ciscoittech/claude-agent-framework` | 中 | MIT | 병렬 에이전트 실행, 97% context reduction 주장. 구조 참조 가치 高 |
| `lucasbrandao4770/claude-agent-teams` | 中 | MIT | 파일 오너십 강제, 8개 팀 템플릿, Leader/Specialist 패턴 |
| `Gentleman-Programming/agent-teams-lite` | 中 | MIT | Spec-Driven. orchestrator + 9 sub-agents. 순수 Markdown |
| `aws-samples/sample-claude-code-agent-team` | 中 | Apache 2.0 | AWS 공식 샘플. Spec-driven, 부모-자식 에이전트 패턴 |

---

## 레포별 상세 분석

### 1. `wshobson/agents` ✅ MIT
**아키텍처 패턴**: Plugin marketplace. 78개 단일 책임 플러그인으로 분리. 설치 단위로 토큰 소비 분리 (python-development 설치 → 해당 에이전트 3개 + 스킬 16개만 로드, ~1,000 토큰).

**핵심 특징**:
- 멀티하네스 단일 소스: Claude Code, Codex CLI, Cursor, OpenCode, Gemini CLI에서 동일 Markdown 사용
- Conductor 플러그인: 멀티에이전트 워크플로우 오케스트레이터
- 52개 슬래시 커맨드로 풀스택·보안·ML 파이프라인 워크플로우 실행

**우리 프레임워크와 차이점**: task type 개념 없음. 멤버 고정 역할 없음 대신 플러그인 조합 방식.

---

### 2. `ciscoittech/claude-agent-framework` ✅ MIT
**아키텍처 패턴**: Explorer → Builder → Reviewer 3단계 팬아웃. 병렬 실행(탐색 3~6개, 빌드 최대 8개, 리뷰 5개).

**핵심 특징**:
- 6개 전문화 에이전트 유형: Architecture, Engineering, Product, Security, Operations, Design
- SYSTEM_GENERATOR_PROMPT.md 기반 프로젝트별 커스텀 에이전트 자동 생성
- 97% context reduction, 3~6× 속도 향상 주장

**우리 프레임워크와 차이점**: 병렬 실행 구조. 우리는 현재 순차 실행 기반.

---

### 3. `lucasbrandao4770/claude-agent-teams` ✅ MIT
**아키텍처 패턴**: Leader/Specialist 패턴. 에이전트별 파일 오너십 명시적 강제.

**핵심 특징**:
- 파일 오너십: 2개 에이전트가 동일 파일 편집 불가 → 충돌 원천 차단
- 8개 사전 빌드 팀 템플릿 (코드리뷰, 디버깅, 풀스택 등)
- `--dry` 플래그: 실제 실행 전 팀 구성 미리보기
- 비용 최적화 기본값: Opus lead + Sonnet workers

**우리 프레임워크와 차이점**: 파일 오너십 강제 규칙이 명시적. 우리는 "절대 금지" 텍스트 규칙만 존재.

---

### 4. `Gentleman-Programming/agent-teams-lite` ✅ MIT
**아키텍처 패턴**: Spec-Driven. orchestrator + 9 sub-agents. Zero dependencies, 순수 Markdown.

**핵심 특징**:
- spec 문서 → 에이전트 태스크 자동 분해
- 멀티하네스 (Claude Code, OpenCode, Cursor 등)
- 의존성 없음, Markdown만으로 동작

**우리 프레임워크와 차이점**: spec 문서 중심 설계. 우리의 plan.md와 개념적으로 유사하나 자동화 수준 상이.

---

### 5. `aws-samples/sample-claude-code-agent-team` ✅ Apache 2.0
**아키텍처 패턴**: 부모-자식 에이전트. Full Stack Developer 부모 → Coding/DevOps/Review 자식 에이전트.

**핵심 특징**:
- Spec-driven 개발 프로세스
- 역할별 3개 전문 에이전트
- AWS 공식 샘플 → 엔터프라이즈 패턴 참조 가치

**우리 프레임워크와 차이점**: 도메인이 소프트웨어 개발 전용. 우리는 리서치·분석 도메인 포함.

---

## 크로스 레포 공통 패턴

1. **역할 분리 + 파일 소유권**: 모든 프레임워크가 에이전트별 책임 범위를 명확히 분리
2. **오케스트레이터 패턴**: Lead/Conductor 에이전트가 조율, 나머지는 실행
3. **파일 기반 데이터 전달**: 에이전트 간 직접 통신 대신 파일을 통한 핸드오프
4. **Markdown 명세**: 에이전트 역할을 코드 아닌 Markdown으로 정의
5. **병렬 실행 지향**: 상위 프레임워크일수록 병렬성 강조

---

## 안티패턴 (품질 신호 기반)

| 안티패턴 | 발견된 레포 | 리스크 |
|---------|-----------|-------|
| 단일 거대 AGENT.md (역할 과부하) | 일부 소규모 레포 | 컨텍스트 오염, 역할 혼선 |
| 에이전트 간 직접 파일 수정 | 파일 오너십 미적용 레포 | 충돌, 덮어쓰기 |
| task type 없이 모든 에이전트 항시 활성화 | 단순 구현체 | 불필요한 비용, 컨텍스트 낭비 |
| 하드코딩된 멤버 구성 | config-less 구현체 | 확장성 부재 |

---

## Planner를 위한 권고 스택·접근법

현재 프레임워크가 이미 올바른 방향이며, 아래 패턴을 우선 보완 검토 권장:

1. **병렬 실행** (`ciscoittech` 패턴): 의존 없는 멤버들의 동시 실행 구조
2. **파일 오너십 강제** (`claude-agent-teams` 패턴): 텍스트 규칙 → 명시적 오너십 테이블
3. **플러그인 단위 스킬 로딩** (`wshobson` 패턴): task type에 따라 필요 스킬만 로드

---

## 출처 목록

| 레포명 | 라이선스 | URL |
|-------|---------|-----|
| wshobson/agents | MIT | https://github.com/wshobson/agents |
| ciscoittech/claude-agent-framework | MIT | https://github.com/ciscoittech/claude-agent-framework |
| lucasbrandao4770/claude-agent-teams | MIT | https://github.com/lucasbrandao4770/claude-agent-teams |
| Gentleman-Programming/agent-teams-lite | MIT | https://github.com/Gentleman-Programming/agent-teams-lite |
| aws-samples/sample-claude-code-agent-team | Apache 2.0 | https://github.com/aws-samples/sample-claude-code-agent-team |
