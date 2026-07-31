# 설계 부합도(Conformance) 평가 — AX 통합 관리 시스템

> 평가자: member-zeta (개발 설계 / 설계 부합도 평가)
> 기준 문서: `ax-management-system/AX_관리시스템_설계서.md` (§0~§9)
> 평가 대상: `ax-management-system/app`, `scripts/seed.py`, `README.md`
> 평가일: 2026-06-18

---

## 작업 컨텍스트

본 평가는 **설계서가 명시한 요구사항·범위·데이터 모델·API·워크플로우**를 구현 코드와 1:1 대조하여, 구현이 설계 의도를 얼마나 충실히 따랐는지(conformance)를 판정한다. 기능의 동작 정확성(런타임 버그)보다 **"설계가 요구한 것이 구현에 존재하는가, 설계와 다르게 구현되지 않았는가"**에 초점을 둔다.

평가 범위:
- §0 시스템 성격(내부망 웹앱, 결정론 1단계 / LLM 2단계)
- §1.3 범위 포함/제외 (특히 **Meeting 전면 제외**)
- §2 데이터 모델 8객체 (User/Case/ActionItem/Report/ChangeRequest/AuditLog/ImportBatch/LookupValue)
- §3 RBAC (역할·권한 매트릭스·즉시/승인 편집 정책·Slack 인증)
- §4 핵심 워크플로우 (로그인·seed·케이스·승인·KPI·실삭제)
- §6 기술 스택 / §7 폴더·API·열거형 / §8 AI 분석 2단계

판정 기호: ✅구현완료 · 🟡부분구현 · ❌미구현 · ⚠️설계이탈

---

## 워크플로우 정의

설계서 §4의 핵심 워크플로우별 구현 매핑:

| 워크플로우 | 설계 §  | 구현 위치 | 판정 |
|---|---|---|---|
| Slack 로그인 & 세션 | §4.1, §3.5 | `auth_router.py`, `auth/slack_oauth.py`, `auth/session.py`(HMAC 서명 쿠키) | 🟡 (미등록자 처리 이탈) |
| 엑셀 Seed 업로드 (덮어쓰기·ImportBatch) | §4.2 | `services/excel_import.py`, `admin_router.import_excel`, `scripts/seed.py` | 🟡 (동적 컬럼매핑·재업로드 경고 누락) |
| 케이스 조회/생성/AX타겟지정/즉시편집 | §4.3 | `case_router.py`(list/patch/delete) | 🟡 (생성 `POST /cases` 누락) |
| 승인 워크플로우(상태전이·supersede) | §4.4 | `services/change_workflow.py`, `approval_router.py` | ✅ |
| KPI 집계 / 스냅샷 보고서 | §4.5 | `services/kpi.py`, `report_router.py` | 🟡 (월말 스냅샷 확정 누락) |
| 실삭제 (AX팀 전용 + AuditLog) | §4.6 | `case_router.delete_case` | 🟡 (pending CR 자동취소 누락) |

