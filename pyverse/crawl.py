"""Link-following discovery for the static export.

Why this exists
---------------
Enumerating the Wagtail tree (`pyverse.seo.live_pages()`) answers "which pages
exist?". A visitor's question is different: "which URLs can I reach by
clicking?". The two diverge for every *routable* sub-path — blog archives
(`/2026/09/`), dated entry URLs, feeds, tag pages — which are served by a page
but are not tree nodes. Each new one would need its own hand-written
enumerator, and a missed one is a dead link on the live site.

So the export is *discovered* instead: start from seeds (every tree page, the
sitemap's source of truth), render each URL through the real URL conf, read the
links out of the HTML and follow them. Whatever a visitor can click is exported,
with no per-model code, and the crawl doubles as a validator:

* a link to a URL that does not render 200 is an error naming the page it is on;
* a `/static/…` reference that no staticfiles finder can resolve is an error
  (this is what a missing Tailwind build looks like);
* a `/media/…` reference with no file under `MEDIA_ROOT` is an error (a navbar
  logo rendition that was never written, say);
* a link into an area the export does not ship (`/cms/`, `/accounts/`…) is an
  error — it would be a 404 on a static host.

The module is pure discovery: it renders, parses and reports, and writes
nothing. `pyverse.freeze` turns the result into django-distill URL sets.
"""

from __future__ import annotations

import posixpath
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from html.parser import HTMLParser
from http import HTTPStatus
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urljoin
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client

# (tag, attribute) -> what the reference is. "page" is a document the visitor
# navigates to; "resource" is something the page loads in order to render.
_REF_ATTRS = {
    ("a", "href"): "page",
    ("area", "href"): "page",
    ("link", "href"): "resource",
    ("script", "src"): "resource",
    ("img", "src"): "resource",
    ("source", "src"): "resource",
    ("video", "src"): "resource",
    ("audio", "src"): "resource",
    ("iframe", "src"): "resource",
}
# <link rel=...> values that are metadata about the page, not something to fetch.
_NON_FETCHED_RELS = {"canonical", "preconnect", "dns-prefetch", "prefetch"}
# <link rel="alternate"> is a feed or a translation: a real URL to export.
_DOCUMENT_RELS = {"alternate"}

# Areas of the project that exist at runtime but are deliberately not exported.
_NOT_EXPORTED = ("cms/", "accounts/", "users/", "documents/")
# Hosts the in-process client answers as; an absolute redirect to one is local.
_LOCAL_HOSTS = {"localhost", "testserver"}


