# Hand-written: the slug column is added nullable, backfilled from titles,
# then tightened to unique + NOT NULL, so existing problems keep their rows.

import wagtail.fields
from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    CodingProblem = apps.get_model("coding", "CodingProblem")
    for problem in CodingProblem.objects.all():
        base = slugify(problem.title)[:200] or "problem"
        slug, suffix = base, 2
        while (
            CodingProblem.objects.filter(slug=slug).exclude(pk=problem.pk).exists()
        ):
            slug = f"{base}-{suffix}"[:200]
            suffix += 1
        problem.slug = slug
        problem.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("coding", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="codingproblem",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text=(
                    "URL segment for this challenge's canonical page "
                    "(/practice/<topic>/<slug>/). Left blank, it is generated "
                    "from the title."
                ),
                max_length=200,
                null=True,
                unique=False,
            ),
        ),
        migrations.AddField(
            model_name="codingproblem",
            name="difficulty",
            field=models.CharField(
                choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
                default="easy",
                help_text=(
                    "Easy / Medium / Hard — the only difficulty axis used "
                    "site-wide."
                ),
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="codingproblem",
            name="description",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text=(
                    "The problem statement shown above the editor on the "
                    "challenge page: what the function must do, constraints, "
                    "examples."
                ),
            ),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="codingproblem",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text=(
                    "URL segment for this challenge's canonical page "
                    "(/practice/<topic>/<slug>/). Left blank, it is generated "
                    "from the title."
                ),
                max_length=200,
                unique=True,
            ),
        ),
    ]
