"""Drills: the Parsons check, topic pagination and the static-export URL set."""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils.html import escape

from pyverse.drills import parsons
from pyverse.drills import quizitems
from pyverse.drills.models import DrillTopicPage
from pyverse.drills.models import ParsonsProblem
from pyverse.lms.models import DrillTopicBlock
from pyverse.quiz.models import Question
from pyverse.quiz.models import QuestionType
from pyverse.seo import live_drill_pages


def line(text, indent=0, distractor=False, feedback=""):
    return (
        "line",
        {
            "text": text,
            "indent": indent,
            "is_distractor": distractor,
            "feedback": feedback,
        },
    )


def values(lines):
    return [value for _, value in lines]


GOOD = [
    line("for n in range(3):"),
    line("print(n)", 1),
    line("print(n)", 1, True, "wrong"),
]


# ── verify() ────────────────────────────────────────────────────────────


def test_solution_source_drops_distractors_and_indents():
    assert parsons.solution_source(values(GOOD)) == "for n in range(3):\n    print(n)\n"


def test_verify_passes_and_compares_output():
    ok = parsons.verify(values(GOOD), "0\n1\n2")
    assert ok.ok, ok.errors
    bad = parsons.verify(values(GOOD), "9")
    assert any("output mismatch" in e for e in bad.errors)


def test_verify_rejects_invalid_python():
    report = parsons.verify(values([line("def f(:"), line("pass", 1)]))
    assert any("not valid Python" in e for e in report.errors)


def test_verify_needs_two_lines():
    assert not parsons.verify(values([line("x = 1")])).ok


def test_verify_scrubs_the_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    lines = [
        line("import os"),
        line("print(os.environ.get('OPENAI_API_KEY', 'absent'))"),
    ]
    assert parsons.verify(values(lines), "absent").ok


def test_verify_warns_on_unexplained_distractor():
    report = parsons.verify(
        values([line("a = 1"), line("print(a)"), line("a = 2", 0, True)]),
    )
    assert report.ok
    assert any("no feedback" in w for w in report.warnings)


# ── pages, pagination, export ───────────────────────────────────────────


@pytest.fixture
def seeded(db):
    call_command("seed_drills", verbosity=0)
    topic = DrillTopicPage.objects.get(slug="control-flow-and-loops")
    for i in range(12):  # 2 seeded + 12 = 14 -> two pages of 10
        ParsonsProblem.objects.create(
            slug=f"extra-{i}",
            title=f"Extra {i}",
            topic=topic,
            position=100 + i,
            description="d",
            lines=GOOD[:2],
        )
    return topic


def test_seed_is_idempotent(seeded):
    before = ParsonsProblem.objects.count()
    call_command("seed_drills", verbosity=0)
    assert ParsonsProblem.objects.count() == before


def test_topic_paginates_at_ten(seeded):
    assert seeded.num_pages() == 2
    assert seeded.paged_urls() == [seeded.url, f"{seeded.url}page/2/"]


def test_pages_render(seeded, client):
    first = client.get(seeded.url)
    second = client.get(f"{seeded.url}page/2/")
    assert first.status_code == second.status_code == 200
    assert len(first.context["items"]) == 10
    assert len(second.context["items"]) == 4
    body = first.content.decode()
    assert 'rel="next"' in body
    assert "parsons.js" in body
    assert body.count("pv-parsons__mount") == 10


@pytest.mark.parametrize("suffix", ["page/1/", "page/3/", "page/0/"])
def test_out_of_range_pages_404(seeded, client, suffix):
    assert client.get(f"{seeded.url}{suffix}").status_code == 404


def test_export_urls_include_every_later_page(seeded):
    assert f"{seeded.url}page/2/" in set(live_drill_pages())
    assert seeded.url not in set(live_drill_pages())  # page 1 comes from live_pages


def test_payload_keeps_authored_order_and_flags_distractors(seeded):
    payload = ParsonsProblem.objects.get(slug="extra-0").payload()
    assert [item["text"] for item in payload["lines"]] == [
        "for n in range(3):",
        "print(n)",
    ]
    assert all(not item["distractor"] for item in payload["lines"])


