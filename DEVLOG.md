# PyVerse — dev log

Working reference for Udit. Sections are fixed and always present; the session
log is append-only (newest first), `Features` / `How to evolve it` / `Wagtail &
Django notes` get overwritten in place. `README.md` (deploy notes) and `docs/`
(Sphinx) are separate and not maintained from here.

## What we're planning

- One site that covers learning Python end to end: guided course path (LMS),
  a free practice problemset with in-browser grading, quizzes, curated sheets
  and tracks, and notes/blog — shipped as a **static export**, so no server,
  no runtime cost, and nothing of ours executes a learner's code.
- Priority order right now (the reasoning is in `docs/roadmap.rst`):
  1. Content on surfaces that already exist — the whole corpus is 4 problems,
     2 quizzes, 1 course, 2 lessons, 2 labs.
  2. Deploy the export — host still undecided.
- The build spec is **not in this repo**: the code cites `pyverse-requirements-v2.md`
  as "spec §2/§3/§5/§12/§18". Find it before re-deriving design decisions.

## Session log

### 2026-09-26 — Lesson checkpoints and notebooks

- `LessonPage.body` gained two blocks, so a lesson no longer ends at prose:
  `practice` (`PracticeBlock`: a `SnippetChooserBlock` for a `CodingProblem`
  **and** one for a `Quiz`, plus `required_to_advance`) and `notebook`
  (`NotebookBlock` → `ListBlock(NotebookCellBlock)`, cells typed `code` or
  `markdown`). Exactly one of the two practice targets must be set — StructBlocks
  have no native "exactly one of", so `PracticeBlock.clean()` raises
  `StructBlockValidationError` keyed on `problem`. Migration
  `lms/0004_alter_lessonpage_body.py`; no `coding` migration (the block move in
  the next bullet changes no migration state).
- `EditorialApproachBlock` moved out of `coding/models.py` into new
  `pyverse/common/blocks.py`, so `quiz`/`labs` can reuse it without a third copy.
  Free of charge: `StructBlock.deconstruct_with_lookup` inlines the structure, so
  migration state never stores the Python path — `makemigrations --check` reports
  nothing for any `pyverse.*` app.
- Notebook code cells run in the browser on the existing runtime:
  `run_notebook()` / `window._pyNotebook()` sits beside `exec_solution()` /
  `_pyExec` in `includes/pyscript_runtime.html` (the site's single PyScript pin,
  2025.7.3), driven by new `static/lms/js/notebook.js`. JS passes the cells in
  `window._pendingNotebook`, read out of the rendered DOM rather than a
  `json_script` payload — a lesson may hold several notebooks, so a fixed payload
  element id would collide. Markdown cells are rendered server-side by
  `wagtailmarkdown`, so only code crosses the bridge. Cells share one namespace
  per Run (Run-All semantics), a second click starts clean, and a raising cell
  captures its traceback while the run continues.
- The runtime partial is included at most once per page and only when the lesson
  has a notebook (`LessonPage.get_context` → `has_notebook`), so a prose lesson
  never pays for the Pyodide download.
- Required checkpoints gate the next-lesson link. `lms/js/lesson-progress.js`
  paints each `[data-checkpoint]` from `problem_status` and, while a
  `data-checkpoint-required` block's slug is not `solved`, sets `aria-disabled`,
  `opacity-40` and `pointer-events-none` on `#lesson-next` (plus a
  `preventDefault()` click guard, because `pointer-events` does not stop Enter on
  a focused link) and unhides `#lesson-gate-note`. The gate uses the new
  **`readStatus()`**, not `statusMap()`: `statusMap()` maps a blocked store to
  `{}`, which a gate would read as "nothing recorded yet" and lock every lesson in
  private browsing — `readStatus()` rejects instead, and the caller fails open.
- Counts, one query per grid instead of one per card: `lms/utils.py`
  `lesson_counts_for()` counts lessons under every course in the grid's container
  with a single descendant query, bucketing each path under its parent course by
  truncating one treebeard segment (`path[:-Page.steplen]`). There is no FK from a
  lesson to its course, so `annotate`/`prefetch_related` cannot see it, and
  `{{ course.lesson_count }}` inside a 12-card grid was one `COUNT` per card.
  `CoursePage.set_lesson_count()` fills the instance cache; `lesson_count` still
  falls back to `ordered_lessons().count()`, so a grid that forgets to fill it is
  correct-but-slower. `Quiz.question_count` is now a `cached_property` preferring
  the `_question_count` annotation both Practice quiz listings add.
- `CoursePage.site_difficulty` maps `DifficultyLevel` onto `taxonomy.Difficulty`
  (beginner→easy, intermediate→medium, advanced→hard, all_levels→`None`). No
  consumer yet — it exists so a future cross-surface comparison reads one table
  instead of comparing two enums field-to-field.
- Checkpoint chooser resolution is batched by Wagtail itself
  (`StreamValue._prefetch_blocks` → `ChooserBlock.bulk_to_python`), measured:
  1 query for one problem checkpoint, 2 for problem + quiz, still 2 for three
  checkpoints (both problems in one `IN (…)`). So the templates carry no
  `practice_problems_by_pk` context dict, no pk scanner and no `get_item` filter —
  the version that was on the table would have resolved the same objects twice and
  added queries for nothing.
- Bug found while wiring the sidebar: `templates/lms/course_page.html` printed
  `{{ lesson_count }}`, a name `CoursePage.get_context` never set, so the
  "Lessons" row rendered blank. It now uses `{{ lessons|length }}`, already in
  context.
