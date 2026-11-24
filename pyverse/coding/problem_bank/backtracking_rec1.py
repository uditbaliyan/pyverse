# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="combination-sum",
        title="Combination Sum",
        topic="backtracking",
        difficulty="medium",
        fn="combination_sum",
        signature="(candidates: list[int], target: int) -> list[list[int]]",
        description=html(
            "<code>candidates</code> holds distinct positive integers. Return every unique combination of them that adds up to <code>target</code>. A number may be used any number of times.",
            "Inside each combination keep the numbers in the same order as they appear in <code>candidates</code>. The combinations may be returned in any order.",
        ),
        examples=[
            ("candidates = [2, 3, 6, 7], target = 7", "[[2, 2, 3], [7]]", "2 + 2 + 3 and 7 are the only ways"),
            ("candidates = [2, 3, 5], target = 8", "[[2, 2, 2, 2], [2, 3, 3], [3, 5]]", "Three combinations reach 8"),
        ],
        constraints=["1 <= len(candidates) <= 30", "2 <= candidates[i] <= 40, all distinct", "1 <= target <= 40"],
        todo="Choose a candidate, recurse with the reduced target starting from the same index, then undo the choice.",
        solution="""
            def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
                result = []
                def search(start: int, remaining: int, path: list[int]) -> None:
                    if remaining == 0:
                        result.append(path[:])
                        return
                    for i in range(start, len(candidates)):
                        if candidates[i] > remaining:
                            continue
                        path.append(candidates[i])
                        search(i, remaining - candidates[i], path)
                        path.pop()
                search(0, target, [])
                return result
        """,
        trace=3,
        comparator="sorted_list",
        cases=[
            ("[2, 3, 6, 7], 7", "[[2, 2, 3], [7]]", False),
            ("[2, 3, 5], 8", "[[2, 2, 2, 2], [2, 3, 3], [3, 5]]", False),
            ("[2, 3], 6", "[[2, 2, 2], [3, 3]]", False),
            ("[2], 1", "[]", True),
            ("[3, 5, 8], 11", "[[3, 3, 5], [3, 8]]", True),
            ("[2, 4], 6", "[[2, 2, 2], [2, 4]]", True),
        ],
        hints=(
            "The same number can repeat, but [2, 3] and [3, 2] must count once. How can you avoid listing both?",
            "Only ever pick candidates at or after the index you last used; staying on the same index allows repeats.",
            "After exploring a choice, remove it from the path again so the next candidate sees the same state.",
        ),
        approaches=[
            ("Try every multiset", "Enumerate multisets of candidates up to the target and filter by sum.", "O(too large)", "O(target)", False),
            ("Backtracking with a start index", "Never move backwards in the list, so each combination is built in one order only.", "O(2^target)", "O(target)", True),
        ],
        notes=[
            (12, "pop undoes the append on line 10, so the next candidate in the loop starts from the same path.", False),
        ],
        predictions=[
            (5, "For candidates = [2, 3], target = 6, what is <code>path</code> the first time <code>result.append(path[:])</code> is reached?", "[2, 2, 2], the first combination found."),
        ],
        patterns=["Recursion"],
        techniques=["Backtracking", "Start Index"],
    ),
    problem(
        slug="combination-sum-ii",
        title="Combination Sum II",
        topic="backtracking",
        difficulty="medium",
        fn="combination_sum_ii",
        signature="(candidates: list[int], target: int) -> list[list[int]]",
        description=html(
            "<code>candidates</code> may contain repeated numbers. Return every unique combination that adds up to <code>target</code>, using each position of <code>candidates</code> at most once.",
            "Each combination must be in non-decreasing order, and no combination may appear twice. The combinations may be returned in any order.",
        ),
        examples=[
            ("candidates = [10, 1, 2, 7, 6, 1, 5], target = 8", "[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]", "[1, 1, 6], [1, 2, 5], [1, 7] and [2, 6]"),
            ("candidates = [2, 5, 2, 1, 2], target = 5", "[[1, 2, 2], [5]]", "[1, 2, 2] and [5]"),
        ],
        constraints=["1 <= len(candidates) <= 20", "1 <= candidates[i] <= 30", "1 <= target <= 30"],
        todo="Sort first, then skip a value equal to the previous one at the same recursion depth.",
        solution="""
            def combination_sum_ii(candidates: list[int], target: int) -> list[list[int]]:
                nums = sorted(candidates)
                result = []
                def search(start: int, remaining: int, path: list[int]) -> None:
                    if remaining == 0:
                        result.append(path[:])
                        return
                    for i in range(start, len(nums)):
                        if i > start and nums[i] == nums[i - 1]:
                            continue
                        if nums[i] > remaining:
                            break
                        path.append(nums[i])
                        search(i + 1, remaining - nums[i], path)
                        path.pop()
                search(0, target, [])
                return result
        """,
        trace=3,
        comparator="sorted_list",
        cases=[
            ("[10, 1, 2, 7, 6, 1, 5], 8", "[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]", False),
            ("[2, 5, 2, 1, 2], 5", "[[1, 2, 2], [5]]", False),
            ("[1, 2, 2], 3", "[[1, 2]]", False),
            ("[1], 2", "[]", True),
            ("[3, 3, 3], 6", "[[3, 3]]", True),
            ("[1, 1, 1, 1], 3", "[[1, 1, 1]]", True),
        ],
        hints=(
            "If you use every position at most once, how can the same combination still show up twice?",
            "Sort the numbers so equal values sit next to each other, then decide which of them may start a branch.",
            "Within one loop, a value that equals the one just before it would only repeat work; later depths can still use equal values.",
        ),
        approaches=[
            ("Generate all subsets, deduplicate", "Enumerate every subset, keep those that sum to target, and put them in a set.", "O(2^n * n)", "O(2^n)", False),
            ("Sort and skip siblings", "Skip a repeated value among siblings, so each distinct combination is generated once.", "O(2^n)", "O(n)", True),
        ],
        notes=[
            (9, "i > start, not i > 0: equal values are skipped only among siblings, so [1, 1, 6] can still use both 1s.", False),
        ],
        predictions=[
            (6, "For candidates = [1, 2, 2], target = 3, what is <code>path</code> the first time <code>result.append(path[:])</code> is reached?", "[1, 2], the first combination found; the second 2 is skipped later because it repeats a sibling."),
        ],
        patterns=["Recursion", "Sorting"],
        techniques=["Backtracking", "Skip Duplicates"],
    ),
    problem(
        slug="subsets-ii",
        title="Subsets II",
        topic="backtracking",
        difficulty="medium",
        fn="subsets_with_duplicates",
        signature="(nums: list[int]) -> list[list[int]]",
        description=html(
            "<code>nums</code> may contain duplicates. Return every distinct subset (the power set without repeats), including the empty subset.",
            "Write each subset in non-decreasing order. The subsets may be returned in any order.",
        ),
        examples=[
            ("nums = [1, 2, 2]", "[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]", "Six distinct subsets, not eight"),
            ("nums = [0]", "[[], [0]]", "Just the empty subset and [0]"),
        ],
        constraints=["1 <= len(nums) <= 10", "-10 <= nums[i] <= 10"],
        todo="Sort, record the current path at every call, and skip a value equal to the previous one among siblings.",
        solution="""
            def subsets_with_duplicates(nums: list[int]) -> list[list[int]]:
                nums = sorted(nums)
                result = []
                def search(start: int, path: list[int]) -> None:
                    result.append(path[:])
                    for i in range(start, len(nums)):
                        if i > start and nums[i] == nums[i - 1]:
                            continue
                        path.append(nums[i])
                        search(i + 1, path)
                        path.pop()
                search(0, [])
                return result
        """,
        trace=1,
        comparator="sorted_list",
        cases=[
            ("[1, 2, 2]", "[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]", False),
            ("[0]", "[[], [0]]", False),
            ("[4, 4, 4, 1, 4]", "[[], [1], [1, 4], [1, 4, 4], [1, 4, 4, 4], [1, 4, 4, 4, 4], [4], [4, 4], [4, 4, 4], [4, 4, 4, 4]]", True),
            ("[1, 1]", "[[], [1], [1, 1]]", True),
        ],
        hints=(
            "Without duplicates, every path of the recursion is a subset. What goes wrong when values repeat?",
            "Sort the numbers so equal values are neighbours, then only the first of a run of equal values may start a branch.",
            "Record the path on entry to every call, not only at the end, because every partial path is a subset.",
        ),
        approaches=[
            ("Generate all, deduplicate", "Make every subset of sorted nums and drop repeats with a set.", "O(2^n * n)", "O(2^n)", False),
            ("Sort and skip siblings", "Skip equal neighbours inside each loop so no subset is built twice.", "O(2^n * n)", "O(n)", True),
        ],
        notes=[
            (7, "i > start means this value is a repeat of a sibling we already expanded, so the whole branch would be a duplicate.", False),
        ],
        predictions=[
            (10, "For nums = [1, 2, 2], what is <code>path</code> the third time <code>search(i + 1, path)</code> is reached?", "[1, 2, 2]; the first two arrivals were [1] and [1, 2]."),
        ],
        patterns=["Recursion", "Sorting"],
        techniques=["Backtracking", "Skip Duplicates"],
    ),
    problem(
        slug="combination-sum-iii",
        title="Combination Sum III",
        topic="backtracking",
        difficulty="medium",
        fn="combination_sum_iii",
        signature="(k: int, n: int) -> list[list[int]]",
        description=html(
            "Choose exactly <code>k</code> different digits from <code>1</code> to <code>9</code> so that they add up to <code>n</code>. Return every such combination, each in increasing order.",
            "No digit may be used twice. The combinations may be returned in any order.",
        ),
        examples=[
            ("k = 3, n = 7", "[[1, 2, 4]]", "Only 1 + 2 + 4 works"),
            ("k = 3, n = 9", "[[1, 2, 6], [1, 3, 5], [2, 3, 4]]", "1 + 2 + 6, 1 + 3 + 5 and 2 + 3 + 4"),
        ],
        constraints=["2 <= k <= 9", "1 <= n <= 60"],
        todo="Pick digits in increasing order; stop when you hold k digits and check whether the sum is n.",
        solution="""
            def combination_sum_iii(k: int, n: int) -> list[list[int]]:
                result = []
                def search(start: int, remaining: int, path: list[int]) -> None:
                    if len(path) == k:
                        if remaining == 0:
                            result.append(path[:])
                        return
                    for digit in range(start, 10):
                        if digit > remaining:
                            break
                        path.append(digit)
                        search(digit + 1, remaining - digit, path)
                        path.pop()
                search(1, n, [])
                return result
        """,
        trace=3,
        comparator="sorted_list",
        cases=[
            ("3, 7", "[[1, 2, 4]]", False),
            ("3, 9", "[[1, 2, 6], [1, 3, 5], [2, 3, 4]]", False),
            ("2, 4", "[[1, 3]]", False),
            ("4, 1", "[]", True),
            ("2, 18", "[]", True),
            ("9, 45", "[[1, 2, 3, 4, 5, 6, 7, 8, 9]]", True),
        ],
        hints=(
            "Only nine digits exist, so the search space is small. How do you stop yourself from picking the same digit twice or listing a set in two orders?",
            "Pass the next allowed digit down the recursion; picking digit d means the next pick must be at least d + 1.",
            "A combination is only complete when it holds exactly k digits; at that point check whether the leftover sum is 0.",
        ),
        approaches=[
            ("Check every k-subset", "Use combinations of 1..9 and keep the ones that sum to n.", "O(C(9, k) * k)", "O(k)", False),
            ("Backtracking with pruning", "Stop a branch as soon as the next digit exceeds what is left.", "O(C(9, k) * k)", "O(k)", True),
        ],
        notes=[
            (9, "Digits are tried in increasing order, so once one is too big every later digit is too big as well.", False),
        ],
        predictions=[
            (6, "For k = 2, n = 4, what is <code>path</code> the first time <code>result.append(path[:])</code> is reached?", "[1, 3], the first valid combination."),
        ],
        patterns=["Recursion"],
        techniques=["Backtracking", "Pruning"],
    ),
    problem(
        slug="letter-combinations-of-a-phone-number",
        title="Letter Combinations of a Phone Number",
        topic="backtracking",
        difficulty="medium",
        fn="letter_combinations",
        signature="(digits: str) -> list[str]",
        description=html(
            "On a classic phone keypad, 2 is abc, 3 is def, 4 is ghi, 5 is jkl, 6 is mno, 7 is pqrs, 8 is tuv and 9 is wxyz. Given a string of digits from 2 to 9, return every letter string those keys could spell.",
            "Return an empty list for an empty input. The strings may be returned in any order.",
        ),
        examples=[
            ('digits = "23"', '["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]', "Three letters for 2 times three for 3 gives nine strings"),
            ('digits = "2"', '["a", "b", "c"]', "Just a, b and c"),
        ],
        constraints=["0 <= len(digits) <= 4", "digits[i] is between '2' and '9'"],
        todo="Choose one letter for the current digit, then recurse to the next digit; record the string at the end.",
        solution="""
            def letter_combinations(digits: str) -> list[str]:
                if not digits:
                    return []
                letters = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
                result = []
                def build(index: int, current: str) -> None:
                    if index == len(digits):
                        result.append(current)
                        return
                    for ch in letters[digits[index]]:
                        build(index + 1, current + ch)
                build(0, "")
                return result
        """,
        trace=1,
        comparator="sorted_list",
        cases=[
            ('"23"', '["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]', False),
            ('"2"', '["a", "b", "c"]', False),
            ('""', "[]", True),
            ('"79"', '["pw", "px", "py", "pz", "qw", "qx", "qy", "qz", "rw", "rx", "ry", "rz", "sw", "sx", "sy", "sz"]', True),
            ('"234"', '["adg", "adh", "adi", "aeg", "aeh", "aei", "afg", "afh", "afi", "bdg", "bdh", "bdi", "beg", "beh", "bei", "bfg", "bfh", "bfi", "cdg", "cdh", "cdi", "ceg", "ceh", "cei", "cfg", "cfh", "cfi"]', True),
        ],
        hints=(
            "Each digit independently offers a few letters. What does the full answer look like for a single digit?",
            "Handle the digits left to right, keeping the string built so far as part of the recursion state.",
            "When the index reaches the end of digits, the current string is finished. Do not forget the empty-input special case.",
        ),
        approaches=[
            ("Iterative product", "Fold the digits, expanding the list of strings by one digit at a time.", "O(4^n * n)", "O(4^n * n)", False),
            ("Backtracking", "Recurse one digit per level and append each letter in turn.", "O(4^n * n)", "O(n)", True),
        ],
        notes=[
            (7, "Reaching the end of the digits means one letter was chosen for each, so the string is complete.", False),
        ],
        predictions=[
            (8, 'For digits = "23", what is <code>current</code> the first time <code>result.append(current)</code> is reached?', '"ad", the first string built.'),
        ],
        patterns=["Recursion", "Strings"],
        techniques=["Backtracking", "Dict Lookup"],
    ),
    problem(
        slug="palindrome-partitioning",
        title="Palindrome Partitioning",
        topic="backtracking",
        difficulty="medium",
        fn="palindrome_partitions",
        signature="(s: str) -> list[list[str]]",
        description=html(
            "Split <code>s</code> into consecutive pieces so that every piece is a palindrome. Return all possible ways to do it, each as a list of the pieces in order.",
            "The partitions may be returned in any order.",
        ),
        examples=[
            ('s = "aab"', '[["a", "a", "b"], ["aa", "b"]]', 'Either ["a", "a", "b"] or ["aa", "b"]'),
            ('s = "a"', '[["a"]]', "One piece, the string itself"),
        ],
        constraints=["1 <= len(s) <= 12", "s uses lowercase English letters"],
        todo="Try every prefix from the current position; if it is a palindrome, take it and split the rest.",
        solution="""
            def palindrome_partitions(s: str) -> list[list[str]]:
                result = []
                def split(start: int, path: list[str]) -> None:
                    if start == len(s):
                        result.append(path[:])
                        return
                    for end in range(start + 1, len(s) + 1):
                        piece = s[start:end]
                        if piece == piece[::-1]:
                            path.append(piece)
                            split(end, path)
                            path.pop()
                split(0, [])
                return result
        """,
        trace=1,
        comparator="sorted_list",
        cases=[
            ('"aab"', '[["a", "a", "b"], ["aa", "b"]]', False),
            ('"a"', '[["a"]]', False),
            ('"aaa"', '[["a", "a", "a"], ["a", "aa"], ["aa", "a"], ["aaa"]]', True),
            ('"abc"', '[["a", "b", "c"]]', True),
            ('"abba"', '[["a", "b", "b", "a"], ["a", "bb", "a"], ["abba"]]', True),
        ],
        hints=(
            "The first piece must be some prefix of s. Which prefixes are allowed?",
            "For each palindromic prefix, the rest of the string is the same problem on a shorter string.",
            "Keep the pieces so far in a list; when start reaches the end of s, that list is one finished partition.",
        ),
        approaches=[
            ("Try every set of cut points", "Choose cut positions with a bitmask and test every piece.", "O(2^n * n)", "O(n)", False),
            ("Backtracking over prefixes", "Only cut after a palindromic prefix, so invalid splits are never explored.", "O(2^n * n)", "O(n)", True),
        ],
        notes=[
            (9, "A piece is only kept when it reads the same reversed, so every complete path is a valid partition.", False),
        ],
        predictions=[
            (5, 'For s = "aab", what is <code>path</code> the first time <code>result.append(path[:])</code> is reached?', "['a', 'a', 'b'], the first complete partition."),
        ],
        patterns=["Recursion", "Strings"],
        techniques=["Backtracking", "Slicing"],
    ),
    problem(
        slug="word-search",
        title="Word Search",
        topic="backtracking",
        difficulty="medium",
        fn="word_search",
        signature="(board: list[list[str]], word: str) -> bool",
        description=html(
            "<code>board</code> is a grid of single letters. Return <code>True</code> if <code>word</code> can be traced by moving between horizontally or vertically adjacent cells, never using the same cell twice in one path.",
            "A path may start from any cell.",
        ),
        examples=[
            ('board = ["ABCE", "SFCS", "ADEE"], word = "ABCCED"', "True", "Follow A, B, C, then down to C, E and D"),
            ('same board, word = "SEE"', "True", "S at the right edge, then down and left through two Es"),
        ],
        constraints=["1 <= rows, cols <= 6", "1 <= len(word) <= 15", "Letters are uppercase or lowercase English letters"],
        todo="Start a depth-first search from every cell, marking cells as visited while they are on the current path.",
        solution="""
            def word_search(board: list[list[str]], word: str) -> bool:
                rows, cols = len(board), len(board[0])
                visited = set()
                def walk(r: int, c: int, i: int) -> bool:
                    if i == len(word):
                        return True
                    if r < 0 or r >= rows or c < 0 or c >= cols:
                        return False
                    if (r, c) in visited or board[r][c] != word[i]:
                        return False
                    visited.add((r, c))
                    found = walk(r + 1, c, i + 1) or walk(r - 1, c, i + 1) or walk(r, c + 1, i + 1) or walk(r, c - 1, i + 1)
                    visited.remove((r, c))
                    return found
                for r in range(rows):
                    for c in range(cols):
                        if walk(r, c, 0):
                            return True
                return False
        """,
        trace=3,
        cases=[
            ('[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"', "True", False),
            ('[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"', "True", False),
            ('[["A", "B"], ["C", "D"]], "ABDC"', "True", False),
            ('[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"', "False", True),
            ('[["a"]], "a"', "True", True),
            ('[["C", "A", "A"], ["A", "A", "A"], ["B", "C", "D"]], "AAB"', "True", True),
        ],
        hints=(
            "A path may start anywhere. How do you try every possible start cell?",
            "From a matching cell, try its four neighbours for the next letter. Which cells must be off limits?",
            "A cell is off limits only while it is on the current path, so un-mark it when the search backs out of it.",
        ),
        approaches=[
            ("Copy the path at every step", "Pass an immutable set of visited cells down each call.", "O(R * C * 4^L)", "O(L^2)", False),
            ("DFS with mark and unmark", "Share one visited set; add on entry, remove on exit.", "O(R * C * 3^L)", "O(L)", True),
        ],
        notes=[
            (13, "Removing the cell frees it for other paths; without this a cell blocked on one branch would stay blocked everywhere.", False),
        ],
        predictions=[
            (6, 'For board = ["AB", "CD"], word = "ABDC", what are <code>r</code>, <code>c</code> and <code>i</code> the first time <code>return True</code> is reached?', "r = 2, c = 0 and i = 4; the whole word has been matched."),
        ],
        patterns=["Recursion", "Matrix"],
        techniques=["Backtracking", "Set", "Grid Neighbours"],
    ),
    problem(
        slug="n-queens",
        title="N-Queens",
        topic="backtracking",
        difficulty="hard",
        fn="n_queens",
        signature="(n: int) -> list[list[str]]",
        description=html(
            "Place <code>n</code> queens on an <code>n x n</code> chessboard so that no two attack each other (no shared row, column or diagonal). Return every distinct arrangement.",
            "Each arrangement is a list of <code>n</code> strings, one per row, with <code>Q</code> for a queen and <code>.</code> for an empty cell. The arrangements may be returned in any order.",
        ),
        examples=[
            ("n = 4", '[[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]', "Two arrangements exist for a 4 x 4 board"),
            ("n = 1", '[["Q"]]', "A single queen on a single cell"),
        ],
        constraints=["1 <= n <= 6"],
        todo="Place one queen per row; keep sets of used columns and diagonals to reject attacked squares.",
        solution="""
            def n_queens(n: int) -> list[list[str]]:
                result = []
                cols = set()
                down = set()
                up = set()
                placement = []
                def place(row: int) -> None:
                    if row == n:
                        result.append(["." * c + "Q" + "." * (n - c - 1) for c in placement])
                        return
                    for c in range(n):
                        if c in cols or row - c in down or row + c in up:
                            continue
                        cols.add(c)
                        down.add(row - c)
                        up.add(row + c)
                        placement.append(c)
                        place(row + 1)
                        placement.pop()
                        cols.remove(c)
                        down.remove(row - c)
                        up.remove(row + c)
                place(0)
                return result
        """,
        trace=2,
        comparator="sorted_list",
        cases=[
            ("4", '[[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]', False),
            ("1", '[["Q"]]', False),
            ("2", "[]", True),
            ("3", "[]", True),
            ("5", '[["Q....", "..Q..", "....Q", ".Q...", "...Q."], ["Q....", "...Q.", ".Q...", "....Q", "..Q.."], [".Q...", "...Q.", "Q....", "..Q..", "....Q"], [".Q...", "....Q", "..Q..", "Q....", "...Q."], ["..Q..", "Q....", "...Q.", ".Q...", "....Q"], ["..Q..", "....Q", ".Q...", "...Q.", "Q...."], ["...Q.", "Q....", "..Q..", "....Q", ".Q..."], ["...Q.", ".Q...", "....Q", "..Q..", "Q...."], ["....Q", ".Q...", "...Q.", "Q....", "..Q.."], ["....Q", "..Q..", "Q....", "...Q.", ".Q..."]]', True),
        ],
        hints=(
            "Two queens can never share a row. How does that shape the recursion?",
            "Place exactly one queen per row. For each row, try each column and ask whether that square is attacked.",
            "Cells on one diagonal share row - col, and cells on the other share row + col, so three sets answer 'is this square attacked' instantly.",
        ),
        approaches=[
            ("Try all permutations", "Test every column permutation for diagonal clashes.", "O(n! * n)", "O(n)", False),
            ("Backtracking with attack sets", "Place row by row and reject attacked columns and diagonals in O(1).", "O(n!)", "O(n)", True),
        ],
        notes=[
            (12, "Squares on one diagonal share row - c, squares on the other share row + c, so two sets cover both diagonals.", False),
        ],
        predictions=[
            (9, 'For n = 1, what is <code>placement</code> the first time <code>result.append(["." * c + "Q" + "." * (n - c - 1) for c in placement])</code> is reached?', "[0], the only queen sits in column 0."),
        ],
        patterns=["Recursion", "Matrix"],
        techniques=["Backtracking", "Set"],
    ),
]
