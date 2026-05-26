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

unknown 반환 시: `POST http://localhost:5000/report` 로 Slack에 에러 보고 후 Team Lead에 에스컬레이션.

---

## Step 2: 공통 유틸리티 함수

```powershell
function Stop-PortProcess {
    param([int]$Port)
    $pidStr = (netstat -ano | Select-String ":$Port\s" |
               Select-Object -First 1).ToString().Trim().Split()[-1]
    if ($pidStr -and $pidStr -ne "0") {
        try { taskkill /PID $pidStr /F 2>$null } catch {}
    }
}

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

## Step 3: 서비스 타입별 Staging / Production / Rollback

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
git -C $ProjectRoot checkout HEAD; Stop-PortProcess $PROD_PORT
Start-Process python -ArgumentList "app.py --port $PROD_PORT" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" -WindowStyle Hidden
```

### Node.js
```powershell
# Staging
Stop-PortProcess $STAGING_PORT; $env:PORT = "$STAGING_PORT"
$stagingProc = Start-Process node -ArgumentList "server.js" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\staging.log" `
  -RedirectStandardError "$LOG_DIR\staging-err.log" -WindowStyle Hidden -PassThru
$healthUrl = "http://localhost:$STAGING_PORT"

# Production
Stop-PortProcess $PROD_PORT; $env:PORT = "$PROD_PORT"
Start-Process node -ArgumentList "server.js" -WorkingDirectory $ProjectRoot `
  -RedirectStandardOutput "$LOG_DIR\production.log" `
  -RedirectStandardError "$LOG_DIR\production-err.log" -WindowStyle Hidden

# Rollback
git -C $ProjectRoot checkout HEAD; Stop-PortProcess $PROD_PORT; $env:PORT = "$PROD_PORT"
Start-Process node -ArgumentList "server.js" -WorkingDirectory $ProjectRoot -WindowStyle Hidden
```

### Next.js
```powershell
# Staging
$buildOut = & npm run build *>&1; $buildOut | Out-File "$LOG_DIR\build.log"
if ($LASTEXITCODE -ne 0) { throw "Next.js build failed" }
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
& npm run build *>&1 | Out-File "$LOG_DIR\rollback-build.log"
Stop-PortProcess $PROD_PORT
Start-Process node -ArgumentList "node_modules/.bin/next start -p $PROD_PORT" `
  -WorkingDirectory $ProjectRoot -WindowStyle Hidden
```

### Flutter
```powershell
# Staging
$stageOut = & flutter build apk --debug *>&1; $stageOut | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)

# Production
$prodOut = & flutter build apk --release *>&1; $prodOut | Out-File "$LOG_DIR\production.log"

# Rollback
git -C $ProjectRoot stash
& flutter build apk --release *>&1 | Out-File "$LOG_DIR\rollback.log"
```

### Android Native
```powershell
# Staging
$stageOut = & "$ProjectRoot\gradlew" assembleDebug *>&1
$stageOut | Out-File "$LOG_DIR\staging.log"
$stagingOk = ($LASTEXITCODE -eq 0)

# Production
$prodOut = & "$ProjectRoot\gradlew" assembleRelease *>&1
$prodOut | Out-File "$LOG_DIR\production.log"

# Rollback
git -C $ProjectRoot stash
& "$ProjectRoot\gradlew" assembleRelease *>&1 | Out-File "$LOG_DIR\rollback.log"
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
& docker compose up -d *>&1 | Out-File "$LOG_DIR\production.log"

# Rollback
& docker compose down
git -C $ProjectRoot checkout HEAD
& docker compose up -d
```

### Python Script
```powershell
# Staging
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

    # (서비스 타입별 Staging 시작 — Step 3 참조)
    Stop-PortProcess $STAGING_PORT
    if (-not $exitCodeBased) { Start-Sleep $WaitSecAfterStart }

    $healthOk = if ($exitCodeBased) { $stagingOk } else { Test-Health -Url $healthUrl }

    if ($healthOk) {
        Stop-PortProcess $PROD_PORT
        # (서비스 타입별 Production 시작 — Step 3 참조)
        Start-Sleep 10

        $prodOk = if ($exitCodeBased) {
            $LASTEXITCODE -eq 0
        } else {
            Test-Health -Url "http://localhost:$PROD_PORT/health"
        }

        if ($prodOk) {
            git -C $ProjectRoot add -A
            git -C $ProjectRoot commit -m "auto-fix: $ServiceType attempt $attempt"
            Send-SlackReport "✅ [배포 완료] production 정상 가동 (시도 $attempt/$MaxAttempts)" "success"
            "| $(Get-Date -Format 'yyyy-MM-dd HH:mm') | $attempt | 성공 | $(git -C $ProjectRoot rev-parse HEAD) |" |
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
    Stop-PortProcess $PROD_PORT
    # (서비스 타입별 Production 재시작 — Step 3 Rollback 참조)
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
  build.log             ← Next.js / Android 빌드
  production.log        ← production stdout
  production-err.log    ← production stderr
  rollback.log          ← 롤백 시 재빌드 로그
  deploy-history.md     ← 배포 이력
```

`deploy-history.md` 초기 헤더 (최초 실행 전 생성):
```markdown
# Deploy History
| 시각 | 시도횟수 | 결과 | Commit Hash |
|------|---------|------|------------|
```
