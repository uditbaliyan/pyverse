"""Starter problem bank for Practice.

    from pyverse.coding.problem_bank import PROBLEMS, TOPICS

Every entry is a plain dict (see `_spec.problem`). Load them into the database
with `manage.py seed_problems`; verify them with `manage.py check_problem_traces`.
"""

from . import arrays
from . import pointers
from . import stack_search
from . import warmup
from . import window
from ._spec import TOPICS

PROBLEMS: list[dict] = [
    *warmup.PROBLEMS,
    *arrays.PROBLEMS,
    *pointers.PROBLEMS,
    *window.PROBLEMS,
    *stack_search.PROBLEMS,
]

__all__ = ["PROBLEMS", "TOPICS"]
