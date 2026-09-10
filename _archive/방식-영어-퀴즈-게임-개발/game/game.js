/**
 * game.js — English Quiz Game core logic
 * State machine: IDLE → SETUP → QUESTION_DISPLAY → ANSWER_CHECK
 *             → FEEDBACK_DISPLAY → NEXT_QUESTION_CHECK → SESSION_END → RESULT_DISPLAY
 * Supports 5 question types, 3 game modes, wildcards, SM-2 review
 */

// ── Game State ─────────────────────────────────────────────────────────────
var gameState = {
  status: "IDLE",
  category: null,
  difficulty: null,
  mainDeck: [],
  wrongQueue: [],
  currentQuestion: null,
  isReviewQuestion: false,
  questionNumber: 0,
  totalQuestions: 0,
  score: 0,
  streak: 0,
  maxStreak: 0,
  correctCount: 0,
  wrongAnswers: [],
  gameMode: "classic",
  questionType: null,
  remainingTime: 0,
  timerInterval: null,
  wildcards: { fiftyFifty: 1, addTime: 1, shield: 1 },
  shieldedThisQuestion: false,
  sm2Items: {},
  lives: 5,
  wildcardEarnCount: 0
};

// ── DOM Cache ──────────────────────────────────────────────────────────────
var screens = {
  start:  document.getElementById("start-screen"),
  quiz:   document.getElementById("quiz-screen"),
  result: document.getElementById("result-screen")
};

var els = {
  categoryList:    document.getElementById("category-list"),
  difficultyList:  document.getElementById("difficulty-list"),
  startBtn:        document.getElementById("start-btn"),
  questionCounter: document.getElementById("question-counter"),
  scoreDisplay:    document.getElementById("score-display"),
  streakDisplay:   document.getElementById("streak-display"),
  progressBar:     document.getElementById("progress-bar"),
  questionBadge:   document.getElementById("question-badge"),
  questionText:    document.getElementById("question-text"),
  answersContainer:document.getElementById("answers-container"),
  hintBtn:         document.getElementById("hint-btn"),
  hintText:        document.getElementById("hint-text"),
  feedbackArea:    document.getElementById("feedback-area"),
  feedbackResult:  document.getElementById("feedback-result"),
  feedbackExplain: document.getElementById("feedback-explanation"),
  nextBtn:         document.getElementById("next-btn"),
  resultGrade:     document.getElementById("result-grade"),
  resultScore:     document.getElementById("result-score"),
  resultAccuracy:  document.getElementById("result-accuracy"),
  resultStreak:    document.getElementById("result-streak"),
  wrongSection:    document.getElementById("wrong-answers-section"),
  wrongList:       document.getElementById("wrong-answers-list"),
  restartBtn:      document.getElementById("restart-btn"),
  homeBtn:         document.getElementById("home-btn"),
  scoresBody:      document.getElementById("scores-body"),

  modeList:        document.getElementById("mode-list"),
  reviewPanel:     document.getElementById("review-panel"),
  reviewCount:     document.getElementById("review-count"),
  reviewBtn:       document.getElementById("review-btn"),
  timerDisplay:    document.getElementById("timer-display"),
  wildcardBar:     document.getElementById("wildcard-bar"),
  livesDisplay:    document.getElementById("lives-display"),
  fillBlankInput:  document.getElementById("fill-blank-input"),
  matchingArea:    document.getElementById("matching-area"),
  sentenceCompleteArea: document.getElementById("sentence-complete-area"),
  speakBtn:        document.getElementById("speak-btn"),
  fillBlankSubmit: document.getElementById("fill-blank-submit"),
  matchingSubmit:  document.getElementById("matching-submit"),
  sentenceSubmit:  document.getElementById("sentence-submit")
};

// ── Utility Helpers ────────────────────────────────────────────────────────

function shuffle(array) {
  var arr = array.slice();
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
  }
  return arr;
}

function showScreen(name) {
  for (var k in screens) screens[k].classList.remove("active");
  screens[name].classList.add("active");
}

function setHidden(el, isHidden) {
  if (!el) return;
  el.classList.toggle("hidden", isHidden);
}

function clearTimer() {
  if (gameState.timerInterval) {
    clearInterval(gameState.timerInterval);
    gameState.timerInterval = null;
  }
}

