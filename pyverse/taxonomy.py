"""Shared, app-independent taxonomy choices.

Spec §5 (§18 cross-cutting finding 2) fixes the difficulty vocabulary at
Easy / Medium / Hard. Both `coding` and `quiz` author against it, so it lives
here rather than in either app — importing one content app from the other
would invert the dependency direction the apps are built on.

Not the same axis as `lms.DifficultyLevel` (beginner / intermediate / advanced
/ all-levels), which describes how advanced a whole course is. This one tags a
single exercise: Easy / Medium / Hard.
"""

from django.db import models
from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Value
from django.db.models import When


class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"


# `difficulty` is stored as a string, so ordering alphabetically would give
# Easy → Hard → Medium. Ranked ordering is what every Practice surface wants
# (Tracks default to difficulty ascending, spec §4).
DIFFICULTY_RANK = Case(
    When(difficulty=Difficulty.EASY, then=Value(0)),
    When(difficulty=Difficulty.MEDIUM, then=Value(1)),
    When(difficulty=Difficulty.HARD, then=Value(2)),
    default=Value(3),
    output_field=IntegerField(),
)
