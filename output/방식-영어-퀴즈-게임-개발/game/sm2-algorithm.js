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

const SM2_KEY = "englishQuizSM2Items";
const DAY_MS = 86400000;

/** @param {string} questionId */
function sm2CreateItem(questionId) {
  return {
    id: questionId,
    ef: 2.5,
    n: 0,
    i: 0,
    nextReview: Date.now()
  };
}

/** grade: 0-5 (0=complete blackout, 5=perfect recall) */
function sm2Update(item, grade) {
  const q = Math.max(0, Math.min(5, grade));

  if (q < 3) {
    item.n = 0;
    item.i = 1;
  } else {
    item.ef = item.ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
    if (item.ef < 1.3) item.ef = 1.3;

    if (item.n === 0) {
      item.i = 1;
    } else if (item.n === 1) {
      item.i = 6;
    } else {
      item.i = Math.round(item.i * item.ef);
    }
    item.n++;
  }

  item.nextReview = Date.now() + item.i * DAY_MS;
  return item;
}

function sm2LoadItems() {
  try {
    const raw = localStorage.getItem(SM2_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function sm2SaveItems(items) {
  try {
    localStorage.setItem(SM2_KEY, JSON.stringify(items));
  } catch (e) {
    // storage full or private mode — silently ignore
  }
}

function sm2IsDue(item) {
  return item.nextReview <= Date.now();
}

function sm2GetDueItems() {
  const items = sm2LoadItems();
  const now = Date.now();
  return Object.values(items).filter(item => item.nextReview <= now);
}

function sm2FormatNextReview(item) {
  const diff = item.nextReview - Date.now();
  if (diff <= 0) return "Now";
  const hours = Math.floor(diff / 3600000);
  if (hours < 24) return `In ${hours}h`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "Tomorrow";
  return `In ${days} days`;
}