# 기획 문서: GPU 지원

## 1. 태스크 요약
**주제**: GPU 지원 현황 및 활용 방안 리서치 보고서
**설명**: 국내외 GPU 지원 프로그램(정부, 클라우드 기업, 스타트업 지원 기관 등)의 현황을 조사·분석하고, AI/ML 스타트업 및 연구기관이 활용 가능한 GPU 자원 지원 방안을 정리한다.
**작성일**: 2026-05-12

## 2. Task Type 판별
- **선택된 Type**: `research-report` (default)
- **근거**: "GPU 지원" 요청문에 research-report 트리거 키워드(리서치/분석/보고서 등)가 명시되지 않았으나, 기본 type이 research-report이므로 자동 선택
- **활성 멤버**: member-alpha · member-gamma · member-delta · member-beta

## 3. 멤버별 배정

| 멤버 | 역할 | 산출물 | 의존성 |
|---|---|---|---|
| member-alpha | GPU 지원 프로그램 현황 조사·데이터 분석 | `member-alpha/analysis-report.md` | 없음 (선행) |
| member-gamma | alpha 산출물 팩트체크 | `member-gamma/fact-check-log.md` | member-alpha 완료 후 |
| member-delta | 시각화 (Mermaid 다이어그램·비교 테이블) | `member-delta/visuals.md` | member-alpha 완료 후 (gamma와 병렬) |
| member-beta | 최종 보고서 초안 작성 | `member-beta/draft-report.md` | gamma·delta 완료 후 |

## 4. 실행 순서
```
1단계: member-alpha (GPU 지원 현황 분석)
         ↓
2단계: member-gamma (팩트체크) ‖ member-delta (시각화) — 병렬
         ↓
3단계: member-beta (최종 보고서 초안)
```

## 5. 의존성 맵
- alpha → gamma (팩트체크 대상 제공)
- alpha → delta (시각화 원자료 제공)
- gamma + delta → beta (검증 결과 + 시각자료 → 보고서 초안)

## 6. 기대 산출물
- `output/gpu-지원/member-alpha/analysis-report.md`: GPU 지원 프로그램 조사 및 분석
- `output/gpu-지원/member-gamma/fact-check-log.md`: 수치·프로그램명 검증 로그
- `output/gpu-지원/member-delta/visuals.md`: 비교 다이어그램 및 테이블
- `output/gpu-지원/member-beta/draft-report.md`: 요약·인사이트·추천 초안
- `output/gpu-지원/final/final-artifact.md`: 최종 통합 보고서
