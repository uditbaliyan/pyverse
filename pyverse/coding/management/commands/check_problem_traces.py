"""Gate for the "solve it, then watch it execute" promise.

Every problem is supposed to have a trace worth watching. This checks, for each
`CodingProblem`, what the learner's page will actually do:

* the reference solution passes every test case (same out-of-process verifier
  the AI authoring pipeline uses, so a wrong answer key is caught here too);
* it traces cleanly on the example the page shows (the pinned `trace_case`, else
  the first visible case), with the tracer that ships to the browser, and the
  value it *returns* equals the answer key under the problem's comparator, the
  grader's own rule (a mismatch means the walk-through shows a wrong answer);
* that trace is not cut off by the step cap and is neither trivial nor too long
  to follow (`MIN_STEPS`..`MAX_STEPS`, see `pyverse/coding/tracing.py`).

Errors fail the run (exit 1); warnings do not unless `--strict`.

    manage.py check_problem_traces
    manage.py check_problem_traces --slug two-sum --slug valid-anagram --strict
    manage.py check_problem_traces --report        # one table row per problem
    manage.py check_problem_traces --apply         # pin the best example where unset
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.ai_content.verify import verify
from pyverse.coding.models import CodingProblem
from pyverse.coding.trace_harness import load_tracer
from pyverse.coding.tracing import MAX_STEPS
from pyverse.coding.tracing import MIN_STEPS
from pyverse.coding.tracing import CaseTrace
from pyverse.coding.tracing import choose_trace_case
from pyverse.coding.tracing import trace_all_visible


@dataclass
class ProblemCheck:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    #: The case the page shows today (pinned, else first visible).
    shown: CaseTrace | None = None
    #: The best usable case, or the fallback first one (see choose_trace_case).
    best: CaseTrace | None = None

    @property
    def status(self) -> str:
        return "FAIL" if self.errors else "warn" if self.warnings else "ok"


def _shown_index(problem: CodingProblem, count: int) -> int:
    pinned = problem.trace_case
    return pinned - 1 if pinned and 1 <= pinned <= count else 0


def check_problem(problem: CodingProblem, tracer) -> ProblemCheck:  # noqa: C901, PLR0912
    check = ProblemCheck()
    errors, warnings = check.errors, check.warnings

    cases = problem.test_case_payload()
    visible = [case for case in cases if not case["hidden"]]
    if not visible:
        warnings.append(
            "no visible test case: the learner must type arguments to trace anything",
        )
    if not problem.solution_code.strip():
        warnings.append("no reference solution: the page offers no reference trace")
        return check
    if not cases:
        errors.append("no test cases: the reference solution cannot be verified")
        return check

    result = verify(
        function_name=problem.function_name,
        solution_code=problem.solution_code,
        comparator=problem.comparator,
        cases=cases,
        custom_comparator_code=problem.custom_comparator_code,
    )
    if not result.ok:
        errors.append(f"reference solution fails:\n{result.failure_report()}")
        return check
    if not visible:
        return check

    traces = trace_all_visible(problem, tracer)
    check.best = choose_trace_case(traces)
    shown = check.shown = traces[_shown_index(problem, len(traces))]
    where = f"reference trace on ({shown.args})"

    if shown.error:
        errors.append(f"{where} stopped: {shown.error}")
        return check
    if shown.matches_expected is False:
        errors.append(
            f"{where} returned a value the answer key rejects: the "
            "walk-through would show a wrong answer",
        )
    elif shown.matches_expected is None:
        warnings.append(f"{where}: the returned value could not be compared")
    if shown.truncated:
        warnings.append(f"{where} hits the step cap; use a smaller example")
    elif shown.steps < MIN_STEPS:
        warnings.append(
            f"{where} has only {shown.steps} steps (< {MIN_STEPS}): too trivial",
        )
    elif shown.steps > MAX_STEPS:
        warnings.append(
            f"{where} has {shown.steps} steps (> {MAX_STEPS}): too long to follow",
        )
    if shown.trivial:
        warnings.append(f"{where} returns an empty value: it shows nothing")

    best = check.best
    if (
        best is not None
        and best.usable
        and best.index != shown.index
        and not shown.usable
    ):
        warnings.append(
            f"visible case {best.index + 1} ({best.steps} steps) would trace better; "
            "set 'Trace example' or run with --apply",
        )
    return check


def _yes_no(value: bool | None) -> str:  # noqa: FBT001
    return "?" if value is None else "yes" if value else "NO"


def _report(rows: list[tuple[CodingProblem, ProblemCheck]]) -> list[str]:
    header = ("slug", "case", "steps", "fits", "matches", "best", "status")
    table = [header]
    for problem, check in rows:
        shown, best = check.shown, check.best
        table.append(
            (
                problem.slug,
                str(shown.index + 1) if shown else "-",
                str(shown.steps) if shown else "-",
                _yes_no(
                    None
                    if shown is None
                    else not shown.truncated and shown.steps <= MAX_STEPS,
                ),
                _yes_no(shown.matches_expected) if shown else "-",
                str(best.index + 1) if best and best.usable else "-",
                check.status,
            ),
        )
    widths = [max(len(row[i]) for row in table) for i in range(len(header))]
    return [
        "  ".join(
            cell.ljust(width) for cell, width in zip(row, widths, strict=True)
        ).rstrip()
        for row in table
    ]


class Command(BaseCommand):
    help = "Check that every coding problem's reference solution verifies and traces."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--slug",
            action="append",
            default=[],
            help="Limit to a slug (repeatable).",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Treat warnings as errors.",
        )
        parser.add_argument(
            "--report",
            action="store_true",
            help="Print a table: slug, case, steps, fits cap, matches, best.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Save the best usable example as 'Trace example' on problems that "
            "have none pinned (an author's pin is never overwritten).",
        )

    def handle(self, *args, **options) -> None:  # noqa: C901, PLR0912
        problems = CodingProblem.objects.order_by("slug")
        if options["slug"]:
            problems = problems.filter(slug__in=options["slug"])
        problems = list(problems)
        if not problems:
            msg = "no coding problems matched"
            raise CommandError(msg)

        tracer = load_tracer()
        failed = warned = applied = 0
        rows: list[tuple[CodingProblem, ProblemCheck]] = []
        for problem in problems:
            check = check_problem(problem, tracer)
            rows.append((problem, check))

            if (
                options["apply"]
                and problem.trace_case is None
                and check.best is not None
                and check.best.usable
                and check.best.index != 0
            ):
                problem.trace_case = check.best.index + 1
                problem.save(update_fields=["trace_case"])
                applied += 1
                # The page will now show the better case; re-judge against it.
                check = check_problem(problem, tracer)
                rows[-1] = (problem, check)

            if check.errors:
                failed += 1
            elif check.warnings:
                warned += 1
            if options["report"]:
                continue
            style = {
                "FAIL": self.style.ERROR,
                "warn": self.style.WARNING,
                "ok": self.style.SUCCESS,
            }[check.status]
            self.stdout.write(style(f"[{check.status:>4}] {problem.slug}"))
            for line in check.errors:
                self.stdout.write(self.style.ERROR(f"         ✗ {line}"))
            for line in check.warnings:
                self.stdout.write(self.style.WARNING(f"         ! {line}"))

        if options["report"]:
            for line in _report(rows):
                self.stdout.write(line)
            for problem, check in rows:
                for line in (*check.errors, *check.warnings):
                    self.stdout.write(f"{problem.slug}: {line}")

        self.stdout.write(
            f"\n{len(problems)} problems: {len(problems) - failed - warned} ok, "
            f"{warned} with warnings, {failed} failing."
            + (f" Pinned an example on {applied}." if options["apply"] else ""),
        )
        if failed or (options["strict"] and warned):
            msg = "problem check failed"
            raise CommandError(msg)
