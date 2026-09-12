from django.core.paginator import Paginator
from django.db import models
from django.template.response import TemplateResponse
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.url_routing import RouteResult


class PracticeHubPage(Page):
    """
    Root landing page for the Free Practice Ecosystem.
    Every practice topic hangs off this single page.
    """

    max_count = 1

    intro = models.TextField(
        blank=True,
        help_text=("Short introductory text shown at the top of the practice hub."),
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["topics.PracticeTopicPage"]

    class Meta:
        verbose_name = "Practice Hub Page"

    def get_context(self, request):
        context = super().get_context(request)
        context["top_level_topics"] = (
            PracticeTopicPage.objects.child_of(self).live().order_by("title")
        )
        return context


class PracticeTopicPage(RoutablePageMixin, Page):
    """
    A single node in the free-practice topic tree.  Topics may nest to
    arbitrary depth (e.g. "Arrays" → "Two Pointers").  Each topic
    aggregates every CodingProblem and Quiz tagged to itself or any
    descendant via an O(1) path__startswith lookup.
    """

    theory_content = RichTextField(
        blank=True,
        help_text=(
            "Optional theory/explanation content shown above the practice "
            "tabs.  Structured exercises belong in CodingProblem / Quiz "
            "snippets, not here."
        ),
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("theory_content"),
    ]

    parent_page_types = ["topics.PracticeHubPage", "topics.PracticeTopicPage"]
    subpage_types = ["topics.PracticeTopicPage"]

    class Meta:
        verbose_name = "Practice Topic Page"

    # ------------------------------------------------------------------
    # Breadcrumb helpers — keep class checks in Python, not templates
    # ------------------------------------------------------------------
    _PRACTICE_TYPES = None  # lazy-loaded tuple of (Hub, Topic) classes

    @classmethod
    def _practice_types(cls):
        if cls._PRACTICE_TYPES is None:
            # Lazy import so the module never forces coding/quiz/ to load
            # before the app registry is ready.
            from pyverse.topics.models import PracticeHubPage as Hub

            PracticeTopicPage._PRACTICE_TYPES = (Hub, cls)
        return cls._PRACTICE_TYPES

    def get_practice_breadcrumb(self):
        """
        Return only the ancestors that are PracticeHubPage or
        PracticeTopicPage, in tree order (root → parent).
        Each item is a dict with 'title', 'url', 'slug'.
        """
        return [
            {
                "title": a.title,
                "url": a.url,
                "slug": a.slug,
            }
            for a in self.get_ancestors().specific()
            if isinstance(a, self._practice_types())
        ]

    # ------------------------------------------------------------------
    # Challenge pages — /practice/<topic>/<slug>/
    # ------------------------------------------------------------------
    def route(self, request, path_components):
        """Resolve a single unmatched segment as a coding problem's slug.

        Child topics are real Wagtail pages whose slugs are equally
        slug-shaped, so they must win: the problem lookup only runs when no
        child page claims that segment. Anything longer than one segment
        falls through to Wagtail's own page walk.
        """
        if len(path_components) == 1:
            slug = path_components[0]
            if not self.get_children().filter(slug=slug).exists():
                from pyverse.coding.models import CodingProblem

                problem = CodingProblem.objects.filter(topic=self, slug=slug).first()
                if problem is not None:
                    return RouteResult(
                        self, args=(self.serve_problem, (problem,), {}),
                    )
        return super().route(request, path_components)

    def serve_problem(self, request, problem):
        """Render one coding problem at its canonical URL.

        Only problems whose *owning* topic is this page resolve here, so a
        problem linked from ancestor topics still has exactly one URL.
        """
        return TemplateResponse(
            request,
            "coding/problem_page.html",
            {
                "page": self,
                "problem": problem,
                "practice_breadcrumb": self.get_practice_breadcrumb(),
                "payload": {
                    "fn": problem.function_name,
                    "cases": problem.test_case_payload(),
                },
            },
        )

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------
    def get_context(self, request):
        context = super().get_context(request)

        # Lazy imports — keeps topics/ decoupled from coding/ and quiz/.
        from pyverse.coding.models import CodingProblem
        from pyverse.quiz.models import Quiz

        active_type = request.GET.get("type", "coding")
        if active_type not in ("coding", "quiz"):
            active_type = "coding"

        # O(1) tree-path inheritance — no recursive Python walk, no MPTT.
        problems_qs = (
            CodingProblem.objects.filter(topic__path__startswith=self.path)
            .select_related("topic")
            .order_by("title")
        )
        quizzes_qs = (
            Quiz.objects.filter(topic__path__startswith=self.path)
            .select_related("topic")
            .order_by("title")
        )

        page_number = request.GET.get("page", 1)

        context.update(
            {
                "practice_breadcrumb": self.get_practice_breadcrumb(),
                "active_type": active_type,
                "coding_problems_page": Paginator(problems_qs, 20).get_page(
                    page_number,
                ),
                "quizzes_page": Paginator(quizzes_qs, 20).get_page(page_number),
            },
        )
        return context
