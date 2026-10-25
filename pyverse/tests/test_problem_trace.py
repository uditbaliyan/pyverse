# ruff: noqa: E501, PLR2004, SLF001
"""Practice → Labs: "solve a problem, then watch it execute".

The tracer is browser Python living in a template; `trace_harness` execs that
exact source, so these tests cover what ships. The JS glue has no runner in this
repo, so the contract with the engine is pinned by `test_engine_ids_exist`.
"""

from __future__ import annotations

import json
import re
import signal
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.template.loader import render_to_string
from django.test import RequestFactory

from pyverse.coding.models import CodingProblem
from pyverse.coding.trace_harness import load_tracer

ROOT = Path(__file__).resolve().parents[1]
TWO_SUM = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n"
    "            return [seen[target - n], i]\n"
    "        seen[n] = i\n"
)


@pytest.fixture(scope="module")
def tracer():
    return load_tracer()


def _call(tracer, code, fn, args, limit=None):
    return json.loads(tracer.trace_call(code, fn, args, limit))


# ── tracer ─────────────────────────────────────────────────────────────────
def test_runtime_boots_and_registers_both_entry_points(tracer):
    assert tracer.ready
    assert tracer.window._pvTrace is tracer.trace
    assert tracer.window._pvTraceCall is tracer.trace_call


def test_trace_call_walks_the_learners_lines_then_the_harness(tracer):
    result = _call(tracer, TWO_SUM, "two_sum", "[2, 7, 11, 15], 9")
    assert result["error"] is None
    lines = [step["line"] for step in result["steps"]]
    assert lines[0] == 1  # the def
    assert result["harness_from"] == 8  # 6 code lines + blank + marker
    assert 9 in lines  # the appended call line was executed
    # the return value is attached to the function's last line, not a new step
    assert result["steps"][-1]["returned"]["items"][0] == {"k": "int", "v": 0}
    assert "_result = two_sum([2, 7, 11, 15], 9)" in result["source"]


def test_trace_call_keeps_main_block_dormant_like_the_grader(tracer):
    code = "def f(a):\n    return a\nif __name__ == '__main__':\n    print('MAIN')\n"
    result = _call(tracer, code, "f", "1")
    assert result["stdout"] == ""
    assert result["error"] is None


@pytest.fixture
def _alarm():
    """Fail, rather than hang CI, if the limit ever stops working (POSIX only)."""
    if not hasattr(signal, "SIGALRM"):
        yield
        return

    def _boom(*_):
        msg = "tracer ignored its line limit"
        raise AssertionError(msg)

    previous = signal.signal(signal.SIGALRM, _boom)
    signal.alarm(10)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


@pytest.mark.usefixtures("_alarm")
def test_runaway_loop_is_stopped_even_if_the_learner_catches_exceptions(tracer):
    code = "def f():\n    try:\n        while True:\n            pass\n    except Exception:\n        pass\n"
    result = _call(tracer, code, "f", "", limit=5_000)
    assert result["error"].startswith("TraceLimitExceeded")
    assert len(result["steps"]) <= 400


def test_bad_arguments_are_reported_not_executed(tracer):
    result = _call(tracer, "def f(a):\n    return a\n", "f", "1,,")
    assert result["steps"] == []
    assert result["error"].startswith("SyntaxError in the arguments")


def test_learner_error_is_located(tracer):
    result = _call(tracer, "def f(a):\n    return 1 / a\n", "f", "0")
    assert result["error"].startswith("ZeroDivisionError")
    assert result["error_line"] == 2


def test_labs_call_is_unchanged_without_a_limit(tracer):
    tracer.window._pendingLabCode = "total = 0\nfor i in range(1000):\n    total += i\n"
    result = json.loads(tracer.trace())
    assert result["error"] is None
    assert result["truncated"] is True  # recorded to the cap, but ran to the end
    assert "harness_from" not in result


