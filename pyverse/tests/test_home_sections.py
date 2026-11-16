"""The home page's live sections must never break the page.

A fresh install (and every test database) has no courses, problems, labs or
notes yet. The home page has to render anyway, with each section hiding what is
empty and the colour rail showing honest zeros.
"""

import pytest

from pyverse.home.sections import build_home_sections
from pyverse.home.sections import plural


@pytest.mark.parametrize(
    ("count", "text"),
    [(0, "0 courses"), (1, "1 course"), (2, "2 courses")],
)
def test_plural(count, text):
    assert plural(count, "course") == text


def test_plural_irregular():
    assert plural(1, "entry", "entries") == "1 entry"
    assert plural(3, "entry", "entries") == "3 entries"


@pytest.mark.django_db
def test_sections_on_an_empty_database():
    data = build_home_sections()

    assert [item["label"] for item in data["rail"]] == [
        "Learn",
        "Practice",
        "Labs",
        "Blog",
        "Python",
    ]
    assert [item["tone"] for item in data["rail"]] == [1, 2, 3, 4, 5]
    assert [item["note"] for item in data["rail"][:4]] == [
        "0 courses",
        "0 problems",
        "0 traces",
        "0 notes",
    ]
    assert data["learn"]["course"] is None
    assert data["learn"]["lessons"] == []
    assert data["practice"]["problems"] == []
    assert data["labs"]["labs"] == []
    assert data["blog"]["entry"] is None
    assert data["blog"]["excerpt"] == ""
