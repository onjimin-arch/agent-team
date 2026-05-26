# Agent Team Framework

This repository contains a scaffold for a Claude Code-based multi-agent team framework.

## Structure
- `CLAUDE.md` - Team Lead instructions.
- `.claude/configs/team-config.yaml` - Config-driven team definition (task types, members, distribution).
- `.claude/configs/queue-config.yaml` - Priority Queue server config (Slack port, OpenCode model, priority rules).
- `.claude/agents/` - Member agent templates and role definitions.
- `.claude/skills/` - Skill bundles and helper scripts.
- `queue_server.py` - Priority Queue server: receives Slack webhooks and direct task injections, dispatches to `opencode run`.
- `output/` - Generated artifact storage (topic-slug workspace layout).

## Task Types
| Type | Members | Triggers |
|------|---------|---------|
| `research-report` (default) | alpha · gamma · delta · beta | 리서치, 분석, 보고서, 시장 … |
| `code-review` | alpha · gamma · beta | 코드 리뷰, PR, code review … |
| `multilingual-brief` | alpha · beta · delta | 영문, 번역, 다국어, translate … |
| `dev` | alpha · epsilon | 개발, 코드, 버그, fix, deploy … |

## Team Members
| Member | Role | Primary Output |
|--------|------|---------------|
| member-alpha | 시장 조사·데이터 분석 | `analysis-report.md` |
| member-beta | 보고서 초안 작성 | `draft-report.md` |
| member-gamma | 팩트체커 (WebSearch/WebFetch) | `fact-check-log.md` |
| member-delta | 시각화 (Mermaid·테이블) | `visuals.md` |
| member-epsilon | Dev Agent (OpenCode headless) | `dev-log.md` |

## How to use
1. Edit `.claude/configs/team-config.yaml` to define the task, team members, and termination rules.
2. Customize member `AGENT.md` files under `.claude/agents/`.
3. Write or adapt skills under `.claude/skills/`.
4. Run the Team Lead process in Claude Code, using `CLAUDE.md` as the agent prompt.

### Running the Priority Queue Server
```bash
pip install flask pyyaml
python queue_server.py          # starts on port 5000 (configurable in queue-config.yaml)

# Inject a task directly
curl -X POST http://localhost:5000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "신규 주제 [dev] 로그인 버그 수정"}'

# Check queue status
curl http://localhost:5000/status
```

Priority tags (prepend to any message): `!urgent` → 0, `!task` → 1 (default), `!schedule` → 2

## Notes
- The framework is file-based and designed for sequential Claude Code execution.
- `output/plan.md`, `output/review-log.md`, and `output/final/` are the primary workflow outputs.
- Workspaces are topic-slug based under `output/{topic-slug}/`. Active workspace is tracked in `output/.active-workspace`.
- Deployment commands (`git push`, `npm run deploy`) require Team Lead human approval before execution.
