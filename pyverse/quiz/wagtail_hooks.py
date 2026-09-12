from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Quiz


@register_snippet
class QuizViewSet(SnippetViewSet):
    model = Quiz
    icon = "help"
    menu_label = "Quizzes"
    menu_name = "quizzes"
    add_to_admin_menu = True
    list_display = ("title", "quiz_type", "topic")
    # Enables the AJAX admin chooser (used by the `lms` app when linking
    # LessonSteps to quizzes) to search by title or type at 10k+ scale
    # without loading the full queryset client-side.
    search_fields = ("title", "quiz_type")
