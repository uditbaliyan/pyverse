"""Starter problem bank for Practice.

    from pyverse.coding.problem_bank import PROBLEMS, TOPICS

Every entry is a plain dict (see `_spec.problem`). Load them into the database
with `manage.py seed_problems`; verify them with `manage.py check_problem_traces`.
"""

from . import arrays
from . import matrix_patterns
from . import pattern_printing
from . import pointers
from . import stack_search
from . import warmup
from . import window
from . import array_drills
from . import grid_drills
from . import number_drills
from . import string_drills
from ._spec import TOPICS

PROBLEMS: list[dict] = [
    *warmup.PROBLEMS,
    *arrays.PROBLEMS,
    *pointers.PROBLEMS,
    *window.PROBLEMS,
    *stack_search.PROBLEMS,
    *pattern_printing.PROBLEMS,
    *matrix_patterns.PROBLEMS,
    *array_drills.PROBLEMS,
    *grid_drills.PROBLEMS,
    *number_drills.PROBLEMS,
    *string_drills.PROBLEMS,
]

__all__ = ["PROBLEMS", "TOPICS"]
