# quiz/models.py
"""
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


class QuestionType(models.TextChoices):
    TRUE_FALSE = "true_false", "True / False"
    MCQ = "mcq", "Multiple Choice"


@register_snippet
class Quiz(ClusterableModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    instructions = models.TextField(blank=True)
    pass_percentage = models.PositiveSmallIntegerField(default=70)
    randomize_questions = models.BooleanField(default=False)

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("instructions"),
        FieldPanel("pass_percentage"),
        FieldPanel("randomize_questions"),
        InlinePanel("questions", label="Questions"),
    ]

    def __str__(self):
        return self.title

    def to_json_dict(self):
        """Flattened, client-safe(ish) representation baked into the static page."""
        return {
            "slug": self.slug,
            "title": self.title,
            "instructions": self.instructions,
            "pass_percentage": self.pass_percentage,
            "randomize_questions": self.randomize_questions,
            "questions": [q.to_json_dict() for q in self.questions.all()],
        }


class Question(Orderable):
    quiz = ParentalKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question_type = models.CharField(
        max_length=20, choices=QuestionType.choices, default=QuestionType.MCQ
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
"""
