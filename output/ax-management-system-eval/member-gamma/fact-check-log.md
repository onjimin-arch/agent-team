# 보안·권한 로직 검증 로그 (member-gamma)

대상: 바로고 AX 통합 관리 시스템 (FastAPI 내부망 RBAC 웹앱)
루트: `ax-management-system`
검증일: 2026-06-18
검증자: member-gamma (보안·로직 검증가)

---

## 검증 요약

총 14건 발견 — **Critical 4 / High 4 / Medium 4 / Low 2**.

가장 심각한 문제는 **인증 자체를 무력화하거나 위조할 수 있는 구성 결함이 코드와 커밋된 `.env`에 함께 존재**한다는 점입니다.

| # | 심각도 | 발견 | 근거 |
|---|--------|------|------|
| F1 | **Critical** | `DEV_AUTH=true`가 코드 기본값이자 커밋된 `.env` 값 — 인증 전면 우회 백도어 | `config.py:16`, `.env:10`, `rbac.py:34-38` |
| F2 | **Critical** | 실시크릿(OpenAI 키, Slack client_secret) 평문 커밋 | `.env:5,13` |
| F3 | **Critical** | `SESSION_SECRET` 기본값 `dev-secret` + `.env`는 `change-me-in-prod` — 세션 쿠키 위조 가능 | `config.py:14`, `.env:6`, `session.py:24` |
| F4 | **Critical** | 요청자가 ax_team이면 자기 ChangeRequest를 자기가 승인 가능 (직무분리 부재) | `approval_router.py:26-33`, `change_workflow.py:35-51` |
| F5 | High | 세션 쿠키에 `Secure` 미설정 — 평문(HTTP)에서 쿠키 탈취 | `auth_router.py:50`, `session.py` |
| F6 | High | 승인 큐 decide/cancel에 부서 스코프 미적용 — 모든 ChangeRequest를 ax_team 전체가 처리 (의도일 수 있으나 IDOR/감사 누락) | `approval_router.py:26-45` |
| F7 | High | `redirect_uri`를 요청 호스트(`request.url_for`)에서 생성 — Host 헤더 주입 시 OAuth code 탈취 가능 | `auth_router.py:14-15,28-35` |
| F8 | High | `edit_case`가 신규값을 old_val 자리에도 전달 → 승인 큐 old_val 오염(감사·표시 결함) | `case_router.py:47` |
| F9 | Medium | OAuth state는 검증하나 토큰 교환 응답의 `id_token`/`nonce` 미검증, userInfo의 email 도메인 미검증 | `slack_oauth.py`, `auth_router.py:28-44` |
| F10 | Medium | 미등록 Slack 사용자 자동 가입(role=staff) — 워크스페이스 외부인이 들어오면 자동 계정 생성 | `auth_router.py:40-43` |
| F11 | Medium | `delete_case` 실삭제에 부서 스코프 없음 — ax_team이면 전 부서 케이스 삭제(대량 삭제 위험), 확인 절차 없음 | `case_router.py:60-70` |
| F12 | Medium | analyze 잡 상태 조회(`/api/admin/analyze/{job_id}`)에 인증 데코레이터 없음 | `admin_router.py:52-57` |
| F13 | Low | `can_edit`가 ceo만 차단 — staff/dept_head는 본인부서 KPI 외 즉시필드 모두 편집 가능(설계상 허용이나 owner/stage 변경 권한 광범위) | `rbac.py:23-24`, `case_router.py:36-57` |
| F14 | Low | 세션 만료 검증이 `_ts` 단방향만(클록 스큐/미래 ts 미처리), 쿠키 회전·무효화 없음 | `session.py:36` |

SQL Injection: SQLAlchemy ORM(`filter(Case.dept_id == ...)`)·`db.get()`만 사용하며 raw SQL/문자열 포매팅 쿼리 없음 → **주입 위험 낮음**. RBAC 부서 스코프는 조회/KPI 경로에 대체로 강제되나, **승인·삭제 경로에서 누락**됩니다.

