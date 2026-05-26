# Agent Team Self-Upgrade: member-eta (GitHub Researcher) 추가

생성: Team Lead | 일시: 2026-05-26 | 워크스페이스: github-researcher

---

## 개요

GitHub 공개 레포 탐색·코드 패턴 분석·라이선스 감사 전담 멤버 **member-eta**를
에이전트 팀 프레임워크에 추가한다. 이 문서는 생성된 3개 산출물의 최종본과
설치 방법을 포함한다.

---

## 산출물 1: `.claude/agents/member-eta/AGENT.md`

**역할**: GitHub Researcher — gh CLI 기반 공개 레포 탐색, 코드 패턴 추출, 라이선스 감사,
탐색 결과를 `github-research-report.md`로 저장.

**파일 위치**: `.claude/agents/member-eta/AGENT.md`

**핵심 동작 요약**:

| 단계 | 수행 내용 |
|------|---------|
| Step 1 | `gh auth status` 인증 확인 (실패 시 에스컬레이션) |
| Step 2 | rate limit 확인 (Remaining < 10 → 중단) |
| Step 3 | `gh search repos` + `gh search code` 후보 수집 |
| Step 4 | Stars / 커밋 시점 / 라이선스 품질 필터 |
| Step 5 | 상위 3~5개 shallow clone → 구조·핵심 파일 분석 |
| Step 6 | LICENSE 감사 (✅ MIT/Apache · ⚠️ GPL · 🚫 없음 · 🔺 불명확) |
| Step 7 | `WS/member-eta/github-research-report.md` 저장 |
| Step 8 | `/tmp/research/` 클린업 |

---

## 산출물 2: `.claude/skills/github-researcher/SKILL.md`

**역할**: member-eta 전용 스킬. gh CLI 명령 레퍼런스, rate limit 보호, 라이선스 매핑
테이블, filter-repos.py 스크립트 명세, 클린업 규칙 제공.

**파일 위치**: `.claude/skills/github-researcher/SKILL.md`

**포함 섹션**:
- Pre-Check Routine (gh auth + rate limit)
- Search Command Reference (repos / code / metadata / clone)
- Quality Filter Script Interface (filter-repos.py 입출력 명세)
- License Audit Logic (5개 케이스 매핑 테이블)
- Cleanup Rule

---

## 산출물 3: `team-config-patch.yaml`

**역할**: 기존 `team-config.yaml`에 병합할 패치. `github-plan` task type과
`member-eta` 멤버 정의를 추가한다.

**파일 위치**: `team-config-patch.yaml` (프로젝트 루트)

**추가 내용 요약**:

```yaml
task.types 추가:
  - name: github-plan
    triggers: [깃허브, 오픈소스 참고, github, 공개 코드, 레퍼런스 찾아, 비슷한 구현, 코드 학습]
    members: [member-eta, member-alpha, member-beta]

team.members 추가:
  - name: member-eta
    role: GitHub 공개 레포 탐색·코드 패턴 분석·라이선스 감사 담당
    agent_md: .claude/agents/member-eta/AGENT.md
    skills: [github-researcher, shared/file-io]
    output.directory: member-eta
    primary_file: github-research-report.md
```

---

## 설치 방법

```bash
# 1. member-eta 에이전트 디렉토리 생성 (이미 생성된 경우 skip)
mkdir -p .claude/agents/member-eta

# 2. 스킬 디렉토리 생성 (이미 생성된 경우 skip)
mkdir -p .claude/skills/github-researcher

# 3. 파일 확인
#    .claude/agents/member-eta/AGENT.md    ← 이미 생성됨
#    .claude/skills/github-researcher/SKILL.md  ← 이미 생성됨

# 4. team-config.yaml에 패치 내용 수동 병합
#    team-config-patch.yaml 파일을 열어 task.types 배열 끝에
#    github-plan 항목을 추가하고, team.members 배열 끝에
#    member-eta 항목을 추가한다.

# 5. gh CLI 설치 확인 (미설치 시)
winget install --id GitHub.cli -e   # Windows
brew install gh                      # macOS
sudo apt install gh                  # Debian/Ubuntu

# 6. GitHub 인증
gh auth login

# 7. 인증 확인
gh auth status
```

---

## CLAUDE.md Team Members Quick Reference 업데이트 안내

`CLAUDE.md`의 "Team Members Quick Reference" 테이블에 아래 행을 추가한다:

```markdown
| member-eta | GitHub Researcher (gh CLI 탐색·라이선스 감사) | `github-research-report.md` | github-plan |
```

`README.md`의 Team Members 테이블에도 동일하게 추가 권장.

---

## 검증 완료 체크리스트

- [x] `.claude/agents/member-eta/AGENT.md` 생성 — 기존 AGENT.md와 섹션 구조 동일
- [x] `.claude/skills/github-researcher/SKILL.md` 생성 — 기존 SKILL.md와 형식 동일
- [x] `team-config-patch.yaml` 생성 — 기존 YAML 스키마 호환
- [x] 라이선스 처리 규칙 4종 (✅/⚠️/🚫/🔺) 모두 포함
- [x] rate limit 보호 규칙 포함 (Remaining < 10 → 중단)
- [x] 설치 방법 포함
