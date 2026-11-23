# ruff: noqa: E501, ISC004
"""Stack and Binary Search."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="valid-parentheses",
        title="Valid Parentheses",
        topic="stack",
        difficulty="easy",
        fn="is_valid",
        signature="(s: str) -> bool",
        description=html(
            "Given a string <code>s</code> made only of <code>( ) [ ] { }</code>, "
            "return <code>True</code> if it is valid.",
            "A string is valid when every opening bracket is closed by the same kind "
            "of bracket, in the correct order.",
        ),
        examples=[
            ('s = "()[]{}"', "True", ""),
            ('s = "(]"', "False", "A square bracket cannot close a round one."),
        ],
        constraints=["1 <= len(s) <= 10^4", "s consists only of ()[]{}."],
        todo="Return True if every bracket is closed correctly and in order.",
        solution="""
            def is_valid(s: str) -> bool:
                pairs = {")": "(", "]": "[", "}": "{"}
                stack = []
                for char in s:
                    if char in pairs:
                        if not stack or stack.pop() != pairs[char]:
                            return False
                    else:
                        stack.append(char)
                return not stack
        """,
        cases=[
            ('"()[]{}"', "True", False),
            ('"(]"', "False", False),
            ('"([)]"', "False", True),
            ('"{[]}"', "True", True),
            ('"("', "False", True),
            ('"]"', "False", True),
        ],
        hints=(
            "The bracket that closes must match the <em>most recent</em> unclosed opener.",
            "That 'most recent first' behaviour is a stack: push openers, pop on closers.",
            "On a closer, fail if the stack is empty or the popped opener is the wrong "
            "kind. At the end the stack must be empty.",
        ),
        approaches=[
            (
                "Remove matched pairs repeatedly",
                "Keep deleting <code>()</code>, <code>[]</code> and <code>{}</code> until nothing changes.",
                "O(n²)",
                "O(n)",
                False,
            ),
            (
                "Stack of openers",
                "Push each opener; a closer must match whatever is on top.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "A closing bracket must match the most recent unmatched opener. "
                "That is exactly what the top of a stack gives you.",
                True,
            ),
            (10, "Leftover openers mean something was never closed.", False),
        ],
        predictions=[
            (
                6,
                "In '()[]{}', what is on top of the stack the first time a closer arrives?",
                "'(': it matches the ')' and the stack empties again.",
            ),
        ],
        patterns=["Stack"],
        techniques=["Dict Lookup", "Early Return"],
    ),
    problem(
        slug="daily-temperatures",
        title="Daily Temperatures",
        topic="stack",
        difficulty="medium",
        fn="daily_temperatures",
        signature="(temps: list[int]) -> list[int]",
        description=html(
            "Given a list <code>temps</code> of daily temperatures, return a list "
            "<code>answer</code> where <code>answer[i]</code> is how many days you must wait "
            "after day <code>i</code> for a warmer temperature.",
            "If no later day is warmer, <code>answer[i]</code> is <code>0</code>.",
        ),
        examples=[
            ("temps = [73,74,75,71,69,72,76,73]", "[1,1,4,2,1,1,0,0]", ""),
            ("temps = [30,40,50,60]", "[1,1,1,0]", ""),
        ],
        constraints=["1 <= temps.length <= 10^5", "30 <= temps[i] <= 100"],
        todo="Return, for each day, the wait until a warmer day (0 if none).",
        solution="""
            def daily_temperatures(temps: list[int]) -> list[int]:
                answer = [0] * len(temps)
                stack = []
                for day, temp in enumerate(temps):
                    while stack and temps[stack[-1]] < temp:
                        previous = stack.pop()
                        answer[previous] = day - previous
                    stack.append(day)
                return answer
        """,
        cases=[
            ("[73, 74, 75, 71, 69, 72, 76, 73]", "[1, 1, 4, 2, 1, 1, 0, 0]", False),
            ("[30, 40, 50, 60]", "[1, 1, 1, 0]", False),
            ("[30, 60, 90]", "[1, 1, 0]", True),
            ("[90, 80, 70]", "[0, 0, 0]", True),
            ("[55]", "[0]", True),
        ],
        hints=(
            "For each day, scanning ahead for a warmer one is O(n²). "
            "Can a warmer day settle several earlier days at once?",
            "Keep a stack of days that are still waiting for a warmer day.",
            "When today is warmer than the day on top of the stack, pop it and record "
            "<code>today - popped</code>. Then push today.",
        ),
        approaches=[
            (
                "Scan ahead from every day",
                "For each day, look forward until a warmer day is found.",
                "O(n²)",
                "O(1)",
                False,
            ),
            (
                "Monotonic stack of waiting days",
                "A warmer day answers every colder day on top of the stack in one go.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Days on the stack are still waiting for a warmer day. "
                "A warmer arrival settles every colder day on top.",
                True,
            ),
        ],
        predictions=[
            (
                7,
                "When day 5 (72°) arrives, which earlier days get an answer?",
                "Days 4 and 3, with waits of 1 and 2 days. Day 2 (75°) is warmer, so it keeps waiting.",
            ),
        ],
        patterns=["Monotonic Stack"],
        techniques=["Enumeration", "Stack"],
    ),
    problem(
        slug="evaluate-reverse-polish-notation",
        title="Evaluate Reverse Polish Notation",
        topic="stack",
        difficulty="medium",
        fn="eval_rpn",
        signature="(tokens: list[str]) -> int",
        description=html(
            "In reverse Polish notation the operator comes <em>after</em> its two operands: "
            '<code>["2","1","+","3","*"]</code> means <code>(2 + 1) * 3</code>.',
            "Evaluate the expression and return the result. The operators are "
            "<code>+ - * /</code>. Division <strong>truncates toward zero</strong>.",
            "Every input is a valid expression.",
        ),
        examples=[
            ('tokens = ["2","1","+","3","*"]', "9", "(2 + 1) * 3"),
            ('tokens = ["4","13","5","/","+"]', "6", "4 + (13 / 5) = 4 + 2"),
        ],
        constraints=[
            "1 <= tokens.length <= 10^4",
            "Division by zero never occurs.",
            "All values fit in 32 bits.",
        ],
        todo="Evaluate the expression and return an int.",
        solution="""
            def eval_rpn(tokens: list[str]) -> int:
                stack = []
                for token in tokens:
                    if token in {"+", "-", "*", "/"}:
                        right = stack.pop()
                        left = stack.pop()
                        if token == "+":
                            stack.append(left + right)
                        elif token == "-":
                            stack.append(left - right)
                        elif token == "*":
                            stack.append(left * right)
                        else:
                            stack.append(int(left / right))
                    else:
                        stack.append(int(token))
                return stack[0]
        """,
        trace=2,
        cases=[
            ('["2", "1", "+", "3", "*"]', "9", False),
            ('["4", "13", "5", "/", "+"]', "6", False),
            (
                '["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]',
                "22",
                True,
            ),
            ('["7", "-3", "/"]', "-2", True),
            ('["18"]', "18", True),
        ],
        hints=(
            "An operator always applies to the two most recent results.",
            "Push numbers on a stack. On an operator, pop two, apply it, push the answer.",
            "Pop the right operand first, then the left. Use <code>int(left / right)</code> "
            "to truncate toward zero.",
        ),
        approaches=[
            (
                "Stack of operands",
                "Numbers are pushed; operators pop two values and push one.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Pop right first: the operand pushed last is the right-hand side. "
                "That matters for - and /.",
                False,
            ),
            (
                14,
                "int() of a float truncates toward zero, which is the rule this problem asks for. "
                "// would round down instead.",
                False,
            ),
        ],
        predictions=[
            (
                14,
                "In the second example, what does 13 / 5 become after int()?",
                "2: int() truncates 2.6.",
            ),
        ],
        patterns=["Stack"],
        techniques=["Stack", "Type Conversion"],
    ),
    problem(
        slug="binary-search",
        title="Binary Search",
        topic="binary-search",
        difficulty="easy",
        fn="search",
        signature="(nums: list[int], target: int) -> int",
        description=html(
            "Given a list <code>nums</code> sorted in ascending order and an integer "
            "<code>target</code>, return the index of <code>target</code> in <code>nums</code>, "
            "or <code>-1</code> if it is not there.",
            "Your solution must run in O(log n) time.",
        ),
        examples=[
            ("nums = [-1,0,3,5,9,12], target = 9", "4", "9 is at index 4."),
            ("nums = [-1,0,3,5,9,12], target = 2", "-1", "2 is not in the list."),
        ],
        constraints=[
            "1 <= nums.length <= 10^4",
            "All values are distinct and sorted ascending.",
        ],
        todo="Return the index of target, or -1.",
        solution="""
            def search(nums: list[int], target: int) -> int:
                low, high = 0, len(nums) - 1
                while low <= high:
                    mid = (low + high) // 2
                    if nums[mid] == target:
                        return mid
                    if nums[mid] < target:
                        low = mid + 1
                    else:
                        high = mid - 1
                return -1
        """,
        cases=[
            ("[-1, 0, 3, 5, 9, 12], 9", "4", False),
            ("[-1, 0, 3, 5, 9, 12], 2", "-1", False),
            ("[5], 5", "0", True),
            ("[5], -5", "-1", True),
            ("[1, 3, 5, 7, 9, 11, 13], 13", "6", True),
        ],
        hints=(
            "Because the list is sorted, one comparison can rule out half of it.",
            "Keep a range <code>[low, high]</code>. Look at the middle element and "
            "discard the half that cannot contain the target.",
            "If <code>nums[mid] &lt; target</code> set <code>low = mid + 1</code>, "
            "otherwise <code>high = mid - 1</code>. Stop when <code>low &gt; high</code>.",
        ),
        approaches=[
            (
                "Linear scan",
                "<code>nums.index(target)</code> or a loop. Ignores the sorting.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Binary search",
                "Halve the search range on every step.",
                "O(log n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "Looking at the middle rules out half of what is left every time. "
                "That is why it takes about log n steps.",
                True,
            ),
        ],
        predictions=[
            (
                4,
                "On the first pass for [-1, 0, 3, 5, 9, 12] and target 9, what is mid?",
                "2, because (0 + 5) // 2 = 2. nums[2] is 3, which is too small.",
            ),
        ],
        patterns=["Binary Search"],
        techniques=["Integer Division"],
    ),
    problem(
        slug="search-insert-position",
        title="Search Insert Position",
        topic="binary-search",
        difficulty="easy",
        fn="search_insert",
        signature="(nums: list[int], target: int) -> int",
        description=html(
            "Given a sorted list of <strong>distinct</strong> integers and a <code>target</code>, "
            "return the index where <code>target</code> is, or the index where it would be "
            "inserted to keep the list sorted.",
            "Your solution must run in O(log n) time.",
        ),
        examples=[
            ("nums = [1,3,5,6], target = 5", "2", ""),
            ("nums = [1,3,5,6], target = 2", "1", "2 would go between 1 and 3."),
        ],
        constraints=[
            "1 <= nums.length <= 10^4",
            "nums is sorted ascending with distinct values.",
        ],
        todo="Return the index of target, or where it would be inserted.",
        solution="""
            def search_insert(nums: list[int], target: int) -> int:
                low, high = 0, len(nums)
                while low < high:
                    mid = (low + high) // 2
                    if nums[mid] < target:
                        low = mid + 1
                    else:
                        high = mid
                return low
        """,
        cases=[
            ("[1, 3, 5, 6], 5", "2", False),
            ("[1, 3, 5, 6], 2", "1", False),
            ("[1, 3, 5, 6], 7", "4", True),
            ("[1, 3, 5, 6], 0", "0", True),
            ("[1], 1", "0", True),
            ("[2, 4, 6, 8, 10], 9", "4", True),
        ],
        hints=(
            "You want the first position whose value is not smaller than the target.",
            "Binary search over <code>[0, len(nums)]</code>: if <code>nums[mid]</code> is too small, "
            "the answer is to its right; otherwise <code>mid</code> could be the answer.",
            "Use <code>high = mid</code> (not <code>mid - 1</code>) when <code>nums[mid] &gt;= target</code>, "
            "and loop while <code>low &lt; high</code>.",
        ),
        approaches=[
            (
                "Linear scan",
                "Return the first index whose value is at least the target.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Binary search for the first value ≥ target",
                "Narrow a half-open range until low meets high.",
                "O(log n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "high = mid, not mid - 1: mid itself might be the spot where the target belongs.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "When the loop ends, how do low and high compare?",
                "They are equal. Both point at the insertion index.",
            ),
        ],
        patterns=["Binary Search"],
        techniques=["Integer Division"],
    ),
    problem(
        slug="koko-eating-bananas",
        title="Koko Eating Bananas",
        topic="binary-search",
        difficulty="medium",
        fn="min_eating_speed",
        signature="(piles: list[int], h: int) -> int",
        description=html(
            "Koko has piles of bananas: <code>piles[i]</code> bananas in pile <code>i</code>. "
            "She eats at a speed of <code>k</code> bananas per hour. "
            "Each hour she picks <strong>one</strong> pile and eats up to <code>k</code> bananas from it; "
            "if the pile has fewer, she finishes it and waits out the rest of the hour.",
            "Return the <strong>smallest</strong> integer speed <code>k</code> with which she "
            "finishes all piles within <code>h</code> hours.",
        ),
        examples=[
            ("piles = [3,6,7,11], h = 8", "4", ""),
            ("piles = [30,11,23,4,20], h = 5", "30", "She needs one hour per pile."),
        ],
        constraints=["1 <= piles.length <= h <= 10^9", "1 <= piles[i] <= 10^9"],
        todo="Return the smallest eating speed that finishes within h hours.",
        solution="""
            def min_eating_speed(piles: list[int], h: int) -> int:
                low, high = 1, max(piles)
                while low < high:
                    speed = (low + high) // 2
                    hours = 0
                    for pile in piles:
                        hours += (pile + speed - 1) // speed
                    if hours <= h:
                        high = speed
                    else:
                        low = speed + 1
                return low
        """,
        cases=[
            ("[3, 6, 7, 11], 8", "4", False),
            ("[30, 11, 23, 4, 20], 5", "30", False),
            ("[30, 11, 23, 4, 20], 6", "23", True),
            ("[1], 1", "1", True),
            ("[312884470], 312884469", "2", True),
        ],
        hints=(
            "Trying every speed from 1 upwards works but could take a billion steps.",
            "If a speed is fast enough, every faster speed is too. That makes the "
            "<em>answer itself</em> something you can binary search for.",
            "Search speeds between 1 and <code>max(piles)</code>. For a speed, hours needed is the "
            "sum of <code>ceil(pile / speed)</code>, written as <code>(pile + speed - 1) // speed</code>.",
        ),
        approaches=[
            (
                "Try every speed",
                "Increase the speed until the hours fit.",
                "O(max(piles) · n)",
                "O(1)",
                False,
            ),
            (
                "Binary search on the answer",
                "Test the middle speed. If it is fast enough, shrink the upper bound; "
                "otherwise raise the lower bound.",
                "O(n log max(piles))",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "If a speed finishes in time, every faster speed does too. "
                "That monotonic property is what makes binary search legal here.",
                True,
            ),
        ],
        predictions=[
            (
                8,
                "On the first pass for [3, 6, 7, 11] (speed 6), how many hours does Koko need?",
                "6 (1 + 1 + 2 + 2). That is within 8, so high becomes 6.",
            ),
        ],
        patterns=["Binary Search"],
        techniques=["Ceiling Division"],
    ),
]
