# 2026 세제개편안 부가가치세 조사 — 실행 계획

자동 확정된 slug: 2026-세제개편안-부가가치세

Phase 0 판별: task_pipeline — quick_query trigger 매칭 없음, 단순 수치 조회가 아니라 정책 조사 요청

## Task Summary
**업무 설명**: `2026 세제개편안` 중 부가가치세 조사  
**사용자 요청**: 2026 세제개편안에서 부가가치세 관련 개정안을 조사하고 산출물로 정리

## Task Type 판별

| Type | Score | 매칭 키워드 |
|------|-------|-------------|
| **research-report** | **0/7 (0.000)** | - |
| code-review | 0/5 | - |
| multilingual-brief | 0/6 | - |
| dev | 0/10 | - |
| design | 0/8 | - |
| github-plan | 0/7 | - |
| ir-relations | 0/9 | - |
| gr-policy | 0/9 | - |
| pr-crisis | 0/9 | - |
| mgmt-planning | 0/8 | - |
| strategy-newbiz | 0/8 | - |

**선택**: `research-report`

**선택 근거**: 모든 type score 가 0이므로 `default: true` 인 `research-report` 선택

## 활성 멤버 목록
alpha(조사) · gamma(팩트체크) · delta(시각화) · beta(보고서)

## 재사용 체크
- 유사 slug: 없음
- 기존 final-artifact 재사용: 해당 없음

## Assignments

### 1. member-gamma(팩트체크)
- **의존성**: 없음
- **지시**: 2026년 세제개편안 부가가치세 항목을 공식/준공식 출처로 교차 검증
- **산출물**: `output/2026-세제개편안-부가가치세/member-gamma/fact-check-log.md`
- **필수 섹션**: 검증 요약, 항목별 검증 결과, 수정 권고

### 2. member-alpha(조사)
- **의존성**: gamma 산출물
- **지시**: gamma 검증 결과를 바탕으로 부가가치세 개정안의 구조, 영향도, 시행 시점을 분석
- **산출물**: `output/2026-세제개편안-부가가치세/member-alpha/analysis-report.md`
- **필수 섹션**: 개요, 분석 결과, 결론

### 3. member-delta(시각화)
- **의존성**: alpha 산출물
- **지시**: 개정 항목, 시행 시기, 영향도 비교를 표와 Mermaid 다이어그램으로 정리
- **산출물**: `output/2026-세제개편안-부가가치세/member-delta/visuals.md`
- **필수 섹션**: 시각자료 개요, Mermaid 다이어그램, 핵심 수치 테이블

### 4. member-beta(보고서)
- **의존성**: alpha, delta 산출물
- **지시**: 정책 검토용 보고서 초안을 작성하되, 경영진이 바로 읽을 수 있게 핵심 인사이트와 대응 권고를 요약
- **산출물**: `output/2026-세제개편안-부가가치세/member-beta/draft-report.md`
- **필수 섹션**: 요약, 핵심 인사이트, 추천 사항

## Execution Order
```
1. member-gamma(팩트체크)
   ↓
2. member-alpha(조사)
   ↓
3. member-delta(시각화)
   ↓
4. member-beta(보고서)
```

## Dependency Map
```
gamma -> alpha -> delta -> beta
                 \-------> beta
```

## Validation
- 모든 활성 멤버에게 1개 이상 assignment 배정: OK
- 의존성 순환 없음: OK
- expected output 명확성: OK

자동 확정 후 Phase 2 진입: 2026-08-10 10:29
