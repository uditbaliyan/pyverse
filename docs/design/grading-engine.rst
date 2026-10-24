Grading engine
==============

Aim / use case
--------------

A ``CodingProblem`` needs grading — comparing a learner's function return value
against an authored expected output for each test case. The site is a static
export, so grading must execute entirely inside the learner's browser with no
server round-trip. The same comparison logic must also run server-side during AI
draft verification so a pass there predicts a pass in the browser.

Design
------

Comparator dispatch
~~~~~~~~~~~~~~~~~~~

``Comparator`` (``pyverse/coding/models.py``, ``TextChoices``) declares how a
return value is compared with a test case's expected output:

``exact``
    Python ``==`` equality — the default.
``sorted_list``
    ``sorted(actual) == sorted(expected)``. Handles order-independent lists
    (e.g. Two Sum may return ``[0, 1]`` or ``[1, 0]``). Falls back to repr-based
    comparison when elements are unorderable.
``float_tolerance``
    ``abs(actual - expected) <= 1e-6``, recursed into nested lists. Handles
    floating-point problems without requiring the learner to round.
``custom``
    User-supplied ``compare(actual, expected) -> bool``, exec'd in the
    learner's browser next to their own code. Source lives in
    ``custom_comparator_code``.

A single equality rule does not generalise across problems — the rationale is
stated in the ``Comparator`` docstring.

Client-side execution via Pyodide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All client-side Python — grading **and** lesson notebooks — runs in
``includes/pyscript_runtime.html``, pinned to PyScript **2025.7.3** (the version
the shared grader prototype ran on). One version for the whole site, never two:

* ``<link rel="stylesheet">`` + ``<script type="module">`` load Pyodide from
  ``pyscript.net``.
* ``<script type="py">`` defines the grading harness: ``_payload()``, ``_call()``,
  ``_matches()``, ``exec_solution()`` — and the notebook runner
  ``run_notebook()`` (see "The same include runs lesson notebooks").
* ``window._pyExec(isSubmit, customJson)`` is the grading bridge — returns a
  Python tuple ``(result_json, stdout_log)``.
* ``window._pyNotebook()`` is the notebook bridge — returns one JSON string.
  Grading and notebooks share the runtime, not a payload element.
* ``document.body.dataset.pyverseReady === "1"`` gates the Run/Submit buttons.
  Without Pyodide (offline, CDN down) the buttons stay disabled.

