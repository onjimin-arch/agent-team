# 계획 문서 — 도심물류 OS

**작성일**: 2026-04-20
**워크스페이스**: `도심물류-os`
**팀장**: team-lead

---

## 1. Task Type 자동 판별

- 사용자 요청: "신규 주제 도심물류 OS"
- 요청에 명시적 태그([...]) 없음 → trigger 키워드 매칭 확인
- 업무 성격이 시장·기술·플레이어 현황 조사 → `research-report` triggers("시장", "현황", "분석") 에 해당
- **선택 결과**: `research-report` (default)
- **활성 멤버**: member-alpha · member-gamma · member-delta · member-beta
- 비활성 멤버: 없음 (현재 팀 4명 전원 research-report 활성 대상)

---

## 2. 업무 요약

도심물류(Urban Logistics / Last-Mile) 를 위한 **도심물류 OS** — 즉 다수의 라이더 · 차량 · 라커 · 허브 · 주문 채널을 통합 제어하는 소프트웨어 플랫폼 — 의 국내외 시장, 기술 스택, 주요 플레이어, 규제·경쟁 구도를 조사·분석하고, 정책·사업 관점 실행 권고를 담은 최종 보고서를 산출한다.

---

## 3. 과제 분해 및 담당자 배정

| # | 과제 | 담당자 | 산출물 |
|---|------|--------|--------|
| T1 | 도심물류 OS 시장·기술·플레이어·규제 리서치 | member-alpha | `member-alpha/analysis-report.md` |
| T2 | 수치·프로그램명·플레이어 명칭 팩트체크 | member-gamma | `member-gamma/fact-check-log.md` |
| T3 | 구조도·프로세스도·핵심 수치 테이블 시각화 | member-delta | `member-delta/visuals.md` |
| T4 | 핵심 인사이트·대상별 추천 보고서 초안 | member-beta | `member-beta/draft-report.md` |

---

## 4. 실행 순서 및 의존성 맵

```
[T1: member-alpha]
    ↓ analysis-report.md
    ├──→ [T2: member-gamma] ── fact-check-log.md
    └──→ [T3: member-delta]  ── visuals.md
              ↓ (T2, T3 병렬 실행)
[T4: member-beta]  ← analysis-report.md + fact-check-log.md + visuals.md
    ↓ draft-report.md
[팀장 통합 → final-artifact.md]
    ↓ (Phase 5)
[Notion 저장 + Slack 알림]
```

- T2, T3 는 T1 완료 후 병렬 실행 가능 (서로 의존 없음)
- T4 는 T1~T3 모두 완료 후 실행
- 의존성 사이클 없음 ✓

---

## 5. 각 담당자 상세 지시

### member-alpha 지시
- **주제**: 도심물류 OS 시장·기술·플레이어·규제 현황 분석
- **조사 범위**:
  1. 도심물류 OS 정의·기능 구성요소 (라우팅·디스패치·라이더 앱·주문 연동·창고/라커·실시간 트래킹)
  2. 국내 주요 플레이어 (바로고, 부릉(메쉬코리아 후신), 생각대로, 우아한청년들(배민커넥트), 쿠팡이츠 서비스, 카카오모빌리티/T맵 연계, 쿠팡로지스틱스서비스, CJ대한통운 오네 등)
  3. 해외 주요 플레이어 (Flexport Last Mile, Bringg, Onfleet, Routific, Locus, Wise Systems, Shipsy, Delivery Hero Dmart, Gorillas/Getir 백엔드, Amazon Logistics/AMZL, Uber Direct 등)
  4. 기술 스택 (VRP/VRPTW 알고리즘, LLM/ML 예측, IoT·엣지 게이트웨이, 실시간 디스패치, HD맵·물류 데이터)
  5. 규제·정책 (국내 생활물류법 개정, 라이더 처우·산재, 해외 gig worker 규제, ESG/탄소)
  6. 시장 규모·성장률·투자·M&A 동향 (2023~2026)
- **필수 섹션**: 개요 / 분석 결과 / 결론
- **저장 경로**: `output/도심물류-os/member-alpha/analysis-report.md`

### member-gamma 지시
- **입력**: `output/도심물류-os/member-alpha/analysis-report.md`
- **임무**: alpha 산출물의 수치·프로그램명·회사명·연도·규제명을 외부 출처로 검증, 팩트체크 로그 생성
- **필수 섹션**: 검증 요약 / 항목별 검증 결과 (표 형태) / 수정 권고
- **저장 경로**: `output/도심물류-os/member-gamma/fact-check-log.md`
- WebSearch·WebFetch 활용

### member-delta 지시
- **입력**: `output/도심물류-os/member-alpha/analysis-report.md`
- **임무**: alpha 데이터로 시각자료 생성 (새 사실 도입 금지)
- **필수 구성**:
  - Mermaid 다이어그램 2종 이상 (예: 도심물류 OS 구조도, 주문→배송 프로세스도)
  - 핵심 수치 테이블 (시장 규모, 주요 플레이어 비교, 기술 스택 매트릭스)
- **필수 섹션**: 시각자료 개요 / Mermaid 다이어그램 / 핵심 수치 테이블
- **저장 경로**: `output/도심물류-os/member-delta/visuals.md`

### member-beta 지시
- **입력**: alpha + gamma + delta 산출물 모두
- **임무**: 의사결정자(경영진/정책) 관점에서 핵심 인사이트 + 대상별 추천 사항 도출
- **필수 섹션**: 요약 / 핵심 인사이트 (5개 이상) / 추천 사항 (대상별 구분)
- **저장 경로**: `output/도심물류-os/member-beta/draft-report.md`
- gamma 의 "수정 권고" 가 있으면 반영, delta 의 시각자료 위치 참조

---

## 6. 검토 기준

- 필수 섹션 모두 포함
- 수치·출처 명시 및 gamma 검증과 일치
- 논리 흐름·중복/모순 없음
- 형식(md) 준수
- delta 시각자료가 alpha 데이터와 일치 (새 수치 생성 금지)

---

## 7. 종료 조건

- `max_cycles`: 3
- 품질 기준 충족 후 팀장 최종 검토 → 인간 승인
- 최종 산출물: `output/도심물류-os/final/final-artifact.md`

---

## 8. Phase 5 (Distribution)

human_approval 통과 시 자동 실행:
- **Notion**: 리서치/분석 BOT DB 에 하위 페이지로 저장
- **Slack**: Webhook 으로 완료 알림 Block Kit 전송
- Gmail/Drive/Calendar: 비활성 (`enabled: false`)
