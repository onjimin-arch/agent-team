# Shared Knowledge Lib

## Purpose
`notion-sync`/`slack-sync`/`file-watcher`/`web-clipper`/`note-structurer`/`knowledge-query`/`knowledge-research`가
공통으로 쓰는 순수 stdlib Python 유틸(`scripts/kb_lib.py`) — frontmatter 파싱, cursor 파일, 락 판정,
quota 카운터, 태그 유사도. 지식수집_구조화_에이전트_설계서.md의 2-3/3-5-1절 결정사항을 코드로 구현한 것.

## When to Use
지식수집 관련 스킬 스크립트를 작성/수정할 때 이 모듈을 import 해서 쓴다. 각 스킬이 개별적으로
frontmatter 파서나 cursor 로직을 다시 구현하지 않는다.

## 사용법
```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared" / "knowledge-lib" / "scripts"))
import kb_lib
```

## 셀프테스트
```bash
python .claude/skills/shared/knowledge-lib/scripts/kb_lib.py --selftest
```

## 한계 (의도적 단순화)
- `parse_frontmatter`/`write_frontmatter`는 범용 YAML이 아니라 이 프로젝트의 frontmatter 필드
  (`source`,`source_id`,`date`,`tags`,`status`,`raw` 등: 문자열/문자열 리스트/불리언만)만 다루는
  손수 작성한 파서다. 중첩 객체나 멀티라인 값이 들어오면 깨진다 — 필요해지면 `pyyaml` 도입.
- `tag_similarity`는 아직 실제 임베딩이 없어 `difflib.SequenceMatcher` 기반 문자열 유사도로
  대체돼 있다 — 오탈자/표기 차이는 잡지만 "AI"/"인공지능" 같은 동의어는 못 잡는다. Smart Connections
  플러그인 설치 후 그 임베딩 인덱스를 읽어 `cosine_similarity`로 교체 예정([`docs/vault_schema.md`](../../../../docs/vault_schema.md) 참고).
