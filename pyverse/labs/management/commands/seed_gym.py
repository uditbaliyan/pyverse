from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.labs.gym_models import GymExercisePage
from pyverse.labs.gym_models import GymHubPage
from pyverse.labs.gym_seed import SEED
from pyverse.labs.models import LabsIndexPage


class Command(BaseCommand):
    help = "Create the Gym hub (if missing) and any seed exercises not already present."

    def handle(self, *args, **opts):
        index = LabsIndexPage.objects.first()
        if index is None:
            raise CommandError("Create a LabsIndexPage first.")  # noqa: EM101, TRY003
        hub = GymHubPage.objects.first() or index.add_child(
            instance=GymHubPage(
                title="Gym",
                slug="gym",
                intro="<p>Free practice. Runs in your browser; nothing is saved.</p>",
            ),
        )
        made = 0
        for ex in SEED:
            if GymExercisePage.objects.filter(slug=ex["slug"]).exists():
                continue
            page = hub.add_child(instance=GymExercisePage(**ex))
            page.save_revision().publish()
            made += 1
        self.stdout.write(f"created {made} exercise(s)")
