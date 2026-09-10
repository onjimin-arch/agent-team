/**
 * questions.js — 영어 퀴즈 문제 데이터셋 (총 120문제)
 * 카테고리: vocabulary(24), grammar(24), prepositions(24), phrasal_verbs(24), idioms(24)
 * 각 카테고리당 multiple 12문제 + truefalse 2문제 + fill_blank/matching/sentence_complete 10문제
 */

const QUESTIONS = [

  // =============================================
  // VOCABULARY (24문제: 기존 12 + 신규 12)
  // =============================================

  {
    id: "vocab_001",
    category: "vocabulary",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'happy' mean?",
    correct_answer: "Feeling joy or pleasure",
    incorrect_answers: ["Feeling sad", "Feeling angry", "Feeling tired"],
    explanation: "'Happy' describes a state of feeling joy, pleasure, or contentment.",
    hint: "Think about a smile on your face"
  },
  {
    id: "vocab_002",
    category: "vocabulary",
    difficulty: "easy",
    type: "multiple",
    question: "Which word means the opposite of 'big'?",
    correct_answer: "Small",
    incorrect_answers: ["Tall", "Heavy", "Loud"],
    explanation: "'Small' is the antonym of 'big'. Both describe size, but in opposite directions.",
    hint: "Think about something tiny"
  },
  {
    id: "vocab_003",
    category: "vocabulary",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'ancient' mean?",
    correct_answer: "Very old",
    incorrect_answers: ["Very new", "Very fast", "Very large"],
    explanation: "'Ancient' means belonging to the very distant past, typically thousands of years ago.",
    hint: "Think about dinosaurs or pyramids"
  },
  {
    id: "vocab_004",
    category: "vocabulary",
    difficulty: "easy",
    type: "truefalse",
    question: "'Brave' means showing courage and not being afraid.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'Brave' correctly means showing courage, willingness to face danger or difficulty.",
    hint: "Think about a hero"
  },
  {
    id: "vocab_005",
    category: "vocabulary",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'ubiquitous' mean?",
    correct_answer: "Found everywhere",
    incorrect_answers: ["Very rare", "Extremely large", "Highly dangerous"],
    explanation: "'Ubiquitous' means present, appearing, or found everywhere.",
    hint: "Think about 'everywhere'"
  },
  {
    id: "vocab_006",
    category: "vocabulary",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'eloquent' mean?",
    correct_answer: "Expressing oneself fluently and persuasively",
    incorrect_answers: ["Speaking very quietly", "Being rude in speech", "Talking too much"],
    explanation: "'Eloquent' describes someone who speaks or writes in a fluent, persuasive, and expressive way.",
    hint: "Think of a great public speaker"
  },
  {
    id: "vocab_007",
    category: "vocabulary",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'ambiguous' mean?",
    correct_answer: "Having more than one possible meaning",
    incorrect_answers: ["Perfectly clear", "Absolutely certain", "Very complicated"],
    explanation: "'Ambiguous' means open to more than one interpretation; not having one obvious meaning.",
    hint: "The word contains 'ambi-' meaning both"
  },
  {
    id: "vocab_008",
    category: "vocabulary",
    difficulty: "medium",
    type: "truefalse",
    question: "'Benevolent' means wanting to do good and being kind to others.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'Benevolent' means well-meaning and kindly; characterized by goodwill.",
    hint: "Think of 'bene-' as meaning good"
  },
  {
    id: "vocab_009",
    category: "vocabulary",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'ephemeral' mean?",
    correct_answer: "Lasting for a very short time",
    incorrect_answers: ["Lasting forever", "Happening repeatedly", "Growing very slowly"],
    explanation: "'Ephemeral' means lasting for only a short time; transitory.",
    hint: "Think of mayflies that live only one day"
  },
  {
    id: "vocab_010",
    category: "vocabulary",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'perfidious' mean?",
    correct_answer: "Deceitful and untrustworthy",
    incorrect_answers: ["Extremely honest", "Overly cautious", "Surprisingly generous"],
    explanation: "'Perfidious' means guilty of betrayal or treachery; deceitful.",
    hint: "It's related to 'perfidy' which means betrayal"
  },
  {
    id: "vocab_011",
    category: "vocabulary",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'sanguine' mean?",
    correct_answer: "Optimistic, especially in difficult situations",
    incorrect_answers: ["Extremely pessimistic", "Deeply suspicious", "Unusually aggressive"],
    explanation: "'Sanguine' means optimistic or positive, especially in a difficult situation.",
    hint: "It comes from Latin 'sanguis' meaning blood (ruddy complexion = health)"
  },
  {
    id: "vocab_012",
    category: "vocabulary",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'laconic' mean?",
    correct_answer: "Using very few words",
    incorrect_answers: ["Speaking at great length", "Being overly emotional", "Writing very neatly"],
    explanation: "'Laconic' means using very few words to express a lot; brief and concise.",
    hint: "The Spartans (from Laconia) were famous for short, direct speech"
  },

  // --- VOCABULARY 신규 12문제 (multiple 2 + fill_blank 3 + matching 3 + sentence_complete 4) ---

  {
    id: "vocab_013",
    category: "vocabulary",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'enormous' mean?",
    correct_answer: "Extremely large in size",
    incorrect_answers: ["Very small in size", "Moderately sized", "Invisible to the eye"],
    explanation: "'Enormous' means very large in size, quantity, or extent.",
    hint: "Think about something massive like a whale"
  },
  {
    id: "vocab_014",
    category: "vocabulary",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'meticulous' mean?",
    correct_answer: "Showing great attention to detail",
    incorrect_answers: ["Being very messy", "Acting carelessly", "Working extremely fast"],
    explanation: "'Meticulous' describes someone who pays careful attention to every detail.",
    hint: "Think about a perfectionist"
  },
  {
    id: "vocab_015",
    category: "vocabulary",
    difficulty: "easy",
    type: "fill_blank",
    question: "The word '___' means to move quickly.",
    correct_answer: "hurry",
    acceptable_answers: ["hurry", "rush", "dash"],
    explanation: "Multiple synonyms accepted: hurry, rush, dash all mean to move quickly.",
    hint: "It starts with 'h'"
  },
  {
    id: "vocab_016",
    category: "vocabulary",
    difficulty: "medium",
    type: "fill_blank",
    question: "A person who is '___' doesn't like to spend money.",
    correct_answer: "stingy",
    acceptable_answers: ["stingy", "cheap", "miserly"],
    explanation: "'Stingy' means unwilling to spend money. 'Cheap' and 'miserly' are synonyms.",
    hint: "It starts with 's' — opposite of generous"
  },
  {
    id: "vocab_017",
    category: "vocabulary",
    difficulty: "hard",
    type: "fill_blank",
    question: "The word '___' means to make someone feel less angry or hostile.",
    correct_answer: "placate",
    acceptable_answers: ["placate", "appease", "pacify"],
    explanation: "'Placate' means to calm someone down by doing what they want.",
    hint: "It starts with 'p' and sounds like 'calm'"
  },
  {
    id: "vocab_018",
    category: "vocabulary",
    difficulty: "easy",
    type: "matching",
    pairs: [
      { "left": "Beautiful", "right": "Pleasing to the eye or mind" },
      { "left": "Intelligent", "right": "Having a high mental capacity" },
      { "left": "Courageous", "right": "Not deterred by danger or pain" },
      { "left": "Generous", "right": "Willing to give more than expected" }
    ],
    question: "Match each word to its definition.",
    explanation: "These are common adjectives describing positive personal qualities.",
    hint: "Each matches one definition"
  },
  {
    id: "vocab_019",
    category: "vocabulary",
    difficulty: "medium",
    type: "matching",
    pairs: [
      { "left": "Obsolete", "right": "No longer used or produced" },
      { "left": "Innovative", "right": "Introducing new ideas or methods" },
      { "left": "Pragmatic", "right": "Dealing with things practically" },
      { "left": "Abstract", "right": "Existing as an idea, not physical" }
    ],
    question: "Match each word to its correct definition.",
    explanation: "These words describe different approaches to ideas and problem-solving.",
    hint: "Think about how each word applies to thinking"
  },
  {
    id: "vocab_020",
    category: "vocabulary",
    difficulty: "hard",
    type: "matching",
    pairs: [
      { "left": "Ostentatious", "right": "Designed to impress or attract notice" },
      { "left": "Pernicious", "right": "Having a harmful effect in a gradual way" },
      { "left": "Magnanimous", "right": "Very generous or forgiving" },
      { "left": "Recalcitrant", "right": "Stubbornly uncooperative" }
    ],
    question: "Match each advanced word to its definition.",
    explanation: "These are SAT/TOEFL-level words that describe behavior and effects.",
    hint: "Each word has a distinct Latin root"
  },
  {
    id: "vocab_021",
    category: "vocabulary",
    difficulty: "easy",
    type: "sentence_complete",
    sentence_template: "She is very ___. She always helps others before thinking of herself.",
    blanks: [
      { "position": 1, "correct": "kind", "options": ["kind", "angry", "lazy", "shy"] }
    ],
    question: "Choose the word that best completes the sentence.",
    explanation: "'Kind' describes someone who is generous, helpful, and caring toward others.",
    hint: "Think about a generous personality trait"
  },
  {
    id: "vocab_022",
    category: "vocabulary",
    difficulty: "medium",
    type: "sentence_complete",
    sentence_template: "The scientist made a ___ discovery that changed the entire field of medicine.",
    blanks: [
      { "position": 1, "correct": "groundbreaking", "options": ["groundbreaking", "ordinary", "minor", "confusing"] }
    ],
    question: "Select the most appropriate word.",
    explanation: "'Groundbreaking' means innovative and pioneering — something that completely changes a field.",
    hint: "Think about something revolutionary and new"
  },
  {
    id: "vocab_023",
    category: "vocabulary",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "The politician's speech was deliberately ___, so no one could accuse him of taking sides.",
    blanks: [
      { "position": 1, "correct": "ambiguous", "options": ["ambiguous", "clear", "offensive", "informative"] }
    ],
    question: "Choose the word that fits the context of avoiding commitment.",
    explanation: "'Ambiguous' means having more than one possible meaning — perfect for politicians who don't want to commit.",
    hint: "The politician wants to be unclear"
  },
  {
    id: "vocab_024",
    category: "vocabulary",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "The ___ nature of the stock market means you can never perfectly predict it.",
    blanks: [
      { "position": 1, "correct": "volatile", "options": ["volatile", "stable", "predictable", "profitable"] }
    ],
    question: "Pick the word that best describes an unpredictable and rapidly changing thing.",
    explanation: "'Volatile' means liable to change rapidly and unpredictably, often used for markets.",
    hint: "Think about something unstable or explosive"
  },

  // =============================================
  // GRAMMAR (24문제: 기존 12 + 신규 12)
  // =============================================

  {
    id: "gram_001",
    category: "grammar",
    difficulty: "easy",
    type: "multiple",
    question: "Which sentence is grammatically correct?",
    correct_answer: "She doesn't like coffee.",
    incorrect_answers: ["She don't like coffee.", "She not like coffee.", "She isn't like coffee."],
    explanation: "With 'she' (third person singular), use 'doesn't' (does + not) for negative sentences.",
    hint: "Third person singular needs 'does' not 'do'"
  },
  {
    id: "gram_002",
    category: "grammar",
    difficulty: "easy",
    type: "multiple",
    question: "What is the plural of 'child'?",
    correct_answer: "Children",
    incorrect_answers: ["Childs", "Childes", "Child's"],
    explanation: "'Children' is the irregular plural form of 'child'. It doesn't follow the standard -s rule.",
    hint: "This is an irregular plural"
  },
  {
    id: "gram_003",
    category: "grammar",
    difficulty: "easy",
    type: "multiple",
    question: "Which word is a noun?",
    correct_answer: "Freedom",
    incorrect_answers: ["Quickly", "Beautiful", "Run"],
    explanation: "'Freedom' is a noun (abstract noun). 'Quickly' is an adverb, 'Beautiful' is an adjective, 'Run' is a verb.",
    hint: "A noun is a person, place, thing, or idea"
  },
  {
    id: "gram_004",
    category: "grammar",
    difficulty: "easy",
    type: "truefalse",
    question: "The sentence 'I goed to school yesterday.' is grammatically correct.",
    correct_answer: "False",
    incorrect_answers: ["True"],
    explanation: "'Goed' is incorrect. 'Go' is an irregular verb; its past tense is 'went'. The correct sentence is 'I went to school yesterday.'",
    hint: "'Go' is an irregular verb"
  },
  {
    id: "gram_005",
    category: "grammar",
    difficulty: "medium",
    type: "multiple",
    question: "Which sentence uses the present perfect correctly?",
    correct_answer: "I have lived here for ten years.",
    incorrect_answers: ["I have lived here since ten years.", "I lived here for ten years already.", "I am living here since ten years."],
    explanation: "Use 'for' with a duration (ten years) and 'since' with a starting point (2014). Present perfect 'have lived' shows the action continues to the present.",
    hint: "Use 'for' with a period of time"
  },
  {
    id: "gram_006",
    category: "grammar",
    difficulty: "medium",
    type: "multiple",
    question: "Choose the correct comparative form: 'This book is _____ than that one.'",
    correct_answer: "more interesting",
    incorrect_answers: ["interestinger", "most interesting", "more interestinger"],
    explanation: "For adjectives with 3 or more syllables, use 'more + adjective' for the comparative form. 'Interesting' has 4 syllables, so we say 'more interesting'.",
    hint: "Long adjectives use 'more' for comparisons"
  },
  {
    id: "gram_007",
    category: "grammar",
    difficulty: "medium",
    type: "multiple",
    question: "Which sentence is in the passive voice?",
    correct_answer: "The cake was baked by Sarah.",
    incorrect_answers: ["Sarah baked the cake.", "Sarah is baking the cake.", "Sarah will bake the cake."],
    explanation: "Passive voice: the subject receives the action. 'The cake was baked by Sarah' — 'the cake' is the subject but receives the action of baking.",
    hint: "In passive voice, the object becomes the subject"
  },
  {
    id: "gram_008",
    category: "grammar",
    difficulty: "medium",
    type: "truefalse",
    question: "In English, adjectives usually come before the noun they describe.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "In English, attributive adjectives precede the noun (e.g., 'a red car', 'a tall building'). This is different from some Romance languages where adjectives often follow the noun.",
    hint: "Think of 'a beautiful house' vs 'a house beautiful'"
  },
  {
    id: "gram_009",
    category: "grammar",
    difficulty: "hard",
    type: "multiple",
    question: "Which sentence contains a dangling modifier?",
    correct_answer: "Walking down the street, the trees were beautiful.",
    incorrect_answers: [
      "Walking down the street, she noticed the beautiful trees.",
      "The trees looked beautiful as she walked down the street.",
      "She found the trees beautiful while walking down the street."
    ],
    explanation: "A dangling modifier occurs when the modifier's implied subject doesn't match the sentence's actual subject. 'Walking down the street' implies a person walking, but the subject is 'the trees' — trees can't walk.",
    hint: "Who or what is doing the walking?"
  },
  {
    id: "gram_010",
    category: "grammar",
    difficulty: "hard",
    type: "multiple",
    question: "Which sentence uses the subjunctive mood correctly?",
    correct_answer: "I suggest that he be present at the meeting.",
    incorrect_answers: [
      "I suggest that he is present at the meeting.",
      "I suggest that he was present at the meeting.",
      "I suggest that he being present at the meeting."
    ],
    explanation: "The subjunctive mood uses the base form of the verb. After verbs like 'suggest', 'recommend', 'insist', use 'that + subject + base verb' (not 'is').",
    hint: "Subjunctive uses the base form of the verb"
  },
  {
    id: "gram_011",
    category: "grammar",
    difficulty: "hard",
    type: "multiple",
    question: "Identify the correct use of 'whom': '_____ did you speak with?'",
    correct_answer: "Whom",
    incorrect_answers: ["Who", "Whose", "Which"],
    explanation: "'Whom' is used as the object of a verb or preposition. Here it is the object of the preposition 'with'. Test: if the answer would be 'him/her', use 'whom'; if 'he/she', use 'who'.",
    hint: "If you can answer 'him', use 'whom'"
  },
  {
    id: "gram_012",
    category: "grammar",
    difficulty: "hard",
    type: "multiple",
    question: "What type of clause is underlined in: 'The man [who called you] is my uncle.'?",
    correct_answer: "Relative clause",
    incorrect_answers: ["Adverbial clause", "Noun clause", "Conditional clause"],
    explanation: "A relative clause modifies a noun and is introduced by relative pronouns (who, which, that, whose, whom). Here, 'who called you' modifies 'the man'.",
    hint: "It starts with 'who' and modifies a noun"
  },

  // --- GRAMMAR 신규 12문제 (multiple 2 + fill_blank 3 + matching 4 + sentence_complete 3) ---

  {
    id: "gram_013",
    category: "grammar",
    difficulty: "easy",
    type: "multiple",
    question: "Which is the correct past tense of 'eat'?",
    correct_answer: "Ate",
    incorrect_answers: ["Eated", "Eating", "Eats"],
    explanation: "'Eat' is an irregular verb. Its past tense form is 'ate'.",
    hint: "Irregular verb — not 'eated'"
  },
  {
    id: "gram_014",
    category: "grammar",
    difficulty: "medium",
    type: "multiple",
    question: "Which sentence correctly uses the past perfect tense?",
    correct_answer: "She had already left when I arrived.",
    incorrect_answers: ["She already left when I had arrived.", "She has already left when I arrived.", "She was already left when I arrived."],
    explanation: "Past perfect (had + past participle) shows an action completed before another past action.",
    hint: "Two past actions — which came first?"
  },
  {
    id: "gram_015",
    category: "grammar",
    difficulty: "easy",
    type: "fill_blank",
    question: "She ___ to the store every Saturday. (go)",
    correct_answer: "goes",
    acceptable_answers: ["goes"],
    explanation: "For the third person singular (she/he/it) in the present simple, add '-es' to 'go' → 'goes'.",
    hint: "Third person singular needs -es"
  },
  {
    id: "gram_016",
    category: "grammar",
    difficulty: "medium",
    type: "fill_blank",
    question: "If I ___ rich, I would travel around the world. (be)",
    correct_answer: "were",
    acceptable_answers: ["were"],
    explanation: "In the second conditional (unreal present), we use 'were' for all persons — the subjunctive form.",
    hint: "This is a hypothetical situation"
  },
  {
    id: "gram_017",
    category: "grammar",
    difficulty: "hard",
    type: "fill_blank",
    question: "By the time you arrive, I ___ for three hours. (work)",
    correct_answer: "will have been working",
    acceptable_answers: ["will have been working"],
    explanation: "Future perfect continuous: 'will have been + verb-ing' — describes an ongoing action that will be completed by a specific future time.",
    hint: "Future perfect continuous tense"
  },
  {
    id: "gram_018",
    category: "grammar",
    difficulty: "easy",
    type: "matching",
    pairs: [
      { "left": "Noun", "right": "A person, place, thing, or idea" },
      { "left": "Verb", "right": "An action or state of being" },
      { "left": "Adjective", "right": "Describes a noun or pronoun" },
      { "left": "Adverb", "right": "Describes a verb, adjective, or another adverb" }
    ],
    question: "Match each part of speech to its definition.",
    explanation: "The 4 main parts of speech: Nouns name things, Verbs show action, Adjectives describe nouns, Adverbs describe verbs/adjectives.",
    hint: "Each matches one definition"
  },
  {
    id: "gram_019",
    category: "grammar",
    difficulty: "medium",
    type: "matching",
    pairs: [
      { "left": "Simple Past", "right": "I walked to school." },
      { "left": "Present Perfect", "right": "I have walked to school many times." },
      { "left": "Past Perfect", "right": "I had walked to school before it rained." },
      { "left": "Future Simple", "right": "I will walk to school tomorrow." }
    ],
    question: "Match each tense to its example sentence.",
    explanation: "Each tense indicates when the action happens relative to the present moment.",
    hint: "Look at the helping verbs for clues"
  },
  {
    id: "gram_020",
    category: "grammar",
    difficulty: "hard",
    type: "matching",
    pairs: [
      { "left": "Conditional Type 1", "right": "If it rains, I will stay home. (real possibility)" },
      { "left": "Conditional Type 2", "right": "If I were you, I would study more. (unreal present)" },
      { "left": "Conditional Type 3", "right": "If I had studied, I would have passed. (unreal past)" },
      { "left": "Zero Conditional", "right": "If you heat water, it boils. (general truth)" }
    ],
    question: "Match each conditional type to its example and use case.",
    explanation: "English has 4 main conditional types, each expressing a different relationship between condition and result.",
    hint: "Look at the tense patterns in the if-clause and main clause"
  },
  {
    id: "gram_021",
    category: "grammar",
    difficulty: "medium",
    type: "matching",
    pairs: [
      { "left": "Countable nouns", "right": "Use 'many' and 'few': many books, few ideas" },
      { "left": "Uncountable nouns", "right": "Use 'much' and 'little': much water, little time" },
      { "left": "Both", "right": "Use 'a lot of' or 'some': a lot of books/water" },
      { "left": "Neither", "right": "Use 'any' in negative sentences: not any books/water" }
    ],
    question: "Match each noun type to the correct quantifier rule.",
    explanation: "Countable and uncountable nouns take different quantifiers in English.",
    hint: "Can you count it? That determines the quantifier"
  },
  {
    id: "gram_022",
    category: "grammar",
    difficulty: "medium",
    type: "sentence_complete",
    sentence_template: "Neither the teacher ___ the students were ready for the surprise quiz.",
    blanks: [
      { "position": 1, "correct": "nor", "options": ["nor", "or", "and", "but"] }
    ],
    question: "Select the correct paired conjunction.",
    explanation: "'Neither...nor' is a correlative conjunction pair. It connects two negative alternatives.",
    hint: "This pairs with 'neither'"
  },
  {
    id: "gram_023",
    category: "grammar",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "Not only did she finish the project early, ___ she also helped her teammates.",
    blanks: [
      { "position": 1, "correct": "but", "options": ["but", "and", "or", "so"] }
    ],
    question: "Choose the correct word to complete the correlative conjunction.",
    explanation: "'Not only...but also' is a correlative conjunction pair. After 'not only' at the start, we invert the subject and auxiliary verb.",
    hint: "This completes the 'not only...' structure"
  },
  {
    id: "gram_024",
    category: "grammar",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "___ he studied very hard, he failed the exam.",
    blanks: [
      { "position": 1, "correct": "Although", "options": ["Although", "Because", "Since", "Unless"] }
    ],
    question: "Choose the correct subordinating conjunction that shows contrast.",
    explanation: "'Although' introduces a concession — a contrast between two ideas. Despite studying hard, the result was unexpected.",
    hint: "This word shows a surprising contrast"
  },

  // =============================================
  // PREPOSITIONS (24문제: 기존 12 + 신규 12)
  // =============================================

  {
    id: "prep_001",
    category: "prepositions",
    difficulty: "easy",
    type: "multiple",
    question: "Fill in the blank: 'The cat is sitting ___ the chair.'",
    correct_answer: "on",
    incorrect_answers: ["in", "at", "by"],
    explanation: "Use 'on' for surfaces. The cat is on the surface of the chair.",
    hint: "Think about a surface"
  },
  {
    id: "prep_002",
    category: "prepositions",
    difficulty: "easy",
    type: "multiple",
    question: "Fill in the blank: 'I will meet you ___ noon.'",
    correct_answer: "at",
    incorrect_answers: ["in", "on", "by"],
    explanation: "Use 'at' for specific times of day (at noon, at midnight, at 3 o'clock).",
    hint: "Use this for specific times"
  },
  {
    id: "prep_003",
    category: "prepositions",
    difficulty: "easy",
    type: "multiple",
    question: "Fill in the blank: 'She was born ___ January.'",
    correct_answer: "in",
    incorrect_answers: ["on", "at", "during"],
    explanation: "Use 'in' for months, years, seasons, and longer time periods.",
    hint: "Use this for months and years"
  },
  {
    id: "prep_004",
    category: "prepositions",
    difficulty: "easy",
    type: "truefalse",
    question: "The sentence 'He arrived at Monday' is correct.",
    correct_answer: "False",
    incorrect_answers: ["True"],
    explanation: "For days of the week, use 'on': 'He arrived on Monday.' Use 'at' for times, 'in' for months/years, 'on' for days and dates.",
    hint: "Which preposition goes with days of the week?"
  },
  {
    id: "prep_005",
    category: "prepositions",
    difficulty: "medium",
    type: "multiple",
    question: "Choose the correct preposition: 'She graduated ___ Harvard University.'",
    correct_answer: "from",
    incorrect_answers: ["at", "in", "of"],
    explanation: "'Graduate from' is the correct collocation. You graduate FROM a school or university.",
    hint: "Think about leaving or completing something"
  },
  {
    id: "prep_006",
    category: "prepositions",
    difficulty: "medium",
    type: "multiple",
    question: "Fill in the blank: 'I'm looking forward ___ seeing you.'",
    correct_answer: "to",
    incorrect_answers: ["for", "at", "about"],
    explanation: "'Look forward to' is a fixed phrase. After 'to' in this expression, use a gerund (verb+ing).",
    hint: "'Look forward ___' is a common phrase"
  },
  {
    id: "prep_007",
    category: "prepositions",
    difficulty: "medium",
    type: "multiple",
    question: "Which preposition is correct? 'She is good ___ playing the piano.'",
    correct_answer: "at",
    incorrect_answers: ["in", "for", "with"],
    explanation: "'Good at' is the correct collocation when describing a skill or ability.",
    hint: "Think about skills and abilities"
  },
  {
    id: "prep_008",
    category: "prepositions",
    difficulty: "medium",
    type: "truefalse",
    question: "'By' can be used to indicate the method or means by which something is done.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'By' can express means or method: 'by car', 'by email', 'by hand'. It shows how something is done.",
    hint: "Think of 'by train' or 'by phone'"
  },
  {
    id: "prep_009",
    category: "prepositions",
    difficulty: "hard",
    type: "multiple",
    question: "Choose the correct preposition: 'The book is ___ the shelf, between the dictionary and the novel.'",
    correct_answer: "on",
    incorrect_answers: ["in", "at", "above"],
    explanation: "Books are placed 'on' shelves (on a surface). 'In' would suggest the book is inside the shelf.",
    hint: "Books rest on a surface"
  },
  {
    id: "prep_010",
    category: "prepositions",
    difficulty: "hard",
    type: "multiple",
    question: "Which sentence uses a preposition correctly in an advanced context?",
    correct_answer: "The decision is contingent upon the board's approval.",
    incorrect_answers: [
      "The decision is contingent on to the board's approval.",
      "The decision is contingent from the board's approval.",
      "The decision is contingent by the board's approval."
    ],
    explanation: "'Contingent upon' (or 'contingent on') means depending on. 'Upon' is a more formal version of 'on'.",
    hint: "Contingent means 'depending on'"
  },
  {
    id: "prep_011",
    category: "prepositions",
    difficulty: "hard",
    type: "multiple",
    question: "Fill in the blank: 'She was accused ___ stealing the documents.'",
    correct_answer: "of",
    incorrect_answers: ["for", "with", "about"],
    explanation: "'Accused of' is the correct collocation. 'Accuse someone of something' is standard usage.",
    hint: "This verb always takes this preposition"
  },
  {
    id: "prep_012",
    category: "prepositions",
    difficulty: "hard",
    type: "multiple",
    question: "Which is correct? 'He insisted ___ paying for dinner.'",
    correct_answer: "on",
    incorrect_answers: ["in", "for", "about"],
    explanation: "'Insist on' is the correct collocation. You insist on something or insist on doing something.",
    hint: "'Insist on' is a fixed expression"
  },

  // --- PREPOSITIONS 신규 12문제 (multiple 2 + fill_blank 4 + matching 3 + sentence_complete 3) ---

  {
    id: "prep_013",
    category: "prepositions",
    difficulty: "easy",
    type: "multiple",
    question: "Fill in the blank: 'I go to work ___ bus.'",
    correct_answer: "by",
    incorrect_answers: ["with", "on", "in"],
    explanation: "Use 'by' for modes of transportation: by bus, by car, by train, by plane.",
    hint: "Think about transportation"
  },
  {
    id: "prep_014",
    category: "prepositions",
    difficulty: "medium",
    type: "multiple",
    question: "Choose the correct preposition: 'I'm not familiar ___ this neighborhood.'",
    correct_answer: "with",
    incorrect_answers: ["about", "of", "in"],
    explanation: "'Familiar with' is the correct collocation. You are familiar WITH something or someone.",
    hint: "Think about knowledge or recognition"
  },
  {
    id: "prep_015",
    category: "prepositions",
    difficulty: "easy",
    type: "fill_blank",
    question: "The book is ___ the table. (on / under / beside — surface)",
    correct_answer: "on",
    acceptable_answers: ["on"],
    explanation: "'On' is used when something is in contact with or supported by a surface.",
    hint: "The book is resting on top of the table"
  },
  {
    id: "prep_016",
    category: "prepositions",
    difficulty: "medium",
    type: "fill_blank",
    question: "I have been waiting ___ you ___ 3 o'clock.",
    correct_answer: "for since",
    acceptable_answers: ["for since"],
    explanation: "Use 'wait for' (someone) and 'since' with a specific starting point in time.",
    hint: "Two prepositions needed — one for the person, one for the time"
  },
  {
    id: "prep_017",
    category: "prepositions",
    difficulty: "hard",
    type: "fill_blank",
    question: "She is very good ___ math but struggles ___ languages.",
    correct_answer: "at with",
    acceptable_answers: ["at with"],
    explanation: "'Good at' describes skills. 'Struggle with' describes difficulty dealing with something.",
    hint: "Two different prepositions — for skill and for difficulty"
  },
  {
    id: "prep_018",
    category: "prepositions",
    difficulty: "hard",
    type: "fill_blank",
    question: "We discussed the issue ___ length before coming ___ a solution.",
    correct_answer: "at to",
    acceptable_answers: ["at to"],
    explanation: "'At length' means in great detail. 'Come to a solution' means to reach or arrive at a solution.",
    hint: "Two different prepositions — one for discussion, one for reaching"
  },
  {
    id: "prep_019",
    category: "prepositions",
    difficulty: "easy",
    type: "matching",
    pairs: [
      { "left": "in", "right": "Used for enclosed spaces and large time periods (months, years)" },
      { "left": "on", "right": "Used for surfaces and specific days/dates" },
      { "left": "at", "right": "Used for specific points and exact times" },
      { "left": "by", "right": "Used for proximity, deadline, and means of transport" }
    ],
    question: "Match each preposition to its general usage rule.",
    explanation: "These are the 4 most common prepositions of time and place.",
    hint: "Think about the spatial and temporal meanings"
  },
  {
    id: "prep_020",
    category: "prepositions",
    difficulty: "medium",
    type: "matching",
    pairs: [
      { "left": "depend on", "right": "The success will ___ your effort." },
      { "left": "believe in", "right": "I ___ the power of education." },
      { "left": "consist of", "right": "The team ___ five members." },
      { "left": "apply for", "right": "She wants to ___ a job at Google." }
    ],
    question: "Match each verb to the correct preposition to form a phrasal-collocation.",
    explanation: "Some verbs always pair with specific prepositions. These are called dependent prepositions.",
    hint: "Each verb takes only one of these prepositions"
  },
  {
    id: "prep_021",
    category: "prepositions",
    difficulty: "hard",
    type: "matching",
    pairs: [
      { "left": "in accordance with", "right": "Following rules or instructions" },
      { "left": "in spite of", "right": "Despite an obstacle or difficulty" },
      { "left": "with regard to", "right": "Concerning or about a topic" },
      { "left": "on behalf of", "right": "Representing or acting for someone else" }
    ],
    question: "Match each prepositional phrase to its meaning.",
    explanation: "These are formal multi-word prepositions often used in academic and business English.",
    hint: "These are compound prepositions used in formal writing"
  },
  {
    id: "prep_022",
    category: "prepositions",
    difficulty: "medium",
    type: "sentence_complete",
    sentence_template: "He was ___ the impression that the meeting was ___ Friday.",
    blanks: [
      { "position": 1, "correct": "under", "options": ["under", "in", "with", "at"] },
      { "position": 2, "correct": "on", "options": ["on", "in", "at", "by"] }
    ],
    question: "Choose the correct prepositions to complete the sentence.",
    explanation: "'Under the impression' is a fixed expression meaning to believe something. 'On' is used for days of the week.",
    hint: "One is a fixed expression, the other is a time preposition"
  },
  {
    id: "prep_023",
    category: "prepositions",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "___ the circumstances, I think we should proceed ___ caution.",
    blanks: [
      { "position": 1, "correct": "Under", "options": ["Under", "In", "With", "By"] },
      { "position": 2, "correct": "with", "options": ["with", "by", "in", "under"] }
    ],
    question: "Select the correct prepositions for this formal expression.",
    explanation: "'Under the circumstances' means given the current situation. 'Proceed with caution' means to continue carefully.",
    hint: "Both are fixed expressions — one for assessment, one for action"
  },
  {
    id: "prep_024",
    category: "prepositions",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "His knowledge ___ the subject is remarkable ___ someone his age.",
    blanks: [
      { "position": 1, "correct": "of", "options": ["of", "about", "in", "with"] },
      { "position": 2, "correct": "for", "options": ["for", "to", "with", "by"] }
    ],
    question: "Choose the correct prepositions to complete the sentence.",
    explanation: "'Knowledge of' is the correct collocation. 'For' is used to indicate comparison or relation to a standard.",
    hint: "'Knowledge ___ something' — the standard preposition"
  },

  // =============================================
  // PHRASAL VERBS (24문제: 기존 12 + 신규 12)
  // =============================================

  {
    id: "phrv_001",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'give up' mean?",
    correct_answer: "To stop trying; to quit",
    incorrect_answers: ["To start something new", "To give a gift", "To improve gradually"],
    explanation: "'Give up' means to stop trying to do something or to abandon an effort.",
    hint: "Think about quitting"
  },
  {
    id: "phrv_002",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'wake up' mean?",
    correct_answer: "To stop sleeping and become conscious",
    incorrect_answers: ["To fall asleep", "To stand up", "To turn off the alarm"],
    explanation: "'Wake up' means to stop sleeping; to become alert after being asleep.",
    hint: "Think of your morning routine"
  },
  {
    id: "phrv_003",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'turn off' mean?",
    correct_answer: "To stop a device from working",
    incorrect_answers: ["To start a device", "To make something louder", "To turn something around"],
    explanation: "'Turn off' means to cause a device or machine to stop working by operating a switch or button.",
    hint: "Think about a light switch"
  },
  {
    id: "phrv_004",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "truefalse",
    question: "'Look up' can mean to search for information in a reference source.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'Look up' has multiple meanings, including to search for information in a dictionary, database, or other reference. 'Look up the word in the dictionary.'",
    hint: "Think about finding information"
  },
  {
    id: "phrv_005",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'run into' mean in this sentence: 'I ran into an old friend at the market.'?",
    correct_answer: "To meet someone unexpectedly",
    incorrect_answers: ["To crash into someone", "To chase someone", "To avoid someone deliberately"],
    explanation: "'Run into' means to encounter or meet someone by chance, without planning to.",
    hint: "Think about accidental meetings"
  },
  {
    id: "phrv_006",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'put off' mean in: 'She put off her dentist appointment again.'?",
    correct_answer: "To delay or postpone",
    incorrect_answers: ["To cancel permanently", "To arrive early for", "To enjoy very much"],
    explanation: "'Put off' means to postpone or delay something to a later time.",
    hint: "Think about doing something later instead of now"
  },
  {
    id: "phrv_007",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'bring up' mean in: 'She brought up an interesting point during the meeting.'?",
    correct_answer: "To mention or introduce a topic",
    incorrect_answers: ["To raise a child", "To vomit", "To lift something heavy"],
    explanation: "'Bring up' can mean to mention or introduce a subject in a conversation. It also means to raise a child, but in this context it means to introduce a topic.",
    hint: "Think about introducing a topic in conversation"
  },
  {
    id: "phrv_008",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "truefalse",
    question: "'Break down' can mean both a vehicle stopping working AND someone losing emotional control.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'Break down' is a polysemous phrasal verb: (1) a car/machine stopping working, and (2) a person crying or losing emotional control. Context determines the meaning.",
    hint: "Phrasal verbs often have multiple meanings"
  },
  {
    id: "phrv_009",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'account for' mean in: 'How do you account for the missing funds?'",
    correct_answer: "To explain or justify something",
    incorrect_answers: ["To count money carefully", "To take responsibility for actions", "To add up totals in accounting"],
    explanation: "'Account for' means to explain or give a satisfactory reason for something. It's asking for an explanation of why the funds are missing.",
    hint: "You need to give an explanation"
  },
  {
    id: "phrv_010",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'bear out' mean in: 'The evidence bears out the theory.'?",
    correct_answer: "To confirm or support something",
    incorrect_answers: ["To contradict or disprove", "To carry something outside", "To endure a difficult situation"],
    explanation: "'Bear out' means to confirm, support, or uphold something. The evidence confirms the theory.",
    hint: "Think of support or confirmation"
  },
  {
    id: "phrv_011",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'come across' mean in: 'She comes across as very confident in interviews.'?",
    correct_answer: "To seem or appear to others in a particular way",
    incorrect_answers: ["To find something by chance", "To travel across a place", "To agree with someone suddenly"],
    explanation: "'Come across' has two main meanings: (1) to find by chance, and (2) to seem or give an impression. In this sentence, it means to appear confident to others.",
    hint: "Think about the impression someone gives"
  },
  {
    id: "phrv_012",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'fend off' mean?",
    correct_answer: "To defend against or repel something",
    incorrect_answers: ["To search for something carefully", "To send someone away politely", "To achieve something with difficulty"],
    explanation: "'Fend off' means to defend oneself against an attack, or to push away something unwanted.",
    hint: "Think about defending or repelling"
  },

  // --- PHRASAL VERBS 신규 12문제 (multiple 2 + fill_blank 3 + matching 3 + sentence_complete 4) ---

  {
    id: "phrv_013",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'pick up' mean in: 'Can you pick up the kids from school?'",
    correct_answer: "To collect someone from a place",
    incorrect_answers: ["To lift something with your hands", "To learn something quickly", "To choose one thing among many"],
    explanation: "'Pick up' has multiple meanings. Here it means to collect or fetch someone from a location.",
    hint: "Think about collecting someone"
  },
  {
    id: "phrv_014",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'carry out' mean in: 'They carried out the experiment successfully.'",
    correct_answer: "To perform or complete a task",
    incorrect_answers: ["To remove something from a place", "To physically carry something outside", "To cancel a plan"],
    explanation: "'Carry out' means to perform, execute, or complete a task, plan, or experiment.",
    hint: "Think about executing a plan or experiment"
  },
  {
    id: "phrv_015",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "fill_blank",
    question: "Please ___ out this form before your appointment. (fill / find / figure)",
    correct_answer: "fill",
    acceptable_answers: ["fill"],
    explanation: "'Fill out' means to complete a form by writing the required information.",
    hint: "What do you do with a form?"
  },
  {
    id: "phrv_016",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "fill_blank",
    question: "I need to ___ up a new hobby to relieve stress. (take / give / get)",
    correct_answer: "take",
    acceptable_answers: ["take", "pick"],
    explanation: "'Take up' means to start a new hobby or activity. 'Pick up' is also acceptable in casual use.",
    hint: "You start doing something new"
  },
  {
    id: "phrv_017",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "fill_blank",
    question: "The company had to ___ down on unauthorized expenses to stay profitable. (crack / cut / break)",
    correct_answer: "crack",
    acceptable_answers: ["crack"],
    explanation: "'Crack down on' means to take severe measures to enforce rules or stop something. It implies strict action.",
    hint: "This implies severe enforcement or strict action"
  },
  {
    id: "phrv_018",
    category: "phrasal_verbs",
    difficulty: "easy",
    type: "matching",
    pairs: [
      { "left": "get up", "right": "To rise from bed in the morning" },
      { "left": "sit down", "right": "To take a seated position" },
      { "left": "stand up", "right": "To rise to a standing position" },
      { "left": "lie down", "right": "To place oneself in a horizontal position" }
    ],
    question: "Match each phrasal verb of movement to its meaning.",
    explanation: "These are common phrasal verbs describing body position changes.",
    hint: "Each describes a different body position"
  },
  {
    id: "phrv_019",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "matching",
    pairs: [
      { "left": "turn down", "right": "To reject or refuse an offer" },
      { "left": "work out", "right": "To exercise or solve a problem" },
      { "left": "point out", "right": "To draw attention to something" },
      { "left": "set up", "right": "To arrange or establish something" }
    ],
    question: "Match each phrasal verb to its correct meaning.",
    explanation: "These separable phrasal verbs are very common in business and daily conversation.",
    hint: "Each has a very specific everyday meaning"
  },
  {
    id: "phrv_020",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "matching",
    pairs: [
      { "left": "fall through", "right": "To fail to happen (a plan or deal)" },
      { "left": "iron out", "right": "To resolve small problems or difficulties" },
      { "left": "drum up", "right": "To generate interest or support" },
      { "left": "boil down to", "right": "To be the essential or main point" }
    ],
    question: "Match each advanced phrasal verb to its meaning.",
    explanation: "These are more sophisticated phrasal verbs often used in professional contexts.",
    hint: "Each has a figurative meaning different from the literal words"
  },
  {
    id: "phrv_021",
    category: "phrasal_verbs",
    difficulty: "medium",
    type: "sentence_complete",
    sentence_template: "I couldn't ___ out what she was trying to say because her accent was too strong.",
    blanks: [
      { "position": 1, "correct": "make", "options": ["make", "figure", "find", "work"] }
    ],
    question: "Choose the correct verb to complete the phrasal verb meaning 'understand'.",
    explanation: "'Make out' means to be able to see, hear, or understand something with difficulty.",
    hint: "This phrasal verb means to perceive or understand with difficulty"
  },
  {
    id: "phrv_022",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "After the scandal, he tried to ___ over a new leaf and become a better person.",
    blanks: [
      { "position": 1, "correct": "turn", "options": ["turn", "make", "get", "start"] }
    ],
    question: "Select the verb that completes this idiom meaning 'to make a fresh start'.",
    explanation: "'Turn over a new leaf' is an idiom meaning to change one's behavior and make a fresh start.",
    hint: "This is a famous idiom about starting fresh"
  },
  {
    id: "phrv_023",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "Don't ___ out on this opportunity — it might never come again.",
    blanks: [
      { "position": 1, "correct": "miss", "options": ["miss", "give", "back", "check"] }
    ],
    question: "Choose the verb that means 'to fail to take advantage of'.",
    explanation: "'Miss out on' means to fail to experience or take advantage of an opportunity.",
    hint: "This phrasal verb is about losing an opportunity"
  },
  {
    id: "phrv_024",
    category: "phrasal_verbs",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "He always ___ out against injustice, even when it's unpopular to do so.",
    blanks: [
      { "position": 1, "correct": "speaks", "options": ["speaks", "stands", "comes", "calls"] }
    ],
    question: "Pick the correct verb meaning 'to publicly oppose or protest'.",
    explanation: "'Speak out against' means to publicly express opposition to something, especially injustice.",
    hint: "This phrasal verb means to publicly oppose something"
  },

  // =============================================
  // IDIOMS (24문제: 기존 12 + 신규 12)
  // =============================================

  {
    id: "idio_001",
    category: "idioms",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'break a leg' mean?",
    correct_answer: "Good luck",
    incorrect_answers: ["Be careful", "Work hard", "Stop immediately"],
    explanation: "'Break a leg' is a theatrical idiom wishing someone good luck, especially before a performance.",
    hint: "Performers say this to each other"
  },
  {
    id: "idio_002",
    category: "idioms",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'it's raining cats and dogs' mean?",
    correct_answer: "It's raining very heavily",
    incorrect_answers: ["Animals are falling from the sky", "The weather is unpredictable", "It will rain soon"],
    explanation: "'Raining cats and dogs' is an idiom meaning it's raining very hard. The origin is uncertain, but it's a very common expression.",
    hint: "Think about the weather"
  },
  {
    id: "idio_003",
    category: "idioms",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'hit the sack' mean?",
    correct_answer: "To go to bed and sleep",
    incorrect_answers: ["To punch something", "To start working hard", "To go shopping"],
    explanation: "'Hit the sack' is an informal idiom meaning to go to bed. 'Sack' is slang for a bed or sleeping bag.",
    hint: "Think about sleeping"
  },
  {
    id: "idio_004",
    category: "idioms",
    difficulty: "easy",
    type: "truefalse",
    question: "'Bite the bullet' means to endure a painful or difficult situation.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'Bite the bullet' means to endure a painful or difficult situation stoically. The phrase originated from the practice of having soldiers bite on a bullet during surgery before anesthesia.",
    hint: "Think about enduring something unpleasant"
  },
  {
    id: "idio_005",
    category: "idioms",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'the ball is in your court' mean?",
    correct_answer: "It's your turn to take action or make a decision",
    incorrect_answers: ["You are the best player", "The problem has been solved", "You must play a sport"],
    explanation: "'The ball is in your court' means it is now your responsibility to take the next step or make a decision. It comes from tennis.",
    hint: "Think about whose responsibility something is"
  },
  {
    id: "idio_006",
    category: "idioms",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'spill the beans' mean?",
    correct_answer: "To reveal secret information",
    incorrect_answers: ["To make a mess", "To cook a meal", "To waste resources"],
    explanation: "'Spill the beans' means to accidentally or intentionally reveal a secret or surprise.",
    hint: "Think about revealing a secret"
  },
  {
    id: "idio_007",
    category: "idioms",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'cost an arm and a leg' mean?",
    correct_answer: "To be very expensive",
    incorrect_answers: ["To cause physical injury", "To be a medical procedure", "To require great effort"],
    explanation: "'Cost an arm and a leg' means something is extremely expensive. It emphasizes high cost humorously.",
    hint: "Think about price"
  },
  {
    id: "idio_008",
    category: "idioms",
    difficulty: "medium",
    type: "truefalse",
    question: "'Under the weather' is an idiom meaning to feel ill or unwell.",
    correct_answer: "True",
    incorrect_answers: ["False"],
    explanation: "'Under the weather' means to feel slightly ill or not quite well. It's commonly used for minor sickness.",
    hint: "Think about not feeling well"
  },
  {
    id: "idio_009",
    category: "idioms",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'burn bridges' mean?",
    correct_answer: "To permanently damage a relationship or eliminate future options",
    incorrect_answers: ["To destroy infrastructure", "To work very hard until exhausted", "To make a dramatic entrance"],
    explanation: "'Burn bridges' (or 'burn one's bridges') means to take an action that permanently damages or destroys a relationship or future possibility.",
    hint: "Think about destroying a path back"
  },
  {
    id: "idio_010",
    category: "idioms",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'blow hot and cold' mean?",
    correct_answer: "To keep changing one's opinions or feelings about something",
    incorrect_answers: ["To have extreme mood swings requiring medical attention", "To describe variable weather conditions", "To breathe irregularly when exercising"],
    explanation: "'Blow hot and cold' means to be inconsistent, alternating between enthusiasm and lack of interest.",
    hint: "Think about being inconsistent"
  },
  {
    id: "idio_011",
    category: "idioms",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'cut to the chase' mean?",
    correct_answer: "To get to the most important point without wasting time",
    incorrect_answers: ["To follow someone quickly", "To edit a film sequence", "To avoid a difficult topic"],
    explanation: "'Cut to the chase' means to get to the point directly, omitting unnecessary details. It originates from silent film editing where editors would 'cut' from boring scenes to the exciting chase.",
    hint: "Think about being direct and efficient"
  },
  {
    id: "idio_012",
    category: "idioms",
    difficulty: "hard",
    type: "multiple",
    question: "What does 'the devil is in the details' mean?",
    correct_answer: "Small details can cause significant problems if overlooked",
    incorrect_answers: [
      "Evil forces hide in complicated situations",
      "It's better to avoid complex plans",
      "Details are unimportant in the big picture"
    ],
    explanation: "'The devil is in the details' means that something may seem simple, but it is the details that make it difficult or cause unexpected problems.",
    hint: "Think about paying attention to small things"
  },

  // --- IDIOMS 신규 12문제 (multiple 2 + fill_blank 4 + matching 3 + sentence_complete 3) ---

  {
    id: "idio_013",
    category: "idioms",
    difficulty: "easy",
    type: "multiple",
    question: "What does 'once in a blue moon' mean?",
    correct_answer: "Something that happens very rarely",
    incorrect_answers: ["Something that happens every night", "A type of astronomical event", "Something that happens daily"],
    explanation: "'Once in a blue moon' means very rarely. A blue moon (2nd full moon in a month) is uncommon, hence the idiom.",
    hint: "Think about frequency — how often does this happen?"
  },
  {
    id: "idio_014",
    category: "idioms",
    difficulty: "medium",
    type: "multiple",
    question: "What does 'barking up the wrong tree' mean?",
    correct_answer: "To pursue the wrong course of action or wrongly accuse someone",
    incorrect_answers: ["To be afraid of dogs", "To be lost in a forest", "To choose the wrong option deliberately"],
    explanation: "'Barking up the wrong tree' means looking in the wrong place, accusing the wrong person, or pursuing a mistaken line of thought.",
    hint: "Think about making a mistake in judgment"
  },
  {
    id: "idio_015",
    category: "idioms",
    difficulty: "easy",
    type: "fill_blank",
    question: "When there is a problem, you shouldn't cry over spilled ___. Just fix it!",
    correct_answer: "milk",
    acceptable_answers: ["milk"],
    explanation: "'Don't cry over spilled milk' means don't waste time worrying about things that have already happened and cannot be changed.",
    hint: "Think about a common white beverage"
  },
  {
    id: "idio_016",
    category: "idioms",
    difficulty: "medium",
    type: "fill_blank",
    question: "This is our last ___ — if this doesn't work, we have to give up entirely.",
    correct_answer: "resort",
    acceptable_answers: ["resort"],
    explanation: "'Last resort' means the final course of action when all else has failed.",
    hint: "Think about the final option when nothing else works"
  },
  {
    id: "idio_017",
    category: "idioms",
    difficulty: "hard",
    type: "fill_blank",
    question: "Let's face the ___ — this project is going to fail without more funding.",
    correct_answer: "music",
    acceptable_answers: ["music"],
    explanation: "'Face the music' means to accept the unpleasant consequences of one's actions.",
    hint: "Think about confronting a difficult reality"
  },
  {
    id: "idio_018",
    category: "idioms",
    difficulty: "hard",
    type: "fill_blank",
    question: "The teacher read them the ___ act after catching them cheating on the exam.",
    correct_answer: "riot",
    acceptable_answers: ["riot"],
    explanation: "'Read someone the riot act' means to severely reprimand someone or give someone a stern warning.",
    hint: "This idiom means to give a severe scolding or warning"
  },
  {
    id: "idio_019",
    category: "idioms",
    difficulty: "easy",
    type: "matching",
    pairs: [
      { "left": "Piece of cake", "right": "Something very easy to do" },
      { "left": "See eye to eye", "right": "To agree completely with someone" },
      { "left": "Let the cat out of the bag", "right": "To reveal a secret accidentally" },
      { "left": "Kill two birds with one stone", "right": "To accomplish two things at once" }
    ],
    question: "Match each common idiom to its meaning.",
    explanation: "These are everyday English idioms that native speakers use frequently.",
    hint: "Each idiom has a figurative meaning"
  },
  {
    id: "idio_020",
    category: "idioms",
    difficulty: "medium",
    type: "matching",
    pairs: [
      { "left": "A blessing in disguise", "right": "Something that seems bad but turns out good" },
      { "left": "Beat around the bush", "right": "To avoid saying what you mean directly" },
      { "left": "Jump on the bandwagon", "right": "To follow a popular trend" },
      { "left": "Pull someone's leg", "right": "To tease or joke with someone" }
    ],
    question: "Match each idiom to its correct meaning.",
    explanation: "These idioms are frequently used in both casual conversation and professional settings.",
    hint: "Don't take the words literally"
  },
  {
    id: "idio_021",
    category: "idioms",
    difficulty: "hard",
    type: "matching",
    pairs: [
      { "left": "Bury the hatchet", "right": "To make peace and end a conflict" },
      { "left": "Steal someone's thunder", "right": "To take credit or attention from someone" },
      { "left": "Swan song", "right": "A final performance or act before retirement" },
      { "left": "Achilles' heel", "right": "A weakness despite overall strength" }
    ],
    question: "Match each advanced idiom to its meaning.",
    explanation: "These idioms come from literature, mythology, and history. They're used in educated English.",
    hint: "Each has a historical or mythological origin"
  },
  {
    id: "idio_022",
    category: "idioms",
    difficulty: "medium",
    type: "sentence_complete",
    sentence_template: "You need to go the extra ___ if you want to get a promotion.",
    blanks: [
      { "position": 1, "correct": "mile", "options": ["mile", "step", "hour", "effort"] }
    ],
    question: "Choose the word that completes this idiom meaning 'to make more effort than expected'.",
    explanation: "'Go the extra mile' means to do more than what is required or expected.",
    hint: "Think about distance — doing more than necessary"
  },
  {
    id: "idio_023",
    category: "idioms",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "He's walking on ___ since the argument with his boss. He could be fired any day.",
    blanks: [
      { "position": 1, "correct": "eggshells", "options": ["eggshells", "glass", "needles", "water"] }
    ],
    question: "Pick the word that completes this idiom meaning 'being in a dangerously vulnerable situation'.",
    explanation: "'Walking on eggshells' means being very careful about what you say or do to avoid upsetting someone.",
    hint: "Think about something fragile and easily broken"
  },
  {
    id: "idio_024",
    category: "idioms",
    difficulty: "hard",
    type: "sentence_complete",
    sentence_template: "Don't count your ___ before they hatch — the deal isn't finalized yet.",
    blanks: [
      { "position": 1, "correct": "chickens", "options": ["chickens", "eggs", "blessings", "profits"] }
    ],
    question: "Choose the word that completes this well-known idiom about premature optimism.",
    explanation: "'Don't count your chickens before they hatch' means don't assume success before it actually happens.",
    hint: "This idiom involves barnyard animals and not being too optimistic"
  }

];