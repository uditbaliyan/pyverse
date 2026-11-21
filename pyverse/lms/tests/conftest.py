"""Builders for LMS tests: a real Wagtail tree in the test database.

Pages go in with `add_child` (what the admin does) under the default site's root
page, so `page.url` and `client.get(page.url)` behave exactly as they do when the
static export renders each page without a query string.
"""

import itertools
import json
from datetime import timedelta
from http import HTTPStatus

import pytest
from django.utils import timezone
from django.utils.text import slugify
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page

from pyverse.lms.models import CoursePage
from pyverse.lms.models import LessonPage
from pyverse.lms.models import LMSIndexPage
from pyverse.lms.models import TopicPage

_published = itertools.count()


def lesson_body(*blocks):
    """StreamField JSON for a lesson; no blocks gives one rich-text paragraph."""
    default = [{"type": "text", "value": "<p>Lesson body.</p>"}]
    return json.dumps(list(blocks) or default)


@pytest.fixture
def lms(db):
    """The Learn hub, published at /learn/."""
    home = Page.objects.get(depth=2)
    index = LMSIndexPage(title="Learn", slug="learn")
    home.add_child(instance=index)
    return index


@pytest.fixture
def add_topic(lms):
    def add(title, **fields):
        slug = fields.pop("slug", slugify(title))
        topic = TopicPage(title=title, slug=slug, **fields)
        lms.add_child(instance=topic)
        return topic

    return add


@pytest.fixture
def add_course():
    def add(topic, title, **fields):
        slug = fields.pop("slug", slugify(title))
        # Later calls publish later, so "newest first" is deterministic.
        stamp = timezone.now() + timedelta(seconds=next(_published))
        fields.setdefault("first_published_at", stamp)
        course = CoursePage(title=title, slug=slug, **fields)
        topic.add_child(instance=course)
        return course

    return add


@pytest.fixture
def add_lesson():
    def add(course, title, **fields):
        slug = fields.pop("slug", slugify(title))
        fields.setdefault("body", lesson_body())
        lesson = LessonPage(title=title, slug=slug, **fields)
        course.add_child(instance=lesson)
        return lesson

    return add


def html_of(client, page):
    """A page rendered the way the static export renders it: no query string."""
    response = client.get(page.url)
    assert response.status_code == HTTPStatus.OK, page.url
    return response.content.decode()


@pytest.fixture
def make_image(settings, tmp_path):
    """Create real images (renditions are generated on first render)."""
    settings.MEDIA_ROOT = tmp_path

    def make(title):
        file = get_test_image_file(filename=f"{title}.png")
        return Image.objects.create(title=title, file=file)

    return make