function resetSubmitButtons() {
  setHidden(els.fillBlankInput, true);
  setHidden(els.fillBlankSubmit, true);
  setHidden(els.matchingArea, true);
  setHidden(els.matchingSubmit, true);
  setHidden(els.sentenceCompleteArea, true);
  setHidden(els.sentenceSubmit, true);
}

// ── Phase: initGame ────────────────────────────────────────────────────────
function initGame() {
  gameState.sm2Items = sm2LoadItems();
  buildCategoryButtons();
  buildDifficultyButtons();
  buildModeButtons();
  buildReviewPanel();
  loadHighScores();

  els.startBtn.addEventListener("click", startGame);
  els.nextBtn.addEventListener("click", nextQuestion);
  els.hintBtn.addEventListener("click", showHint);
  els.restartBtn.addEventListener("click", function () { showScreen("start"); buildReviewPanel(); });
  els.homeBtn.addEventListener("click", function () {
    clearTimer();
    showScreen("start");
    loadHighScores();
    buildReviewPanel();
  });
  els.speakBtn.addEventListener("click", function () {
    var q = gameState.currentQuestion;
    if (!q) return;
    if (q.type === "multiple" || q.type === "truefalse") {
      speakWord(q.question);
    } else if (q.type === "fill_blank") {
      speakWord(q.question);
    } else if (q.type === "sentence_complete") {
      speakWord(q.question + " " + q.sentence_template);
    } else if (q.type === "matching") {
      speakWord(q.question);
    }
  });
  els.fillBlankSubmit.addEventListener("click", handleFillBlankSubmit);
  els.matchingSubmit.addEventListener("click", handleMatchingSubmit);
  els.sentenceSubmit.addEventListener("click", handleSentenceCompleteSubmit);

  els.fillBlankInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") handleFillBlankSubmit();
  });

  document.addEventListener("keydown", handleKeyboard);

  showScreen("start");
}

// ── Build UI ───────────────────────────────────────────────────────────────

function buildCategoryButtons() {
  els.categoryList.innerHTML = "";
  Object.values(CATEGORIES).forEach(function (cat) {
    var btn = document.createElement("button");
    btn.className = "category-card";
    btn.dataset.key = cat.key;
    btn.setAttribute("aria-label", "Category: " + cat.label);
    btn.innerHTML =
      '<div class="category-icon">' + cat.icon + '</div>' +
      '<div class="category-name">' + cat.label + '</div>' +
      '<div class="category-desc">' + cat.description + '</div>';
    btn.addEventListener("click", function () { selectCategory(cat.key, btn); });
    els.categoryList.appendChild(btn);
  });
}

function buildDifficultyButtons() {
  els.difficultyList.innerHTML = "";
  Object.values(DIFFICULTIES).forEach(function (diff) {
    var btn = document.createElement("button");
    btn.className = "diff-btn";
    btn.dataset.key = diff.key;
    btn.setAttribute("aria-label", "Difficulty: " + diff.label);
    btn.innerHTML =
      '<span class="diff-label">' + diff.label + '</span>' +
      '<span class="diff-pts">' + diff.points + ' pts</span>';
    btn.addEventListener("click", function () { selectDifficulty(diff.key, btn); });
    els.difficultyList.appendChild(btn);
  });
}

function buildModeButtons() {
  els.modeList.innerHTML = "";
  Object.values(GAME_MODES).forEach(function (mode) {
    var btn = document.createElement("button");
    btn.className = "mode-btn";
    btn.dataset.key = mode.key;
    btn.setAttribute("aria-label", "Game mode: " + mode.label);
    btn.innerHTML =
      '<span class="mode-label">' + mode.label + '</span>' +
      '<span class="mode-desc">' + mode.description + '</span>';
    btn.addEventListener("click", function () { selectMode(mode.key, btn); });
    els.modeList.appendChild(btn);
  });
  if (els.modeList.firstChild) {
    els.modeList.firstChild.classList.add("selected");
    gameState.gameMode = els.modeList.firstChild.dataset.key;
  }
}

function buildReviewPanel() {
  var dueItems = sm2GetDueItems();
  if (dueItems.length > 0) {
    els.reviewCount.textContent = dueItems.length + " questions need review today";
    setHidden(els.reviewPanel, false);
    els.reviewBtn.onclick = function () {
      startReviewGame(dueItems);
    };
  } else {
    setHidden(els.reviewPanel, true);
  }
}

