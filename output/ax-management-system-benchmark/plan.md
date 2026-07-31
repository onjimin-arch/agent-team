# 평가 계획서 — AX 관리 시스템 vs 업무 관리 시스템 경쟁 벤치마크

> 자동 확정된 slug: `ax-management-system-benchmark`
> 작성: 2026-06-18 / Team Lead
> 평가 대상: `C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\ax-management-system`
> 참조 입력: `output/ax-management-system-eval/final/final-artifact.md` (2026-06-18, 동일 앱의 코드·보안 평가 — 본 작업은 그와 다른 **기능·UI 경쟁 비교** 관점)

## 1. Task 요약
바로고 AX 관리 시스템의 **기능 범위와 UI/UX**를 일반 업무·프로젝트 관리 시스템(Notion, Asana, Jira, ClickUp, Monday.com, Linear, Trello 등) 및 인접 영역(프로세스 개선/BPM)과 비교하여 **격차와 개선점**을 도출한다. 코드 품질·보안은 본 작업 범위 밖(선행 eval에서 다룸).

## 2. Task Type 판별
- 사용자 문장: "이 앱의 기능이나 UI 전반적으로 다른 업무 관리 시스템들과 비교. 개선점 도출"
- trigger 매칭: research-report("분석"·"비교"는 의미상 리서치/벤치마크) ← 경쟁 비교·개선점 도출은 리서치 보고서 성격
- 직접 trigger: "비교/개선점"은 어느 type에도 직접 없음 → 의미 판별로 **research-report** 채택 (벤치마크 = 시장 조사형)
- code-review와 달리 외부 시스템 대비 **기능/UX 벤치마크**이므로 research-report가 적합

**선택된 type: `research-report`**

## 3. 활성 멤버 (4명)
| 멤버 | 역할 | 산출물 |
|---|---|---|
| member-alpha | 앱 기능·UI 인벤토리 작성 + 경쟁 시스템 기능 매핑 + 비교 차원(rubric) 정의 | `analysis-report.md` |
| member-gamma | 경쟁 시스템(Notion/Asana/Jira/ClickUp/Monday/Linear 등) 현행 기능·UX 사실 검증 (WebSearch/WebFetch) | `fact-check-log.md` |
| member-delta | 기능 비교 매트릭스·UX 갭 히트맵·개선 우선순위 시각화 | `visuals.md` |
| member-beta | 최종 통합 비교 보고서 + 개선 로드맵 | `draft-report.md` |

## 4. 평가 차원 (Benchmark Rubric)
1. **정보 구조·뷰** — 테이블/보드/타임라인/캘린더/간트/리스트, 저장된 뷰, 그룹핑·필터·정렬
2. **데이터 모델·커스터마이징** — 커스텀 필드, 관계형 연결, 수식/롤업, 템플릿
3. **협업·워크플로우** — 코멘트·멘션·알림, 승인/상태 전이, 자동화 룰, 권한
4. **AX 도메인 특화 기능** — RI 정량화, 가치사슬, AI 도입 단계, KPI 스냅샷 (경쟁 대비 차별점)
5. **UI/UX 완성도** — 인라인 편집, 상세 패널, 일괄 작업, 검색, 모바일/반응형, 온보딩, 접근성
6. **확장·통합** — API, 외부 연동(Slack 등), 임포트/엑스포트, 리포팅·대시보드

## 5. 실행 순서 & 의존성
```
Phase 2-A (병렬):
  alpha ─┐ (앱 기능·UI 인벤토리 + 경쟁 기능 매핑 + rubric)
  gamma ─┘ (경쟁 시스템 현행 기능 사실 검증)
        │
Phase 2-B (의존):
  delta ← alpha + gamma (비교 매트릭스·갭 히트맵 시각화)
  beta  ← alpha + gamma + delta (통합 비교 보고서 + 개선 로드맵)
        │
Phase 3: member-reviewer ×4 (격리 리뷰)
Phase 4: final/final-artifact.md 통합
Phase 5: Notion 저장 + Slack 링크 전송
```

## 6. 검증 기준 (termination)
- 각 멤버 산출물 필수 섹션 포함 (rule)
- 통합 보고서 논리 정합성·중복/모순 없음 (llm_self_check)
- 개선점이 "근거(경쟁 비교) → 갭 → 구체 조치"로 추적 가능
- human_approval: false → 자동 진행

---
_자동 확정 후 Phase 2 진입: 2026-06-18_
