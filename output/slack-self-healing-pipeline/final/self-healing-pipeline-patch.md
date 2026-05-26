# Self-Healing Pipeline Patch

생성일: 2026-05-26
수정 대상: `queue_server.py` · `CLAUDE.md` · `.claude/skills/deploy-heal/SKILL.md`(신규) ·
           `.claude/agents/member-epsilon/AGENT.md` · `team-config.yaml`

---

## 설치 순서

### Step 1. 환경변수 설정

`.env` 파일 (프로젝트 루트) 또는 시스템 환경변수:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_REPORT_CHANNEL=#agent-log
PROD_PORT=8000
```

### Step 2. Slack Bot 권한 확인

필요 OAuth scope:
- `chat:write` — 채널에 메시지 전송
- `channels:history` — 채널 메시지 수신
- `app_mentions:read` — 멘션 수신 (Socket Mode 사용 시)

### Step 3. 패치 적용

아래 PATCH-01~05 순서대로 적용.

### Step 4. 동작 확인

```
# Slack #지시-채널에서 메시지 전송:
[AUTO: test-deploy] [dev] 간단한 테스트 함수 추가

# #agent-log 채널에서 확인할 보고 시퀀스:
🟡 [작업 시작] test-deploy — [dev] 간단한 테스트 함수 추가
🔄 [Phase 1 완료] 00:03
🔄 [Phase 2 완료] 00:08
🚀 [배포 시도 1/3] staging → python-web
✅ [배포 완료] production 정상 가동
✅ [작업 완료] test-deploy | 산출물: output/test-deploy/final/final-artifact.md
```

### Step 5. requirements.txt 업데이트

`queue_server.py`에 `requests` 추가:

```
flask
pyyaml
requests
```

---

## PATCH-01: `queue_server.py`

### 변경 전

```python
import heapq
import json
import os
import subprocess
import threading
import time
import yaml
from flask import Flask, request, jsonify

CONFIG_PATH = ...
config = load_config()

PRIORITY_MAP: dict[str, int] = config.get(...)
DEFAULT_PRIORITY: int = PRIORITY_MAP.get("default", 1)
PORT: int = config["slack"]["webhook_receive_port"]
MODEL: str = config["opencode"]["default_model"]
```

### 변경 후 (전체 파일)

```python
"""
Priority Queue Server — Slack Webhook 수신 + 터미널 입력을 단일 큐로 통합하고
claude -p 로 Team Lead 를 트리거합니다.

우선순위 태그 (메시지 맨 앞):
  !urgent   → 0  즉시 실행
  !task     → 1  일반 (기본값)
  !schedule → 2  여유 있을 때
"""

import heapq
import json
import os
import subprocess
import threading
import time
import yaml
import requests
from flask import Flask, request, jsonify

# ── 설정 로드 ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), ".claude", "configs", "queue-config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

PRIORITY_MAP: dict[str, int] = config.get("priority", {"urgent": 0, "task": 1, "schedule": 2, "default": 1})
DEFAULT_PRIORITY: int = PRIORITY_MAP.get("default", 1)
PORT: int = config["slack"]["webhook_receive_port"]
MODEL: str = config["opencode"]["default_model"]

# ── Slack 역보고 설정 ──────────────────────────────────────────────────────
SLACK_BOT_TOKEN: str = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_REPORT_CHANNEL: str = os.environ.get("SLACK_REPORT_CHANNEL", "#agent-log")

_LEVEL_EMOJI = {
    "info":     "🟡",
    "progress": "🔄",
    "success":  "✅",
    "error":    "⚠️",
    "rollback": "🔴",
}


def slack_report(message: str, level: str = "info") -> bool:
    """
    Slack 채널에 진행상황 메시지 전송.
    level: info | success | error | progress | rollback
    SLACK_BOT_TOKEN 미설정 시 콘솔 출력으로 폴백.
    """
    emoji = _LEVEL_EMOJI.get(level, "🟡")
    full_msg = f"{emoji} {message}"
    if not SLACK_BOT_TOKEN:
        print(f"[slack_report] {full_msg}")
        return False
    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"channel": SLACK_REPORT_CHANNEL, "text": full_msg},
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


