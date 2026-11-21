"""Query helpers for the LMS page contexts."""

from wagtail.models import Page


def _live_child_counts(model, container, parents):
    """`{parent pk: live count}` of `model` pages directly under each of `parents`.

    LMS pages hang off their parent by Wagtail tree path only — there is no
    ForeignKey for `annotate` or `prefetch_related` to follow — so a grid of cards
    would otherwise cost one COUNT per card. One descendant query over
    `container`, then each page is bucketed under its parent's path (Wagtail paths
    are fixed `Page.steplen`-character segments).
    """
    by_path = {parent.path: parent.pk for parent in parents}
    counts = dict.fromkeys(by_path.values(), 0)
    if not by_path:
        return counts
    rows = model.objects.descendant_of(container).live().values_list("path", flat=True)
    for path in rows:
        pk = by_path.get(path[: -Page.steplen])
        if pk is not None:
            counts[pk] += 1
    return counts


def lesson_counts_for(container, courses):
    """`{course pk: live lesson count}` for every course in `courses`."""
    # Imported here, not at module scope: `lms.models` imports this module, so a
    # top-level import would close the cycle with a half-built models module.
    from .models import LessonPage  # noqa: PLC0415

    return _live_child_counts(LessonPage, container, list(courses))


def course_counts_for(container, topics):
    """`{topic pk: live course count}` for every topic in `topics`."""
    from .models import CoursePage  # noqa: PLC0415

    return _live_child_counts(CoursePage, container, list(topics))
