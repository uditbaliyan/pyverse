from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.fields import StreamField
from wagtail_ai.panels import AITitleFieldPanel

from pyverse.common.blocks import EditorialApproachBlock
from pyverse.taxonomy import Difficulty


# Each axis needs its own through model: taggit refuses two TaggableManagers
# sharing one, and separate tables keep company/pattern/technique tags from
# being conflated in queries.
class ProblemCompany(TaggedItemBase):
    content_object = ParentalKey(
        "coding.CodingProblem",
        related_name="tagged_companies",
        on_delete=models.CASCADE,
    )


class ProblemPattern(TaggedItemBase):
    content_object = ParentalKey(
        "coding.CodingProblem",
        related_name="tagged_patterns",
        on_delete=models.CASCADE,
    )


class ProblemTechnique(TaggedItemBase):
    content_object = ParentalKey(
        "coding.CodingProblem",
        related_name="tagged_techniques",
        on_delete=models.CASCADE,
    )


class Comparator(models.TextChoices):
    """How a returned value is compared with a test case's expected output.

    A single equality rule does not generalise across problems: Two Sum may
    return its index pair in either order, float problems need an epsilon, and
    some answers are only equal structurally. The harness dispatches on this
    field instead of hardcoding one comparison.
    """

    EXACT = "exact", "Exact equality"
    SORTED_LIST = "sorted_list", "Order-independent list"
    FLOAT_TOLERANCE = "float_tolerance", "Numbers within epsilon"
    CUSTOM = "custom", "Custom comparator (compare(actual, expected) -> bool)"


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


class ExampleBlock(blocks.StructBlock):
    input = blocks.TextBlock(
        required=False,
        help_text='Arguments as they should be read, e.g. "nums = [2,7,11,15], target = 9".',
    )
    output = blocks.TextBlock(
        required=False,
        help_text='The value the function should return, e.g. "[0,1]".',
    )
    note = blocks.CharBlock(
        required=False,
        help_text="Optional one-line explanation shown under the example.",
    )

    class Meta:
        icon = "doc-full"
        label = "Example"


class HintBlock(blocks.StructBlock):
    class Tier(models.TextChoices):
        NUDGE = "nudge", "1 · Nudge"
        APPROACH = "approach", "2 · Approach"
        SOLUTION = "solution", "3 · Near-solution"

    tier = blocks.ChoiceBlock(choices=Tier.choices, default=Tier.NUDGE)
    text = blocks.RichTextBlock(
        help_text="Revealed only when the learner asks for this tier.",
    )

    class Meta:
        icon = "help"
        label = "Hint"


class TraceNoteBlock(blocks.StructBlock):
    """A sentence of *why*, shown while the reference trace is on `line`."""

    line = blocks.IntegerBlock(
        min_value=1,
        help_text="1-based line of the reference solution this note explains.",
    )
    note = blocks.CharBlock(
        max_length=240,
        help_text="Plain text, one or two sentences. Say why, not what.",
    )
    every_visit = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Off: shown the first time the trace reaches the line only.",
    )

    class Meta:
        icon = "comment"
        label = "Trace note"


