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
`/learn/`.

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
  page (hero, what-you'll-learn, prerequisites, lesson list), lesson page
  (rich text, code examples, Mermaid diagrams via CDN, callouts, images) with
  prev/next navigation. Icons render — lucide via CDN, loaded by
  `templates/lms/_lucide.html`. Lesson completion is kept in the shared
  `PyverseProgress` store: the course page counts ticks and a progress bar, the
  lesson page has mark-complete + undo, and the lesson sidebar ticks along.
- Auth: allauth login / signup / logout / profile; Wagtail admin login.
- Authoring: Wagtail admin at `/cms/` — pages, snippets, settings, sitemap-driven freeze.

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
  2 lessons. Each new problem = one snippet + a topic tag.

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
- StreamField: `lms.LessonPage.body` (rich text, code example, Mermaid, callout,
  image+caption), `lms.CoursePage.prerequisites` / `what_you_will_learn`,
  `coding.CodingProblem.test_cases` / `constraints` / `hint_tiers` / `editorial`,
  `topics.SheetPage.categories` (SnippetChooserBlock lists), `StandardPage.body`.
- Custom StructBlocks with their own templates: `coding` (TestCase, Example, Hint,
  EditorialApproach), `lms` (CodeExample, Mermaid, Callout, ImageWithCaption).
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
  `templates/base.html`, built output committed at
  `pyverse/theme/static/css/dist/styles.css`; marketing shell instead uses the
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
