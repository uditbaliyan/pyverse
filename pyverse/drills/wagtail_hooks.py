from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import ParsonsProblem


@register_snippet
class ParsonsProblemViewSet(SnippetViewSet):
    model = ParsonsProblem
    icon = "list-ol"
    menu_label = "Parsons Puzzles"
    menu_name = "parsons-problems"
    add_to_admin_menu = True
    list_display = ("title", "topic", "difficulty", "concept", "position")
    search_fields = ("title", "concept")
    list_filter = ("topic", "difficulty")
