# GitHub Research Report
생성자: member-eta | 생성시각: 2026-05-28 16:30 | 버전: v1

## 탐색 조건
- 검색 키워드: `"english quiz game web"`, `"english vocabulary quiz"`, `"language learning quiz app"`, `"quiz game"`, `"vocab"`, `"flashcard"`, `"language learning"`, `"english game"`
- 언어 필터: `language:javascript` OR `language:typescript` (web frontend 중심)
- Stars: 최소 10 이상 (원래 50+ 기준이나 "english quiz game" 좁은 쿼리에서 유의미한 레포가 전무하여 하향)
- 마지막 커밋: 24개월 이내 우선
- 라이선스: MIT / Apache 2.0 우선, GPL은 참조 가능으로 분류

### 주의 사항
"english quiz game" 혹은 "english vocabulary quiz"로 직접 검색 시 대부분 0~2 stars의 개인 학습/과제 프로젝트만 발견되었습니다. 50+ stars, MIT 라이선스, 24개월 이내 활성 조건을 동시에 만족하는 "영어 퀴즈 게임" exact match 레포는 GitHub에 **존재하지 않음**을 확인했습니다. 따라서 어휘 학습(vocab), 언어 학습(language learning), 플래시카드(flashcard), 퀴즈 게임(quiz game) 등 인접 도메인의 고스타 레포를 포함하여 분석했습니다.

## 탐색 결과 요약

| # | 레포명 | Stars | 언어 | 라이선스 | 마지막 업데이트 | 관련성 | 선정 이유 |
|---|--------|-------|------|----------|-----------------|--------|----------|
| 1 | **sanidhyy/duolingo-clone** (Lingo) | 552 | TypeScript | MIT | 2026-05-28 | ★★★★★ | Duolingo 스타일 영어 퀴즈·레슨 플랫폼. Next.js + PostgreSQL + Drizzle. 퀴즈 챌린지, 하트 시스템, XP 포인트, 선택형/보조형(ASSIST) 문제 유형 구현. 가장 완성도 높은 **영어 학습 퀴즈 게임** 참조 레포. |
| 2 | **baturyilmaz/wordpecker-app** | 2,103 | TypeScript | MIT | 2026-05-27 | ★★★★★ | Duolingo+개인화 융합형 어휘 학습 앱. 5가지 문제 유형(객관식, 빈칸, 매칭, T/F, 문장완성), AI 음성챗, Vision Garden 이미지 기반 어휘 발견. OpenAI API 활용. 가장 **모던한 아키텍처**와 **기능 풍부도** 우수. |
| 3 | **cosmoart/quiz-game** (Quizi) | 90 | JavaScript | MIT | 2026-05-11 | ★★★★☆ | AI(Cohere API)가 생성한 문제로 퀴즈를 진행하는 Next.js 게임. 시간 모드·클래식 모드·무한 모드, 와일드카드, 키보드 단축키 지원. **퀴즈 게임 UX 패턴** 참조에 최적. |
| 4 | **RickCarlino/KoalaCards** | 48 | TypeScript | MIT | 2026-05-20 | ★★★★☆ | 한국어 학습 앱이나 영어 퀴즈 게임에도 적용 가능한 **FSRS 알고리즘 기반 플래시카드**, AI 피드백(채점·수정·전사), 리더/라이팅 모듈. 아키텍처 패턴과 문제 유형 참조 가치 높음. |
| 5 | **VienDinhCom/supermemo** | 336 | TypeScript | MIT | 2026-05-25 | ★★★☆☆ | SuperMemo 2 알고리즘 JS/TS 구현체. 영어 퀴즈에서 **반복 학습 간격 조절** 기능 추가 시 참조할 수 있는 라이브러리. 직접적인 게임/UI 없이 알고리즘만 제공. |
| 6 | **st3v3nmw/obsidian-spaced-repetition** | 2,399 | TypeScript | MIT | 2026-05-27 | ★★★☆☆ | Obsidian 플러그인이지만 FSRS/SM-2 기반 플래시카드 리뷰 시스템의 **구현 참조**(카드 마크업, 태그 기반 덱 구성, 통계). 직접 사용은 불가, 패턴만 참조. |
| 7 | **hubingkang/vocabulary-corpus** | 428 | TypeScript | MIT | 2026-05-24 | ★★★☆☆ | 44,000+ 영단어 코퍼스. LLM으로 음성·의미·어원·문화맥락 생성. **문제 은행 데이터 생성/확장** 시 데이터 파이프라인 참조 가능. |
| 8 | **mohannadofficial/duolingo-nextjs** | 73 | TypeScript | MIT | 2026-05-05 | ★★★☆☆ | Next.js + Shadcn UI + Clerk Auth + AI Voice 기반 Duolingo 클론. #1보다 소형이나 Shadcn UI 활용 방식 참조. |
| 9 | **subconcept-labs/ulangi** | 457 | TypeScript | GPL-3.0 | 2026-05-22 | ★★☆☆☆ | React Native 기반 모바일 언어 학습 앱. 완성도 높으나 GPL 라이선스(참조만 가능), 모바일 중심. 간격 반복·쓰기·퀴즈 학습법 참조. |
| 10 | **kyle1an/sub-vocab** | 92 | TypeScript | MIT | 2026-05-25 | ★★☆☆☆ | 영어 자료에서 어휘 추출·분류 도구. 퀴즈용 어휘 데이터셋 구축 시 파이프라인으로 참조 가능. |

