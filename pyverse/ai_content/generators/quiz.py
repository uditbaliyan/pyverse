"""Generate a ``Quiz`` with its ``Question`` and ``Choice`` children.

Built through modelcluster's child-object pattern rather than a StreamField:
save the quiz, then its questions, then each question's choices, setting
``sort_order`` explicitly so the order the model wrote is the order learners
meet.

The one thing that cannot be checked mechanically is the answer key — there is
no way to *run* a factual answer the way a DSA solution is run. Two things
stand in for that: the schema requires the model to state its reasoning in
``explanation``, and the shape of the key is validated hard (exactly one correct
choice, a real boolean for true/false) so the only remaining risk is a
confidently wrong fact, which the review notes tell Udit to look for.

Like ``CodingProblem``, a quiz with no topic is unreachable from any track, so
leaving ``topic`` unset is what keeps it out of learners' way until review.
"""

from __future__ import annotations

from typing import Any
from typing import ClassVar

from django.urls import reverse
from django.utils.text import slugify

from pyverse.ai_content.exceptions import GenerationError
from pyverse.ai_content.generators.base import Draft
from pyverse.ai_content.generators.base import Generator
from pyverse.ai_content.generators.base import choice as pick
from pyverse.ai_content.generators.base import flag as yes_no
from pyverse.ai_content.generators.base import optional_text
from pyverse.ai_content.generators.base import required_text
from pyverse.ai_content.generators.base import rows
from pyverse.ai_content.generators.base import whole_number
from pyverse.quiz.models import Choice
from pyverse.quiz.models import Question
from pyverse.quiz.models import QuestionType
from pyverse.quiz.models import Quiz
from pyverse.taxonomy import Difficulty

#: The quiz page renders choices as single-answer buttons, so a question with
#: one choice could not be answered wrong.
MIN_CHOICES = 2

_SCHEMA = f"""\
Reply with one JSON object with exactly these keys:

{{
  "title": "quiz title, sentence case",
  "instructions": "one or two plain sentences on what this quiz checks",
  "difficulty": "easy",
  "pass_percentage": 70,
  "randomize_questions": false,
  "quiz_type": "mcq",
  "questions": [
    {{
      "question_type": "mcq",
      "text": "The question, plain text",
      "code_snippet": "",
      "explanation": "Why the right answer is right, and why the close one is not",
      "points": 1,
      "correct_bool": null,
      "choices": [
        {{"text": "The correct answer", "is_correct": true}},
        {{"text": "A plausible mistake", "is_correct": false}},
        {{"text": "Another plausible mistake", "is_correct": false}},
        {{"text": "A third plausible mistake", "is_correct": false}}
      ]
    }},
    {{
      "question_type": "true_false",
      "text": "A statement that is either true or false",
      "code_snippet": "",
      "explanation": "Why it is what it is",
      "points": 1,
      "correct_bool": false,
      "choices": []
    }}
  ]
}}

Rules the answer key depends on:
- question_type is "mcq" or "true_false"; quiz_type is one of
  {", ".join(f'"{value}"' for value in QuestionType.values)} and should be the type
  most of the questions use.
- An mcq has exactly four choices and exactly one of them correct. A
  true_false question has correct_bool set to true or false, no choices, and
  correct_bool left null on every mcq.
- explanation is required on every question and is the reasoning a reviewer
  reads to check the key: say why the correct answer is correct, in terms of
  the language, not "this is the right one".
- code_snippet is plain Python shown above the choices, or "" when the
  question needs no code. It must run as written.
- difficulty is one of {", ".join(f'"{value}"' for value in Difficulty.values)}.
- Wrong answers must be wrong for a reason a beginner could believe: no
  "all of the above", no negations stacked on negations.
"""


