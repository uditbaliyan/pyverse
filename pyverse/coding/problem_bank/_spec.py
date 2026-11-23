"""Authoring helpers for the problem bank.

Pure Python, no Django imports: the bank must stay importable by tests, by
`seed_problems`, and by any script that just wants to read the data.

A problem is a plain dict built by `problem(...)`. Nothing here talks to the
database; `manage.py seed_problems` turns these dicts into `CodingProblem`
rows (see `pyverse/coding/management/commands/seed_problems.py`).
"""

from __future__ import annotations

import textwrap
from typing import Any

# Topic slug -> display title. `warm-up` and `arrays-and-hashing` already exist
# in content/site.json; the seed command creates the rest under the Practice
# hub the first time it runs. Order here is the order they are created in.
TOPICS: dict[str, str] = {
    "warm-up": "Warm-up",
    "arrays-and-hashing": "Arrays & Hashing",
    "two-pointers": "Two Pointers",
    "sliding-window": "Sliding Window",
    "stack": "Stack",
    "binary-search": "Binary Search",
    "pattern-printing": "Pattern Printing",
    "matrix-patterns": "Matrix Patterns",
    "number-play": "Number Play",
    "string-play": "String Play",
    "grid-play": "Grids & Patterns",
    "array-play": "Array Practice",
}


def code(source: str) -> str:
    """Dedent a triple-quoted snippet and end it with exactly one newline."""
    return textwrap.dedent(source).strip("\n") + "\n"


def html(*paragraphs: str) -> str:
    """Wrap each string in <p>…</p>; a string that starts with '<' is kept as is."""
    return "".join(
        p if p.lstrip().startswith("<") else f"<p>{p}</p>" for p in paragraphs
    )


def problem(  # noqa: PLR0913
    *,
    slug: str,
    title: str,
    topic: str,
    difficulty: str,
    fn: str,
    signature: str,
    description: str,
    examples: list[tuple[str, str, str]],
    constraints: list[str],
    solution: str,
    cases: list[tuple[str, str, bool]],
    hints: tuple[str, str, str],
    approaches: list[tuple[str, str, str, str, bool]],
    todo: str,
    trace: int = 1,
    explanation: str = "",
    notes: list[tuple[int, str, bool]] | None = None,
    predictions: list[tuple[int, str, str]] | None = None,
    patterns: list[str] | None = None,
    techniques: list[str] | None = None,
    companies: list[str] | None = None,
    comparator: str = "exact",
    custom_comparator: str = "",
) -> dict[str, Any]:
    """One problem, in the shape `seed_problems` expects.

    `cases` are `(args_source, expected_source, is_hidden)`; the args are the
    argument list exactly as it would be written inside the call, which is how
    the grader evaluates them. `trace` is the 1-based index among the *visible*
    cases (the same convention as `CodingProblem.trace_case`).
    """
    solution = code(solution)
    header = solution.splitlines()[0]
    starter = f"{header}\n    # {todo}\n    pass\n"
    return {
        "slug": slug,
        "title": title,
        "topic": topic,
        "difficulty": difficulty,
        "function_name": fn,
        "function_signature": signature,
        "description": description,
        "examples": examples,
        "constraints": constraints,
        "starter_code": starter,
        "solution_code": solution,
        "solution_explanation": explanation,
        "comparator": comparator,
        "custom_comparator_code": code(custom_comparator) if custom_comparator else "",
        "cases": cases,
        "trace_case": trace,
        "hints": hints,
        "approaches": approaches,
        "trace_notes": notes or [],
        "trace_predictions": predictions or [],
        "patterns": patterns or [],
        "techniques": techniques or [],
        "companies": companies or [],
    }
