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

# Static export. Uses a scratch DB so the committed db.sqlite3 is never migrated.
# To export your real content instead: make build-site DB=db.sqlite3 (after backup)
DB ?= build.sqlite3
build-site: vendor tailwind
	DJANGO_SETTINGS_MODULE=config.settings.distill \
	DATABASE_URL=sqlite:///$(CURDIR)/$(DB) \
	PYVERSE_CANONICAL_BASE_URL=$${PYVERSE_CANONICAL_BASE_URL:-https://pyverse.com} \

	sh -c 'uv run python manage.py migrate && uv run python manage.py load_content && uv run python manage.py distill-local _site --collectstatic --force'
	uv run python -m pyverse.relativize _site

	sh -c 'uv run python manage.py migrate && uv run python manage.py load_content && uv run python manage.py seed_drills && uv run python manage.py distill-local _site --collectstatic --force'
# Drills: separate section (hub > type > paginated topic) with Parsons puzzles, check_parsons gate, export wiring
	python3 utility/check_export.py _site --min-pages 38
