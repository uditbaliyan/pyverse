# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="sliding-window-maximum",
        title="Sliding Window Maximum",
        topic="stack",
        difficulty="hard",
        fn="max_sliding_window",
        signature="(nums: list[int], k: int) -> list[int]",
        description=html(
            "A window of size <code>k</code> starts at the left end of <code>nums</code> and moves one position right each step until it reaches the right end.",
            "Return the maximum value inside the window for every position it takes.",
        ),
        examples=[
            (
                "nums = [4, 2, 12, 3, 8, 1], k = 3",
                "[12, 12, 12, 8]",
                "Windows: [4,2,12], [2,12,3], [12,3,8], [3,8,1]",
            ),
        ],
        constraints=["1 <= k <= len(nums) <= 10^5", "-10^4 <= nums[i] <= 10^4"],
        todo="Keep a list of indices whose values decrease from front to back; the front index is always the window maximum.",
        solution="""
            def max_sliding_window(nums: list[int], k: int) -> list[int]:
                window = []
                head = 0
                result = []
                for i, x in enumerate(nums):
                    if head < len(window) and window[head] <= i - k:
                        head += 1
                    while head < len(window) and nums[window[-1]] <= x:
                        window.pop()
                    window.append(i)
                    if i >= k - 1:
                        result.append(nums[window[head]])
                return result
        """,
        trace=1,
        cases=[
            ("[4, 2, 12, 3, 8, 1], 3", "[12, 12, 12, 8]", False),
            ("[1], 1", "[1]", False),
            ("[9, 11], 2", "[11]", False),
            ("[1, -1], 1", "[1, -1]", True),
            ("[5, 4, 3, 2, 1], 2", "[5, 4, 3, 2]", True),
            ("[1, 2, 3, 4, 5], 3", "[3, 4, 5]", True),
        ],
        hints=(
            "Recomputing the maximum of every window costs O(k) each time. What information could you keep between windows?",
            "Keep candidate indices in decreasing order of value. A new value makes every smaller earlier value useless, and an index that slid out of the window must be dropped from the front.",
            "Here the front is tracked by <code>head</code> (a list does not pop from the front cheaply): advance it when the front index leaves the window, pop from the back while values are not larger than the new one.",
        ),
        approaches=[
            (
                "Max of every window",
                "Call max on each slice.",
                "O(n * k)",
                "O(1)",
                False,
            ),
            (
                "Monotonic deque of indices",
                "Each index is added and removed at most once; the front is the answer.",
                "O(n)",
                "O(k)",
                True,
            ),
        ],
        notes=[
            (
                9,
                "Values not larger than x can never be the maximum while x is in the window, and x leaves later than they do, so they are discarded.",
                False,
            ),
        ],
        predictions=[
            (
                12,
                "For [4, 2, 12, 3, 8, 1] and k = 3, what is window the first time this line is reached?",
                "[2]: the 12 removed both earlier, smaller values.",
            ),
        ],
        patterns=["Monotonic Stack", "Sliding Window"],
        techniques=["Monotonic Deque", "Index Stack"],
    ),
    problem(
        slug="trapping-rain-water",
        title="Trapping Rain Water",
        topic="stack",
        difficulty="hard",
        fn="trap",
        signature="(height: list[int]) -> int",
        description=html(
            "<code>height[i]</code> is the height of a wall of width 1 at position <code>i</code>. After rain, water collects in the dips between walls.",
            "Return the total number of unit squares of water that stay trapped.",
        ),
        examples=[
            (
                "height = [3, 0, 2, 0, 4]",
                "7",
                "Water levels of 3, 1 and 3 above the dips at indices 1, 2 and 3",
            ),
        ],
        constraints=["1 <= len(height) <= 2 * 10^4", "0 <= height[i] <= 10^5"],
        todo="Keep a stack of decreasing wall indices; when a taller wall arrives, fill the basin between it and the previous wall on the stack.",
        solution="""
            def trap(height: list[int]) -> int:
                stack = []
                water = 0
                for i, h in enumerate(height):
                    while stack and height[stack[-1]] < h:
                        bottom = stack.pop()
                        if not stack:
                            break
                        width = i - stack[-1] - 1
                        water += width * (min(height[stack[-1]], h) - height[bottom])
                    stack.append(i)
                return water
        """,
        trace=1,
        cases=[
            ("[3, 0, 2, 0, 4]", "7", False),
            ("[2, 0, 2]", "2", False),
            ("[1, 2, 3]", "0", False),
            ("[4, 2, 3]", "1", True),
            ("[5, 4, 1, 2]", "1", True),
            ("[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]", "6", True),
            ("[5]", "0", True),
        ],
        hints=(
            "Water sits above a column only if there are taller walls on both sides. What decides the level?",
            "Think in horizontal layers: when a wall higher than the previous ones appears, it closes a basin with the wall before the bottom.",
            "Keep indices of non-increasing heights. On a taller wall pop the bottom, then the new top is the left wall; add width times (min(left, right) - bottom).",
        ),
        approaches=[
            (
                "Per-column max on both sides",
                "For each column take the lower of the tallest wall to its left and right.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Monotonic stack",
                "Fill the water one basin layer at a time as walls close them.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "With nothing left on the stack there is no left wall, so the popped column cannot hold water.",
                False,
            ),
        ],
        predictions=[
            (
                10,
                "For [3, 0, 2, 0, 4], what is width the third time this line is reached?",
                "3: the basin between index 0 and index 4 is three columns wide.",
            ),
        ],
        patterns=["Monotonic Stack", "Two Pointers"],
        techniques=["Decreasing Stack", "Layer Filling"],
    ),
    problem(
        slug="largest-rectangle-in-a-histogram",
        title="Largest Rectangle in a Histogram",
        topic="stack",
        difficulty="hard",
        fn="largest_rectangle",
        signature="(heights: list[int]) -> int",
        description=html(
            "A histogram has bars of width 1 with the given <code>heights</code>.",
            "Return the area of the largest rectangle that fits entirely inside the histogram.",
        ),
        examples=[
            (
                "heights = [3, 1, 3, 2, 2]",
                "6",
                "The last three bars (3, 2, 2) are all at least 2 tall: 2 * 3",
            ),
        ],
        constraints=["1 <= len(heights) <= 10^5", "0 <= heights[i] <= 10^4"],
        todo="Use a stack of increasing bar indices; when a shorter bar arrives, pop taller bars and compute the rectangle each one spans.",
        solution="""
            def largest_rectangle(heights: list[int]) -> int:
                stack = []
                best = 0
                for i in range(len(heights) + 1):
                    current = heights[i] if i < len(heights) else 0
                    while stack and heights[stack[-1]] >= current:
                        height = heights[stack.pop()]
                        left = stack[-1] if stack else -1
                        best = max(best, height * (i - left - 1))
                    stack.append(i)
                return best
        """,
        trace=1,
        cases=[
            ("[3, 1, 3, 2, 2]", "6", False),
            ("[2, 4]", "4", False),
            ("[2, 1, 5, 6, 2, 3]", "10", True),
            ("[3, 3, 3]", "9", True),
            ("[5, 4, 3, 2, 1]", "9", True),
            ("[0, 0]", "0", True),
            ("[6, 2, 5, 4, 5, 1, 6]", "12", True),
        ],
        hints=(
            "For a bar of height h, the biggest rectangle using that bar as its height stretches left and right until it meets a shorter bar.",
            "A stack of increasing heights finds both boundaries: the shorter bar that pops an entry is the right boundary, the new top is the left boundary.",
            "Append a bar of height 0 at the end so every bar gets popped, and measure the width as <code>i - left - 1</code>.",
        ),
        approaches=[
            (
                "Expand from each bar",
                "Walk left and right from every bar until a shorter one appears.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Monotonic stack",
                "Each bar is pushed and popped once, and its rectangle is computed on the pop.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                9,
                "The popped bar is the shortest in the span (left, i), so its height times that width is a valid rectangle.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For [3, 1, 3, 2, 2], what are height and left the fourth time this line is reached?",
                "height = 2 and left = 1, so the width is 5 - 1 - 1 = 3 and the area is 6.",
            ),
        ],
        patterns=["Monotonic Stack"],
        techniques=["Increasing Stack", "Sentinel Value"],
    ),
    problem(
        slug="maximal-rectangle",
        title="Maximal Rectangle",
        topic="stack",
        difficulty="hard",
        fn="maximal_rectangle",
        signature="(matrix: list[list[int]]) -> int",
        description=html(
            "<code>matrix</code> is a grid of 0s and 1s. Return the area of the largest rectangle that contains only 1s.",
        ),
        examples=[
            (
                "matrix = [[1, 0, 1], [1, 1, 1], [1, 1, 1]]",
                "6",
                "The bottom two rows form a 2 x 3 block of ones",
            ),
        ],
        constraints=["1 <= rows, cols <= 200", "matrix[i][j] is 0 or 1"],
        todo="Turn each row into a histogram of consecutive ones above it, and solve largest-rectangle on that histogram.",
        solution="""
            def maximal_rectangle(matrix: list[list[int]]) -> int:
                heights = [0] * len(matrix[0])
                best = 0
                for row in matrix:
                    for j, cell in enumerate(row):
                        heights[j] = heights[j] + 1 if cell == 1 else 0
                    stack = []
                    for i in range(len(heights) + 1):
                        current = heights[i] if i < len(heights) else 0
                        while stack and heights[stack[-1]] >= current:
                            height = heights[stack.pop()]
                            left = stack[-1] if stack else -1
                            best = max(best, height * (i - left - 1))
                        stack.append(i)
                return best
        """,
        trace=1,
        cases=[
            ("[[1, 1], [1, 1]]", "4", False),
            ("[[1, 0, 1], [1, 1, 1], [1, 1, 1]]", "6", False),
            ("[[0]]", "0", False),
            ("[[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]", "6", True),
            ("[[0, 0], [0, 0]]", "0", True),
            ("[[1, 1, 1, 1]]", "4", True),
        ],
        hints=(
            "Fix the bottom row of the rectangle. What does the grid above it look like as bars?",
            "For every column, count how many consecutive ones end at the current row; that is a histogram.",
            "Update the heights row by row (reset to 0 on a zero cell) and run the largest-rectangle stack scan on each histogram.",
        ),
        approaches=[
            (
                "Check every rectangle",
                "Try all pairs of corners and verify they hold only ones.",
                "O(rows^2 * cols^2)",
                "O(1)",
                False,
            ),
            (
                "Histogram per row",
                "Reuse the largest-rectangle stack scan for each row's heights.",
                "O(rows * cols)",
                "O(cols)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "A 1 extends the column of ones by one; a 0 breaks it, so the height resets to zero.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [[1, 1], [1, 1]], what is heights the second time this line is reached?",
                "[2, 2]: both columns now have two consecutive ones.",
            ),
        ],
        patterns=["Monotonic Stack", "Matrix"],
        techniques=["Histogram Reduction", "Sentinel Value"],
    ),
    problem(
        slug="stock-span-problem",
        title="Stock Span Problem",
        topic="stack",
        difficulty="medium",
        fn="stock_span",
        signature="(prices: list[int]) -> list[int]",
        description=html(
            "<code>prices[i]</code> is a stock's price on day <code>i</code>. The span of a day is the number of consecutive days ending on that day (the day itself included) whose price is less than or equal to that day's price.",
            "Return the span for every day.",
        ),
        examples=[
            (
                "prices = [31, 27, 14, 21, 18, 26, 35]",
                "[1, 1, 1, 2, 1, 4, 7]",
                "The 26 on day 5 covers 18, 21, 14 and itself; 27 blocks it",
            ),
        ],
        constraints=["1 <= len(prices) <= 10^5", "1 <= prices[i] <= 10^5"],
        todo="Keep a stack of days with prices greater than everything after them; the span is the distance to the day left on top.",
        solution="""
            def stock_span(prices: list[int]) -> list[int]:
                spans = []
                stack = []
                for i, price in enumerate(prices):
                    while stack and prices[stack[-1]] <= price:
                        stack.pop()
                    spans.append(i - stack[-1] if stack else i + 1)
                    stack.append(i)
                return spans
        """,
        trace=1,
        cases=[
            ("[31, 27, 14, 21, 18, 26, 35]", "[1, 1, 1, 2, 1, 4, 7]", False),
            ("[10, 20, 30]", "[1, 2, 3]", False),
            ("[30, 20, 10]", "[1, 1, 1]", False),
            ("[5]", "[1]", True),
            ("[7, 7, 7, 7]", "[1, 2, 3, 4]", True),
            ("[3, 1, 2, 5, 4]", "[1, 1, 2, 4, 1]", True),
        ],
        hints=(
            "The span of a day ends where a strictly higher price appears to the left. What are you really looking for?",
            "You want the previous day with a greater price. Days with a price not greater than today's can never matter for later days either.",
            "Pop those days off the stack; the span is the distance from today to the new top (or i + 1 if the stack is empty).",
        ),
        approaches=[
            (
                "Walk back each day",
                "Step left until a greater price is found.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Monotonic stack",
                "Maintain days with strictly decreasing prices.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "After the pops the top is the previous strictly greater price, so everything between it and today is covered by today's span.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [31, 27, 14, 21, 18, 26, 35], what is stack the fourth time this line is reached?",
                "[0, 1]: day 2 (price 14) was popped because 21 covers it.",
            ),
        ],
        patterns=["Monotonic Stack"],
        techniques=["Decreasing Stack", "Conditional Expression"],
    ),
    problem(
        slug="celebrity-problem",
        title="Celebrity Problem",
        topic="stack",
        difficulty="medium",
        fn="find_celebrity",
        signature="(knows: list[list[int]]) -> int",
        description=html(
            "At a party of <code>n</code> people, <code>knows[i][j] == 1</code> means person <code>i</code> knows person <code>j</code> (the relation is not necessarily symmetric).",
            "A celebrity is known by everyone else and knows nobody. Return the celebrity's index, or <code>-1</code> if there is none.",
        ),
        examples=[
            (
                "knows = [[0, 1, 0], [0, 0, 0], [0, 1, 0]]",
                "1",
                "Persons 0 and 2 know person 1, who knows nobody",
            ),
        ],
        constraints=["1 <= n <= 1000", "knows[i][i] == 0", "knows[i][j] is 0 or 1"],
        todo="Eliminate candidates in one pass: if the candidate knows i, the candidate is out; then verify the survivor.",
        solution="""
            def find_celebrity(knows: list[list[int]]) -> int:
                n = len(knows)
                candidate = 0
                for i in range(1, n):
                    if knows[candidate][i] == 1:
                        candidate = i
                for i in range(n):
                    if i != candidate and (knows[candidate][i] == 1 or knows[i][candidate] == 0):
                        return -1
                return candidate
        """,
        trace=1,
        cases=[
            ("[[0, 1, 0], [0, 0, 0], [0, 1, 0]]", "1", False),
            ("[[0, 1], [1, 0]]", "-1", False),
            ("[[0, 0], [1, 0]]", "0", False),
            ("[[0]]", "0", True),
            ("[[0, 0, 0], [0, 0, 0], [0, 0, 0]]", "-1", True),
            ("[[0, 1, 1], [0, 0, 1], [0, 0, 0]]", "2", True),
        ],
        hints=(
            "Pick two people a and b and ask whether a knows b. Whatever the answer, one of them can no longer be the celebrity. Which one?",
            "If a knows b, a is not a celebrity; if a does not know b, b is not one. So one question removes one candidate.",
            "After eliminating down to a single candidate, check that nobody the candidate knows is left and everyone knows the candidate.",
        ),
        approaches=[
            (
                "Check every person",
                "For each person verify the full row and column.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            (
                "Eliminate, then verify",
                "n - 1 questions leave one candidate; 2(n - 1) more confirm it.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "If the candidate knows i, the candidate cannot be the celebrity, but i still might be.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [[0, 1, 0], [0, 0, 0], [0, 1, 0]], what is candidate the first time this line is reached?",
                "1: person 0 knows person 1, so 0 is ruled out.",
            ),
        ],
        patterns=["Elimination", "Stack"],
        techniques=["Candidate Elimination", "Two Pass Verification"],
    ),
    problem(
        slug="infix-to-postfix-conversion",
        title="Infix to Postfix Conversion",
        topic="stack",
        difficulty="medium",
        fn="infix_to_postfix",
        signature="(expression: str) -> str",
        description=html(
            "Convert an infix expression to postfix (reverse Polish) notation. Operands are single letters or digits; operators are <code>+ - * / ^</code> and parentheses may appear.",
            "<code>^</code> has the highest precedence and is right-associative, <code>* /</code> come next and <code>+ -</code> are lowest; the other operators are left-associative. The expression has no spaces.",
        ),
        examples=[
            (
                'expression = "(a+b)*c"',
                '"ab+c*"',
                "The sum happens first because of the parentheses",
            ),
        ],
        constraints=["1 <= len(expression) <= 1000", "Valid expression, no spaces"],
        todo="Send operands straight to the output; use a stack of operators and pop higher-precedence ones first.",
        solution="""
            def infix_to_postfix(expression: str) -> str:
                precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
                output = []
                stack = []
                for ch in expression:
                    if ch.isalnum():
                        output.append(ch)
                    elif ch == "(":
                        stack.append(ch)
                    elif ch == ")":
                        while stack[-1] != "(":
                            output.append(stack.pop())
                        stack.pop()
                    else:
                        while stack and stack[-1] != "(" and (precedence[stack[-1]] > precedence[ch] or (precedence[stack[-1]] == precedence[ch] and ch != "^")):
                            output.append(stack.pop())
                        stack.append(ch)
                while stack:
                    output.append(stack.pop())
                return "".join(output)
        """,
        trace=1,
        cases=[
            ('"(a+b)*c"', '"ab+c*"', False),
            ('"a+b*c"', '"abc*+"', False),
            ('"a^b^c"', '"abc^^"', False),
            ('"a-b-c"', '"ab-c-"', True),
            ('"a"', '"a"', True),
            ('"a+b*(c^d-e)^(f+g*h)-i"', '"abcd^e-fgh*+^*+i-"', True),
        ],
        hints=(
            "Operands never need to wait: they go straight to the output in their original order.",
            "Operators wait on a stack. Before pushing a new operator, pop the ones that must be applied first (higher precedence, or equal precedence when the operator is left-associative).",
            "An opening parenthesis is pushed and never popped by an operator; a closing parenthesis pops everything back to the matching opening one.",
        ),
        approaches=[
            (
                "Build a tree, then walk it",
                "Parse into an expression tree and emit a post-order walk.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Shunting-yard with a stack",
                "A single left-to-right pass with an operator stack.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                14,
                "Equal precedence pops only for left-associative operators; ^ is right-associative, so a^b^c keeps the first ^ waiting.",
                False,
            ),
        ],
        predictions=[
            (
                13,
                'For "(a+b)*c", what is output the first time this line is reached?',
                "['a', 'b', '+']: the sum was emitted before the parenthesis is discarded.",
            ),
        ],
        patterns=["Stack", "Parsing"],
        techniques=["Operator Precedence", "Shunting Yard"],
    ),
]
