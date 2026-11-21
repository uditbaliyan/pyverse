import re
from functools import cached_property

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.html import conditional_escape
from django.utils.html import format_html_join
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.blocks import PageChooserBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail_ai.panels import AIDescriptionFieldPanel
from wagtail_ai.panels import AITitleFieldPanel

# ── Import shared mixins from home app ──────────────────────────────────
from pyverse.home.models import SEOFields
from pyverse.taxonomy import Difficulty as SiteDifficulty

from .utils import course_counts_for
from .utils import lesson_counts_for

# ── Choices ──────────────────────────────────────────────────────────────
# `TopicPage.color` ends up in a style attribute and `icon` in a `data-lucide`
# name, so both are checked on save; `accent_color` checks again on the way out
# for rows saved before the validators existed.
HEX_COLOR = r"\A#[0-9A-Fa-f]{6}\Z"
ICON_NAME = r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z"


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

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # The <code> contents are built here, not in the template, because
        # whitespace inside <pre> is rendered and must be exact. With line numbers
        # every line is its own <span> and CSS (`.code-lines`) draws the digits
        # from a counter, so they are not text: selecting or copying never picks
        # them up. `format_html_join` / `conditional_escape` escape the code.
        if value["show_line_numbers"]:
            lines = re.split(r"\r\n|\r|\n", value["code"])
            if lines and lines[-1] == "":
                lines.pop()  # a trailing newline is not a numbered empty line
            context["code_html"] = format_html_join(
                "\n",
                '<span class="code-line">{}</span>',
                ((line,) for line in lines),
            )
            context["code_lines_class"] = "code-lines"
        else:
            context["code_html"] = conditional_escape(value["code"])
            context["code_lines_class"] = ""
        return context


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
    "exactly one of", so `clean()` enforces it. The target must also sit in a
    Practice topic: the static export only writes the pages of problems and
    quizzes that have one (`seo.live_problems` / `live_quizzes`), so a topic-less
    target would leave this checkpoint linking to a page that does not exist. A
    topic that is merely unpublished is accepted, so authors can build the lesson
    first; publish the topic before the lesson.
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
        field = "problem" if result["problem"] else "quiz"
        if result[field].topic_id is None:
            raise blocks.StructBlockValidationError(
                block_errors={
                    field: ValidationError(
                        f"This {field} is not in a Practice topic, so its page is "
                        "never published. Add it to a topic first.",
                    ),
                },
            )
        return result


class DrillTopicBlock(blocks.StructBlock):
    """A reference from a lesson to a whole Drills topic (e.g. a Parsons set).

    Drill items have no page of their own, so the topic page is the unit a lesson
    can point at. The card shows the item count and, client-side, how many the
    learner has solved (``static/js/drill-progress.js``). No gating: a topic is a
    practice set, not a checkpoint.
    """

    topic = PageChooserBlock(page_type="drills.DrillTopicPage")
    prompt = blocks.CharBlock(
        required=False,
        max_length=200,
        help_text="Optional one-liner: what to practise here, shown on the card.",
    )

    class Meta:
        icon = "list-ol"
        template = "lms/blocks/drill_topic_embed.html"
        label = "Drill Set"


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
        topics = list(
            TopicPage.objects.child_of(self).live().order_by("display_order", "title"),
        )
        topic_counts = course_counts_for(self, topics)
        for topic in topics:
            topic.set_course_count(topic_counts.get(topic.pk, 0))
        context["topics"] = topics
        featured_courses = list(
            CoursePage.objects.descendant_of(self)
            .live()
            .filter(is_featured=True)
            .select_related("hero_image")
            .order_by("-first_published_at", "path")[:6],
        )
        counts = lesson_counts_for(self, featured_courses)
        for course in featured_courses:
            course.set_lesson_count(counts.get(course.pk, 0))
        context["featured_courses"] = featured_courses
        context["all_courses_count"] = (
            CoursePage.objects.descendant_of(self).live().count()
        )
        context["all_topics_count"] = len(topics)
        return context


