"""Gate for the "solve it, then watch it execute" promise.

Every problem is supposed to have a trace worth watching. This checks, for each
`CodingProblem`, what the learner's page will actually do:

* the reference solution passes every test case (same out-of-process verifier
  the AI authoring pipeline uses, so a wrong answer key is caught here too);
* it traces cleanly on the first *visible* case, with the tracer that ships to
  the browser (`includes/tracer_runtime.html`, loaded by `trace_harness`);
* that trace is not cut off by the step cap, which would end the walk-through
  mid-loop on the very example the learner is shown first.

Errors fail the run (exit 1); warnings do not unless `--strict`.

    manage.py check_problem_traces
    manage.py check_problem_traces --slug two-sum --slug valid-anagram --strict
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.ai_content.verify import verify
from pyverse.coding.models import CodingProblem
from pyverse.coding.trace_harness import load_tracer

# Mirrors LINE_LIMIT in static/js/problem-trace.js.
LINE_LIMIT = 200_000
MIN_STEPS = 3


def check_problem(problem: CodingProblem, tracer) -> tuple[list[str], list[str]]:
    """Return `(errors, warnings)` for one problem."""
    errors: list[str] = []
    warnings: list[str] = []

    cases = problem.test_case_payload()
    visible = [case for case in cases if not case["hidden"]]
    if not visible:
        warnings.append(
            "no visible test case: the learner must type arguments to trace anything",
        )
    if not problem.solution_code.strip():
        warnings.append("no reference solution: the page offers no reference trace")
        return errors, warnings
    if not cases:
        errors.append("no test cases: the reference solution cannot be verified")
        return errors, warnings

    result = verify(
        function_name=problem.function_name,
        solution_code=problem.solution_code,
        comparator=problem.comparator,
        cases=cases,
        custom_comparator_code=problem.custom_comparator_code,
    )
    if not result.ok:
        errors.append(f"reference solution fails:\n{result.failure_report()}")
        return errors, warnings
    if not visible:
        return errors, warnings

    args = visible[0]["input"]
    traced = json.loads(
        tracer.trace_call(
            problem.solution_code, problem.function_name, args, LINE_LIMIT,
        ),
    )
    if traced["error"]:
        errors.append(f"reference trace on ({args}) stopped: {traced['error']}")
    elif len(traced["steps"]) < MIN_STEPS:
        warnings.append(
            f"reference trace on ({args}) has only {len(traced['steps'])} steps",
        )
    if traced["truncated"]:
        warnings.append(
            f"reference trace on ({args}) hits the step cap; "
            "use a smaller first visible example",
        )
    return errors, warnings


class Command(BaseCommand):
    help = "Check that every coding problem's reference solution verifies and traces."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--slug", action="append", default=[], help="Limit to a slug (repeatable).",
        )
        parser.add_argument(
            "--strict", action="store_true", help="Treat warnings as errors.",
        )

    def handle(self, *args, **options) -> None:
        problems = CodingProblem.objects.order_by("slug")
        if options["slug"]:
            problems = problems.filter(slug__in=options["slug"])
        problems = list(problems)
        if not problems:
            msg = "no coding problems matched"
            raise CommandError(msg)

        tracer = load_tracer()
        failed = warned = 0
        for problem in problems:
            errors, warnings = check_problem(problem, tracer)
            if errors:
                failed += 1
            elif warnings:
                warned += 1
            status = "FAIL" if errors else "warn" if warnings else "ok"
            style = {
                "FAIL": self.style.ERROR,
                "warn": self.style.WARNING,
                "ok": self.style.SUCCESS,
            }[status]
            self.stdout.write(style(f"[{status:>4}] {problem.slug}"))
            for line in errors:
                self.stdout.write(self.style.ERROR(f"         ✗ {line}"))
            for line in warnings:
                self.stdout.write(self.style.WARNING(f"         ! {line}"))

        self.stdout.write(
            f"\n{len(problems)} problems: {len(problems) - failed - warned} ok, "
            f"{warned} with warnings, {failed} failing.",
        )
        if failed or (options["strict"] and warned):
            msg = "problem check failed"
            raise CommandError(msg)
