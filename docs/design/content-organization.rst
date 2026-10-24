Content organization
====================

Aim / use case
--------------

A learner browsing practice problems should be able to find them in the way that
matches their current goal — a plain table of everything, a single-skill drill
(Track), or a curated multi-stage path (Sheet). These are three different browse
models for the same underlying ``CodingProblem`` records, not three separate
problem sets.

Design
------

All three surfaces are served by the ``topics`` app and read the same
``CodingProblem`` snippet records. No problem data is copied; every surface
queries the same table and renders it differently.

Landing table (PracticeHubPage)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``/`` — ``topics.PracticeHubPage``, a ``RoutablePageMixin`` at the root.

* Displays **every** live ``CodingProblem`` (``topic__isnull=False,
  topic__live=True``) in a single sortable, filterable table.
* Default sort: difficulty ascending (via ``DIFFICULTY_RANK``), then title.
* Filter controls for Difficulty, Company, Pattern, Technique — rendered only
  for axes that have values (see ``tag-taxonomy.rst``).
* Progress strip: solved count, attempt count, streak — all read from the
  shared IndexedDB store (see ``progress-tracking.rst``).
* Sidebar: Track cards showing name + problem count + real completion bar.
  Quiz listing: cards showing title, question count, topic.
* Client-side filter/sort/search — no server round-trip, works on the frozen
  export.

Spec §2 reference: "show real aggregate data or nothing, never a made-up number"
— the comment in ``practice_hub_page.html`` notes acceptance rate is deliberately
omitted.

Tracks (PracticeTopicPage)
~~~~~~~~~~~~~~~~~~~~~~~~~~

``/practice/<topic-slug>/`` — ``topics.PracticeTopicPage``, also
``RoutablePageMixin``. Topics nest to arbitrary depth ("Arrays" → "Two Pointers").

* Aggregates problems via O(1) subtree lookup:
  ``CodingProblem.objects.filter(topic__path__startswith=self.path)`` — every
  problem tagged to this topic or any descendant.
* Same table template as the Landing, but pre-filtered to one topic subtree.
* Default sort: difficulty ascending (spec §4), so a learner drills easy problems
  first within a skill.
* No new content type: the comment in ``practice_topic_page.html`` says "Track
  (spec §4): a Topic hub page, re-skinned as a single-axis drilling surface …
  Not a new content type: same URL, same Wagtail page."
* Quizzes tagged to the same subtree are listed too.

Sheets (SheetPage)
~~~~~~~~~~~~~~~~~~

``/practice/sheets/<slug>/`` — ``topics.SheetPage``, part of a
``SheetsIndexPage`` listing.

* A curated, ordered path through problems arranged in a two-level collapsible
  tree: categories → problems in solving order.
* Problems are referenced via ``SnippetChooserBlock("coding.CodingProblem")`` —
  never copied. The same ``CodingProblem`` can sit in three sheets, one track,
  the Landing table, and still be one record.
* Per-category progress read from the shared IndexedDB store; collapse state
  remembered per sheet in localStorage (``data-tree-key``).

Spec §3 reference: "Sheets answer a different question from the Landing table
('tell me what order to solve things in'), so they live beside the tag hubs
rather than replacing them" — ``SheetsIndexPage`` docstring.

Why one wasn't enough
---------------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 30 20

   * - Surface
     - Question it answers
     - Who it serves
     - Curated?
   * - Landing table
     - "What's here?"
     - Anyone browsing; repeat visitor checking new problems
     - No (authoring=automatic)
   * - Track
     - "Drill me on this skill"
     - Learner who knows what they need to practice
     - Per topic (all problems in subtree)
   * - Sheet
     - "What order should I solve these?"
     - Learner who wants a guided progression
     - Fully (explicit ordering + categories)

A learner who only wants the table would be served by the Landing. A learner who
wants to grind "Two Pointers" problems wants a Track that locks them to that
topic. A learner who wants a six-week study plan wants a Sheet. Each is a
different answer to the same "find me problems" question, and none is a strict
superset of another — a Track cannot express "solve these 15 problems in this
exact order, grouped by week, starting with the easy reviews."

Alternatives considered
-----------------------

*One surface, with multi-axis filtering only.* The Landing table already has
client-side filter/sort/solve-status. That covers "find me Easy problems" and
"find me problems I haven't solved." It does not cover "drill one skill for 30
minutes" (a Track) or "follow this 6-week plan" (a Sheet). The code comment in
``practice_hub_page.html`` says "Sheets answer a different question".

*Separate content types for each surface.* Rejected: all three read the same
``CodingProblem`` records. No copied data, no sync problem, no "is this
problem in my Track and my Sheet" drift.

*Acceptance rate.* Deliberately omitted from the Landing (spec §2 comment):
show real aggregate data or nothing, never a made-up number. Acceptance rate
from client-side-only data is meaningless — no server aggregates submissions.

Trade-offs accepted
-------------------

*Three surface templates, one data source.* Three Django templates to maintain,
each with its own JS (``practice-browse.js`` shared, but Sheet collapse state
is separate). The data model aligns perfectly (one ``CodingProblem`` table), but
the UI surface grows.

*No pagination.* The Land table renders every problem, and the subject volume
is well under the point where an initial payload matters. At 10,000 problems a
client-side table would be slow. Distill write time would also increase
(same queryset).

*Three surfaces can show different "totals" if a problem is unassigned.* A
problem with ``topic__isnull=False`` appears on the Landing, but only if
``topic__live=True``. A problem inside a Sheet via ``SnippetChooserBlock``
appears even if its topic is not live (``SheetPage.problems()`` does not filter
on topic status). This is inconsistent but edge-case: a Sheet author would not
intentionally include an invisible problem.

When to revisit
---------------

* When the corpus hits ~500 problems and the Landing table starts to feel slow
  without server-side pagination. The fix would be client-side virtual scrolling
  or server-side paginated API (which breaks static export — you'd need
  either a server per-page pagination during build).
* When someone wants to compose Sheets from Tracks ("give me a Sheet of every
  problem in the 'Two Pointers' Track, but exclude the three I already solved").
  That's a query composition problem, not a new surface.