---

## 항목별 검증 결과

### 1. Slack OAuth (state CSRF / redirect_uri / 토큰 교환)

**state CSRF 방어 — 부분 통과.**
`auth_router.py:22-24`에서 `secrets.token_urlsafe(16)`로 state 생성, `oauth_state` 쿠키(httponly, samesite=lax, max_age=600)에 저장 후 콜백에서 `state != request.cookies.get("oauth_state")`로 비교(`:30`). 기본적인 CSRF 방어는 존재. 다만 비교가 단순 `!=`(상수시간 비교 아님)이고, state-쿠키 바인딩만 있고 세션 바인딩은 없음 → 실질 위험은 낮으나 개선 권고.

**F7 (High) redirect_uri Host 주입.**
`_redirect_uri()`가 `request.url_for("slack_callback")`로 redirect_uri를 만든다(`:14-15`). 이 값은 들어온 요청의 Host/scheme에 의존한다. 리버스 프록시가 `Host`/`X-Forwarded-Host`를 신뢰·전달하면, 공격자가 조작한 Host로 로그인 링크를 유도해 **authorization code를 공격자 도메인으로 리다이렉트**시킬 수 있다(Slack 앱에 와일드카드/다중 redirect 등록 시 특히). 권고: redirect_uri를 설정값(고정 절대 URL)으로 못박고, authorize와 callback에서 동일 상수를 사용.

**F9 (Medium) 토큰/ID 검증 미흡.**
`exchange_code`(`slack_oauth.py:21-27`)는 `access_token` 존재만 확인(`auth_router.py:33`). OIDC `id_token` 서명/`nonce`/`aud`/`iss` 검증 없음, userInfo의 `email` 도메인(사내 도메인) 화이트리스트 검증도 없음. 내부망 가정이라 해도, 토큰 교환은 정상 HTTPS이나 응답 신뢰 검증이 약함.

**부가:** `urllib.request.urlopen` 직접 사용 — 타임아웃 미설정(`slack_oauth.py:26,32`)으로 외부 응답 지연 시 행(hang) 가능(가용성). 권고: `timeout=` 지정.

### 2. 세션 쿠키 (서명/위변조/만료/플래그)

**서명 방식 — HMAC-SHA256 적절.**
`session.py:21-38`. payload(JSON+`_ts`)를 base64url, `hmac.new(secret, raw, sha256)`로 서명, 검증 시 `hmac.compare_digest`로 상수시간 비교 → **위변조 방어 로직 자체는 견고**.

**F3 (Critical) 비밀키가 약함/예측 가능.**
서명 강도는 전적으로 `session_secret`에 의존하는데, 코드 기본값이 `"dev-secret"`(`config.py:14`), 커밋된 `.env`는 `change-me-in-prod`(`.env:6`). 둘 다 공개/추측 가능한 값이라 **공격자가 임의 role(ax_team)·dept_id로 세션 쿠키를 직접 위조**할 수 있다. 운영 전 강제 교체·검증 부재.
공격 시나리오: 공격자가 `sign({"role":"ax_team",...})`를 위 시크릿으로 직접 계산 → `ax_session` 쿠키로 주입 → AX팀 전권 획득(승인/삭제/임포트).

**F5 (High) Secure 플래그 누락.**
`auth_router.py:50` `set_cookie(sess.COOKIE, token, httponly=True, max_age=..., samesite="lax")` — `secure=True` 없음. `oauth_state` 쿠키(`:24`)도 동일. 내부망이라도 HTTP 평문 구간이 있으면 쿠키 가로채기 가능. SameSite=lax는 설정됨(CSRF 일부 완화), HttpOnly는 설정됨(XSS 탈취 완화). 권고: 운영에서 `secure=True` 강제.

