# ruff: noqa: E501, PLR2004, SLF001
"""Trace quality gate: is the walk-through correct, instructive, and the best example?

Runs the shipped tracer (`trace_harness`) in CPython, like `test_problem_trace.py`.
"""

from __future__ import annotations

import json
from io import StringIO
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.template.loader import render_to_string
from django.test import RequestFactory

from pyverse.coding.management.commands import check_problem_traces as cmd
from pyverse.coding.models import CodingProblem
from pyverse.coding.trace_harness import load_tracer
from pyverse.coding.tracing import MAX_STEPS
from pyverse.coding.tracing import MIN_STEPS
from pyverse.coding.tracing import CaseTrace
from pyverse.coding.tracing import choose_trace_case
from pyverse.coding.tracing import returned_matches
from pyverse.coding.tracing import trace_all_visible

TOTAL = (
    "def total(n):\n    t = 0\n    for i in range(n):\n        t += i\n    return t\n"
)
#: (input, expected, steps once traced): 0 is too trivial, 500 hits the step cap.
CASES = [("0", "0"), ("60", "1770"), ("5", "10"), ("3", "3"), ("500", "124750")]


@pytest.fixture(scope="module")
def tracer():
    return load_tracer()


def _fake(solution=TOTAL, cases=CASES, comparator="exact", custom=""):
    return SimpleNamespace(
        function_name="total",
        solution_code=solution,
        comparator=comparator,
        custom_comparator_code=custom,
        visible_test_cases=[
            {"input": a, "expected": e, "hidden": False} for a, e in cases
        ],
    )


def _db_problem(cases=CASES, solution=TOTAL, **extra):
    return CodingProblem.objects.create(
        title="Total",
        function_name="total",
        function_signature="(n)",
        solution_code=solution,
        test_cases=json.dumps(
            [
                {
                    "type": "test_case",
                    "value": {"input": a, "expected_output": e, "is_hidden": False},
                }
                for a, e in cases
            ],
        ),
        **extra,
    )


# ── the tracer reports what the call returned ──────────────────────────────
def test_practice_trace_reports_return_value_labs_trace_does_not(tracer):
    practice = json.loads(tracer.trace_call(TOTAL, "total", "5"))
    assert practice["returned_repr"] == "10"
    tracer.window._pendingLabCode = "x = 1\n"
    assert "returned_repr" not in json.loads(tracer.trace())  # Labs shape unchanged


def test_unrepresentable_or_missing_return_is_none(tracer):
    boom = "class B:\n    def __repr__(self):\n        raise RuntimeError\n\ndef f():\n    return B()\n"
    assert json.loads(tracer.trace_call(boom, "f", ""))["returned_repr"] is None
    crash = json.loads(tracer.trace_call("def f():\n    1 / 0\n", "f", ""))
    assert crash["error"]
    assert crash["returned_repr"] is None


# ── same comparator semantics as the grader ────────────────────────────────
@pytest.mark.parametrize(
    ("returned", "expected", "comparator", "custom", "matches"),
    [
        ("[0, 1]", "[0, 1]", "exact", "", True),
        ("[1, 0]", "[0, 1]", "exact", "", False),
        ("[1, 0]", "[0, 1]", "sorted_list", "", True),
        ("0.3000000001", "0.3", "float_tolerance", "", True),
        ("0.31", "0.3", "float_tolerance", "", False),
        ("5", "10", "custom", "def compare(a, e):\n    return a * 2 == e\n", True),
        ("5", "11", "custom", "def compare(a, e):\n    return a * 2 == e\n", False),
        ("5", "5", "custom", "", None),  # custom declared, no code: undecidable
        (None, "5", "exact", "", None),  # repr unavailable
    ],
)
def test_returned_matches_follows_the_graders_comparators(
    returned,
    expected,
    comparator,
    custom,
    matches,
):
    assert returned_matches(returned, expected, comparator, custom)[0] is matches


def test_empty_answers_are_trivial():
    assert returned_matches("[]", "[]", "exact")[1] is True
    assert (
        returned_matches("0", "0", "exact")[1] is False
    )  # 0 / False can be real answers


# ── choosing the example ───────────────────────────────────────────────────
def test_best_case_is_the_fewest_steps_that_is_still_instructive(tracer):
    traces = trace_all_visible(_fake(), tracer)
    assert [t.steps for t in traces][:4] == [5, 125, 15, 11]
    assert traces[0].steps < MIN_STEPS
    assert not traces[0].usable  # trivial: skipped
    assert traces[4].truncated
    assert not traces[4].usable  # cut off: skipped
    best = choose_trace_case(traces)
    assert (best.index, best.args, best.steps) == (3, "3", 11)


