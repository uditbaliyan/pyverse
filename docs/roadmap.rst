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
section keeps the URL shape stable for the frozen export.

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
   with the line-trace and memory-graph views of a single step stream.
3. **LMS learner progress.** ``CoursePage``/``LessonPage`` already publish
   ``window.__LESSON_SLUGS__`` and ``window.__CURRENT_LESSON__``; wire lesson
   completion into the same ``PyverseProgress`` IndexedDB store the practice
   surfaces read, rather than a second store.
4. **Content and deployment.** Every remaining surface is bottlenecked on
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
- Two styling systems coexist (built Tailwind for LMS/base, the marketing shell
  on the Tailwind CDN, plus the practice engine's own tokens). Pick one before
  adding the next surface.
- CDN runtime dependencies (PyScript, Tailwind CDN, CodeMirror, Mermaid, lucide,
  Alpine, Google Fonts) mean offline visitors get a rendered-but-dead challenge
  page. Self-hosting is the fix if that matters.
