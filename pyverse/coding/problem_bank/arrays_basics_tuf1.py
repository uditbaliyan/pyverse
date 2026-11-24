# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="linear-search",
        title="Linear Search",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="linear_search",
        signature="(nums: list[int], target: int) -> int",
        description=html(
            "Return the index of the <strong>first</strong> occurrence of <code>target</code> in <code>nums</code>, or <code>-1</code> if it does not appear.",
            "Check the elements one by one from the left; do not use <code>list.index</code>.",
        ),
        examples=[
            ("nums = [4, 8, 15, 16, 23, 42], target = 23", "4", "23 is at index 4"),
            ("nums = [1, 2, 3], target = 9", "-1", "9 never appears"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "-10^9 <= nums[i], target <= 10^9"],
        todo="Loop over the indices; return the first index whose value equals target, else -1.",
        solution="""
            def linear_search(nums: list[int], target: int) -> int:
                for i in range(len(nums)):
                    if nums[i] == target:
                        return i
                return -1
        """,
        trace=1,
        cases=[
            ("[4, 8, 15, 16, 23, 42], 23", "4", False),
            ("[1, 2, 3], 9", "-1", False),
            ("[], 1", "-1", True),
            ("[5, 5, 5], 5", "0", True),
            ("[7], 7", "0", True),
            ("[3, 1, 4, 1, 5], 1", "1", True),
        ],
        hints=(
            "What must you do if the list is empty?",
            "Compare each element with the target, starting at index 0.",
            "Return as soon as you find a match; only return -1 after the loop has checked every element.",
        ),
        approaches=[
            ("Scan from the left", "Check every element until a match.", "O(n)", "O(1)", True),
        ],
        notes=[
            (3, "Returning inside the loop is what guarantees the FIRST match is reported.", False),
        ],
        predictions=[
            (3, "For the first example, what is <code>i</code> the third time this line is reached?", "2: the indices go 0, 1, 2."),
        ],
        patterns=["Arrays", "Searching"],
        techniques=["Iteration", "Early Return"],
    ),
    problem(
        slug="largest-element",
        title="Largest Element in an Array",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="largest_element",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return the largest value in the non-empty list <code>nums</code>.",
            "Do not use the built-in <code>max()</code>.",
        ),
        examples=[
            ("nums = [3, 9, 2, 17, 5, 11]", "17", "17 beats every other value"),
        ],
        constraints=["1 <= len(nums) <= 10^5", "-10^9 <= nums[i] <= 10^9"],
        todo="Start with the first value as the best so far and update it whenever you see something bigger.",
        solution="""
            def largest_element(nums: list[int]) -> int:
                largest = nums[0]
                for i in range(1, len(nums)):
                    if nums[i] > largest:
                        largest = nums[i]
                return largest
        """,
        trace=1,
        cases=[
            ("[3, 9, 2, 17, 5, 11]", "17", False),
            ("[-4, -9, -1, -7]", "-1", False),
            ("[5]", "5", True),
            ("[2, 2, 2]", "2", True),
            ("[10, 1, 2, 3]", "10", True),
            ("[1, 2, 3, 100]", "100", True),
        ],
        hints=(
            "Why can you not start from 0 as the best value so far?",
            "Start from <code>nums[0]</code> and look at the rest.",
            "Update the best value only when the current element is strictly greater.",
        ),
        approaches=[
            ("Single scan", "Keep the maximum seen so far.", "O(n)", "O(1)", True),
            ("Sort and take the last", "Sort, then read the last element.", "O(n log n)", "O(n)", False),
        ],
        notes=[
            (2, "Starting from nums[0] keeps negative-only lists correct; a start of 0 would wrongly win.", False),
        ],
        predictions=[
            (6, "For [3, 9, 2, 17, 5, 11], what is <code>largest</code> when this line is reached?", "17."),
        ],
        patterns=["Arrays"],
        techniques=["Running Maximum", "Iteration"],
    ),
    problem(
        slug="second-largest-element",
        title="Second Largest Element",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="second_largest",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return the <strong>second largest distinct</strong> value in <code>nums</code>. If the list has fewer than two distinct values, return <code>-1</code>.",
            "Solve it in one pass; do not sort.",
        ),
        examples=[
            ("nums = [12, 35, 1, 10, 34, 1]", "34", "35 is largest, 34 is next"),
            ("nums = [7, 7, 7]", "-1", "only one distinct value"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "0 <= nums[i] <= 10^9"],
        todo="Track the largest and the second largest distinct values together as you scan.",
        solution="""
            def second_largest(nums: list[int]) -> int:
                largest = None
                second = None
                for x in nums:
                    if largest is None or x > largest:
                        second = largest
                        largest = x
                    elif x != largest and (second is None or x > second):
                        second = x
                return -1 if second is None else second
        """,
        trace=1,
        cases=[
            ("[12, 35, 1, 10, 34, 1]", "34", False),
            ("[7, 7, 7]", "-1", False),
            ("[]", "-1", True),
            ("[5]", "-1", True),
            ("[0, 0, 1]", "0", True),
            ("[10, 5, 10]", "5", True),
            ("[1, 2, 3, 4]", "3", True),
        ],
        hints=(
            "You need two variables, not one.",
            "When a new largest arrives, the old largest becomes the second largest.",
            "A value equal to the current largest must not become the second largest.",
        ),
        approaches=[
            ("Sort distinct values", "<code>sorted(set(nums))[-2]</code>", "O(n log n)", "O(n)", False),
            ("One pass with two trackers", "Maintain largest and second largest while scanning.", "O(n)", "O(1)", True),
        ],
        notes=[
            (6, "Shifting the old largest down is what keeps the second-largest correct when a new maximum arrives.", False),
        ],
        predictions=[
            (6, "For [12, 35, 1, 10, 34, 1], what is <code>largest</code> the second time this line is reached?", "12: this line runs when 35 arrives, and 12 is the old largest about to become second."),
        ],
        patterns=["Arrays"],
        techniques=["Running Maximum", "Sentinel Value"],
    ),
    problem(
        slug="left-rotate-array-by-one",
        title="Left Rotate Array by One",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="rotate_left_by_one",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list where every element of <code>nums</code> has moved one place to the left and the first element has wrapped around to the end.",
            "For an empty list, return an empty list.",
        ),
        examples=[
            ("nums = [1, 2, 3, 4, 5]", "[2, 3, 4, 5, 1]", "the 1 wraps to the end"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "-10^9 <= nums[i] <= 10^9"],
        todo="Shift each element one step left into a copy, then put the first element in the last slot.",
        solution="""
            def rotate_left_by_one(nums: list[int]) -> list[int]:
                n = len(nums)
                rotated = list(nums)
                for i in range(1, n):
                    rotated[i - 1] = nums[i]
                if n:
                    rotated[n - 1] = nums[0]
                return rotated
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 5]", "[2, 3, 4, 5, 1]", False),
            ("[9, 8]", "[8, 9]", False),
            ("[]", "[]", True),
            ("[4]", "[4]", True),
            ("[1, 1, 2]", "[1, 2, 1]", True),
        ],
        hints=(
            "Where does the element at index i end up?",
            "Element i moves to index i - 1, except index 0, which moves to the last index.",
            "Guard the wrap-around write so an empty list does not crash.",
        ),
        approaches=[
            ("Slicing", "<code>nums[1:] + nums[:1]</code>", "O(n)", "O(n)", False),
            ("Shift into a copy", "Move each element left, then place the first at the end.", "O(n)", "O(n)", True),
        ],
        notes=[
            (7, "The saved first element is read from the original list, so the shifting loop cannot overwrite it.", False),
        ],
        predictions=[
            (6, "For [1, 2, 3, 4, 5], what is <code>rotated</code> when this line is reached?", "[2, 3, 4, 5, 5]: the shifts are done but the last slot still holds the old 5."),
        ],
        patterns=["Arrays"],
        techniques=["Iteration", "Index Arithmetic"],
    ),
    problem(
        slug="left-rotate-array-by-k-places",
        title="Left Rotate Array by K Places",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="rotate_left_k",
        signature="(nums: list[int], k: int) -> list[int]",
        description=html(
            "Return a new list where <code>nums</code> is rotated to the left by <code>k</code> places: the first <code>k</code> elements move to the end in the same order.",
            "<code>k</code> can be larger than the length of the list. Aim for O(1) extra space beyond the copy by using the three-reversal trick.",
        ),
        examples=[
            ("nums = [1, 2, 3, 4, 5, 6, 7], k = 3", "[4, 5, 6, 7, 1, 2, 3]", "1, 2, 3 move to the end"),
            ("nums = [1, 2, 3], k = 4", "[2, 3, 1]", "4 % 3 = 1"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "0 <= k <= 10^9"],
        todo="Reduce k modulo the length. Reverse the first k, reverse the rest, then reverse the whole list.",
        solution="""
            def rotate_left_k(nums: list[int], k: int) -> list[int]:
                n = len(nums)
                if n == 0:
                    return []
                k %= n
                arr = list(nums)
                def reverse_range(lo, hi):
                    while lo < hi:
                        arr[lo], arr[hi] = arr[hi], arr[lo]
                        lo += 1
                        hi -= 1
                reverse_range(0, k - 1)
                reverse_range(k, n - 1)
                reverse_range(0, n - 1)
                return arr
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 5, 6, 7], 3", "[4, 5, 6, 7, 1, 2, 3]", False),
            ("[1, 2, 3], 4", "[2, 3, 1]", False),
            ("[], 3", "[]", True),
            ("[5], 10", "[5]", True),
            ("[1, 2, 3, 4], 0", "[1, 2, 3, 4]", True),
            ("[1, 2, 3, 4], 4", "[1, 2, 3, 4]", True),
            ("[1, 2], 5", "[2, 1]", True),
        ],
        hints=(
            "Rotating by k and by k + n gives the same result. What does that suggest doing to k first?",
            "What happens if you reverse the first k elements and the remaining n - k elements separately?",
            "After those two partial reversals, one more reversal of the whole list puts everything in place.",
        ),
        approaches=[
            ("Slicing", "<code>nums[k:] + nums[:k]</code> after reducing k.", "O(n)", "O(n)", False),
            ("Three reversals", "Reverse [0, k), reverse [k, n), reverse everything.", "O(n)", "O(1) beyond the copy", True),
        ],
        notes=[
            (5, "Without k %= n a large k would index out of range; the modulo makes every k equivalent to one in [0, n).", False),
        ],
        predictions=[
            (13, "For [1, 2, 3, 4, 5, 6, 7] and k = 3, what is <code>arr</code> the first time this line is reached?", "[3, 2, 1, 4, 5, 6, 7]: only the first 3 are reversed so far."),
        ],
        patterns=["Arrays", "Two Pointers"],
        techniques=["Reversal", "Modulo", "Swap"],
    ),
    problem(
        slug="remove-duplicates-from-sorted-array",
        title="Remove Duplicates from Sorted Array",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="remove_duplicates",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "<code>nums</code> is sorted in non-decreasing order. Return a new list with each distinct value kept once, in the same order.",
            "Use two pointers (a read position and a write position) rather than a set.",
        ),
        examples=[
            ("nums = [1, 1, 2, 2, 2, 3, 4, 4]", "[1, 2, 3, 4]", "equal values sit next to each other"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "nums is sorted in non-decreasing order"],
        todo="Write each value that differs from the last written value to the next write slot, then return the written prefix.",
        solution="""
            def remove_duplicates(nums: list[int]) -> list[int]:
                if not nums:
                    return []
                arr = list(nums)
                write = 1
                for read in range(1, len(arr)):
                    if arr[read] != arr[write - 1]:
                        arr[write] = arr[read]
                        write += 1
                return arr[:write]
        """,
        trace=1,
        cases=[
            ("[1, 1, 2, 2, 2, 3, 4, 4]", "[1, 2, 3, 4]", False),
            ("[5, 5, 5]", "[5]", False),
            ("[]", "[]", True),
            ("[3]", "[3]", True),
            ("[1, 2, 3]", "[1, 2, 3]", True),
            ("[-2, -2, 0, 0, 7]", "[-2, 0, 7]", True),
        ],
        hints=(
            "Because the list is sorted, duplicates are always adjacent.",
            "Keep a write index that marks where the next distinct value goes.",
            "Compare the value at the read index with the last value you wrote, at <code>write - 1</code>.",
        ),
        approaches=[
            ("Set then sort", "<code>sorted(set(nums))</code>", "O(n log n)", "O(n)", False),
            ("Two pointers", "Write only values that differ from the last written one.", "O(n)", "O(1) beyond the copy", True),
        ],
        notes=[
            (7, "Comparing with arr[write - 1] (the last kept value) rather than arr[read - 1] is what lets overwritten slots be ignored safely.", False),
        ],
        predictions=[
            (10, "For [1, 1, 2, 2, 2, 3, 4, 4], what is <code>write</code> when this line is reached?", "4: four distinct values were kept."),
        ],
        patterns=["Arrays", "Two Pointers"],
        techniques=["Read/Write Pointers", "Slicing"],
    ),
    problem(
        slug="union-of-two-sorted-arrays",
        title="Union of Two Sorted Arrays",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="union_sorted",
        signature="(a: list[int], b: list[int]) -> list[int]",
        description=html(
            "Both lists are sorted in non-decreasing order. Return the <strong>union</strong> of the two lists as a sorted list in which every value appears exactly once.",
            "Do it with two pointers in a single merge-like pass; do not use <code>set</code>.",
        ),
        examples=[
            ("a = [1, 2, 2, 4, 6], b = [2, 3, 4, 4, 7]", "[1, 2, 3, 4, 6, 7]", "every value appears once"),
        ],
        constraints=["0 <= len(a), len(b) <= 10^5", "both lists are sorted"],
        todo="Merge with two pointers, always taking the smaller front value, and append it only if it differs from the last appended value.",
        solution="""
            def union_sorted(a: list[int], b: list[int]) -> list[int]:
                i = j = 0
                result = []
                while i < len(a) or j < len(b):
                    if j == len(b) or (i < len(a) and a[i] <= b[j]):
                        value = a[i]
                        i += 1
                    else:
                        value = b[j]
                        j += 1
                    if not result or result[-1] != value:
                        result.append(value)
                return result
        """,
        trace=1,
        cases=[
            ("[1, 2, 2, 4, 6], [2, 3, 4, 4, 7]", "[1, 2, 3, 4, 6, 7]", False),
            ("[1, 3, 5], [2, 4, 6]", "[1, 2, 3, 4, 5, 6]", False),
            ("[], []", "[]", True),
            ("[1, 2], []", "[1, 2]", True),
            ("[], [3, 3]", "[3]", True),
            ("[1, 1, 1], [1, 1]", "[1]", True),
            ("[-5, 0], [-3, 0, 9]", "[-5, -3, 0, 9]", True),
        ],
        hints=(
            "This is the merge step of merge sort, with one extra rule.",
            "Because both lists are sorted, a duplicate can only equal the last value you added.",
            "Keep looping while either list still has elements, and take from a when b is exhausted.",
        ),
        approaches=[
            ("Set union", "<code>sorted(set(a) | set(b))</code>", "O((n + m) log(n + m))", "O(n + m)", False),
            ("Two-pointer merge", "Merge and skip values equal to the last appended one.", "O(n + m)", "O(1) beyond the output", True),
        ],
        notes=[
            (11, "Checking only result[-1] is enough: the merged stream is sorted, so equal values arrive consecutively.", False),
        ],
        predictions=[
            (11, "For the first example, what is <code>value</code> the third time this line is reached?", "2: it is the second 2 from a, which will be skipped because result[-1] is already 2."),
        ],
        patterns=["Arrays", "Two Pointers", "Merge"],
        techniques=["Two Pointers", "Deduplication"],
    ),
    problem(
        slug="intersection-of-two-sorted-arrays",
        title="Intersection of Two Sorted Arrays",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="intersection_sorted",
        signature="(a: list[int], b: list[int]) -> list[int]",
        description=html(
            "Both lists are sorted in non-decreasing order. Return the values they have in common as a sorted list. A value that appears <code>x</code> times in <code>a</code> and <code>y</code> times in <code>b</code> must appear <code>min(x, y)</code> times in the result.",
            "Use two pointers; do not use <code>set</code> or <code>Counter</code>.",
        ),
        examples=[
            ("a = [1, 2, 2, 3, 3, 4, 5, 6], b = [2, 3, 3, 5, 6, 6, 7]", "[2, 3, 3, 5, 6]", "2 once, 3 twice, 5 once, 6 once"),
        ],
        constraints=["0 <= len(a), len(b) <= 10^5", "both lists are sorted"],
        todo="Advance the pointer at the smaller value; when the values match, record it and advance both.",
        solution="""
            def intersection_sorted(a: list[int], b: list[int]) -> list[int]:
                i = j = 0
                result = []
                while i < len(a) and j < len(b):
                    if a[i] < b[j]:
                        i += 1
                    elif a[i] > b[j]:
                        j += 1
                    else:
                        result.append(a[i])
                        i += 1
                        j += 1
                return result
        """,
        trace=1,
        cases=[
            ("[1, 2, 2, 3, 3, 4, 5, 6], [2, 3, 3, 5, 6, 6, 7]", "[2, 3, 3, 5, 6]", False),
            ("[1, 2, 3], [4, 5, 6]", "[]", False),
            ("[], [1]", "[]", True),
            ("[2, 2, 2], [2, 2]", "[2, 2]", True),
            ("[1, 1, 2], [1, 2, 2]", "[1, 2]", True),
            ("[-3, 0, 5], [-3, 0, 5]", "[-3, 0, 5]", True),
        ],
        hints=(
            "If a[i] is smaller than b[j], can a[i] match anything later in b?",
            "On a match, both pointers move forward so each copy is paired only once.",
            "Stop as soon as either list is exhausted.",
        ),
        approaches=[
            ("Counter intersection", "Count both lists and take min counts.", "O(n + m)", "O(n + m)", False),
            ("Two pointers", "Walk both sorted lists together.", "O(n + m)", "O(1) beyond the output", True),
        ],
        notes=[
            (11, "Advancing both pointers pairs each element with exactly one partner, which gives the min-count behaviour.", False),
        ],
        predictions=[
            (10, "For the first example, what is appended the first time this line is reached?", "2: both lists hold a 2 at that point."),
        ],
        patterns=["Arrays", "Two Pointers", "Merge"],
        techniques=["Two Pointers"],
    ),
]
