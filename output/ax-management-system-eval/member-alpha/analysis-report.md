# 바로고 AX 통합 관리 시스템 — 코드 품질·아키텍처·핵심 로직 분석 (member-alpha)

## 개요

FastAPI + SQLAlchemy 2.0 + SQLite(WAL) 기반 내부망 RBAC 웹앱의 1단계 스캐폴드(약 1,018 LOC). 레이어 분리는 깔끔하고(router→service→model), stdlib 기반 세션/OAuth로 외부 의존성을 최소화한 설계가 돋보인다. 핵심 리스크는 RI 계산 비결정론, KPI 가중평균 미적용, 승인 통제 우회 경로, DB 유니크 제약 누락, 테스트 전무이다.

## 분석 결과

### 1. 레이어 분리·의존성 방향
- (양호) router→service/model/auth 단방향, 순환 의존 없음 — `case_router.py:6-8`
- (낮음) `routers/__init__.py`·`services/__init__.py` 빈 파일, `__all__` 부재 — `main.py:9`
- (낮음) 모델 단일 모듈 9클래스 집약(의도적) — `models/__init__.py:1-5`

### 2. RI 계산 (`ri.py`) — 정확성 핵심
- **(높음) 반복성 가중치가 batch 전체 min/max 분포에 의존** → 같은 업무도 함께 계산되는 구성/호출 단위(부서 전체 vs 일부)에 따라 RI가 달라짐 = "결정론" 약속 위배 — `ri.py:56-64`, `analysis/__init__.py:19-24`
- (중간) `normalize_frequency` 폴백이 매칭 실패 시 `20.0(수시)` 반환 → 미상 빈도 과대추정 — `ri.py:42`
- (중간) `FREQUENCY_MAP` 부분일치가 dict 순서 의존("주 2~3회" vs "주 2회") — `ri.py:30-32`
- (중간) `to_num`이 첫 숫자만 추출("3-5명"→3) — `ri.py:45-48`
- (중간) import 경로는 빈도 정규화하나 재분석 경로는 정규화된 freq 재사용 → 비대칭 — `excel_import.py:42` vs `analysis/__init__.py:20-22`

### 3. KPI 집계 (`kpi.py`)
- **(높음) `avg_reduction`이 단순 산술평균** — hours 가중 없어 부서 절감률 왜곡 — `kpi.py:38`
- (중간) ax_rate/saved_hours/resource_reduction_rate 분모 기준 불일치 — `kpi.py:29,37,40`
- (중간/차단) 설계서상 "계산식 미확정" 스텁 상태 — `kpi.py:2-3`

### 4. 데이터 모델 (`models/__init__.py`)
- **(높음) Case.code 부서 내 유니크 제약 부재** (index만) → 중복 코드 적재 가능 — `:23`
- (중간) ChangeRequest/AuditLog ondelete 미지정 → case 삭제 시 고아 레코드(ActionItem만 cascade) — `:68,86`
- (중간) `edit_policy.APPROVAL`의 `hours_before/hours_after`가 Case 모델에 컬럼 부재 → setattr 무효 — `edit_policy.py:13`, `change_workflow.py:62`
- (낮음) `datetime.utcnow` deprecated + naive — `:64-65`

### 5. excel_import / change_workflow / edit_policy
- **(높음) 하드코딩 컬럼 인덱스(r[8]…r[23])** → 양식 변동 시 조용히 오매핑 — `excel_import.py:42-50`
- (중간) overwrite=True 기본 → 재임포트 시 기존 Case 무조건 삭제, 의존 레코드 고아화 — `:97-103`
- (중간) 시트 미발견 시 조용히 0건 임포트(예외 없음) — `:11-21,35`
- (낮음) `decide`가 status!=pending이면 조용히 no-op — `change_workflow.py:37-38`

### 6. 에러·트랜잭션·동시성(WAL)·보안
- **(높음) 승인 우회**: 파생필드(hours/ri/weight)가 IMMEDIATE에 포함 → 클라이언트가 RI 직접 덮어써 KPI 통제 우회. 미지정 patch 키는 조용히 무시 — `edit_policy.py:5-9`, `case_router.py:44-51`
- **(높음) dev_auth 기본 true + dev 기본 역할 ax_team(전권)** → 운영 전환 누락 시 인증 없이 전권 — `config.py:16`, `rbac.py:35`
- (중간) `decide` action 무검증 → 임의 문자열이 else 분기로 cancel 처리 — `approval_router.py:27`, `change_workflow.py:44-46`
- (중간) `analysis.JOBS`가 프로세스 메모리 dict → 멀티워커/재시작 시 잡 상태 유실 — `analysis/__init__.py:14`
- (중간) slack_oauth urlopen 타임아웃 미설정(DoS 표면) — `slack_oauth.py:26,32`
- (중간) 쿠키 secure 미설정, session_secret 기본 "dev-secret" — `auth_router.py:50`, `config.py:14`
- (중간) edit_case에서 pending만 있을 때 부분 commit으로 원자성 약화 — `case_router.py:44-56`

### 7. 테스트·검증·기술부채
- **(높음) 테스트 전무** — RI/KPI 결정론 로직조차 단위 테스트 없음
- (중간) 원시 `dict = Body(...)` — Pydantic 스키마 미사용으로 검증 누락 — `case_router.py:36`
- (낮음) 광범위 `except Exception`, requirements 상한 미지정, print만 사용

## 결론

**코드 품질 종합 점수: 68 / 100** (스캐폴드 기준 보정). 아키텍처 의도는 우수하나 결정론 약속 미충족·승인 우회·DB 제약/테스트 부재가 정량 통제 시스템 신뢰도를 깎음.

**Top 5 우선 개선:**
1. RI 결정론 보장 — 가중치 기준 batch 독립화 + 빈도 정규화 일원화 (`ri.py:56-64`, `analysis/__init__.py:20-22`)
2. 승인 통제 우회 차단 — 파생필드 클라이언트 편집 제거, 미지정 키 400 (`edit_policy.py:5-9`, `case_router.py:44-51`)
3. dev 인증 기본값 강경화 — dev_auth 기본 false, 기본 역할 staff (`config.py:16`, `rbac.py:35`)
4. DB 제약 보강 — UniqueConstraint(dept_id, code) + cascade/ondelete + 정책-모델 필드 정합성 (`models/__init__.py:23,68,86`)
5. 핵심 로직 단위 테스트 도입 + excel_import 헤더 기반 매핑 전환
