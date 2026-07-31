# Agent Team Slack Bridge - always-restart supervisor loop.
# Restarts app.py automatically whenever it exits (normal or crash), no retry limit.
# app.py itself has a single-instance lock, so a manual duplicate start is safely rejected.
#
# NOTE: keep this file ASCII-only. Windows PowerShell 5.1 can misparse non-ASCII
# characters (e.g. Korean text, em-dash) in a .ps1 file without a UTF-8 BOM.

$ErrorActionPreference = "Continue"
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$script = Join-Path $PSScriptRoot "app.py"
$logDir = Join-Path $PSScriptRoot "..\logs"
$logFile = Join-Path $logDir "slack-bridge-supervisor.log"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

while ($true) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "[$ts] starting app.py"

    & $python $script
    $exitCode = $LASTEXITCODE

    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "[$ts] app.py exited (code $exitCode) - restarting in 5s"
    Start-Sleep -Seconds 5
}
