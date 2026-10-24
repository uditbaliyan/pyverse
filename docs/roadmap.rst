PyVerse roadmap
===============

Decisions and the order they imply. Anything not listed here is either already
shipped (see ``DEVLOG.md``) or not yet decided.

Decided
-------

**Labs are reinstated as an active surface.** Labs are the next feature after
the DSA slice, ahead of more problems/quizzes/courses. The execution + memory
tracer merges the two PyTutor prototypes into one ``LabPage`` with a rendering
mode toggle — a line-trace view (``pyvis_v8_1.html``) and a memory-graph view
(``pyvis_mg.html``) — not two separate labs. **Shipped** as ``pyverse/labs/``:
one ``sys.settrace`` tracer behind both views, so the line view sees every
iteration and real call depth, and the memory view builds its DOT from the
tracer's own value nodes instead of the prototypes' unpinned ``memory-graph``
wheel.

**Labs live at the top level, not under Practice or Learn.** Their own section
under Home (``/labs/<slug>/``), with its own nav entry and its own sitemap
bucket. Labs are neither graded practice nor a guided lesson, so neither
``PracticeHubPage`` nor ``LMSIndexPage`` is a natural parent, and a top-level
section keeps the URL shape stable for the frozen export. They render in the
site's own shell (``home/base_.html``), not the dark engine shell, so the
section looks like the rest of PyVerse; only the tracer console inside is dark.

**Flashcards stay on the roadmap but not in this phase.** The prototype
(``neetcode/pyverse-flashcards.html``) is a later surface; the tracer lab comes
first. No flashcard models or templates exist in the project yet.

**Every course is free.** ``CoursePage.is_free`` keeps existing as the switch
behind the "Free" badge and the JSON-LD ``isAccessibleForFree`` value, but it
defaults to ``True`` (``lms/migrations/0003``). There is no entitlement system
and no plan to build one.

**One blog engine: vendored puput.** The earlier ``wagtail-code-blog``
recommendation is superseded; puput is vendored and working, so no second engine
goes on top of it.

Order
-----

1. **Dead code.** Orphaned quiz blocks and their templates, the ``quiz``/``lms``
   URL modules, the stale ``lms/wagtail_hooks.py``, the unloaded lucide markup
   and the junk redirect rows are all gone; the puput canonical-URL fix is
   committed with them.
2. **Tracer lab.** Shipped: ``/labs/`` plus one lab page per traced program,
   with the line-trace and memory-graph views of a single step stream. Practice
   was re-skinned at the same time: every Practice page now uses the site shell
   with its engine inside a ``.pe-console`` frame, which supersedes spec §8's
   "Practice is its own dark product" as a *page chrome* decision — the engines
   themselves are still dark.
3. **LMS learner progress.** Shipped: lessons complete into the same
   ``PyverseProgress`` IndexedDB store the practice surfaces read (a
   ``lesson_status`` store in the same database, not a second store). The
   course page counts ticks and shows a progress bar; the lesson page offers
   mark-complete with an undo.
4. **Lesson checkpoints and notebooks.** Shipped: a lesson body can carry a
   graded ``practice`` checkpoint (one problem **or** one quiz, optionally
   ``required_to_advance``) and a ``notebook`` whose code cells run and print in
   the learner's browser on the existing PyScript runtime, with Markdown cells
   rendered server-side. A required checkpoint gates the next-lesson link until
   that slug reads ``solved`` in ``problem_status`` — a client-side nudge, not an
   entitlement check. Lesson counts on a course grid moved from one ``COUNT`` per
   card to one descendant query per grid.
5. **Content and deployment.** Every remaining surface is bottlenecked on
   corpus size (4 problems, 2 quizzes, 1 course, 2 lessons, 2 labs). Deploy the
   static export once the tree is clean — host still undecided.

Tag axes
--------

Difficulty and Topic are the baseline. ``Company``, ``Pattern`` and
``Technique`` through-models already exist on ``CodingProblem`` and ``Quiz``
(they were added with the DSA slice), so this is no longer a "do we add them"
question — it is a "when does the corpus justify filling them" question, and
filtered listing pages that combine them need canonical tags before they are
indexed.

Open
----

- Which host serves the export (real 301s vs. redirect stubs).
- Settled: the site shell (``home/base_.html``) is the theme for every
  learner-facing page — Practice and Labs included — and the engine's dark token
  set is used only inside ``.pe-console`` panels. Two Tailwind pipelines still
  ship (the built one for LMS/account pages, the CDN one for the shell); folding
  the first into the second is cleanup, not a decision. Worth knowing before a
  deploy: the built stylesheet is gitignored build output, so it has to be rebuilt
  (``manage.py tailwind build``) after new utility classes or the classes silently
  do nothing — the lesson checkpoint gate was unstyled until a rebuild.
- CDN runtime dependencies (PyScript, Tailwind CDN, CodeMirror, Mermaid, lucide,
  Alpine, Google Fonts) mean offline visitors get a rendered-but-dead challenge
  page. Self-hosting is the fix if that matters.
