"""PyVerse has no paywall, so `is_free` defaults on.

The field was added defaulting to `False`, which made authored courses ship
`"isAccessibleForFree": false` in their JSON-LD and no "Free" badge. Flip the
default and backfill the rows that already exist.
"""

from django.db import migrations
from django.db import models


def mark_existing_courses_free(apps, schema_editor):
    CoursePage = apps.get_model("lms", "CoursePage")
    CoursePage.objects.update(is_free=True)


def noop(apps, schema_editor):
    """Reversing only undoes the default; the backfill is deliberately one-way."""


class Migration(migrations.Migration):

    dependencies = [
        ("lms", "0002_coursepage_og_image_lmsindexpage_og_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursepage",
            name="is_free",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(mark_existing_courses_free, noop),
    ]
