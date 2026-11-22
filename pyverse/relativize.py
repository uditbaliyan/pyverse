"""Make an exported site work wherever it is hosted.

Django renders root-absolute URLs (`/static/css/a.css`, `/learn/`). Those only
resolve when the site sits at the *root* of its host. Put the export under a
project path (`user.github.io/pyverse/`), a sub-directory, or open it from disk,
and every stylesheet, script, image and navigation link points at the wrong
place — which is exactly "no CSS, broken nav, and it gets worse the deeper the
page is".

This pass rewrites each root-absolute reference in every exported HTML file to a
path relative to *that file*:

    learn/python/index.html   /static/css/a.css  ->  ../../static/css/a.css
    index.html                /learn/            ->  learn/index.html

so the same `_site/` folder works at a domain root, under any sub-path, behind a
CDN, or from `file://`, with no base-URL setting to keep in sync.

Directory links (`/learn/`) become `learn/index.html` by default, because
`file://` and some static hosts do not serve a directory's index. Pass
`clean_urls=True` to keep the trailing-slash form where the host does.

Untouched on purpose: absolute URLs with a host (canonical, Open Graph; a
`https://…` URL is never root-absolute),
protocol-relative `//cdn…` URLs, `mailto:`/`tel:`, `#fragments`, already-relative
links, and every non-HTML file (sitemap.xml and robots.txt must stay absolute).

Run it:  python -m pyverse.relativize _site [--clean-urls]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

# Attributes that can hold a URL (a regex alternation). `data-*-href` and friends
# are how a template hands JavaScript a URL, so JS never hard-codes a root path.
_URL_ATTRS = ("href", "src", "action", "poster", r"data-[\w-]+")
# A data-* attribute is a URL if it is named like one (data-back-href), or if its
# value points into the site's own asset trees (data-worker="/static/js/x.js").
_DATA_URL_NAME = re.compile(r"data-[\w-]*(?:href|src|url)$", re.IGNORECASE)
_ASSET_PREFIXES = ("/static/", "/media/")
_ATTR_NAMES = "|".join(_URL_ATTRS)
_QUOTED_TAIL = r"(?P<q>[\"'])(?P<val>[^\"']*)(?P=q)"
_TAG = re.compile(
    r"<(?P<name>[a-zA-Z][\w:-]*)(?P<attrs>(?:[^>\"']|\"[^\"]*\"|'[^']*')*)>",
)
_ATTR = re.compile(
    rf"(?P<pre>\s(?P<attr>{_ATTR_NAMES})\s*=\s*){_QUOTED_TAIL}",
    re.IGNORECASE,
)
_SRCSET = re.compile(rf"(?P<pre>\ssrcset\s*=\s*){_QUOTED_TAIL}", re.IGNORECASE)
_REFRESH = re.compile(
    r"(?P<pre>content\s*=\s*[\"'][^\"']*?url\s*=\s*)(?P<val>/[^\"']*)",
    re.IGNORECASE,
)


def is_root_absolute(url: str) -> bool:
    """`/x` yes; `//host/x`, `https://…`, `x`, `#x`, `?x` no."""
    return url.startswith("/") and not url.startswith("//")


def relative_url(url: str, page: str, *, clean_urls: bool = False) -> str:
    """Rewrite one root-absolute `url` as seen from the exported file `page`.

    `page` is the file's path inside the site root, e.g. ``learn/python/index.html``.
    """
    parts = urlsplit(url)
    depth = page.count("/")
    prefix = "../" * depth
    target = parts.path.lstrip("/")
    if not clean_urls and (target == "" or target.endswith("/")):
        target += "index.html"
    path = prefix + target if target else (prefix or "./")
    return urlunsplit(("", "", path, parts.query, parts.fragment))


def _is_url_attr(name: str, value: str) -> bool:
    if not name.lower().startswith("data-") or _DATA_URL_NAME.match(name):
        return True
    return value.startswith(_ASSET_PREFIXES)


def _rewrite_srcset(value: str, page: str, *, clean_urls: bool) -> str:
    candidates = []
    for candidate in value.split(","):
        pieces = candidate.split()
        if pieces and is_root_absolute(pieces[0]):
            pieces[0] = relative_url(pieces[0], page, clean_urls=clean_urls)
        candidates.append(" ".join(pieces))
    return ", ".join(candidates)


def relativize_html(html: str, page: str, *, clean_urls: bool = False) -> str:
    """Return `html` with root-absolute URLs made relative to `page`."""

    def rewrite_tag(match: re.Match) -> str:
        tag, attrs = match.group("name").lower(), match.group("attrs")
        lowered = attrs.lower()

        def attr(m: re.Match) -> str:
            value = m.group("val")
            if not is_root_absolute(value) or not _is_url_attr(m.group("attr"), value):
                return m.group(0)
            new = relative_url(value, page, clean_urls=clean_urls)
            return f"{m.group('pre')}{m.group('q')}{new}{m.group('q')}"

        def srcset(m: re.Match) -> str:
            new = _rewrite_srcset(m.group("val"), page, clean_urls=clean_urls)
            return f"{m.group('pre')}{m.group('q')}{new}{m.group('q')}"

        def refresh(m: re.Match) -> str:
            return m.group("pre") + relative_url(
                m.group("val"),
                page,
                clean_urls=clean_urls,
            )

        attrs = _ATTR.sub(attr, attrs)
        attrs = _SRCSET.sub(srcset, attrs)
        if tag == "meta" and "refresh" in lowered:
            attrs = _REFRESH.sub(refresh, attrs)
        return f"<{match.group('name')}{attrs}>"

    return _TAG.sub(rewrite_tag, html)


def relativize_tree(root: Path, *, clean_urls: bool = False) -> int:
    """Rewrite every `.html` file under `root` in place; return how many changed."""
    changed = 0
    for file in sorted(root.rglob("*.html")):
        page = file.relative_to(root).as_posix()
        original = file.read_text(encoding="utf-8")
        updated = relativize_html(original, page, clean_urls=clean_urls)
        if updated != original:
            file.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("site", type=Path)
    parser.add_argument(
        "--clean-urls",
        action="store_true",
        help="keep `/learn/`-style links (the host must serve directory indexes)",
    )
    args = parser.parse_args(argv)
    if not args.site.is_dir():
        sys.stderr.write(f"not a directory: {args.site}\n")
        return 2
    count = relativize_tree(args.site, clean_urls=args.clean_urls)
    sys.stdout.write(f"relativized {count} page(s) in {args.site}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
