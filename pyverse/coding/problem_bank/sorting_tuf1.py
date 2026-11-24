# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="selection-sort",
        title="Selection Sort",
        topic="sorting",
        difficulty="easy",
        fn="selection_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order, using <strong>selection sort</strong>: on each pass, find the smallest value in the unsorted part and swap it into the next free slot at the front.",
            "Do not call <code>sorted()</code> or <code>list.sort()</code>. The input list may be empty.",
        ),
        examples=[
            ("nums = [5, 2, 9, 1, 3]", "[1, 2, 3, 5, 9]", "each pass fixes one more value at the front"),
            ("nums = [3, 3, 1, 3]", "[1, 3, 3, 3]", "duplicates are kept"),
        ],
        constraints=["0 <= len(nums) <= 1000", "-10^9 <= nums[i] <= 10^9"],
        todo="For each position i, find the index of the smallest value in nums[i:] and swap it into place.",
        solution="""
            def selection_sort(nums: list[int]) -> list[int]:
                arr = list(nums)
                n = len(arr)
                for i in range(n - 1):
                    smallest = i
                    for j in range(i + 1, n):
                        if arr[j] < arr[smallest]:
                            smallest = j
                    arr[i], arr[smallest] = arr[smallest], arr[i]
                return arr
        """,
        trace=1,
        cases=[
            ("[5, 2, 9, 1, 3]", "[1, 2, 3, 5, 9]", False),
            ("[4, 3, 2, 1]", "[1, 2, 3, 4]", False),
            ("[]", "[]", True),
            ("[7]", "[7]", True),
            ("[3, 3, 1, 3]", "[1, 3, 3, 3]", True),
            ("[1, 2, 3]", "[1, 2, 3]", True),
            ("[-2, 5, -9, 0]", "[-9, -2, 0, 5]", True),
        ],
        hints=(
            "After the first pass, which value must sit at index 0?",
            "Track the index of the smallest value seen so far in the unsorted part, then swap once at the end of the pass.",
            "The outer loop only needs <code>n - 1</code> passes: when one value is left, it is already in place.",
        ),
        approaches=[
            ("Selection sort", "Repeatedly pick the minimum of the unsorted part and swap it to the front.", "O(n^2)", "O(1) extra", False),
            ("Built-in sort", "<code>sorted(nums)</code> uses Timsort.", "O(n log n)", "O(n)", True),
        ],
        notes=[
            (9, "One swap per pass: selection sort does at most n - 1 swaps, fewer than bubble or insertion sort.", False),
        ],
        predictions=[
            (9, "For [5, 2, 9, 1, 3], what is <code>smallest</code> the first time this line is reached?", "3, the index where the value 1 sits."),
        ],
        patterns=["Sorting", "Arrays"],
        techniques=["Nested Loops", "Swap", "Tuple Unpacking"],
    ),
    problem(
        slug="bubble-sort",
        title="Bubble Sort",
        topic="sorting",
        difficulty="easy",
        fn="bubble_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order using <strong>bubble sort</strong>: walk through the list swapping neighbours that are out of order, so the largest value of the unsorted part moves to the end on every pass.",
            "Stop early when a full pass makes no swap. Do not use <code>sorted()</code> or <code>list.sort()</code>.",
        ),
        examples=[
            ("nums = [5, 1, 4, 2, 8]", "[1, 2, 4, 5, 8]", "8 is already last; 5, 4 and 2 bubble right"),
            ("nums = [1, 2, 3]", "[1, 2, 3]", "no swaps in the first pass, so it stops at once"),
        ],
        constraints=["0 <= len(nums) <= 1000", "-10^9 <= nums[i] <= 10^9"],
        todo="Repeat passes over the unsorted prefix, swapping neighbours that are out of order; break if a pass swaps nothing.",
        solution="""
            def bubble_sort(nums: list[int]) -> list[int]:
                arr = list(nums)
                n = len(arr)
                for end in range(n - 1, 0, -1):
                    swapped = False
                    for j in range(end):
                        if arr[j] > arr[j + 1]:
                            arr[j], arr[j + 1] = arr[j + 1], arr[j]
                            swapped = True
                    if not swapped:
                        break
                return arr
        """,
        trace=1,
        cases=[
            ("[5, 1, 4, 2, 8]", "[1, 2, 4, 5, 8]", False),
            ("[3, 2, 1]", "[1, 2, 3]", False),
            ("[]", "[]", True),
            ("[1, 2, 3, 4, 5]", "[1, 2, 3, 4, 5]", True),
            ("[2, 2, 1]", "[1, 2, 2]", True),
            ("[9, -1]", "[-1, 9]", True),
        ],
        hints=(
            "After one full pass left to right, where is the largest value?",
            "Each pass can stop one position earlier than the last, because the tail is already sorted.",
            "Keep a flag that you reset at the start of each pass and set when you swap. If it is still unset at the end, break.",
        ),
        approaches=[
            ("Bubble sort without early exit", "Always run n - 1 passes.", "O(n^2)", "O(1) extra", False),
            ("Bubble sort with early exit", "Break when a pass has no swaps; sorted input costs one pass.", "O(n^2) worst, O(n) best", "O(1) extra", True),
        ],
        notes=[
            (10, "If no swap happened, every neighbour pair was in order, so the list is sorted and more passes are wasted.", False),
        ],
        predictions=[
            (8, "For [5, 1, 4, 2, 8], what is <code>arr[j]</code> the first time this line is reached?", "5: the pair (5, 1) is the first one out of order."),
        ],
        patterns=["Sorting", "Arrays"],
        techniques=["Nested Loops", "Swap", "Early Exit"],
    ),
    problem(
        slug="insertion-sort",
        title="Insertion Sort",
        topic="sorting",
        difficulty="easy",
        fn="insertion_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order using <strong>insertion sort</strong>: keep a sorted prefix, and for each next value slide it left past every larger value until it fits.",
            "Do not use <code>sorted()</code> or <code>list.sort()</code>.",
        ),
        examples=[
            ("nums = [7, 3, 5, 1]", "[1, 3, 5, 7]", "3 slides past 7, 5 slides past 7, 1 slides to the front"),
        ],
        constraints=["0 <= len(nums) <= 1000", "-10^9 <= nums[i] <= 10^9"],
        todo="For each i from 1, hold arr[i] as key, shift larger values on its left one step right, then drop key into the gap.",
        solution="""
            def insertion_sort(nums: list[int]) -> list[int]:
                arr = list(nums)
                for i in range(1, len(arr)):
                    key = arr[i]
                    j = i - 1
                    while j >= 0 and arr[j] > key:
                        arr[j + 1] = arr[j]
                        j -= 1
                    arr[j + 1] = key
                return arr
        """,
        trace=1,
        cases=[
            ("[7, 3, 5, 1]", "[1, 3, 5, 7]", False),
            ("[9, 8, 7, 6, 5]", "[5, 6, 7, 8, 9]", False),
            ("[]", "[]", True),
            ("[4]", "[4]", True),
            ("[1, 2, 3, 4]", "[1, 2, 3, 4]", True),
            ("[2, 1, 2, 1]", "[1, 1, 2, 2]", True),
        ],
        hints=(
            "Think of sorting a hand of cards: the cards you have already placed are in order.",
            "Save <code>arr[i]</code> in a variable, then move larger values on its left one slot to the right to open a gap.",
            "Loop while <code>j >= 0 and arr[j] > key</code>; when the loop stops, <code>arr[j + 1]</code> is the gap.",
        ),
        approaches=[
            ("Insertion sort", "Grow a sorted prefix by inserting one value at a time.", "O(n^2) worst, O(n) best", "O(1) extra", True),
        ],
        notes=[
            (9, "After the while loop, j + 1 is the first slot not holding a larger value, which is exactly where key belongs.", False),
        ],
        predictions=[
            (9, "For [7, 3, 5, 1], what is <code>j</code> the first time this line is reached?", "-1: 3 slid past 7, so the gap is slot 0."),
        ],
        patterns=["Sorting", "Arrays"],
        techniques=["Nested Loops", "Shifting"],
    ),
    problem(
        slug="merge-sort",
        title="Merge Sort",
        topic="sorting",
        difficulty="medium",
        fn="merge_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order using <strong>merge sort</strong>: split the list in half, sort each half recursively, then merge the two sorted halves into one.",
            "Equal values must keep their original relative order (the sort is stable). Do not use <code>sorted()</code> or <code>list.sort()</code>.",
        ),
        examples=[
            ("nums = [4, 1, 3, 2]", "[1, 2, 3, 4]", "[4, 1] and [3, 2] sort to [1, 4] and [2, 3], which merge into [1, 2, 3, 4]"),
        ],
        constraints=["0 <= len(nums) <= 10^4", "-10^9 <= nums[i] <= 10^9"],
        todo="Base case: length 0 or 1. Otherwise sort both halves recursively and merge with two pointers.",
        solution="""
            def merge_sort(nums: list[int]) -> list[int]:
                if len(nums) <= 1:
                    return list(nums)
                mid = len(nums) // 2
                left = merge_sort(nums[:mid])
                right = merge_sort(nums[mid:])
                merged = []
                i = j = 0
                while i < len(left) and j < len(right):
                    if left[i] <= right[j]:
                        merged.append(left[i])
                        i += 1
                    else:
                        merged.append(right[j])
                        j += 1
                merged.extend(left[i:])
                merged.extend(right[j:])
                return merged
        """,
        trace=1,
        cases=[
            ("[4, 1, 3, 2]", "[1, 2, 3, 4]", False),
            ("[5, 2, 9, 1, 5, 6]", "[1, 2, 5, 5, 6, 9]", False),
            ("[]", "[]", True),
            ("[1]", "[1]", True),
            ("[3, 2, 1]", "[1, 2, 3]", True),
            ("[2, 2, 2]", "[2, 2, 2]", True),
            ("[-1, 4, -7, 0, 4]", "[-7, -1, 0, 4, 4]", True),
        ],
        hints=(
            "What is the smallest list that is already sorted?",
            "Merging two sorted lists only needs one pointer per list: always take the smaller front value.",
            "When one half runs out, the rest of the other half can be appended as it is.",
        ),
        approaches=[
            ("Top-down merge sort", "Split in half, recurse, merge.", "O(n log n)", "O(n)", True),
            ("Insertion sort", "Simple but quadratic.", "O(n^2)", "O(1)", False),
        ],
        notes=[
            (10, "Taking from the left on ties (<=) is what makes the sort stable.", False),
        ],
        predictions=[
            (7, "For [4, 1, 3, 2], what are <code>left</code> and <code>right</code> the first time this line is reached?", "left = [4], right = [1]: the first merge happens inside the call for [4, 1]."),
        ],
        patterns=["Sorting", "Divide And Conquer", "Recursion"],
        techniques=["Two Pointers", "Slicing", "Recursion"],
    ),
    problem(
        slug="quick-sort",
        title="Quick Sort",
        topic="sorting",
        difficulty="medium",
        fn="quick_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order using <strong>quick sort</strong>: pick a pivot, split the values into those smaller than, equal to and larger than the pivot, sort the smaller and larger groups recursively, and join the three parts.",
            "Use the middle element (<code>nums[len(nums) // 2]</code>) as the pivot. Do not use <code>sorted()</code> or <code>list.sort()</code>.",
        ),
        examples=[
            ("nums = [6, 2, 9, 2, 5]", "[2, 2, 5, 6, 9]", "pivot 9 leaves everything else on the smaller side"),
        ],
        constraints=["0 <= len(nums) <= 10^4", "-10^9 <= nums[i] <= 10^9"],
        todo="Base case: length 0 or 1. Otherwise partition around the middle value and recurse on the smaller and larger parts.",
        solution="""
            def quick_sort(nums: list[int]) -> list[int]:
                if len(nums) <= 1:
                    return list(nums)
                pivot = nums[len(nums) // 2]
                smaller = [x for x in nums if x < pivot]
                equal = [x for x in nums if x == pivot]
                larger = [x for x in nums if x > pivot]
                return quick_sort(smaller) + equal + quick_sort(larger)
        """,
        trace=1,
        cases=[
            ("[6, 2, 9, 2, 5]", "[2, 2, 5, 6, 9]", False),
            ("[3, 8, 1, 7, 4, 2]", "[1, 2, 3, 4, 7, 8]", False),
            ("[]", "[]", True),
            ("[5]", "[5]", True),
            ("[4, 4, 4, 4]", "[4, 4, 4, 4]", True),
            ("[1, 2, 3, 4, 5]", "[1, 2, 3, 4, 5]", True),
            ("[0, -3, 8, -3, 1]", "[-3, -3, 0, 1, 8]", True),
        ],
        hints=(
            "After you pick a pivot, which values must end up to its left in the answer, and which to its right?",
            "Values equal to the pivot are already in their final place relative to the rest, so keep them out of the recursive calls.",
            "The result is the sorted smaller part, then the equal part, then the sorted larger part.",
        ),
        approaches=[
            ("Quick sort with three-way split", "Partition into smaller / equal / larger lists and recurse.", "O(n log n) average, O(n^2) worst", "O(n)", True),
            ("Selection sort", "Simple but always quadratic.", "O(n^2)", "O(1)", False),
        ],
        notes=[
            (8, "Because equal values are separated out, many duplicates never cause deep recursion.", False),
        ],
        predictions=[
            (8, "For [6, 2, 9, 2, 5], what is <code>smaller</code> the first time this line is reached?", "[6, 2, 2, 5]: the pivot is 9."),
        ],
        patterns=["Sorting", "Divide And Conquer", "Recursion"],
        techniques=["List Comprehension", "Recursion"],
    ),
    problem(
        slug="recursive-bubble-sort",
        title="Recursive Bubble Sort",
        topic="sorting",
        difficulty="medium",
        fn="recursive_bubble_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order using bubble sort <strong>without an outer loop</strong>: do one bubbling pass over the first <code>size</code> elements, then call yourself for the first <code>size - 1</code> elements.",
            "Do not use <code>sorted()</code> or <code>list.sort()</code>.",
        ),
        examples=[
            ("nums = [4, 3, 2, 5, 1]", "[1, 2, 3, 4, 5]", "after the first pass 5 is last: [3, 2, 4, 1, 5]"),
        ],
        constraints=["0 <= len(nums) <= 1000", "-10^9 <= nums[i] <= 10^9"],
        todo="Copy the list, then write a helper sort_prefix(size): do one pass over arr[:size], then recurse with size - 1.",
        solution="""
            def recursive_bubble_sort(nums: list[int]) -> list[int]:
                arr = list(nums)
                def sort_prefix(size):
                    if size <= 1:
                        return
                    for j in range(size - 1):
                        if arr[j] > arr[j + 1]:
                            arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    sort_prefix(size - 1)
                sort_prefix(len(arr))
                return arr
        """,
        trace=1,
        cases=[
            ("[4, 3, 2, 5, 1]", "[1, 2, 3, 4, 5]", False),
            ("[3, 1, 2]", "[1, 2, 3]", False),
            ("[]", "[]", True),
            ("[8]", "[8]", True),
            ("[1, 2, 3, 4]", "[1, 2, 3, 4]", True),
            ("[2, 2, 1, 1]", "[1, 1, 2, 2]", True),
        ],
        hints=(
            "What does one left-to-right bubbling pass guarantee about the last position it touched?",
            "The recursive call handles a prefix that is one element shorter.",
            "Stop recursing once the prefix has 0 or 1 elements.",
        ),
        approaches=[
            ("Recursive bubble sort", "One pass per call, recursion replaces the outer loop.", "O(n^2)", "O(n) stack", False),
            ("Iterative bubble sort", "Same passes with a for loop.", "O(n^2)", "O(1)", True),
        ],
        notes=[
            (9, "The recursion depth equals the number of passes: n - 1 calls deep for n values.", False),
        ],
        predictions=[
            (9, "For [4, 3, 2, 5, 1], what is <code>arr</code> the first time this line is reached?", "[3, 2, 4, 1, 5]: the first pass moved 5 to the end."),
        ],
        patterns=["Sorting", "Recursion"],
        techniques=["Recursion", "Swap", "Closure"],
    ),
    problem(
        slug="recursive-insertion-sort",
        title="Recursive Insertion Sort",
        topic="sorting",
        difficulty="medium",
        fn="recursive_insertion_sort",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Return a new list with the values of <code>nums</code> in ascending order using insertion sort <strong>written recursively</strong>: sort everything except the last element, then insert the last element into its place in the sorted result.",
            "Do not use <code>sorted()</code> or <code>list.sort()</code>.",
        ),
        examples=[
            ("nums = [4, 2, 5, 1]", "[1, 2, 4, 5]", "sort [4, 2, 5] to [2, 4, 5], then insert 1 at the front"),
        ],
        constraints=["0 <= len(nums) <= 1000", "-10^9 <= nums[i] <= 10^9"],
        todo="Base case: length 0 or 1. Otherwise recurse on nums[:-1], then slide nums[-1] left into position.",
        solution="""
            def recursive_insertion_sort(nums: list[int]) -> list[int]:
                if len(nums) <= 1:
                    return list(nums)
                arr = recursive_insertion_sort(nums[:-1])
                key = nums[-1]
                j = len(arr) - 1
                arr.append(key)
                while j >= 0 and arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                arr[j + 1] = key
                return arr
        """,
        trace=1,
        cases=[
            ("[4, 2, 5, 1]", "[1, 2, 4, 5]", False),
            ("[3, 1, 2]", "[1, 2, 3]", False),
            ("[]", "[]", True),
            ("[6]", "[6]", True),
            ("[1, 2, 3, 4]", "[1, 2, 3, 4]", True),
            ("[5, 5, 1, 5]", "[1, 5, 5, 5]", True),
        ],
        hints=(
            "If the first n - 1 values were already sorted, what would be left to do?",
            "The recursive call returns a sorted list; append the last value and shift larger values to the right.",
            "Use the same while loop as iterative insertion sort, with <code>j</code> starting at the old last index.",
        ),
        approaches=[
            ("Recursive insertion sort", "Sort the prefix by recursion, then insert the last value.", "O(n^2)", "O(n) stack", False),
            ("Iterative insertion sort", "Same insertions driven by a for loop.", "O(n^2)", "O(1)", True),
        ],
        notes=[
            (11, "After append, the list has one extra slot at the end; shifting larger values right fills the gap that key then takes.", False),
        ],
        predictions=[
            (5, "For [4, 2, 5, 1], what is <code>arr</code> the first time this line is reached?", "[4]: the base case returned the one-element prefix."),
        ],
        patterns=["Sorting", "Recursion"],
        techniques=["Recursion", "Slicing", "Shifting"],
    ),
]
