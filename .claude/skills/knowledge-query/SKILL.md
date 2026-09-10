# Knowledge Query Skill

## Purpose
vault(`01_Projects`~`04_Permanent`)를 파일시스템에서 직접 검색한다. Obsidian이 꺼져 있어도 항상
동작한다(설계서 3-1절 — 조회 경로는 Obsidian 상시 실행 전제에서 제외됨). 신규 노트를 만들지 않는다.

## When to Use
어떤 멤버든 작업 중 vault에 관련 정보가 있는지 확인하고 싶을 때 직접 호출한다. 특히 조사/리서치
계열 멤버(alpha 등)는 웹 리서치나 `knowledge-research`를 쓰기 **전에 먼저 이걸 호출**해서 이미
vault에 있는 정보인지 확인하는 걸 권장한다(중복 리서치 방지, quota 절약).

## 사용법
```bash
python scripts/knowledge_query.py --vault "<vault 절대경로>" --query "검색어" --max-results 5
```
반환값은 관련 문단 발췌 + 노트 경로다. **전문이 필요하면 그 경로를 직접 Read로 열어라** — 발췌만으로
충분한 경우가 대부분이고, 매번 전문을 다 받으면 토큰 낭비다.

## 동작 원리
- 키워드 매칭(제목/태그/본문) 후 점수순 정렬. "하이브리드: 필터→임베딩 재순위" 중 임베딩 재순위
  단계는 아직 미구현이다(`rerank_by_embedding()`이 현재는 통과만 시킴) — Smart Connections 플러그인
  설치·조사가 끝나면 채워진다(설계서 5절 가정 4, 미해소). 그때까지는 키워드 검색만 동작한다.
- note-structurer 배치가 돌고 있으면 최대 30초 폴링 대기 후, 안 풀리면 `vault_busy`를 반환한다.
  그러면 잠시 후 다시 호출하면 된다([2-3] 락 판정 결정).

## 셀프테스트
```bash
python scripts/knowledge_query.py --selftest
```
