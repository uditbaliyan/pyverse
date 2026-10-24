Page tree / course model
========================

Aim / use case
--------------

The guided LMS needs a navigable structure: a Learn hub, subject-level Topics,
courses within a topic, and ordered lessons within a course. The tree must be
editable in Wagtail, constrain what can be created where (so an editor cannot
put a Lesson under Home), and produce stable URLs that the static export can
freeze. A lesson must also be able to hold everything a lesson is — prose,
examples, and now graded practice and a runnable notebook — without the tree
growing a page type per content shape.

Design
------

The tree
~~~~~~~~

Every page type declares ``parent_page_types`` and ``subpage_types``; Wagtail
enforces the shape in the admin.

.. code-block:: text

   Home (home.HomePage, max_count=1)
   ├── Learn        (lms.LMSIndexPage, max_count=1)
   │   └── Topic    (lms.TopicPage)
   │       └── Course    (lms.CoursePage)
   │           └── Lesson (lms.LessonPage)
   ├── Practice     (topics.PracticeHubPage, max_count=1)
   │   ├── Topic    (topics.PracticeTopicPage — nestable)
   │   └── Sheets   (topics.SheetsIndexPage, max_count=1)
   │       └── Sheet (topics.SheetPage)
   ├── Labs         (labs.LabsIndexPage, max_count=1)
   │   └── Lab      (labs.LabPage)
   ├── Python       (puput.BlogFolderPage, max_count=1)
   │   └── Notes    (puput.BlogPage)
   │       └── Entry (puput.EntryPage)
   └── Standard     (home.StandardPage — unlimited; About, Privacy, Terms …)

The LMS chain specifically:

* ``LMSIndexPage`` — ``/learn/``, one per site. Lists topics and featured
  courses.
* ``TopicPage`` — a subject ("Arrays & Hashing"). Carries ``icon``, ``color``,
  ``description`` and ``display_order``; orders by ``display_order, title``.
  Filters its course grid by ``?difficulty=``, ``?type=``, ``?free=1`` with
  server-side pagination (12 per page).
