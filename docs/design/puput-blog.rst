Puput blog integration
======================

Aim / use case
--------------

The site needs a notes/blog: long-form prose entries under ``/python/notes/``,
with Markdown bodies, categories, tags, related entries, an archive, feeds and
share links. This is the "reading" surface alongside Practice and Learn.

Design
------

Vendored, not pip-installed
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The blog engine is **vendored**: puput's source lives in-tree at
``pyverse/puput/`` and is renamed to the ``pyverse.puput`` app
(``apps.py``: ``name = "pyverse.puput"``). It is **not** a ``pyproject.toml``
dependency — there is no ``puput`` line in the dependency list, and no ``puput``
package in ``uv.lock``. ``wagtail-markdown`` *is* a real dependency, because the
vendored ``EntryPage`` uses its ``MarkdownField``.

The vendored source carries upstream's identity: ``pyverse/puput/__init__.py``
records ``__author__ = "Marc Tudurí"`` and ``__version__ = "2.2.0"``.

**Why it was vendored rather than installed is not documented in this
repository.** Neither the dev log nor a code comment states the original reason
(patched behaviour? a Wagtail-version incompatibility? the need for a
``BlogFolderPage`` that upstream does not have?). The observable facts are: the
copy exists, it is namespaced under ``pyverse.``, and it has been modified
(see below). The rationale would live in the build spec
(``pyverse-requirements-v2.md``), which is not in the repo.

Page types
~~~~~~~~~~

.. code-block:: text

   Home
   └── Python  (puput.BlogFolderPage, max_count=1)
       └── Notes  (puput.BlogPage, BlogRoutes)
           └── Entry (puput.EntryPage)

``pyverse/puput/models.py``:

* ``BlogFolderPage`` — the top-level folder. Overrides ``parent_page_types =
  ["home.HomePage"]`` and ``subpage_types = ["puput.BlogPage"]`` explicitly to
  "lock down the tree architecture", sets ``max_count = 1`` and clears
  ``settings_panels``. This model is **not upstream puput** — it is a local
  addition (migration ``0010_blogfolderpage``).
* ``BlogPage`` — one blog, using ``BlogRoutes`` mixin plus the ``Blog``
  abstract. ``subpage_types = ["puput.EntryPage"]``.
* ``EntryPage`` — one post. Uses the ``Entry`` abstract, which provides
  ``markdown_body`` (``wagtailmarkdown.MarkdownField``), ``tags``
  (``ClusterTaggableManager`` through ``puput.TagEntryPage``), ``date``,
  ``excerpt`` (``RichTextField``), ``categories`` (M2M through
  ``puput.CategoryEntryPage``) and ``header_image``. Adds Wagtail search fields
  and ``get_sitemap_urls``.

Support models: ``Category`` and ``Tag`` are registered as snippets *without*
viewsets ("Snippets without viewsets (vendored puput)" — DEVLOG).
``EntryPageRelated`` models related entries; ``CategoryEntryPage`` and
``TagEntryPage`` are the through rows.

Other pieces: ``routes.py`` (``BlogRoutes``), ``feeds.py`` (RSS), ``comments.py``
(two providers — Disqus and django_comments), ``urls.py``
(``get_entry_url``), ``templatetags/puput_tags.py``.

``PUPUT_AS_PLUGIN = True``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Set in ``config/settings/base.py``. This tells the vendored ``urls.py`` to skip
registering Wagtail's URL modules itself (the project's own ``config/urls.py``
includes them) and instead just be includable at the root. The DEVLOG records
the consequence: "``PUPUT_AS_PLUGIN = True`` plus the vendored app means puput's
own ``canonical_url`` / ``entry_url`` tags must stay shadowed by
``seo_tags.absolute_url`` / ``{% pageurl %}``."

Local modifications to upstream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The vendored copy is not a pristine 2.2.0. Known local changes:

* ``BlogFolderPage`` added (upstream has no folder layer).
* The app renamed to ``pyverse.puput`` throughout.
* ``AITitleFieldPanel`` imported into ``abstracts.py`` — wagtail-ai panels on
  entry titles.
* Blog share/entry links emit canonical-origin URLs instead of request-host
  URLs (the fix described next).

The canonical-URL bug
~~~~~~~~~~~~~~~~~~~~~

