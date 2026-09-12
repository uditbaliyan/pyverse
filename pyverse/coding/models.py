from django.db import models
from django.utils.text import slugify
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks

from pyverse.taxonomy import Difficulty


class TestCaseBlock(blocks.StructBlock):
    input = blocks.TextBlock(
        required=True,
        help_text=(
            "The raw input passed to the student's function, written exactly "
            'as it should appear (e.g. "[1, 2, 3], 5").'
        ),
    )
    expected_output = blocks.TextBlock(
        required=True,
        help_text=(
            "The exact expected output/return value for this input. Used to "
            "automatically grade student submissions."
        ),
    )
    is_hidden = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text=(
            "If checked, this test case is still run during grading but its "
            "input/output is never shown to the student, preventing "
            "answer-peeking on edge cases."
        ),
    )

    class Meta:
        icon = "list-ul"
        label = "Test Case"


class CodingProblem(ClusterableModel):
    """
    A single free-practice coding problem, addressable independently of the
    guided LMS. Belongs to exactly one PracticeTopicPage so it can be
    surfaced via an O(1) tree-path query from that topic (or any ancestor
    topic). The `lms` app will later reference this snippet via its own
    ForeignKey to build guided playlists — this app has no knowledge of
    `lms` or `quiz`.
    """

    topic = models.ForeignKey(
        "topics.PracticeTopicPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coding_problems",
        help_text=(
            "The practice topic this problem belongs to. Determines where it "
            "appears in the topic tree. If the topic is later deleted, this "
            "problem is orphaned (topic set to empty) rather than deleted."
        ),
    )
    title = models.CharField(
        max_length=255,
        help_text='The problem\'s display title, shown in listings and admin choosers (e.g. "Two Sum").',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text=(
            "URL segment for this challenge's canonical page "
            "(/practice/<topic>/<slug>/). Left blank, it is generated from "
            "the title."
        ),
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
        help_text="Easy / Medium / Hard — the only difficulty axis used site-wide.",
    )
    description = RichTextField(
        blank=True,
        help_text=(
            "The problem statement shown above the editor on the challenge "
            "page: what the function must do, constraints, examples."
        ),
    )
    function_name = models.CharField(
        max_length=100,
        help_text=(
            "The exact name of the function the student must implement "
            '(e.g. "two_sum"). Used to wire up the grading harness — must '
            "match the function name used in the starter code."
        ),
    )
    starter_code = models.TextField(
        blank=True,
        help_text="Boilerplate/stub code pre-filled into the student's editor when they open this problem.",
    )
    test_cases = StreamField(
        [("test_case", TestCaseBlock())],
        use_json_field=True,
        blank=True,
        help_text="The ordered list of test cases used to grade submissions to this problem. Add at least one non-hidden case so students can self-check.",
    )

    panels = [
        FieldPanel("topic"),
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("difficulty"),
        FieldPanel("description"),
        FieldPanel("function_name"),
        FieldPanel("starter_code"),
        FieldPanel("test_cases"),
    ]

    class Meta:
        verbose_name = "Coding Problem"
        verbose_name_plural = "Coding Problems"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "problem"
            slug, suffix = base, 2
            while (
                CodingProblem.objects.filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base}-{suffix}"[:200]
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Canonical URL: nested under this problem's owning topic.

        One URL per problem, because `topic` is a single FK — browsing an
        ancestor topic links here rather than minting a second path.
        """
        topic = self.topic
        if topic is None or not topic.live:
            return ""
        return f"{topic.url}{self.slug}/"

    @property
    def visible_test_cases(self):
        return [case for case in self.test_case_payload() if not case["hidden"]]

    def test_case_payload(self):
        """Test cases as plain JSON-safe dicts, for the client-side grader.

        `input` is Python source for the argument list (e.g. "[1, 2], 5") and
        is evaluated in the student's namespace, which is why it is authored
        as source rather than split into typed fields.
        """
        return [
            {
                "input": child.value["input"],
                "expected": child.value["expected_output"],
                "hidden": bool(child.value["is_hidden"]),
            }
            for child in self.test_cases
        ]