# ── Topic Page ───────────────────────────────────────────────────────────
class TopicPage(Page):
    icon = models.CharField(
        max_length=50,
        blank=True,
        validators=[
            RegexValidator(
                ICON_NAME,
                "Use a Lucide icon name: lowercase letters, digits and single "
                "hyphens, e.g. chart-bar.",
            ),
        ],
        help_text='Icon name (e.g. "code", "database", "chart-bar")',
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        validators=[
            RegexValidator(HEX_COLOR, "Use a six-digit hex colour, e.g. #C62828."),
        ],
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

    @property
    def accent_color(self):
        """`color` when it is a valid hex colour, else "" (see `HEX_COLOR`)."""
        return self.color if re.fullmatch(HEX_COLOR, self.color) else ""

    #: Filled by `set_course_count` on the hub so a grid of topic cards costs one
    #: query instead of one COUNT per card. `None` means "not filled".
    _course_count: int | None = None

    def set_course_count(self, count):
        """Record a count the caller already batched (`course_counts_for`), so
        rendering this topic's card costs no query."""
        self._course_count = count

    @property
    def course_count(self):
        """Live course count — cached on the instance after the first access."""
        if self._course_count is None:
            self._course_count = CoursePage.objects.child_of(self).live().count()
        return self._course_count

    def get_context(self, request):
        context = super().get_context(request)
        # Every live course goes on this one page. The export writes one file per
        # page and never sees a query string, so the grid cannot be filtered or
        # paged on the server; `static/lms/js/course-filter.js` filters it in the
        # browser. Editors arrange courses with `display_order`; courses sharing
        # a number stay newest first, and `path` keeps equal timestamps stable.
        courses = list(
            CoursePage.objects.child_of(self)
            .live()
            .select_related("hero_image")
            .order_by("display_order", "-first_published_at", "path"),
        )
        counts = lesson_counts_for(self, courses)
        for course in courses:
            course.set_lesson_count(counts.get(course.pk, 0))
        context["courses"] = courses
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
    display_order = models.IntegerField(
        default=0,
        help_text=(
            "Position in its topic: lower numbers come first (use a negative "
            "number to pin a course to the top). Courses with the same number "
            "stay newest first."
        ),
    )
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
                FieldPanel("display_order"),
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

    @cached_property
    def topic(self):
        return TopicPage.objects.parent_of(self).first()

    def get_context(self, request):
        context = super().get_context(request)
        context["lessons"] = self.ordered_lessons()
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
            ("drill_set", DrillTopicBlock()),
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

    @cached_property
    def course(self):
        return CoursePage.objects.parent_of(self).first()

    @cached_property
    def topic(self):
        course = self.course
        return course.topic if course else None

    @property
    def progress_key(self):
        """The identity the browser stores this lesson's progress under.

        `topic/course/lesson` slugs, read off `url_path` (no query). A lesson slug
        alone is only unique among its siblings, so two courses that both have an
        `introduction` lesson would otherwise share one progress record. See
        `static/lms/js/lesson-progress.js`.
        """
        return "/".join(self.url_path.strip("/").split("/")[-3:])

    def _lessons_in_reading_order(self):
        """The course's live lessons in tree order, with this lesson among them.

        A draft previewed from the editor is not live, so the live query alone
        would leave it out and the preview would read "Lesson 0 of N" with no
        neighbours. Slot it in by tree path instead; a page that is not saved yet
        has no place in the tree and goes last.
        """
        lessons = list(LessonPage.objects.sibling_of(self).live().order_by("path"))
        if self in lessons:
            return lessons
        if self.pk is None:
            return [*lessons, self]
        before = [lesson for lesson in lessons if lesson.path < self.path]
        return [*before, self, *lessons[len(before) :]]

    def get_context(self, request):
        context = super().get_context(request)
        siblings = self._lessons_in_reading_order()
        idx = siblings.index(self)
        context["prev_lesson"] = siblings[idx - 1] if idx > 0 else None
        context["next_lesson"] = siblings[idx + 1] if idx < len(siblings) - 1 else None
        context["lesson_index"] = idx + 1
        context["total_lessons"] = len(siblings)
        context["course"] = self.course
        context["topic"] = self.topic
        context["lesson_list"] = siblings
        # Heavy scripts load only on lessons that use them: a page includes
        # `includes/pyscript_runtime.html` once, never twice (see that file's
        # header), and Mermaid is a multi-megabyte CDN download.
        block_types = {block.block_type for block in self.body}
        context["has_notebook"] = "notebook" in block_types
        context["has_mermaid"] = "mermaid" in block_types
        return context
