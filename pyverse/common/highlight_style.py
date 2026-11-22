"""Pygments colours for code on PyVerse's ink (#1a1a1a) code surfaces.

Every colour here clears WCAG AA (4.5:1) against ``CODE_BACKGROUND``; a test
enforces it. Edit the palette, then regenerate the stylesheet with
``uv run python utility/build_highlight_css.py``.
"""

from pygments.style import Style
from pygments.token import Comment
from pygments.token import Error
from pygments.token import Generic
from pygments.token import Keyword
from pygments.token import Name
from pygments.token import Number
from pygments.token import Operator
from pygments.token import String

CODE_BACKGROUND = "#1a1a1a"
CODE_FOREGROUND = "#f5eeda"


class PyVerseStyle(Style):
    background_color = CODE_BACKGROUND
    styles = {
        Comment: "italic #a39a85",
        Keyword: "bold #ff8a7a",
        Keyword.Constant: "bold #f2b560",
        Operator: "#f5eeda",
        Operator.Word: "bold #ff8a7a",
        Name.Builtin: "#7fd8d0",
        Name.Function: "bold #86bcff",
        Name.Class: "bold #86bcff",
        Name.Decorator: "#d9a8ff",
        Name.Exception: "bold #86bcff",
        String: "#a9d67c",
        String.Doc: "italic #a9d67c",
        Number: "#f2b560",
        Generic.Deleted: "#ff8a7a",
        Generic.Inserted: "#a9d67c",
        Generic.Heading: "bold #86bcff",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Error: "#ff8a7a",
    }
