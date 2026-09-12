# quiz/models.py
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import InlinePanel
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet

from pyverse.taxonomy import Difficulty


class QuizTechnique(TaggedItemBase):
    """Technique tags for quizzes (spec §5: Technique covers quiz items)."""

    content_object = ParentalKey(
        "quiz.Quiz",
        related_name="tagged_techniques",
        on_delete=models.CASCADE,
    )


class QuestionType(models.TextChoices):
    TRUE_FALSE = "true_false", "True / False"
    MCQ = "mcq", "Multiple Choice"


class Quiz(ClusterableModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    instructions = models.TextField(blank=True)
    pass_percentage = models.PositiveSmallIntegerField(default=70)
    randomize_questions = models.BooleanField(default=False)
    quiz_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.TRUE_FALSE,
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
        help_text="Easy / Medium / Hard — the same axis challenges use.",
    )

    topic = models.ForeignKey(
        "topics.PracticeTopicPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quizzes",  # different related_name than coding_problems
        help_text=(
            "The practice topic this quiz belongs to. Without one it is "
            "unreachable from any Track."
        ),
    )

    techniques = TaggableManager(
        through=QuizTechnique,
        related_name="quiz_techniques",
        blank=True,
        verbose_name="Techniques",
        help_text=(
            "Python idioms this quiz drills (spec §5: Technique applies to quiz "
            "items and challenges)."
        ),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("topic"),
        FieldPanel("difficulty"),
        FieldPanel("instructions"),
        FieldPanel("pass_percentage"),
        FieldPanel("randomize_questions"),
        FieldPanel("techniques"),
        InlinePanel("questions", label="Questions"),
    ]

    class Meta:
        verbose_name_plural = "quizzes"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Flat, like challenge pages: /practice/quiz/<slug>/."""
        return f"/practice/quiz/{self.slug}/"

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def total_points(self):
        return sum(question.points for question in self.questions.all())

    def to_json_dict(self):
        return {
            "slug": self.slug,
            "title": self.title,
            "instructions": self.instructions,
            "pass_percentage": self.pass_percentage,
            "randomize_questions": self.randomize_questions,
            "questions": [q.to_json_dict() for q in self.questions.all()],
        }


class Question(Orderable, ClusterableModel):
    quiz = ParentalKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question_type = models.CharField(
        max_length=20, choices=QuestionType.choices, default=QuestionType.MCQ,
    )
    text = models.TextField()
    code_snippet = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    points = models.PositiveSmallIntegerField(default=1)
    correct_bool = models.BooleanField(null=True, blank=True)

    panels = [
        FieldPanel("question_type"),
        FieldPanel("text"),
        FieldPanel("code_snippet"),
        FieldPanel("correct_bool"),
        FieldPanel("points"),
        FieldPanel("explanation"),
        InlinePanel("choices", label="Choices (MCQ only)"),
    ]

    def to_json_dict(self):
        return {
            "id": self.id,
            "type": self.question_type,
            "text": self.text,
            "code_snippet": self.code_snippet,
            "explanation": self.explanation,
            "points": self.points,
            "correct_bool": self.correct_bool
            if self.question_type == QuestionType.TRUE_FALSE
            else None,
            "choices": [c.to_json_dict() for c in self.choices.all()],
        }


class Choice(Orderable):
    question = ParentalKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    panels = [FieldPanel("text"), FieldPanel("is_correct")]

    def to_json_dict(self):
        return {"id": self.id, "text": self.text, "is_correct": self.is_correct}
