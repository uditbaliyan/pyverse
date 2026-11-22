"""Replace the default Wagtail scaffold with the committed content fixture.

    uv run python manage.py migrate
    uv run python manage.py load_content            # content/site.json

Safe to re-run (a test loads it repeatedly): it clears the page tree below the
root, and the child-table rows under it, first. Never run it
against a database holding content you have not dumped (``dump_content``).
"""

from __future__ import annotations

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import connections
from django.db import transaction
from wagtail.models import Page
from wagtail.models import Site
from wagtail.models import get_page_models

DEFAULT_PATH = Path("content/site.json")


def delete_orphaned_page_rows(db: str) -> int:
    """Remove child-table rows whose `page_ptr` no longer has a page.

    Raw-deleting `wagtailcore_page` rows skips Django's cascade, so the
    multi-table-inheritance rows below them (`lms_lessonpage`, `labs_labpage`,
    `topics_sheetsindexpage`, ...) are left behind pointing at pages that no
    longer exist. The next `loaddata` then fails its foreign-key check, so the
    command was only ever safe on its *first* run against a database.

    The ORM cannot select these rows (it INNER JOINs the missing parent), hence
    SQL. Models are processed shallowest-first so a grandchild table is judged
    against an already-cleaned parent table.
    """
    connection = connections[db]
    quote = connection.ops.quote_name
    removed = 0
    with connection.cursor() as cursor:
        for model in sorted(get_page_models(), key=lambda m: len(m.__mro__)):
            for parent, link in model._meta.parents.items():  # noqa: SLF001
                if link is None:
                    continue
                cursor.execute(
                    f"DELETE FROM {quote(model._meta.db_table)} "  # noqa: S608, SLF001
                    f"WHERE {quote(link.column)} NOT IN "
                    f"(SELECT {quote(parent._meta.pk.column)} "  # noqa: SLF001
                    f"FROM {quote(parent._meta.db_table)})",  # noqa: SLF001
                )
                removed += max(cursor.rowcount, 0)
    return removed


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
        delete_orphaned_page_rows(db)
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
