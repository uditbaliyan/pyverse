"""The export must work at any host path, not just a domain root.

Root-absolute URLs (`/static/x.css`) break under `user.github.io/pyverse/` and
from `file://`, and get worse the deeper the page. These tests pin the rewrite
at every depth, and prove it with a real HTTP server mounted under a sub-path.
"""

from __future__ import annotations

import functools
import http.server
import threading
import urllib.request
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import pytest

from pyverse.relativize import relative_url
from pyverse.relativize import relativize_html
from pyverse.relativize import relativize_tree

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("page", "url", "expected"),
    [
        ("index.html", "/static/a.css", "static/a.css"),
        ("learn/index.html", "/static/a.css", "../static/a.css"),
        ("a/b/c/d/index.html", "/static/a.css", "../../../../static/a.css"),
        ("index.html", "/", "index.html"),
        ("learn/index.html", "/learn/", "../learn/index.html"),
        ("a/b/index.html", "/a/", "../../a/index.html"),
        ("a/index.html", "/x/?page=2#top", "../x/index.html?page=2#top"),
        ("a/index.html", "/x.css?v=3", "../x.css?v=3"),
    ],
)
def test_relative_url_depth(page, url, expected):
    assert relative_url(url, page) == expected


def test_clean_urls_keeps_directory_links():
    assert relative_url("/learn/", "a/index.html", clean_urls=True) == "../learn/"
    assert relative_url("/", "index.html", clean_urls=True) == "./"
    assert relative_url("/", "a/index.html", clean_urls=True) == "../"


def test_rewrites_every_url_bearing_attribute():
    html = (
        '<link rel="stylesheet" href="/static/a.css">'
        '<script src="/static/a.js"></script>'
        '<img src="/media/x.png" srcset="/media/x.png 1x, /media/y.png 2x">'
        '<a class="n" href="/learn/">L</a>'
        "<form action='/search/'></form>"
        '<meta http-equiv="refresh" content="0; url=/new/">'
        '<link rel="canonical" href="/new/">'
    )
    out = relativize_html(html, "a/b/index.html")
    assert "/static" not in out.replace("../../static", "")
    for expected in (
        'href="../../static/a.css"',
        'src="../../static/a.js"',
        'srcset="../../media/x.png 1x, ../../media/y.png 2x"',
        'href="../../learn/index.html"',
        "action='../../search/index.html'",
        "url=../../new/index.html",
    ):
        assert expected in out


def test_leaves_everything_that_is_not_root_absolute_alone():
    html = (
        '<a href="https://example.com/x">e</a><a href="//cdn.example/x.js">c</a>'
        '<a href="mailto:a@b.c">m</a><a href="#top">t</a><a href="?p=2">q</a>'
        '<a href="sibling/">s</a><a href="../up/">u</a>'
        '<link rel="canonical" href="https://pyverse.com/learn/">'
        '<p>Visit /learn/ or href="/not/a/tag" in prose</p>'
    )
    assert relativize_html(html, "a/index.html") == html


def test_non_html_files_are_not_touched(tmp_path):
    (tmp_path / "sitemap.xml").write_text("<loc>https://pyverse.com/a/</loc>")
    (tmp_path / "robots.txt").write_text("Sitemap: /sitemap.xml")
    (tmp_path / "index.html").write_text('<a href="/a/">a</a>')
    assert relativize_tree(tmp_path) == 1
    assert (tmp_path / "robots.txt").read_text() == "Sitemap: /sitemap.xml"


@pytest.fixture
def site(tmp_path):
    for rel, body in {
        "index.html": (
            '<link rel="stylesheet" href="/static/a.css"><a href="/a/b/">b</a>'
        ),
        "a/b/index.html": (
            '<link rel="stylesheet" href="/static/a.css"><a href="/">home</a>'
        ),
        "static/a.css": "body{}",
    }.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    relativize_tree(tmp_path)
    return tmp_path


def serve_under(root: Path, prefix: str):
    """Serve `root` at http://host/<prefix>/, as a project-pages host would."""
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(root),
    )

    class Prefixed(handler.func):
        def translate_path(self, path):
            assert path.startswith(prefix), f"request escaped {prefix}: {path}"
            return super().translate_path(path[len(prefix) - 1 :])

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        functools.partial(Prefixed, directory=str(root)),
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@pytest.mark.parametrize("prefix", ["/", "/pyverse/", "/a/deep/mount/"])
def test_every_link_and_stylesheet_resolves_under_any_mount_point(site, prefix):
    server = serve_under(site, prefix)
    try:
        base = f"http://127.0.0.1:{server.server_port}{prefix}"
        for page in ("index.html", "a/b/index.html"):
            url = urljoin(base, page)
            html = urllib.request.urlopen(url).read().decode()  # noqa: S310
            for ref in (
                "static/a.css" if page == "index.html" else "../../static/a.css",
            ):
                assert urllib.request.urlopen(urljoin(url, ref)).status == HTTPStatus.OK  # noqa: S310
            # follow the nav link and land on a real page, not a 404
            nav = html.split('href="')[-1].split('"')[0]
            assert urllib.request.urlopen(urljoin(url, nav)).status == HTTPStatus.OK  # noqa: S310
    finally:
        server.shutdown()


def test_data_attributes_that_hand_javascript_a_url_are_rewritten():
    html = '<body data-back-href="/practice/" data-quiz-slug="/not/a/url">'
    out = relativize_html(html, "practice/quiz/x/index.html")
    assert 'data-back-href="../../../practice/index.html"' in out
    assert 'data-quiz-slug="/not/a/url"' in out


def test_script_config_attributes_holding_asset_urls_are_rewritten():
    # The Python runtime reads data-worker / data-pyodide to start its worker. Left
    # root-absolute, `new Worker("/static/…")` 404s on any host that serves the
    # site under a sub-path, and the page reports "Python runtime failed to load".
    html = (
        '<script src="/static/js/pyverse-runtime.js"'
        ' data-worker="/static/js/pyverse-runner.js"'
        ' data-pyodide="/static/vendor/pyodide/0.27.7/pyodide.js"></script>'
        '<div data-viz="/static/vendor/viz/viz.js" data-slug="/practice/x"></div>'
    )
    out = relativize_html(html, "practice/problem/x/index.html")
    assert 'data-worker="../../../static/js/pyverse-runner.js"' in out
    assert 'data-pyodide="../../../static/vendor/pyodide/0.27.7/pyodide.js"' in out
    assert 'data-viz="../../../static/vendor/viz/viz.js"' in out
    # not an asset URL and not named like one: left alone
    assert 'data-slug="/practice/x"' in out
