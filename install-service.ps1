# Agent Team Slack Bridge 자동 시작 서비스 설치 스크립트
# 관리자 권한으로 실행하세요

$bridgePath = "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\slack-bridge\app-B-jmlee-N2.py"
$bridgeVenv = "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\slack-bridge\.venv\Scripts\python.exe"

if (-not (Test-Path $bridgeVenv)) {
    Write-Host "slack-bridge .venv 를 찾을 수 없습니다: $bridgeVenv"
    Write-Host "slack-bridge/ 에서 'python -m venv .venv && .venv\Scripts\pip install -r requirements.txt' 를 먼저 실행하세요."
    exit 1
}

# 작업 스케줄러 태스크 생성 (로그온 시 자동 시작)
$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = "PT00:01:00"
$action = New-ScheduledTaskAction -Execute $bridgeVenv -Argument $bridgePath -WorkingDirectory (Split-Path $bridgePath)
Register-ScheduledTask -TaskName "AgentTeam-SlackBridge" -Action $action -Trigger $trigger -RunLevel Highest -Force

Write-Host "작업 스케줄러가 등록되었습니다."
Write-Host "  - AgentTeam-SlackBridge: 슬랙 브릿지 (로그온 후 1 분 지연 시작)"
Write-Host ""
Write-Host "확인: 작업 스케줄러 > 작업 스케줄러 라이브러리 > AgentTeam-SlackBridge"
