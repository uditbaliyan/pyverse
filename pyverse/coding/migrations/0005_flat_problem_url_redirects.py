"""Keep every published nested challenge URL alive after the flat-URL move.

Challenge pages moved from `/practice/<topic>/<slug>/` to
`/practice/problem/<slug>/`. Each problem that existed at the time gets a
permanent redirect from its old nested path, so inbound links, sitemap
entries and search results keep working.

The redirects are also what the static export turns into stubs:
`manage.py distill-local --generate-redirects` writes one per row.
"""

from django.db import migrations

# Historical models carry fields only, so the path normaliser is imported from
# the real model. It is pure string handling, independent of schema state.
from wagtail.contrib.redirects.models import Redirect as LiveRedirect


def old_path_for(root_path, topic_path, slug):
    """Mirror Wagtail's Page.url for a challenge, without the page instance."""
    relative = topic_path[len(root_path) :] if topic_path.startswith(root_path) else topic_path
    return "/" + relative.strip("/") + "/" + slug + "/"


def create_redirects(apps, schema_editor):
    Page = apps.get_model("wagtailcore", "Page")
    Site = apps.get_model("wagtailcore", "Site")
    CodingProblem = apps.get_model("coding", "CodingProblem")
    Redirect = apps.get_model("wagtailredirects", "Redirect")

    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
    if site is None:
        return
    root = Page.objects.filter(pk=site.root_page_id).first()
    root_path = root.url_path if root else "/"

    for problem in CodingProblem.objects.exclude(topic__isnull=True).select_related(
        "topic"
    ):
        topic = problem.topic
        if topic is None:
            continue
        old_path = old_path_for(root_path or "/", topic.url_path, problem.slug)
        new_path = f"/practice/problem/{problem.slug}/"
        Redirect.objects.get_or_create(
            old_path=LiveRedirect.normalise_path(old_path),
            site=site,
            defaults={"redirect_link": new_path, "is_permanent": True},
        )


def remove_redirects(apps, schema_editor):
    Redirect = apps.get_model("wagtailredirects", "Redirect")
    Redirect.objects.filter(redirect_link__startswith="/practice/problem/").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("coding", "0004_codingproblem_comparator_codingproblem_constraints_and_more"),
        ("wagtailcore", "0001_initial"),
        ("wagtailredirects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_redirects, remove_redirects),
    ]
