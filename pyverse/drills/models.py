"""Drills: topic-grouped question sets, IndiaBIX style.

    /drills/                       DrillsHubPage
      /drills/parsons/             DrillTypePage   (one per question type)
        /drills/parsons/<topic>/   DrillTopicPage  (paginated: .../page/2/)

Items (``ParsonsProblem``) are snippets that live *inside* a topic page; they
have no URL of their own, so thousands of items never mean thousands of pages.
A topic page is the unit other parts of the site link to (LMS, home).
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.db import models
from django.http import Http404
from django.template.response import TemplateResponse
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.contrib.routable_page.models import route
from wagtail.fields import StreamField
from wagtail.models import Page

from pyverse.drills import parsons
from pyverse.home.models import SEOFields
from pyverse.taxonomy import DIFFICULTY_RANK
from pyverse.taxonomy import Difficulty

STORES = {
    "parsons": "pv:parsons:solved",
    "quiz": "pv:drillquiz:solved",
}


class DrillsHubPage(SEOFields, Page):
    """`/drills/` — the question types. One per site."""

    max_count = 1
    intro = models.TextField(blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro")]
    parent_page_types = ["home.HomePage"]
    subpage_types = ["drills.DrillTypePage"]

    class Meta:
        verbose_name = "Drills Hub Page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["types"] = self.get_children().live().public().specific()
        return context


class DrillTypePage(SEOFields, Page):
    """`/drills/<type>/` — the topic groups of one question type."""

    class Kind(models.TextChoices):
        PARSONS = "parsons", "Parsons (arrange the lines)"
        QUIZ = "quiz", "Quiz (multiple choice, true / false)"

    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.PARSONS)
    intro = models.TextField(blank=True)

    content_panels = [*Page.content_panels, FieldPanel("kind"), FieldPanel("intro")]
    parent_page_types = ["drills.DrillsHubPage"]
    subpage_types = ["drills.DrillTopicPage"]

    class Meta:
        verbose_name = "Drill Type Page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        topics = list(self.get_children().live().public().specific())
        context["item_noun"] = "question" if self.kind == self.Kind.QUIZ else "puzzle"
        context["topics"] = [
            {
                "page": t,
                "count": t.item_count(),
                "slugs": ",".join(t.item_slugs()),
                "store": t.progress_store,
            }
            for t in topics
        ]
        return context


class DrillTopicPage(RoutablePageMixin, SEOFields, Page):
    """`/drills/<type>/<topic>/` — one group, paginated at ``page/<n>/``."""

    PER_PAGE = 10

    intro = models.TextField(blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro")]
    parent_page_types = ["drills.DrillTypePage"]
    subpage_types: list[str] = []

    class Meta:
        verbose_name = "Drill Topic Page"

    @property
    def kind(self) -> str:
        return self.get_parent().specific.kind

    @property
    def progress_store(self) -> str:
        """localStorage key the browser records solved items under."""
        return STORES[self.kind]

    def items(self):
        """Every item of this topic in display order: Parsons puzzles, or the
        questions of the quizzes assigned to it. Items have no pages of their own."""
        if self.kind == DrillTypePage.Kind.QUIZ:
            from pyverse.quiz.models import Question  # noqa: PLC0415

            return (
                Question.objects.filter(quiz__drill_topic=self)
                .select_related("quiz")
                .prefetch_related("choices")
                .order_by("quiz__id", "sort_order", "id")
            )
        return self.parsons_problems.order_by("position", DIFFICULTY_RANK, "id")

    def item_count(self) -> int:
        return self.items().count()

    def item_slugs(self) -> list[str]:
        """Stable per-item ids in display order; the browser matches them against
        saved progress (``p<slug>`` for puzzles' slugs, ``q<pk>`` for questions)."""
        if self.kind == DrillTypePage.Kind.QUIZ:
            return [f"q{q.pk}" for q in self.items()]
        return [p.slug for p in self.items()]

    def num_pages(self) -> int:
        return max(1, Paginator(self.items(), self.PER_PAGE).num_pages)

    def page_url_for(self, number: int) -> str:
        return self.url if number == 1 else f"{self.url}page/{number}/"

    def paged_urls(self) -> list[str]:
        """Every URL of this topic, page 1 first — the static export's file list."""
        return [self.page_url_for(n) for n in range(1, self.num_pages() + 1)]

    def get_context(self, request, *args, number: int = 1, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        paginator = Paginator(self.items(), self.PER_PAGE)
        try:
            current = paginator.page(number)
        except EmptyPage as exc:
            raise Http404 from exc
        context["items"] = list(current.object_list)
        context["kind"] = self.kind
        context["store"] = self.progress_store
        context["total"] = paginator.count
        context["current"] = number
        context["offset"] = (number - 1) * self.PER_PAGE
        context["page_links"] = [
            {"number": n, "url": self.page_url_for(n), "current": n == number}
            for n in range(1, paginator.num_pages + 1)
        ]
        context["prev_url"] = self.page_url_for(number - 1) if number > 1 else ""
        context["next_url"] = (
            self.page_url_for(number + 1) if number < paginator.num_pages else ""
        )
        return context

    def _render(self, request, number: int):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, number=number),
        )

    @route(r"^$")
    def first_page(self, request):
        return self._render(request, 1)

    @route(r"^page/(?P<number>[0-9]+)/$")
    def numbered_page(self, request, number):
        number = int(number)
        if number < 2:  # noqa: PLR2004 - page 1 lives at the topic URL itself
            raise Http404
        return self._render(request, number)


