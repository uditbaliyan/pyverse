"""Blocks shared by more than one content app.

Only genuinely cross-app blocks live here — `coding`, `quiz` and `labs` all want
the same editorial-approach shape. A block only one app renders stays in that
app (`lms/models.py`), because it carries that app's templates with it.
"""

from wagtail import blocks


class EditorialApproachBlock(blocks.StructBlock):
    """One editorially-approved solution approach (moved from `coding.models`)."""

    name = blocks.CharBlock(help_text='e.g. "Hash map, one pass".')
    description = blocks.RichTextBlock(required=False)
    time_complexity = blocks.CharBlock(required=False, label="Time complexity")
    space_complexity = blocks.CharBlock(required=False, label="Space complexity")
    is_optimal = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Marks this approach as the intended optimal one.",
    )

    class Meta:
        icon = "code"
        label = "Editorial approach"
