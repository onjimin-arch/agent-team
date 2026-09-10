# Windows 작업 스케줄러 등록

Claude Code 내장 cron 대신 이 방식으로 스케줄링하기로 결정함(2026-08-13). 4개 작업 모두
`scripts/run_scheduled.py`를 호출하며, 실제 값(quota/시각/드롭폴더)은 `config/knowledge_pipeline.json`
에서 읽는다 — 이 파일만 고치면 스크립트 동작은 바로 바뀐다(단, 아래 트리거 **시각** 자체를 바꾸려면
작업 스케줄러 쪽도 다시 등록해야 한다).

## 등록 명령 (PowerShell 관리자 권한 불필요, 현재 사용자 권한으로 충분)

```powershell
$py = (Get-Command python).Source -replace 'python\.exe$', 'pythonw.exe'   # 콘솔 창 안 뜨는 버전(2026-08-13 정정)
$root = "C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\agent-team"

# notion-sync — 15분마다
schtasks /create /tn "KB-notion-sync" /tr "`"$py`" `"$root\scripts\run_scheduled.py`" --task notion-sync" /sc minute /mo 15 /f

# slack-sync — 15분마다
schtasks /create /tn "KB-slack-sync" /tr "`"$py`" `"$root\scripts\run_scheduled.py`" --task slack-sync" /sc minute /mo 15 /f

# file-watcher — 5분마다
schtasks /create /tn "KB-file-watcher" /tr "`"$py`" `"$root\scripts\run_scheduled.py`" --task file-watcher" /sc minute /mo 5 /f

# note-structurer — 매일 09:00, 13:00 (config의 batch_times와 맞춤)
schtasks /create /tn "KB-note-structurer-am" /tr "`"$py`" `"$root\scripts\run_scheduled.py`" --task note-structurer" /sc daily /st 09:00 /f
schtasks /create /tn "KB-note-structurer-pm" /tr "`"$py`" `"$root\scripts\run_scheduled.py`" --task note-structurer" /sc daily /st 13:00 /f
```

## 확인 / 삭제
```powershell
schtasks /query /tn "KB-notion-sync"
schtasks /delete /tn "KB-notion-sync" /f   # 마음에 안 들면 이렇게 하나씩 제거
```

## 실행 로그 확인
`pythonw.exe`는 콘솔이 없어 화면에 아무것도 안 보인다 — 대신 매 실행 결과가
`output/knowledge-agent/scheduler_logs/YYYYMMDD.log`에 남는다(실행 명령·stdout·stderr·종료 코드).
"진짜 도는지" 확인하고 싶으면 이 파일을 열어보면 된다.

## 주의
- `note-structurer` 작업은 `claude -p`(헤드리스 Claude Code)를 호출한다. PC가 꺼져 있거나 잠자기
  상태면 그 시각엔 실행되지 않는다(작업 스케줄러의 "다음에 켜졌을 때 놓친 작업 실행" 옵션을 켜면
  완화 가능 — `/RL HIGHEST`나 GUI의 "사용 가능해지면 즉시 실행" 체크박스).
- Windows 로그인이 안 돼 있으면(화면 잠금 등) 일부 작업이 안 돌 수 있다 — 실행 안 되면 작업
  스케줄러 GUI에서 "사용자가 로그온했는지 여부와 상관없이 실행"으로 바꿔야 할 수 있다.
