Progress tracking
=================

Aim / use case
--------------

Every learner-facing surface must show the same progress: the Landing stats
strip, Track completion bars, Sheet progress rings, quiz cards, the challenge
Submissions tab, and LMS lesson completion. A learner who solves a problem on
one page must see it marked solved everywhere else. Because production is a
static export with no accounts and no server, progress has to live in the
browser and be readable by every surface independently.

Design
------

One IndexedDB database, four object stores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``static/js/pyverse-progress.js`` exposes ``window.PyverseProgress``. Single
database ``pyverse_progress``, version ``2``:

.. list-table::
   :header-rows: 1
   :widths: 22 20 58

   * - Store
     - keyPath
     - Contents
   * - ``submissions``
     - ``id`` (autoIncrement)
     - One row per Run/Submit attempt: ``{id, slug, status, latency, title,
       timestamp}``. Indexed on ``slug``.
   * - ``problem_status``
     - ``slug``
     - Derived status per problem: ``{slug, status: "solved"|"attempted",
       updated}``. Absent means untouched.
   * - ``streak_meta``
     - ``id`` (fixed key ``"single"``)
     - ``{id, last_active_date, current_streak, longest_streak}``.
   * - ``lesson_status``
     - ``slug``
     - LMS lesson completion: ``{slug, course, title, updated}``. Added in v2.

The comment at the top of the file states the model: "One IndexedDB store,
shared by every Practice surface … and only the problem page writes to it.
``problem_status`` is derived from ``submissions`` so it can be recomputed
rather than trusted — a drifted copy is never the source of truth."

The API
~~~~~~~

.. code-block:: javascript

   recordSubmission({slug, status, latency, title})  // write (challenge page)
   statusMap()        // {slug: "solved"|"attempted"} — {} if unreadable
   readStatus()       // the same map, but rejects when the store cannot be read
   stats()            // {available, solved, attempted, tracked}
   streak()           // current streak number
   submissionsFor(slug, limit = 20)  // newest-first attempts for one problem
   completeLesson({slug, course, title})
   uncompleteLesson(slug)
   lessonMap()        // {slug: {course, title, updated}}
   clear()            // wipes ALL four stores at once

