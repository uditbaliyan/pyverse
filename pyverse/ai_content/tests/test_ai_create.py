"""What ``ai_create`` must refuse, and what it must leave behind.

The model call is the only thing stubbed: the prompt is built, the JSON parsed,
the solution executed, the StreamField converted and the row written for real.
"""

from __future__ import annotations

import io
import json
from copy import deepcopy

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from pyverse.ai_content import llm
from pyverse.coding.models import CodingProblem
from pyverse.lms.models import LessonPage
from pyverse.puput.models import EntryPage
from pyverse.quiz.models import Question
from pyverse.quiz.models import Quiz

TWO_SUM = {
    "title": "Two Sum",
    "difficulty": "easy",
    "description": (
        "<p>Return the indices of the two numbers adding to <code>target</code>.</p>"
    ),
    "function_name": "two_sum",
    "function_signature": "(nums: list[int], target: int) -> list[int]",
    "comparator": "sorted_list",
    "custom_comparator_code": "",
    "starter_code": "def two_sum(nums, target):\n    pass\n",
    "solution_code": (
        "def two_sum(nums, target):\n"
        "    seen = {}\n"
        "    for index, value in enumerate(nums):\n"
        "        if target - value in seen:\n"
        "            return [seen[target - value], index]\n"
        "        seen[value] = index\n"
        "    return []\n"
    ),
    "solution_explanation": "<p>Remember each index and look for a complement.</p>",
    "examples": [
        {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "note": "2 + 7"},
    ],
    "constraints": ["2 <= nums.length <= 10^4"],
    "hint_tiers": [
        {
            "tier": "solution",
            "text": "<p>Return as soon as the complement is known.</p>",
        },
        {"tier": "nudge", "text": "<p>Every pair costs O(n²).</p>"},
        {
            "tier": "approach",
            "text": "<p>Keep a <code>dict</code> from value to index.</p>",
        },
    ],
    "editorial_approaches": [
        {
            "name": "Hash map, one pass",
            "description": "<p>One pass, remembering what came before.</p>",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "is_optimal": True,
        },
    ],
    "test_cases": [
        {"input": "[2, 7, 11, 15], 9", "expected_output": "[0, 1]", "is_hidden": False},
        {"input": "[3, 2, 4], 6", "expected_output": "[1, 2]", "is_hidden": False},
        {"input": "[3, 3], 6", "expected_output": "[0, 1]", "is_hidden": True},
    ],
    "companies": ["Google", "Nonexistent Corp"],
    "patterns": ["Hash Map"],
    "techniques": [],
}

QUIZ = {
    "title": "Return values",
    "instructions": "Two quick checks on return values.",
    "difficulty": "easy",
    "pass_percentage": 70,
    "randomize_questions": False,
    "quiz_type": "mcq",
    "questions": [
        {
            "question_type": "mcq",
            "text": "What does a function hand back to its caller?",
            "code_snippet": "",
            "explanation": "Whatever `return` is given; `print` writes to the console.",
            "points": 1,
            "correct_bool": None,
            "choices": [
                {"text": "The value after `return`", "is_correct": True},
                {"text": "Whatever it printed", "is_correct": False},
                {"text": "Nothing", "is_correct": False},
                {"text": "The function name", "is_correct": False},
            ],
        },
        {
            "question_type": "true_false",
            "text": "`print(1 + 1)` and `return 1 + 1` do the same thing.",
            "code_snippet": "",
            "explanation": "False: only the returned value can be graded.",
            "points": 1,
            "correct_bool": False,
            "choices": [],
        },
    ],
}

LESSON = {
    "title": "Loops and accumulators",
    "estimated_minutes": 6,
    "blocks": [
        {
            "type": "text",
            "html": "<h2>Carry a value</h2><p>One loop, one variable.</p>",
        },
        {
            "type": "code_example",
            "language": "python",
            "filename": "total.py",
            "code": "def total(numbers):\n    running = 0\n    return running\n",
        },
        {
            "type": "callout",
            "style": "warning",
            "title": "Watch the indentation",
            "body": "<p>The update must sit inside the loop.</p>",
        },
    ],
}

BLOG = {
    "title": "Why your function returns None",
    "markdown_body": (
        "## What the grader sees\n\n```python\ndef double(n):\n    return n * 2\n```\n"
    ),
    "excerpt": "<p>Why a function that prints its answer still fails.</p>",
    "tags": ["Return values", "return values", "Graders"],
}


@pytest.fixture
def model_says(monkeypatch: pytest.MonkeyPatch):
    """Stand in for the provider: the rest of the pipeline stays real."""

    def _reply(payload: dict | str) -> None:
        text = payload if isinstance(payload, str) else json.dumps(payload)
        monkeypatch.setattr(llm, "complete", lambda _prompt: f"```json\n{text}\n```")

    return _reply


def run_command(stdin: str) -> str:
    out = io.StringIO()
    call_command("ai_create", stdin=io.StringIO(stdin), stdout=out)
    return out.getvalue()


@pytest.mark.django_db
def test_dsa_draft_is_verified_then_saved_without_a_topic(model_says):
    model_says(TWO_SUM)
    existing = CodingProblem.objects.create(
        title="Vocabulary holder",
        function_name="noop",
    )
    existing.patterns.add("Hash Map")
    existing.companies.add("Google")

    output = run_command("1\nTwo sum, easy, hash map\n")

    problem = CodingProblem.objects.exclude(pk=existing.pk).get()
    assert "✓ All 3 cases pass" in output
    assert '✓ Draft ready: CodingProblem "Two Sum"' in output
    assert f"/cms/snippets/coding/codingproblem/edit/{problem.pk}/" in output
    # Unassigned topic is what keeps it out of every learner-facing listing.
    assert problem.topic is None
    assert problem.slug == "two-sum"
    assert [hint.value["tier"] for hint in problem.hint_tiers] == [
        "nudge",
        "approach",
        "solution",
    ]
    assert [case["hidden"] for case in problem.test_case_payload()] == [
        False,
        False,
        True,
    ]
    assert problem.comparator == "sorted_list"
    assert sorted(problem.patterns.names()) == ["Hash Map"]
    # A tag no browse filter knows is dropped, and said so.
    assert sorted(problem.companies.names()) == ["Google"]
    assert "Nonexistent Corp" in output