class QuizGenerator(Generator):
    slug: ClassVar[str] = "quiz"
    menu_label: ClassVar[str] = "Quiz"
    label: ClassVar[str] = "Quiz"
    style_file: ClassVar[str] = "quiz.md"
    schema: ClassVar[str] = _SCHEMA
    review_notes: ClassVar[tuple[str, ...]] = (
        "Read the answer key closely — nothing can run a factual answer, so a "
        "wrong key here is invisible to every other check.",
        "Assign a topic to publish it: learners only see quizzes that have one.",
    )

    def pre_create(self, data: dict[str, Any], report: Any = None) -> None:
        # Validated here, before the quiz row exists, so a bad key cannot leave
        # half a quiz behind.
        self._questions(data)

    def create(self, data: dict[str, Any], parent: Any = None) -> Draft:
        # Snippet type: no parent, and no topic until review.
        quiz = Quiz(
            title=required_text(data, "title"),
            slug=_unique_slug(required_text(data, "title")),
            instructions=optional_text(data, "instructions"),
            pass_percentage=whole_number(
                data,
                "pass_percentage",
                default=70,
                minimum=1,
                maximum=100,
            ),
            randomize_questions=yes_no(data, "randomize_questions"),
            quiz_type=pick(
                data,
                "quiz_type",
                list(QuestionType.values),
                default=QuestionType.TRUE_FALSE.value,
            ),
            difficulty=pick(
                data,
                "difficulty",
                list(Difficulty.values),
                default=Difficulty.EASY.value,
            ),
        )
        quiz.save()

        for index, question in enumerate(self._questions(data)):
            choices = question.pop("choices")
            row = Question(quiz=quiz, sort_order=index, **question)
            row.save()
            for choice_index, choice in enumerate(choices):
                Choice(
                    question=row,
                    sort_order=choice_index,
                    text=choice["text"],
                    is_correct=choice["is_correct"],
                ).save()

        return Draft(
            label=self.label,
            title=quiz.title,
            review_url=reverse("wagtailsnippets_quiz_quiz:edit", args=[quiz.pk]),
            notes=self.review_notes,
        )

    def _questions(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        questions = [
            _question(row, index)
            for index, row in enumerate(rows(data, "questions"), start=1)
        ]
        if not questions:
            message = "the model returned no questions"
            raise GenerationError(message)
        return questions


def _question(row: dict[str, Any], index: int) -> dict[str, Any]:
    """One question and its choices, validated against the model's own rules."""
    where = f"question {index}"
    kind = pick(row, "question_type", list(QuestionType.values))
    question: dict[str, Any] = {
        "question_type": kind,
        "text": required_text(row, "text"),
        # The reasoning istelf is the review mechanism for a factual key.
        "explanation": required_text(row, "explanation"),
        "code_snippet": optional_text(row, "code_snippet"),
        "points": whole_number(row, "points", default=1, minimum=1, maximum=10),
        "correct_bool": None,
        "choices": [],
    }

    if kind == QuestionType.TRUE_FALSE.value:
        answer = row.get("correct_bool")
        if not isinstance(answer, bool):
            message = f"{where} is true/false but correct_bool is {answer!r}"
            raise GenerationError(message)
        question["correct_bool"] = answer
        return question

    choices = [
        {
            "text": required_text(choice_row, "text"),
            "is_correct": bool(choice_row.get("is_correct")),
        }
        for choice_row in rows(row, "choices")
    ]
    if len(choices) < MIN_CHOICES:
        message = (
            f"{where} has {len(choices)} choices; a multiple choice question "
            f"needs at least {MIN_CHOICES}"
        )
        raise GenerationError(message)
    correct = [choice for choice in choices if choice["is_correct"]]
    if len(correct) != 1:
        message = (
            f"{where} marks {len(correct)} choices correct; the quiz page answers "
            "each question once, so exactly one must be"
        )
        raise GenerationError(message)
    question["choices"] = choices
    return question


def _unique_slug(title: str) -> str:
    """Quiz slugs are unique and not auto-generated — unlike CodingProblem."""
    base = slugify(title)[:50] or "quiz"
    slug, suffix = base, 2
    while Quiz.objects.filter(slug=slug).exists():
        slug = f"{base}-{suffix}"[:50]
        suffix += 1
    return slug
