"""What the pre-save check has to get right.

These mirror ``pyverse/templates/includes/pyscript_runtime.html``: the same
argument-list-as-source inputs, the same comparator behaviours. A disagreement
between the two would mean a problem that passes here and fails in a learner's
browser, which is the one failure mode this module exists to prevent.
"""

from __future__ import annotations

from pyverse.ai_content.verify import verify

TWO_SUM = """
def solve(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        if target - value in seen:
            return [seen[target - value], index]
        seen[value] = index
    return []
"""


def run(solution: str, cases, comparator: str = "exact", custom: str = ""):
    return verify(
        function_name="solve",
        solution_code=solution,
        comparator=comparator,
        custom_comparator_code=custom,
        cases=cases,
    )


def test_passing_solution_grades_every_case():
    result = run(
        TWO_SUM,
        [
            {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"},
            {"input": "[3, 2, 4], 6", "expected": "[1, 2]"},
        ],
        comparator="sorted_list",
    )

    assert result.ok
    assert (result.passed_count, result.total) == (2, 2)


def test_wrong_expectation_is_reported_with_the_case_that_failed():
    result = run(
        TWO_SUM,
        [
            {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"},
            {"input": "[3, 2, 4], 6", "expected": "[0, 1]"},
        ],
        comparator="sorted_list",
    )

    assert not result.ok
    report = result.failure_report()
    assert "case 2" in report
    assert "[3, 2, 4], 6" in report
    assert "[0, 1]" in report
    assert "[1, 2]" in report


def test_order_independent_comparator_accepts_the_other_order():
    assert run(
        TWO_SUM,
        [{"input": "[2, 7, 11, 15], 9", "expected": "[1, 0]"}],
        comparator="sorted_list",
    ).ok


def test_float_tolerance_accepts_a_near_miss_and_rejects_a_far_one():
    solution = "def solve(nums):\n    return sum(nums) / len(nums)\n"

    assert run(
        solution,
        [{"input": "[1, 2]", "expected": "1.5000000001"}],
        comparator="float_tolerance",
    ).ok
    assert not run(
        solution,
        [{"input": "[1, 2]", "expected": "1.6"}],
        comparator="float_tolerance",
    ).ok


def test_custom_comparator_decides_the_match():
    solution = "def solve(value):\n    return value + 1\n"

    assert run(
        solution,
        [{"input": "9", "expected": "10"}],
        comparator="custom",
        custom=(
            "def compare(actual, expected):\n    return abs(actual - expected) <= 1\n"
        ),
    ).ok


def test_expected_value_that_is_not_a_python_literal_compares_as_text():
    # The harness falls back to a repr comparison rather than crashing, so a
    # problem written with prose for an expected output still grades.
    solution = "def solve(text):\n    return text.upper()\n"

    assert (
        run(
            solution,
            [{"input": "'ok'", "expected": "the uppercased text"}],
            comparator="exact",
        ).ok
        is False
    )
    assert run(
        solution,
        [{"input": "'ok'", "expected": "'OK'"}],
    ).ok


def test_zero_argument_function_is_called_with_an_empty_argument_list():
    result = run("def solve():\n    return 42\n", [{"input": "", "expected": "42"}])

    assert result.ok


def test_solution_that_prints_does_not_corrupt_the_result():
    result = run(
        "def solve(value):\n    print('debug', value)\n    return value\n",
        [{"input": "7", "expected": "7"}],
    )

    assert result.ok


def test_missing_function_fails_the_whole_run():
    result = run(
        "def another_name():\n    return []\n",
        [{"input": "[1], 1", "expected": "[]"}],
    )

    assert not result.ok
    assert result.cases == ()
    assert "no function named solve()" in result.error


def test_solution_that_loops_forever_is_stopped(settings):
    settings.AI_CONTENT_VERIFY_TIMEOUT = 1

    result = run(
        "def solve():\n    while True:\n        pass\n",
        [{"input": "", "expected": "None"}],
    )

    assert not result.ok
    assert result.cases == ()
    assert "did not finish" in result.error


def test_raising_case_is_reported_with_its_exception():
    result = run(
        "def solve(nums):\n    return nums[5]\n",
        [{"input": "[1]", "expected": "1"}],
    )

    assert not result.ok
    assert "IndexError" in result.failure_report()