function selectCategory(key) {
  gameState.category = key;
  document.querySelectorAll(".category-card").forEach(function (b) {
    b.classList.toggle("selected", b.dataset.key === key);
  });
  checkStartReady();
}

function selectDifficulty(key) {
  gameState.difficulty = key;
  document.querySelectorAll(".diff-btn").forEach(function (b) {
    b.classList.toggle("selected", b.dataset.key === key);
  });
  checkStartReady();
}

function selectMode(key) {
  gameState.gameMode = key;
  document.querySelectorAll(".mode-btn").forEach(function (b) {
    b.classList.toggle("selected", b.dataset.key === key);
  });
}

function checkStartReady() {
  els.startBtn.disabled = !(gameState.category && gameState.difficulty);
}

// ── Phase: startGame ───────────────────────────────────────────────────────
function startGame() {
  clearTimer();
  var pool = QUESTIONS.filter(function (q) {
    return q.category === gameState.category && q.difficulty === gameState.difficulty;
  });

  if (pool.length === 0) {
    alert("No questions found for this combination. Please choose another.");
    return;
  }

  var mode = GAME_MODES[gameState.gameMode];
  var sessionSize = mode ? mode.questions : QUIZ_SETTINGS.questionsPerSession;

  var deck = shuffle(pool).slice(0, sessionSize);

  gameState.status = "SETUP";
  gameState.mainDeck = deck;
  gameState.wrongQueue = [];
  gameState.currentQuestion = null;
  gameState.isReviewQuestion = false;
  gameState.questionNumber = 0;
  gameState.totalQuestions = deck.length;
  gameState.score = 0;
  gameState.streak = 0;
  gameState.maxStreak = 0;
  gameState.correctCount = 0;
  gameState.wrongAnswers = [];
  gameState.remainingTime = 0;
  gameState.timerInterval = null;
  gameState.wildcards = { fiftyFifty: 1, addTime: 1, shield: 1 };
  gameState.shieldedThisQuestion = false;
  gameState.lives = 5;
  gameState.wildcardEarnCount = 0;

  showScreen("quiz");
  setupQuizUI();
  updateHUD();
  startTimer();
  nextQuestion();
}

function startReviewGame(dueItems) {
  clearTimer();
  var deck = [];
  dueItems.forEach(function (item) {
    var q = QUESTIONS.find(function (x) { return x.id === item.id; });
    if (q) deck.push(q);
  });

  if (deck.length === 0) {
    alert("No review questions available.");
    return;
  }

  gameState.status = "SETUP";
  gameState.mainDeck = shuffle(deck);
  gameState.wrongQueue = [];
  gameState.currentQuestion = null;
  gameState.isReviewQuestion = true;
  gameState.questionNumber = 0;
  gameState.totalQuestions = deck.length;
  gameState.score = 0;
  gameState.streak = 0;
  gameState.maxStreak = 0;
  gameState.correctCount = 0;
  gameState.wrongAnswers = [];
  gameState.gameMode = "classic";
  gameState.remainingTime = 0;
  gameState.timerInterval = null;
  gameState.wildcards = { fiftyFifty: 1, addTime: 1, shield: 1 };
  gameState.shieldedThisQuestion = false;
  gameState.lives = 5;
  gameState.wildcardEarnCount = 0;
  gameState.category = "vocabulary";
  gameState.difficulty = "medium";

  showScreen("quiz");
  setupQuizUI();
  updateHUD();
  nextQuestion();
}

function setupQuizUI() {
  var mode = GAME_MODES[gameState.gameMode];
  setHidden(els.timerDisplay, mode.key === "classic");
  setHidden(els.wildcardBar, false);
  updateWildcardDisplay();
  updateLivesDisplay();
}

