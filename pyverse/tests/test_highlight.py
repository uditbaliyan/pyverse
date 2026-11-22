"""Build-time syntax highlighting: lesson code blocks and blog Markdown."""

import importlib.util
import re
from html import unescape
from pathlib import Path

import pytest

from pyverse.common.highlight import highlight_block
from pyverse.common.highlight import highlight_lines
from pyverse.common.highlight import highlight_numbered_block
from pyverse.common.highlight import render_markdown
from pyverse.common.highlight_style import CODE_BACKGROUND
from pyverse.common.highlight_style import CODE_FOREGROUND
from pyverse.common.highlight_style import PyVerseStyle

WCAG_AA = 4.5
SRGB_LINEAR_CUTOFF = 0.03928
THREE = 3
TWO = 2

SOURCE = 'def f(x):\n    """a\n    b"""\n    return x < 1  # <ok>\n'


def text_of(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", html))


def test_python_is_tokenised_and_escaped():
    html = highlight_block(SOURCE, "python")

    assert 'class="tok-k"' in html  # keyword
    assert 'class="tok-nf"' in html  # function name
    assert "&lt;" in html
    assert "x < 1" not in html


def test_visible_text_is_exactly_the_source():
    # The Copy button reads textContent, so highlighting must not change it.
    assert text_of(highlight_block(SOURCE.rstrip("\n"), "python")) == SOURCE.rstrip(
        "\n",
    )


def test_a_multiline_string_never_leaves_a_span_open_across_lines():
    for line in highlight_lines(SOURCE, "python"):
        assert line.count("<span") == line.count("</span>")


def test_one_line_per_source_line_and_a_trailing_newline_adds_none():
    assert len(highlight_lines("a\nb\nc", "python")) == THREE
    assert len(highlight_lines("a\nb\nc\n", "python")) == THREE
    assert len(highlight_lines("a\r\nb\rc", "python")) == THREE


def test_numbered_lines_keep_the_wrapper_the_css_counter_needs():
    html = highlight_numbered_block("a = 1\nb = 2", "python")

    assert html.count('<span class="code-line">') == TWO


@pytest.mark.parametrize("language", ["", "no-such-language", "TEXT"])
def test_unknown_language_falls_back_to_plain_escaped_text(language):
    html = highlight_block("<script>alert(1)</script>", language)

    assert "<script>" not in html
    assert text_of(html) == "<script>alert(1)</script>"


def test_markdown_fence_with_a_language_is_highlighted():
    html = render_markdown("```python\nprint('<b>')\n```")

    assert '<div class="codehilite">' in html
    assert 'class="tok-nb"' in html  # builtin: print
    assert "&lt;b&gt;" in html


def test_markdown_fence_without_a_language_is_not_guessed():
    # Guessing mis-lexed short Python snippets; an untagged fence stays plain.
    html = render_markdown("```\ndef f(x):\n    return x+1\n```")

    assert "tok-" not in html
    assert text_of(html).strip() == "def f(x):\n    return x+1"


def _luminance(hex_colour: str) -> float:
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= SRGB_LINEAR_CUTOFF else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_colour.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_luminance(foreground), _luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_every_token_colour_is_readable_on_the_code_background():
    colours = {CODE_FOREGROUND.lstrip("#")}
    colours.update(style["color"] for _, style in PyVerseStyle if style["color"])
    for colour in colours:
        assert _contrast(colour, CODE_BACKGROUND) >= WCAG_AA, colour


def test_the_committed_stylesheet_matches_the_style():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "build_highlight_css",
        root / "utility" / "build_highlight_css.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    committed = (root / "pyverse" / "static" / "css" / "code-highlight.css").read_text(
        encoding="utf-8",
    )
    assert committed == module.build(), (
        "run `uv run python utility/build_highlight_css.py`"
    )
