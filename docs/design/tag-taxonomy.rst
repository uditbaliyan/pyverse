Tag taxonomy
============

Aim / use case
--------------

Tag coding problems and quizzes along independent axes so learners can browse by
difficulty, filter by interview relevance (company, pattern), and see what
Python-level idioms a problem exercises. The taxonomy also drives ordering
(Tracks and the Landing default to difficulty ascending) and determines which
filter controls render on the Practice landing.

Design
------

The axes
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 16 20 34 30

   * - Axis
     - Kind
     - Applies to
     - Example values
   * - Difficulty
     - ``Difficulty`` ``TextChoices``
     - ``CodingProblem``, ``Quiz``, ``LabPage``
     - Easy / Medium / Hard
   * - Topic
     - ``ForeignKey`` to ``topics.PracticeTopicPage``
     - ``CodingProblem``, ``Quiz``
     - Arrays & Hashing → Two Pointers
   * - Company
     - taggit through-model (``ProblemCompany``)
     - ``CodingProblem``
     - Google, Amazon, Startup
   * - Pattern
     - taggit through-model (``ProblemPattern``)
     - ``CodingProblem``
     - Two Pointers, Sliding Window, DFS/BFS
   * - Technique
     - taggit through-model (``ProblemTechnique`` / ``QuizTechnique``)
     - ``CodingProblem``, ``Quiz``
     - Enumeration, Dict Comprehension

Shared difficulty vocabulary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pyverse/taxonomy.py`` holds ``Difficulty`` and is imported by ``coding``,
``quiz`` and ``labs``. The module docstring states the reason: spec §5 (§18
cross-cutting finding 2) fixes the difficulty vocabulary at Easy / Medium /
Hard, both ``coding`` and ``quiz`` author against it, and importing one content
app from the other would invert the dependency direction.

It also holds ``DIFFICULTY_RANK``, a ``Case``/``When`` expression:
``difficulty`` is stored as a string, so alphabetical ordering would give
Easy → Hard → Medium. The ranked expression gives Easy → Medium → Hard, which
every Practice surface wants (Tracks default to difficulty ascending, spec §4).

This is **not** the same axis as ``lms.DifficultyLevel`` (beginner /
intermediate / advanced / all-levels). That one describes how advanced a whole
course is; ``taxonomy.Difficulty`` tags a single exercise. The distinction is
called out in the ``taxonomy.py`` docstring.

Why taggit tags rather than choice fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The three browsing axes (Company, Pattern, Technique) are taggit tags, not
``TextChoices``. The comment in ``coding/models.py`` gives two reasons:

1. A problem genuinely carries several of each — a problem can be tagged both
   "Google" and "Amazon", both "Two Pointers" and "Sliding Window".
2. A closed vocabulary would need a migration per new pattern. new company, new
   technique → a new migration. Tags are data, not schema.

Each axis gets its own through-model (``ProblemCompany``, ``ProblemPattern``,
``ProblemTechnique``) because "taggit refuses two TaggableManagers sharing one,
and separate tables keep company/pattern/technique tags from being conflated in
queries." A tag named "Google" (company) and a tag named "Google" (pattern)
would otherwise be the same row.

``QuizTechnique`` is the same pattern on ``Quiz`` — Technique is the one axis
that spans both problems and quizzes (spec §5: "Technique covers quiz items").

Topic is not a tag
~~~~~~~~~~~~~~~~~~

``topic`` is a ``ForeignKey`` to ``topics.PracticeTopicPage``, not a tag. Topics
are Wagtail pages that nest to arbitrary depth ("Arrays" → "Two Pointers"), and
the page tree gives O(1) subtree aggregation via ``path__startswith``. A tag
cannot express a hierarchy or carry a URL.

``topic`` is also the de-facto publish switch: every learner-facing listing
filters on ``topic__isnull=False, topic__live=True``. A problem or quiz with no
topic is unreachable from any Track or the Landing — useful for drafts
(``manage.py ai_create`` creates problems with ``topic`` null and assigns it
during human review).