# ── page wiring ────────────────────────────────────────────────────────────
@pytest.fixture
def problem(db):
    return CodingProblem.objects.create(
        title="Two Sum",
        function_name="two_sum",
        function_signature="(nums, target)",
        solution_code=TWO_SUM,
        starter_code="def two_sum(nums, target):\n    pass\n",
        test_cases=json.dumps(
            [
                {
                    "type": "test_case",
                    "value": {
                        "input": "[2, 7, 11, 15], 9",
                        "expected_output": "[0, 1]",
                        "is_hidden": False,
                    },
                },
                {
                    "type": "test_case",
                    "value": {
                        "input": "[3, 3], 6",
                        "expected_output": "[0, 1]",
                        "is_hidden": True,
                    },
                },
            ],
        ),
    )


def _render(problem):
    class _Page:
        title = "Arrays"
        url = "/practice/arrays/"

    request = RequestFactory().get(problem.get_absolute_url())
    return render_to_string(
        "coding/problem_page.html",
        {
            "page": _Page(),
            "problem": problem,
            "topic": None,
            "payload": problem.grading_payload(),
        },
        request=request,
    )


def test_problem_page_has_one_runtime_two_py_blocks_and_the_trace_panel(problem):
    html = _render(problem)
    assert html.count("pyscript.net/releases/2025.7.3/core.js") == 1
    assert html.count('<script type="py">') == 2
    for needle in (
        'id="trace-section"',
        'id="trace-btn"',
        'id="trace-prompt"',
        'id="lab-root"',
        "js/problem-trace.js",
        "css/problem-trace.css",
    ):
        assert needle in html


def test_reference_is_baked_in_only_when_there_is_one(problem):
    assert 'id="pyverse-trace-reference"' in _render(problem)
    problem.solution_code = ""
    problem.save()
    html = _render(problem)
    assert 'id="pyverse-trace-reference"' not in html
    assert 'id="trace-src-ref"' not in html


def test_hidden_case_input_never_reaches_the_trace_surface(problem):
    html = _render(problem)
    # the grader payload carries every case by design; the trace UI must not
    # add a second copy of a hidden input anywhere outside it
    panel = render_to_string("includes/trace_panel.html", {"problem": problem})
    assert "[3, 3], 6" not in panel
    assert html.count("[3, 3], 6") == 1


def test_engine_ids_exist():
    """Every element id the engine requires must be in the embedded panel."""
    engine = (ROOT / "static/js/lab-engine.js").read_text(encoding="utf-8")
    panel = (ROOT / "templates/includes/trace_panel.html").read_text(encoding="utf-8")
    ids = set(re.findall(r'getElementById\("([^"]+)"\)', engine))
    optional = {
        "lab-run",
        "lab-new-editor",
        "lab-code",
    }  # editor lives on lab_page only
    missing = {i for i in ids - optional if f'id="{i}"' not in panel}
    for name in ("first", "back", "play", "next", "last"):  # built as "lab-" + name
        assert f'id="lab-{name}"' in panel
    assert not missing, missing


# ── QA command ─────────────────────────────────────────────────────────────
def test_check_problem_traces_passes_a_good_problem(problem):
    out = StringIO()
    call_command("check_problem_traces", "--strict", stdout=out)
    assert "[  ok] two-sum" in out.getvalue()


def test_check_problem_traces_fails_a_wrong_reference(problem):
    problem.solution_code = problem.solution_code.replace(
        "[seen[target - n], i]", "[i, i]",
    )
    problem.save()
    with pytest.raises(CommandError):
        call_command("check_problem_traces", stdout=StringIO())


def test_check_problem_traces_warns_when_trace_is_truncated(db):
    CodingProblem.objects.create(
        title="Sum Range",
        function_name="total",
        solution_code="def total(n):\n    t = 0\n    for i in range(n):\n        t += i\n    return t\n",
        test_cases=json.dumps(
            [
                {
                    "type": "test_case",
                    "value": {
                        "input": "500",
                        "expected_output": "124750",
                        "is_hidden": False,
                    },
                },
            ],
        ),
    )
    out = StringIO()
    call_command("check_problem_traces", stdout=out)
    assert "step cap" in out.getvalue()
    with pytest.raises(CommandError):
        call_command("check_problem_traces", "--strict", stdout=StringIO())