class LineBlock(blocks.StructBlock):
    text = blocks.CharBlock(
        max_length=200,
        help_text="One line of code, no leading spaces.",
    )
    indent = blocks.IntegerBlock(
        min_value=0,
        max_value=6,
        default=0,
        help_text="Indent level in the correct program (0 = top level). Ignored for distractors.",
    )
    is_distractor = blocks.BooleanBlock(
        required=False,
        help_text="A line that does NOT belong in the solution.",
    )
    feedback = blocks.CharBlock(
        required=False,
        max_length=300,
        help_text="Shown after Check. Required in spirit for distractors: say why it is wrong.",
    )

    class Meta:
        icon = "code"
        label = "Line"


class ParsonsProblem(models.Model):
    """One arrange-the-lines puzzle. The correct program is the non-distractor
    lines, in the order they are listed here."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True)
    topic = models.ForeignKey(
        DrillTopicPage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="parsons_problems",
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Order inside the topic (lower first); ties fall back to difficulty.",
    )
    concept = models.CharField(max_length=120, blank=True)
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    description = models.TextField(help_text="What the program must do.")
    expected_output = models.TextField(
        blank=True,
        help_text="What the correct program prints. `check_parsons` runs it and compares.",
    )
    lines = StreamField([("line", LineBlock())], use_json_field=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("topic"),
        FieldPanel("position"),
        FieldPanel("concept"),
        FieldPanel("difficulty"),
        FieldPanel("description"),
        FieldPanel("expected_output"),
        FieldPanel("lines"),
    ]

    class Meta:
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return f"{self.topic.url}#{self.slug}" if self.topic_id else ""

    def clean(self):
        super().clean()
        if self.lines:
            report = parsons.verify(
                self.lines,
                "",
            )  # parse only; running is check_parsons's job
            if report.errors:
                raise ValidationError({"lines": report.errors})

    def payload(self) -> dict:
        """What the browser needs. The correct order is the list order."""
        return {
            "id": self.slug,
            "lines": [
                {
                    "id": f"{self.slug}-{i}",
                    "text": block.value["text"],
                    "indent": int(block.value["indent"]),
                    "distractor": bool(block.value["is_distractor"]),
                    "feedback": block.value["feedback"],
                }
                for i, block in enumerate(self.lines)
            ],
        }
