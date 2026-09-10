# Slack Sync Skill

## Purpose
지정 채널에서 "결정됨"/"공유됨" 리액션이 달린 메시지만 cursor 이후로 골라 `00_Inbox`에 원문 그대로
저장한다. 지식수집_구조화_에이전트_설계서.md 3-5/3-5-1절.

## When to Use
Claude Code 내장 cron이 주기적으로 호출한다.

## 사용법
```bash
export SLACK_BOT_TOKEN=xoxb-...   # agent-team과 동일한 토큰 재사용 — 지민님 확인 완료
python scripts/slack_pull.py --vault "<vault 절대경로>" --config scripts/filter_config.json
```
`scripts/filter_config.json`은 `scripts/filter_config.example.json`을 복사해서 실채널/리액션으로 채운다.

## 필터 기준 — 확정 아님
"결정됨"/"공유됨" 태그는 **리액션 이모지**(`:결정:`, `:공유:` 등)로 구현했다. 이것은 가정이며 실제
팀이 저 이름의 이모지를 쓰는지, 아니면 메시지 텍스트 접두어("[결정]" 등) 방식을 쓰는지 확인이
필요하다(설계서 5절 가정 3, 미해소). 텍스트 접두어 방식으로 바뀌면 `message_matches_tags()`만
고치면 된다.

## 동작 원리
- **요약 안 함**: 이 스크립트는 원문을 그대로 저장한다. 요약은 note-structurer(LLM 배치)의 몫이다 —
  당초 여기서 요약하는 설계였다가 "①은 LLM 미사용" 원칙과 모순돼 정정된 이력이 있다(2-2절).
  같은 실수를 반복하지 않도록 이 스킬에 판단 로직을 넣지 않는다.
- **cursor**: 채널별 마지막 조회 `ts`를 `output/knowledge-agent/cursors/slack.json`에 저장. 태그
  안 붙은 메시지도 훑은 시점까지는 cursor를 전진시켜 같은 메시지를 매번 다시 스캔하지 않는다. 단,
  실제로 Inbox에 쓴 메시지 기준으로는 쓰기 성공분만 반영한다([2-3] 결정).
- **source_id**: `slack:<channel>:<ts>` 형식으로 frontmatter에 기록.

## 재사용
Slack Web API 호출은 `agent-team/scripts/slack_publish.py`의 `_call_get`/`resolve_channel_id`를
그대로 가져다 쓴다 — 채널명→ID 변환, 페이지네이션, 에러 처리를 새로 만들지 않는다.

## 셀프테스트
```bash
python scripts/slack_pull.py --selftest
```
