# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="rat-in-a-maze",
        title="Rat in a Maze",
        topic="backtracking",
        difficulty="medium",
        fn="rat_in_a_maze",
        signature="(maze: list[list[int]]) -> list[str]",
        description=html(
            "<code>maze</code> is an <code>n x n</code> grid where <code>1</code> is an open cell and <code>0</code> is a wall. A rat starts at the top-left cell and wants to reach the bottom-right cell.",
            "It moves one step at a time as <code>D</code> (down), <code>L</code> (left), <code>R</code> (right) or <code>U</code> (up), never steps on a wall and never visits the same cell twice in one path. Return every possible path as a string of moves; return an empty list if there is none. The paths may be returned in any order.",
        ),
        examples=[
            ("a 4 x 4 maze with one wall column", '["DDRDRR", "DRDDRR"]', "Two routes lead to the exit"),
            ("a 2 x 2 maze with no walls", '["DR", "RD"]', "Down then right, or right then down"),
        ],
        constraints=["2 <= n <= 5", "maze[i][j] is 0 or 1"],
        todo="Try the four moves from each open, unvisited cell; mark the cell while it is on the path and unmark it on the way back.",
        solution="""
            def rat_in_a_maze(maze: list[list[int]]) -> list[str]:
                n = len(maze)
                paths = []
                if maze[0][0] == 0:
                    return paths
                visited = [[False] * n for _ in range(n)]
                moves = [("D", 1, 0), ("L", 0, -1), ("R", 0, 1), ("U", -1, 0)]
                def walk(r: int, c: int, path: str) -> None:
                    if r == n - 1 and c == n - 1:
                        paths.append(path)
                        return
                    visited[r][c] = True
                    for letter, dr, dc in moves:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n and maze[nr][nc] == 1 and not visited[nr][nc]:
                            walk(nr, nc, path + letter)
                    visited[r][c] = False
                walk(0, 0, "")
                return paths
        """,
        trace=2,
        comparator="sorted_list",
        cases=[
            ("[[1, 0, 0, 0], [1, 1, 0, 1], [1, 1, 0, 0], [0, 1, 1, 1]]", '["DDRDRR", "DRDDRR"]', False),
            ("[[1, 1], [1, 1]]", '["DR", "RD"]', False),
            ("[[1, 0], [0, 1]]", "[]", True),
            ("[[0, 1], [1, 1]]", "[]", True),
            ("[[1, 1, 1], [1, 1, 1], [1, 1, 1]]", '["DDRR", "DDRURD", "DDRUURDD", "DRDR", "DRRD", "DRURDD", "RDDR", "RDLDRR", "RDRD", "RRDD", "RRDLDR", "RRDLLDRR"]', True),
        ],
        hints=(
            "From any cell the rat has up to four moves. What stops it from walking in circles forever?",
            "Keep a visited grid. A cell is blocked while it is on the current path, but a different path may use it again.",
            "When the recursion returns from a cell, the cell must become available again. Record the path as soon as the last cell is reached.",
        ),
        approaches=[
            ("Enumerate all walks, then filter", "Generate move strings and test each one against the maze.", "O(4^(n*n))", "O(n * n)", False),
            ("DFS with visited marking", "Only extend onto open, unvisited cells and unmark on return.", "O(4^(n*n))", "O(n * n)", True),
        ],
        notes=[
            (17, "Unmarking lets other paths pass through this cell later; only cells on the current path are blocked.", False),
        ],
        predictions=[
            (10, "For the 2 x 2 maze with no walls, what is <code>path</code> the first time <code>paths.append(path)</code> is reached?", '"DR", the first route to the exit (down was tried first).'),
        ],
        patterns=["Recursion", "Matrix"],
        techniques=["Backtracking", "Grid Neighbours"],
    ),
    problem(
        slug="m-coloring-problem",
        title="M-Coloring Problem",
        topic="backtracking",
        difficulty="medium",
        fn="can_color_graph",
        signature="(graph: list[list[int]], m: int) -> bool",
        description=html(
            "<code>graph</code> is an adjacency matrix: <code>graph[i][j] == 1</code> means nodes <code>i</code> and <code>j</code> are joined by an edge. Return <code>True</code> if every node can be given one of <code>m</code> colours so that no two joined nodes share a colour, otherwise <code>False</code>.",
        ),
        examples=[
            ("a triangle, m = 3", "True", "Each of the three nodes gets its own colour"),
            ("a triangle, m = 2", "False", "Three mutually joined nodes need three colours"),
        ],
        constraints=["1 <= n <= 8", "graph is symmetric with a zero diagonal", "1 <= m <= 8"],
        todo="Colour nodes one by one; for each node try every colour that no neighbour already uses, and undo it if the rest fails.",
        solution="""
            def can_color_graph(graph: list[list[int]], m: int) -> bool:
                n = len(graph)
                colors = [0] * n
                def is_safe(node: int, color: int) -> bool:
                    for other in range(n):
                        if graph[node][other] == 1 and colors[other] == color:
                            return False
                    return True
                def paint(node: int) -> bool:
                    if node == n:
                        return True
                    for color in range(1, m + 1):
                        if is_safe(node, color):
                            colors[node] = color
                            if paint(node + 1):
                                return True
                            colors[node] = 0
                    return False
                return paint(0)
        """,
        trace=1,
        cases=[
            ("[[0, 1, 1], [1, 0, 1], [1, 1, 0]], 3", "True", False),
            ("[[0, 1, 1], [1, 0, 1], [1, 1, 0]], 2", "False", False),
            ("[[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]], 2", "True", True),
            ("[[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]], 3", "False", True),
            ("[[0]], 1", "True", True),
        ],
        hints=(
            "Think of colouring the nodes in order 0, 1, 2, .... What decides whether a colour is allowed for the current node?",
            "A colour is allowed if no already-coloured neighbour has it. Write a small helper that checks this.",
            "If no colour works for a later node, the earlier choices were wrong: undo the last colour and try the next one.",
        ),
        approaches=[
            ("Try every assignment", "Check all m^n colourings against every edge.", "O(m^n * n^2)", "O(n)", False),
            ("Backtracking with a safety check", "Reject a colour as soon as a neighbour uses it, pruning most assignments.", "O(m^n)", "O(n)", True),
        ],
        notes=[
            (17, "Resetting the colour to 0 undoes the choice so the next colour is checked against a clean state.", False),
        ],
        predictions=[
            (11, "For a triangle, m = 3, what is <code>colors</code> the first time <code>return True</code> is reached?", "[1, 2, 3], a valid colouring."),
        ],
        patterns=["Recursion"],
        techniques=["Backtracking", "Pruning"],
    ),
    problem(
        slug="expression-add-operators",
        title="Expression Add Operators",
        topic="backtracking",
        difficulty="hard",
        fn="expression_add_operators",
        signature="(num: str, target: int) -> list[str]",
        description=html(
            "<code>num</code> is a string of digits. Insert <code>+</code>, <code>-</code> or <code>*</code> between some digits (or none) so the expression evaluates to <code>target</code>, using normal precedence (multiplication first).",
            "Operands must not have leading zeros (so <code>05</code> is not allowed, but <code>0</code> alone is). Return every valid expression; the order does not matter.",
        ),
        examples=[
            ('num = "123", target = 6', '["1+2+3", "1*2*3"]', "1+2+3 and 1*2*3"),
            ('num = "232", target = 8', '["2+3*2", "2*3+2"]', "2*3+2 and 2+3*2"),
        ],
        constraints=["1 <= len(num) <= 10", "num contains only digits", "-2^31 <= target <= 2^31 - 1"],
        todo="Choose the next operand, then try +, - and *; remember the last term so a * can undo it.",
        solution="""
            def expression_add_operators(num: str, target: int) -> list[str]:
                result = []
                def build(index: int, expr: str, value: int, last: int) -> None:
                    if index == len(num):
                        if value == target:
                            result.append(expr)
                        return
                    for end in range(index + 1, len(num) + 1):
                        if end > index + 1 and num[index] == "0":
                            break
                        text = num[index:end]
                        n = int(text)
                        if index == 0:
                            build(end, text, n, n)
                        else:
                            build(end, expr + "+" + text, value + n, n)
                            build(end, expr + "-" + text, value - n, -n)
                            build(end, expr + "*" + text, value - last + last * n, last * n)
                build(0, "", 0, 0)
                return result
        """,
        trace=3,
        comparator="sorted_list",
        cases=[
            ('"123", 6', '["1+2+3", "1*2*3"]', False),
            ('"232", 8', '["2+3*2", "2*3+2"]', False),
            ('"12", 3', '["1+2"]', False),
            ('"105", 5', '["1*0+5", "10-5"]', True),
            ('"00", 0', '["0+0", "0-0", "0*0"]', True),
            ('"3456237490", 9191', "[]", True),
        ],
        hints=(
            "Between every two digits you can put an operator or nothing (which makes a longer number). How many operand splits are possible?",
            "Evaluate while you build instead of at the end: carry the running value and the last term added.",
            "Multiplication binds tighter than the previous term, so a * must replace that term rather than add to the total. Watch out for operands with leading zeros.",
        ),
        approaches=[
            ("Build every expression, then evaluate", "Generate all strings and evaluate each one.", "O(4^n * n)", "O(n)", False),
            ("Backtracking with a running value", "Track the value and the last term so each extension is O(1).", "O(4^n)", "O(n)", True),
        ],
        notes=[
            (18, "A product applies to the previous term only: undo it (value - last) and add last * n in its place.", False),
        ],
        predictions=[
            (6, 'For num = "12", target = 3, what is <code>expr</code> the first time <code>result.append(expr)</code> is reached?', '"1+2", the first expression that reaches the target.'),
        ],
        patterns=["Recursion", "Strings"],
        techniques=["Backtracking", "Slicing"],
    ),
]
