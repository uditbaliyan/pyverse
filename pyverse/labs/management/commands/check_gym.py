from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.labs.gym import verify
from pyverse.labs.gym_models import GymExercisePage


class Command(BaseCommand):
    help = "Quality gate: each live exercise's solution must pass its check; the starter must not."  # noqa: E501

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            action="append",
            help="limit to a slug (repeatable)",
        )
        parser.add_argument("--strict", action="store_true", help="warnings fail too")

    def handle(self, *args, **opts):
        qs = GymExercisePage.objects.live()
        if opts["slug"]:
            qs = qs.filter(slug__in=opts["slug"])
        errors = warnings = 0
        for ex in qs:
            if not ex.solution_code.strip():
                warnings += 1
                self.stdout.write(f"WARN  {ex.slug}: no solution to verify")
            else:
                ok, msg = verify(ex.setup_code, ex.solution_code, ex.check_code)
                if not ok:
                    errors += 1
                    self.stdout.write(f"ERROR {ex.slug}: solution fails: {msg}")
            if (
                ex.starter_code.strip()
                and verify(ex.setup_code, ex.starter_code, ex.check_code)[0]
            ):
                warnings += 1
                self.stdout.write(f"WARN  {ex.slug}: starter already passes the check")
        self.stdout.write(
            f"{qs.count()} exercises, {errors} errors, {warnings} warnings",
        )
        if errors or (opts["strict"] and warnings):
            raise CommandError("check_gym failed")  # noqa: EM101, TRY003
