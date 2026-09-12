"""Settings for freezing the static site.

Usage (from the repo root):

    DJANGO_SETTINGS_MODULE=config.settings.distill \
    PYVERSE_CANONICAL_BASE_URL=https://pyverse.com \
    .venv/bin/python manage.py distill-local _site --collectstatic --force

Difference from `local`: the dev-only apps and middleware (debug toolbar,
browser reload) are removed, and DEBUG is off — their markup, plus Django's
debug error pages, must never be frozen into a public build.

`PYVERSE_CANONICAL_BASE_URL` decides the origin baked into canonical links,
OpenGraph URLs and sitemap entries. Without it the `django.contrib.sites`
domain is used, which is the right hostname but cannot know the scheme
(https) reliably — set it explicitly for a real build.
"""

from .local import *  # noqa: F403
from .local import BASE_DIR
from .local import INSTALLED_APPS
from .local import MIDDLEWARE

DEBUG = False

# Distill's renderer already forces this; being explicit keeps collectstatic
# and any stray request on the same footing.
ALLOWED_HOSTS = ["*"]

_DEBUG_ONLY_APPS = {"debug_toolbar", "django_browser_reload"}
_DEBUG_ONLY_MIDDLEWARE = (
    "debug_toolbar.",
    "django_browser_reload.",
)

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in _DEBUG_ONLY_APPS]
MIDDLEWARE = [
    mw for mw in MIDDLEWARE if not mw.startswith(_DEBUG_ONLY_MIDDLEWARE)
]

# django-distill
# ------------------------------------------------------------------------------
# Must be an installed app: Django discovers management commands per installed
# app, and without this `manage.py distill-local` is reported as unknown.
INSTALLED_APPS += ["django_distill"]
# Adds the export-only URL set (see pyverse/freeze.py) to the URLconf.
DISTILL_ENABLED = True
# Default output dir, so `manage.py distill-local` needs no argument.
DISTILL_DIR = str(BASE_DIR / "_site")
# Admin/static bundling for the Django and Wagtail admin is dead weight in a
# static export; only the site's own assets are copied.
DISTILL_SKIP_ADMIN_DIRS = True
