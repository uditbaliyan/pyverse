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
    problem(
        slug="second-smallest-distinct",
        title="Second Smallest Distinct Value",
        topic="array-play",
        difficulty="easy",
        fn="second_smallest",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return the second smallest <strong>distinct</strong> value in <code>nums</code>. A repeated minimum does not count twice. If there are fewer than two distinct values, return <code>-1</code>.",
        ),
        examples=[
            (
                "nums = [12, 13, 1, 10, 34, 1]",
                "10",
                "Distinct values are 1, 10, 12, 13, 34; the second smallest is 10",
            ),
        ],
        constraints=["0 <= len(nums) <= 10^5"],
        todo="Track the smallest and second smallest values seen so far in one pass.",
        solution="""
            def second_smallest(nums: list[int]) -> int:
                smallest = None
                second = None
                for x in nums:
                    if smallest is None or x < smallest:
                        second = smallest
                        smallest = x
                    elif x != smallest and (second is None or x < second):
                        second = x
                return -1 if second is None else second
        """,
        trace=1,
        cases=[
            ("[12, 13, 1, 10, 34, 1]", "10", False),
            ("[5, 3, 8]", "5", False),
            ("[4, 4, 4]", "-1", True),
            ("[7]", "-1", True),
            ("[]", "-1", True),
            ("[-3, -3, 0, -1]", "-1", True),
        ],
        hints=(
            "Sorting works, but can you do it with just two variables?",
            "When a new minimum appears, the old minimum becomes the runner-up.",
            "Use <code>x != smallest</code> so a repeat of the minimum is not mistaken for the second value.",
        ),
        approaches=[
            (
                "Sort the distinct values",
                "<code>sorted(set(nums))[1]</code> when it exists.",
                "O(n log n)",
                "O(n)",
                False,
            ),
            (
                "Track two values",
                "One pass keeping the smallest and runner-up.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "x != smallest stops a repeat of the minimum from becoming the runner-up; that is why the second 1 does not count.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For [12, 13, 1, 10, 34, 1], what is second just before <code>second = x</code> runs with x = 10?",
                "12, the old runner-up that 10 is about to replace.",
            ),
        ],
        patterns=["Array Scan"],
        techniques=["None sentinel", "Conditional expression"],
    ),
    problem(
        slug="maximum-subarray-sum",
        title="Maximum Subarray Sum",
        topic="array-play",
        difficulty="medium",
        fn="max_subarray_sum",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return the largest sum of any non-empty contiguous slice of <code>nums</code>. The list always has at least one element and may contain negatives.",
        ),
        examples=[
            (
                "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]",
                "6",
                "The slice [4, -1, 2, 1] sums to 6",
            ),
        ],
        constraints=["1 <= len(nums) <= 10^5", "-10^4 <= nums[i] <= 10^4"],
        todo="Track the best sum of a slice ending at the current element, and the best seen overall.",
        solution="""
            def max_subarray_sum(nums: list[int]) -> int:
                best = nums[0]
                current = nums[0]
                for x in nums[1:]:
                    current = max(x, current + x)
                    best = max(best, current)
                return best
        """,
        trace=1,
        cases=[
            ("[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "6", False),
            ("[5, -9, 6]", "6", False),
            ("[-3]", "-3", True),
            ("[-4, -2, -7]", "-2", True),
            ("[1, 2, 3]", "6", True),
            ("[8, -19, 5, -4, 20]", "21", True),
        ],
        hints=(
            "Consider the best slice that ends exactly at position i. How does it relate to the one ending at i - 1?",
            "Either extend the previous slice or start fresh at x, whichever is larger.",
            "<code>current = max(x, current + x)</code>, then <code>best = max(best, current)</code>.",
        ),
        approaches=[
            (
                "Try every slice",
                "Sum all pairs of start and end.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Extend or restart (Kadane)",
                "One pass; drop a running sum once it hurts.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Either extend the slice ending at the previous element or restart at x; if current + x < x the old run was a burden and is dropped.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For [-2, 1, -3, 4, -1, 2, 1, -5, 4], what is current before <code>current = max(x, current + x)</code> runs with x = 4 (the first 4)?",
                "-2, so current + x = 2 is smaller than 4 and the run restarts at 4.",
            ),
        ],
        patterns=["Dynamic Programming"],
        techniques=["Running maximum", "max()"],
    ),
    problem(
        slug="longest-run-of-ones",
        title="Longest Run of Ones",
        topic="array-play",
        difficulty="medium",
        fn="longest_ones",
        signature="(bits: list[int]) -> int",
        description=html(
            "<code>bits</code> contains only 0s and 1s. Return the length of the longest block of consecutive 1s, or 0 if there are none.",
        ),
        examples=[
            (
                "bits = [1, 1, 0, 1, 1, 1]",
                "3",
                "The last three 1s form the longest block",
            ),
        ],
        constraints=["0 <= len(bits) <= 10^5"],
        todo="Count the current streak; reset it on a 0 and remember the largest streak seen.",
        solution="""
            def longest_ones(bits: list[int]) -> int:
                best = 0
                run = 0
                for bit in bits:
                    if bit == 1:
                        run += 1
                        best = max(best, run)
                    else:
                        run = 0
                return best
        """,
        trace=1,
        cases=[
            ("[1, 1, 0, 1, 1, 1]", "3", False),
            ("[1, 0, 1, 1, 0, 1]", "2", False),
            ("[]", "0", True),
            ("[0, 0]", "0", True),
            ("[1]", "1", True),
            ("[1, 1, 1, 1]", "4", True),
        ],
        hints=(
            "What breaks a streak of 1s?",
            "Keep a counter of the current streak and a separate best.",
            "Add 1 to <code>run</code> on a 1 and update <code>best</code>; on a 0 reset <code>run</code> to 0.",
        ),
        approaches=[
            (
                "Join and split",
                "Turn the bits into a string and split on '0'.",
                "O(n)",
                "O(n)",
                False,
            ),
            ("Running streak", "One pass with two counters.", "O(n)", "O(1)", True),
        ],
        notes=[
            (
                9,
                "A zero cuts the streak, so run restarts; best still holds the longest streak seen before the cut.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For [1, 1, 0, 1, 1, 1], what are run and best the first time <code>run = 0</code> is reached?",
                "run = 2 and best = 2.",
            ),
        ],
        patterns=["Array Scan"],
        techniques=["Running counter", "max()"],
    ),
    problem(
        slug="median-of-a-list",
        title="Median of a List",
        topic="array-play",
        difficulty="medium",
        fn="median",
        signature="(nums: list[int]) -> float",
        description=html(
            "Return the median of <code>nums</code> as a float. After sorting, the median is the middle value; when the length is even it is the average of the two middle values. The list has at least one element.",
            "Answers are compared with a small tolerance.",
        ),
        examples=[
            (
                "nums = [3, 1, 4, 1, 5]",
                "3.0",
                "Sorted: [1, 1, 3, 4, 5]; the middle value is 3",
            ),
        ],
        constraints=["1 <= len(nums) <= 10^5"],
        todo="Sort a copy, then pick the middle element or average the two middle ones.",
        solution="""
            def median(nums: list[int]) -> float:
                ordered = sorted(nums)
                count = len(ordered)
                mid = count // 2
                if count % 2 == 1:
                    result = float(ordered[mid])
                else:
                    low = ordered[mid - 1]
                    high = ordered[mid]
                    result = (low + high) / 2
                return result
        """,
        trace=2,
        comparator="float_tolerance",
        cases=[
            ("[3, 1, 4, 1, 5]", "3.0", False),
            ("[7, 1, 3, 5]", "4.0", False),
            ("[2]", "2.0", True),
            ("[1, 2]", "1.5", True),
            ("[-5, -1, -3]", "-3.0", True),
            ("[10, 10, 10, 10]", "10.0", True),
        ],
        hints=(
            "The median needs the values in order. What happens to 'the middle' when the count is even?",
            "Sort first; with an odd count take index <code>count // 2</code>.",
            "With an even count average <code>ordered[mid - 1]</code> and <code>ordered[mid]</code>.",
        ),
        approaches=[
            (
                "Sort and pick",
                "Sorting dominates the cost.",
                "O(n log n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "An even count has no single middle element, so take the two values that straddle the centre and average them.",
                False,
            ),
        ],
        predictions=[
            (
                10,
                "For [7, 1, 3, 5], what are low and high when <code>result = (low + high) / 2</code> is reached?",
                "low = 3 and high = 5 (sorted: 1, 3, 5, 7).",
            ),
        ],
        patterns=["Sorting"],
        techniques=["sorted()", "Integer division"],
    ),
    problem(
        slug="common-elements-two-lists",
        title="Common Elements of Two Lists",
        topic="array-play",
        difficulty="medium",
        fn="common_elements",
        signature="(a: list[int], b: list[int]) -> list[int]",
        description=html(
            "Return the values that appear in both <code>a</code> and <code>b</code>. Each value is listed once, in ascending order.",
        ),
        examples=[
            (
                "a = [1, 2, 3, 4], b = [3, 4, 5, 6]",
                "[3, 4]",
                "3 and 4 appear in both lists",
            ),
        ],
        constraints=["0 <= len(a), len(b) <= 10^5"],
        todo="Put one list in a set so membership tests are fast, then collect matches from the other.",
        solution="""
            def common_elements(a: list[int], b: list[int]) -> list[int]:
                in_b = set(b)
                common = set()
                for x in a:
                    if x in in_b:
                        common.add(x)
                return sorted(common)
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4], [3, 4, 5, 6]", "[3, 4]", False),
            ("[5, 5, 1, 2], [2, 5, 5, 9]", "[2, 5]", False),
            ("[], [1]", "[]", True),
            ("[1, 2], [3, 4]", "[]", True),
            ("[7, 7, 7], [7]", "[7]", True),
            ("[-1, 0, 4], [4, 0, -1, 8]", "[-1, 0, 4]", True),
        ],
        hints=(
            "Testing x in a list rescans the list. What structure makes that test cheap?",
            "Convert one list to a set, then loop over the other.",
            "Add matches to a second set so duplicates collapse, and finish with <code>sorted(common)</code>.",
        ),
        approaches=[
            (
                "Compare every pair",
                "Two nested loops over the lists.",
                "O(n * m)",
                "O(k)",
                False,
            ),
            (
                "Set membership",
                "A set test is O(1) on average.",
                "O(n + m + k log k)",
                "O(n + k)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Membership in a set is O(1) on average; testing against the list b would rescan b for every x.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [1, 2, 3, 4] and [3, 4, 5, 6], what is the set common before it is sorted?",
                "{3, 4}.",
            ),
        ],
        patterns=["Hash Set"],
        techniques=["Set", "sorted()"],
    ),
    problem(
        slug="triplets-summing-to-zero",
        title="Triplets Summing to Zero",
        topic="array-play",
        difficulty="medium",
        fn="three_sum",
        signature="(nums: list[int]) -> list[list[int]]",
        description=html(
            "Return every unique triplet of values from <code>nums</code> that adds up to 0. The three values must come from three different positions, and no triplet may be listed twice (compare by values). Triplets and the values inside them may come back in any order.",
        ),
        examples=[
            (
                "nums = [-1, 0, 1, 2, -1, -4]",
                "[[-1, -1, 2], [-1, 0, 1]]",
                "[-1, -1, 2] and [-1, 0, 1]",
            ),
        ],
        constraints=["0 <= len(nums) <= 3000", "-10^5 <= nums[i] <= 10^5"],
        todo="Sort, fix the first value, then close in on the other two with a left and a right pointer.",
        solution="""
            def three_sum(nums: list[int]) -> list[list[int]]:
                nums = sorted(nums)
                triplets = []
                for i in range(len(nums) - 2):
                    if i > 0 and nums[i] == nums[i - 1]:
                        continue
                    left, right = i + 1, len(nums) - 1
                    while left < right:
                        total = nums[i] + nums[left] + nums[right]
                        if total < 0:
                            left += 1
                        elif total > 0:
                            right -= 1
                        else:
                            triplets.append([nums[i], nums[left], nums[right]])
                            left += 1
                            while left < right and nums[left] == nums[left - 1]:
                                left += 1
                return triplets
        """,
        trace=1,
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
            ("[-1, 0, 1, 2, -1, -4]", "[[-1, -1, 2], [-1, 0, 1]]", False),
            ("[0, 0, 0, 0]", "[[0, 0, 0]]", False),
            ("[]", "[]", True),
            ("[1, 2, -2, -1]", "[]", True),
            ("[-2, 0, 1, 1, 2]", "[[-2, 0, 2], [-2, 1, 1]]", True),
            ("[3, 0, -2, -1, 1, 2]", "[[-2, -1, 3], [-2, 0, 2], [-1, 0, 1]]", True),
        ],
        hints=(
            "If you fix one value, the other two must add to its negative. How does sorting help find them?",
            "After sorting, move a left pointer up when the sum is too small and a right pointer down when it is too big.",
            "Skip repeated values for the fixed index and for the left pointer after recording a triplet.",
        ),
        approaches=[
            (
                "Try every triple",
                "Three nested loops and a set to remove duplicates.",
                "O(n^3)",
                "O(k)",
                False,
            ),
            (
                "Sort and two pointers",
                "Fix one value and sweep the rest from both ends.",
                "O(n^2)",
                "O(1) extra",
                True,
            ),
        ],
        notes=[
            (
                5,
                "After sorting, equal values sit side by side, so skipping an i that equals the previous one avoids starting the same triplet twice.",
                False,
            ),
            (
                17,
                "After recording a triplet, skip equal values on the left so the same triplet is not recorded again.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For [-1, 0, 1, 2, -1, -4], what is i the first time <code>continue</code> is reached? (The sorted list is [-4, -1, -1, 0, 1, 2].)",
                "2, because nums[2] repeats nums[1].",
            ),
        ],
        patterns=["Two Pointers", "Sorting"],
        techniques=["Sorted-array sweep", "Duplicate skipping"],
    ),
    problem(
        slug="even-minus-odd-sum",
        title="Even Sum Minus Odd Sum",
        topic="array-play",
        difficulty="easy",
        fn="even_odd_difference",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return (the sum of the even numbers in <code>nums</code>) minus (the sum of the odd numbers). The result can be negative. Negative numbers count as odd or even by the usual rule (-3 is odd, -4 is even).",
        ),
        examples=[
            (
                "nums = [1, 2, 3, 4, 5, 6]",
                "3",
                "Evens sum to 12, odds to 9, and 12 - 9 = 3",
            ),
        ],
        constraints=["0 <= len(nums) <= 10^5"],
        todo="Keep two running sums, one for evens and one for odds.",
        solution="""
            def even_odd_difference(nums: list[int]) -> int:
                even_sum = 0
                odd_sum = 0
                for x in nums:
                    if x % 2 == 0:
                        even_sum += x
                    else:
                        odd_sum += x
                return even_sum - odd_sum
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 5, 6]", "3", False),
            ("[10, 7, 4]", "7", False),
            ("[]", "0", True),
            ("[-3, 2]", "5", True),
            ("[5]", "-5", True),
            ("[0, 0]", "0", True),
        ],
        hints=(
            "How do you tell whether a number is even?",
            "Use <code>x % 2 == 0</code> and keep a separate total for each group.",
            "Return <code>even_sum - odd_sum</code> after the loop.",
        ),
        approaches=[
            (
                "Two passes",
                "Sum evens, then sum odds, with two generator expressions.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "One pass, two totals",
                "Route each number to the right accumulator.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "In Python -3 % 2 is 1, so the remainder test classifies negative numbers correctly as well.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For [1, 2, 3, 4, 5, 6], what are even_sum and odd_sum when <code>return</code> is reached?",
                "even_sum = 12 and odd_sum = 9, so the answer is 3.",
            ),
        ],
        patterns=["Array Scan"],
        techniques=["Accumulator", "Modulo"],
    ),
]
