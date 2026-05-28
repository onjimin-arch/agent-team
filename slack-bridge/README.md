# Slack Bridge

Slack DM 또는 채널 멘션으로 팀장 에이전트를 호출하기 위한 로컬 브릿지. Socket Mode 로 동작하므로 공용 URL 이 필요 없으며, 산출물은 로컬 경로(`output/{topic-slug}/`)에 저장됩니다.

## 구성 요소

| 파일 | 역할 |
|------|------|
| `app.py` | Slack Bolt Socket Mode 봇 — DM/멘션 수신, 스레드 팔로업, 완료 알림 발송 |
| `agent_runner.py` | `opencode run` 서브프로세스로 팀장(CLAUDE.md) 실행, stdout 모니터링 |
| `slug.py` | 한국어·영어 혼합 텍스트 → kebab-case 슬러그 생성 |
| `state.py` | 파일 기반 런타임 상태 관리 (`state/` 폴더) |
| `app-B-*.py` | 테스트/실험용 봇 변형 (`.gitignore` 제외) |
| `smoke_test.py` | 배포 없이 핵심 로직 단위 테스트 |
| `state/` | 진행 중 작업·스레드 매핑·DM slug 대기 상태 저장 (런타임 생성) |
| `.env` | 토큰/경로 (직접 생성, 커밋 금지) |

## 1. Slack 앱 생성

1. https://api.slack.com/apps → **Create New App → From scratch**
2. App Name: `claude-agent-team`, Workspace 선택
3. 좌측 메뉴를 이동하며 아래 설정:

### Socket Mode
- **Socket Mode → Enable Socket Mode** 토글 ON
- App-Level Token 발급: 이름 `socket`, Scope `connections:write`
- 발급된 토큰 `xapp-...` 을 `.env` 의 `SLACK_APP_TOKEN` 에 저장

### OAuth & Permissions → Bot Token Scopes
- `chat:write` — DM/채널 메시지 발송
- `im:history` — DM 내역 읽기
- `im:read` — DM 채널 조회
- `im:write` — DM 채널 열기
- `channels:history` — 채널 내 스레드 팔로업 읽기
- `channels:read` — 채널 목록 조회
- `app_mentions:read` — 채널 멘션 수신
- `users:read` — 사용자 ID 매핑 (선택)

### Event Subscriptions
- **Enable Events** ON
- **Subscribe to bot events**:
  - `message.im` — DM 수신
  - `app_mention` — 채널 멘션 수신

### Interactivity & Shortcuts
- **Interactivity** ON (Socket Mode 사용 시 Request URL 불필요)

### Install App
- **Install to Workspace** → 승인
- 발급된 `Bot User OAuth Token` `xoxb-...` 을 `.env` 의 `SLACK_BOT_TOKEN` 에 저장

## 2. 내 Slack User ID 확인

Slack 앱 → 본인 프로필 → 더보기 → "Copy member ID" → `U0XXXXXXX` 형태.  
`.env` 의 `SLACK_ALLOWED_USER_ID` 에 저장(본인 외 DM 은 무시).

여러 명 허용 시: `SLACK_ALLOWED_USER_IDS=U0XXX,U1YYY` (쉼표 구분).

## 3. 로컬 환경 준비

```bash
cd slack-bridge
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env         # 값 채우기
```

### .env 주요 항목

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_ALLOWED_USER_ID=U0XXXXXXX
# SLACK_ALLOWED_USER_IDS=U0XXXXXXX,U1YYYYYYY  # 다중 허용 시
ANTHROPIC_API_KEY=sk-ant-...
TEAM_ROOT=C:/Users/<USERNAME>/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team
AGENT_MODEL=claude-sonnet-4-6
SLACK_WEBHOOK_FILE=C:/Users/<USERNAME>/.claude-secrets/slack-webhook.txt
```

`TEAM_ROOT`: `CLAUDE.md` 가 있는 agent-team 폴더의 절대 경로.

## 4. 실행

```bash
python app.py
```

### 4-1. 업무 요청 (DM 또는 채널 멘션)

```
2026년 국내 전기차 시장 리서치 후 보고서 작성
```
또는 채널에서:
```
@봇 2026년 국내 전기차 시장 리서치 후 보고서 작성
```

봇의 `_is_command()` 가 리서치/분석/개발 등 업무 키워드를 자동 감지하면 **슬러그 확인 없이 즉시 실행**을 시작합니다. 메시지에 `[AUTO: slug]` 를 직접 포함해도 됩니다.

**진행 흐름**:
1. 봇이 "⏳ 작업을 시작합니다…" 메시지로 응답
2. `agent_runner.py` 가 `opencode run` 서브프로세스로 팀장 에이전트 실행
3. 에이전트 stdout(`Write-Host` 출력)을 실시간 모니터링 → Slack 스레드에 중계
4. 완료 시 `output/{slug}/slack-notification.json` Block Kit 페이로드로 결과 보고  
   (파일 없으면 텍스트 요약으로 폴백)

### 4-2. 스레드 후속 지시

봇이 처음 응답한 스레드에 대화를 이어가면 같은 워크스페이스에 대한 **후속 지시**로 접수됩니다:

- 실행 **중**: 현재 실행을 중단(`⏹️ 중단 중…`) → follow-up 모드로 재시작
- 실행이 **끝난** 경우: 바로 follow-up 태스크 시작

예:
```
gamma 가 쓴 팩트체크가 얕은 것 같아요. 경쟁사 대비 점유율을 2024/2025 분기별로 재검증해 주세요.
```

### 4-3. AUTO 모드

메시지 첫 줄에 `[AUTO: slug]` 를 포함하면 팀장이 모든 승인 단계를 자동 처리합니다:

```
[AUTO: 2026-ev-market]
2026년 국내 전기차 시장 리서치 후 보고서 작성
```

## 5. 다중 PC 운영

- **노트북**: 개발·테스트용, 필요 시 `python app.py` 실행
- **상시 PC**: 24시간 봇 상주 (별도 PC에서 동일 `.env` + `python app.py`)
- 두 PC 동시에 실행하면 Slack 이벤트가 중복 처리될 수 있으므로 하나만 실행

## 6. smoke_test.py

앱을 시작하지 않고 핵심 로직을 단위 테스트합니다:

```bash
python smoke_test.py
```

슬러그 생성, 상태 관리, 명령 감지(`_is_command`) 등을 검증합니다.

## 보안 주의

- `.env` 절대 커밋 금지 (`.gitignore` 에 포함됨)
- OneDrive 동기화 지연 시 `output/` 쓰기 충돌 가능 → 필요시 동기화 제외 설정
- 봇이 실행 중인 동안만 DM/멘션 수신 가능 (노트북 절전 시 중단)
