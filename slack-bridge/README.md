# Slack Bridge

Slack DM 및 채널 멘션으로 팀장 에이전트를 호출하기 위한 로컬 브릿지. Socket Mode로 동작하므로 공용 URL이 필요 없으며, 산출물은 로컬 OneDrive 경로(`output/{topic-slug}/`)에 저장됩니다.

## 구성 요소

| 파일 | 역할 |
|------|------|
| `app.py` | Slack Bolt Socket Mode 봇 — DM/채널 수신, 승인 UI, 알림 발송 |
| `app-B-*.py` | 다른 PC 전용 봇 사본 (`.gitignore` 제외됨) |
| `agent_runner.py` | `opencode run` 서브프로세스로 팀장 프로토콜(CLAUDE.md) 실행 |
| `state.py` | 파일 기반 작업 상태·스레드 매핑 관리 (`state/` 폴더에 저장) |
| `slug.py` | 한글·영문 혼재 업무 설명에서 kebab-case 슬러그 생성 |
| `smoke_test.py` | opencode CLI 연결 최소 검증용 테스트 |
| `state/` | 런타임 생성 상태 파일 (`.gitignore` 제외됨) |
| `.env` | 토큰·경로 (직접 생성, 커밋 금지) |

---

## 1. Slack 앱 생성

