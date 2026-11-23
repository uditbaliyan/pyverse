"""Load the starter problem bank into the database.

    manage.py seed_problems                      # create what is missing
    manage.py seed_problems --dry-run            # verify and report, write nothing
    manage.py seed_problems --update             # also overwrite existing slugs
    manage.py seed_problems --slug two-sum-ii-sorted --slug 3sum

What it does, in order:

1. **Verifies every reference solution** against its own answer key with the same
   out-of-process verifier `check_problem_traces` and `ai_create` use. If any
   problem fails, nothing is written: a wrong answer key silently marks correct
   learners wrong, so it must never reach the database.
2. Creates the Practice topic pages the bank needs (under the Practice hub) if
   they do not exist yet. Existing topics are reused by slug.
3. Creates each `CodingProblem`, or, with `--update`, rewrites the existing one.
   Without `--update`, a slug that already exists is left alone so hand edits
   made in the CMS are never overwritten by accident.

Afterwards run the quality gate and, if you keep a content fixture, dump it:

    manage.py check_problem_traces --report
    manage.py dump_content
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from pyverse.ai_content.verify import verify
from pyverse.coding.models import CodingProblem
from pyverse.coding.problem_bank import PROBLEMS
from pyverse.coding.problem_bank import TOPICS

HINT_TIERS = ("nudge", "approach", "solution")


def _rich(text: str) -> str:
    """Rich-text fields store HTML; make sure a bare string is a paragraph."""
    text = text.strip()
    return text if text.startswith("<") else f"<p>{text}</p>"


def _stream_fields(spec: dict[str, Any]) -> dict[str, list[dict]]:
    """The StreamField columns, as raw block data Wagtail turns into StreamValues."""
    return {
        "examples": [
            {
                "type": "example",
                "value": {"input": inp, "output": out, "note": note},
            }
            for inp, out, note in spec["examples"]
        ],
        "constraints": [
            {"type": "item", "value": text} for text in spec["constraints"]
        ],
        "hint_tiers": [
            {"type": "hint", "value": {"tier": tier, "text": _rich(text)}}
            for tier, text in zip(HINT_TIERS, spec["hints"], strict=True)
        ],
        "editorial_approaches": [
            {
                "type": "approach",
                "value": {
                    "name": name,
                    "description": _rich(description),
                    "time_complexity": time,
                    "space_complexity": space,
                    "is_optimal": optimal,
                },
            }
            for name, description, time, space, optimal in spec["approaches"]
        ],
        "trace_notes": [
            {
                "type": "note",
                "value": {"line": line, "note": note, "every_visit": every},
            }
            for line, note, every in spec["trace_notes"]
        ],
        "trace_predictions": [
            {
                "type": "prediction",
                "value": {"line": line, "question": question, "answer": answer},
            }
            for line, question, answer in spec["trace_predictions"]
        ],
        "test_cases": [
            {
                "type": "test_case",
                "value": {
                    "input": args,
                    "expected_output": expected,
                    "is_hidden": hidden,
                },
            }
            for args, expected, hidden in spec["cases"]
        ],
    }


def _case_payload(spec: dict[str, Any]) -> list[dict]:
    """The shape `CodingProblem.test_case_payload()` gives the verifier."""
    return [
        {"input": args, "expected": expected, "hidden": hidden}
        for args, expected, hidden in spec["cases"]
    ]


def verify_spec(spec: dict[str, Any]):
    """Run one bank entry's reference solution against its answer key."""
    return verify(
        function_name=spec["function_name"],
        solution_code=spec["solution_code"],
        comparator=spec["comparator"],
        cases=_case_payload(spec),
        custom_comparator_code=spec["custom_comparator_code"],
    )


