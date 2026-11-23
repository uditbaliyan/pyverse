# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="pairs-with-target-sum",
        title="Pairs with a Target Sum",
        topic="array-play",
        difficulty="medium",
        fn="find_pairs",
        signature="(nums: list[int], target: int) -> list[list[int]]",
        description=html(
            "Find every distinct pair of values <code>[a, b]</code> with <code>a <= b</code> and <code>a + b == target</code>, where the two values come from two different positions in <code>nums</code>.",
            "List each value pair once, even if it can be formed several ways, sorted in ascending order. Order inside the result does not matter to the grader.",
        ),
        examples=[
            (
                "nums = [1, 2, 3, 4, 5], target = 5",
                "[[1, 4], [2, 3]]",
                "[1, 4] and [2, 3] both add to 5",
            ),
        ],
        constraints=["0 <= len(nums) <= 10^4", "-10^6 <= nums[i], target <= 10^6"],
        todo="Remember the values you have seen; for each x look for target - x among them.",
        solution="""
            def find_pairs(nums: list[int], target: int) -> list[list[int]]:
                seen = set()
                found = set()
                for x in nums:
                    need = target - x
                    if need in seen:
                        found.add((min(x, need), max(x, need)))
                    seen.add(x)
                return [list(pair) for pair in sorted(found)]
        """,
        trace=1,
        comparator="custom",
        custom_comparator="""
def compare(actual, expected):
    norm = lambda pairs: sorted(tuple(sorted(p)) for p in pairs)
    try:
        return norm(actual) == norm(expected)
    except TypeError:
        return False
""",
        cases=[
            ("[1, 2, 3, 4, 5], 5", "[[1, 4], [2, 3]]", False),
            ("[3, 3, 3, 6], 6", "[[3, 3]]", False),
            ("[], 5", "[]", True),
            ("[2, 2, 2], 4", "[[2, 2]]", True),
            ("[-1, 1, 0, 2, -2], 0", "[[-2, 2], [-1, 1]]", True),
            ("[5], 10", "[]", True),
        ],
        hints=(
            "For a given x, which single value would complete the pair?",
            "Keep a set of values already seen; test whether <code>target - x</code> is in it.",
            "Check the set before adding x, and store pairs as <code>(min, max)</code> tuples in a set so repeats collapse.",
        ),
        approaches=[
            (
                "Check every pair",
                "Two nested loops over positions i < j.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Seen set",
                "One pass; a set answers 'have I seen the complement?' in O(1).",
                "O(n log n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "Checking before adding x means x cannot pair with itself; a pair needs two different positions.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For nums = [1, 2, 3, 4, 5] and target 5, what are x and need the first time <code>found.add(...)</code> is reached?",
                "x = 3 and need = 2 (2 was seen earlier).",
            ),
        ],
        patterns=["Hash Set"],
        techniques=["Set", "List comprehension"],
    ),
    problem(
        slug="longest-consecutive-run",
        title="Longest Consecutive Run",
        topic="array-play",
        difficulty="medium",
        fn="longest_consecutive",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return the length of the longest run of consecutive integers (such as 5, 6, 7, 8) that can be formed from values in <code>nums</code>. The values may appear in any order and may repeat; a repeated value counts once.",
            "Aim for linear time: do not sort.",
        ),
        examples=[
            ("nums = [100, 4, 200, 1, 3, 2]", "4", "1, 2, 3, 4 is the longest run"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "-10^9 <= nums[i] <= 10^9"],
        todo="Put the values in a set; only start counting from values whose predecessor is missing.",
        solution="""
            def longest_consecutive(nums: list[int]) -> int:
                values = set(nums)
                best = 0
                for x in values:
                    if x - 1 not in values:
                        length = 1
                        while x + length in values:
                            length += 1
                        best = max(best, length)
                return best
        """,
        trace=1,
        cases=[
            ("[100, 4, 200, 1, 3, 2]", "4", False),
            ("[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]", "9", False),
            ("[]", "0", True),
            ("[5]", "1", True),
            ("[1, 2, 2, 3]", "3", True),
            ("[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]", "7", True),
        ],
        hints=(
            "A run has exactly one start: a number whose predecessor is not in the data.",
            "Store the numbers in a set and only walk upwards from numbers where <code>x - 1</code> is absent.",
            "Walk with <code>while x + length in values</code> and keep the maximum length seen.",
        ),
        approaches=[
            (
                "Sort, then scan",
                "Sort the distinct values and count streaks.",
                "O(n log n)",
                "O(n)",
                False,
            ),
            (
                "Hash set, start only at run beginnings",
                "Each run is walked once.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Only a number with no left neighbour can start a run, so every run is walked exactly once; that keeps the total work linear.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For [100, 4, 200, 1, 3, 2], what is length when <code>best = max(best, length)</code> is reached for the run starting at 1?",
                "4 (1, 2, 3, 4).",
            ),
        ],
        patterns=["Hash Set"],
        techniques=["Set", "Counting loop"],
    ),
    problem(
        slug="all-subsets",
        title="All Subsets",
        topic="array-play",
        difficulty="medium",
        fn="all_subsets",
        signature="(nums: list[int]) -> list[list[int]]",
        description=html(
            "Return every subset of the list <code>nums</code> (all values are distinct), including the empty subset and the whole list. Subsets may come back in any order, and the order of values inside a subset does not matter.",
        ),
        examples=[
            ("nums = [1, 2]", "[[], [1], [2], [1, 2]]", "[], [1], [2], [1, 2]"),
        ],
        constraints=["0 <= len(nums) <= 10", "All values are distinct"],
        todo="Start with just the empty subset; for each value, add a copy of every existing subset that also contains it.",
        solution="""
            def all_subsets(nums: list[int]) -> list[list[int]]:
                subsets = [[]]
                for x in nums:
                    subsets += [subset + [x] for subset in subsets]
                return subsets
        """,
        trace=2,
        comparator="custom",
        custom_comparator="""
def compare(actual, expected):
    norm = lambda groups: sorted(sorted(g) for g in groups)
    try:
        return norm(actual) == norm(expected)
    except TypeError:
        return False
""",
        cases=[
            ("[1, 2]", "[[], [1], [2], [1, 2]]", False),
            (
                "[1, 2, 3]",
                "[[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]",
                False,
            ),
            ("[]", "[[]]", True),
            ("[5]", "[[], [5]]", True),
            (
                "[3, 1, 2, 4]",
                "[[], [3], [1], [2], [4], [3, 1], [3, 2], [3, 4], [1, 2], [1, 4], [2, 4], [3, 1, 2], [3, 1, 4], [3, 2, 4], [1, 2, 4], [3, 1, 2, 4]]",
                True,
            ),
            ("[-1, 0]", "[[], [-1], [0], [-1, 0]]", True),
        ],
        hints=(
            "Each element is either in a subset or out of it. How many subsets does that give for n elements?",
            "Process one element at a time; every subset built so far can be copied with that element added.",
            "<code>subsets += [subset + [x] for subset in subsets]</code> doubles the list on every pass.",
        ),
        approaches=[
            (
                "Bitmask enumeration",
                "Treat each number from 0 to 2^n - 1 as a choose/skip pattern.",
                "O(n * 2^n)",
                "O(n * 2^n)",
                False,
            ),
            (
                "Doubling",
                "Each new element doubles the collection of subsets.",
                "O(n * 2^n)",
                "O(n * 2^n)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "Every existing subset spawns a twin that also contains x, so the list doubles on each pass: 2^n subsets in total.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For [1, 2, 3], how many subsets are in the list the third time <code>subsets += ...</code> is reached (x = 3)?",
                "4: [], [1], [2], [1, 2].",
            ),
        ],
        patterns=["Combinatorics", "Backtracking"],
        techniques=["List comprehension", "Augmented assignment"],
    ),
]
