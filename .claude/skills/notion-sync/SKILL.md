# Notion Sync Skill

## Purpose
화이트리스트로 지정한 Notion DB/페이지에서 cursor 이후 변경분만 가져와 `00_Inbox`에 md로 쌓는다.
지식수집_구조화_에이전트_설계서.md 3-5/3-5-1절 결정사항의 구현.

## When to Use
Claude Code 내장 cron(예: 매 10~15분)이 이 스킬을 호출한다. 사람이 직접 호출할 일은 거의 없다 —
급하게 특정 페이지를 지금 당장 넣고 싶을 때만 수동 실행.

## 사용법
```bash
export NOTION_API_TOKEN=secret_xxx   # 이미 발급된 토큰 재사용(읽기 전용) — 지민님 확인 완료
python scripts/notion_pull.py --vault "<vault 절대경로>" --whitelist scripts/whitelist.json
```
`scripts/whitelist.json`은 `scripts/whitelist.example.json`을 복사해서 실제 페이지/데이터소스 id로
채운다(레포에는 example만 커밋).

## 동작 원리 (설계서 근거)
- **LLM 미사용**: 이 스크립트는 순수 코드다. 분류·태깅·요약은 하지 않는다 — 원문 그대로 저장(2-2절 ①,
  당초 slack-sync처럼 "요약"을 여기서 하면 안 된다는 교훈이 이미 한번 반영됨).
- **증분 수집**: `output/knowledge-agent/cursors/notion.json`에 `{page_id: last_edited_time}` 형태로
  cursor를 저장. 다음 실행 때 `last_edited_time`이 cursor 이후인 것만 가져온다.
- **cursor 전진 시점**: vault 쓰기까지 성공한 항목만 cursor에 반영한다. 쓰기 실패분은 다음 실행에서
  재시도된다(유실 방지, [2-3] 결정).
- **source_id**: 노트 frontmatter에 `notion:page-<id>`로 기록. note-structurer 배치가 이 값으로
  기존 노트를 찾아 갱신할지 신규 생성할지 판단한다([2-3] "소스 문서 업데이트/중복 방지" 결정).

## 재사용
Notion API 요청·블록→텍스트 변환은 새로 만들지 않고 `agent-team/scripts/notion_fetch.py`의 헬퍼
(`_request`, `_fetch_children`, `blocks_to_text`, `_title_of`)를 import해서 쓴다. 토큰만
`NOTION_API_TOKEN`(우리 조직, 읽기 전용 재사용)으로 다르다 — `notion_fetch.py`가 쓰는
`DEPT_NOTION_API_TOKEN`(다른 부서 워크스페이스용)과 혼용하지 않는다.

## 한계
- 화이트리스트가 아직 비어있다(`scripts/whitelist.json` 미생성) — 지민님이 실제 페이지/DB id를
  채워야 동작한다.
- Notion 표(table) 블록·이미지 등은 `notion_fetch.py`와 동일한 단순화 한계를 그대로 물려받는다.

## 셀프테스트
```bash
python scripts/notion_pull.py --selftest
```
