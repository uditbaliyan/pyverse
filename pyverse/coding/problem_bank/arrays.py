# ruff: noqa: E501, ISC004, RUF001
"""Arrays & Hashing: the dict/set toolbox."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="contains-duplicate",
        title="Contains Duplicate",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="contains_duplicate",
        signature="(nums: list[int]) -> bool",
        description=html(
            "Given an integer array <code>nums</code>, return <code>True</code> if any "
            "value appears at least twice, and <code>False</code> if every element is distinct.",
        ),
        examples=[
            ("nums = [1,2,3,1]", "True", "1 appears twice."),
            ("nums = [1,2,3,4]", "False", "All elements are distinct."),
        ],
        constraints=["1 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"],
        todo="Return True if any value repeats.",
        solution="""
            def contains_duplicate(nums: list[int]) -> bool:
                seen = set()
                for value in nums:
                    if value in seen:
                        return True
                    seen.add(value)
                return False
        """,
        cases=[
            ("[1, 2, 3, 1]", "True", False),
            ("[1, 2, 3, 4]", "False", False),
            ("[5]", "False", True),
            ("[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]", "True", True),
            ("[-7, 7, -7]", "True", True),
        ],
        hints=(
            "Comparing every pair works but is slow. What could you remember as you scan?",
            "Keep a <code>set</code> of values already seen. Membership tests on a set are O(1).",
            "For each value: if it is already in the set, return True; otherwise add it.",
        ),
        approaches=[
            (
                "Compare every pair",
                "Two nested loops. Simple, but quadratic.",
                "O(n²)",
                "O(1)",
                False,
            ),
            (
                "Set of seen values",
                "One pass; stop as soon as a value is already in the set.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "A set answers 'have I seen this?' in one step, which is why one pass is enough.",
                True,
            ),
        ],
        predictions=[
            (
                5,
                "Which value triggers this return for [1, 2, 3, 1]?",
                "The last 1: it is already in seen.",
            ),
        ],
        patterns=["Hash Set"],
        techniques=["Sets"],
    ),
    problem(
        slug="valid-anagram",
        title="Valid Anagram",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="is_anagram",
        signature="(s: str, t: str) -> bool",
        description=html(
            "Given two strings <code>s</code> and <code>t</code>, return <code>True</code> "
            "if <code>t</code> is an anagram of <code>s</code>: the same letters, "
            "the same number of times, in any order.",
        ),
        examples=[
            ('s = "anagram", t = "nagaram"', "True", ""),
            ('s = "rat", t = "car"', "False", "Different letters."),
        ],
        constraints=[
            "1 <= s.length, t.length <= 5 * 10^4",
            "Lower-case English letters only.",
        ],
        todo="Return True if t uses exactly the letters of s.",
        solution="""
            def is_anagram(s: str, t: str) -> bool:
                if len(s) != len(t):
                    return False
                counts = {}
                for char in s:
                    counts[char] = counts.get(char, 0) + 1
                for char in t:
                    if counts.get(char, 0) == 0:
                        return False
                    counts[char] -= 1
                return True
        """,
        cases=[
            ('"anagram", "nagaram"', "True", False),
            ('"rat", "car"', "False", False),
            ('"a", "a"', "True", True),
            ('"ab", "a"', "False", True),
            ('"aacc", "ccac"', "False", True),
        ],
        hints=(
            "Two strings are anagrams exactly when every letter occurs the same number of times.",
            "Count the letters of <code>s</code> in a dict, then use up those counts with <code>t</code>.",
            "While walking <code>t</code>, a letter whose count is already 0 means "
            "<code>t</code> has too many of it.",
        ),
        approaches=[
            (
                "Sort both",
                "<code>sorted(s) == sorted(t)</code>. Very short; the sort costs time.",
                "O(n log n)",
                "O(n)",
                False,
            ),
            (
                "Count letters",
                "Tally <code>s</code>, then cancel the tally with <code>t</code>.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "counts.get(char, 0) gives 0 for a letter not seen yet, "
                "so there is no special first-time case.",
                False,
            ),
            (
                10,
                "Each letter of t cancels one letter of s. A letter with no tally left "
                "means t has too many of it.",
                True,
            ),
        ],
        predictions=[
            (
                7,
                "What does counts['a'] hold when this line is first reached, for 'anagram'?",
                "3: 'a' appears three times in 'anagram'.",
            ),
        ],
        patterns=["Hash Map"],
        techniques=["Dict Counting"],
    ),
    problem(
        slug="group-anagrams",
        title="Group Anagrams",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="group_anagrams",
        signature="(strs: list[str]) -> list[list[str]]",
        description=html(
            "Given a list of strings, group the anagrams together. "
            "You may return the groups, and the words inside each group, in any order.",
        ),
        examples=[
            (
                'strs = ["eat","tea","tan","ate","nat","bat"]',
                '[["eat","tea","ate"],["tan","nat"],["bat"]]',
                "Order of groups does not matter.",
            ),
            ('strs = [""]', '[[""]]', ""),
        ],
        constraints=[
            "1 <= strs.length <= 10^4",
            "0 <= strs[i].length <= 100",
            "Lower-case letters only.",
        ],
        todo="Return the words grouped by anagram.",
        solution="""
            def group_anagrams(strs: list[str]) -> list[list[str]]:
                groups = {}
                for word in strs:
                    key = "".join(sorted(word))
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(word)
                return list(groups.values())
        """,
        comparator="custom",
        custom_comparator="""
            def compare(actual, expected):
                def normal(groups):
                    return sorted(sorted(group) for group in groups)

                return normal(actual) == normal(expected)
        """,
        cases=[
            (
                '["eat", "tea", "tan", "ate", "nat", "bat"]',
                '[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]',
                False,
            ),
            ('["a", "b", "a"]', '[["a", "a"], ["b"]]', False),
            ('[""]', '[[""]]', True),
            ('["abc", "bca", "cab", "xyz"]', '[["abc", "bca", "cab"], ["xyz"]]', True),
        ],
        hints=(
            "What do all the words in one group have in common once you ignore order?",
            "Sorting a word's letters gives the same string for every anagram of it. "
            "Use that as a dict key.",
            "<code>key = ''.join(sorted(word))</code>, then append the word to "
            "<code>groups[key]</code>.",
        ),
        approaches=[
            (
                "Sorted word as key",
                "Anagrams sort to the same string, so it works as a shared label.",
                "O(n · k log k)",
                "O(n · k)",
                True,
            ),
            (
                "Letter-count tuple as key",
                "Use a 26-slot count as the key instead of sorting. "
                "Faster when words are long.",
                "O(n · k)",
                "O(n · k)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "Anagrams sort to the same letters, so the sorted word works as a shared label.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "How many keys does groups have when the loop ends?",
                "3: 'aet', 'ant' and 'abt'.",
            ),
        ],
        patterns=["Hash Map"],
        techniques=["Dict of Lists", "Sorting"],
    ),
    problem(
        slug="top-k-frequent-elements",
        title="Top K Frequent Elements",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="top_k_frequent",
        signature="(nums: list[int], k: int) -> list[int]",
        description=html(
            "Given an integer array <code>nums</code> and an integer <code>k</code>, "
            "return the <code>k</code> most frequent elements. "
            "The answer can be in any order.",
            "The answer is guaranteed to be unique.",
        ),
        examples=[
            (
                "nums = [1,1,1,2,2,3], k = 2",
                "[1,2]",
                "1 appears 3 times, 2 appears twice.",
            ),
            ("nums = [1], k = 1", "[1]", ""),
        ],
        constraints=[
            "1 <= nums.length <= 10^5",
            "k is in the range [1, number of distinct elements]",
            "The answer is unique.",
        ],
        todo="Return the k most frequent values, any order.",
        solution="""
            def top_k_frequent(nums: list[int], k: int) -> list[int]:
                counts = {}
                for value in nums:
                    counts[value] = counts.get(value, 0) + 1
                buckets = [[] for _ in range(len(nums) + 1)]
                for value, count in counts.items():
                    buckets[count].append(value)
                result = []
                for count in range(len(buckets) - 1, 0, -1):
                    for value in buckets[count]:
                        result.append(value)
                        if len(result) == k:
                            return result
                return result
        """,
        comparator="sorted_list",
        cases=[
            ("[1, 1, 1, 2, 2, 3], 2", "[1, 2]", False),
            ("[1], 1", "[1]", False),
            ("[4, 4, 4, 4, 5, 5, 6], 1", "[4]", True),
            ("[-1, -1, 2, 2, 3], 2", "[-1, 2]", True),
        ],
        hints=(
            "First you need a count for every value. Which structure gives you that?",
            "Sorting all values by count works. Can you avoid the sort by using the count "
            "itself as an index?",
            "No value can occur more than <code>len(nums)</code> times, so make a list of "
            "buckets indexed by frequency and read it from the top.",
        ),
        approaches=[
            (
                "Count, then sort",
                "Sort the distinct values by count and take the first k.",
                "O(n log n)",
                "O(n)",
                False,
            ),
            (
                "Bucket by frequency",
                "Put each value in <code>buckets[count]</code>, then walk from the highest "
                "count down until k values are collected.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "A value occurs at most len(nums) times, so 'frequency as an index' never runs out "
                "of room. This replaces sorting.",
                False,
            ),
            (
                9,
                "Walk from the highest frequency down. The first k values met are the answer.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For [1, 1, 1, 2, 2, 3], which bucket index holds the value 1?",
                "3: the value 1 appears three times.",
            ),
        ],
        patterns=["Hash Map", "Bucket Sort"],
        techniques=["Dict Counting", "List Comprehension"],
    ),
    problem(
        slug="product-of-array-except-self",
        title="Product of Array Except Self",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="product_except_self",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Given an integer array <code>nums</code>, return an array <code>answer</code> "
            "where <code>answer[i]</code> is the product of every element of <code>nums</code> "
            "except <code>nums[i]</code>.",
            "Do it <strong>without division</strong>, in O(n) time.",
        ),
        examples=[
            ("nums = [1,2,3,4]", "[24,12,8,6]", ""),
            ("nums = [-1,1,0,-3,3]", "[0,0,9,0,0]", "A zero makes most products zero."),
        ],
        constraints=[
            "2 <= nums.length <= 10^5",
            "-30 <= nums[i] <= 30",
            "Every prefix and suffix product fits in a 32-bit integer.",
        ],
        todo="Return the product of everything except each element, without dividing.",
        solution="""
            def product_except_self(nums: list[int]) -> list[int]:
                n = len(nums)
                result = [1] * n
                prefix = 1
                for i in range(n):
                    result[i] = prefix
                    prefix *= nums[i]
                suffix = 1
                for i in range(n - 1, -1, -1):
                    result[i] *= suffix
                    suffix *= nums[i]
                return result
        """,
        cases=[
            ("[1, 2, 3, 4]", "[24, 12, 8, 6]", False),
            ("[-1, 1, 0, -3, 3]", "[0, 0, 9, 0, 0]", False),
            ("[2, 3]", "[3, 2]", True),
            ("[0, 0]", "[0, 0]", True),
            ("[5, 1, 1]", "[1, 5, 5]", True),
        ],
        hints=(
            "The product of everything except <code>nums[i]</code> is "
            "(product to its left) × (product to its right).",
            "Fill the answer with left-products in one pass, then multiply in the "
            "right-products in a second pass from the end.",
            "Keep a running <code>prefix</code> going forwards and a running "
            "<code>suffix</code> going backwards; write both straight into <code>result</code>.",
        ),
        approaches=[
            (
                "Divide by each element",
                "Total product divided by <code>nums[i]</code>. Breaks on zeros and is "
                "not allowed here.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Prefix then suffix",
                "Two passes that build left-products and then right-products in the "
                "same output list.",
                "O(n)",
                "O(1) extra",
                True,
            ),
        ],
        notes=[
            (
                6,
                "result[i] is everything to the left of i, stored before nums[i] is multiplied in.",
                False,
            ),
            (
                10,
                "Now multiply in everything to the right. Left times right is the product "
                "of everything but nums[i].",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For [1, 2, 3, 4], what does result hold after the first loop?",
                "[1, 1, 2, 6]: the product of everything to the left of each index.",
            ),
        ],
        patterns=["Prefix Sum"],
        techniques=["Accumulator"],
    ),
    problem(
        slug="longest-consecutive-sequence",
        title="Longest Consecutive Sequence",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="longest_consecutive",
        signature="(nums: list[int]) -> int",
        description=html(
            "Given an unsorted array of integers <code>nums</code>, return the length of the "
            "longest run of consecutive values (like <code>3, 4, 5, 6</code>). "
            "The run does not need to appear in order in the array.",
            "Your solution should run in O(n) time.",
        ),
        examples=[
            ("nums = [100,4,200,1,3,2]", "4", "The run is 1, 2, 3, 4."),
            ("nums = [0,3,7,2,5,8,4,6,0,1]", "9", "0 through 8."),
        ],
        constraints=["0 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"],
        todo="Return the length of the longest run of consecutive integers.",
        solution="""
            def longest_consecutive(nums: list[int]) -> int:
                numbers = set(nums)
                best = 0
                for value in numbers:
                    if value - 1 not in numbers:
                        length = 1
                        while value + length in numbers:
                            length += 1
                        best = max(best, length)
                return best
        """,
        cases=[
            ("[100, 4, 200, 1, 3, 2]", "4", False),
            ("[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]", "9", False),
            ("[]", "0", True),
            ("[1, 2, 0, 1]", "3", True),
            ("[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]", "7", True),
        ],
        hints=(
            "Sorting finds the answer in O(n log n). To beat that you need O(1) lookups.",
            "Put everything in a set. Only start counting from a number that has no "
            "smaller neighbour in the set.",
            "If <code>value - 1</code> is not in the set, count upwards with "
            "<code>value + length in numbers</code>.",
        ),
        approaches=[
            (
                "Sort and scan",
                "Sort, then count the length of each run of neighbours.",
                "O(n log n)",
                "O(1)",
                False,
            ),
            (
                "Set, start only at run beginnings",
                "A number starts a run only if its predecessor is missing, so each number "
                "is visited a constant number of times.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Only a number with no left neighbour starts a run. That keeps the total work "
                "linear instead of quadratic.",
                True,
            ),
        ],
        predictions=[
            (
                10,
                "For [100, 4, 200, 1, 3, 2], which numbers start a run?",
                "100, 200 and 1. The numbers 4, 3 and 2 each have a left neighbour.",
            ),
        ],
        patterns=["Hash Set"],
        techniques=["Sets"],
    ),
    problem(
        slug="missing-number",
        title="Missing Number",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="missing_number",
        signature="(nums: list[int]) -> int",
        description=html(
            "Given an array <code>nums</code> holding <code>n</code> distinct numbers from "
            "the range <code>[0, n]</code>, return the one number in that range "
            "that is missing from the array.",
        ),
        examples=[
            ("nums = [3,0,1]", "2", "n = 3, so the range is 0..3 and 2 is absent."),
            ("nums = [9,6,4,2,3,5,7,0,1]", "8", ""),
        ],
        constraints=["n == nums.length", "1 <= n <= 10^4", "All values are distinct."],
        todo="Return the number from 0..n that does not appear.",
        solution="""
            def missing_number(nums: list[int]) -> int:
                n = len(nums)
                expected = n * (n + 1) // 2
                actual = 0
                for value in nums:
                    actual += value
                return expected - actual
        """,
        cases=[
            ("[3, 0, 1]", "2", False),
            ("[9, 6, 4, 2, 3, 5, 7, 0, 1]", "8", False),
            ("[0]", "1", True),
            ("[1]", "0", True),
            ("[0, 1]", "2", True),
        ],
        hints=(
            "If nothing were missing, you would know exactly what the numbers add up to.",
            "The numbers 0..n add up to <code>n * (n + 1) // 2</code>. Compare that with "
            "the actual sum.",
            "The missing number is <code>expected - actual</code>.",
        ),
        approaches=[
            (
                "Set of numbers",
                "Put <code>nums</code> in a set and find the number in 0..n that is not in it.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Gauss sum",
                "The gap between the expected and actual sum is the missing number.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                3,
                "The numbers 0..n always add up to n(n+1)/2. The missing number is the gap "
                "between that and what we actually hold.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [3, 0, 1], what are expected and actual?",
                "expected = 6 (0+1+2+3), actual = 4, so the answer is 2.",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator"],
    ),
    problem(
        slug="majority-element",
        title="Majority Element",
        topic="arrays-and-hashing",
        difficulty="easy",
        fn="majority_element",
        signature="(nums: list[int]) -> int",
        description=html(
            "Given an array <code>nums</code> of size <code>n</code>, return the majority "
            "element: the value that appears <strong>more than</strong> <code>n / 2</code> times.",
            "You may assume a majority element always exists.",
        ),
        examples=[
            ("nums = [3,2,3]", "3", ""),
            ("nums = [2,2,1,1,1,2,2]", "2", ""),
        ],
        constraints=[
            "1 <= nums.length <= 5 * 10^4",
            "A majority element always exists.",
        ],
        todo="Return the value that appears more than n / 2 times.",
        solution="""
            def majority_element(nums: list[int]) -> int:
                candidate = 0
                votes = 0
                for value in nums:
                    if votes == 0:
                        candidate = value
                    if value == candidate:
                        votes += 1
                    else:
                        votes -= 1
                return candidate
        """,
        trace=2,
        cases=[
            ("[3, 2, 3]", "3", False),
            ("[2, 2, 1, 1, 1, 2, 2]", "2", False),
            ("[1]", "1", True),
            ("[6, 6, 6, 7, 7]", "6", True),
            ("[-1, -1, -1, 2, 3]", "-1", True),
        ],
        hints=(
            "Counting every value in a dict works. Can you do it with O(1) memory?",
            "Think of votes: the majority element out-votes everything else combined.",
            "Keep one <code>candidate</code> and a <code>votes</code> tally. A matching value adds one, "
            "a different value removes one, and at zero the next value becomes the candidate.",
        ),
        approaches=[
            (
                "Count with a dict",
                "Tally every value and return the one above n / 2.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Boyer–Moore voting",
                "Pairs of different values cancel out. The majority element is the one left standing.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "When the tally hits zero, the old candidate has been fully cancelled out, "
                "so the next value takes over.",
                True,
            ),
        ],
        predictions=[
            (
                6,
                "How many times does this line run for [2, 2, 1, 1, 1, 2, 2]?",
                "3 times: at the first 2, at the third 1 and at the last 2.",
            ),
        ],
        patterns=["Voting"],
        techniques=["Accumulator"],
    ),
]
