"""Canonical URL, social-preview and structured-data plumbing.

One module owns "how a page describes itself to crawlers and social cards", so
`base.html`, `robots.txt` and `sitemap.xml` can never disagree about the origin.

Nothing here writes to the database, so it needs no migrations: it reads
Wagtail's built-in `seo_title` / `search_description` promote fields first and
falls back to per-model fields (course summary, post excerpt, problem
statement…) so meta descriptions are templated rather than hand-written.
"""

from __future__ import annotations

import json
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.utils.html import strip_tags
from wagtail.models import Page

DESCRIPTION_LIMIT = 160

# Fallback order for a page's meta description. `search_description` is
# Wagtail's promote-panel field, so an author's explicit choice always wins;
# the rest are per-model conveniences. StreamFields are handled separately.
_DESCRIPTION_ATTRS = (
    "search_description",
    "excerpt",  # puput EntryPage
    "description",  # puput BlogPage, CodingProblem
    "summary",  # lms.CoursePage
    "intro",  # lms.LMSIndexPage, topics.PracticeHubPage
    "hero_subtitle",  # home.HomePage
    "theory_content",  # topics.PracticeTopicPage
    "body",  # home.StandardPage
)


# ── Origin ──────────────────────────────────────────────────────────────
def base_url(request=None):
    """Absolute origin for canonical, OpenGraph and sitemap URLs.

    `PYVERSE_CANONICAL_BASE_URL` wins when set — a static export must pin the
    production origin, since no request host survives the freeze. Otherwise the
    `django.contrib.sites` domain is used, which is the same record Django's
    sitemap view reads, so the two cannot drift apart.
    """
    configured = getattr(settings, "PYVERSE_CANONICAL_BASE_URL", "") or ""
    if configured:
        return configured.rstrip("/")

    site = get_current_site(request) if request is not None else _default_site()
    if site is None or not site.domain:
        return ""

    scheme = "http" if settings.DEBUG else "https"
    return f"{scheme}://{site.domain}".rstrip("/")


def _default_site():
    from django.contrib.sites.models import Site

    return Site.objects.filter(pk=settings.SITE_ID).first()


def canonical_for(request, page=None, routed_path=None):
    """Canonical URL for a page, or for a routed sub-path (challenge pages)."""
    origin = base_url(request)
    if not origin:
        return ""
    if routed_path:
        return origin + routed_path
    return origin + (page.url or "") if page is not None else ""


# ── Text helpers ────────────────────────────────────────────────────────
_BLOCK_BOUNDARY = re.compile(
    r"</(?:p|li|ul|ol|div|h[1-6]|tr|blockquote|pre)\s*>|<br\s*/?>",
    re.IGNORECASE,
)


def _plain(value):
    """HTML → single-line text, keeping block boundaries as word gaps.

    Without the substitution, `<li>Return the string</li><li>Use one space</li>`
    collapses to "stringUse", which reads as a typo in a meta description.
    """
    html = _BLOCK_BOUNDARY.sub(" ", str(value or ""))
    return " ".join(strip_tags(html).split())


def _clamp(text, limit=DESCRIPTION_LIMIT):
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"


def _stream_text(value):
    """First rich-text block of a StreamField body, as plain text."""
    for child in value or []:
        if child.block_type == "text":
            return _plain(child.value)
    return ""


def _first_text(*candidates):
    for candidate in candidates:
        text = _plain(candidate)
        if text:
            return text
    return ""


# ── Per-entity metadata ─────────────────────────────────────────────────
def _problem_description(problem):
    return _clamp(_plain(problem.description)) if problem is not None else ""


def _quiz_description(quiz):
    if quiz is None:
        return ""
    text = _plain(quiz.instructions) or _plain(
        f"{quiz.question_count} question quiz",
    )
    return _clamp(text)


def _page_description(page):
    if page is None:
        return ""
    explicit = _plain(getattr(page, "search_description", ""))
    if explicit:
        return _clamp(explicit)

    for attr in _DESCRIPTION_ATTRS:
        if attr == "search_description":
            continue
        if hasattr(page, attr):
            text = _plain(getattr(page, attr))
            if text:
                return _clamp(text)

    return _clamp(_stream_text(getattr(page, "body", None)))


def _description(page=None, problem=None, request=None, quiz=None):
    """First authored description that exists, then the site-wide fallback."""
    return (
        _problem_description(problem)
        or _quiz_description(quiz)
        or _page_description(page)
        # Editable in Wagtail under Settings → Site settings.
        or _clamp(getattr(_site_settings(request), "footer_tagline", ""))
    )


def _site_settings(request):
    from pyverse.home.models import SiteSettings

    if request is not None:
        return SiteSettings.for_request(request)
    return SiteSettings.for_site(_default_wagtail_site())


