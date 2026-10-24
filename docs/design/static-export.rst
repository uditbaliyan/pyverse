Static export pipeline
======================

Aim / use case
--------------

Production is a static site: Wagtail and the database exist only while
authoring, and the deployable artifact is a tree of HTML files plus
``static/`` and ``media/``. The pipeline must turn every live page, challenge
and quiz into a file, generate ``sitemap.xml``/``robots.txt``/``404.html``, and
keep old URLs alive on hosts that cannot issue a server-side 301.

Design
------

``django-distill``
~~~~~~~~~~~~~~~~~~

The export is ``manage.py distill-local`` (``django-distill>=3.2.7``). The
command is invoked against a dedicated settings module so nothing dev-only can
leak into the frozen markup:

.. code-block:: bash

   DJANGO_SETTINGS_MODULE=config.settings.distill \
   PYVERSE_CANONICAL_BASE_URL=https://pyverse.com \
   .venv/bin/python manage.py distill-local _site --collectstatic --force

``config/settings/distill.py`` makes four changes from ``local``:

* Debug toolbar and browser reload are removed and ``DEBUG`` is off — "their
  markup, plus Django's debug pages, can never be frozen into a public build."
* ``ALLOWED_HOSTS = ["*"]`` ("Distill's renderer already forces this; being
  explicit keeps collectstatic and any stray request on the same footing").
* ``INSTALLED_APPS += ["django_distill"]`` — "without this ``manage.py
  distill-local`` is reported as unknown."
* ``DISTILL_ENABLED = True``, ``DISTILL_DIR = _site``,
  ``DISTILL_SKIP_ADMIN_DIRS = True`` ("Admin/static bundling for the Django and
  Wagtail admin is dead weight in a static export; only the site's own assets
  are copied").

``config/urls.py`` registers ``freeze_urlpatterns`` **only** when
``DISTILL_ENABLED`` is set — "because the ``<path:path>`` entry below would
otherwise shadow normal serving."

What gets written
~~~~~~~~~~~~~~~~~~

``pyverse/freeze.py`` decides the URL set. Every URL comes from
``pyverse/seo.py``'s ``live_pages()`` / ``live_problems()`` / ``live_quizzes()``
— the same enumerations ``sitemap.xml`` uses, "so the sitemap and the frozen file
tree cannot drift apart" (``freeze.py`` docstring).

* ``content_paths()`` yields one entry per live page (minus home, which is
  served by the empty-route entry), plus every problem and quiz at its
  ``get_absolute_url()``.
* ``serve_exported_page`` hands each path to ``wagtail.views.serve`` — "Challenge
  pages need no special casing here: they are routed sub-paths served by
  ``PracticeTopicPage.route()``, so handing the whole path to Wagtail's own
  serve view resolves them exactly as a live request would."

``freeze_urlpatterns`` is a list of ``distill_path`` entries:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Route
     - Purpose
   * - ``""`` → ``index.html``
     - Home page. Reversing ``<path:path>`` needs at least one character, so
       home gets its own empty-route entry.
   * - ``<path:path>`` → ``serve_exported_page``
     - Every other page, challenge and quiz.
   * - ``sitemap.xml``
     - ``render_sitemap`` via ``django.contrib.sitemaps.views``.
   * - ``robots.txt``
     - ``pyverse.seo.robots_txt``.
   * - ``404.html``
     - The custom 404, with ``distill_status_codes=(404,)``, because Netlify /
       GitHub Pages / Cloudflare Pages serve a root ``404.html``.
   * - ``_redirects``
     - Real 301s for Netlify and Cloudflare Pages.
   * - ``<path:path>`` → ``render_redirect_stub``
     - One HTML meta-refresh stub per old path, for hosts that only serve
       files. Declared **last** so a real page always wins if a path was reused.

Canonical origin
~~~~~~~~~~~~~~~~

``PYVERSE_CANONICAL_BASE_URL`` fixes the origin used by canonical links,
OpenGraph URLs and ``sitemap.xml``. Without it, ``seo.base_url()`` falls back to
the ``django.contrib.sites`` domain, "which cannot know the scheme" (README).
``_CanonicalOrigin`` in ``seo.py`` pins ``<loc>`` to the same origin the
canonical tags use.

Redirects — hand-rolled, not distill's
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``distill-local --generate-redirects`` is unusable here. The comment in
``freeze.py`` states why: "it imports Django's own ``django.contrib.redirects``,
which this project does not install (it uses ``wagtail.contrib.redirects``)."
The workaround produces two artifacts:

* one HTML stub per old path — meta refresh plus canonical link, works on any
  host including GitHub Pages;
* ``_redirects`` — real 301s on Netlify and Cloudflare Pages.

Django itself already serves the same Wagtail ``Redirect`` rows as 301s while
authoring, so an old URL resolves in every environment. ``legacy_redirect_paths``
also skips any old path that collides with a real exported page
(``_exported_page_paths``), so a reused path is never shadowed by a stub.

The one gotcha not in ``freeze.py``: the frozen ``404.html`` only works on hosts
that use a root ``404.html``; a host wanting a different filename needs the
mapping configured (README).

Django 6.0.7 compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

The project runs ``django==6.0.7`` with ``django-distill>=3.2.7``. The risk that
distill would not support Django 6.x is **analysed in the build spec
(``pyverse-requirements-v2.md``), which is not in this repository** — the dev log
records that the spec is external and says "Find it before re-deriving design
decisions." What is observable in-repo is how it actually resolved: the export
runs clean on Django 6.0.7, and the dev log records a verification run —
``distill-local /tmp/pvsite --force`` → "Site generation complete" in 5.6 s, 34
HTML files. Every migration in the repo is stamped "Generated by Django 6.0.7",
so the whole model layer is authored against that version.

Alternatives considered
-----------------------

*Server-side rendering in production.* Rejected: the project's premise is no
server, no hosting cost, no execution risk. See ``progress-tracking.rst`` and
``grading-engine.rst`` for the two subsystems that depend on this.

*``distill-local --generate-redirects``.* Rejected — incompatible with
``wagtail.contrib.redirects`` (see above). The hand-rolled stubs plus
``_redirects`` reproduce the same behaviour without installing Django's redirect
app.

*A separate static site generator (Hugo, Eleventy).* Would duplicate the content
model in a second system; Wagtail's page tree and the freeze enumeration already
answer "what exists". The export is a build step, not a second site.

*Enumerating URLs by hand or by crawling.* Rejected: share the querysets with
``sitemap.xml`` so the two cannot drift. The docstring makes this binding.

Trade-offs accepted
-------------------

*The frozen tree is only as fresh as the last run.* ``_site/`` is gitignored and
"stale-but-gitignored; regenerate before any deploy (5.6 s)" (DEVLOG). There is
no CI deploy in the repo.

*Distill walks the whole site per build.* Every page, problem and quiz is
rendered through Wagtail's serve view. At the current corpus (30-ish files) this
is seconds; it scales linearly with content.

*Redirect stubs are duplicated content.* A host with real 301 support ignores
the stubs, but they are still written into the tree. ``legacy_redirect_paths``
guards against collisions with real pages, but the stubs are dead weight on
Netlify/Cloudflare.

*No server means no dynamic 404, no search, no forms.* ``wagtail.contrib.forms``
is installed, but form submissions need a backend; a frozen form cannot post
anywhere.

When to revisit
---------------

* When the site is actually deployed to a host. The host choice is still open
  (``docs/roadmap.rst``: "Which host serves the export (real 301s vs. redirect
  stubs)"). If the host supports real 301s, the stub generation is dead weight;
  if it only serves files (GitHub Pages), the stubs are load-bearing.
* When the build time stops being negligible. Not close at the current corpus.
* If Django is upgraded past 6.x and django-distill lags. The compatibility
  question would move from "spec analysis" to a concrete breakage; the fallback
  is to pin Django or to replace distill with a hand-written
  ``render-to-file`` script (the URL enumeration in ``freeze.py`` is already
  independent of distill).
