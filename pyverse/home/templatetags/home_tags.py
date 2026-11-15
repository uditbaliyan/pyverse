"""Template filters for the home page and the site chrome."""

import html
import re

from django import template
from django.utils.html import strip_tags

register = template.Library()

_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
_MAX_LINES = 3
_MAX_LINE_LENGTH = 40


@register.filter
def hero_lines(value):
    """Split the CMS headline into plain-text lines.

    `HomePage.hero_text` is free HTML (its help text suggests
    ``PY<br>VERSE<span class="text-red">.</span>``), and the stored value can
    be malformed: an unclosed span, a lost trailing dot. Rendering it with
    ``|safe`` made the headline's look depend on that markup being exactly
    right. This keeps only the words and the line breaks, so the template can
    own the styling (red last line plus the square dot). The result is plain
    text and is auto-escaped by the template.

    A trailing "." is dropped: the square dot button replaces the period.
    """
    if not value:
        return []
    text = html.unescape(strip_tags(_BR.sub("\n", str(value))))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        lines[-1] = lines[-1].rstrip(". ")
        if not lines[-1]:
            lines.pop()
    return [line[:_MAX_LINE_LENGTH] for line in lines[:_MAX_LINES]]


@register.filter
def brand_text(value):
    """The wordmark text without its trailing period.

    The site name is stored as "PYVERSE."; the template draws the period as a
    red square instead, so the text itself must not carry one.
    """
    text = str(value or "").strip().rstrip(".").strip()
    return text or "PYVERSE"