def _default_wagtail_site():
    from wagtail.models import Site as WagtailSite

    return (
        WagtailSite.objects.filter(is_default_site=True).first()
        or WagtailSite.objects.first()
    )


def _image_url(image, base):
    if not image:
        return ""
    try:
        url = image.get_rendition("1200x630").url
    except (AttributeError, OSError, ValueError):
        # Missing file, unusable image, or a filter the storage can't honour:
        # a broken social card is not worth a 500 on the page itself.
        url = getattr(image, "url", "")
    if not url:
        return ""
    return base + url if url.startswith("/") else url


def _social_image(page, problem, request, base):
    for candidate in (
        getattr(problem, "og_image", None) if problem is not None else None,
        getattr(page, "og_image", None),
        getattr(page, "header_image", None),
    ):
        url = _image_url(candidate, base)
        if url:
            return url
    return _image_url(_site_settings(request).default_og_image, base)


def _title(page, problem, site_name, override=None, quiz=None):
    if override:
        title = override
    elif problem is not None:
        title = f"{problem.title} · {page.title}" if page is not None else problem.title
    elif quiz is not None:
        title = f"{quiz.title} · {page.title}" if page is not None else quiz.title
    elif page is not None:
        title = _first_text(getattr(page, "seo_title", ""), page.title)
    else:
        title = site_name
    if site_name and title and site_name.lower() not in title.lower():
        return f"{title} · {site_name}"
    return title


# ── Structured data ─────────────────────────────────────────────────────
def _json_ld(page, problem, canonical, request=None, quiz=None):
    """Course / BlogPosting / LearningResource, per spec §15.3."""
    from pyverse.labs.models import LabPage
    from pyverse.lms.models import CoursePage
    from pyverse.puput.models import EntryPage

    origin = base_url(request)
    site_name = getattr(settings, "WAGTAIL_SITE_NAME", "PyVerse")
    publisher = {"@type": "Organization", "name": site_name, "url": origin}

    if problem is not None:
        payload = {
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": problem.title,
            "description": _description(page, problem, request),
            "url": canonical,
            "learningResourceType": "coding challenge",
            "educationalLevel": problem.get_difficulty_display(),
            "isAccessibleForFree": True,
            "inLanguage": "en",
            "provider": publisher,
        }
    elif quiz is not None:
        payload = {
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": quiz.title,
            "description": _description(page, request=request, quiz=quiz),
            "url": canonical,
            "learningResourceType": "quiz",
            "educationalLevel": quiz.get_difficulty_display(),
            "isAccessibleForFree": True,
            "inLanguage": "en",
            "provider": publisher,
        }
    elif isinstance(page, CoursePage):
        payload = {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": page.title,
            "description": _description(page, request=request),
            "url": canonical,
            "provider": publisher,
            "isAccessibleForFree": page.is_free,
            "educationalLevel": page.get_difficulty_display(),
            "inLanguage": "en",
        }
        if page.estimated_hours:
            payload["hasCourseInstance"] = [
                {
                    "@type": "CourseInstance",
                    "courseMode": "online",
                    "courseWorkload": f"PT{page.estimated_hours}H",
                },
            ]
    elif isinstance(page, LabPage):
        payload = {
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": page.title,
            "description": _description(page, request=request),
            "url": canonical,
            "learningResourceType": "interactive lab",
            "educationalLevel": page.get_difficulty_display(),
            "isAccessibleForFree": True,
            "inLanguage": "en",
            "provider": publisher,
        }
    elif isinstance(page, EntryPage):
        payload = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": page.title,
            "description": _description(page, request=request),
            "url": canonical,
            "mainEntityOfPage": canonical,
            "datePublished": _iso(page.first_published_at or page.date),
            "dateModified": _iso(page.last_published_at or page.date),
            "inLanguage": "en",
            "publisher": publisher,
        }
        image = _image_url(getattr(page, "header_image", None), origin)
        if image:
            payload["image"] = image
    else:
        return ""

    # `</script>` inside a JSON string would end the tag early; `\u003c` cannot.
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def _iso(value):
    return value.isoformat() if value else ""


