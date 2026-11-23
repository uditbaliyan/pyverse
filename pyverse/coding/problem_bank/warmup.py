# ruff: noqa: E501, ISC004
"""Warm-up: loops, strings and arithmetic. No data structures needed."""

from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="fizz-buzz",
        title="Fizz Buzz",
        topic="warm-up",
        difficulty="easy",
        fn="fizz_buzz",
        signature="(n: int) -> list[str]",
        description=html(
            "Return a list of strings for the numbers <code>1</code> to <code>n</code>:",
            '<ul><li><code>"FizzBuzz"</code> if the number is a multiple of both 3 and 5</li>'
            '<li><code>"Fizz"</code> if it is a multiple of 3</li>'
            '<li><code>"Buzz"</code> if it is a multiple of 5</li>'
            "<li>otherwise the number itself, as a string</li></ul>",
        ),
        examples=[
            ("n = 5", '["1","2","Fizz","4","Buzz"]', "3 is Fizz, 5 is Buzz."),
        ],
        constraints=["1 <= n <= 10^4"],
        todo="Build and return the list for 1..n.",
        solution="""
            def fizz_buzz(n: int) -> list[str]:
                result = []
                for number in range(1, n + 1):
                    if number % 15 == 0:
                        result.append("FizzBuzz")
                    elif number % 3 == 0:
                        result.append("Fizz")
                    elif number % 5 == 0:
                        result.append("Buzz")
                    else:
                        result.append(str(number))
                return result
        """,
        cases=[
            ("5", '["1", "2", "Fizz", "4", "Buzz"]', False),
            ("3", '["1", "2", "Fizz"]', False),
            ("1", '["1"]', True),
            (
                "15",
                '["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", '
                '"11", "Fizz", "13", "14", "FizzBuzz"]',
                True,
            ),
        ],
        hints=(
            "A number can match more than one rule. What should happen to 15?",
            "Loop over <code>range(1, n + 1)</code> and test the most specific rule first.",
            "Check <code>number % 15 == 0</code> before the 3 and 5 checks, "
            "then fall back to <code>str(number)</code>.",
        ),
        approaches=[
            (
                "Test 15 first",
                "One loop with an if/elif chain. The multiple-of-15 test must come first.",
                "O(n)",
                "O(n)",
                True,
            ),
            (
                "Build the word, then fall back",
                "Start with an empty string, add 'Fizz' for 3 and 'Buzz' for 5, "
                "and use the number when the string stayed empty.",
                "O(n)",
                "O(n)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "Check 15 first. A multiple of 15 is also a multiple of 3 and of 5, so "
                "any later position would catch it too early.",
                False,
            ),
            (
                11,
                "Everything that matched no rule is just the number, as a string.",
                False,
            ),
        ],
        predictions=[
            (7, "For n = 5, which number is being handled when this line runs?", "3"),
        ],
        patterns=["Iteration"],
        techniques=["Modulo", "String Formatting"],
    ),
    problem(
        slug="count-vowels",
        title="Count Vowels",
        topic="warm-up",
        difficulty="easy",
        fn="count_vowels",
        signature="(s: str) -> int",
        description=html(
            "Return how many vowels (<code>a</code>, <code>e</code>, <code>i</code>, "
            "<code>o</code>, <code>u</code>) appear in the string <code>s</code>.",
            "Upper and lower case count the same. <code>y</code> is not a vowel.",
        ),
        examples=[
            ('s = "hello"', "2", "e and o."),
            ('s = "Python is fun"', "3", "o, i and u."),
        ],
        constraints=["0 <= len(s) <= 10^5", "s may contain spaces and punctuation."],
        todo="Count the vowels in s, ignoring case.",
        solution="""
            def count_vowels(s: str) -> int:
                vowels = set("aeiou")
                count = 0
                for char in s.lower():
                    if char in vowels:
                        count += 1
                return count
        """,
        cases=[
            ('"hello"', "2", False),
            ('"Python is fun"', "3", False),
            ('""', "0", True),
            ('"rhythm"', "0", True),
            ('"AEIOU"', "5", True),
        ],
        hints=(
            "Which characters should be ignored? Which should be counted?",
            "Turn the string to lower case once, then test each character "
            "against the five vowels.",
            "Keep the vowels in a <code>set</code> and add 1 to a counter "
            "whenever <code>char in vowels</code>.",
        ),
        approaches=[
            (
                "Loop with a counter",
                "Lower-case the string and add 1 for every character in a set of vowels.",
                "O(n)",
                "O(1)",
                True,
            ),
            (
                "Generator and sum",
                "<code>sum(char in vowels for char in s.lower())</code> does the same "
                "thing in one line.",
                "O(n)",
                "O(1)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "lower() runs once, before the loop, so 'A' and 'a' are treated the same.",
                False,
            ),
            (5, "A set answers 'is this one of the vowels?' in one step.", False),
        ],
        predictions=[
            (
                7,
                'How many times did the counter line run for "hello"?',
                "2 (the e and the o)",
            ),
        ],
        patterns=["Iteration"],
        techniques=["Sets", "Accumulator"],
    ),
    problem(
        slug="sum-of-digits",
        title="Sum of Digits",
        topic="warm-up",
        difficulty="easy",
        fn="digit_sum",
        signature="(n: int) -> int",
        description=html(
            "Return the sum of the decimal digits of the non-negative integer <code>n</code>.",
            "Do it with arithmetic (<code>%</code> and <code>//</code>), "
            "without converting <code>n</code> to a string.",
        ),
        examples=[
            ("n = 123", "6", "1 + 2 + 3"),
            ("n = 9045", "18", "9 + 0 + 4 + 5"),
        ],
        constraints=["0 <= n <= 10^9"],
        todo="Peel digits off n with % and //.",
        solution="""
            def digit_sum(n: int) -> int:
                total = 0
                while n > 0:
                    total += n % 10
                    n //= 10
                return total
        """,
        cases=[
            ("123", "6", False),
            ("9045", "18", False),
            ("0", "0", True),
            ("7", "7", True),
            ("99999", "45", True),
        ],
        hints=(
            "What does <code>n % 10</code> give you? What does <code>n // 10</code> do?",
            "Use a <code>while n > 0</code> loop: take the last digit, add it, then drop it.",
            "<code>total += n % 10</code> followed by <code>n //= 10</code>, "
            "until <code>n</code> reaches 0.",
        ),
        approaches=[
            (
                "Peel digits with % and //",
                "The remainder by 10 is the last digit; integer division by 10 removes it.",
                "O(log n)",
                "O(1)",
                True,
            ),
            (
                "Via a string",
                "<code>sum(int(d) for d in str(n))</code>. Shorter, but the question "
                "asks for arithmetic.",
                "O(log n)",
                "O(log n)",
                False,
            ),
        ],
        notes=[
            (
                5,
                "Integer division drops the last digit: 123 becomes 12, then 1, then 0, "
                "and the loop ends.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "What is n % 10 the first time through, for n = 123?",
                "3, the last digit.",
            ),
        ],
        patterns=["Math"],
        techniques=["Accumulator", "Modulo"],
    ),
]