- Verified in a browser against the dev server, and in the frozen export: notebook
  cells printed `5` then `6` from one namespace and repeat runs stayed
  idempotent; a `raise ValueError` cell showed a red traceback with "1 cell
  failed" while the other cells kept their output; the locked gate rendered
  `aria-disabled="true"` / opacity 0.4 / `pointer-events: none` with the amber
  note, and a programmatic click did not navigate;
  `recordSubmission({slug: "two-sum", status: "ACCEPTED"})` + reload gave
  `✓ Done` with the green pair and an enabled next link to
  `loops-and-accumulators`; a lesson without a notebook renders no PyScript tag
  and no notebook markup (checked live and in `_site/`); `distill-local` froze the
  new blocks with `has_notebook` correctly omitting the runtime; course cards and
  the course sidebar show real lesson counts in the export. Two throwaway pytest
  files (5 + 3 tests) covered the validation, query-count and render contracts and
  were deleted; full suite 44 passed.
- Gotcha that cost a rebuild: `pyverse/theme/static/css/dist/styles.css` is
  **gitignored build output** (despite the note further down this file) and it was
  stale — `opacity-40`, `pointer-events-none`, `border-green-300`, `bg-green-50`
  and `text-amber-700` were simply absent, so the gate painted nothing until
  `.venv/bin/python manage.py tailwind build`. Run the build after adding any new
  utility class, or run `manage.py tailwind start` as `Procfile.tailwind` does.
- Pre-existing lint debt, left alone: `pre-commit run --files` fails
  `djlint-django` on `T003`/`H020` in `course_page.html` and `lesson_page.html`
  (present at `HEAD`), and `ruff check` reports `E501` ×5 in `coding/models.py`
  plus `PLC0415` ×9 in `topics/models.py`. The one violation this change *adds* is
  a `PLC0415` in `lms/utils.py`, where `LessonPage` is imported inside the function
  on purpose — `lms.models` imports that module, so a module-level import closes
  the cycle with a half-built models module (the same cycle-break `topics/models.py`
  already uses nine times). `djlint-reformat` rewrites those templates wholesale
  (4→2 indent, mangled `{% comment %}` blocks, and it can inject whitespace into
  `<pre>`-carried cell source) and *still* fails the lint hook, so the reformat was
  reverted rather than committed.

### 2026-09-19 — AI content drafting (`manage.py ai_create`)

- New app `pyverse/ai_content/`: one interactive command — a menu of four
  content types, then a free-text description — over pluggable generators
  (`generators/{dsa,blog,lesson,quiz}.py`). Everything except the per-type
  schema and the Wagtail-construction step is shared: style-guide loading,
  prompt assembly, JSON parsing, parent selection, refusal handling, output.
- Style prompts are plain markdown in `styles/*.md` (tone, formatting, good/bad
  examples); the field schema lives in Python next to the `create()` that
  consumes it, and derives its enum values from the real models
  (`Difficulty.values`, `Comparator.values`, `HintBlock.Tier.values`, the lesson
  block choices) so it cannot drift from `coding/models.py`.
