"""The static export is *discovered* by following links (pyverse/crawl.py).

Two layers:

* Logic tests drive the crawler with a fake client, so they need no database
  and run in milliseconds. They pin every rule: what is followed, what is an
  error, what is reported once.
* One integration test builds a real blog and proves that what the crawler
  discovers is what the exporter can actually render. That is the regression for
  the blog archive / dated-entry / feed URLs that a Wagtail-tree walk could not
  see.
"""

from __future__ import annotations

from http import HTTPStatus

import pytest
from django.test import RequestFactory
from django.utils import timezone
from wagtail.models import Page

from pyverse.crawl import crawl
from pyverse.crawl import extract_refs
from pyverse.crawl import page_key

# ── Link extraction ──────────────────────────────────────────────────────


def test_extract_refs_separates_navigation_from_resources():
    html = """
    <link rel="stylesheet" href="/static/css/a.css">
    <script src="/static/js/a.js"></script>
    <a href="/learn/">Learn</a>
    <img src="/media/x.png" srcset="/media/x.png 1x, /media/x2.png 2x">
    """
    assert extract_refs(html) == [
        ("resource", "/static/css/a.css"),
        ("resource", "/static/js/a.js"),
        ("page", "/learn/"),
        ("resource", "/media/x.png"),
        ("resource", "/media/x.png"),
        ("resource", "/media/x2.png"),
    ]


def test_extract_refs_survives_attribute_order_quotes_and_line_breaks():
    # A regex over "<a ... href=" misses all three of these; a parser does not.
    html = "<a\n  class='x'\n  href='/a/'>A</a><a href=/b/ >B</a><A HREF=\"/c/\">C</A>"
    assert [url for _, url in extract_refs(html)] == ["/a/", "/b/", "/c/"]


def test_canonical_and_preconnect_are_not_fetched_but_feeds_are_pages():
    html = """
    <link rel="canonical" href="/x/">
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link rel="alternate" type="application/rss+xml" href="/blog/feed/">
    """
    assert extract_refs(html) == [("page", "/blog/feed/")]


@pytest.mark.parametrize(
    ("raw", "key"),
    [
        ("/", ""),
        ("/python/notes", "python/notes/"),
        ("/python/notes/", "python/notes/"),
        ("python/notes/", "python/notes/"),
        ("/sitemap.xml", "sitemap.xml"),  # a file keeps its name
    ],
)
def test_page_key_gives_one_spelling_per_page(raw, key):
    assert page_key(raw) == key


# ── Crawl rules, with a fake site ────────────────────────────────────────


class FakeResponse:
    def __init__(
        self,
        status=200,
        body="",
        content_type="text/html; charset=utf-8",
        location="",
    ):
        self.status_code = status
        self.content = body.encode()
        self.charset = "utf-8"
        self._headers = {"Content-Type": content_type, "Location": location}

    def get(self, name, default=""):
        return self._headers.get(name, default)

    def __getitem__(self, name):
        return self._headers[name]


class FakeSite:
    """`client.get(path)` over a dict of path -> response (or HTML string)."""

    def __init__(self, pages):
        self.pages = pages
        self.requested = []

    def get(self, path, *, follow=False):
        self.requested.append(path)
        page = self.pages.get(path)
        if page is None:
            return FakeResponse(404)
        return FakeResponse(body=page) if isinstance(page, str) else page


def run(pages, seeds=("",)):
    return crawl(seeds, client=FakeSite(pages))


def test_follows_links_to_pages_no_seed_mentions():
    result = run(
        {"/": '<a href="/a/">a</a>', "/a/": '<a href="/a/b/">b</a>', "/a/b/": ""},
    )
    assert set(result.pages) == {"", "a/", "a/b/"}
    assert result.errors == []


def test_a_page_linked_from_two_places_is_rendered_once():
    site = FakeSite(
        {
            "/": '<a href="/a/">1</a><a href="/a/">2</a>',
            "/a/": '<a href="/">home</a>',
        },
    )
    crawl([""], client=site)
    assert site.requested == ["/", "/a/"]


def test_query_strings_fragments_and_external_links_are_not_followed():
    site = FakeSite(
        {
            "/": (
                '<a href="?page=2">next</a><a href="#top">top</a>'
                '<a href="https://example.com/x/">ext</a>'
                '<a href="mailto:a@b.c">mail</a><a href="/a/?x=1#y">a</a>'
            ),
            "/a/": "",
        },
    )
    result = crawl([""], client=site)
    assert site.requested == ["/", "/a/"]
    assert result.errors == []


def test_relative_links_resolve_against_the_page_they_are_on():
    result = run(
        {"/a/": '<a href="b/">b</a><a href="../c/">c</a>', "/a/b/": "", "/c/": ""},
        seeds=("a/",),
    )
    assert set(result.pages) == {"a/", "a/b/", "c/"}


def test_dead_link_names_the_page_it_is_on():
    # The home page's key is "", which must not be mistaken for "no origin".
    result = run({"/": '<a href="/gone/">x</a>'})
    assert result.errors == ["/: /gone/ returned 404"]


