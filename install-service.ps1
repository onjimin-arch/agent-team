# Agent Team 자동 시작 서비스 설치 스크립트
# 관리자 권한으로 실행하세요

$pythonPath = "C:\Python311\python.exe"
if (-not (Test-Path $pythonPath)) {
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonPath) {
        Write-Host "Python 을 찾을 수 없습니다."
        exit 1
    }
}

$queueServerPath = "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\queue_server.py"
$bridgePath = "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\slack-bridge\app.py"
$bridgeVenv = "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\slack-bridge\.venv\Scripts\python.exe"

# 작업 스케줄러 태스크 생성 (로그온 시 자동 시작)
$trigger = New-ScheduledTaskTrigger -AtLogOn
$action1 = New-ScheduledTaskAction -Execute $pythonPath -Argument $queueServerPath -WorkingDirectory (Split-Path $queueServerPath)
Register-ScheduledTask -TaskName "AgentTeam-QueueServer" -Action $action1 -Trigger $trigger -RunLevel Highest -Force

$trigger2 = New-ScheduledTaskTrigger -AtLogOn
$trigger2.Delay = "PT00:02:00"
$action2 = New-ScheduledTaskAction -Execute $bridgeVenv -Argument $bridgePath -WorkingDirectory (Split-Path $bridgePath)
Register-ScheduledTask -TaskName "AgentTeam-SlackBridge" -Action $action2 -Trigger $trigger2 -RunLevel Highest -Force

Write-Host "작업 스케줄러가 등록되었습니다."
Write-Host "  - AgentTeam-QueueServer: 큐 서버 (로그온 시 자동 시작)"
Write-Host "  - AgentTeam-SlackBridge: 슬랙 브릿지 (2 분 지연 시작)"
Write-Host ""
Write-Host "확인: 작업 스케줄러 > 작업 스케줄러 라이브러리 > AgentTeam-*"
