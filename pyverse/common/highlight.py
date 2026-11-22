"""Build-time syntax highlighting, shared by lesson code blocks and blog posts.

Pygments runs on the server while the site is frozen, so the exported HTML
already carries the colours: no highlighter ships to the browser and there is no
flash of unstyled code. Token classes are prefixed ``tok-`` and styled once in
``static/css/code-highlight.css`` (generate it with
``python utility/build_highlight_css.py``).
"""

import re

import markdown
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

CLASS_PREFIX = "tok-"

# `nowrap`: we supply our own <pre><code>. Pygments closes every span at a line
# end (a multi-line string becomes one span per line), so splitting the output
# on newlines never cuts a tag in half.
_FORMATTER = HtmlFormatter(nowrap=True, classprefix=CLASS_PREFIX)

_NEWLINES = re.compile(r"\r\n|\r|\n")


def _lexer(language: str):
    try:
        # stripnl=False keeps leading/trailing blank lines exactly as authored.
        return get_lexer_by_name(language or "text", stripnl=False)
    except ClassNotFound:
        return TextLexer(stripnl=False)


def highlight_lines(code: str, language: str = "text") -> list[str]:
    """Return one already-escaped HTML string per source line.

    The visible text of the joined lines equals ``code`` (what the Copy button
    reads), and an unknown ``language`` falls back to plain, escaped text.
    """
    code = _NEWLINES.sub("\n", code)
    html = highlight(code, _lexer(language), _FORMATTER)
    lines = html.split("\n")
    # Pygments always ends its output with a newline, so the split leaves one
    # empty tail: a trailing newline in the source is not a numbered empty line.
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def highlight_block(code: str, language: str = "text"):
    """Escaped, highlighted code with no per-line wrappers (safe to put in <code>)."""
    return mark_safe("\n".join(highlight_lines(code, language)))  # noqa: S308


def highlight_numbered_block(code: str, language: str = "text"):
    """Same, with each line in ``<span class="code-line">`` for CSS line numbers."""
    return format_html_join(
        "\n",
        '<span class="code-line">{}</span>',
        ((mark_safe(line),) for line in highlight_lines(code, language)),  # noqa: S308
    )


# `guess_lang` is off: Python-Markdown's guesser mis-lexes short snippets, so a
# fence with no language tag is shown as plain text rather than with wrong colours.
MARKDOWN_EXTENSIONS = ["extra", "codehilite"]
MARKDOWN_EXTENSION_CONFIGS = {
    "codehilite": {
        "guess_lang": False,
        "classprefix": CLASS_PREFIX,
        "css_class": "codehilite",
    },
}


def render_markdown(source: str) -> str:
    """The one place blog Markdown becomes HTML (save and admin preview)."""
    return markdown.markdown(
        source,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
    )
