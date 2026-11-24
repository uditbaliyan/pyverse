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
from . import sorting_tuf1
from . import arrays_basics_tuf1
from . import arrays_faq_tuf1
from . import recursion_rec1
from . import backtracking_rec1
from . import bits_rec1
from . import singles_rec1
from . import mazes_rec2
from . import linkedlist_rec2
from . import window_str1
from . import window_count_str1
from . import stack_str1
from . import stack_hard_str1
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
    *sorting_tuf1.PROBLEMS,
    *arrays_basics_tuf1.PROBLEMS,
    *arrays_faq_tuf1.PROBLEMS,
    *recursion_rec1.PROBLEMS,
    *backtracking_rec1.PROBLEMS,
    *bits_rec1.PROBLEMS,
    *singles_rec1.PROBLEMS,
    *mazes_rec2.PROBLEMS,
    *linkedlist_rec2.PROBLEMS,
    *window_str1.PROBLEMS,
    *window_count_str1.PROBLEMS,
    *stack_str1.PROBLEMS,
    *stack_hard_str1.PROBLEMS,
]

__all__ = ["PROBLEMS", "TOPICS"]
