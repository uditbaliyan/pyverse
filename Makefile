.PHONY: setup vendor test build-site check-site

setup:
	uv sync --locked
	uv run python utility/vendor_assets.py

vendor:
	uv run python utility/vendor_assets.py

test: vendor
	uv run pytest

# Static export. Uses a scratch DB so the committed db.sqlite3 is never migrated.
# To export your real content instead: make build-site DB=db.sqlite3 (after backup)
DB ?= build.sqlite3
build-site: vendor
	DJANGO_SETTINGS_MODULE=config.settings.distill \
	DATABASE_URL=sqlite:///$(CURDIR)/$(DB) \
	PYVERSE_CANONICAL_BASE_URL=$${PYVERSE_CANONICAL_BASE_URL:-https://pyverse.com} \
	sh -c 'uv run python manage.py migrate && uv run python manage.py distill-local _site --collectstatic --force'
	python3 utility/check_export.py _site
