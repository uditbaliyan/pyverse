# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="leaders-in-an-array",
        title="Leaders in an Array",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="leaders",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "An element is a <strong>leader</strong> if it is strictly greater than every element to its right. The last element is always a leader.",
            "Return the leaders in the same left-to-right order they appear in <code>nums</code>.",
        ),
        examples=[
            ("nums = [10, 22, 12, 3, 0, 6]", "[22, 12, 6]", "10 loses to 22; 3 and 0 lose to 6"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "-10^9 <= nums[i] <= 10^9"],
        todo="Scan from the right, remembering the largest value seen so far; collect values that beat it, then restore the order.",
        solution="""
            def leaders(nums: list[int]) -> list[int]:
                result = []
                best = None
                for i in range(len(nums) - 1, -1, -1):
                    if best is None or nums[i] > best:
                        result.append(nums[i])
                        best = nums[i]
                result.reverse()
                return result
        """,
        trace=1,
        cases=[
            ("[10, 22, 12, 3, 0, 6]", "[22, 12, 6]", False),
            ("[4, 7, 1, 0]", "[7, 1, 0]", False),
            ("[]", "[]", True),
            ("[5]", "[5]", True),
            ("[1, 2, 3, 4]", "[4]", True),
            ("[4, 3, 2, 1]", "[4, 3, 2, 1]", True),
            ("[5, 5, 5]", "[5]", True),
        ],
        hints=(
            "Checking every element against everything on its right is O(n^2). Which direction makes that unnecessary?",
            "Walk from the right and keep the maximum of what you have already passed.",
            "You will collect leaders right to left, so reverse the list before returning.",
        ),
        approaches=[
            ("Brute force", "For each element scan everything to its right.", "O(n^2)", "O(1)", False),
            ("Right-to-left scan", "Track the running maximum from the right.", "O(n)", "O(1) beyond the output", True),
        ],
        notes=[
            (8, "Leaders were gathered right to left, so reversing restores the original order.", False),
        ],
        predictions=[
            (8, "For [10, 22, 12, 3, 0, 6], what is <code>result</code> when this line is reached?", "[6, 12, 22]."),
        ],
        patterns=["Arrays", "Running Maximum"],
        techniques=["Reverse Iteration", "Running Maximum"],
    ),
    problem(
        slug="rearrange-array-elements-by-sign",
        title="Rearrange Array Elements by Sign",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="rearrange_by_sign",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "<code>nums</code> has an equal number of positive and negative integers and no zeros. Return a new list in which signs alternate, starting with a positive value.",
            "Positives must keep their original relative order, and so must negatives.",
        ),
        examples=[
            ("nums = [3, 1, -2, -5, 2, -4]", "[3, -2, 1, -5, 2, -4]", "positives 3, 1, 2 go to even slots; negatives -2, -5, -4 to odd slots"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "nums has as many positives as negatives", "nums[i] != 0"],
        todo="Keep two write positions: positives fill indices 0, 2, 4, ... and negatives fill 1, 3, 5, ...",
        solution="""
            def rearrange_by_sign(nums: list[int]) -> list[int]:
                result = [0] * len(nums)
                pos = 0
                neg = 1
                for x in nums:
                    if x > 0:
                        result[pos] = x
                        pos += 2
                    else:
                        result[neg] = x
                        neg += 2
                return result
        """,
        trace=1,
        cases=[
            ("[3, 1, -2, -5, 2, -4]", "[3, -2, 1, -5, 2, -4]", False),
            ("[-1, 1]", "[1, -1]", False),
            ("[]", "[]", True),
            ("[1, -1]", "[1, -1]", True),
            ("[-3, -2, 5, 6]", "[5, -3, 6, -2]", True),
            ("[2, 4, -1, -3]", "[2, -1, 4, -3]", True),
        ],
        hints=(
            "Where must the k-th positive value end up in the answer?",
            "Positives go to even indices and negatives to odd indices, so each needs its own write position.",
            "Advance each write position by 2 after using it.",
        ),
        approaches=[
            ("Separate lists then interleave", "Split into positives and negatives, then zip them back together.", "O(n)", "O(n)", False),
            ("Two write pointers", "Write each value directly to its final slot in one pass.", "O(n)", "O(n) for the output", True),
        ],
        notes=[
            (7, "pos only ever visits even indices, so positives can never overwrite a negative slot.", False),
        ],
        predictions=[
            (12, "For [3, 1, -2, -5, 2, -4], what are <code>pos</code> and <code>neg</code> when this line is reached?", "pos = 6 and neg = 7: three values were written to each side."),
        ],
        patterns=["Arrays", "Two Pointers"],
        techniques=["Write Pointers", "Stable Partition"],
    ),
    problem(
        slug="pascals-triangle-value",
        title="Pascal's Triangle: Value at a Position",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="pascal_value",
        signature="(row: int, col: int) -> int",
        description=html(
            "Pascal's triangle starts with a single <code>1</code>; each later number is the sum of the two above it. Return the number at 1-indexed position <code>(row, col)</code>.",
            "Do not build the triangle. The value equals the binomial coefficient C(row - 1, col - 1), which you can compute in <code>col - 1</code> steps.",
        ),
        examples=[
            ("row = 5, col = 3", "6", "row 5 is 1 4 6 4 1"),
            ("row = 1, col = 1", "1", "the apex"),
        ],
        constraints=["1 <= col <= row <= 30"],
        todo="Compute C(row - 1, col - 1) iteratively: multiply by (n - i) and divide by (i + 1) for i = 0 .. r - 1.",
        solution="""
            def pascal_value(row: int, col: int) -> int:
                n = row - 1
                r = col - 1
                result = 1
                for i in range(r):
                    result = result * (n - i) // (i + 1)
                return result
        """,
        trace=1,
        cases=[
            ("10, 5", "126", False),
            ("5, 3", "6", False),
            ("1, 1", "1", True),
            ("6, 1", "1", True),
            ("6, 6", "1", True),
            ("20, 10", "92378", True),
            ("30, 15", "77558760", True),
        ],
        hints=(
            "Row n of the triangle lists the binomial coefficients C(n - 1, 0), C(n - 1, 1), ...",
            "C(n, r) = n * (n - 1) * ... * (n - r + 1) / r!. Build it one factor at a time.",
            "Multiply first, then use <code>//</code>; after each step the running value is itself a binomial coefficient, so the division is exact.",
        ),
        approaches=[
            ("Build the triangle", "Compute rows 1..row by adding neighbours.", "O(row^2)", "O(row)", False),
            ("Multiplicative formula", "Compute C(n, r) in r steps.", "O(col)", "O(1)", True),
        ],
        notes=[
            (6, "Multiplying before dividing keeps every intermediate value an integer, because result is always C(n, i + 1) after step i.", False),
        ],
        predictions=[
            (6, "For row = 10, col = 5, what is <code>result</code> the third time this line is reached (before it updates)?", "36: after two steps result is C(9, 2) = 36."),
        ],
        patterns=["Math", "Combinatorics"],
        techniques=["Accumulator", "Integer Division"],
    ),
    problem(
        slug="rotate-matrix-by-90-degrees",
        title="Rotate Matrix by 90 Degrees",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="rotate_matrix",
        signature="(matrix: list[list[int]]) -> list[list[int]]",
        description=html(
            "Given a square <code>n x n</code> matrix, return a new matrix that is the original rotated <strong>90 degrees clockwise</strong>.",
            "A neat way: transpose the matrix, then reverse every row. Do not modify the input.",
        ),
        examples=[
            ("matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]", "the first column, read bottom to top, becomes the first row"),
        ],
        constraints=["1 <= n <= 200", "matrix is n x n"],
        todo="Copy the matrix, swap matrix[i][j] with matrix[j][i] above the diagonal, then reverse each row.",
        solution="""
            def rotate_matrix(matrix: list[list[int]]) -> list[list[int]]:
                n = len(matrix)
                rotated = [row[:] for row in matrix]
                for i in range(n):
                    for j in range(i + 1, n):
                        rotated[i][j], rotated[j][i] = rotated[j][i], rotated[i][j]
                for row in rotated:
                    row.reverse()
                return rotated
        """,
        trace=1,
        cases=[
            ("[[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]", False),
            ("[[1, 2], [3, 4]]", "[[3, 1], [4, 2]]", False),
            ("[[5]]", "[[5]]", True),
            ("[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]", "[[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]", True),
        ],
        hints=(
            "Where does the element in row 0, column j end up after a clockwise rotation?",
            "Transposing (swapping across the main diagonal) gets every element to the right row; the columns are then mirrored.",
            "Only swap pairs with j > i, otherwise you swap each pair twice and undo the transpose.",
        ),
        approaches=[
            ("New matrix by index formula", "<code>new[j][n - 1 - i] = old[i][j]</code>", "O(n^2)", "O(n^2)", False),
            ("Transpose then reverse rows", "Two simple passes; the in-place variant needs no copy.", "O(n^2)", "O(n^2) here, O(1) in place", True),
        ],
        notes=[
            (7, "Each pair above the diagonal is visited exactly once, so the matrix is transposed rather than restored.", False),
        ],
        predictions=[
            (7, "For the 3 x 3 example, what is <code>rotated</code> the first time this line is reached?", "[[1, 4, 7], [2, 5, 8], [3, 6, 9]]: the transpose."),
        ],
        patterns=["Matrix", "Arrays"],
        techniques=["Transpose", "Nested Loops", "Reversal"],
    ),
    problem(
        slug="set-matrix-zeroes",
        title="Set Matrix Zeroes",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="set_zeroes",
        signature="(matrix: list[list[int]]) -> list[list[int]]",
        description=html(
            "If a cell of <code>matrix</code> is <code>0</code>, its entire row and entire column must become <code>0</code>.",
            "Return the resulting matrix as a new list of lists, leaving the input unchanged. Zeroes that were created by this rule must not trigger further zeroing: decide which rows and columns to clear using the original matrix only.",
        ),
        examples=[
            ("matrix = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]", "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]", "the single zero clears row 1 and column 1"),
        ],
        constraints=["1 <= rows, cols <= 200", "-2^31 <= matrix[r][c] <= 2^31 - 1"],
        todo="Record the rows and columns that contain a zero, then build the new matrix, writing 0 for any cell in a recorded row or column.",
        solution="""
            def set_zeroes(matrix: list[list[int]]) -> list[list[int]]:
                rows = len(matrix)
                cols = len(matrix[0])
                zero_rows = set()
                zero_cols = set()
                for r in range(rows):
                    for c in range(cols):
                        if matrix[r][c] == 0:
                            zero_rows.add(r)
                            zero_cols.add(c)
                return [[0 if r in zero_rows or c in zero_cols else matrix[r][c] for c in range(cols)] for r in range(rows)]
        """,
        trace=1,
        cases=[
            ("[[1, 1, 1], [1, 0, 1], [1, 1, 1]]", "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]", False),
            ("[[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]", "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]", False),
            ("[[0]]", "[[0]]", True),
            ("[[1, 2], [3, 4]]", "[[1, 2], [3, 4]]", True),
            ("[[1, 0]]", "[[0, 0]]", True),
            ("[[0, 0, 0], [0, 0, 0]]", "[[0, 0, 0], [0, 0, 0]]", True),
        ],
        hints=(
            "Why can you not zero cells while you are still scanning for zeroes?",
            "First pass: remember which rows and which columns contain a zero. Second pass: build the answer.",
            "A cell becomes 0 when its row is in the zero-row set or its column is in the zero-column set.",
        ),
        approaches=[
            ("Row and column sets", "Record zero rows/columns, then rebuild.", "O(rows * cols)", "O(rows + cols) extra", False),
            ("First row/column as markers", "Use the matrix's own first row and column to store flags in place.", "O(rows * cols)", "O(1)", True),
        ],
        notes=[
            (8, "The scan reads only original values, so zeroes added later cannot spread.", False),
        ],
        predictions=[
            (11, "For the first example, what are <code>zero_rows</code> and <code>zero_cols</code> when this line is reached?", "{1} and {1}: only the centre cell is zero."),
        ],
        patterns=["Matrix", "Arrays", "Hashing"],
        techniques=["Two Pass", "Sets", "List Comprehension"],
    ),
    problem(
        slug="four-sum",
        title="4Sum",
        topic="arrays-and-hashing",
        difficulty="hard",
        fn="four_sum",
        signature="(nums: list[int], target: int) -> list[list[int]]",
        description=html(
            "Return every <strong>unique</strong> quadruplet of values from <code>nums</code> that adds up to <code>target</code>. The four values must come from four different positions, and no two quadruplets in the answer may contain the same four values.",
            "Each quadruplet is listed in ascending order; the quadruplets themselves may come in any order.",
        ),
        examples=[
            ("nums = [1, 0, -1, 0, -2, 2], target = 0", "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]", "three distinct quadruplets"),
        ],
        constraints=["0 <= len(nums) <= 200", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
        todo="Sort, fix the first two values with nested loops (skipping repeats), then close in with two pointers.",
        solution="""
            def four_sum(nums: list[int], target: int) -> list[list[int]]:
                nums = sorted(nums)
                n = len(nums)
                result = []
                for a in range(n - 3):
                    if a > 0 and nums[a] == nums[a - 1]:
                        continue
                    for b in range(a + 1, n - 2):
                        if b > a + 1 and nums[b] == nums[b - 1]:
                            continue
                        lo, hi = b + 1, n - 1
                        while lo < hi:
                            total = nums[a] + nums[b] + nums[lo] + nums[hi]
                            if total < target:
                                lo += 1
                            elif total > target:
                                hi -= 1
                            else:
                                result.append([nums[a], nums[b], nums[lo], nums[hi]])
                                lo += 1
                                hi -= 1
                                while lo < hi and nums[lo] == nums[lo - 1]:
                                    lo += 1
                                while lo < hi and nums[hi] == nums[hi + 1]:
                                    hi -= 1
                return result
        """,
        trace=1,
        comparator="sorted_list",
        cases=[
            ("[1, 0, -1, 0, -2, 2], 0", "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]", False),
            ("[2, 2, 2, 2, 2], 8", "[[2, 2, 2, 2]]", False),
            ("[1, 2, 3], 6", "[]", True),
            ("[0, 0, 0, 0], 0", "[[0, 0, 0, 0]]", True),
            ("[-3, -1, 0, 2, 4, 5], 2", "[[-3, -1, 2, 4]]", True),
            ("[], 0", "[]", True),
        ],
        hints=(
            "Sorting lets you reason about sums being too small or too large.",
            "Fix the first two values; the remaining pair is a sorted two-sum problem solved by two pointers.",
            "To avoid duplicate quadruplets, skip a value equal to the previous one at every level, and also after recording a match.",
        ),
        approaches=[
            ("Brute force", "Try all four-index combinations and deduplicate with a set.", "O(n^4)", "O(k)", False),
            ("Sort + two pointers", "Two nested loops plus a two-pointer sweep.", "O(n^3)", "O(1) beyond the output", True),
        ],
        notes=[
            (15, "total < target means the sum is too small, so only moving lo right (to a larger value) can help.", False),
        ],
        predictions=[
            (19, "For the first example, what are <code>nums[lo]</code> and <code>nums[hi]</code> the first time this line is reached?", "1 and 2: the sorted list is [-2, -1, 0, 0, 1, 2] and a = -2, b = -1."),
        ],
        patterns=["Arrays", "Two Pointers", "Sorting"],
        techniques=["Sorting", "Two Pointers", "Duplicate Skipping"],
    ),
    problem(
        slug="sort-an-array-of-0s-1s-and-2s",
        title="Sort an Array of 0s, 1s and 2s",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="sort_colors",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "<code>nums</code> contains only the values <code>0</code>, <code>1</code> and <code>2</code>. Return a new list with the values in ascending order.",
            "Do it in a single pass with three pointers (the Dutch national flag method); do not use any sort function.",
        ),
        examples=[
            ("nums = [2, 0, 2, 1, 1, 0]", "[0, 0, 1, 1, 2, 2]", "all 0s first, then 1s, then 2s"),
        ],
        constraints=["0 <= len(nums) <= 10^5", "nums[i] is 0, 1 or 2"],
        todo="Keep low, mid and high pointers: 0s are swapped to low, 2s are swapped to high, 1s are left in the middle.",
        solution="""
            def sort_colors(nums: list[int]) -> list[int]:
                arr = list(nums)
                low = mid = 0
                high = len(arr) - 1
                while mid <= high:
                    if arr[mid] == 0:
                        arr[low], arr[mid] = arr[mid], arr[low]
                        low += 1
                        mid += 1
                    elif arr[mid] == 1:
                        mid += 1
                    else:
                        arr[mid], arr[high] = arr[high], arr[mid]
                        high -= 1
                return arr
        """,
        trace=1,
        cases=[
            ("[2, 0, 2, 1, 1, 0]", "[0, 0, 1, 1, 2, 2]", False),
            ("[2, 0, 1]", "[0, 1, 2]", False),
            ("[]", "[]", True),
            ("[0]", "[0]", True),
            ("[1, 1, 1]", "[1, 1, 1]", True),
            ("[2, 2, 0, 0]", "[0, 0, 2, 2]", True),
        ],
        hints=(
            "Counting 0s, 1s and 2s and rewriting the list works but needs two passes. Can you place values as you meet them?",
            "Maintain three regions: 0s on the left, 1s in the middle, 2s on the right, with an unknown region between mid and high.",
            "After swapping a 2 to the right, do not advance mid: the value that arrived there has not been looked at yet.",
        ),
        approaches=[
            ("Counting sort", "Count each value, then rewrite the list.", "O(n)", "O(1)", False),
            ("Dutch national flag", "One pass with low, mid and high pointers.", "O(n)", "O(1) beyond the copy", True),
        ],
        notes=[
            (14, "mid is not advanced here: the element swapped in from high is still unclassified.", False),
        ],
        predictions=[
            (13, "For [2, 0, 2, 1, 1, 0], what is <code>arr[high]</code> the first time this line is reached?", "0: the last element will be swapped to the front."),
        ],
        patterns=["Arrays", "Two Pointers", "Sorting"],
        techniques=["Three Pointers", "Swap", "Partitioning"],
    ),
    problem(
        slug="next-permutation",
        title="Next Permutation",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="next_permutation",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return the permutation of <code>nums</code> that comes right after it in dictionary order. If <code>nums</code> is already the largest arrangement, return the smallest one (ascending order).",
            "Do not modify the input list. Values may repeat.",
        ),
        examples=[
            ("nums = [1, 2, 3]", "[1, 3, 2]", "the next arrangement in dictionary order"),
            ("nums = [3, 2, 1]", "[1, 2, 3]", "the largest wraps to the smallest"),
        ],
        constraints=["1 <= len(nums) <= 100", "0 <= nums[i] <= 100"],
        todo="Find the rightmost i with arr[i] < arr[i + 1], swap it with the smallest larger value on its right, then reverse the tail.",
        solution="""
            def next_permutation(nums: list[int]) -> list[int]:
                arr = list(nums)
                n = len(arr)
                i = n - 2
                while i >= 0 and arr[i] >= arr[i + 1]:
                    i -= 1
                if i >= 0:
                    j = n - 1
                    while arr[j] <= arr[i]:
                        j -= 1
                    arr[i], arr[j] = arr[j], arr[i]
                arr[i + 1:] = reversed(arr[i + 1:])
                return arr
        """,
        trace=1,
        cases=[
            ("[2, 1, 5, 4, 3, 0, 0]", "[2, 3, 0, 0, 1, 4, 5]", False),
            ("[3, 2, 1]", "[1, 2, 3]", False),
            ("[1, 2, 3]", "[1, 3, 2]", True),
            ("[1, 1, 5]", "[1, 5, 1]", True),
            ("[1]", "[1]", True),
            ("[1, 3, 2]", "[2, 1, 3]", True),
            ("[5, 4, 7, 5, 3, 2]", "[5, 5, 2, 3, 4, 7]", True),
        ],
        hints=(
            "The longest non-increasing suffix cannot be made larger by rearranging only itself.",
            "Find the pivot just left of that suffix, swap it with the smallest suffix value that is larger than it.",
            "The suffix is still non-increasing after the swap; reversing it gives its smallest arrangement. If there is no pivot, the reverse alone wraps to ascending.",
        ),
        approaches=[
            ("Generate all permutations", "Sort every permutation and find the next one.", "O(n! * n)", "O(n!)", False),
            ("Pivot, swap, reverse", "Standard next-permutation algorithm.", "O(n)", "O(1) beyond the copy", True),
        ],
        notes=[
            (12, "When no pivot exists (i = -1) this line reverses the whole list, which is the wrap-around case.", False),
        ],
        predictions=[
            (8, "For [2, 1, 5, 4, 3, 0, 0], what is <code>i</code> when this line is reached?", "1: the pivot is the value 1."),
        ],
        patterns=["Arrays", "Two Pointers"],
        techniques=["Pivot Search", "Swap", "Reversal"],
    ),
    problem(
        slug="majority-element-ii",
        title="Majority Element II",
        topic="arrays-and-hashing",
        difficulty="hard",
        fn="majority_element_ii",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return all values that appear <strong>more than</strong> <code>len(nums) / 3</code> times in <code>nums</code>, sorted in ascending order. There are never more than two such values.",
            "Aim for O(n) time and O(1) extra space with the extended Boyer-Moore voting idea, rather than counting every value in a dictionary.",
        ),
        examples=[
            ("nums = [3, 2, 3]", "[3]", "3 appears twice, more than 3 / 3 = 1"),
            ("nums = [1, 1, 1, 3, 3, 2, 2, 2]", "[1, 2]", "1 and 2 appear 3 times each, more than 8 / 3"),
        ],
        constraints=["0 <= len(nums) <= 5 * 10^4", "-10^9 <= nums[i] <= 10^9"],
        todo="Keep two candidates with counters, then verify each candidate by counting it.",
        solution="""
            def majority_element_ii(nums: list[int]) -> list[int]:
                cand1 = cand2 = None
                cnt1 = cnt2 = 0
                for x in nums:
                    if x == cand1:
                        cnt1 += 1
                    elif x == cand2:
                        cnt2 += 1
                    elif cnt1 == 0:
                        cand1, cnt1 = x, 1
                    elif cnt2 == 0:
                        cand2, cnt2 = x, 1
                    else:
                        cnt1 -= 1
                        cnt2 -= 1
                threshold = len(nums) // 3
                result = []
                for cand in (cand1, cand2):
                    if cand is not None and nums.count(cand) > threshold:
                        result.append(cand)
                return sorted(result)
        """,
        trace=2,
        cases=[
            ("[3, 2, 3]", "[3]", False),
            ("[1, 1, 1, 3, 3, 2, 2, 2]", "[1, 2]", False),
            ("[1]", "[1]", True),
            ("[1, 2]", "[1, 2]", True),
            ("[1, 2, 3, 4, 5, 6]", "[]", True),
            ("[2, 2, 9, 9, 3, 2, 9, 3]", "[2, 9]", True),
            ("[]", "[]", True),
        ],
        hints=(
            "How many values can exceed a third of the list? Think about what that says about how many candidates you need.",
            "Track two candidates. A value that matches neither candidate cancels one vote from each.",
            "The candidates are only possible answers: count each one at the end to confirm it really exceeds the threshold.",
        ),
        approaches=[
            ("Hash map count", "Count every value with a dictionary.", "O(n)", "O(n)", False),
            ("Extended Boyer-Moore", "Two candidates, then verify.", "O(n)", "O(1)", True),
        ],
        notes=[
            (14, "Decrementing both counters cancels three different values at once, which is why anything above n/3 survives.", False),
        ],
        predictions=[
            (16, "For [1, 1, 1, 3, 3, 2, 2, 2], what are <code>cand1</code> and <code>cand2</code> when this line is reached?", "cand1 = 1 and cand2 = 2."),
        ],
        patterns=["Arrays", "Voting"],
        techniques=["Boyer-Moore Voting", "Two Pass Verification"],
    ),
    problem(
        slug="find-the-repeating-and-missing-number",
        title="Find the Repeating and Missing Number",
        topic="arrays-and-hashing",
        difficulty="medium",
        fn="find_repeating_and_missing",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "<code>nums</code> has <code>n</code> values taken from <code>1..n</code>. Exactly one value in that range appears twice and exactly one is missing.",
            "Return <code>[repeating, missing]</code>. Aim for O(n) time and O(1) extra space using sums rather than a set.",
        ),
        examples=[
            ("nums = [3, 1, 2, 5, 3]", "[3, 4]", "3 appears twice and 4 never appears"),
        ],
        constraints=["2 <= len(nums) <= 10^5", "1 <= nums[i] <= len(nums)", "exactly one repeated and one missing value"],
        todo="Compare the sum and the sum of squares of nums with those of 1..n to get repeating - missing and repeating + missing.",
        solution="""
            def find_repeating_and_missing(nums: list[int]) -> list[int]:
                diff = 0
                sq_diff = 0
                for i, x in enumerate(nums, start=1):
                    diff += x - i
                    sq_diff += x * x - i * i
                total = sq_diff // diff
                repeating = (total + diff) // 2
                missing = total - repeating
                return [repeating, missing]
        """,
        trace=1,
        cases=[
            ("[3, 1, 2, 5, 3]", "[3, 4]", False),
            ("[4, 3, 6, 2, 1, 1]", "[1, 5]", False),
            ("[1, 1]", "[1, 2]", True),
            ("[2, 2]", "[2, 1]", True),
            ("[1, 2, 2, 4]", "[2, 3]", True),
            ("[7, 5, 3, 2, 1, 5, 4]", "[5, 6]", True),
        ],
        hints=(
            "Compare sum(nums) with 1 + 2 + ... + n. What does the difference equal in terms of the repeated and missing values?",
            "The difference of squares gives (repeating - missing) * (repeating + missing). Divide to get the sum.",
            "With the difference and the sum of the two numbers, you can solve for each one.",
        ),
        approaches=[
            ("Hash set / counts", "Count occurrences, then read off the one with count 2 and the one with count 0.", "O(n)", "O(n)", False),
            ("Sum and sum of squares", "Two equations in two unknowns.", "O(n)", "O(1)", True),
        ],
        notes=[
            (7, "sq_diff equals diff * (repeating + missing), so dividing by diff isolates the sum of the two unknowns.", False),
        ],
        predictions=[
            (7, "For [3, 1, 2, 5, 3], what are <code>diff</code> and <code>sq_diff</code> when this line is reached?", "diff = -1 and sq_diff = -7: 3 - 4 and 9 - 16."),
        ],
        patterns=["Arrays", "Math"],
        techniques=["Algebra", "Accumulator", "Enumerate"],
    ),
]
