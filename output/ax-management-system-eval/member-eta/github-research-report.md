# GitHub Research Report — 바로고 AX 통합 관리 시스템 벤치마크

**작성:** member-eta (GitHub Researcher / 라이선스 감사)
**평가 대상:** `ax-management-system` (FastAPI + SQLAlchemy 2.0 + SQLite WAL + Jinja2/HTMX + Slack OAuth + RBAC, 내부망 단일 PC 관리 웹앱)
**작성일:** 2026-06-18

---

## 탐색 조건

평가 대상의 성격(내부망·단일 PC·소규모 인원·서버사이드 렌더·Slack 로그인·역할/부서 스코프 RBAC)에 맞춰 다음 5개 축으로 비교군을 선정했다.

| 축 | 검색 키워드 | 목적 |
|---|---|---|
| A. 공식 풀스택 레퍼런스 | `full-stack-fastapi-template`, `tiangolo`, Alembic, OAuth | "정석" 기준선(인증·마이그레이션·테스트·설정) |
| B. 비동기 프로덕션 보일러플레이트 | `FastAPI-boilerplate`, SQLAlchemy 2.0, 세션, 백그라운드 잡 | 세션 인증·잡 큐·CRUD 패턴 비교 |
| C. Admin/RBAC 프레임워크 | `fastapi-amis-admin`, `fastapi-user-auth`, Casbin RBAC | 관리화면·RBAC 구현 방식 비교 |
| D. Slack/OAuth 통합 패턴 | `fastapi-oauth-examples`, authlib, itsdangerous, slack_sdk.oauth | OAuth 코드 플로우·서명 세션·state CSRF |
| E. HTMX/Jinja 서버렌더 | `fastapi-htmx`, `fasthx`, Jinja2 hypermedia | 무빌드 서버사이드 렌더 패턴 |

대상 앱은 **의도적으로 외부 의존성을 최소화**(requirements.txt 8줄, Slack OAuth·세션을 stdlib `urllib`/`hmac`로 자체 구현)한 점이 특징이므로, "경량 자체구현 vs 라이브러리 사용"의 트레이드오프를 핵심 비교 관점으로 삼았다.

---

## 탐색 결과 요약

| # | 레포 | 스타(근사) | 라이선스 | 비교 축 | 핵심 패턴 |
|---|---|---|---|---|---|
| 1 | fastapi/full-stack-fastapi-template | ~43.7k | MIT | A | JWT·SQLModel·**Alembic**·Pytest·Playwright·Pydantic Settings |
| 2 | benavlabs/FastAPI-boilerplate | ~2.0k | MIT | B | 서버사이드 세션+CSRF·OAuth·SQLAlchemy 2.0 async·**Taskiq** 잡·Alembic |
| 3 | amisadmin/fastapi-amis-admin | ~1.6k | Apache-2.0 | C | django-admin식 자동 admin·SQLAlchemy 2.0 모델 지원 |
| 4 | amisadmin/fastapi-user-auth | ~0.7k | Apache-2.0 | C | **Casbin** 기반 RBAC·다중 입도 권한·시각 관리 UI |
| 5 | lukasthaler/fastapi-oauth-examples | ~62 | MIT | D | authlib OAuth2 code flow·Starlette SessionMiddleware 서명 쿠키 |
| 6 | volfpeter/fasthx | (소규모) | MIT | E | 데코레이터 기반 HTMX 서버렌더(`@jinja.hx`/`page`) |
| 7 | maces/fastapi-htmx | (소규모) | (MIT 계열) | E | 데코레이터로 Jinja2 보일러플레이트 감축 |

**한 줄 결론:** 대상 앱은 라우터/서비스 분리, RBAC 스코프, 감사로그, 승인 워크플로우 등 **도메인 설계는 비교군 대비 견고**하나, 인증 세션·마이그레이션·테스트·DI·백그라운드 잡 **인프라 레이어는 업계 표준(라이브러리 위임)을 우회한 자체 경량 구현**이라 운영 확장 시 리스크가 집중된다.

