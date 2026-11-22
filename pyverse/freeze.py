"""Static-export URL set (django-distill), frozen by `manage.py distill-local`.

Only importable while `DISTILL_ENABLED` is set — see `config/urls.py`. The
`<path:path>` catch-all below would otherwise shadow normal serving, so it must
not exist at runtime.

The URL set is *discovered*, not enumerated (see `pyverse.crawl`): the sitemap's
own querysets (`live_pages()` / `live_problems()` / `live_quizzes()`) are only
the **seeds**, and every internal link found in the rendered HTML is followed.
That is what exports routable sub-paths no tree walk can see — blog archives,
dated entry URLs, feeds, challenge pages — and what makes a broken stylesheet,
a missing navbar image or a dead link fail the build instead of shipping.

Pages are rendered by handing the whole path to Wagtail's own serve view, which
resolves routed sub-paths exactly as a live request would.

Static files and uploads are copied by `distill-local` itself (`--collectstatic`
and MEDIA_ROOT); the crawl's part is to prove that every one a page references
exists, so a missing stylesheet or navbar image stops the build.
"""

from functools import lru_cache
from html import escape

from django.contrib.sitemaps import views as sitemap_views
from django.core.management.base import CommandError
from django.http import HttpResponse
from django.urls import resolve
from django.views.defaults import page_not_found
from django_distill import distill_path
from wagtail.views import serve as wagtail_serve

from pyverse.crawl import CrawlResult
from pyverse.crawl import crawl
from pyverse.crawl import page_key
from pyverse.seo import SITEMAPS
from pyverse.seo import live_pages
from pyverse.seo import live_problems
from pyverse.seo import live_quizzes
from pyverse.seo import robots_txt


def serve_exported_page(request, path=""):
    """Render one exported URL exactly as a live request would be dispatched.

    The URL is resolved against the real URLconf, so whatever serves it live
    serves it in the export: Wagtail pages and their routed sub-paths, but also
    plain Django routes such as puput's dated entry URLs and feeds, which
    `wagtail.views.serve` knows nothing about.

    Hard-coding `wagtail_serve` here is what made the blog's archive and entry
    URLs un-exportable.
    """
    match = resolve(request.path_info)
    if match.url_name and match.url_name.startswith("freeze-"):
        # Nothing but this catch-all claims the path (resolving it again would
        # recurse), so let Wagtail produce the canonical 404.
        return wagtail_serve(request, path)
    # Django's handler sets this before calling a view; views such as puput's
    # EntryPageServe branch on `request.resolver_match.url_name`.
    request.resolver_match = match
    return match.func(request, *match.args, **match.kwargs)


def seed_paths():
    """Every page, challenge and quiz the CMS says is live (the sitemap's set).

    Seeds, not the final list: they guarantee that a page nothing links to is
    still exported. Everything *linked* from them is found by the crawl.
    """
    for page in live_pages():
        yield page_key(page.url or "")
    for problem in live_problems():
        yield page_key(problem.get_absolute_url())
    for quiz in live_quizzes():
        yield page_key(quiz.get_absolute_url())


@lru_cache(maxsize=1)
def discovered() -> CrawlResult:
    """Crawl the site once per export; every URL set below reads this result.

    A broken link or asset is a build failure: a static host cannot fix it up
    later, and shipping it is how an unstyled page or a dead navbar image gets
    to production.
    """
    result = crawl(seed_paths())
    if result.errors:
        problems = "\n  ".join(sorted(set(result.errors)))
        count = len(result.errors)
        msg = f"Static export would ship {count} broken reference(s):\n  {problems}"
        raise CommandError(msg)
    return result


def content_paths():
    """One entry per exported page: seeds plus everything reachable by links.

    Reversing `<path:path>` needs at least one character, so the home page is
    served by the empty-route entry below rather than by an empty kwarg.
    """

    for key in sorted(discovered().pages):
        if key:
            yield {"path": key}


def render_sitemap(request):
    return sitemap_views.sitemap(request, SITEMAPS)


def render_404(request):
    """The custom 404 page, so static hosts can serve it for unknown paths."""
    return page_not_found(request, Exception("Not found"))


