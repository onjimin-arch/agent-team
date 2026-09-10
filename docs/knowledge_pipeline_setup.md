# 지식 수집·구조화 파이프라인 — 설치 체크리스트

코드는 다 만들어졌지만, 아래는 지민님이 직접 해야 하는 것들이다(제가 자동으로 못 하거나, 안 하는
게 맞는 것들). 지식수집_구조화_에이전트_설계서.md 5절 "확인이 필요한 가정"과 연결됨.

## 1. 환경변수
```
NOTION_API_TOKEN=...   # 이미 발급된 토큰 재사용(읽기 전용) — agent-team의 다른 스크립트와 공유
SLACK_BOT_TOKEN=...    # 이미 발급된 토큰 재사용 — 마찬가지로 공유
```

## 2. 설정 파일 채우기 (example를 복사해서 실제 값 입력)
- `.claude/skills/notion-sync/scripts/whitelist.json` ← `whitelist.example.json` 복사
  → 실제로 수집할 Notion 페이지/데이터소스 id 채우기
- `.claude/skills/slack-sync/scripts/filter_config.json` ← `filter_config.example.json` 복사
  → 실제 채널, 리액션 태그(또는 다른 필터 방식으로 교체) 채우기

## 3. 값 확정 필요 (아직 코드에 하드코딩 안 함, 설계서 5절 미해소 항목)
- `knowledge-research` 일일 quota 숫자 (`check-quota --daily-limit N`의 N)
- `note-structurer` 배치 주기 ("1일 1~2회" 중 실제 몇 회, 몇 시)
- `file-watcher` 드롭 폴더 경로
- Slack "결정됨"/"공유됨" 필터가 실제 이모지 리액션 이름과 맞는지 (`slack-sync/SKILL.md` 참고)

## 4. 배치 스케줄 등록 (Windows 작업 스케줄러)
2026-08-13 확정: Claude Code 내장 cron 대신 **Windows 작업 스케줄러**에 각 스크립트를 직접 등록하는
방식으로 진행 중 (지민님이 vault 폴더 쪽에서 직접 작업). 아래를 등록해야 실제로 동작을 시작한다:
- `notion-sync` (`notion_pull.py`), `slack-sync` (`slack_pull.py`): 10~15분 주기
- `file-watcher` (`watch_inbox.py`): 5분 내외
- `note-structurer` (`note_structurer.py`): 1일 1~2회 (위 3번 시각 확정 후)

등록한 실행 시각은 `config/knowledge_pipeline.json`의 `batch_times`와 맞춰둘 것. **`schedule` 스킬/
`CronCreate`로 같은 작업을 중복 등록하지 않는다** — 두 스케줄러가 동시에 돌면 vault에 중복 노트가
쌓인다.

## 5. Smart Connections(또는 동급) Obsidian 플러그인 설치
지민님이 Obsidian 커뮤니티 플러그인 브라우저에서 직접 설치하는 걸 권장한다(외부 플러그인 코드를
제가 vault에 직접 심는 것보다 공식 채널이 안전함). 설치되면 그 임베딩 인덱스 포맷을 확인해
`knowledge-query/scripts/knowledge_query.py`의 `rerank_by_embedding()`을 채워 넣을 예정이다.
그 전까지 `knowledge-query`는 키워드 검색만으로 동작한다(빈 결과보다는 낫다는 판단, 가짜 유사도는
지어내지 않음).

## 6. 기존 지식베이스(`경영전략실_지식베이스`, 9개 파일) 이관
"(C) 구조만 먼저 설계하고 이관은 나중에"로 결정됨(2026-08-12). `scripts/migrate_existing_kb.py`가
준비돼 있고 실제 vault 대상 dry-run까지 확인했다(48개 섹션 감지, 원본 파일 미변경). 이관하고 싶을
때:
```bash
python scripts/migrate_existing_kb.py --vault "<vault>" --kb-dir "<vault>/경영전략실_지식베이스"
# 위 계획 출력을 검토한 뒤에만
python scripts/migrate_existing_kb.py --vault "<vault>" --kb-dir "<vault>/경영전략실_지식베이스" --execute
```
`--execute` 뒤에는 `00_Inbox`에 48개 raw 노트가 생기고, note-structurer 배치가 돌면서 각각을
분류·에스컬레이션한다 — 애매한 것들은 `review_needed`로 빠지니 `_지식수집_검토대기.md`(vault 루트)
를 열어 확인하면 된다. 원본 9개 파일은 이 스크립트가 절대 건드리지 않는다(삭제는 지민님이 결과를
보고 나서 판단).

## 7. 다 됐는지 한 번에 확인
```bash
for s in shared/knowledge-lib notion-sync slack-sync web-clipper file-watcher note-structurer knowledge-query knowledge-research; do
  echo "== $s =="
done
python .claude/skills/shared/knowledge-lib/scripts/kb_lib.py --selftest
python .claude/skills/notion-sync/scripts/notion_pull.py --selftest
python .claude/skills/slack-sync/scripts/slack_pull.py --selftest
python .claude/skills/web-clipper/scripts/web_clip.py --selftest
python .claude/skills/file-watcher/scripts/watch_inbox.py --selftest
python .claude/skills/note-structurer/scripts/note_structurer.py --selftest
python .claude/skills/knowledge-query/scripts/knowledge_query.py --selftest
python .claude/skills/knowledge-research/scripts/knowledge_research.py --selftest
python scripts/migrate_existing_kb.py --selftest
```
전부 `OK: ... selftest passed`가 나와야 한다(2026-08-12 구현 시점에 전부 통과 확인함).