// ── Phase: renderQuestion ──────────────────────────────────────────────────
function renderQuestion(questionObj, isReview) {
  gameState.currentQuestion = questionObj;
  gameState.isReviewQuestion = isReview;
  gameState.status = "QUESTION_DISPLAY";
  gameState.questionNumber++;
  gameState.shieldedThisQuestion = false;

  setHidden(els.feedbackArea, true);
  setHidden(els.nextBtn, true);
  setHidden(els.hintText, true);
  els.hintBtn.disabled = false;
  els.feedbackArea.classList.remove("correct", "incorrect");

  resetSubmitButtons();

  var catLabel = CATEGORIES[questionObj.category] ? CATEGORIES[questionObj.category].label : questionObj.category;
  var diffLabel = DIFFICULTIES[questionObj.difficulty] ? DIFFICULTIES[questionObj.difficulty].label : questionObj.difficulty;
  els.questionBadge.textContent = catLabel + " · " + diffLabel + (isReview ? " · Review" : "");

  els.questionText.textContent = questionObj.question;

  switch (questionObj.type) {
    case "multiple": renderMultipleChoice(questionObj); break;
    case "truefalse": renderTrueFalse(questionObj); break;
    case "fill_blank": renderFillBlank(questionObj); break;
    case "matching": renderMatching(questionObj); break;
    case "sentence_complete": renderSentenceComplete(questionObj); break;
    default: renderMultipleChoice(questionObj); break;
  }

  // speed mode: reset per-question timer
  if (gameState.gameMode === "speed") {
    clearTimer();
    gameState.remainingTime = GAME_MODES.speed.timePerQuestion;
    gameState.timerInterval = setInterval(tickTimer, 1000);
    updateTimerDisplay();
  }

  var progress = (gameState.questionNumber - 1) / gameState.totalQuestions * 100;
  els.progressBar.style.width = progress + "%";

  updateHUD();
}

function renderMultipleChoice(q) {
  els.answersContainer.innerHTML = "";
  var allAnswers = shuffle([q.correct_answer].concat(q.incorrect_answers));
  allAnswers.forEach(function (answer) {
    var btn = document.createElement("button");
    btn.className = "answer-btn";
    btn.textContent = answer;
    btn.setAttribute("aria-label", "Answer: " + answer);
    btn.addEventListener("click", function () { handleAnswer(answer); });
    els.answersContainer.appendChild(btn);
  });
}

function renderTrueFalse(q) {
  renderMultipleChoice(q);
}

function renderFillBlank(q) {
  els.answersContainer.innerHTML = "";
  els.fillBlankInput.value = "";
  setHidden(els.fillBlankInput, false);
  setHidden(els.fillBlankSubmit, false);
  els.fillBlankInput.focus();
}

function renderMatching(q) {
  els.answersContainer.innerHTML = "";
  setHidden(els.matchingArea, false);
  setHidden(els.matchingSubmit, false);
  els.matchingArea.innerHTML = "";

  var shuffledRight = shuffle(q.pairs.map(function (p) { return p.right; }));

  q.pairs.forEach(function (pair, idx) {
    var row = document.createElement("div");
    row.className = "matching-pair";

    var leftSpan = document.createElement("span");
    leftSpan.className = "matching-term";
    leftSpan.textContent = pair.left;

    var select = document.createElement("select");
    select.className = "matching-select";
    select.dataset.correct = pair.right;

    var defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "Select...";
    select.appendChild(defaultOpt);

    shuffledRight.forEach(function (option) {
      var opt = document.createElement("option");
      opt.value = option;
      opt.textContent = option;
      select.appendChild(opt);
    });

    row.appendChild(leftSpan);
    row.appendChild(select);
    els.matchingArea.appendChild(row);
  });
}

function renderSentenceComplete(q) {
  els.answersContainer.innerHTML = "";
  setHidden(els.sentenceCompleteArea, false);
  setHidden(els.sentenceSubmit, false);

  var html = q.sentence_template;
  q.blanks.forEach(function (blank) {
    var opts = blank.options.map(function (opt) {
      return '<option value="' + opt + '">' + opt + '</option>';
    }).join("");
    var selectHtml = ' <select class="sentence-blank-select" data-position="' + blank.position + '" data-correct="' + blank.correct + '"><option value="">...</option>' + opts + '</select> ';
    html = html.replace("___", selectHtml);
  });

  els.sentenceCompleteArea.innerHTML = html;
}

// ── Phase: handleAnswer (multiple choice / truefalse) ──────────────────────
function handleAnswer(selected) {
  if (gameState.status === "FEEDBACK_DISPLAY") return;
  gameState.status = "ANSWER_CHECK";
  var q = gameState.currentQuestion;
  var isCorrect = selected === q.correct_answer;

  document.querySelectorAll(".answer-btn").forEach(function (btn) {
    btn.disabled = true;
    if (btn.textContent === q.correct_answer) {
      btn.classList.add("correct");
    } else if (btn.textContent === selected && !isCorrect) {
      btn.classList.add("incorrect");
    }
  });

  processAnswer(isCorrect, q);
}

