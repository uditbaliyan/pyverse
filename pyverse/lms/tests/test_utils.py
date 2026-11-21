"""Batched counts: one query per card grid, live pages only."""

from pyverse.lms.utils import course_counts_for
from pyverse.lms.utils import lesson_counts_for


def test_lesson_counts_cover_live_lessons_of_each_course(
    lms,
    add_topic,
    add_course,
    add_lesson,
    django_assert_num_queries,
):
    topic = add_topic("Python")
    full = add_course(topic, "Full")
    empty = add_course(topic, "Empty")
    other = add_course(topic, "Other")
    add_lesson(full, "One")
    add_lesson(full, "Two")
    add_lesson(full, "Draft", live=False)
    add_lesson(other, "Elsewhere")

    with django_assert_num_queries(1):
        counts = lesson_counts_for(lms, [full, empty])

    assert counts == {full.pk: 2, empty.pk: 0}


def test_course_counts_cover_live_courses_of_each_topic(
    lms,
    add_topic,
    add_course,
    django_assert_num_queries,
):
    busy = add_topic("Busy")
    quiet = add_topic("Quiet")
    add_course(busy, "One")
    add_course(busy, "Two")
    add_course(busy, "Draft", live=False)

    with django_assert_num_queries(1):
        counts = course_counts_for(lms, [busy, quiet])

    assert counts == {busy.pk: 2, quiet.pk: 0}


def test_counts_for_no_parents_cost_nothing(lms, django_assert_num_queries):
    with django_assert_num_queries(0):
        assert course_counts_for(lms, []) == {}
        assert lesson_counts_for(lms, []) == {}
