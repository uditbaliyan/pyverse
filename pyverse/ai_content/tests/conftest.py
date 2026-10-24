"""Page trees the page-based generators need.

Both puput entries and lessons can only hang off an existing page, so the tests
build the same tree the site does — root → Home → folder → entry, and root →
Home → Learn → topic → course.
"""

from __future__ import annotations

import pytest
from wagtail.models import Page

from pyverse.home.models import HomePage
from pyverse.lms.models import CoursePage
from pyverse.lms.models import LMSIndexPage
from pyverse.lms.models import TopicPage
from pyverse.puput.models import BlogFolderPage
from pyverse.puput.models import BlogPage


@pytest.fixture
def home(db) -> HomePage:
    # Wagtail's initial data ships a root page and a welcome page under it, so
    # the test site hangs off the root with slugs of its own.
    page = HomePage(title="Test home", slug="test-home")
    Page.get_first_root_node().add_child(instance=page)
    return page


@pytest.fixture
def course(home: HomePage) -> CoursePage:
    index = LMSIndexPage(title="Learn", slug="learn")
    home.add_child(instance=index)
    topic = TopicPage(title="Python", slug="python")
    index.add_child(instance=topic)
    page = CoursePage(title="Fundamentals", slug="fundamentals")
    topic.add_child(instance=page)
    return page


@pytest.fixture
def blog(home: HomePage) -> BlogPage:
    folder = BlogFolderPage(title="Blog folder", slug="blog-folder")
    home.add_child(instance=folder)
    page = BlogPage(title="Notes", slug="notes")
    folder.add_child(instance=page)
    return page
