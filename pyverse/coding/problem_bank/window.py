# ruff: noqa: E501, ISC004
"""Sliding Window: one pass with a moving range."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="best-time-to-buy-and-sell-stock",
        title="Best Time to Buy and Sell Stock",
        topic="sliding-window",
        difficulty="easy",
        fn="max_profit",
        signature="(prices: list[int]) -> int",
        description=html(
            "<code>prices[i]</code> is the price of a stock on day <code>i</code>. "
            "You may buy on one day and sell on a <strong>later</strong> day.",
            "Return the maximum profit you can make. If no profit is possible, return <code>0</code>.",
        ),
        examples=[
            ("prices = [7,1,5,3,6,4]", "5", "Buy at 1, sell at 6."),
            ("prices = [7,6,4,3,1]", "0", "Prices only fall, so do not trade."),
        ],
        constraints=["1 <= prices.length <= 10^5", "0 <= prices[i] <= 10^4"],
        todo="Return the best profit from one buy followed by one later sell.",
        solution="""
            def max_profit(prices: list[int]) -> int:
                lowest = prices[0]
                best = 0
                for price in prices:
                    if price < lowest:
                        lowest = price
                    elif price - lowest > best:
                        best = price - lowest
                return best
        """,
        cases=[
            ("[7, 1, 5, 3, 6, 4]", "5", False),
            ("[7, 6, 4, 3, 1]", "0", False),
            ("[2, 4, 1]", "2", True),
            ("[1]", "0", True),
            ("[3, 3, 3]", "0", True),
            ("[2, 1, 2, 0, 1]", "1", True),
        ],
        hints=(
            "For any selling day, which buying day would be best?",
            "The best day to buy before day <code>i</code> is the cheapest day seen so far. "
            "Track it as you scan.",
            "At each price: if it is a new low, remember it; otherwise see whether "
            "<code>price - lowest</code> beats the best profit so far.",
        ),
        approaches=[
            (
                "Try every pair of days",
                "Two nested loops over buy and sell days.",
                "O(n²)",
                "O(1)",
                False,
            ),
            (
                "Track the lowest price so far",
                "One pass keeps the cheapest buy price and the best profit.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "A new low is the best day to have bought so far. Nothing earlier can beat it.",
                True,
            ),
        ],
        predictions=[
            (
                9,
                "For [7, 1, 5, 3, 6, 4], what does best hold when the function returns?",
                "5: buy at 1, sell at 6.",
            ),
        ],
        patterns=["Sliding Window", "Greedy"],
        techniques=["Accumulator"],
    ),
    problem(
        slug="maximum-sum-subarray-of-size-k",
        title="Maximum Sum Subarray of Size K",
        topic="sliding-window",
        difficulty="easy",
        fn="max_sum_subarray",
        signature="(nums: list[int], k: int) -> int",
        description=html(
            "Given an array <code>nums</code> and a window size <code>k</code>, return the "
            "largest sum of any <code>k</code> consecutive elements.",
        ),
        examples=[
            ("nums = [2,1,5,1,3,2], k = 3", "9", "5 + 1 + 3"),
            ("nums = [1,4,2,10,2,3,1,0,20], k = 4", "24", "3 + 1 + 0 + 20"),
        ],
        constraints=["1 <= k <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
        todo="Return the largest sum of k consecutive elements.",
        solution="""
            def max_sum_subarray(nums: list[int], k: int) -> int:
                window = sum(nums[:k])
                best = window
                for end in range(k, len(nums)):
                    window += nums[end] - nums[end - k]
                    best = max(best, window)
                return best
        """,
        cases=[
            ("[2, 1, 5, 1, 3, 2], 3", "9", False),
            ("[1, 4, 2, 10, 2, 3, 1, 0, 20], 4", "24", False),
            ("[5], 1", "5", True),
            ("[-1, -2, -3, -4], 2", "-3", True),
            ("[1, 2, 3], 3", "6", True),
        ],
        hints=(
            "Adding up k numbers for every start position repeats a lot of work.",
            "When the window slides one step, only two numbers change: one enters on the right, "
            "one leaves on the left.",
            "Start with <code>sum(nums[:k])</code>, then for each new <code>end</code> add "
            "<code>nums[end]</code> and subtract <code>nums[end - k]</code>.",
        ),
        approaches=[
            (
                "Re-sum every window",
                "Add up k numbers for every start index.",
                "O(n · k)",
                "O(1)",
                False,
            ),
            (
                "Sliding window",
                "Update the running sum by adding the new element and removing the oldest.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Slide by one: add the number entering on the right, drop the one leaving on "
                "the left. No need to re-add all k numbers.",
                True,
            ),
        ],
        predictions=[
            (
                3,
                "For [2, 1, 5, 1, 3, 2] with k = 3, what is window before the loop starts?",
                "8: 2 + 1 + 5.",
            ),
        ],
        patterns=["Sliding Window"],
        techniques=["Slicing", "Builtins"],
    ),
    problem(
        slug="longest-substring-without-repeating-characters",
        title="Longest Substring Without Repeating Characters",
        topic="sliding-window",
        difficulty="medium",
        fn="length_of_longest_substring",
        signature="(s: str) -> int",
        description=html(
            "Given a string <code>s</code>, return the length of the longest "
            "<strong>substring</strong> (a contiguous part of <code>s</code>) "
            "that contains no repeated character.",
        ),
        examples=[
            ('s = "abcabcbb"', "3", 'The answer is "abc".'),
            ('s = "bbbbb"', "1", 'The answer is "b".'),
        ],
        constraints=[
            "0 <= len(s) <= 5 * 10^4",
            "s may contain letters, digits, symbols and spaces.",
        ],
        todo="Return the length of the longest substring with all-different characters.",
        solution="""
            def length_of_longest_substring(s: str) -> int:
                last_seen = {}
                start = 0
                best = 0
                for end, char in enumerate(s):
                    if char in last_seen and last_seen[char] >= start:
                        start = last_seen[char] + 1
                    last_seen[char] = end
                    best = max(best, end - start + 1)
                return best
        """,
        cases=[
            ('"abcabcbb"', "3", False),
            ('"bbbbb"', "1", False),
            ('""', "0", True),
            ('"pwwkew"', "3", True),
            ('"abba"', "2", True),
            ('"dvdf"', "3", True),
        ],
        hints=(
            "Checking every substring is cubic. Think of a window that always holds "
            "distinct characters.",
            "Grow the window by moving <code>end</code>. When a character repeats inside the window, "
            "move <code>start</code> forward.",
            "Remember each character's last index. If it is inside the window, "
            "jump <code>start</code> to just after it.",
        ),
        approaches=[
            (
                "Check every substring",
                "Test each substring for duplicates.",
                "O(n³)",
                "O(n)",
                False,
            ),
            (
                "Window with last-seen indexes",
                "One pass; a dict of last positions lets the left edge jump instead of creep.",
                "O(n)",
                "O(min(n, alphabet))",
                True,
            ),
        ],
        notes=[
            (
                6,
                "last_seen[char] >= start matters: a repeat to the left of the window "
                "no longer counts.",
                True,
            ),
            (
                7,
                "Jump the window's left edge just past the earlier copy instead of shrinking "
                "one step at a time.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "In 'abcabcbb', what does start become when the second 'a' (index 3) arrives?",
                "1: one past the first 'a' at index 0.",
            ),
        ],
        patterns=["Sliding Window", "Hash Map"],
        techniques=["Enumeration", "Dict Lookup"],
    ),
]
