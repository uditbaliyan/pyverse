from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_remove_homepage_body_remove_homepage_hero_cta_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PricingTier",
        ),
        migrations.DeleteModel(
            name="PricingPage",
        ),
    ]
