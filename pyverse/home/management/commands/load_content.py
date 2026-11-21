"""Replace the default Wagtail scaffold with the committed content fixture.

    uv run python manage.py migrate
    uv run python manage.py load_content            # content/site.json

Safe to re-run: it clears the page tree below the root first. Never run it
against a database holding content you have not dumped (``dump_content``).
"""

from __future__ import annotations

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from wagtail.models import Page
from wagtail.models import Site

DEFAULT_PATH = Path("content/site.json")


class Command(BaseCommand):
    help = "Load content/site.json into an otherwise empty, migrated database."

    def add_arguments(self, parser):
        parser.add_argument("--input", default=str(DEFAULT_PATH))
        parser.add_argument(
            "--hostname",
            default="localhost",
            help="hostname for the default Site (default: localhost)",
        )
        parser.add_argument("--port", type=int, default=80)

    @transaction.atomic
    def handle(self, *args, **options):
        src = Path(options["input"])
        if not src.is_file():
            msg = f"{src} not found; run `manage.py dump_content` first"
            raise CommandError(msg)

        # Raw deletes: Wagtail 7.4.x models reference tables (search promotions)
        # that no released migration creates, so the collector-based
        # ``Page.delete()`` fails on a clean database. The scaffold being
        # cleared is only the welcome page, which has no dependants.
        db = Page.objects.db
        Site.objects.all()._raw_delete(db)  # noqa: SLF001
        Page.objects.filter(depth__gt=1)._raw_delete(db)  # noqa: SLF001
        call_command("loaddata", str(src), verbosity=0)

        Page.fix_tree()
        if not Site.objects.exists():
            root = Page.objects.filter(slug="ghar").first() or Page.objects.get(depth=2)
            Site.objects.create(
                hostname=options["hostname"],
                port=options["port"],
                root_page=root,
                is_default_site=True,
                site_name="PyVerse",
            )
        self.stdout.write(
            self.style.SUCCESS(f"loaded {src}: {Page.objects.count()} pages"),
        )
