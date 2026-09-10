Creator: member-alpha | Created: 2026-05-28 17:00 | Version: 2.0

## 개요 (Overview)

### 프로젝트 목표
웹 브라우저에서 `file://` 또는 GitHub Pages 만으로 즉시 실행 가능한 영어 단어·문법 퀴즈 게임을 **2차 고도화**한다. 기존 게임(Phase 1)에 다음을 추가한다:
- 5가지 문제 유형 지원 (객관식, True/False, 빈칸 채우기, 매칭, 문장 완성)
- 게임 모드 다양화 (Classic, Time Attack, Speed Run)
- 와일드카드 아이템 시스템 (50:50, +시간, 생명)
- SuperMemo-2 기반 오답 복습 스케줄링
- 문제 데이터셋 2배 확장 (60 → 120제)
- 접근성 및 키보드 네비게이션 강화

### 참조 근거
Member-eta의 GitHub 리서치 (2026-05-28, 10개 레포 분석)를 기반으로 하되, 기존 게임 아키텍처(Vanilla JS, 정적 파일, 제로 의존성) 위에 증분 개선한다. WordPecker, Quizi, supermemo, KoalaCards 등에서 학습한 패턴을 기존 코드에 녹여낸다.

---

## 분석 결과 (Analysis Results)

### 기술 스택

기존 스택을 유지한다 (추가 의존성 없음):