**F14 (Low) 만료/무효화.**
`verify`는 `now - _ts > MAX_AGE`만 검사(`session.py:36`). 미래 `_ts`(클록 스큐/위조 시도) 음수 처리 없음. 서버측 세션 무효화(로그아웃 후 토큰 폐기, 비밀 회전)가 없어 탈취 토큰은 12h간 유효. 로그아웃은 쿠키 삭제만 하므로 탈취본은 계속 유효.

### 3. RBAC 부서 스코프 강제

**조회·KPI 경로 — 통과.**
`scope_dept`(`rbac.py:42-48`)가 ax_team/ceo는 임의 부서, 그 외는 `dept_id != user.dept_id`면 403. `list_cases`(`case_router.py:26-29`), `kpi_view`(`report_router.py:13-18`), `list_reports`(`report_router.py:25-29`)에서 호출/필터 적용됨. `edit_case`도 `scope_dept(user, case.dept_id)`로 타부서 케이스 편집 차단(`case_router.py:43`). 부서 스코프 자체는 대체로 일관 적용.

**우회 경로 점검:**
- `list_cases`에서 staff가 `dept` 파라미터 미지정 시 → `scope_dept(user, None)`은 `user.dept_id` 반환 → 본인부서로 필터됨. **우회 불가(정상).**
- 단, **dev_auth=true이면 헤더 `x-role: ax_team`/`x-dept`만으로 임의 부서·임의 역할 가장** → 부서 스코프 전면 무력화(F1과 결합).

**F13 (Low) 편집 권한 과대.**
`can_edit`은 ceo만 false(`rbac.py:23-24`). staff도 본인부서 케이스의 stage/owner/progress/asis 등 즉시필드 전부 편집 가능. 설계 의도일 수 있으나, staff가 `owner` 자유텍스트·`stage`를 임의 변경 가능 → 부서 내 권한 세분화 부재.

### 4. 승인 워크플로우 (ChangeRequest 우회 / 자기승인)

**승인 필요 필드 우회 — 통과(부분).**
`edit_case`(`case_router.py:44-50`)는 `requires_approval(field)`면 즉시반영 없이 `submit()`으로 큐 등록, `IMMEDIATE` 집합 필드만 직접 `setattr`. APPROVAL 필드(reduction_rate 등)를 IMMEDIATE 경로로 우회 불가(두 집합 분리, `edit_policy.py`). **직접 반영 우회는 차단됨.**
주의: patch에 APPROVAL/IMMEDIATE 어디에도 없는 임의 필드명을 주면 둘 다 걸리지 않아 **무시**됨(silently dropped) — 데이터 무결성상 안전하나 사용자에겐 무피드백.

**F4 (Critical) 자기승인 가능.**
`decide`(`approval_router.py:26-33`)는 `require_ax`만 검사하고 **요청자(`cr.requester`)와 승인자(`user.name`) 동일 여부를 검사하지 않는다**. ax_team 사용자는 자신이 올린 KPI 변경 요청(reduction_rate 등)을 **스스로 승인**할 수 있다. 직무분리(maker-checker) 위배.
공격/오용 시나리오: ax_team 담당자가 자기 부서 절감률을 임의로 높여 제출 → 본인이 즉시 approve → KPI 조작. `_apply`(`change_workflow.py:54-62`)가 그대로 반영.
권고: `decide`에서 `cr.requester == user.name`이면 403(또는 2인 승인 정책).
추가로 식별 키가 `user.name`(표시명) 기반이라 동명이인/이름변경 시 직무분리·취소권한 판단이 깨질 수 있음 → `slack_id` 기반 비교 권고(`approval_router.py:42`의 cancel 권한도 동일 이슈).

