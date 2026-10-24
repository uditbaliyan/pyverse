import json

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail_ai.panels import AIDescriptionFieldPanel
from wagtail_ai.panels import AITitleFieldPanel

# ── Import shared mixins from home app ──────────────────────────────────
from pyverse.home.models import SEOFields
from pyverse.taxonomy import Difficulty as SiteDifficulty

from .utils import lesson_counts_for


# ── Choices ──────────────────────────────────────────────────────────────
class CourseType(models.TextChoices):
    COURSE = "course", "Standard Course"
    MICRO = "micro", "Micro-course"
    WORKSHOP = "workshop", "Workshop"


class DifficultyLevel(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    ALL_LEVELS = "all_levels", "All Levels"


# How a course's level projects onto the Easy/Medium/Hard axis that
# `CodingProblem` / `Quiz` / `LabPage` use. Compare a course's `site_difficulty`
# with an exercise's `difficulty`; never compare `CoursePage.difficulty` with
# `taxonomy.Difficulty` directly — they are different vocabularies.
_COURSE_TO_SITE_DIFFICULTY = {
    DifficultyLevel.BEGINNER: SiteDifficulty.EASY,
    DifficultyLevel.INTERMEDIATE: SiteDifficulty.MEDIUM,
    DifficultyLevel.ADVANCED: SiteDifficulty.HARD,
    DifficultyLevel.ALL_LEVELS: None,
}


# ── StreamField Blocks ───────────────────────────────────────────────────
class CodeExampleBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        choices=[
            ("python", "Python"),
            ("sql", "SQL"),
            ("javascript", "JavaScript"),
            ("bash", "Bash"),
            ("html", "HTML"),
            ("css", "CSS"),
        ],
        default="python",
    )
    code = blocks.TextBlock(rows=10)
    filename = blocks.CharBlock(required=False, max_length=100)
    show_line_numbers = blocks.BooleanBlock(default=True)

    class Meta:
        icon = "code"
        template = "lms/blocks/code_example.html"
        label = "Code Example"


class MermaidBlock(blocks.TextBlock):
    """Renders Mermaid diagram syntax into an SVG diagram."""

    class Meta:
        icon = "site"
        template = "lms/blocks/mermaid.html"
        label = "Mermaid Diagram"


class CalloutBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[
            ("info", "Info"),
            ("tip", "Tip"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("note", "Note"),
        ],
        default="info",
    )
    title = blocks.CharBlock(required=False, max_length=200)
    body = blocks.RichTextBlock()

    class Meta:
        icon = "warning"
        template = "lms/blocks/callout.html"
        label = "Callout"


class ImageWithCaptionBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False, max_length=255)
    width = blocks.ChoiceBlock(
        choices=[
            ("full", "Full Width"),
            ("wide", "Wide"),
            ("half", "Half"),
        ],
        default="wide",
    )

    class Meta:
        icon = "image"
        template = "lms/blocks/image_with_caption.html"
        label = "Image"


class PracticeBlock(blocks.StructBlock):
    """A graded checkpoint embedded in a lesson body.

    Exactly one of `problem` / `quiz` must be set; StructBlock has no native
    "exactly one of", so `clean()` enforces it.
    """

    problem = SnippetChooserBlock("coding.CodingProblem", required=False)
    quiz = SnippetChooserBlock("quiz.Quiz", required=False)
    required_to_advance = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text=(
            "If checked, the learner must complete this before the next lesson unlocks."
        ),
    )

    class Meta:
        icon = "code"
        template = "lms/blocks/practice_embed.html"
        label = "Practice Checkpoint"

    def clean(self, value):
        result = super().clean(value)
        if bool(result["problem"]) == bool(result["quiz"]):
            raise blocks.StructBlockValidationError(
                block_errors={
                    "problem": ValidationError(
                        "Choose exactly one: a problem or a quiz, not both or neither.",
                    ),
                },
            )
        return result


class NotebookCellBlock(blocks.StructBlock):
    cell_type = blocks.ChoiceBlock(
        choices=[("code", "Code"), ("markdown", "Markdown")],
        default="code",
    )
    source = blocks.TextBlock(rows=6)

    class Meta:
        icon = "code"
        label = "Cell"


