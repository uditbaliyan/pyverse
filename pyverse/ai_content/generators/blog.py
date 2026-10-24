"""Generate a puput ``EntryPage`` — the long-form prose type.

Puput's body is Markdown, so nothing here needs StreamField wiring: the model
returns one well-formed Markdown string against ``blog.md``.

Draft behaviour comes from puput's own Page-derived mechanics, not from
anything this generator does — an entry created through ``add_child`` is simply
unpublished, and every site surface that lists entries filters on ``live()``
(``BlogPage.get_entries``), so an unpublished entry is invisible until Udit
publishes it in /cms/.
"""

from __future__ import annotations

from typing import Any
from typing import ClassVar

from django.urls import reverse
from django.utils import timezone

from pyverse.ai_content.generators.base import Draft
from pyverse.ai_content.generators.base import Generator
from pyverse.ai_content.generators.base import optional_text
from pyverse.ai_content.generators.base import require_parent
from pyverse.ai_content.generators.base import required_text
from pyverse.puput.models import BlogPage
from pyverse.puput.models import EntryPage

_SCHEMA = """\
Reply with one JSON object with exactly these keys:

{
  "title": "post title in sentence case, no site name, no date",
  "markdown_body": "the whole post in Markdown",
  "excerpt": "one HTML paragraph, at most two sentences, shown in listings",
  "tags": ["2 to 5 short topical tags"]
}

- markdown_body is Markdown, not HTML: ## for sections, fenced code blocks
  with a language tag, links as [text](/url). It is rendered by puput.
- excerpt is HTML, unlike the body: a single <p> with no links inside it.
- Every code sample must be valid Python that runs as written.
"""

#: Blog tags are free-form (puput has no curated tag vocabulary), but a post
#: with fifty tags is noise, and duplicates do happen.
MAX_TAGS = 5


class BlogGenerator(Generator):
    slug: ClassVar[str] = "blog"
    menu_label: ClassVar[str] = "Blog post"
    label: ClassVar[str] = "EntryPage"
    style_file: ClassVar[str] = "blog.md"
    schema: ClassVar[str] = _SCHEMA
    review_notes: ClassVar[tuple[str, ...]] = (
        "Entries stay unpublished drafts until you publish them in /cms/.",
    )

    def parent_queryset(self) -> tuple[str, Any] | None:
        return "BlogPage", BlogPage.objects.all()

    def create(self, data: dict[str, Any], parent: Any = None) -> Draft:
        entry = EntryPage(
            title=required_text(data, "title"),
            markdown_body=required_text(data, "markdown_body"),
            excerpt=optional_text(data, "excerpt"),
            # puput's own default is a naive datetime, which warns under
            # USE_TZ; store an aware one.
            date=timezone.now(),
            # Page.live defaults to True, so add_child would publish this to
            # the site. A generated draft must not be live until Udit says so.
            live=False,
        )
        require_parent(parent, self.label).add_child(instance=entry)

        names = _tags(data)
        if names:
            entry.tags.add(*names)
            # ClusterTaggableManager keeps its through rows in the parent's
            # cluster and writes them on save (modelcluster's parented-child
            # behaviour), so this second save is what persists the tags.
            entry.save()

        return Draft(
            label=self.label,
            title=entry.title,
            review_url=reverse("wagtailadmin_pages:edit", args=[entry.pk]),
            notes=self.review_notes,
        )


def _tags(data: dict[str, Any]) -> list[str]:
    """The model's tags, trimmed to something a reader could browse by."""
    wanted = data.get("tags")
    if not isinstance(wanted, list):
        return []

    names: list[str] = []
    seen: set[str] = set()
    for name in wanted:
        tag = str(name).strip()
        if tag and tag.casefold() not in seen:
            seen.add(tag.casefold())
            names.append(tag)
    return names[:MAX_TAGS]
