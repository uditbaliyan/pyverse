# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="add-two-numbers",
        title="Add Two Numbers",
        topic="linked-list-play",
        difficulty="medium",
        fn="add_two_numbers",
        signature="(a: list[int], b: list[int]) -> list[int]",
        description=html(
            "Two non-negative integers are stored as lists of digits with the <em>least</em> significant digit first (as if each were a linked list). Return their sum in the same format.",
        ),
        examples=[
            ("a = [2, 4, 3], b = [5, 6, 4]", "[7, 0, 8]", "342 + 465 = 807, stored as [7, 0, 8]"),
            ("a = [9, 9, 9, 9], b = [1]", "[0, 0, 0, 0, 1]", "9999 + 1 = 10000"),
        ],
        constraints=["1 <= len(a), len(b) <= 100", "0 <= digit <= 9", "No leading zeros except the number 0 itself"],
        todo="Walk both lists together, adding digits and a carry; keep going while a digit or a carry remains.",
        solution="""
            def add_two_numbers(a: list[int], b: list[int]) -> list[int]:
                result = []
                carry = 0
                i = 0
                while i < len(a) or i < len(b) or carry:
                    total = carry
                    if i < len(a):
                        total += a[i]
                    if i < len(b):
                        total += b[i]
                    result.append(total % 10)
                    carry = total // 10
                    i += 1
                return result
        """,
        trace=1,
        cases=[
            ("[2, 4, 3], [5, 6, 4]", "[7, 0, 8]", False),
            ("[9, 9, 9, 9], [1]", "[0, 0, 0, 0, 1]", False),
            ("[0], [0]", "[0]", True),
            ("[5], [5]", "[0, 1]", True),
            ("[1, 8], [0]", "[1, 8]", True),
        ],
        hints=(
            "Add the way you do on paper, starting from the units digit. What do you carry to the next column?",
            "The two lists can have different lengths; treat a missing digit as 0.",
            "After both lists end there may still be a carry left over, so the loop condition has three parts.",
        ),
        approaches=[
            ("Convert to integers", "Rebuild both numbers, add, and split the result back into digits.", "O(n)", "O(n)", False),
            ("Column addition with carry", "Add digit by digit in one pass.", "O(max(len(a), len(b)))", "O(1) extra", True),
        ],
        notes=[
            (12, "total // 10 is 0 or 1 here, since two digits plus a carry never exceed 19.", False),
        ],
        predictions=[
            (11, "For a = [2, 4, 3], b = [5, 6, 4], what is <code>total</code> the second time <code>result.append(total % 10)</code> is reached?", "total = 10, so 0 is stored and a carry of 1 moves on."),
        ],
        patterns=["Math", "Iteration"],
        techniques=["Accumulator", "Integer Division"],
    ),
    problem(
        slug="add-one-to-a-number",
        title="Add One to a Number",
        topic="linked-list-play",
        difficulty="easy",
        fn="add_one",
        signature="(digits: list[int]) -> list[int]",
        description=html(
            "A non-negative integer is stored as a list of digits with the <em>most</em> significant digit first (as if it were a linked list). Return the list for that integer plus one.",
        ),
        examples=[
            ("digits = [1, 9, 9, 9]", "[2, 0, 0, 0]", "1999 + 1 = 2000"),
            ("digits = [9, 9, 9]", "[1, 0, 0, 0]", "999 + 1 = 1000 needs a new leading digit"),
        ],
        constraints=["1 <= len(digits) <= 100", "0 <= digit <= 9", "No leading zeros except the number 0 itself"],
        todo="Turn trailing 9s into 0s from the right; add 1 to the first digit that is not 9, or prepend a 1.",
        solution="""
            def add_one(digits: list[int]) -> list[int]:
                result = digits[:]
                i = len(result) - 1
                while i >= 0 and result[i] == 9:
                    result[i] = 0
                    i -= 1
                if i < 0:
                    return [1] + result
                result[i] += 1
                return result
        """,
        trace=1,
        cases=[
            ("[1, 9, 9, 9]", "[2, 0, 0, 0]", False),
            ("[9, 9, 9]", "[1, 0, 0, 0]", False),
            ("[0]", "[1]", True),
            ("[4, 5, 6]", "[4, 5, 7]", True),
            ("[1, 2, 9]", "[1, 3, 0]", True),
        ],
        hints=(
            "Adding 1 only disturbs the last digits. Which digits change when you add 1 to 1999?",
            "Work from the right: a 9 becomes 0 and passes a carry left, anything else just grows by 1 and stops the carry.",
            "If every digit was a 9, the carry falls off the left end, so the number gets one more digit.",
        ),
        approaches=[
            ("Convert to an integer", "Join the digits, add 1 and split again.", "O(n)", "O(n)", False),
            ("Carry from the right", "Only the trailing 9s and one more digit are touched.", "O(n)", "O(1) extra", True),
        ],
        notes=[
            (7, "i < 0 means every digit was 9 and became 0, so a new leading 1 is needed.", False),
        ],
        predictions=[
            (9, "For digits = [1, 9, 9, 9], what are <code>i</code> and <code>result</code> the first time <code>result[i] += 1</code> is reached?", "i = 0 and result = [1, 0, 0, 0]; the digit at index 0 is about to become 2."),
        ],
        patterns=["Math", "Iteration"],
        techniques=["Carry", "Slicing"],
    ),
    problem(
        slug="segregate-odd-and-even-positions",
        title="Segregate Odd and Even Positions",
        topic="linked-list-play",
        difficulty="medium",
        fn="segregate_odd_even_positions",
        signature="(values: list[int]) -> list[int]",
        description=html(
            "Number the items of <code>values</code> starting from 1. Return a list with all the items at odd positions (1st, 3rd, 5th, ...) first, then all the items at even positions, each group keeping its original order. This is about positions, not about whether the values are odd.",
        ),
        examples=[
            ("values = [1, 2, 3, 4, 5]", "[1, 3, 5, 2, 4]", "Positions 1, 3, 5 then 2, 4"),
            ("values = [2, 1, 3, 5, 6, 4, 7]", "[2, 3, 6, 7, 1, 5, 4]", "2, 3, 6, 7 then 1, 5, 4"),
        ],
        constraints=["1 <= len(values) <= 1000", "-10^9 <= values[i] <= 10^9"],
        todo="Send items at even indices to one list and the rest to another, then join them.",
        solution="""
            def segregate_odd_even_positions(values: list[int]) -> list[int]:
                odd = []
                even = []
                for i, v in enumerate(values):
                    if i % 2 == 0:
                        odd.append(v)
                    else:
                        even.append(v)
                return odd + even
        """,
        trace=2,
        cases=[
            ("[1, 2, 3, 4, 5]", "[1, 3, 5, 2, 4]", False),
            ("[2, 1, 3, 5, 6, 4, 7]", "[2, 3, 6, 7, 1, 5, 4]", False),
            ("[8]", "[8]", True),
            ("[1, 2]", "[1, 2]", True),
            ("[5, 6, 7, 8]", "[5, 7, 6, 8]", True),
        ],
        hints=(
            "Careful with the numbering: the first item is position 1, which is index 0 in Python.",
            "Each item goes to exactly one of two groups depending on its index.",
            "Collect both groups in one pass, then place the first group before the second.",
        ),
        approaches=[
            ("Two passes", "One pass for odd positions, another for even positions.", "O(n)", "O(n)", False),
            ("One pass, two buckets", "Append each item to the correct bucket as you go.", "O(n)", "O(n)", True),
        ],
        notes=[
            (5, "Index 0 is position 1, so even indices belong to the 'odd positions' group.", False),
        ],
        predictions=[
            (8, "For values = [2, 1, 3, 5, 6, 4, 7], what is <code>even</code> the second time <code>even.append(v)</code> is reached?", "even = [1]; only the first even-position item has been stored so far."),
        ],
        patterns=["Iteration"],
        techniques=["enumerate", "Two Buckets"],
    ),
    problem(
        slug="sort-0s-1s-and-2s",
        title="Sort 0s, 1s and 2s",
        topic="linked-list-play",
        difficulty="medium",
        fn="sort_zeros_ones_twos",
        signature="(values: list[int]) -> list[int]",
        description=html(
            "<code>values</code> contains only the numbers 0, 1 and 2. Return it sorted in increasing order, in a single pass and without calling a sorting function.",
        ),
        examples=[
            ("values = [1, 0, 2, 1, 0]", "[0, 0, 1, 1, 2]", "Zeros first, then ones, then twos"),
            ("values = [2, 0, 2, 1, 1, 0]", "[0, 0, 1, 1, 2, 2]", "0, 0, 1, 1, 2, 2"),
        ],
        constraints=["1 <= len(values) <= 10^4", "values[i] is 0, 1 or 2"],
        todo="Keep three regions with pointers low, mid and high; swap each unknown item into the right region.",
        solution="""
            def sort_zeros_ones_twos(values: list[int]) -> list[int]:
                result = values[:]
                low = 0
                mid = 0
                high = len(result) - 1
                while mid <= high:
                    if result[mid] == 0:
                        result[low], result[mid] = result[mid], result[low]
                        low += 1
                        mid += 1
                    elif result[mid] == 1:
                        mid += 1
                    else:
                        result[mid], result[high] = result[high], result[mid]
                        high -= 1
                return result
        """,
        trace=1,
        cases=[
            ("[1, 0, 2, 1, 0]", "[0, 0, 1, 1, 2]", False),
            ("[2, 0, 2, 1, 1, 0]", "[0, 0, 1, 1, 2, 2]", False),
            ("[0]", "[0]", True),
            ("[2, 2, 1, 1, 0, 0]", "[0, 0, 1, 1, 2, 2]", True),
            ("[1, 1, 1]", "[1, 1, 1]", True),
        ],
        hints=(
            "Counting the 0s, 1s and 2s works with two passes. Can you do it in one by keeping the three groups in place?",
            "Maintain: everything before low is 0, everything from low to mid is 1, everything after high is 2.",
            "Look at result[mid]: a 0 swaps to the front, a 1 stays, a 2 swaps to the back. One of those cases must not advance mid.",
        ),
        approaches=[
            ("Count and rebuild", "Count each value, then write out the zeros, ones and twos.", "O(n)", "O(1)", False),
            ("Dutch national flag", "Three pointers partition the list in a single pass.", "O(n)", "O(1)", True),
        ],
        notes=[
            (14, "The item swapped in from high has not been looked at yet, so mid must stay where it is.", False),
        ],
        predictions=[
            (14, "For values = [1, 0, 2, 1, 0], what are <code>mid</code> and <code>high</code> the first time <code>result[mid], result[high] = result[high], result[mid]</code> is reached?", "mid = 2 and high = 4."),
        ],
        patterns=["Two Pointers"],
        techniques=["Three Pointers", "Tuple Unpacking"],
    ),
    problem(
        slug="remove-nth-from-the-end",
        title="Remove the Nth Item From the End",
        topic="linked-list-play",
        difficulty="medium",
        fn="remove_nth_from_end",
        signature="(values: list[int], n: int) -> list[int]",
        description=html(
            "Return <code>values</code> with its <code>n</code>-th item from the end removed (<code>n = 1</code> removes the last item). Do it with two indices that move together, rather than by computing the length first.",
        ),
        examples=[
            ("values = [1, 2, 3, 4, 5], n = 2", "[1, 2, 3, 5]", "The second item from the end is 4"),
            ("values = [10, 20, 30], n = 1", "[10, 20]", "Remove the last item"),
        ],
        constraints=["1 <= len(values) <= 1000", "1 <= n <= len(values)"],
        todo="Start a fast index n steps ahead of a slow index; move both until fast reaches the end.",
        solution="""
            def remove_nth_from_end(values: list[int], n: int) -> list[int]:
                fast = n
                slow = 0
                while fast < len(values):
                    fast += 1
                    slow += 1
                return values[:slow] + values[slow + 1:]
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 5], 2", "[1, 2, 3, 5]", False),
            ("[10, 20, 30], 1", "[10, 20]", False),
            ("[1, 2], 2", "[2]", True),
            ("[7, 8, 9], 3", "[8, 9]", True),
            ("[1], 1", "[]", True),
        ],
        hints=(
            "Counting from the end needs the length. Is there a way to find the target without knowing it?",
            "If one index is n steps ahead of another, what is the gap between them when the front one reaches the end?",
            "When the front index runs off the end, the back index is sitting on the item to remove.",
        ),
        approaches=[
            ("Two passes", "Compute the length, then remove index length - n.", "O(n)", "O(n)", False),
            ("Gap of n between two indices", "Move both together; the back one stops at the target.", "O(n)", "O(n)", True),
        ],
        notes=[
            (4, "fast starts n steps ahead, so when it passes the end, slow is exactly n items from the end.", False),
        ],
        predictions=[
            (6, "For values = [1, 2, 3, 4, 5], n = 2, what are <code>fast</code> and <code>slow</code> the third time <code>slow += 1</code> is reached?", "fast = 5 and slow = 2."),
        ],
        patterns=["Two Pointers"],
        techniques=["Fast And Slow Pointers", "Slicing"],
    ),
    problem(
        slug="reverse-in-groups-of-k",
        title="Reverse in Groups of K",
        topic="linked-list-play",
        difficulty="hard",
        fn="reverse_in_groups",
        signature="(values: list[int], k: int) -> list[int]",
        description=html(
            "Cut <code>values</code> into consecutive groups of <code>k</code> items and reverse each complete group. A final group with fewer than <code>k</code> items is left as it is.",
        ),
        examples=[
            ("values = [1, 2, 3, 4, 5], k = 2", "[2, 1, 4, 3, 5]", "[2, 1, 4, 3, 5]; the lone 5 stays"),
            ("values = [1, 2, 3, 4, 5, 6, 7, 8], k = 3", "[3, 2, 1, 6, 5, 4, 7, 8]", "Two groups reversed, 7 and 8 untouched"),
        ],
        constraints=["1 <= len(values) <= 1000", "1 <= k <= 1000"],
        todo="For each full group, swap items from both ends towards the middle.",
        solution="""
            def reverse_in_groups(values: list[int], k: int) -> list[int]:
                result = values[:]
                start = 0
                while start + k <= len(result):
                    left = start
                    right = start + k - 1
                    while left < right:
                        result[left], result[right] = result[right], result[left]
                        left += 1
                        right -= 1
                    start += k
                return result
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 5], 2", "[2, 1, 4, 3, 5]", False),
            ("[1, 2, 3, 4, 5, 6, 7, 8], 3", "[3, 2, 1, 6, 5, 4, 7, 8]", False),
            ("[1, 2, 3], 1", "[1, 2, 3]", True),
            ("[1, 2, 3], 3", "[3, 2, 1]", True),
            ("[1, 2], 5", "[1, 2]", True),
        ],
        hints=(
            "Reversing one block is a familiar two-ended swap. How do you decide where each block starts?",
            "Blocks start at 0, k, 2k, ... and only count if all k items exist.",
            "Inside a block, swap the outermost pair, then the next pair in, until the two ends meet.",
        ),
        approaches=[
            ("Slice and reverse", "Take each slice, reverse it with [::-1] and join.", "O(n)", "O(n)", False),
            ("In-place swaps per block", "Swap towards the middle inside each full block.", "O(n)", "O(1) extra", True),
        ],
        notes=[
            (4, "start + k <= len(result) is true only for complete groups, so a short tail is never touched.", False),
        ],
        predictions=[
            (8, "For values = [1, 2, 3, 4, 5], k = 2, what are <code>left</code>, <code>right</code> and <code>result</code> the second time <code>result[left], result[right] = result[right], result[left]</code> is reached?", "left = 2, right = 3 and result = [2, 1, 3, 4, 5]."),
        ],
        patterns=["Two Pointers"],
        techniques=["Tuple Unpacking", "Nested Loops"],
    ),
    problem(
        slug="merge-two-sorted-lists",
        title="Merge Two Sorted Lists",
        topic="linked-list-play",
        difficulty="easy",
        fn="merge_sorted_lists",
        signature="(a: list[int], b: list[int]) -> list[int]",
        description=html(
            "<code>a</code> and <code>b</code> are each sorted in non-decreasing order. Return one sorted list containing all their items, without sorting the combined list from scratch.",
        ),
        examples=[
            ("a = [1, 2, 4], b = [1, 3, 4]", "[1, 1, 2, 3, 4, 4]", "[1, 1, 2, 3, 4, 4]"),
            ("a = [5, 6], b = [1, 2, 3]", "[1, 2, 3, 5, 6]", "All of b comes first"),
        ],
        constraints=["0 <= len(a), len(b) <= 1000", "-10^4 <= a[i], b[i] <= 10^4"],
        todo="Compare the fronts of both lists, take the smaller, and move that list's index forward; append what is left at the end.",
        solution="""
            def merge_sorted_lists(a: list[int], b: list[int]) -> list[int]:
                result = []
                i = 0
                j = 0
                while i < len(a) and j < len(b):
                    if a[i] <= b[j]:
                        result.append(a[i])
                        i += 1
                    else:
                        result.append(b[j])
                        j += 1
                result.extend(a[i:])
                result.extend(b[j:])
                return result
        """,
        trace=1,
        cases=[
            ("[1, 2, 4], [1, 3, 4]", "[1, 1, 2, 3, 4, 4]", False),
            ("[5, 6], [1, 2, 3]", "[1, 2, 3, 5, 6]", False),
            ("[], []", "[]", True),
            ("[1], []", "[1]", True),
            ("[-3, -1], [-2, 0]", "[-3, -2, -1, 0]", True),
        ],
        hints=(
            "At each step, which item can safely go next in the merged list?",
            "Keep one index per list and always take the smaller front item.",
            "One list will run out first; whatever remains of the other is already sorted and can be appended.",
        ),
        approaches=[
            ("Concatenate and sort", "Join the lists and call sort.", "O((n + m) log(n + m))", "O(n + m)", False),
            ("Two-index merge", "Walk both lists once, taking the smaller front item.", "O(n + m)", "O(n + m)", True),
        ],
        notes=[
            (6, "Using <= takes from a on ties, which keeps the merge stable.", False),
        ],
        predictions=[
            (10, "For a = [1, 2, 4], b = [1, 3, 4], what are <code>i</code> and <code>j</code> the first time <code>result.append(b[j])</code> is reached?", "i = 1 and j = 0; 2 is larger than the front of b."),
        ],
        patterns=["Two Pointers"],
        techniques=["Two Pointers Merge"],
    ),
    problem(
        slug="middle-of-the-list",
        title="Middle of the List",
        topic="linked-list-play",
        difficulty="easy",
        fn="middle_of_list",
        signature="(values: list[int]) -> int",
        description=html(
            "Return the middle item of <code>values</code>. If there are two middle items, return the second one. Find it with a slow index that moves one step while a fast index moves two.",
        ),
        examples=[
            ("values = [1, 2, 3, 4, 5]", "3", "3 is in the centre"),
            ("values = [1, 2, 3, 4, 5, 6]", "4", "3 and 4 are both middles; return the second"),
        ],
        constraints=["1 <= len(values) <= 100"],
        todo="Advance slow by 1 and fast by 2 until fast cannot move two more steps; slow is the middle.",
        solution="""
            def middle_of_list(values: list[int]) -> int:
                slow = 0
                fast = 0
                while fast + 1 < len(values):
                    slow += 1
                    fast += 2
                return values[slow]
        """,
        trace=2,
        cases=[
            ("[1, 2, 3, 4, 5]", "3", False),
            ("[1, 2, 3, 4, 5, 6]", "4", False),
            ("[9]", "9", True),
            ("[1, 2]", "2", True),
            ("[4, 8, 15, 16, 23, 42, 7, 3]", "23", True),
        ],
        hints=(
            "Counting the length first takes two passes. Can you find the middle in a single pass?",
            "If one index moves twice as fast as another, where is the slower one when the faster one finishes?",
            "Stop when fast has no room for another full step; check both odd and even lengths by hand.",
        ),
        approaches=[
            ("Count then index", "Use len(values) // 2.", "O(1)", "O(1)", False),
            ("Slow and fast indices", "Slow reaches the middle as fast reaches the end (the linked-list technique).", "O(n)", "O(1)", True),
        ],
        notes=[
            (4, "fast + 1 < len means fast can still take its two-step jump or has an item after it.", False),
        ],
        predictions=[
            (6, "For values = [1, 2, 3, 4, 5, 6], what are <code>slow</code> and <code>fast</code> the second time <code>fast += 2</code> is reached?", "slow = 2 and fast = 2."),
        ],
        patterns=["Two Pointers"],
        techniques=["Fast And Slow Pointers"],
    ),
    problem(
        slug="linked-list-cycle",
        title="Detect a Cycle",
        topic="linked-list-play",
        difficulty="medium",
        fn="has_cycle",
        signature="(nxt: list[int]) -> bool",
        description=html(
            "A linked list is described by a list <code>nxt</code> where <code>nxt[i]</code> is the index of the node that follows node <code>i</code>, or <code>-1</code> if node <code>i</code> is the last node. The list starts at node 0.",
            "Return <code>True</code> if following the links from node 0 ever revisits a node (a loop), otherwise <code>False</code>.",
        ),
        examples=[
            ("nxt = [1, 2, 3, 4, 2]", "True", "Node 4 links back to node 2"),
            ("nxt = [1, 2, 3, -1]", "False", "The chain simply ends at node 3"),
        ],
        constraints=["1 <= len(nxt) <= 1000", "-1 <= nxt[i] < len(nxt)"],
        todo="Move a slow pointer one link and a fast pointer two links per step; if they ever meet there is a loop.",
        solution="""
            def has_cycle(nxt: list[int]) -> bool:
                slow = 0
                fast = 0
                while fast != -1 and nxt[fast] != -1:
                    slow = nxt[slow]
                    fast = nxt[nxt[fast]]
                    if slow == fast:
                        return True
                return False
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 2]", "True", False),
            ("[1, 2, 3, -1]", "False", False),
            ("[-1]", "False", True),
            ("[0]", "True", True),
            ("[1, 0]", "True", True),
            ("[1, 2, -1]", "False", True),
        ],
        hints=(
            "Remembering every visited node works but costs memory. Is there a way to notice a loop with only two variables?",
            "Two runners on a circular track, one faster, must eventually meet.",
            "Move slow by one link and fast by two. If fast reaches -1 the list ends and there is no loop.",
        ),
        approaches=[
            ("Visited set", "Remember each node; stop when one repeats.", "O(n)", "O(n)", False),
            ("Floyd's tortoise and hare", "A fast and a slow pointer meet inside any loop.", "O(n)", "O(1)", True),
        ],
        notes=[
            (4, "Both checks guard the double step: fast must not be at the end, and the node after it must exist.", False),
        ],
        predictions=[
            (8, "For nxt = [1, 2, 3, 4, 2], what are <code>slow</code> and <code>fast</code> the first time <code>return True</code> is reached?", "slow = 3 and fast = 3; the two pointers have met inside the loop."),
        ],
        patterns=["Two Pointers"],
        techniques=["Fast And Slow Pointers"],
    ),
    problem(
        slug="linked-list-cycle-start",
        title="Find Where the Cycle Starts",
        topic="linked-list-play",
        difficulty="medium",
        fn="cycle_start",
        signature="(nxt: list[int]) -> int",
        description=html(
            "A linked list is described by a list <code>nxt</code> where <code>nxt[i]</code> is the index of the node that follows node <code>i</code>, or <code>-1</code> if node <code>i</code> is the last node. The list starts at node 0.",
            "If following the links from node 0 leads into a loop, return the index of the first node of that loop (the first node reached twice). If there is no loop, return <code>-1</code>.",
        ),
        examples=[
            ("nxt = [1, 2, 3, 4, 2]", "2", "The loop 2 -> 3 -> 4 -> 2 starts at node 2"),
            ("nxt = [1, 2, 3, -1]", "-1", "No loop"),
        ],
        constraints=["1 <= len(nxt) <= 1000", "-1 <= nxt[i] < len(nxt)"],
        todo="Find the meeting point with a slow and a fast pointer, then walk one pointer from node 0 and one from the meeting point, one step each, until they meet.",
        solution="""
            def cycle_start(nxt: list[int]) -> int:
                slow = 0
                fast = 0
                while fast != -1 and nxt[fast] != -1:
                    slow = nxt[slow]
                    fast = nxt[nxt[fast]]
                    if slow == fast:
                        finger = 0
                        while finger != slow:
                            finger = nxt[finger]
                            slow = nxt[slow]
                        return finger
                return -1
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 2]", "2", False),
            ("[1, 2, 3, -1]", "-1", False),
            ("[0]", "0", True),
            ("[1, 0]", "0", True),
            ("[1, 2, 3, 1]", "1", True),
            ("[1, 2, 3, 4, 5, 6, 3]", "3", True),
        ],
        hints=(
            "First detect that a loop exists. Once the two pointers have met, what do you know about where they are?",
            "The distance from node 0 to the loop start equals the distance from the meeting point forward to the loop start, modulo the loop length.",
            "Start a second pointer at node 0 and move it together with the meeting-point pointer, one link at a time; where they meet is the start.",
        ),
        approaches=[
            ("Visited set", "Walk from node 0 and return the first node seen twice.", "O(n)", "O(n)", False),
            ("Floyd's second phase", "After the pointers meet, restart one from node 0; they meet at the loop start.", "O(n)", "O(1)", True),
        ],
        notes=[
            (10, "Moving both pointers one link at a time makes them meet exactly at the first node of the loop.", False),
        ],
        predictions=[
            (10, "For nxt = [1, 2, 3, 4, 2], what are <code>finger</code> and <code>slow</code> the first time <code>finger = nxt[finger]</code> is reached?", "finger = 0 and slow = 3; slow is where the first phase met."),
        ],
        patterns=["Two Pointers"],
        techniques=["Fast And Slow Pointers"],
    ),
    problem(
        slug="linked-list-cycle-length",
        title="Length of the Cycle",
        topic="linked-list-play",
        difficulty="medium",
        fn="loop_length",
        signature="(nxt: list[int]) -> int",
        description=html(
            "A linked list is described by a list <code>nxt</code> where <code>nxt[i]</code> is the index of the node that follows node <code>i</code>, or <code>-1</code> if node <code>i</code> is the last node. The list starts at node 0.",
            "If following the links from node 0 leads into a loop, return how many nodes the loop contains. If there is no loop, return <code>0</code>.",
        ),
        examples=[
            ("nxt = [1, 2, 3, 4, 2]", "3", "The loop is nodes 2, 3 and 4"),
            ("nxt = [1, 2, 3, -1]", "0", "No loop"),
        ],
        constraints=["1 <= len(nxt) <= 1000", "-1 <= nxt[i] < len(nxt)"],
        todo="Find a node inside the loop with a slow and a fast pointer, then count steps until you come back to it.",
        solution="""
            def loop_length(nxt: list[int]) -> int:
                slow = 0
                fast = 0
                while fast != -1 and nxt[fast] != -1:
                    slow = nxt[slow]
                    fast = nxt[nxt[fast]]
                    if slow == fast:
                        length = 1
                        node = nxt[slow]
                        while node != slow:
                            length += 1
                            node = nxt[node]
                        return length
                return 0
        """,
        trace=1,
        cases=[
            ("[1, 2, 3, 4, 2]", "3", False),
            ("[1, 2, 3, -1]", "0", False),
            ("[0]", "1", True),
            ("[1, 0]", "2", True),
            ("[1, 2, 3, 4, 5, 6, 3]", "4", True),
        ],
        hints=(
            "Counting the loop is easy if you start from a node that is certainly inside it. How do you get one?",
            "When the slow and fast pointers meet, that node is on the loop.",
            "From that node, follow the links and count steps until you return to it.",
        ),
        approaches=[
            ("Visited map of positions", "Record when each node was first seen; the loop length is the difference when one repeats.", "O(n)", "O(n)", False),
            ("Floyd then count", "Meet inside the loop, then walk once around it.", "O(n)", "O(1)", True),
        ],
        notes=[
            (10, "node starts one link past slow and length starts at 1, so the walk counts every node on the loop exactly once.", False),
        ],
        predictions=[
            (11, "For nxt = [1, 2, 3, 4, 2], what are <code>length</code> and <code>node</code> the second time <code>length += 1</code> is reached?", "length = 2 and node = 2."),
        ],
        patterns=["Two Pointers"],
        techniques=["Fast And Slow Pointers"],
    ),
]
