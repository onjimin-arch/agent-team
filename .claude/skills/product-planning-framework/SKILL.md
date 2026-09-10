# Product Planning Framework Skill

## Purpose
`product-planning` task type에서 Team Lead가 Phase 1-1(Task 분해)을 수행할 때 따르는 IP 융합
신제품기획 5단계 Stage-Gate 프레임워크. 각 STEP의 세부활동과 Gate Review 기준을 정의해, alpha·
gamma·delta·beta의 assignment가 임의로 흐트러지지 않고 이 구조를 그대로 따르게 한다.

## When to Use
- Phase 1-1: `product-planning` type의 `plan.md` 작성 시, assignment를 STEP 단위로 쪼갤 때.
- Phase 3: 각 멤버 산출물이 자신이 맡은 STEP의 세부활동을 실제로 담았는지 확인할 때.

## 5단계 Stage-Gate

| STEP | 세부활동 (4개) | 담당 | Gate Review 통과 기준 |
|---|---|---|---|
| STEP1 고객환경분석 | 제품/니즈 분석 · 보유·동종 특허 분석 · 환경분석 · 프로젝트 정의 | alpha | 프로젝트 범위·목표 고객군이 한 문단으로 명확히 정의됨 |
| STEP2 고객가치분석 | 고객 경험 조사 · JTBD 분석 · 목표고객 선정 · 고객가치 제안 | alpha(분석) + gamma(고객조사 원천자료 검증) | 고객가치제안(Value Proposition) 문장이 목표고객·핵심 Job·차별점을 모두 포함 |
| STEP3 신제품기획 | 프롬프트 구성 · IP융합 특허 분석 · IP융합 특허 선정 · 신제품기획 | alpha | 선정된 IP/특허와 신제품 기능의 연결 관계가 표로 명시됨 |
| STEP4 경제가치설계 | 기업이 할 일 · 비즈니스모델 설계 · 실행계획 수립 · IP전략 수립 | delta(BM·실행계획 시각화) + beta(초안 정리) | BM 캔버스(또는 표)와 실행계획에 담당·기한이 채워짐 |
| STEP5 검증 | 사업타당성 검토 · 가설검증 · IP검증(FTO) · 시장검증(CRM) | gamma(사실·특허·시장 검증) + beta(최종보고서 통합) | FTO(자유실시 가능 여부) 결론과 시장검증 근거가 둘 다 명시됨 |

## Gate Review 기록 규칙
- STEP이 끝날 때마다 `WS/plan.md`(또는 `WS/review-log.md`)에 "STEP{n} Gate Review: PASS/FAIL — 근거"
  한 줄을 남긴다.
- FAIL이면 다음 STEP으로 넘어가지 않고 해당 STEP 담당 멤버에게 Phase 3 REASSIGN과 동일하게 재작업을
  맡긴다(사유는 FAIL 근거 그대로 사용).
- 5개 STEP 전부 PASS해야 Phase 4 통합으로 진행한다.

## Assignment 작성 시 주의
- alpha에게 STEP1·STEP3를 한 번에 배정할 때도 두 STEP 세부활동을 각각 명시한다 — "IP/특허 분석"만
  적으면 STEP1의 보유·동종 특허 분석과 STEP3의 IP융합 특허 분석이 뭉개진다.
- gamma는 이 type에서는 팩트체크가 아니라 "고객조사 원천자료 검증"(STEP2)과 "사업타당성·시장검증"
  (STEP5) 역할이므로, assignment 지시문에 일반적인 fact-check-log 형식 대신 이 두 역할을 명시한다.
