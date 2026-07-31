# 평가 계획서 — 바로고 AX 통합 관리 시스템

> 자동 확정된 slug: `ax-management-system-eval`
> 작성: 2026-06-18 / Team Lead
> 평가 대상: `C:\Users\jmlee\OneDrive - 바로고\문서\클로드 코드 에이전트\ax-management-system`
> 기준 문서: `AX_관리시스템_설계서.md` (2026-06-15, 인터뷰 업데이트 2026-06-16)

## 1. Task 요약
약 1,018 LOC 규모의 FastAPI + SQLAlchemy + SQLite(WAL) 기반 **사무실 내부망 RBAC 웹 애플리케이션**(1단계 스캐폴드)에 대한 종합 평가. 사용자 요청: "이 앱에 대한 평가 진행 + 에이전트 팀 기능 총 동원".

## 2. Task Type 판별
- 사용자 문장: "이 앱에 대한 평가 진행 / 에이전트 팀 기능 총 동원"
- 직접 trigger 매칭: 없음 ("평가"는 어떤 type trigger에도 직접 포함되지 않음)
- 의미 판별: **앱 평가 = code-review 계열** (기존 코드베이스 품질·보안·설계 부합도 검증)
- score: code-review 0(직접) / research-report 0 / 그 외 0 → 의미적으로 code-review 채택
- **사용자 명시 요청 "총 동원"**에 따라 code-review 기본 멤버(alpha·gamma·beta)를 **평가에 유효한 멤버로 확장**

**선택된 type: `code-review` (확장형, 평가 전용)**

## 3. 활성 멤버 (6명 투입 — epsilon 제외)
| 멤버 | 평가 역할 | 산출물 |
|---|---|---|
| member-eta | 유사 오픈소스 벤치마크 / 라이선스 감사 / 업계 표준 대비 격차 | `github-research-report.md` |
| member-alpha | 코드·아키텍처 분석 (구조/RI·KPI 로직/데이터 모델) | `analysis-report.md` |
| member-gamma | 보안·로직 검증 (인증/세션/RBAC 스코프/승인 워크플로우) | `fact-check-log.md` |
| member-zeta | 설계서 부합도 평가 (§ 범위·제외·워크플로우 대조) | `design-spec.md` |
| member-delta | 시각화 (아키텍처 다이어그램·평가 스코어 매트릭스·리스크 히트맵) | `visuals.md` |
| member-beta | 최종 통합 평가 보고서 초안 | `draft-report.md` |

> epsilon(코드 수정·배포)은 read-only 평가 범위 밖이므로 미투입. 발견된 결함은 보고서 권고로 정리.

## 4. 평가 차원 (Evaluation Rubric)
1. **설계 부합도** — 설계서 §1~§8 대비 구현 일치/누락/이탈 (Meeting 전면 제외, 승인 워크플로우, 감사 로그, KPI 집계)
2. **보안** — Slack OAuth, 세션 서명/쿠키, RBAC 부서 스코프 강제, 승인 우회 가능성, 입력 처리
3. **코드 품질·아키텍처** — 레이어 분리, RI/KPI 결정론 로직 정확성, 에러 처리, 테스트 부재
4. **업계 표준 대비** — 유사 오픈소스 대비 누락된 모범 사례
5. **운영 준비도** — 배포(NSSM/mkcert), 마이그레이션, 동시성(WAL), 백업

## 5. 실행 순서 & 의존성
```
Phase 2-A (병렬, 독립):
  eta   ─┐ (벤치마크)
  alpha ─┤ (코드 분석)
  gamma ─┤ (보안 검증)
  zeta  ─┘ (설계 부합도)
        │
Phase 2-B (의존):
  delta ← alpha·gamma·zeta 산출물 (시각화)
        │
  beta  ← 전 멤버 산출물 (통합 보고서 초안)
        │
Phase 3: member-reviewer ×6 (격리 리뷰)
Phase 4: final-artifact.md 통합
Phase 5: Notion 저장 + Slack 링크 전송
```

## 6. 의존성 맵
- eta, alpha, gamma, zeta: 입력 = 평가 대상 소스 + 설계서 (상호 독립)
- delta: 입력 = alpha + gamma + zeta 결과
- beta: 입력 = eta + alpha + gamma + zeta + delta 결과

## 7. 검증 기준 (termination)
- 각 멤버 산출물 필수 섹션 포함 (rule)
- 통합 보고서 논리 정합성·중복/모순 없음 (llm_self_check)
- 최종 산출물 md 형식 준수 (schema)
- human_approval: false → 자동 진행

---
_자동 확정 후 Phase 2 진입: 2026-06-18_