The payload contract (``#pyverse-payload``, emitted by ``json_script``):

.. code-block:: json

   {
     "fn": "two_sum",
     "comparator": "exact",
     "custom": "",
     "cases": [
       {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]", "hidden": false}
     ]
   }

``input`` is Python source for the argument list, evaluated in the learner's
namespace. ``expected`` is a Python literal, also evaluated — which is why it is
authored as source rather than split into typed fields. Hidden cases ship
``expected`` in the payload (see Trade-offs below).

Spec approach A: data baked into the page, no runtime fetch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``CodingProblem.grading_payload()`` returns the entire payload as a plain dict.
The problem page calls ``{{ payload|json_script:"pyverse-payload" }}`` at build
time. The grading harness reads it from ``#pyverse-payload``. There is no API
call, no ``fetch()``, no server — the page is its own data source.

This is spec "approach A". The alternative (approach B, fetch-on-load) would
need a running server or a second static file per problem.

The same include runs lesson notebooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``run_notebook()`` sits beside ``exec_solution()`` in the same
``<script type="py">``, exposed as ``window._pyNotebook()``. A lesson notebook is
a different job from grading — no test cases, no comparators, just "run these
cells in order and show me what they printed" — so it gets its own entry point
rather than a mode flag on ``_pyExec``:

* JS writes the cell list to ``window._pendingNotebook`` as ``{"cells":
  [{"type": "code", "source": "…"}]}`` and calls ``_pyNotebook()``. The two entry
  points never share a payload element: ``exec_solution`` reads
  ``#pyverse-payload`` (which a lesson page does not have), ``run_notebook`` reads
  the JS global.
* It returns one JSON string — ``{"cells": [{"stdout": "…", "error": "…"}],
  "ok": bool}`` — with one entry per cell **in cell order**, so the caller zips
  the outputs back onto the cells it rendered.
* Cells share one namespace per call, i.e. Run behaves like Jupyter's "Run All":
  a name bound in cell 1 is visible in cell 3. A *second* click starts from an
  empty namespace, so a run is idempotent instead of accumulating state.
* A cell that raises captures ``traceback.format_exc()`` into ``error`` and the
  runner keeps going; ``ok`` is ``false``. One broken cell does not hide the
  output of the others.
* ``sys.stdout`` is redirected per cell, so each cell's output is attributed to
  that cell rather than to the run.

Markdown cells never reach the runtime: ``templates/lms/blocks/notebook.html``
renders them server-side through ``wagtailmarkdown``'s ``markdown`` filter, and
``static/lms/js/notebook.js`` reads only ``[data-cell][data-cell-type="code"]``
from the DOM. So a lesson page needs no second Markdown renderer and no second CDN
dependency, and everything that crosses the bridge is code.

The DOM contract ``notebook.js`` keys off (stated in full at the top of that
file): ``[data-notebook]`` per notebook, ``[data-notebook-status]``,
``[data-notebook-run]``, and per code cell ``[data-cell-source]`` (read as
``textContent``) plus ``[data-cell-out]`` for the result. Sources are read at
click time, which is what lets a lesson hold several notebooks with no payload-id
collision (``page-tree.rst``). The runtime partial is not included by the block
template at all — ``lesson_page.html`` includes it once, and only when
``LessonPage.get_context`` reports ``has_notebook``.

Hidden test cases
~~~~~~~~~~~~~~~~~

Each test case carries ``is_hidden``. Hidden cases are:

* Still shipped in the payload (``expected`` included).
* Masked in the UI — the Run/Ad-hoc args dropdown only lists visible cases.
* Labelled ``<hidden case>`` in the grading log when they fail; a passing
  hidden case is silent.
* Counted in the total — the verdict is ``ACCEPTED`` iff every case (visible and
  hidden) passes.

The masking is cosmetic, not cryptographic: the ``expected`` value is in the
page source. This is the accepted cost of approach A client-side grading.

Three-tier hints
~~~~~~~~~~~~~~~~

``HintBlock.Tier``: ``nudge`` → ``approach`` → ``near-solution``, revealed one
at a time. The learner clicks to request each tier; earlier tiers must be shown
before later ones. Authored in StreamField on ``CodingProblem.hint_tiers``.

Verification
~~~~~~~~~~~~

``pyverse/ai_content/verify_runner.py`` mirrors the browser harness: same four
comparators, same "input is Python source for the argument list" convention,
same fallback to repr comparison. It is executed as a subprocess during AI
drafting (``manage.py ai_create``) so a generated solution that passes here is
expected to pass in a learner's browser. The code comment in ``verify_runner.py``
says "reading the two side by side is the point" — the harness and the verifier
share the same structure deliberately.

Alternatives considered
-----------------------

*Server-side grading.* The obvious alternative. Rejected because it requires a
running server and an execution sandbox (or a third-party grading API), both of
which lose the static-site property. The project's core premise is "no server,
no hosting cost, no execution risk on our side."

*One equality function.* A single ``==`` check was insufficient. The
``Comparator`` docstring in ``coding/models.py`` explains: "Two Sum may return
its index pair in either order, float problems need an epsilon, and some answers
are only equal structurally."

*Fetch-at-runtime (approach B).* Would keep answers out of the page source but
needs either a server or a separate static file per problem. Approach A was
chosen for simplicity: one page is one file, the data is right there, and the
hidden-case exposure was deemed acceptable for MVP.

*A second runtime include for notebooks.* Rejected by the same rule the partial's
own header states for the tracer: one PyScript version for the whole site, pinned
in one file, and a page includes the partial once. A notebook is a lesson-body
block, so the lesson page — which includes no other runtime — is where it lives.

*A ``json_script`` payload for the notebook cells.* Rejected: a payload element
needs one id per notebook and a lesson may hold several notebooks. Reading cell
sources out of the rendered DOM removes the id from the problem instead of
parameterising it.

*Rendering notebook Markdown client-side.* Would add a second Markdown renderer
in the browser plus a second CDN dependency, for content ``wagtailmarkdown``
already renders server-side at build/freeze time.

*A mode flag on ``_pyExec`` instead of a second entry point.* Grading and notebook
execution share only ``compile``/``exec`` and a stdout capture; their payload
source, return shape and error policy all differ, so a flag would branch a
grading function that is otherwise entirely about test cases.

Trade-offs accepted
-------------------

*Hidden case answers are readable in page source.* A learner who inspects the
page can see every expected output. This is inherent to approach A client-side
grading. No fix is planned unless it becomes a real problem (see below).

*Pyodide is a multi-megabyte WASM download.* Without it (offline, blocked CDN)
the challenge page renders but Run/Submit never enable ("Python runtime failed
to load" after 45 s). Self-hosting Pyodide is the fix if that matters.

*No rate limiting, no anti-abuse.* The challenge page is a static file. A
learner can submit as many times as they want, can modify the page's JavaScript
to mark every case accepted, and can read the answers. There is no "correct"
verdict on the server to trust — the site's model is that the learner is grading
for their own benefit.

*Only one PyScript version for the whole site.* Pinned in
``includes/pyscript_runtime.html``. The same pin is used by
``includes/tracer_runtime.html`` — the Labs tracer shares the same runtime.
Extending one means testing both surfaces. The pin now has three consumers: the
grader (``_pyExec``), the tracer (``_pvTrace``) and the notebook runner
(``_pyNotebook``), which lives in the same file as the grader.

*A notebook traceback names the harness frame.* A failing cell reports
``File "<exec>", line N, in run_notebook`` above the learner's own frame, because
``run_notebook`` uses ``traceback.format_exc()`` exactly as ``exec_solution``
does. It is conspicuous; it is also consistent with the grader rather than
special-cased away.

*Run executes the whole notebook synchronously.* One click runs every cell on the
browser's main thread — no per-cell execution, no streaming output, and a
"Running…" label is the only progress signal (painted before the call, because the
Python side blocks the thread while it runs).

*45 s to a working runtime.* ``notebook.js`` stops waiting for
``dataset.pyverseReady`` after 45 s and leaves Run disabled with "Python runtime
failed to load" — the same deadline the grader's offline case reports. A cold
Pyodide download can exceed it: observed once on this machine, where the first
load of the page missed the window and the cached reload was ready in seconds.

When to revisit
---------------

If hidden-case answer exposure causes real problems (cheating in a context that
matters, e.g. a paid certification — the site has no such plans). The fix is
server-side grading, which loses the no-server property. The spec considered
this trade-off explicitly and chose approach A for MVP.

* If notebooks need per-cell execution, streaming output, or a learner-editable
  cell. The first two mean giving up the synchronous one-shot bridge; the third
  means an editor and a store, which is ``lab-engine.js``'s terrain, not the
  lesson body's.
* If the 45 s runtime window starts failing for real learners on slow or blocked
  connections. The constant lives in ``static/lms/js/notebook.js``
  (``waitForRuntime``); raising it or adding an explicit retry is a local change,
  but it applies to every Pyodide surface at once if it is shared.
* If PyScript is vendored or the pin moves, every entry point has to be
  re-verified: ``_pyExec`` and ``_pyNotebook`` in ``pyscript_runtime.html``,
  ``_pvTrace`` in ``tracer_runtime.html``.
