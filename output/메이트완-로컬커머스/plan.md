# Plan: 메이트완 로컬커머스

## 태스크 요약
메이트완(Matewan)의 로컬커머스 비즈니스 모델, 현황, 시장 환경 및 성장 전략을 분석하는 리서치 보고서를 작성합니다.
메이트완은 국내 오토바이 기반 라스트마일 배달 플랫폼인 '바로고'와 연계된 로컬커머스 서비스로, 지역 상점과 소비자를 연결하는 플랫폼입니다.

## 선택된 Task Type
- **Type**: `research-report` (default)
- **근거**: 사용자 요청에 별도 trigger 키워드 없음 → default 타입 적용. 업무 내용이 시장/비즈니스 리서치에 해당.
- **활성 멤버**: member-alpha · member-gamma · member-delta · member-beta

## 활성 멤버 목록
| 멤버 | 역할 | 산출물 |
|------|------|--------|
| member-alpha | 시장 조사 및 데이터 분석 | `member-alpha/analysis-report.md` |
| member-gamma | 팩트체크 (수치·출처 검증) | `member-gamma/fact-check-log.md` |
| member-delta | 시각화 (Mermaid·테이블) | `member-delta/visuals.md` |
| member-beta | 보고서 초안 작성 | `member-beta/draft-report.md` |

## 과제 배정

### member-alpha (1순위)
- **과제**: 메이트완 로컬커머스 개요, 비즈니스 모델, 시장 현황, 경쟁사 비교, 핵심 지표 분석
- **입력**: 없음 (독립 조사)
- **출력**: `member-alpha/analysis-report.md`

### member-gamma (2순위 — alpha 완료 후)
- **과제**: alpha 보고서의 수치, 출처, 날짜, 고유명사 팩트체크
- **입력**: `member-alpha/analysis-report.md`
- **출력**: `member-gamma/fact-check-log.md`

### member-delta (2순위 — alpha 완료 후, gamma와 병렬)
- **과제**: alpha 분석 기반 시각자료 (Mermaid 다이어그램 ≥2개, 핵심 수치 테이블)
- **입력**: `member-alpha/analysis-report.md`
- **출력**: `member-delta/visuals.md`

### member-beta (3순위 — alpha·gamma·delta 완료 후)
- **과제**: 모든 산출물을 통합해 최종 보고서 초안 작성
- **입력**: `member-alpha/analysis-report.md`, `member-gamma/fact-check-log.md`, `member-delta/visuals.md`
- **출력**: `member-beta/draft-report.md`

## 실행 순서 및 의존 관계

```
[member-alpha] 
    ↓
[member-gamma] [member-delta]  (병렬)
    ↓               ↓
         [member-beta]
              ↓
    [team-lead: 통합 → final]
```

## 검증 기준
- 모든 필수 섹션 포함 여부
- 논리적 정합성 및 중복/모순 없음
- 최종 산출물 형식 준수 (md)

---
_작성: team-lead | 2026-04-24_
