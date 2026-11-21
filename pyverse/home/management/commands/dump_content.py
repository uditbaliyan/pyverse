"""Write the site's authored content to a reviewable JSON fixture.

    uv run python manage.py dump_content            # -> content/site.json

Only content is dumped: no users, sessions, password hashes, revisions, logs or
image renditions. The fixture is what CI loads (``load_content``) so the static
export is built from the real site, not an empty database.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand

EXCLUDE = (
    "contenttypes",
    "auth",
    "sessions",
    "admin",
    "sites",
    "users",
    "account",
    "socialaccount",
    "mfa",
    "wagtail_ai",
    "wagtailsearch",
    "wagtailusers",
    "wagtailadmin",
    "wagtailimages.rendition",
    "wagtailcore.pagelogentry",
    "wagtailcore.modellogentry",
    "wagtailcore.referenceindex",
    "wagtailcore.revision",
    "wagtailcore.workflow",
    "wagtailcore.workflowpage",
    "wagtailcore.workflowtask",
    "wagtailcore.workflowstate",
    "wagtailcore.task",
    "wagtailcore.taskstate",
    "wagtailcore.groupapprovaltask",
    "wagtailcore.comment",
    "wagtailcore.commentreply",
    "wagtailcore.pagesubscription",
    "wagtailcore.grouppagepermission",
    "wagtailcore.groupcollectionpermission",
    "wagtailcore.groupsitepermission",
    "wagtailcore.uploadedfile",
)

DEFAULT_PATH = Path("content/site.json")

# Per-model fields that point at users or excluded tables (revisions); nulled so
# the fixture loads into a database with no accounts and carries no user data.
NULL_FIELDS = (
    "owner",
    "locked_by",
    "latest_revision",
    "live_revision",
    "uploaded_by_user",
    "first_published_at_by",
)


class Command(BaseCommand):
    help = "Dump authored content (pages, quizzes, problems, nav) to content/site.json."

    def add_arguments(self, parser):
        parser.add_argument("--output", default=str(DEFAULT_PATH))

    def handle(self, *args, **options):
        out = Path(options["output"])
        out.parent.mkdir(parents=True, exist_ok=True)
        buf = io.StringIO()
        call_command(
            "dumpdata",
            *[f"--exclude={label}" for label in EXCLUDE],
            natural_foreign=True,
            natural_primary=True,
            stdout=buf,
        )
        rows = json.loads(buf.getvalue())
        for row in rows:
            for field in NULL_FIELDS:
                if field in row["fields"]:
                    row["fields"][field] = None
        out.write_text(
            json.dumps(rows, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self.stdout.write(self.style.SUCCESS(f"wrote {out}"))
