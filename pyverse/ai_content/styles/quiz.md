# PyVerse quiz style guide

Prepended to every quiz generation. Tone and conventions only — the JSON shape
and the answer-key rules are in the schema that follows this file.

## What a quiz is

Three to five quick checks on one topic, taken straight after a lesson or a
couple of practice problems. It tests understanding, not recall: every question
should be answerable by someone who understood the idea, and missable by
someone who memorised the syntax. It is not an exam and not a trick.

## Questions

- Plain text, one sentence where possible. State the question, not the setup.
- Ask about *behavior* ("What does this code print?", "Which approach finds the
  pair in one pass?") rather than definitions that can be pattern-matched.
- No "all of the above", no double negatives, no "which is NOT", no questions
  whose answer depends on a version detail.
- `code_snippet` only when the question is about code. It is plain Python, runs
  as written, is short (under 10 lines), and prints nothing on its own unless
  the question asks what it prints.

## Choices

- Exactly four, similar in length and shape, so the answer is not obvious from
  formatting. All four should be things a beginner might actually believe.
- The distractors are the point: each one should be the wrong mental model of
  the topic, not a random value. "Whatever it printed" is a good distractor for
  a question about `return`; "42" is not.
- One correct choice, never two. Vary which position it sits in across the
  quiz — a key that is always first is not a quiz.

## Explanations

Every question needs an `explanation`, and it is not a restatement of the
answer. It says *why*: what the correct answer does, and what the tempting
wrong one would have done instead. Backticks around code are fine here.

This field is how the answer key gets reviewed, because nothing can execute a
factual answer the way it can execute a solution. Write it for the reviewer as
much as for the learner.

## Tone

- Neutral and concrete. No "Great job!", no "Remember, always...".
- Instructions field: one or two plain sentences on what the quiz checks and
  that retrying is fine.
- Difficulty is `easy` unless the topic itself is medium or hard.
- `pass_percentage` 70 unless the quiz is deliberately strict.

## Good and bad

Bad question: "Which of the following statements about dictionaries is NOT
incorrect?"

Good question: "What is the average time complexity of a dictionary lookup in
Python?"

Bad explanation: "O(1) is the correct answer."

Good explanation: "Dicts are hash tables: one hash, one probe, so O(1) on
average. The O(n) choice would be right for a list membership test, which is
the usual mix-up."

Bad distractor set: ["O(1)", "banana", "42", "None"].

Good distractor set: ["O(1)", "O(log n)", "O(n)", "O(n log n)"].
