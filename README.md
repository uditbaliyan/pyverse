# PyVerse

Behold My Awesome Project!

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy pyverse

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

## Deployment

The production site is a **static export** — Wagtail and the database exist only
while authoring. Nothing in `pyverse/` runs in production.

### Static export

```bash
DJANGO_SETTINGS_MODULE=config.settings.distill \
PYVERSE_CANONICAL_BASE_URL=https://pyverse.com \
python manage.py distill-local _site --collectstatic --force
```

- `config/settings/distill.py` turns off `DEBUG` and drops the dev-only apps
  (debug toolbar, browser reload) so their markup can never be frozen into a
  public build.
- `PYVERSE_CANONICAL_BASE_URL` fixes the origin used by canonical links,
  OpenGraph URLs and `sitemap.xml`. Without it the `django.contrib.sites`
  domain is used, which cannot know the scheme.
- `pyverse/freeze.py` decides *what* gets written, from the same querysets
  `sitemap.xml` uses: every live page under the site root, every challenge page,
  plus `sitemap.xml`, `robots.txt` and a top-level `404.html` for hosts that
  serve one (Netlify, GitHub Pages, Cloudflare Pages).
- Output is `_site/` (gitignored): HTML tree + `static/` + `media/`. Serve it
  with any static host; there is no server-side component.

`_site/404.html` only works on hosts that use a root `404.html`; map it
explicitly if the host wants a different filename.

### Deploying
