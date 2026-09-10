# Web Clipper Skill

## Purpose
URL 하나를 md로 변환해 `00_Inbox`에 저장한다. robots.txt를 최소 확인해 차단 사이트는 자동 배제한다.

## When to Use
직접 호출하지 않는다. 두 경로로만 트리거된다(설계서 3-5-1 결정 — 별도 URL 제출 기능 없음):
1. `knowledge-research`가 리서치 중 스스로 찾은 URL을 처리할 때
2. `file-watcher`가 드롭 폴더의 `urls.txt`를 감지해 넘길 때

## 사용법
```bash
python scripts/web_clip.py --url https://example.com --vault "<vault 절대경로>"
```
다른 스킬에서는 CLI 대신 `clip_url(url, vault_path)` 함수를 직접 import해서 쓰는 걸 권장한다
(file-watcher가 이렇게 한다 — 매 URL마다 프로세스를 새로 띄우지 않음).

## 출처 원칙
`shared/web-research/SKILL.md`의 원칙(출처·날짜·URL 인용, 단일 출처 미검증 사실로 단정 금지)을 그대로
따른다. 출처 신뢰도 등급화(공식 문서 vs 블로그 등)는 이번 범위에서 하지 않는다 — researcher가 여러
출처를 종합할 때 상충 여부만 노트에 기록한다([3-6] 결정).

## 한계
- HTML→텍스트 변환은 `html.parser` 기반 손수 태그 스트리퍼다. 레이아웃·표·이미지는 버려지고 본문
  텍스트만 남는다 — 복잡한 SPA(JS로 렌더링되는 페이지)는 빈 본문이 나올 수 있다.
- robots.txt를 못 읽으면(네트워크 오류 등) 차단 근거가 없다고 보고 허용한다 — 완벽한 준수가 아니라
  "최소 확인"이다(설계서 3-5 결정 문구 그대로).

## 셀프테스트
```bash
python scripts/web_clip.py --selftest
```