class Command(BaseCommand):
    help = "Create (or with --update, refresh) the starter Practice problems."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            action="append",
            default=[],
            help="Only this problem (repeatable). Default: the whole bank.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite problems whose slug already exists (default: skip them).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Verify the solutions and report what would change; write nothing.",
        )
        parser.add_argument(
            "--no-verify",
            action="store_true",
            help="Skip the solution-vs-answer-key check (not recommended).",
        )

    def handle(self, *args, **options):
        specs = self._select(options["slug"])

        if not options["no_verify"]:
            self._verify_all(specs)

        if options["dry_run"]:
            self._report_plan(specs, update=options["update"])
            return

        with transaction.atomic():
            topics = self._ensure_topics({spec["topic"] for spec in specs})
            created = updated = skipped = 0
            for spec in specs:
                outcome = self._save(
                    spec,
                    topics[spec["topic"]],
                    update=options["update"],
                )
                created += outcome == "created"
                updated += outcome == "updated"
                skipped += outcome == "skipped"

        self.stdout.write(
            self.style.SUCCESS(
                f"{created} created, {updated} updated, {skipped} skipped "
                f"({len(specs)} in selection).",
            ),
        )
        self.stdout.write(
            "Next: manage.py check_problem_traces --report   "
            "(then manage.py dump_content to refresh content/site.json)",
        )

    # ------------------------------------------------------------------
    def _select(self, slugs: list[str]) -> list[dict[str, Any]]:
        known = {spec["slug"]: spec for spec in PROBLEMS}
        if len(known) != len(PROBLEMS):
            msg = "problem_bank has duplicate slugs"
            raise CommandError(msg)
        unknown = sorted(set(slugs) - known.keys())
        if unknown:
            msg = f"unknown slug(s): {', '.join(unknown)}"
            raise CommandError(msg)
        return [known[slug] for slug in slugs] if slugs else list(PROBLEMS)

    def _verify_all(self, specs: list[dict[str, Any]]) -> None:
        failures = []
        for spec in specs:
            result = verify_spec(spec)
            if result.ok:
                counts = f"{result.passed_count}/{result.total} cases"
                self.stdout.write(f"  verified {spec['slug']}: {counts}")
            else:
                failures.append(f"{spec['slug']}:\n{result.failure_report()}")
        if failures:
            msg = (
                "reference solution(s) fail their own answer key; "
                "nothing was written:\n"
            )
            raise CommandError(msg + "\n".join(failures))

    def _report_plan(self, specs: list[dict[str, Any]], *, update: bool) -> None:
        existing = set(
            CodingProblem.objects.filter(
                slug__in=[spec["slug"] for spec in specs],
            ).values_list("slug", flat=True),
        )
        for spec in specs:
            if spec["slug"] not in existing:
                action = "create"
            else:
                action = "update" if update else "skip (exists)"
            self.stdout.write(f"  {action:<14} {spec['slug']}  [{spec['topic']}]")
        self.stdout.write(self.style.WARNING("dry run: nothing written"))

    def _ensure_topics(self, wanted: set[str]) -> dict[str, Any]:
        from pyverse.topics.models import PracticeHubPage  # noqa: PLC0415
        from pyverse.topics.models import PracticeTopicPage  # noqa: PLC0415

        unknown = wanted - TOPICS.keys()
        if unknown:
            msg = f"topic(s) not declared in problem_bank.TOPICS: {sorted(unknown)}"
            raise CommandError(msg)

        hub = PracticeHubPage.objects.first()
        if hub is None:
            msg = (
                "no Practice hub page exists. Run `manage.py load_content` "
                "or create one in the CMS first."
            )
            raise CommandError(msg)

        topics = {}
        for slug in TOPICS:
            if slug not in wanted:
                continue
            topic = PracticeTopicPage.objects.filter(slug=slug).first()
            if topic is None:
                topic = hub.add_child(
                    instance=PracticeTopicPage(title=TOPICS[slug], slug=slug),
                )
                self.stdout.write(f"  created topic page: {TOPICS[slug]} ({slug})")
            topics[slug] = topic
        return topics

    def _save(self, spec: dict[str, Any], topic, *, update: bool) -> str:
        problem = CodingProblem.objects.filter(slug=spec["slug"]).first()
        if problem is not None and not update:
            self.stdout.write(
                f"  skipped {spec['slug']} (already exists; use --update)",
            )
            return "skipped"

        outcome = "created" if problem is None else "updated"
        problem = problem or CodingProblem(slug=spec["slug"])

        problem.topic = topic
        problem.title = spec["title"]
        problem.difficulty = spec["difficulty"]
        problem.description = _rich(spec["description"])
        problem.function_name = spec["function_name"]
        problem.function_signature = spec["function_signature"]
        problem.comparator = spec["comparator"]
        problem.custom_comparator_code = spec["custom_comparator_code"]
        problem.starter_code = spec["starter_code"]
        problem.solution_code = spec["solution_code"]
        problem.solution_explanation = (
            _rich(spec["solution_explanation"]) if spec["solution_explanation"] else ""
        )
        problem.trace_case = spec["trace_case"]
        for name, value in _stream_fields(spec).items():
            setattr(problem, name, value)

        # Runs CodingProblem.clean(): trace notes must point at real solution lines.
        problem.full_clean()
        problem.save()

        problem.companies.set(spec["companies"])
        problem.patterns.set(spec["patterns"])
        problem.techniques.set(spec["techniques"])
        problem.save()

        self.stdout.write(f"  {outcome} {spec['slug']}")
        return outcome
