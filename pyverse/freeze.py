"""Static-export URL set (django-distill), frozen by `manage.py distill-local`.

Only importable while `DISTILL_ENABLED` is set — see `config/urls.py`. The
`<path:path>` catch-all below would otherwise shadow normal serving, so it must
not exist at runtime.

Every URL comes from `pyverse.seo.live_pages()` / `live_problems()`, the same
enumerations `sitemap.xml` uses, so the sitemap and the frozen file tree cannot
drift apart.

Challenge pages need no special casing here: they are routed sub-paths served by
`PracticeTopicPage.route()`, so handing the whole path to Wagtail's own serve
view resolves them exactly as a live request would.
"""

from html import escape

from django.contrib.sitemaps import views as sitemap_views
from django.http import HttpResponse
from django.views.defaults import page_not_found
from django_distill import distill_path
from wagtail.views import serve as wagtail_serve

from pyverse.seo import SITEMAPS
from pyverse.seo import live_pages
from pyverse.seo import live_problems
from pyverse.seo import live_quizzes
from pyverse.seo import robots_txt


def serve_exported_page(request, path=""):
    """Render one exported URL through Wagtail's page router.

    `path` is what Django's `<path:path>` converter captured — the site-relative
    URL without a leading slash, exactly what `wagtail.views.serve` expects.
    The home page arrives as ``""`` from its own route.
    """
    return wagtail_serve(request, path)


def content_paths():
    """One entry per page, challenge and quiz, minus the home page.

    Reversing `<path:path>` needs at least one character, so the home page is
    served by the empty-route entry below rather than by an empty kwarg.
    """
    for page in live_pages():
        relative = (page.url or "").lstrip("/")
        if relative:
            yield {"path": relative}
    for problem in live_problems():
        relative = problem.get_absolute_url().lstrip("/")
        if relative:
            yield {"path": relative}
    for quiz in live_quizzes():
        relative = quiz.get_absolute_url().lstrip("/")
        if relative:
            yield {"path": relative}


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
    from wagtail.contrib.redirects.models import Redirect

    return [row for row in Redirect.objects.all().order_by("old_path") if row.link]


def _exported_page_paths():
    paths = {(page.url or "").lstrip("/") for page in live_pages()}
    paths |= {problem.get_absolute_url().lstrip("/") for problem in live_problems()}
    paths |= {quiz.get_absolute_url().lstrip("/") for quiz in live_quizzes()}
    return paths


def legacy_redirect_paths():
    """Old paths that must not collide with a real page in the export."""
    taken = _exported_page_paths()
    for row in _live_redirects():
        path = row.old_path.lstrip("/") + "/"
        if path not in taken:
            yield {"path": path}


def render_redirect_stub(request, path=""):
    """A redirect page for hosts that can't issue a 301 of their own."""
    from wagtail.contrib.redirects.models import Redirect

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
    # Every other page, and every challenge page.
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
