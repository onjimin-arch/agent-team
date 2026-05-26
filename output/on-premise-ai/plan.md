# Plan — 온프레미스 AI 종합 리서치

- **Workspace slug**: `on-premise-ai`
- **작성일**: 2026-04-23
- **요청자**: onjimin@gmail.com

## 1. Task 요약
사용자 요청: **"신규 주제 온프레미스 AI"** — 기업 도입 전략, 하드웨어·인프라 요구사항, 오픈소스 모델 비교, 보안·컴플라이언스, 비용 대비 효과(TCO) 등 5대 영역을 **모두 포함**하는 종합 리서치 보고서.

사용자가 "전부 다" 로 명시 → 단일 영역 심화가 아닌 **전방위 개괄 + 의사결정 프레임** 이 최종 산출물의 목표.

## 2. 선택된 Task Type
- **Task Type**: `research-report` (default)
- **선택 근거**: 사용자 요청에 직접적인 trigger 키워드(`리서치`)가 포함됨. 또한 요청 성격이 "현황 조사 + 비교 분석 + 의사결정 지원" 으로 리서치 보고서 패턴에 부합.
- **활성 멤버**: `member-alpha`, `member-gamma`, `member-delta`, `member-beta` (전원)
- **비활성 멤버**: 없음

## 3. 리서치 범위 (5대 축)
| 축 | 핵심 질문 | 주 담당 |
|---|---|---|
| A. 기업 도입 전략 | 왜 온프레미스인가? 어떤 기업/워크로드가 적합? 도입 단계별 로드맵은? | alpha |
| B. 하드웨어·인프라 | GPU/서버/네트워크/스토리지 요구사항. 2026년 현재 가용 옵션(NVIDIA H100/H200/B200, AMD MI300X, 국산 NPU 등) | alpha |
| C. 오픈소스 모델 비교 | Llama 3.x/4, Qwen 2.5/3, Mistral, DeepSeek, Gemma, SOLAR 등 — 라이선스·성능·운영 난이도 비교 | alpha + gamma |
| D. 보안·컴플라이언스 | 데이터 주권, 국내 개인정보보호법·AI 기본법, 금융/의료 규제, 망분리, 모델 가드레일 | alpha + gamma |
| E. 비용 대비 효과 (TCO) | CapEx(하드웨어·구축) vs OpEx(전력·인력·운영) vs 클라우드 API 대비 손익분기 토큰량 | alpha + delta |

## 4. Assignments (활성 멤버별)

### 4-1. member-alpha — 시장 조사 및 데이터 분석
- **입력**: 사용자 요청 + 본 plan.md
- **작업**: 위 5대 축 각각에 대한 현황·옵션·정량 데이터 수집 및 분석
- **출력**: `output/on-premise-ai/member-alpha/analysis-report.md`
  - 필수 섹션: `개요`, `분석 결과`(5대 축 각각 서브섹션), `결론`
  - 구체적 포함 요구사항:
    - B축: GPU 모델별 VRAM/TFLOPS/가격/전력소비 비교표
    - C축: 최소 5개 이상 오픈소스 모델 라이선스·파라미터·한국어 성능 비교표
    - D축: 국내 적용 규제 목록(개인정보보호법, AI 기본법 2026, 금융권 망분리, 의료 가명처리 등)
    - E축: 3가지 시나리오(중소기업/중견기업/대기업) TCO 3년 추정치

### 4-2. member-gamma — 팩트체커
- **입력**: `member-alpha/analysis-report.md` (완료 후)
- **작업**: WebSearch/WebFetch 로 수치·인용·출처 검증. 특히 다음 항목 집중 검증:
  - GPU 스펙·가격 (NVIDIA 공식, 리셀러 견적)
  - 오픈소스 모델 벤치마크 점수 (HuggingFace Leaderboard, LMSYS, KMMLU 등)
  - 국내 AI 기본법 시행일·주요 조항
  - 클라우드 API 단가 (OpenAI, Anthropic, Google)
- **출력**: `output/on-premise-ai/member-gamma/fact-check-log.md`
  - 필수 섹션: `검증 요약`, `항목별 검증 결과`, `수정 권고`

### 4-3. member-delta — 시각화
- **입력**: `member-alpha/analysis-report.md` + `member-gamma/fact-check-log.md`
- **작업**: 핵심 데이터를 Mermaid 다이어그램·비교표로 변환
- **출력**: `output/on-premise-ai/member-delta/visuals.md`
  - 필수 섹션: `시각자료 개요`, `Mermaid 다이어그램`, `핵심 수치 테이블`
  - 요구 시각자료 (최소):
    1. 온프레미스 AI 도입 의사결정 플로우차트 (Mermaid)
    2. 하드웨어 옵션 비교표 (GPU 스펙·가격·용도)
    3. 오픈소스 모델 맵 (라이선스 축 × 성능 축, Mermaid quadrantChart 또는 표)
    4. TCO 시나리오 비교 막대 스펙 (Markdown 표로 표현)
    5. 3단계 도입 로드맵 (Mermaid gantt 또는 flowchart)

### 4-4. member-beta — 최종 보고서 초안 작성
- **입력**: alpha · gamma · delta 산출물 전부
- **작업**: 검증된 데이터 + 시각자료를 바탕으로 의사결정자용 종합 보고서 초안 작성
- **출력**: `output/on-premise-ai/member-beta/draft-report.md`
  - 필수 섹션: `요약`(executive summary), `핵심 인사이트`, `추천 사항`
  - 톤: CTO/CIO 대상 — 실행 가능한 의사결정 프레임 제시
  - 반드시 delta 의 Mermaid/표를 본문에 임베드

## 5. Execution Order (실행 순서)
```
[1] alpha (독립)
        ↓
[2] gamma (alpha 산출물 검증)
        ↓
[3] delta (alpha + gamma 기반 시각화)
        ↓
[4] beta (alpha + gamma + delta 전부 통합)
        ↓
[5] Lead Review & Integration → final/final-artifact.md
```

## 6. Dependency Map
- alpha → (gamma, delta, beta)
- gamma → (delta, beta)
- delta → (beta)
- beta → (final integration)

순환 의존성 없음. ✅

## 7. Validation
- [x] 모든 활성 멤버에게 최소 1개 assignment 배정됨
- [x] 의존성 그래프에 순환 없음
- [x] 각 expected output 의 필수 섹션·포맷 명시됨

## 8. 종료 조건
- `max_cycles: 3`
- `max_review_per_member: 2`
- `human_approval: true` (승인 후 Phase 5 Distribution → Notion + Slack)
