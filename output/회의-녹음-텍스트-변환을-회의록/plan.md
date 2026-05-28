# Plan: 회의 녹음 텍스트 변환을 통한 회의록 작성 앱 개발

자동 확정된 slug: 회의-녹음-텍스트-변환을-회의록

## Task 요약
회의 음성을 녹음하거나 오디오 파일을 업로드하여 STT(Speech-to-Text) 변환 후,
Claude API를 활용해 자동으로 회의록(요약, 액션아이템, 결정사항)을 생성하는 웹 앱을 개발한다.

## Task Type 판별

| Task Type         | 매칭 키워드            | Score |
|-------------------|-----------------------|-------|
| research-report   | 없음                   | 0/8   |
| code-review       | 없음                   | 0/5   |
| multilingual-brief| 없음                   | 0/6   |
| **dev**           | **개발** (1개 매칭)    | **1/10** |
| design            | 없음                   | 0/8   |
| github-plan       | 없음                   | 0/7   |

- **선택된 type**: `dev`
- **선택 근거**: "개발" 키워드 매칭 (score 1위, 0.1)
- **활성 멤버**: member-alpha, member-epsilon

## 활성 멤버 목록
| 멤버 | 역할 | 산출물 |
|------|------|--------|
| member-alpha | 구현 방향 분석 및 기술 스택 정의 | `member-alpha/analysis-report.md` |
| member-epsilon | 실제 코드 구현 및 검증 | `member-epsilon/dev-log.md`, `member-epsilon/diff-summary.md` |

## 배정 내용

### member-alpha 배정
- 회의록 앱의 핵심 기능 요구사항 분석
- 기술 스택 선정: 언어, 프레임워크, STT 라이브러리, LLM API
- 프로젝트 디렉터리 구조 및 파일 구성 계획
- 각 모듈별 구현 스펙 정의
- 산출물: `analysis-report.md`

### member-epsilon 배정 (alpha 완료 후)
- alpha 분석 보고서 기반으로 프로젝트 신규 생성
- 디렉터리 경로: `output/회의-녹음-텍스트-변환을-회의록/app/`
- 핵심 기능 구현:
  1. 오디오 녹음 또는 파일 업로드
  2. Whisper 기반 STT 변환
  3. Claude API 기반 회의록 자동 생성
  4. 결과물 표시/다운로드 UI
- 자체 검증 후 dev-log.md 작성
- 산출물: `dev-log.md`, `diff-summary.md`

## 실행 순서 및 의존성

```
member-alpha (독립 실행)
       ↓
member-epsilon (alpha 산출물 참조 후 실행)
       ↓
Team Lead 리뷰 → 통합 → final-artifact.md
```

## 예상 최종 산출물
- `output/회의-녹음-텍스트-변환을-회의록/final/final-artifact.md` — 구현 완료 보고서 + 앱 코드 요약
- `output/회의-녹음-텍스트-변환을-회의록/app/` — 실제 앱 코드

자동 확정 후 Phase 2 진입: 2026-05-27 (human_approval: false)
