# Design Spec — AUTO 모드 무인화 + deploy-heal 스킬 + team-config 패치

Creator: member-zeta
Created: 2026-05-26
Version: 1.0

---

## 개요

본 설계서는 세 가지 산출물(PATCH-02·03·05)을 포함한다:
- **PATCH-02**: CLAUDE.md AUTO 모드 8개 인터럽트 포인트 완전 무인화
- **PATCH-03**: `.claude/skills/deploy-heal/SKILL.md` 신규 생성
- **PATCH-05**: `team-config-auto-patch.yaml` 신규 생성

---

## 분석 결과

### AUTO 모드 인터럽트 맵 (현재 CLAUDE.md 기준)

| # | 위치 | 현재 동작 | AUTO 처리 |
|---|------|---------|---------|
| ① | Workspace Protocol — 슬러그 확인 | human_approval:true 시 사용자 확인 | 자동 확정, plan.md에 기록 |
| ② | Phase 1 선행 — 재사용 여부 | Y/N 사용자 제안 | 30일+80% 시 자동 재사용, 아니면 신규 |
| ③ | Phase 1-0 — 동점 처리 | 사용자 선택 요청 | config 순서 기준 자동 선택 |
| ④ | Phase 3 — 직접수정 기준 | 미명시 (20% 가정) | 30%로 완화, 최대한 직접 수정 |
| ⑤ | Phase 4 — 품질 미충족 재실행 | 미명시 (사용자 확인 가능) | max_cycles 이내 자동 재실행 |
| ⑥ | Termination — human_approval 게이트 | 최종 산출물 사용자 제시 | 자동 승인, Phase 5 즉시 |
| ⑦ | 에스컬레이션 — 파일 없음 등 | 대기 | Slack 보고 후 최선 버전 진행 |
| ⑧ | Phase 5 Distribution | enabled:true 엔드포인트 실행 | 동일, auto-log.md에 결과 기록 |

---

## PATCH-02: CLAUDE.md AUTO 모드 무인화

### 수정 위치 1 — Workspace Protocol 자동 모드 섹션 확장

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
AUTO 모드에서는 아래 인터럽트 포인트를 모두 자동 처리한다. 각 판단은 `WS/auto-log.md`에 기록한다.

**① 슬러그 확인 (Workspace Protocol)**
- 자동 확정. plan.md 상단에 "자동 확정된 slug: {slug}" 기록.

**② 리서치 재사용 여부 (Phase 1 선행 체크)**
- 30일 이내 + 80% 겹침 판단 시 → 자동 재사용 (Y 선택).
- 조건 미충족 시 → 자동 신규 탐색 (N 선택).
- `auto-log.md`에 판단 근거 기록.

**③ Task Type 동점 처리 (Phase 1-0)**
- 동점 발생 시 `team-config.yaml`의 `task.types` 나열 순서를 기준으로 자동 선택.
- `auto-log.md`에 동점 후보 목록과 선택 결과 기록.

**④ Phase 3 Review — 직접수정 기준 완화**
- AUTO 모드에서 직접수정(EDIT) 기준: 수정량 30% 이하 (일반 모드 기본 대비 완화).
- 30% 초과 시 REASSIGN 처리 (멤버 재실행).
- 목표: 재호출 최소화.

**⑤ Phase 4 품질 미충족 재실행**
- `max_cycles` 이내면 사용자 확인 없이 자동 재실행.
- `auto-log.md`에 재실행 사유 기록.

**⑥ human_approval 게이트 (Termination Protocol)**
- AUTO 모드에서 자동 승인 처리.
- 즉시 Phase 5 진입.

**⑦ 에스컬레이션 (파일 없음, 서비스 타입 감지 실패 등)**
- `/report` 엔드포인트(queue_server.py)를 통해 Slack에 에러 보고.
- 대기하지 않고 현재 최선 버전으로 계속 진행.
- `auto-log.md`에 에스컬레이션 사유와 대응 기록.

**⑧ Phase 5 Distribution**
- `enabled: true` 인 모든 엔드포인트 즉시 실행.
- 각 결과(성공/실패/URL)를 `WS/auto-log.md`에 추가 기록.
```

### 수정 위치 2 — auto-log.md 형식 정의 (Phase 1 이전 또는 Handoff Rules 섹션에 추가)

```markdown
## AUTO 모드 실행 로그 형식 (`WS/auto-log.md`)

AUTO 모드 실행 시 아래 형식으로 실시간 기록한다:

