# Agent Team Slack Bridge - register an always-on, self-restarting scheduled task.
# Run this from an Administrator PowerShell window.
#
# Replaces the existing "AgentTeam-SlackBridge" task (AtLogOn once, runs app.py directly)
# with one that runs run-forever.ps1 - a supervisor loop that restarts app.py 5 seconds
# after it exits, for any reason, with no retry limit. That makes it effectively always-on.
#
# NOTE: keep this file ASCII-only (Windows PowerShell 5.1 can misparse non-ASCII text
# in a .ps1 file without a UTF-8 BOM).

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Administrator privileges required. Re-run this from an elevated PowerShell window."
    exit 1
}

$taskName = "AgentTeam-SlackBridge"
$supervisorScript = Join-Path $PSScriptRoot "run-forever.ps1"

if (-not (Test-Path $supervisorScript)) {
    Write-Host "run-forever.ps1 not found: $supervisorScript"
    exit 1
}

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop
    Write-Host "Removed existing task '$taskName'."
}

$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = "PT30S"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$supervisorScript`"" `
    -WorkingDirectory $PSScriptRoot

# The supervisor script loops forever internally, so remove Task Scheduler's default
# execution time limit (usually 3 days) - otherwise Task Scheduler would kill it itself.
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -RunLevel Highest -User $env:USERNAME -Force -ErrorAction Stop

Write-Host "Task '$taskName' re-registered as an always-on supervised task."
Write-Host "Starting it now..."
Start-ScheduledTask -TaskName $taskName

Start-Sleep -Seconds 3
$info = Get-ScheduledTaskInfo -TaskName $taskName
Write-Host "LastTaskResult: $($info.LastTaskResult)  LastRunTime: $($info.LastRunTime)"
