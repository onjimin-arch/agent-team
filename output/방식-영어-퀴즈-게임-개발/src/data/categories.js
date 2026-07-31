/**
 * categories.js — 카테고리, 난이도, 게임 설정 상수
 * 전역 변수 방식 (file:// CORS 문제 없음)
 */

const CATEGORIES = {
  vocabulary: {
    key: "vocabulary",
    label: "Vocabulary",
    icon: "📚",
    description: "Word meanings & usage"
  },
  grammar: {
    key: "grammar",
    label: "Grammar",
    icon: "✏️",
    description: "Grammar rules & sentence structure"
  },
  prepositions: {
    key: "prepositions",
    label: "Prepositions",
    icon: "🔤",
    description: "at, in, on, by, with and more"
  },
  phrasal_verbs: {
    key: "phrasal_verbs",
    label: "Phrasal Verbs",
    icon: "➡️",
    description: "look up, give up, run into and more"
  },
  idioms: {
    key: "idioms",
    label: "Idioms",
    icon: "💬",
    description: "Common English expressions"
  }
};

const DIFFICULTIES = {
  easy: {
    key: "easy",
    label: "Easy",
    points: 10,
    description: "Basic level"
  },
  medium: {
    key: "medium",
    label: "Medium",
    points: 20,
    description: "Intermediate level"
  },
  hard: {
    key: "hard",
    label: "Hard",
    points: 30,
    description: "Advanced level"
  }
};

const QUESTION_TYPES = {
  multiple:        { key: "multiple",        label: "Multiple Choice", answerCount: 4 },
  truefalse:       { key: "truefalse",       label: "True / False",    answerCount: 2 },
  fill_blank:      { key: "fill_blank",      label: "Fill in the Blank", answerCount: 0 },
  matching:        { key: "matching",        label: "Matching",        answerCount: 0 },
  sentence_complete: { key: "sentence_complete", label: "Sentence Complete", answerCount: 0 }
};

const GAME_MODES = {
  classic: { key: "classic", label: "Classic",   questions: 10, timePerQuestion: 0,  totalTime: 0,   description: "No time limit, 10 questions" },
  timed:   { key: "timed",   label: "Timed",     questions: 10, timePerQuestion: 0,  totalTime: 180, description: "10 questions in 3 minutes" },
  speed:   { key: "speed",   label: "Speed Run", questions: 15, timePerQuestion: 12, totalTime: 0,   description: "15 questions, 12 seconds each" }
};

const WILDCARD_SETTINGS = {
  fiftyFifty: { key: "fiftyFifty", label: "50:50",   icon: "🎯", startingCount: 1, description: "Remove 2 wrong answers" },
  addTime:    { key: "addTime",    label: "+Time",    icon: "⏱️", startingCount: 1, description: "Add 15 seconds" },
  shield:     { key: "shield",     label: "Shield",   icon: "🛡️", startingCount: 1, description: "Protect your streak" }
};

const QUIZ_SETTINGS = {
  questionsPerSession: 10,
  wrongAnswerRepeatMin: 2,
  maxStoredHighScores: 5,
  wildcardEarnThreshold: 5,
  sm2ReviewIntervalCheckMinutes: 1440
};