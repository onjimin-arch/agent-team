# vault frontmatter 스키마 (지식수집·구조화 에이전트)

지식수집_구조화_에이전트_설계서.md 3-8절 근거. `00_Inbox`~`04_Permanent`(vault 루트, 신규 생성)
아래 노트에만 적용된다 — 기존 `경영전략실_지식베이스`의 9개 파일은 frontmatter가 없는 별개 문서라
이 스키마와 무관(섞어 쓰지 않음, 확인 완료 2026-08-12).

## 폴더 구조 (PARA 변형)
- `00_Inbox` — 수집 스킬이 원문을 그대로 떨어뜨리는 곳. `status: pending`으로 시작.
- `01_Projects` / `02_Areas` / `03_Resources` / `04_Permanent` — note-structurer가 배정하는 목적지.
  (이름은 표준 PARA 방법론 차용 — 설계서에 명시되지 않아 임의 결정, 마음에 안 들면 폴더명만
  바꾸면 됨. note-structurer의 목적지 후보 로직도 이 4개 이름을 참조하므로 바꿀 경우 같이 수정)

## frontmatter 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `source` | string | O | `notion` / `slack` / `file` / `web` |
| `source_id` | string | O | 원문 재수집 시 기존 노트를 찾는 키. 예: `notion:page-abc123`, `slack:C0123:1699999999.000100`, `file:<절대경로 해시>`, `web:<url>` |
| `date` | string (ISO8601) | O | 수집 시각 |
| `raw` | boolean | O | ①수집 단계 산출물이면 `true`, ②구조화를 거치면 `false`로 내림 |
| `status` | string | O | `pending` \| `done` — idempotency/재처리/review_needed 재통합에 사용 ([2-3] 참고) |
| `project` | string | X | note-structurer가 판단해 채움. 없으면 생략 |
| `tags` | string[] | X | note-structurer가 자유 생성 + 태그 유사도 검토를 거쳐 채움 |
| `related` | string[] (wikilink) | X | 링크 후보가 있을 때만. 없어도 통과(강제 아님) |
| `review_needed` | boolean | X | 에스컬레이션된 노트에만 존재. 사람이 확인 후 태그(필드)만 지우면 `status: pending`이 남아 다음 배치가 자동 재처리 |

## 예시
```markdown
---
source: notion
source_id: notion:page-abc123
date: 2026-08-12T09:10:00+00:00
raw: false
status: done
project: AX 인프라 자동화
tags: ["ax", "n8n"]
related: ["[[01_AX_인프라_자동화]]"]
---

[사실] ...본문...
```

## 본문 마킹 규칙
설계서 용어 정의에 따라 본문 문장 단위로 `[사실]`/`[분석]`/`[제언]`을 붙인다(frontmatter 필드 아님,
지식수집_구조화_에이전트_설계서.md 자체가 이미 이 표기를 쓰고 있어 동일 관례를 따름).