```
# AUTO 실행 로그
slug: {slug}
시작: {YYYY-MM-DD HH:MM}

## 판단 기록
| 시각 | 포인트 | 판단 내용 | 근거 |
|------|--------|---------|------|
| HH:MM | ① 슬러그 | 자동 확정 | human_approval:false |
| HH:MM | ② 재사용 | 신규 탐색 | 30일 초과 |
...

## Phase 진행
| Phase | 시작 | 완료 | 결과 |
|-------|------|------|------|
| 1 | HH:MM | HH:MM | task_type=design |
...

## Distribution
| 엔드포인트 | 결과 | URL |
|-----------|------|-----|
| notion | 성공 | https://... |
```
```

---

## PATCH-03: `.claude/skills/deploy-heal/SKILL.md` (신규 생성)

```markdown
# deploy-heal Skill

## 목적
서비스 타입 자동 감지 → staging 테스트 → self-healing 루프 → production 배포 → 롤백

## 호출 방법
member-epsilon이 Phase 2 코드 수정 완료 후 자동 호출.
Team Lead도 직접 호출 가능.

---

## Step 1: 서비스 타입 감지

프로젝트 루트에서 아래 순서로 파일 존재 여부를 확인한다:

| 순서 | 확인 파일 | 서비스 타입 |
|------|---------|-----------|
| 1 | `pubspec.yaml` | Flutter |
| 2 | `android/build.gradle` | Android Native |
| 3 | `Dockerfile` | Docker |
| 4 | `package.json` (next in deps) | Next.js |
| 4 | `package.json` | Node.js |
| 5 | `requirements.txt` (flask OR fastapi) | Python Web |
| 5 | `requirements.txt` | Python Script |
| - | 감지 실패 | → Team Lead 에스컬레이션 |

PowerShell 감지 로직:
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

---

## Step 2: 서비스 타입별 실행 명세

### 공통 변수
```powershell
$PROD_PORT    = $env:PROD_PORT    # .env 또는 시스템 환경변수
$STAGING_PORT = [int]$PROD_PORT + 1000
$LOG_DIR      = "$ProjectRoot\logs"
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
```

### Python Web (flask / fastapi)
```powershell
# Staging 시작
$stagingProc = Start-Process python `
  -ArgumentList "app.py --port $STAGING_PORT" `
  -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError  "$LOG_DIR\staging-err.log" `
  -WindowStyle Hidden -PassThru

# Health Check
$healthUrl = "http://localhost:$STAGING_PORT/health"
# → Step 3 공통 Health Check 루프

# Production 배포
Stop-PortProcess $PROD_PORT
$prodProc = Start-Process python `
  -ArgumentList "app.py --port $PROD_PORT" `
  -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" `
  -RedirectStandardError  "$LOG_DIR\production-err.log" `
  -WindowStyle Hidden -PassThru

# 롤백
git -C $ProjectRoot checkout HEAD~1
Stop-PortProcess $PROD_PORT
Start-Process python -ArgumentList "app.py --port $PROD_PORT" ...
```

### Node.js
```powershell
# Staging
$env:PORT = $STAGING_PORT
$stagingProc = Start-Process node `
  -ArgumentList "server.js" `
  -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError  "$LOG_DIR\staging-err.log" `
  -WindowStyle Hidden -PassThru
$healthUrl = "http://localhost:$STAGING_PORT"
# Production: $env:PORT = $PROD_PORT 후 동일 패턴
# 롤백: git checkout HEAD~1 + 재시작
```

### Next.js
```powershell
# Build + Staging
$buildOut = & npm run build *>&1
$buildOut | Out-File "$LOG_DIR\build.log"
if ($LASTEXITCODE -ne 0) { throw "Build failed" }
$stagingProc = Start-Process node `
  -ArgumentList "node_modules/.bin/next start -p $STAGING_PORT" `
  -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError  "$LOG_DIR\staging-err.log" `
  -WindowStyle Hidden -PassThru
$healthUrl = "http://localhost:$STAGING_PORT"
# Production: -p $PROD_PORT 로 재시작
# 롤백: git checkout HEAD~1 + 재빌드 + 재시작
```

### Flutter
```powershell
# Staging: debug 빌드 (exit code로 성공 판정)
$flutterStage = & flutter build apk --debug *>&1
$flutterStage | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)
# Health Check: exit code == 0 → Pass

# Production: release 빌드
$flutterProd = & flutter build apk --release *>&1
$flutterProd | Out-File "$LOG_DIR\production.log"

# 롤백: 변경사항 되돌리기 (자동수정 코드 취소)
git -C $ProjectRoot stash
```

