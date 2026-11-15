"""Site chrome shared by every section.

The primary navigation lives in one place — Wagtail's Site Settings → nav items
— and is exposed to every template as `site_nav`, with the current section
already marked. Before this, three navs drifted apart: the homepage read Site
Settings, the light pages hardcoded HOME/ABOUT, and the Practice engine header
had its own list.
"""

from pyverse.home.models import SiteSettings

#: The designated colour of each section, as on the poster: 1 red, 2 orange,
#: 3 yellow, 4 green, 5 blue. It is keyed on the item's URL, not its position,
#: so reordering or adding nav items in the CMS never shuffles the colours.
#: Sheets live under /practice/, so they share Practice's orange.
_SECTION_TONES = (
    ("/learn", 1),
    ("/practice", 2),
    ("/labs", 3),
    ("/python", 4),
    ("/blog", 4),
    ("/about", 5),
)


def section_tone(url):
    """The 1-5 colour designated for the section `url` belongs to, else 0."""
    if not url or url.startswith("http"):
        return 0
    for prefix, tone in _SECTION_TONES:
        if url == prefix or url.startswith(prefix + "/"):
            return tone
    return 0


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
            "tone": section_tone(row.url),
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
