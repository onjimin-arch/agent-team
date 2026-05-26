# Slack 에이전트 봇 — 다른 PC 설정 가이드

## 사전 준비

아래 항목이 설치되어 있어야 합니다.

| 항목 | 확인 명령 | 설치 링크 |
|---|---|---|
| Python 3.9+ | `python --version` | https://www.python.org/downloads/ |
| Claude Code CLI | `claude --version` | https://claude.ai/code |
| Git | `git --version` | https://git-scm.com/install/windows |

---

## 1. 코드 가져오기

```powershell
# Git clone (GitHub 사용 시)
git clone <저장소 URL>
cd agent-team

# 또는 기존 PC에서 폴더 전체를 복사
```

---

## 2. 패키지 설치

```powershell
cd slack-bot
pip install -r requirements.txt
```

---

## 3. 환경변수 설정

```powershell
# .env.example 을 복사해서 .env 생성
copy .env.example .env
```

`.env` 파일을 열어 토큰 두 개를 입력합니다.

```
SLACK_BOT_TOKEN=xoxb-...   ← Slack 앱 > OAuth & Permissions > Bot User OAuth Token
SLACK_APP_TOKEN=xapp-...   ← Slack 앱 > Basic Information > App-Level Tokens
AGENT_TIMEOUT=600
```

### 토큰 위치 찾기

1. https://api.slack.com/apps 접속 → 해당 앱 선택
2. **Bot User OAuth Token**: OAuth & Permissions 탭 → `xoxb-` 로 시작하는 값
3. **App-Level Token**: Basic Information 탭 → App-Level Tokens 섹션
   - 없으면 **Generate Token** 클릭 → 이름 입력 → `connections:write` 스코프 추가 → 생성

---

## 4. Slack 앱 이벤트 스코프 확인

Slack 앱 설정에서 아래 두 항목이 등록되어 있는지 확인합니다.

**OAuth & Permissions → Bot Token Scopes**
- `app_mentions:read`
- `chat:write`

**Event Subscriptions → Subscribe to Bot Events**
- `app_mention`
- `message.im`

변경했다면 **Reinstall App** 버튼을 눌러 재설치합니다.

---

## 5. 봇 실행

```powershell
cd slack-bot
python bot.py
```

터미널에 아래 메시지가 출력되면 정상입니다.

```
⚡ Slack 에이전트 봇 시작 (Socket Mode)
```

### 동작 확인

- Slack에서 봇에게 **DM** 으로 메시지 전송
- 또는 채널에서 **@봇이름 작업내용** 입력
- `⏳ 에이전트 팀이 작업을 시작합니다.` 응답이 오면 성공

---

## 6. PC 켜질 때 자동 시작 설정 (선택)

로그인 시 봇이 자동으로 백그라운드 실행되도록 Windows 작업 스케줄러에 등록합니다.

```powershell
# 관리자 권한 PowerShell 에서 실행
schtasks /create /tn "SlackAgentBot" /tr "\"<agent-team 전체 경로>\slack-bot\start-bot.bat\"" /sc ONLOGON /ru "%USERNAME%" /f
```

경로 예시:
```
"C:\Users\사용자명\문서\클로드 코드 에이전트\agent-team\slack-bot\start-bot.bat"
```

등록 확인:
```powershell
schtasks /query /tn "SlackAgentBot"
```

수동 제거:
```powershell
schtasks /delete /tn "SlackAgentBot" /f
```

---

## 7. 로그 확인

봇 실행 중 오류가 발생하면 `slack-bot/logs/bot.log` 를 확인합니다.

```powershell
# 마지막 30줄 확인
Get-Content slack-bot\logs\bot.log -Tail 30
```

---

## 8. 자주 발생하는 오류

| 오류 메시지 | 원인 | 해결 |
|---|---|---|
| `invalid_auth` | 토큰이 잘못됨 | `.env` 의 토큰 값 재확인 |
| `not_allowed_token_type` | App-Level Token 미설정 | Socket Mode 활성화 후 `xapp-` 토큰 발급 |
| `claude` CLI 를 찾을 수 없습니다 | PATH 미등록 | `claude --version` 확인 후 CLI 재설치 |
| 응답 없음 (타임아웃) | 작업이 너무 복잡하거나 오래 걸림 | `.env` 의 `AGENT_TIMEOUT` 값 늘리기 |
