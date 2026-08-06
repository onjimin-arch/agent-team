# Agent Team Framework

Claude Code 기반 다중 에이전트 팀 프레임워크. 팀장(Team Lead)이 작업 유형을 판별하고 역할별 멤버 에이전트를 순서대로 호출하여 최종 산출물을 생성합니다. Slack을 통해 지시를 내리고 결과를 받습니다.

---

## 디렉토리 구조

```
agent-team/
├── CLAUDE.md                          # 팀장 프롬프트 (핵심 운영 규칙)
├── .claude/
│   ├── configs/
│   │   └── team-config.yaml           # 팀 구성, 태스크 유형, 배포 설정
│   ├── agents/                        # 멤버별 AGENT.md 프롬프트
│   │   ├── member-alpha/
│   │   ├── member-beta/
│   │   ├── member-gamma/
│   │   ├── member-delta/
│   │   ├── member-epsilon/
│   │   ├── member-zeta/
│   │   ├── member-eta/
│   │   └── member-reviewer/
│   └── skills/                        # 공용 스킬 (file-io, deploy-heal 등)
├── slack-bridge/                      # Slack ↔ 팀장 연결 봇
│   ├── app.py                         # Slack 봇 (Socket Mode)
│   ├── agent_runner.py                # opencode run 서브프로세스 실행기
│   ├── state.py                       # 작업 상태·스레드 매핑 관리
│   ├── run-forever.ps1                # app.py 상시 실행 + 자동 재시작 감시 스크립트
│   ├── register-always-on-task.ps1    # 위 감시 스크립트를 작업 스케줄러에 등록 (관리자 권한 필요)
│   └── requirements.txt
└── output/                            # 산출물 저장소 (워크스페이스별 폴더)
    └── .active-workspace              # 현재 활성 작업 슬러그 포인터
```

> 다른 PC에서도 봇을 돌리려면 `app-B-<hostname>.py`/`-B-<hostname>.env` 사본을 만들어 관리합니다
> (반드시 별도 Slack 앱/토큰으로 — 같은 토큰으로 두 프로세스를 동시에 띄우면 이벤트 중복 수신·상태 파일
> 경합이 발생합니다). 예전 사본은 `_archive/2026-07-29-cleanup/`에 보관돼 있습니다.

---

## 팀 구성

| 멤버 | 역할 | 주요 산출물 |
|------|------|------------|
| **member-alpha** | 시장 조사·데이터 분석 | `analysis-report.md` |
| **member-beta** | 최종 보고서 초안 작성 | `draft-report.md` |
| **member-gamma** | 팩트체커 (인용·수치·출처 검증) | `fact-check-log.md` |
| **member-delta** | 시각화 (Mermaid·테이블·차트 스펙) | `visuals.md` |
| **member-epsilon** | 개발 태스크 실행 (코드 수정·검증·배포) | `dev-log.md`, `diff-summary.md` |
| **member-zeta** | 에이전트 설계서 작성 | `design-spec.md` |
| **member-eta** | GitHub 공개 레포 탐색·라이선스 감사 | `github-research-report.md` |
| **member-reviewer** | 산출물 품질 검토 (팀장 보조) | 리뷰 코멘트 |

---

## 태스크 유형

| 유형 | 멤버 흐름 | 트리거 키워드 |
|------|-----------|--------------|
| `research-report` (기본값) | alpha → gamma → delta → beta | 리서치, 분석, 보고서, 시장, 정책, 현황 |
| `code-review` | alpha → gamma → beta | 코드 리뷰, PR, 풀리퀘, code review, 리뷰해 |
| `multilingual-brief` | alpha → beta → delta | 영문, 번역, 다국어, translate, 브리프 |
| `dev` | **eta** → alpha → epsilon | 개발, 코드, 배포, 수정, 버그, 기능 추가, fix, deploy |
| `design` | alpha → zeta | 설계, 설계서, 아키텍처, 시스템 설계, design, spec |
| `github-plan` | eta → alpha → beta | 깃허브, 오픈소스 참고, github, 공개 코드, 레퍼런스 찾아 |

> **dev 타입**: eta가 GitHub 공개 레포 5개 이상을 먼저 탐색하여 구현 레퍼런스를 수집한 뒤, alpha가 방향을 분석하고 epsilon이 코드를 수정·배포합니다.

---

## Slack 사용법

### 채널 메시지 (일반 요청)

Slack 채널에 작업 내용을 그냥 입력하면 됩니다:

```
새 작업 [리서치] 국내 퀵커머스 시장 현황 분석해줘
새 작업 [dev] 로그인 버그 수정 - 토큰 만료 시 재로그인 안 됨
새 작업 [설계] queue_server 없이 Slack 직접 연동하는 아키텍처 설계해줘
새 작업 [깃허브] FastAPI 기반 큐 시스템 오픈소스 참고해서 구현 계획 세워줘
```

