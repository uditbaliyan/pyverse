"""`{% seo_meta as seo %}` — the single source of `<head>` metadata.

Templates get a plain dict (title, description, canonical, og/twitter fields,
json_ld) so a base template can render some of it inline (the `<title>`) and
include the rest from one partial. All the decisions live in `pyverse/seo.py`.

Context it understands, in priority order: `problem` (a challenge page),
`quiz` (a quiz page), `page`/`self` (any Wagtail page). Views with none of
those pass `title` and `description` explicitly so they still get a canonical
URL and social card:

    {% seo_meta title="About" description="…" as seo %}
"""

from django import template

from pyverse import seo

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_meta(context, title=None, description=None):
    overrides = {}
    if title:
        overrides["title"] = title
    if description:
        overrides["description"] = description
    return seo.meta_for(
        request=context.get("request"),
        page=context.get("page") or context.get("self"),
        problem=context.get("problem"),
        quiz=context.get("quiz"),
        overrides=overrides or None,
    )
