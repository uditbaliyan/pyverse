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
    write(site, "index.html", '<a href="/learn/">Learn</a><a href="/learn">Learn</a>')

    assert problems(site, capsys) == []


def test_a_link_to_a_page_that_was_not_exported_is_reported(site, capsys):
    write(site, "index.html", '<a href="/practice/problem/gone/">Try it</a>')

    assert problems(site, capsys) == [
        "index.html: dead link /practice/problem/gone/",
    ]


def test_fragments_and_query_strings_do_not_hide_a_dead_link(site, capsys):
    write(
        site,
        "index.html",
        '<a href="/learn/#top">ok</a><a href="/nope/?a=1#x">no</a>',
    )

    assert problems(site, capsys) == ["index.html: dead link /nope/?a=1#x"]


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
        '<img src="/media/x.png"><script src="/static/a.js"></script>',
    )

    assert problems(site, capsys) == [
        "index.html: dead reference /media/x.png",
        "index.html: dead reference /static/a.js",
    ]