- The model is reached only through `llm.py`, which uses **wagtail-ai**'s
  provider config (`WAGTAIL_AI["PROVIDERS"]`; `AI_PROVIDER` / `AI_MODEL` /
  `AI_API_KEY` or the provider's own env var). One key serves the command and
  the admin AI panels. Replies are parsed tolerantly (fences, prose, one
  corrective retry) and every failure names the field or the environment.
- DSA drafts are **verified before saving**: the generated solution is executed
  against the generated test cases in a subprocess, with `verify_runner.py`
  mirroring the browser harness (same four comparators, same
  "input is Python source for the argument list" convention, same fallback to a
  repr comparison) so a pass here predicts a pass in a learner's browser. A
  failing case refuses the draft and prints the case, the expectation and what
  came back; so do `custom` with no comparator code, all-hidden cases, a quiz
  key marking two choices correct, a `true_false` question with no answer, and a
  lesson block that needs an asset (`video`/`image`).
- "Draft" is per type, deliberately: `CodingProblem` and `Quiz` are created with
  no `topic` (every learner-facing listing filters on `topic__isnull=False`, so
  assigning a topic in review is the publish step); puput entries and lessons
  are real pages created `live=False` — `Page.live` defaults to `True`, so
  `add_child` alone would have published them. `function_name`,
  `function_signature` and `comparator` are proposed, then called out in the
  printed review notes as needing a human yes.
- Tag axes are constrained to the vocabulary already in the database: a
  generated tag no other row carries matches no browse filter, so unknown names
  are dropped and listed as a note instead.
- Verified end to end (stub provider, real everything else): `1` → describe →
  `✓ All 5 cases pass` → `CodingProblem "Search in Rotated Sorted Array"` with
  the review URL, `topic` null, hints sorted nudge→approach→solution, and the
  unknown tag dropped in a note. The verifier was also run against the three
  shipped solved problems (4/4, 3/3, 3/3), a mutated expectation, a renamed
  function and an infinite loop (stopped at 10 s). Blog/lesson/quiz smoke-run
  against a real page tree, with refusals creating no rows. wagtail-ai's panels
  and Draftail feature verified by rendering the four admin edit pages (200,
  `wai-field-panel`, `wagtail_ai/main.js`, `"ai"` in the rich-text features).
- 22 new tests in `pyverse/ai_content/tests/` (grading semantics + every refusal
  gate); full suite 44 passed. `ruff` clean on the new app.
- Two blockers had to be cleared first, both pre-existing:
  - `puput`, `lms`, `home`, `labs` and `topics` migrations all depended on
    `wagtailcore.0098_query_searchpromotion_querydailyhits`, which no released
    Wagtail has ever shipped. The migration graph failed to load, so `migrate`
    and **the entire test suite** were broken (16 tests: 2 passed, 14 errors).
    Repointed at `0097_baselogentry_uuid_action_timestamp_indexes`.
  - The venv ran CPython 3.14.0rc2, whose `typing._eval_type` has no
    `prefer_fwd_module` argument; pydantic ≥ 2.11 passes it on any 3.14, so
    importing wagtail-ai (`any-llm` → pydantic) crashed at `django.setup()`.
    The venv is now on **3.14.7** (`uv sync --python 3.14.7`; `uv.lock`
    unchanged, same 182 packages).

### 2026-09-17 — Practice moves into the site shell

- Practice was the last dark island: hub, tracks, sheets, challenge and quiz
  pages were standalone documents with their own header and no footer. All six
  now extend `home/base_.html` — same cream brutalist theme, navbar, footer,
  fonts and card language as home and about — which settles the "two styling
  systems coexist" question in favour of the site theme.
- Interactive surfaces stay dark, framed in a shared `.pe-console` panel
  (3px ink border, hard shadow, `.pe-console-bar` caption bar) defined in
  `practice-engine.css`; the same classes now back the Labs tracer, so there is
  one console pattern rather than one per feature. Light pages that still need
  engine tokens wrap content in `.pe-engine pe-on-light` (keeps `var(--…)` and
  every `pe-*` component resolvable, drops the dark full-page painting).
- `home/base_.html` gained `{% block body_class %}` and `{% block body_attrs %}`
  so a page can add `data-problem-*` / `data-quiz-*` to `<body>` without
  restating the shell.
- No JS contract changed: `practice-browse.js`, `pyverse-progress.js` and the
  inline state machines on the challenge and quiz pages were untouched, so every
  id, `data-*` hook and status decoration behaves exactly as before.
- `practice/includes/engine_header.html` is gone — the site navbar replaced it.
- Verified in a browser, dev server and frozen export: solved `two_sum` in the
  page's editor → `✓ Accepted`, 4/4 cases; the Landing then shows solved=1,
  easy=1, a `✓`/`solved` row and streak 1; the sheet page offers "Continue: print
  hello world", its dots and ring move (25%) and its tree still collapses; the
  quiz grades 2/3 with "Not passed — 67% (needs 70%)" and records the attempt;
  no console errors or failed requests on any of the six pages; no horizontal
  overflow at 1365px or 390px, and the challenge still stacks its panes on a
  phone.

### 2026-09-17 — Labs wear the site's own theme

- Labs no longer ship their own shell. Both pages extend `home/base_.html` —
  the same cream brutalist theme, navbar, footer, fonts and card language as
  the home and about pages — so Labs reads as part of PyVerse instead of a
  second, darker product.
- The tracer itself stays dark on purpose: it sits in a thick-ink framed
  console, the same pattern the home page uses for its device mockup, so a
  dark code surface is native to this theme rather than a clash. The frame
  bar carries the runtime status pill.
- `lab-engine.css` lost its full-viewport assumptions (`.lab-app` is `height:
  100%` inside the frame; the `body.lab-app` margin reset and the engine's own
  header are gone), and `practice-engine.css` is now scoped to the console
  rather than the document.
- Verified against the About page by computed style rather than by eye: body,
  navbar (63px, 3px ink border), `h1` (72px/900/-3.6px), footer and the
  Tailwind CDN config now match exactly, and both labs render inside the theme
  on the dev server and in the frozen export, with the tracer still tracing
  (12 steps for `two_sum`, 7 for the aliasing lab, memory graph intact).

### 2026-09-17 — LMS learner progress

- Lessons complete into the *same* IndexedDB store the practice surfaces read
  rather than a second one: `pyverse-progress.js` goes to `DB_VERSION = 2` and
  adds a `lesson_status` store (keyPath `slug`, with `course` + `title`), so a
  browser profile keeps one progress record for both halves of the site. The
  upgrade only adds a store — existing submissions, statuses and streak survive
  (confirmed by reading the store after the bump).
- New API on the shared store: `completeLesson`, `uncompleteLesson`,
  `lessonMap`; `clear()` now empties the lesson store too.
- `static/lms/js/lesson-progress.js` is the LMS half: the course page ticks
  completed lessons, shows "n of N complete" and a progress bar; the lesson page
  gets a "Mark complete" control with an undo, and the sidebar lesson list picks
  up the same ticks. Storage blocked (private mode, denied permission) hides the
  controls instead of offering a button that cannot keep its promise.
- `window.__LESSON_SLUGS__` / `__CURRENT_LESSON__` are no longer dead: the
  templates now carry `data-lesson-slug` hooks and the page reads its own
  completion state from the store.
- Verified in a browser on both the dev server and the frozen export: complete a
  lesson → the course page counts 1 of 2 with a 50% bar; undo clears it; the
  sidebar marks the right lesson; no console errors or failed requests on the
  course, lesson, topic and lab pages; the practice landing still reads the same
  store after the version bump.

### 2026-09-17 — Labs: the tracer lab

- New `pyverse/labs/` app: `LabsIndexPage` (`/labs/`) and `LabPage`
  (`/labs/<slug>/`), top level under Home as `docs/roadmap.rst` records. Two
  labs seeded — "Two Sum, one pass" (line view) and "Two names, one list"
  (memory view) — and a Labs entry added to the Site Settings nav between Blog
  and About.
- One tracer, two renderers. `includes/tracer_runtime.html` traces with
  `sys.settrace` inside PyScript (the same 2025.7.3 pin as the grading harness,
  so no second runtime) and returns a single step list;
  `static/js/lab-engine.js` renders it as source lines + variables + stdout +
  a step timeline, or as a Graphviz record diagram through `@viz-js/viz`
  3.11.0, fetched only when the memory view is first opened.
- Deliberate departures from the prototypes:
  - Neither prototype is a real tracer: both inject AST probes before
    statements, so a loop body records once per loop and a function's own body
    is never probed; `pyvis_v8_1` also marks *every* line above the current one
    as executed. `sys.settrace` gives per-line events per iteration, real call
    depth and return values — `two_sum` records 12 steps, `seen` grows on each
    pass, and the return step reads `↩ returns [0, 1]`.
  - `pyvis_mg` micropip-installs an unpinned `memory-graph` wheel at page load
    and precomputes up to 500 DOT strings. The port builds DOT in JS from the
    tracer's own value nodes, for the current step only: no extra wheel, no
    unpinned dependency, no payload for steps nobody opens. `oid` is emitted
    for containers and objects only, so two independent `5`s are never drawn as
    one shared box.
  - CodeMirror 6 from esm.sh is replaced by the CodeMirror 5 build every other
    engine surface already loads, and the canvas memory diagram is dropped —
    viz-js is the memory renderer, the line view is the other.
- Verified in a browser against both the dev server and the frozen export:
  runtime ready, Trace/step/play/seek, per-iteration steps, changed values
  highlighted, stdout appearing only once its line has run, `IndexError`
  highlighted on the raising line with the stdout printed before it, a
  `SyntaxError` tracing 0 steps, and editing + re-tracing recovering. In the
  aliasing lab's memory view `a` and `b` point at one object while `c[0]` still
  shares `a[0]` and `d` is detached — the whole point of that lab.
- Export: 30 HTML files, `/labs/` and both labs in `sitemap.xml` on the
  canonical origin, `LearningResource` JSON-LD with
  `"learningResourceType": "interactive lab"`.

### 2026-09-17 — cleanup pass

- Ran the kickoff prompt's priority list against the real tree. Decisions are
  now written down in `docs/roadmap.rst` (added to the Sphinx toctree): Labs
  reinstated as the next feature and living at top level (`/labs/<slug>/`),
  Flashcards backlogged, `is_free` kept but defaulted on.
- Deleted the dead weight — `quiz/blocks.py` + `templates/quiz/blocks/`, the
  stale `quiz/views.py` model dump, `quiz/urls.py`, `lms/urls.py`,
  `lms/wagtail_hooks.py`. Grepped before deleting: nothing imported any of them.
- Lucide icons actually load now. `templates/lms/_lucide.html` (CDN + guarded
  `createIcons()`) is included by the four LMS page templates, so icons are only
  fetched where they are used. Verified in a browser against the frozen build:
  every `data-lucide` placeholder becomes a real SVG on `/learn/`, topic, course
  and lesson pages. First attempt used a multi-line `{# … #}` comment — Django
  does not parse those, so the literal comment text shipped into the frozen
  HTML until it became a `{% comment %}`.
- Pruned the 7 junk redirect rows (slug-edit typo fragments). The 4 real
  flat-URL 301s from `coding/migrations/0005` stay. Frozen page count 34 → 27
  and `_redirects` is down to its 4 real lines.
- `CoursePage.is_free` defaulted to `False`, so authored courses shipped
  `"isAccessibleForFree": false` and no "Free" badge; `lms/migrations/0003`
  flips the default and backfills the existing rows. Site Settings docstring
  path corrected to `/cms/settings/home/sitesettings/`.
- Committed the in-flight puput canonical-URL fix on its own.
- Re-verified after the churn: `manage.py check` unchanged (15 treebeard + 1
  `WAGTAILADMIN_BASE_URL`, all pre-existing), 22 tests pass, `distill-local`
  clean, browser smoke over the LMS pages.

### 2026-09-17

- Created this file (DEVLOG prompt introduced this session); backfilled
  2026-09-12 from `git log`.
- Re-verified the pipeline instead of trusting the 4-day-old `_site/`:
  - `distill-local /tmp/pvsite --force` → "Site generation complete" in 5.6 s, 34 HTML files.
  - Live smoke of 22 URLs (Django test client, dev settings): all pages 200;
    `/practice/arrays-and-hashing/two-sum/` → 301 to the flat URL; `/quiz/` and
    `/lms/` → 404; `/cms/` → 302 login.
  - Real browser against the frozen build: PyScript loaded from CDN
    ("PyScript ready"), submitted a working `two_sum` → `✓ Accepted`, 4/4 cases
    (2 hidden masked), `PyverseProgress` stored `ACCEPTED`; Landing strip then
    read solved=1 with the row marked `solved`; quiz graded 2/3 →
    "Not passed — 67% (needs 70%)", "attempt recorded".
- Uncommitted tree changes (`seo_tags.absolute_url` + 4 puput templates) are a
  verified **fix**: puput's `canonical_url`/`entry_url` baked the request host
  (`http://testserver`) and blog-root paths into frozen pages; `{% absolute_url %}`
  / `{% pageurl %}` now emit `https://pyverse.com/python/notes/why-return-matters/`.
  Committed in the cleanup pass below.
- Gaps found while reading — all of these were fixed in the cleanup pass above:
  - lucide icons never load — LMS templates use `<i data-lucide=…>` but no lucide
    script or `createIcons()` exists anywhere.
  - `pyverse/quiz/blocks.py` + `templates/quiz/blocks/*.html` are orphaned: the
    Quiz model has no StreamField (only `true_false` / `mcq` questions).
  - `pyverse/quiz/urls.py` and `pyverse/lms/urls.py` point at a commented-out
    `views.index` and are included nowhere.
  - `pyverse/lms/wagtail_hooks.py` is a stale comment block naming a `TrackPage`
    that no longer exists.
  - `course_page.html` / `lesson_page.html` expose `window.__LESSON_SLUGS__` and
    `__CURRENT_LESSON__`; nothing reads them.
  - 11 `wagtailredirects_redirect` rows are slug-edit typos (`/l`, `/p`, `/py`,
    `/abo`, `/lear`, `/practice/syntax/ni`) and ship as stubs + `_redirects` lines.
  - `home/models.py` SiteSettings docstring says `/admin/settings/…`; the real
    path is `/cms/settings/home/sitesettings/`.

### 2026-09-12 (backfilled from git history — 9 commits)

- `525f2a3` baseline before the DSA slice; pricing removed, puput import fixed.
- `c4aa00e` DSA slice: canonical challenge pages with client-side grading.
- `4a081b0` SEO plumbing: canonical, OG/Twitter, JSON-LD, sitemap.xml, robots.txt.
- `9af7fab` `/about/` served from Wagtail instead of a shadowing TemplateView.
- `f4e957e` static export via django-distill on Django 6.0.7.
- `9dfd31f` Practice section: LeetWasm engine, Landing, Tracks, Sheets.
- `794cb88` Quiz Suite, tag axes, orphan cleanup, flat challenge URLs (+ data
  migration writing redirect rows for the old nested URLs).
- `27d8c1d` homepage nav fixed; templates stopped leaking source into pages.
- `2b73409` one nav everywhere, real page metadata, content for the empty surfaces.

## How it works / how to use it

### Run it locally

- Python 3.14 venv is already at `.venv/` (`uv` works too). Env vars live in
  `.envs/.local/.django` and `.envs/.local/.postgres`; the authoring DB is
  `db.sqlite3` at the repo root.
- `DJANGO_SETTINGS_MODULE` defaults to `config.settings.local` through `manage.py`,
  so: `.venv/bin/python manage.py runserver`.
- `manage.py createsuperuser` for a staff login (one `users_user` row exists).
- AI drafting needs a provider: `AI_PROVIDER=openai AI_MODEL=gpt-4o-mini` (or
  `anthropic`, `ollama`, …) plus that provider's own key env var, or
  `AI_API_KEY` for any of them. Then `.venv/bin/python manage.py ai_create`.
  Without credentials the command fails with the provider's own message; nothing
  else on the site needs a model.

### Where things live in the admin

- Wagtail admin is **`/cms/`** (not `/admin/`). `/admin/` is stock Django admin and
  unused; auth is allauth at `/accounts/`, profile at `/users/<username>/`.
- `/cms/settings/home/sitesettings/` — Site Settings: logo/wordmark, nav CTA,
  default OG image, nav items and footer links (orderable inline children). Single
  source of the nav (`home.context_processors.site_nav`).
- `/cms/snippets/coding/codingproblem/` — Coding Problems (practice corpus).
- `/cms/snippets/quiz/quiz/` — Quizzes (questions + choices are inline children).
- Page tree (`/cms/pages/`): Home → `LMSIndexPage`(Learn) → `TopicPage` →
  `CoursePage` → `LessonPage`; Home → `PracticeHubPage`(Practice) →
  `PracticeTopicPage` (nestable) and `SheetsIndexPage` → `SheetPage`;
  Home → `StandardPage` (About); Home → `BlogFolderPage` (Python) → `BlogPage`
  (Notes) → `EntryPage` (puput).
- Authoring rules that bite:
  - `function_name` must match what the starter code defines; `test_case.input` is
    Python source for the argument list (`"[2, 7, 11, 15], 9"`), `expected_output`
    a Python literal.
  - Comparator decides grading: exact / sorted_list / float_tolerance / custom
    (`compare(actual, expected)` source, exec'd in the learner's browser).
  - Leave at least one test case non-hidden or the learner has nothing to self-check.
  - A problem or quiz with no `topic` is unreachable from any Track or the Landing.
  - A lesson's `practice` block takes **one** problem *or* one quiz (never both —
    the save is rejected); tick `required_to_advance` to gate the next lesson until
    that problem is accepted or that quiz is passed. A `notebook` block's Markdown
    cells render server-side and its code cells run in the learner's browser when
    the learner presses Run.
