from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.contrib.routable_page.models import route
from wagtail.fields import RichTextField
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock


class PracticeHubPage(RoutablePageMixin, Page):
    """
    Root landing page for the Free Practice Ecosystem.
    Every practice topic hangs off this single page — and, since the flat URL
    scheme, so do the challenge pages themselves: `/practice/problem/<slug>/`.
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
    subpage_types = ["topics.PracticeTopicPage", "topics.SheetsIndexPage"]

    class Meta:
        verbose_name = "Practice Hub Page"

    # ------------------------------------------------------------------
    # Flat challenge URLs — /practice/problem/<slug>/
    # ------------------------------------------------------------------
    @route(r"problem/(?P<slug>[\w-]+)/$")
    def problem(self, request, slug):
        """Serve one coding problem at its flat canonical URL.

        Topic child pages still resolve through the normal page walk: this
        pattern only matches a `problem/` prefix, so nothing else is shadowed.
        The nested `/practice/<topic>/<slug>/` paths that used to be canonical
        are kept alive as permanent redirects.
        """
        from pyverse.coding.models import CodingProblem

        problem = get_object_or_404(CodingProblem, slug=slug)
        return TemplateResponse(
            request,
            "coding/problem_page.html",
            {
                "page": self,
                "problem": problem,
                "topic": problem.topic,
                "payload": problem.grading_payload(),
            },
        )

    @route(r"quiz/(?P<slug>[\w-]+)/$")
    def quiz(self, request, slug):
        """Serve one quiz at its flat URL — same scheme as challenge pages."""
        from pyverse.quiz.models import Quiz

        quiz = get_object_or_404(Quiz, slug=slug)
        return TemplateResponse(
            request,
            "quiz/quiz_page.html",
            {
                "page": self,
                "quiz": quiz,
                "topic": quiz.topic,
                "payload": quiz.to_json_dict(),
            },
        )

    def get_context(self, request):
        context = super().get_context(request)

        from pyverse.coding.models import CodingProblem
        from pyverse.taxonomy import DIFFICULTY_RANK

        # The Landing table: every live problem, difficulty ascending by
        # default (spec §2). Filtering and sorting happen client-side so the
        # static export needs no server round-trip.
        context["problems"] = (
            CodingProblem.objects.filter(topic__isnull=False, topic__live=True)
            .select_related("topic")
            .order_by(DIFFICULTY_RANK, "title")
        )
        # Filter controls are rendered only for axes that actually have values
        # (spec §5 phasing: no empty Company/Pattern/Technique dropdowns).
        problems = list(context["problems"])
        context["company_options"] = sorted(
            {name for problem in problems for name in problem.companies.names()},
        )
        context["pattern_options"] = sorted(
            {name for problem in problems for name in problem.patterns.names()},
        )
        context["technique_options"] = sorted(
            {name for problem in problems for name in problem.techniques.names()},
        )
        context["practice_topics"] = (
            PracticeTopicPage.objects.live().public().order_by("title")
        )
        # Track cards need their problems server-side so the client can show a
        # real completion bar: progress lives in IndexedDB, but the *set* of
        # problems in a track is a build-time fact. Counts use the same
        # subtree aggregation the Track page itself uses.
        context["tracks"] = [
            {
                "page": topic,
                "problems": CodingProblem.objects.filter(
                    topic__path__startswith=topic.path,
                ).order_by(DIFFICULTY_RANK, "title"),
            }
            for topic in PracticeTopicPage.objects.live().public().order_by("title")
        ]
        # Quizzes are a first-class Practice surface too (Quiz Suite): listed
        # here and on Tracks, graded client-side, and recorded in the same
        # progress store as challenges.
        from pyverse.quiz.models import Quiz

        context["quizzes"] = (
            Quiz.objects.filter(topic__isnull=False, topic__live=True)
            .select_related("topic")
            .annotate(_question_count=Count("questions"))
            .order_by("title")
        )
        context["top_level_topics"] = (
            PracticeTopicPage.objects.child_of(self).live().order_by("title")
        )
        return context


class SheetsIndexPage(Page):
    """`/practice/sheets/` — the curated-sheet listing (spec §3).

    Sheets answer a different question from the Landing table ("tell me what
    order to solve things in"), so they live beside the tag hubs rather than
    replacing them.
    """

    max_count = 1

    intro = RichTextField(
        blank=True,
        help_text="Shown above the sheet cards.",
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("intro"),
    ]

    parent_page_types = ["topics.PracticeHubPage"]
    subpage_types = ["topics.SheetPage"]

    class Meta:
        verbose_name = "Sheets Index Page"

    def get_context(self, request):
        context = super().get_context(request)
        context["sheets"] = (
            SheetPage.objects.child_of(self).live().public().order_by("title")
        )
        return context


class SheetPage(Page):
    """One curated, ordered path through problems (spec §3).

    Problems are referenced with a `SnippetChooserBlock`, never copied: the
    same `CodingProblem` can sit in three sheets, one track and the Landing
    table at once, and still be one record.
    """

    description = RichTextField(
        blank=True,
        help_text="What this sheet is for, and who it suits.",
    )
    categories = StreamField(
        [
            (
                "category",
                blocks.StructBlock(
                    [
                        ("name", blocks.CharBlock()),
                        (
                            "problems",
                            blocks.ListBlock(
                                SnippetChooserBlock(
                                    "coding.CodingProblem",
                                    label="Problem",
                                ),
                                label="Problems, in solving order",
                            ),
                        ),
                    ],
                    icon="list-ul",
                    label="Category",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        help_text=(
            "Group the sheet into categories (Arrays & Hashing, Two Pointers…) "
            "each holding problems in the order they should be solved."
        ),
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("description"),
        FieldPanel("categories"),
    ]

    parent_page_types = ["topics.SheetsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Sheet Page"

    def problem_count(self):
        return sum(len(block.value["problems"]) for block in self.categories)

    def problems(self):
        """Every referenced problem, in sheet order."""
        for block in self.categories:
            yield from block.value["problems"]

    def get_context(self, request):
        context = super().get_context(request)
        context["problem_total"] = self.problem_count()
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
    # Context
    # ------------------------------------------------------------------
    def get_context(self, request):
        context = super().get_context(request)

        from pyverse.coding.models import CodingProblem
        from pyverse.quiz.models import Quiz
        from pyverse.taxonomy import DIFFICULTY_RANK

        # A Track is this page: every problem tagged to it or a descendant,
        # difficulty ascending by default (spec §4). No pagination — the table
        # is filtered/sorted client-side, and MVP volume is well under the
        # point where an initial payload matters.
        context["problems"] = (
            CodingProblem.objects.filter(topic__path__startswith=self.path)
            .select_related("topic")
            .order_by(DIFFICULTY_RANK, "title")
        )
        context["quizzes"] = (
            Quiz.objects.filter(topic__path__startswith=self.path)
            .select_related("topic")
            .annotate(_question_count=Count("questions"))
            .order_by("title")
        )
        context["subtopics"] = (
            PracticeTopicPage.objects.child_of(self).live().public().order_by("title")
        )
        context["practice_breadcrumb"] = self.get_practice_breadcrumb()
        return context
