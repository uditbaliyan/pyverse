from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import CodingProblem


@register_snippet
class CodingProblemViewSet(SnippetViewSet):
    model = CodingProblem
    icon = "code"
    menu_label = "Coding Problems"
    menu_name = "coding-problems"
    add_to_admin_menu = True
    list_display = ("title", "difficulty", "function_name", "topic", "trace_status")
    # Enables the AJAX admin chooser (used by the `lms` app when linking
    # LessonSteps to problems) to search by title at 10k+ scale without
    # loading the full queryset client-side.
    search_fields = ("title",)
