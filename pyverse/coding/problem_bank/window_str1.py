# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="maximum-points-you-can-obtain-from-cards",
        title="Maximum Points from Cards",
        topic="sliding-window",
        difficulty="medium",
        fn="max_card_points",
        signature="(card_points: list[int], k: int) -> int",
        description=html(
            "A row of cards is laid out, and card <code>i</code> is worth <code>card_points[i]</code> points. In exactly <code>k</code> moves you take one card per move, always from the left end or the right end of what remains.",
            "Return the largest total score you can collect.",
        ),
        examples=[
            (
                "card_points = [1, 2, 3, 4, 5, 6, 1], k = 3",
                "12",
                "Take the three rightmost cards: 5 + 6 + 1",
            ),
        ],
        constraints=["1 <= k <= len(card_points) <= 10^5", "1 <= card_points[i] <= 10^4"],
        todo="Start with the k leftmost cards, then swap them one at a time for cards from the right end.",
        solution="""
            def max_card_points(card_points: list[int], k: int) -> int:
                window = sum(card_points[:k])
                best = window
                n = len(card_points)
                for i in range(1, k + 1):
                    window += card_points[n - i] - card_points[k - i]
                    best = max(best, window)
                return best
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 5, 6, 1], 3", "12", False),
            ("[2, 2, 2], 2", "4", False),
            ("[100, 40, 17, 9, 73, 75], 3", "248", False),
            ("[9, 7, 7, 9, 7, 7, 9], 7", "55", True),
            ("[1, 1000, 1], 1", "1", True),
            ("[5, 4], 2", "9", True),
        ],
        hints=(
            "Whatever you take, the cards you take from the left form a prefix and the ones from the right form a suffix. How many combinations are there?",
            "Begin with all k cards taken from the left. Moving to 'one fewer from the left, one more from the right' changes the total by two cards only.",
            "Loop i from 1 to k: add the i-th card from the right end and subtract the card that leaves the left group. Track the best total.",
        ),
        approaches=[
            (
                "Recompute every split",
                "For each split, add the left prefix and the right suffix from scratch.",
                "O(k^2)",
                "O(1)",
                False,
            ),
            (
                "Slide the split point",
                "Keep a running total of the k chosen cards and update it with one addition and one subtraction per step.",
                "O(k)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "Each pass moves one card from the left group to the right group, so the window always holds exactly k cards.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For [1, 2, 3, 4, 5, 6, 1] and k = 3, what is window the second time this line is reached?",
                "4 (the starting 1 + 2 + 3 = 6, then 6 + 1 - 3 after the first swap).",
            ),
        ],
        patterns=["Sliding Window"],
        techniques=["Accumulator", "Slicing"],
    ),
    problem(
        slug="max-consecutive-ones-iii",
        title="Max Consecutive Ones III",
        topic="sliding-window",
        difficulty="medium",
        fn="longest_ones",
        signature="(nums: list[int], k: int) -> int",
        description=html(
            "<code>nums</code> holds only 0s and 1s. You may turn at most <code>k</code> of the zeros into ones.",
            "Return the length of the longest run of consecutive ones you can end up with.",
        ),
        examples=[
            (
                "nums = [1, 0, 1, 1, 0, 1], k = 1",
                "4",
                "Flip the zero at index 1 (or index 4) to get four ones in a row",
            ),
        ],
        constraints=["1 <= len(nums) <= 10^5", "nums[i] is 0 or 1", "0 <= k <= len(nums)"],
        todo="Grow a window to the right; shrink it from the left whenever it holds more than k zeros.",
        solution="""
            def longest_ones(nums: list[int], k: int) -> int:
                left = 0
                zeros = 0
                best = 0
                for right in range(len(nums)):
                    if nums[right] == 0:
                        zeros += 1
                    while zeros > k:
                        if nums[left] == 0:
                            zeros -= 1
                        left += 1
                    best = max(best, right - left + 1)
                return best
        """,
        trace=1,
        cases=[
            ("[1, 0, 1, 1, 0, 1], 1", "4", False),
            ("[1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2", "6", False),
            ("[0, 0, 0], 0", "0", True),
            ("[1, 1, 1], 0", "3", True),
            ("[0, 0, 1, 1, 1, 0, 0], 0", "3", True),
            ("[0, 0, 0, 1], 4", "4", True),
        ],
        hints=(
            "Flipping at most k zeros is the same as finding the longest stretch that contains at most k zeros.",
            "Slide a window: extend the right edge each step and count the zeros inside it.",
            "When the zero count goes above k, move the left edge forward until it is back to k, then compare the window size with the best so far.",
        ),
        approaches=[
            (
                "Check every window",
                "Count the zeros in every pair (start, end).",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Variable-size window",
                "Each element enters and leaves the window at most once.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "This loop restores the invariant: the window never holds more than k zeros when the size is measured.",
                False,
            ),
        ],
        predictions=[
            (
                11,
                "For [1, 0, 1, 1, 0, 1] and k = 1, what are left and zeros the second time this line is reached?",
                "left = 1 and zeros = 1: the zero at index 1 was just dropped from the window.",
            ),
        ],
        patterns=["Sliding Window"],
        techniques=["Shrinking Window", "Counter Variable"],
    ),
    problem(
        slug="fruit-into-baskets",
        title="Fruit Into Baskets",
        topic="sliding-window",
        difficulty="medium",
        fn="total_fruit",
        signature="(fruits: list[int]) -> int",
        description=html(
            "Trees stand in a row and <code>fruits[i]</code> is the kind of fruit on tree <code>i</code>. You carry two baskets, each holding a single kind of fruit without a size limit.",
            "Pick one fruit from each tree while walking right from any starting tree, and stop as soon as a tree's fruit fits neither basket. Return the largest number of fruits you can collect.",
        ),
        examples=[
            (
                "fruits = [1, 2, 3, 2, 2]",
                "4",
                "Start at index 1 and pick 2, 3, 2, 2",
            ),
        ],
        constraints=["1 <= len(fruits) <= 10^5", "0 <= fruits[i] < len(fruits)"],
        todo="Find the longest stretch containing at most two different values.",
        solution="""
            def total_fruit(fruits: list[int]) -> int:
                counts = {}
                left = 0
                best = 0
                for right, fruit in enumerate(fruits):
                    counts[fruit] = counts.get(fruit, 0) + 1
                    while len(counts) > 2:
                        counts[fruits[left]] -= 1
                        if counts[fruits[left]] == 0:
                            del counts[fruits[left]]
                        left += 1
                    best = max(best, right - left + 1)
                return best
        """,
        trace=3,
        cases=[
            ("[1, 2, 1]", "3", False),
            ("[0, 1, 2, 2]", "3", False),
            ("[1, 2, 3, 2, 2]", "4", False),
            ("[3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]", "5", True),
            ("[5]", "1", True),
            ("[1, 1, 1, 1]", "4", True),
            ("[1, 2, 3, 4]", "2", True),
        ],
        hints=(
            "Rephrase the story: what is the longest contiguous part of the array with at most two distinct values?",
            "Keep a dictionary of counts for the values inside the window.",
            "While the dictionary has more than two keys, shrink from the left, deleting a key when its count reaches zero.",
        ),
        approaches=[
            (
                "Check every start",
                "From each start, walk right until a third kind appears.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Window with a count map",
                "Slide a window that keeps at most two kinds.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                10,
                "Deleting the key at zero keeps len(counts) equal to the number of distinct kinds inside the window.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For [1, 2, 3, 2, 2], what is counts the first time this line is reached?",
                "{1: 1, 2: 1, 3: 1}, three kinds, so the window must shrink.",
            ),
        ],
        patterns=["Sliding Window", "Hash Map"],
        techniques=["Dictionary Counting", "Shrinking Window"],
    ),
    problem(
        slug="longest-substring-with-at-most-k-distinct-characters",
        title="Longest Substring With At Most K Distinct Characters",
        topic="sliding-window",
        difficulty="medium",
        fn="longest_k_distinct",
        signature="(s: str, k: int) -> int",
        description=html(
            "Given a string <code>s</code> and an integer <code>k</code>, return the length of the longest substring that contains at most <code>k</code> different characters.",
        ),
        examples=[
            (
                's = "abaccc", k = 2',
                "4",
                'The substring "accc" has only the characters a and c',
            ),
        ],
        constraints=["1 <= len(s) <= 10^5", "0 <= k <= 26", "s has lowercase letters only"],
        todo="Slide a window and keep a count per character; shrink while there are more than k kinds.",
        solution="""
            def longest_k_distinct(s: str, k: int) -> int:
                counts = {}
                left = 0
                best = 0
                for right, ch in enumerate(s):
                    counts[ch] = counts.get(ch, 0) + 1
                    while len(counts) > k:
                        counts[s[left]] -= 1
                        if counts[s[left]] == 0:
                            del counts[s[left]]
                        left += 1
                    best = max(best, right - left + 1)
                return best
        """,
        trace=1,
        cases=[
            ('"eceba", 2', "3", False),
            ('"aa", 1', "2", False),
            ('"abaccc", 2', "4", False),
            ('"a", 0', "0", True),
            ('"abcabc", 5', "6", True),
            ('"abcd", 1', "1", True),
        ],
        hints=(
            "What changes in the window when you add one character on the right?",
            "Store the number of occurrences of each character inside the window in a dictionary.",
            "When the dictionary has more than k keys, advance the left edge, decrementing counts and deleting keys that hit zero.",
        ),
        approaches=[
            (
                "Check every substring",
                "Count distinct characters in every substring.",
                "O(n^2)",
                "O(k)",
                False,
            ),
            (
                "Window with a count map",
                "Both edges only move forward.",
                "O(n)",
                "O(k)",
                True,
            ),
        ],
        notes=[
            (
                10,
                "When the last copy of a character leaves the window its key must be removed, otherwise len(counts) would overstate the distinct count.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                'For s = "eceba" and k = 2, what is counts the first time this line is reached?',
                "{'e': 2, 'c': 1, 'b': 1} with left = 0.",
            ),
        ],
        patterns=["Sliding Window", "Hash Map"],
        techniques=["Dictionary Counting", "Shrinking Window"],
    ),
    problem(
        slug="longest-repeating-character-replacement",
        title="Longest Repeating Character Replacement",
        topic="sliding-window",
        difficulty="medium",
        fn="character_replacement",
        signature="(s: str, k: int) -> int",
        description=html(
            "You may change at most <code>k</code> characters of the uppercase string <code>s</code> into any other uppercase letters.",
            "Return the length of the longest substring made of one repeated letter that you can obtain.",
        ),
        examples=[
            (
                's = "AABABBA", k = 1',
                "4",
                'Change the B at index 2 into A to get "AAAA"',
            ),
        ],
        constraints=["1 <= len(s) <= 10^5", "s has uppercase letters only", "0 <= k <= len(s)"],
        todo="A window is valid if (its length - the count of its most common letter) <= k.",
        solution="""
            def character_replacement(s: str, k: int) -> int:
                counts = {}
                left = 0
                most = 0
                best = 0
                for right, ch in enumerate(s):
                    counts[ch] = counts.get(ch, 0) + 1
                    most = max(most, counts[ch])
                    if right - left + 1 - most > k:
                        counts[s[left]] -= 1
                        left += 1
                    best = max(best, right - left + 1)
                return best
        """,
        trace=2,
        cases=[
            ('"ABAB", 2', "4", False),
            ('"AABABBA", 1', "4", False),
            ('"AAAA", 0', "4", True),
            ('"ABCDE", 1', "2", True),
            ('"A", 0', "1", True),
            ('"ABBB", 2', "4", True),
        ],
        hints=(
            "In a window, which letters would you keep and which would you replace?",
            "Keep the most frequent letter; everything else must be replaced, so the cost is length minus the highest count.",
            "Use a single <code>if</code> instead of a <code>while</code>: the window slides at most one step, and <code>most</code> never has to be lowered.",
        ),
        approaches=[
            (
                "Try every target letter",
                "For each of the 26 letters run a window that allows k other letters.",
                "O(26 * n)",
                "O(1)",
                False,
            ),
            (
                "One pass with the max count",
                "Track the largest count seen in any window; the window only grows when that count improves.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "most is never lowered: a window can only beat the best size if some letter reaches a higher count, so a stale value does no harm.",
                False,
            ),
        ],
        predictions=[
            (
                10,
                'For s = "AABABBA" and k = 1, what is most the first time this line is reached?',
                "3 (A appeared three times by index 3).",
            ),
        ],
        patterns=["Sliding Window", "Hash Map"],
        techniques=["Dictionary Counting", "Running Maximum"],
    ),
    problem(
        slug="minimum-window-substring",
        title="Minimum Window Substring",
        topic="sliding-window",
        difficulty="hard",
        fn="min_window",
        signature="(s: str, t: str) -> str",
        description=html(
            "Return the shortest substring of <code>s</code> that contains every character of <code>t</code>, counting duplicates (if <code>t</code> has two As, the window needs two As).",
            "If no such substring exists return the empty string. The tests are built so that the shortest answer is unique.",
        ),
        examples=[
            (
                's = "AXBYCAB", t = "ABC"',
                '"CAB"',
                'The window "CAB" holds A, B and C; no window of length 2 does',
            ),
        ],
        constraints=["1 <= len(s), len(t) <= 10^5", "s and t consist of letters"],
        todo="Expand right until the window covers t, then shrink from the left while it still does.",
        solution="""
            def min_window(s: str, t: str) -> str:
                need = {}
                for ch in t:
                    need[ch] = need.get(ch, 0) + 1
                missing = len(t)
                left = 0
                best_start, best_len = 0, len(s) + 1
                for right, ch in enumerate(s):
                    if need.get(ch, 0) > 0:
                        missing -= 1
                    need[ch] = need.get(ch, 0) - 1
                    while missing == 0:
                        if right - left + 1 < best_len:
                            best_start, best_len = left, right - left + 1
                        need[s[left]] += 1
                        if need[s[left]] > 0:
                            missing += 1
                        left += 1
                return "" if best_len > len(s) else s[best_start:best_start + best_len]
        """,
        trace=2,
        cases=[
            ('"AXBYCAB", "ABC"', '"CAB"', False),
            ('"XABXC", "ABC"', '"ABXC"', False),
            ('"a", "aa"', '""', False),
            ('"ADOBECODEBANC", "ABC"', '"BANC"', True),
            ('"aa", "aa"', '"aa"', True),
            ('"ab", "b"', '"b"', True),
        ],
        hints=(
            "Store how many of each character you still need. What does a negative need mean?",
            "Count how many required characters are still missing; when it reaches 0 the window is valid, so record it and start shrinking.",
            "Shrink from the left while valid. When removing a character makes its need positive again, the window is invalid and one more character is missing.",
        ),
        approaches=[
            (
                "Check every substring",
                "Test each substring against the character counts of t.",
                "O(n^2 * m)",
                "O(m)",
                False,
            ),
            (
                "Expand then contract",
                "Maintain a need-count table plus a single 'missing' counter so each step is O(1).",
                "O(n + m)",
                "O(m)",
                True,
            ),
        ],
        notes=[
            (
                17,
                "A need above 0 after restoring means the window just lost a required character, so the window is no longer valid.",
                False,
            ),
        ],
        predictions=[
            (
                15,
                'For s = "XABXC" and t = "ABC", what is best_len the first time this line is reached?',
                'best_len = 5: the whole string "XABXC" is the first window that covers A, B and C.',
            ),
        ],
        patterns=["Sliding Window", "Hash Map"],
        techniques=["Dictionary Counting", "Shrinking Window", "Tuple Unpacking"],
    ),
]