function handleFillBlankSubmit() {
  if (gameState.status === "FEEDBACK_DISPLAY") return;
  gameState.status = "ANSWER_CHECK";
  var q = gameState.currentQuestion;
  var input = els.fillBlankInput;
  var userAnswer = input.value.trim().toLowerCase();
  var acceptable = q.acceptable_answers.map(function (a) { return a.toLowerCase(); });
  var isCorrect = acceptable.indexOf(userAnswer) !== -1;

  input.classList.add(isCorrect ? "input-correct" : "input-incorrect");
  if (isCorrect) {
    input.value = input.value.trim();
  } else {
    input.value = userAnswer + "  →  " + q.correct_answer;
  }
  input.disabled = true;
  els.fillBlankSubmit.disabled = true;

  processAnswer(isCorrect, q);
}

function handleMatchingSubmit() {
  if (gameState.status === "FEEDBACK_DISPLAY") return;
  gameState.status = "ANSWER_CHECK";
  var q = gameState.currentQuestion;
  var selects = els.matchingArea.querySelectorAll(".matching-select");
  var allCorrect = true;

  selects.forEach(function (sel) {
    sel.disabled = true;
    if (sel.value === sel.dataset.correct) {
      sel.classList.add("select-correct");
    } else {
      sel.classList.add("select-incorrect");
      allCorrect = false;
    }
  });
  els.matchingSubmit.disabled = true;

  processAnswer(allCorrect, q);
}

function handleSentenceCompleteSubmit() {
  if (gameState.status === "FEEDBACK_DISPLAY") return;
  gameState.status = "ANSWER_CHECK";
  var q = gameState.currentQuestion;
  var selects = els.sentenceCompleteArea.querySelectorAll(".sentence-blank-select");
  var allCorrect = true;

  selects.forEach(function (sel) {
    sel.disabled = true;
    if (sel.value === sel.dataset.correct) {
      sel.classList.add("select-correct");
    } else {
      sel.classList.add("select-incorrect");
      allCorrect = false;
      sel.value = sel.value + " → " + sel.dataset.correct;
    }
  });
  els.sentenceSubmit.disabled = true;

  processAnswer(allCorrect, q);
}

function processAnswer(isCorrect, q) {
  if (gameState.shieldedThisQuestion && !isCorrect) {
    gameState.shieldedThisQuestion = false;
    sm2UpdateItem(q.id, 2);
    handleCorrectAnswer(q);
    showFeedback(true, q.explanation + " (Shield protected your streak)");
  } else {
    if (isCorrect) {
      handleCorrectAnswer(q);
      sm2UpdateItem(q.id, 5);
    } else {
      handleWrongAnswer(q);
      sm2UpdateItem(q.id, 1);
    }
    showFeedback(isCorrect, q.explanation);
  }

  gameState.status = "FEEDBACK_DISPLAY";
  setHidden(els.nextBtn, false);
  setHidden(els.hintBtn, true);
  els.fillBlankSubmit.disabled = true;
}

function sm2UpdateItem(questionId, grade) {
  var items = sm2LoadItems();
  var item = items[questionId];
  if (!item) {
    item = sm2CreateItem(questionId);
  }
  sm2Update(item, grade);
  items[questionId] = item;
  sm2SaveItems(items);
}

function handleCorrectAnswer(q) {
  var mode = GAME_MODES[gameState.gameMode];
  var basePoints = gameState.difficulty ? DIFFICULTIES[gameState.difficulty].points : 10;

  gameState.streak++;
  if (gameState.streak > gameState.maxStreak) {
    gameState.maxStreak = gameState.streak;
  }

  var bonus = 0;
  if (gameState.streak >= 10) bonus = 20;
  else if (gameState.streak >= 5) bonus = 10;
  else if (gameState.streak >= 3) bonus = 5;

  var pts = gameState.isReviewQuestion ? Math.floor(basePoints * 0.5) + bonus : basePoints + bonus;
  gameState.score += pts;
  gameState.correctCount++;

  gameState.wildcardEarnCount++;
  if (gameState.wildcardEarnCount >= QUIZ_SETTINGS.wildcardEarnThreshold) {
    gameState.wildcardEarnCount = 0;
    gameState.wildcards.fiftyFifty++;
    gameState.wildcards.addTime++;
    gameState.wildcards.shield++;
    updateWildcardDisplay();
  }

  if (gameState.isReviewQuestion) {
    var queueEntry = gameState.wrongQueue.find(function (e) { return e.question.id === q.id; });
    if (queueEntry && queueEntry.remainingAttempts > 0) {
      queueEntry.remainingAttempts--;
      if (queueEntry.remainingAttempts > 0) gameState.wrongQueue.push(queueEntry);
    }
  }
}