---

## 레포별 상세 분석

### 1. fastapi/full-stack-fastapi-template (MIT, ~43.7k) — 기준선
- **URL:** https://github.com/fastapi/full-stack-fastapi-template
- FastAPI 공식 레퍼런스. JWT 인증 + 안전한 패스워드 해싱, **Alembic 마이그레이션**, Pytest(백엔드) + Playwright(E2E), Pydantic Settings 기반 설정.
- 대상 앱과의 차이: 대상은 Alembic·테스트·해싱이 전무. 단, 대상은 Slack OIDC 외부 IdP에 위임하므로 자체 패스워드 저장이 없는 것은 오히려 합리적 선택.
- **시사점:** "마이그레이션·테스트 부재"는 스캐폴드 단계라도 가장 먼저 메울 갭. 스키마가 14개 컬럼 추가 등으로 자주 변하는 도메인(Case 모델 40+ 컬럼)에서 `create_all`만으로는 운영 중 컬럼 추가가 불가능.

### 2. benavlabs/FastAPI-boilerplate (MIT, ~2.0k) — 세션·잡 표준
- **URL:** https://github.com/benavlabs/FastAPI-boilerplate
- 서버사이드 세션 + **CSRF 토큰**, OAuth(Google), SQLAlchemy 2.0 async, **Taskiq** 워커(Redis/RabbitMQ), Alembic(prod-confirm 게이트), FastCRUD.
- 대상 앱과의 차이: 대상의 백그라운드 잡은 `BackgroundTasks` + **모듈 전역 `analysis.JOBS` 딕셔너리**로 상태 추적 → 프로세스 재시작 시 잡 상태 소실, 멀티워커 불가. 단일 PC·uvicorn 단일 워커 환경에서는 "지금은" 동작하나, 표준은 잡 상태를 DB/브로커에 영속화한다(대상 앱엔 이미 `ImportBatch` 테이블이 있으므로 잡 테이블 추가로 정합 가능).
- 대상엔 **CSRF 방어가 없음**(상태 변경 PATCH/POST가 쿠키 인증 기반). state CSRF는 OAuth 콜백에만 적용됨.

### 3. amisadmin/fastapi-amis-admin (Apache-2.0, ~1.6k) — Admin 자동화
- **URL:** https://github.com/amisadmin/fastapi-amis-admin
- django-admin 스타일 자동 CRUD admin. SQLAlchemy 2.0 모델 지원.
- 대상 앱과의 차이: 대상은 admin UI를 직접 구현(목업 HTML + 향후 HTMX). 컬럼 매핑/일괄 적재 Admin UI가 "잔여 과제"로 남아 있어, amis-admin류로 대체하면 공수 절감 가능하나 Apache-2.0 의존성·러닝커브·Amis 프론트 종속이 트레이드오프.

### 4. amisadmin/fastapi-user-auth (Apache-2.0, ~0.7k) — Casbin RBAC
- **URL:** https://github.com/amisadmin/fastapi-user-auth
- **Casbin** 정책 엔진 기반 RBAC, 다중 입도(메뉴/페이지/필드) 권한.
- 대상 앱과의 차이: 대상 RBAC는 4개 역할(`ax_team/dept_head/staff/ceo`)을 `Principal` 데이터클래스 + `scope_dept()`/`require_ax()` 함수로 **코드에 하드코딩**. 규모가 작고 정책이 단순하면 이 방식이 명료하고 충분하다(Casbin은 오버엔지니어링일 수 있음). 다만 역할/권한이 늘면 정책 외부화가 필요.

