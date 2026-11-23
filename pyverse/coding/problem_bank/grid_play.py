# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="multiplication-tables-range",
        title="Multiplication Tables for a Range",
        topic="grid-play",
        difficulty="easy",
        fn="multiplication_tables",
        signature="(start: int, end: int, upto: int) -> list[list[str]]",
        description=html(
            "Build a table of multiplication facts for every number from <code>start</code> to <code>end</code> (inclusive).",
            'Return one row per multiplier <code>k = 1..upto</code>. Each row is a list of strings <code>"n x k = product"</code>, one for each <code>n</code> from <code>start</code> to <code>end</code>, in increasing order of <code>n</code>.',
        ),
        examples=[
            (
                "start = 2, end = 4, upto = 2",
                '[["2 x 1 = 2", "3 x 1 = 3", "4 x 1 = 4"], ["2 x 2 = 4", "3 x 2 = 6", "4 x 2 = 8"]]',
                "Row 1 holds the facts for k = 1, row 2 for k = 2",
            ),
        ],
        constraints=["1 <= start <= end <= 20", "1 <= upto <= 12"],
        todo="Loop over k for the rows and over n for the columns, building one string per fact.",
        solution="""
            def multiplication_tables(start: int, end: int, upto: int) -> list[list[str]]:
                rows = []
                for k in range(1, upto + 1):
                    row = []
                    for n in range(start, end + 1):
                        row.append(f"{n} x {k} = {n * k}")
                    rows.append(row)
                return rows
        """,
        trace=1,
        cases=[
            (
                "2, 4, 4",
                '[["2 x 1 = 2", "3 x 1 = 3", "4 x 1 = 4"], ["2 x 2 = 4", "3 x 2 = 6", "4 x 2 = 8"], ["2 x 3 = 6", "3 x 3 = 9", "4 x 3 = 12"], ["2 x 4 = 8", "3 x 4 = 12", "4 x 4 = 16"]]',
                False,
            ),
            (
                "3, 5, 2",
                '[["3 x 1 = 3", "4 x 1 = 4", "5 x 1 = 5"], ["3 x 2 = 6", "4 x 2 = 8", "5 x 2 = 10"]]',
                False,
            ),
            ("5, 5, 3", '[["5 x 1 = 5"], ["5 x 2 = 10"], ["5 x 3 = 15"]]', True),
            ("1, 3, 1", '[["1 x 1 = 1", "2 x 1 = 2", "3 x 1 = 3"]]', True),
        ],
        hints=(
            "Each output row is a list of strings; what changes along a row, and what changes between rows?",
            "The outer loop picks the multiplier k, the inner loop picks the number n.",
            "Create a fresh <code>row = []</code> inside the outer loop, fill it, then append it to <code>rows</code>.",
        ),
        approaches=[
            (
                "Nested loops",
                "Outer loop over multipliers, inner loop over numbers.",
                "O(upto * (end - start + 1))",
                "O(upto * (end - start + 1))",
                True,
            ),
        ],
        notes=[
            (
                4,
                "A fresh row for each k. Creating it outside the outer loop would reuse one list and every row would end up identical.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For (2, 4, 4), what is row the first time <code>rows.append(row)</code> is reached?",
                "['2 x 1 = 2', '3 x 1 = 3', '4 x 1 = 4']",
            ),
        ],
        patterns=["Matrix", "Simulation"],
        techniques=["Nested loops", "f-strings"],
    ),
    problem(
        slug="diamond-of-stars",
        title="Diamond of Stars",
        topic="grid-play",
        difficulty="medium",
        fn="diamond",
        signature="(size: int) -> list[str]",
        description=html(
            "Return the lines of a star diamond with <code>size</code> rows (<code>size</code> is odd). The widest row is in the middle and has <code>size</code> stars; each row away from the middle has two fewer.",
            "Pad each line on the left with spaces so the diamond is centred. Do not add trailing spaces.",
        ),
        examples=[
            (
                "size = 5",
                '["  *", " ***", "*****", " ***", "  *"]',
                "Rows hold 1, 3, 5, 3, 1 stars",
            ),
        ],
        constraints=["1 <= size <= 99", "size is odd"],
        todo="Work out how many stars row i has, then pad with (size - stars) // 2 spaces.",
        solution="""
            def diamond(size: int) -> list[str]:
                mid = size // 2
                lines = []
                for i in range(size):
                    stars = size - 2 * abs(mid - i)
                    lines.append(" " * ((size - stars) // 2) + "*" * stars)
                return lines
        """,
        trace=1,
        cases=[
            ("5", '["  *", " ***", "*****", " ***", "  *"]', False),
            ("3", '[" *", "***", " *"]', False),
            ("1", '["*"]', True),
            (
                "7",
                '["   *", "  ***", " *****", "*******", " *****", "  ***", "   *"]',
                True,
            ),
            (
                "9",
                '["    *", "   ***", "  *****", " *******", "*********", " *******", "  *****", "   ***", "    *"]',
                True,
            ),
        ],
        hints=(
            "How does the star count change as you move away from the middle row?",
            "Row i is <code>abs(mid - i)</code> rows from the middle; each step away removes 2 stars.",
            '<code>stars = size - 2 * abs(mid - i)</code>, then <code>" " * ((size - stars) // 2) + "*" * stars</code>.',
        ),
        approaches=[
            (
                "Build top half, mirror it",
                "Build rows up to the middle, then add them again in reverse.",
                "O(size^2)",
                "O(size^2)",
                False,
            ),
            (
                "Distance from the middle",
                "One loop; star count comes from the distance to the middle row.",
                "O(size^2)",
                "O(size^2)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "abs(mid - i) is the distance from the widest row; each step away trims one star from each side, hence 2 * distance.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For size = 5, what is stars the third time <code>lines.append(...)</code> is reached (i = 2)?",
                "5, the widest row (it sits at the middle).",
            ),
        ],
        patterns=["Simulation"],
        techniques=["String repetition", "abs()"],
    ),
    problem(
        slug="multiplication-matrix",
        title="Multiplication Matrix",
        topic="grid-play",
        difficulty="easy",
        fn="multiplication_matrix",
        signature="(size: int) -> list[list[int]]",
        description=html(
            "Return a <code>size x size</code> matrix whose cell in row <code>i</code> and column <code>j</code> (both counted from 1) is <code>i * j</code>.",
        ),
        examples=[
            ("size = 3", "[[1, 2, 3], [2, 4, 6], [3, 6, 9]]", "Row 2 is [2, 4, 6]"),
        ],
        constraints=["1 <= size <= 20"],
        todo="Build each row with an inner loop, then append the row to the matrix.",
        solution="""
            def multiplication_matrix(size: int) -> list[list[int]]:
                matrix = []
                for i in range(1, size + 1):
                    row = []
                    for j in range(1, size + 1):
                        row.append(i * j)
                    matrix.append(row)
                return matrix
        """,
        trace=1,
        cases=[
            ("3", "[[1, 2, 3], [2, 4, 6], [3, 6, 9]]", False),
            ("4", "[[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12], [4, 8, 12, 16]]", False),
            ("1", "[[1]]", True),
            (
                "5",
                "[[1, 2, 3, 4, 5], [2, 4, 6, 8, 10], [3, 6, 9, 12, 15], [4, 8, 12, 16, 20], [5, 10, 15, 20, 25]]",
                True,
            ),
        ],
        hints=(
            "What are the row and column numbers of a cell, and how do they combine?",
            "Use one loop for rows and one nested loop for columns, both starting at 1.",
            "Inside the inner loop append <code>i * j</code> to <code>row</code>; append <code>row</code> after it.",
        ),
        approaches=[
            (
                "Nested loops",
                "One pass over every cell.",
                "O(size^2)",
                "O(size^2)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "Each row needs its own new list; appending the same list repeatedly would make all rows alias each other.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For size = 3, what is row the second time <code>matrix.append(row)</code> is reached?",
                "[2, 4, 6].",
            ),
        ],
        patterns=["Matrix"],
        techniques=["Nested loops"],
    ),
    problem(
        slug="fibonacci-matrix",
        title="Fibonacci Matrix",
        topic="grid-play",
        difficulty="medium",
        fn="fibonacci_matrix",
        signature="(size: int) -> list[list[int]]",
        description=html(
            "Fill a <code>size x size</code> matrix with the Fibonacci numbers <code>1, 1, 2, 3, 5, ...</code> in row-major order (left to right, top to bottom) and return it.",
        ),
        examples=[
            (
                "size = 3",
                "[[1, 1, 2], [3, 5, 8], [13, 21, 34]]",
                "Row 1 = [1, 1, 2], row 2 = [3, 5, 8], row 3 = [13, 21, 34]",
            ),
        ],
        constraints=["1 <= size <= 10"],
        todo="Keep two running Fibonacci values and take the next one for every cell.",
        solution="""
            def fibonacci_matrix(size: int) -> list[list[int]]:
                prev, curr = 0, 1
                matrix = []
                for _ in range(size):
                    row = []
                    for _ in range(size):
                        row.append(curr)
                        prev, curr = curr, prev + curr
                    matrix.append(row)
                return matrix
        """,
        trace=1,
        cases=[
            ("3", "[[1, 1, 2], [3, 5, 8], [13, 21, 34]]", False),
            ("2", "[[1, 1], [2, 3]]", False),
            ("1", "[[1]]", True),
            (
                "4",
                "[[1, 1, 2, 3], [5, 8, 13, 21], [34, 55, 89, 144], [233, 377, 610, 987]]",
                True,
            ),
        ],
        hints=(
            "The matrix is just the Fibonacci sequence cut into rows. How do you produce the next term?",
            "Track <code>prev</code> and <code>curr</code>; after using curr, move both forward.",
            "<code>prev, curr = curr, prev + curr</code> after appending <code>curr</code> to the row.",
        ),
        approaches=[
            (
                "Two running values",
                "Generate terms on the fly while filling cells.",
                "O(size^2)",
                "O(size^2)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "Both right-hand values use the old prev and curr before either name changes, so no temporary variable is needed.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For size = 3, what is row the second time <code>matrix.append(row)</code> is reached?",
                "[3, 5, 8].",
            ),
        ],
        patterns=["Matrix", "Math"],
        techniques=["Tuple unpacking", "Nested loops"],
    ),
    problem(
        slug="spiral-matrix",
        title="Spiral Matrix",
        topic="grid-play",
        difficulty="medium",
        fn="spiral_matrix",
        signature="(size: int) -> list[list[int]]",
        description=html(
            "Fill a <code>size x size</code> grid with <code>1, 2, 3, ...</code> by walking a clockwise spiral that starts at the top-left corner and winds inwards. Return the grid.",
        ),
        examples=[
            (
                "size = 3",
                "[[1, 2, 3], [8, 9, 4], [7, 6, 5]]",
                "Top row 1 2 3, then down the right side, then back along the bottom, up, and into the centre",
            ),
        ],
        constraints=["1 <= size <= 20"],
        todo="Track four shrinking borders (top, bottom, left, right) and fill one edge at a time.",
        solution="""
            def spiral_matrix(size: int) -> list[list[int]]:
                grid = [[0] * size for _ in range(size)]
                top, bottom, left, right = 0, size - 1, 0, size - 1
                value = 1
                while top <= bottom and left <= right:
                    for col in range(left, right + 1):
                        grid[top][col] = value
                        value += 1
                    top += 1
                    for row in range(top, bottom + 1):
                        grid[row][right] = value
                        value += 1
                    right -= 1
                    if top <= bottom:
                        for col in range(right, left - 1, -1):
                            grid[bottom][col] = value
                            value += 1
                        bottom -= 1
                    if left <= right:
                        for row in range(bottom, top - 1, -1):
                            grid[row][left] = value
                            value += 1
                        left += 1
                return grid
        """,
        trace=1,
        cases=[
            ("3", "[[1, 2, 3], [8, 9, 4], [7, 6, 5]]", False),
            (
                "4",
                "[[1, 2, 3, 4], [12, 13, 14, 5], [11, 16, 15, 6], [10, 9, 8, 7]]",
                False,
            ),
            ("1", "[[1]]", True),
            ("2", "[[1, 2], [4, 3]]", True),
            (
                "5",
                "[[1, 2, 3, 4, 5], [16, 17, 18, 19, 6], [15, 24, 25, 20, 7], [14, 23, 22, 21, 8], [13, 12, 11, 10, 9]]",
                True,
            ),
        ],
        hints=(
            "Which cells does one lap of the spiral touch, and what is left afterwards?",
            "Keep four borders. Fill the top row, then right column, then bottom row, then left column, moving each border inwards after its edge.",
            "Guard the bottom row with <code>top <= bottom</code> and the left column with <code>left <= right</code> so a final single strip is not filled twice.",
        ),
        approaches=[
            (
                "Turn at walls and filled cells",
                "Walk one step at a time and turn right when blocked.",
                "O(size^2)",
                "O(size^2)",
                False,
            ),
            (
                "Shrinking borders",
                "Fill whole edges and move the four borders inwards.",
                "O(size^2)",
                "O(size^2)",
                True,
            ),
        ],
        notes=[
            (
                14,
                "After removing the top row and right column, only a single row or column may remain; the guards here and below stop that strip being written twice.",
                False,
            ),
        ],
        predictions=[
            (
                13,
                "For size = 3, what is value the first time <code>right -= 1</code> is reached?",
                "6; the numbers 1 to 5 already fill the top row and right column.",
            ),
        ],
        patterns=["Matrix", "Simulation"],
        techniques=["Boundary pointers", "Nested loops"],
    ),
    problem(
        slug="main-diagonal-sum",
        title="Main Diagonal Sum",
        topic="grid-play",
        difficulty="easy",
        fn="diagonal_sum",
        signature="(matrix: list[list[int]]) -> int",
        description=html(
            "Given a square matrix, return the sum of the cells on its main diagonal: the cells where the row index equals the column index (top-left to bottom-right).",
        ),
        examples=[
            ("matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "15", "1 + 5 + 9"),
        ],
        constraints=["1 <= len(matrix) <= 100", "The matrix is square"],
        todo="Add up matrix[i][i] for every i.",
        solution="""
            def diagonal_sum(matrix: list[list[int]]) -> int:
                total = 0
                for i in range(len(matrix)):
                    total += matrix[i][i]
                return total
        """,
        trace=1,
        cases=[
            ("[[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "15", False),
            ("[[2, 0, 1, 4], [3, 5, 0, 1], [1, 1, 7, 2], [6, 2, 3, 9]]", "23", False),
            ("[[7]]", "7", True),
            ("[[-1, 2], [3, -4]]", "-5", True),
            ("[[0, 0], [0, 0]]", "0", True),
        ],
        hints=(
            "Which cells have the same row number and column number?",
            "One loop over i is enough; you do not need to visit every cell.",
            "<code>total += matrix[i][i]</code> inside <code>for i in range(len(matrix))</code>.",
        ),
        approaches=[
            (
                "Scan every cell",
                "Two loops, add the cell when row == column.",
                "O(n^2)",
                "O(1)",
                False,
            ),
            ("Index the diagonal", "Read matrix[i][i] directly.", "O(n)", "O(1)", True),
        ],
        notes=[
            (
                4,
                "Row i contributes its cell in column i; those are exactly the cells where row index equals column index.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For the 3 x 3 example, what is total the third time <code>total += matrix[i][i]</code> is reached (i = 2)?",
                "6 (1 + 5).",
            ),
        ],
        patterns=["Matrix"],
        techniques=["Indexing", "Accumulator"],
    ),
]
