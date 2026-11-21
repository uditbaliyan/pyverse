# ruff: noqa: INP001
"""Sanity-check a frozen site: every local <script src>/<link href>/<img src> must
resolve to a file in the export, every local <a href> must lead to an exported
page, and the sitemap must match the pages.

    python utility/check_export.py _site
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse

REF = re.compile(
    r"""<(?:script|link|img)\b[^>]*?\b(?:src|href)=["']([^"']+)["']""",
    re.I,
)
ANCHOR = re.compile(r"""<a\b[^>]*?\bhref=["']([^"']*)["']""", re.I)
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def exported(target: Path) -> bool:
    return target.is_file() or (target / "index.html").is_file()


def resolve(root: Path, path: str) -> bool:
    return exported(root / unquote(path).lstrip("/"))


def check_anchor(root: Path, page: Path, href: str) -> str | None:
    """Why this <a href> leads nowhere in a static export, or None if it is fine.

    A static host serves one file per path and ignores the query string, so a
    link to a page that was not exported (an unpublished practice problem, say) is
    a 404, and a query-only link ("?page=2") just reloads the page it is on.
    """
    url = urlparse(href)
    if not href or url.scheme or url.netloc or href.startswith("#"):
        return None  # leaves the site, or stays on this page
    if not url.path:
        return f"query-only link {href} (a static host ignores the query)"
    base = root if url.path.startswith("/") else page.parent
    target = Path(os.path.normpath(base / unquote(url.path).lstrip("/")))
    inside = target == root or root in target.parents
    return None if inside and exported(target) else f"dead link {href}"


def main(site: str) -> int:
    root = Path(site).resolve()
    if not root.is_dir():
        print(f"{site}: not a directory")  # noqa: T201
        return 2
    errors: list[str] = []
    for page in root.rglob("*.html"):
        html = page.read_text(encoding="utf-8", errors="ignore")
        name = page.relative_to(root)
        for ref in REF.findall(html):
            url = urlparse(ref)
            if url.scheme or url.netloc or ref.startswith(("#", "data:")):
                continue
            if not resolve(root, url.path):
                errors.append(f"{name}: dead reference {ref}")
        errors.extend(
            f"{name}: {problem}"
            for href in ANCHOR.findall(html)
            if (problem := check_anchor(root, page, href))
        )
    sitemap = root / "sitemap.xml"
    if not sitemap.is_file():
        errors.append("sitemap.xml missing")
    else:
        errors.extend(
            f"sitemap entry not exported: {loc}"
            for loc in LOC.findall(sitemap.read_text(encoding="utf-8"))
            if not resolve(root, urlparse(loc).path)
        )
    for err in sorted(set(errors)):
        print(err)  # noqa: T201
    print(f"{len(set(errors))} problem(s)")  # noqa: T201
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "_site"))