function handleWrongAnswer(q) {
  gameState.streak = 0;
  gameState.wildcardEarnCount = 0;

  if (!gameState.shieldedThisQuestion) {
    gameState.lives--;
    updateLivesDisplay();
  }

  if (gameState.isReviewQuestion) {
    var queueEntry = gameState.wrongQueue.find(function (e) { return e.question.id === q.id; });
    if (queueEntry) {
      queueEntry.remainingAttempts = QUIZ_SETTINGS.wrongAnswerRepeatMin;
      gameState.wrongQueue.push(queueEntry);
    }
  } else {
    var alreadyQueued = gameState.wrongQueue.some(function (e) { return e.question.id === q.id; });
    if (!alreadyQueued) {
      gameState.wrongQueue.push({
        question: q,
        remainingAttempts: QUIZ_SETTINGS.wrongAnswerRepeatMin
      });
    }
    if (!gameState.wrongAnswers.find(function (w) { return w.id === q.id; })) {
      gameState.wrongAnswers.push({
        id: q.id,
        question: q.question,
        correct_answer: q.correct_answer
      });
    }
  }

  if (gameState.lives <= 0) {
    clearTimer();
    showResult();
  }
}

function showFeedback(isCorrect, explanation) {
  var feedbackArea = els.feedbackArea;
  feedbackArea.classList.remove("correct", "incorrect");
  feedbackArea.classList.add(isCorrect ? "correct" : "incorrect");

  els.feedbackResult.textContent = isCorrect
    ? "✓ Correct!" + (gameState.streak >= 3 ? " 🔥 " + gameState.streak + " in a row!" : "")
    : "✗ Incorrect";

  els.feedbackExplain.textContent = explanation;
  setHidden(feedbackArea, false);

  updateHUD();
}

// ── Phase: nextQuestion ────────────────────────────────────────────────────
function nextQuestion() {
  gameState.status = "NEXT_QUESTION_CHECK";

  if (gameState.lives <= 0) {
    clearTimer();
    showResult();
    return;
  }

  if (gameState.mainDeck.length > 0) {
    var q = gameState.mainDeck.shift();
    renderQuestion(q, false);
  } else if (gameState.wrongQueue.length > 0) {
    var entry = gameState.wrongQueue.shift();
    renderQuestion(entry.question, true);
  } else {
    clearTimer();
    gameState.status = "SESSION_END";
    showResult();
  }
}

// ── Timer ──────────────────────────────────────────────────────────────────
function startTimer() {
  var mode = GAME_MODES[gameState.gameMode];
  if (mode.key === "classic") return;

  if (mode.key === "timed") {
    gameState.remainingTime = mode.totalTime;
  } else if (mode.key === "speed") {
    gameState.remainingTime = mode.timePerQuestion;
  }

  updateTimerDisplay();
  gameState.timerInterval = setInterval(tickTimer, 1000);
}

function tickTimer() {
  gameState.remainingTime--;
  updateTimerDisplay();

  if (gameState.remainingTime <= 10 && gameState.remainingTime > 0) {
    els.timerDisplay.classList.add("urgent");
  } else {
    els.timerDisplay.classList.remove("urgent");
  }

  if (gameState.remainingTime <= 0) {
    clearTimer();
    if (gameState.gameMode === "timed") {
      showResult();
    } else if (gameState.gameMode === "speed") {
      processAnswer(false, gameState.currentQuestion);
    }
  }
}

function updateTimerDisplay() {
  var secs = Math.max(0, gameState.remainingTime);
  var min = Math.floor(secs / 60);
  var sec = secs % 60;
  els.timerDisplay.textContent = "⏱ " + min + ":" + (sec < 10 ? "0" : "") + sec;
}

