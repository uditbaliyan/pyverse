# ruff: noqa: PLR2004
"""The starter problem bank: data shape, answer keys, and `seed_problems`."""

from __future__ import annotations

import copy
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from wagtail.models import Page

from pyverse.coding.management.commands.seed_problems import verify_spec
from pyverse.coding.models import CodingProblem
from pyverse.coding.problem_bank import PROBLEMS
from pyverse.coding.problem_bank import TOPICS
from pyverse.taxonomy import Difficulty
from pyverse.topics.models import PracticeHubPage
from pyverse.topics.models import PracticeTopicPage

BY_SLUG = {spec["slug"]: spec for spec in PROBLEMS}
COMPARATORS = {"exact", "sorted_list", "float_tolerance", "custom"}


# ── the data ────────────────────────────────────────────────────────────


def test_bank_has_twenty_to_thirty_problems_with_unique_slugs():
    assert 20 <= len(PROBLEMS) <= 30
    assert len(BY_SLUG) == len(PROBLEMS)


@pytest.mark.parametrize("spec", PROBLEMS, ids=lambda spec: spec["slug"])
def test_problem_is_well_formed(spec):
    assert spec["topic"] in TOPICS
    assert spec["difficulty"] in Difficulty.values
    assert spec["comparator"] in COMPARATORS
    if spec["comparator"] == "custom":
        assert "def compare(" in spec["custom_comparator_code"]

    solution = spec["solution_code"]
    assert solution.endswith("\n")
    assert solution.startswith(f"def {spec['function_name']}(")
    # The starter shows the same signature line the reference solution has.
    assert spec["starter_code"].splitlines()[0] == solution.splitlines()[0]

    visible = [case for case in spec["cases"] if not case[2]]
    hidden = [case for case in spec["cases"] if case[2]]
    assert len(visible) >= 2, "learners need at least two examples to self-check"
    assert hidden, "keep at least one hidden edge case"
    assert 1 <= spec["trace_case"] <= len(visible)

    assert len(spec["hints"]) == 3
    assert any(optimal for *_, optimal in spec["approaches"]), (
        "mark an optimal approach"
    )
    assert spec["examples"], "the description tab needs a worked example"
    assert spec["patterns"], "tag at least one pattern so the browse filters work"

    lines = len(solution.splitlines())
    for line, *_ in [*spec["trace_notes"], *spec["trace_predictions"]]:
        assert 1 <= line <= lines


@pytest.mark.parametrize("spec", PROBLEMS, ids=lambda spec: spec["slug"])
def test_reference_solution_passes_its_answer_key(spec):
    result = verify_spec(spec)
    assert result.ok, result.failure_report()


# ── the command ─────────────────────────────────────────────────────────


@pytest.fixture
def hub(db):
    root = Page.get_first_root_node()
    return root.add_child(instance=PracticeHubPage(title="Practice", slug="practice"))


def _seed(*args) -> str:
    out = StringIO()
    call_command("seed_problems", *args, stdout=out)
    return out.getvalue()


def test_dry_run_writes_nothing(hub):
    out = _seed("--dry-run")
    assert "dry run" in out
    assert CodingProblem.objects.count() == 0
    assert not PracticeTopicPage.objects.exists()


@pytest.mark.django_db
def test_seed_creates_topics_and_problems_and_is_idempotent(hub):
    _seed()
    assert CodingProblem.objects.count() == len(PROBLEMS)
    assert set(PracticeTopicPage.objects.values_list("slug", flat=True)) == {
        spec["topic"] for spec in PROBLEMS
    }

    sample = CodingProblem.objects.get(slug="two-sum-ii-sorted")
    assert sample.topic.slug == "two-pointers"
    assert sample.trace_case == BY_SLUG["two-sum-ii-sorted"]["trace_case"]
    assert len(sample.test_case_payload()) == len(BY_SLUG["two-sum-ii-sorted"]["cases"])
    assert [h.value["tier"] for h in sample.hint_tiers] == [
        "nudge",
        "approach",
        "solution",
    ]
    assert "Two Pointers" in sample.patterns.names()
    assert sample.trace_status.startswith("ready")

    # Second run: nothing duplicated, nothing overwritten.
    sample.title = "Edited in the CMS"
    sample.save()
    out = _seed()
    assert CodingProblem.objects.count() == len(PROBLEMS)
    assert PracticeTopicPage.objects.count() == len({s["topic"] for s in PROBLEMS})
    assert "0 created, 0 updated" in out
    sample.refresh_from_db()
    assert sample.title == "Edited in the CMS"


@pytest.mark.django_db
def test_update_overwrites_existing_problems(hub):
    _seed("--slug", "binary-search")
    CodingProblem.objects.filter(slug="binary-search").update(title="Changed")
    _seed("--slug", "binary-search", "--update")
    assert CodingProblem.objects.get(slug="binary-search").title == "Binary Search"


@pytest.mark.django_db
def test_seed_reuses_an_existing_topic_page(hub):
    existing = hub.add_child(instance=PracticeTopicPage(title="Stack", slug="stack"))
    _seed("--slug", "valid-parentheses")
    assert PracticeTopicPage.objects.filter(slug="stack").count() == 1
    assert CodingProblem.objects.get(slug="valid-parentheses").topic_id == existing.pk


def test_unknown_slug_is_an_error(hub):
    with pytest.raises(CommandError, match="unknown slug"):
        _seed("--slug", "no-such-problem")


@pytest.mark.django_db
def test_a_wrong_answer_key_blocks_the_whole_run(hub, monkeypatch):
    broken = copy.deepcopy(BY_SLUG["fizz-buzz"])
    broken["cases"][0] = ("5", '["1", "2", "Fizz", "4", "WRONG"]', False)
    monkeypatch.setattr(
        "pyverse.coding.management.commands.seed_problems.PROBLEMS",
        [broken, BY_SLUG["count-vowels"]],
    )
    with pytest.raises(CommandError, match="nothing was written"):
        _seed()
    assert CodingProblem.objects.count() == 0


def test_without_a_practice_hub_the_command_explains_itself(db):
    with pytest.raises(CommandError, match="no Practice hub"):
        _seed("--slug", "binary-search")