class LinkParser(HTMLParser):
    """Collect `(kind, url)` pairs from one HTML document.

    `kind` is ``"page"`` for navigation targets and ``"resource"`` for what the
    page loads. Parsing with `html.parser` (not a regex) means attribute order,
    quoting and multi-line tags cannot hide a reference.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for (ref_tag, attr), kind in _REF_ATTRS.items():
            value = attributes.get(attr)
            if ref_tag == tag and value and self._wanted(tag, attributes):
                self.refs.append((self._kind(tag, attributes, kind), value))
        if tag in {"img", "source"} and attributes.get("srcset"):
            # "a.png 1x, b.png 2x" -> each candidate's URL.
            for candidate in attributes["srcset"].split(","):
                parts = candidate.split()
                if parts:
                    self.refs.append(("resource", parts[0]))

    @staticmethod
    def _rels(tag, attributes) -> set[str]:
        if tag != "link":
            return set()
        return set((attributes.get("rel") or "").lower().split())

    def _wanted(self, tag, attributes) -> bool:
        return not (self._rels(tag, attributes) & _NON_FETCHED_RELS)

    def _kind(self, tag, attributes, kind: str) -> str:
        # <link rel="alternate"> is a feed or a translation: a document to export.
        return "page" if self._rels(tag, attributes) & _DOCUMENT_RELS else kind


def extract_refs(html: str) -> list[tuple[str, str]]:
    parser = LinkParser()
    parser.feed(html)
    parser.close()
    return parser.refs


def _local_path(url: str, current: str) -> str | None:
    """The site-absolute path `url` points at, or None if it leaves the site.

    Query strings and fragments are dropped: a static host serves one file per
    path and ignores both.
    """
    parts = urlsplit(url.strip())
    if parts.scheme in {"mailto", "tel", "javascript", "data"}:
        return None
    if parts.netloc and parts.hostname not in _LOCAL_HOSTS:
        return None  # another origin
    if parts.scheme and not parts.netloc:
        return None
    if not parts.path:
        return None  # "#top" or "?page=2": the page it is already on
    joined = urljoin(current, parts.path)
    return unquote(urlsplit(joined).path)


def page_key(path: str) -> str:
    """Normalise a URL path to the form distill's `<path:path>` expects.

    No leading slash, and a directory-style trailing slash on every page, so
    `/python/notes` and `/python/notes/` are the same page.
    """
    stripped = path.lstrip("/")
    if stripped and not posixpath.splitext(stripped)[1] and not stripped.endswith("/"):
        stripped += "/"
    return stripped


@dataclass
class CrawlResult:
    # page key ("python/notes/") -> response content type
    pages: dict[str, str] = field(default_factory=dict)
    # paths under MEDIA_URL, relative to MEDIA_ROOT ("images/logo.width-32.png")
    media: set[str] = field(default_factory=set)
    static: set[str] = field(default_factory=set)
    errors: list[str] = field(default_factory=list)
    # page key -> the page it was first linked from (None for seeds). The
    # home page's own key is "", so "no origin" must not be spelled "".
    found_from: dict[str, str | None] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"{len(self.pages)} page(s), {len(self.media)} media file(s), "
            f"{len(self.static)} static file(s), {len(self.errors)} problem(s)"
        )


def _static_hint(rel: str) -> str:
    if rel.startswith("css/dist/"):
        return " — run `python manage.py tailwind build` first"
    if rel.startswith("vendor/"):
        return " — run `python utility/vendor_assets.py` first"
    return ""


class _Crawler:
    """One breadth-first pass over the site. Use via `crawl()`."""

    def __init__(self, client: Client, limit: int) -> None:
        self.client = client
        self.limit = limit
        self.result = CrawlResult()
        self.queue: deque[str] = deque()
        self.seen: set[str] = set()
        # resource problem -> every page that references it. A missing logo is
        # one problem on 40 pages, so it is reported once, not 40 times.
        self.broken: dict[str, list[str]] = {}

    # ── queue ────────────────────────────────────────────────────────────
    def enqueue(self, key: str, origin: str | None) -> None:
        if key not in self.seen:
            self.seen.add(key)
            self.result.found_from[key] = origin
            self.queue.append(key)

    def run(self) -> CrawlResult:
        while self.queue:
            if len(self.result.pages) >= self.limit:
                self.result.errors.append(
                    f"crawl stopped at {self.limit} pages (runaway links?)",
                )
                break
            self.visit(self.queue.popleft())
        for msg, origins in self.broken.items():
            unique = sorted(set(origins))
            more = f" (+{len(unique) - 1} more pages)" if len(unique) > 1 else ""
            self.result.errors.append(f"{unique[0]}{more}: {msg}")
        return self.result

    # ── one page ─────────────────────────────────────────────────────────
    def visit(self, key: str) -> None:
        origin = self.result.found_from[key]
        label = f"/{key}"
        who = "(seed)" if origin is None else f"/{origin}"

        if _is_not_exported(key):
            self.result.errors.append(
                f"{who}: links to {label}, which the static export does not ship",
            )
            return

        response = self.client.get(label, follow=False)
        status = response.status_code
        if status in {HTTPStatus.MOVED_PERMANENTLY, HTTPStatus.FOUND}:
            self.follow_redirect(response, label, origin, who)
        elif status != HTTPStatus.OK:
            self.result.errors.append(f"{who}: {label} returned {status}")
        else:
            self.read_page(key, label, response)

    def follow_redirect(
        self,
        response,
        label: str,
        origin: str | None,
        who: str,
    ) -> None:
        target = _local_path(response["Location"], label)
        if target is None:
            self.result.errors.append(f"{who}: {label} redirects off-site")
        else:
            self.enqueue(page_key(target), origin)

    def read_page(self, key: str, label: str, response) -> None:
        content_type = response.get("Content-Type", "")
        self.result.pages[key] = content_type
        if "html" not in content_type:
            return  # a feed or other document: exported, but has no links
        html = response.content.decode(response.charset or "utf-8", errors="replace")
        for kind, url in extract_refs(html):
            path = _local_path(url, label)
            if path is None:
                continue
            is_file = path.startswith((settings.STATIC_URL, settings.MEDIA_URL))
            if kind == "resource" or is_file:
                self.check_resource(path, label)
            else:
                self.enqueue(page_key(path), key)

    # ── one referenced file ──────────────────────────────────────────────
    def check_resource(self, path: str, origin: str) -> None:
        static_url, media_url = settings.STATIC_URL, settings.MEDIA_URL
        if path.startswith(static_url):
            rel = path[len(static_url) :]
            if rel in self.result.static:
                return
            if finders.find(rel):
                self.result.static.add(rel)
            else:
                self.report(f"static file not found: {path}{_static_hint(rel)}", origin)
        elif path.startswith(media_url):
            rel = path[len(media_url) :]
            if rel in self.result.media:
                return
            if (Path(settings.MEDIA_ROOT) / rel).is_file():
                self.result.media.add(rel)
            else:
                self.report(f"media file missing under MEDIA_ROOT: {path}", origin)
        else:
            self.report(f"resource outside /static/ and /media/: {path}", origin)

    def report(self, message: str, origin: str) -> None:
        self.broken.setdefault(message, []).append(origin)


def _is_not_exported(key: str) -> bool:
    admin = (getattr(settings, "ADMIN_URL", "") or "").lstrip("/")
    return key.startswith(_NOT_EXPORTED) or bool(admin and key.startswith(admin))


def crawl(seeds, client: Client | None = None, limit: int = 20_000) -> CrawlResult:
    """Render `seeds` and everything they link to; report what was reached.

    `seeds` are page keys (see `page_key`). `limit` is a runaway guard for a
    calendar-style page that links to an endless next month.
    """
    client = client or Client(SERVER_NAME="testserver", raise_request_exception=False)
    crawler = _Crawler(client, limit)
    for seed in seeds:
        crawler.enqueue(page_key(seed), None)
    return crawler.run()
