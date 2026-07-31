# 2026-07-29 정리 보관함

전수 점검 세션 중 더 이상 사용하지 않기로 한 파일들을 삭제 대신 여기로 옮겨둔 것입니다.
문제없다고 판단되면 폴더째 지워도 됩니다.

| 파일 | 원래 위치 | 옮긴 이유 |
|---|---|---|
| `slack-bridge-nul.txt` | `slack-bridge/nul` | `git ... > nul` 명령이 잘못된 작업 디렉터리에서 실행되며 생긴 잔재 파일. 내용은 git 에러 메시지 텍스트뿐. |
| `slack-bridge-output/` | `slack-bridge/output/` | 2026-07-28 `2026-배달-시장-점유율-분석해줘` 워크스페이스 실행 중 opencode 서브프로세스가 원인불명으로 조기 종료됐을 때, 작업 디렉터리가 잘못 잡혀 `output/` 대신 여기에 미완성 초안이 저장된 것. 완전한 최종본은 `output/2026-배달-시장-점유율-분석해줘/`에 이미 있음(내용 비교로 확인됨, 중복·구버전). |
| `app-B-jmlee-N2.py` | `slack-bridge/app-B-jmlee-N2.py` | 메인 봇(`app.py`)과는 **다른 Slack 앱/봇 토큰**을 쓰는 별도 브릿지 사본(해시 비교로 토큰이 다름을 확인). 이 PC의 실제 예약 작업(`AgentTeam-SlackBridge`)은 이걸 실행하는 게 아니라 `app.py`를 실행하도록 되어 있었고, 세션 중 발견한 "app.py 프로세스 중복 실행" 문제의 원인은 아니었지만 용도가 불명확해 정리 대상으로 분류. |
| `-B-jmlee-N2.env` | `slack-bridge/-B-jmlee-N2.env` | 위 `app-B-jmlee-N2.py` 전용 환경설정. 별도의 실제 Slack 봇 토큰을 담고 있음 — 복구 필요 시 이 값을 그대로 쓰면 됨. |
| `output-B-jmlee-N2.active-workspace` | `output/-B-jmlee-N2.active-workspace` | 위 `app-B-jmlee-N2.py` 가 자신의 활성 워크스페이스로 추적하던 포인터 파일(마지막 값: `방식-영어-퀴즈-게임-개발`). |
| `start-bridge.bat` / `start-bridge.ps1` | `slack-bridge/` | 단발성 수동 실행 스크립트. `run-forever.ps1`(무한 자동 재시작 감시 스크립트)로 대체됨. |
| `install-service.ps1` | 저장소 루트 | `app-B-jmlee-N2.py`를 작업 스케줄러에 등록하는 스크립트였는데, 그 대상 파일이 위로 옮겨져 더 이상 유효하지 않음. `slack-bridge/register-always-on-task.ps1`(app.py 를 등록)로 대체됨. |

## 복구하려면
그냥 원래 경로로 다시 옮기면 됩니다. `.env`류 파일은 `.gitignore`의 `*.env` 규칙에 걸려 어차피 git에는 안 올라갑니다.
