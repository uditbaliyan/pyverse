"""Pure helpers for Parsons puzzles: build the reference program, verify it.

``verify`` is an authoring-time gate (``check_parsons``), like ``labs.gym.verify``:
the learner's arrangement is only ever checked in the browser.
"""

from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass
from dataclasses import field

from pyverse.common.sandbox import run_python

INDENT = "    "
TIMEOUT = 10


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def solution_lines(lines) -> list[tuple[str, int]]:
    """The correct program as ``(text, indent)`` pairs, distractors left out."""
    out = []
    for item in lines:
        value = item.value if hasattr(item, "value") else item
        if not value["is_distractor"]:
            out.append((value["text"], int(value["indent"])))
    return out


def solution_source(lines) -> str:
    return "".join(f"{INDENT * ind}{text}\n" for text, ind in solution_lines(lines))


def verify(lines, expected_output: str = "") -> Report:
    """Parse the reference program; if ``expected_output`` is set, run and compare."""
    report = Report()
    pairs = solution_lines(lines)
    if len(pairs) < 2:  # noqa: PLR2004
        report.errors.append("needs at least two non-distractor lines")
        return report
    source = solution_source(lines)
    try:
        ast.parse(source)
    except SyntaxError as exc:
        report.errors.append(
            f"reference solution is not valid Python: {exc.msg} (line {exc.lineno})",
        )
        return report
    texts = [t for t, _ in pairs]
    if len(set(texts)) != len(texts) and not any(
        t.strip() in {"else:", "pass", "break", "continue"}
        or t.startswith(("elif ", "print("))
        for t in texts
    ):
        report.warnings.append(
            "duplicate lines: learners may find several valid orders",
        )
    for item in lines:
        value = item.value if hasattr(item, "value") else item
        if value["is_distractor"] and not value["feedback"]:
            report.warnings.append(f"distractor {value['text']!r} has no feedback")
    if expected_output.strip():
        try:
            done = run_python(
                [sys.executable, "-c", source],
                stdin="",
                timeout=TIMEOUT,
                parent_env=os.environ,
            )
        except Exception as exc:  # noqa: BLE001 - timeout or OS error: report, don't crash
            report.errors.append(f"reference solution did not run: {exc}")
            return report
        if done.returncode != 0:
            report.errors.append(
                f"reference solution raised: {done.stderr.strip().splitlines()[-1:]}",
            )
        elif done.stdout.strip() != expected_output.strip():
            report.errors.append(
                f"output mismatch: expected {expected_output.strip()!r}, got {done.stdout.strip()!r}",
            )
    return report
