# 작업 계획서

생성: Team Lead | 생성시각: 2026-05-26 | 워크스페이스: slack-self-healing-pipeline (자동 확정된 slug)

---

## 작업 요약

Slack 단방향 수신 구조를 양방향으로 확장하고, `[AUTO: slug]` 트리거 시 모든 인터럽트 없이
개발 → staging 테스트 → 자가 수정 → production 배포까지 완전 자동 실행되는 파이프라인을 설계한다.

## 선택된 Task Type

- **Type**: `design` (`[design]` 태그 명시 → score 무관 우선 적용)
- **Task Type Score**: design(태그 우선) / 태그 없었다면 research-report·code-review 등 scoring 비교 필요 없음
- **활성 멤버**: member-alpha · member-zeta · member-epsilon · member-beta (사용자 명시 위임 포함)

---

## 컨텍스트 파일 분석 요약

| 파일 | 현재 상태 | 변경 필요 |
|------|---------|---------|
| `queue_server.py` | Flask 수신 전용, opencode 트리거만 | Slack 역보고 함수 + 7개 시점 보고 |
| `CLAUDE.md` | AUTO 모드 기본 정의 있으나 인터럽트 8개 미처리 | 각 인터럽트 포인트 AUTO 분기 추가 |
| `member-epsilon/AGENT.md` | 배포 시 human_approval 필수 | AUTO 모드 + deploy-heal 자동 실행 |
| `queue-config.yaml` | SLACK_BOT_TOKEN·보고 채널 없음 | 환경변수 섹션 추가 |
| `team-config.yaml` | auto_mode 섹션 없음 | auto_mode + deployment 설정 추가 |

---

## 작업 분해

### member-alpha 배정
- `queue_server.py` 현재 구조 분석 (Flask 라우트, opencode 트리거 방식, 스레드 구조)
- Slack Web API (chat.postMessage) 역보고 함수 설계
- 7개 보고 시점별 호출 위치 명세화
- **산출물**: `analysis-report.md` + PATCH-01 (queue_server.py) 초안

### member-zeta 배정
- CLAUDE.md 인터럽트 포인트 8개 → AUTO 분기 로직 설계 (PATCH-02)
- `deploy-heal/SKILL.md` 전체 작성 — 서비스 감지·staging·self-healing·rollback (PATCH-03)
- `team-config-auto-patch.yaml` 작성 (PATCH-05)
- **산출물**: `design-spec.md` (PATCH-02·03·05 포함)

### member-epsilon 배정
- 자신의 AGENT.md Deployment Protocol 섹션 설계 (PATCH-04)
- Windows PowerShell 포트 관리 명령 검증 메모
- **산출물**: `dev-log.md` (PATCH-04 포함)

### member-beta 배정 (alpha + zeta + epsilon 완료 후)
- PATCH-01~05 통합 → `final/self-healing-pipeline-patch.md`
- 설치 순서·환경변수·동작 확인 가이드 작성
- 검증 체크리스트 완성
- **산출물**: `draft-report.md` → 최종 통합 반영

---

## 실행 순서 및 의존성

```
member-alpha ─┐
member-zeta  ─┼→ member-beta → Team Lead (Review + 최종 통합)
member-epsilon─┘
```

alpha · zeta · epsilon 병렬 실행 (상호 의존 없음)
beta는 세 멤버 완료 후 실행

---

## 기대 최종 산출물

`output/slack-self-healing-pipeline/final/self-healing-pipeline-patch.md`

포함 내용:
- PATCH-01: queue_server.py 양방향 Slack 보고
- PATCH-02: CLAUDE.md AUTO 모드 완전 무인화
- PATCH-03: deploy-heal/SKILL.md (신규)
- PATCH-04: member-epsilon/AGENT.md 배포 프로토콜
- PATCH-05: team-config.yaml 자동화 설정

자동 확정 후 Phase 2 진입 (human_approval: false)
