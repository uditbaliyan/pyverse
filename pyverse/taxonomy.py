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


class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"
