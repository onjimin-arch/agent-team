# File Watcher Skill

## Purpose
로컬 드롭 폴더를 짧은 주기로 폴링해 새 파일을 `00_Inbox`에 반영한다. `urls.txt` 류 파일은
web-clipper로 위임한다(설계서 3-5-1절).

## When to Use
Claude Code 내장 cron이 짧은 주기(예: 5분)로 호출한다. 드롭 폴더는 지민님이 파일을 직접 넣거나
URL 목록을 적어두는 용도다.

## 사용법
```bash
python scripts/watch_inbox.py --watch-dir "<드롭 폴더 절대경로>" --vault "<vault 절대경로>"
```
드롭 폴더 경로는 아직 확정되지 않았다 — 지민님이 원하는 위치를 정해서 CLAUDE.md의 cron 트리거
설정에 반영해야 한다.

## URL 목록 넣는 법
드롭 폴더에 `urls.txt`(또는 이름에 "url"이 들어간 .txt 파일)를 만들고 한 줄에 URL 하나씩 적는다.
다음 스캔 때 file-watcher가 감지해 각 URL을 `web-clipper`(`web_clip.clip_url`)로 넘긴다.

## 동작 원리
- **지원 포맷**: `.txt`/`.md`/`.csv`/`.log`/`.json`만 텍스트로 직접 읽는다. pdf/docx/이미지 OCR은
  범위 밖이다(설계서 5절 가정 7) — 만나면 `skipped(unsupported_format)`로 로그만 남기고, cursor에도
  기록하지 않아 나중에 포맷 지원이 추가되면 자동으로 다시 시도된다.
- **감지 방식**: OS 이벤트(inotify 등)나 `watchdog` 같은 신규 의존성 대신, 파일명+mtime을
  `output/knowledge-agent/cursors/`에 기록해두고 폴링마다 비교한다 — 폴링 주기 안에서는 실시간이
  아니지만 신규 의존성 없이 stdlib만으로 충분하다.
- **source_id**: `file:<절대경로 sha1 해시>`. 같은 파일을 다시 수정해서 저장하면 mtime이 바뀌어
  재수집되고, note-structurer가 source_id로 기존 노트를 찾아 갱신한다.

## 셀프테스트
```bash
python scripts/watch_inbox.py --selftest
```
