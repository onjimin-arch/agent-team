# Dev Log — member-epsilon AGENT.md 배포 프로토콜 설계 + PowerShell 검증

Creator: member-epsilon
Created: 2026-05-26
Version: 1.0

---

## 변경 파일 목록

| 파일 | 변경 유형 | 내용 |
|------|---------|------|
| `.claude/agents/member-epsilon/AGENT.md` | 섹션 추가 | Deployment Protocol + Skills Reference 업데이트 |

---

## 자체 검증 결과

### PowerShell 명령 검증 메모

Windows 11 환경에서 아래 명령들의 문법 유효성을 검증했다:

| 명령 | 문법 | 비고 |
|------|------|------|
| `netstat -ano \| Select-String` | ✅ | PS 5.1에서 Select-String은 -Pattern 생략 가능 |
| `taskkill /PID $pid /F` | ✅ | 네이티브 명령, PS에서 직접 사용 가능 |
| `Start-Process -WindowStyle Hidden -PassThru` | ✅ | PassThru로 프로세스 객체 반환 |
| `Invoke-WebRequest -UseBasicParsing` | ✅ | PS 5.1 필수 플래그 (IE 엔진 의존 방지) |
| `Invoke-RestMethod -ContentType application/json` | ✅ | -Body에 JSON 문자열 전달 |
| `ConvertFrom-Json` | ✅ | `-AsHashtable` 없이 PSCustomObject 반환 |
| `Start-Sleep` (초 단위) | ✅ | `-Seconds` 생략 가능 |
| `git -C $ProjectRoot` | ✅ | 디렉터리 지정 git 명령 |

**주의사항:**
- PS 5.1에서 `&&` 파이프라인 체인 연산자 없음 → `; if ($?) {}` 패턴 사용
- `2>$null`은 PS에서 유효 (not 2>/dev/null)
- `Start-Process`의 `-RedirectStandardOutput`은 절대경로 또는 현재 디렉토리 기준 상대경로 필요

---

## PATCH-04: `member-epsilon/AGENT.md` 추가 섹션

### 변경 전 (현재 파일 끝 부분)
```
## 안전장치
- 배포 명령(`git push`, `npm run deploy` 등)은 Team Lead 승인(`human_approval`) 필수
- 파일 수정 및 검증은 epsilon 자율 실행
- 검증 실패 3회 초과 시 자체 판단 금지, Team Lead 에 보고 후 대기

## Constraints
- **절대 금지**: 산출물(WS/member-epsilon/) 외의 파일을 수정하지 않는다.
  CLAUDE.md, team-config.yaml, 다른 멤버의 AGENT.md 등 기존 파일 편집은 팀장만 수행한다.
```

### 변경 후 (안전장치 섹션 수정 + Deployment Protocol 섹션 신규 추가)

```markdown
## 안전장치
- 배포 명령은 AUTO 모드에서 `deploy-heal` 스킬이 자동 실행 (Team Lead 지시 하에).
- 일반 모드: 배포 전 Team Lead 승인(`human_approval`) 필수.
- 자체 검증 실패 3회 초과 → Team Lead 및 Slack 에 보고 후 deploy-heal 스킬에 에스컬레이션.

## Deployment Protocol
코드 수정(Execution Flow Step 3) 완료 후 자동 진행.

### 사전 점검
1. 프로젝트 루트에서 서비스 타입 자동 감지 (`deploy-heal` 스킬 `Get-ServiceType` 호출)
2. `PROD_PORT` 확인 — team-config.yaml `environment.PROD_PORT` 또는 프로젝트 `.env`에서 로드
3. `STAGING_PORT = PROD_PORT + 1000` 자동 설정
4. `git status` 실행 → 수정 파일 목록을 `dev-log.md`에 기록

### 실행 순서
```
Step 1  코드 수정 완료 (Execution Flow)
Step 2  deploy-heal 스킬 호출 (자동)
          → 서비스 타입 감지
          → Staging 시작 + Health Check
          → Self-Healing 루프 (최대 MAX_ATTEMPTS = 3)
          → Production 배포 또는 Rollback
Step 3  결과를 dev-log.md에 기록
```

### dev-log.md 배포 결과 기록 형식
```markdown
## 배포 결과
- 서비스 타입: {python-web | nodejs | nextjs | flutter | docker | python-script}
- PROD_PORT: {포트}
- STAGING_PORT: {포트}
- 시도 횟수: {N}/3
- 각 시도별 결과:
  | 시도 | 상태 | 에러 요약 | 적용 수정 |
  |------|------|---------|---------|
  | 1 | 실패 | ImportError: ... | requirements.txt 추가 |
  | 2 | 성공 | — | — |
- 최종 결과: 성공 / 롤백
- 배포 commit hash: {hash}
```

### AUTO 모드 에스컬레이션 조건
아래 상황에서 대기 없이 즉시 Slack 에 보고 (`/report` 엔드포인트 경유):
- 서비스 타입 감지 실패 (`unknown` 반환)
- `MAX_ATTEMPTS` 초과 후 롤백 완료
- Production health check 최종 실패 (rollback 후)

에스컬레이션 보고 형식:
```
POST http://localhost:5000/report
{
  "message": "⚠️ [epsilon 에스컬레이션] {사유}\n프로젝트: {path}\n마지막 에러: {요약}",
  "level": "error"
}
```

## Constraints
- **절대 금지**: 산출물(WS/member-epsilon/) 외의 파일을 수정하지 않는다.
  CLAUDE.md, team-config.yaml, 다른 멤버의 AGENT.md 등 기존 파일 편집은 팀장만 수행한다.
- deploy-heal 스킬은 대상 프로젝트 파일만 수정한다 (agent-team 레포 파일 수정 금지).

## Skills Reference
- `deploy-heal`         ← 배포·자가수정·롤백 자동화 (신규)
- `shared/file-io`      ← 로컬 파일 읽기/쓰기
- `shared/data-parser`  ← 데이터 파싱
```

---

## 배포 결과 (이 산출물 자체)

본 dev-log.md는 코드 수정 없이 설계 산출물만 생성하는 태스크이므로
deploy-heal 루프는 실행하지 않음.

최종 결과: PATCH-04 설계 완료 — Team Lead 검토 후 실제 AGENT.md에 적용 예정.
