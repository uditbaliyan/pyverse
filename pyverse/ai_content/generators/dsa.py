"""Generate a ``CodingProblem`` — the one content type with a hard check.

Two things make this generator different from its siblings:

* The generated solution is *executed* against the generated test cases before
  anything is saved (``verify.py``). A draft whose answer key does not reproduce
  itself is refused outright.
* What "draft" means here is "no topic". ``CodingProblem`` has no draft state,
  but every learner-facing listing filters on ``topic__isnull=False``, so
  generating without a topic is what keeps the problem invisible until Udit
  reviews it and assigns one — that assignment is the publish step.
"""

from __future__ import annotations

from string import Template
from typing import Any
from typing import ClassVar

from django.urls import reverse

from pyverse.ai_content.exceptions import GenerationError
from pyverse.ai_content.exceptions import VerificationError
from pyverse.ai_content.generators.base import Draft
from pyverse.ai_content.generators.base import Generator
from pyverse.ai_content.generators.base import Report
from pyverse.ai_content.generators.base import choice
from pyverse.ai_content.generators.base import flag
from pyverse.ai_content.generators.base import optional_text
from pyverse.ai_content.generators.base import required_text
from pyverse.ai_content.generators.base import rows
from pyverse.ai_content.verify import verify
from pyverse.coding.models import CodingProblem
from pyverse.coding.models import Comparator
from pyverse.coding.models import HintBlock
from pyverse.coding.models import ProblemCompany
from pyverse.coding.models import ProblemPattern
from pyverse.coding.models import ProblemTechnique
from pyverse.quiz.models import QuizTechnique
from pyverse.taxonomy import Difficulty

# Reveal order of the three hint tiers (coding/models.py HintBlock.Tier).
_TIER_ORDER = {
    HintBlock.Tier.NUDGE.value: 0,
    HintBlock.Tier.APPROACH.value: 1,
    HintBlock.Tier.SOLUTION.value: 2,
}

# The three browsing tag axes. The keys are both the JSON keys the model fills
# in and the CodingProblem manager attributes those tags are added through.
_TAG_AXES: dict[str, Any] = {
    "companies": ProblemCompany,
    "patterns": ProblemPattern,
    "techniques": ProblemTechnique,
}

# The field schema. Kept to the model's field names, and to values the grader
# actually reads, so nothing here can drift from coding/models.py unnoticed.
_SCHEMA = Template(
    """\
Reply with one JSON object with exactly these keys:

{
  "title": "problem title, title case, no difficulty in it",
  "difficulty": one of $difficulties,
  "description": "HTML problem statement",
  "function_name": "snake_case name the learner must define",
  "function_signature": "signature as written in a def, e.g. (nums: list[int]) -> int",
  "comparator": one of $comparators,
  "custom_comparator_code": "compare() source, or empty unless custom",
  "starter_code": "the signature, a one-line comment and `pass`",
  "solution_code": "the complete reference solution: the function only, no prints",
  "solution_explanation": "HTML prose on why it works, including complexity",
  "examples": [
    {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]",
     "note": "nums[0] + nums[1] == 9"}
  ],
  "constraints": ["2 <= nums.length <= 10^4"],
  "hint_tiers": [
    {"tier": "nudge", "text": "HTML"},
    {"tier": "approach", "text": "HTML"},
    {"tier": "solution", "text": "HTML"}
  ],
  "editorial_approaches": [
    {"name": "Hash map, one pass", "description": "HTML",
     "time_complexity": "O(n)", "space_complexity": "O(n)",
     "is_optimal": true}
  ],
  "test_cases": [
    {"input": "[2, 7, 11, 15], 9", "expected_output": "[0, 1]",
     "is_hidden": false}
  ],
  "companies": [],
  "patterns": [],
  "techniques": []
}

What each field is judged on:
- description, solution_explanation, hint text and approach description are
  HTML: paragraphs in <p>, identifiers and literals in <code>, the deciding
  detail in <strong>. No Markdown.
- input inside test_cases is the argument list alone, as Python source, as it
  would sit between the parentheses of a call. expected_output is what the
  function returns for it, written as the Python value it is — [0, 1], "hi",
  2.5, True — never a string that merely looks like one.
- constraint strings are the bounds a solution must respect, one per entry.
- The solution_code you return must pass every test_case you return: it is
  executed against them before this draft is accepted. Include at least two
  non-hidden cases and cover the edges of the constraints; hide the cases that
  would give the trick away.
""",
)