**F8 (High) old_val 오염.**
`edit_case`가 `submit(db, case, field, val, val, user.name)`을 호출 — 시그니처는 `submit(db, case, field, new_val, raw_val, requester)`(`change_workflow.py:13`). 즉 `raw_val` 자리에 신규값을 넣는 것은 맞으나, 큐의 `old_val`은 `submit` 내부에서 `getattr(case, field)`로 현재값을 다시 읽어 채우므로(`:23`) old_val 자체는 정상. **그러나** 호출부 4번째 인자 `new_val`과 5번째 `raw_val`이 모두 동일 `val`이라 의미 중복이며, `new_val`을 클라이언트 표시값/`raw_val`을 적용값으로 분리하려던 설계 의도가 무력화됨. 표시·적용 분리 로직 회귀 위험. 권고: 호출부 인자 의미 명확화 및 검증.

**F6 (High) 승인 IDOR/스코프.**
`decide`/`cancel`은 `crid`로 `db.get(ChangeRequest, crid)`만 하고 해당 cr의 케이스 부서를 사용자 부서와 대조하지 않음(`approval_router.py:29-32, 39-44`). decide는 ax_team 전권이라 설계상 전부서 처리가 의도일 수 있으나, cancel은 `cr.requester != user.name`이면 비-ax는 막히긴 함. 그래도 ChangeRequest를 부서 단위로 격리하지 않아 ax_team 내부에서 부서 책임 경계가 없음(감사·최소권한 관점 개선 필요).

### 5. DEV_AUTH 백도어

**F1 (Critical).**
`config.py:16` `dev_auth: bool = True` — **코드 기본값이 True**. `.env:10`도 `DEV_AUTH=true`로 커밋. `rbac.py:34-38`: dev_auth면 세션 없이도 `x-role`/`?role=`, `x-dept`/`?dept=` 헤더·쿼리만으로 Principal 생성, 기본 role=`ax_team`. 즉 **인증 없이 `?role=ax_team`만 붙이면 AX팀 전권**.
공격 시나리오: 운영 배포 시 `.env`를 그대로 쓰거나 `DEV_AUTH`를 명시적으로 false 처리하지 않으면, 외부에서 `GET /api/cases?role=ax_team&dept=...`, `DELETE /api/cases/{id}?role=ax_team`로 전 부서 데이터 조회·삭제·임포트 가능. `/health`가 `dev_auth` 값을 그대로 노출(`main.py:37`)해 공격자가 백도어 활성 여부를 사전 탐지 가능.
권고: 기본값을 `False`로, 운영 환경에서 dev_auth=true면 기동 거부(fail-closed), `/health`에서 dev_auth 노출 제거.

### 6. 입력 검증 / SQLi / 대량삭제·IDOR

**SQLi — 위험 낮음.** 전 경로 ORM 비교식/`db.get`만 사용. 문자열 보간 쿼리 없음. `import_file`의 `db.query(Case).filter(Case.dept_id == dept_id).delete()`(`excel_import.py:98`)도 파라미터 바인딩.

**F11 (Medium) 대량삭제/실삭제.** `import_file(overwrite=True)`(기본값)이 해당 부서 케이스를 통째 삭제 후 재적재(`excel_import.py:97-98`). `import_excel` 엔드포인트(`admin_router.py:17-27`)는 ax_team이면 임의 `dept`로 호출 가능 → 잘못된 dept 지정 시 **타 부서 전 케이스 소거**. 확인·드라이런·백업 없음. `delete_case`도 단건이나 부서 스코프 없이 ax_team이면 전부서 삭제(`case_router.py:60-70`). AuditLog는 남기나 복구 수단 없음.

**파일 업로드 검증 부재.** `import_excel`이 `file.filename`을 `uuid + filename`으로 저장(`admin_router.py:23`) — 경로주입은 uuid 접두로 일부 완화되나 확장자/MIME/사이즈 검증 없음. `openpyxl.load_workbook`에 신뢰 안 된 파일 직접 전달(`excel_import.py:26`) — zip-bomb/대용량 DoS 가능. 권고: 확장자 화이트리스트·사이즈 상한.

### 7. 관리자 엔드포인트 접근 통제 (/api/admin/*)

