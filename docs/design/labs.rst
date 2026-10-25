Labs
====

Aim / use case
--------------

A learner should be able to watch a short Python program execute — line by line,
with variables changing, and with the shape of memory visible (which names share
which object). This is the "understand what the code actually does" surface,
distinct from Practice (graded exercises) and Learn (guided lessons).

Design
------

One tracer, two renderers
~~~~~~~~~~~~~~~~~~~~~~~~~

A lab is **one page** with a rendering-mode toggle, not two separate labs. Both
modes read the same step stream:

* ``line`` — source lines with executed/current marking, the variables at each
  step, stdout, and a step timeline.
* ``memory`` — the same value nodes drawn as a Graphviz record diagram, with
  references following ``oid``.

The split of responsibility:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Piece
     - Role
   * - ``templates/includes/tracer_runtime.html``
     - The Python side. ``sys.settrace`` inside PyScript, exposed as
       ``window._pvTrace()`` returning one JSON string. Records; does not render.
   * - ``static/js/lab-engine.js``
     - The rendering and transport side. One IIFE: CodeMirror 5 editor, step
       transport, both renderers, keyboard shortcuts.
   * - ``includes/tracer_runtime.html`` (PyScript)
     - Pinned to **2025.7.3**, the same version as the grading harness. "Do not
       add a second runtime tag — a page includes one of the two partials, never
       both."

The runtime contract
~~~~~~~~~~~~~~~~~~~~

``window._pvTrace()`` returns JSON:

.. code-block:: text

   {steps, stdout, error, error_line, truncated, source}

Each step is ``{line, fn, depth, out, vars, returned?}``:

* ``line`` — ``frame.f_lineno``.
* ``fn`` — ``frame.f_code.co_name`` (the function the line belongs to).
* ``depth`` — call-stack depth, tracked by ``call``/``return`` events.
* ``out`` — how many characters of ``stdout`` had been printed by that step, so
  the line view can show output only up to the current step.
* ``vars`` — visible locals mapped to JSON-safe value nodes.
* ``returned`` — the return value, attached to the function's last executed
  line ("so a return is visible without inventing an extra step").

Value nodes are JSON-safe projections of Python values. Each is an object whose
``k`` (kind) is one of ``int``, ``float``, ``bool``, ``str``, ``none``, ``seq``,
``dict``, ``obj``, ``cycle``, ``deep`` or ``other``. Containers and objects
carry ``oid`` (the CPython ``id()``), which is how the memory view knows two
names point at one object. **Primitives deliberately carry no ``oid``**: equal
small ints are interned, and drawing a shared node for two independent ``5``
values would lie.

Caps keep a runaway program from filling the bridge with JSON:
``_STEP_CAP = 400`` (with a ``truncated`` flag), ``_ITEM_CAP = 25``,
``_ATTR_CAP = 20``, ``_DEPTH_CAP = 3``, ``_STR_CAP = 28``.

Why ``sys.settrace``
~~~~~~~~~~~~~~~~~~~~

The prototypes in ``neetcode/pytutor_with_pyscript/`` (``pyvis_v8_1.html``,
``pyvis_mg.html``) inject AST probes before statements. That approach has two
consequences the dev log calls out:

* a loop body records **once per loop**, not once per iteration;
* a function's own body is **never probed**;
* ``pyvis_v8_1`` additionally marks *every* line above the current one as
  executed.

``sys.settrace`` gives real per-line events per iteration, real call depth and
real return values. The dev log records the observed difference: ``two_sum``
records 12 steps, ``seen`` grows on each pass, and the return step reads
``↩ returns [0, 1]``.

Two details make the tracer safe:

* Frames are filtered by ``co_filename`` (``_FILE = "<lab>"``), so serialising
  inside the trace callback cannot recurse into the tracer.
* ``sys.settrace(None)`` runs in a ``finally`` even when the learner's code
  raises.

Memory view: DOT built in JS, not a wheel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pyvis_mg`` micropip-installs an **unpinned** ``memory-graph`` wheel at page
load and precomputes up to 500 DOT strings. The port instead builds DOT in JS
from the tracer's own value nodes, for the **current step only**: no extra wheel,
no unpinned dependency, no payload for steps nobody opens. ``@viz-js/viz``
3.11.0 is fetched only when the memory view is first opened, so a line-trace
reader never pays for the WASM download.

``oid`` is emitted for containers and objects only, so two independent ``5``
values are never drawn as one shared box. The aliasing lab's point is exactly this: in
the memory view ``a`` and ``b`` point at one object while ``c[0]`` still shares
``a[0]`` and ``d`` is detached.

Other deliberate departures from the prototypes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* CodeMirror 6 from esm.sh is replaced by the **CodeMirror 5** build every other
  engine surface already loads.