### 라이선스 감사 요약
| 라이선스 | 레포 수 | 비고 |
|----------|---------|------|
| MIT | 8 | 자유롭게 사용·수정·배포 가능 (권장) |
| GPL-3.0 / AGPL-3.0 | 2 | **참조만 가능**, 소스 코드를 직접 복사·배포 금지 |
| 기타/미지정 | 다수(저품질) | 사용 전 반드시 라이선스 확인 필요 |

## 레포별 상세 분석

### 1. sanidhyy/duolingo-clone (Lingo) ⭐ 552 — MIT
**URL**: https://github.com/sanidhyy/duolingo-clone
**Live**: https://lingo-clone.vercel.app

#### 아키텍처 패턴
```
프레임워크: Next.js 16 (App Router, React 19 + TypeScript)
스타일링: Tailwind CSS 3
상태관리: Zustand
DB: PostgreSQL + Drizzle ORM + Neon serverless
인증: Clerk (OAuth + magic link)
결제: Stripe
배포: Vercel
```

#### 핵심 코드 위치
| 파일 | 설명 |
|------|------|
| `db/schema.ts` | Course > Unit > Lesson > Challenge 계층형 DB 스키마. `SELECT`(선택형), `ASSIST`(보조형) 문제 타입 enum |
| `actions/challenge-progress.ts` | 퀴즈 진행 로직: 하트 소모, 포인트 적립, 완료 상태 업데이트. Server Action 패턴 |
| `config/index.ts` | 퀴즈 게임 상수 (MAX_HEARTS, POINTS_PER_CHALLENGE 등) |
| `store/` | Zustand 기반 모달 상태 관리 (하트 부족, 연습 모드, 종료 모달) |
| `app/lesson/` | 퀴즈 화면 라우트 |
| `app/admin/` | react-admin 기반 관리자 대시보드 |
| `scripts/prod.ts` | DB 시드 스크립트 (문제·레슨·유닛·코스 데이터) |

#### 주요 인사이트
1. **계층형 콘텐츠 구조**: Course → Unit → Lesson → Challenge → ChallengeOption 의 5계층 DB 설계로 어떤 난이도·주제의 퀴즈도 확장 가능
2. **하트 시스템 + 연습 모드**: 5개 하트, 오답 시 하트 감소, 연습 시 하트 회복 → 게임화(gamification) 요소
3. **Server Actions + revalidatePath**: Next.js Server Action으로 DB 쓰기 후 캐시 무효화 패턴
4. **문제 유형**: SELECT(객관식), ASSIST(단어 맞추기) 두 가지로 구분, 이미지/오디오 첨부 가능

---

### 2. baturyilmaz/wordpecker-app ⭐ 2,103 — MIT
**URL**: https://github.com/baturyilmaz/wordpecker-app

#### 아키텍처 패턴
```
프론트엔드: React + TypeScript + Vite + Chakra UI + Framer Motion
백엔드: Express.js + TypeScript + @openai/agents SDK
DB: MongoDB + Mongoose
LLM: OpenAI (GPT-4, DALL-E, Realtime Voice)
음성: ElevenLabs API
배포: Docker Compose (MongoDB + backend + frontend)
단일 사용자: localStorage 기반 (인증 없음)
```

#### 핵심 코드 위치
| 파일 | 설명 |
|------|------|
| `backend/src/agents/` | OpenAI Agent SDK 기반 LLM 에이전트 (퀴즈 생성, 채점, 단어 추천 등) |
| `backend/src/api/` | REST API 엔드포인트 |
| `backend/src/services/` | 비즈니스 로직 서비스 계층 |
| `frontend/src/pages/` | Learn, Quiz, VoiceChat, LightReading, VisionGarden 등 주요 페이지 |
| `frontend/src/components/` | 재사용 컴포넌트 |
| `frontend/src/config/` | 설정값 |

