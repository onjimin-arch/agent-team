# Integrator Skill

## Purpose
Help the Team Lead merge approved member artifacts into a final deliverable.

## When to Use
- Phase 4: INTEGRATE

## Outputs
- A final artifact saved under `output/{slug}/final/`
- Integration quality checks

## Validation
아래 순서로 확인한다(상세 절차는 CLAUDE.md "Phase 4: Integration Protocol"이 원본이며, 이 문서는 요약이다):
1. **결정론적 섹션 검증**: `scripts/validate_artifact.py --file "WS/final/final-artifact.md" --sections "..."`
   로 필수 섹션이 실제로 존재/비어있지 않은지 재확인한다. 통합 편집 중 섹션 제목을 임의로 바꾸거나
   다른 섹션에 흡수시키지 않는다.
2. **독립 품질 검토**: `scripts/review_artifact.py`로 최종 산출물 자체를 member-reviewer 기준(task
   type별 깊이 rubric)으로 한 번 더 검토한다 — 방금 통합문을 쓴 Team Lead 본인이 아니라 격리된
   리뷰어가 판단해야 통합 과정에서 생긴 깊이 저하를 걸러낼 수 있다.
3. **`llm_self_check`**: 여러 멤버 산출물을 모두 본 사람만 판단 가능한 부분(섹션 간 논리적 정합성·
   중복/모순 없음)만 Team Lead가 직접 판단한다. 개별 섹션 깊이는 2번에서 이미 검토했으므로 여기서
   다시 판단하지 않는다.