class DsaGenerator(Generator):
    slug: ClassVar[str] = "dsa"
    menu_label: ClassVar[str] = "DSA problem"
    label: ClassVar[str] = "CodingProblem"
    style_file: ClassVar[str] = "dsa.md"
    review_notes: ClassVar[tuple[str, ...]] = (
        "Confirm function_name, function_signature and comparator — they wire "
        "the grading harness.",
        "Assign a topic to publish it: learners only see problems that have one.",
    )

    def build_schema(self) -> str:
        schema = _SCHEMA.substitute(
            difficulties=_quoted(Difficulty.values),
            comparators=_quoted(Comparator.values),
        )
        return f"{schema}\n{_tag_rules()}"

    def pre_create(self, data: dict[str, Any], report: Report) -> None:
        comparator = self._comparator(data)
        custom = optional_text(data, "custom_comparator_code")
        if comparator == Comparator.CUSTOM.value and not custom:
            message = (
                "the model chose the 'custom' comparator but returned no "
                "compare(actual, expected) code"
            )
            raise GenerationError(message)

        cases = self._test_cases(data)
        if not cases:
            message = "the model returned no test cases to verify"
            raise GenerationError(message)
        if all(case["value"]["is_hidden"] for case in cases):
            message = (
                "every generated test case is hidden — learners need at least "
                "one visible case to check themselves against"
            )
            raise GenerationError(message)

        report("Verifying test cases against the generated solution...")
        result = verify(
            function_name=required_text(data, "function_name"),
            solution_code=required_text(data, "solution_code"),
            comparator=comparator,
            custom_comparator_code=custom,
            cases=[_payload_case(case) for case in cases],
        )
        if not result.ok:
            raise VerificationError(_report(result))

        report(f"✓ All {result.total} cases pass")

    def create(self, data: dict[str, Any], parent: Any = None) -> Draft:
        # Snippet types have no parent: the topic is assigned during review.
        problem = CodingProblem(
            title=required_text(data, "title"),
            difficulty=choice(
                data,
                "difficulty",
                list(Difficulty.values),
                default=Difficulty.EASY.value,
            ),
            description=optional_text(data, "description"),
            function_name=required_text(data, "function_name"),
            function_signature=optional_text(data, "function_signature"),
            comparator=self._comparator(data),
            custom_comparator_code=optional_text(data, "custom_comparator_code"),
            solution_code=required_text(data, "solution_code"),
            solution_explanation=optional_text(data, "solution_explanation"),
            starter_code=optional_text(data, "starter_code"),
        )
        problem.examples = self._examples(data)
        problem.constraints = [
            {"type": "item", "value": value}
            for value in (data.get("constraints") or [])
            if isinstance(value, str) and value.strip()
        ]
        problem.hint_tiers = self._hints(data)
        problem.editorial_approaches = self._approaches(data)
        problem.test_cases = self._test_cases(data)
        problem.save()

        notes = [*self.review_notes, *self._apply_tags(problem, data)]
        return Draft(
            label=self.label,
            title=problem.title,
            review_url=reverse(
                "wagtailsnippets_coding_codingproblem:edit",
                args=[problem.pk],
            ),
            notes=tuple(notes),
        )

    # ── JSON → field values ──────────────────────────────────────────────
    # pre_create() and create() share these, so the cases that were verified
    # are literally the cases that get stored.

    def _comparator(self, data: dict[str, Any]) -> str:
        return choice(
            data,
            "comparator",
            list(Comparator.values),
            default=Comparator.EXACT.value,
        )

    def _examples(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "type": "example",
                "value": {
                    "input": optional_text(row, "input"),
                    "output": optional_text(row, "output"),
                    "note": optional_text(row, "note"),
                },
            }
            for row in rows(data, "examples")
        ]

    def _hints(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        hints = [
            {
                "type": "hint",
                "value": {
                    "tier": choice(row, "tier", list(HintBlock.Tier.values)),
                    "text": required_text(row, "text"),
                },
            }
            for row in rows(data, "hint_tiers")
        ]
        # Hints are revealed one at a time in the order written, so order by
        # tier rather than trusting the model to have sorted its own list.
        hints.sort(key=lambda hint: _TIER_ORDER[hint["value"]["tier"]])
        return hints

    def _approaches(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "type": "approach",
                "value": {
                    "name": required_text(row, "name"),
                    "description": optional_text(row, "description"),
                    "time_complexity": optional_text(row, "time_complexity"),
                    "space_complexity": optional_text(row, "space_complexity"),
                    "is_optimal": flag(row, "is_optimal"),
                },
            }
            for row in rows(data, "editorial_approaches")
        ]

    def _test_cases(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "type": "test_case",
                "value": {
                    # An empty input is legitimate: a zero-argument function.
                    "input": optional_text(row, "input"),
                    "expected_output": required_text(row, "expected_output"),
                    "is_hidden": flag(row, "is_hidden"),
                },
            }
            for row in rows(data, "test_cases")
        ]

    def _apply_tags(self, problem: CodingProblem, data: dict[str, Any]) -> list[str]:
        """Tag the problem, using only names the browse filters already know."""
        notes = []
        for axis, through_model in _TAG_AXES.items():
            wanted = data.get(axis)
            if not isinstance(wanted, list):
                continue
            vocabulary = {
                name.casefold(): name for name in _vocabulary(axis, through_model)
            }
            names = [vocabulary.get(str(name).strip().casefold()) for name in wanted]
            getattr(problem, axis).add(*[name for name in names if name])

            dropped = [
                str(name)
                for name, found in zip(wanted, names, strict=True)
                if not found
            ]
            if dropped:
                notes.append(
                    f"{axis} dropped (not an existing tag): {', '.join(dropped)} "
                    "— add the tag in /cms/ if it is a real new one.",
                )
        return notes


