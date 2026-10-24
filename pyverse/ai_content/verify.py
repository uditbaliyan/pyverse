"""Run a generated solution against a generated answer key, out of process.

This is the step that makes the DSA generator trustworthy: a hallucinated
``expected_output`` is invisible during review but silently marks correct learner
submissions wrong later, and nothing else in the pipeline can catch it.

What is verified is exactly what the challenge page will bake into
``#pyverse-payload`` — ``CodingProblem.test_case_payload()`` — so a pass here
predicts a pass in the learner's browser, because ``verify_runner.py`` mirrors
that page's harness.

The solution runs in a subprocess for two reasons: an infinite loop must not
hang the command, and a solution that raises must not take the command with it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Mapping

RUNNER = Path(__file__).with_name("verify_runner.py")


@dataclass(frozen=True)
class CaseResult:
    """One test case's outcome, as the reviewer needs to read it."""

    index: int
    input: str
    passed: bool
    expected: str
    actual: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class Verification:
    function_name: str
    cases: tuple[CaseResult, ...] = ()
    #: Set when the run itself failed (timeout, crash, no such function): then
    #: no case was graded and ``cases`` is empty.
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and all(case.passed for case in self.cases)

    @property
    def passed_count(self) -> int:
        return sum(case.passed for case in self.cases)

    @property
    def total(self) -> int:
        return len(self.cases)

    def failure_report(self) -> str:
        """The failing cases, one paragraph each, for the refusal message."""
        if self.error is not None:
            return self.error

        lines: list[str] = []
        for case in self.cases:
            if case.passed:
                continue
            lines.append(f"  case {case.index}  {self.function_name}({case.input})")
            lines.append(f"          expected {case.expected}")
            if case.error is not None:
                lines.append(f"          raised   {case.error}")
            else:
                lines.append(f"          got      {case.actual}")
        return "\n".join(lines)


def verify(
    *,
    function_name: str,
    solution_code: str,
    comparator: str,
    cases: Iterable[Mapping[str, str]],
    custom_comparator_code: str = "",
) -> Verification:
    """Grade ``solution_code`` against ``cases`` (``test_case_payload()`` shape)."""
    job = json.dumps(
        {
            "function_name": function_name,
            "solution_code": solution_code,
            "comparator": comparator,
            "custom_comparator_code": custom_comparator_code,
            "cases": [
                {"input": case["input"], "expected": case["expected"]} for case in cases
            ],
        },
        ensure_ascii=False,
    )
    limit = settings.AI_CONTENT_VERIFY_TIMEOUT

    try:
        completed = subprocess.run(  # noqa: S603 - argv list, no shell, absolute interpreter
            [sys.executable, str(RUNNER)],
            input=job,
            capture_output=True,
            text=True,
            timeout=limit,
            check=False,
        )
    except subprocess.TimeoutExpired:
        message = (
            f"the generated solution did not finish within {limit}s "
            "— it probably loops forever"
        )
        return Verification(function_name=function_name, error=message)
    except OSError as exc:
        return Verification(
            function_name=function_name,
            error=f"could not start the verifier: {exc}",
        )

    if completed.returncode != 0:
        tail = "\n".join((completed.stderr or "").strip().splitlines()[-3:])
        message = f"the verifier exited with code {completed.returncode}"
        return Verification(
            function_name=function_name,
            error=f"{message}\n{tail}" if tail else message,
        )

    try:
        payload = json.loads(completed.stdout)
    except ValueError:
        snippet = completed.stdout.strip()[:200]
        return Verification(
            function_name=function_name,
            error=f"the verifier returned unreadable output: {snippet!r}",
        )

    if payload.get("error"):
        return Verification(function_name=function_name, error=payload["error"])

    return Verification(
        function_name=function_name,
        cases=tuple(
            CaseResult(
                index=index,
                input=case["input"],
                passed=bool(case["passed"]),
                expected=case["expected"],
                actual=case.get("actual"),
                error=case.get("error"),
            )
            for index, case in enumerate(payload["cases"], start=1)
        ),
    )
