# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="single-number",
        title="Single Number",
        topic="bit-manipulation",
        difficulty="easy",
        fn="single_number",
        signature="(nums: list[int]) -> int",
        description=html(
            "Every value in <code>nums</code> appears exactly twice except one value that appears once. Return that value.",
            "Aim for linear time and constant extra space.",
        ),
        examples=[
            ("nums = [4, 1, 2, 1, 2]", "4", "1 and 2 come in pairs, 4 is alone"),
            ("nums = [2, 2, 1]", "1", "Only 1 has no partner"),
        ],
        constraints=["1 <= len(nums) <= 30000, and the length is odd", "-30000 <= nums[i] <= 30000"],
        todo="XOR all the numbers together; equal pairs cancel to 0.",
        solution="""
            def single_number(nums: list[int]) -> int:
                result = 0
                for x in nums:
                    result ^= x
                return result
        """,
        trace=1,
        cases=[
            ("[4, 1, 2, 1, 2]", "4", False),
            ("[2, 2, 1]", "1", False),
            ("[7]", "7", True),
            ("[-1, -1, -3]", "-3", True),
            ("[10, 20, 10, 30, 30]", "20", True),
        ],
        hints=(
            "A dictionary of counts works, but it needs extra space. What operation turns two equal numbers into something harmless?",
            "XOR of a number with itself is 0, and XOR with 0 changes nothing.",
            "XOR is also order independent, so the pairs cancel wherever they sit in the list.",
        ),
        approaches=[
            ("Count with a dictionary", "Tally each value and return the one with count 1.", "O(n)", "O(n)", False),
            ("XOR everything", "Equal pairs cancel, leaving the single value.", "O(n)", "O(1)", True),
        ],
        notes=[
            (4, "a ^ a = 0 and a ^ 0 = a, so after the loop only the unpaired value is left.", False),
        ],
        predictions=[
            (4, "For nums = [4, 1, 2, 1, 2], what are <code>x</code> and <code>result</code> the fourth time <code>result ^= x</code> is reached?", "x = 1 and result = 7."),
        ],
        patterns=["Bit Manipulation"],
        techniques=["Bitwise XOR", "Accumulator"],
    ),
    problem(
        slug="single-number-ii",
        title="Single Number II",
        topic="bit-manipulation",
        difficulty="medium",
        fn="single_number_ii",
        signature="(nums: list[int]) -> int",
        description=html(
            "Every value in <code>nums</code> appears exactly three times except one value that appears once. Return that value.",
            "Aim for linear time and constant extra space.",
        ),
        examples=[
            ("nums = [2, 2, 3, 2]", "3", "2 appears three times, 3 once"),
            ("nums = [0, 1, 0, 1, 0, 1, 99]", "99", "99 is the loner"),
        ],
        constraints=["1 <= len(nums) <= 30000", "-2^31 <= nums[i] <= 2^31 - 1"],
        todo="Track bits seen once and bits seen twice; a bit seen three times is cleared from both.",
        solution="""
            def single_number_ii(nums: list[int]) -> int:
                ones = 0
                twos = 0
                for x in nums:
                    ones = (ones ^ x) & ~twos
                    twos = (twos ^ x) & ~ones
                return ones
        """,
        trace=1,
        cases=[
            ("[2, 2, 3, 2]", "3", False),
            ("[0, 1, 0, 1, 0, 1, 99]", "99", False),
            ("[-2, -2, 1, 1, -3, 1, -3, -3, -4, -2]", "-4", True),
            ("[5]", "5", True),
            ("[-7, -1, -1, -1]", "-7", True),
        ],
        hints=(
            "XOR alone fails here because three equal numbers do not cancel. Look at a single bit position: what is the count of 1s there?",
            "For each bit position, the count of 1s across all numbers is a multiple of 3 plus the loner's bit.",
            "You can keep that count modulo 3 for all bit positions at once with two variables, one for 'seen once' and one for 'seen twice'.",
        ),
        approaches=[
            ("Count each bit position", "Sum bit i over all numbers; if the sum mod 3 is 1, the loner has that bit.", "O(32 * n)", "O(1)", False),
            ("Two-state bit counter", "ones and twos form a mod-3 counter for every bit in parallel.", "O(n)", "O(1)", True),
        ],
        notes=[
            (5, "A bit enters ones when seen once, leaves it when seen twice (it moves to twos), and the &amp; ~twos stops it re-entering at the third sighting.", False),
        ],
        predictions=[
            (5, "For nums = [2, 2, 3, 2], what are <code>x</code>, <code>ones</code> and <code>twos</code> the third time <code>ones = (ones ^ x) &amp; ~twos</code> is reached?", "x = 3, ones = 0 and twos = 2; the first two 2s moved their bits from ones to twos."),
        ],
        patterns=["Bit Manipulation"],
        techniques=["Bitwise XOR", "Bit Mask"],
    ),
    problem(
        slug="single-number-iii",
        title="Single Number III",
        topic="bit-manipulation",
        difficulty="medium",
        fn="single_number_iii",
        signature="(nums: list[int]) -> list[int]",
        description=html(
            "Exactly two values in <code>nums</code> appear once and every other value appears twice. Return the two single values in any order.",
            "Aim for linear time and constant extra space.",
        ),
        examples=[
            ("nums = [1, 2, 1, 3, 2, 5]", "[3, 5]", "3 and 5 have no partner"),
            ("nums = [-1, 0]", "[-1, 0]", "Both values are singles"),
        ],
        constraints=["2 <= len(nums) <= 30000", "-2^31 <= nums[i] <= 2^31 - 1", "The two singles are different values"],
        todo="XOR everything to get a ^ b, pick a bit where they differ, and split the numbers by that bit.",
        solution="""
            def single_number_iii(nums: list[int]) -> list[int]:
                xor_all = 0
                for x in nums:
                    xor_all ^= x
                low_bit = xor_all & -xor_all
                a = 0
                b = 0
                for x in nums:
                    if x & low_bit:
                        a ^= x
                    else:
                        b ^= x
                return [a, b]
        """,
        trace=1,
        comparator="sorted_list",
        cases=[
            ("[1, 2, 1, 3, 2, 5]", "[3, 5]", False),
            ("[-1, 0]", "[-1, 0]", False),
            ("[0, 1]", "[1, 0]", True),
            ("[4, 4, 6, 7, 6, 9]", "[7, 9]", True),
            ("[-3, 8, -3, 5, 8, -4]", "[5, -4]", True),
        ],
        hints=(
            "XOR of the whole list cancels every pair, leaving a combination of the two singles. What does a 1 bit in that result tell you?",
            "A 1 bit in the XOR means the two singles differ at that position, so that bit can split them apart.",
            "Split all numbers into two groups by that bit; each group holds one single plus complete pairs, which a plain XOR can solve.",
        ),
        approaches=[
            ("Count with a dictionary", "Tally values and return the two with count 1.", "O(n)", "O(n)", False),
            ("XOR and split by a differing bit", "Use the lowest set bit of a ^ b to separate the singles into two groups.", "O(n)", "O(1)", True),
        ],
        notes=[
            (5, "xor_all &amp; -xor_all isolates the lowest set bit, a position where the two single values differ.", False),
        ],
        predictions=[
            (5, "For nums = [1, 2, 1, 3, 2, 5], what is <code>xor_all</code> the first time <code>low_bit = xor_all &amp; -xor_all</code> is reached?", "xor_all = 6, which is 3 ^ 5."),
        ],
        patterns=["Bit Manipulation"],
        techniques=["Bitwise XOR", "Bit Mask"],
    ),
]
