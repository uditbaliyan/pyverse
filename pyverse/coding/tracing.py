"""Which example a problem's trace should show, and whether that trace is sound.

Authoring-time only (used by `check_problem_traces` and tests); never imported
by the exported site. Pure functions over a problem-like object and the tracer
from `trace_harness.load_tracer()`, so they can be unit-tested with fakes.

A trace is *sound* when the reference solution, run by the shipped tracer on
the example, returns what the answer key says under the problem's own
comparator, the same rule the learner's grader applies (`verify_runner`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from pyverse.ai_content.verify_runner import _load_comparator
from pyverse.ai_content.verify_runner import _matches

# Mirrors LINE_LIMIT in static/js/problem-trace.js.
LINE_LIMIT = 200_000
#: Fewer steps than this is too trivial to teach anything (warning).
MIN_STEPS = 6
#: More steps than this is too long to follow (warning). Below the tracer's cap.
MAX_STEPS = 250


@dataclass
class CaseTrace:
    """The reference solution traced on one visible case."""

    index: int  # position among the visible cases, 0-based
    args: str
    steps: int = 0
    error: str | None = None
    truncated: bool = False
    #: None = could not be decided (no/oversized repr, bad comparator).
    matches_expected: bool | None = None
    trivial: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def usable(self) -> bool:
        """Sound and instructive: a candidate for the page's example."""
        return (
            self.error is None
            and not self.truncated
            and self.matches_expected is True
            and not self.trivial
            and MIN_STEPS <= self.steps <= MAX_STEPS
        )


def _is_trivial(value: Any) -> bool:
    """An answer that shows nothing: None or an empty container/string."""
    return value is None or (
        isinstance(value, (str, list, tuple, dict, set, frozenset)) and not value
    )


def returned_matches(
    returned_repr: str | None,
    expected_source: str,
    comparator: str,
    custom_comparator_code: str = "",
) -> tuple[bool | None, bool]:
    """`(matches, trivial)` for a traced return value, per the grader's rules.

    `matches` is None when the comparison cannot be made (repr unavailable, or
    not evaluable, or the custom comparator is broken).
    """
    if returned_repr is None:
        return None, False
    try:
        actual = eval(returned_repr, {})  # noqa: S307 - our own tracer's repr()
    except Exception:  # noqa: BLE001
        # Not a literal (e.g. a custom object): the grader falls back to repr.
        if comparator != "custom":
            return (
                returned_repr.strip() == str(expected_source).strip(),
                False,
            )
        return None, False
    namespace, error = _load_comparator(
        {"comparator": comparator, "custom_comparator_code": custom_comparator_code},
    )
    if error is not None:
        return None, _is_trivial(actual)
    try:
        matched = bool(
            _matches(actual, expected_source, comparator or "exact", namespace),
        )
    except Exception:  # noqa: BLE001 - a throwing custom compare() is "unknown"
        return None, _is_trivial(actual)
    return matched, _is_trivial(actual)


def trace_visible_case(problem: Any, tracer: Any, index: int) -> CaseTrace:
    """Trace the reference solution on the `index`-th visible case."""
    case = problem.visible_test_cases[index]
    result = CaseTrace(index=index, args=case["input"])
    traced = json.loads(
        tracer.trace_call(
            problem.solution_code,
            problem.function_name,
            case["input"],
            LINE_LIMIT,
        ),
    )
    result.steps = len(traced["steps"])
    result.error = traced["error"]
    result.truncated = bool(traced["truncated"])
    if result.error is None:
        result.matches_expected, result.trivial = returned_matches(
            traced.get("returned_repr"),
            case["expected"],
            problem.comparator,
            problem.custom_comparator_code,
        )
    return result


def trace_all_visible(problem: Any, tracer: Any) -> list[CaseTrace]:
    return [
        trace_visible_case(problem, tracer, index)
        for index in range(len(problem.visible_test_cases))
    ]


def choose_trace_case(traces: list[CaseTrace]) -> CaseTrace | None:
    """The best example to show: fewest steps among the usable ones.

    Usable = sound, not cut off, non-trivial answer, and MIN_STEPS..MAX_STEPS
    steps. Ties go to the earlier case. With no usable case, fall back to the
    first visible one (what the page did before), or None if there is none.
    """
    usable = [trace for trace in traces if trace.usable]
    if usable:
        return min(usable, key=lambda trace: (trace.steps, trace.index))
    return traces[0] if traces else None
