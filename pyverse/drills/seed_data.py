"""Starter Parsons puzzles, ported from neetcode/quiz/parsons_quiz.html.

Lines are (text, indent, is_distractor, feedback); the correct program is the
non-distractor lines in the order given.
"""

TOPICS = {
    "control-flow-and-loops": "Control Flow & Loops",
    "comprehensions": "Comprehensions",
}

PUZZLES = [
    {
        "slug": "word-frequency-counter",
        "title": "Word Frequency Counter",
        "topic": "control-flow-and-loops",
        "concept": "Dictionary Iteration",
        "difficulty": "medium",
        "description": "Build a function that counts word frequencies in a sentence and prints each word "
        "with its count in `word: count` format, sorted alphabetically. Use a dict and a "
        "loop.",
        "expected_output": "apple: 2\nbanana: 1\ncherry: 3",
        "lines": [
            (
                "def count_words(sentence):",
                0,
                False,
                "This must be the first line — it defines the function.",
            ),
            (
                "freq = {}",
                1,
                False,
                "Initialize the frequency dict at indent level 1 (inside the function).",
            ),
            (
                "for word in sentence.split():",
                1,
                False,
                "Iterate over words — one indent level inside the function body.",
            ),
            (
                "freq[word] = freq.get(word, 0) + 1",
                2,
                False,
                "This is the body of the for-loop, so it needs 2 levels of indentation.",
            ),
            (
                "for word in sorted(freq):",
                1,
                False,
                "Second loop to print results — back to 1 level of indent.",
            ),
            (
                'print(f"{word}: {freq[word]}")',
                2,
                False,
                "Inside the print loop — 2 levels of indent.",
            ),
            (
                'sentence = "apple banana cherry apple cherry cherry"',
                0,
                False,
                "Top-level call — no indentation.",
            ),
            (
                "count_words(sentence)",
                0,
                False,
                "Call the function at top level — no indentation.",
            ),
            (
                "freq[word] += 1",
                2,
                True,
                "This crashes if the key doesn't exist yet. Use freq.get() instead.",
            ),
            (
                "return freq",
                1,
                True,
                "We're printing, not returning. Remove this block.",
            ),
        ],
    },
    {
        "slug": "grade-classifier",
        "title": "Grade Classifier",
        "topic": "control-flow-and-loops",
        "concept": "Nested Conditionals",
        "difficulty": "easy",
        "description": "Write a program that reads a score (0–100) and prints a grade: `A` for ≥90, `B` "
        "for ≥80, `C` for ≥70, `D` for ≥60, otherwise `F`. Then print `Pass` or `Fail` "
        "based on whether the grade is D or above.",
        "expected_output": "Grade: B\nPass",
        "lines": [
            ("score = 85", 0, False, "Set the score at top level — no indentation."),
            (
                "if score >= 90:",
                0,
                False,
                "First condition, top-level — no indentation.",
            ),
            ('grade = "A"', 1, False, "Inside the if block — 1 level of indent."),
            (
                "elif score >= 80:",
                0,
                False,
                "elif must align with if — no indentation.",
            ),
            ('grade = "B"', 1, False, "Inside elif — 1 level of indent."),
            (
                "elif score >= 70:",
                0,
                False,
                "Another elif at top level — no indentation.",
            ),
            ('grade = "C"', 1, False, "Inside elif — 1 level of indent."),
            (
                "elif score >= 60:",
                0,
                False,
                "Another elif at top level — no indentation.",
            ),
            ('grade = "D"', 1, False, "Inside elif — 1 level of indent."),
            ("else:", 0, False, "else aligns with if — no indentation."),
            ('grade = "F"', 1, False, "Inside else — 1 level of indent."),
            (
                'print(f"Grade: {grade}")',
                0,
                False,
                "Print at top level after all branches — no indent.",
            ),
            (
                'if grade in ("A","B","C","D"):',
                0,
                False,
                "Second if-block at top level — no indent.",
            ),
            ('print("Pass")', 1, False, "Inside the pass check — 1 level of indent."),
            ("else:", 0, False, "else for pass/fail — top level, no indent."),
            ('print("Fail")', 1, False, "Inside the else — 1 level of indent."),
            (
                "score = int(input())",
                0,
                True,
                "We're hardcoding score = 85, not reading from input.",
            ),
            (
                "print(grade)",
                0,
                True,
                "Use the f-string version: print(f'Grade: {grade}')",
            ),
        ],
    },
    {
        "slug": "pythagorean-triples-finder",
        "title": "Pythagorean Triples Finder",
        "topic": "comprehensions",
        "concept": "List Comprehension + Filter",
        "difficulty": "medium",
        "description": "Use a list comprehension to find all Pythagorean triples `(a, b, c)` where `a "
        "&lt; b &lt; c`, all values are in range 1–20, and `a² + b² == c²`. Print each "
        "triple on its own line.",
        "expected_output": "(3, 4, 5)\n(5, 12, 13)\n(6, 8, 10)\n(8, 15, 17)\n(9, 12, 15)\n(12, 16, 20)",
        "lines": [
            (
                "limit = 20",
                0,
                False,
                "Set the range limit at top level — no indentation.",
            ),
            (
                "triples = [",
                0,
                False,
                "Start the list comprehension at top level — no indent.",
            ),
            (
                "    (a, b, c)",
                0,
                False,
                "The output expression — what each element looks like.",
            ),
            (
                "    for a in range(1, limit + 1)",
                0,
                False,
                "Outer loop over 'a' values.",
            ),
            (
                "    for b in range(a + 1, limit + 1)",
                0,
                False,
                "Middle loop — b starts at a+1 to ensure a < b.",
            ),
            (
                "    for c in range(b + 1, limit + 1)",
                0,
                False,
                "Inner loop — c starts at b+1 to ensure b < c.",
            ),
            (
                "    if a**2 + b**2 == c**2",
                0,
                False,
                "The Pythagorean condition — the filter clause.",
            ),
            ("]", 0, False, "Close the list comprehension bracket."),
            (
                "for triple in triples:",
                0,
                False,
                "Loop to print each triple — top level.",
            ),
            (
                "    print(triple)",
                0,
                False,
                "Print inside the loop — already indented in the text, keep indent at 0.",
            ),
            (
                "    if a < b < c",
                0,
                True,
                "The order is already enforced by range(a+1, ...) and range(b+1, ...) — this is "
                "redundant.",
            ),
            (
                "triples.sort()",
                0,
                True,
                "The comprehension naturally produces sorted output — no explicit sort needed.",
            ),
        ],
    },
]