Every reader catches errors and returns an empty result. "Everything degrades
gracefully: if IndexedDB is unavailable (private mode, blocked storage) the pages
still render, they just show no progress." Storage-blocked states hide controls
rather than offering a button that cannot keep its promise (DEVLOG, LMS progress
entry: "Storage blocked … hides the controls instead of offering a button that
cannot keep its promise").

The ``lesson_status`` store is the same database, not a second one
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added when LMS learner progress shipped (DEVLOG 2026-09-17). The dev log states
the reason: "lessons complete into the *same* IndexedDB store the practice
surfaces read rather than a second one … so a browser profile keeps one progress
record for both halves of the site." ``DB_VERSION`` went 1 → 2; the upgrade only
adds a store, so existing submissions, statuses and streak survive (confirmed by
reading the store after the bump — DEVLOG).

The four stores share a single version bump. Adding a fifth store is the
documented extension path: "a new progress surface adds a store and an API method
to ``static/js/pyverse-progress.js``" (DEVLOG, Wagtail/Django notes).

Checkpoints read ``problem_status`` and gate the next-lesson link
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A lesson body can carry a **required practice checkpoint** — a
``PracticeBlock`` with ``required_to_advance`` set, pointing at a
``coding.CodingProblem`` or a ``quiz.Quiz`` (``page-tree.rst``). Its
satisfaction is not new progress: a checkpoint is satisfied exactly when the
target's slug reads ``solved`` in ``problem_status``, which is what the challenge
page writes when a submission is accepted and what the quiz page writes when the
quiz is passed (``recordSubmission({…, status: passed ? "ACCEPTED" :
"WRONG_ANSWER"})`` in ``templates/quiz/quiz_page.html``). One store, no second
notion of "done".

The block renders the target's slug as ``data-checkpoint-slug`` and, when
required, ``data-checkpoint-required``. ``static/lms/js/lesson-progress.js``
paints each ``[data-checkpoint]`` from that map (state text,
``data-checkpoint-done``, and the neutral → green class swap) and then decides the
gate:

* ``#lesson-next`` gets ``aria-disabled="true"``, ``opacity-40`` and
  ``pointer-events-none`` while any required checkpoint is unmet, and
  ``#lesson-gate-note`` is unhidden with the count of unmet checkpoints.
* The mouse is stopped by CSS, keyboard activation by a click listener that calls
  ``preventDefault()`` when ``aria-disabled`` is set — both, because
  ``pointer-events: none`` does not block Enter on a focused link.
* The gate reads ``readStatus()``, **not** ``statusMap()``. ``statusMap()``
  swallows a failed read and returns ``{}``, which a gate cannot distinguish from
  "nothing recorded yet" — and a gate that read a blocked store as "nothing
  recorded" would lock every lesson in private browsing. ``readStatus()`` rejects,
  and the ``.catch`` unhides nothing and removes ``aria-disabled``: unreadable
  storage never gates.

This is the first reader that has to tell "no record" from "no storage", which is
the whole reason ``readStatus()`` exists as a separate function instead of a
second ``try``/``catch`` inside the gate.

Derived status, not a trusted copy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``recordSubmission`` writes the submission row and updates ``problem_status`` in
one transaction:

* A new submission with status ``ACCEPTED`` sets the problem to ``solved``.
* Any other status sets it to ``attempted`` unless it was already ``solved`` —
  a solved problem never regresses on a later failed submission.

``problem_status`` can be rebuilt from ``submissions`` at any time, so a drift
between the two is recoverable rather than corrupting.

Streak
~~~~~~

``touchStreak()`` runs on every submission. It compares today's date to
``last_active_date``: if they differ, the streak increments when the previous
activity was yesterday, otherwise resets to 1. ``longest_streak`` is a running
high-water mark. Dates are UTC ``YYYY-MM-DD`` strings (``toISOString().slice(0,
10)``), which means the streak boundary is UTC midnight, not the learner's local
midnight.

Verified flows
~~~~~~~~~~~~~~

The dev log records these flows verified in a browser against both the dev
server and the frozen export:

* Solve ``two_sum`` → ``✓ Accepted`` → Landing shows ``solved=1`` with a
  ``✓``/``solved`` row.
* Complete a lesson → the course page counts ``1 of 2`` with a 50% bar; undo
  clears it; the sidebar ticks the right lesson.
* Quiz graded 2/3 → ``Not passed — 67%`` (needs 70%), attempt recorded.
* Required checkpoint (DEVLOG 2026-09-26): the lesson's next-lesson link renders
  ``aria-disabled="true"`` at opacity 0.4 with ``pointer-events: none``, the
  checkpoint reads "Not started", and a programmatic click on the locked link does
  not navigate. After
  ``recordSubmission({slug: "two-sum", status: "ACCEPTED"})`` and a reload: ``✓
  Done`` with the green pair applied, ``aria-disabled="false"``, gate note hidden.
  The same page's notebook ran (``5`` then ``6``, cells sharing one namespace),
  which is the load-bearing case for "a lesson can carry both a checkpoint and a
  notebook".

Alternatives considered
-----------------------

*localStorage.* Simpler API, but synchronous, string-only, and no indexes.
``submissions`` needs an index on ``slug`` to look up a problem's history;
``localStorage`` would require reading and parsing the entire blob per lookup.
IndexedDB is asynchronous but the surfaces are already async.

*One database per feature.* Rejected. The DEVLOG states the rule as "one
IndexedDB database … with four stores" and "a new progress surface adds a store
and an API method" — i.e. stores are the extension point, not databases. A
second database for lessons would mean a second ``open()``, a second version
counter, and ``clear()`` could not wipe both halves. The unified store is why
"``clear()`` now empties the lesson store too."

*A server-side progress API.* Impossible without a server. The whole point of
the static export is no runtime component. Progress is inherently per-browser
because there is nowhere to persist it centrally.

*Accounts.* allauth exists (login/signup/profile) but is used for admin
authoring and profile, not progress. Account-linked progress would require a
server and a database in production, which contradicts the static-export model.

*A ``lesson_status``-based checkpoint.* Rejected — a completed lesson is not a
completed problem. The checkpoint's identity has to be the *target's* slug, so the
write the learner already makes on the challenge or quiz page is what satisfies
it; recording checkpoint completion separately would give one fact two identities
and a second thing to keep in sync.

*``statusMap()`` for the gate.* Rejected — it turns a blocked store into ``{}``,
and a gate reading that as "nothing recorded yet" would hide the next lesson from
a learner who has no way to satisfy the checkpoint. ``readStatus()`` exists so the
gate can fail open instead.

*A hard gate.* Would require knowing server-side whether a learner solved the
problem, i.e. accounts and a server. The same architectural limit as
account-linked progress; see "When to revisit".

Trade-offs accepted
-------------------

*No account-linked progress.* Progress cannot follow a learner to another
device, another browser, or after clearing site data. The DEVLOG lists this under
"Known rough edges": "Progress — practice and lessons alike — is per-browser and
per-device; there is no account-linked progress, and ``clear()`` wipes both
halves at once."

*``clear()`` is all-or-nothing.* There is no per-surface reset. A learner who
wants to clear quiz history must also lose practice submissions and lesson
completion, because all four stores share one database and one ``clear()``.

*UTC streak boundaries.* A learner in UTC−8 who works at 5pm local (1am UTC
next day) may see a different streak date than expected. Minor, but real.

*The store is readable and writable by any script on the page.* A learner can
edit their own IndexedDB rows. This is the same self-grading model as the
grading engine — the site grades for the learner's benefit, not against them.

*Storage can vanish.* Private browsing, storage pressure, or the learner
clearing site data removes progress with no warning beyond the hidden controls
in a blocked state.

*The checkpoint gate is soft, partial and per-browser.* Only the **next-lesson
link** is gated; the lesson sidebar, the course page's lesson list and the course
progress bar are not, so a learner can pick the next lesson out of the sidebar.
This is inherent to a site with no server — the gate is a nudge, not an
entitlement check — and it inherits every per-browser limit above (a different
browser, or cleared storage, opens the gate again).

*A checkpoint can be satisfied before the lesson is opened.* Nothing ties the
submission to the lesson that asks for it: solve the problem first and the
checkpoint already reads ``✓ Done``. That is the honest shape of "one slug, one
status" — the alternative is per-lesson checkpoint rows, i.e. the second identity
rejected above.

When to revisit
---------------

* When account-linked or cross-device progress becomes a requirement. That
  needs a server and a database in production, i.e. it breaks the static-export
  model. The decision to revisit is architectural, not local.
* When a checkpoint must actually block progress rather than nudge it. That is
  the same architectural decision as above: a gate that cannot be walked around
  has to be enforced where the learner cannot edit it.
* If the next-lesson link is replaced by a different navigation component. The
  gate keys off ``#lesson-next`` and ``#lesson-gate-note``; a redesign has to keep
  those two ids or move the gate with them.
* When the ``submissions`` store grows large enough that an unbounded
  ``submissionsFor`` scan is slow — the store is never pruned, so a learner with
  thousands of attempts keeps every row.
* When a fifth progress surface appears (flashcards are the candidate on the
  roadmap). By convention that adds a fifth store and new API methods; if the
  database version bump becomes risky, extracting the store definitions into a
  migration function is the cleanup.
