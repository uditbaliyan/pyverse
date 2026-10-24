"""Query helpers for the LMS page contexts."""

from wagtail.models import Page


def lesson_counts_for(container, courses):
    """`{course pk: live lesson count}` for every course in `courses`.

    Lesson pages hang off their course by Wagtail tree path only — there is no
    ForeignKey for `annotate` or `prefetch_related` to follow — so a grid of
    course cards would otherwise cost one COUNT per card. One descendant query
    over `container`, then each lesson is bucketed under its parent course's path
    (Wagtail paths are fixed `Page.steplen`-character segments).
    """
    # Imported here, not at module scope: `lms.models` imports this module, so a
    # top-level import would close the cycle with a half-built models module.
    from .models import LessonPage

    courses = list(courses)
    by_path = {course.path: course.pk for course in courses}
    counts = dict.fromkeys(by_path.values(), 0)
    if not by_path:
        return counts
    rows = (
        LessonPage.objects.descendant_of(container)
        .live()
        .values_list("path", flat=True)
    )
    for path in rows:
        pk = by_path.get(path[: -Page.steplen])
        if pk is not None:
            counts[pk] += 1
    return counts
