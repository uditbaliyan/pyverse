"""`utility/check_export.py` must catch links that lead nowhere, not only assets."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "utility"))
import check_export


def write(root: Path, rel: str, text: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def site(tmp_path: Path) -> Path:
    write(tmp_path, "sitemap.xml", "<urlset></urlset>")
    write(tmp_path, "learn/index.html", "<p>learn</p>")
    write(tmp_path, "learn/topic/index.html", "<p>topic</p>")
    return tmp_path


def problems(site: Path, capsys: pytest.CaptureFixture[str]) -> list[str]:
    check_export.main(str(site))
    lines = capsys.readouterr().out.splitlines()
    return [line for line in lines if "problem(s)" not in line]


def test_a_link_to_an_exported_page_is_fine(site, capsys):
    write(site, "index.html", '<a href="learn/">Learn</a><a href="learn">Learn</a>')

    assert problems(site, capsys) == []


def test_a_link_to_a_page_that_was_not_exported_is_reported(site, capsys):
    write(site, "index.html", '<a href="practice/problem/gone/">Try it</a>')

    assert problems(site, capsys) == [
        "index.html: dead link practice/problem/gone/",
    ]


def test_fragments_and_query_strings_do_not_hide_a_dead_link(site, capsys):
    write(
        site,
        "index.html",
        '<a href="learn/#top">ok</a><a href="nope/?a=1#x">no</a>',
    )

    assert problems(site, capsys) == ["index.html: dead link nope/?a=1#x"]


def test_links_that_leave_the_site_or_need_no_file_are_skipped(site, capsys):
    write(
        site,
        "index.html",
        '<a href="https://example.org/x">a</a><a href="//cdn.example/x">b</a>'
        '<a href="mailto:a@b.c">c</a><a href="tel:1">d</a><a href="#top">e</a>'
        '<a href="javascript:void(0)">f</a><a href="">g</a>',
    )

    assert problems(site, capsys) == []


def test_relative_links_resolve_against_the_page_they_are_on(site, capsys):
    write(site, "learn/index.html", '<a href="topic/">ok</a><a href="../learn/">ok</a>')
    write(
        site,
        "learn/topic/index.html",
        '<a href="missing/">no</a><a href="../">ok</a>',
    )

    assert problems(site, capsys) == [
        "learn/topic/index.html: dead link missing/",
    ]


def test_a_relative_link_cannot_climb_out_of_the_site(site, capsys):
    write(site, "index.html", '<a href="../../../etc/passwd">x</a>')

    assert problems(site, capsys) == ["index.html: dead link ../../../etc/passwd"]


def test_a_query_only_link_is_reported_because_a_static_host_ignores_it(site, capsys):
    write(site, "learn/index.html", '<a href="?page=2">Next</a>')

    assert problems(site, capsys) == [
        "learn/index.html: query-only link ?page=2 (a static host ignores the query)",
    ]


def test_missing_assets_are_still_reported_as_before(site, capsys):
    write(
        site,
        "index.html",
        '<img src="media/x.png"><script src="static/a.js"></script>',
    )

    assert problems(site, capsys) == [
        "index.html: dead reference media/x.png",
        "index.html: dead reference static/a.js",
    ]


def test_root_absolute_references_are_errors_even_when_the_file_exists(site, capsys):
    # /learn/ exists, but "/..." only resolves at a domain root: under
    # user.github.io/pyverse/ it points at the host's root and 404s.
    write(site, "static/a.css", "b{}")
    write(
        site,
        "learn/topic/index.html",
        '<link rel="stylesheet" href="/static/a.css"><a href="/learn/">Learn</a>',
    )

    found = problems(site, capsys)

    assert len(found) == 2  # noqa: PLR2004
    assert all("root-absolute" in line for line in found)


def test_relative_references_resolve_from_the_page_not_the_site_root(site, capsys):
    write(site, "static/a.css", "b{}")
    write(
        site,
        "learn/topic/index.html",
        '<link rel="stylesheet" href="../../static/a.css">'
        '<link rel="stylesheet" href="static/a.css">',
    )

    assert problems(site, capsys) == [
        "learn/topic/index.html: dead reference static/a.css",
    ]


# ── content checks: placeholders, landmarks, duplicate ids, page-count floor ──


def content_problems(site: Path, capsys, floor: int = 0) -> list[str]:
    check_export.main(str(site), floor, content_checks=True)
    lines = capsys.readouterr().out.splitlines()
    return [line for line in lines if "problem(s)" not in line]


PAGE = "<body><main id='main'><h1>ok</h1></main></body>"


def test_a_clean_page_passes_content_checks(site, capsys):
    write(site, "index.html", PAGE)
    write(site, "learn/index.html", PAGE)
    write(site, "learn/topic/index.html", PAGE)

    assert content_problems(site, capsys) == []


@pytest.mark.parametrize(
    "snippet",
    [
        "<a href='https://neetcode.io/'>x</a>",
        "<a href='https://chat.z.ai'>x</a>",
        "<p>Lorem ipsum dolor</p>",
        "<p>page desc</p>",
        "<h1>Welcome to your new Wagtail site!</h1>",
    ],
)
def test_placeholder_content_is_reported(site, capsys, snippet):
    write(site, "index.html", f"<main id='main'>{snippet}</main>")

    found = content_problems(site, capsys)

    assert any("placeholder content" in line and "index.html" in line for line in found)


def test_a_page_needs_exactly_one_main(site, capsys):
    write(site, "index.html", "<main>a</main><main>b</main>")

    assert any("exactly one <main>" in line for line in content_problems(site, capsys))


def test_a_redirect_stub_needs_no_main(site, capsys):
    write(site, "index.html", PAGE)
    write(
        site,
        "old/index.html",
        '<meta http-equiv="refresh" content="0; url=/learn/">',
    )

    assert not any("old/index.html" in line for line in content_problems(site, capsys))


def test_duplicate_ids_are_reported_but_scripts_are_ignored(site, capsys):
    write(
        site,
        "index.html",
        "<main id='main'><div id='a'></div><div id='a'></div>"
        "<script>var s = '<div id=\"z\"></div><div id=\"z\"></div>';</script></main>",
    )

    found = content_problems(site, capsys)

    assert any("duplicate id 'a'" in line for line in found)
    assert not any("'z'" in line for line in found)


def test_page_count_floor_catches_an_empty_export(site, capsys):
    write(site, "index.html", PAGE)

    found = content_problems(site, capsys, floor=38)

    assert any("expected at least 38" in line for line in found)


def test_asset_urls_in_data_attributes_are_caught(site, capsys):
    # Scripts read these (the Python runtime starts its worker from data-worker),
    # so a root-absolute one breaks the page under a sub-path just like a <link>.
    write(site, "static/js/w.js", "")
    write(
        site,
        "learn/topic/index.html",
        '<script src="../../static/js/w.js" data-worker="/static/js/w.js"></script>',
    )

    found = problems(site, capsys)

    assert len(found) == 1
    assert "root-absolute reference /static/js/w.js" in found[0]
