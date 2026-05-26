# Draft Report — Self-Healing Pipeline 통합 검토

Creator: member-beta
Created: 2026-05-26
Version: 1.0

---

## 개요

alpha·zeta·epsilon 산출물을 검토하고 최종 통합 패치(`self-healing-pipeline-patch.md`) 구성을 확정한다.

---

## 분석 결과

### 산출물 간 일관성 검증

| 항목 | alpha | zeta | epsilon | 판정 |
|------|-------|------|---------|------|
| 역보고 엔드포인트 | `POST /report` (localhost:5000) | `Send-SlackReport` → localhost:5000/report | `POST http://localhost:5000/report` | ✅ 일치 |
| 환경변수 명칭 | `SLACK_BOT_TOKEN`, `SLACK_REPORT_CHANNEL` | PATCH-05 동일 | 동일 참조 | ✅ 일치 |
| 포트 변수명 | — | `PROD_PORT`, `STAGING_PORT` | `PROD_PORT`, `STAGING_PORT` | ✅ 일치 |
| MAX_ATTEMPTS | — | 3 (스크립트 상수) | 3 (참조) | ✅ 일치 |
| /report 포트 | 5000 (queue-config 기준) | `http://localhost:5000/report` | 동일 | ✅ 일치 |
| PS 버전 | `requests` (Python) | `*>&1`, `Invoke-RestMethod` | PS 5.1 검증 완료 | ✅ 일치 |

### 보고 시점 7개 커버리지

| 시점 | 담당 | 구현 위치 | 상태 |
|------|------|---------|------|
| 작업 수신 | queue_server.py | `enqueue()` 직후 `slack_report()` | ✅ PATCH-01 |
| Phase 완료 | queue_server.py | `_run_opencode()` 완료 후 | ✅ PATCH-01 |
| 배포 시도 N/3 | deploy-heal | `Send-SlackReport` 루프 내 | ✅ PATCH-03 |
| 배포 성공 | deploy-heal | production health check 통과 후 | ✅ PATCH-03 |
| 배포 실패 | deploy-heal | staging/production health check 실패 시 | ✅ PATCH-03 |
| 롤백 | deploy-heal | MAX_ATTEMPTS 초과 후 | ✅ PATCH-03 |
| 최종 완료 | queue_server.py | `_run_opencode()` 종료 후 | ✅ PATCH-01 |

### AUTO 모드 인터럽트 8개 커버리지

| # | 인터럽트 | PATCH-02 처리 | 상태 |
|---|---------|-------------|------|
| ① | 슬러그 확인 | 자동 확정 + plan.md 기록 | ✅ |
| ② | 리서치 재사용 | 조건 자동 판단 | ✅ |
| ③ | 동점 처리 | config 순서 기준 자동 선택 | ✅ |
| ④ | Phase 3 직접수정 기준 | 30%로 완화 명시 | ✅ |
| ⑤ | Phase 4 재실행 | max_cycles 이내 자동 | ✅ |
| ⑥ | human_approval 게이트 | 자동 승인 + Phase 5 즉시 | ✅ |
| ⑦ | 에스컬레이션 | Slack 보고 후 최선 버전 진행 | ✅ |
| ⑧ | Phase 5 Distribution | enabled:true 즉시 실행 | ✅ |

### 서비스 타입 7종 커버리지

| 타입 | 감지 | Staging | Health Check | 롤백 |
|------|------|---------|-------------|------|
| Python Web | ✅ | Start-Process | curl /health | ✅ |
| Node.js | ✅ | Start-Process | curl | ✅ |
| Next.js | ✅ | npm build + Start-Process | curl | ✅ |
| Flutter | ✅ | flutter build apk --debug | exit code | ✅ |
| Android | ✅ | gradlew assembleDebug | exit code | ✅ |
| Docker | ✅ | docker compose staging | docker ps | ✅ |
| Python Script | ✅ | --dry-run | exit code | ✅ |

---

## 결론

5개 패치 모두 구조적으로 일관됨. 통합 순서:
1. PATCH-01 (queue_server.py) — Slack 역보고 기반 구축
2. PATCH-02 (CLAUDE.md) — AUTO 무인화
3. PATCH-03 (deploy-heal/SKILL.md) — 배포 자동화 엔진
4. PATCH-04 (member-epsilon/AGENT.md) — 에이전트 배포 권한 부여
5. PATCH-05 (team-config.yaml) — 설정 연결

설치 순서: 환경변수 → Slack 권한 확인 → 패치 적용 → 동작 확인
