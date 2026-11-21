"""Gym labs: browser-run practice exercises (core Python, NumPy, pandas, Matplotlib, seaborn).

Nothing here executes learner code on the server. `verify()` is an authoring-time
quality gate only (management command + tests), mirroring what the browser does.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from pyverse.common.sandbox import run_python

# key, label, Pyodide packages to load
LIBRARIES = [
    ("python", "Core Python", ()),
    ("numpy", "NumPy", ("numpy",)),
    ("pandas", "pandas", ("numpy", "pandas")),
    ("matplotlib", "Matplotlib", ("matplotlib",)),
    ("seaborn", "seaborn", ("numpy", "pandas", "matplotlib", "seaborn")),
]
LIBRARY_CHOICES = [(k, label) for k, label, _ in LIBRARIES]
LIBRARY_LABELS = dict(LIBRARY_CHOICES)
LIBRARY_ORDER = {k: i for i, (k, *_) in enumerate(LIBRARIES)}
PACKAGES = {k: pk for k, _, pk in LIBRARIES}
DIFFICULTY_CHOICES = [(1, "Easy"), (2, "Medium"), (3, "Hard")]

# Same contract as the browser worker: one namespace, setup -> learner code -> check.
_RUNNER = """
import json, sys
d = json.loads(sys.stdin.read())
ns = {"__name__": "__main__"}
for key in ("setup", "code", "check"):
    if d[key].strip():
        exec(compile(d[key], "<%s>" % key, "exec"), ns)
"""


def verify(setup: str, code: str, check: str, timeout: int = 60) -> tuple[bool, str]:
    """Run setup + code + check in a throwaway interpreter. Authoring/CI only."""
    try:
        p = run_python(
            [sys.executable, "-c", _RUNNER],
            stdin=json.dumps({"setup": setup, "code": code, "check": check}),
            timeout=timeout,
            parent_env=os.environ,
            extra_env={"MPLBACKEND": "Agg"},
            memory_mb=2048,  # numpy / pandas / matplotlib import cost
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    if p.returncode == 0:
        return True, ""
    lines = p.stderr.strip().splitlines()
    return False, lines[-1] if lines else f"exit {p.returncode}"
