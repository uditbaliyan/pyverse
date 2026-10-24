"""Generate a ``LessonPage`` — prose plus the blocks a lesson actually uses.

``body`` supports eight block types; only four are generated. ``video`` and
``image`` need assets a human has to supply, and ``notebook`` / ``practice``
carry content chosen by hand (cells; a specific problem or quiz), so a generated
lesson that used them would arrive with holes in it.

``LessonPage`` is a real Wagtail ``Page``, so it gets draft and revision
support for free: creating it through ``parent.add_child`` without publishing
leaves it as an unpublished draft that the admin already knows how to show.
"""

from __future__ import annotations

from typing import Any
from typing import ClassVar

from django.urls import reverse

from pyverse.ai_content.exceptions import GenerationError
from pyverse.ai_content.generators.base import Draft
from pyverse.ai_content.generators.base import Generator
from pyverse.ai_content.generators.base import optional_text
from pyverse.ai_content.generators.base import require_parent
from pyverse.ai_content.generators.base import required_text
from pyverse.ai_content.generators.base import rows
from pyverse.ai_content.generators.base import whole_number
from pyverse.lms.models import CalloutBlock
from pyverse.lms.models import CodeExampleBlock
from pyverse.lms.models import CoursePage
from pyverse.lms.models import LessonPage

#: Read off the real blocks, so a new language or callout style in
#: lms/models.py is offered to the model without a second edit here.
_LANGUAGES = [
    value for value, _label in CodeExampleBlock.base_blocks["language"].field.choices
]
_CALLOUT_STYLES = [
    value for value, _label in CalloutBlock.base_blocks["style"].field.choices
]

_SCHEMA = f"""\
Reply with one JSON object with exactly these keys:

{{
  "title": "lesson title in sentence case, e.g. Functions that return a value",
  "estimated_minutes": 8,
  "blocks": [
    {{"type": "text", "html": "<h2>Section</h2><p>Prose.</p>"}},
    {{"type": "code_example", "language": "python", "filename": "greet.py",
      "code": "def greet(name):\\n    return \\"Hello, \\" + name"}},
    {{"type": "callout", "style": "tip", "title": "Short heading",
      "body": "<p>The thing that catches people out.</p>"}},
    {{"type": "mermaid", "code": "graph TD\\n  A[Start] --> B{{Check}}"}}
  ]
}}

Block rules:
- "blocks" is the lesson in reading order. Start with "text" and use four to
  eight blocks in total.
- text and callout body are HTML (paragraphs in <p>, headings in <h2>, code in
  <code>). Never Markdown.
- code_example.language is one of {", ".join(_LANGUAGES)}; give the file a name
  from the lesson's own example, and make the code run as written.
- callout.style is one of {", ".join(_CALLOUT_STYLES)}. Use a callout for the
  one mistake readers actually make, not for encouragement.
- mermaid.code is raw Mermaid source. Use it only when the lesson describes
  control flow or a data structure; skip it otherwise.
- Never emit "video" or "image" blocks: those need assets a human supplies.
"""


class LessonGenerator(Generator):
    slug: ClassVar[str] = "lesson"
    menu_label: ClassVar[str] = "Lesson"
    label: ClassVar[str] = "LessonPage"
    style_file: ClassVar[str] = "lesson.md"
    schema: ClassVar[str] = _SCHEMA
    review_notes: ClassVar[tuple[str, ...]] = (
        "Lessons stay unpublished drafts until you publish them in /cms/.",
    )

    def parent_queryset(self) -> tuple[str, Any] | None:
        return "CoursePage", CoursePage.objects.all()

    def pre_create(self, data: dict[str, Any], report: Any = None) -> None:
        self._blocks(data)

    def create(self, data: dict[str, Any], parent: Any = None) -> Draft:
        lesson = LessonPage(
            title=required_text(data, "title"),
            estimated_minutes=whole_number(
                data,
                "estimated_minutes",
                default=10,
                minimum=1,
            ),
            body=self._blocks(data),
            # Page.live defaults to True, so add_child would publish this to
            # the site. A generated draft must not be live until Udit says so.
            live=False,
        )
        require_parent(parent, self.label).add_child(instance=lesson)

        return Draft(
            label=self.label,
            title=lesson.title,
            review_url=reverse("wagtailadmin_pages:edit", args=[lesson.pk]),
            notes=self.review_notes,
        )

    def _blocks(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        blocks = [
            _block(row, index)
            for index, row in enumerate(rows(data, "blocks"), start=1)
        ]
        if not blocks:
            message = "the model returned no lesson blocks"
            raise GenerationError(message)
        return blocks


def _block(row: dict[str, Any], index: int) -> dict[str, Any]:
    """One generated block, in Wagtail's StreamField-internal shape."""
    kind = optional_text(row, "type")
    where = f"block {index}"

    if kind == "text":
        return {"type": "text", "value": required_text(row, "html")}
    if kind == "code_example":
        language = optional_text(row, "language") or _LANGUAGES[0]
        if language not in _LANGUAGES:
            supported = ", ".join(_LANGUAGES)
            message = f"{where} asked for language {language!r}; supported: {supported}"
            raise GenerationError(message)
        return {
            "type": "code_example",
            "value": {
                "language": language,
                "code": required_text(row, "code"),
                "filename": optional_text(row, "filename"),
                "show_line_numbers": True,
            },
        }
    if kind == "callout":
        style = optional_text(row, "style") or "info"
        if style not in _CALLOUT_STYLES:
            supported = ", ".join(_CALLOUT_STYLES)
            message = f"{where} asked for style {style!r}; supported: {supported}"
            raise GenerationError(message)
        return {
            "type": "callout",
            "value": {
                "style": style,
                "title": optional_text(row, "title"),
                "body": required_text(row, "body"),
            },
        }
    if kind == "mermaid":
        return {"type": "mermaid", "value": required_text(row, "code")}

    message = f"{where} is of unsupported type {kind!r}"
    raise GenerationError(message)