@pytest.mark.django_db
def test_answer_key_that_does_not_hold_refuses_the_draft(model_says):
    broken = deepcopy(TWO_SUM)
    broken["test_cases"][1]["expected_output"] = "[0, 1]"
    model_says(broken)

    with pytest.raises(CommandError) as refusal:
        run_command("1\nTwo sum\n")

    message = str(refusal.value)
    assert "does not reproduce the generated test cases (2/3 pass)" in message
    assert "[3, 2, 4], 6" in message
    assert CodingProblem.objects.count() == 0


@pytest.mark.django_db
def test_reply_that_is_not_json_refuses_the_draft(model_says):
    model_says("I would rather not.")

    with pytest.raises(CommandError) as refusal:
        run_command("1\nTwo sum\n")

    assert "no JSON object" in str(refusal.value)
    assert CodingProblem.objects.count() == 0


@pytest.mark.django_db
def test_custom_comparator_without_its_code_refuses_the_draft(model_says):
    payload = deepcopy(TWO_SUM)
    payload["comparator"] = "custom"
    payload["custom_comparator_code"] = ""
    model_says(payload)

    with pytest.raises(CommandError) as refusal:
        run_command("1\nTwo sum\n")

    assert "no compare" in str(refusal.value)
    assert CodingProblem.objects.count() == 0


@pytest.mark.django_db
def test_problem_whose_cases_are_all_hidden_refuses_the_draft(model_says):
    payload = deepcopy(TWO_SUM)
    for case in payload["test_cases"]:
        case["is_hidden"] = True
    model_says(payload)

    with pytest.raises(CommandError) as refusal:
        run_command("1\nTwo sum\n")

    assert "every generated test case is hidden" in str(refusal.value)
    assert CodingProblem.objects.count() == 0


@pytest.mark.django_db
def test_blog_post_is_created_unpublished_with_its_tags(model_says, blog):
    model_says(BLOG)

    output = run_command("2\nA post about return values\n")

    entry = EntryPage.objects.get()
    assert entry.live is False
    assert entry.get_parent().id == blog.id
    assert "✓ Draft ready: EntryPage" in output
    # ClusterTaggableManager defers to the parent's save: the tags have to be
    # in the database, not just on the in-memory instance.
    assert sorted(EntryPage.objects.get(pk=entry.pk).tags.names()) == [
        "Graders",
        "Return values",
    ]
    # puput stores what templates render separately from the Markdown source.
    assert "<h2>What the grader sees</h2>" in entry.body


@pytest.mark.django_db
def test_lesson_is_created_unpublished_with_its_blocks_in_order(model_says, course):
    model_says(LESSON)

    run_command("3\nLoops and accumulators\n")

    lesson = LessonPage.objects.get()
    assert lesson.live is False
    assert lesson.get_parent().id == course.id
    assert lesson.estimated_minutes == LESSON["estimated_minutes"]
    assert [block.block_type for block in lesson.body] == [
        "text",
        "code_example",
        "callout",
    ]


@pytest.mark.django_db
def test_lesson_block_that_needs_an_asset_refuses_the_draft(model_says, course):
    payload = deepcopy(LESSON)
    payload["blocks"].append({"type": "image", "caption": "a diagram"})
    model_says(payload)

    with pytest.raises(CommandError) as refusal:
        run_command("3\nLoops\n")

    assert "unsupported type 'image'" in str(refusal.value)
    assert LessonPage.objects.count() == 0


@pytest.mark.django_db
def test_quiz_is_saved_with_its_questions_choices_and_no_topic(model_says, course):
    model_says(QUIZ)

    output = run_command("4\nReturn values\n")

    quiz = Quiz.objects.get()
    assert quiz.topic is None
    assert quiz.slug == "return-values"
    assert "✓ Draft ready: Quiz" in output
    questions = list(quiz.questions.order_by("sort_order"))
    assert [question.question_type for question in questions] == ["mcq", "true_false"]
    assert [question.sort_order for question in questions] == [0, 1]
    assert questions[1].correct_bool is False
    choices = list(questions[0].choices.order_by("sort_order"))
    assert choices[0].text == "The value after `return`"
    assert [choice.is_correct for choice in choices] == [True, False, False, False]


@pytest.mark.django_db
def test_quiz_key_with_two_correct_choices_refuses_the_draft(model_says):
    payload = deepcopy(QUIZ)
    payload["questions"][0]["choices"][1]["is_correct"] = True
    model_says(payload)

    with pytest.raises(CommandError) as refusal:
        run_command("4\nReturn values\n")

    assert "marks 2 choices correct" in str(refusal.value)
    assert Quiz.objects.count() == 0
    assert Question.objects.count() == 0


@pytest.mark.django_db
def test_true_false_question_without_an_answer_refuses_the_draft(model_says):
    payload = deepcopy(QUIZ)
    payload["questions"][1]["correct_bool"] = None
    model_says(payload)

    with pytest.raises(CommandError) as refusal:
        run_command("4\nReturn values\n")

    assert "correct_bool is None" in str(refusal.value)
    assert Quiz.objects.count() == 0
