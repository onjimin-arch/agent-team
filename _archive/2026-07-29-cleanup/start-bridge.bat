@echo off
cd /d "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team\slack-bridge"
.venv\Scripts\python app.py >> logs\bridge.log 2>&1
