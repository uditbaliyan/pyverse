# PyVerse DSA problem style guide

Prepended to every CodingProblem generation. Tone and conventions only — the
JSON shape and the grader's rules are in the schema that follows this file.

## Who reads this

Someone a few weeks into Python, practising for interviews. They can read code
but not yet guess what an algorithm is *for*. They will be graded by running
their function against the test cases, so the one thing the statement must make
unmistakable is **what the function returns**.

## Voice

- Second person, present tense, plain words. "Return the indices", not "the
  indices should be returned".
- Explain the *why* in one clause rather than adding a sentence of motivation.
- No filler openings ("In this problem, we will..."), no closers ("Good luck!"),
  no difficulty labels in the title, no exclamation marks.
- American spelling, sentence case for headings.

## Formatting

- `description`, `solution_explanation`, hint `text`, and approach
  `description` are HTML, not Markdown: `<p>` per paragraph, `<code>` for
  identifiers and literals, `<strong>` for the one detail that decides the
  problem. Never emit `**`, backticks or fenced blocks in these fields.
- Do not restate the constraints inside the description; they have their own
  list. One short paragraph plus a second paragraph for the tricky detail is
  usually the whole statement.
- `constraints`: the bounds a solution must respect, each as a bare inequality
  string, e.g. `2 <= nums.length <= 10^4`. Skip "the input is valid" boilerplate.
- Examples: arguments as a reader would write them (`nums = [2,7,11,15],
  target = 9`), the returned value, and a note that shows the arithmetic.

## The parts that must be true

- `solution_code` is the reference answer and **must actually pass every test
  case you return**; it is executed before the draft is saved.
- Solutions are deterministic and pure: no printing, no input prompts, no
  randomness, no reliance on the caller's globals.
- Write every expected output as the Python value it is (`[0, 1]`, `"hi"`,
  `2.5`, `True`) — it is compared with real equality, so a string that merely
  looks like a list fails every learner.
- One logical task per problem. If the statement needs "and also", split it.

## Test cases

Four to six cases, in this order:

1. The example from the statement, so the first run looks familiar.
2. Two or three more visible cases, including the smallest legal input.
3. The boundary and degenerate cases of the stated constraints, marked
   `"is_hidden": true` — these are what stop a brute-force answer passing.

Never hide *all* of them: the learner needs something to check against.

## Hints

Write all three tiers, in ascending order of revelation:

- `nudge`: a question that points at the inefficiency or the missing idea.
  Never names the data structure.
- `approach`: names the mechanism and how it is used in one sentence.
- `solution`: the final move, as prose with a fragment of code at most. Never
  the complete solution.

## Editorial

Two approaches unless the problem genuinely has one: the obvious one first
(`"is_optimal": false`), then the intended one (`"is_optimal": true`). Say what
each costs. Exactly one approach is optimal.

## Good and bad

Bad hint (gives it away at tier 1): "Use a dict mapping value to index."

Good hint at tier 1: "Checking every pair works, but it costs O(n²). Is there
something you could remember as you scan once?"

Bad test case (fails on a correct solution that returns floats):

    {"input": "[1, 2]", "expected_output": "2", "is_hidden": false}

Good test case, with the comparator chosen to match:

    {"input": "[1, 2]", "expected_output": "1.5", "is_hidden": false}

Bad statement: "Given an array, find two numbers that sum to a target and
return their indices. Constraints: 2 <= n <= 10^4."

Good statement: "Given an array of integers `nums` and an integer `target`,
return the indices of the two numbers that add up to `target`. Each input has
**exactly one solution**, and you may not use the same element twice."
