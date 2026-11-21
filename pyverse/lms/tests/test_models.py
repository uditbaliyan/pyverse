"""Field validation and the small model properties the templates rely on."""

import pytest
from django.core.exceptions import ValidationError

from pyverse.lms.models import TopicPage

COLOR = TopicPage._meta.get_field("color")  # noqa: SLF001
ICON = TopicPage._meta.get_field("icon")  # noqa: SLF001


@pytest.mark.parametrize("color", ["", "#C62828", "#c62828"])
def test_a_hex_colour_or_nothing_is_accepted(color):
    assert COLOR.clean(color, None) == color


@pytest.mark.parametrize(
    "color",
    ["red", "#fff", "C62828", "#C6282", "#GGGGGG", "#C628288", "#C62828;x"],
)
def test_anything_else_is_not_a_colour(color):
    with pytest.raises(ValidationError):
        COLOR.clean(color, None)


@pytest.mark.parametrize("icon", ["", "code", "chart-bar", "book-open", "square-2"])
def test_lucide_style_icon_names_are_accepted(icon):
    assert ICON.clean(icon, None) == icon


@pytest.mark.parametrize(
    "icon",
    ["Code", "chart bar", "chart_bar", "-code", "code-", "co--de", "x" * 51],
)
def test_other_icon_names_cannot_work_and_are_rejected(icon):
    with pytest.raises(ValidationError):
        ICON.clean(icon, None)


@pytest.mark.parametrize(
    ("stored", "accent"),
    [("#2D5F5D", "#2D5F5D"), ("", ""), ("red", ""), ("#2D5F5D;x:y", "")],
)
def test_only_a_valid_stored_colour_is_ever_used_as_an_accent(stored, accent):
    """Rows saved before validation existed must not reach a style attribute."""
    assert TopicPage(color=stored).accent_color == accent