- `/cms/settings/wagtail_ai/agentsettings/` — the prompts behind the admin AI
  buttons (page title, meta description, content feedback); `/cms/prompt/` holds
  wagtail-ai's reusable Correction/Completion prompts. `manage.py ai_create`
  uses the same provider but its own style guides in
  `pyverse/ai_content/styles/`.

### Static export (production is a static site)

```bash
DJANGO_SETTINGS_MODULE=config.settings.distill \
PYVERSE_CANONICAL_BASE_URL=https://pyverse.com \
.venv/bin/python manage.py distill-local _site --collectstatic --force
```

- `config/settings/distill.py` drops debug toolbar / browser reload, sets DEBUG off,
  enables `DISTILL_ENABLED`, defaults the output dir to `_site/`.
- `pyverse/freeze.py` enumerates every live page (`seo.live_pages()`), problem
  (`live_problems()`) and quiz (`live_quizzes()`) — the same querysets the sitemap
  uses — plus `sitemap.xml`, `robots.txt`, `404.html`, `_redirects`, and one HTML
  redirect stub per Wagtail redirect row.
- `PYVERSE_CANONICAL_BASE_URL` feeds canonical/OG/sitemap URLs; without it
  `seo.base_url()` falls back to the `django.contrib.sites` domain, which cannot
  know the scheme.
