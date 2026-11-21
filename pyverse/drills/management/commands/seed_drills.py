"""Create the Drills pages and starter Parsons puzzles (idempotent).

    manage.py seed_drills

Puts /drills/ -> /drills/parsons/ -> topic pages under the site's home page and
upserts the puzzles from ``seed_data``. Existing pages and edits to puzzles'
positions are left alone; puzzle content is refreshed from the seed.
"""

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.text import slugify
from wagtail.models import Site

from pyverse.drills.models import DrillsHubPage
from pyverse.drills.models import DrillTopicPage
from pyverse.drills.models import DrillTypePage
from pyverse.drills.models import ParsonsProblem
from pyverse.drills.seed_data import PUZZLES
from pyverse.drills.seed_data import TOPICS


def _child(parent, model, slug, **fields):
    page = parent.get_children().filter(slug=slug).first()
    if page:
        return page.specific
    page = model(slug=slug, **fields)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page


class Command(BaseCommand):
    help = "Create /drills/ pages and the starter Parsons puzzles."

    def handle(self, *args, **options):
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            msg = "no default Wagtail site; run load_content or create one first"
            raise CommandError(msg)
        home = site.root_page.specific
        hub = _child(
            home,
            DrillsHubPage,
            "drills",
            title="Drills",
            intro="Short, focused question sets grouped by topic. Pick a type, then a topic.",
        )
        parsons = _child(
            hub,
            DrillTypePage,
            "parsons",
            title="Parsons Puzzles",
            kind=DrillTypePage.Kind.PARSONS,
            intro="Arrange shuffled lines of code, with the right indentation, into a working program.",
        )
        topics = {
            key: _child(parsons, DrillTopicPage, key, title=title)
            for key, title in TOPICS.items()
        }
        for position, item in enumerate(PUZZLES):
            problem, _ = ParsonsProblem.objects.get_or_create(
                slug=item["slug"] or slugify(item["title"]),
                defaults={"title": item["title"], "position": position},
            )
            problem.title = item["title"]
            problem.topic = topics[item["topic"]]
            problem.concept = item["concept"]
            problem.difficulty = item["difficulty"]
            problem.description = item["description"]
            problem.expected_output = item["expected_output"]
            problem.lines = [
                (
                    "line",
                    {
                        "text": text,
                        "indent": indent,
                        "is_distractor": distractor,
                        "feedback": feedback,
                    },
                )
                for text, indent, distractor, feedback in item["lines"]
            ]
            problem.save()
        self.stdout.write(
            self.style.SUCCESS(f"{len(PUZZLES)} puzzles in {len(topics)} topics"),
        )