def test_check_parsons_command(seeded):
    call_command("check_parsons", verbosity=0)
    ParsonsProblem.objects.create(
        slug="broken",
        title="Broken",
        topic=seeded,
        description="d",
        lines=[line("def f(:"), line("pass", 1)],
    )
    with pytest.raises(CommandError):
        call_command("check_parsons", verbosity=0)


# ── LMS reference block ─────────────────────────────────────────────────


def test_drill_set_block_renders_a_card_with_slugs(seeded):
    block = DrillTopicBlock()
    html = block.render(block.to_python({"topic": seeded.pk, "prompt": "Warm up"}))
    assert escape(seeded.title) in html
    assert "Warm up" in html
    assert 'data-drill-slugs="' in html
    assert "grade-classifier" in html
    assert f'href="{seeded.url}"' in html


def test_drill_set_block_renders_nothing_for_a_missing_or_unpublished_topic(seeded):
    block = DrillTopicBlock()
    assert block.render(block.to_python({"topic": 999999, "prompt": ""})).strip() == ""
    seeded.unpublish()
    assert (
        block.render(block.to_python({"topic": seeded.pk, "prompt": ""})).strip() == ""
    )


def test_type_page_cards_carry_slugs_for_progress(seeded, client):
    type_page = seeded.get_parent()
    response = client.get(type_page.url)
    assert response.status_code == 200
    assert "data-drill-slugs=" in response.content.decode()
    assert "drill-progress.js" in response.content.decode()


# ── quiz type ───────────────────────────────────────────────────────────


@pytest.fixture
def quiz_topic(db):
    call_command("seed_drills", verbosity=0)
    return DrillTopicPage.objects.get(slug="python-basics")


def test_quiz_topic_lists_the_questions_of_its_quizzes(quiz_topic, client):
    assert quiz_topic.kind == "quiz"
    assert quiz_topic.item_count() == 5
    response = client.get(quiz_topic.url)
    body = response.content.decode()
    assert response.status_code == 200
    assert body.count("data-qitem") == 5
    assert "drill-quiz.js" in body
    assert "parsons.js" not in body
    assert body.count('data-correct="1"') == 5  # one right answer per question
    assert 'data-slugs="q' in body


def test_quiz_questions_paginate_like_puzzles(quiz_topic, client):
    quiz = quiz_topic.quizzes.get()
    for i in range(8):
        Question.objects.create(
            quiz=quiz,
            sort_order=100 + i,
            question_type=QuestionType.TRUE_FALSE,
            text=f"Extra {i}",
            correct_bool=True,
        )
    assert quiz_topic.num_pages() == 2
    assert f"{quiz_topic.url}page/2/" in set(live_drill_pages())
    assert len(client.get(f"{quiz_topic.url}page/2/").context["items"]) == 3


def test_quiz_options_cover_true_false_and_mcq(quiz_topic):
    first = quiz_topic.items()[0]
    assert [o["text"] for o in quizitems.options(first)] == [
        "int",
        "float",
        "str",
        "Fraction",
    ]
    tf = quiz_topic.items().filter(question_type=QuestionType.TRUE_FALSE).first()
    assert [o["text"] for o in quizitems.options(tf)] == ["True", "False"]
    assert sum(o["correct"] for o in quizitems.options(tf)) == 1


def test_check_drill_quizzes_passes_then_fails_on_a_broken_question(quiz_topic):
    call_command("check_drill_quizzes", verbosity=0)
    broken = quiz_topic.items().filter(question_type=QuestionType.MCQ).first()
    broken.choices.update(is_correct=False)
    with pytest.raises(CommandError):
        call_command("check_drill_quizzes", verbosity=0)


def test_type_pages_label_their_items(quiz_topic, client):
    html = client.get(quiz_topic.get_parent().url).content.decode()
    assert "5 questions" in html
    assert 'data-drill-store="pv:drillquiz:solved"' in html