`새 작업` (`team-config.yaml`의 `execution.workspace.new_topic_trigger` 값)을 포함하면 새 워크스페이스를 생성합니다.

### 스레드 메시지 (기존 작업 후속)

진행 중인 작업 스레드에 답글을 달면 같은 워크스페이스에서 후속 작업으로 처리됩니다:

```
(기존 스레드에) 결론 부분을 더 간결하게 다듬어줘
(기존 스레드에) 수치 출처 다시 확인해줘
```

### DM 메시지 (채널 작업 후속)

봇에게 DM을 보내면 최근 진행한 채널 작업의 후속으로 처리됩니다.

### AUTO 모드

`[AUTO: {슬러그}]` 접두사를 붙이면 팀장이 중단 없이 Phase 1~5를 자동 실행합니다:

```
[AUTO: quickcommerce-analysis] 국내 퀵커머스 시장 점유율 분석 보고서 작성
```

### 작업 취소

```
취소
```

---

## 실행 방법

### 0. Git Pre-commit Hook 활성화 (최초 1회)

이 저장소에는 `team-config.yaml`과 `.claude/skills/dept-dashboard-reader/SKILL.md`처럼 같은
정보를 이중 관리하는 파일들이 있다. 한쪽만 고치고 커밋하면 서로 다른 사실을 가리키게 되는 걸
막기 위해 커밋 직전 자동 검사를 도는 Git 훅을 저장소에 함께 두었다(`scripts/git-hooks/`). 다만
`.git/hooks/`는 버전 관리되지 않으므로, **클론(또는 이 저장소를 새로 내려받은 환경)마다 최초
1회** 아래 명령으로 직접 연결해야 한다(`git clone`이 자동으로 해주지 않는다):

```bash
git config core.hooksPath scripts/git-hooks
```

### 1. 환경 설정

```bash
cd slack-bridge
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

`.env` 파일 생성 (`.env.example` 참고):

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_REPORT_CHANNEL=#agent-log
AGENT_MODEL=anthropic/claude-sonnet-4-6
```

### 2. Slack 봇 실행

```bash
# 이지민 PC
cd slack-bridge
.venv\Scripts\python app.py

# 상시 실행 + 자동 재시작 (재부팅/로그오프 이후에도 유지) — 관리자 PowerShell에서:
.\register-always-on-task.ps1
```

### 3. 팀장 직접 실행 (CLI)

Slack 없이 팀장을 직접 호출할 때:

```bash
cd agent-team
opencode run --dangerously-skip-permissions
```

---

## 워크스페이스 구조

작업마다 `output/{topic-slug}/` 폴더가 생성됩니다:

```
output/
├── .active-workspace                  # 현재 활성 슬러그 (예: quickcommerce-analysis)
├── quickcommerce-analysis/
│   ├── plan.md                        # 팀장 실행 계획
│   ├── member-alpha/analysis-report.md
│   ├── member-gamma/fact-check-log.md
│   ├── member-delta/visuals.md
│   ├── member-beta/draft-report.md
│   ├── review-log.md                  # 팀장 리뷰 코멘트
│   └── final-report.md                # 최종 통합 산출물
└── login-bug-fix/
    ├── member-eta/github-research-report.md
    ├── member-alpha/analysis-report.md
    └── member-epsilon/dev-log.md
```

---

## 배포 (Phase 5)

최종 산출물은 다음 채널로 자동 배포됩니다:

| 채널 | 설정 위치 | 비고 |
|------|-----------|------|
| **Slack** | `distribution.slack` in team-config.yaml | 결과 링크 전송 |
| **Notion** | `distribution.notion` in team-config.yaml | 리서치/분석 DB 저장 |
| Gmail / Google Drive | 비활성화 (`enabled: false`) | 필요 시 인증 후 활성화 |

---

## 설정 파일

| 파일 | 역할 |
|------|------|
| `CLAUDE.md` | 팀장 운영 프로토콜 (Phase 1~5, AUTO 모드, 종료 조건) |
| `.claude/configs/team-config.yaml` | 팀 구성·태스크 유형·배포 설정 |
| `.claude/agents/*/AGENT.md` | 각 멤버의 역할·출력 스펙 |
| `.claude/skills/` | 공용 스킬 번들 |

---

## 참고

- 산출물은 파일 기반으로 주고받습니다 (`data_passing: file_based`).
- 팀장이 작업 유형을 자동 판별합니다. 트리거 키워드가 없으면 `research-report`(기본값)로 처리됩니다.
- `dev` 타입의 배포 명령(`git push`, `npm run deploy`)은 팀장이 결과 확인 후 실행합니다.
- 핵심 설정 변경 시 CLAUDE.md, team-config.yaml, 관련 AGENT.md를 함께 업데이트해야 합니다.