// ── Wildcards ──────────────────────────────────────────────────────────────
document.addEventListener("click", function (e) {
  var btn = e.target.closest(".wildcard-btn");
  if (!btn) return;
  useWildcard(btn.dataset.type);
});

function useWildcard(type) {
  if (gameState.wildcards[type] <= 0) return;
  if (gameState.status !== "QUESTION_DISPLAY" && type !== "addTime") return;
  if (type === "addTime" && gameState.gameMode === "classic") return;

  gameState.wildcards[type]--;

  switch (type) {
    case "fiftyFifty":
      applyFiftyFifty();
      break;
    case "addTime":
      gameState.remainingTime += 15;
      updateTimerDisplay();
      break;
    case "shield":
      gameState.shieldedThisQuestion = true;
      break;
  }
  updateWildcardDisplay();
}

function applyFiftyFifty() {
  var buttons = els.answersContainer.querySelectorAll(".answer-btn");
  if (buttons.length < 3) return;
  var correctAnswer = gameState.currentQuestion.correct_answer;
  var wrongButtons = [];
  buttons.forEach(function (b) {
    if (b.textContent !== correctAnswer) wrongButtons.push(b);
  });

  var toHide = shuffle(wrongButtons).slice(0, Math.max(2, wrongButtons.length - 1));
  toHide.forEach(function (b) {
    b.classList.add("hidden");
    b.disabled = true;
  });
}

function updateWildcardDisplay() {
  var wcBtns = els.wildcardBar.querySelectorAll(".wildcard-btn");
  var keys = ["fiftyFifty", "addTime", "shield"];
  keys.forEach(function (key, i) {
    if (wcBtns[i]) {
      var countSpan = wcBtns[i].querySelector(".wc-count");
      if (countSpan) countSpan.textContent = gameState.wildcards[key];
      wcBtns[i].disabled = gameState.wildcards[key] <= 0;
    }
  });
}

function updateLivesDisplay() {
  var hearts = "";
  for (var i = 0; i < gameState.lives; i++) {
    hearts += "❤️";
  }
  hearts += '<span class="lost-lives">' + "🖤".repeat(Math.max(0, 5 - gameState.lives)) + '</span>';
  els.livesDisplay.innerHTML = hearts;
}

// ── Keyboard ───────────────────────────────────────────────────────────────
function handleKeyboard(e) {
  if (gameState.status !== "QUESTION_DISPLAY") return;
  if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") return;

  var key = e.key.toLowerCase();

  if (key === "1" || key === "a") clickAnswer(0);
  else if (key === "2" || key === "b") clickAnswer(1);
  else if (key === "3" || key === "c") clickAnswer(2);
  else if (key === "4" || key === "d") clickAnswer(3);
  else if (key === "h") { e.preventDefault(); showHint(); }
  else if (key === "w") { e.preventDefault(); document.querySelector(".wildcard-btn:not([disabled])")?.click(); }
  else if (key === " ") { e.preventDefault(); if (!els.nextBtn.classList.contains("hidden")) nextQuestion(); }
  else if (key === "enter") {
    if (!els.nextBtn.classList.contains("hidden")) nextQuestion();
  }
}

function clickAnswer(idx) {
  var btns = els.answersContainer.querySelectorAll(".answer-btn:not(.hidden)");
  if (btns.length > idx && !btns[idx].disabled) btns[idx].click();
}