Conditional filter rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``PracticeHubPage.get_context()`` computes three option lists from the problems
that actually exist:

.. code-block:: python

   context["company_options"] = sorted(
       {name for problem in problems for name in problem.companies.names()},
   )
   context["pattern_options"] = sorted(
       {name for problem in problems for name in problem.patterns.names()},
   )
   context["technique_options"] = sorted(
       {name for problem in problems for name in problem.techniques.names()},
   )

The template (``topics/practice_hub_page.html``) wraps each filter block in
``{% if company_options %}`` / ``{% if pattern_options %}`` /
``{% if technique_options %}``. A filter dropdown is rendered **only** when at
least one problem carries a tag on that axis. Code comment: "Filter controls are
rendered only for axes that actually have values (spec §5 phasing: no empty
Company/Pattern/Technique dropdowns)."

This is the fix for the "empty filter" problem. The original phasing plan tried
to avoid a shipped empty Company dropdown by deferring the axis's introduction
until the corpus justified it. The through-models already existed on day one
(added with the DSA slice, commit ``794cb88``), so instead of phasing the schema
the fix became: render the control conditionally. The schema is always there;
the UI appears when there is data to filter.

Alternatives considered
-----------------------

*Choice fields for Company/Pattern/Technique.* Rejected in the
``coding/models.py`` comment: a problem carries several of each, and a closed
vocabulary needs a migration per new value.

*A single tag namespace with prefixes.* Rejected: would conflate axes in queries
and lose the through-model separation. Separate tables also let Company tags be
searched by company-only.

*Deferring the axes until after launch (original phasing plan).* Rejected in
favour of adding the through-models with the DSA slice, then rendering the
filter controls conditionally. The roadmap records the reframing: "``Company``,
``Pattern`` and ``Technique`` through-models already exist … so this is no longer
a 'do we add them' question — it is a 'when does the corpus justify filling
them' question" (``docs/roadmap.rst``).

*Reusing ``lms.DifficultyLevel`` for exercises.* Rejected. A course's depth
(beginner/intermediate/advanced/all-levels) and an exercise's difficulty
(Easy/Medium/Hard) are different questions with different vocabularies. The
spec fixes the exercise vocabulary at three values; reusing the four-value
course vocabulary would have left it ambiguous.

Trade-offs accepted
-------------------

*Three-way joins.* Company, Pattern and Technique are separate tables; a query
that filters on all three joins three tables. The corpus is tiny (four problems
at the time of writing), so this costs nothing today. It is a real cost at
scale.

*No completeness rule.* An author can tag a problem "Google" and "Hard" and
leave Pattern and Technique empty. Nothing enforces coverage; the filter
dropdowns simply reflect what is tagged. The roadmap notes that filtered listing
pages "need canonical tags before they are indexed" — i.e. the corpus must be
tagged deliberately, not just as a by-product of authoring.

*Empty axes are invisible.* The conditional-rendering fix means an axis with no
tags is simply absent from the UI. A visitor cannot tell whether Company
filtering does not exist or is not yet populated. For MVP that is the right
call; it is a discoverability trade-off if the site later wants to advertise
coverage.

*Tag vocabulary is implicit.* Unlike a ``TextChoices`` field, taggit accepts any
string. Two authors can create "Two-Pointers" and "Two Pointers" as distinct
tags. There is no vocabulary constraint beyond consistency. The AI drafting
command partially mitigates this: it drops generated tags that no existing row
carries and lists them as review notes, so a draft cannot invent a new tag.

When to revisit
---------------

* When tag cardinality makes the three-way joins noticeable — not the case at
  the current corpus size.
* When cross-axis queries ("Medium Two-Pointer problems tagged Google") need a
  dedicated facility rather than client-side filtering of the full table.
* When the corpus is large enough that free-form tag drift ("Two-Pointers" vs
  "Two Pointers") is a real browsing problem. The fix would be a canonical tag
  list with validation, which is the migration-per-value cost the choice-field
  approach was rejected for.