class NotebookBlock(blocks.StructBlock):
    """A notebook whose code cells run — and print — in the learner's browser.

    Same rule as `labs`: nothing here executes on the server. Markdown cells are
    rendered server-side by `wagtailmarkdown`; code cells are read out of the
    rendered DOM by `static/lms/js/notebook.js` and executed in order in one
    Pyodide namespace by `includes/pyscript_runtime.html`.
    """

    cells = blocks.ListBlock(NotebookCellBlock())

    class Meta:
        icon = "doc-full"
        template = "lms/blocks/notebook.html"
        label = "Notebook"


# ── LMS Index Page ───────────────────────────────────────────────────────
class LMSIndexPage(SEOFields, Page):
    max_count = 1
    intro = models.TextField(blank=True)
    featured_courses_heading = models.CharField(
        max_length=100,
        default="Featured Courses",
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("intro"),
        FieldPanel("featured_courses_heading"),
        FieldPanel("og_image"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["lms.TopicPage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["topics"] = TopicPage.objects.child_of(self).live().order_by("title")
        featured_courses = list(
            CoursePage.objects.descendant_of(self)
            .live()
            .filter(is_featured=True)
            .select_related("hero_image")
            .order_by("-first_published_at")[:6],
        )
        counts = lesson_counts_for(self, featured_courses)
        for course in featured_courses:
            course.set_lesson_count(counts.get(course.pk, 0))
        context["featured_courses"] = featured_courses
        context["all_courses_count"] = (
            CoursePage.objects.descendant_of(self).live().count()
        )
        context["all_topics_count"] = context["topics"].count()
        return context


# ── Topic Page ───────────────────────────────────────────────────────────
class TopicPage(Page):
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Icon name (e.g. "code", "database", "chart-bar")',
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text='Hex color, e.g. "#C62828"',
    )
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    content_panels = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("icon"),
                FieldPanel("color"),
                FieldPanel("display_order"),
            ],
            heading="Appearance",
        ),
        FieldPanel("description"),
    ]

    parent_page_types = ["lms.LMSIndexPage"]
    subpage_types = ["lms.CoursePage"]

    class Meta:
        ordering = ["display_order", "title"]

    def get_context(self, request):
        context = super().get_context(request)
        courses = (
            CoursePage.objects.child_of(self)
            .live()
            .select_related("hero_image")
            .order_by("-first_published_at")
        )

        difficulty = request.GET.get("difficulty")
        if difficulty in DifficultyLevel.values:
            courses = courses.filter(difficulty=difficulty)

        course_type = request.GET.get("type")
        if course_type in CourseType.values:
            courses = courses.filter(course_type=course_type)

        is_free = request.GET.get("free")
        if is_free == "1":
            courses = courses.filter(is_free=True)

        paginator = Paginator(courses, 12)
        page_number = request.GET.get("page", 1)
        courses_page = paginator.get_page(page_number)
        counts = lesson_counts_for(self, courses_page)
        for course in courses_page:
            course.set_lesson_count(counts.get(course.pk, 0))
        context["courses_page"] = courses_page
        context["active_difficulty"] = difficulty
        context["active_type"] = course_type
        context["active_free"] = is_free
        context["difficulty_choices"] = DifficultyLevel.choices
        context["type_choices"] = CourseType.choices
        return context