- `import`(`:21`), `analyze`(`:44`), `analyze-case`(`:63`) — 모두 `require_ax(current_user(...))` 적용. **통과.**
- **F12 (Medium):** `analyze_status`(`admin_router.py:52-57`)는 `current_user`/`require_ax` **없음**. 인증 없이(dev_auth면 더 쉽게) `GET /api/admin/analyze/{job_id}` 호출 가능. `JOBS` 딕셔너리에 `dept_id`·에러 메시지가 들어가 정보노출(소량)이며, job_id가 `uuid4hex[:8]`(32bit)로 짧아 추측 가능성도 일부. 권고: 인증 추가.
- `JOBS`가 프로세스 인메모리 전역(`admin_router.py:33,47`) — 멀티워커/재시작 시 유실, 동시성 보호 없음(기능 결함, 보안 외).

### .env 시크릿 점검 (값 비노출)

**F2 (Critical):** 저장소에 커밋된 `.env`에 **실제 OpenAI API 키(sk-proj-...)와 Slack client_secret**이 평문 포함(`.env:5,13`). 키 형식·길이상 실 키로 보임. 즉시 **로테이션(폐기·재발급) + git 히스토리 제거 + `.gitignore` 등록** 필요. 또한 `SESSION_SECRET`/`DEV_AUTH`가 안전치 않은 값으로 커밋됨(F1, F3).

---

## 수정 권고

우선순위 순.

**즉시(Critical):**
1. **시크릿 로테이션·제거(F2):** OpenAI 키·Slack client_secret 즉시 폐기 후 재발급. `.env`를 `.gitignore`에 추가하고 git 히스토리에서 제거(`git filter-repo`/BFG). 저장소에는 `.env.example`(더미값)만.
2. **DEV_AUTH fail-closed(F1):** `config.py` 기본값 `dev_auth=False`. 기동 시 `dev_auth and not is_local`이면 예외로 부팅 중단. `.env`에서 `DEV_AUTH=true` 제거. `/health`에서 `dev_auth` 노출 제거(`main.py:37`).
3. **SESSION_SECRET 강제(F3):** 기본값 제거하고 미설정 또는 `dev-secret`/`change-me-*`면 기동 거부. 운영은 32바이트+ 랜덤. 비밀 회전 절차 마련.
4. **자기승인 차단(F4):** `approval_router.decide`에서 `cr.requester == 승인자`면 403. 비교는 `slack_id` 기반으로. 가능하면 2인 승인 정책.

**높음(High):**
5. **쿠키 Secure(F5):** `ax_session`·`oauth_state` set_cookie에 `secure=True`(운영). HTTPS 종단 보장.
6. **redirect_uri 고정(F7):** 설정값 절대 URL을 authorize/callback 양쪽에서 사용. 프록시 `Host`/`X-Forwarded-*` 신뢰 정책 점검.
7. **승인 식별 키(F6/F8):** 요청자·취소·승인 권한 비교를 `user.name` 대신 `slack_id`로. `edit_case`의 `submit` 호출 인자(new_val/raw_val) 의미 명확화 및 단위테스트.

**중간(Medium):**
8. **analyze_status 인증(F12):** `require_ax(current_user(request))` 추가, job_id 엔트로피 상향.
9. **임포트/삭제 가드(F11):** `import_excel`·`delete_case`에 dept 스코프/확인 플래그·백업 스냅샷. 파일 확장자·사이즈 화이트리스트. overwrite 기본 False 검토.
10. **OAuth 응답 검증(F9/F10):** id_token 검증, email 사내 도메인 화이트리스트, 미등록자 자동가입 대신 승인 대기 큐.

**낮음(Low):**
11. 세션 만료에 미래 `_ts` 음수 가드, 서버측 로그아웃 무효화(jti 블랙리스트 또는 secret 회전), OAuth state 상수시간 비교, `urlopen` 타임아웃 설정.