# ── Redirects ───────────────────────────────────────────────────────────
# `distill-local --generate-redirects` is unusable here: it imports Django's
# own `django.contrib.redirects`, which this project does not install (it uses
# `wagtail.contrib.redirects`). Stubs are generated from Wagtail's rows instead.
#
# Two artifacts, because static hosts differ:
#   * one HTML stub per old path — a meta refresh plus a canonical link, works
#     on any host (GitHub Pages included);
#   * `_redirects` — real 301s on Netlify and Cloudflare Pages.
# Django itself already serves the same rows as 301s while authoring, so the
# old URL resolves in every environment.


def _live_redirects():
    from wagtail.contrib.redirects.models import Redirect  # noqa: PLC0415

    return [row for row in Redirect.objects.all().order_by("old_path") if row.link]


def legacy_redirect_paths():
    """Old paths that must not collide with a real page in the export."""
    taken = set(discovered().pages)
    for row in _live_redirects():
        path = row.old_path.lstrip("/") + "/"
        if path not in taken:
            yield {"path": path}


def render_redirect_stub(request, path=""):
    """A redirect page for hosts that can't issue a 301 of their own."""
    from wagtail.contrib.redirects.models import Redirect  # noqa: PLC0415

    # Stored paths keep their leading slash and drop the trailing one
    # (`Redirect.normalise_path`), while the route kwarg has neither.
    old_path = Redirect.normalise_path("/" + path.lstrip("/"))
    row = Redirect.objects.filter(old_path=old_path).first()
    if row is None or not row.link:
        return page_not_found(request, Exception("Not found"))

    target = escape(row.link, quote=True)
    body = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8" />\n'
        f'<meta http-equiv="refresh" content="0; url={target}" />\n'
        f'<link rel="canonical" href="{target}" />\n'
        '<meta name="robots" content="noindex, follow" />\n'
        f"<title>Moved to {target}</title>\n</head>\n<body>\n"
        f'<p>This page moved to <a href="{target}">{target}</a>.</p>\n'
        "</body>\n</html>\n"
    )
    return HttpResponse(body, content_type="text/html; charset=utf-8")


def render_redirects_file(request):
    """Netlify / Cloudflare Pages redirect rules, one `301` per row."""
    lines = [f"/{row.old_path.lstrip('/')} {row.link} 301" for row in _live_redirects()]
    return HttpResponse(
        "\n".join(lines) + "\n",
        content_type="text/plain; charset=utf-8",
    )


freeze_urlpatterns = [
    # The home page: "" reverses to "/" and renders index.html.
    distill_path(
        "",
        serve_exported_page,
        name="freeze-home",
        distill_func=lambda: None,
        distill_file="index.html",
    ),
    # Every other page, discovered by following links from the seeds.
    distill_path(
        "<path:path>",
        serve_exported_page,
        name="freeze-page",
        distill_func=content_paths,
    ),
    distill_path(
        "sitemap.xml",
        render_sitemap,
        name="freeze-sitemap",
        distill_func=lambda: None,
        distill_file="sitemap.xml",
    ),
    distill_path(
        "robots.txt",
        robots_txt,
        name="freeze-robots",
        distill_func=lambda: None,
        distill_file="robots.txt",
    ),
    # Netlify / GitHub Pages / Cloudflare Pages serve a top-level 404.html for
    # unknown paths, so the export ships one.
    distill_path(
        "404.html",
        render_404,
        name="freeze-404",
        distill_func=lambda: None,
        distill_file="404.html",
        distill_status_codes=(404,),
    ),
    # Redirect rules for hosts that support them (real 301s).
    distill_path(
        "_redirects",
        render_redirects_file,
        name="freeze-redirects-file",
        distill_func=lambda: None,
        distill_file="_redirects",
    ),
    # Redirect stubs for old paths, for hosts that only serve files. Declared
    # last so a real page always wins if a path was reused.
    distill_path(
        "<path:path>",
        render_redirect_stub,
        name="freeze-redirect-stub",
        distill_func=legacy_redirect_paths,
        distill_file="{path}index.html",
    ),
]
