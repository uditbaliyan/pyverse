"""The generators ``ai_create`` offers, in menu order.

Adding a content type is adding one module here and one style guide in
``styles/`` — the menu, the parent selection, the style loading, the model call
and the refusal handling are shared.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .blog import BlogGenerator
from .dsa import DsaGenerator
from .lesson import LessonGenerator
from .quiz import QuizGenerator

if TYPE_CHECKING:
    from .base import Generator

GENERATORS: tuple[type[Generator], ...] = (
    DsaGenerator,
    BlogGenerator,
    LessonGenerator,
    QuizGenerator,
)