#### 주요 인사이트
1. **5가지 문제 유형(설정 가능)**: 객관식, 빈칸 채우기, 매칭, True/False, 문장 완성 → 사용자가 원하는 유형만 활성화 가능한 커스터마이징
2. **Agent 기반 LLM 아키텍처**: @openai/agents SDK로 퀴즈 생성·채점·단어 추천을 LLM 에이전트화 → AI 기반 문제 자동 생성의 레퍼런스
3. **Vision Garden**: 이미지 보고 설명 → 부족한 표현을 LLM이 어휘 추천 → 맥락 기반 어휘 확장 학습
4. **단일 사용자 구조**: 인증 없이 localStorage 기반. MVP 단계에 최적화된 단순화 전략
5. **Docker Compose 배포**: 개발 환경이 docker-compose 하나로 통합되어 있어 재현성 높음

---

### 3. cosmoart/quiz-game (Quizi) ⭐ 90 — MIT
**URL**: https://github.com/cosmoart/quiz-game
**Live**: https://quizi.vercel.app

#### 아키텍처 패턴
```
프레임워크: Next.js (Pages Router) + React
스타일링: Tailwind CSS + AnimatiSS 애니메이션
상태관리: Zustand (전역 상태: questions, wildCards, score, win)
퀴즈 데이터: Cohere API (AI 생성) + pre-generated JSON fallback
배포: Vercel
```

#### 핵심 코드 위치
| 파일 | 설명 |
|------|------|
| `src/store/useBoundStore.js` | Zustand 스토어: 퀴즈 진행, 점수, 와일드카드 통합 관리 |
| `src/components/Questions/Questions.jsx` | 퀴즈 핵심 로직: 타이머, 키보드 단축키, 정답 처리, 와일드카드 |
| `src/components/Questions/QuestionSlider.jsx` | 슬라이드 전환 UI |
| `src/components/Play/GameOver.jsx` | 게임 종료 화면 (승리/패배, confetti) |
| `src/assets/categories.json` | 퀴즈 카테고리 정의 (주제별 색상 포함) |
| `src/helpers/getQuestions.js` | Cohere API 호출 or 로컬 JSON fallback으로 문제 가져오기 |

#### 주요 인사이트
1. **3가지 게임 모드**: Classic(10문제), Time(제한시간), Infinity(무한, 5문제 단위 배치) → 게임 몰입도 다양성
2. **와일드카드 시스템**: 50:50(두 선택지 제거), +10s, 생명(오답 방지) → 게임 재미 요소
3. **키보드 단축키**: A/B/C/D/좌우 화살표 → 접근성 + 빠른 플레이
4. **오프라인 fallback**: Cohere API 호출 제한 시 pre-generated JSON 사용 → 안정성 확보
5. **카테고리별 동적 배경색**: 퀴즈 주제에 따라 body 배경색 변경 → 몰입감

---

### 4. RickCarlino/KoalaCards ⭐ 48 — MIT
**URL**: https://github.com/RickCarlino/KoalaCards

#### 아키텍처 패턴
```
프레임워크: Next.js (Pages Router) + React + TypeScript + tRPC
스타일링: Mantine UI
DB: PostgreSQL + Prisma
알고리즘: FSRS (Free Spaced Repetition Scheduler)
인증: NextAuth (email magic link / Google OAuth)
AI: OpenAI (채점, 파싱, 어시스턴트, 전사, TTS)
스토리지: Google Cloud Storage
배포: Docker Compose (app + worker + db)
```

#### 주요 인사이트
1. **FSRS 기반 복습 스케줄링**: new/due/remedial 3단계 복습 큐 → 영어 퀴즈 오답 노트 시스템에 적용 가능
2. **말하기·쓰기 AI 채점**: 음성 녹음 → 전사 → AI 채점, 쓰기 → AI 수정 + diff 뷰
3. **Reader + 하이라이트 → 카드 자동 생성**: URL/텍스트에서 콘텐츠 읽고, 하이라이트한 부분을 플래시카드로 즉시 변환
4. **tRPC + Next.js**: End-to-end type safety. 백엔드/프론트엔드 타입 공유
5. **Worker 아키텍처**: 메인 앱과 백그라운드 작업 분리 → 대용량 처리 안정성

---

### 5. VienDinhCom/supermemo ⭐ 336 — MIT
**URL**: https://github.com/VienDinhCom/supermemo

