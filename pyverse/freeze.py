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

from django.contrib.sitemaps import views as sitemap_views
from django.views.defaults import page_not_found
from django_distill import distill_path
from wagtail.views import serve as wagtail_serve

from pyverse.seo import SITEMAPS
from pyverse.seo import live_pages
from pyverse.seo import live_problems
from pyverse.seo import robots_txt


def serve_exported_page(request, path=""):
    """Render one exported URL through Wagtail's page router.

    `path` is what Django's `<path:path>` converter captured — the site-relative
    URL without a leading slash, exactly what `wagtail.views.serve` expects.
    The home page arrives as ``""`` from its own route.
    """
    return wagtail_serve(request, path)


def content_paths():
    """One entry per page and per challenge, minus the home page.

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


def render_sitemap(request):
    return sitemap_views.sitemap(request, SITEMAPS)


def render_404(request):
    """The custom 404 page, so static hosts can serve it for unknown paths."""
    return page_not_found(request, Exception("Not found"))


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
]
