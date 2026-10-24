Design notes
============

Why these pages exist
---------------------

The companion ``architecture-notes.rst`` (the mention-level Wagtail/Django
inventory) answers "what feature was used where," fast. These pages answer a
different question: **why does this subsystem look the way it does, and what
else was on the table.** The distinction matters because the reasoning behind a decision is
the first thing lost once the decision is a few months old — the code keeps the
*what*, and nothing keeps the *why* unless it is written down deliberately.

Someone who has never seen this codebase should be able to read one page here and
understand not just what was built, but why it looks this way instead of the
obvious alternative, and what would have to be true for that choice to be wrong.

Each page follows the same five-part shape:

1. **Aim / use case** — who this serves and what problem it solves.
2. **Design** — the actual shape: real class/model/file names, how the pieces
   connect.
3. **Alternatives considered** — what else was on the table and why it lost.
4. **Trade-offs accepted** — what this costs, stated plainly.
5. **When to revisit** — what would actually justify changing this later.

The pages
---------

.. toctree::
   :maxdepth: 1

   grading-engine
   tag-taxonomy
   content-organization
   progress-tracking
   static-export
   page-tree
   labs
   puput-blog

Roughly in order of how load-bearing they are. The grading engine and the tag
taxonomy were written first because they carry the richest reasoning already
recorded in code comments and the spec.

Sources — and what is honestly *not* sourced
--------------------------------------------

Every "why" on these pages is traceable to one of three places. Nothing is
reconstructed from a plausible-sounding guess.

**Code comments.** The load-bearing rationale often lives next to the code that
depends on it, citing spec sections directly (``# spec §5 phasing``,
``# spec §2``). Examples: the ``Comparator`` docstring in
``pyverse/coding/models.py``; the taggit-through-model comment in the same file;
``pyverse/taxonomy.py``'s module docstring explaining why difficulty is shared
between ``coding`` and ``quiz``; the redirect comment in ``pyverse/freeze.py``;
the canonical-URL docstring in ``pyverse/home/templatetags/seo_tags.py``.

**``pyverse-requirements-v2.md``.** The full build spec. **This file is not in
this repository.** The dev log records that: "The build spec is **not in this
repo**: the code cites ``pyverse-requirements-v2.md`` as 'spec
§2/§3/§5/§12/§18'. Find it before re-deriving design decisions." Consequences
are flagged inline on the affected pages:

* ``page-tree.rst`` — the course-model reversal (three subclasses, then
  reverted) is only in the spec. The repository contains no trace of the
  three-subclass version.
* ``static-export.rst`` — the ``django-distill`` compatibility risk analysis is
  in the spec; only the outcome is observable in-repo.
* ``puput-blog.rst`` — the reason puput was vendored rather than pip-installed
  is not recorded anywhere in the repository.

Where the reasoning is genuinely absent, the page **says so** instead of
inventing a rationale. A false "why" is worse than an honest "not documented at
the time": it survives review, gets cited, and misleads the next person.

**The dev log.** Session history with dates and verified outcomes. The prompt
that commissioned these pages calls it ``docs/devlog.rst``, but the actual dev
log lives at ``DEVLOG.md`` in the repository root — Sphinx's ``docs/`` tree does
not contain a ``devlog.rst``. These pages cite ``DEVLOG.md``.

**Note on sibling docs.** The prompt lists ``planning.rst``, ``devlog.rst``,
``usage.rst``, ``features.rst`` and ``architecture-notes.rst`` as already set
up in ``docs/``. At the time these pages were written, ``docs/`` contained only
``howto.rst``, ``roadmap.rst`` and ``users.rst`` — the other five were not
present, so the companion mention-level inventory (``architecture-notes.rst``)
is referenced above but does not exist in this tree yet. The in-depth pages
stand alone; they do not depend on that inventory being present.

Related documentation
---------------------

* ``DEVLOG.md`` — append-only session log; the source of the dated, verified
  outcomes cited above.
* ``docs/roadmap.rst`` — what is decided, and the order it implies.
* ``README.md`` — the deploy path and the static-export command.
