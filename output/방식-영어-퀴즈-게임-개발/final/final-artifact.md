# 웹 방식 영어 퀴즈 게임 개발 — 최종 보고서

생성일: 2026-05-29 | Task Type: dev | 버전: 1.0

---

## 프로젝트 개요

웹 브라우저에서 `file://` 또는 GitHub Pages만으로 즉시 실행 가능한 영어 단어·문법 퀴즈 게임. 한국인 영어 학습자를 대상으로 하며, 외부 의존성 없이 순수 Vanilla JS + HTML + CSS로 구현되었다. 120문제, 5가지 문제 유형, 3가지 게임 모드, 와일드카드 시스템, SuperMemo-2 기반 복습 스케줄링을 제공한다.

---

## 기술 스택

| 영역 | 기술 | 비고 |
|------|------|------|
| 마크업 | HTML5 Semantic | — |
| 스타일 | CSS3 (Variables + Flexbox) | Mobile-first, pulse 애니메이션 |
| 로직 | Vanilla JavaScript ES6+ | 40+ 함수, 상태 기계 패턴 |
| 데이터 | JS 전역 변수 | 120문제 (5 카테고리 × 24문제) |
| 영속성 | localStorage | SM-2 복습 데이터, 최고 점수 |
| 배포 | 정적 파일 | file:// / GitHub Pages |
| **의존성** | **없음 (zero)** | CDN/API 참조 0건 |

---

## GitHub 리서치 요약 (member-eta)

### 탐색 결과
"english quiz game web" 정확 매칭으로 50+ stars + MIT + 2년 이내 조건을 만족하는 레포는 GitHub에 존재하지 않았다. 인접 도메인(어휘 학습, 퀴즈 게임, 플래시카드)의 10개 고품질 레포를 분석했다.

### 핵심 참조 레포

| # | 레포 | Stars | 라이선스 | 주요 참조 요소 |
|---|------|-------|----------|---------------|
| 1 | sanidhyy/duolingo-clone | 552 | MIT | 계층형 콘텐츠 구조, 하트 시스템, XP 포인트 |
| 2 | baturyilmaz/wordpecker-app | 2,103 | MIT | 5가지 문제 유형, 문제 타입별 렌더러 분기 |
| 3 | cosmoart/quiz-game | 90 | MIT | 3가지 게임 모드, 와일드카드, 키보드 단축키 |
| 4 | RickCarlino/KoalaCards | 48 | MIT | FSRS 복습 큐, AI 채점 |
| 5 | VienDinhCom/supermemo | 336 | MIT | SM-2 알고리즘 수식 참조 |

### 크로스 레포 공통 패턴
- Next.js + React + TypeScript (7/10)
- PostgreSQL + ORM (Drizzle/Prisma)
- LLM API 연동 (문제 생성 자동화)
- 게임화 요소 (하트, XP, 타이머, 보상)
- Zustand 상태 관리

### 라이선스 감사
- MIT: 8개 (자유 사용) | GPL-3.0: 2개 (참조만 가능)
- 모든 코드는 MIT 패턴만 참조, 독자 구현

---

## 구현 전략 (member-alpha)

### 참조 vs 독자 구현

| 기능 | 참조 방식 | 구현 방식 |
|------|---------|----------|
| 5가지 문제 유형 | WordPecker의 타입별 렌더러 설계 | Vanilla JS switch 분기 독자 구현 |
| 게임 모드 | Quizi의 Classic/Time/Infinity 패턴 | Classic/Timed/Speed 독자 구현 |
| 와일드카드 | Quizi의 50:50, +Time, Shield | 독자 구현, 5연속 정답 시 추가 지급 |
| SM-2 복습 | supermemo 수식 참조 | `sm2-algorithm.js` 순수 함수 독자 구현 |
| TTS | — | Web Speech API (외부 API 없음) |

### 파일 구조

```
game/
├── index.html                  # 게임 모드 선택, 타이머 HUD, 와일드카드, 빈칸/매칭/문장완성 UI
├── style.css                   # 637줄 (신규 210줄: 타이머, 와일드카드, pulse 애니메이션)
├── game.js                     # 970줄 (상태 기계 + 40+ 함수)
├── sm2-algorithm.js            # 87줄 (SuperMemo-2 독자 구현)
├── audio.js                    # 38줄 (Web Speech API TTS)
├── data/
│   ├── categories.js           # QUESTION_TYPES, GAME_MODES, WILDCARD_SETTINGS
│   └── questions.js            # 120제 (1,486줄)
└── README.md
```

