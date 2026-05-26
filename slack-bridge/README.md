# Slack Bridge

Slack DM 으로 팀장 에이전트를 호출하기 위한 로컬 브릿지. Socket Mode 로 동작하므로 공용 URL 이 필요 없으며, 산출물은 로컬 OneDrive 경로(`output/{topic-slug}/`)에 저장됩니다.

## 구성 요소
- `app.py` — Slack Bolt Socket Mode 봇 (DM 수신, 승인 UI, 알림 발송)
- `agent_runner.py` — Claude Agent SDK 로 팀장 프로토콜(CLAUDE.md) 실행
- `state/` — 진행 중 작업, 승인 대기 상태 저장 (런타임 생성)
- `.env` — 토큰/경로 (직접 생성, 커밋 금지)

## 1. Slack 앱 생성
1. https://api.slack.com/apps → **Create New App → From scratch**
2. App Name: `claude-agent-team`, Workspace 선택
3. 좌측 메뉴 이동하며 아래 설정:

### Socket Mode
- **Socket Mode → Enable Socket Mode** 토글 ON
- App-Level Token 발급: 이름 `socket`, Scope `connections:write`
- 발급된 토큰 `xapp-...` 을 `.env` 의 `SLACK_APP_TOKEN` 에 저장

### OAuth & Permissions → Bot Token Scopes
- `chat:write` (DM 발송)
- `im:history` (DM 읽기)
- `im:read` (DM 채널 조회)
- `im:write` (DM 채널 열기)
- `users:read` (사용자 ID 매핑, 선택)

### Event Subscriptions
- **Enable Events** ON
- **Subscribe to bot events**: `message.im`

### Interactivity & Shortcuts
- **Interactivity** ON (Socket Mode 사용 시 Request URL 불필요)

### Install App
- **Install to Workspace** → 승인
- 발급된 `Bot User OAuth Token` `xoxb-...` 을 `.env` 의 `SLACK_BOT_TOKEN` 에 저장

## 2. 내 Slack User ID 확인
Slack 앱 → 본인 프로필 → 더보기 → "Copy member ID" → `U0XXXXXXX` 형태.
`.env` 의 `SLACK_ALLOWED_USER_ID` 에 저장(본인 외 DM 은 무시).

## 3. 로컬 환경 준비
```bash
cd slack-bridge
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env         # 값 채우기
```

## 4. 실행
```bash
python app.py
```

### 4-1. 새 주제 시작 (DM 또는 채널 멘션)
```
신규 주제 2026년 국내 전기차 시장 리서치 후 보고서 작성
```
→ 봇이 슬러그 후보 제안 → 버튼으로 확인 → 백그라운드 실행 → 진행/완료 알림. 채널에서는 `@봇 신규 주제 …` 멘션 사용.

**완료 시 보고서**: 팀장 에이전트가 `output/{slug}/slack-notification.json` (CLAUDE.md Phase 5-2 Block Kit 템플릿) 를 작성하면, slack-bridge 가 지시받은 DM/스레드에 그 블록을 그대로 재포스팅합니다. payload 파일이 없으면 간단한 텍스트 알림으로 폴백.

### 4-2. 스레드 대화 (후속 지시)
봇이 처음 응답한 스레드(채널) 또는 봇의 메시지에 대한 in-thread 회신(DM) 으로 아무 지시를 남기면, 같은 워크스페이스 슬러그에 대한 **후속 지시** 로 접수됩니다:

- 실행 **중** 이면: 현재 실행을 먼저 중단(`⏹️ 중단 중…`) → 기존 산출물을 읽고 **follow-up 모드** 로 재시작.
- 실행이 **끝난** 경우: 곧바로 follow-up 태스크 시작 (취소 없음).
- 후속 지시는 기존 파일을 **보강/부분 교체** 하고, `review-log.md` 하단에 "Follow-up (…)" 기록을 추가합니다.

예:
```
@봇 gamma 가 쓴 팩트체크가 얕은 것 같아요. 경쟁사 대비 점유율 수치를 2024/2025 동별로 재검증해 주세요.
@봇 최종 보고서의 "Executive Summary" 를 3문장으로 더 압축해 주세요.
```

중단 신호 후 45초 내 응답이 없으면 봇은 follow-up 시작을 **보류**(파일 경쟁 방지)하고 잠시 뒤 다시 시도하라고 알립니다.

### 4-3. 슬러그 수정
슬러그 제안 메시지에서 **[슬러그 수정]** 버튼을 누르면 봇이 재입력 대기 상태가 됩니다. 다음 메시지로 회신:
```
슬러그: 2026-ev-market
```
또는 슬러그만 단독 입력(`2026-ev-market`). 잘못된 포맷이면 안내 메시지가 나갑니다. 슬러그 규칙: 소문자·숫자·하이픈, 2~65자.

## 보안 주의
- `.env` 절대 커밋 금지 (`.gitignore` 에 포함됨)
- OneDrive 동기화 지연 시 `output/` 쓰기 충돌 가능 → 필요시 동기화 제외 설정
- 봇이 실행 중인 동안만 DM 수신 가능 (노트북 절전 시 중단)
