from __future__ import annotations

from django.conf import settings
from django.db import models
from django.templatetags.static import static
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from .gym import DIFFICULTY_CHOICES
from .gym import LIBRARIES
from .gym import LIBRARY_CHOICES
from .gym import LIBRARY_ORDER
from .gym import PACKAGES

_RT = ["bold", "italic", "code", "link", "ol", "ul"]


class GymHubPage(Page):
    """/labs/gym/ : browse exercises by library."""

    intro = RichTextField(blank=True, features=_RT)

    parent_page_types = ["labs.LabsIndexPage"]
    subpage_types = ["labs.GymExercisePage"]
    max_count = 1
    template = "labs/gym_hub_page.html"
    content_panels = Page.content_panels + [FieldPanel("intro")]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        pages = sorted(
            GymExercisePage.objects.child_of(self).live().specific(),
            key=lambda p: (LIBRARY_ORDER[p.library], p.difficulty, p.title),
        )
        groups = []
        for key, label, _ in LIBRARIES:
            items = [p for p in pages if p.library == key]
            if items:
                groups.append({"key": key, "label": label, "items": items})
        ctx["groups"] = groups
        return ctx


class GymExercisePage(Page):
    """One exercise. Runs entirely in the visitor's browser; nothing is stored anywhere."""

    library = models.CharField(max_length=12, choices=LIBRARY_CHOICES, default="python")
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=1)
    prompt = RichTextField(features=_RT)
    setup_code = models.TextField(
        blank=True, help_text="Hidden. Runs first in the same namespace: build data here.",
    )
    starter_code = models.TextField(blank=True)
    check_code = models.TextField(
        help_text="assert-based; runs after the learner's code in the same namespace. "
        "Give every assert a message. Visible in page source (client-side by design).",
    )
    solution_code = models.TextField(
        blank=True, help_text="Reference answer; also verified by `manage.py check_gym`.",
    )
    hints = models.TextField(blank=True, help_text="One hint per line, revealed in order.")

    parent_page_types = ["labs.GymHubPage"]
    subpage_types: list[str] = []
    template = "labs/gym_exercise_page.html"

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("library"), FieldPanel("difficulty")], heading="Classification",
        ),
        FieldPanel("prompt"),
        MultiFieldPanel(
            [
                FieldPanel("setup_code"),
                FieldPanel("starter_code"),
                FieldPanel("check_code"),
                FieldPanel("solution_code"),
            ],
            heading="Code (run in the browser via Pyodide)",
        ),
        FieldPanel("hints"),
    ]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx["gym"] = {
            "library": self.library,
            "packages": list(PACKAGES[self.library]),
            "setup": self.setup_code,
            "starter": self.starter_code,
            "check": self.check_code,
            "solution": self.solution_code,
            "hints": [h.strip() for h in self.hints.splitlines() if h.strip()],
            "pyodide": getattr(settings, "GYM_PYODIDE_VERSION", "0.27.7"),
            "timeout": getattr(settings, "GYM_TIMEOUT_SECONDS", 10),
            "worker": static("labs/js/gym-worker.js"),
        }
        return ctx