// ── Phase: showResult ──────────────────────────────────────────────────────
function showResult() {
  clearTimer();
  saveHighScore();
  sm2SaveItems(sm2LoadItems());

  var attempted = gameState.correctCount + gameState.wrongAnswers.length;
  var total = Math.max(attempted, gameState.totalQuestions);
  var accuracy = total > 0 ? Math.round(gameState.correctCount / total * 100) : 0;

  var grade = getGrade(accuracy);

  els.resultGrade.textContent = grade;
  els.resultGrade.className = "result-grade grade-" + grade.toLowerCase();

  var gradeLabels = { A: "Outstanding!", B: "Good Job!", C: "Keep Practicing!", D: "Try Again!" };
  els.resultScore.textContent = gameState.score + " points · " + (gradeLabels[grade] || "");

  if (gameState.lives <= 0) {
    els.resultAccuracy.textContent = "Game Over! Lives: 0 | Accuracy: " + gameState.correctCount + " / " + total + " (" + accuracy + "%)";
  } else {
    els.resultAccuracy.textContent = "Accuracy: " + gameState.correctCount + " / " + total + " (" + accuracy + "%)";
  }

  els.resultStreak.textContent = "Best streak: " + gameState.maxStreak + " in a row";

  if (gameState.wrongAnswers.length > 0) {
    els.wrongList.innerHTML = "";
    gameState.wrongAnswers.forEach(function (w) {
      var li = document.createElement("li");
      li.className = "wrong-answer-item";
      li.innerHTML = "<strong>" + w.question + "</strong><span>Correct answer: " + w.correct_answer + "</span>";
      els.wrongList.appendChild(li);
    });
    setHidden(els.wrongSection, false);
  } else {
    setHidden(els.wrongSection, true);
  }

  gameState.status = "RESULT_DISPLAY";
  showScreen("result");
}

function getGrade(accuracy) {
  if (accuracy >= 90) return "A";
  if (accuracy >= 75) return "B";
  if (accuracy >= 60) return "C";
  return "D";
}

// ── Hint ───────────────────────────────────────────────────────────────────
function showHint() {
  var q = gameState.currentQuestion;
  if (!q) return;
  if (q.hint) {
    els.hintText.textContent = "Hint: " + q.hint;
  } else {
    els.hintText.textContent = "No hint available for this question.";
  }
  setHidden(els.hintText, false);
  els.hintBtn.disabled = true;
}

// ── HUD Update ─────────────────────────────────────────────────────────────
function updateHUD() {
  var total = gameState.totalQuestions;
  var num = Math.min(gameState.questionNumber, total);
  els.questionCounter.textContent = "Question " + num + " / " + total;
  els.scoreDisplay.textContent = "Score: " + gameState.score;

  if (gameState.streak >= 3) {
    els.streakDisplay.textContent = "🔥 ×" + gameState.streak;
    setHidden(els.streakDisplay, false);
  } else {
    setHidden(els.streakDisplay, true);
  }
}

// ── localStorage: High Scores ──────────────────────────────────────────────
function saveHighScore() {
  var attempted = gameState.correctCount + gameState.wrongAnswers.length;
  var total = Math.max(attempted, gameState.totalQuestions);
  var accuracy = total > 0 ? Math.round(gameState.correctCount / total * 100) : 0;

  var entry = {
    score:      gameState.score,
    grade:      getGrade(accuracy),
    category:   CATEGORIES[gameState.category] ? CATEGORIES[gameState.category].label : (gameState.category || "Review"),
    difficulty: DIFFICULTIES[gameState.difficulty] ? DIFFICULTIES[gameState.difficulty].label : (gameState.difficulty || "N/A"),
    mode:       GAME_MODES[gameState.gameMode] ? GAME_MODES[gameState.gameMode].label : "Classic",
    date:       new Date().toLocaleDateString(),
    lives:      gameState.lives
  };

  var scores = [];
  try {
    scores = JSON.parse(localStorage.getItem("englishQuizHighScores")) || [];
  } catch (e) {
    scores = [];
  }

  scores.push(entry);
  scores.sort(function (a, b) { return b.score - a.score; });
  scores = scores.slice(0, QUIZ_SETTINGS.maxStoredHighScores);
  localStorage.setItem("englishQuizHighScores", JSON.stringify(scores));
}

function loadHighScores() {
  var scores = [];
  try {
    scores = JSON.parse(localStorage.getItem("englishQuizHighScores")) || [];
  } catch (e) {
    scores = [];
  }

  if (scores.length === 0) {
    els.scoresBody.innerHTML = '<tr><td colspan="6" class="no-scores">No scores yet. Play a game!</td></tr>';
    return;
  }

  els.scoresBody.innerHTML = scores.map(function (s, i) {
    return '<tr>' +
      '<td>' + (i + 1) + '</td>' +
      '<td>' + s.score + '</td>' +
      '<td>' + s.grade + '</td>' +
      '<td>' + s.category + '</td>' +
      '<td>' + s.difficulty + '</td>' +
      '<td>' + s.date + '</td>' +
    '</tr>';
  }).join("");
}

// ── Bootstrap ──────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", initGame);