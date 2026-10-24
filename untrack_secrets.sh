#!/usr/bin/env sh
# Run once after applying the patch. Stops tracking secrets/DB WITHOUT deleting your local copies.
set -e
git rm -r --cached .envs db.sqlite3
echo "Untracked. Local files kept. Now: back up db.sqlite3, rotate DJANGO_SECRET_KEY and DJANGO_ADMIN_URL."
