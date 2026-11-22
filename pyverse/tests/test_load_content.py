"""`load_content` must be safe to run again on the same database.

`make build-site` reuses a scratch database between builds. Raw-deleting pages
left their child-table rows behind, so the second run died in loaddata's
foreign-key check (`labs_labpage.page_ptr_id ... has an invalid foreign key`)
while CI, which always starts from an empty database, never noticed.
"""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.db import connection
from wagtail.models import Page

from pyverse.home.management.commands.load_content import delete_orphaned_page_rows
from pyverse.home.models import NavItem
from pyverse.lms.models import LessonPage

pytestmark = pytest.mark.django_db


def foreign_key_violations() -> list:
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_key_check")
        return cursor.fetchall()


def orphans(table: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {table} "  # noqa: S608
            "WHERE page_ptr_id NOT IN (SELECT id FROM wagtailcore_page)",
        )
        return cursor.fetchone()[0]


def test_loading_the_same_content_repeatedly_succeeds_and_stays_consistent():
    call_command("load_content", verbosity=0)
    first = Page.objects.count()

    for _ in range(3):  # the second run is the one that used to fail
        call_command("load_content", verbosity=0)

    assert Page.objects.count() == first
    assert foreign_key_violations() == []


def test_orphaned_child_rows_are_removed_without_touching_live_pages():
    call_command("load_content", verbosity=0)
    live = Page.objects.count()
    # A lesson page nothing links to, so deleting just its parent row is a
    # faithful copy of what the raw delete in load_content leaves behind.
    victim = LessonPage.objects.exclude(
        pk__in=NavItem.objects.values("link_page_id"),
    ).first()
    with connection.cursor() as cursor:  # FKs are deferred inside the test transaction
        cursor.execute("DELETE FROM wagtailcore_page WHERE id = %s", [victim.pk])
    assert orphans("lms_lessonpage") == 1

    removed = delete_orphaned_page_rows("default")

    assert removed == 1
    assert orphans("lms_lessonpage") == 0
    assert Page.objects.count() == live - 1
