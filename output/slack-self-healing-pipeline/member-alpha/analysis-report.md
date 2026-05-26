# Analysis Report — queue_server.py 구조 분석 및 Slack 역보고 설계

Creator: member-alpha
Created: 2026-05-26
Version: 1.0

---

## 개요

현재 `queue_server.py`는 Slack 메시지를 수신해 priority queue에 적재하고,
백그라운드 스레드가 `opencode run`을 실행하는 단방향 구조이다.
이 보고서는 역보고(Slack → Agent → Slack) 기능 추가 위치와 구현 방식을 명세화한다.

---

## 분석 결과

### 현재 아키텍처

```
Slack → /slack/events → enqueue() → _runner_loop() → _run_opencode() → [끝]
                                                           ↑
                                              opencode run {task} --model {MODEL}
```

**단방향의 문제점:**
- opencode(Team Lead)가 작업을 완료해도 결과를 Slack으로 돌려줄 방법이 없음
- 실패·롤백 등 중간 상태를 사용자가 알 수 없음
- 배포 성공/실패 여부를 채널에서 확인 불가

### 역보고 함수 삽입 위치

| 위치 | 함수 | 보고 내용 |
|------|------|---------|
| `enqueue()` 호출 직후 | `slack_report()` | 작업 수신 확인 |
| `_run_opencode()` 진입 전 | `slack_report()` | Phase 시작 |
| `_run_opencode()` 완료 후 | `slack_report()` | Phase N 완료 + 소요시간 |
| opencode returncode != 0 | `slack_report()` | 에러 상세 |

**실제 배포 시점 보고(배포 성공·실패·롤백)는** Team Lead(CLAUDE.md) → epsilon → deploy-heal 스킬 내에서
`slack_report`를 직접 호출하거나, opencode가 `queue_server.py`의 HTTP 엔드포인트를 통해 보고한다.
가장 단순한 구현: `queue_server.py`에 `/report` POST 엔드포인트 추가 → opencode 측이 curl로 호출.

### Slack Web API 역보고 방식

```python
import requests

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_REPORT_CHANNEL = os.environ.get("SLACK_REPORT_CHANNEL", "#agent-log")

LEVEL_EMOJI = {
    "info":     "🔵",
    "progress": "🔄",
    "success":  "✅",
    "error":    "⚠️",
    "rollback": "🔴",
}

def slack_report(message: str, level: str = "info") -> bool:
    if not SLACK_BOT_TOKEN:
        print(f"[slack_report] SLACK_BOT_TOKEN 미설정 — 콘솔 출력만: {message}")
        return False
    emoji = LEVEL_EMOJI.get(level, "🔵")
    payload = {
        "channel": SLACK_REPORT_CHANNEL,
        "text": f"{emoji} {message}",
    }
    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                     "Content-Type": "application/json"},
            json=payload,
            timeout=5,
        )
        data = resp.json()
        if not data.get("ok"):
            print(f"[slack_report] Slack API 오류: {data.get('error')}")
            return False
        return True
    except Exception as e:
        print(f"[slack_report] 전송 실패: {e}")
        return False
```

### /report 엔드포인트 설계

opencode(Team Lead) 측이 배포 단계별로 `POST /report` 를 호출해 Slack에 보고한다.

```python
@app.route("/report", methods=["POST"])
def report():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    level   = data.get("level", "info")
    if not message:
        return jsonify({"error": "message required"}), 400
    ok = slack_report(message, level)
    return jsonify({"ok": ok}), 200
```

opencode 측 호출 예시 (Team Lead 또는 epsilon이 PowerShell로 실행):
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/report" `
  -Method POST -ContentType "application/json" `
  -Body '{"message":"🚀 [배포 시도 1/3] staging → Python Web","level":"progress"}'
```

---

## 결론

### PATCH-01 구현 요소 (우선순위 순)

1. **환경변수 로드 블록** — `SLACK_BOT_TOKEN`, `SLACK_REPORT_CHANNEL` 추가
2. **`slack_report()` 함수** — `requests` 사용, SLACK_BOT_TOKEN 미설정 시 콘솔 폴백
3. **작업 수신 보고** — `enqueue()` 성공 직후
4. **runner 시작/완료 보고** — `_run_opencode()` 전후에 시각 포함
5. **`/report` 엔드포인트** — opencode·epsilon이 배포 단계를 push할 진입점
6. **`queue-config.yaml` 업데이트** — `SLACK_REPORT_CHANNEL` 기본값 기재

### 유의사항

- `requests` 패키지를 `requirements.txt`에 추가해야 함 (현재 `flask`, `pyyaml`만 있을 가능성)
- Slack Bot에 `chat:write` scope 필요
- `/report` 엔드포인트는 인증 없음 → 로컬 전용(127.0.0.1 bind) 고려 또는 간단한 토큰 검증 추가 가능
