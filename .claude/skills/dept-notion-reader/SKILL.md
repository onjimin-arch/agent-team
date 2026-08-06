# Dept Notion Reader Skill

## Purpose
member-alpha가 **다른 부서의 Notion 워크스페이스**(우리 조직 자체 Notion과는 별개)에서 데이터를
읽어와 분석에 활용하는 데 필요한 명령 레퍼런스와 인용 원칙을 제공한다.

## When to Use
Team Lead가 부서 Notion 조회가 필요한 assignment를 줄 때만 사용한다. 스스로 판단해 먼저 조회하지 않는다.

## 토큰 주의사항
이 스킬이 사용하는 `DEPT_NOTION_API_TOKEN`은 Phase 5 배포에 쓰는 `NOTION_API_TOKEN`(우리 조직 Notion,
쓰기 전용)과 **완전히 다른 워크스페이스, 다른 토큰**이다. 절대 혼용하지 않는다 — 잘못된 토큰으로
호출하면 엉뚱한 워크스페이스에 접근하거나 권한 오류가 난다.

## 명령 레퍼런스

```bash
# 키워드로 페이지/데이터베이스 검색
python scripts/notion_fetch.py --search "<키워드>"

# 특정 페이지 내용 조회 (본문 블록을 markdown 유사 텍스트로 변환해 반환)
python scripts/notion_fetch.py --page-id <page-id>

# 데이터소스(데이터베이스) 조회, 선택적으로 Notion filter 객체(JSON) 전달
python scripts/notion_fetch.py --data-source-id <data-source-id> [--filter '<json>']
```

모든 호출은 `{"success": bool, "source_url": ..., "fetched_at": "<ISO8601>", "content": ...}` 형태의
JSON을 stdout에 출력한다. `success: false`면 `error`/`hint` 필드를 확인하고, 토큰 미설정 등 설정
문제면 Team Lead에 그대로 보고한다.

## 인용 원칙
- 조회 결과를 분석 결과에 사용할 때는 **`source_url`과 `fetched_at`을 반드시 함께 인용**한다 —
  이 데이터가 언제 어느 페이지에서 온 것인지 항상 추적 가능해야 한다.
- 조회한 원문과 alpha 자신의 해석·분석을 명확히 구분해서 기술한다(원문 그대로 인용 vs 해석 문장을
  섞어 쓰지 않는다).
- 조회에 실패했거나 페이지가 비어 있으면 "조회 실패" 또는 "내용 없음"으로 명시하고, 내용을 지어내지 않는다.
- 조회된 수치·통계에 확신 수준이 불명확하면(오래된 데이터, 부분 조회 등) "추정"으로 명시하고,
  조회되지 않은 항목을 알고 있는 배경지식으로 채우지 않는다.

## 한계 (의도적 단순화)
`notion_publish.py`의 쓰기 변환과 대칭적으로, 읽기 쪽도 완벽한 렌더링이 아니라 최소 신뢰성이 목적이다:
- 표(table) 블록은 셀 텍스트를 `|`로 이어붙인 plain text로만 변환한다.
- 이미지·임베드·synced block 등 텍스트가 아닌 블록은 `[지원되지 않는 블록: {type}]`으로 표시하고 건너뛴다.
- 블록 자식은 1단계까지만 재귀 조회한다. 더 깊은 중첩이 필요하면 Team Lead에 보고한다.
