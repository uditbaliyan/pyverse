"""Vendored assets exist and the pages point at them, not at a CDN."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "utility"))
import vendor_assets  # noqa: E402

PAGES = [
    ROOT / "templates/coding/problem_page.html",
    ROOT / "templates/labs/lab_page.html",
    ROOT / "templates/includes/trace_panel.html",
]


def test_every_vendored_file_is_present_and_nonempty():
    missing = [
        p
        for p in vendor_assets.expected_files()
        if not p.is_file() or p.stat().st_size == 0
    ]
    assert not missing, missing


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_pages_reference_only_vendored_files_that_exist(page):
    text = page.read_text(encoding="utf-8")
    refs = re.findall(r"\{% static 'vendor/([^']+)' %\}", text)
    assert refs, f"{page.name} no longer references vendor/"
    assert not [r for r in refs if not (ROOT / "static/vendor" / r).is_file()]


@pytest.mark.parametrize("page", PAGES[:2], ids=lambda p: p.name)
def test_codemirror_is_not_loaded_from_a_cdn(page):
    assert "jsdelivr.net/npm/codemirror" not in page.read_text(encoding="utf-8")


def test_problem_page_boots_pyodide_from_the_vendored_copy():
    html = PAGES[0].read_text(encoding="utf-8")
    assert "data-pyodide=\"{% static 'vendor/pyodide/0.27.7/pyodide.js' %}\"" in html