# ── The one entry point templates use ───────────────────────────────────
def meta_for(request, page=None, problem=None, quiz=None, overrides=None):
    """Everything the `<head>` needs, derived from whatever context exists.

    `overrides` carries an explicit title/description for views that render no
    Wagtail page (a plain TemplateView), so they can still get a canonical URL
    and social card without a Page row behind them.
    """
    overrides = overrides or {}
    title = overrides.get("title")
    description = overrides.get("description")
    site_name = getattr(settings, "WAGTAIL_SITE_NAME", "PyVerse")
    origin = base_url(request)

    # Routed sub-pages (challenges, quizzes) are canonical at their own path,
    # not at the hub page that owns the route — check them first.
    if request is not None and (problem is not None or quiz is not None):
        canonical = canonical_for(request, routed_path=request.path)
    elif page is not None:
        canonical = canonical_for(request, page=page)
    elif request is not None and (title or description):
        # A non-page view that declared its own title/description (plain
        # TemplateView) is a real content page: its request path is canonical.
        # Anything else — every error page — gets no canonical, because
        # pointing at a URL that does not exist helps nobody.
        canonical = canonical_for(request, routed_path=request.path)
    else:
        canonical = ""

    # Only claim indexability for a real content object. For everything else
    # (plain TemplateViews, and every error page — Wagtail's catch-all makes an
    # unmatched URL indistinguishable from a matched route that 404s) the meta
    # tag is omitted: the HTTP status code is what actually governs crawlers,
    # and a wrong robots directive is worse than none.
    robots = (
        "index, follow"
        if (page is not None or problem is not None or quiz is not None)
        else ""
    )

    return {
        "title": _title(page, problem, site_name, override=title, quiz=quiz),
        "description": description or _description(page, problem, request, quiz) or "",
        "canonical": canonical,
        "og_type": "article" if _is_blog_entry(page) else "website",
        "image": _social_image(page, problem, request, origin),
        "site_name": site_name,
        "robots": robots,
        "json_ld": _json_ld(page, problem, canonical, request, quiz),
    }


def _is_blog_entry(page):
    from pyverse.puput.models import EntryPage

    return isinstance(page, EntryPage)


# ── robots.txt ──────────────────────────────────────────────────────────
def robots_txt(request):
    """Plain-text crawler policy. Frozen to /robots.txt by the static export.

    AI crawlers (GPTBot, ClaudeBot, PerplexityBot…) inherit the `*` stanza and
    are deliberately allowed: the content is free, and being cited in AI
    answers is reachable traffic rather than lost traffic.
    """
    admin_path = (getattr(settings, "ADMIN_URL", "admin/") or "admin/").strip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Disallow: /{admin_path}/",
        "Disallow: /cms/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {base_url(request)}/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


# ── What exists (shared by the sitemap and the static export) ───────────
def live_pages():
    """Live, publicly served pages under the configured site root.

    `path__startswith(root.path)` includes the root itself and excludes pages
    above it — those are not routable (the cookiecutter "Welcome" page is a
    live page whose URL 404s), so they must be neither advertised in the
    sitemap nor written to the static export.
    """
    site = _default_wagtail_site()
    queryset = Page.objects.live().public()
    if site is not None and site.root_page_id:
        queryset = queryset.filter(path__startswith=site.root_page.path)
    return queryset.order_by("path")


def live_problems():
    """Coding problems reachable at a canonical challenge URL."""
    from pyverse.coding.models import CodingProblem

    return (
        CodingProblem.objects.filter(topic__isnull=False, topic__live=True)
        .select_related("topic")
        .order_by("slug")
    )


def live_quizzes():
    """Quizzes reachable at a canonical quiz URL."""
    from pyverse.quiz.models import Quiz

    return (
        Quiz.objects.filter(topic__isnull=False, topic__live=True)
        .select_related("topic")
        .order_by("title")
    )


# ── sitemap.xml ─────────────────────────────────────────────────────────
class _CanonicalOrigin:
    """Pin <loc> to the same origin the canonical tags use."""

    def get_domain(self, site=None):
        return urlsplit(base_url()).netloc or super().get_domain(site)

    def get_protocol(self, protocol=None):
        return urlsplit(base_url()).scheme or super().get_protocol(protocol)


class LivePageSitemap(_CanonicalOrigin, Sitemap):
    def items(self):
        return live_pages()

    def lastmod(self, obj):
        return obj.last_published_at or obj.latest_revision_created_at

    def location(self, obj):
        return obj.url or ""


class CodingProblemSitemap(_CanonicalOrigin, Sitemap):
    def items(self):
        return live_problems()

    def lastmod(self, obj):
        return obj.topic.last_published_at

    def location(self, obj):
        return obj.get_absolute_url()


class QuizSitemap(_CanonicalOrigin, Sitemap):
    def items(self):
        return live_quizzes()

    def lastmod(self, obj):
        return obj.topic.last_published_at

    def location(self, obj):
        return obj.get_absolute_url()


# What `/sitemap.xml` serves, and the same set the static export walks.
SITEMAPS = {
    "pages": LivePageSitemap,
    "problems": CodingProblemSitemap,
    "quizzes": QuizSitemap,
}