def test_dead_link_on_a_deeper_page_names_that_page():
    result = run({"/": '<a href="/a/">a</a>', "/a/": '<a href="/gone/">x</a>'})
    assert result.errors == ["/a/: /gone/ returned 404"]


def test_a_failing_seed_is_reported_as_a_seed():
    result = run({}, seeds=("missing/",))
    assert result.errors == ["(seed): /missing/ returned 404"]


def test_links_into_unexported_areas_are_errors():
    result = run({"/": '<a href="/accounts/login/">in</a><a href="/cms/">cms</a>'})
    assert len(result.errors) == 2  # noqa: PLR2004
    assert all("does not ship" in error for error in result.errors)


def test_redirects_are_followed_to_their_target():
    old = FakeResponse(status=301, location="/new/")
    result = run({"/": '<a href="/old/">o</a>', "/old/": old, "/new/": ""})
    assert "new/" in result.pages
    assert result.errors == []


def test_non_html_pages_are_exported_but_not_parsed():
    feed = FakeResponse(body='<a href="/never/">', content_type="application/rss+xml")
    result = run({"/": '<link rel="alternate" href="/feed/">', "/feed/": feed})
    assert "feed/" in result.pages
    assert "never/" not in result.pages


def test_missing_static_file_is_reported_once_with_a_fix(settings):
    page = '<link rel="stylesheet" href="/static/css/dist/nope.css">'
    result = run({"/": page + '<a href="/a/">a</a>', "/a/": page})
    assert len(result.errors) == 1
    assert "(+1 more pages)" in result.errors[0]
    assert "tailwind build" in result.errors[0]


def test_present_static_file_is_recorded_not_reported():
    result = run({"/": '<link rel="stylesheet" href="/static/css/project.css">'})
    assert result.errors == []
    assert result.static == {"css/project.css"}


def test_missing_media_file_is_an_error_present_one_is_not(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    settings.MEDIA_URL = "/media/"  # test settings use a host-style URL
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "logo.png").write_bytes(b"png")
    result = run(
        {"/": '<img src="/media/images/logo.png"><img src="/media/images/gone.png">'},
    )
    assert result.media == {"images/logo.png"}
    assert len(result.errors) == 1
    assert "gone.png" in result.errors[0]


def test_runaway_links_stop_at_the_limit():
    pages = {f"/p{n}/": f'<a href="/p{n + 1}/">next</a>' for n in range(50)}
    result = crawl(["p0/"], client=FakeSite(pages), limit=10)
    assert len(result.pages) == 10  # noqa: PLR2004
    assert any("stopped" in error for error in result.errors)


# ── Integration: the blog the tree walk could not export ─────────────────


@pytest.fixture
def stylesheet(settings, tmp_path):
    """Stand in for the gitignored Tailwind build, which CI's test job lacks."""
    dist = tmp_path / "static" / "css" / "dist"
    dist.mkdir(parents=True)
    (dist / "styles.css").write_text("/* built */")
    settings.STATICFILES_DIRS = [*settings.STATICFILES_DIRS, str(tmp_path / "static")]


@pytest.fixture
def blog(db):
    from pyverse.puput.models import BlogPage  # noqa: PLC0415
    from pyverse.puput.models import EntryPage  # noqa: PLC0415

    home = Page.objects.get(depth=2)
    notes = BlogPage(title="Notes", slug="notes")
    home.add_child(instance=notes)
    entry = EntryPage(
        title="Why return matters",
        slug="why-return-matters",
        body="<p>Hello</p>",
        date=timezone.now(),
    )
    notes.add_child(instance=entry)
    return notes, entry


def test_linked_blog_routes_are_discovered_and_every_one_is_renderable(
    blog,
    stylesheet,
    settings,
):
    from pyverse.freeze import seed_paths  # noqa: PLC0415
    from pyverse.freeze import serve_exported_page  # noqa: PLC0415

    settings.SHOW_ACCOUNT_LINKS = False  # as under config.settings.distill
    _notes, entry = blog
    result = crawl(seed_paths())

    assert result.errors == []
    found = set(result.pages)
    # The year archive is a routed sub-path, not a node in the Wagtail tree: the
    # tree walk could never have listed it. Only following links finds it.
    assert {"notes/", f"notes/{entry.date:%Y}/", "notes/why-return-matters/"} <= found

    # What the crawler reaches, the exporter must be able to render. Distill
    # calls serve_exported_page with a bare RequestFactory request.
    for key in sorted(found):
        response = serve_exported_page(RequestFactory().get(f"/{key}"), key)
        assert response.status_code == HTTPStatus.OK, key


def test_plain_django_routes_render_through_the_exporter(blog, stylesheet):
    """puput's dated entry URL is a Django route, not a Wagtail-routed page.

    Hard-coding `wagtail_serve` in the exporter 404s on it. Even though the blog
    no longer links it, a URL a visitor can bookmark must still be renderable.
    """
    from pyverse.freeze import serve_exported_page  # noqa: PLC0415

    _notes, entry = blog
    stamp = entry.date
    key = f"notes/{stamp:%Y}/{stamp:%m}/{stamp:%d}/{entry.slug}/"
    response = serve_exported_page(RequestFactory().get(f"/{key}"), key)
    assert response.status_code == HTTPStatus.OK
