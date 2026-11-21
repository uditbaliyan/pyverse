# ruff: noqa: INP001
"""Sanity-check a frozen site: every local <script src>/<link href>/<img src> must
resolve to a file in the export, every local <a href> must lead to an exported
page, and the sitemap must match the pages.

    python utility/check_export.py _site [--min-pages N]

Also fails on placeholder content (example/scaffold URLs, lorem, "page desc"), on
duplicate element ids within a page, on pages without exactly one <main>, and,
with ``--min-pages``, when the export has fewer HTML pages than expected (the
guard against CI quietly exporting an empty database).
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
ID_ATTR = re.compile(r"""<[a-z][^>]*?\sid=["']([^"']+)["']""", re.I)
MAIN = re.compile(r"<main\b", re.I)
SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
TAG = re.compile(r"<[^>]+>")

# Text that must never ship: scaffold leftovers and stand-in copy.
PLACEHOLDERS = (
    "neetcode.io",
    "chat.z.ai",
    "lorem ipsum",
    "page desc",
    "welcome to your new wagtail site",
    "example.com",
    "todo:",
)


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


def placeholder_problems(html: str) -> list[str]:
    """Placeholder strings in the page's markup or visible text."""
    visible = TAG.sub(" ", SCRIPT_STYLE.sub(" ", html)).lower()
    haystack = html.lower()
    found = [needle for needle in PLACEHOLDERS if needle in haystack]
    # A card or link whose entire title is the bare word "page".
    if re.search(r">\s*page\s*<", html, re.I) and " page " in f" {visible} ":
        found.append("untitled 'page' card")
    return [f"placeholder content: {needle}" for needle in found]


def structure_problems(html: str, name: Path) -> list[str]:
    problems = []
    redirect_stub = re.search(r"http-equiv=[\"']refresh", html, re.I) is not None
    if name.name == "index.html" and not redirect_stub and name.parts[:-1] != ("404",):
        mains = len(MAIN.findall(html))
        if mains != 1:
            problems.append(f"expected exactly one <main>, found {mains}")
    seen: set[str] = set()
    dupes: set[str] = set()
    for ident in ID_ATTR.findall(SCRIPT_STYLE.sub(" ", html)):
        (dupes if ident in seen else seen).add(ident)
    problems.extend(f"duplicate id {ident!r}" for ident in sorted(dupes))
    return problems


def main(site: str, min_pages: int = 0, *, content_checks: bool = False) -> int:
    root = Path(site).resolve()
    if not root.is_dir():
        print(f"{site}: not a directory")  # noqa: T201
        return 2
    errors: list[str] = []
    pages = list(root.rglob("*.html"))
    if len(pages) < min_pages:
        errors.append(
            f"export has {len(pages)} HTML pages, expected at least {min_pages}"
            " (was the content loaded?)",
        )
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="ignore")
        name = page.relative_to(root)
        if content_checks:
            errors.extend(f"{name}: {p}" for p in placeholder_problems(html))
            errors.extend(f"{name}: {p}" for p in structure_problems(html, name))
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
    args = sys.argv[1:]
    floor = 0
    if "--min-pages" in args:
        at = args.index("--min-pages")
        floor = int(args[at + 1])
        del args[at : at + 2]
    sys.exit(main(args[0] if args else "_site", floor, content_checks=True))
