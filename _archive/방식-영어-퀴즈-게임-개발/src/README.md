# English Quiz Game

A static web app for practicing English vocabulary, grammar, prepositions, phrasal verbs, and idioms.  
No server required. Works offline via `file://` or GitHub Pages.

---

## How to Run

### Option 1 — Local (file://)
1. Open the `game/` folder in your file explorer.
2. Double-click `index.html` to open it in your default browser.
3. No internet connection needed.

### Option 2 — GitHub Pages
1. Push this repository to GitHub.
2. Go to **Settings → Pages → Source** and select the branch + `/game` folder.
3. Access the game at `https://<username>.github.io/<repo-name>/`.

---

## File Structure

```
game/
├── index.html          Main page (3 sections: start / quiz / result)
├── style.css           Dark theme stylesheet
├── game.js             Core game logic (state machine, scoring)
└── data/
    ├── categories.js   CATEGORIES, DIFFICULTIES, QUIZ_SETTINGS constants
    └── questions.js    QUESTIONS array (60 questions)
```

---

## Gameplay

1. Select a **category** (Vocabulary, Grammar, Prepositions, Phrasal Verbs, Idioms).
2. Select a **difficulty** (Easy = 10 pts, Medium = 20 pts, Hard = 30 pts).
3. Answer 10 questions per session.
4. Wrong answers are automatically re-queued after the main deck finishes.
5. Correct answers earn points; consecutive correct answers build a streak bonus.
6. Final results show your grade (A/B/C/D), accuracy, and wrong questions to review.

---

## How to Add Questions

Open `data/questions.js` and add an object to the `QUESTIONS` array:

```javascript
{
  id: "vocab_013",          // unique ID: category prefix + 3-digit number
  category: "vocabulary",   // must match a CATEGORIES key
  difficulty: "medium",     // "easy" | "medium" | "hard"
  type: "multiple",         // "multiple" (4 choices) | "truefalse" (2 choices)
  question: "What does 'tenacious' mean?",
  correct_answer: "Holding firmly to something",
  incorrect_answers: ["Very flexible", "Easily distracted", "Overly generous"],
  explanation: "'Tenacious' means tending to keep a firm hold of something.",
  hint: "Think about persistence"
}
```

- For `truefalse` type: provide exactly one string in `incorrect_answers` (`"True"` or `"False"`).
- The `explanation` field is required (cannot be empty).
- The `hint` field is optional.