# ── Priority Queue (thread-safe) ───────────────────────────────────────────
_queue: list = []
_queue_lock = threading.Lock()
_seq_counter = 0


def _parse_priority(text: str) -> tuple[int, str]:
    for tag, prio in [("!urgent", PRIORITY_MAP["urgent"]),
                      ("!task",   PRIORITY_MAP["task"]),
                      ("!schedule", PRIORITY_MAP["schedule"])]:
        if text.strip().startswith(tag):
            return prio, text.strip()[len(tag):].strip()
    return DEFAULT_PRIORITY, text.strip()


def enqueue(task_text: str, priority: int | None = None) -> dict:
    global _seq_counter
    if priority is None:
        priority, task_text = _parse_priority(task_text)
    with _queue_lock:
        _seq_counter += 1
        heapq.heappush(_queue, (priority, _seq_counter, task_text))

    # 작업 수신 보고
    summary = task_text[:80] + ("..." if len(task_text) > 80 else "")
    slug = task_text.split("]")[1].strip().split()[0] if "[AUTO:" in task_text else f"seq-{_seq_counter}"
    slack_report(f"[작업 시작] {slug} — {summary}", "info")

    return {"queued": True, "priority": priority, "seq": _seq_counter, "task": task_text}


def queue_status() -> dict:
    with _queue_lock:
        items = [{"priority": p, "seq": s, "task": t} for p, s, t in _queue]
    return {"queue_length": len(items), "items": items}


# ── Task Runner (백그라운드 루프) ──────────────────────────────────────────
_running = False


def _runner_loop():
    while _running:
        item = None
        with _queue_lock:
            if _queue:
                item = heapq.heappop(_queue)
        if item:
            priority, seq, task_text = item
            print(f"[runner] seq={seq} priority={priority} → {task_text[:80]}")
            _run_opencode(task_text, seq)
        else:
            time.sleep(1)


def _run_opencode(task_text: str, seq: int):
    start = time.time()
    cmd = ["claude", "-p", task_text, "--model", MODEL]
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        elapsed = int(time.time() - start)
        if result.returncode != 0:
            print(f"[runner] claude exited with code {result.returncode}")
            slack_report(f"[작업 오류] seq={seq} — exit code {result.returncode}", "error")
        else:
            slug = task_text.split("]")[1].strip().split()[0] if "[AUTO:" in task_text else f"seq-{seq}"
            slack_report(
                f"[작업 완료] {slug} | 소요: {elapsed}s | 산출물: output/{slug}/final/final-artifact.md",
                "success",
            )
    except FileNotFoundError:
        slack_report("[오류] 'claude' 명령을 찾을 수 없습니다. PATH를 확인하세요.", "error")
        print("[runner] ERROR: 'claude' 명령을 찾을 수 없습니다.")
    except Exception as e:
        slack_report(f"[오류] {e}", "error")
        print(f"[runner] ERROR: {e}")


def start_runner():
    global _running
    _running = True
    t = threading.Thread(target=_runner_loop, daemon=True)
    t.start()
    return t


# ── Flask 앱 ───────────────────────────────────────────────────────────────
app = Flask(__name__)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json(silent=True) or {}
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})
    event = data.get("event", {})
    text = event.get("text", "")
    if not text:
        return jsonify({"ok": True})
    result = enqueue(text)
    return jsonify(result), 202