def test_choice_skips_cases_whose_value_the_answer_key_rejects(tracer):
    wrong_key = [("0", "0"), ("60", "1770"), ("5", "10"), ("3", "999")]
    best = choose_trace_case(trace_all_visible(_fake(cases=wrong_key), tracer))
    assert best.args == "5"  # 3 would be shorter but its traced value is "wrong"


def test_choice_falls_back_to_first_visible_when_nothing_is_usable(tracer):
    traces = trace_all_visible(_fake(cases=[("0", "0"), ("500", "124750")]), tracer)
    assert not any(t.usable for t in traces)
    assert choose_trace_case(traces).index == 0
    assert choose_trace_case([]) is None


def test_ties_go_to_the_earlier_case():
    mk = lambda i: CaseTrace(index=i, args=str(i), steps=10, matches_expected=True)  # noqa: E731
    assert choose_trace_case([mk(0), mk(1)]).index == 0
    assert MIN_STEPS < 10 < MAX_STEPS


# ── the command: gate, report, apply ───────────────────────────────────────
def test_a_solution_returning_the_wrong_value_fails_the_gate(db, monkeypatch):
    """Even if verification were fooled, a traced value the key rejects is an error."""
    _db_problem(cases=[("3", "3")], solution=TOTAL.replace("return t", "return t + 1"))
    monkeypatch.setattr(cmd, "verify", lambda **_: SimpleNamespace(ok=True))
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("check_problem_traces", stdout=out)
    assert "answer key rejects" in out.getvalue()


def test_wrong_reference_fails_even_without_the_stub(db):
    _db_problem(cases=[("3", "3")], solution=TOTAL.replace("return t", "return t + 1"))
    with pytest.raises(CommandError):
        call_command("check_problem_traces", stdout=StringIO())


def test_too_short_and_too_long_traces_warn(db):
    _db_problem(cases=[("0", "0")])
    out = StringIO()
    call_command("check_problem_traces", stdout=out)
    assert "too trivial" in out.getvalue()
    CodingProblem.objects.all().delete()
    _db_problem(cases=[("150", "11175")])  # ~305 steps: under the cap, over MAX_STEPS
    out = StringIO()
    call_command("check_problem_traces", stdout=out)
    assert f"> {MAX_STEPS}" in out.getvalue()


def test_report_prints_one_row_per_problem(db):
    _db_problem()
    out = StringIO()
    call_command("check_problem_traces", "--report", stdout=out)
    lines = out.getvalue().splitlines()
    assert lines[0].split() == [
        "slug",
        "case",
        "steps",
        "fits",
        "matches",
        "best",
        "status",
    ]
    row = next(line for line in lines if line.startswith("total"))
    assert row.split()[:7] == ["total", "1", "5", "yes", "yes", "4", "warn"]


def test_apply_pins_the_best_case_and_never_overwrites_an_authors_pin(db):
    first = _db_problem()
    pinned = _db_problem(trace_case=3)
    pinned.title = "Total pinned"
    pinned.slug = "total-pinned"
    pinned.save()
    call_command("check_problem_traces", "--apply", stdout=StringIO())
    first.refresh_from_db()
    pinned.refresh_from_db()
    assert first.trace_case == 4
    assert first.trace_case_input == "3"
    assert pinned.trace_case == 3  # the author's choice stands


def test_page_offers_the_chosen_example_only_when_set(db):
    problem = _db_problem()

    class _Page:
        title = "T"
        url = "/practice/t/"

    def render():
        return render_to_string(
            "coding/problem_page.html",
            {
                "page": _Page(),
                "problem": problem,
                "topic": None,
                "payload": problem.grading_payload(),
            },
            request=RequestFactory().get(problem.get_absolute_url()),
        )

    assert "pyverse-trace-case" not in render()
    problem.trace_case = 4
    assert (
        '<script id="pyverse-trace-case" type="application/json">"3"</script>'
        in render()
    )
    problem.trace_case = 99  # stale after cases were removed: ignored, not an error
    assert "pyverse-trace-case" not in render()


def test_admin_column_reports_trace_readiness(db):
    assert _db_problem().trace_status == "ready (first example)"
    assert _db_problem(solution="").trace_status == "no reference solution"
    assert _db_problem(cases=[], trace_case=None).trace_status == "no visible example"
    assert _db_problem(trace_case=4).trace_status == "ready (example 4)"
    from pyverse.coding.wagtail_hooks import CodingProblemViewSet  # noqa: PLC0415

    assert "trace_status" in CodingProblemViewSet.list_display