- Serve the output locally: `python -m http.server 8000 --directory _site`.
- `--collectstatic` matters on a fresh clone; `_site/` itself is gitignored.

### Learner flow (live site)

`/` → Practice: table of every problem with client-side filter/sort/search and a
stats + streak strip read from IndexedDB → challenge page
`/practice/problem/<slug>/` (description, hints revealed one tier at a time,
CodeMirror editor, Run with ad-hoc args, Submit → per-case log + metrics,
Submissions tab hydrated from IndexedDB; the PyScript runtime must load before
Run/Submit enable) → quiz pages `/practice/quiz/<slug>/` (one question at a time,
pass at `pass_percentage`) → Tracks (topic pages, progress bars) → Sheets
(`/practice/sheets/<slug>/`). Notes/blog live at `/python/notes/`, courses under
`/learn/` — where a lesson can carry a runnable notebook (code cells print in the
page, Markdown rendered server-side) and a graded checkpoint that keeps the
next-lesson link locked until the checkpoint's problem is solved or its quiz is
passed.

## Features

Implemented and observed working end-to-end (verified 2026-09-17):

- Site chrome: nav, footer, CTA and logo from Site Settings; current section marked;
  responsive mobile menu; messages.
- Marketing pages: HomePage (hero, module grid, stats strip), StandardPage (About).
- Practice ecosystem: hub table, Tracks (topic pages aggregating
  `topic__path__startswith`), curated Sheet pages, flat `/practice/problem/<slug>/`
  and `/practice/quiz/<slug>/` URLs, 301s from the retired nested URLs — all in
  the site shell, with the challenge editor/test pane and the quiz stage inside
  framed dark consoles.
