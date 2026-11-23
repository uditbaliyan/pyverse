# ruff: noqa: E501
"""Pattern Printing: nested loops and string repetition. Rows are returned, not printed."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="star-right-triangle",
        title="Right-Angle Triangle of Stars",
        topic="pattern-printing",
        difficulty="easy",
        fn="star_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a right-angled triangle out of <code>*</code> characters with <code>n</code> rows. Row 1 has one star, and every following row has one more star than the row above it.",
            "<pre>*\n**\n***\n****</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            ("n = 4", '["*", "**", "***", "****"]', "Rows hold 1, 2, 3 and 4 stars."),
        ],
        constraints=["1 <= n <= 50"],
        todo="Loop over the row sizes and collect one string of stars per row.",
        solution="""
            def star_triangle(n: int) -> list[str]:
                rows = []
                for size in range(1, n + 1):
                    rows.append("*" * size)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['*', '**', '***', '****']", False),
            ("2", "['*', '**']", False),
            ("1", "['*']", True),
            ("7", "['*', '**', '***', '****', '*****', '******', '*******']", True),
        ],
        hints=(
            "How many stars does row number <code>k</code> contain?",
            "Loop <code>size</code> from 1 to <code>n</code> and add one string per pass.",
            'Strings can be repeated: <code>"*" * 3</code> is <code>"***"</code>. Append <code>"*" * size</code>.',
        ),
        approaches=[
            (
                "Inner loop per row",
                "Build each row one star at a time with a second loop.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "String repetition",
                '<code>"*" * size</code> builds a whole row in one step.',
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "Multiplying a string repeats it, so row k is exactly k stars. No inner loop is needed.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "When this line is reached with size = 3, how many strings are already in rows?",
                "2: the rows for size 1 and size 2.",
            ),
        ],
        patterns=["Iteration"],
        techniques=["String Repetition", "Accumulator"],
    ),
    problem(
        slug="star-square",
        title="Square of Stars",
        topic="pattern-printing",
        difficulty="easy",
        fn="star_square",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a solid square of <code>*</code> characters: <code>n</code> rows, each with <code>n</code> stars.",
            "<pre>*****\n*****\n*****\n*****\n*****</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 5",
                '["*****", "*****", "*****", "*****", "*****"]',
                "Five rows of five stars.",
            ),
        ],
        constraints=["1 <= n <= 50"],
        todo="Create n identical rows of n stars.",
        solution="""
            def star_square(n: int) -> list[str]:
                rows = []
                for _ in range(n):
                    rows.append("*" * n)
                return rows
        """,
        trace=1,
        cases=[
            ("5", "['*****', '*****', '*****', '*****', '*****']", False),
            ("3", "['***', '***', '***']", False),
            ("1", "['*']", True),
            ("2", "['**', '**']", True),
            (
                "8",
                "['********', '********', '********', '********', '********', '********', '********', '********']",
                True,
            ),
        ],
        hints=(
            "Every row is identical. What decides how many rows there are?",
            "Repeat the same loop body <code>n</code> times.",
            'Append <code>"*" * n</code> once per pass of <code>for _ in range(n)</code>.',
        ),
        approaches=[
            (
                "Loop and append",
                'One pass per row, each row is <code>"*" * n</code>.',
                "O(n^2)",
                "O(n^2)",
                True,
            ),
            (
                "List multiplication",
                '<code>["*" * n] * n</code> repeats one row n times (safe because strings are immutable).',
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "The loop variable is never used: only the count of passes matters, which is why it is named _.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "When the return line is reached, how many strings does rows hold?",
                "5: one per pass of the loop.",
            ),
        ],
        patterns=["Iteration"],
        techniques=["String Repetition", "Accumulator"],
    ),
    problem(
        slug="star-pyramid",
        title="Pyramid of Stars",
        topic="pattern-printing",
        difficulty="easy",
        fn="star_pyramid",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a centred pyramid of <code>*</code> characters with <code>n</code> rows. Row 1 has a single star; each row below it has two more stars than the one above, and every row is indented so that the pyramid is centred.",
            "<pre>  *\n ***\n*****</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 3",
                '["  *", " ***", "*****"]',
                "Rows hold 1, 3 and 5 stars, indented by 2, 1 and 0 spaces.",
            ),
        ],
        constraints=["1 <= n <= 40"],
        todo="For each row, add the indent and then the stars.",
        solution="""
            def star_pyramid(n: int) -> list[str]:
                rows = []
                for row in range(1, n + 1):
                    spaces = " " * (n - row)
                    stars = "*" * (2 * row - 1)
                    rows.append(spaces + stars)
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['  *', ' ***', '*****']", False),
            ("5", "['    *', '   ***', '  *****', ' *******', '*********']", False),
            ("1", "['*']", True),
            ("2", "[' *', '***']", True),
            (
                "8",
                "['       *', '      ***', '     *****', '    *******', '   *********', '  ***********', ' *************', '***************']",
                True,
            ),
        ],
        hints=(
            "Write down, for rows 1, 2, 3, how many spaces and how many stars you need.",
            "Spaces shrink by one per row (<code>n - row</code>); stars grow by two (<code>2 * row - 1</code>).",
            'Append <code>" " * (n - row) + "*" * (2 * row - 1)</code> for each row from 1 to n.',
        ),
        approaches=[
            (
                "Indent plus stars",
                "Compute the indent and the star count from the row number.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
            (
                "Centre a star string",
                "Build the stars and use <code>str.center(2 * n - 1)</code>, then strip trailing spaces.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                5,
                "Each row adds one star on the left and one on the right, so the width grows by 2: 1, 3, 5, ...",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "On the second pass (row = 2) when this line is reached, how long is spaces?",
                "1: n - row = 3 - 2.",
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["String Repetition"],
    ),
    problem(
        slug="star-diamond",
        title="Diamond of Stars",
        topic="pattern-printing",
        difficulty="easy",
        fn="star_diamond",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a centred diamond of stars. The top half is the pyramid from the previous problem (<code>n</code> rows, 1, 3, 5, ... stars). The bottom half mirrors it, so the whole diamond has <code>2 * n - 1</code> rows and the widest row appears once.",
            "<pre>  *\n ***\n*****\n ***\n  *</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 3",
                '["  *", " ***", "*****", " ***", "  *"]',
                "A pyramid on top of an upside-down pyramid, sharing the widest row.",
            ),
        ],
        constraints=["1 <= n <= 40"],
        todo="Build the top half, then add its mirror image without repeating the middle row.",
        solution="""
            def star_diamond(n: int) -> list[str]:
                top = []
                for row in range(1, n + 1):
                    top.append(" " * (n - row) + "*" * (2 * row - 1))
                return top + top[-2::-1]
        """,
        trace=1,
        cases=[
            ("3", "['  *', ' ***', '*****', ' ***', '  *']", False),
            (
                "4",
                "['   *', '  ***', ' *****', '*******', ' *****', '  ***', '   *']",
                False,
            ),
            ("1", "['*']", True),
            ("2", "[' *', '***', ' *']", True),
            (
                "6",
                "['     *', '    ***', '   *****', '  *******', ' *********', '***********', ' *********', '  *******', '   *****', '    ***', '     *']",
                True,
            ),
        ],
        hints=(
            "The bottom half is the top half read backwards. Which row must not appear twice?",
            "Build the top half first; the bottom is the top reversed, minus the widest row.",
            "<code>top[-2::-1]</code> walks the list backwards starting from the second-to-last row.",
        ),
        approaches=[
            (
                "Two loops",
                "One loop counting up for the top, a second counting down for the bottom.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Mirror the top half",
                "Build the top once and append <code>top[-2::-1]</code>.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Starting the slice at -2 skips the widest row, so it is not listed twice. For n = 1 the slice is empty, which is exactly right.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For n = 3, when the return line is reached, what is top[-2::-1]?",
                '[" ***", "  *"]: the rows above the widest one, in reverse order.',
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Slicing", "String Repetition"],
    ),
    problem(
        slug="hollow-star-square",
        title="Hollow Square of Stars",
        topic="pattern-printing",
        difficulty="easy",
        fn="hollow_square",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an <code>n</code> by <code>n</code> square whose border is made of stars and whose inside is empty (spaces).",
            "<pre>*****\n*   *\n*   *\n*   *\n*****</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row. For <code>n = 1</code> the answer is a single star, and for <code>n = 2</code> the square is full.",
        ),
        examples=[
            (
                "n = 5",
                '["*****", "*   *", "*   *", "*   *", "*****"]',
                "Top and bottom rows are solid; the middle rows have a star at each end.",
            ),
        ],
        constraints=["1 <= n <= 40"],
        todo="Decide per row: solid border row, or star + spaces + star.",
        solution="""
            def hollow_square(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    if row == 0 or row == n - 1:
                        rows.append("*" * n)
                    else:
                        rows.append("*" + " " * (n - 2) + "*")
                return rows
        """,
        trace=1,
        cases=[
            ("5", "['*****', '*   *', '*   *', '*   *', '*****']", False),
            ("3", "['***', '* *', '***']", False),
            ("1", "['*']", True),
            ("2", "['**', '**']", True),
            (
                "7",
                "['*******', '*     *', '*     *', '*     *', '*     *', '*     *', '*******']",
                True,
            ),
        ],
        hints=(
            "Which rows are completely filled, and which are not?",
            "The first and last rows are solid. Every other row is a star, some spaces, a star.",
            'Interior rows have <code>n - 2</code> spaces: <code>"*" + " " * (n - 2) + "*"</code>.',
        ),
        approaches=[
            (
                "Test every cell",
                "Nested loops decide star or space cell by cell.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Row types",
                "Two kinds of row; build each with string repetition.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Interior rows are a star, n - 2 spaces and a star. Only the first and last rows are fully solid.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For n = 5, how many times does this interior-row line run?",
                "3 times, for rows 1, 2 and 3.",
            ),
        ],
        patterns=["Iteration"],
        techniques=["String Repetition"],
    ),
    problem(
        slug="number-triangle",
        title="Number Triangle",
        topic="pattern-printing",
        difficulty="easy",
        fn="number_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a right-angled triangle of digits. Row <code>k</code> is the digits <code>1</code> up to <code>k</code> written next to each other.",
            "<pre>1\n12\n123\n1234</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 4", '["1", "12", "123", "1234"]', "Each row restarts from 1.")],
        constraints=["1 <= n <= 9"],
        todo="Build every row by joining the numbers 1..row as text.",
        solution="""
            def number_triangle(n: int) -> list[str]:
                rows = []
                for size in range(1, n + 1):
                    line = ""
                    for number in range(1, size + 1):
                        line += str(number)
                    rows.append(line)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['1', '12', '123', '1234']", False),
            ("2", "['1', '12']", False),
            ("1", "['1']", True),
            (
                "9",
                "['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789']",
                True,
            ),
        ],
        hints=(
            "Each row is its own little counting loop starting at 1.",
            "Use an outer loop for the row length and an inner loop for the numbers.",
            'Reset <code>line = ""</code> for every row, then add <code>str(number)</code> for 1..size.',
        ),
        approaches=[
            (
                "Nested loops",
                "Outer loop for rows, inner loop for the numbers in the row.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
            (
                "Slice a digit string",
                'Slice <code>"123456789"[:size]</code> (only works because n <= 9).',
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "line is reset for every row. Without this, the digits of all rows would pile up in one string.",
                False,
            ),
        ],
        predictions=[
            (7, "When size is 3 and this line is reached, what is line?", '"123"'),
        ],
        patterns=["Iteration"],
        techniques=["Accumulator", "Type Conversion"],
    ),
    problem(
        slug="inverted-star-triangle",
        title="Inverted Triangle of Stars",
        topic="pattern-printing",
        difficulty="easy",
        fn="inverted_star_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an upside-down right-angled triangle of stars, aligned to the <strong>right</strong>. The first row has <code>n</code> stars; each following row has one star fewer and one more leading space.",
            "<pre>*****\n ****\n  ***\n   **\n    *</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 5",
                '["*****", " ****", "  ***", "   **", "    *"]',
                "Stars 5, 4, 3, 2, 1 with indents 0, 1, 2, 3, 4.",
            ),
        ],
        constraints=["1 <= n <= 50"],
        todo="Each row is some leading spaces followed by some stars.",
        solution="""
            def inverted_star_triangle(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    rows.append(" " * row + "*" * (n - row))
                return rows
        """,
        trace=1,
        cases=[
            ("5", "['*****', ' ****', '  ***', '   **', '    *']", False),
            ("3", "['***', ' **', '  *']", False),
            ("1", "['*']", True),
            (
                "8",
                "['********', ' *******', '  ******', '   *****', '    ****', '     ***', '      **', '       *']",
                True,
            ),
        ],
        hints=(
            "As the stars shrink by one, something else grows by one. What?",
            "Row <code>r</code> (starting at 0) has <code>r</code> spaces and <code>n - r</code> stars.",
            'Append <code>" " * row + "*" * (n - row)</code>.',
        ),
        approaches=[
            (
                "Spaces then stars",
                "Compute both counts from the row index.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
            (
                "Right-justify",
                "Build the stars and use <code>str.rjust(n)</code>.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "Spaces plus stars always add up to n, which is what keeps every row right-aligned.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For n = 5, on the third pass (row = 2), how many stars does this row get?",
                "3 stars: n - row = 5 - 2.",
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["String Repetition"],
    ),
    problem(
        slug="number-diamond",
        title="Number Diamond",
        topic="pattern-printing",
        difficulty="easy",
        fn="number_diamond",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a centred diamond of digits. A row that peaks at <code>k</code> counts up <code>1, 2, ..., k</code> and back down <code>k-1, ..., 1</code>. The rows peak at 1, 2, ..., n, ..., 2, 1, so there are <code>2 * n - 1</code> rows.",
            "<pre>  1\n 121\n12321\n 121\n  1</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 3",
                '["  1", " 121", "12321", " 121", "  1"]',
                "Peaks 1, 2, 3, 2, 1.",
            ),
        ],
        constraints=["1 <= n <= 9"],
        todo="Build the top half row by row, then mirror it without repeating the middle row.",
        solution="""
            def number_diamond(n: int) -> list[str]:
                top = []
                for peak in range(1, n + 1):
                    up = ""
                    for digit in range(1, peak + 1):
                        up += str(digit)
                    down = up[-2::-1]
                    top.append(" " * (n - peak) + up + down)
                return top + top[-2::-1]
        """,
        trace=1,
        cases=[
            ("3", "['  1', ' 121', '12321', ' 121', '  1']", False),
            (
                "4",
                "['   1', '  121', ' 12321', '1234321', ' 12321', '  121', '   1']",
                False,
            ),
            ("1", "['1']", True),
            ("2", "[' 1', '121', ' 1']", True),
            (
                "9",
                "['        1', '       121', '      12321', '     1234321', '    123454321', '   12345654321', '  1234567654321', ' 123456787654321', '12345678987654321', ' 123456787654321', '  1234567654321', '   12345654321', '    123454321', '     1234321', '      12321', '       121', '        1']",
                True,
            ),
        ],
        hints=(
            "A row is a number run going up and then the same run, reversed, going down.",
            'Build <code>up = "123..peak"</code>; the descending part is <code>up</code> reversed without its last digit.',
            "<code>up[-2::-1]</code> is that reversed part. Mirror the finished top half the same way.",
        ),
        approaches=[
            (
                "Compute each digit",
                "For every column compute the digit from its distance to the centre.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Up, down, mirror",
                "Build the ascending run, slice-reverse it, and mirror the top half.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Reversing up while skipping its last digit gives the descending half, so the peak digit is not repeated: 123 becomes 21.",
                False,
            ),
        ],
        predictions=[
            (8, "When peak is 3 and this line is reached, what is down?", '"21"'),
        ],
        patterns=["Iteration"],
        techniques=["Slicing", "Accumulator", "Type Conversion"],
    ),
    problem(
        slug="consecutive-number-triangle",
        title="Triangle of Consecutive Numbers",
        topic="pattern-printing",
        difficulty="easy",
        fn="counting_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            'Fill a right-angled triangle with the numbers 1, 2, 3, ... in order. Row <code>k</code> holds <code>k</code> numbers, and the numbers are written directly next to each other (no spaces), so a row such as 7, 8, 9, 10 becomes <code>"78910"</code>. Numbering does not restart on a new row.',
            "<pre>1\n23\n456\n78910</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 4",
                '["1", "23", "456", "78910"]',
                "Rows hold 1, 2, 3 and 4 numbers: 1 | 2 3 | 4 5 6 | 7 8 9 10.",
            ),
        ],
        constraints=["1 <= n <= 20"],
        todo="Keep one running counter that is never reset between rows.",
        solution="""
            def counting_triangle(n: int) -> list[str]:
                rows = []
                number = 1
                for size in range(1, n + 1):
                    line = ""
                    for _ in range(size):
                        line += str(number)
                        number += 1
                    rows.append(line)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['1', '23', '456', '78910']", False),
            ("3", "['1', '23', '456']", False),
            ("1", "['1']", True),
            ("2", "['1', '23']", True),
            ("6", "['1', '23', '456', '78910', '1112131415', '161718192021']", True),
        ],
        hints=(
            "The counter belongs outside the row loop. Why?",
            "Row k writes k numbers, taking each from one shared counter.",
            "Inner loop: <code>line += str(number)</code> then <code>number += 1</code>. Reset only <code>line</code> per row.",
        ),
        approaches=[
            (
                "Shared counter",
                "One counter outside both loops hands out the numbers.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
            (
                "Triangular formula",
                "Row k starts at <code>k * (k - 1) // 2 + 1</code>; use <code>range</code> per row.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                8,
                "number is defined before both loops and never reset, so each row continues where the last one stopped.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "When size is 4 and this line is reached, what is number?",
                "11: the row just used 7, 8, 9 and 10.",
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Accumulator", "Type Conversion"],
    ),
    problem(
        slug="number-pyramid",
        title="Number Pyramid",
        topic="pattern-printing",
        difficulty="easy",
        fn="number_pyramid",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a centred pyramid of digits. Row <code>k</code> starts at <code>k</code>, counts up to <code>2k - 1</code> and then counts back down to <code>k</code>.",
            "<pre>  1\n 232\n34543</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["  1", " 232", "34543"]', "Row 3 is 3 4 5 4 3.")],
        constraints=["1 <= n <= 5 (so every number is a single digit)"],
        todo="Each row is an indent, an ascending run and a descending run.",
        solution="""
            def number_pyramid(n: int) -> list[str]:
                rows = []
                for row in range(1, n + 1):
                    up = ""
                    for digit in range(row, 2 * row):
                        up += str(digit)
                    down = ""
                    for digit in range(2 * row - 2, row - 1, -1):
                        down += str(digit)
                    rows.append(" " * (n - row) + up + down)
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['  1', ' 232', '34543']", False),
            ("4", "['   1', '  232', ' 34543', '4567654']", False),
            ("1", "['1']", True),
            ("2", "[' 1', '232']", True),
            ("5", "['    1', '   232', '  34543', ' 4567654', '567898765']", True),
        ],
        hints=(
            "Split each row into a rising part (ending at the peak) and a falling part.",
            "Rising: <code>range(row, 2 * row)</code>. Falling: from <code>2 * row - 2</code> down to <code>row</code>.",
            "A falling range needs a negative step: <code>range(2 * row - 2, row - 1, -1)</code>.",
        ),
        approaches=[
            (
                "Rise then fall",
                "Two small loops per row, one counting up and one down.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
            (
                "Distance from centre",
                "Compute each digit as <code>2k - 1 - |offset|</code>.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
        ],
        notes=[
            (
                8,
                "A negative step counts down. The stop value row - 1 is excluded, so the last digit written is row itself.",
                False,
            ),
        ],
        predictions=[
            (
                10,
                "When row is 3 and this line is reached, what are up and down?",
                'up is "345" and down is "43".',
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Accumulator", "Type Conversion"],
    ),
    problem(
        slug="growing-star-rows",
        title="Rows of Growing Stars",
        topic="pattern-printing",
        difficulty="medium",
        fn="growing_star_rows",
        signature="(n: int) -> list[str]",
        description=html(
            "Build <code>n</code> left-aligned rows of stars where the row widths are the odd numbers <code>1, 3, 5, ...</code>.",
            "<pre>*\n***\n*****</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["*", "***", "*****"]', "Widths 1, 3, 5.")],
        constraints=["1 <= n <= 50"],
        todo="Work out the star count of row r (starting from 0) and repeat '*' that many times.",
        solution="""
            def growing_star_rows(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    rows.append("*" * (2 * row + 1))
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['*', '***', '*****']", False),
            ("4", "['*', '***', '*****', '*******']", False),
            ("1", "['*']", True),
            ("2", "['*', '***']", True),
            (
                "9",
                "['*', '***', '*****', '*******', '*********', '***********', '*************', '***************', '*****************']",
                True,
            ),
        ],
        hints=(
            "List the widths for n = 4: 1, 3, 5, 7. How does each differ from the one before?",
            "The width is always odd and grows by 2 per row.",
            "With the row index starting at 0, the width is <code>2 * row + 1</code>.",
        ),
        approaches=[
            (
                "Add 2 each time",
                "Keep a width variable and add 2 after every row.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Closed formula",
                "Width = <code>2 * row + 1</code>.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "2 * row is even for every row and adding 1 makes it odd, which is why the widths are 1, 3, 5, ... without any extra state.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For n = 3, on the last pass of the loop, how many stars are appended?",
                "5 stars: 2 * 2 + 1.",
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["String Repetition"],
    ),
    problem(
        slug="letter-triangle",
        title="Letter Triangle",
        topic="pattern-printing",
        difficulty="medium",
        fn="letter_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a right-angled triangle of letters. Row 1 is <code>A</code>, row 2 is <code>BB</code>, row 3 is <code>CCC</code>, and so on: row <code>k</code> is the k-th capital letter repeated <code>k</code> times.",
            "<pre>A\nBB\nCCC</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["A", "BB", "CCC"]', "A once, B twice, C three times.")],
        constraints=["1 <= n <= 26"],
        todo="Turn the row index into a letter and repeat it.",
        solution="""
            def letter_triangle(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    letter = chr(ord("A") + row)
                    rows.append(letter * (row + 1))
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['A', 'BB', 'CCC']", False),
            ("5", "['A', 'BB', 'CCC', 'DDDD', 'EEEEE']", False),
            ("1", "['A']", True),
            (
                "12",
                "['A', 'BB', 'CCC', 'DDDD', 'EEEEE', 'FFFFFF', 'GGGGGGG', 'HHHHHHHH', 'IIIIIIIII', 'JJJJJJJJJJ', 'KKKKKKKKKKK', 'LLLLLLLLLLLL']",
                True,
            ),
        ],
        hints=(
            "Letters have number codes. Which built-in turns a letter into its code and back?",
            '<code>ord("A")</code> is the code of A; adding the row index and calling <code>chr</code> gives the next letters.',
            '<code>letter = chr(ord("A") + row)</code>, then append <code>letter * (row + 1)</code>.',
        ),
        approaches=[
            (
                "Alphabet string",
                'Index into <code>"ABC...Z"</code>.',
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "chr and ord",
                "Compute the letter from the row index with character codes.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "Capital letters have consecutive codes, so adding row to the code of A steps through the alphabet.",
                False,
            ),
        ],
        predictions=[
            (5, "When row is 2 and this line is reached, what is letter?", '"C"'),
        ],
        patterns=["Iteration"],
        techniques=["Character Codes", "String Repetition"],
    ),
    problem(
        slug="inverted-letter-triangle",
        title="Inverted Letter Triangle",
        topic="pattern-printing",
        difficulty="medium",
        fn="inverted_letter_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an upside-down right-aligned triangle of letters. The first row is the n-th letter repeated <code>n</code> times. Every row after it uses the previous letter of the alphabet, one fewer copy, and one more leading space. The last row is a single <code>A</code>.",
            "<pre>CCC\n BB\n  A</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["CCC", " BB", "  A"]', "CCC, then BB, then A.")],
        constraints=["1 <= n <= 26"],
        todo="Row r uses the letter n - 1 - r places after A.",
        solution="""
            def inverted_letter_triangle(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    letter = chr(ord("A") + n - 1 - row)
                    rows.append(" " * row + letter * (n - row))
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['CCC', ' BB', '  A']", False),
            ("5", "['EEEEE', ' DDDD', '  CCC', '   BB', '    A']", False),
            ("1", "['A']", True),
            ("2", "['BB', ' A']", True),
            (
                "10",
                "['JJJJJJJJJJ', ' IIIIIIIII', '  HHHHHHHH', '   GGGGGGG', '    FFFFFF', '     EEEEE', '      DDDD', '       CCC', '        BB', '         A']",
                True,
            ),
        ],
        hints=(
            "Row 0 uses the n-th letter, the last row uses A. The letter index goes down as the row goes up.",
            "The letter for row r is <code>n - 1 - r</code> steps after A; the copies are <code>n - r</code>.",
            '<code>chr(ord("A") + n - 1 - row)</code> for the letter, <code>" " * row + letter * (n - row)</code> for the row.',
        ),
        approaches=[
            (
                "Build then reverse",
                "Build the letter triangle and reverse the list, then fix the indentation.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Direct formula",
                "Compute letter, spaces and copies from the row index.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "The letter walks backwards through the alphabet while the row index walks forwards, hence n - 1 - row.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For n = 3, when row is 1 and this line is reached, what is letter?",
                '"B"',
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Character Codes", "String Repetition"],
    ),
    problem(
        slug="alternating-letter-grid",
        title="Alternating Letter Grid",
        topic="pattern-printing",
        difficulty="easy",
        fn="letter_grid",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an <code>n</code> by <code>n</code> grid of the letters <code>A</code> and <code>B</code>. The top-left letter is <code>A</code>, and every letter differs from its neighbours to the left, right, above and below.",
            "<pre>ABAB\nBABA\nABAB\nBABA</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 4",
                '["ABAB", "BABA", "ABAB", "BABA"]',
                "Rows alternate between ABAB and BABA.",
            ),
        ],
        constraints=["1 <= n <= 30"],
        todo="Choose A or B for each cell from the parity of its row and column.",
        solution="""
            def letter_grid(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    line = ""
                    for col in range(n):
                        line += "AB"[(row + col) % 2]
                    rows.append(line)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['ABAB', 'BABA', 'ABAB', 'BABA']", False),
            ("3", "['ABA', 'BAB', 'ABA']", False),
            ("1", "['A']", True),
            ("2", "['AB', 'BA']", True),
            (
                "7",
                "['ABABABA', 'BABABAB', 'ABABABA', 'BABABAB', 'ABABABA', 'BABABAB', 'ABABABA']",
                True,
            ),
        ],
        hints=(
            "Neighbouring cells always differ. What number is different for neighbours?",
            "The parity of <code>row + col</code> flips with every step right or down.",
            'A string can be indexed: <code>"AB"[0]</code> is "A" and <code>"AB"[1]</code> is "B". Use <code>(row + col) % 2</code> as the index.',
        ),
        approaches=[
            ("If / else", "Test the parity and add A or B.", "O(n^2)", "O(n^2)", False),
            (
                "Index a string",
                'Use the parity (0 or 1) directly as an index into <code>"AB"</code>.',
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "The parity is always 0 or 1, so it doubles as an index into the string. That replaces an if/else.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For n = 4, when row is 1 and this line is reached, what is line?",
                '"BABA"',
            ),
        ],
        patterns=["Iteration", "Matrix"],
        techniques=["Modulo", "Nested Loops"],
    ),
    problem(
        slug="letter-pyramid",
        title="Letter Pyramid",
        topic="pattern-printing",
        difficulty="medium",
        fn="letter_pyramid",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a centred pyramid whose rows are filled with the alphabet in order. Row <code>k</code> has <code>2k - 1</code> letters, and each row continues from the letter after the previous row's last letter.",
            "<pre>  A\n BCD\nEFGHI</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 3",
                '["  A", " BCD", "EFGHI"]',
                "A | BCD | EFGHI: 1, 3 and 5 letters.",
            ),
        ],
        constraints=["1 <= n <= 5 (the pyramid uses n * n letters, at most 26)"],
        todo="Slice the alphabet: each row takes the next 2 * row - 1 letters.",
        solution="""
            def letter_pyramid(n: int) -> list[str]:
                alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                rows = []
                start = 0
                for row in range(1, n + 1):
                    count = 2 * row - 1
                    rows.append(" " * (n - row) + alphabet[start:start + count])
                    start += count
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['  A', ' BCD', 'EFGHI']", False),
            ("4", "['   A', '  BCD', ' EFGHI', 'JKLMNOP']", False),
            ("1", "['A']", True),
            ("2", "[' A', 'BCD']", True),
            ("5", "['    A', '   BCD', '  EFGHI', ' JKLMNOP', 'QRSTUVWXY']", True),
        ],
        hints=(
            "Every row is a centred pyramid row, just filled with letters instead of stars.",
            "Keep a position in the alphabet and advance it by the row's width after each row.",
            "<code>alphabet[start:start + count]</code> takes the letters, then <code>start += count</code>.",
        ),
        approaches=[
            (
                "Character codes",
                "Compute each letter from a running counter using chr and ord.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Slice the alphabet",
                "Take each row as a slice and advance the start index.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "Moving start by the row's width means the next slice begins at the letter after this row's last one.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For n = 3, when row is 3 and this line is reached, what is start?",
                "4: A to D are used by rows 1 and 2; this row took E to I.",
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Slicing", "String Repetition"],
    ),
    problem(
        slug="hollow-letter-triangle",
        title="Hollow Letter Triangle",
        topic="pattern-printing",
        difficulty="medium",
        fn="hollow_letter_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Build a triangle outline of letters. Row <code>k</code> uses the k-th capital letter. Row 1 is just <code>A</code>; every later row has that row's letter at both ends, with spaces between, so the two copies move apart along two diagonals.",
            "<pre>A\nB B\nC   C\nD     D</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 4",
                '["A", "B B", "C   C", "D     D"]',
                "The gap between the letters is 1, 3, 5 spaces in rows 2, 3, 4.",
            ),
        ],
        constraints=["1 <= n <= 26"],
        todo="Row 0 is one letter; later rows are letter + spaces + letter.",
        solution="""
            def hollow_letter_triangle(n: int) -> list[str]:
                rows = []
                for row in range(n):
                    letter = chr(ord("A") + row)
                    if row == 0:
                        rows.append(letter)
                    else:
                        rows.append(letter + " " * (2 * row - 1) + letter)
                return rows
        """,
        trace=1,
        cases=[
            ("4", "['A', 'B B', 'C   C', 'D     D']", False),
            ("3", "['A', 'B B', 'C   C']", False),
            ("1", "['A']", True),
            ("2", "['A', 'B B']", True),
            (
                "8",
                "['A', 'B B', 'C   C', 'D     D', 'E       E', 'F         F', 'G           G', 'H             H']",
                True,
            ),
        ],
        hints=(
            "Count the spaces between the two letters in each row of the example.",
            "The gap is 1, 3, 5, ... spaces, and the first row has no gap at all.",
            "For row <code>r</code> (from 0), the gap is <code>2 * r - 1</code> spaces; treat row 0 separately.",
        ),
        approaches=[
            (
                "Character grid",
                "Create a row of spaces and set the two end positions.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Letter, gap, letter",
                "Build each row from the gap size.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "Row 0 would need a negative gap, so it is handled by its own branch with a single letter.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For n = 4, on the last pass of the loop, how many spaces sit between the two letters?",
                "5: 2 * 3 - 1.",
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Character Codes", "String Repetition"],
    ),
    problem(
        slug="star-hourglass",
        title="Star Hourglass",
        topic="pattern-printing",
        difficulty="medium",
        fn="star_hourglass",
        signature="(n: int) -> list[str]",
        description=html(
            "Build an hourglass of stars that are separated by single spaces. The top row has <code>n</code> stars, and each row below it has one star fewer and is indented one more space, until a single star is left. The bottom half mirrors the top, so there are <code>2 * n - 1</code> rows.",
            "<pre>* * * * *\n * * * *\n  * * *\n   * *\n    *\n   * *\n  * * *\n * * * *\n* * * * *</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[
            (
                "n = 5",
                '["* * * * *", " * * * *", "  * * *", "   * *", "    *", "   * *", "  * * *", " * * * *", "* * * * *"]',
                "5, 4, 3, 2, 1, 2, 3, 4, 5 stars.",
            ),
        ],
        constraints=["1 <= n <= 30"],
        todo="Build the top half (n rows), then mirror it without repeating the single star.",
        solution="""
            def star_hourglass(n: int) -> list[str]:
                top = []
                for row in range(n):
                    stars = " ".join("*" * (n - row))
                    top.append(" " * row + stars)
                return top + top[-2::-1]
        """,
        trace=1,
        cases=[
            (
                "5",
                "['* * * * *', ' * * * *', '  * * *', '   * *', '    *', '   * *', '  * * *', ' * * * *', '* * * * *']",
                False,
            ),
            ("3", "['* * *', ' * *', '  *', ' * *', '* * *']", False),
            ("1", "['*']", True),
            ("2", "['* *', ' *', '* *']", True),
            (
                "6",
                "['* * * * * *', ' * * * * *', '  * * * *', '   * * *', '    * *', '     *', '    * *', '   * * *', '  * * * *', ' * * * * *', '* * * * * *']",
                True,
            ),
        ],
        hints=(
            "The bottom half is the top half read backwards.",
            "A row is an indent plus stars separated by spaces. How can you put a space between characters?",
            '<code>" ".join("***")</code> gives <code>"* * *"</code>. Mirror with <code>top[-2::-1]</code>.',
        ),
        approaches=[
            (
                "Two loops",
                "One loop shrinking, one growing.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Mirror the top half",
                "Build the top once; append it reversed without the middle row.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                4,
                'join treats the string as a sequence of characters and puts one space between each pair: "***" becomes "* * *".',
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For n = 5, when row is 1 and this line is reached, what is stars?",
                '"* * * *"',
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Slicing", "String Methods"],
    ),
    problem(
        slug="floyds-triangle",
        title="Floyd's Triangle",
        topic="pattern-printing",
        difficulty="easy",
        fn="floyds_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Fill a right-angled triangle with the numbers 1, 2, 3, ... in order, one number after another with no restart. Row <code>k</code> holds <code>k</code> numbers separated by single spaces.",
            "<pre>1\n2 3\n4 5 6\n7 8 9 10</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["1", "2 3", "4 5 6"]', "1 | 2 3 | 4 5 6.")],
        constraints=["1 <= n <= 30"],
        todo="Use one running counter and join each row with spaces.",
        solution="""
            def floyds_triangle(n: int) -> list[str]:
                rows = []
                number = 1
                for size in range(1, n + 1):
                    cells = []
                    for _ in range(size):
                        cells.append(str(number))
                        number += 1
                    rows.append(" ".join(cells))
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['1', '2 3', '4 5 6']", False),
            ("4", "['1', '2 3', '4 5 6', '7 8 9 10']", False),
            ("1", "['1']", True),
            ("2", "['1', '2 3']", True),
            (
                "6",
                "['1', '2 3', '4 5 6', '7 8 9 10', '11 12 13 14 15', '16 17 18 19 20 21']",
                True,
            ),
        ],
        hints=(
            "Numbers never restart, so the counter lives outside the row loop.",
            "Collect each row's numbers as strings in a list.",
            '<code>" ".join(cells)</code> turns the list into one line with single spaces.',
        ),
        approaches=[
            (
                "Triangular formula",
                "Row k starts at <code>k * (k - 1) // 2 + 1</code>.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Running counter",
                "One counter hands out the numbers across all rows.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                8,
                "number is never reset, so each row continues exactly where the previous one stopped.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For n = 3, when size is 3 and this line is reached, what is cells?",
                '["4", "5", "6"]',
            ),
        ],
        patterns=["Iteration", "Math"],
        techniques=["Accumulator", "String Methods", "Nested Loops"],
    ),
    problem(
        slug="spaced-letter-triangle",
        title="Letter Triangle with Spaces",
        topic="pattern-printing",
        difficulty="medium",
        fn="spaced_letter_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Fill a right-angled triangle with the letters A, B, C, ... in alphabet order. Row <code>k</code> holds <code>k</code> letters separated by single spaces, and the lettering does not restart on a new row.",
            "<pre>A\nB C\nD E F</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["A", "B C", "D E F"]', "A | B C | D E F.")],
        constraints=["1 <= n <= 6 (the triangle uses at most 21 letters)"],
        todo="Keep a running letter code; join each row's letters with spaces.",
        solution="""
            def spaced_letter_triangle(n: int) -> list[str]:
                rows = []
                code = ord("A")
                for size in range(1, n + 1):
                    letters = []
                    for _ in range(size):
                        letters.append(chr(code))
                        code += 1
                    rows.append(" ".join(letters))
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['A', 'B C', 'D E F']", False),
            ("4", "['A', 'B C', 'D E F', 'G H I J']", False),
            ("1", "['A']", True),
            ("2", "['A', 'B C']", True),
            ("6", "['A', 'B C', 'D E F', 'G H I J', 'K L M N O', 'P Q R S T U']", True),
        ],
        hints=(
            "It is the number triangle again, but the numbers are letters.",
            "<code>ord</code> gives a letter's code, <code>chr</code> turns a code back into a letter.",
            'Keep <code>code = ord("A")</code> outside the loops; append <code>chr(code)</code> and add 1.',
        ),
        approaches=[
            (
                "Index the alphabet",
                "Keep a position and index into an alphabet string.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Character codes",
                "Count codes upwards and convert with chr.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "chr converts the running code back to a character. Because capital letters have consecutive codes, adding 1 moves to the next letter.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For n = 3, when size is 3 and this line is reached, what is letters?",
                '["D", "E", "F"]',
            ),
        ],
        patterns=["Iteration"],
        techniques=["Character Codes", "String Methods", "Nested Loops"],
    ),
    problem(
        slug="packed-letter-triangle",
        title="Letter Triangle without Spaces",
        topic="pattern-printing",
        difficulty="medium",
        fn="packed_letter_triangle",
        signature="(n: int) -> list[str]",
        description=html(
            "Fill a right-angled triangle with the letters A, B, C, ... in alphabet order, with no restart. Row <code>k</code> holds <code>k</code> letters written directly next to each other.",
            "<pre>A\nBC\nDEF</pre>",
            "Return the rows as a list of strings; do not print them. A row has no trailing spaces, but leading spaces are part of the row.",
        ),
        examples=[("n = 3", '["A", "BC", "DEF"]', "A | BC | DEF.")],
        constraints=["1 <= n <= 6 (the triangle uses at most 21 letters)"],
        todo="Same as the spaced version, but build every row as one string.",
        solution="""
            def packed_letter_triangle(n: int) -> list[str]:
                rows = []
                code = ord("A")
                for size in range(1, n + 1):
                    line = ""
                    for _ in range(size):
                        line += chr(code)
                        code += 1
                    rows.append(line)
                return rows
        """,
        trace=1,
        cases=[
            ("3", "['A', 'BC', 'DEF']", False),
            ("4", "['A', 'BC', 'DEF', 'GHIJ']", False),
            ("1", "['A']", True),
            ("2", "['A', 'BC']", True),
            ("6", "['A', 'BC', 'DEF', 'GHIJ', 'KLMNO', 'PQRSTU']", True),
        ],
        hints=(
            "No separator is needed this time, so each row can be one growing string.",
            "Keep the running letter code outside both loops.",
            "Inner loop: <code>line += chr(code)</code> then <code>code += 1</code>; reset <code>line</code> per row.",
        ),
        approaches=[
            (
                "Slice the alphabet",
                "Take each row as a slice of the alphabet.",
                "O(n^2)",
                "O(n^2)",
                False,
            ),
            (
                "Running code",
                "Count character codes upwards, append characters to a row string.",
                "O(n^2)",
                "O(n^2)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Strings are immutable, so += builds a new string each time. That is fine for rows this short.",
                False,
            ),
        ],
        predictions=[
            (
                9,
                "For n = 3, when size is 3 and this line is reached, which letter will chr(code) give next?",
                '"G": rows used A to F.',
            ),
        ],
        patterns=["Iteration"],
        techniques=["Character Codes", "Accumulator", "Nested Loops"],
    ),
]
