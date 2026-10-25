# ruff: noqa: E501, PLR2004
"""Headless-browser smoke test of the learner loop. Not part of the default run.

    PYVERSE_E2E_URL=http://127.0.0.1:8000 uv run pytest -m e2e

`PYVERSE_E2E_URL` is the root of a running site: `manage.py runserver`, or a
built `_site/` served with `python -m http.server -d _site 8000`. Optional:

    PYVERSE_E2E_PROBLEM   slug of a problem with a reference solution (two-sum)
    PYVERSE_E2E_CHROMIUM  path to a Chromium binary (else Playwright's own)
    PYVERSE_E2E_LAB       slug of a /labs/ page (skipped if unset: Labs still
                          load PyScript from pyscript.net, so they need internet)

Needs `playwright` (`uv pip install playwright && playwright install chromium`).
"""

from __future__ import annotations

import os
import re

import pytest

pytestmark = pytest.mark.e2e

BASE = os.environ.get("PYVERSE_E2E_URL", "").rstrip("/")
PROBLEM = os.environ.get("PYVERSE_E2E_PROBLEM", "two-sum")
LAB = os.environ.get("PYVERSE_E2E_LAB", "")
BOOT_MS = 120_000  # Pyodide cold start

if not BASE:
    pytest.skip("set PYVERSE_E2E_URL to run the browser tests", allow_module_level=True)
sync_api = pytest.importorskip("playwright.sync_api")

LOOP = "def two_sum(nums, target):\n    while True:\n        pass\n"
HEARTBEAT = "window.__ticks = 0; setInterval(() => { window.__ticks += 1; }, 50);"


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as pw:
        exe = os.environ.get("PYVERSE_E2E_CHROMIUM") or None
        launched = pw.chromium.launch(
            executable_path=exe,
            args=["--no-sandbox", "--disable-gpu"],
        )
        yield launched
        launched.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


def _open_problem(page):
    page.goto(f"{BASE}/practice/problem/{PROBLEM}/")
    page.wait_for_selector(
        "body[data-pyverse-ready='1']",
        timeout=BOOT_MS,
        state="attached",
    )
    page.wait_for_function(
        "document.getElementById('run-btn') && !document.getElementById('run-btn').disabled",
    )


def _click(page, selector):
    """DOM click: immune to the dev server's debug-toolbar overlay (absent in `_site/`)."""
    page.wait_for_selector(selector, state="attached")
    page.evaluate("(s) => document.querySelector(s).click()", selector)


def _set_code(page, code):
    page.evaluate(
        "(c) => { const h = document.querySelector('#editor-host .CodeMirror');"
        " if (h) h.CodeMirror.setValue(c); else document.getElementById('editor-ta').value = c; }",
        code,
    )


def test_infinite_loop_times_out_and_never_freezes_the_page(page):
    _open_problem(page)
    page.evaluate(HEARTBEAT)
    _set_code(page, LOOP)
    _click(page, "#run-btn")

    # Mid-loop (budget is 5 s): the page's own timers must still be firing.
    page.wait_for_timeout(2000)
    ticks_mid_loop = page.evaluate("window.__ticks")
    assert ticks_mid_loop > 10, "main thread was blocked while the loop ran"

    page.wait_for_function(
        "document.getElementById('out-area').textContent.includes('Time limit exceeded')",
        timeout=15_000,
    )
    assert "ran for too long" in page.inner_text("#out-area")

    # The worker was killed and re-created: the page recovers and still grades.
    page.wait_for_selector(
        "body[data-pyverse-ready='1']",
        timeout=BOOT_MS,
        state="attached",
    )
    page.wait_for_function("!document.getElementById('run-btn').disabled")


def test_a_passing_run_offers_a_trace_that_steps(page):
    _open_problem(page)
    _click(page, "#run-btn")
    page.wait_for_selector("#trace-prompt button", timeout=30_000)
    _click(page, "#trace-prompt button")  # "Trace your solution" / "Trace this call"
    page.wait_for_selector("#tv-code", timeout=60_000)
    page.wait_for_function(
        "/\\d+/.test((document.getElementById('tv-status') || {}).textContent || '')",
        timeout=60_000,
    )
    status = page.inner_text("#tv-status")
    assert re.search(r"\d+", status), status