The DEVLOG records a verified fix: "puput's ``canonical_url``/``entry_url`` tags
baked the request host (``http://testserver``) and blog-root paths into frozen
pages; ``{% absolute_url %}`` / ``{% pageurl %}`` now emit
``https://pyverse.com/python/notes/why-return-matters/``."

The cause is in ``pyverse/puput/templatetags/puput_tags.py``: ``canonical_url``
calls ``context.request.build_absolute_uri(...)``, and ``entry_url`` resolves
through ``get_entry_url(...)`` against the site's root page. The DEVLOG groups
both as the tags that baked the request host and blog-root paths into frozen
pages. During a static export the request host is the build server, and freezing
that into the HTML would ship ``http://testserver`` links to production. The
project's own ``home/templatetags/seo_tags.py`` provides ``absolute_url``, which
resolves against ``seo.canonical_for`` — the configured canonical origin — and
its docstring states exactly this: "puput's own tag uses
``request.build_absolute_uri``, which stamped ``http://testserver`` into every
frozen share link."

The four vendored templates (``blog_page.html``, ``entry_page.html`` and their
share-link includes) were changed to use ``{% absolute_url %}`` /
``{% pageurl %}``. This is the concrete cost of vendoring expressed as a
standing constraint: the shadow must not be reverted by an upstream merge.

Alternatives considered
-----------------------

*``wagtail-code-blog``.* "The earlier ``wagtail-code-blog`` recommendation is
superseded; puput is vendored and working, so no second engine goes on top of
it" (``docs/roadmap.rst``). The earlier recommendation is recorded; the reason
puput won over it is not elaborated in-repo beyond "working".

*A pip-installed puput.* Rejected or abandoned — but the *reason* is not in the
repo (see above). A pip install would track upstream automatically; the
consequence of the vendored choice is stated plainly in the DEVLOG's open
decisions: "Vendored ``pyverse/puput/`` means upstream puput updates are manual."

*Building a blog app on Wagtail pages + StreamField.* Rejected implicitly: the
site already uses StreamField for lessons and problems, but puput supplies
Markdown authoring, categories, tags, archives, feeds, related entries and
comment providers out of the box. Reimplementing those is real work for no
differentiation.

*Disqus / django_comments.* Both providers exist in ``comments.py``. Neither is
enabled by default: ``BlogAbstract.display_comments`` defaults to ``False``, and
django_comments is not installed (the provider raises if imported).

Trade-offs accepted
-------------------

*Manual upstream updates.* No ``pip install -U puput``. Bringing in an upstream
release means diffing ``pyverse/puput/`` against the release and re-applying the
local changes (the ``BlogFolderPage`` addition, the ``pyverse.`` rename, the AI
panel import, the URL-tag shadow). The DEVLOG lists this as an explicit open
decision cost.

*Fork drift is invisible.* There is no recorded upstream commit hash — only
``__version__ = "2.2.0"``. It is not stated which upstream commit the copy came
from or whether it includes post-2.2.0 fixes.

*Two URL-tag systems coexist.* ``puput_tags.entry_url`` /
``canonical_url`` still exist; the templates use ``seo_tags.absolute_url``
instead. A future edit that "simplifies" a template back to the puput tag
silently reintroduces request-host URLs into the frozen export. The DEVLOG calls
this out as a standing constraint.

*Comments need a backend.* The site is a static export; a comment form cannot
post anywhere. Disqus is the only provider that could work (third-party
JavaScript), and it is off by default.

*Sitemap integration is split.* ``EntryPage.get_sitemap_urls`` builds its own
URLs via ``get_entry_url`` while the project's ``seo.py`` sitemaps handle pages,
problems and quizzes. Blog entries are live pages, so they also appear in
``LivePageSitemap`` — the two mechanisms could disagree if the frozen export and
puput's own sitemap logic diverge (the project serves ``seo.SITEMAPS``, so
``get_sitemap_urls`` is not actually used).

When to revisit
---------------

* When an upstream puput release carries a fix or feature worth taking. The
  re-vendor cost is the diff against local changes plus re-verifying the
  canonical-URL shadow.
* If the blog ever needs StreamField authoring or non-Markdown blocks, the
  vendored ``EntryAbstract`` body would have to change — a deeper divergence from
  upstream.
* If comments are ever wanted in production. That requires a third-party embed
  (Disqus) or moving off the static export.
