"""Labs — execution and memory tracing, in the learner's browser.

A lab is one authored Python program plus the tracer that steps through it.
Nothing here executes code on a server: the page bakes the program into a
`json_script` payload, and the runtime partial (`includes/tracer_runtime.html`)
traces it client-side, exactly like the Practice challenge page grades it.

Top level (`/labs/`, `/labs/<slug>/`) rather than under Practice or Learn: a lab
is neither a graded exercise nor a guided lesson, and its URL shape is frozen
into the static export (`docs/roadmap.rst`).
"""

from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from pyverse.home.models import SEOFields
from pyverse.taxonomy import Difficulty


class LabsIndexPage(SEOFields, Page):
    """`/labs/` — the list of labs. One per site."""

    max_count = 1
    intro = models.TextField(
        blank=True,
        help_text="Short lead-in shown above the lab list.",
    )

    content_panels = [*Page.content_panels, FieldPanel("intro")]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["labs.LabPage"]

    class Meta:
        verbose_name = "Labs Index Page"

    def get_context(self, request):
        context = super().get_context(request)
        context["labs"] = self.get_children().live().public().specific()
        return context


class LabPage(SEOFields, Page):
    """One traced program — `/labs/<slug>/`."""

    class Mode(models.TextChoices):
        LINE = "line", "Line trace"
        MEMORY = "memory", "Memory graph"

    summary = models.TextField(
        help_text="One or two sentences: what the program shows and why it is "
        "worth stepping through. Doubles as the page's meta description.",
    )
    code = models.TextField(
        help_text="The Python program to trace. It is baked into the exported "
        "page and runs in the learner's browser.",
    )
    what_to_watch = StreamField(
        [("item", blocks.CharBlock(label="Observation"))],
        use_json_field=True,
        blank=True,
        help_text="What the learner should notice while stepping through.",
    )
    default_mode = models.CharField(
        max_length=10,
        choices=Mode.choices,
        default=Mode.LINE,
        help_text="Which view opens first. Both are always available.",
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    estimated_minutes = models.PositiveSmallIntegerField(
        default=5,
        help_text="Roughly how long the lab takes to work through.",
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("summary"),
        FieldPanel("code"),
        FieldPanel("what_to_watch"),
        MultiFieldPanel(
            [
                FieldPanel("default_mode"),
                FieldPanel("difficulty"),
                FieldPanel("estimated_minutes"),
            ],
            heading="Lab details",
        ),
    ]

    parent_page_types = ["labs.LabsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Lab Page"

    def get_context(self, request):
        context = super().get_context(request)
        context["lab_payload"] = {
            "code": self.code,
            "mode": self.default_mode,
        }
        return context
