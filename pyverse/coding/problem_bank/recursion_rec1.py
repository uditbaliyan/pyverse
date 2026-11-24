# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="pow-x-n",
        title="Pow(x, n)",
        topic="recursion",
        difficulty="medium",
        fn="my_pow",
        signature="(x: float, n: int) -> float",
        description=html(
            "Return <code>x</code> raised to the integer power <code>n</code> without using <code>**</code> or <code>pow</code>.",
            "<code>n</code> may be negative, in which case the answer is <code>1 / x<sup>|n|</sup></code>. Answers are compared with a small tolerance.",
        ),
        examples=[
            ("x = 2.0, n = 10", "1024.0", "2 multiplied by itself ten times is 1024"),
            ("x = 2.0, n = -2", "0.25", "2 to the minus 2 is 1 / 4"),
        ],
        constraints=["-100.0 < x < 100.0", "-2^31 <= n <= 2^31 - 1", "x is not 0 when n is negative"],
        todo="Flip x when n is negative, then repeatedly square x and halve n, collecting x whenever n is odd.",
        solution="""
            def my_pow(x: float, n: int) -> float:
                if n < 0:
                    x = 1 / x
                    n = -n
                result = 1.0
                while n > 0:
                    if n % 2 == 1:
                        result *= x
                    x *= x
                    n //= 2
                return result
        """,
        trace=1,
        comparator="float_tolerance",
        cases=[
            ("2.0, 10", "1024.0", False),
            ("2.0, -2", "0.25", False),
            ("2.1, 3", "9.261000000000001", False),
            ("1.0, 2147483647", "1.0", True),
            ("0.0, 5", "0.0", True),
            ("-2.0, 3", "-8.0", True),
            ("5.0, 0", "1.0", True),
        ],
        hints=(
            "Multiplying x by itself n times is far too slow when n can be about two billion. Which identity halves the work?",
            "x^n equals (x * x)^(n / 2) when n is even; when n is odd there is one extra factor of x left over.",
            "Look at the binary digits of n: each 1 digit means one of the repeated squares of x belongs in the answer.",
        ),
        approaches=[
            ("Multiply n times", "Loop |n| times, multiplying by x each pass.", "O(|n|)", "O(1)", False),
            ("Exponentiation by squaring", "Square the base and halve the exponent, folding the base into the result on every odd step.", "O(log |n|)", "O(1)", True),
        ],
        notes=[
            (8, "An odd exponent leaves one copy of x behind; result collects it before x is squared.", False),
        ],
        predictions=[
            (8, "For x = 2.0, n = 10, what are <code>x</code> and <code>result</code> the first time <code>result *= x</code> is reached?", "x = 4.0 and result = 1.0."),
        ],
        patterns=["Math", "Recursion"],
        techniques=["Exponentiation By Squaring", "Accumulator"],
    ),
    problem(
        slug="generate-parentheses",
        title="Generate Parentheses",
        topic="recursion",
        difficulty="medium",
        fn="generate_parentheses",
        signature="(n: int) -> list[str]",
        description=html(
            "Given <code>n</code> pairs of round brackets, return every well-formed (balanced) string that uses exactly <code>n</code> opening and <code>n</code> closing brackets.",
            "The strings may be returned in any order.",
        ),
        examples=[
            ("n = 3", '["((()))", "(()())", "(())()", "()(())", "()()()"]', "Five balanced strings exist for three pairs"),
            ("n = 2", '["(())", "()()"]', "Only (()) and ()() are balanced"),
        ],
        constraints=["1 <= n <= 8"],
        todo="Build the string one bracket at a time, tracking how many opens and closes you have used.",
        solution="""
            def generate_parentheses(n: int) -> list[str]:
                result = []
                def build(current: str, opened: int, closed: int) -> None:
                    if len(current) == 2 * n:
                        result.append(current)
                        return
                    if opened < n:
                        build(current + "(", opened + 1, closed)
                    if closed < opened:
                        build(current + ")", opened, closed + 1)
                build("", 0, 0)
                return result
        """,
        trace=2,
        comparator="sorted_list",
        cases=[
            ("3", '["((()))", "(()())", "(())()", "()(())", "()()()"]', False),
            ("2", '["(())", "()()"]', False),
            ("1", '["()"]', True),
            ("4", '["(((())))", "((()()))", "((())())", "((()))()", "(()(()))", "(()()())", "(()())()", "(())(())", "(())()()", "()((()))", "()(()())", "()(())()", "()()(())", "()()()()"]', True),
        ],
        hints=(
            "Which prefixes are worth extending? Think about when a prefix can no longer be completed into a balanced string.",
            "Count the opening and closing brackets placed so far. A closing bracket only makes sense if something is still open.",
            "Recurse with those two counts and record the string once it reaches length 2n.",
        ),
        approaches=[
            ("Generate all, then filter", "Build every one of the 2^(2n) bracket strings and keep the balanced ones.", "O(2^(2n) * n)", "O(n)", False),
            ("Backtracking with counts", "Extend a prefix only when it can still become balanced.", "O(4^n / sqrt(n))", "O(n)", True),
        ],
        notes=[
            (9, "A closing bracket is only allowed while there are more opens than closes, which keeps every prefix valid.", False),
        ],
        predictions=[
            (5, "For n = 2, what is <code>current</code> the first time <code>result.append(current)</code> is reached?", '"(())", the first complete string.'),
        ],
        patterns=["Recursion", "Strings"],
        techniques=["Backtracking", "Nested Functions"],
    ),
    problem(
        slug="count-good-numbers",
        title="Count Good Numbers",
        topic="number-play",
        difficulty="medium",
        fn="count_good_numbers",
        signature="(n: int) -> int",
        description=html(
            "A digit string is <em>good</em> if the digits at even positions (0, 2, 4, ...) are even and the digits at odd positions (1, 3, 5, ...) are prime (2, 3, 5 or 7). Leading zeros are allowed.",
            "Return how many good digit strings of length <code>n</code> exist, modulo <code>10^9 + 7</code>.",
        ),
        examples=[
            ("n = 1", "5", "Position 0 must be one of 0, 2, 4, 6, 8: five strings"),
            ("n = 4", "400", "5 * 4 * 5 * 4 = 400"),
        ],
        constraints=["1 <= n <= 10^15"],
        todo="Each even position has 5 choices and each odd position has 4, so compute 5^a * 4^b with fast modular powers.",
        solution="""
            def count_good_numbers(n: int) -> int:
                mod = 10**9 + 7
                def power(base: int, exp: int) -> int:
                    result = 1
                    base %= mod
                    while exp > 0:
                        if exp % 2 == 1:
                            result = result * base % mod
                        base = base * base % mod
                        exp //= 2
                    return result
                return power(5, (n + 1) // 2) * power(4, n // 2) % mod
        """,
        trace=2,
        cases=[
            ("1", "5", False),
            ("4", "400", False),
            ("2", "20", True),
            ("50", "564908303", True),
            ("806166225460393", "643535977", True),
        ],
        hints=(
            "How many choices does each position have on its own? Do the choices at different positions affect each other?",
            "There are ceil(n / 2) even positions and floor(n / 2) odd positions, so the answer is a product of two powers.",
            "n can be 10^15, so a loop of n multiplications is far too slow. Use repeated squaring and reduce modulo 10^9 + 7 as you go.",
        ),
        approaches=[
            ("Multiply position by position", "Multiply 5 or 4 into the answer once per position.", "O(n)", "O(1)", False),
            ("Fast modular power", "Compute 5^ceil(n/2) and 4^floor(n/2) by repeated squaring.", "O(log n)", "O(1)", True),
        ],
        notes=[
            (11, "(n + 1) // 2 counts the even positions (0, 2, ...) and n // 2 counts the odd ones, for odd and even n alike.", False),
        ],
        predictions=[
            (8, "For n = 4, what are <code>base</code> and <code>exp</code> the first time <code>result = result * base % mod</code> is reached?", "base = 25 and exp = 1; 5 was squared once to reach 25 before the first odd exponent."),
        ],
        patterns=["Math", "Recursion"],
        techniques=["Exponentiation By Squaring", "Modular Arithmetic"],
    ),
    problem(
        slug="subsequence-with-sum-k",
        title="Subsequence With Sum K",
        topic="recursion",
        difficulty="medium",
        fn="has_subsequence_with_sum",
        signature="(nums: list[int], k: int) -> bool",
        description=html(
            "A subsequence keeps some of the elements of <code>nums</code> in their original order (it may skip any of them). Return <code>True</code> if at least one non-empty subsequence adds up to exactly <code>k</code>, otherwise <code>False</code>.",
        ),
        examples=[
            ("nums = [3, 34, 4, 12, 5, 2], k = 9", "True", "4 + 5 = 9"),
            ("nums = [1, 2, 3], k = 7", "False", "All three together only reach 6"),
        ],
        constraints=["1 <= len(nums) <= 20", "1 <= nums[i] <= 100", "1 <= k <= 1000"],
        todo="For each index choose to take the element or skip it; stop with True as soon as the remaining sum hits 0.",
        solution="""
            def has_subsequence_with_sum(nums: list[int], k: int) -> bool:
                def search(i: int, remaining: int) -> bool:
                    if remaining == 0:
                        return True
                    if i == len(nums) or remaining < 0:
                        return False
                    if search(i + 1, remaining - nums[i]):
                        return True
                    return search(i + 1, remaining)
                return search(0, k)
        """,
        trace=1,
        cases=[
            ("[3, 34, 4, 12, 5, 2], 9", "True", False),
            ("[1, 2, 3], 7", "False", False),
            ("[7], 7", "True", True),
            ("[2, 4, 6], 5", "False", True),
            ("[5, 5, 5], 10", "True", True),
        ],
        hints=(
            "For every element there are exactly two options. What are they, and what do they do to the sum you still need?",
            "Write a function of (index, remaining) that answers: can the elements from index onward make exactly remaining?",
            "Because every number is positive, a negative remaining can never recover, so that branch can stop early.",
        ),
        approaches=[
            ("Take or skip recursion", "Try both options for every element, stopping when the target is reached.", "O(2^n)", "O(n)", False),
            ("Dynamic programming over sums", "Track which sums up to k are reachable after each element.", "O(n * k)", "O(k)", True),
        ],
        notes=[
            (3, "Positive numbers only ever grow a subsequence sum, so remaining == 0 means a non-empty match was found.", False),
        ],
        predictions=[
            (4, "For nums = [3, 34, 4, 12, 5, 2], k = 9, what is <code>i</code> the first time <code>return True</code> is reached?", "i = 6; the subsequence 3 + 4 + 2 = 9 was found, so the search stops with True."),
        ],
        patterns=["Recursion"],
        techniques=["Backtracking", "Early Exit"],
    ),
    problem(
        slug="count-subsequences-with-sum-k",
        title="Count Subsequences With Sum K",
        topic="recursion",
        difficulty="medium",
        fn="count_subsequences_with_sum",
        signature="(nums: list[int], k: int) -> int",
        description=html(
            "Count how many subsequences of <code>nums</code> add up to exactly <code>k</code>. Two subsequences are different when they use different positions, even if the values are equal.",
        ),
        examples=[
            ("nums = [1, 2, 3], k = 3", "2", "[3] and [1, 2]"),
            ("nums = [4, 9, 2, 5, 1], k = 10", "2", "[9, 1] and [4, 5, 1]"),
        ],
        constraints=["1 <= len(nums) <= 20", "1 <= nums[i] <= 100", "1 <= k <= 1000"],
        todo="Return 1 or 0 at the end of the list, and add the counts of the take and skip choices.",
        solution="""
            def count_subsequences_with_sum(nums: list[int], k: int) -> int:
                def count(i: int, remaining: int) -> int:
                    if i == len(nums):
                        return 1 if remaining == 0 else 0
                    take = count(i + 1, remaining - nums[i])
                    skip = count(i + 1, remaining)
                    return take + skip
                return count(0, k)
        """,
        trace=1,
        cases=[
            ("[1, 2, 3], 3", "2", False),
            ("[4, 9, 2, 5, 1], 10", "2", False),
            ("[2, 2, 2], 4", "3", True),
            ("[5], 3", "0", True),
            ("[1, 1, 1, 1], 2", "6", True),
        ],
        hints=(
            "Instead of asking whether a subsequence exists, ask how many of them there are. How would counting change the recursion?",
            "Every complete pass over the list is one subsequence. It counts as 1 if the leftover sum is 0, otherwise 0.",
            "The count for position i is the count if you take nums[i] plus the count if you skip it.",
        ),
        approaches=[
            ("Take or skip recursion", "Count both branches at every index and add them.", "O(2^n)", "O(n)", False),
            ("Dynamic programming over sums", "ways[s] is the number of subsequences so far that make s.", "O(n * k)", "O(k)", True),
        ],
        notes=[
            (3, "Every leaf of the recursion tree is one choice of positions, so the leaf values add up to the answer.", False),
        ],
        predictions=[
            (6, "For nums = [1, 2, 3], k = 3, what are <code>i</code> and <code>remaining</code> the first time <code>skip = count(i + 1, remaining)</code> is reached?", "i = 2 and remaining = 0; this branch took 1 and 2 and has just evaluated taking 3."),
        ],
        patterns=["Recursion"],
        techniques=["Backtracking", "Accumulator"],
    ),
    problem(
        slug="generate-binary-strings-without-consecutive-ones",
        title="Binary Strings Without Consecutive 1s",
        topic="recursion",
        difficulty="medium",
        fn="binary_strings_without_consecutive_ones",
        signature="(n: int) -> list[str]",
        description=html(
            "Return every binary string of length <code>n</code> that never has two <code>1</code> characters next to each other.",
            "The strings may be returned in any order.",
        ),
        examples=[
            ("n = 3", '["000", "001", "010", "100", "101"]', "000, 001, 010, 100 and 101 qualify"),
            ("n = 2", '["00", "01", "10"]', "11 is the only length-2 string that is ruled out"),
        ],
        constraints=["1 <= n <= 12"],
        todo="Build the string one character at a time; only append 1 if the previous character is not 1.",
        solution="""
            def binary_strings_without_consecutive_ones(n: int) -> list[str]:
                result = []
                def build(current: str) -> None:
                    if len(current) == n:
                        result.append(current)
                        return
                    build(current + "0")
                    if not current or current[-1] != "1":
                        build(current + "1")
                build("")
                return result
        """,
        trace=1,
        comparator="sorted_list",
        cases=[
            ("3", '["000", "001", "010", "100", "101"]', False),
            ("2", '["00", "01", "10"]', False),
            ("1", '["0", "1"]', True),
            ("4", '["0000", "0001", "0010", "0100", "0101", "1000", "1001", "1010"]', True),
        ],
        hints=(
            "At each position you may write a 0 or a 1. Which choice is sometimes forbidden?",
            "Only the last character you wrote matters when deciding whether a 1 is allowed.",
            "A 0 is always safe to append; a 1 is only safe when the string is empty or does not already end in 1.",
        ),
        approaches=[
            ("Generate all, then filter", "Build every one of the 2^n strings and discard those containing 11.", "O(2^n * n)", "O(n)", False),
            ("Backtracking", "Skip the forbidden extension, so only valid prefixes are ever explored.", "O(F(n) * n)", "O(n)", True),
        ],
        notes=[
            (7, "Appending 0 is always legal, so this branch has no condition.", False),
        ],
        predictions=[
            (5, "For n = 3, what is <code>current</code> the first time <code>result.append(current)</code> is reached?", '"000", the first complete string.'),
        ],
        patterns=["Recursion", "Strings"],
        techniques=["Backtracking"],
    ),
]
