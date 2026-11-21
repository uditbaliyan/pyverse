"""The Learn hub and topic pages, rendered the way the static export renders them.

The export writes one HTML file per page path and never sees a query string, so
nothing a learner needs may depend on one.
"""

import re
from http import HTTPStatus

from django.db import connection
from django.test.utils import CaptureQueriesContext

from pyverse.lms.models import CoursePage
from pyverse.lms.models import LessonPage
from pyverse.lms.models import LMSIndexPage
from pyverse.lms.models import TopicPage
from pyverse.seo import live_pages

from .conftest import html_of


def card_text(html, topic):
    """The visible text of one topic's card on the hub."""
    card = re.search(rf'<a href="{re.escape(topic.url)}".*?</a>', html, re.S)
    assert card, f"no card for {topic.url}"
    return " ".join(re.sub(r"<[^>]+>", " ", card.group(0)).split())


# ── Hub ──────────────────────────────────────────────────────────────────


def test_topic_cards_show_how_many_live_courses_each_topic_has(
    client,
    lms,
    add_topic,
    add_course,
):
    big = add_topic("Big Topic")
    small = add_topic("Small Topic")
    for n in range(3):
        add_course(big, f"Big {n}")
    add_course(small, "Only one")
    add_course(small, "Not yet", live=False)

    html = html_of(client, lms)

    assert card_text(html, big).endswith("3 courses")
    assert card_text(html, small).endswith("1 course")


def test_topics_follow_display_order_then_title(client, lms, add_topic):
    add_topic("Zulu", display_order=1)
    add_topic("Alpha", display_order=2)  # first alphabetically, later by order
    add_topic("Mike", display_order=1)

    html = html_of(client, lms)

    positions = [html.index(f">{title}</h3>") for title in ("Mike", "Zulu", "Alpha")]
    assert positions == sorted(positions)


def test_the_hub_costs_the_same_queries_however_many_topics_it_lists(
    client,
    lms,
    add_topic,
    add_course,
):
    def queries():
        client.get(lms.url)  # warm the per-process caches first
        with CaptureQueriesContext(connection) as captured:
            assert client.get(lms.url).status_code == HTTPStatus.OK
        return len(captured)

    add_course(add_topic("First"), "First course")
    baseline = queries()
    for n in range(4):
        add_course(add_topic(f"Extra {n}"), f"Extra course {n}")

    assert queries() == baseline


def test_lucide_icons_load_only_where_a_page_uses_them(
    client,
    lms,
    add_topic,
    add_course,
    add_lesson,
):
    topic = add_topic("Python")
    course = add_course(topic, "Basics")
    lesson = add_lesson(course, "Intro")

    assert "lucide.min.js" in html_of(client, lms)
    for page in (topic, course, lesson):
        assert "lucide.min.js" not in html_of(client, page)


# ── Topic page ───────────────────────────────────────────────────────────


def test_a_topic_page_lists_every_live_course_on_its_one_exported_page(
    client,
    add_topic,
    add_course,
):
    topic = add_topic("Python")
    for n in range(15):  # the old server-side pager stopped at 12
        add_course(topic, f"Course {n:02d}")
    add_course(topic, "Hidden draft", live=False)

    html = html_of(client, topic)

    for n in range(15):
        assert f"Course {n:02d}" in html
    assert "Hidden draft" not in html


def test_a_topic_page_has_no_query_string_links(client, add_topic, add_course):
    topic = add_topic("Python")
    add_course(topic, "One")
    add_course(topic, "Two")

    html = html_of(client, topic)

    assert 'href="?' not in html
    assert "Pagination" not in html


def test_filtering_happens_in_the_browser_so_the_server_ignores_the_query(
    client,
    add_topic,
    add_course,
):
    topic = add_topic("Python")
    add_course(topic, "Starter", difficulty="beginner")
    add_course(topic, "Expert", difficulty="advanced")

    filtered = client.get(topic.url, {"difficulty": "advanced", "page": "2"})

    assert filtered.content.decode() == html_of(client, topic)


def test_course_cards_carry_what_the_filter_needs(client, add_topic, add_course):
    topic = add_topic("Python")
    add_course(
        topic,
        "Starter",
        difficulty="beginner",
        course_type="micro",
        is_free=True,
    )
    add_course(
        topic,
        "Pro",
        difficulty="advanced",
        course_type="workshop",
        is_free=False,
    )

    html = html_of(client, topic)

    assert 'data-difficulty="beginner"' in html
    assert 'data-type="micro"' in html
    assert 'data-free="1"' in html
    assert 'data-difficulty="advanced"' in html
    assert 'data-type="workshop"' in html
    assert 'data-free="0"' in html


def test_filter_controls_stay_hidden_until_javascript_can_drive_them(
    client,
    add_topic,
    add_course,
):
    topic = add_topic("Python")
    add_course(topic, "One")
    add_course(topic, "Two")

    html = html_of(client, topic)

    bar = re.search(r"<section[^>]*data-course-filter[^>]*>", html)
    assert bar, "filter bar missing"
    assert re.search(r"\shidden[\s>]", bar.group(0)), "must be hidden without JS"
    assert "lms/js/course-filter.js" in html


