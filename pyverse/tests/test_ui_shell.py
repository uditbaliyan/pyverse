"""Regression tests for the single page shell and the shared components.

These pin the things that were broken before the UI unification: two shells
(one loading the Tailwind Play CDN), no skip link or <main> on many pages, a
whole <body> nested in a template, error pages with no layout, and a 500 page
that crashed when rendered without a request.
"""

import re
from http import HTTPStatus
from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.test import Client

TEMPLATE_ROOTS = [
    Path(__file__).resolve().parents[1] / "templates",
    Path(__file__).resolve().parents[1] / "theme" / "templates",
]


def _templates():
    for root in TEMPLATE_ROOTS:
        yield from root.rglob("*.html")


def _count(html: str, tag: str) -> int:
    return len(re.findall(rf"<{tag}[\s>]", html))


# --- static rules over the template tree -------------------------------------


def test_no_template_loads_the_tailwind_play_cdn():
    offenders = [str(p) for p in _templates() if "cdn.tailwindcss.com" in p.read_text()]
    assert not offenders, f"Play CDN is back in: {offenders}"


def test_only_the_shell_owns_the_document():
    """A page template must never emit <html>/<body>/<!DOCTYPE> itself."""
    allowed = {"base.html", "sitemap.xml"}
    offenders = []
    for p in _templates():
        if p.name in allowed or "wagtailadmin" in p.parts:
            continue
        text = re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
            "",
            p.read_text(),
            flags=re.S,
        )
        if re.search(r"<body[\s>]|<html[\s>]|<!DOCTYPE", text, re.I):
            offenders.append(str(p.relative_to(TEMPLATE_ROOTS[0].parent)))
    assert not offenders, f"templates that nest a document: {offenders}"


def test_font_black_is_not_a_font_family_token():
    css = (
        Path(__file__).resolve().parents[1] / "theme/static_src/src/styles.css"
    ).read_text()
    assert "--font-black" not in css, (
        "collides with Tailwind's font-black weight utility"
    )


# --- the shell, rendered ------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/accounts/login/", "/accounts/signup/"])
def test_auth_pages_use_the_shell(url):
    html = Client().get(url).content.decode()
    assert 'href="#main"' in html, "skip link"
    assert _count(html, "main") == 1
    assert _count(html, "h1") == 1
    assert _count(html, "footer") == 1
    assert 'id="main"' in html
    assert "cdn.tailwindcss.com" not in html


@pytest.mark.django_db
def test_404_is_a_real_page():
    resp = Client().get("/definitely/not/here/")
    html = resp.content.decode()
    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert "find that page" in html
    assert _count(html, "h1") == 1
    assert _count(html, "main") == 1


def test_500_renders_without_a_request():
    """Django renders 500.html with no request or context processors."""
    html = render_to_string("500.html")
    assert "went wrong" in html
    assert _count(html, "h1") == 1
    assert "Skip to main content" in html


# --- shared components --------------------------------------------------------


@pytest.mark.parametrize(
    ("level", "role", "prefix"),
    [
        ("info", "status", "Note:"),
        ("success", "status", "Success:"),
        ("warning", "status", "Warning:"),
        ("error", "alert", "Error:"),
    ],
)
def test_alert_is_never_colour_only(level, role, prefix):
    html = render_to_string("components/alert.html", {"level": level, "text": "Saved"})
    assert f'role="{role}"' in html
    assert prefix in html, "visually-hidden text label"
    assert "<svg" in html, "icon"


def test_static_alert_has_no_live_region():
    html = render_to_string(
        "components/alert.html",
        {"level": "tip", "text": "x", "static": True},
    )
    assert "role=" not in html


def test_button_renders_link_or_button_with_states():
    link = render_to_string("components/button.html", {"label": "Go", "href": "/x/"})
    assert link.lstrip().startswith("<a ")
    assert 'class="btn' in link
    btn = render_to_string(
        "components/button.html",
        {"label": "Save", "type": "submit", "variant": "danger", "disabled": True},
    )
    assert "<button" in btn
    assert "disabled" in btn
    assert "btn-danger" in btn
    busy = render_to_string("components/button.html", {"label": "Run", "loading": True})
    assert 'aria-busy="true"' in busy
    assert "disabled" in busy


def test_badge_label_is_text():
    html = render_to_string("components/badge.html", {"label": "Hard", "tone": "err"})
    assert ">Hard<" in html
    assert "badge-err" in html


def test_empty_state_can_be_the_page_h1():
    h1 = render_to_string(
        "components/empty_state.html",
        {"title": "Gone", "as_h1": True},
    )
    h2 = render_to_string("components/empty_state.html", {"title": "Gone"})
    assert "<h1" in h1
    assert "<h2" in h2
    assert "<h1" not in h2


def test_prev_next_is_one_pattern():
    html = render_to_string(
        "components/prev_next.html",
        {
            "prev_url": "/a/",
            "prev_title": "A",
            "next_url": "/b/",
            "next_title": "B",
            "next_id": "go",
        },
    )
    assert 'aria-label="Previous and next"' in html
    assert 'id="go"' in html


def test_navbar_drawer_is_a_native_disclosure():
    """No-JS-safe: <details>/<summary>, and 44px targets."""
    html = render_to_string("partials/_navbar.html", {})
    assert "<details" in html
    assert "<summary" in html
    assert "min-h-11" in html
