# ruff: noqa: E501
"""Matrix Patterns: grids built row by row. Rows are returned, not printed."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="alternating-bits-grid",
        title="Alternating 0 and 1 Grid",
        topic="matrix-patterns",
        difficulty="medium",
        fn="bit_grid",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an <code>n</code> by <code>n</code> grid of <code>0</code>s and <code>1</code>s that alternates along both rows and columns, with <code>0</code> in the top-left corner. Each row is one string of digits.",
            "<pre>0101\n1010\n0101\n1010</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 4",
                '["0101", "1010", "0101", "1010"]',
                "Every neighbour (left, right, up, down) differs.",
            ),
        ],
        constraints=["1 <= n <= 30"],
        todo="Decide each cell's digit from its row and column.",
        solution="""
            def bit_grid(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    line = ""
                    for col in range(n):
                        line += str((row + col) % 2)
                    rows.append(line)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['0101', '1010', '0101', '1010']", False),
            ("3", "['010', '101', '010']", False),
            ("1", "['0']", True),
            ("2", "['01', '10']", True),
            (
                "7",
                "['0101010', '1010101', '0101010', '1010101', '0101010', '1010101', '0101010']",
                True,
            ),
        ],
        hints=(
            "Look at a cell's row number plus its column number. What do neighbouring cells have in common?",
            "Moving one step right or down changes <code>row + col</code> by 1, so its parity flips.",
            "The digit for a cell is <code>(row + col) % 2</code>.",
        ),
        approaches=[
            (
                "Flip a flag",
                "Toggle a variable after every cell (needs care at the start of each row when n is even).",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Parity of row + col",
                "One formula per cell, no state to track.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "Any step right or down changes row + col by exactly 1, so its parity (the remainder mod 2) flips. That is the whole alternation rule.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For n = 4, when row is 1 and this line is reached, what is line?",
                '"1010"',
            ),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["Modulo", "Nested Loops"],
    ),
    problem(
        slug="pascals-triangle",
        title="Pascal's Triangle",
        topic="matrix-patterns",
        difficulty="medium",
        fn="pascal_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build the first <code>n</code> rows of Pascal's triangle. Every row starts and ends with 1; every other entry is the sum of the two entries just above it. Write each row with its numbers separated by single spaces, and put <code>n - 1 - r</code> leading spaces in front of row <code>r</code> (counting from 0).",
            "<pre>   1\n  1 1\n 1 2 1\n1 3 3 1</pre>",
            "Return the rows as a list of strings; do not print them. The indent is fixed by the rule above even when numbers get wider than one digit, so rows with larger numbers will not look perfectly centred.",
        ),
        examples=[
            (
                "n = 4",
                '["   1", "  1 1", " 1 2 1", "1 3 3 1"]',
                "Row 3 is 1 3 3 1: 1, 1+2, 2+1, 1.",
            ),
        ],
        constraints=["1 <= n <= 12"],
        todo="Build each row from the previous one, then format it.",
        solution="""
            def pascal_triangle(n: int) -> list[str]:
                rows = []
                previous = []
                for row in range(n):
                    current = [1] * (row + 1)
                    for col in range(1, row):
                        current[col] = previous[col - 1] + previous[col]
                    rows.append(" " * (n - 1 - row) + " ".join(map(str, current)))
                    previous = current
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['   1', '  1 1', ' 1 2 1', '1 3 3 1']", False),
            ("3", "['  1', ' 1 1', '1 2 1']", False),
            ("1", "['1']", True),
            ("2", "[' 1', '1 1']", True),
            (
                "6",
                "['     1', '    1 1', '   1 2 1', '  1 3 3 1', ' 1 4 6 4 1', '1 5 10 10 5 1']",
                True,
            ),
        ],
        hints=(
            "Each row can be computed from the row right above it. What do you have to remember between rows?",
            "Start a row as all 1s, then overwrite the inner entries with sums from the previous row.",
            "<code>current[col] = previous[col - 1] + previous[col]</code> for <code>col</code> from 1 to <code>row - 1</code>.",
        ),
        approaches=[
            (
                "Binomial coefficients",
                "Entry (r, c) is <code>math.comb(r, c)</code>; no previous row needed.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Row from previous row",
                "Keep the last row and add neighbouring pairs.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Only the inner entries need a sum; the two 1s at the ends were already placed by [1] * (row + 1).",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "When row is 3 and this line is reached, what is current?",
                "[1, 3, 3, 1]",
            ),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["List Comprehension", "Nested Loops"],
    ),
    problem(
        slug="consecutive-number-grid",
        title="Grid of Consecutive Numbers",
        topic="matrix-patterns",
        difficulty="medium",
        fn="number_grid",
        signature="(n: int) -> list[str]",
        description=html(
            "Fill an <code>n</code> by <code>n</code> grid with the numbers 1, 2, 3, ... going left to right, row by row. Write each row as its numbers separated by single spaces.",
            "<pre>1 2 3\n4 5 6\n7 8 9</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 3",
                '["1 2 3", "4 5 6", "7 8 9"]',
                "Row 2 continues from where row 1 stopped.",
            ),
        ],
        constraints=["1 <= n <= 30"],
        todo="Keep one running counter; collect each row's numbers, then join them with spaces.",
        solution="""
            def number_grid(n: int) -> list[str]:
                rows = []
                number = 1
                for _ in range(n):
                    cells = []
                    for _ in range(n):
                        cells.append(str(number))
                        number += 1
                    rows.append(" ".join(cells))
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['1 2 3', '4 5 6', '7 8 9']", False),
            ("4", "['1 2 3 4', '5 6 7 8', '9 10 11 12', '13 14 15 16']", False),
            ("1", "['1']", True),
            ("2", "['1 2', '3 4']", True),
            (
                "6",
                "['1 2 3 4 5 6', '7 8 9 10 11 12', '13 14 15 16 17 18', '19 20 21 22 23 24', '25 26 27 28 29 30', '31 32 33 34 35 36']",
                True,
            ),
        ],
        hints=(
            "You need a counter that survives from one row to the next.",
            "Collect each row's numbers in a list of strings, then turn the list into one line.",
            '<code>" ".join(cells)</code> glues the strings together with single spaces.',
        ),
        approaches=[
            (
                "Arithmetic",
                "Cell (r, c) holds <code>r * n + c + 1</code>.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Running counter",
                "Count up while filling, joining each row at the end.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                9,
                "join glues the strings with a single space between them and none at the ends, so rows never end with a stray space.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "On the second row (the second time this line is reached), what is cells?",
                '["4", "5", "6"]',
            ),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["Accumulator", "String Methods", "Nested Loops"],
    ),
    problem(
        slug="checkerboard-grid",
        title="Checkerboard Pattern",
        topic="matrix-patterns",
        difficulty="medium",
        fn="checkerboard",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an <code>n</code> by <code>n</code> checkerboard from the letters <code>X</code> and <code>O</code>. The top-left square is <code>X</code> and no two squares that share an edge have the same letter.",
            "<pre>XOXO\nOXOX\nXOXO\nOXOX</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 4",
                '["XOXO", "OXOX", "XOXO", "OXOX"]',
                "Rows alternate between XOXO and OXOX.",
            ),
        ],
        constraints=["1 <= n <= 30"],
        todo="Pick X or O for every square from its row and column.",
        solution="""
            def checkerboard(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    line = ""
                    for col in range(n):
                        if (row + col) % 2 == 0:
                            line += "X"
                        else:
                            line += "O"
                    rows.append(line)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['XOXO', 'OXOX', 'XOXO', 'OXOX']", False),
            ("3", "['XOX', 'OXO', 'XOX']", False),
            ("1", "['X']", True),
            ("2", "['XO', 'OX']", True),
            (
                "7",
                "['XOXOXOX', 'OXOXOXO', 'XOXOXOX', 'OXOXOXO', 'XOXOXOX', 'OXOXOXO', 'XOXOXOX']",
                True,
            ),
        ],
        hints=(
            "Which squares share a letter with the top-left corner?",
            "Squares of the same colour have the same parity of row + col.",
            'If <code>(row + col) % 2 == 0</code> add "X", otherwise "O".',
        ),
        approaches=[
            ("Parity test", "Even row + col is X, odd is O.", "O(n^2)", "O(n^2)", True),
            (
                "Two row templates",
                'Build "XOXO..." and "OXOX..." once and alternate them.',
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                6,
                "Squares of one colour all have the same parity of row + col, so one test picks the letter.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For n = 4, how many times is this line reached?",
                "8: half of the 16 squares.",
            ),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["Modulo", "Nested Loops"],
    ),
    problem(
        slug="number-border-frame",
        title="Number Frame",
        topic="matrix-patterns",
        difficulty="medium",
        fn="number_frame",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an <code>n</code> by <code>n</code> frame. The top and bottom rows read <code>1 2 ... n</code> written without spaces. Every row in between is a <code>1</code> at each end with spaces in the middle.",
            "<pre>1234\n1  1\n1  1\n1234</pre>",
            'Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row. For <code>n = 1</code> the answer is <code>["1"]</code>.',
        ),
        examples=[
            (
                "n = 4",
                '["1234", "1  1", "1  1", "1234"]',
                "Top and bottom are 1234; middle rows are 1, two spaces, 1.",
            ),
        ],
        constraints=["1 <= n <= 9"],
        todo="Build the solid border row once, then decide for every row which kind it is.",
        solution="""
            def number_frame(n: int) -> list[str]:
                edge = ""
                for digit in range(1, n + 1):
                    edge += str(digit)
                rows = []
                for row in range(n):
                    if row == 0 or row == n - 1:
                        rows.append(edge)
                    else:
                        rows.append("1" + " " * (n - 2) + "1")
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['1234', '1  1', '1  1', '1234']", False),
            ("5", "['12345', '1   1', '1   1', '1   1', '12345']", False),
            ("1", "['1']", True),
            ("2", "['12', '12']", True),
            ("3", "['123', '1 1', '123']", True),
            (
                "9",
                "['123456789', '1       1', '1       1', '1       1', '1       1', '1       1', '1       1', '1       1', '123456789']",
                True,
            ),
        ],
        hints=(
            "There are only two kinds of row. Which are they?",
            "Compute the border row once before the loop, because it is reused twice.",
            'Middle rows are <code>"1" + " " * (n - 2) + "1"</code>.',
        ),
        approaches=[
            (
                "Test every cell",
                "Nested loops, with a condition for the border.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Two row types",
                "Build the border row once; middle rows come from string repetition.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "edge is finished before any row is built, so the top and bottom rows can just reuse it.",
                False,
            ),
        ],
        predictions=[
            (5, "For n = 4, when this line is reached, what is edge?", '"1234"'),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["String Repetition", "Accumulator"],
    ),
    problem(
        slug="spiral-matrix",
        title="Spiral Matrix",
        topic="matrix-patterns",
        difficulty="hard",
        fn="spiral_matrix",
        signature="(n: int) -> list[str]",
        description=html(
            "Fill an <code>n</code> by <code>n</code> grid with the numbers 1 to n*n, starting in the top-left corner and spiralling clockwise towards the centre: right along the top, down the right side, left along the bottom, up the left side, then repeat on the inner ring. Write each row as its numbers separated by single spaces.",
            "<pre>1 2 3\n8 9 4\n7 6 5</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 3",
                '["1 2 3", "8 9 4", "7 6 5"]',
                "1-2-3 across, 4-5 down, 6-7 back, 8 up, 9 in the middle.",
            ),
        ],
        constraints=["1 <= n <= 20"],
        todo="Fill the grid ring by ring, shrinking four boundaries as you go.",
        solution="""
            def spiral_matrix(n: int) -> list[str]:
                grid = [[0] * n for _ in range(n)]
                top, bottom, left, right = 0, n - 1, 0, n - 1
                number = 1
                while top <= bottom and left <= right:
                    for col in range(left, right + 1):
                        grid[top][col] = number
                        number += 1
                    top += 1
                    for row in range(top, bottom + 1):
                        grid[row][right] = number
                        number += 1
                    right -= 1
                    if top <= bottom:
                        for col in range(right, left - 1, -1):
                            grid[bottom][col] = number
                            number += 1
                        bottom -= 1
                    if left <= right:
                        for row in range(bottom, top - 1, -1):
                            grid[row][left] = number
                            number += 1
                        left += 1
                return [" ".join(map(str, row)) for row in grid]
        """,
        trace=1,
        cases=[
            ("3", "['1 2 3', '8 9 4', '7 6 5']", False),
            ("4", "['1 2 3 4', '12 13 14 5', '11 16 15 6', '10 9 8 7']", False),
            ("1", "['1']", True),
            ("2", "['1 2', '4 3']", True),
            (
                "5",
                "['1 2 3 4 5', '16 17 18 19 6', '15 24 25 20 7', '14 23 22 21 8', '13 12 11 10 9']",
                True,
            ),
            (
                "6",
                "['1 2 3 4 5 6', '20 21 22 23 24 7', '19 32 33 34 25 8', '18 31 36 35 26 9', '17 30 29 28 27 10', '16 15 14 13 12 11']",
                True,
            ),
        ],
        hints=(
            "Think in rings: the outer ring is walked, then the same job repeats on a smaller square.",
            "Keep four boundaries (top, bottom, left, right). After walking a side, move that boundary inwards.",
            "After the top row and right column, guard the bottom row and left column with <code>if top &lt;= bottom</code> / <code>if left &lt;= right</code> so a leftover single row or column is not walked twice.",
        ),
        approaches=[
            (
                "Walk and turn",
                "Move one cell at a time and turn right at an edge or a filled cell.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Shrinking boundaries",
                "Fill four sides per ring and tighten the boundaries.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                14,
                "After the top row and right column are done, the ring may have collapsed to a single row or column. This guard stops it being written twice.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For n = 3, when this line is first reached, what is grid[0]?",
                "[1, 2, 3]: the top row has just been filled.",
            ),
        ],
        patterns=["Simulation", "Matrix"],
        techniques=["Nested Loops", "Tuple Unpacking"],
    ),
    problem(
        slug="snake-matrix",
        title="Snake Matrix",
        topic="matrix-patterns",
        difficulty="medium",
        fn="snake_matrix",
        signature="(rows: int, cols: int) -> list[str]",
        description=html(
            "Fill a grid that has <code>rows</code> rows and <code>cols</code> columns with the numbers 1, 2, 3, ... in a snake. The first row runs left to right, the second runs right to left, the third left to right again, and so on. Write each row as its numbers separated by single spaces.",
            "<pre>1 2 3 4\n8 7 6 5\n9 10 11 12</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "rows = 3, cols = 4",
                '["1 2 3 4", "8 7 6 5", "9 10 11 12"]',
                "Row 2 is written backwards: 8 7 6 5.",
            ),
        ],
        constraints=["1 <= rows <= 20", "1 <= cols <= 20"],
        todo="Each row is a run of consecutive numbers; reverse every second row.",
        solution="""
            def snake_matrix(rows: int, cols: int) -> list[str]:
                result = []
                number = 1
                for row in range(rows):
                    values = list(range(number, number + cols))
                    number += cols
                    if row % 2 == 1:
                        values.reverse()
                    result.append(" ".join(map(str, values)))
                return result
        """,
        trace=1,
        cases=[
            ("3, 4", "['1 2 3 4', '8 7 6 5', '9 10 11 12']", False),
            ("2, 2", "['1 2', '4 3']", False),
            ("1, 5", "['1 2 3 4 5']", True),
            ("4, 1", "['1', '2', '3', '4']", True),
            ("2, 3", "['1 2 3', '6 5 4']", True),
        ],
        hints=(
            "Without the snake, every row would be a plain run of consecutive numbers.",
            "Create each row as a run, then reverse the rows with an odd index.",
            "<code>values = list(range(number, number + cols))</code>, and <code>values.reverse()</code> when <code>row % 2 == 1</code>.",
        ),
        approaches=[
            (
                "Formula per cell",
                "Compute each value from its row and column, mirroring the column on odd rows.",
                "O(rows * cols)",
                "O(rows * cols)",
                False,
            ),
            (
                "Run then reverse",
                "Make a normal run for each row and reverse the odd ones.",
                "O(rows * cols)",
                "O(rows * cols)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "Only odd rows are reversed, but number was already advanced past the row. The counting continues upwards while the direction alternates.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For rows = 3 and cols = 4, when row is 1 and this line is reached, what is values?",
                "[8, 7, 6, 5]",
            ),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["Modulo", "List Methods"],
    ),
]