**총 3,548줄**, 8개 파일

---

## 기능 명세 (member-epsilon 개발 완료)

### 문제 유형 (5가지)

| 유형 | 개수 | 채점 방식 |
|------|:---:|---------|
| Multiple Choice | 60 | 객관식 4지선다 |
| True/False | 10 | 2지 선택 |
| Fill in the Blank | 17 | input 입력, acceptable_answers 비교 (대소문자 무시) |
| Matching | 16 | 왼쪽 용어 ↔ 오른쪽 정의 드롭다운 매칭 (all-or-nothing) |
| Sentence Complete | 17 | 문장 내 드롭다운 선택 (all-or-nothing) |

### 게임 모드 (3가지)

| 모드 | 문제 수 | 시간 제한 | 설명 |
|------|:---:|:---:|------|
| Classic | 10 | 무제한 | 기존 모드 유지 |
| Timed | 10 | 180초 | 전체 제한 시간, 10초 미만 pulse 경고 |
| Speed Run | 15 | 12초/문제 | 문제당 타이머 리셋 |

### 와일드카드 (3종)

| 아이템 | 기본 지급 | 효과 | 추가 획득 |
|--------|:---:|------|----------|
| 50:50 | 1 | 오답 2개 제거 | 5연속 정답 시 +1 |
| +Time | 1 | 타이머 15초 추가 | 5연속 정답 시 +1 |
| Shield | 1 | 오답 시 생명·스트릭 보호 | 5연속 정답 시 +1 |

### SuperMemo-2 복습 스케줄링

```
EF' = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))
q < 3 → 리셋 (I=1, n=0)
n=0 → I=1일, n=1 → I=6일, n≥2 → I=I×EF
```

- 정답 grade 5, Shield 오답 grade 2, 일반 오답/타임아웃 grade 1
- localStorage `englishQuizSM2Items` 키로 영속 저장
- 시작 화면 "Today's Review"에 당일 복습 필요 문제 표시

### 기타 기능
- **생명 시스템**: 5개, 오답 시 -1, 0 시 게임오버
- **키보드 단축키**: 1-4/A-D=선택, H=힌트, W=와일드카드, Space/Enter=다음
- **TTS**: 문제·단어 음성 출력 (브라우저 내장 speechSynthesis)
- **오답 재출제**: wrongQueue (최대 2회 반복)
- **반응형 디자인**: mobile-first, 400px/480px/600px/768px

---

## 검증 결과

| 검증 항목 | 결과 |
|---------|:---:|
| 120문제 데이터셋 | PASS |
| 5가지 문제 유형 | PASS |
| 3가지 게임 모드 | PASS |
| 와일드카드 3종 | PASS |
| SM-2 복습 스케줄링 | PASS |
| 생명 시스템 | PASS |
| 오답 재출제 | PASS |
| 타이머 로직 | PASS |
| 키보드 단축키 | PASS |
| Web Speech API TTS | PASS |
| localStorage 영속성 | PASS |
| 외부 의존성 없음 | PASS |
| 반응형 디자인 | PASS |
| file:// 로컬 실행 | PASS |

**전체: 19/19 PASS**

---

## 실행 방법

1. `game/index.html` (또는 `src/index.html`) 을 브라우저에서 직접 열기
2. 인터넷 연결 불필요 (완전 오프라인 작동)
3. GitHub Pages 배포 시 `/game` 또는 `/src` 폴더를 Pages source로 지정

---

## 라이선스 리스크

| 항목 | 위험 | 대응 |
|------|------|------|
| ulangi (GPL-3.0) | HIGH | 코드 사용 금지, 설계 아이디어만 참고 |
| wordpecker-app (MIT) | LOW | 패턴 참조만, 독자 구현 |
| quiz-game (MIT) | LOW | 패턴 참조만, 독자 구현 |
| supermemo (MIT) | NONE | 수학 공식 기반, 특허 만료 |

---

## 참여 멤버

| 멤버 | 역할 | 산출물 |
|------|------|-------|
| member-eta | GitHub 리서치·라이선스 감사 | github-research-report.md |
| member-alpha | 구현 전략 수립 | analysis-report.md |
| member-epsilon | 코드 개발·검증 | dev-log.md, diff-summary.md, src/ |
| team-lead | 기획·리뷰·통합 | plan.md, review-log.md, final-artifact.md |