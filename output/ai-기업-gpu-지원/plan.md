# 계획 문서 — AI 기업 GPU 지원

**작성일**: 2026-04-20  
**워크스페이스**: `ai-기업-gpu-지원`  
**팀장**: team-lead

---

## 1. 업무 요약

AI 기업에 대한 GPU 지원 현황을 조사·분석하고, 국내외 주요 지원 프로그램·정책·민간 사례를 정리하여 실행 가능한 인사이트와 추천 사항을 담은 최종 보고서를 산출한다.

---

## 2. 과제 분해 및 담당자 배정

| # | 과제 | 담당자 | 산출물 |
|---|------|--------|--------|
| T1 | GPU 지원 시장·정책 리서치 및 데이터 분석 | member-alpha | `member-alpha/analysis-report.md` |
| T2 | 분석 결과 기반 최종 보고서 초안 작성 | member-beta | `member-beta/draft-report.md` |

---

## 3. 실행 순서 및 의존성 맵

```
[T1: member-alpha]
    ↓ analysis-report.md 전달
[T2: member-beta]
    ↓ draft-report.md 전달
[팀장 통합 → final-artifact.md]
```

- T2는 T1 완료 후 실행 (단방향 의존성, 사이클 없음 ✓)
- 모든 파일 전달은 파일 경로 참조 방식(file-based)

---

## 4. 각 담당자 상세 지시

### member-alpha 지시
- **주제**: AI 기업 대상 GPU 지원 프로그램 현황 분석
- **조사 범위**:
  1. 국내 정부/공공기관 GPU 지원 정책 (과기부, NIPA, NIA, 클라우드 바우처 등)
  2. 해외 주요국 GPU 지원 프로그램 (미국 NAIRR, EU AI Office, 일본 GENIAC 등)
  3. 민간 클라우드 기업의 AI 스타트업 GPU 지원 크레딧 프로그램 (AWS, GCP, Azure, NVIDIA)
  4. 국내 AI 기업의 GPU 수요·공급 현황 및 격차
- **필수 섹션**: 개요 / 분석 결과 / 결론
- **저장 경로**: `output/ai-기업-gpu-지원/member-alpha/analysis-report.md`

### member-beta 지시
- **입력**: `output/ai-기업-gpu-지원/member-alpha/analysis-report.md`
- **주제**: AI 기업 GPU 지원 현황 보고서 초안
- **작성 방향**: member-alpha 분석 결과를 바탕으로 핵심 인사이트 도출 및 정책·사업 추천 사항 제시
- **필수 섹션**: 요약 / 핵심 인사이트 / 추천 사항
- **저장 경로**: `output/ai-기업-gpu-지원/member-beta/draft-report.md`

---

## 5. 검토 기준

- 필수 섹션 모두 포함 여부
- 데이터·사실 기반 근거 명시
- 논리적 흐름 및 중복·모순 없음
- 최종 산출물 형식(md) 준수

---

## 6. 종료 조건

- `max_cycles`: 3
- 품질 기준 충족 후 팀장 최종 검토
- 최종 산출물: `output/ai-기업-gpu-지원/final/final-artifact.md`