def _payload_case(case: dict[str, Any]) -> dict[str, str]:
    """One verified case in the shape ``verify`` and the browser payload use."""
    return {
        "input": case["value"]["input"],
        "expected": case["value"]["expected_output"],
    }


def _report(result: Any) -> str:
    summary = (
        "the generated solution does not reproduce the generated test cases "
        f"({result.passed_count}/{result.total} pass)"
        if result.total
        else "the generated solution could not be graded"
    )
    return f"{summary}\n{result.failure_report()}"


def _quoted(values: list[str]) -> str:
    return " | ".join(f'"{value}"' for value in values)


def _vocabulary(axis: str, through_model: Any) -> list[str]:
    """Tag names already in use on this axis, across problems and quizzes.

    Generated problems join the existing vocabulary instead of inventing a
    parallel one: a tag no other row carries matches no browse filter.
    """
    names = set(through_model.objects.values_list("tag__name", flat=True))
    if axis == "techniques":
        # Techniques span problems and quizzes (spec §5), so both count.
        names.update(QuizTechnique.objects.values_list("tag__name", flat=True))
    return sorted(names)


def _tag_rules() -> str:
    vocabulary = {
        axis: _vocabulary(axis, through_model)
        for axis, through_model in _TAG_AXES.items()
    }
    if not any(vocabulary.values()):
        return (
            "## Tags\n\nNo tags exist yet, so leave companies, patterns and "
            "techniques as empty lists.\n"
        )
    lines = [
        "## Tags",
        "",
        "Use only names from these lists — a new name would be a tag no browse",
        "filter can match. Leave an axis empty when nothing fits.",
        "",
    ]
    lines.extend(
        f"- {axis}: {', '.join(names)}" if names else f"- {axis}: (none yet)"
        for axis, names in vocabulary.items()
    )
    return "\n".join(lines) + "\n"