def test_a_single_course_gets_no_filter_bar(client, add_topic, add_course):
    topic = add_topic("Python")
    add_course(topic, "Only")

    html = html_of(client, topic)

    assert "data-course-filter" not in html
    assert "course-filter.js" not in html


def test_an_empty_topic_says_so_instead_of_blaming_filters(client, add_topic):
    html = html_of(client, add_topic("Empty"))

    assert "No courses yet" in html
    assert "match your filters" not in html
    assert "data-course-filter" not in html


def test_courses_are_listed_newest_first(client, add_topic, add_course):
    topic = add_topic("Python")
    add_course(topic, "Older course")
    add_course(topic, "Newer course")

    html = html_of(client, topic)

    assert html.index("Newer course") < html.index("Older course")


def test_course_cards_pluralise_the_lesson_count(
    client,
    add_topic,
    add_course,
    add_lesson,
):
    topic = add_topic("Python")
    single = add_course(topic, "Single")
    double = add_course(topic, "Double")
    add_lesson(single, "Only")
    add_lesson(double, "First")
    add_lesson(double, "Second")

    html = html_of(client, topic)

    assert "1 lesson ·" in html
    assert "2 lessons ·" in html
    assert "1 lessons" not in html


# ── Static export ────────────────────────────────────────────────────────


def test_every_live_lms_page_renders_the_way_the_export_renders_it(
    client,
    lms,
    add_topic,
    add_course,
    add_lesson,
):
    topic = add_topic("Python")
    course = add_course(topic, "Basics")
    add_lesson(course, "One")
    add_lesson(course, "Two")
    add_lesson(course, "Unpublished", live=False)

    lms_types = (LMSIndexPage, TopicPage, CoursePage, LessonPage)
    pages = [p for p in live_pages() if isinstance(p.specific, lms_types)]

    hub_topic_course_and_two_live_lessons = 5
    assert len(pages) == hub_topic_course_and_two_live_lessons
    for page in pages:
        assert client.get(page.url).status_code == HTTPStatus.OK, page.url


# ── Arranging courses, accent colour, hero images, "Continue" ────────────


def test_editors_can_arrange_courses_with_display_order(client, add_topic, add_course):
    topic = add_topic("Python")
    add_course(topic, "Older default")
    add_course(topic, "Newer default")
    add_course(topic, "Pinned last", display_order=5)
    add_course(topic, "Pinned first", display_order=-1)

    html = html_of(client, topic)

    order = ["Pinned first", "Newer default", "Older default", "Pinned last"]
    positions = [html.index(f">{title}</h3>") for title in order]
    assert positions == sorted(positions)


def test_topic_cards_show_the_topics_accent_colour(client, lms, add_topic):
    add_topic("Teal", color="#2D5F5D")
    add_topic("Plain")

    html = html_of(client, lms)

    assert html.count("#2D5F5D") == 1


def test_a_stored_colour_that_is_not_hex_never_reaches_the_page(
    client,
    lms,
    add_topic,
):
    topic = add_topic("Odd")
    TopicPage.objects.filter(pk=topic.pk).update(color="red;background:url(x)")

    assert "background:url(x)" not in html_of(client, lms)


def test_the_course_page_marks_its_start_button_for_the_progress_script(
    client,
    add_topic,
    add_course,
    add_lesson,
):
    course = add_course(add_topic("Python"), "Basics")
    first = add_lesson(course, "First")
    add_lesson(course, "Second")

    html = html_of(client, course)

    cta = re.search(r"data-course-cta[^>]*>(.*?)</div>", html, re.S)
    assert cta, "start button wrapper missing"
    assert f'href="{first.url}"' in cta.group(1)


def queries_for(client, page):
    client.get(page.url)  # the first render creates any missing renditions
    with CaptureQueriesContext(connection) as captured:
        assert client.get(page.url).status_code == HTTPStatus.OK
    return len(captured)


def test_topic_page_cost_does_not_grow_with_hero_images(
    client,
    add_topic,
    add_course,
    make_image,
):
    topic = add_topic("Python")
    add_course(topic, "Course 0", hero_image=make_image("image-0"))
    baseline = queries_for(client, topic)
    for n in range(1, 5):
        add_course(topic, f"Course {n}", hero_image=make_image(f"image-{n}"))

    assert queries_for(client, topic) == baseline


def test_hub_cost_does_not_grow_with_featured_hero_images(
    client,
    lms,
    add_topic,
    add_course,
    make_image,
):
    topic = add_topic("Python")
    add_course(topic, "Course 0", is_featured=True, hero_image=make_image("image-0"))
    baseline = queries_for(client, lms)
    for n in range(1, 5):
        add_course(
            topic,
            f"Course {n}",
            is_featured=True,
            hero_image=make_image(f"image-{n}"),
        )

    assert queries_for(client, lms) == baseline
