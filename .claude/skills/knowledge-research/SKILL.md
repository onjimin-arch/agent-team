# Knowledge Research Skill

## Purpose
특정 topic에 대해 즉시 웹 리서치 + vault 검색을 종합해 출처 명시된 요약 노트를 생성한다. 격리된
임시 서브에이전트가 실제 리서치를 수행한다(고정 멤버 AGENT.md 없음 — 설계서 3-1/3-3절 결정).

## When to Use
`knowledge-query`로 vault를 먼저 찾아봤는데 관련 노트가 없거나 부족할 때만 호출한다. 고비용(LLM
호출)이고 일 단위 quota 하드캡이 있다 — quota 초과 시 즉시 거부된다.

## 절차

1. **quota 확인**: `python scripts/knowledge_research.py check-quota --daily-limit <N>`
   `{"allowed": false, "error": "quota_exceeded"}`면 여기서 멈추고 호출한 멤버에게 "오늘 리서치
   quota 소진, 내일 다시 시도하거나 다른 방법을 쓰라"고 응답한다. daily-limit 값은 CLAUDE.md의
   설정에서 가져온다(아직 미정 — 지민님이 정해야 함, README 참고).

2. **격리된 리서치 서브에이전트 기동** — agent-team CLAUDE.md 391~417줄의 "방법 B"(Agent 도구,
   `subagent_type: "general-purpose"`, cold-start로 자동 격리)를 그대로 따른다. 프롬프트에는
   아래 역할 설명 + topic + urgency만 넣는다(팀장의 대화 맥락은 넣지 않음 — 넣을 필요도 없다):

   ```
   당신은 지식 리서치 담당입니다. topic: "{topic}" (urgency: {urgency})에 대해 웹 리서치와
   vault 검색(knowledge-query 스킬 사용 가능)을 종합해 출처가 명시된 요약을 작성하세요.

   원칙(agent-team/.claude/skills/shared/web-research/SKILL.md와 동일):
   - 모든 항목에 출처명·날짜·URL을 기록한다.
   - 숫자·날짜·사실 주장에는 확신 수준(확인됨/추정/확인 필요)을 표시한다.
   - 단일 미검증 출처를 확정 사실처럼 쓰지 않는다.
   - 출처 신뢰도 등급화는 하지 않는다. 여러 출처가 상충하면 어느 쪽이 맞는지 판단하지 말고
     "출처 간 상충 있음"만 기록한다.
   - 소스에 없는 내용을 배경지식으로 채우지 않는다.

   출력: {"topic": str, "body": "[사실]/[분석] 마킹된 요약 본문", "sources": [url, ...],
          "has_conflicting_sources": bool} 형식의 JSON.
   ```

3. **vault 반영**: 서브에이전트가 반환한 JSON을 파일로 저장한 뒤
   `python scripts/knowledge_research.py finalize --vault <vault> --draft-file <draft.json>`
   → 초안을 `output/knowledge-agent/research_drafts/`에 보관하고, `03_Resources`에 정식 노트로
   반영한다. 목적지는 항상 `03_Resources`로 고정한다(리서치 결과는 정의상 참고자료 — [3-6] 결정,
   note-structurer처럼 목적지 후보를 여러 개 판단할 필요가 없어 단순화함).

4. 호출한 멤버에게는 `finalize` 응답의 `path`(노트 경로)와 `summary`(본문 앞부분)만 인라인으로
   전달한다 — 전문은 필요하면 그 경로로 직접 읽게 한다.

## 절대 하지 말 것
- quota 확인 없이 서브에이전트부터 기동하지 않는다(하드캡을 우회하게 됨).
- `knowledge-research`를 직접 여러 멤버가 각자 호출하게 두지 않는다 — CLAUDE.md에 "이 스킬 경유만
  허용, researcher를 직접 Agent 도구로 즉흥 기동하지 말 것"을 명시해야 한다(3-2절 결정).

## 셀프테스트 (quota/파일 저장 로직만)
```bash
python scripts/knowledge_research.py --selftest
```
