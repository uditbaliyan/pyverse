"""Site chrome shared by every section.

The primary navigation lives in one place — Wagtail's Site Settings → nav items
— and is exposed to every template as `site_nav`, with the current section
already marked. Before this, three navs drifted apart: the homepage read Site
Settings, the light pages hardcoded HOME/ABOUT, and the Practice engine header
had its own list.
"""

from pyverse.home.models import SiteSettings


def _is_active(path, url):
    """True when `path` is inside the section a nav item points at."""
    if not url or url == "#" or url.startswith("http"):
        return False
    if url == "/":
        return path == "/"
    return path == url or path.startswith(url)


def site_nav(request):
    settings_obj = SiteSettings.for_request(request)
    rows = list(settings_obj.nav_items.all())

    # A path inside /practice/sheets/ matches both the Practice and the Sheets
    # item; only the most specific one may claim to be the current section.
    matches = [row.url for row in rows if _is_active(request.path, row.url)]
    current = max(matches, key=len) if matches else None

    items = [
        {
            "label": row.label,
            "url": row.url,
            "external": bool(row.link_external),
            "active": row.url == current,
        }
        for row in rows
    ]
    return {
        "site_nav": {
            "items": items,
            "cta_text": settings_obj.nav_cta_text,
            "cta_url": settings_obj.nav_cta_url,
            "brand": settings_obj.logo_text or "PYVERSE.",
            "logo": settings_obj.logo,
        },
    }