### 5. lukasthaler/fastapi-oauth-examples (MIT, ~62) — OAuth/세션 정석
- **URL:** https://github.com/lukasthaler/fastapi-oauth-examples
- authlib로 OAuth2 code flow, **Starlette SessionMiddleware 서명 쿠키**(itsdangerous), state CSRF는 authlib가 내부 처리.
- 대상 앱과의 차이: 대상은 동일 목표를 **stdlib `urllib.request` + 자체 `hmac`(session.py)**로 구현. 기능적으로 동등하나 (a) `urllib.request.urlopen`은 타임아웃 미지정 → Slack 응답 지연 시 무한 블로킹, (b) 토큰 검증·만료만 있고 토큰 회전/무효화·동시 만료 처리는 authlib/slack_sdk 대비 빈약, (c) `session_secret` 기본값이 `"dev-secret"`이라 운영에서 미설정 시 위조 가능. 표준 라이브러리(`slack_sdk.oauth`, authlib)는 이런 엣지를 검증된 코드로 처리.

### 6~7. fasthx / fastapi-htmx (MIT 계열) — HTMX 서버렌더
- **URL:** https://github.com/volfpeter/fasthx , https://github.com/maces/fastapi-htmx
- 라우트에 데코레이터를 붙여 JSON/HTML 협상, Jinja 보일러플레이트 감축.
- 대상 앱과의 차이: 대상은 현재 라우터가 **순수 JSON 반환**(`_ser()` dict)이고 프런트는 목업 정적 파일. README상 HTMX는 "예정". HTMX 전환 시 fasthx의 "동일 핸들러가 JSON·HTML 동시 응답" 패턴이 기존 JSON API를 유지하며 점진 도입하기에 적합.

---

## 크로스 레포 공통 패턴

비교군 5~7개에서 반복적으로 관찰되는, 대상 앱이 **부분적으로만 따른** 공통 표준:

1. **마이그레이션 = Alembic** (1·2·기타 대부분). `Base.metadata.create_all()`은 초기 부트스트랩 전용이고, 운영 스키마 진화는 Alembic이 사실상 표준.
2. **설정 = Pydantic Settings** (1·2 + 대상도 채택 ✅). 대상은 `BaseSettings`를 올바르게 사용 — 이 항목은 표준 부합.
3. **인증 세션 = 검증된 라이브러리에 위임** (authlib / Starlette SessionMiddleware / slack_sdk.oauth). 자체 HMAC 구현은 드묾.
4. **백그라운드 잡 = 영속 상태 + 외부 워커**(Taskiq/Celery/RQ) 또는 최소한 DB 영속 잡 테이블. 인메모리 dict는 데모 수준.
5. **테스트 = Pytest 기본 탑재** (1·2). 보일러플레이트조차 테스트 디렉터리를 기본 포함.
6. **DI = FastAPI `Depends`** (전부 + 대상도 `get_db` ✅). 대상은 DB 세션 DI는 표준이나, `current_user`를 `Depends`가 아니라 **핸들러 내부에서 직접 호출**(`current_user(request)`)해 의존성 그래프/오버라이드(테스트 시 인증 목킹)에서 벗어남.
7. **SQLAlchemy 2.0 스타일 = `DeclarativeBase` + `Mapped[]` + `mapped_column()`**. 대상은 `sqlalchemy>=2.0`를 쓰지만 모델은 **1.x 레거시 스타일(`declarative_base()` + `Column`)**. 동작은 하나 2.0 권장 패턴(타입 안전·IDE 지원) 미적용.

---

## 안티패턴