승인 상태 전이 검증: `change_workflow.submit()`은 동일 필드 기존 pending을 `cancelled(reason="superseded")`로 자동 처리하고(§9.1 #17 충족), `decide()`는 `pending → approved | rejected | cancelled` 단방향 전이만 허용(`if cr.status != "pending": return`)하며 approve 시에만 `_apply()`로 원본 반영 → **§4.4 "승인 전 원본·KPI 불변" 원칙 정확히 구현**. 취소 권한은 `요청자 또는 AX팀`으로 제한(§9.1 #16 충족).

---

## 구현 스펙 (설계요구 ↔ 구현상태 대조)

### A. 시스템 성격 / 범위 (§0, §1.3)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| 내부망 웹앱(FastAPI+SQLite) | §0, §6 | ✅ | `main.py:11`, `db.py:6` | |
| SQLite WAL 모드 | §1.5, §9.1 #24 | ✅ | `db.py:12` `PRAGMA journal_mode=WAL` | foreign_keys=ON도 적용 |
| 1단계 결정론 / 2단계 LLM 분리 | §0, §8 | ✅ | `services/analysis/__init__.py:17,31` | 결정론 RI + LLM/휴리스틱 폴백 |
| **Meeting 전면 제외** | §1.3, §2.1, §9.1 #9 | ✅ | 모델·라우터·DB 전체 검색 결과 `meeting`/`linked_meeting` 0건 | **준수 확인** |
| 엑셀 역방향 export 제외 | §1.3 | ✅ | 해당 코드 없음 | 의도대로 제외 |
| Slack 알림 제외(인박스만) | §1.3 | ✅ | Slack 알림 코드 없음 | |

### B. 데이터 모델 8객체 (§2)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| Department (dept_id+name만) | §2.1, §9.1 #21 | ✅ | `models/__init__.py:12-16` | KPI 수치 미저장 = 준수 |
| Case (stage 생애주기·progress_rate·hours·KPI필드) | §2.1, §7.4 | ✅ | `models/__init__.py:19-69` | stage 기본값 `일반업무` |
| ActionItem (owner 자유텍스트, linked_case) | §2.1, §9.1 #13 | 🟡 | `models/__init__.py:71-79` | 모델 존재, **라우터/API 부재** |
| Report (KPI 스냅샷 + 부서보고서) | §2.1, §9.1 #14,#30 | 🟡 | `models/__init__.py:136-145` | `scope=dept\|snapshot` 필드는 있으나 snapshot 생성 경로 없음 |
| User (slack_id·role·dept_id·active) | §2.2 | 🟡 | `models/__init__.py:127-133` | **`active` 필드 누락**(설계 명시) |
| ChangeRequest (status 4값·requested_by·reason) | §2.2 | ✅ | `models/__init__.py:82-95` | 설계의 `reviewed_by`는 AuditLog로 대체 |
| AuditLog (actor·action·object·field·old·new) | §2.2 | 🟡 | `models/__init__.py:106-114` | `detail` 단일 텍스트로 통합 — field/old/new 분리 안 됨 |
| ImportBatch (file·imported_by·scope·rows·overwrote) | §2.2 | 🟡 | `models/__init__.py:117-124` | **`imported_by`·`overwrote` 필드 누락** |
| LookupValue (category·value·label·sort) | §2.2, §9.1 #11 | 🟡 | `models/__init__.py:98-103` | 모델 존재(kind/value/sort), **`label` 누락 + 관리 API 부재** |
| 8객체 모두 존재 | §2, §7.3 | ✅ | 9개 테이블 모두 정의 | 단, **per-file 분리(§7.1) 미준수** — 단일 `__init__.py` |

### C. RBAC / 권한 (§3)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| 3역할(ax_team/dept_head/staff) | §3.1, §7.4 | ✅ | `auth/rbac.py:13-24` | +대표(ceo) 역할 추가(§9.1 #31 반영) |
| 부서 스코프 검사(dept_id 기준) | §2.4, §3.2 | ✅ | `auth/rbac.py:42-48` `scope_dept()` | ax_team/ceo 전부서, 그외 자부서만 |
| 즉시/승인 편집 정책 분류 | §3.3, §7.2 | ✅ | `services/edit_policy.py:4-24` | IMMEDIATE/APPROVAL 집합 분리 |
| 승인필요 필드(절감률·목표달성·자동화·밸류체인) | §3.3, §9.1 #33 | ✅ | `edit_policy.py:12-15` | reduction_rate 등 승인 큐 경유 |
| status/stage/progress_rate 즉시반영 | §3.3, §9.1 #28 | ✅ | `edit_policy.py:8` | 설계대로 즉시 집합 포함 |
| 실삭제 AX팀만 | §3.2, §9.1 #10 | ✅ | `case_router.py:62` `require_ax` | AuditLog 기록 동반 |
| 변경요청 승인/반려 AX팀만 | §3.2 | ✅ | `approval_router.py:28` | |
| 대표(ceo) 읽기전용 | §9.1 #31 | ✅ | `rbac.py:23` `can_edit`, `case_router.py:38` | |
| Slack OAuth + 세션쿠키 | §3.5, §4.1 | ✅ | `auth_router.py:28-52`, `session.py` | state 검증·HMAC 서명 |
| **미매핑 사용자 접근거부** | §3.5(4), §4.1 | ⚠️ | `auth_router.py:40-44` | 설계는 "접근 거부+안내", 구현은 **staff로 자동 생성** → 설계 이탈 |
| ADMIN_SLACK_IDS 부트스트랩 | §3.5, §9.1 #22 | ✅ | `main.py:17-23` | 시작 시 ax_team upsert |
| OAuth 실패 재시도(최대 3회) | §4.1 | ❌ | 해당 로직 없음 | 즉시 400 에러 |

### D. 워크플로우 / API (§4, §7.5)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| `GET /cases`, `PATCH /cases/{id}`, `DELETE` | §7.5 | ✅ | `case_router.py:22,35,60` | 경로는 `/api/cases`(prefix 차이) |
| **`POST /cases` 케이스 생성** | §1.3, §4.3, §7.5, §9.1 #19 | ❌ | `case_router.py` 생성 엔드포인트 없음 | UI 직접 생성 요구인데 미구현 |
| 케이스 편집 즉시/승인 라우팅 | §4.3, §4.4 | ✅ | `case_router.py:44-51` | requires_approval 분기 |
| `GET/POST /cases/{id}/action-items` | §7.5 | ❌ | **action_item_router 없음** | 액션아이템 생성/조회 API 전무 |
| `GET /approvals`, `decide`, `cancel` | §7.5 | ✅ | `approval_router.py:12,26,36` | 완전 구현 |
| `POST /admin/import` | §7.5 | ✅ | `admin_router.py:17` | |
| `GET/POST /admin/users` 매핑관리 | §7.5, §3.2 | ❌ | 라우터 없음 | 사용자–부서–역할 매핑 UI/API 부재 |
| `GET/POST/PATCH /admin/lookups` | §7.5, §9.1 #11 | ❌ | 라우터 없음 | LookupValue 관리 API 부재 |
| `GET /reports/kpi` 실시간 집계 | §4.5, §7.5 | ✅ | `report_router.py:12`, `kpi.py` | stage∈{AX진행,완료} 한정 정확 |
| KPI 집계 대상 stage 한정 | §2.4, §4.5, §9.1 #27 | ✅ | `kpi.py:8,27` `AX_STAGES` | **정확히 준수** |
| `POST /reports/snapshot` 월말 KPI 확정 | §4.5, §7.5, §9.1 #14 | ❌ | snapshot 엔드포인트/서비스 없음 | `services/snapshot.py` 미존재 |
| `GET /reports` 스냅샷 이력조회 | §4.5, §7.5 | 🟡 | `report_router.py:22` | `scope=="dept"`만 필터 → 스냅샷 조회 불가 |
| 부서 AX 자체평가 보고서 | §9.1 #30 | ✅ | `report_router.py:35` `save_report` | |
| `/admin/analyze` 백그라운드 잡 | §8.2 | ✅ | `admin_router.py:42-57` | 상태 폴링(queued/running/done/failed) |
| 케이스단위 "✨ AI 분석" | §8.3 | ✅ | `admin_router.py:60`, `analysis.run_ai_analysis` | LLM/휴리스틱 폴백 |

### E. Seed / 엑셀 (§4.2)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| 엑셀 1회 seed → DB 진실원천 | §1.3, §2.4 | ✅ | `excel_import.py:91`, `seed.py` | 다중시트 파싱 |
| 재업로드 덮어쓰기 | §4.2 | 🟡 | `excel_import.py:97-98` | overwrite 동작은 있으나 **사전경고/명시확인 단계 없음** |
| 동적 컬럼매핑(Admin UI) | §1.5, §4.2, §9.2 #2 | ❌ | 고정 인덱스 파싱(`r[2]`,`r[5]`…) | Admin 동적 매핑 미구현(하드코딩) |
| ImportBatch 기록 | §4.2 | ✅ | `excel_import.py:101` | imported_by/overwrote 필드는 누락 |
| 11개 부서 플레이스홀더 | §1.5, §9.2 #1 | 🟡 | seed가 파일에서 부서명 추론 | 부서 마스터 미선재 |

### F. 기술스택 / 폴더구조 (§6, §7)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| FastAPI+SQLAlchemy+SQLite | §6 | ✅ | 전반 | |
| **Jinja2 + HTMX 서버렌더** | §6, §7.1 | ❌ | `app/templates`, `app/static` **디렉터리 없음** | 정적 mockup(`/mockup`)으로 대체 |
| models per-file 분리 | §7.1 | ⚠️ | 단일 `models/__init__.py` | 설계 폴더구조 이탈(주석에 "후속 리팩터"로 명시) |
| `services/snapshot.py` | §7.1, §7.2 | ❌ | 파일 없음 | KPI 스냅샷 직렬화 모듈 부재 |
| `services/ri.py` (RI 계산) | §8.1 | ✅ | `services/ri.py` | 설계에 명시 없으나 §8 RI 이식 |
| `tests/` 단위테스트 | §7.1 | ❌ | 디렉터리 없음 | KPI·권한·전이 테스트 부재 |
| NSSM/mkcert HTTPS 가이드 | §1.5, §3.5, §7.1 | ✅ | `README.md:47-61` | 배포 가이드 문서화 |
| .env 구성(OAuth·SESSION·OPENAI) | §8.6 | ✅ | `config.py:11-18` | 모든 키 정의 |

### G. 열거형 / 상태값 (§7.4)

| 요구항목 | 설계 근거(§) | 구현 상태 | 근거 파일:라인 | 비고 |
|---|---|---|---|---|
| user.role 3+1값 | §7.4 | ✅ | `rbac.py:13` | ceo 추가 |
| change_request.status 4값 | §7.4 | ✅ | `change_workflow.py` | pending/approved/rejected/cancelled |
| case.stage 4값 | §7.4 | ✅ | `models:47`, `kpi.py:32` | 일반업무/AX후보/AX진행/완료 |
| progress_rate 0~100 정수 | §7.4 | ✅ | `models:48` Integer | |
| value_chain_level 단일값 | §9.1 #12 | ✅ | `models:54` 단일 String | |

---

## 부합도 점수

**종합 부합도: 72%**

산정 근거 (가중 항목 기준, 핵심 모델/워크플로우에 가중치):

| 영역 | 가중 | 충족도 | 비고 |
|---|---|---|---|
| 시스템성격/범위(Meeting 제외 포함) | 15% | 95% | Meeting 제외 완벽 준수 |
| 데이터 모델 8객체 | 20% | 80% | 8객체 모두 존재, 일부 필드 누락 |
| RBAC/권한 | 20% | 85% | 미매핑 처리 이탈 1건 |
| 워크플로우/API | 25% | 55% | 생성·매핑·lookup·snapshot API 다수 누락 |
| Seed/엑셀 | 10% | 60% | 동적 컬럼매핑·재업로드 경고 미구현 |
| 기술스택/폴더/테스트 | 10% | 55% | 프런트(Jinja2/HTMX)·tests 부재 |

가중 합 ≈ **72%**. 1단계 스캐폴드로서 **데이터 모델·승인 워크플로우·KPI 집계·Meeting 제외 등 설계 핵심 골격은 충실**하나, **CRUD 생성 계열 API와 관리(admin) API, 프런트엔드 계층이 미완**이다.

---

## 주요 이탈 / 누락 목록 (우선순위순)

**❌ 미구현 (설계 명시 요구)**
1. **케이스 생성 `POST /cases` 부재** (§4.3, §9.1 #19) — UI 직접 생성이 핵심 요구인데 없음. 현재 seed로만 Case 적재 가능.
2. **ActionItem 라우터 전무** (§7.5 `GET/POST /cases/{id}/action-items`) — 모델만 있고 조회·생성 API 없음. 케이스 상세 '액션 추가' 기능 불가.
3. **관리 API 누락**: 사용자–부서–역할 매핑(`/admin/users`)·LookupValue 관리(`/admin/lookups`) — AX팀 전용 관리 기능 2종 부재. 미매핑 staff에 부서 배정 경로가 없음.
4. **KPI 월말 스냅샷 확정 `POST /reports/snapshot` + `services/snapshot.py` 부재** (§4.5, §9.1 #14) — Report 모델에 `scope=snapshot` 필드만 있고 생성·조회 경로 없음. "이전 감사 조회" 요구 미충족.
5. **프런트엔드 계층(Jinja2+HTMX)·`templates/`·`static/` 부재** (§6, §7.1) — 정적 mockup으로 대체. 인라인 편집 UI 미구현.
6. **동적 컬럼매핑 Admin UI 부재** (§1.5, §4.2) — 엑셀 파싱이 고정 인덱스 하드코딩.
7. **`tests/` 단위테스트 부재** (§7.1) — KPI·권한·승인전이 검증 테스트 없음.

**⚠️ 설계 이탈 (설계와 다르게 구현)**
8. **미매핑 Slack 사용자 처리 이탈** (§3.5(4), §4.1) — 설계는 "접근 거부 화면", 구현은 `auth_router.py:40-44`에서 **staff로 자동 생성**. 미매핑 사용자가 자동으로 시스템 접근을 얻는 보안/거버넌스 이탈.
9. **모델 per-file 구조 미준수** (§7.1) — 단일 `models/__init__.py`. 코드 자체 주석에 "후속 리팩터 대상"으로 인지됨.

**🟡 부분구현 (필드/세부 누락)**
10. 모델 필드 누락: `User.active`, `ImportBatch.imported_by/overwrote`, `LookupValue.label`, `AuditLog`의 field/old/new 분리(현재 detail 단일 텍스트).
11. 실삭제 시 연결된 pending ChangeRequest 자동 cancelled 처리 누락 (§4.6) — cascade는 action_items만 설정.
12. 재업로드 덮어쓰기 사전 경고/명시 확인 단계 누락 (§4.2) — 무조건 덮어씀.

**✅ 특기할 준수 사항**
- **Meeting 전면 제외**가 모델·라우터·DB·필드 전체에서 완벽히 지켜짐 (검색 0건).
- **승인 워크플로우**(상태전이 단방향 + supersede + 승인 전 KPI 불변)가 §4.4 의도대로 정확히 구현.
- **KPI 집계 대상 stage∈{AX진행,완료} 한정**(§9.1 #27)이 `kpi.py`에 정확히 반영.
- WAL 모드·ADMIN_SLACK_IDS 부트스트랩·AI분석 2단계(결정론/LLM 폴백) 충실.
