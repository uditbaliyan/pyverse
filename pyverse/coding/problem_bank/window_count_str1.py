# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="minimum-window-subsequence",
        title="Minimum Window Subsequence",
        topic="sliding-window",
        difficulty="hard",
        fn="min_window_subsequence",
        signature="(s1: str, s2: str) -> str",
        description=html(
            "Return the shortest contiguous substring of <code>s1</code> that has <code>s2</code> as a subsequence (the letters of <code>s2</code> appear in order, not necessarily next to each other).",
            "If several substrings tie for shortest, return the one that starts first. If there is none, return the empty string.",
        ),
        examples=[
            (
                's1 = "axbxcxb", s2 = "abc"',
                '"axbxc"',
                "a, b, c occur in order inside indices 0 to 4",
            ),
        ],
        constraints=["1 <= len(s1) <= 2000", "1 <= len(s2) <= 100", "Lowercase letters only"],
        todo="Scan forward to find where s2 is first completed, then scan backward from there to find the tightest start.",
        solution="""
            def min_window_subsequence(s1: str, s2: str) -> str:
                best_start, best_len = 0, len(s1) + 1
                i = 0
                while i < len(s1):
                    j = 0
                    while i < len(s1):
                        if s1[i] == s2[j]:
                            j += 1
                            if j == len(s2):
                                break
                        i += 1
                    if i == len(s1):
                        break
                    end = i
                    j = len(s2) - 1
                    while j >= 0:
                        if s1[i] == s2[j]:
                            j -= 1
                        i -= 1
                    i += 1
                    if end - i + 1 < best_len:
                        best_start, best_len = i, end - i + 1
                    i += 1
                return "" if best_len > len(s1) else s1[best_start:best_start + best_len]
        """,
        trace=2,
        cases=[
            ('"abcdebdde", "bde"', '"bcde"', False),
            ('"abxbc", "abc"', '"abxbc"', False),
            ('"axbxcxb", "abc"', '"axbxc"', True),
            ('"abc", "d"', '""', True),
            ('"abc", "abc"', '"abc"', True),
            ('"aab", "ab"', '"ab"', True),
            ('"cnhczmccqouqadqtmjjzl", "mm"', '"mccqouqadqtm"', True),
        ],
        hints=(
            "If you know where a match of s2 ends, how could you find the best start for that particular end?",
            "Scan forward matching s2 letter by letter until all are matched; that index is the end. Then walk backward matching s2 from its last letter to find the latest possible start.",
            "Record the window, then restart the forward scan from one past that start, so every candidate end is considered.",
        ),
        approaches=[
            (
                "Check every start",
                "For each start, greedily match s2 and keep the shortest.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Forward then backward scan",
                "Each forward match is tightened with one backward pass, then scanning resumes just after the new start.",
                "O(n * m)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                16,
                "Walking backward from the end and matching s2 from its last letter lands on the latest valid start, which is the shortest window for this end.",
                False,
            ),
        ],
        predictions=[
            (
                15,
                'For s1 = "abxbc" and s2 = "abc", what is end the first time this line is reached?',
                "4, the index of the 'c' that completes a, b, c.",
            ),
        ],
        patterns=["Sliding Window", "Two Pointers"],
        techniques=["Forward Backward Scan", "Tuple Unpacking"],
    ),
    problem(
        slug="number-of-substrings-containing-all-three-characters",
        title="Substrings Containing a, b and c",
        topic="sliding-window",
        difficulty="medium",
        fn="count_abc_substrings",
        signature="(s: str) -> int",
        description=html(
            "The string <code>s</code> contains only the letters <code>a</code>, <code>b</code> and <code>c</code>.",
            "Return how many substrings contain at least one of each of the three letters.",
        ),
        examples=[
            (
                's = "abcabc"',
                "10",
                "Substrings ending at index 2, 3, 4, 5 contribute 1, 2, 3, 4",
            ),
        ],
        constraints=["3 <= len(s) <= 5 * 10^4", "s uses only a, b, c"],
        todo="For every end index, the valid starts are all positions up to the earliest of the last a, last b and last c.",
        solution="""
            def count_abc_substrings(s: str) -> int:
                last = {"a": -1, "b": -1, "c": -1}
                total = 0
                for i, ch in enumerate(s):
                    last[ch] = i
                    total += min(last.values()) + 1
                return total
        """,
        trace=1,
        cases=[
            ('"abcabc"', "10", False),
            ('"aaacb"', "3", False),
            ('"abc"', "1", False),
            ('"aaa"', "0", True),
            ('"ccbbaa"', "4", True),
            ('"abababc"', "5", True),
        ],
        hints=(
            "Fix the right end of the substring. Which starting positions make it valid?",
            "A start works if it is at or before the most recent a, the most recent b and the most recent c.",
            "The number of valid starts for this end is the minimum of the three last positions plus one (0 if any letter has not appeared).",
        ),
        approaches=[
            (
                "Check every substring",
                "Test each substring for the three letters.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Last seen positions",
                "Each end index adds min(last positions) + 1 valid substrings.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "If a letter has not appeared its last index is -1, so the min is -1 and the contribution is 0.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                'For s = "abcabc", what is last the fourth time this line is reached?',
                "{'a': 3, 'b': 1, 'c': 2}: the minimum is 1, so two substrings end here.",
            ),
        ],
        patterns=["Sliding Window", "Counting"],
        techniques=["Last Seen Index", "Accumulator"],
    ),
    problem(
        slug="binary-subarrays-with-sum",
        title="Binary Subarrays With Sum",
        topic="sliding-window",
        difficulty="medium",
        fn="num_subarrays_with_sum",
        signature="(nums: list[int], goal: int) -> int",
        description=html(
            "<code>nums</code> contains only 0s and 1s. Return the number of non-empty contiguous subarrays whose elements add up to exactly <code>goal</code>.",
        ),
        examples=[
            (
                "nums = [1, 0, 1, 0, 1], goal = 2",
                "4",
                "[1,0,1], [1,0,1,0], [0,1,0,1] and [1,0,1] (the last three elements)",
            ),
        ],
        constraints=["1 <= len(nums) <= 3 * 10^4", "nums[i] is 0 or 1", "0 <= goal <= len(nums)"],
        todo="Maintain two windows per right end: one for sums <= goal and one for sums < goal; their left edges bracket the matches.",
        solution="""
            def num_subarrays_with_sum(nums: list[int], goal: int) -> int:
                count = 0
                lo = 0
                hi = 0
                sum_lo = 0
                sum_hi = 0
                for right, x in enumerate(nums):
                    sum_lo += x
                    sum_hi += x
                    while lo <= right and sum_lo > goal:
                        sum_lo -= nums[lo]
                        lo += 1
                    while hi <= right and sum_hi >= goal:
                        sum_hi -= nums[hi]
                        hi += 1
                    count += hi - lo
                return count
        """,
        trace=1,
        cases=[
            ("[1, 0, 1, 0, 1], 2", "4", False),
            ("[0, 0, 0, 0, 0], 0", "15", False),
            ("[1, 1, 1], 2", "2", False),
            ("[0, 1, 0], 0", "2", True),
            ("[1], 1", "1", True),
            ("[1, 0, 0, 1], 1", "6", True),
        ],
        hints=(
            "Because all values are non-negative, sliding the left edge right never increases the sum. What does that tell you about the starts that give an exact sum?",
            "For a fixed right end, the starts with sum exactly goal form one contiguous block: from the first start whose sum is at most goal up to (but not including) the first start whose sum is below goal.",
            "Keep two left edges with their own running sums, and add the size of that block for every right end.",
        ),
        approaches=[
            (
                "Check every subarray",
                "Sum each pair (start, end) using a running sum.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Two left edges",
                "Equivalent to counting subarrays with sum at most goal minus those at most goal - 1, in a single pass.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                13,
                "hi stops at the first start whose sum is below goal, so hi - lo counts the starts whose sum is exactly goal.",
                False,
            ),
        ],
        predictions=[
            (
                16,
                "For [1, 0, 1, 0, 1] and goal = 2, what are lo and hi the third time this line is reached?",
                "lo = 0 and hi = 1: the starts in [0, 1) give a sum of exactly 2.",
            ),
        ],
        patterns=["Sliding Window", "Counting"],
        techniques=["Two Windows", "Accumulator"],
    ),
    problem(
        slug="count-number-of-nice-subarrays",
        title="Count Number of Nice Subarrays",
        topic="sliding-window",
        difficulty="medium",
        fn="number_of_nice_subarrays",
        signature="(nums: list[int], k: int) -> int",
        description=html(
            "A subarray is nice if it contains exactly <code>k</code> odd numbers.",
            "Return how many nice subarrays <code>nums</code> has.",
        ),
        examples=[
            (
                "nums = [1, 2, 1, 2, 1], k = 2",
                "4",
                "[1,2,1], [1,2,1,2], [2,1,2,1] and [1,2,1]",
            ),
        ],
        constraints=["1 <= len(nums) <= 5 * 10^4", "1 <= nums[i] <= 10^5", "1 <= k <= len(nums)"],
        todo="Track how many odd numbers you have seen so far, and how often each running odd-count has occurred.",
        solution="""
            def number_of_nice_subarrays(nums: list[int], k: int) -> int:
                seen = {0: 1}
                odds = 0
                count = 0
                for x in nums:
                    odds += x % 2
                    count += seen.get(odds - k, 0)
                    seen[odds] = seen.get(odds, 0) + 1
                return count
        """,
        trace=1,
        cases=[
            ("[1, 1, 2, 1, 1], 3", "2", False),
            ("[2, 4, 6], 1", "0", False),
            ("[1, 2, 1, 2, 1], 2", "4", False),
            ("[2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2", "16", True),
            ("[1], 1", "1", True),
            ("[2, 2, 1], 1", "3", True),
        ],
        hints=(
            "Replace every number by x % 2. The task becomes counting subarrays with sum exactly k.",
            "A subarray from i to j has k odd numbers when (odds up to j) - (odds before i) equals k.",
            "Keep a dictionary of how many times each odd-count has appeared as a prefix; for each element look up the count of <code>odds - k</code>.",
        ),
        approaches=[
            (
                "Check every subarray",
                "Count the odd numbers in each pair (start, end).",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Prefix odd-counts",
                "Look up how many earlier prefixes have exactly k fewer odd numbers.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Every earlier prefix with odd-count (odds - k) starts exactly one nice subarray ending here.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [1, 1, 2, 1, 1] and k = 3, what are odds and seen the fourth time this line is reached?",
                "odds = 3 and seen = {0: 1, 1: 1, 2: 2}, so the lookup of 0 adds 1.",
            ),
        ],
        patterns=["Prefix Sum", "Hash Map"],
        techniques=["Dictionary Counting", "Accumulator"],
    ),
    problem(
        slug="subarrays-with-k-different-integers",
        title="Subarrays With K Different Integers",
        topic="sliding-window",
        difficulty="hard",
        fn="subarrays_with_k_distinct",
        signature="(nums: list[int], k: int) -> int",
        description=html(
            "Return the number of contiguous subarrays of <code>nums</code> that contain exactly <code>k</code> different integers.",
        ),
        examples=[
            (
                "nums = [1, 2, 1, 3], k = 2",
                "4",
                "[1,2], [2,1], [1,2,1] and [1,3]",
            ),
        ],
        constraints=["1 <= len(nums) <= 2 * 10^4", "1 <= nums[i] <= len(nums)", "1 <= k <= len(nums)"],
        todo="For each right end, find the earliest start with at most k distinct values and the earliest start with at most k - 1; the gap is the answer for that end.",
        solution="""
            def subarrays_with_k_distinct(nums: list[int], k: int) -> int:
                count = 0
                lo = 0
                hi = 0
                freq_lo = {}
                freq_hi = {}
                for right, x in enumerate(nums):
                    freq_lo[x] = freq_lo.get(x, 0) + 1
                    freq_hi[x] = freq_hi.get(x, 0) + 1
                    while len(freq_lo) > k:
                        freq_lo[nums[lo]] -= 1
                        if freq_lo[nums[lo]] == 0:
                            del freq_lo[nums[lo]]
                        lo += 1
                    while len(freq_hi) >= k:
                        freq_hi[nums[hi]] -= 1
                        if freq_hi[nums[hi]] == 0:
                            del freq_hi[nums[hi]]
                        hi += 1
                    count += hi - lo
                return count
        """,
        trace=1,
        cases=[
            ("[1, 2, 1, 3], 2", "4", False),
            ("[1, 2, 1, 2, 3], 2", "7", False),
            ("[1, 1, 1], 1", "6", False),
            ("[1, 2, 1, 3, 4], 3", "3", True),
            ("[1, 2], 1", "2", True),
            ("[1, 2, 3], 4", "0", True),
            ("[2, 1, 1, 1, 2], 1", "8", True),
        ],
        hints=(
            "Counting subarrays with exactly k distinct values is hard directly. Which easier counts could you subtract?",
            "'At most k distinct' is easy with a window. Exactly k equals at most k minus at most k - 1.",
            "Run both windows together. For each right end, lo is the first start with at most k distinct values and hi the first start with at most k - 1; add hi - lo.",
        ),
        approaches=[
            (
                "Check every subarray",
                "Count distinct values for each pair (start, end).",
                "O(n^2)",
                "O(n)",
                False,
            ),
            (
                "At most k minus at most k - 1",
                "Two coordinated windows in a single pass.",
                "O(n)",
                "O(k)",
                True,
            ),
        ],
        notes=[
            (
                20,
                "Starts in [lo, hi) have at most k distinct values but not at most k - 1, so they have exactly k.",
                False,
            ),
        ],
        predictions=[
            (
                20,
                "For [1, 2, 1, 3] and k = 2, what are lo and hi the third time this line is reached?",
                "lo = 0 and hi = 2: starts 0 and 1 give exactly two distinct values.",
            ),
        ],
        patterns=["Sliding Window", "Hash Map"],
        techniques=["Two Windows", "Dictionary Counting"],
    ),
]
