"""C1/C2: authored step notes and prediction prompts on the reference trace.

Payload building, authoring validation, the dead-note check and page rendering
are covered here; the viewer's DOM behavior is covered by the e2e suite.
"""

from __future__ import annotations

import json
from io import StringIO

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory

from pyverse.coding.models import CodingProblem

SOLUTION = (
    "def two_sum(nums, target):\n"  # 1
    "    if not nums:\n"  # 2
    "        return []\n"  # 3  (never runs on the example)
    "    seen = {}\n"  # 4
    "    for i, n in enumerate(nums):\n"  # 5
    "        if target - n in seen:\n"  # 6
    "            return [seen[target - n], i]\n"  # 7
    "        seen[n] = i\n"  # 8
)
CASES = [
    {
        "type": "test_case",
        "value": {
            "input": "[2, 7, 11, 15], 9",
            "expected_output": "[0, 1]",
            "is_hidden": False,
        },
    },
]


def _note(line, text="because", *, every_visit=False):
    return {
        "type": "note",
        "value": {"line": line, "note": text, "every_visit": every_visit},
    }


def _prediction(line, question="What is in seen?", answer="{2: 0}"):
    return {
        "type": "prediction",
        "value": {"line": line, "question": question, "answer": answer},
    }


def _make(db, *, notes=(), predictions=(), trace_case=1, solution=SOLUTION):
    return CodingProblem.objects.create(
        title="Two Sum",
        function_name="two_sum",
        function_signature="(nums, target)",
        solution_code=solution,
        test_cases=json.dumps(CASES),
        trace_case=trace_case,
        trace_notes=json.dumps(list(notes)),
        trace_predictions=json.dumps(list(predictions)),
    )


def _page(problem):
    class _Page:
        title = "Arrays"
        url = "/practice/arrays/"

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


# ── payload ────────────────────────────────────────────────────────────────
def test_annotations_are_plain_json_for_the_pinned_example(db):
    problem = _make(
        db,
        notes=[_note(8, every_visit=True)],
        predictions=[_prediction(8)],
    )
    assert problem.trace_annotations == {
        "notes": [{"line": 8, "note": "because", "every_visit": True}],
        "predictions": [
            {"line": 8, "question": "What is in seen?", "answer": "{2: 0}"},
        ],
    }
    json.dumps(problem.trace_annotations)  # must be JSON-safe as built


def test_no_annotations_without_a_pinned_example(db):
    # They describe one specific call, so without a pinned example they are not served.
    assert _make(db, notes=[_note(8)], trace_case=0).trace_annotations is None


def test_no_annotations_without_a_reference_solution(db):
    assert _make(db, notes=[_note(8)], solution="").trace_annotations is None


def test_no_annotations_when_nothing_is_authored(db):
    assert _make(db).trace_annotations is None


# ── authoring validation ───────────────────────────────────────────────────
def test_clean_accepts_lines_inside_the_solution(db):
    _make(db, notes=[_note(1), _note(8)], predictions=[_prediction(5)]).clean()


@pytest.mark.parametrize("field", ["trace_notes", "trace_predictions"])
def test_clean_rejects_a_line_past_the_end(db, field):
    block = _note(99) if field == "trace_notes" else _prediction(99)
    kwargs = {"notes" if field == "trace_notes" else "predictions": [block]}
    with pytest.raises(ValidationError) as caught:
        _make(db, **kwargs).clean()
    assert field in caught.value.message_dict
    assert "8 lines" in caught.value.message_dict[field][0]


# ── page rendering ─────────────────────────────────────────────────────────
def test_page_bakes_annotations_only_when_there_are_some(db):
    assert 'id="pyverse-trace-annotations"' not in _page(_make(db))
    page = _page(_make(db, notes=[_note(8)]))
    assert 'id="pyverse-trace-annotations"' in page


def test_authored_text_cannot_break_out_of_the_page(db):
    evil = "</script><script>alert(1)</script>"
    page = _page(
        _make(db, notes=[_note(8, evil)], predictions=[_prediction(8, evil, evil)]),
    )
    assert evil not in page
    assert "\\u003C/script\\u003E" in page


def test_viewer_writes_authored_text_with_textcontent_only():
    from pathlib import Path  # noqa: PLC0415

    viewer = (
        Path(__file__).resolve().parents[1] / "static/js/tutor-view.js"
    ).read_text(
        encoding="utf-8",
    )
    region = viewer[
        viewer.index("authored notes + predictions") : viewer.index("function render()")
    ]
    assert "innerHTML" not in region
    assert "textContent" in region


# ── check_problem_traces ───────────────────────────────────────────────────
def test_check_warns_about_a_note_on_a_line_that_never_runs(db):
    _make(db, notes=[_note(3)], predictions=[_prediction(8)])
    out = StringIO()
    call_command("check_problem_traces", stdout=out)
    text = out.getvalue()
    assert "note on line 3" in text
    assert "prediction on line 8" not in text  # line 8 runs on the example


def test_check_is_quiet_when_every_annotated_line_runs(db):
    _make(db, notes=[_note(6)], predictions=[_prediction(8)])
    out = StringIO()
    call_command("check_problem_traces", "--strict", stdout=out)
    assert "[  ok] two-sum" in out.getvalue()


def test_check_warns_when_annotations_have_no_pinned_example(db):
    _make(db, notes=[_note(6)], trace_case=0)
    out = StringIO()
    call_command("check_problem_traces", stdout=out)
    assert "no 'Trace example' is pinned" in out.getvalue()
