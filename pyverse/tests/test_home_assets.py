"""Static guards for the home page's hand-written CSS, JS and template hooks.

None of these need a browser. They pin the rules the work depends on:

* No ``url()`` in the new CSS. Production uses a manifest static-files storage,
  which fails ``collectstatic`` on a CSS ``url()`` it cannot resolve.
* The script writes text with ``textContent``, never ``innerHTML``: the screen
  can show CMS-supplied code.
* The template compiles, and every hook the script looks up exists in it, so
  renaming one side cannot silently turn a feature into a dead button.
"""

import re
from pathlib import Path

import pytest
from django.template.loader import get_template

APP = Path(__file__).resolve().parents[1]
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT = re.compile(r"(?m)^\s*//.*$")


def code_of(path):
    """The file's source with comments removed: comments may name the rules."""
    return LINE_COMMENT.sub("", BLOCK_COMMENT.sub("", path.read_text()))


CSS = ("pyverse-pop.css", "pyverse-home.css")
JS = ("pyverse-pop.js", "home-device.js")
HOME_TEMPLATE = APP / "templates" / "home" / "home_page.html"


@pytest.mark.parametrize("name", CSS)
def test_css_has_no_url_references(name):
    assert "url(" not in code_of(APP / "static" / "css" / name)


@pytest.mark.parametrize("name", JS)
def test_scripts_never_write_markup(name):
    js = code_of(APP / "static" / "js" / name)
    for unsafe in (
        "innerHTML",
        "outerHTML",
        "insertAdjacentHTML",
        "document.write",
        "eval(",
    ):
        assert unsafe not in js, f"{name} uses {unsafe}"


def test_home_template_compiles():
    get_template("home/home_page.html")


def test_every_hook_the_home_script_reads_exists_in_the_template():
    template = HOME_TEMPLATE.read_text()
    script = (APP / "static" / "js" / "home-device.js").read_text()

    # attribute / id / class hooks the script queries
    wanted = set(re.findall(r'querySelector(?:All)?\(\s*["\']([^"\']+)["\']', script))
    wanted |= {
        f"#{i}" for i in re.findall(r'getElementById\(\s*["\']([^"\']+)["\']', script)
    }

    missing = []
    for selector in sorted(wanted):
        tokens = re.findall(r"\[([a-z-]+)(?:=[^\]]*)?\]|#([\w-]+)|\.([\w-]+)", selector)
        for attr, ident, cls in tokens:
            needle = attr or ident or cls
            if needle and needle not in template:
                missing.append((selector, needle))
    assert not missing, f"script looks for hooks the template lacks: {missing}"


def test_the_easter_egg_dot_is_inside_the_only_h1():
    template = HOME_TEMPLATE.read_text()
    h1 = re.findall(r"<h1\b.*?</h1>", template, flags=re.DOTALL)
    assert len(h1) == 1
    assert 'id="egg"' in h1[0]


def test_hero_headline_is_not_rendered_with_safe():
    """`|safe` made the headline's look depend on CMS markup being exact."""
    template = HOME_TEMPLATE.read_text()
    assert "hero_text|safe" not in template
    assert "hero_text|hero_lines" in template