* The canvas memory diagram is dropped — viz-js is the memory renderer, the line
  view is the other.
* Keyboard shortcuts are bound to the lab root element, not ``document``, so
  they do not fire on unrelated pages (and do not fight other surfaces' keys).

Page model
~~~~~~~~~~

``pyverse/labs/models.py``:

* ``LabsIndexPage`` — ``/labs/``, ``max_count = 1``. Lists ``LabPage`` children.
* ``LabPage`` — ``/labs/<slug>/``. Fields: ``summary`` (doubles as the meta
  description via ``seo._DESCRIPTION_ATTRS``), ``code`` (the program, a plain
  ``TextField`` baked into the page), ``what_to_watch`` (StreamField of
  observations), ``default_mode`` (line / memory), ``difficulty``
  (``taxonomy.Difficulty``), ``estimated_minutes``.

Top level, under Home — not under Practice or Learn: "a lab is neither a graded
exercise nor a guided lesson, and its URL shape is frozen into the static export
(``docs/roadmap.rst``)."

SEO: labs are pages, so ``seo.live_pages()`` and ``LivePageSitemap`` pick them
up with no freeze work. ``seo._json_ld`` gained a ``LabPage`` branch emitting
``LearningResource`` with ``"learningResourceType": "interactive lab"``.

**Discrepancy worth knowing:** ``docs/roadmap.rst`` describes labs as having
"its own sitemap bucket." The implementation does not create one — ``SITEMAPS``
in ``seo.py`` holds only ``pages`` / ``problems`` / ``quizzes``, and labs ride
the ``pages`` sitemap because they are Wagtail pages. The roadmap statement is
either loose phrasing or was written against an intended-but-unbuilt split; the
code is the accurate description.

Alternatives considered
-----------------------

*Two separate labs (a line lab and a memory lab).* Rejected in
``docs/roadmap.rst``: the tracer "merges the two PyTutor prototypes into one
``LabPage`` with a rendering mode toggle … not two separate labs." One step
stream, two views.

*AST-probe instrumentation (the prototypes' approach).* Rejected on accuracy
grounds — see above. It cannot show per-iteration loop state or function-body
execution, which is most of the value of a tracer.

*The ``memory-graph`` wheel (the prototype's memory view).* Rejected: unpinned
dependency, extra micropip install at load, and 500 precomputed DOT strings for
steps the learner never opens. Building DOT from the tracer's own nodes for the
current step only is smaller and has no third-party runtime.

*PyTutor's server-side visualisation.* Rejected — it needs a server, which the
static export forbids. The whole tracer runs in the browser.

*Canvas-based memory diagram.* Dropped mid-port in favour of viz-js; the dev log
records it as one of three deliberate departures.

Trade-offs accepted
-------------------

*Pyodide dependency.* Pyodide 0.27.7 is vendored under ``static/vendor/``
(``utility/vendor_assets.py``) and runs in a Web Worker with a wall-clock
watchdog (``static/js/pyverse-runtime.js``), so a CDN outage or ``while True``
cannot take the page down. Offline, pages render and the runtime still loads
from the site's own files.

*400-step cap.* A long-running program is truncated at 400 steps with a flag.
Honest, but a learner tracing a 10,000-iteration loop sees only the beginning.

*Depth/item/attr caps.* Nested structures are shown to depth 3, 25 items, 20
attributes. Deep or wide data renders as ``deep``/``cycle`` markers rather than
the full object. Necessary to keep each step's JSON small; it does mean the
memory view is a sketch, not a full object dump.

*One more hand-rolled engine.* ``lab-engine.js`` is 675 lines of bespoke
rendering. It duplicates concerns the other engines have (CodeMirror setup,
transport controls) rather than sharing them. The dev log frames the trade the
other way — one console pattern across Practice and Labs — but the JS itself is
not shared.

When to revisit
---------------

* If a learner needs to trace programs longer than 400 steps, or data wider than
  the caps allow. The caps are constants in ``tracer_runtime.html``; raising them
  trades bridge payload for fidelity.
* If a third rendering mode is wanted (e.g. a call-stack view). The contract is
  "one tracer, N renderers", and the step stream already carries ``depth`` and
  ``fn``.
* If the Pyodide pin moves, re-run ``utility/vendor_assets.py`` and the e2e
  suite (``pytest -m e2e``); the pin lives in that script, not in templates.


Two surfaces, one tracer
------------------------

*Labs* are **free-run playgrounds** (tracer today; pandas, numpy and other
libraries later): paste anything, run it, nothing is graded and nothing is tied
to a problem. *Watch it execute* is a panel **on the Practice problem page**
(``includes/trace_panel.html`` → ``tutor-view.js``, fed by
``problem-trace.js``). It traces the learner's own code or the reference
solution on one example, on the same page. There is deliberately no
``LabPage``-per-problem link: the loop never leaves the problem page.

Teaching layer on the problem-page trace (increment C)
------------------------------------------------------

The tracer shows *what* happens; C adds *why*. Both C1 and C2 are optional
authoring features on ``CodingProblem`` and only apply while the reference
solution is being traced (they describe that code, not the learner's).

C1 — step notes
~~~~~~~~~~~~~~~

* **Authoring.** New StreamField ``trace_notes`` (migration ``coding.0008``),
  each item ``{line, note, every_visit}``. ``line`` is 1-based in
  ``solution_code``; ``note`` ≤ 240 chars; ``every_visit`` false = show on the
  first visit to that line only.
* **Line mapping.** The traced program is ``solution_code`` plus an appended call
  harness, so reference line numbers equal tracer ``step.line`` for every line
  before ``harness_from``. No remapping.
* **Payload.** ``{{ notes|json_script:"pyverse-trace-notes" }}``, emitted only
  when ``solution_code`` and a trace case exist. No runtime fetch.
* **Rendering.** ``problem-trace.js`` hands the list to the viewer; the viewer
  writes the matching note into the existing ``#tv-note`` slot with
  ``textContent`` (never ``innerHTML``), and ``#tv-status`` stays the
  ``aria-live`` announcement of the step. When stepping back, the note for the
  step shown is recomputed from step history, so "first visit" is stable.
* **Validation.** ``clean()`` rejects a ``line`` beyond ``solution_code``'s
  length; ``check_problem_traces`` *warns* on a note whose line the shown example
  never executes (the note would be dead).
* **Only for the pinned call.** Notes describe one specific example, so
  ``problem-trace.js`` passes them to the viewer only when the *reference*
  solution is traced on exactly the pinned ``trace_case`` arguments. Tracing the
  learner's code, or editing the call, shows no notes (the note would be wrong).
  Hence ``trace_annotations`` is ``None`` unless ``trace_case`` is pinned.
* **Not doing.** Markdown/HTML in notes, per-learner notes, notes on the
  learner's own code.

C2 — prediction prompts
~~~~~~~~~~~~~~~~~~~~~~~

* **Authoring.** StreamField ``trace_predictions`` (same migration), each item
  ``{line, question, answer}``.
* **Behaviour.** On the step where ``line`` is about to run for the first time
  (the viewer's "runs next" arrow), a card shows the question and a *Reveal
  answer* button. It never blocks the transport controls (a keyboard or
  impatient learner can always keep stepping); revealing is the only state. The
  card is derived from the current step, so stepping back to that step shows it
  again. Focus is **not** moved (that would break ←/→ stepping); the card sits
  in an ``aria-live="polite"`` region and its button is a normal Tab stop.
* **Persistence.** ``pyverse-progress.js`` is an IndexedDB store keyed by problem
  ``slug`` and records submissions; predictions are not progress truth, so no
  schema bump (v3). Reuse its keying only: ``localStorage`` key
  ``pyverse:predict:<slug>`` → JSON list of revealed prediction indexes, wrapped
  in ``try/catch`` (private mode ⇒ simply not remembered). Nothing leaves the
  browser.
* **Not doing.** Scoring typed answers, streaks or XP (the progress module's
  streak is existing behaviour, not extended here).

C3 — compare with your attempt (already shipped, to be verified)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because the trace lives on the problem page, code never travels between pages:
the *your code* / *reference solution* toggle and the *Watch your code run on
it* button after a failed submission read the live editor (``#editor-ta``) and
call ``PyverseRuntime.trace(code, fn, args)`` directly. The ``location.hash``
design is therefore dropped; there is no URL-size limit to handle. Remaining
work is a test for the failed-submission path (currently unverified; the
passing-run path is covered by ``test_a_passing_run_offers_a_trace_that_steps``).

Tests (``pyverse/tests/test_trace_annotations.py`` + one e2e)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Payload building (omitted without a solution, a pinned case, or any authored
item), ``clean()`` bounds, ``check_problem_traces`` warnings (a note on a line
the example never runs; annotations authored with no pinned example), the page
bakes ``pyverse-trace-annotations`` only when there is something to show, a
``</script>`` in authored text cannot escape ``json_script``, and the viewer
writes authored text with ``textContent`` only. The e2e test drives the real
viewer: note shown as text (not markup), reveal, persistence key, annotations
off.

Not tested: screen-reader output of the live regions (no AT available here);
keyboard flow was reasoned from the markup (Tab reaches the button, ←/→ still
step) and the e2e DOM checks, not exercised with a real keyboard-only session.
