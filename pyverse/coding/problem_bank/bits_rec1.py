# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="count-set-bits",
        title="Count Set Bits",
        topic="bit-manipulation",
        difficulty="easy",
        fn="count_set_bits",
        signature="(n: int) -> int",
        description=html(
            "Return the number of <code>1</code> bits in the binary representation of the non-negative integer <code>n</code>.",
        ),
        examples=[
            ("n = 13", "3", "13 is 1101 in binary, which has three 1s"),
            ("n = 255", "8", "255 is 11111111, eight 1s"),
        ],
        constraints=["0 <= n <= 2^31 - 1"],
        todo="Repeatedly clear the lowest set bit of n and count how many times you can do it.",
        solution="""
            def count_set_bits(n: int) -> int:
                count = 0
                while n > 0:
                    n &= n - 1
                    count += 1
                return count
        """,
        trace=1,
        cases=[
            ("13", "3", False),
            ("255", "8", False),
            ("0", "0", True),
            ("1", "1", True),
            ("1073741823", "30", True),
        ],
        hints=(
            "Write 13 in binary. What would you look at to count its 1s?",
            "Is there an operation that removes exactly one 1 bit per step, so the loop runs once per set bit?",
            "Compare n with n - 1 in binary: the lowest 1 and every bit below it change. What does n AND (n - 1) give?",
        ),
        approaches=[
            ("Test every bit", "Shift right and test the lowest bit until n becomes 0.", "O(log n)", "O(1)", False),
            ("Clear the lowest set bit", "n &amp; (n - 1) drops one 1 bit per step (Kernighan's trick).", "O(number of set bits)", "O(1)", True),
        ],
        notes=[
            (4, "n &amp; (n - 1) clears the lowest set bit, so the loop runs once per 1 bit rather than once per bit position.", False),
        ],
        predictions=[
            (5, "For n = 13, what are <code>n</code> and <code>count</code> the second time <code>count += 1</code> is reached?", "n = 8 and count = 1."),
        ],
        patterns=["Bit Manipulation"],
        techniques=["Bitwise AND", "Accumulator"],
    ),
    problem(
        slug="check-power-of-2",
        title="Check for a Power of Two",
        topic="bit-manipulation",
        difficulty="easy",
        fn="is_power_of_two",
        signature="(n: int) -> bool",
        description=html(
            "Return <code>True</code> if <code>n</code> equals <code>2^k</code> for some integer <code>k >= 0</code>, otherwise <code>False</code>.",
        ),
        examples=[
            ("n = 64", "True", "64 = 2^6"),
            ("n = 12", "False", "12 lies between 8 and 16"),
        ],
        constraints=["-2^31 <= n <= 2^31 - 1"],
        todo="Rule out n <= 0, then halve n while it is even; a power of two ends at exactly 1.",
        solution="""
            def is_power_of_two(n: int) -> bool:
                if n <= 0:
                    return False
                while n % 2 == 0:
                    n //= 2
                return n == 1
        """,
        trace=1,
        cases=[
            ("64", "True", False),
            ("12", "False", False),
            ("1", "True", True),
            ("0", "False", True),
            ("-8", "False", True),
            ("1073741824", "True", True),
        ],
        hints=(
            "What happens to a power of two if you keep halving it? What about a number that is not one?",
            "Negative numbers and 0 are never powers of two, so handle them first.",
            "Write 1, 2, 4, 8, 16 in binary. What do they have in common, and what does n - 1 look like next to n?",
        ),
        approaches=[
            ("Divide by two", "Halve while the number is even and check that you end at 1.", "O(log n)", "O(1)", False),
            ("Single set bit", "A power of two has exactly one 1 bit, so n &gt; 0 and n &amp; (n - 1) == 0.", "O(1)", "O(1)", True),
        ],
        notes=[
            (6, "Each halving removes a factor of 2; a leftover other than 1 means an odd factor greater than 1 exists.", False),
        ],
        predictions=[
            (5, "For n = 64, what is <code>n</code> the third time <code>n //= 2</code> is reached?", "n = 16; 64 was halved to 32 and then to 16."),
        ],
        patterns=["Math", "Bit Manipulation"],
        techniques=["Integer Division", "Early Exit"],
    ),
    problem(
        slug="minimum-bit-flips-to-convert-number",
        title="Minimum Bit Flips to Convert Number",
        topic="bit-manipulation",
        difficulty="easy",
        fn="min_bit_flips",
        signature="(start: int, goal: int) -> int",
        description=html(
            "Return the minimum number of single-bit flips needed to turn the binary form of <code>start</code> into the binary form of <code>goal</code>.",
        ),
        examples=[
            ("start = 10, goal = 7", "3", "1010 and 0111 differ in three positions"),
            ("start = 3, goal = 4", "3", "011 and 100 differ in all three bits"),
        ],
        constraints=["0 <= start, goal <= 10^9"],
        todo="XOR the two numbers, then count the 1 bits of the result.",
        solution="""
            def min_bit_flips(start: int, goal: int) -> int:
                diff = start ^ goal
                flips = 0
                while diff > 0:
                    flips += diff & 1
                    diff >>= 1
                return flips
        """,
        trace=1,
        cases=[
            ("10, 7", "3", False),
            ("3, 4", "3", False),
            ("5, 5", "0", True),
            ("0, 1073741823", "30", True),
            ("1, 2", "2", True),
        ],
        hints=(
            "A flip is needed exactly where the two numbers disagree. How can you find all disagreeing bit positions at once?",
            "XOR gives a 1 exactly where two bits differ.",
            "Now the problem is to count the 1 bits of that XOR value.",
        ),
        approaches=[
            ("Compare bit by bit", "Shift both numbers and compare the lowest bits each time.", "O(log n)", "O(1)", False),
            ("XOR then count set bits", "XOR marks every differing bit; counting them gives the answer.", "O(log n)", "O(1)", True),
        ],
        notes=[
            (5, "diff &amp; 1 is 1 when the lowest remaining bit is a difference, so flips counts the differing positions.", False),
        ],
        predictions=[
            (5, "For start = 10, goal = 7, what are <code>diff</code> and <code>flips</code> the third time <code>flips += diff &amp; 1</code> is reached?", "diff = 3 and flips = 1."),
        ],
        patterns=["Bit Manipulation"],
        techniques=["Bitwise XOR", "Accumulator"],
    ),
    problem(
        slug="set-the-rightmost-unset-bit",
        title="Set the Rightmost Unset Bit",
        topic="bit-manipulation",
        difficulty="easy",
        fn="set_rightmost_unset_bit",
        signature="(n: int) -> int",
        description=html(
            "Return <code>n</code> with its lowest <code>0</code> bit turned into a <code>1</code>. Only bits below the highest set bit count: if every bit of <code>n</code> is already 1 (such as 7 = 111), return <code>n</code> unchanged.",
        ),
        examples=[
            ("n = 6", "7", "110 becomes 111"),
            ("n = 47", "63", "101111 becomes 111111"),
        ],
        constraints=["1 <= n <= 2^31 - 1"],
        todo="If n is all ones return it; otherwise find the lowest zero bit by walking a mask upward.",
        solution="""
            def set_rightmost_unset_bit(n: int) -> int:
                if n & (n + 1) == 0:
                    return n
                bit = 1
                while n & bit:
                    bit <<= 1
                return n | bit
        """,
        trace=1,
        cases=[
            ("47", "63", False),
            ("6", "7", False),
            ("7", "7", True),
            ("1", "1", True),
            ("10", "11", True),
        ],
        hints=(
            "Write n in binary and point at the lowest 0. What do all the bits to its right look like?",
            "A number with all bits set is one less than a power of two. How can you detect that case?",
            "Slide a single-bit mask up from the lowest position until it lands on a 0, then use OR to set it.",
        ),
        approaches=[
            ("Convert to a string", "Find the last '0' in the binary string and flip it.", "O(log n)", "O(log n)", False),
            ("Mask upward then OR", "Move a one-bit mask left past every set bit, then n | mask.", "O(log n)", "O(1)", True),
        ],
        notes=[
            (2, "n &amp; (n + 1) is 0 only when n is all ones, because adding 1 carries through every bit.", False),
        ],
        predictions=[
            (6, "For n = 47, what is <code>bit</code> the third time <code>bit &lt;&lt;= 1</code> is reached?", "bit = 4; the three lowest bits of 47 are all set."),
        ],
        patterns=["Bit Manipulation"],
        techniques=["Bit Mask", "Bitwise OR"],
    ),
    problem(
        slug="xor-of-numbers-in-a-given-range",
        title="XOR of Numbers in a Range",
        topic="bit-manipulation",
        difficulty="medium",
        fn="xor_in_range",
        signature="(left: int, right: int) -> int",
        description=html(
            "Return the XOR of every integer from <code>left</code> to <code>right</code> inclusive.",
        ),
        examples=[
            ("left = 3, right = 5", "2", "3 ^ 4 ^ 5 = 2"),
            ("left = 4, right = 8", "8", "4 ^ 5 ^ 6 ^ 7 ^ 8 = 8"),
        ],
        constraints=["0 <= left <= right <= 10^6"],
        todo="XOR every number from left to right into a running result.",
        solution="""
            def xor_in_range(left: int, right: int) -> int:
                result = 0
                for x in range(left, right + 1):
                    result ^= x
                return result
        """,
        trace=2,
        cases=[
            ("3, 5", "2", False),
            ("4, 8", "8", False),
            ("7, 7", "7", True),
            ("0, 0", "0", True),
            ("1, 100000", "100000", True),
        ],
        hints=(
            "XOR is associative and commutative, so the order does not matter. Can you do better than one XOR per number?",
            "Let f(n) be the XOR of 0..n. Then the XOR of left..right is f(right) ^ f(left - 1).",
            "Write f(n) for n = 0 to 8 and look at the pattern every four numbers.",
        ),
        approaches=[
            ("XOR them all", "Loop from left to right.", "O(right - left)", "O(1)", False),
            ("Prefix XOR formula", "f(n) cycles with n % 4: n, 1, n + 1, 0; the answer is f(right) ^ f(left - 1).", "O(1)", "O(1)", True),
        ],
        notes=[
            (4, "XOR is its own inverse, so the order of numbers does not change the result.", False),
        ],
        predictions=[
            (4, "For left = 4, right = 8, what are <code>x</code> and <code>result</code> the third time <code>result ^= x</code> is reached?", "x = 6 and result = 1 (4 ^ 5)."),
        ],
        patterns=["Bit Manipulation", "Math"],
        techniques=["Bitwise XOR", "Accumulator"],
    ),
    problem(
        slug="divide-two-integers",
        title="Divide Two Integers",
        topic="bit-manipulation",
        difficulty="medium",
        fn="divide_integers",
        signature="(dividend: int, divisor: int) -> int",
        description=html(
            "Divide <code>dividend</code> by <code>divisor</code> without using multiplication, division or modulo, truncating the result toward zero (so 7 / -3 is -2).",
            "If the quotient falls outside the signed 32-bit range, clamp it to <code>-2^31</code> or <code>2^31 - 1</code>.",
        ),
        examples=[
            ("dividend = 10, divisor = 3", "3", "3 * 3 = 9 fits, 4 * 3 = 12 does not"),
            ("dividend = 22, divisor = 3", "7", "7 * 3 = 21 and 1 is left over"),
        ],
        constraints=["-2^31 <= dividend, divisor <= 2^31 - 1", "divisor is not 0"],
        todo="Work with absolute values and repeatedly subtract the largest divisor * 2^k that still fits.",
        solution="""
            def divide_integers(dividend: int, divisor: int) -> int:
                negative = (dividend < 0) != (divisor < 0)
                a = abs(dividend)
                b = abs(divisor)
                quotient = 0
                while a >= b:
                    shift = 0
                    while a >= (b << (shift + 1)):
                        shift += 1
                    a -= b << shift
                    quotient += 1 << shift
                if negative:
                    quotient = -quotient
                return min(max(quotient, -2**31), 2**31 - 1)
        """,
        trace=3,
        cases=[
            ("10, 3", "3", False),
            ("7, -3", "-2", False),
            ("22, 3", "7", False),
            ("-2147483648, -1", "2147483647", True),
            ("0, 5", "0", True),
            ("1, 1", "1", True),
        ],
        hints=(
            "Division is repeated subtraction, but subtracting the divisor one at a time is too slow. How could you subtract larger chunks?",
            "The chunks b, 2b, 4b, 8b, ... are cheap to produce with left shifts. Find the biggest one that still fits.",
            "After removing the biggest chunk, repeat on what is left, and add up which powers of two you used. Handle the sign and the overflow case separately.",
        ),
        approaches=[
            ("Repeated subtraction", "Subtract the divisor until the remainder is smaller.", "O(dividend / divisor)", "O(1)", False),
            ("Shift and subtract", "Subtract the largest b * 2^k that fits, then repeat on the remainder.", "O((log n)^2)", "O(1)", True),
        ],
        notes=[
            (10, "b &lt;&lt; shift is b * 2^shift without multiplication; it is the biggest chunk that fits into a.", False),
        ],
        predictions=[
            (10, "For dividend = 22, divisor = 3, what are <code>a</code> and <code>shift</code> the first time <code>a -= b &lt;&lt; shift</code> is reached?", "a = 22 and shift = 2, so 3 * 2^2 = 12 is removed first."),
        ],
        patterns=["Math", "Bit Manipulation"],
        techniques=["Bit Shift", "Greedy"],
    ),
]
