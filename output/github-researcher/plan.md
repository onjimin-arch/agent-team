# 작업 계획서

생성: Team Lead | 생성시각: 2026-05-26 | 워크스페이스: github-researcher

## 작업 요약

GitHub 공개 레포 탐색·코드 패턴 분석·구현 계획 입력 생성을 담당하는 신규 팀 멤버
**member-eta (GitHub Researcher)**를 프레임워크에 추가한다.

생성 산출물 3개:
1. `.claude/agents/member-eta/AGENT.md` — 멤버 역할 정의
2. `.claude/skills/github-researcher/SKILL.md` — 전용 스킬
3. `team-config-patch.yaml` — team-config.yaml에 병합할 패치

## 선택된 Task Type

- **Type**: `design`
- **근거**: 사용자 요청에 `[design]` 태그 명시
- **활성 멤버**: member-alpha, member-zeta

## 활성 멤버

| 멤버 | 역할 | 담당 산출물 |
|------|------|-----------|
| member-zeta | 개발 설계 담당 | 산출물 1 (AGENT.md) + 산출물 2 (SKILL.md) |
| member-alpha | 데이터 분석·config 설계 | 산출물 3 (team-config-patch.yaml) |

## 작업 분해

### member-zeta 배정

기존 AGENT.md 형식(member-gamma, member-zeta 참조)을 따라 아래 섹션을 포함하는
`.claude/agents/member-eta/AGENT.md`를 작성한다:
- Identity & Role, Assignment Protocol, Execution Rules (Step 1–8)
- Revision Protocol, Skills & Tools Reference, Constraints

기존 SKILL.md 형식을 참조하여 `.claude/skills/github-researcher/SKILL.md`를 작성한다:
- Purpose, When to Use, Pre-Check Routine, Search Command Reference
- Quality Filter Script Interface, License Audit Logic, Cleanup Rule

### member-alpha 배정

기존 team-config.yaml 스키마를 분석하여 `task.types`에 추가할 `github-plan`과
`team.members`에 추가할 `member-eta` 항목을 담은 패치 파일을 작성한다.

## 실행 순서

1. member-zeta와 member-alpha 병렬 실행
2. Team Lead: 3개 파일 Review
3. Team Lead: `WS/final/final-artifact.md` 생성

## 의존성 맵

```
member-zeta (AGENT.md + SKILL.md)  ─┐
                                    ├─→ final-artifact.md
member-alpha (team-config-patch)   ─┘
```

- member-zeta와 member-alpha 간 의존 없음 (병렬 가능)
- final-artifact.md는 3개 파일 모두 완료 후 생성
