.PHONY: setup vendor tailwind test build-site check-site

setup:
	uv sync --locked
	uv run python utility/vendor_assets.py

vendor:
	uv run python utility/vendor_assets.py

# django-tailwind uses a standalone binary (no Node). The output is gitignored,
# and the export fails (by design) if any page links a stylesheet that is absent.
tailwind:
	uv run python manage.py tailwind build

test: vendor
	uv run pytest

# Static export.
#
# Default: a scratch DB (build.sqlite3) that is deleted and rebuilt from
# content/site.json on every run, so no state survives between builds. The
# Drills section is seeded on top, exactly as CI does.
#
# make build-site DB=db.sqlite3 exports *your own* database as-is: it is
# migrated but never wiped or seeded, because load_content replaces the page tree.
DB ?= build.sqlite3
ifeq ($(DB),build.sqlite3)
PREPARE_DB = rm -f $(DB) && uv run python manage.py migrate && uv run python manage.py load_content && uv run python manage.py seed_drills
else
PREPARE_DB = uv run python manage.py migrate
endif

build-site: vendor tailwind
	DJANGO_SETTINGS_MODULE=config.settings.distill \
	DATABASE_URL=sqlite:///$(CURDIR)/$(DB) \
	PYVERSE_CANONICAL_BASE_URL=$${PYVERSE_CANONICAL_BASE_URL:-https://pyverse.com} \
	sh -c '$(PREPARE_DB) && uv run python manage.py distill-local _site --collectstatic --force'
	uv run python -m pyverse.relativize _site
	python3 utility/check_export.py _site --min-pages 38