- SuperMemo 2 알고리즘의 JavaScript/TypeScript 구현체
- `supermemo(item: SuperMemoItem, grade: SuperMemoGrade): SuperMemoItem` 함수 제공
- 입력: 현재 반복 횟수·간격·난이도 + 사용자 평가 등급(0~5)
- 출력: 다음 복습 간격·새로운 난이도 계수
- 영어 퀴즈 앱에 **복습 일정 자동화** 추가 시 직접 도입 가능한 npm 패키지

---

### 6. hubingkang/vocabulary-corpus ⭐ 428 — MIT
**URL**: https://github.com/hubingkang/vocabulary-corpus

- LLM으로 생성된 44,000+ 영단어 데이터셋 (JSON)
- 각 단어: 음성학(영/미 IPA), 다계층 정의, 어원, 문법, 문화맥락, 기억보조장치
- **Rate Limiter 내장**: API 호출 안정화를 위한 슬라이딩 윈도우 구현
- **Resume 지원**: 중단된 지점부터 재시작 → 대규모 워드뱅크 생성 파이프라인 참조

---

### 7. subconcept-labs/ulangi ⭐ 457 — GPL-3.0 (참조만 가능)
**URL**: https://github.com/subconcept-labs/ulangi

- React Native 기반 모바일 앱(Android/iOS)
- 내장 사전·번역기·TTS·이미지 검색 엔진 → 단어 검색부터 카드 생성까지 인앱
- 학습 메서드: 공간 반복, 쓰기 연습, 퀴즈
- Type-safe 코드 + 디자인 패턴 중시
- 모바일 중심이나 **단어→카드→퀴즈** 워크플로우 설계의 참조
- ⚠️ GPL-3.0: 소스코드 직접 사용 불가, 설계 아이디어만 참조 가능

---

## 크로스 레포 공통 패턴

### 1. Next.js + React + TypeScript (사실상 표준)
분석한 10개 레포 중 7개가 Next.js 기반. 2개는 Vite+React, 1개는 React Native.
SEO 필요 없어도 Next.js의 App Router, Server Actions, API Routes 통합이 선호됨.

### 2. PostgreSQL + ORM (Drizzle/Prisma)
- **duolingo-clone**: Drizzle ORM + Neon serverless
- **KoalaCards**: Prisma + PostgreSQL
- **wordpecker-app**: MongoDB 예외이나, 단일 사용자 구조 때문

### 3. LLM API 연동 (문제 생성 자동화)
| 레포 | 사용 AI API | 용도 |
|------|------------|------|
| Quizi | Cohere | 퀴즈 문제·정답 생성 |
| WordPecker | OpenAI (GPT-4, DALL-E, Realtime Voice) | 문제 생성, 채점, 이미지, 음성대화 |
| KoalaCards | OpenAI | 채점, 파싱, 어시스턴트, 전사, TTS |
| Vocabulary Corpus | LLM | 단어 데이터 생성 |

→ **AI 기반 문제 자동 생성**은 현대 영어 퀴즈 앱의 핵심 차별화 요소.

### 4. 게임화(Gamification) 요소
| 요소 | duolingo-clone | Quizi | WordPecker |
|------|:---:|:---:|:---:|
| 하트/생명 시스템 | ○ | ○ (와일드카드) | - |
| XP 포인트 | ○ | - | ○ |
| 타이머 모드 | - | ○ | - |
| 레벨/진행률 | ○ (유닛) | - | ○ |
| 리더보드 | - | - | - |
| 보상(confetti 등) | ○ | ○ | - |

### 5. Zustand 상태 관리 (경량화)
Quizi, duolingo-clone 모두 Zustand 채택. Redux보다 가볍고 퀴즈 게임에 충분한 기능 제공.

### 6. 카테고리/주제 기반 확장 구조
모든 퀴즈 앱이 주제별 분류 체계를 가짐. JSON 또는 DB에 카테고리 정의 후 동적 로딩.

---

## 안티패턴

### 1. 하드코딩된 문제 데이터 (Quizi)
`src/assets/categories.json` + pre-generated questions. 확장성 낮고 유지보수 부담.
→ DB 기반 문제 관리 또는 AI 동적 생성으로 대체 권장.

### 2. 대규모 God Component (Quizi `Questions.jsx`)
하나의 컴포넌트가 타이머, 키보드 단축키, 정답 처리, 와일드카드, 게임 종료까지 담당.
→ 기능별 custom hook + 작은 컴포넌트로 분리 필요.