### 대상 앱에서 관찰된 것
| 안티패턴 | 위치 | 영향 | 비교군 대안 |
|---|---|---|---|
| **모듈 전역 가변 상태로 잡 추적** | `analysis.JOBS` dict (admin_router) | 재시작 시 소실, 멀티워커 불가 | DB 잡 테이블 / Taskiq |
| **`create_all`만으로 스키마 관리, Alembic 부재** | `db.init_db()` | 운영 중 컬럼 추가 불가, 데이터 마이그레이션 경로 없음 | Alembic (repo #1·#2) |
| **외부 HTTP 호출 타임아웃 미지정** | `slack_oauth.exchange_code/fetch_user`의 `urlopen` | Slack 지연 시 워커 블로킹 | `httpx`(timeout 기본) / slack_sdk |
| **약한 기본 시크릿** | `session_secret="dev-secret"`, `dev_auth=True` 기본 | 운영 미설정 시 세션 위조·인증 우회 | 부팅 시 필수값 검증/실패-닫기 |
| **상태변경 요청에 CSRF 미적용** | 쿠키 인증 PATCH/POST 전반 | 내부망이라도 CSRF 표면 존재 | CSRF 토큰 (repo #2) |
| **인증을 `Depends`가 아닌 직접 호출** | `current_user(request)` 핸들러 내 호출 | 테스트 목킹·재사용·문서화 약화 | `Depends(current_user)` |
| **SQLAlchemy 1.x 레거시 매핑 스타일** | `models/__init__.py` 전체 `Column` | 타입 미보장, 2.0 이점 미활용 | `Mapped[]`/`mapped_column` |
| **`@app.on_event("startup")` (deprecated)** | `main.py` | FastAPI 0.110+에서 deprecated | lifespan 컨텍스트 매니저 |
| **단일 거대 모델 모듈** | `models/__init__.py` 9개 모델 1파일 | (경미, README도 후속 분리 명시) | per-file 모델 |

### 일반적으로 알려진(이 도메인에서 흔한) 안티패턴 — 대상은 회피함 ✅
- 패스워드 자체 저장/해싱 누락 → 대상은 Slack OIDC 위임으로 **회피**.
- 부서 스코프 누락(IDOR) → 대상은 `scope_dept()`로 **방어**.
- 감사 추적 부재 → 대상은 `AuditLog` 모델로 **확보**.
- 동시성/락 미고려 SQLite → 대상은 **WAL + check_same_thread=False**로 **선제 대응**.

---

## Planner를 위한 권고 스택·접근법

대상 앱의 "경량 자체구현" 철학(내부망·단일 PC)을 존중하되, 표준 갭 중 **운영 리스크가 큰 항목부터** 보강할 것을 권고한다.

**우선순위 1 (운영 차단급)**
- **Alembic 도입**: Case 모델이 40+ 컬럼으로 계속 확장(README "잔여 과제")되므로 `create_all` 단독은 운영에서 막힘. autogenerate로 점진 도입.
- **시크릿/설정 강제**: `dev_auth`·`session_secret`을 부팅 시 검증(운영에서 기본값이면 기동 실패). repo #1·#2의 Settings 검증 패턴 차용.
- **Slack HTTP 호출에 타임아웃**: `urlopen(..., timeout=10)` 또는 `httpx`/`slack_sdk.oauth`로 교체.

**우선순위 2 (확장성·신뢰성)**
- **백그라운드 잡 영속화**: 인메모리 `JOBS` → DB 잡 테이블(이미 있는 `ImportBatch` 패턴 재사용). 향후 분석 전용 PC(§8.4) 분리 시 Taskiq/RQ 고려.
- **테스트 도입**: Pytest + httpx TestClient로 RBAC 스코프(`scope_dept`)·승인 워크플로우(`change_workflow`) 회귀 테스트. 인증을 `Depends(current_user)`로 바꾸면 `app.dependency_overrides`로 목킹 용이.
- **CSRF**: 쿠키 세션 기반 상태변경에 토큰 적용(내부망이라도 권장).

**우선순위 3 (현대화·점진)**
- **SQLAlchemy 2.0 매핑 마이그레이션**: `DeclarativeBase` + `Mapped[]`/`mapped_column`. 신규 모델부터 적용 가능.
- **`@app.on_event` → lifespan** 전환.
- **HTMX 전환**: fasthx 데코레이터 패턴으로 기존 JSON API 유지하며 HTML fragment 점진 도입.

**채택하지 말 것(오버엔지니어링)**
- Casbin RBAC(repo #4): 4개 역할·단순 정책에는 과함. 현 함수형 RBAC 유지가 적절.
- fastapi-amis-admin 전면 도입: Amis 프론트 종속·Apache-2.0 의존성 추가. 컬럼 매핑 Admin UI는 자체 HTMX로 충분.
- PostgreSQL/Redis 전환: 내부망 단일 PC·소규모에서 SQLite WAL이 적합. 잡 영속화는 DB 테이블로 해결 가능.

---

## 라이선스 관점

### requirements.txt 의존성 라이선스 (내부망 사용 기준)
| 패키지 | 라이선스 | 내부망 리스크 |
|---|---|---|
| fastapi | MIT | 없음 |
| uvicorn[standard] | BSD-3-Clause | 없음 |
| sqlalchemy | MIT | 없음 |
| pydantic-settings | MIT | 없음 |
| jinja2 | BSD-3-Clause | 없음 |
| python-multipart | Apache-2.0 | 없음 |
| openpyxl | MIT | 없음 |
| openai | Apache-2.0 | 없음 (단, **데이터 외부 전송** 이슈 — 아래) |

- **카피레프트(GPL/AGPL/LGPL) 의존성 없음.** 전부 MIT/BSD/Apache-2.0 퍼미시브 → 내부 배포·수정·재배포에 라이선스 충돌 없음.
- **표기 의무:** Apache-2.0(`python-multipart`, `openai`)은 NOTICE·라이선스 고지 보존 의무가 있으나, 내부망 무배포 운영에서는 실질 부담 거의 없음. 외부 배포 전환 시 라이선스 텍스트 동봉 필요.
- **벤치마크 레포 이식 시 주의:** fastapi-amis-admin·fastapi-user-auth는 **Apache-2.0**(퍼미시브, 호환). 단 코드 스니펫 직접 복붙 시 출처·라이선스 고지 유지 권장. 표절 위험 패턴은 발견되지 않음(대상 앱은 자체 구현 위주).

### 내부망 사용상 가장 큰 라이선스/컴플라이언스 리스크 = **OpenAI 의존성(데이터 경계)**
- `openai>=1.40`는 라이선스 자체는 Apache-2.0으로 무해하나, **§8 LLM 2단계 분석이 부서 업무 데이터를 외부 OpenAI API로 전송**한다. 내부망 격리 정책과 충돌 가능 — 이는 라이선스가 아닌 **데이터 거버넌스 리스크**.
- 대상 앱은 `OPENAI_API_KEY` 미설정 시 **오프라인 휴리스틱 폴백**을 둔 점이 적절한 완충. Planner는 (a) LLM 경로를 분석 전용 PC로 분리(§8.4 명시)하거나 (b) 온프레미스 LLM(Ollama 등)으로 대체하는 옵션을 명문화할 것을 권고.

---

## 출처 목록

- Full Stack FastAPI Template: https://github.com/fastapi/full-stack-fastapi-template
- FastAPI 공식 프로젝트 제너레이션 문서: https://fastapi.tiangolo.com/project-generation/
- benavlabs/FastAPI-boilerplate: https://github.com/benavlabs/FastAPI-boilerplate
- amisadmin/fastapi-amis-admin: https://github.com/amisadmin/fastapi-amis-admin
- amisadmin/fastapi-user-auth: https://github.com/amisadmin/fastapi-user-auth
- lukasthaler/fastapi-oauth-examples: https://github.com/lukasthaler/fastapi-oauth-examples
- volfpeter/fasthx: https://github.com/volfpeter/fasthx
- maces/fastapi-htmx: https://github.com/maces/fastapi-htmx
- 00-Python/FastAPI-Role-and-Permissions: https://github.com/00-Python/FastAPI-Role-and-Permissions
- awesome-fastapi (큐레이션): https://github.com/mjhea0/awesome-fastapi
- slack_sdk.oauth API 문서: https://tools.slack.dev/python-slack-sdk/api-docs/slack_sdk/oauth/index.html
- Using HTMX with FastAPI (TestDriven.io): https://testdriven.io/blog/fastapi-htmx/
- SQLAlchemy 2.0 Declarative Mapping Styles: https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html
- SQLAlchemy 2.0 Table Configuration (mapped_column): https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
