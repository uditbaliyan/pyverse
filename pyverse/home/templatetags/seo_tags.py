"""`{% seo_meta as seo %}` — the single source of `<head>` metadata.

Templates get a plain dict (title, description, canonical, og/twitter fields,
json_ld) so a base template can render some of it inline (the `<title>`) and
include the rest from one partial. All the decisions live in `pyverse/seo.py`.

Views with no Wagtail page behind them (a plain TemplateView) pass `title` and
`description` explicitly so they still get a canonical URL and social card:
    {% seo_meta title="About" description="…" as seo %}
"""

from django import template

from pyverse import seo

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_meta(context, title=None, description=None):
    return seo.meta_for(
        request=context.get("request"),
        page=context.get("page") or context.get("self"),
        problem=context.get("problem"),
        title=title,
        description=description,
    )