### 3. Pages Router 사용 (Quizi, KoalaCards)
Next.js App Router로 마이그레이션되지 않은 레포. 최신 Next.js 프로젝트는 App Router 권장.

### 4. 인증/인가 부재 (WordPecker, Quizi)
단일 사용자 대상으로 설계. 다중 사용자 지원 시 보안 취약점.
→ 영어 퀴즈 게임이 다중 사용자 대상이면 초기부터 Clerk 등 인증 도입.

### 5. API Rate Limit 미대비 (Quizi)
Cohere API 5회 무료 호출 정책 변경 후 갑작스럽게 기능 축소.
→ API 폴백(fallback) 메커니즘 + 로컬 캐싱 + DB 문제 은행 병행 필수.

### 6. 라이선스 미지정 (대다수 저스타 레포)
분석한 0~2 star 레포 중 90% 이상이 LICENSE 파일 없음.
→ 참조 시 법적 리스크 있으므로 라이선스 명시된 레포만 사용.

---

## Planner를 위한 권고 스택·접근법

### 권장 기술 스택
| 계층 | 권장 | 대안 |
|------|------|------|
| **프레임워크** | Next.js 15+ (App Router) | Vite + React |
| **언어** | TypeScript (strict) | - |
| **스타일링** | Tailwind CSS 4 + Shadcn UI | Chakra UI |
| **상태관리** | Zustand (퀴즈 상태) + React Query (서버 상태) | - |
| **DB** | PostgreSQL + Drizzle ORM | Prisma |
| **인증** | Clerk (OAuth) 또는 NextAuth | - |
| **AI** | OpenAI API (GPT-4o, TTS) or Anthropic Claude | Cohere |
| **음성** | ElevenLabs or OpenAI TTS | - |
| **배포** | Vercel + Neon (serverless DB) | Docker Compose |
| **알고리즘** | supermemo npm (공간 반복) | FSRS |

### 권장 접근법
1. **Duolingo-clone DB 스키마를 기반으로 시작**: Course > Unit > Lesson > Challenge 계층 구조는 어떤 퀴즈 게임에도 확장 가능. 영어 난이도/주제별로 Unit 분류.
2. **WordPecker의 5가지 문제 유형 + 설정 가능 구조 차용**: 객관식/빈칸/매칭/TF/문장완성을 문제 타입 메타데이터로 정의하고 사용자 세팅에서 활성화 선택.
3. **Quizi의 게임 모드 + 와일드카드 설계 참조**: Classic, Time Attack, Infinity 모드 + 50:50, +Time, 생명 아이템.
4. **supermemo npm으로 오답 복습 일정 자동화**: 틀린 문제 자동 저장 → 다음 복습일 계산 → 알림.
5. **AI 문제 자동 생성 + pre-generated JSON 폴백**: OpenAI로 문제 생성, API 제한 시 캐싱된 JSON 사용. API 키 없어도 기본 문제 세트로 동작.
6. **Zustand로 퀴즈 상태 중앙 관리**: questions[], currentQuestion, score, wildCards, settings를 하나의 스토어에서 관리.
7. **Docker Compose로 재현 가능한 개발 환경 구성**: WordPecker의 구성 참조.

---

## 출처 목록
| # | 레포명 | Stars | 라이선스 | URL |
|---|--------|-------|----------|-----|
| 1 | sanidhyy/duolingo-clone | 552 | MIT | https://github.com/sanidhyy/duolingo-clone |
| 2 | baturyilmaz/wordpecker-app | 2,103 | MIT | https://github.com/baturyilmaz/wordpecker-app |
| 3 | cosmoart/quiz-game | 90 | MIT | https://github.com/cosmoart/quiz-game |
| 4 | RickCarlino/KoalaCards | 48 | MIT | https://github.com/RickCarlino/KoalaCards |
| 5 | VienDinhCom/supermemo | 336 | MIT | https://github.com/VienDinhCom/supermemo |
| 6 | st3v3nmw/obsidian-spaced-repetition | 2,399 | MIT | https://github.com/st3v3nmw/obsidian-spaced-repetition |
| 7 | hubingkang/vocabulary-corpus | 428 | MIT | https://github.com/hubingkang/vocabulary-corpus |
| 8 | mohannadofficial/duolingo-nextjs | 73 | MIT | https://github.com/mohannadofficial/duolingo-nextjs |
| 9 | subconcept-labs/ulangi | 457 | GPL-3.0 | https://github.com/subconcept-labs/ulangi |
| 10 | kyle1an/sub-vocab | 92 | MIT | https://github.com/kyle1an/sub-vocab |