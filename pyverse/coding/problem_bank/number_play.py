# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="digital-root",
        title="Digital Root",
        topic="number-play",
        difficulty="easy",
        fn="digital_root",
        signature="(n: int) -> int",
        description=html(
            "Replace <code>n</code> with the sum of its decimal digits, and keep doing that until only a single digit is left. Return that digit.",
            "For <code>n = 9875</code> the chain is 9875 -> 29 -> 11 -> 2.",
        ),
        examples=[
            ("n = 9875", "2", "29, then 11, then 2"),
        ],
        constraints=["0 <= n <= 10^9"],
        todo="Sum the digits of n; repeat while the result still has two or more digits.",
        solution="""
            def digital_root(n: int) -> int:
                while n >= 10:
                    total = 0
                    while n > 0:
                        total += n % 10
                        n //= 10
                    n = total
                return n
        """,
        trace=2,
        cases=[
            ("123", "6", False),
            ("9875", "2", False),
            ("0", "0", True),
            ("7", "7", True),
            ("99999", "9", True),
            ("10", "1", True),
        ],
        hints=(
            "What does <code>n % 10</code> give you, and how do you drop that digit?",
            "An inner loop sums the digits; an outer loop repeats while the sum is still 10 or more.",
            "After the inner loop, assign <code>n = total</code> so the outer loop sees the digit sum.",
        ),
        approaches=[
            (
                "Repeat the digit sum",
                "Simulate the process exactly as described.",
                "O(log n)",
                "O(1)",
                False,
            ),
            (
                "Casting out nines",
                "For n > 0 the answer is <code>1 + (n - 1) % 9</code>.",
                "O(1)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                7,
                "Reassigning n restarts the outer loop on the digit sum, which is smaller than n, so the process must end.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For n = 9875, what is total the first time <code>n = total</code> is reached?",
                "29 (9 + 8 + 7 + 5).",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator", "Nested loops"],
    ),
    problem(
        slug="harmonic-series-sum",
        title="Harmonic Series Sum",
        topic="number-play",
        difficulty="medium",
        fn="harmonic_sum",
        signature="(n: int) -> float",
        description=html(
            "Return <code>1 + 1/2 + 1/3 + ... + 1/n</code> as a float. For <code>n = 0</code> the sum is empty, so return <code>0.0</code>.",
            "Answers are compared with a small tolerance, so you do not need to round.",
        ),
        examples=[
            (
                "n = 4",
                "2.0833333333333335",
                "1 + 0.5 + 0.3333 + 0.25 is about 2.083333",
            ),
        ],
        constraints=["0 <= n <= 10^5"],
        todo="Add 1 / k to a running total for k = 1..n.",
        solution="""
            def harmonic_sum(n: int) -> float:
                total = 0.0
                for k in range(1, n + 1):
                    total += 1 / k
                return total
        """,
        trace=1,
        comparator="float_tolerance",
        cases=[
            ("4", "2.0833333333333335", False),
            ("1", "1.0", False),
            ("10", "2.9289682539682538", True),
            ("0", "0.0", True),
            ("50", "4.499205338329425", True),
        ],
        hints=(
            "Which operator gives a true fraction in Python 3: <code>/</code> or <code>//</code>?",
            "Keep a float accumulator and add one term per loop pass.",
            "<code>total += 1 / k</code> inside <code>for k in range(1, n + 1)</code>.",
        ),
        approaches=[
            ("Running total", "Add each term as you go.", "O(n)", "O(1)", True),
        ],
        notes=[
            (
                4,
                "/ is true division, so 1 / k keeps the fraction; // would give 0 for every k above 1.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For n = 4, what is total the third time <code>total += 1 / k</code> is reached (k = 3)?",
                "1.5 (1 + 1/2).",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator", "Float arithmetic"],
    ),
    problem(
        slug="gcd-of-a-list",
        title="GCD of a List",
        topic="number-play",
        difficulty="medium",
        fn="gcd_of_list",
        signature="(nums: list[int]) -> int",
        description=html(
            "Return the greatest common divisor of every number in <code>nums</code>: the largest integer that divides all of them exactly.",
        ),
        examples=[
            (
                "nums = [12, 24, 36]",
                "12",
                "12 divides all three and nothing larger does",
            ),
        ],
        constraints=["1 <= len(nums) <= 1000", "1 <= nums[i] <= 10^9"],
        todo="Fold the list: combine the running gcd with each next number using Euclid's algorithm.",
        solution="""
            def gcd_of_list(nums: list[int]) -> int:
                result = nums[0]
                for x in nums[1:]:
                    a, b = result, x
                    while b != 0:
                        a, b = b, a % b
                    result = a
                return result
        """,
        trace=2,
        cases=[
            ("[12, 24, 36]", "12", False),
            ("[48, 18, 30]", "6", False),
            ("[7]", "7", True),
            ("[17, 5]", "1", True),
            ("[100, 75, 25, 50]", "25", True),
        ],
        hints=(
            "gcd(a, b) equals gcd(b, a % b). What happens when the second number reaches 0?",
            "Compute the gcd of two numbers with a while loop, then reuse it across the list.",
            "Keep <code>result</code> as the gcd so far; for each x replace it with gcd(result, x).",
        ),
        approaches=[
            (
                "Try every divisor",
                "Count down from min(nums) until one divides everything.",
                "O(n * min(nums))",
                "O(1)",
                False,
            ),
            (
                "Euclid, folded",
                "gcd(a, b, c) = gcd(gcd(a, b), c); Euclid is logarithmic per step.",
                "O(n log m)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "a % b shrinks every round and gcd(a, b) == gcd(b, a % b), so the loop ends at b == 0 with the answer in a.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                "For [48, 18, 30], what is a the first time <code>result = a</code> is reached?",
                "6, which is gcd(48, 18).",
            ),
        ],
        patterns=["Math"],
        techniques=["Tuple unpacking", "Fold / reduce"],
    ),
    problem(
        slug="sum-of-first-n-odd-numbers",
        title="Sum of the First N Odd Numbers",
        topic="number-play",
        difficulty="easy",
        fn="sum_first_odds",
        signature="(n: int) -> int",
        description=html(
            "Return the sum of the first <code>n</code> odd numbers: <code>1 + 3 + 5 + ...</code>. For <code>n = 0</code> the sum is 0.",
        ),
        examples=[
            ("n = 5", "25", "1 + 3 + 5 + 7 + 9"),
        ],
        constraints=["0 <= n <= 10^5"],
        todo="Keep the next odd number in a variable; add it, then step it up by 2.",
        solution="""
            def sum_first_odds(n: int) -> int:
                total = 0
                odd = 1
                for _ in range(n):
                    total += odd
                    odd += 2
                return total
        """,
        trace=1,
        cases=[
            ("5", "25", False),
            ("1", "1", False),
            ("0", "0", True),
            ("10", "100", True),
            ("100", "10000", True),
        ],
        hints=(
            "What is the difference between two consecutive odd numbers?",
            "Loop n times, adding the current odd number then moving to the next.",
            "<code>total += odd</code> then <code>odd += 2</code>.",
        ),
        approaches=[
            (
                "Add term by term (this solution)",
                "One pass that adds each odd number.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Closed form",
                "The first n odd numbers always sum to <code>n * n</code>.",
                "O(1)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "odd advances by 2 each pass, so total is always the next perfect square: 1, 4, 9, 16, 25.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For n = 5, what is total the third time <code>odd += 2</code> is reached?",
                "9 (1 + 3 + 5).",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator"],
    ),
    problem(
        slug="count-perfect-numbers",
        title="Count Perfect Numbers",
        topic="number-play",
        difficulty="medium",
        fn="count_perfect_numbers",
        signature="(limit: int) -> int",
        description=html(
            "A perfect number equals the sum of its proper divisors (all positive divisors except itself). For example 6 = 1 + 2 + 3.",
            "Return how many perfect numbers are at most <code>limit</code>.",
        ),
        examples=[
            ("limit = 30", "2", "6 = 1 + 2 + 3 and 28 = 1 + 2 + 4 + 7 + 14"),
        ],
        constraints=["1 <= limit <= 1000"],
        todo="For each n, add up its divisors below n and compare with n.",
        solution="""
            def count_perfect_numbers(limit: int) -> int:
                count = 0
                for n in range(2, limit + 1):
                    divisor_sum = 1
                    for d in range(2, n // 2 + 1):
                        if n % d == 0:
                            divisor_sum += d
                    if divisor_sum == n:
                        count += 1
                return count
        """,
        trace=2,
        cases=[
            ("30", "2", False),
            ("10", "1", False),
            ("5", "0", True),
            ("28", "2", True),
            ("500", "3", True),
            ("1", "0", True),
        ],
        hints=(
            "What is a 'proper divisor', and which numbers can never be one?",
            "Divisors of n (other than n) are at most n // 2. Sum them and compare with n.",
            "Start <code>divisor_sum</code> at 1 (1 always divides n) and loop d from 2 to n // 2.",
        ),
        approaches=[
            (
                "Scan every smaller number",
                "Test d = 1..n-1 for each n.",
                "O(limit^2)",
                "O(1)",
                False,
            ),
            (
                "Scan up to n // 2",
                "No proper divisor exceeds n // 2, so half the work; pairing divisors up to sqrt(n) is faster still.",
                "O(limit^2)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "1 divides every n, and n itself is left out because only proper divisors count.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                "For limit = 10, what is divisor_sum on the fifth arrival at the line <code>if divisor_sum == n</code> (n = 6)?",
                "6, since 1 + 2 + 3 = 6.",
            ),
        ],
        patterns=["Math", "Brute Force"],
        techniques=["Nested loops", "Accumulator"],
    ),
    problem(
        slug="largest-prime-factor",
        title="Largest Prime Factor",
        topic="number-play",
        difficulty="medium",
        fn="largest_prime_factor",
        signature="(n: int) -> int",
        description=html(
            "Return the largest prime number that divides <code>n</code> exactly. If <code>n</code> is itself prime, the answer is <code>n</code>.",
        ),
        examples=[
            ("n = 28", "7", "28 = 2 * 2 * 7, so the largest prime factor is 7"),
        ],
        constraints=["2 <= n <= 10^12"],
        todo="Divide out small factors one at a time; whatever is left at the end may be a bigger prime.",
        solution="""
            def largest_prime_factor(n: int) -> int:
                factor = 2
                largest = 1
                while factor * factor <= n:
                    if n % factor == 0:
                        n //= factor
                        largest = factor
                    else:
                        factor += 1
                return max(largest, n)
        """,
        trace=2,
        cases=[
            ("28", "7", False),
            ("45", "5", False),
            ("2", "2", True),
            ("97", "97", True),
            ("1024", "2", True),
            ("999983", "999983", True),
        ],
        hints=(
            "Every composite number is a product of primes. What happens if you keep dividing by the smallest factor?",
            "Try factors from 2 upwards; when one divides n, divide it out and keep the same factor. Stop when factor * factor > n.",
            "The leftover n after the loop (if above 1) is prime, so return <code>max(largest, n)</code>.",
        ),
        approaches=[
            (
                "Test every number up to n",
                "Check each candidate for being a prime divisor.",
                "O(n sqrt n)",
                "O(1)",
                False,
            ),
            (
                "Trial division with shrinking n",
                "Divide factors out as found and stop at sqrt of the remaining n.",
                "O(sqrt n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                10,
                "If n is still above 1 here it is a prime larger than every factor tried, hence max(largest, n).",
                False,
            ),
        ],
        predictions=[
            (
                10,
                "For n = 45, what are largest and n when <code>return</code> is reached?",
                "largest = 3 and n = 5; the leftover 5 is the answer.",
            ),
        ],
        patterns=["Math", "Number Theory"],
        techniques=["Trial division", "Early stop at sqrt"],
    ),
    problem(
        slug="sum-of-first-n-primes",
        title="Sum of the First N Primes",
        topic="number-play",
        difficulty="medium",
        fn="sum_first_primes",
        signature="(n: int) -> int",
        description=html(
            "Return the sum of the first <code>n</code> prime numbers (2, 3, 5, 7, ...). For <code>n = 0</code> return 0.",
        ),
        examples=[
            ("n = 4", "17", "2 + 3 + 5 + 7"),
        ],
        constraints=["0 <= n <= 1000"],
        todo="Test candidates 2, 3, 4, ... and keep the primes you find until you have n of them.",
        solution="""
            def sum_first_primes(n: int) -> int:
                primes = []
                candidate = 2
                while len(primes) < n:
                    if all(candidate % p != 0 for p in primes):
                        primes.append(candidate)
                    candidate += 1
                return sum(primes)
        """,
        trace=1,
        cases=[
            ("4", "17", False),
            ("10", "129", False),
            ("0", "0", True),
            ("1", "2", True),
            ("25", "1060", True),
        ],
        hints=(
            "A number is prime if no smaller prime divides it. Which primes do you already know?",
            "Keep a list of primes found so far and test each candidate against that list.",
            "Append the candidate when <code>all(candidate % p != 0 for p in primes)</code>, then step the candidate.",
        ),
        approaches=[
            (
                "Test every smaller number",
                "Check candidate against all d below it.",
                "O(p_n^2)",
                "O(n)",
                False,
            ),
            (
                "Test against known primes",
                "A composite always has a smaller prime factor already in the list.",
                "O(n * p_n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Only earlier primes need testing: any composite candidate has a smaller prime factor that is already in the list.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For n = 4, what is candidate the third time <code>primes.append(candidate)</code> is reached?",
                "5 (4 was rejected by 2).",
            ),
        ],
        patterns=["Math", "Prime Numbers"],
        techniques=["all()", "Generator expression"],
    ),
    problem(
        slug="perfect-squares-in-range",
        title="Perfect Squares in a Range",
        topic="number-play",
        difficulty="easy",
        fn="perfect_squares_in_range",
        signature="(start: int, end: int) -> list[int]",
        description=html(
            "Return, in increasing order, every perfect square (1, 4, 9, 16, ...) that lies between <code>start</code> and <code>end</code> inclusive. Return an empty list if there are none.",
        ),
        examples=[
            (
                "start = 1, end = 10",
                "[1, 4, 9]",
                "1, 4 and 9 are the squares of 1, 2, 3",
            ),
        ],
        constraints=["1 <= start <= end <= 10^9"],
        todo="Walk over the roots 1, 2, 3, ... and keep each square that falls in the range.",
        solution="""
            def perfect_squares_in_range(start: int, end: int) -> list[int]:
                squares = []
                root = 1
                while root * root <= end:
                    if root * root >= start:
                        squares.append(root * root)
                    root += 1
                return squares
        """,
        trace=2,
        cases=[
            ("1, 10", "[1, 4, 9]", False),
            ("10, 50", "[16, 25, 36, 49]", False),
            ("5, 8", "[]", True),
            ("16, 16", "[16]", True),
            ("1, 1", "[1]", True),
            ("1, 100", "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]", True),
        ],
        hints=(
            "A perfect square is root * root. Which roots can land in the range?",
            "Instead of testing every number, step the root upwards and square it.",
            "Stop when <code>root * root > end</code>; append the square only if it is at least <code>start</code>.",
        ),
        approaches=[
            (
                "Test every number",
                "Check each n in the range for an integer square root.",
                "O(end - start)",
                "O(1)",
                False,
            ),
            (
                "Step the root",
                "Only about sqrt(end) squares are ever examined.",
                "O(sqrt(end))",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Stepping the root checks about sqrt(end) candidates; this guard skips squares that are still below start.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For (10, 50), what is root the first time <code>squares.append(...)</code> is reached?",
                "4, because 4 * 4 = 16 is the first square that is at least 10.",
            ),
        ],
        patterns=["Math"],
        techniques=["While loop", "Accumulator list"],
    ),
]
