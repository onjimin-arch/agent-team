# Note Structurer Skill

## Purpose
`00_Inbox`의 원자료를 분류·태깅·요약해서 `01_Projects`~`04_Permanent`로 배정한다. 지식수집_구조화_
에이전트_설계서.md 2-2/2-3절의 핵심 — 이 스킬을 쓸 때는 **메인 에이전트(너 자신)가 직접 판단**해야
한다. 분류·태깅·요약·민감정보 판단은 스크립트가 아니라 네가 하는 일이다.

## When to Use
Claude Code 내장 cron이 1일 1~2회, 또는 `00_Inbox` 누적량이 threshold를 넘으면 호출한다.

## 절차 (반드시 이 순서로)

1. **락 획득**: `python scripts/note_structurer.py acquire-lock --vault <vault>`
   (다른 멤버의 knowledge-query/knowledge-research가 배치 중 충돌하지 않도록 — [2-3] 결정)

2. **대기 목록 조회**: `python scripts/note_structurer.py list-pending --vault <vault>`
   → `status: pending`인 Inbox 노트 목록(JSON)이 나온다.

3. **각 노트마다 네가 직접 판단**한다 (스크립트가 아니라 너):
   - `references/classification-rules.md`를 참고해 목적지 폴더 후보를 정한다. **후보가 정확히
     하나로 좁혀지지 않으면 여러 개를 그대로 `destination_candidates`에 넣는다** — 억지로 하나를
     고르지 않는다. 그래야 스크립트의 규칙 기반 필터가 동률을 감지해 에스컬레이션한다.
   - 태그를 자유롭게 생성한다 (기존 태그와의 유사도 병합은 스크립트가 자동으로 함 — 신경 쓰지 않아도 됨).
   - 본문에 `[사실]`/`[분석]`/`[제언]` 마킹을 적용한 최종 본문을 작성한다. Slack/Notion 원문이 길면
     이 단계에서 요약한다(수집 단계는 요약하지 않았으므로 여기가 요약을 하는 유일한 지점).
   - 링크 후보가 있으면 `related`에 wikilink로 넣는다 — **없으면 그냥 빈 배열로 둔다(강제 아님)**.
   - 민감정보(인사평가·급여·타인의 민감한 발언 등)로 보이면 `sensitive_flag: true`로 표시한다.
   - 판단 근거를 `reasoning`에 한두 문장으로 적는다 — 에스컬레이션되면 이 텍스트가 그대로
     `review_needed` 노트에 남아 사람이 읽는다.
   - 이 모든 걸 담은 decision JSON을 임시 파일로 저장한다.

4. **완료 처리**: `python scripts/note_structurer.py finalize --vault <vault> --decision-file <decision.json>`
   → 스크립트가 나머지를 전부 처리한다: 태그 유사도 병합, 에스컬레이션 규칙 판정(2개 이상 동률/태그
   없음/원문 30자 미만/민감정보 의심 중 하나라도 해당하면 자동으로 `review_needed`), source_id 중복
   확인(같은 원문이 이미 구조화돼 있으면 새로 만들지 않고 그 노트를 갱신), 폴더 이동, frontmatter 기록.

5. 모든 노트 처리 후 **로그 기록 + 락 해제**:
   `python scripts/note_structurer.py release-lock --vault <vault>`

## 절대 하지 말 것
- destination_candidates를 억지로 1개로 좁혀서 에스컬레이션을 피하지 않는다 — 그러면 규칙 기반
  필터가 무력화된다.
- decision.body에 원문에 없는 내용을 지어내지 않는다(요약이지 창작이 아니다).
- finalize 호출 없이 파일을 직접 옮기거나 편집하지 않는다 — source_id 중복 병합·태그 유사도 병합이
  스크립트에만 있다.

## 참고 문서
- `references/classification-rules.md` — 목적지 폴더 4개의 정의와 판단 기준

## 셀프테스트 (스크립트 로직만, LLM 판단 없이)
```bash
python scripts/note_structurer.py --selftest
```
