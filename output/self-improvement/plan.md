# 작업 계획서

생성: Team Lead | 생성시각: 2026-05-26 | 워크스페이스: self-improvement (자동 확정)

---

## 작업 요약

현재 프레임워크의 구조적 비효율 4종 + 추가 관찰 2종을 분석하고,
파일별 섹션 단위 패치(PATCH-01~05)를 생성한 뒤 실제 파일에 적용한다.

## 선택된 Task Type

- **Type**: `design` (`[design]` 태그 명시)
- **활성 멤버**: member-alpha, member-zeta, member-beta (태스크 지침 포함)

---

## 수정 대상 비효율 목록

| ID | 비효율 | 수정 파일 | 패치 |
|----|-------|---------|------|
| BUG-01 | alpha·gamma 역할 중복 (이중 웹 검색) | member-alpha/AGENT.md, member-gamma/AGENT.md | PATCH-01, 02 |
| BUG-02 | 새 작업마다 slug 확인 인터럽트 | CLAUDE.md § Workspace Protocol | PATCH-03 |
| BUG-03 | 과거 리서치 재사용 불가 | CLAUDE.md § Phase 1 | PATCH-04 |
| BUG-04 | trigger 첫 번째 매칭으로 task type 오결정 | CLAUDE.md § Phase 1-0 | PATCH-05 |
| OBS-01 | Review 독립성 제로 (작성자=리뷰어) | 아키텍처 수준 — 이번 범위 외 | 기록만 |
| OBS-02 | plan.md 사후 문서화 | 운용 관행 개선 — 이번 범위 외 | 기록만 |

> OBS-01·02는 `Agent` 도구 기반 진짜 서브에이전트 도입이 선행돼야 해결 가능.
> 현재 텍스트 패치 범위를 초과하므로 이번 사이클에서 제외, 별도 태스크로 예약.

---

## 작업 분해

### member-alpha 배정
- 현재 alpha·gamma AGENT.md에서 역할 중복 구간 정확히 식별
- PATCH-01 (alpha Execution Rules 수정), PATCH-02 (gamma role 강화) 초안

### member-zeta 배정
- CLAUDE.md 수정 대상 섹션 3곳 현재 내용 추출
- BUG-02·03·04 수정 방향 반영한 PATCH-03·04·05 설계

### member-beta 배정 (alpha + zeta 완료 후)
- 5개 패치를 `self-improvement-patch.md` 형식으로 통합
- 변경 전·후 형식 통일, 검증 체크리스트 작성

### Team Lead
- Review: 패치 간 충돌 확인, 기존 task type 5종 동작 유지 검증
- 승인 후 실제 파일 적용

---

## 실행 순서 및 의존성

```
member-alpha ─┐
              ├→ member-beta → Team Lead (Review + 적용)
member-zeta  ─┘
```

alpha와 zeta는 병렬 실행 가능 (의존 없음).

---

## 추가 관찰 사항 (OBS-01·02) — 향후 태스크 예약

**OBS-01: Review 독립성 제로**
Team Lead = 작성자 = 리뷰어로 자기 검증 구조. 해결 방안: 별도 Claude 인스턴스를
`Agent` 도구로 생성해 리뷰 단계 분리. → `새 작업 [design] review-independence-refactor`

**OBS-02: plan.md 사후 문서화**
실행 방향이 결정된 후 plan.md를 소급 작성하는 역순. 해결 방안: Phase 1에서
plan.md 초안을 먼저 작성하고 사용자 승인(human_approval: true) 또는
자동 진행 전 지연 타이머를 두는 체크포인트 추가. → 운용 관행 개선으로 처리 가능.