class TracePredictionBlock(blocks.StructBlock):
    """A question asked before the learner steps past `line`."""

    line = blocks.IntegerBlock(
        min_value=1,
        help_text="1-based line of the reference solution the question is about.",
    )
    question = blocks.CharBlock(
        max_length=240,
        help_text="E.g. 'What will seen contain after this line runs?'",
    )
    answer = blocks.CharBlock(
        max_length=240,
        help_text="Revealed on request. Must hold for the pinned Trace example.",
    )

    class Meta:
        icon = "help"
        label = "Prediction"


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
    function_signature = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Arguments and return type as written in the definition, "
            'e.g. "(nums: list[int], target: int) -> list[int]".'
        ),
    )
    comparator = models.CharField(
        max_length=20,
        choices=Comparator,
        default=Comparator.EXACT,
        help_text=(
            "How a returned value is compared against each test case's "
            "expected output. Wrong choice = correct solutions marked wrong."
        ),
    )
    custom_comparator_code = models.TextField(
        blank=True,
        help_text=(
            "Only used when the comparator is 'Custom comparator'. Python "
            "source defining compare(actual, expected) -> bool; it runs in "
            "the learner's browser next to their own code."
        ),
    )
    examples = StreamField(
        [("example", ExampleBlock())],
        use_json_field=True,
        blank=True,
        help_text="Worked examples shown in the Description tab.",
    )
    constraints = StreamField(
        [("item", blocks.CharBlock(label="Constraint"))],
        use_json_field=True,
        blank=True,
        help_text="Constraints listed under the examples, e.g. '1 <= nums.length <= 10^4'.",
    )
    hint_tiers = StreamField(
        [("hint", HintBlock())],
        use_json_field=True,
        blank=True,
        help_text=(
            "Up to three hints, revealed one at a time in the order written. "
            "Write them nudge → approach → near-solution."
        ),
    )
    editorial_approaches = StreamField(
        [("approach", EditorialApproachBlock())],
        use_json_field=True,
        blank=True,
        help_text="Editorial tab content: one block per approach, cheapest first.",
    )
    trace_notes = StreamField(
        [("note", TraceNoteBlock())],
        use_json_field=True,
        blank=True,
        help_text=(
            "Optional 'why' notes shown while the reference solution is traced on "
            "the pinned Trace example. Needs a reference solution and a Trace example."
        ),
    )
    trace_predictions = StreamField(
        [("prediction", TracePredictionBlock())],
        use_json_field=True,
        blank=True,
        help_text=(
            "Optional 'what happens next?' questions for the same trace. "
            "Learners can always keep stepping; answers are revealed on request."
        ),
    )
    solution_code = models.TextField(
        blank=True,
        help_text="Reference solution shown in the Solutions tab.",
    )
    solution_explanation = RichTextField(
        blank=True,
        help_text="Prose that accompanies the reference solution.",
    )
    starter_code = models.TextField(
        blank=True,
        help_text="Boilerplate/stub code pre-filled into the student's editor when they open this problem.",
    )
    # Tag axes (spec §5). Company and Pattern are interview-prep browsing;
    # Technique is idiomatic-Python browsing. They are taggit tags rather than
    # choice fields because a problem genuinely carries several of each, and a
    # closed vocabulary would need a migration per new pattern.
    companies = TaggableManager(
        through=ProblemCompany,
        related_name="problem_companies",
        blank=True,
        verbose_name="Companies",
        help_text=(
            "Interview-style relevance (e.g. Google, Amazon, Startup). "
            "Adds a Company filter to the Practice landing."
        ),
    )
    patterns = TaggableManager(
        through=ProblemPattern,
        related_name="problem_patterns",
        blank=True,
        verbose_name="Patterns",
        help_text=(
            "Algorithmic approach (e.g. Two Pointers, Sliding Window, DFS/BFS)."
        ),
    )
    techniques = TaggableManager(
        through=ProblemTechnique,
        related_name="problem_techniques",
        blank=True,
        verbose_name="Techniques",
        help_text=(
            "Python-level idioms this problem exercises (e.g. Enumeration, "
            "Dict Comprehension)."
        ),
    )
    test_cases = StreamField(
        [("test_case", TestCaseBlock())],
        use_json_field=True,
        blank=True,
        help_text="The ordered list of test cases used to grade submissions to this problem. Add at least one non-hidden case so students can self-check.",
    )
    trace_case = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Trace example",
        help_text=(
            "Which visible case (1 = first) 'Trace the reference solution' shows "
            "after a pass. Leave empty to use the first. "
            "`manage.py check_problem_traces --apply` picks one for you."
        ),
    )

    panels = [
        FieldPanel("topic"),
        AITitleFieldPanel("title", classname="title"),
        FieldPanel("slug"),
        FieldPanel("difficulty"),
        FieldPanel("description"),
        FieldPanel("examples"),
        FieldPanel("constraints"),
        FieldPanel("function_name"),
        FieldPanel("function_signature"),
        FieldPanel("starter_code"),
        FieldPanel("comparator"),
        FieldPanel("custom_comparator_code"),
        FieldPanel("test_cases"),
        FieldPanel("trace_case"),
        FieldPanel("hint_tiers"),
        FieldPanel("editorial_approaches"),
        FieldPanel("solution_code"),
        FieldPanel("trace_notes"),
        FieldPanel("trace_predictions"),
        FieldPanel("solution_explanation"),
        FieldPanel("companies"),
        FieldPanel("patterns"),
        FieldPanel("techniques"),
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
            while CodingProblem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{suffix}"[:200]
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Canonical URL: flat, under the Practice hub.

        Was `/practice/<topic>/<slug>/`; every published nested URL is kept
        alive by a permanent redirect (see the `coding` data migration), so the
        move costs no inbound links.
        """
        return f"/practice/problem/{self.slug}/"

    @property
    def visible_test_cases(self):
        return [case for case in self.test_case_payload() if not case["hidden"]]

    # Tag axes, flattened for templates and the client-side filters. Sorted so
    # the emitted attribute is stable between renders.
    @property
    def company_names(self):
        return ",".join(sorted(self.companies.names()))

    @property
    def pattern_names(self):
        return ",".join(sorted(self.patterns.names()))

    @property
    def technique_names(self):
        return ",".join(sorted(self.techniques.names()))

    @property
    def trace_case_input(self):
        """Argument source for the reference trace's example, or "" for none.

        `trace_case` is 1-based among the visible cases; an out-of-range value
        (cases were removed after it was set) is ignored, not an error.
        """
        visible = self.visible_test_cases
        if self.trace_case and 1 <= self.trace_case <= len(visible):
            return visible[self.trace_case - 1]["input"]
        return ""

    @property
    def trace_annotations(self):
        """Step notes and predictions for the reference trace, or None.

        They describe one specific example, so they are only served when the
        reference solution exists and a Trace example is pinned (the page then
        shows them only while that exact call is traced). Plain JSON-safe data;
        the page renders it with `json_script` and the viewer with `textContent`.
        """
        if not (self.solution_code.strip() and self.trace_case_input):
            return None
        notes = [
            {
                "line": block.value["line"],
                "note": block.value["note"],
                "every_visit": bool(block.value["every_visit"]),
            }
            for block in self.trace_notes
        ]
        predictions = [
            {
                "line": block.value["line"],
                "question": block.value["question"],
                "answer": block.value["answer"],
            }
            for block in self.trace_predictions
        ]
        if not (notes or predictions):
            return None
        return {"notes": notes, "predictions": predictions}

    def clean(self):
        super().clean()
        total = len(self.solution_code.splitlines())
        errors = {}
        for field_name, label in (
            ("trace_notes", "note"),
            ("trace_predictions", "prediction"),
        ):
            bad = [
                block.value["line"]
                for block in getattr(self, field_name)
                if not 1 <= block.value["line"] <= max(total, 1)
            ]
            if bad:
                errors[field_name] = (
                    f"Line {', '.join(map(str, bad))}: the reference solution has "
                    f"{total} lines, so this {label} would never show."
                )
        if errors:
            raise ValidationError(errors)

    @property
    def trace_status(self):
        """Cheap authoring-time status for the admin list (no code is run).

        The full check (does it verify, how many steps) is the
        `check_problem_traces` command; running it per list row would be slow.
        """
        if not self.solution_code.strip():
            return "no reference solution"
        if not self.visible_test_cases:
            return "no visible example"
        if self.trace_case_input:
            return f"ready (example {self.trace_case})"
        return "ready (first example)"

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

    def grading_payload(self):
        """Everything the in-browser harness needs, baked into the page.

        Spec approach A: no runtime fetch — the problem's own static HTML
        carries its function name, comparator and cases. Custom comparator
        source travels as a string and is exec'd in the learner's browser,
        next to their own code, so nothing executes server-side.
        """
        return {
            "fn": self.function_name,
            "signature": self.function_signature,
            "comparator": self.comparator,
            "custom": (
                self.custom_comparator_code
                if self.comparator == Comparator.CUSTOM
                else ""
            ),
            "cases": self.test_case_payload(),
        }
