# ruff: noqa: INP001
"""Sanity-check a frozen site: every local <script src>/<link href>/<img src>
must resolve to a file in the export, and the sitemap must match the pages.

    python utility/check_export.py _site
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse

REF = re.compile(r"""<(?:script|link|img)\b[^>]*?\b(?:src|href)=["']([^"']+)["']""", re.I)
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def resolve(root: Path, path: str) -> bool:
    target = root / unquote(path).lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def main(site: str) -> int:
    root = Path(site)
    if not root.is_dir():
        print(f"{site}: not a directory")  # noqa: T201
        return 2
    errors: list[str] = []
    for page in root.rglob("*.html"):
        for ref in REF.findall(page.read_text(encoding="utf-8", errors="ignore")):
            url = urlparse(ref)
            if url.scheme or url.netloc or ref.startswith(("#", "data:")):
                continue
            if not resolve(root, url.path):
                errors.append(f"{page.relative_to(root)}: dead reference {ref}")
    sitemap = root / "sitemap.xml"
    if not sitemap.is_file():
        errors.append("sitemap.xml missing")
    else:
        for loc in LOC.findall(sitemap.read_text(encoding="utf-8")):
            if not resolve(root, urlparse(loc).path):
                errors.append(f"sitemap entry not exported: {loc}")
    for err in sorted(set(errors)):
        print(err)  # noqa: T201
    print(f"{len(set(errors))} problem(s)")  # noqa: T201
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "_site"))