### Android Native
```powershell
# Staging: debug 빌드
$gradleStage = & "$ProjectRoot\gradlew" assembleDebug *>&1
$gradleStage | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)
# Health Check: exit code == 0 → Pass (APK 생성 성공)

# Production: release 빌드
$gradleProd = & "$ProjectRoot\gradlew" assembleRelease *>&1
$gradleProd | Out-File "$LOG_DIR\production.log"

# 롤백: 코드 변경사항 취소 후 이전 버전 재빌드
git -C $ProjectRoot stash
& "$ProjectRoot\gradlew" assembleRelease *>&1 | Out-File "$LOG_DIR\rollback.log"
```

### Docker
```powershell
# Staging
$dockerStage = & docker compose -f docker-compose.staging.yml up -d *>&1
$dockerStage | Out-File "$LOG_DIR\staging.log"
$containerName = (Get-Content docker-compose.staging.yml | Select-String "container_name").ToString().Split(":")[-1].Trim()
$stagingOk = [bool](docker ps --filter "name=$containerName" --format "{{.Names}}")

# Production
$dockerProd = & docker compose up -d *>&1
$dockerProd | Out-File "$LOG_DIR\production.log"

# 롤백
& docker compose down
git -C $ProjectRoot checkout HEAD~1
& docker compose up -d
```

### Python Script
```powershell
# Staging: dry-run
$dryOut = & python script.py --dry-run *>&1
$dryOut | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)

# Production
$prodProc = Start-Process python `
  -ArgumentList "script.py" `
  -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" `
  -RedirectStandardError  "$LOG_DIR\production-err.log" `
  -WindowStyle Hidden -PassThru

# 롤백
git -C $ProjectRoot checkout HEAD
```

---

## Step 3: 공통 유틸리티 함수

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

# Health Check 루프 (HTTP)
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

# Slack 역보고 (queue_server.py /report 엔드포인트 경유)
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

## Step 4: Self-Healing 루프

```powershell
param(
    [string]$ProjectRoot,
    [string]$ServiceType,   # Get-ServiceType 결과
    [int]$WaitSecAfterStart = 30
)
$MaxAttempts = 3  # 하드코딩 — 변경 시 SKILL.md 수정 필요

$attempt = 0
$success = $false

# 현재 변경사항 임시 저장
git -C $ProjectRoot stash

while ($attempt -lt $MaxAttempts -and -not $success) {
    $attempt++
    Send-SlackReport "🚀 [배포 시도 $attempt/$MaxAttempts] staging → $ServiceType" "progress"

    # [Step 1] 코드 변경 적용
    git -C $ProjectRoot stash pop

    # [Step 2] Staging 시작
    Stop-PortProcess $STAGING_PORT
    # (서비스 타입별 Staging 시작 명령 실행 — Step 2 참조)
    Start-Sleep $WaitSecAfterStart

    # [Step 3] Health Check
    $healthOk = $false
    if ($ServiceType -in @("python-web","nodejs","nextjs","docker")) {
        $healthOk = Test-Health -Url $healthUrl -Retries 3 -IntervalSec 10
    } elseif ($ServiceType -in @("flutter","python-script","android")) {
        # exit code 기반 판정은 이미 Start 단계에서 완료
        $healthOk = $stagingOk
    }

    if ($healthOk) {
        # [Step 4] Production 배포
        Stop-PortProcess $PROD_PORT
        # (서비스 타입별 Production 시작 명령 실행)
        Start-Sleep 10

        $prodOk = Test-Health -Url "http://localhost:$PROD_PORT/health" -Retries 3 -IntervalSec 10
        if ($prodOk) {
            git -C $ProjectRoot add -A
            git -C $ProjectRoot commit -m "auto-fix: deploy attempt $attempt ($ServiceType)"
            Send-SlackReport "✅ [배포 완료] production 정상 가동 (시도 $attempt/$MaxAttempts)" "success"

            # deploy-history.md 기록
            $histLine = "| $(Get-Date -Format 'yyyy-MM-dd HH:mm') | $attempt | 성공 | $(git -C $ProjectRoot rev-parse HEAD) |"
            Add-Content "$LOG_DIR\deploy-history.md" $histLine

            $success = $true
        } else {
            Send-SlackReport "⚠️ [배포 실패 $attempt/$MaxAttempts] production health check 실패 — 자동 수정 중" "error"
            $errorSummary = Get-Content "$LOG_DIR\production-err.log" -Tail 20 | Out-String
            # epsilon이 에러 분석 후 코드 수정 (Team Lead를 통한 재호출)
            git -C $ProjectRoot stash  # 실패한 변경사항 임시 저장
        }
    } else {
        Send-SlackReport "⚠️ [배포 실패 $attempt/$MaxAttempts] staging health check 실패 — 자동 수정 중" "error"
        $errorSummary = Get-Content "$LOG_DIR\staging-err.log" -Tail 20 | Out-String
        git -C $ProjectRoot stash
    }
}

# ROLLBACK
if (-not $success) {
    $lastError = Get-Content "$LOG_DIR\staging-err.log" -Tail 5 | Out-String
    git -C $ProjectRoot checkout HEAD
    Stop-PortProcess $STAGING_PORT

    # production은 기존 코드로 재시작
    Stop-PortProcess $PROD_PORT
    # (서비스 타입별 Production 재시작)

    Send-SlackReport "🔴 [롤백] max_attempts 초과 — 이전 버전 복구 완료`n에러: $($lastError.Trim())`n로그: $LOG_DIR\staging-err.log" "rollback"

    $histLine = "| $(Get-Date -Format 'yyyy-MM-dd HH:mm') | $MaxAttempts | 롤백 | $(git -C $ProjectRoot rev-parse HEAD) |"
    Add-Content "$LOG_DIR\deploy-history.md" $histLine
}
```

