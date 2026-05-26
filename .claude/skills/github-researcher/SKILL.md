# GitHub Researcher Skill

## Purpose
member-eta가 GitHub 공개 레포를 탐색·필터·분석·라이선스 감사하는 데 필요한
명령 레퍼런스, 스크립트 인터페이스, 라이선스 매핑 테이블, 보호 규칙을 제공한다.

## When to Use
member-eta가 Execution Rules의 탐색 절차(Step 1–8)를 수행할 때 호출한다.

## Pre-Check Routine

탐색 시작 전 인증과 rate limit을 순서대로 확인한다:

```bash
# 1. gh 인증 확인
gh auth status

# 2. rate limit 확인
gh api rate_limit | python3 -c "
import sys, json
r = json.load(sys.stdin)['rate']
remaining = r['remaining']
limit = r['limit']
print(f'Remaining: {remaining}/{limit}')
if remaining < 10:
    print('WARNING: rate limit 임박 — 탐색 중단 후 Team Lead 보고')
"
```

**rate limit 보호 규칙**: Remaining < 10 이면 탐색을 즉시 중단하고 Team Lead에 보고한다.

## Search Command Reference

```bash
# 레포 검색 (stars 내림차순, 언어 필터)
gh search repos "<키워드>" --language <lang> --sort stars --limit 20

# 코드 검색
gh search code "<키워드>" --language <lang> --limit 20

# 레포 메타데이터 조회 (stars, 마지막 커밋, 라이선스)
gh api repos/<owner>/<repo> --jq '{name:.name, stars:.stargazers_count, pushed:.pushed_at, license:.license.spdx_id}'

# Shallow clone (분석용, /tmp/research/ 아래에 저장)
git clone --depth=1 https://github.com/<owner>/<repo>.git /tmp/research/<repo-name>

# 레포 루트 파일 목록 확인
ls /tmp/research/<repo-name>

# README 조회
cat /tmp/research/<repo-name>/README.md | head -100
```

## Quality Filter Script Interface

`filter-repos.py` — 후보 레포 목록을 품질 기준으로 필터링한다.

**입력 (JSON)**:
```json
[
  {
    "name": "owner/repo",
    "stars": 1200,
    "last_commit_days_ago": 45,
    "license": "MIT"
  }
]
```

**출력 (JSON)**: 필터링 통과 레포 목록 (동일 스키마)

**필터 기준**:
```
stars >= 100                                  (권장 >= 500)
last_commit_days_ago <= 548                   (18개월; 권장 <= 180 = 6개월)
license in ["MIT", "Apache-2.0"]              (없음·GPL 제외)
```

## License Audit Logic

LICENSE 파일 내용 → 상태 매핑 테이블:

| 라이선스 문자열 | SPDX ID | 상태 | 처리 규칙 |
|--------------|---------|------|---------|
| "MIT License" | MIT | ✅ | 패턴 참조 가능, 출처 명기 필수 |
| "Apache License 2.0" | Apache-2.0 | ✅ | 패턴 참조 가능, 출처 명기 필수 |
| "GNU General Public License v2" | GPL-2.0 | ⚠️ | 참조만 가능, 코드 복사 금지, 리포트에 플래그 |
| "GNU General Public License v3" | GPL-3.0 | ⚠️ | 참조만 가능, 코드 복사 금지, 리포트에 플래그 |
| "GNU Lesser General Public License" | LGPL-2.1/3.0 | ⚠️ | 참조만 가능, 코드 복사 금지, 리포트에 플래그 |
| LICENSE 파일 없음 | (none) | 🚫 | 사용 금지, 리포트에 명시 |
| 위에 해당 없음 | unknown | 🔺 | Team Lead에 에스컬레이션 |

## Cleanup Rule

분석 완료 후 반드시 실행한다:

```bash
rm -rf /tmp/research/
```

생략하면 후속 탐색 시 오래된 클론이 분석 결과를 오염시킬 수 있다.
