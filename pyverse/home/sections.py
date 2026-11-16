"""Live content for the home page's Learn / Practice / Labs / Blog sections.

The home page shows a taste of each part of the site: the featured course and
its lessons, a few problems, the labs, the latest note. All of it is read from
the same pages and records those sections already serve, so the home page can
never drift from them. Every part degrades to "nothing to show" on an empty
database, and the template hides what is empty.

The models are imported inside the function: `home` is imported by the other
apps (nav, settings), so importing them at module level would be circular.
"""

from __future__ import annotations

from django.utils.html import strip_tags
from django.utils.text import Truncator

LESSON_LIMIT = 4
PROBLEM_LIMIT = 4
LAB_LIMIT = 4
EXCERPT_WORDS = 32


def plural(count: int, one: str, many: str | None = None) -> str:
    """'1 course', '2 courses', '0 courses'."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


def _index_url(model) -> str:
    page = model.objects.live().public().first()
    return page.url if page else ""


def build_home_sections() -> dict:
    from pyverse.coding.models import CodingProblem  # noqa: PLC0415
    from pyverse.labs.models import LabPage  # noqa: PLC0415
    from pyverse.labs.models import LabsIndexPage  # noqa: PLC0415
    from pyverse.lms.models import CoursePage  # noqa: PLC0415
    from pyverse.lms.models import LMSIndexPage  # noqa: PLC0415
    from pyverse.puput.models import BlogPage  # noqa: PLC0415
    from pyverse.puput.models import EntryPage  # noqa: PLC0415
    from pyverse.topics.models import PracticeHubPage  # noqa: PLC0415

    # ── Learn ──────────────────────────────────────────────
    courses = CoursePage.objects.live().public()
    course = courses.order_by("-is_featured", "path").first()
    lessons = list(course.ordered_lessons()[:LESSON_LIMIT]) if course else []

    # ── Practice ───────────────────────────────────────────
    problems_qs = CodingProblem.objects.filter(
        topic__isnull=False,
        topic__live=True,
    ).select_related("topic")
    problem_total = problems_qs.count()
    problems = list(problems_qs.order_by("title")[:PROBLEM_LIMIT])

    # ── Labs ───────────────────────────────────────────────
    labs_qs = LabPage.objects.live().public()
    lab_total = labs_qs.count()
    labs = list(labs_qs.order_by("path")[:LAB_LIMIT])

    # ── Blog ───────────────────────────────────────────────
    entries_qs = EntryPage.objects.live().public()
    entry_total = entries_qs.count()
    entry = entries_qs.order_by("-date").first()
    excerpt = ""
    if entry is not None:
        excerpt = Truncator(strip_tags(str(entry.excerpt or ""))).words(EXCERPT_WORDS)

    course_total = courses.count()
    rail = [
        {
            "tone": 1,
            "label": "Learn",
            "href": "#learn",
            "note": plural(course_total, "course"),
        },
        {
            "tone": 2,
            "label": "Practice",
            "href": "#practice",
            "note": plural(problem_total, "problem"),
        },
        {
            "tone": 3,
            "label": "Labs",
            "href": "#labs",
            "note": plural(lab_total, "trace"),
        },
        {
            "tone": 4,
            "label": "Blog",
            "href": "#blog",
            "note": plural(entry_total, "note"),
        },
        {"tone": 5, "label": "Python", "href": "#python", "note": "the basics"},
    ]

    return {
        "rail": rail,
        "learn": {
            "course": course,
            "lessons": lessons,
            "url": _index_url(LMSIndexPage),
        },
        "practice": {
            "problems": problems,
            "total": problem_total,
            "url": _index_url(PracticeHubPage),
        },
        "labs": {"labs": labs, "url": _index_url(LabsIndexPage)},
        "blog": {
            "entry": entry,
            "excerpt": excerpt,
            "url": _index_url(BlogPage),
        },
    }
