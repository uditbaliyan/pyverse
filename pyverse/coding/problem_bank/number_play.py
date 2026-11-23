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
    problem(
        slug="digit-sum-of-product",
        title="Digit Sum of a Product",
        topic="number-play",
        difficulty="easy",
        fn="digit_sum_of_product",
        signature="(a: int, b: int) -> int",
        description=html(
            "Multiply <code>a</code> and <code>b</code>, then return the sum of the decimal digits of the product.",
        ),
        examples=[
            ("a = 12, b = 34", "12", "12 * 34 = 408 and 4 + 0 + 8 = 12"),
        ],
        constraints=["0 <= a, b <= 10^6"],
        todo="Compute the product, then peel its digits with % 10 and // 10.",
        solution="""
            def digit_sum_of_product(a: int, b: int) -> int:
                product = a * b
                total = 0
                while product > 0:
                    total += product % 10
                    product //= 10
                return total
        """,
        trace=1,
        cases=[
            ("12, 34", "12", False),
            ("99, 99", "18", False),
            ("0, 5", "0", True),
            ("1, 1", "1", True),
            ("1000, 25", "7", True),
            ("123456, 789", "45", True),
        ],
        hints=(
            "Python integers do not overflow, so multiply first. How do you read one digit?",
            "<code>product % 10</code> is the last digit and <code>product // 10</code> removes it.",
            "Loop while <code>product > 0</code>, adding each last digit to <code>total</code>.",
        ),
        approaches=[
            (
                "Via a string",
                "<code>sum(int(d) for d in str(a * b))</code>.",
                "O(log(a*b))",
                "O(log(a*b))",
                False,
            ),
            (
                "Peel digits",
                "Use % and // so no string is needed.",
                "O(log(a*b))",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "% 10 reads the last digit and // 10 removes it, so product shrinks towards 0 and the loop ends.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For (12, 34), what is product the second time <code>total += product % 10</code> is reached?",
                "40 (408 with its last digit removed).",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator", "Integer division"],
    ),
    problem(
        slug="palindromic-numbers-in-range",
        title="Palindromic Numbers in a Range",
        topic="number-play",
        difficulty="medium",
        fn="palindromic_numbers",
        signature="(start: int, end: int) -> list[int]",
        description=html(
            "Return, in increasing order, every number from <code>start</code> to <code>end</code> inclusive that reads the same forwards and backwards (such as 7, 11 or 121).",
        ),
        examples=[
            (
                "start = 1, end = 20",
                "[1, 2, 3, 4, 5, 6, 7, 8, 9, 11]",
                "Single digits and 11 are palindromes",
            ),
        ],
        constraints=["0 <= start <= end <= 10^5"],
        todo="Convert each number to a string and compare it with its reverse.",
        solution="""
            def palindromic_numbers(start: int, end: int) -> list[int]:
                found = []
                for n in range(start, end + 1):
                    digits = str(n)
                    if digits == digits[::-1]:
                        found.append(n)
                return found
        """,
        trace=2,
        cases=[
            (
                "1, 100",
                "[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, 44, 55, 66, 77, 88, 99]",
                False,
            ),
            ("95, 112", "[99, 101, 111]", False),
            ("5, 5", "[5]", True),
            ("120, 130", "[121]", True),
            ("0, 9", "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]", True),
            ("100, 200", "[101, 111, 121, 131, 141, 151, 161, 171, 181, 191]", True),
        ],
        hints=(
            "When does a string equal its own reverse?",
            "Turn n into a string with <code>str(n)</code> and compare with <code>digits[::-1]</code>.",
            "Append n to the result whenever the comparison is true.",
        ),
        approaches=[
            (
                "Reverse the number arithmetically",
                "Rebuild the reversed number with % and //.",
                "O((end - start) log end)",
                "O(1)",
                False,
            ),
            (
                "Compare with the reversed string",
                "<code>s[::-1]</code> reverses a string in one slice.",
                "O((end - start) log end)",
                "O(log end)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "s[::-1] reverses the string; a number is a palindrome exactly when it equals its reverse.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                "For (95, 112), what is n the first time <code>found.append(n)</code> is reached?",
                "99.",
            ),
        ],
        patterns=["Math", "String"],
        techniques=["Slicing", "str()"],
    ),
    problem(
        slug="divisors-of-a-product",
        title="Divisors of a Product",
        topic="number-play",
        difficulty="medium",
        fn="divisors_of_product",
        signature="(a: int, b: int) -> list[int]",
        description=html(
            "Multiply <code>a</code> and <code>b</code> and return all positive divisors of the product in ascending order.",
        ),
        examples=[
            (
                "a = 6, b = 10",
                "[1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]",
                "60 has twelve divisors, from 1 up to 60",
            ),
        ],
        constraints=["1 <= a, b <= 10^6"],
        todo="Divisors come in pairs d and n // d, so only test d up to the square root of n.",
        solution="""
            def divisors_of_product(a: int, b: int) -> list[int]:
                n = a * b
                small = []
                large = []
                d = 1
                while d * d <= n:
                    if n % d == 0:
                        small.append(d)
                        if d != n // d:
                            large.append(n // d)
                    d += 1
                return small + large[::-1]
        """,
        trace=1,
        cases=[
            ("6, 10", "[1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]", False),
            ("4, 4", "[1, 2, 4, 8, 16]", False),
            ("1, 1", "[1]", True),
            ("7, 1", "[1, 7]", True),
            ("12, 12", "[1, 2, 3, 4, 6, 8, 9, 12, 16, 18, 24, 36, 48, 72, 144]", True),
            ("97, 3", "[1, 3, 97, 291]", True),
        ],
        hints=(
            "If d divides n, so does n // d. How can that halve the search?",
            "Loop d while <code>d * d <= n</code>; each hit gives two divisors, a small one and a large one.",
            "Collect small divisors ascending, large ones descending, then join with <code>small + large[::-1]</code>.",
        ),
        approaches=[
            (
                "Test every number up to n",
                "Check each d from 1 to n.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Pair divisors up to sqrt(n)",
                "Each divisor d below sqrt(n) brings n // d with it.",
                "O(sqrt n)",
                "O(number of divisors)",
                True,
            ),
        ],
        notes=[
            (
                9,
                "When d * d == n, d and n // d are the same divisor; this check keeps perfect squares from listing it twice.",
                False,
            ),
        ],
        predictions=[
            (
                12,
                "For (6, 10), what is small when <code>return</code> is reached?",
                "[1, 2, 3, 4, 5, 6].",
            ),
        ],
        patterns=["Math", "Number Theory"],
        techniques=["Divisor pairing", "Reverse slice"],
    ),
    problem(
        slug="sum-of-first-n-fibonacci",
        title="Sum of the First N Fibonacci Numbers",
        topic="number-play",
        difficulty="medium",
        fn="sum_first_fibonacci",
        signature="(n: int) -> int",
        description=html(
            "The Fibonacci sequence here starts <code>1, 1, 2, 3, 5, 8, ...</code> (each term is the sum of the two before it). Return the sum of the first <code>n</code> terms; for <code>n = 0</code> return 0.",
        ),
        examples=[
            ("n = 5", "12", "1 + 1 + 2 + 3 + 5"),
        ],
        constraints=["0 <= n <= 90"],
        todo="Generate the terms with two running values and add each one to a total.",
        solution="""
            def sum_first_fibonacci(n: int) -> int:
                total = 0
                a, b = 1, 1
                for _ in range(n):
                    total += a
                    a, b = b, a + b
                return total
        """,
        trace=1,
        cases=[
            ("5", "12", False),
            ("8", "54", False),
            ("0", "0", True),
            ("1", "1", True),
            ("2", "2", True),
            ("30", "2178308", True),
        ],
        hints=(
            "You only ever need the last two Fibonacci numbers.",
            "Keep a and b; add a to the total, then slide the pair forward.",
            "<code>a, b = b, a + b</code> after <code>total += a</code>.",
        ),
        approaches=[
            (
                "Two running values",
                "Generate each term once and add it.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "The right side uses the old a and b, so one tuple assignment advances the pair without a temporary variable.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For n = 5, what are a and total the fourth time <code>total += a</code> is reached?",
                "a = 3 and total = 4 (1 + 1 + 2).",
            ),
        ],
        patterns=["Math"],
        techniques=["Tuple unpacking", "Accumulator"],
    ),
    problem(
        slug="sum-of-first-n-even-numbers",
        title="Sum of the First N Even Numbers",
        topic="number-play",
        difficulty="easy",
        fn="sum_first_evens",
        signature="(n: int) -> int",
        description=html(
            "Return the sum of the first <code>n</code> positive even numbers: <code>2 + 4 + 6 + ...</code>. For <code>n = 0</code> return 0.",
        ),
        examples=[
            ("n = 4", "20", "2 + 4 + 6 + 8"),
        ],
        constraints=["0 <= n <= 10^5"],
        todo="Keep the next even number in a variable; add it, then step it up by 2.",
        solution="""
            def sum_first_evens(n: int) -> int:
                total = 0
                even = 2
                for _ in range(n):
                    total += even
                    even += 2
                return total
        """,
        trace=1,
        cases=[
            ("4", "20", False),
            ("1", "2", False),
            ("0", "0", True),
            ("10", "110", True),
            ("50", "2550", True),
        ],
        hints=(
            "What is the gap between two consecutive even numbers?",
            "Loop n times, adding the current even number and then moving to the next.",
            "<code>total += even</code> then <code>even += 2</code>.",
        ),
        approaches=[
            (
                "Add term by term (this solution)",
                "One pass that adds each even number.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Closed form",
                "The first n even numbers sum to <code>n * (n + 1)</code>.",
                "O(1)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "Even numbers are 2 apart, so stepping by 2 visits each one in turn without any divisibility test.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For n = 4, what are even and total the third time <code>total += even</code> is reached?",
                "even = 6 and total = 6 (2 + 4).",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator"],
    ),
    problem(
        slug="count-digits-above-value",
        title="Count Digits Above a Value",
        topic="number-play",
        difficulty="easy",
        fn="count_digits_above",
        signature="(number: int, value: int) -> int",
        description=html(
            "Count how many decimal digits of <code>number</code> are strictly greater than <code>value</code>.",
        ),
        examples=[
            (
                "number = 54321, value = 3",
                "2",
                "Only the digits 5 and 4 are greater than 3",
            ),
        ],
        constraints=["0 <= number <= 10^9", "0 <= value <= 8"],
        todo="Peel digits off with % 10 and // 10, counting the ones above value.",
        solution="""
            def count_digits_above(number: int, value: int) -> int:
                count = 0
                while number > 0:
                    if number % 10 > value:
                        count += 1
                    number //= 10
                return count
        """,
        trace=1,
        cases=[
            ("54321, 3", "2", False),
            ("9090, 4", "2", False),
            ("0, 0", "0", True),
            ("777, 6", "3", True),
            ("100, 0", "1", True),
            ("5, 8", "0", True),
        ],
        hints=(
            "How do you read the last digit of an integer?",
            "<code>number % 10</code> is the last digit and <code>number // 10</code> drops it.",
            "Inside <code>while number > 0</code> add 1 to count when the last digit is above value.",
        ),
        approaches=[
            (
                "Via a string",
                "Loop over <code>str(number)</code> and compare each digit.",
                "O(log n)",
                "O(log n)",
                False,
            ),
            (
                "Peel digits",
                "Use % and // without building a string.",
                "O(log n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                6,
                "Dropping the last digit each pass moves the next digit into the units place, so every digit is checked exactly once.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For (54321, 3), what is number the first time <code>count += 1</code> is reached?",
                "54 (the digits 1, 2 and 3 were removed first).",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator", "Integer division"],
    ),
    problem(
        slug="sum-of-even-squares",
        title="Sum of Even Squares",
        topic="number-play",
        difficulty="medium",
        fn="sum_even_squares",
        signature="(n: int) -> int",
        description=html(
            "Return the sum of the squares of all even numbers from 2 up to <code>n</code> inclusive. If <code>n < 2</code> the sum is 0.",
        ),
        examples=[
            ("n = 4", "20", "2 * 2 + 4 * 4 = 20"),
        ],
        constraints=["0 <= n <= 10^5"],
        todo="Step through 2, 4, 6, ... up to n and add each square.",
        solution="""
            def sum_even_squares(n: int) -> int:
                total = 0
                for k in range(2, n + 1, 2):
                    total += k * k
                return total
        """,
        trace=2,
        cases=[
            ("4", "20", False),
            ("8", "120", False),
            ("1", "0", True),
            ("0", "0", True),
            ("10", "220", True),
            ("100", "171700", True),
        ],
        hints=(
            "Which numbers between 1 and n do you actually need?",
            "range accepts a step, so you can visit only the even numbers.",
            "<code>for k in range(2, n + 1, 2): total += k * k</code>.",
        ),
        approaches=[
            (
                "Add term by term (this solution)",
                "Visit every even k and add its square.",
                "O(n)",
                "O(1)",
                False,
            ),
            (
                "Closed form",
                "With m = n // 2 the sum is <code>2 * m * (m + 1) * (2 * m + 1) // 3</code>.",
                "O(1)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                3,
                "The step of 2 visits only even numbers, so no k % 2 == 0 test is needed inside the loop.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For n = 8, what is total the third time <code>total += k * k</code> is reached (k = 6)?",
                "20 (4 + 16).",
            ),
        ],
        patterns=["Math"],
        techniques=["range with step", "Accumulator"],
    ),
]
