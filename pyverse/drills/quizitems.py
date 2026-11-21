"""Quiz questions as drill items: the options to show and the authoring check.

Mirrors the grading rules of ``templates/quiz/quiz_page.html``: true/false has
``correct_bool``; multiple choice has exactly one correct choice.
"""

from __future__ import annotations

from pyverse.quiz.models import QuestionType


def options(question) -> list[dict]:
    """``[{"text", "correct"}]`` in display order."""
    if question.question_type == QuestionType.TRUE_FALSE:
        return [
            {"text": "True", "correct": question.correct_bool is True},
            {"text": "False", "correct": question.correct_bool is False},
        ]
    return [{"text": c.text, "correct": c.is_correct} for c in question.choices.all()]


def errors(question) -> list[str]:
    """Why this question cannot be answered, or ``[]``."""
    if question.question_type == QuestionType.TRUE_FALSE:
        return (
            []
            if question.correct_bool is not None
            else ["true/false question has no correct answer set"]
        )
    choices = list(question.choices.all())
    found = []
    if len(choices) < 2:  # noqa: PLR2004
        found.append("needs at least two choices")
    correct = sum(c.is_correct for c in choices)
    if correct != 1:
        found.append(f"needs exactly one correct choice, has {correct}")
    return found