- Challenge pages: in-browser grading via PyScript/Pyodide (CDN, pinned 2025.7.3) —
  ACCEPTED / WRONG_ANSWER / RUNTIME_ERROR, per-case pass log with hidden cases
  masked, latency + case metrics, three-tier hints, editorial, solutions, starter
  code, resizable split, Ctrl-Enter to run.
- Quiz pages: plain-JS grading (no Python runtime), true/false + MCQ, optional
  randomization, per-question explanation, pass threshold.
- Progress: one IndexedDB store (`PyverseProgress`: submissions, derived
  `problem_status`, streak) shared by Landing stats, Track bars, Sheet rings, quiz
  cards and the challenge Submissions tab; degrades silently when storage is blocked.
- SEO: canonical, authored-or-derived description, OG/Twitter, per-page `og_image`
  with site default fallback, JSON-LD (Course / BlogPosting / LearningResource),
  `sitemap.xml` (pages + problems + quizzes on the canonical origin), `robots.txt`.
- Static export: 30 frozen HTML files plus static/media, `404.html`, `_redirects`
  (Netlify/Cloudflare 301s), HTML redirect stubs for hosts without redirect rules;
  no request-host leakage after the share-link fix.
- Labs: `/labs/` index plus a per-lab tracer page, both in the site's own shell
  (`home/base_.html` — same navbar, footer and cream brutalist theme as home
  and about), with the tracer in a framed dark console. Line-trace and
  memory-graph views of the same step stream, step/play/seek transport,
  variables with changed-value highlighting, per-step stdout, and the raising
  line marked on error. The program is CMS-authored and editable in the browser
  before re-tracing (`pyverse/labs/`).
- Blog (vendored puput): BlogFolderPage / BlogPage / EntryPage, share links,
  related entries, comments providers, Markdown body field.
- LMS: hub (topic/course counts, featured courses), topic page (course grid), course
  page (hero, what-you'll-learn, prerequisites, lesson list, real lesson count in
  the sidebar), lesson page (rich text, code examples, Mermaid diagrams via CDN,
  callouts, images, **runnable notebooks**, **graded practice checkpoints**) with
  prev/next navigation. Icons render — lucide via CDN, loaded by
  `templates/lms/_lucide.html`. Lesson completion is kept in the shared
  `PyverseProgress` store: the course page counts ticks and a progress bar, the
  lesson page has mark-complete + undo, and the lesson sidebar ticks along. A
  checkpoint marked *required* gates the next-lesson link until its problem or
  quiz reads `solved` in the same store, and notebook code cells run — and print —
  in the learner's browser on the same PyScript runtime the grader and tracer use.
- Auth: allauth login / signup / logout / profile; Wagtail admin login.
- Authoring: Wagtail admin at `/cms/` — pages, snippets, settings, sitemap-driven freeze.
- AI drafting: `manage.py ai_create` (menu → description → verified draft) for
  problems, blog posts, lessons and quizzes; DSA drafts are only saved if the
  generated solution reproduces every generated test case. Admin-side,
  wagtail-ai adds title/meta suggestions (`AITitleFieldPanel` on CodingProblem,
  CoursePage, LessonPage and puput entries; `AIDescriptionFieldPanel` on
  `CoursePage.summary`) and AI completion/correction in every Draftail toolbar.

## Problem it solves

Python learners currently stitch together a course site, a problemset and a notes
blog, and carry separate progress across all three — and every one of those parts
normally needs a server that executes untrusted code. PyVerse puts the guided path,
free practice, quizzes and notes in one place, grades challenges and quizzes
*inside the learner's browser* (Pyodide for code, plain JS for quizzes) so the whole
thing is a static site with no hosting cost and no execution risk on our side, and
it records one progress store that every surface reads — the Landing table, Track
bars, Sheet rings and quiz cards all move together instead of pretending progress is
per-page.

## How to evolve it

### Next, in order

- Deploy the export. Netlify or Cloudflare Pages get real 301s + a root
  `404.html`; GitHub Pages needs the redirect stubs.
- Content: everything else is bottlenecked on 4 problems / 2 quizzes / 1 course /
  2 lessons. Each new problem = one snippet + a topic tag — or one
  `manage.py ai_create` run, reviewed and assigned to a topic.

### Open decisions

- Hidden cases and quiz answer flags ship inside each page payload
  (`grading_payload()` includes `expected` even for hidden cases), so answers are
  readable in page source. That is the accepted cost of spec "approach A"
  client-side grading — live with it, or move grading server-side and lose the
  no-server property.
- Settled: the site theme (`home/base_.html`, Tailwind CDN + inline config) is
  the shell for every learner-facing page, including Practice and Labs, and the
  engine token set in `practice-engine.css` is used only inside `.pe-console`
  panels. What is left is that `base.html`/`pyverse.theme`'s built Tailwind still
  serves the LMS and account pages, so two Tailwind pipelines ship — worth
  collapsing, not worth doing mid-feature.
