# lms/wagtail_hooks.py
"""
from django_distill import distill_path
from wagtail.models import Page

from .models import LMSIndexPage, TrackPage, CoursePage, LessonPage


def get_lms_index_pages():
    for page in LMSIndexPage.objects.live().public():
        yield {"path": page.url_path.strip("/")}


def get_track_pages():
    for page in TrackPage.objects.live().public():
        yield {"path": page.url_path.strip("/")}


def get_course_pages():
    for page in CoursePage.objects.live().public():
        yield {"path": page.url_path.strip("/")}


def get_lesson_pages():
    for page in LessonPage.objects.live().public():
        yield {"path": page.url_path.strip("/")}

"""