* ``CoursePage`` — one course. ``course_type`` and ``difficulty`` discriminate;
  ``ordered_lessons()`` returns ``LessonPage.objects.child_of(self).live()
  .order_by("path")`` — treebeard path order, i.e. the order the editor arranged
  them. ``lesson_count`` is cached on the instance, and card grids fill it from
  one batched query rather than one ``COUNT`` per card (see "Lesson counts on a
  grid of cards").
* ``LessonPage`` — one lesson. ``body`` is a StreamField of ``text`` / ``video``
  / ``code_example`` / ``callout`` / ``image`` / ``mermaid`` / ``notebook`` /
  ``practice`` blocks. ``prev`` / ``next`` navigation is computed from sibling
  order.

``course_type`` and ``difficulty``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``CourseType`` (``lms/models.py``):

* ``course`` — Standard Course
* ``micro`` — Micro-course
* ``workshop`` — Workshop

``DifficultyLevel``:

* ``beginner`` / ``intermediate`` / ``advanced`` / ``all_levels``

These are two different axes on purpose: ``course_type`` says what *shape* the
course is, ``difficulty`` says how advanced it is. ``CoursePage.difficulty``
uses ``DifficultyLevel``, **not** ``pyverse.taxonomy.Difficulty`` (Easy / Medium
/ Hard) — the latter tags a single exercise; the former describes a whole
course. The distinction is documented in the ``taxonomy.py`` docstring.

``site_difficulty`` is the one sanctioned bridge between the two vocabularies:
``_COURSE_TO_SITE_DIFFICULTY`` in ``lms/models.py`` maps ``beginner`` /
``intermediate`` / ``advanced`` onto ``taxonomy.Difficulty`` and ``all_levels``
onto ``None`` (an "any level" course has no site-wide equivalent, and a wrong
guess would be worse than an absent value). Nothing consumes it yet — it exists
so that a future cross-surface comparison ("easy practice inside this course")
reads one table instead of comparing ``CoursePage.difficulty`` with
``taxonomy.Difficulty`` field-to-field, which is a silent category error.

Lesson body blocks: ``practice`` and ``notebook``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``LessonPage.body`` ended at prose — text, video, code, callout, image, mermaid
— so a lesson could not carry graded practice and could not carry a runnable
notebook. Two blocks close that gap; both live in ``lms/models.py``, because a
block only one app renders carries that app's template with it.

``practice`` (``PracticeBlock``)
    A ``SnippetChooserBlock`` for ``coding.CodingProblem`` **and** one for
    ``quiz.Quiz``, plus ``required_to_advance``. Exactly one of the two choosers
    must be set: ``StructBlock`` has no native "exactly one of", so
    ``PracticeBlock.clean()`` raises ``blocks.StructBlockValidationError`` keyed
    on ``problem`` when both or neither are filled. Renders
    ``templates/lms/blocks/practice_embed.html``.

    The chooser targets are the snippets the practice surfaces already serve —
    "a problem page" is a route on a snippet, not a page (see ``labs.rst``'s
    sibling note and the Wagtail notes on ``RoutablePageMixin``), so a checkpoint
    references the same object rather than duplicating it. The block renders the
    target's slug into ``data-checkpoint-slug``; that slug is the identity the
    challenge and quiz pages write into ``problem_status``, which is what makes
    the checkpoint tick and the next-lesson gate work (``progress-tracking.rst``).

``notebook`` (``NotebookBlock`` → ``ListBlock(NotebookCellBlock)``)
    Cells are ``code`` (the default) or ``markdown``, each with a plain
    ``source`` TextBlock. Markdown is rendered server-side by
    ``wagtailmarkdown``; code cells travel in the DOM and are executed in the
    learner's browser by ``static/lms/js/notebook.js`` on the shared PyScript
    runtime (``grading-engine.rst``). Renders
    ``templates/lms/blocks/notebook.html``.

    Cell sources live in the rendered DOM (``[data-cell-source]``) rather than in
    a ``json_script`` element: a lesson can hold more than one notebook, and a
    single hardcoded payload element id would collide. The same reasoning that
    keeps one PyScript include per *page* also keeps one payload per *notebook* —
    there is no page-level notebook payload at all.

``LessonPage.get_context`` sets ``has_notebook`` (any ``notebook`` block in the
body) and ``lesson_page.html`` includes ``includes/pyscript_runtime.html`` only
when it is true: the partial's own header forbids including it twice on a page,
and a lesson without a notebook should not pay for a multi-megabyte Pyodide
download it never uses.

Resolving the choosers is batched, not per block
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wagtail resolves a stream's chooser children itself: ``StreamValue`` prefetches
each block *type* it is asked for via the child block's ``bulk_to_python``, which
for a ``ChooserBlock`` is one ``in_bulk`` query for every pk of that field in the
stream. So a lesson costs one query per chooser field *in use*, never one per
checkpoint. Measured (2026-09-26) over ``[block.value for block in lesson.body]``
inside a ``CaptureQueriesContext``:

.. list-table::
   :header-rows: 1
   :widths: 46 12 42

   * - Lesson body
     - Queries
     - SQL
   * - one ``practice`` (problem)
     - 1
     - ``coding_codingproblem WHERE id IN (…)``
   * - two checkpoints (problem + quiz)
     - 2
     - one per chooser field
   * - three checkpoints (2 problems + 1 quiz)
     - 2
     - both problems in a single ``IN (…)``

The templates therefore do **not** build a ``practice_problems_by_pk`` context
dict, a pk-collecting scanner, or a ``get_item`` filter. They would duplicate
work Wagtail already does, and a ``get_item:value.problem`` lookup would be a
dictionary lookup by pk against an already-resolved object.

Lesson counts on a grid of cards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``templates/lms/components/course_card.html`` prints ``{{ course.lesson_count }}
lessons``, so a grid of course cards needs one count per card. There is **no
ForeignKey** from a lesson to its course — a lesson is a Wagtail page whose
parent is the course, and that relationship exists only in the treebeard
``path`` — so neither ``annotate(Count(...))`` nor ``prefetch_related`` can see
it, and the naive implementation costs one ``COUNT`` per card.

``lms/utils.py`` holds the batch instead:

* ``lesson_counts_for(container, courses)`` runs **one** query —
  ``LessonPage.objects.descendant_of(container).live().values_list("path",
  flat=True)`` — and buckets each path under its parent course by truncating one
  treebeard segment (``path[:-Page.steplen]``). Wagtail paths are fixed-width
  segments, so a lesson's parent path is exactly its own path minus one segment;
  the map is ``{course pk: count}``, with ``0`` for courses that have no live
  lessons.
* The grid calls ``CoursePage.set_lesson_count()`` for each card before render.
  ``lesson_count`` stays a plain property that falls back to
  ``ordered_lessons().count()`` when nothing filled it: a single-course page
  keeps working with no plumbing, and a grid that forgets to fill the cache is
  correct-but-slower rather than wrong.
* Both grids are wired: ``TopicPage.get_context`` (the course grid, 12 per page)
  and ``LMSIndexPage.get_context`` (the up-to-six featured courses).

``container`` is the page the grid's courses hang under — the ``TopicPage``
itself for the topic grid, the ``LMSIndexPage`` for featured courses — so the
query counts lessons under every course in that subtree, which is exactly what
the grid wants.

While wiring this, one pre-existing bug fell out:
``templates/lms/course_page.html``'s sidebar printed ``{{ lesson_count }}``, a
name ``CoursePage.get_context`` never set, so the "Lessons" row rendered blank.
It now prints ``{{ lessons|length }}`` — already in that context, and already
evaluated for the lesson list, so it costs no extra query.

``is_free``
~~~~~~~~~~~

``CoursePage.is_free`` defaults to ``True``. The comment in ``models.py`` states
the reason: "PyVerse has no paywall: this only drives the 'Free' badge and JSON-LD
``isAccessibleForFree``, so it defaults on for every course." It stays as a field
because it feeds the badge and structured data, not because an entitlement system
exists (``docs/roadmap.rst``: "There is no entitlement system and no plan to
build one").

The earlier 3-subclass design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An earlier design represented the three ``course_type`` values as three separate
page models (a standard-course page, a micro-course page, a workshop page),
which was built and then reverted to the single ``CoursePage`` with a
``course_type`` discriminator field.

**This reversal is documented in the build spec
(``pyverse-requirements-v2.md``), which is not in this repository.** Within the
repository there is no trace of the three-subclass version: no such model, no
migration creating or dropping one, and no comment explaining the change. The
git history begins at the pre-DSA baseline (``525f2a3``), which already contains
the single ``CoursePage`` with ``course_type``. An exhaustive search of the
history for ``MicroCourse`` / ``WorkshopPage`` returns nothing. The surviving
evidence of the reversal is the three-value ``CourseType`` enum on a single
model — the vocabulary outlived the model split.

Therefore the *why* cannot be sourced here; it must be read from the external
spec. What can be said from the code is only the end state and its consequences
(see Trade-offs).

Alternatives considered
-----------------------

*Three page subclasses, one per ``course_type``.* This was built and reverted;
the rationale lives in the external spec (see above). What the current design
implies about the trade-off: subclasses give each course shape its own fields and
its own template without conditional branching, at the cost of three models,
three admin entry points, three sets of migrations, and cross-type queries that
must union three tables. A discriminator field keeps one model, one queryset, one
admin view — and forces any shape-specific difference into a conditional.

*Flat course list, no Topic level.* Rejected — ``TopicPage`` groups courses by
subject and drives the Learn hub's topic grid. Without it, ``/learn/`` would be
one long course list with no organising axis.

*Course-less lessons (a flat lesson library).* Rejected — the guided-path premise
is a course with ordered lessons and prev/next navigation.
``LessonPage.get_context`` computes ``lesson_index`` / ``total_lessons`` from
sibling order, which presupposes a course parent.

*Per-card ``COUNT`` on a course grid.* What ``{{ course.lesson_count }}``
did when a grid rendered it: each card evaluated its own ``ordered_lessons()
.count()``, so twelve cards cost twelve ``COUNT`` queries. Rejected in favour of
one descendant query over the grid's own container — and the saving was measured
rather than assumed (the query table above).

*Plumbing the practice choosers through the request context.* A
``practice_problems_by_pk`` dict, a pk-collecting scanner over the body, and a
``get_item`` filter were all on the table for rendering checkpoints. Rejected:
Wagtail already resolves a stream's chooser children in one batched query per
chooser field (``StreamValue._prefetch_blocks`` →
``ChooserBlock.bulk_to_python``), so a context dict would resolve the same objects
a second time, and ``get_item:value.problem`` would look up by pk in a dict for an
object the template already holds.

Trade-offs accepted
-------------------

*One ``CoursePage`` with conditional fields.* Any difference between a standard
course, a micro-course and a workshop has to be expressed as conditional logic
on the single model (``course_type`` in a template, a filter on a queryset)
rather than as a subclass override. The current site does not yet branch on
``course_type`` much — ``get_course_type_display`` is shown as a badge — so this
cost is latent rather than paid.

*``course_type`` values are schema, not data.* Adding a fourth kind of course
means a code change and a migration, unlike the taggit axes on ``CodingProblem``.
That is the accepted cost of a deliberate, small vocabulary.

*``max_count = 1`` singletons.* ``LMSIndexPage``, ``PracticeHubPage``,
``SheetsIndexPage``, ``LabsIndexPage`` and ``BlogFolderPage`` are all singletons.
This keeps URL shapes stable (``/learn/``, ``/practice/``) and the static export
predictable, at the cost of inflexibility — a second Learn hub is impossible
without a code change.

*A lesson body can pair a block with the wrong surface.* Nothing constrains a
``practice`` block to a problem the lesson actually teaches, or a ``notebook`` to
a lesson whose subject is programming. The block's only rule is its own
(``practice``: exactly one target; ``notebook``: at least the cells it was given).
Per-lesson allowed-block sets would be more machinery than the corpus justifies
while one person authors every lesson.

*``PracticeBlock.clean()`` runs on validated saves only.* It fires in the admin
and under ``full_clean()``; a body assigned from a script or a data migration can
carry both choosers, or neither, and the template then renders whichever side is
truthy (both-set renders the problem, since ``{% if value.problem %}`` is tested
first). The two malformed shapes are visible on the page — an empty title slot —
but the invariant is not enforced at the database level.

*Lesson counts are per request.* ``lesson_counts_for`` runs on every grid render,
with no cache beyond the instance attribute: one extra query per grid, traded
against zero staleness. It also assumes a lesson's parent is always the course —
true only because ``CoursePage.subpage_types`` is exactly
``["lms.LessonPage"]``; a lesson nested one level deeper would be missed by the
one-segment path truncation.

When to revisit
---------------

* If the three course shapes diverge enough that ``CoursePage`` accumulates
  per-type conditionals. The subclass split would then be reconsidered — with
  the reversal's original reasoning in hand, since it presumably weighed exactly
  this cost.
* If the page-count cap at the current corpus (1 course, 2 lessons) actually
  gets exercised — the current tree has never been stressed with dozens of
  courses per topic, and the admin ergonomics or the ``path``-ordered lesson
  navigation may not hold up at that scale.
* If ``_site/`` deploy reveals that the ``BlogFolderPage`` / ``BlogPage`` split
  (both singletons, one folder holding one blog) is over-structured. It is a
  two-page indirection that exists to lock the tree shape.
* If a surface needs lesson counts without a container to scope the query — a
  global course search, a sitemap summary — ``lesson_counts_for`` has nothing to
  batch against, and a stored counter on ``CoursePage`` starts to be worth its
  write path on every publish, unpublish and move.
* If a lesson can ever nest under something other than a course. The
  one-segment ``path`` truncation is only correct while
  ``CoursePage.subpage_types == ["lms.LessonPage"]`` holds; otherwise the
  bucketing has to walk the tree.
* If checkpoints must block progress instead of nudging it.
  ``required_to_advance`` is already the flag; enforcing it needs a server
  (``progress-tracking.rst``).
* If notebooks become editable, or a learner's cells must persist, the notebook
  stops being a lesson-body block and becomes a surface with its own store — the
  same shape ``labs`` chose when a program became a page field.
