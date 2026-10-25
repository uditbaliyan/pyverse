"""Run the browser's tracer in CPython — one source of truth, no port.

The "watch it execute" feature is Python that lives in a template
(`includes/tracer_runtime.html`) because it runs in the learner's browser under
PyScript. This module extracts that very `<script type="py">` block and execs it
against a stub `js` module, so tests and the `check_problem_traces` command
exercise the code that ships, not a copy of it (the same parity rule as
`ai_content/verify_runner.py` for grading).

Not used at request time and never imported by the exported site.
"""

from __future__ import annotations

import re
import sys
import types
from pathlib import Path
from typing import Any

TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "templates"
    / "includes"
    / "tracer_runtime.html"
)
_BLOCK = re.compile(r'<script type="py">\n(.*?)</script>', re.DOTALL)


class _Anything:
    """Absorbs the DOM calls the runtime makes while booting."""

    def __init__(self) -> None:
        self.dataset = types.SimpleNamespace()
        self.head = self
        self.body = self

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *args, **kwargs: _Anything()


def load_tracer() -> types.SimpleNamespace:
    """Return `.trace`, `.trace_call` and `.window` from the shipped runtime."""
    match = _BLOCK.search(TEMPLATE.read_text(encoding="utf-8"))
    if match is None:
        msg = f'no <script type="py"> block found in {TEMPLATE}'
        raise RuntimeError(msg)

    window = types.SimpleNamespace(_pendingLabCode="")
    document = _Anything()
    stub = types.ModuleType("js")
    stub.document = document  # type: ignore[attr-defined]
    stub.window = window  # type: ignore[attr-defined]

    previous = sys.modules.get("js")
    sys.modules["js"] = stub
    namespace: dict[str, Any] = {"__name__": "pyverse_tracer"}
    try:
        exec(compile(match.group(1), str(TEMPLATE), "exec"), namespace)  # noqa: S102
    finally:
        if previous is None:
            sys.modules.pop("js", None)
        else:
            sys.modules["js"] = previous

    return types.SimpleNamespace(
        trace=namespace["trace"],
        trace_call=namespace["trace_call"],
        window=window,
        ready=document.dataset.labReady == "1",
    )
