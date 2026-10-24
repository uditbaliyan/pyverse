"""Regressions for audit findings F-01 (ignored templates) and F-08 (stub escaping)."""

import pytest
from django.template.loader import get_template
from django.test import RequestFactory

PUPUT_TAG_TEMPLATES = [
    "puput/tags/entries_list.html",
    "puput/tags/tags_list.html",
    "puput/tags/categories_list.html",
    "puput/tags/archives_list.html",
    "puput/tags/breadcrumbs.html",
]


@pytest.mark.parametrize("name", PUPUT_TAG_TEMPLATES)
def test_puput_tag_templates_exist(name):
    get_template(name)


def test_tags_dir_not_gitignored():
    import subprocess  # noqa: PLC0415
    from pathlib import Path  # noqa: PLC0415

    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["git", "check-ignore", "-q", "pyverse/templates/puput/tags/entries_list.html"],  # noqa: S607
        cwd=root,
        check=False,
    )
    assert result.returncode == 1, "a .gitignore rule swallows puput/tags/ again"


@pytest.mark.django_db
def test_redirect_stub_escapes_target():
    from wagtail.contrib.redirects.models import Redirect  # noqa: PLC0415

    from pyverse.freeze import render_redirect_stub  # noqa: PLC0415

    hostile = '/x"><script>alert(1)</script>'
    Redirect.objects.create(old_path="/old", redirect_link=hostile)
    request = RequestFactory().get("/old/")
    body = render_redirect_stub(request, path="old").content.decode()
    assert "<script>" not in body
    assert "&lt;script&gt;" in body
