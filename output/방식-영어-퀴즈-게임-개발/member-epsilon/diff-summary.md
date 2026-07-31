# Diff Summary — member-epsilon

**날짜:** 2026-05-29 11:30
**변경 유형:** 기존 코드 고도화 (Phase 2 증분 개선)

---

## 변경된 파일 요약

### game/data/categories.js (수정, 64→86줄)

**추가된 상수:**
- `QUESTION_TYPES`: multiple, truefalse, fill_blank, matching, sentence_complete (5가지 유형)
- `GAME_MODES`: classic (10문제, 무제한), timed (10문제, 180초), speed (15문제, 12초/문제)
- `WILDCARD_SETTINGS`: fiftyFifty, addTime, shield 각 key/label/icon/startingCount
- `QUIZ_SETTINGS.wildcardEarnThreshold`: 5연속 정답 시 와일드카드 추가 지급
- `QUIZ_SETTINGS.sm2ReviewIntervalCheckMinutes`: 1440 (24시간)

### game/data/questions.js (확장, 710→1486줄)

**추가된 문제 (기존 60제 보존):**
- vocabulary: +12문제 (multiple 2, fill_blank 3, matching 3, sentence_complete 4)
- grammar: +12문제 (multiple 2, fill_blank 3, matching 4, sentence_complete 3)
- prepositions: +12문제 (multiple 2, fill_blank 4, matching 3, sentence_complete 3)
- phrasal_verbs: +12문제 (multiple 2, fill_blank 3, matching 3, sentence_complete 4)
- idioms: +12문제 (multiple 2, fill_blank 4, matching 3, sentence_complete 3)
- 신규 유형별: fill_blank 17 + matching 16 + sentence_complete 17 + multiple 10 = 60문제
- 신규 문제 id: vocab_013~vocab_024, gram_013~gram_024, prep_013~prep_024, phrv_013~phrv_024, idio_013~idio_024

### game/sm2-algorithm.js (신규, 87줄)

SuperMemo-2 독자 구현 (supermemo 패키지 수식만 참조):
- `sm2CreateItem(questionId)`: 새 SM-2 아이템 생성 (ef=2.5, n=0, i=0)
- `sm2Update(item, grade)`: grade 0~5 기반 EF 계산 및 간격 업데이트
- `sm2LoadItems()` / `sm2SaveItems(items)`: localStorage "englishQuizSM2Items" 키로 영속 저장
- `sm2IsDue(item)`: 현재 시각 기준 복습 필요 여부 판정
- `sm2GetDueItems()`: 오늘 복습이 필요한 모든 아이템 반환

### game/audio.js (신규, 38줄)

Web Speech API TTS 헬퍼:
- `speakWord(text, lang)`: 브라우저 TTS로 텍스트 읽기 (en-US 기본)
- `stopSpeaking()`: 현재 재생 중인 음성 중지
- 브라우저 미지원 시 silent fallback (에러 없음)

### game/game.js (대폭 리팩토링, 495→970줄)

**신규 gameState 필드:**
```javascript
gameMode, questionType, remainingTime, timerInterval,
wildcards: { fiftyFifty, addTime, shield },
shieldedThisQuestion, sm2Items, lives: 5, wildcardEarnCount
```

**신규/변경 함수 (총 40+개):**
- 문제 유형 렌더러 분기: `renderQuestion()` → `renderMultipleChoice()`, `renderTrueFalse()`, `renderFillBlank()`, `renderMatching()`, `renderSentenceComplete()`
- 제출 핸들러: `handleFillBlankSubmit()`, `handleMatchingSubmit()`, `handleSentenceCompleteSubmit()`
- 타이머: `startTimer()`, `tickTimer()`, `updateTimerDisplay()`, `clearTimer()`
- 와일드카드: `useWildcard(type)`, `applyFiftyFifty()`, `updateWildcardDisplay()`
- 생명: `updateLivesDisplay()`, handleWrongAnswer에서 lives 감소
- SM-2 연동: `sm2UpdateItem()`, `processAnswer()`에서 grade 자동 계산
- 복습: `buildReviewPanel()`, `startReviewGame(dueItems)`
- 키보드: `handleKeyboard()` — 1-4/A-D/Enter/Space/H/W
- TTS: Speak 버튼 이벤트 핸들러
- `setupQuizUI()`: 모드별 타이머/와일드카드 초기 설정

### game/index.html (중간 변경, 139→177줄)

**추가된 UI:**
- 게임 모드 선택 (`#mode-list`) — Classic / Timed / Speed 버튼 그룹
- SM-2 복습 패널 (`#review-panel`) — "Today's Review" 알림
- 타이머 HUD (`#timer-display`)
- 와일드카드 바 (`#wildcard-bar`) — 50:50 / +Time / Shield 버튼
- 생명 표시 (`#lives-display`)
- 빈칸 입력 (`#fill-blank-input` + `#fill-blank-submit`)
- 매칭 영역 (`#matching-area` + `#matching-submit`)
- 문장 완성 영역 (`#sentence-complete-area` + `#sentence-submit`)
- 음성 버튼 (`#speak-btn`)
- 스크립트 로드 순서 변경: +sm2-algorithm.js, +audio.js

### game/style.css (중간 변경, 427→637줄)

**추가된 스타일 (210줄):**
- `.timer`, `.timer.urgent` — 긴급 시 pulse 애니메이션
- `.wildcard-bar`, `.wildcard-btn`, `.wc-count`, `.wildcard-btn:disabled`
- `.fill-blank-input`, `.fill-blank-wrapper`, `.input-correct`, `.input-incorrect`
- `.matching-area`, `.matching-pair`, `.matching-term`, `.matching-select`, `.select-correct`, `.select-incorrect`
- `.sentence-complete-area`, `.sentence-blank-select`
- `.review-panel`, `.review-count`
- `.mode-btn`, `.mode-label`, `.mode-desc`, `.game-mode-group`
- `.lives`, `.lost-lives`
- `.hud-left`, `.hud-center`, `.hud-right`
- `@keyframes pulse` — 긴급 타이머 애니메이션
- 모바일 400px 이하 미디어 쿼리 추가

---

## 주요 설계 결정

| 결정 | 내용 |
|------|------|
| 제로 의존성 | npm 패키지 대신 SM-2 수식 독자 구현, Web Speech API는 브라우저 내장 기능 |
| all-or-nothing 채점 | matching/sentence_complete는 모든 쌍 정답 시에만 correct 처리 |
| wildcardEarnCount | 5연속 정답마다 모든 와일드카드 +1 (중독성 강화) |
| speed 모드 타이머 | 문제당 타이머, 매 renderQuestion 시 reset (Timed는 초기 1회) |
| 생명 0 게임오버 | handleWrongAnswer에서 lives 체크 후 즉시 showResult() |
| SM-2 grade 매핑 | 정답=5, Shield 오답=2, 일반 오답=1, 타임아웃 오답=1 |
| 오답 재출제 보존 | 기존 wrongQueue 로직 유지, fill_blank/matching/sentence_complete도 동일하게 처리 |