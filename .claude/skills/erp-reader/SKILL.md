# (Deprecated) ERP Reader Skill

이 스킬은 `.claude/skills/dept-dashboard-reader/SKILL.md`로 대체되었다. ERP뿐 아니라 현장·인사·AX·
브랜드·법무 등 여러 부서 대시보드를 같은 방식(범용 `scripts/dashboard_fetch.py`)으로 다루기 위해
일반화했다. `scripts/erp_fetch.py`는 삭제되었다 — ERP 조회는 이제
`dept-dashboard-reader/SKILL.md`의 레지스트리 표(ERP 행)를 참조해 `dashboard_fetch.py`로 호출한다.

이 폴더는 더 이상 참조하지 않는다.