- CDN runtime dependencies: pyscript.net, cdn.tailwindcss.com, CodeMirror, Mermaid,
  Alpine, lucide, Google Fonts, and viz-js (fetched only when a lab's memory view
  is opened). Offline, the challenge page renders but never enables
  Run/Submit ("Python runtime failed to load" after 45 s). Self-host if that matters.
- Vendored `pyverse/puput/` means upstream puput updates are manual.
- The homepage's live slug is `ghar` (`/home/ghar/`), and the default Wagtail
  "Welcome" page (id 2) is still in the tree — tidy before launch.

### Known rough edges

- `_site/` is stale-but-gitignored; regenerate before any deploy (5.6 s).
- Nothing tests practice, quiz, LMS, Labs or SEO — the only tests are
  cookiecutter's (`tests/`, `pyverse/users/tests/`). The tracer is verified in a
  browser, which is the only place it can run.
- Progress — practice and lessons alike — is per-browser and per-device; there is
  no account-linked progress, and `clear()` wipes both halves at once.
- The required-checkpoint gate is a client-side nudge on the **next-lesson link
  only**: the lesson sidebar, the course page and the course progress bar stay
  open, so it can be walked around in two clicks. A gate that cannot be bypassed
  needs a server, i.e. the same decision as account-linked progress.
- New Tailwind utilities need `manage.py tailwind build` — the built stylesheet is
  gitignored and is not rebuilt by `runserver` alone. A class that is missing from
  it fails silently (the element just renders unstyled).
- `PUPUT_AS_PLUGIN = True` plus the vendored app means puput's own `canonical_url`
  / `entry_url` tags must stay shadowed by `seo_tags.absolute_url` / `{% pageurl %}`.

## Wagtail / Django notes (mention-level)

- `register_setting` + `BaseSiteSetting` + `ClusterableModel`: `home.SiteSettings`
  (branding, CTA, socials, default OG image) at `/cms/settings/home/sitesettings/`.
- Snippets via `SnippetViewSet` + `@register_snippet` (not legacy `register_snippet`
  alone): `coding.CodingProblem` (`/cms/snippets/coding/codingproblem/`),
  `quiz.Quiz` (`/cms/snippets/quiz/quiz/`); both set `list_display` + `search_fields`
  for the AJAX chooser.
- Snippets without viewsets (vendored puput): `puput.Category`, `puput.Tag` (proxy).
- StreamField: `lms.LessonPage.body` (rich text, video, code example, Mermaid,
  callout, image+caption, notebook cells, practice checkpoint),
  `lms.CoursePage.prerequisites` / `what_you_will_learn`,
  `coding.CodingProblem.test_cases` / `constraints` / `hint_tiers` / `editorial`,
  `topics.SheetPage.categories` (SnippetChooserBlock lists), `StandardPage.body`.
- Custom StructBlocks with their own templates: `pyverse/common` (EditorialApproach
  — shared by `coding` and available to `quiz`/`labs`), `coding` (TestCase, Example,
  Hint), `lms` (CodeExample, Mermaid, Callout, ImageWithCaption, Practice,
  NotebookCell). A StructBlock's template is what keeps it in the app that renders
  it: a cross-app block moves to `common/`, a single-app block stays put.
- `SnippetChooserBlock` *inside a page's* StreamField: `PracticeBlock` points at
  one `CodingProblem` or one `Quiz` (never both — `clean()` enforces it), and
  Wagtail resolves the choosers in one batched query per chooser field
  (`StreamValue._prefetch_blocks` → `bulk_to_python`), so N checkpoints on a page
  cost what one costs. Snippet *pages* stay snippets — the checkpoint renders the
  target's `get_absolute_url()`, it does not embed the target.
- Lesson counts without an FK: a lesson's course exists only in the treebeard
  `path`, so `lms/utils.py:lesson_counts_for()` does one descendant query and
  buckets paths by parent (`path[:-Page.steplen]`), then hands each card its number
  through `CoursePage.set_lesson_count()`. `Quiz.question_count` reads an
  `_question_count` annotation when the listing queryset provides one.
- Two progress readers, deliberately: `statusMap()` swallows a blocked store into
  `{}`, `readStatus()` rejects — the checkpoint gate uses the latter so an
  unreadable IndexedDB opens navigation instead of locking it.
- `RoutablePageMixin` + `@route`: `topics.PracticeHubPage` serves
  `/practice/problem/<slug>/` and `/practice/quiz/<slug>/`; `topics.PracticeTopicPage`
  is routable for its subtrees.
- Snippets served as pages via route + `TemplateResponse` (no page model per problem
  or quiz) — `CodingProblem.get_absolute_url()` / `Quiz.get_absolute_url()` are the
  canonical flat URLs used by export and sitemap.
- taggit through-models: `ProblemCompany` / `ProblemPattern` / `ProblemTechnique`
  (`TaggedItemBase` + `ParentalKey`) on `CodingProblem`; `QuizTechnique` on `Quiz`;
  vendored `puput.TagEntryPage`.
- `Orderable` + `ParentalKey` inline children: NavItem, FooterLink, ModuleCard,
  StatItem, Question, Choice, and puput's category/related rows.
- Page tree constraints with `parent_page_types` / `subpage_types` on every page type
  (Home → LMS/Practice/Blog/Standard; the chain down to lessons and sheets).
- `wagtail.contrib.routable_page`, `wagtail.contrib.redirects` (Wagtail's redirects,
  **not** `django.contrib.redirects` — hence the hand-rolled `_redirects` + stubs in
  `freeze.py`), `wagtail.contrib.forms`, `wagtail.snippets.blocks.SnippetChooserBlock`.