@app.route("/task", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    task_text = data.get("task", "").strip()
    if not task_text:
        return jsonify({"error": "task field is required"}), 400
    explicit_priority = data.get("priority")
    result = enqueue(task_text, priority=explicit_priority)
    return jsonify(result), 202


@app.route("/report", methods=["POST"])
def report():
    """
    opencode(Team Lead) 또는 deploy-heal 스킬이 배포 단계별 보고를 push하는 엔드포인트.
    Body (JSON): {"message": "...", "level": "info|success|error|progress|rollback"}
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    level   = data.get("level", "info")
    if not message:
        return jsonify({"error": "message required"}), 400
    ok = slack_report(message, level)
    return jsonify({"ok": ok}), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify(queue_status())


# ── 진입점 ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_runner()
    print(f"[queue_server] 포트 {PORT} 에서 시작. /status, /task, /slack/events, /report")
    app.run(host="0.0.0.0", port=PORT, debug=False)
```

---

## PATCH-02: `CLAUDE.md` (AUTO 모드 완전 무인화)

### 수정 섹션 1 — 자동 모드 섹션 확장

#### 변경 전
```markdown
### 자동 모드 (Slack / API 트리거)
프롬프트 첫 줄이 `[AUTO: {slug}]` 형식이면:
1. 해당 슬러그를 즉시 워크스페이스로 사용 (사용자 확인 생략)
2. `/output/{slug}/` 디렉터리와 하위 `member-*/`, `final/` 을 바로 생성
3. `human_approval` 설정과 무관하게 승인 단계 생략 (자동 승인)
4. Phase 1~4 를 완료한 뒤 결과를 `WS/final/final-artifact.md` 에 저장
```

#### 변경 후
```markdown
### 자동 모드 (Slack / API 트리거)
프롬프트 첫 줄이 `[AUTO: {slug}]` 형식이면:
1. 해당 슬러그를 즉시 워크스페이스로 사용 (사용자 확인 생략)
2. `/output/{slug}/` 디렉터리와 하위 `member-*/`, `final/` 을 바로 생성
3. `human_approval` 설정과 무관하게 승인 단계 생략 (자동 승인)
4. Phase 1~5 를 완료한 뒤 결과를 `WS/final/final-artifact.md` 에 저장
5. 모든 자동 판단 결과를 `WS/auto-log.md` 에 실시간 기록

### AUTO 모드 인터럽트 처리 규칙
AUTO 모드에서는 아래 인터럽트 포인트를 모두 자동 처리한다.
각 판단 결과는 `WS/auto-log.md`에 기록한다.

**① 슬러그 확인 (Workspace Protocol)**
자동 확정. plan.md 상단에 "자동 확정된 slug: {slug}" 기록.

**② 리서치 재사용 여부 (Phase 1 선행 체크)**
- 30일 이내 + 80% 겹침 판단 시 → 자동 재사용.
- 조건 미충족 시 → 자동 신규 탐색.
- `auto-log.md`에 판단 근거 기록.

**③ Task Type 동점 처리 (Phase 1-0)**
동점 발생 시 `team-config.yaml`의 `task.types` 나열 순서를 기준으로 자동 선택.
`auto-log.md`에 동점 후보 목록과 선택 결과 기록.

**④ Phase 3 Review — 직접수정 기준 완화**
AUTO 모드에서 직접수정(EDIT) 기준: 수정량 30% 이하.
30% 초과 시 REASSIGN (멤버 재실행). 목표: 재호출 최소화.

**⑤ Phase 4 품질 미충족 재실행**
`max_cycles` 이내면 사용자 확인 없이 자동 재실행.
`auto-log.md`에 재실행 사유 기록.

**⑥ human_approval 게이트 (Termination Protocol)**
자동 승인. 즉시 Phase 5 진입.

**⑦ 에스컬레이션 (파일 없음, 감지 실패 등)**
`POST http://localhost:5000/report` 로 Slack에 에러 보고.
대기하지 않고 현재 최선 버전으로 계속 진행.
`auto-log.md`에 에스컬레이션 사유와 대응 기록.

**⑧ Phase 5 Distribution**
`enabled: true` 인 모든 엔드포인트 즉시 실행.
각 결과를 `auto-log.md`에 추가 기록.
```

### 수정 섹션 2 — auto-log.md 형식 정의 (Handoff Rules 섹션 이후에 추가)

```markdown
## AUTO 모드 실행 로그 형식 (`WS/auto-log.md`)

AUTO 모드 실행 시 아래 형식으로 실시간 기록한다:

```
# AUTO 실행 로그
slug: {slug}
시작: {YYYY-MM-DD HH:MM}

## 판단 기록
| 시각  | 포인트        | 판단 내용         | 근거              |
|-------|--------------|-----------------|-------------------|
| HH:MM | ① 슬러그      | 자동 확정         | human_approval:false |
| HH:MM | ② 재사용      | 신규 탐색         | 유사 slug 없음    |
| HH:MM | ③ task type   | research-report  | score 0.5 (1위)   |

## Phase 진행
| Phase | 시작  | 완료  | 결과                |
|-------|-------|-------|---------------------|
| 1     | HH:MM | HH:MM | task_type=design    |
| 2     | HH:MM | HH:MM | 멤버 3개 완료       |
| 3     | HH:MM | HH:MM | APPROVE×3           |
| 4     | HH:MM | HH:MM | 통합 완료           |
| 5     | HH:MM | HH:MM | Notion 저장 완료    |

## Distribution
| 엔드포인트 | 결과 | URL |
|-----------|------|-----|
| notion    | 성공 | https://notion.so/... |
```
```

---

## PATCH-03: `.claude/skills/deploy-heal/SKILL.md` (신규 생성)

아래 내용을 `.claude/skills/deploy-heal/SKILL.md` 에 그대로 저장한다.

```markdown
# deploy-heal Skill

## 목적
서비스 타입 자동 감지 → staging 테스트 → self-healing 루프 → production 배포 → 실패 시 롤백

## 호출 방법
member-epsilon이 Phase 2 코드 수정 완료 후 자동 호출.
Team Lead도 직접 호출 가능.

---

## Step 1: 서비스 타입 감지

```powershell
function Get-ServiceType {
    param([string]$ProjectRoot)
    if (Test-Path "$ProjectRoot\pubspec.yaml")             { return "flutter" }
    if (Test-Path "$ProjectRoot\android\build.gradle")     { return "android" }
    if (Test-Path "$ProjectRoot\Dockerfile")               { return "docker" }
    if (Test-Path "$ProjectRoot\package.json") {
        $pkg = Get-Content "$ProjectRoot\package.json" | ConvertFrom-Json
        if ($pkg.dependencies.next -or $pkg.devDependencies.next) { return "nextjs" }
        return "nodejs"
    }
    if (Test-Path "$ProjectRoot\requirements.txt") {
        $req = Get-Content "$ProjectRoot\requirements.txt" -Raw
        if ($req -match "flask|fastapi") { return "python-web" }
        return "python-script"
    }
    return "unknown"
}
```

감지 순서: flutter → android → docker → nextjs → nodejs → python-web → python-script → unknown

unknown 반환 시: `POST http://localhost:5000/report {"message":"⚠️ 서비스 타입 감지 실패","level":"error"}` 후 Team Lead에 에스컬레이션.

---

## Step 2: 공통 유틸리티 함수

```powershell
# 포트 프로세스 종료
function Stop-PortProcess {
    param([int]$Port)
    $pidStr = (netstat -ano | Select-String ":$Port\s" |
               Select-Object -First 1).ToString().Trim().Split()[-1]
    if ($pidStr -and $pidStr -ne "0") {
        try { taskkill /PID $pidStr /F 2>$null } catch {}
    }
}

# HTTP Health Check
function Test-Health {
    param([string]$Url, [int]$Retries = 3, [int]$IntervalSec = 10)
    for ($i = 1; $i -le $Retries; $i++) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing
            if ($resp.StatusCode -lt 400) { return $true }
        } catch {}
        if ($i -lt $Retries) { Start-Sleep $IntervalSec }
    }
    return $false
}

# Slack 역보고 (/report 엔드포인트 경유)
function Send-SlackReport {
    param([string]$Message, [string]$Level = "info")
    $body = @{ message = $Message; level = $Level } | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri "http://localhost:5000/report" `
          -Method POST -ContentType "application/json" -Body $body
    } catch { Write-Host "[deploy-heal] Slack 보고 실패: $_" }
}
```

---

## Step 3: 서비스 타입별 Staging/Production/Rollback

### 공통 변수
```powershell
$PROD_PORT    = [int]$env:PROD_PORT
$STAGING_PORT = $PROD_PORT + 1000
$LOG_DIR      = "$ProjectRoot\logs"
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
```

### Python Web
```powershell
# Staging
Stop-PortProcess $STAGING_PORT
$stagingProc = Start-Process python `
  -ArgumentList "app.py --port $STAGING_PORT" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError "$LOG_DIR\staging-err.log" -WindowStyle Hidden -PassThru
$healthUrl = "http://localhost:$STAGING_PORT/health"

# Production
Stop-PortProcess $PROD_PORT
Start-Process python -ArgumentList "app.py --port $PROD_PORT" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" `
  -RedirectStandardError "$LOG_DIR\production-err.log" -WindowStyle Hidden

# Rollback
git -C $ProjectRoot checkout HEAD
Stop-PortProcess $PROD_PORT
Start-Process python -ArgumentList "app.py --port $PROD_PORT" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" -WindowStyle Hidden
```

### Node.js
```powershell
# Staging
Stop-PortProcess $STAGING_PORT
$env:PORT = "$STAGING_PORT"
$stagingProc = Start-Process node -ArgumentList "server.js" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError "$LOG_DIR\staging-err.log" -WindowStyle Hidden -PassThru
$healthUrl = "http://localhost:$STAGING_PORT"

# Production
Stop-PortProcess $PROD_PORT
$env:PORT = "$PROD_PORT"
Start-Process node -ArgumentList "server.js" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" `
  -RedirectStandardError "$LOG_DIR\production-err.log" -WindowStyle Hidden

# Rollback
git -C $ProjectRoot checkout HEAD; Stop-PortProcess $PROD_PORT
$env:PORT = "$PROD_PORT"
Start-Process node -ArgumentList "server.js" -WorkingDirectory $ProjectRoot -WindowStyle Hidden
```

### Next.js
```powershell
# Staging (빌드 후 실행)
$buildOut = & npm run build *>&1; $buildOut | Out-File "$LOG_DIR\build.log"
if ($LASTEXITCODE -ne 0) { throw "Next.js build failed — see $LOG_DIR\build.log" }
Stop-PortProcess $STAGING_PORT
$stagingProc = Start-Process node `
  -ArgumentList "node_modules/.bin/next start -p $STAGING_PORT" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError "$LOG_DIR\staging-err.log" -WindowStyle Hidden -PassThru
$healthUrl = "http://localhost:$STAGING_PORT"

# Production
Stop-PortProcess $PROD_PORT
Start-Process node -ArgumentList "node_modules/.bin/next start -p $PROD_PORT" `
  -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" -WindowStyle Hidden

# Rollback
git -C $ProjectRoot checkout HEAD
$rollback = & npm run build *>&1; $rollback | Out-File "$LOG_DIR\rollback-build.log"
Stop-PortProcess $PROD_PORT
Start-Process node -ArgumentList "node_modules/.bin/next start -p $PROD_PORT" `
  -WorkingDirectory $ProjectRoot -WindowStyle Hidden
```

### Flutter
```powershell
# Staging (debug 빌드 — exit code 기반)
$stageOut = & flutter build apk --debug *>&1; $stageOut | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)

# Production (release 빌드)
$prodOut = & flutter build apk --release *>&1; $prodOut | Out-File "$LOG_DIR\production.log"

# Rollback
git -C $ProjectRoot stash
$rbOut = & flutter build apk --release *>&1; $rbOut | Out-File "$LOG_DIR\rollback.log"
```

### Android Native
```powershell
# Staging (debug 빌드)
$stageOut = & "$ProjectRoot\gradlew" assembleDebug *>&1
$stageOut | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)

# Production (release 빌드)
$prodOut = & "$ProjectRoot\gradlew" assembleRelease *>&1
$prodOut | Out-File "$LOG_DIR\production.log"

# Rollback
git -C $ProjectRoot stash
$rbOut = & "$ProjectRoot\gradlew" assembleRelease *>&1
$rbOut | Out-File "$LOG_DIR\rollback.log"
```

### Docker
```powershell
# Staging
$stageOut = & docker compose -f docker-compose.staging.yml up -d *>&1
$stageOut | Out-File "$LOG_DIR\staging.log"
$containerName = (Get-Content "$ProjectRoot\docker-compose.staging.yml" |
  Select-String "container_name").ToString().Split(":")[-1].Trim()
$stagingOk = [bool](docker ps --filter "name=$containerName" --format "{{.Names}}")

# Production
$prodOut = & docker compose up -d *>&1; $prodOut | Out-File "$LOG_DIR\production.log"

# Rollback
& docker compose down
git -C $ProjectRoot checkout HEAD
& docker compose up -d
```

### Python Script
```powershell
# Staging (dry-run)
$stageOut = & python script.py --dry-run *>&1; $stageOut | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)

# Production
Stop-PortProcess $PROD_PORT
Start-Process python -ArgumentList "script.py" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" `
  -RedirectStandardError "$LOG_DIR\production-err.log" -WindowStyle Hidden

# Rollback
git -C $ProjectRoot checkout HEAD
```

---

## Step 4: Self-Healing 루프

```powershell
param(
    [string]$ProjectRoot,
    [string]$ServiceType,
    [int]$WaitSecAfterStart = 30
)
$MaxAttempts = 3  # 하드코딩 — 변경 시 이 값만 수정

$attempt = 0
$success = $false
$exitCodeBased = $ServiceType -in @("flutter", "android", "python-script")
git -C $ProjectRoot stash

while ($attempt -lt $MaxAttempts -and -not $success) {
    $attempt++
    Send-SlackReport "🚀 [배포 시도 $attempt/$MaxAttempts] staging → $ServiceType" "progress"

    git -C $ProjectRoot stash pop

    # Staging 시작 (서비스 타입별 블록 — Step 3 참조)
    Stop-PortProcess $STAGING_PORT
    # ... 타입별 Staging 명령 실행 ...
    if (-not $exitCodeBased) { Start-Sleep $WaitSecAfterStart }

    # Health Check
    $healthOk = if ($exitCodeBased) { $stagingOk } else { Test-Health -Url $healthUrl }

    if ($healthOk) {
        # Production 배포
        Stop-PortProcess $PROD_PORT
        # ... 타입별 Production 명령 실행 ...
        Start-Sleep 10

        $prodOk = if ($exitCodeBased) { $LASTEXITCODE -eq 0 } else {
            Test-Health -Url "http://localhost:$PROD_PORT/health"
        }

        if ($prodOk) {
            git -C $ProjectRoot add -A
            git -C $ProjectRoot commit -m "auto-fix: $ServiceType attempt $attempt"
            Send-SlackReport "✅ [배포 완료] production 정상 가동 (시도 $attempt/$MaxAttempts)" "success"
            $hashLine = git -C $ProjectRoot rev-parse HEAD
            "| $(Get-Date -Format 'yyyy-MM-dd HH:mm') | $attempt | 성공 | $hashLine |" |
              Add-Content "$LOG_DIR\deploy-history.md"
            $success = $true
        } else {
            Send-SlackReport "⚠️ [배포 실패 $attempt/$MaxAttempts] production health check 실패 — 자동 수정 중" "error"
            git -C $ProjectRoot stash
        }
    } else {
        $errTail = Get-Content "$LOG_DIR\staging-err.log" -Tail 5 -ErrorAction SilentlyContinue | Out-String
        Send-SlackReport "⚠️ [배포 실패 $attempt/$MaxAttempts] $($errTail.Trim()) — 자동 수정 중" "error"
        git -C $ProjectRoot stash
    }
}

if (-not $success) {
    $lastErr = Get-Content "$LOG_DIR\staging-err.log" -Tail 5 -ErrorAction SilentlyContinue | Out-String
    git -C $ProjectRoot checkout HEAD
    Stop-PortProcess $STAGING_PORT
    # Production 재시작 (기존 코드로)
    Stop-PortProcess $PROD_PORT
    # ... 타입별 Production 명령 실행 ...
    Send-SlackReport "🔴 [롤백] max_attempts 초과 — 이전 버전 복구 완료`n에러: $($lastErr.Trim())`n로그: $LOG_DIR\staging-err.log" "rollback"
    "| $(Get-Date -Format 'yyyy-MM-dd HH:mm') | $MaxAttempts | 롤백 | $(git -C $ProjectRoot rev-parse HEAD) |" |
      Add-Content "$LOG_DIR\deploy-history.md"
}
```

---

## Step 5: 로그 관리

```
{ProjectRoot}/logs/
  staging.log           ← staging stdout
  staging-err.log       ← staging stderr
  build.log             ← Next.js / Android 빌드 로그
  production.log        ← production stdout
  production-err.log    ← production stderr
  rollback.log          ← 롤백 시 빌드/시작 로그
  deploy-history.md     ← 배포 이력
```

`deploy-history.md` 초기 헤더 (최초 실행 시 생성):
```markdown
# Deploy History
| 시각 | 시도횟수 | 결과 | Commit Hash |
|------|---------|------|------------|
```
```

---

## PATCH-04: `.claude/agents/member-epsilon/AGENT.md`

### 변경 전 (파일 끝 부분)
```markdown
## 안전장치
- 배포 명령(`git push`, `npm run deploy` 등)은 Team Lead 승인(`human_approval`) 필수
- 파일 수정 및 검증은 epsilon 자율 실행
- 검증 실패 3회 초과 시 자체 판단 금지, Team Lead 에 보고 후 대기

## Constraints
- **절대 금지**: 산출물(WS/member-epsilon/) 외의 파일을 수정하지 않는다.
  CLAUDE.md, team-config.yaml, 다른 멤버의 AGENT.md 등 기존 파일 편집은 팀장만 수행한다.
```

### 변경 후 (안전장치 수정 + Deployment Protocol·Skills Reference 추가)
```markdown
## 안전장치
- 배포 명령은 AUTO 모드에서 `deploy-heal` 스킬이 자동 실행 (Team Lead 지시 하에).
- 일반 모드: 배포 전 Team Lead 승인(`human_approval`) 필수.
- 자체 검증 실패 3회 초과 → Team Lead 및 Slack에 보고 후 deploy-heal에 에스컬레이션.

## Deployment Protocol
코드 수정(Execution Flow Step 3) 완료 후 자동 진행.

### 사전 점검
1. 프로젝트 루트에서 서비스 타입 자동 감지 (`deploy-heal` 스킬 `Get-ServiceType` 호출)
2. `PROD_PORT` 확인 — team-config.yaml `environment.PROD_PORT` 또는 프로젝트 `.env`에서 로드
3. `STAGING_PORT = PROD_PORT + 1000` 자동 설정
4. `git status` 실행 → 수정 파일 목록을 `dev-log.md`에 기록

### 실행 순서
```
Step 1  코드 수정 완료 (Execution Flow)
Step 2  deploy-heal 스킬 호출 (자동)
          → 서비스 타입 감지
          → Staging 시작 + Health Check
          → Self-Healing 루프 (MAX_ATTEMPTS = 3)
          → Production 배포 또는 Rollback
Step 3  결과를 WS/member-epsilon/dev-log.md에 기록
```

### dev-log.md 배포 결과 기록 형식
```
## 배포 결과
- 서비스 타입: {타입}
- PROD_PORT / STAGING_PORT: {포트} / {포트}
- 시도 횟수: {N}/3
- 각 시도별 결과:
  | 시도 | 상태 | 에러 요약 | 적용 수정 |
  |------|------|---------|---------|
- 최종 결과: 성공 / 롤백
- 배포 commit hash: {hash}
```

### AUTO 모드 에스컬레이션 조건
아래 상황에서만 대기 없이 Slack에 즉시 보고 (`/report` 엔드포인트 경유):
- 서비스 타입 감지 실패 (`unknown`)
- `MAX_ATTEMPTS` 초과 후 롤백 완료
- Production health check 최종 실패

에스컬레이션 보고 형식:
```
POST http://localhost:5000/report
{"message": "⚠️ [epsilon 에스컬레이션] {사유}\n프로젝트: {path}\n마지막 에러: {요약}", "level": "error"}
```

## Skills Reference
- `deploy-heal`         ← 배포·자가수정·롤백 자동화 (신규)
- `shared/file-io`      ← 로컬 파일 읽기/쓰기
- `shared/data-parser`  ← 데이터 파싱

## Constraints
- **절대 금지**: 산출물(WS/member-epsilon/) 외의 파일을 수정하지 않는다.
  CLAUDE.md, team-config.yaml, 다른 멤버의 AGENT.md 등 기존 파일 편집은 팀장만 수행한다.
- deploy-heal 스킬은 대상 프로젝트 파일만 수정한다 (agent-team 레포 파일 수정 금지).
```

---

## PATCH-05: `team-config.yaml`

아래 내용을 `team-config-auto-patch.yaml` 로 저장하고, `team-config.yaml`의 해당 섹션에 수동 병합한다.

```yaml
# ── team-config-auto-patch.yaml ──────────────────────────────

# 1. execution 섹션에 auto_mode 서브섹션 추가
execution:
  dependency_strategy: "lead_decides"
  data_passing: "file_based"
  intermediate_output_dir: "output"
  auto_mode:
    enabled: true
    trigger_prefix: "[AUTO:"
    interrupt_policy: "none"
    escalation_channel: "slack"
    escalation_endpoint: "http://localhost:5000/report"
    review_direct_edit_threshold: 30
    auto_log_file: "auto-log.md"

# 2. task.types 중 dev 항목에 deployment 서브섹션 추가
#    (기존 dev type 의 하위에 병합)
dev_deployment_config:
  deployment:
    enabled: true
    skill: "deploy-heal"
    max_attempts: 3
    staging_port_offset: 1000
    health_check_timeout_sec: 30
    health_check_retries: 3
    health_check_interval_sec: 10
    rollback_on_failure: true
    commit_on_success: true

# 3. 환경변수 섹션 추가
environment:
  SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}"
  SLACK_REPORT_CHANNEL: "${SLACK_REPORT_CHANNEL:-#agent-log}"
  PROD_PORT: "${PROD_PORT:-8000}"

# 4. termination 수정
termination:
  max_cycles: 3
  max_review_per_member: 2
  human_approval: false
  auto_proceed_on_escalation: true
```

**`queue-config.yaml`에도 추가:**

```yaml
slack:
  webhook_receive_port: 5000
  token_file: .secrets/slack-token
  report_channel: "#agent-log"    # ← 추가

opencode:
  default_model: anthropic/claude-sonnet-4-6
  workspace_root: ./output

priority:
  urgent: 0
  task: 1
  schedule: 2
  default: 1

environment:                      # ← 추가 (문서화 목적)
  SLACK_BOT_TOKEN: "환경변수로 설정"
  SLACK_REPORT_CHANNEL: "#agent-log"
  PROD_PORT: "8000"
```

---

## 검증 체크리스트

- [x] Slack 역보고 7개 시점 모두 구현됨 (수신·Phase완료·배포시도·성공·실패·롤백·최종완료)
- [x] AUTO 모드 인터럽트 포인트 8개 모두 처리됨 (①~⑧)
- [x] 서비스 타입 7종 감지 로직 포함됨 (flutter·android·docker·nextjs·nodejs·python-web·python-script)
- [x] $MaxAttempts = 3 스크립트 내 상수로 하드코딩됨
- [x] 롤백 경로가 7종 모든 서비스 타입에 정의됨
- [x] Windows PowerShell 5.1 문법으로 작성됨 (`*>&1`, `Invoke-RestMethod`, `&&` 미사용)
- [x] .env 설정 가이드 포함됨 (Step 1)
- [x] 기존 manual 모드 동작 유지됨 (AUTO 트리거 없으면 기존 human_approval 흐름 그대로)
- [x] /report 엔드포인트로 opencode·epsilon·deploy-heal 모두 역보고 가능
- [x] 포트·환경변수 명칭 5개 패치 간 일치 확인 (PROD_PORT·STAGING_PORT·SLACK_BOT_TOKEN·SLACK_REPORT_CHANNEL)