def _open_lab(page):
    page.goto(f"{BASE}/labs/{LAB}/")
    page.wait_for_selector(
        "body[data-lab-ready='1']", timeout=BOOT_MS, state="attached"
    )
    page.wait_for_function("!document.getElementById('lab-run').disabled")


def _set_lab_code(page, code):
    page.evaluate(
        "(c) => document.querySelector('#lab-new-editor .CodeMirror').CodeMirror.setValue(c)",
        code,
    )


needs_lab = pytest.mark.skipif(not LAB, reason="set PYVERSE_E2E_LAB to a lab slug")


@needs_lab
def test_lab_trace_button_produces_steps(page):
    _open_lab(page)
    _click(page, "#lab-run")
    page.wait_for_function(
        "Number(document.getElementById('lab-step-tot').textContent) > 0",
        timeout=60_000,
    )


@needs_lab
@pytest.mark.parametrize(
    ("program", "message"),
    [
        # Python-level loop: the tracer's own 200,000-line limit stops it fast.
        ("while True:\n    pass\n", "executed lines"),
        # One C-level call, no line events: only the watchdog can end this.
        ("total = sum(range(10**13))\n", "Time limit exceeded"),
    ],
)
def test_lab_runaway_program_is_stopped_and_the_page_stays_alive(
    page, program, message
):
    _open_lab(page)
    page.evaluate(HEARTBEAT)
    _set_lab_code(page, program)
    _click(page, "#lab-run")
    page.wait_for_timeout(2000)
    assert page.evaluate("window.__ticks") > 10, "main thread was blocked"
    page.wait_for_function(
        "(m) => document.getElementById('lab-status').textContent.includes(m)",
        arg=message,
        timeout=20_000,
    )
    # Still usable afterwards (after a kill the worker has restarted).
    _set_lab_code(page, "x = 1\ny = x + 1\n")
    page.wait_for_function("!document.getElementById('lab-run').disabled")
    _click(page, "#lab-run")
    page.wait_for_function(
        "document.getElementById('lab-status').textContent.includes('steps')",
        timeout=BOOT_MS,
    )


NOTEBOOK_DOM = """
<div data-notebook id="nb"><span data-notebook-status></span>
  <button data-notebook-run>Run</button>
  <div data-cell data-cell-type="code"><pre data-cell-source></pre>
    <pre data-cell-out class="hidden"></pre></div>
</div>"""


def test_lesson_notebook_cell_that_never_ends_is_stopped(page):
    """notebook.js is the real file; the DOM is injected into the problem page (which
    ships the notebook runner's Python), so no lesson fixture is needed."""
    _open_problem(page)
    page.evaluate(HEARTBEAT)
    page.evaluate(
        "(h) => document.body.insertAdjacentHTML('beforeend', h)", NOTEBOOK_DOM
    )
    page.add_script_tag(url=f"{BASE}/static/lms/js/notebook.js")
    page.wait_for_function(
        "document.querySelector('[data-notebook-status]').textContent === 'Ready'",
    )

    def run(source):
        page.evaluate(
            "(s) => { document.querySelector('[data-cell-source]').textContent = s; }",
            source,
        )
        _click(page, "[data-notebook-run]")

    run("while True:\n    pass\n")
    page.wait_for_timeout(2000)
    assert page.evaluate("window.__ticks") > 10, "main thread was blocked"
    page.wait_for_function(
        "document.querySelector('[data-notebook-status]').textContent"
        ".includes('Time limit exceeded')",
        timeout=25_000,
    )
    page.wait_for_function("!document.querySelector('[data-notebook-run]').disabled")
    run("print(1 + 2)")
    page.wait_for_function(
        "document.querySelector('[data-cell-out]').textContent.trim() === '3'",
        timeout=BOOT_MS,
    )
