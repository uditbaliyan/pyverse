"""Grading harness, executed as a subprocess by ``verify.py``.

Never imported by application code: its whole job is to run a *generated*
solution against a *generated* answer key in a process the caller can kill. It
mirrors ``pyverse/templates/includes/pyscript_runtime.html`` deliberately — the
same "input is Python source for the argument list" convention, the same four
comparators, the same fallback to a repr comparison when an expected value is
not evaluable as a Python literal. The point of the check is to predict what a
learner's browser will do, so inventing a second grading rule here would defeat
it.

Contract: one JSON job on stdin, one JSON result on stdout, nothing else on
stdout. The solution's own output is captured, never forwarded.

This is process isolation, not a security sandbox. The code being run is
reviewed by a human before publication and executes in every learner's browser
by design; running it here too is what stops a wrong answer key reaching them.
"""

from __future__ import annotations

import io
import json
import sys
from typing import Any

TOLERANCE = 1e-6
MAX_REPR = 160


def _short(value: Any) -> str:
    """``repr`` a value, clipped: a wrong answer may be a 10^5-element list."""
    text = repr(value)
    return text if len(text) <= MAX_REPR else f"{text[:MAX_REPR]}…"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _float_close(actual: Any, expected: Any, tolerance: float = TOLERANCE) -> bool:
    if _is_number(actual) and _is_number(expected):
        return abs(actual - expected) <= tolerance
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        if len(actual) != len(expected):
            return False
        return all(
            _float_close(a, e, tolerance) for a, e in zip(actual, expected, strict=True)
        )
    return actual == expected


def _sorted_equal(actual: Any, expected: Any) -> bool:
    try:
        return sorted(actual) == sorted(expected)
    except TypeError:
        # Unorderable elements (dicts, nested mixed types): compare by repr.
        try:
            return sorted(map(repr, actual)) == sorted(map(repr, expected))
        # Mirroring the harness's last-resort guard, blind except included.
        except Exception:  # noqa: BLE001
            return False


def _expected_value(source: str) -> tuple[Any, bool]:
    """Expected outputs are authored as Python literals; evaluate when possible."""
    try:
        # Same rule as the harness: expected values are Python source literals.
        return eval(source, {}), True  # noqa: S307
    except Exception:  # noqa: BLE001 - a non-literal falls back to text compare
        return source, False


def _call(fn: Any, args_source: str) -> Any:
    # The harness calls the learner's function exactly this way.
    return eval("__fn(" + (args_source or "") + ")", {"__fn": fn})  # noqa: S307


# One return per comparator, in the harness's order: reading the two side by
# side is the point.
def _matches(  # noqa: PLR0911
    actual: Any,
    expected_source: str,
    mode: str,
    comparator_ns: dict,
) -> bool:
    """Dispatch on the problem's declared comparator (spec §5.2)."""
    expected, evaluated = _expected_value(expected_source)

    if mode == "sorted_list":
        if not evaluated:
            return repr(actual).strip() == str(expected_source).strip()
        return _sorted_equal(actual, expected)
    if mode == "float_tolerance":
        if not evaluated:
            return repr(actual).strip() == str(expected_source).strip()
        return _float_close(actual, expected)
    if mode == "custom":
        return bool(comparator_ns["compare"](actual, expected))
    if evaluated:
        return actual == expected
    return repr(actual).strip() == str(expected_source).strip()


def _load_solution(job: dict) -> tuple[Any, str | None]:
    """Compile the generated solution. Returns ``(fn, error)``."""
    namespace: dict = {}
    try:
        # Running generated code is this module's entire purpose.
        exec(compile(job["solution_code"], "<generated solution>", "exec"), namespace)  # noqa: S102
    except Exception as exc:  # noqa: BLE001
        return None, f"the solution did not run — {type(exc).__name__}: {exc}"

    fn = namespace.get(job["function_name"])
    if not callable(fn):
        name = job["function_name"]
        return None, f"the solution defines no function named {name}()"
    return fn, None


def _load_comparator(job: dict) -> tuple[dict, str | None]:
    """Compile the custom comparator, if one is declared. Returns ``(ns, error)``."""
    if (job.get("comparator") or "exact") != "custom":
        return {}, None

    source = job.get("custom_comparator_code") or ""
    if not source.strip():
        return (
            {},
            "the 'custom' comparator was declared but no compare() code was given",
        )

    namespace: dict = {}
    try:
        # The comparator travels as source and is exec'd by the harness too.
        exec(compile(source, "<custom comparator>", "exec"), namespace)  # noqa: S102
    except Exception as exc:  # noqa: BLE001
        return {}, f"the custom comparator did not run — {type(exc).__name__}: {exc}"
    if not callable(namespace.get("compare")):
        return {}, "the custom comparator defines no compare(actual, expected)"
    return namespace, None


def grade(job: dict) -> dict:
    fn, error = _load_solution(job)
    if error is not None:
        return {"error": error, "cases": []}

    comparator_ns, error = _load_comparator(job)
    if error is not None:
        return {"error": error, "cases": []}

    mode = job.get("comparator") or "exact"
    results = []
    for case in job["cases"]:
        entry: dict[str, Any] = {
            "input": case["input"],
            "expected": case["expected"],
            "passed": False,
            "actual": None,
            "error": None,
        }
        try:
            actual = _call(fn, case["input"])
            entry["actual"] = _short(actual)
            entry["passed"] = bool(
                _matches(actual, case["expected"], mode, comparator_ns),
            )
        # Any exception out of the generated code is a case failure, not a crash.
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
        results.append(entry)

    return {"error": None, "cases": results}


def main() -> int:
    job = json.load(sys.stdin)
    captured, real_stdout = io.StringIO(), sys.stdout
    sys.stdout = captured  # the solution may print; that must not corrupt our reply
    try:
        result = grade(job)
    finally:
        sys.stdout = real_stdout
    json.dump(result, real_stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
