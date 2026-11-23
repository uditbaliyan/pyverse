# ruff: noqa: E501, ISC004, RUF001
"""Two Pointers: converging and read/write pointers over one array or string."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="valid-palindrome",
        title="Valid Palindrome",
        topic="two-pointers",
        difficulty="easy",
        fn="is_palindrome",
        signature="(s: str) -> bool",
        description=html(
            "A phrase is a palindrome if, after ignoring everything that is not a letter or "
            "digit and ignoring case, it reads the same forwards and backwards.",
            "Return <code>True</code> if <code>s</code> is a palindrome under that rule.",
        ),
        examples=[
            (
                's = "A man, a plan, a canal: Panama"',
                "True",
                '"amanaplanacanalpanama" reads the same both ways.',
            ),
            ('s = "race a car"', "False", '"raceacar" does not.'),
        ],
        constraints=["1 <= len(s) <= 2 * 10^5", "s is printable ASCII."],
        todo="Compare letters and digits from both ends, skipping everything else.",
        solution="""
            def is_palindrome(s: str) -> bool:
                left, right = 0, len(s) - 1
                while left < right:
                    if not s[left].isalnum():
                        left += 1
                    elif not s[right].isalnum():
                        right -= 1
                    else:
                        if s[left].lower() != s[right].lower():
                            return False
                        left += 1
                        right -= 1
                return True
        """,
        trace=2,
        cases=[
            ('"A man, a plan, a canal: Panama"', "True", False),
            ('"race a car"', "False", False),
            ('" "', "True", True),
            ('"0P"', "False", True),
            ('".,"', "True", True),
        ],
        hints=(
            "You could build a cleaned copy and compare it with its reverse. "
            "Is there a way to avoid the copy?",
            "Put one index at each end and move them towards each other, "
            "skipping characters that are not letters or digits.",
            "Use <code>str.isalnum()</code> to skip, and compare with <code>.lower()</code>. "
            "Return False at the first mismatch.",
        ),
        approaches=[
            (
                "Clean, then compare with the reverse",
                "Build <code>cleaned</code> and test <code>cleaned == cleaned[::-1]</code>.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Two pointers",
                "Walk inwards from both ends and skip junk in place.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "Skip anything that is not a letter or digit instead of building a cleaned copy. "
                "That keeps extra memory at O(1).",
                True,
            ),
            (10, "One mismatch is enough to answer, so return early.", False),
        ],
        predictions=[
            (
                10,
                "On 'race a car', which pair of characters finally disagrees?",
                "'e' on the left and 'a' on the right.",
            ),
        ],
        patterns=["Two Pointers"],
        techniques=["String Methods"],
    ),
    problem(
        slug="two-sum-ii-sorted",
        title="Two Sum II – Sorted Input",
        topic="two-pointers",
        difficulty="medium",
        fn="two_sum_sorted",
        signature="(numbers: list[int], target: int) -> list[int]",
        description=html(
            "Given an array <code>numbers</code> that is already sorted in "
            "<strong>non-decreasing</strong> order, find two numbers that add up to "
            "<code>target</code>.",
            "Return their <strong>1-based</strong> positions as <code>[index1, index2]</code> "
            "with <code>index1 &lt; index2</code>. Exactly one solution exists, "
            "and you may not use the same element twice. Use only O(1) extra space.",
        ),
        examples=[
            ("numbers = [2,7,11,15], target = 9", "[1,2]", "2 + 7 = 9"),
            ("numbers = [1,3,4,5,7,10,11], target = 9", "[3,4]", "4 + 5 = 9"),
        ],
        constraints=[
            "2 <= numbers.length <= 3 * 10^4",
            "numbers is sorted.",
            "Exactly one solution exists.",
        ],
        todo="Return the 1-based positions of the two numbers that add to target.",
        solution="""
            def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
                left, right = 0, len(numbers) - 1
                while left < right:
                    total = numbers[left] + numbers[right]
                    if total == target:
                        return [left + 1, right + 1]
                    if total < target:
                        left += 1
                    else:
                        right -= 1
                return []
        """,
        trace=2,
        cases=[
            ("[2, 7, 11, 15], 9", "[1, 2]", False),
            ("[1, 3, 4, 5, 7, 10, 11], 9", "[3, 4]", False),
            ("[-1, 0], -1", "[1, 2]", True),
            ("[5, 25, 75], 100", "[2, 3]", True),
            ("[1, 2, 3, 4, 4, 9, 56, 90], 8", "[4, 5]", True),
        ],
        hints=(
            "The classic Two Sum uses a dict. The array being sorted should let you do "
            "it with no extra memory.",
            "Put one pointer at each end. Look at their sum.",
            "Too small: move the left pointer right. Too big: move the right pointer left.",
        ),
        approaches=[
            (
                "Dict of seen values",
                "The Two Sum solution works, but uses O(n) memory and ignores the sorting.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Two pointers",
                "The sort tells you which pointer to move after every comparison.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Sorted order is the whole trick: too small means only moving left can help, "
                "too big means only moving right can.",
                True,
            ),
        ],
        predictions=[
            (
                6,
                "For [1, 3, 4, 5, 7, 10, 11] and target 9, what is returned?",
                "[3, 4] (1-based positions of 4 and 5).",
            ),
        ],
        patterns=["Two Pointers"],
        techniques=["Tuple Unpacking"],
    ),
    problem(
        slug="container-with-most-water",
        title="Container With Most Water",
        topic="two-pointers",
        difficulty="medium",
        fn="max_area",
        signature="(height: list[int]) -> int",
        description=html(
            "You are given an array <code>height</code>. The <code>i</code>-th vertical line "
            "stands at position <code>i</code> and is <code>height[i]</code> tall.",
            "Pick two lines. Together with the x-axis they form a container; "
            "its water level is limited by the <em>shorter</em> line. "
            "Return the largest area of water any container can hold.",
        ),
        examples=[
            (
                "height = [1,8,6,2,5,4,8,3,7]",
                "49",
                "Lines of height 8 and 7, seven apart: 7 × 7.",
            ),
            ("height = [1,1]", "1", ""),
        ],
        constraints=["2 <= height.length <= 10^5", "0 <= height[i] <= 10^4"],
        todo="Return the largest area formed by any two lines.",
        solution="""
            def max_area(height: list[int]) -> int:
                left, right = 0, len(height) - 1
                best = 0
                while left < right:
                    width = right - left
                    area = width * min(height[left], height[right])
                    best = max(best, area)
                    if height[left] < height[right]:
                        left += 1
                    else:
                        right -= 1
                return best
        """,
        cases=[
            ("[1, 8, 6, 2, 5, 4, 8, 3, 7]", "49", False),
            ("[1, 1]", "1", False),
            ("[4, 3, 2, 1, 4]", "16", True),
            ("[1, 2, 1]", "2", True),
            ("[2, 3, 4, 5, 18, 17, 6]", "17", True),
        ],
        hints=(
            "Trying every pair of lines is O(n²). Start from the widest container instead.",
            "Begin with the two outermost lines. Which one would you move inwards, and why?",
            "Always move the pointer at the <em>shorter</em> line: keeping it can only give a "
            "smaller width with the same or lower height.",
        ),
        approaches=[
            (
                "Try every pair",
                "Two nested loops over every pair of lines.",
                "O(n²)",
                "O(1)",
                False,
            ),
            (
                "Shrink from the outside",
                "Start at the widest pair and move whichever side is shorter.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "The water level is capped by the shorter wall, so moving the taller wall can "
                "never help. Always move the shorter one.",
                True,
            ),
        ],
        predictions=[
            (
                12,
                "For [1, 8, 6, 2, 5, 4, 8, 3, 7], what is best when the loop ends?",
                "49: the walls of height 8 and 7, seven apart.",
            ),
        ],
        patterns=["Two Pointers", "Greedy"],
        techniques=["Builtins"],
    ),
    problem(
        slug="move-zeroes",
        title="Move Zeroes",
        topic="two-pointers",
        difficulty="easy",
        fn="move_zeroes",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Given an integer array <code>nums</code>, return a <strong>new</strong> list in "
            "which every <code>0</code> has been moved to the end and the non-zero values "
            "keep their original relative order.",
            "Do not change <code>nums</code> itself.",
        ),
        examples=[
            ("nums = [0,1,0,3,12]", "[1,3,12,0,0]", ""),
            ("nums = [0,0,1]", "[1,0,0]", ""),
        ],
        constraints=["1 <= nums.length <= 10^4", "-2^31 <= nums[i] <= 2^31 - 1"],
        todo="Return a copy with all zeros moved to the end, order of the rest kept.",
        solution="""
            def move_zeroes(nums: list[int]) -> list[int]:
                result = nums[:]
                write = 0
                for read in range(len(result)):
                    if result[read] != 0:
                        result[write], result[read] = result[read], result[write]
                        write += 1
                return result
        """,
        cases=[
            ("[0, 1, 0, 3, 12]", "[1, 3, 12, 0, 0]", False),
            ("[0, 0, 1]", "[1, 0, 0]", False),
            ("[0]", "[0]", True),
            ("[1, 2, 3]", "[1, 2, 3]", True),
            ("[4, 0, 5, 0, 0, 6]", "[4, 5, 6, 0, 0, 0]", True),
        ],
        hints=(
            "You could collect the non-zeros and pad with zeros. Can you do it in one pass "
            "over a single list?",
            "Use two indices: <code>read</code> scans every item, <code>write</code> marks "
            "the next slot for a non-zero value.",
            "When <code>result[read]</code> is not zero, swap it into <code>write</code> and advance "
            "<code>write</code>.",
        ),
        approaches=[
            (
                "Filter and pad",
                "Keep the non-zeros, then append the right number of zeros.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Read / write pointers",
                "One pass; each non-zero is swapped into the next free slot.",
                "O(n)",
                "O(1) extra",
                True,
            ),
        ],
        notes=[
            (
                6,
                "Swapping drops each non-zero into the next free slot at write. "
                "Zeros get pushed behind it without a second list.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For [0, 1, 0, 3, 12], what is write at the end?",
                "3: one step for each non-zero value.",
            ),
        ],
        patterns=["Two Pointers"],
        techniques=["Tuple Unpacking", "Slicing"],
    ),
    problem(
        slug="three-sum",
        title="3Sum",
        topic="two-pointers",
        difficulty="medium",
        fn="three_sum",
        signature="(nums: list[int]) -> list[list[int]]",
        description=html(
            "Given an integer array <code>nums</code>, return every <strong>unique</strong> "
            "triplet <code>[a, b, c]</code> of values that adds up to <code>0</code>, "
            "using three different positions.",
            "The answer must not contain duplicate triplets. Triplets and the order "
            "of the answer may be in any order.",
        ),
        examples=[
            ("nums = [-1,0,1,2,-1,-4]", "[[-1,-1,2],[-1,0,1]]", ""),
            ("nums = [0,1,1]", "[]", "No triplet sums to 0."),
        ],
        constraints=["3 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"],
        todo="Return all unique triplets that sum to 0.",
        solution="""
            def three_sum(nums: list[int]) -> list[list[int]]:
                nums = sorted(nums)
                result = []
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
                            result.append([nums[i], nums[left], nums[right]])
                            left += 1
                            while left < right and nums[left] == nums[left - 1]:
                                left += 1
                return result
        """,
        comparator="custom",
        custom_comparator="""
            def compare(actual, expected):
                def normal(triplets):
                    return sorted(sorted(triplet) for triplet in triplets)

                return normal(actual) == normal(expected)
        """,
        cases=[
            ("[-1, 0, 1, 2, -1, -4]", "[[-1, -1, 2], [-1, 0, 1]]", False),
            ("[0, 1, 1]", "[]", False),
            ("[0, 0, 0]", "[[0, 0, 0]]", True),
            ("[-2, 0, 1, 1, 2]", "[[-2, 0, 2], [-2, 1, 1]]", True),
            ("[0, 0, 0, 0]", "[[0, 0, 0]]", True),
        ],
        hints=(
            "Fix one number. What are you looking for in the rest of the array?",
            "Sort first. For each fixed number, the rest is a sorted Two Sum problem for "
            "<code>-nums[i]</code>.",
            "Skip a fixed number if it equals the previous one, and after recording a "
            "triplet advance <code>left</code> past equal values to avoid repeats.",
        ),
        approaches=[
            (
                "Three nested loops",
                "Check every triplet and de-duplicate with a set. Far too slow for 3000 items.",
                "O(n³)",
                "O(n)",
                False,
            ),
            (
                "Sort and two pointers",
                "Fix one value, then sweep two pointers over the sorted remainder.",
                "O(n²)",
                "O(1) extra",
                True,
            ),
        ],
        notes=[
            (
                2,
                "Sorting lets two pointers work and puts duplicates side by side, "
                "so they are easy to skip.",
                False,
            ),
            (
                6,
                "Same first number as last time would only repeat the same triplets, so skip it.",
                False,
            ),
        ],
        predictions=[
            (
                15,
                "How many triplets have been appended by the end, for [-1, 0, 1, 2, -1, -4]?",
                "2: [-1, -1, 2] and [-1, 0, 1].",
            ),
        ],
        patterns=["Two Pointers", "Sorting"],
        techniques=["Sorting", "Early Continue"],
    ),
]
