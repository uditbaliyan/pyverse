# ruff: noqa: PLR2004
"""Every page that runs learner Python does it in the killable worker."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "templates/coding/problem_page.html",
    "templates/labs/lab_page.html",
    "templates/lms/lesson_page.html",
]


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize("rel", PAGES)
def test_page_hands_python_to_the_worker_not_to_pyscript(rel):
    html = _read(rel)
    assert "with embedded=True" in html
    assert "js/pyverse-runtime.js" in html
    assert "js/pyverse-runner.js" in html
    assert "vendor/pyodide/" in html
    assert "pyscript.net" not in html


@pytest.mark.parametrize(
    "rel",
    ["static/js/lab-engine.js", "static/lms/js/notebook.js"],
)
def test_page_scripts_no_longer_call_python_on_the_main_thread(rel):
    js = _read(rel)
    assert "window._pyNotebook" not in js.replace("`window._pyNotebook`", "")
    assert "_pvTrace(" not in js
    assert "PyverseRuntime" in js


def test_runner_handles_every_message_type_the_runtime_sends():
    sent = set(
        re.findall(r'call\(\{ type: "(\w+)"', _read("static/js/pyverse-runtime.js")),
    )
    handled = set(
        re.findall(r'msg\.type === "(\w+)"', _read("static/js/pyverse-runner.js")),
    )
    assert sent == {"exec", "trace", "lab", "notebook"}
    assert sent <= handled


def test_every_call_has_a_time_budget():
    runtime = _read("static/js/pyverse-runtime.js")
    body = re.search(r"var BUDGET = \{(.*?)\}", runtime).group(1)
    budgets = dict(re.findall(r"(\w+): (\d+)", body))
    assert set(budgets) == {"run", "submit", "trace", "lab", "notebook"}
    assert all(int(ms) <= 10_000 for ms in budgets.values())