1. [https://api.slack.com/apps](https://api.slack.com/apps) → **Create New App → From scratch**
2. App Name: `agent-team-bot`, Workspace 선택
3. 아래 항목 순서대로 설정:

### Socket Mode
- **Socket Mode → Enable Socket Mode** 토글 ON
- App-Level Token 발급: 이름 `socket`, Scope `connections:write`
- 발급된 `xapp-...` 토큰을 `.env`의 `SLACK_APP_TOKEN`에 저장

### OAuth & Permissions → Bot Token Scopes
| Scope | 용도 |
|-------|------|
| `chat:write` | DM·채널 메시지 발송 |
| `im:history` | DM 읽기 |
| `im:read` | DM 채널 조회 |
| `im:write` | DM 채널 열기 |
| `channels:history` | 채널 메시지 읽기 (멘션용) |
| `channels:read` | 채널 정보 조회 |
| `channels:join` | Phase 5 배포 채널(`distribution.slack.channel`)에 봇이 자동 참여 (`scripts/slack_publish.py`). 없으면 공개 채널도 수동 `/invite` 필요 |
| `app_mentions:read` | 채널 `@봇` 멘션 수신 |

### Event Subscriptions
- **Enable Events** ON
- **Subscribe to bot events**: `message.im`, `app_mention`

### Interactivity & Shortcuts
- **Interactivity** ON (Socket Mode 사용 시 Request URL 불필요)

### Install App
- **Install to Workspace** → 승인
- 발급된 `xoxb-...` 토큰을 `.env`의 `SLACK_BOT_TOKEN`에 저장

---

## 2. 내 Slack User ID 확인

Slack 앱 → 본인 프로필 → 더보기 → "Copy member ID" → `U0XXXXXXX` 형태.
`.env`의 `SLACK_ALLOWED_USER_ID`에 저장 (본인 외 DM·멘션은 무시).

여러 명 허용 시 `SLACK_ALLOWED_USER_IDS`에 콤마 구분으로 추가.

---

## 3. 로컬 환경 준비

```bash
cd slack-bridge
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env         # 값 채우기
```

### 필수 환경변수 (`.env`)

```env
# Slack 토큰
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# 허용 사용자 (본인 Slack User ID)
SLACK_ALLOWED_USER_ID=U0XXXXXXX
# SLACK_ALLOWED_USER_IDS=U0XXXXXXX,U1YYYYYYY  # 여러 명

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# 팀장 에이전트 루트 경로 (agent-team 폴더 절대경로)
TEAM_ROOT=C:/Users/<USERNAME>/OneDrive - 바로고/문서/클로드 코드 에이전트/agent-team

# opencode 모델 (anthropic/ prefix 없어도 자동 변환)
AGENT_MODEL=claude-sonnet-4-6

# 완료 알림 Webhook URL 파일 경로 (없으면 webhook 발송 생략)
SLACK_WEBHOOK_FILE=C:/Users/<USERNAME>/.claude-secrets/slack-webhook.txt
```

---

## 4. 실행

```bash
python app.py
```

또는 Windows 작업 스케줄러 등록 (상위 폴더의 `install-service.ps1` 참고).

---

## 5. 사용법

### 5-1. 새 작업 시작

**DM 또는 채널 `@봇` 멘션**:

```
신규 주제 2026년 국내 전기차 시장 리서치 후 보고서 작성
신규 주제 [dev] 로그인 버그 수정 - 토큰 만료 시 재로그인 안 됨
개발 로그인 버그 수정
리서치 2026년 퀵커머스 시장 점유율 분석
```

- `신규 주제`(또는 `team-config.yaml`의 `execution.workspace.new_topic_trigger`) 키워드가 있으면 새 워크스페이스를 즉시 생성합니다.
- 없어도 개발·리서치 관련 키워드가 있으면 자동 감지해 새 작업으로 처리합니다.
- 슬러그는 업무 설명에서 자동 생성됩니다 (`slug.py` 기반).
- 인사말은 간단히 응답하고 지시로 처리하지 않습니다.

**완료 알림**: 에이전트가 `output/{slug}/slack-notification.json`을 생성하면 봇이 해당 Block Kit 블록을 DM/스레드에 재포스팅합니다. 파일이 없으면 보고서 내용에서 자동 합성하고, `SLACK_WEBHOOK_FILE`이 설정되어 있으면 Webhook 채널에도 동일 내용을 발송합니다.

### 5-2. 스레드·DM 후속 지시

봇이 처음 응답한 스레드(채널) 또는 봇과의 DM 스레드에 회신하면, **동일 워크스페이스 슬러그의 후속 지시**로 접수됩니다.

- 실행 **중**이면: 현재 실행을 먼저 중단(`⏹️ 중단 중…`) → 기존 산출물을 읽고 **follow-up 모드**로 재시작.
- 실행이 **끝난** 경우: 바로 follow-up 태스크 시작.
- 중단 신호 후 45초 내 응답 없으면 follow-up 보류 → 잠시 뒤 다시 시도 안내.

```
@봇 gamma가 쓴 팩트체크가 얕아요. 경쟁사 점유율 수치를 2025년 기준으로 재검증해 주세요.
@봇 최종 보고서 Executive Summary를 3문장으로 압축해 주세요.
```

DM에서 슬러그 없이 보내면 가장 최근 작업의 후속 지시로 자동 처리됩니다.

### 5-3. AUTO 모드

`[AUTO: {슬러그}]` 접두사를 붙이면 팀장이 Phase 1~5를 중단 없이 자동 실행합니다:

```
[AUTO: quickcommerce-analysis] 국내 퀵커머스 시장 점유율 분석 보고서 작성
```

### 5-4. 슬러그 수정

작업 시작 후 슬러그를 바꾸고 싶다면 "슬러그 수정" 버튼을 누르면 봇이 재입력 대기 상태가 됩니다:

```
슬러그: 2026-ev-market
```

또는 슬러그만 단독 입력 (`2026-ev-market`). 잘못된 포맷이면 안내 메시지가 나갑니다.
슬러그 규칙: 소문자·숫자·하이픈, 2~65자.

---

## 6. 개발/디버깅

### opencode 연결 확인

```bash
python smoke_test.py
```

### Phase 5 배포(Notion/Slack) 실패 디버깅

팀장 에이전트가 opencode 서브프로세스 안에서 `../scripts/notion_publish.py`, `../scripts/slack_publish.py`
를 호출한다 (MCP 커넥터 없이도 동작하는 토큰 기반 폴백, CLAUDE.md Phase 5 참조). 실패하면 각 스크립트가
JSON으로 원인과 해결 힌트를 출력하므로, 같은 명령을 직접 실행해 원인을 재현할 수 있다:

```bash
cd ..
python scripts/notion_publish.py --file output/<slug>/final/final-artifact.md \
  --data-source-id 348363ae-08db-80aa-ba4a-000b3160d6ed --title-property 이름
python scripts/slack_publish.py --channel "#agent-log" --text "테스트"
```

자주 발생하는 실패:
- `NOTION_API_TOKEN_missing` → `.env`에 토큰 미설정. `https://www.notion.so/my-integrations` 에서 발급 후
  대상 데이터소스에 Connect 필요.
- `not_in_channel` (join_error 포함) → 봇이 비공개 채널이거나 `channels:join` 스코프 미부여. 해당 채널에서
  `/invite @agent-team-bot` 실행.

### 로그 확인

```bash
# 봇 실행 시 stderr를 파일로 저장 (로그 수준 DEBUG)
python app.py 2>> ../logs/slack-bridge-err.log
```

### 여러 PC 운영

- 각 PC마다 `app-B-<hostname>.py`와 `<hostname>.env` 사본을 만들어 관리합니다 (`.gitignore` 에 `app-B-*.py`, `-B-*.env` 패턴으로 제외).
- `TEAM_ROOT`를 각 PC 경로에 맞게 설정합니다.
- 동시에 두 봇을 실행하면 이벤트가 중복 수신될 수 있으므로, 한 번에 하나만 실행합니다.

---

## 보안 주의

- `.env` 절대 커밋 금지 (`.gitignore`에 포함됨)
- `state/` 폴더는 런타임 생성이며 커밋하지 않습니다.
- OneDrive 동기화 지연 시 `output/` 쓰기 충돌 가능 → 필요시 동기화 제외 설정
- 봇이 실행 중인 동안만 DM·멘션 수신 가능 (노트북 절전 시 중단)
