import json

from django.core.paginator import Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

# ── Import shared mixins from home app ──────────────────────────────────
from pyverse.home.models import SEOFields


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
        context["featured_courses"] = (
            CoursePage.objects.descendant_of(self)
            .live()
            .filter(is_featured=True)
            .select_related("hero_image")
            .order_by("-first_published_at")[:6]
        )
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
        max_length=7, blank=True, help_text='Hex color, e.g. "#C62828"'
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
        context["courses_page"] = paginator.get_page(page_number)
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
        choices=CourseType.choices,
        default=CourseType.COURSE,
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER,
    )
    language = models.CharField(
        max_length=50, blank=True, help_text='e.g. "Python", "SQL"'
    )
    summary = models.TextField(blank=True)
    is_free = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    estimated_hours = models.PositiveIntegerField(
        default=1, help_text="Estimated time to complete (in hours)"
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

    content_panels = Page.content_panels + [
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
        FieldPanel("summary"),
        FieldPanel("what_you_learn"),
        FieldPanel("prerequisites"),
        FieldPanel("og_image"),
    ]

    parent_page_types = ["lms.TopicPage"]
    subpage_types = ["lms.LessonPage"]

    def ordered_lessons(self):
        return LessonPage.objects.child_of(self).live().order_by("path")

    @property
    def lesson_count(self):
        return self.ordered_lessons().count()

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
        context["lesson_slugs_json"] = json.dumps([l.slug for l in lessons])
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
        ],
        use_json_field=True,
    )
    estimated_minutes = models.PositiveIntegerField(
        default=10, help_text="Estimated reading time (minutes)"
    )

    content_panels = Page.content_panels + [
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
        return context
