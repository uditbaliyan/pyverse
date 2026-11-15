"""Pins for the colour-designated nav and the home headline parser.

`section_tone` decides which of the five poster colours a nav item hovers in.
It reads the item's URL, so reordering or adding nav items in the CMS can never
shuffle the colours. `hero_lines` turns the free-HTML headline into plain lines
so its look no longer depends on the CMS markup being exactly right.
"""

from pathlib import Path

import pytest

from pyverse.home.context_processors import section_tone
from pyverse.home.templatetags.home_tags import brand_text
from pyverse.home.templatetags.home_tags import hero_lines

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"


@pytest.mark.parametrize(
    ("url", "tone"),
    [
        ("/learn/", 1),
        ("/learn/python-basics/", 1),
        ("/practice/", 2),
        ("/practice/sheets/", 2),  # Sheets belong to Practice
        ("/labs/", 3),
        ("/python/", 4),  # the blog
        ("/about/", 5),
        ("/", 0),
        ("", 0),
        ("#", 0),
        ("https://example.com/learn/", 0),  # external links never take a tone
        ("/learnings/", 0),  # a prefix match must stop at a path boundary
    ],
)
def test_section_tone(url, tone):
    assert section_tone(url) == tone


def test_the_headline_stored_in_the_database_still_parses():
    """The real value has an unclosed span and lost its trailing dot."""
    assert hero_lines('PY<br>VERSE<span class="text-red">') == ["PY", "VERSE"]


def test_the_documented_headline_parses_and_drops_the_period():
    """The model's help text: the square dot replaces the red period."""
    assert hero_lines('PY<br>VERSE<span class="text-red">.</span>') == ["PY", "VERSE"]


@pytest.mark.parametrize("value", ["", None, "   ", "<br>", '<span class="x">.</span>'])
def test_an_empty_headline_yields_no_lines(value):
    assert hero_lines(value) == []


def test_headline_markup_and_scripts_are_removed_not_rendered():
    lines = hero_lines("A<br/><script>alert(1)</script>B &amp; C")
    assert all("<" not in line for line in lines)
    assert "B & C" in lines[-1]  # entities come back as text; the template escapes


def test_headline_is_capped():
    max_lines, max_line_length = 3, 40
    assert len(hero_lines("a<br>b<br>c<br>d<br>e")) == max_lines
    assert len(hero_lines("x" * 500)[0]) == max_line_length


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("PYVERSE.", "PYVERSE"),
        (" PyVerse ", "PyVerse"),
        ("", "PYVERSE"),
        (None, "PYVERSE"),
    ],
)
def test_brand_text_drops_the_trailing_period(value, expected):
    assert brand_text(value) == expected


def test_the_progress_line_lives_in_the_header_not_on_top_of_the_page():
    navbar = (TEMPLATES / "partials" / "_navbar.html").read_text()
    base = (TEMPLATES / "base.html").read_text()
    assert "pv-prog" in navbar
    assert "pv-prog" not in base
