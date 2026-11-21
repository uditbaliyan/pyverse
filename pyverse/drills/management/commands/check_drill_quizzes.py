"""Authoring gate: every quiz question shown in Drills must be answerable.

manage.py check_drill_quizzes
"""

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.drills import quizitems
from pyverse.quiz.models import Question


class Command(BaseCommand):
    help = "Check that quiz questions in Drills topics have a correct answer."

    def handle(self, *args, **options):
        failing = 0
        questions = Question.objects.filter(quiz__drill_topic__isnull=False)
        for question in questions.select_related("quiz").prefetch_related("choices"):
            problems = quizitems.errors(question)
            if problems:
                failing += 1
                self.stdout.write(f"[FAIL] {question.quiz.slug} #{question.pk}")
                for problem in problems:
                    self.stdout.write(f"         ! {problem}")
        self.stdout.write(f"{questions.count()} questions, {failing} failing.")
        if failing:
            msg = "drill quiz check failed"
            raise CommandError(msg)
