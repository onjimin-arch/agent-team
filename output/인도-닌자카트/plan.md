# Plan: 인도 닌자카트 조사

## 태스크 요약
인도 애그리테크 스타트업 Ninjacart(닌자카트)에 대한 종합 리서치 보고서 작성.
창업 배경, 비즈니스 모델, 시장 위치, 재무 현황, 주요 경쟁사 비교, 향후 전망을 분석합니다.

## 선택된 Task Type
- **Type**: `research-report` (default)
- **근거**: "조사"는 리서치/분석 보고서 유형에 해당; default type 적용
- **활성 멤버**: member-alpha · member-gamma · member-delta · member-beta

## 활성 멤버 목록
| 멤버 | 역할 |
|---|---|
| member-alpha | 시장 조사 및 데이터 분석 |
| member-gamma | 팩트체커 (수치·출처 검증) |
| member-delta | 시각화 (Mermaid/테이블) |
| member-beta | 최종 보고서 초안 작성 |

## 업무 배정

### member-alpha (1순위)
- 닌자카트 기업 개요 및 창업 배경 조사
- 비즈니스 모델 및 수익 구조 분석
- 인도 애그리테크 시장 현황 및 닌자카트 포지셔닝
- 투자 유치 내역 및 주요 투자자
- 경쟁사 비교 분석 (WayCool, DeHaat, Agrimart 등)
- 산출물: `output/인도-닌자카트/member-alpha/analysis-report.md`

### member-gamma (2순위, alpha 산출물 의존)
- member-alpha 수치·주장 팩트체크
- 투자 금액, 창업연도, 창업자 이름, 시장 규모 등 검증
- 산출물: `output/인도-닌자카트/member-gamma/fact-check-log.md`

### member-delta (2순위, alpha 산출물 의존)
- 닌자카트 비즈니스 모델 구조도 (Mermaid flowchart)
- 인도 애그리테크 경쟁사 비교 테이블
- 투자 라운드 타임라인 (Mermaid timeline/gantt)
- 산출물: `output/인도-닌자카트/member-delta/visuals.md`

### member-beta (3순위, alpha·gamma·delta 산출물 의존)
- 전체 조사 결과를 보고서로 통합
- 핵심 인사이트 및 추천 사항 작성
- 산출물: `output/인도-닌자카트/member-beta/draft-report.md`

## 실행 순서 및 의존성 맵
```
member-alpha (독립 실행)
    ↓
member-gamma (alpha 완료 후)
member-delta (alpha 완료 후, gamma와 병렬)
    ↓
member-beta (alpha + gamma + delta 완료 후)
    ↓
팀장 통합 → final-artifact.md
```

## 최종 산출물 경로
`output/인도-닌자카트/final/final-artifact.md`
