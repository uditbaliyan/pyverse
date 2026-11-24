# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="next-greater-element",
        title="Next Greater Element",
        topic="stack",
        difficulty="easy",
        fn="next_greater_element",
        signature="(nums1: list[int], nums2: list[int]) -> list[int]",
        description=html(
            "Every value of <code>nums1</code> also appears in <code>nums2</code>, and all values in <code>nums2</code> are distinct.",
            "For each <code>x</code> in <code>nums1</code>, find <code>x</code> inside <code>nums2</code> and return the first larger value to its right there, or <code>-1</code> if there is none. Return the answers in the order of <code>nums1</code>.",
        ),
        examples=[
            (
                "nums1 = [4, 1, 2], nums2 = [1, 3, 4, 2]",
                "[-1, 3, -1]",
                "Nothing larger follows 4; 3 follows 1; nothing larger follows 2",
            ),
        ],
        constraints=[
            "1 <= len(nums1) <= len(nums2) <= 1000",
            "0 <= nums1[i], nums2[i] <= 10^4",
            "Values of nums2 are distinct",
        ],
        todo="Walk nums2 with a stack of values still waiting for a larger one; record each answer in a dictionary.",
        solution="""
            def next_greater_element(nums1: list[int], nums2: list[int]) -> list[int]:
                greater = {}
                stack = []
                for x in nums2:
                    while stack and stack[-1] < x:
                        greater[stack.pop()] = x
                    stack.append(x)
                return [greater.get(x, -1) for x in nums1]
        """,
        trace=2,
        cases=[
            ("[4, 1, 2], [1, 3, 4, 2]", "[-1, 3, -1]", False),
            ("[2, 4], [1, 2, 3, 4]", "[3, -1]", False),
            ("[1], [1]", "[-1]", True),
            ("[5, 3], [5, 4, 3, 2, 1]", "[-1, -1]", True),
            ("[1, 3, 5, 2, 4], [6, 5, 4, 3, 2, 1, 7]", "[7, 7, 7, 7, 7]", True),
        ],
        hints=(
            "Looking right from every element costs too much. Think about when an element's answer is decided.",
            "Keep a stack of values that have not yet met a larger value; a new value x resolves every smaller value on top of the stack.",
            "Store each resolved pair in a dictionary, then answer nums1 with a lookup (default -1).",
        ),
        approaches=[
            (
                "Scan right for each query",
                "Find x in nums2, then scan to its right.",
                "O(n * m)",
                "O(1)",
                False,
            ),
            (
                "Monotonic stack plus map",
                "Each value of nums2 is pushed and popped at most once.",
                "O(n + m)",
                "O(m)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Anything popped here has just met the first larger value to its right, which is exactly its answer.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For nums2 = [1, 2, 3, 4], what are stack and x the first time this line is reached?",
                "stack = [1] and x = 2, so greater[1] becomes 2.",
            ),
        ],
        patterns=["Monotonic Stack", "Hash Map"],
        techniques=["Decreasing Stack", "List Comprehension"],
    ),
    problem(
        slug="next-greater-element-ii",
        title="Next Greater Element in a Circle",
        topic="stack",
        difficulty="medium",
        fn="next_greater_circular",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "The array <code>nums</code> is circular: after the last element comes the first one again.",
            "For every element return the first strictly greater value you meet moving to the right (wrapping around if needed), or <code>-1</code> if no element is greater.",
        ),
        examples=[
            (
                "nums = [1, 2, 3, 4, 3]",
                "[2, 3, 4, -1, 4]",
                "The last 3 wraps around and finds the 4",
            ),
        ],
        constraints=["1 <= len(nums) <= 10^4", "-10^9 <= nums[i] <= 10^9"],
        todo="Loop over the array twice (indices 0 to 2n - 1), taking values modulo n, and keep a stack of indices waiting for an answer.",
        solution="""
            def next_greater_circular(nums: list[int]) -> list[int]:
                n = len(nums)
                result = [-1] * n
                stack = []
                for i in range(2 * n):
                    x = nums[i % n]
                    while stack and nums[stack[-1]] < x:
                        result[stack.pop()] = x
                    if i < n:
                        stack.append(i)
                return result
        """,
        trace=1,
        cases=[
            ("[1, 2, 1]", "[2, -1, 2]", False),
            ("[1, 2, 3, 4, 3]", "[2, 3, 4, -1, 4]", False),
            ("[5]", "[-1]", True),
            ("[3, 3, 3]", "[-1, -1, -1]", True),
            ("[5, 4, 3, 2, 1]", "[-1, 5, 5, 5, 5]", True),
        ],
        hints=(
            "A circle can be handled by pretending the array is written twice in a row.",
            "Use a stack of indices whose answers are still unknown, and process 2n positions using <code>i % n</code>.",
            "Only push indices during the first pass; the second pass only resolves them.",
        ),
        approaches=[
            (
                "Scan the circle for each element",
                "Walk up to n steps from every index.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Stack over a doubled pass",
                "Each index is pushed once and popped at most once.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                9,
                "Only indices from the first lap are pushed: the second lap exists to resolve them, not to create new waiters.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For [1, 2, 1], what is stack the second time this line is reached?",
                "[1, 2]: index 2 (value 1) is about to receive 2 from the wrapped-around element.",
            ),
        ],
        patterns=["Monotonic Stack"],
        techniques=["Index Stack", "Modulo Indexing"],
    ),
    problem(
        slug="asteroid-collision",
        title="Asteroid Collision",
        topic="stack",
        difficulty="medium",
        fn="asteroid_collision",
        signature="(asteroids: list[int]) -> list[int]",
        description=html(
            "Asteroids move along a line. The absolute value of <code>asteroids[i]</code> is its size, a positive sign means it moves right and a negative sign means it moves left. All move at the same speed.",
            "When two meet, the smaller one explodes; if they have the same size, both explode. Asteroids moving in the same direction never meet. Return the asteroids that remain, in their original order.",
        ),
        examples=[
            (
                "asteroids = [10, 2, -5]",
                "[10]",
                "-5 destroys the 2, then loses to the 10",
            ),
        ],
        constraints=["2 <= len(asteroids) <= 10^4", "asteroids[i] != 0", "-1000 <= asteroids[i] <= 1000"],
        todo="Keep a stack of survivors; a left-moving asteroid fights the right-moving ones on top of the stack.",
        solution="""
            def asteroid_collision(asteroids: list[int]) -> list[int]:
                stack = []
                for a in asteroids:
                    alive = True
                    while alive and a < 0 and stack and stack[-1] > 0:
                        if stack[-1] < -a:
                            stack.pop()
                        elif stack[-1] == -a:
                            stack.pop()
                            alive = False
                        else:
                            alive = False
                    if alive:
                        stack.append(a)
                return stack
        """,
        trace=3,
        cases=[
            ("[5, 10, -5]", "[5, 10]", False),
            ("[8, -8]", "[]", False),
            ("[10, 2, -5]", "[10]", False),
            ("[-2, -1, 1, 2]", "[-2, -1, 1, 2]", True),
            ("[1, -2, -2, -2]", "[-2, -2, -2]", True),
            ("[3, -5, 4, -1, -2]", "[-5, 4]", True),
        ],
        hints=(
            "When can a collision happen at all? Think about the signs of two neighbouring survivors.",
            "A stack of survivors works: only a left-moving newcomer facing a right-moving top can collide.",
            "Compare sizes in a loop: pop smaller tops, destroy both on a tie, and push the newcomer only if it survives.",
        ),
        approaches=[
            (
                "Repeat collisions until stable",
                "Rescan the list and remove colliding pairs until nothing changes.",
                "O(n^2)",
                "O(n)",
                False,
            ),
            (
                "Stack of survivors",
                "Each asteroid is pushed once and popped at most once.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "A tie removes both asteroids, so the newcomer is marked dead and the top is popped.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For [10, 2, -5], what is stack the second time this line is reached?",
                "[10], because the 2 was destroyed by the -5.",
            ),
        ],
        patterns=["Stack", "Simulation"],
        techniques=["Flag Variable", "Collision Loop"],
    ),
    problem(
        slug="sum-of-subarray-minimums",
        title="Sum of Subarray Minimums",
        topic="stack",
        difficulty="medium",
        fn="sum_subarray_mins",
        signature="(arr: list[int]) -> int",
        description=html(
            "For every contiguous subarray of <code>arr</code> take its minimum value, then add all those minimums together.",
            "Return the sum modulo <code>10^9 + 7</code>.",
        ),
        examples=[
            (
                "arr = [4, 2, 3, 1]",
                "19",
                "Minimums: 4, 2, 3, 1, 2, 2, 1, 2, 1, 1",
            ),
        ],
        constraints=["1 <= len(arr) <= 3 * 10^4", "1 <= arr[i] <= 3 * 10^4"],
        todo="For each element count the subarrays where it is the minimum: (distance to the previous smaller) times (distance to the next smaller or equal).",
        solution="""
            def sum_subarray_mins(arr: list[int]) -> int:
                stack = []
                total = 0
                for i in range(len(arr) + 1):
                    current = arr[i] if i < len(arr) else -1
                    while stack and arr[stack[-1]] >= current:
                        mid = stack.pop()
                        prev = stack[-1] if stack else -1
                        total += arr[mid] * (mid - prev) * (i - mid)
                    stack.append(i)
                return total % (10**9 + 7)
        """,
        trace=1,
        cases=[
            ("[4, 2, 3, 1]", "19", False),
            ("[1, 2, 3]", "10", False),
            ("[11, 81, 94, 43, 3]", "444", False),
            ("[5]", "5", True),
            ("[2, 2, 2]", "12", True),
            ("[30000] * 1000", "14999895", True),
        ],
        hints=(
            "Instead of listing subarrays, ask for each element: in how many subarrays is it the smallest?",
            "If the previous smaller element is at index p and the next one at index q, the element at m is the minimum of (m - p) * (q - m) subarrays.",
            "A monotonic stack finds p and q in one pass. Break ties by letting the left side use strictly smaller and the right side smaller-or-equal, so no subarray is counted twice.",
        ),
        approaches=[
            (
                "Enumerate subarrays",
                "Track the running minimum for every start.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Contribution of each element",
                "A stack gives the left and right reach of every element.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                9,
                "arr[mid] is the minimum of exactly (mid - prev) * (i - mid) subarrays: any start after prev and any end before i.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For [4, 2, 3, 1], what is total the third time this line is reached?",
                "7 (4 from the element 4, then 3 from the element 3).",
            ),
        ],
        patterns=["Monotonic Stack", "Math"],
        techniques=["Contribution Technique", "Sentinel Value"],
    ),
    problem(
        slug="sum-of-subarray-ranges",
        title="Sum of Subarray Ranges",
        topic="stack",
        difficulty="medium",
        fn="subarray_ranges",
        signature="(nums: list[int]) -> int",
        description=html(
            "The range of a subarray is its largest element minus its smallest element.",
            "Return the sum of the ranges of all contiguous subarrays of <code>nums</code>.",
        ),
        examples=[
            (
                "nums = [2, 1, 3]",
                "5",
                "Ranges: 0, 0, 0, 1 ([2,1]), 2 ([1,3]), 2 ([2,1,3])",
            ),
        ],
        constraints=["1 <= len(nums) <= 1000", "-10^9 <= nums[i] <= 10^9"],
        todo="The answer is (sum of subarray maximums) - (sum of subarray minimums); compute both with monotonic stacks.",
        solution="""
            def subarray_ranges(nums: list[int]) -> int:
                n = len(nums)
                total = 0
                max_stack = []
                min_stack = []
                for i in range(n + 1):
                    while max_stack and (i == n or nums[max_stack[-1]] <= nums[i]):
                        mid = max_stack.pop()
                        prev = max_stack[-1] if max_stack else -1
                        total += nums[mid] * (mid - prev) * (i - mid)
                    while min_stack and (i == n or nums[min_stack[-1]] >= nums[i]):
                        mid = min_stack.pop()
                        prev = min_stack[-1] if min_stack else -1
                        total -= nums[mid] * (mid - prev) * (i - mid)
                    max_stack.append(i)
                    min_stack.append(i)
                return total
        """,
        trace=2,
        cases=[
            ("[1, 2, 3]", "4", False),
            ("[2, 1, 3]", "5", False),
            ("[4, -2, -3, 4, 1]", "59", False),
            ("[7]", "0", True),
            ("[5, 5, 5]", "0", True),
            ("[3, 1, 4, 1, 5]", "33", True),
        ],
        hints=(
            "Sum of (max - min) over all subarrays splits into a sum of maximums and a sum of minimums.",
            "Each element is the maximum of some number of subarrays and the minimum of some other number; a monotonic stack tells you both counts.",
            "Run one decreasing stack for maximums (add the contribution) and one increasing stack for minimums (subtract it), with strict versus non-strict comparisons chosen so ties are counted once.",
        ),
        approaches=[
            (
                "Enumerate subarrays",
                "Track the running max and min for every start.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Two monotonic stacks",
                "Sum of maximums minus sum of minimums, each in linear time.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "i == n acts as a sentinel that empties both stacks at the end, so every element's contribution is added.",
                False,
            ),
        ],
        predictions=[
            (
                14,
                "For [2, 1, 3], what is total the third time this line is reached?",
                "9 (the maximum contributions total 12, and 3 has been subtracted for the element 3).",
            ),
        ],
        patterns=["Monotonic Stack", "Math"],
        techniques=["Contribution Technique", "Sentinel Value"],
    ),
    problem(
        slug="remove-k-digits",
        title="Remove K Digits",
        topic="stack",
        difficulty="medium",
        fn="remove_k_digits",
        signature="(num: str, k: int) -> str",
        description=html(
            "<code>num</code> is a non-negative integer written as a string. Delete exactly <code>k</code> of its digits so that the number that remains is as small as possible.",
            "Return it without leading zeros; if nothing is left, return <code>\"0\"</code>.",
        ),
        examples=[
            (
                'num = "1432219", k = 3',
                '"1219"',
                "Removing 4, 3 and one 2 gives the smallest result",
            ),
        ],
        constraints=["1 <= k <= len(num) <= 10^5", "num has digits only"],
        todo="Keep a stack of digits; while the top is bigger than the incoming digit and removals remain, pop it.",
        solution="""
            def remove_k_digits(num: str, k: int) -> str:
                stack = []
                for digit in num:
                    while k > 0 and stack and stack[-1] > digit:
                        stack.pop()
                        k -= 1
                    stack.append(digit)
                if k > 0:
                    stack = stack[:-k]
                return "".join(stack).lstrip("0") or "0"
        """,
        trace=1,
        cases=[
            ('"1432219", 3', '"1219"', False),
            ('"10200", 1', '"200"', False),
            ('"10", 2', '"0"', False),
            ('"112", 1', '"11"', True),
            ('"9", 1', '"0"', True),
            ('"100", 1', '"0"', True),
            ('"1234567890", 9', '"0"', True),
        ],
        hints=(
            "Compare two digits that are next to each other: when does removing the left one make the number smaller?",
            "Whenever a digit is greater than the one after it, deleting it helps. A stack lets you look back at earlier digits as well.",
            "If removals are left over after the loop the digits are non-decreasing, so drop them from the end. Finally strip leading zeros.",
        ),
        approaches=[
            (
                "Try every choice",
                "Generate all ways to delete k digits and take the minimum.",
                "O(C(n, k) * n)",
                "O(n)",
                False,
            ),
            (
                "Greedy with a stack",
                "Remove a peak digit as soon as a smaller digit follows.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "A non-decreasing stack with removals left over means the largest digits are at the end, so cutting the tail is optimal.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                'For num = "1432219" and k = 3, what is k the fifth time this line is reached (digit "2", the second one)?',
                "1: the digits 4 and 3 were already removed.",
            ),
        ],
        patterns=["Monotonic Stack", "Greedy"],
        techniques=["Increasing Stack", "String Join"],
    ),
    problem(
        slug="next-smaller-element",
        title="Next Smaller Element",
        topic="stack",
        difficulty="medium",
        fn="next_smaller_element",
        signature="(arr: list[int]) -> list[int]",
        description=html(
            "For each element of <code>arr</code> find the first element to its right that is strictly smaller, and return those values in order. Use <code>-1</code> when no smaller element exists on the right.",
        ),
        examples=[
            (
                "arr = [4, 8, 5, 2, 25]",
                "[2, 5, 2, -1, -1]",
                "2 is the first smaller value after 4; after 8 it is 5; after 5 it is 2",
            ),
        ],
        constraints=["1 <= len(arr) <= 10^5", "1 <= arr[i] <= 10^9"],
        todo="Scan from right to left, popping stack values that are not smaller than the current one.",
        solution="""
            def next_smaller_element(arr: list[int]) -> list[int]:
                result = [-1] * len(arr)
                stack = []
                for i in range(len(arr) - 1, -1, -1):
                    while stack and stack[-1] >= arr[i]:
                        stack.pop()
                    if stack:
                        result[i] = stack[-1]
                    stack.append(arr[i])
                return result
        """,
        trace=1,
        cases=[
            ("[4, 8, 5, 2, 25]", "[2, 5, 2, -1, -1]", False),
            ("[5, 6, 2, 3, 1, 7]", "[2, 2, 1, 1, -1, -1]", False),
            ("[1, 2, 3]", "[-1, -1, -1]", False),
            ("[3, 3, 3]", "[-1, -1, -1]", True),
            ("[9]", "[-1]", True),
            ("[3, 2, 1]", "[2, 1, -1]", True),
        ],
        hints=(
            "Scanning right from every element repeats a lot of work.",
            "Go from right to left and keep a stack of candidates; a candidate that is not smaller than arr[i] can never be the answer for anything further left.",
            "Pop those useless values, read the top as the answer (if any), then push the current value.",
        ),
        approaches=[
            (
                "Scan right for each element",
                "For every index walk right until a smaller value is found.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Right-to-left stack",
                "Each value is pushed and popped at most once.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "A value on the stack that is greater than or equal to arr[i] is hidden behind arr[i] for every element further left, so it can be discarded.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For [4, 8, 5, 2, 25], what is stack the first time this line is reached?",
                "[2]: the next smaller value after 5 is 2.",
            ),
        ],
        patterns=["Monotonic Stack"],
        techniques=["Increasing Stack", "Reverse Iteration"],
    ),
]