---

## Step 5: 로그 관리

```
{ProjectRoot}/logs/
  staging.log         ← staging stdout
  staging-err.log     ← staging stderr
  build.log           ← Next.js / Flutter 빌드 로그
  production.log      ← production stdout
  production-err.log  ← production stderr
  deploy-history.md   ← 배포 이력
```

`deploy-history.md` 형식:
```markdown
# Deploy History
| 시각 | 시도횟수 | 결과 | Commit Hash |
|------|---------|------|------------|
| 2026-05-26 14:30 | 1 | 성공 | abc1234 |
| 2026-05-26 15:10 | 3 | 롤백 | def5678 |
```
```

---

## PATCH-05: `team-config-auto-patch.yaml` (신규 생성)

실제 파일 내용:

```yaml
# ── team-config-auto-patch.yaml ──────────────────────────────
# 적용: team-config.yaml의 해당 섹션에 병합 또는 추가
# 주의: 이 파일은 diff 패치가 아닌 추가 설정 명세임.
#       실제 team-config.yaml에 수동 병합하거나 자동 로드 로직을 구현할 것.

# 1. execution 섹션에 auto_mode 서브섹션 추가
execution:
  dependency_strategy: "lead_decides"
  data_passing: "file_based"
  intermediate_output_dir: "output"
  auto_mode:
    enabled: true
    trigger_prefix: "[AUTO:"           # Slack 메시지 감지 패턴
    interrupt_policy: "none"           # 모든 인터럽트 자동 처리
    escalation_channel: "slack"        # 대기 대신 Slack /report 엔드포인트 사용
    review_direct_edit_threshold: 30   # AUTO 모드 직접수정 기준 (%)
    auto_log_file: "auto-log.md"       # WS 내 판단 기록 파일

# 2. task.types 중 dev 항목에 deployment 서브섹션 추가
# (기존 dev type 아래에 병합)
dev_task_deployment_patch:
  deployment:
    enabled: true
    skill: "deploy-heal"               # 호출할 스킬 이름
    max_attempts: 3
    staging_port_offset: 1000          # PROD_PORT + 1000 = STAGING_PORT
    health_check_timeout_sec: 30       # staging 서비스 초기화 대기
    health_check_retries: 3
    health_check_interval_sec: 10
    rollback_on_failure: true
    commit_on_success: true
    report_endpoint: "http://localhost:5000/report"  # queue_server.py 역보고

# 3. 환경변수 섹션 추가
environment:
  SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}"
  SLACK_REPORT_CHANNEL: "${SLACK_REPORT_CHANNEL:-#agent-log}"
  PROD_PORT: "${PROD_PORT:-8000}"

# 4. termination 수정 (AUTO 모드 기본값 명시)
termination:
  max_cycles: 3
  max_review_per_member: 2
  human_approval: false
  auto_proceed_on_escalation: true    # 에스컬레이션 시 대기 없이 진행
```

---

## 결론

세 패치의 핵심 설계 원칙:

1. **PATCH-02**: AUTO 모드는 "판단만 자동화"가 아닌 "기록하면서 자동화" — 모든 자동 판단을 `auto-log.md`에 남겨 감사 가능하게 유지
2. **PATCH-03**: Self-healing 루프는 `$MaxAttempts = 3` 스크립트 내 상수 + Android 포함 7종 전체 서비스 타입에 롤백 경로 명시적으로 정의
3. **PATCH-05**: 기존 team-config.yaml을 직접 덮어쓰지 않고 patch 파일로 분리해 병합 시 충돌 최소화
