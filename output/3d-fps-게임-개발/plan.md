# Plan: 3D FPS 게임 개발
자동 확정된 slug: 3d-fps-게임-개발
생성시각: 2026-05-30

## Task 요약
3D FPS(1인칭 슈팅) 게임을 개발한다. GitHub 공개 레포를 참조해 아키텍처와 구현 전략을 수립하고, 실제 코드를 작성·검증·배포한다.

## Task Type 판별
| Task Type | 매칭 키워드 | Score |
|-----------|-----------|-------|
| **dev** ✅ | 개발 | 1/10 |
| research-report | - | 0/8 |
| code-review | - | 0/5 |
| multilingual-brief | - | 0/6 |
| design | - | 0/8 |
| github-plan | - | 0/7 |

선택: **dev** (최고 score, 기본값 아님)

## 활성 멤버
- **member-eta**: GitHub Researcher — 3D FPS 오픈소스 레포 탐색·라이선스 감사
- **member-alpha**: 구현 방향 분석 — eta 보고서 기반 구현 전략 수립
- **member-epsilon**: Dev Agent — 실제 코드 작성·검증·배포

## 실행 순서 (dev 타입 선행 규칙)
```
Phase 2-1: member-eta  (선행 필수)
           ↓
Phase 2-2: member-alpha (eta 보고서 의존)
           ↓
Phase 2-3: member-epsilon (alpha 분석 의존)
```

## 배정 내용

### member-eta
- 검색 키워드: "3d fps game", "first person shooter engine", "fps game python", "godot fps", "unity fps"
- 언어 필터: Python, C#, GDScript, C++
- 품질 기준: Stars 100+, 최근 18개월 커밋
- 라이선스: MIT / Apache 2.0 우선
- 산출물: `WS/member-eta/github-research-report.md`

### member-alpha
- 입력: `WS/member-eta/github-research-report.md`
- 역할: 구현 전략 수립, 참조 코드와 독자 구현 구분, epsilon 실행 가능 수준의 구현 방향서
- 산출물: `WS/member-alpha/analysis-report.md`

### member-epsilon
- 입력: `WS/member-alpha/analysis-report.md`
- 역할: 실제 3D FPS 게임 코드 작성 → 자체 검증 → 배포
- 산출물: `WS/member-epsilon/dev-log.md`, `WS/member-epsilon/diff-summary.md`

## 최종 산출물
`WS/final/final-artifact.md`

## 자동 확정 후 Phase 2 진입
타임스탬프: 2026-05-30 (human_approval: false)
