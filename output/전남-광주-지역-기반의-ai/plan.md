# 플랜: 전남·광주 지역 기반 AI·로보틱스·물류 파트너사 조사

## 업무 요약
전라남도 및 광주광역시를 기반으로 활동하는 AI, 로보틱스, 물류 관련 기업·기관을 조사하여, 잠재 파트너사 목록과 각 사의 역량·현황을 정리한 리서치 보고서를 작성한다.

---

## 선택된 Task Type
- **Type**: `research-report` (default)
- **근거**: 명시적 trigger 키워드("리서치", "분석", "보고서" 등) 미매칭 → default 적용. 업무 성격상 현황 조사·분석 보고서 유형.
- **활성 멤버**: member-alpha · member-gamma · member-delta · member-beta (전원)

---

## 활성 멤버 목록
| 멤버 | 역할 | 담당 산출물 |
|---|---|---|
| member-alpha | 시장 조사·데이터 분석 | `member-alpha/analysis-report.md` |
| member-gamma | 팩트체커 (수치·출처 검증) | `member-gamma/fact-check-log.md` |
| member-delta | 시각화 (Mermaid·테이블) | `member-delta/visuals.md` |
| member-beta | 최종 보고서 초안 작성 | `member-beta/draft-report.md` |

---

## 업무 분해 (Assignments)

### Assignment 1 — member-alpha
**목표**: 전남·광주 지역 AI·로보틱스·물류 파트너사 조사·분석
- 기업/기관 목록 수집: 지역 기반 AI·로보틱스·물류 스타트업, 중견기업, 연구기관, 협력기관
- 각 파트너사별 핵심 역량, 사업 분야, 지역 거점, 협업 가능성 분석
- 도표 및 분류 체계 포함
- 산출물: `output/전남-광주-지역-기반의-ai/member-alpha/analysis-report.md`

### Assignment 2 — member-gamma
**목표**: member-alpha 분석 보고서의 수치·기업명·정책명 등 팩트 검증
- 입력: `output/전남-광주-지역-기반의-ai/member-alpha/analysis-report.md`
- 기업명, 설립연도, 사업 분야, 수치 데이터 검증
- 불명확 출처 또는 오류 항목 플래그
- 산출물: `output/전남-광주-지역-기반의-ai/member-gamma/fact-check-log.md`

### Assignment 3 — member-delta
**목표**: 분석 결과를 시각화 (Mermaid·테이블)
- 입력: `output/전남-광주-지역-기반의-ai/member-alpha/analysis-report.md`
- 파트너사 분류 다이어그램, 도메인별 기업 분포 테이블
- 파트너사 생태계 관계도
- 산출물: `output/전남-광주-지역-기반의-ai/member-delta/visuals.md`

### Assignment 4 — member-beta
**목표**: 최종 보고서 초안 작성
- 입력: alpha 분석 보고서, gamma 팩트체크 로그, delta 시각화 자료
- 요약 · 핵심 인사이트 · 추천 사항 섹션 포함
- 산출물: `output/전남-광주-지역-기반의-ai/member-beta/draft-report.md`

---

## 실행 순서 및 의존성

```
member-alpha (1단계: 조사·분석)
    ├─→ member-gamma (2단계: 팩트체크) ← alpha 산출물 의존
    └─→ member-delta (2단계: 시각화) ← alpha 산출물 의존
         ↓
    member-beta (3단계: 보고서 초안) ← alpha + gamma + delta 의존
         ↓
    team-lead (4단계: 통합 → final-artifact.md)
```

## 의존성 맵
- member-gamma → member-alpha/analysis-report.md
- member-delta → member-alpha/analysis-report.md
- member-beta → member-alpha/analysis-report.md + member-gamma/fact-check-log.md + member-delta/visuals.md

---

## 종료 조건
- max_cycles: 3
- quality_criteria: 필수 섹션 포함 + 논리적 정합성 + 형식 준수
- human_approval: false