# ── Course Page ──────────────────────────────────────────────────────────
class CoursePage(SEOFields, Page):
    course_type = models.CharField(
        max_length=10,
        choices=CourseType,
        default=CourseType.COURSE,
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel,
        default=DifficultyLevel.BEGINNER,
    )
    language = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g. "Python", "SQL"',
    )
    summary = models.TextField(blank=True)
    # PyVerse has no paywall: this only drives the "Free" badge and JSON-LD
    # `isAccessibleForFree`, so it defaults on for every course.
    is_free = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    estimated_hours = models.PositiveIntegerField(
        default=1,
        help_text="Estimated time to complete (in hours)",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    what_you_learn = StreamField(
        [("item", blocks.CharBlock(label="Learning objective"))],
        use_json_field=True,
        blank=True,
        verbose_name="What You'll Learn",
    )
    prerequisites = StreamField(
        [("item", blocks.CharBlock(label="Prerequisite"))],
        use_json_field=True,
        blank=True,
    )

    content_panels = [
        AITitleFieldPanel("title", classname="title"),
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("course_type"),
                FieldPanel("difficulty"),
                FieldPanel("language"),
                FieldPanel("estimated_hours"),
                FieldPanel("is_free"),
                FieldPanel("is_featured"),
            ],
            heading="Course Details",
        ),
        AIDescriptionFieldPanel("summary"),
        FieldPanel("what_you_learn"),
        FieldPanel("prerequisites"),
        FieldPanel("og_image"),
    ]

    parent_page_types = ["lms.TopicPage"]
    subpage_types = ["lms.LessonPage"]

    def ordered_lessons(self):
        return LessonPage.objects.child_of(self).live().order_by("path")

    #: Filled by `set_lesson_count` on card grids so a page of course cards
    #: costs one query instead of one COUNT per card. `None` means "not filled".
    _lesson_count: int | None = None

    def set_lesson_count(self, count):
        """Record a count the caller already batched (`lesson_counts_for`), so
        rendering this course's card costs no query."""
        self._lesson_count = count

    @property
    def lesson_count(self):
        """Live lesson count — cached on the instance after the first access."""
        if self._lesson_count is None:
            self._lesson_count = self.ordered_lessons().count()
        return self._lesson_count

    @property
    def site_difficulty(self):
        """This course's level on the Easy/Medium/Hard exercise axis, or `None`
        for "All Levels" (which has no site-wide equivalent)."""
        return _COURSE_TO_SITE_DIFFICULTY.get(self.difficulty)

    @property
    def topic(self):
        parent = self.get_parent()
        if parent and isinstance(parent.specific, TopicPage):
            return parent.specific
        return None

    def get_context(self, request):
        context = super().get_context(request)
        lessons = self.ordered_lessons()
        context["lessons"] = lessons
        context["lesson_slugs_json"] = json.dumps(
            [lesson.slug for lesson in lessons],
        )
        return context


# ── Lesson Page ──────────────────────────────────────────────────────────
class LessonPage(Page):
    body = StreamField(
        [
            ("text", blocks.RichTextBlock()),
            ("video", blocks.URLBlock(label="Video URL")),
            ("code_example", CodeExampleBlock()),
            ("callout", CalloutBlock()),
            ("image", ImageWithCaptionBlock()),
            ("mermaid", MermaidBlock()),
            ("notebook", NotebookBlock()),
            ("practice", PracticeBlock()),
        ],
        use_json_field=True,
    )
    estimated_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Estimated reading time (minutes)",
    )

    content_panels = [
        AITitleFieldPanel("title", classname="title"),
        FieldPanel("estimated_minutes"),
        FieldPanel("body"),
    ]

    parent_page_types = ["lms.CoursePage"]
    subpage_types = []

    @property
    def course(self):
        parent = self.get_parent()
        if parent and isinstance(parent.specific, CoursePage):
            return parent.specific
        return None

    @property
    def topic(self):
        course = self.course
        return course.topic if course else None

    def get_context(self, request):
        context = super().get_context(request)
        siblings = list(LessonPage.objects.sibling_of(self).live().order_by("path"))
        idx = siblings.index(self) if self in siblings else -1
        context["prev_lesson"] = siblings[idx - 1] if idx > 0 else None
        context["next_lesson"] = (
            siblings[idx + 1] if 0 <= idx < len(siblings) - 1 else None
        )
        context["lesson_index"] = idx + 1 if idx >= 0 else 0
        context["total_lessons"] = len(siblings)
        context["course"] = self.course
        context["topic"] = self.topic
        context["lesson_list"] = siblings
        # The lesson page includes the PyScript runtime only when it has a
        # notebook: a page includes `includes/pyscript_runtime.html` once, never
        # twice (see that file's header).
        context["has_notebook"] = any(
            block.block_type == "notebook" for block in self.body
        )
        return context
