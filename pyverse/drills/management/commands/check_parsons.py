"""Authoring gate for Parsons puzzles (run in CI next to ``check_gym``).

manage.py check_parsons [--strict]
"""

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.drills import parsons
from pyverse.drills.models import ParsonsProblem


class Command(BaseCommand):
    help = "Verify every Parsons puzzle's reference program parses and prints what it claims."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="warnings fail too")

    def handle(self, *args, **options):
        failing = warned = 0
        problems = list(ParsonsProblem.objects.order_by("slug"))
        for problem in problems:
            report = parsons.verify(problem.lines, problem.expected_output)
            if problem.topic_id is None:
                report.warnings.append("not in any topic page (unreachable)")
            status = (
                "FAIL" if report.errors else ("warn" if report.warnings else "  ok")
            )
            self.stdout.write(f"[{status}] {problem.slug}")
            for line in (*report.errors, *report.warnings):
                self.stdout.write(f"         ! {line}")
            failing += bool(report.errors)
            warned += bool(report.warnings) and not report.errors
        self.stdout.write(
            f"\n{len(problems)} puzzles: {len(problems) - failing - warned} ok, "
            f"{warned} with warnings, {failing} failing.",
        )
        if failing or (options["strict"] and warned):
            msg = "parsons check failed"
            raise CommandError(msg)
