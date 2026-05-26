# Plan: 에이전트 팀 셀프 검증

## Task Summary
에이전트 팀 구성 파일(CLAUDE.md, team-config.yaml, 각 AGENT.md)을 검토하여
역할 정의·경로·설정 간의 일관성과 누락을 확인한다.

## 선택된 Task Type
- **Type**: `code-review`
- **근거**: 설정 파일 구조 검토·검증 작업
- **활성 멤버**: alpha · gamma · beta

## 검토 대상 파일
- `CLAUDE.md`
- `.claude/configs/team-config.yaml`
- `.claude/agents/member-alpha/AGENT.md`
- `.claude/agents/member-beta/AGENT.md`
- `.claude/agents/member-gamma/AGENT.md`
- `.claude/agents/member-delta/AGENT.md`
- `.claude/agents/member-epsilon/AGENT.md`
- `.claude/agents/member-zeta/AGENT.md`

## Assignments

| 멤버 | 역할 | 산출물 |
|------|------|--------|
| member-alpha | 전체 파일 구조 분석 — 역할 정의, task type 매핑, 산출물 경로 일관성 점검 | `member-alpha/analysis-report.md` |
| member-gamma | 팩트체크 — 파일 존재 여부, 경로 정합성, 설정값 유효성 확인 | `member-gamma/fact-check-log.md` |
| member-beta | 검증 결과 통합 보고서 작성 | `member-beta/draft-report.md` |

## Execution Order
1. alpha (독립 분석)
2. gamma (독립 팩트체크) — alpha와 병렬 가능
3. beta (alpha + gamma 결과 참조하여 보고서 작성)

## Dependency Map
- beta → alpha, gamma 결과 필요
- alpha, gamma → 상호 독립

---

# Plan: Slack 트리거 에이전트 구현

## Task Summary
Slack Bot (Socket Mode)으로 agent-team 을 원격 작동시키는 시스템 구현.
슬랙 @mention 메시지 → 에이전트 팀 실행 → 결과 슬랙 스레드 전송.

## 선택된 Task Type
- **Type**: `dev`
- **근거**: "구현" → implement 에 해당
- **활성 멤버**: member-alpha · member-epsilon

## Assignments

| 멤버 | 역할 | 산출물 |
|------|------|--------|
| member-alpha | Slack Socket Mode + Claude CLI 연동 기술 설계 | (팀장이 직접 처리) |
| member-epsilon | `slack-bot/` 폴더 전체 구현 + CLAUDE.md 자동 모드 추가 | `slack-bot/` |

## 구현 파일 목록

| 파일 | 역할 |
|------|------|
| `slack-bot/bot.py` | Slack Socket Mode 리스너. @mention 수신 → 즉시 응답 후 백그라운드 스레드로 에이전트 실행 |
| `slack-bot/runner.py` | `claude --print` CLI 호출 래퍼. `[AUTO: slug]` 프롬프트로 비대화형 실행. final-artifact.md 읽어 반환 |
| `slack-bot/requirements.txt` | `slack-bolt`, `python-dotenv` |
| `slack-bot/.env.example` | 토큰 설정 템플릿 + Slack 앱 설정 가이드 |
| `CLAUDE.md` (수정) | `### 자동 모드` 섹션 추가 — `[AUTO: slug]` 수신 시 슬러그 확인 생략 |

## 실행 흐름
```
Slack @mention
  └→ bot.py: 즉시 "⏳ 시작" 메시지 전송
  └→ runner.py (백그라운드 스레드)
       └→ claude --print "[AUTO: slack-YYYYMMDD-HHMMSS]\n새 작업\n{task}"
            └→ CLAUDE.md Phase 1~4 실행
                 └→ output/{slug}/final/final-artifact.md 생성
       └→ final-artifact.md 읽어 Slack 스레드에 전송
```

## Execution Order
1. CLAUDE.md 자동 모드 섹션 추가 (완료)
2. slack-bot/ 구현 파일 작성 (완료)
3. 설치 및 토큰 설정
4. 테스트: `python slack-bot/runner.py 테스트 작업`
