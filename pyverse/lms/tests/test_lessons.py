"""Course and lesson pages: progress identity, preview navigation, lean pages."""

import re

import pytest

from pyverse.lms.models import CoursePage
from pyverse.lms.models import LessonPage

from .conftest import html_of
from .conftest import lesson_body

KEY = re.compile(r'data-lesson-key="([^"]+)"')


@pytest.fixture
def twin_lessons(add_topic, add_course, add_lesson):
    """Two lessons with the same slug in two different courses and topics."""
    python = add_course(add_topic("Python"), "Basics")
    sql = add_course(add_topic("SQL"), "Basics")
    return add_lesson(python, "Introduction"), add_lesson(sql, "Introduction")


# ── Navigation properties ────────────────────────────────────────────────


def test_a_lesson_knows_its_course_and_topic(add_topic, add_course, add_lesson):
    topic = add_topic("Python")
    course = add_course(topic, "Basics")
    lesson = add_lesson(course, "One")

    fresh = LessonPage.objects.get(pk=lesson.pk)

    assert fresh.course == course
    assert fresh.topic == topic
    assert CoursePage.objects.get(pk=course.pk).topic == topic


def test_a_lesson_page_resolves_its_course_and_topic_once_each(
    rf,
    add_topic,
    add_course,
    add_lesson,
    django_assert_max_num_queries,
):
    course = add_course(add_topic("Python"), "Basics")
    add_lesson(course, "One")
    lesson = LessonPage.objects.get(pk=add_lesson(course, "Two").pk)
    request = rf.get("/")

    with django_assert_max_num_queries(3):  # siblings, course, topic
        lesson.get_context(request)


# ── Progress identity ────────────────────────────────────────────────────


def test_progress_keys_stay_unique_when_lesson_slugs_repeat(twin_lessons):
    python, sql = twin_lessons

    assert python.slug == sql.slug
    assert python.progress_key == "python/basics/introduction"
    assert sql.progress_key == "sql/basics/introduction"


def test_course_page_rows_carry_each_lessons_progress_key(client, twin_lessons):
    python, _ = twin_lessons

    html = html_of(client, python.get_parent())

    assert 'data-lesson-key="python/basics/introduction"' in html
    assert "data-lesson-slug" not in html


def test_a_lesson_page_uses_the_same_keys_as_its_course_page(
    client,
    add_topic,
    add_course,
    add_lesson,
):
    course = add_course(add_topic("Python"), "Basics")
    first = add_lesson(course, "First")
    add_lesson(course, "Second")

    lesson_html = html_of(client, first)

    assert set(KEY.findall(lesson_html)) == set(KEY.findall(html_of(client, course)))
    button = re.search(r'<button[^>]*id="lesson-complete"[^>]*>', lesson_html)
    assert button
    assert f'data-lesson-key="{first.progress_key}"' in button.group(0)


# ── Previewing drafts ────────────────────────────────────────────────────


def test_a_draft_lesson_previews_in_its_place_among_its_siblings(
    rf,
    add_topic,
    add_course,
    add_lesson,
):
    course = add_course(add_topic("Python"), "Basics")
    first = add_lesson(course, "First")
    draft = add_lesson(course, "Draft", live=False)
    last = add_lesson(course, "Last")

    context = draft.get_context(rf.get("/"))

    assert (context["lesson_index"], context["total_lessons"]) == (2, 3)
    assert context["prev_lesson"] == first
    assert context["next_lesson"] == last
    assert [lesson.pk for lesson in context["lesson_list"]] == [
        first.pk,
        draft.pk,
        last.pk,
    ]


def test_live_lessons_are_numbered_among_live_siblings_only(
    rf,
    add_topic,
    add_course,
    add_lesson,
):
    course = add_course(add_topic("Python"), "Basics")
    add_lesson(course, "First")
    add_lesson(course, "Draft", live=False)
    last = add_lesson(course, "Last")

    context = last.get_context(rf.get("/"))

    assert (context["lesson_index"], context["total_lessons"]) == (2, 2)
    assert context["next_lesson"] is None


# ── Lean pages ───────────────────────────────────────────────────────────


def test_mermaid_loads_only_for_lessons_that_have_a_diagram(
    client,
    add_topic,
    add_course,
    add_lesson,
):
    course = add_course(add_topic("Python"), "Basics")
    plain = add_lesson(course, "Plain")
    diagram = add_lesson(
        course,
        "Diagram",
        body=lesson_body({"type": "mermaid", "value": "graph TD\n  A-->B"}),
    )

    assert "mermaid.min.js" not in html_of(client, plain)
    assert "mermaid.min.js" in html_of(client, diagram)