| 영역 | 기술 | 비고 |
|------|------|------|
| 마크업 | HTML5 Semantic | 기존 유지 |
| 스타일 | CSS3 (CSS Variables + Flexbox) | 기존 유지, 게임 모드 선택 UI 추가 |
| 로직 | Vanilla JavaScript ES6+ | game.js 리팩토링, sm2-algorithm.js 신규 추가 |
| 데이터 | JS 전역 변수 | questions.js 기존 60제 유지 + 60제 추가 |
| 영속성 | localStorage | 복습 스케줄 데이터 저장 추가 |
| 배포 | 정적 파일 (file:// / GitHub Pages) | 기존 유지 |
| **의존성** | **없음 (zero)** | 외부 CDN/IP 지속 금지 |

**참조만 하는 리소스** (실제 코드는 포함하지 않음):
- `supermemo` npm 패키지 (MIT) — **알고리즘 공식만 참조, 독자 구현**
- `VienDinhCom/supermemo` (MIT, 336 stars) — SM-2 수식 참조

### 참조할 오픈소스 및 참조 방식

#### 적극 패턴 참조 (MIT — 구조·알고리즘 패턴만 차용, 코드 직접 복사 금지)

| 레포 | 참조할 설계 패턴 | 적용 대상 |
|------|-----------------|----------|
| **baturyilmaz/wordpecker-app** (MIT, 2,103★) | 5가지 문제 유형 객관식·T/F·빈칸·매칭·문장완성, 문제 타입별 렌더러 분기 설계 | `renderQuestion()` 확장 → `renderMultipleChoice()`, `renderFillBlank()`, `renderMatching()`, `renderSentenceComplete()` |
| **cosmoart/quiz-game** (MIT, 90★) | 3가지 게임 모드(Classic·Time·Infinity), 와일드카드(50:50, +10s, 생명), 키보드 단축키 | `GameMode` enum 신설, `wildcardStore` 상태, 키보드 이벤트 핸들러 |
| **sanidhyy/duolingo-clone** (MIT, 552★) | 하트 시스템, XP 포인트 구조, 카테고리 계층 설계 | `heartSystem()`, XP/레벨 계산 로직, 문제 유형 enum |
| **VienDinhCom/supermemo** (MIT, 336★) | SM-2 알고리즘: EF·간격·반복횟수 계산식 | `sm2-algorithm.js` — 독자 구현 |
| **RickCarlino/KoalaCards** (MIT, 48★) | FSRS 복습 큐 개념 (new/due/remedial 3단계) | 오답 복습 스케줄링에 SM-2를 접목한 `ReviewManager` |

#### 데이터 구조 참조 (코드 사용 불가)

| 레포 | 참조 방식 |
|------|---------|
| **hubingkang/vocabulary-corpus** (MIT, 428★) | 문제 데이터 구조 확장 시 단어 속성 설계(어원·문화맥락) 참고 |
| **subconcept-labs/ulangi** (GPL-3.0, 457★) | 단어→카드→퀴즈 워크플로우 개념만 참조. 코드 금지 |

### 라이선스 리스크

| 항목 | 위험 | 대응 |
|------|------|------|
| ulangi 코드 복사 | **HIGH** (GPL-3.0) | 절대 금지. 설계 아이디어만 참고 |
| wordpecker-app 코드 복사 | LOW (MIT) | 패턴 참조만, 독자 구현 |
| quiz-game 코드 복사 | LOW (MIT) | 패턴 참조만, 독자 구현 |
| supermemo 알고리즘 구현 | **NONE** | SM-2 알고리즘은 특허 만료, 수식은 수학적 공식으로 저작권 대상 아님. npm 패키지 대신 공식 기반 독자 구현 |
| duolingo-clone 코드 복사 | LOW (MIT) | 서버/DB 의존 패턴이므로 직접 복사 불가. 설계만 참고 |
| 외부 API 의존 | — | API 호출 제로. 100% 로컬 데이터 |

### 기존 코드 변경 범위 분석

기존 게임(`game/`) 파일별 상태:

| 파일 | 상태 | 변경 계획 |
|------|------|----------|
| `index.html` | **중간 변경** | 퀴즈 화면 UI 확장(빈칸 입력, 매칭 드래그), 게임 모드 선택 추가, 타이머 HUD, 와일드카드 버튼 |
| `style.css` | **중간 변경** | 새로운 문제 유형 스타일(.fill-blank-input, .matching-pair, .wildcard-btn 등), 타이머 애니메이션, 게임 모드 카드 |
| `game.js` | **대폭 리팩토링** | 상태 기계 유지 + 모듈화, renderQuestion() 분기, 타이머 로직, 와일드카드 로직, SM-2 복습 통합 |
| `data/categories.js` | **경미 변경** | 게임 모드 상수 추가, 와일드카드 설정 상수 추가 |
| `data/questions.js` | **확장** | 기존 60제 유지 + 신규 유형(빈칸·매칭·문장완성) 문제 60제 추가 |
| **`game/sm2-algorithm.js`** | **신규** | SuperMemo-2 독자 구현 모듈 |
| **`game/audio.js`** | **신규** | Web Speech API 기반 TTS (외부 API 없음) |
| `README.md` | **경미 변경** | 신규 기능 문서화 |

### 독자 구현할 기능

모든 기능은 오픈소스 코드 복사 없이 독자 구현한다:

1. **문제 유형 렌더러 시스템**
   - 기존 `renderQuestion()` → `dispatchQuestionRenderer(q.type)` 분기
   - 각 유형별 전용 렌더러 함수:
     - `renderMultipleChoice()` — 기존 패턴 유지 (객관식 버튼 4개)
     - `renderTrueFalse()` — 기존 패턴 유지 (True/False 버튼 2개)
     - `renderFillBlank()` — `<input>` 필드 + 정답 문자열 비교
     - `renderMatching()` — 왼쪽 용어 ↔ 오른쪽 정의 드롭다운 매칭
     - `renderSentenceComplete()` — 문장 내 드롭다운 선택

2. **게임 모드 시스템**

   | 모드 | 규칙 | 출제 수 | 타이머 |
   |------|------|--------|--------|
   | Classic | 기존과 동일 | 10문제 | 제한 없음 |
   | Timed | 전체 제한 시간 | 10문제 | 180초 | 
   | Speed | 문제당 제한 시간 | 15문제 | 문제당 12초 |

3. **와일드카드 아이템 시스템**
   - 50:50 — 오답 2개 제거 (기본 지급: 1회)
   - +Time — 타이머 모드에서 15초 추가 (기본 지급: 1회)
   - Shield — 오답 시 생명 소모, 스트릭 유지 (기본 지급: 1회)

4. **SM-2 복습 스케줄링**
   ```
   EF' = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))
   if q < 3: I = 1, n = 0  (리셋)
   if n = 0: I = 1
   if n = 1: I = 6 (일)
   if n >= 2: I = I × EF
   ```
   - 각 문제별 SM-2 Item을 localStorage에 영속 저장
   - 오답 문제와 정답 문제 모두 SM-2로 스케줄링
   - 당일 복습이 필요한 문제 목록을 시작 화면에 "Today's Review"로 표시
   - `sm2-algorithm.js`에서 순수 함수로 구현, game.js에서 호출

5. **키보드 단축키**
   - `1`~`4` (또는 `A`~`D`): 객관식 선택지 선택
   - `Space` / `Enter` / `→`: 다음 문제
   - `H`: 힌트 보기
   - `W`: 와일드카드 메뉴

6. **Web Speech API TTS**
   - `speechSynthesis` API로 문제 및 단어 음성 출력
   - Play 버튼으로 원어민 발음 듣기 (브라우저 내장, API 불필요)

### 구현 우선순위 및 단계

| 순서 | 작업 | 파일 | 예상 시간 | 의존성 |
|------|------|------|----------|--------|
| **P1** | 문제 데이터셋 확장 (60→120제) | `data/questions.js` | 中 | 없음 |
| **P2** | `categories.js` 상수 확장 (게임 모드·와일드카드·문제 타입) | `data/categories.js` | 小 | 없음 |
| **P3** | SM-2 알고리즘 모듈 구현 | `game/sm2-algorithm.js` (신규) | 中 | 없음 |
| **P4** | `game.js` 모듈화 리팩토링 + 문제 유형 렌더러 | `game.js` | 大 | P1, P2 |
| **P5** | 게임 모드 시스템 + 타이머 로직 | `game.js` | 中 | P4 |
| **P6** | 와일드카드 시스템 | `game.js` | 小 | P4 |
| **P7** | SM-2 복습 스케줄링 통합 | `game.js` | 中 | P3, P4 |
| **P8** | 키보드 단축키 + 접근성 | `game.js`, `index.html` | 小 | P4 |
| **P9** | Web Speech API TTS | `game/audio.js` (신규) | 小 | 없음 |
| **P10** | UI/스타일 확장 (새로운 문제 유형·게임 모드·와일드카드) | `index.html`, `style.css` | 中 | P4~P9 |
| **P11** | README 업데이트 | `README.md` | 小 | P10 |
| **P12** | 통합 검증 | 전체 | 中 | P1~P11 |

### 구체적 파일/컴포넌트 구조

#### 최종 파일 트리
```
game/
├── index.html                  # 메인 HTML (확장: 게임 모드 선택, 빈칸 입력, 매칭 UI, 와일드카드 버튼)
├── style.css                   # 확장 스타일 (새 유형, 타이머, 와일드카드, SM-2 복습 목록)
├── game.js                     # 코어 로직 (상태 기계 + 모듈 분리)
├── sm2-algorithm.js            # [신규] SM-2 순수 함수 (calcEF, calcInterval, createItem, updateItem)
├── audio.js                    # [신규] Web Speech API TTS 헬퍼
├── data/
│   ├── categories.js           # 확장 상수: QUESTION_TYPES, GAME_MODES, WILDCARD_SETTINGS
│   └── questions.js            # 120제 (기존 60제 + 빈칸·매칭·문장완성 60제)
└── README.md                   # 업데이트된 문서
```

#### `categories.js` 확장 명세

기존 `CATEGORIES`, `DIFFICULTIES`, `QUIZ_SETTINGS` 는 유지하고 아래를 **추가**:

```javascript
const QUESTION_TYPES = {
  multiple:        { key: "multiple",        label: "Multiple Choice", answerCount: 4 },
  truefalse:       { key: "truefalse",       label: "True / False",    answerCount: 2 },
  fill_blank:      { key: "fill_blank",      label: "Fill in the Blank", answerCount: 0 },
  matching:        { key: "matching",        label: "Matching",        answerCount: 0 },
  sentence_complete: { key: "sentence_complete", label: "Sentence Complete", answerCount: 0 }
};

const GAME_MODES = {
  classic: { key: "classic", label: "Classic",   questions: 10, timePerQuestion: 0,    totalTime: 0,    description: "No time limit, 10 questions" },
  timed:   { key: "timed",   label: "Timed",     questions: 10, timePerQuestion: 0,    totalTime: 180,  description: "10 questions in 3 minutes" },
  speed:   { key: "speed",   label: "Speed Run", questions: 15, timePerQuestion: 12,   totalTime: 0,    description: "15 questions, 12 seconds each" }
};

const WILDCARD_SETTINGS = {
  fiftyFifty: { key: "fiftyFifty", label: "50:50",   icon: "🎯", startingCount: 1, description: "Remove 2 wrong answers" },
  addTime:    { key: "addTime",    label: "+Time",    icon: "⏱️", startingCount: 1, description: "Add 15 seconds" },
  shield:     { key: "shield",     label: "Shield",   icon: "🛡️", startingCount: 1, description: "Protect your streak" }
};

// QUIZ_SETTINGS에 추가
QUIZ_SETTINGS.wildcardEarnThreshold = 5;  // 5연속 정답 시 와일드카드 1개 추가 지급
QUIZ_SETTINGS.sm2ReviewIntervalCheckMinutes = 1440;  // 24시간마다 복습 체크
```

#### `questions.js` 확장 명세

기존 60문제(카테고리별 12문제, multiple + truefalse)는 **유지**한다. 각 카테고리에 아래 신규 유형 문제를 **추가**:

| 카테고리 | 추가 multiple | 추가 truefalse | 추가 fill_blank | 추가 matching | 추가 sentence_complete | 카테고리당 신규 합계 |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|
| vocabulary | 2 | 0 | 3 | 3 | 4 | 12 |
| grammar | 2 | 0 | 3 | 4 | 3 | 12 |
| prepositions | 2 | 0 | 4 | 3 | 3 | 12 |
| phrasal_verbs | 2 | 0 | 3 | 3 | 4 | 12 |
| idioms | 2 | 0 | 4 | 3 | 3 | 12 |
| **합계** | **10** | **0** | **17** | **16** | **17** | **60** |

신규 문제 유형별 JSON 스키마:

**fill_blank:**
```json
{
  "id": "vocab_013",
  "category": "vocabulary",
  "difficulty": "easy",
  "type": "fill_blank",
  "question": "The word '___' means to move quickly.",
  "correct_answer": "hurry",
  "acceptable_answers": ["hurry", "rush", "dash"],
  "explanation": "Multiple synonyms accepted: hurry, rush, dash all mean to move quickly.",
  "hint": "It starts with 'h'"
}
```

**matching:**
```json
{
  "id": "gram_017",
  "category": "grammar",
  "difficulty": "medium",
  "type": "matching",
  "pairs": [
    { "left": "Noun", "right": "A person, place, thing, or idea" },
    { "left": "Verb", "right": "An action or state of being" },
    { "left": "Adjective", "right": "Describes a noun or pronoun" },
    { "left": "Adverb", "right": "Describes a verb, adjective, or another adverb" }
  ],
  "question": "Match each part of speech to its definition.",
  "explanation": "The 4 main parts of speech: Nouns name things, Verbs show action, Adjectives describe nouns, Adverbs describe verbs/adjectives.",
  "hint": "Each matches one definition"
}
```

**sentence_complete:**
```json
{
  "id": "prep_017",
  "category": "prepositions",
  "difficulty": "medium",
  "type": "sentence_complete",
  "sentence_template": "I have been waiting ___ you ___ 3 o'clock.",
  "blanks": [
    { "position": 1, "correct": "for", "options": ["for", "to", "at", "by"] },
    { "position": 2, "correct": "since", "options": ["since", "for", "from", "during"] }
  ],
  "question": "Complete the sentence with the correct prepositions.",
  "explanation": "Use 'wait for' (someone) and 'since' with a specific starting point in time.",
  "hint": "Think about duration vs. starting point"
}
```

#### `sm2-algorithm.js` 구현 명세 (신규)

```javascript
/**
 * sm2-algorithm.js — SuperMemo-2 spaced repetition algorithm
 * Reference: VienDinhCom/supermemo (MIT, formula only — 독자 구현)
 * 
 * SM-2 Formula:
 *   EF' = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))
 *   IF q < 3: reset (I=1, n=0)
 *   IF n=0: I=1
 *   IF n=1: I=6
 *   IF n>=2: I = I × EF
 */

/** @typedef {{ id: string, ef: number, n: number, i: number, nextReview: number }} SM2Item */

/** Create a new SM-2 item for a question */
function sm2CreateItem(questionId) { ... }

/** Apply SM-2 update after a user response (q = 0~5 grade) */
function sm2Update(item, grade) { ... }

/** Calculate next review timestamp (Date.now() + interval in ms) */
function sm2NextReview(item) { ... }

/** Get all items due for review today from localStorage */
function sm2GetDueItems() { ... }

/** Load SM-2 items from localStorage */
function sm2LoadItems() { ... }

/** Save SM-2 items to localStorage */
function sm2SaveItems(items) { ... }

/** Check if an item is due for review */
function sm2IsDue(item) { ... }
```

key: `"englishQuizSM2Items"`, value: `{ [questionId]: SM2Item }`

#### `game.js` 리팩토링 명세

기존 state machine은 유지한다. 주요 변경:

1. **GameState 확장**
```javascript
let gameState = {
  // 기존 필드 유지
  status, category, difficulty, mainDeck, wrongQueue,
  currentQuestion, isReviewQuestion, questionNumber, totalQuestions,
  score, streak, maxStreak, correctCount, wrongAnswers,
  
  // 신규 필드
  gameMode: "classic",           // GAME_MODES 키
  questionType: null,            // 현재 문제의 QUESTION_TYPES 키
  remainingTime: 0,              // 타이머 남은 초
  timerInterval: null,           // setInterval ID
  wildcards: {                   // 와일드카드 보유 수
    fiftyFifty: 1, addTime: 1, shield: 1
  },
  shieldedThisQuestion: false,   // 현재 문제에서 Shield 사용 여부
  sm2Items: {},                  // SM-2 학습 상태 (localStorage에서 로드)
  lives: 5                       // 생명 (Duolingo-clone 하트 시스템 참조)
};
```

2. **renderQuestion() 분기**
```javascript
function renderQuestion(q, isReview) {
  // ... 공통 초기화 (기존 코드 유지)
  
  switch (q.type) {
    case "multiple":        renderMultipleChoice(q); break;
    case "truefalse":       renderTrueFalse(q); break;
    case "fill_blank":      renderFillBlank(q); break;
    case "matching":        renderMatching(q); break;
    case "sentence_complete": renderSentenceComplete(q); break;
  }
}
```

3. **타이머 통합**
```javascript
function startTimer() {
  if (gameState.gameMode === "classic") return;
  if (gameState.gameMode === "timed") {
    gameState.remainingTime = GAME_MODES.timed.totalTime;
  } else if (gameState.gameMode === "speed") {
    gameState.remainingTime = GAME_MODES.speed.timePerQuestion;
  }
  gameState.timerInterval = setInterval(tickTimer, 1000);
}

function tickTimer() {
  gameState.remainingTime--;
  updateTimerDisplay();
  if (gameState.remainingTime <= 0) {
    clearInterval(gameState.timerInterval);
    if (gameState.gameMode === "timed") showResult();
    else handleAnswer("__TIMEOUT__");
  }
}
```

4. **와일드카드 적용**
```javascript
function useWildcard(type) {
  if (gameState.wildcards[type] <= 0) return;
  gameState.wildcards[type]--;
  
  switch (type) {
    case "fiftyFifty": applyFiftyFifty(); break;
    case "addTime":    gameState.remainingTime += 15; updateTimerDisplay(); break;
    case "shield":     gameState.shieldedThisQuestion = true; break;
  }
  updateWildcardDisplay();
}
```

5. **handleAnswer() 확장 — SM-2 통합 + Shield 적용**
```javascript
function handleAnswer(selected) {
  // ... 기존 disable 로직 유지
  
  if (gameState.shieldedThisQuestion && !isCorrect) {
    // Shield로 스트릭 보호: 오답이지만 streak 유지, lives 감소 없음
    gameState.shieldedThisQuestion = false;
    // SM-2 grade: shield 사용 오답 = grade 2 (poor but not fail)
    sm2UpdateItem(q.id, 2);
  } else {
    if (isCorrect) {
      handleCorrectAnswer(q);
      sm2UpdateItem(q.id, 5); // perfect recall
    } else {
      handleWrongAnswer(q);
      sm2UpdateItem(q.id, 1); // complete blackout
    }
  }
}
```

6. **생명(Lives) 시스템 추가** (Duolingo-clone 참조)
   - 기본 5개 생명
   - 오답 시 생명 1개 감소
   - 생명 0이면 게임 오버 (퀴즈 중단, 결과 화면으로)
   - Shield 사용 시 생명 감소 방지

#### `index.html` 변경 명세

기존 3섹션 구조 유지. 추가할 요소:

**#start-screen 추가:**
```html
<!-- Game Mode Selection -->
<div class="section-label">Game Mode</div>
<div id="mode-list" class="btn-group" role="group" aria-label="Game mode selection">
  <!-- JS로 동적 생성 -->
</div>

<!-- Today's Review (SM-2) -->
<div id="review-panel" class="review-panel hidden">
  <h2 class="panel-title">📅 Today's Review</h2>
  <p id="review-count" class="review-count"></p>
  <button id="review-btn" class="btn btn-secondary">Start Review</button>
</div>
```

**#quiz-screen 추가:**
```html
<!-- Timer HUD -->
<span id="timer-display" class="timer hidden">⏱ 3:00</span>

<!-- Wildcard bar -->
<div id="wildcard-bar" class="wildcard-bar hidden">
  <button class="wildcard-btn" data-type="fiftyFifty">🎯 50:50 <span class="wc-count">1</span></button>
  <button class="wildcard-btn" data-type="addTime">⏱ +Time <span class="wc-count">1</span></button>
  <button class="wildcard-btn" data-type="shield">🛡️ Shield <span class="wc-count">1</span></button>
</div>

<!-- Fill-in-the-blank input -->
<input id="fill-blank-input" class="fill-blank-input hidden" type="text" placeholder="Type your answer...">

<!-- Matching area -->
<div id="matching-area" class="matching-area hidden">
  <!-- JS로 동적 생성 -->
</div>

<!-- Sentence complete area -->
<div id="sentence-complete-area" class="sentence-complete-area hidden">
  <!-- JS로 동적 생성 -->
</div>

<!-- Speech button -->
<button id="speak-btn" class="btn btn-secondary btn-small">🔊 Listen</button>

<!-- Lives display -->
<span id="lives-display" class="lives">
  ❤️❤️❤️❤️❤️
</span>
```

#### `style.css` 변경 명세

기존 CSS는 그대로 유지하고 아래 스타일을 **추가**:

- `.timer` — 타이머 표시, 긴급 시 빨간색 깜빡임 애니메이션
- `.timer.urgent` — 10초 미만 시 color: var(--incorrect), animation: pulse
- `.wildcard-bar` — 상단 HUD 아래 가로 배치 flex
- `.wildcard-btn` — 작은 버튼, 아이콘 + 라벨 + 남은 개수
- `.wildcard-btn:disabled` — 회색, 개수 0일 때
- `.fill-blank-input` — 큰 입력창, 정답 시 테두리 var(--correct), 오답 시 var(--incorrect)
- `.matching-area` — 2열 그리드, 왼쪽 용어 ↔ 오른쪽 드롭다운
- `.matching-pair` — 한 쌍의 매칭 행
- `.matching-select` — 드롭다운 select 요소
- `.sentence-complete-area` — 문장 내 inline 드롭다운
- `.sentence-blank-select` — 문장 중간에 들어가는 작은 select
- `.review-panel` — 시작 화면의 SM-2 복습 알림 카드
- `.lives` — 하트 이모지, 오답 시 하나씩 사라짐 (opacity transition)
- `.mode-btn` — 게임 모드 선택 버튼 스타일
- `@keyframes pulse` — 긴급 타이머 애니메이션

---

## 결론 (Conclusion)

### 구현 요약

기존 60제 Vanilla JS 정적 퀴즈 게임을 120제·5가지 문제 유형·3가지 게임 모드·와일드카드·SM-2 복습 스케줄링을 갖춘 고도화된 영어 학습 앱으로 업그레이드한다. 모든 기능은 외부 의존성 없이 순수 Vanilla JS + CSS로 구현하며, 기존 코드를 최대한 보존한 증분 개선 방식으로 접근한다.

핵심 증분:
1. **데이터**: 60→120제, fill_blank/matching/sentence_complete 신규 유형 추가
2. **로직**: SM-2 알고리즘, 타이머, 와일드카드, 생명 시스템, 문제 유형별 렌더러 분기
3. **UI**: 게임 모드 선택, 타이머 HUD, 와일드카드 바, 음성 지원, 복습 알림
4. **파일**: `sm2-algorithm.js`, `audio.js` 2개 신규 파일

### member-epsilon 전달 지침

**CRITICAL: 모든 작업은 `output/방식-영어-퀴즈-게임-개발/game/` 디렉터리 내에서만 수행한다. agent-team 레포의 다른 파일은 절대 수정하지 않는다.**

#### 실행 순서 (위에서 아래로, 의존성 준수)

**Step 1: `data/categories.js` 확장**
- 기존 CATEGORIES, DIFFICULTIES, QUIZ_SETTINGS 는 유지
- QUESTION_TYPES, GAME_MODES, WILDCARD_SETTINGS 상수 추가
- QUIZ_SETTINGS에 wildcardEarnThreshold, sm2ReviewIntervalCheckMinutes 추가

**Step 2: `data/questions.js` 확장**
- 기존 60문제 전부 유지 (수정 금지)
- 각 카테고리별 fill_blank, matching, sentence_complete, multiple 추가 문제 12개씩 작성 (총 60문제)
- 신규 문제는 id를 vocab_013부터 시작, 기존 문제와 중복 없는 ID 사용
- 모든 신규 문제에 explanation 필수 포함

**Step 3: `game/sm2-algorithm.js` 신규 생성**
- SuperMemo-2 알고리즘 순수 함수 구현 (sm2CreateItem, sm2Update, sm2NextReview, sm2GetDueItems, sm2LoadItems, sm2SaveItems, sm2IsDue)
- localStorage 키: "englishQuizSM2Items"
- grade: 0~5 (0=complete blackout, 5=perfect recall)
- interval: 일(day) 단위 → Date.now() + interval * 86400000

**Step 4: `game/audio.js` 신규 생성**
- `window.speechSynthesis` API 사용
- `speakWord(text, lang = "en-US")` 함수
- `stopSpeaking()` 함수
- 브라우저 미지원 시 조용히 fallback (에러 없음)

**Step 5: `game.js` 리팩토링**
- `gameState`에 신규 필드 추가 (gameMode, questionType, remainingTime, timerInterval, wildcards, shieldedThisQuestion, sm2Items, lives)
- `renderQuestion()` → switch 분기로 문제 유형별 렌더러 호출
- `renderMultipleChoice()`, `renderTrueFalse()`는 기존 코드를 함수로 추출
- `renderFillBlank(q)` — `<input>` 생성, `handleFillBlankSubmit()`에서 acceptable_answers 비교 (대소문자 무시)
- `renderMatching(q)` — pairs 배열로 왼쪽 라벨 + 오른쪽 `<select>` 생성, `handleMatchingSubmit()`에서 전체 쌍 비교
- `renderSentenceComplete(q)` — blanks 배열로 문장 내 `<select>` 삽입
- `startTimer()`, `tickTimer()`, `updateTimerDisplay()` 추가
- `useWildcard(type)`, `applyFiftyFifty()`, `updateWildcardDisplay()` 추가
- `handleAnswer()`에서 shield 처리 + SM-2 업데이트 연동
- `handleCorrectAnswer()`, `handleWrongAnswer()`에서 생명 시스템 연동
- 키보드 이벤트 리스너: '1'~'4'/'a'~'d' = 선택, 'Space'/'Enter'/'ArrowRight' = 다음, 'h' = 힌트, 'w' = 와일드카드
- 시작 화면에서 SM-2 복습 대상 항목 표시 (`sm2GetDueItems()`)
- `showResult()`에서 SM-2 저장

**Step 6: `index.html` 확장**
- 게임 모드 선택 UI 추가
- 타이머 HUD, 와일드카드 바, 생명 표시 추가
- fill-blank input, matching area, sentence-complete area 추가
- Speak 버튼 추가
- SM-2 복습 패널 추가
- 스크립트 로드 순서: categories.js → questions.js → sm2-algorithm.js → audio.js → game.js

**Step 7: `style.css` 확장**
- 신규 UI 요소에 대한 스타일 추가 (타이머·와일드카드·빈칸입력·매칭·문장완성·복습패널·생명·pulse 애니메이션)
- 기존 스타일 보존

**Step 8: `README.md` 업데이트**
- 신규 기능 문서화 (게임 모드, 와일드카드, 복습 스케줄링, 문제 유형)
- 신규 문제 데이터 추가 방법 안내

**Step 9: 통합 검증**
- Chrome에서 `index.html` 직접 열어 모든 게임 모드 테스트
- 각 문제 유형 정상 렌더링 및 정답 판정 확인
- 와일드카드 3종 정상 동작 확인
- 타이머 모드 초과 시 결과 화면 전환 확인
- SM-2 복습 데이터 localStorage 저장/로드 확인
- 음성 출력 확인 (브라우저 지원 여부 확인)
- 모바일 뷰포트(375px) 렌더링 확인
- 오답 재출제 + SM-2 연동 확인
- 키보드 단축키 작동 확인

### 위험 요소

| 위험 | 완화 방안 |
|------|----------|
| `speechSynthesis` 일부 브라우저 미지원 | try/catch 감싸고, Speak 버튼 미지원 시 숨김 |
| 많은 문제 데이터로 questions.js 파일 거대화 | 현재 120제는 710줄 → ~700줄 추가 → ~1,400줄. 충분히 관리 가능한 크기 |
| game.js 함수 과다로 유지보수 어려움 | 상태 기계 패턴 유지, 함수 역할 명확히 분리. 400→~700줄 예상 |
| SM-2 localStorage 데이터 손상 | JSON parse에 try/catch, 손상 시 초기화 |
| 매칭/문장완성 타입 문제 출제 시 세션 문제 수 초과 | 세션 문제 수 = GAME_MODES 기준. 매칭은 1문제로 카운트 |

### 예상 산출물 크기

| 파일 | 기존 | 변경 후 |
|------|------|---------|
| `index.html` | 139줄 | ~200줄 |
| `style.css` | 427줄 | ~600줄 |
| `game.js` | 495줄 | ~750줄 |
| `sm2-algorithm.js` | — | ~120줄 |
| `audio.js` | — | ~40줄 |
| `data/categories.js` | 64줄 | ~130줄 |
| `data/questions.js` | 710줄 | ~1,450줄 |
| `README.md` | 67줄 | ~100줄 |
| **합계** | 1,902줄 | ~3,390줄 |