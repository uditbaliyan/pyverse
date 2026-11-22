"""`PracticeBlock`: what authors may embed in a lesson and what learners see."""

import re
from html import unescape

import pytest
from wagtail.blocks import StructBlockValidationError
from wagtail.models import Page

from pyverse.coding.models import CodingProblem
from pyverse.lms.models import CodeExampleBlock
from pyverse.lms.models import PracticeBlock
from pyverse.quiz.models import Quiz
from pyverse.topics.models import PracticeTopicPage

pytestmark = pytest.mark.django_db


@pytest.fixture
def practice_topic():
    topic = PracticeTopicPage(title="Arrays", slug="arrays")
    Page.objects.get(depth=2).add_child(instance=topic)
    return topic


def problem_in(topic=None, slug="sum"):
    return CodingProblem.objects.create(
        title=slug.title(),
        slug=slug,
        function_name="f",
        topic=topic,
    )


def quiz_in(topic=None, slug="basics"):
    return Quiz.objects.create(title=slug.title(), slug=slug, topic=topic)


def checkpoint(problem=None, quiz=None, *, required=False):
    block = PracticeBlock()
    raw = {
        "problem": problem.pk if problem else None,
        "quiz": quiz.pk if quiz else None,
        "required_to_advance": required,
    }
    return block, block.to_python(raw)


def rejection(block, value):
    with pytest.raises(StructBlockValidationError) as error:
        block.clean(value)
    return error.value.block_errors


# ── Authoring rules ──────────────────────────────────────────────────────


def test_a_problem_in_a_topic_is_accepted(practice_topic):
    problem = problem_in(practice_topic)
    block, value = checkpoint(problem=problem)

    assert block.clean(value)["problem"] == problem


def test_a_quiz_in_a_topic_is_accepted(practice_topic):
    quiz = quiz_in(practice_topic)
    block, value = checkpoint(quiz=quiz)

    assert block.clean(value)["quiz"] == quiz


def test_a_problem_without_a_topic_is_rejected_because_it_is_never_exported():
    block, value = checkpoint(problem=problem_in(topic=None))

    errors = rejection(block, value)

    assert "topic" in " ".join(errors["problem"].messages).lower()


def test_a_quiz_without_a_topic_is_rejected_because_it_is_never_exported():
    block, value = checkpoint(quiz=quiz_in(topic=None))

    errors = rejection(block, value)

    assert "topic" in " ".join(errors["quiz"].messages).lower()


def test_a_target_in_a_topic_that_is_still_a_draft_is_accepted():
    """Authors may build the lesson before publishing the topic."""
    draft_topic = PracticeTopicPage(title="Later", slug="later", live=False)
    Page.objects.get(depth=2).add_child(instance=draft_topic)
    block, value = checkpoint(problem=problem_in(draft_topic))

    assert block.clean(value)


def test_exactly_one_target_is_required(practice_topic):
    problem = problem_in(practice_topic)
    quiz = quiz_in(practice_topic)

    for given in ({}, {"problem": problem, "quiz": quiz}):
        block, value = checkpoint(**given)
        assert "problem" in rejection(block, value)


# ── What learners see ────────────────────────────────────────────────────


def test_a_checkpoint_links_to_its_problem_and_exposes_its_progress_hooks(
    practice_topic,
):
    problem = problem_in(practice_topic)
    block, value = checkpoint(problem=problem, required=True)

    html = block.render(value)

    assert 'data-checkpoint-kind="problem"' in html
    assert f'data-checkpoint-slug="{problem.slug}"' in html
    assert "data-checkpoint-required" in html
    assert f'href="{problem.get_absolute_url()}"' in html
    assert "Required checkpoint" in html


def test_a_checkpoint_links_to_its_quiz(practice_topic):
    quiz = quiz_in(practice_topic)
    block, value = checkpoint(quiz=quiz)

    html = block.render(value)

    assert 'data-checkpoint-kind="quiz"' in html
    assert f'href="{quiz.get_absolute_url()}"' in html
    assert "data-checkpoint-required" not in html


def test_a_checkpoint_whose_target_was_deleted_renders_nothing(practice_topic):
    problem = problem_in(practice_topic)
    pk = problem.pk
    problem.delete()
    block = PracticeBlock()
    value = block.to_python({"problem": pk, "quiz": None, "required_to_advance": True})

    assert block.render(value).strip() == ""


# ── Code examples ────────────────────────────────────────────────────────

SAMPLE = "if a < b:\n    print(1)\n\nprint(2)"


def render_code(code, *, numbers):
    block = CodeExampleBlock()
    raw = {
        "language": "python",
        "code": code,
        "filename": "",
        "show_line_numbers": numbers,
    }
    return block.render(block.to_python(raw))


def copied_text(html):
    """What the Copy button copies: the text of the <code> element."""
    match = re.search(r"<code[^>]*>(.*?)</code>", html, re.S)
    assert match, "no <code> element rendered"
    return unescape(re.sub(r"<[^>]+>", "", match.group(1)))


def test_line_numbers_wrap_every_line_and_copy_still_gives_the_exact_code():
    html = render_code(SAMPLE, numbers=True)

    assert html.count('<span class="code-line">') == len(SAMPLE.split("\n"))
    assert "code-lines" in html
    assert "&lt;" in html
    assert "a < b" not in html  # still escaped
    assert copied_text(html) == SAMPLE


def test_code_without_line_numbers_is_left_exactly_as_written():
    html = render_code(SAMPLE, numbers=False)

    assert "code-line" not in html
    assert copied_text(html) == SAMPLE


def test_python_code_in_a_lesson_is_syntax_highlighted_and_still_copies_exactly():
    html = render_code(SAMPLE, numbers=True)

    assert 'class="tok-k"' in html  # `if`
    assert 'class="tok-nb"' in html  # `print`
    assert copied_text(html) == SAMPLE


def test_highlighting_without_line_numbers_also_copies_exactly():
    html = render_code(SAMPLE, numbers=False)

    assert 'class="tok-k"' in html
    assert copied_text(html) == SAMPLE