- `django.contrib.sitemaps` with custom `Sitemap` subclasses plus a `_CanonicalOrigin`
  mixin pinning `<loc>` to the canonical scheme; `SITEMAPS` shared by the URLconf and
  the export.
- `django-distill`: `distill_path` entries in `freeze.py` (`distill_func` generators,
  `distill_file`, `distill_status_codes=(404,)`), gated behind `DISTILL_ENABLED`;
  `wagtail.views.serve` reused to render each frozen path through the page router.
- One IndexedDB database (`pyverse_progress`, v2) with four stores: practice
  `submissions` / `problem_status` / `streak_meta` plus `lesson_status` for LMS
  lessons. Pages never share a database per feature — a new progress surface
  adds a store and an API method to `static/js/pyverse-progress.js`.
- `django.contrib.sites` for the origin fallback; `Site` lookups via
  `wagtail.models.Site` where the request has no host.
- `{% json_script %}` to bake grading payloads, `PyverseProgress` reading them client-side.
- `wagtailimages` choosers + renditions (`{% image %}`) for hero/OG/header images;
  `og_image` FK on the `SEOFields` mixin shared by HomePage/StandardPage/CoursePage.
- `wagtailsettings_tags` `{% get_settings %}` and `SiteSettings.for_request` /
  `for_site`; `home.context_processors.site_nav` for nav + active section.
- Data migration writing redirect rows: `coding/migrations/0005_flat_problem_url_redirects.py`.
- django-tailwind: `TAILWIND_APP_NAME = "pyverse.theme"`, `{% tailwind_css %}` in
  `templates/base.html`. The built output
  (`pyverse/theme/static/css/dist/styles.css`) is **gitignored** (`.gitignore`'s
  `dist/`) — it is not committed despite what this file said before 2026-09-26 —
  so it must be built (`manage.py tailwind build`, or `manage.py tailwind start`
  as `Procfile.tailwind` does) after any new utility class, and again before
  `--collectstatic` on a fresh clone. The marketing shell instead uses the
  Tailwind CDN with an inline `tailwind.config`.
- Alpine.js for the navbar drawer and messages; allauth templates overridden under
  `pyverse/templates/allauth/`; vendored puput provides blog pages, routes and
  Markdown (`wagtailmarkdown.MarkdownField`) on `EntryPage`.
- `wagtail_hooks.py` exists only in `coding/` and `quiz/`, and only to register the
  two snippets above — no admin-menu or URL hooks. (`lms/wagtail_hooks.py` was a
  stale comment block naming a `TrackPage` that no longer exists; deleted.)
- Labs are page types, not snippets: `labs.LabsIndexPage` → `labs.LabPage`, with
  the program in a plain `TextField` (baked into the page) and `summary` reused
  as the meta description via `seo._DESCRIPTION_ATTRS`.
- Both Labs templates extend `home/base_.html` (the marketing shell with the
  Tailwind CDN config, navbar and footer), not `base.html`. Page chrome is that
  theme; only the tracer console is dark, and `practice-engine.css` +
  `lab-engine.css` are loaded through `{% block extra_head %}` to style it.
- The tracer is `sys.settrace` inside `includes/tracer_runtime.html`, exposed to
  JS as `window._pvTrace()` returning one JSON string — the same bridge shape as
  the grading harness's `window._pyExec`. Frames are filtered by `co_filename`,
  so serialising inside the trace callback cannot recurse; `sys.settrace(None)`
  runs in a `finally` even when the learner's code raises.
- `static/js/lab-engine.js` is one IIFE: CM5 editor, step transport, two
  renderers (source lines + variables + stdout; DOT → SVG via `@viz-js/viz`),
  and keyboard shortcuts bound to the lab root rather than `document`.
- `seo._json_ld` gained a `LabPage` branch (`LearningResource`,
  `learningResourceType: "interactive lab"`); pages need no freeze work because
  `live_pages()` and the sitemap already walk every live page.
- Django admin (`pyverse/*/admin.py`) is untouched cookiecutter stubs.
- `wagtail-ai` (3.1.1) is installed for the admin side: AI title/description
  panels, Draftail completion/correction and the content-feedback agent. It
  needs `wagtail_ai` in `INSTALLED_APPS`, `WAGTAIL_AI["PROVIDERS"]` (one alias,
  `AI_PROVIDER`/`AI_MODEL`/`AI_API_KEY`), and its three migrations applied —
  they create the `Prompt` and `AgentSettings` tables, and without them every
  admin page 500s because the global AI config reads `Prompt`.
- `ai_content` is the only app that talks to a model from the command line:
  `llm.py` wraps wagtail-ai's `get_llm_service(alias)` so both surfaces share
  one provider config, and `AI_CONTENT_COMPLETION_KWARGS` passes provider-specific
  call options without touching code.
- Migration graph warning: `puput/0010_blogfolderpage` (and `lms`, `home`,
  `labs`, `topics` 0001) once depended on
  `wagtailcore.0098_query_searchpromotion_querydailyhits`, a migration no
  released Wagtail ships (7.4.2's latest is
  `0097_baselogentry_uuid_action_timestamp_indexes`; `main`'s 0098 is
  `0098_apitoken`). Any dependency on a nonexistent node makes the *whole* graph
  unloadable, so one bad line breaks `migrate` and every test run. If a
  `NodeNotFoundError` appears again, check the wagtailcore migrations actually
  installed before touching anything else.
- Interpreter note: pydantic ≥ 2.11 calls `typing._eval_type(..., prefer_fwd_module=)`
  whenever `sys.version_info >= (3, 14)`, and CPython 3.14.0rc2 does not accept
  that argument — so wagtail-ai (→ `django-ai-core` → `any-llm` → pydantic)
  cannot even import on a 3.14 *pre-release*. The venv now runs 3.14.7; any
  3.14.0 final or later is fine, an rc is not.
