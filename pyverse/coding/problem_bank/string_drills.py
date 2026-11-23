# ruff: noqa: E501
from ._spec import html
from ._spec import problem

PROBLEMS = [
    problem(
        slug="count-palindromic-substrings",
        title="Count Palindromic Substrings",
        topic="string-play",
        difficulty="medium",
        fn="count_palindromic_substrings",
        signature="(s: str) -> int",
        description=html(
            "Count the substrings of <code>s</code> that read the same forwards and backwards. Substrings at different positions count separately even if their letters match.",
            'In <code>"aaa"</code> the answer is 6: three single letters, two copies of <code>"aa"</code> and one <code>"aaa"</code>.',
        ),
        examples=[
            ('s = "aaa"', "6", "a, a, a, aa, aa, aaa"),
        ],
        constraints=["0 <= len(s) <= 1000"],
        todo="Treat every letter and every gap between letters as a centre and grow outwards while the ends match.",
        solution="""
            def count_palindromic_substrings(s: str) -> int:
                count = 0
                for center in range(2 * len(s) - 1):
                    left = center // 2
                    right = left + center % 2
                    while left >= 0 and right < len(s) and s[left] == s[right]:
                        count += 1
                        left -= 1
                        right += 1
                return count
        """,
        trace=1,
        cases=[
            ('"aaa"', "6", False),
            ('"abc"', "3", False),
            ('"a"', "1", True),
            ('"abba"', "6", True),
            ('"racecar"', "10", True),
            ('""', "0", True),
        ],
        hints=(
            "A palindrome mirrors around its middle. Where can a middle sit?",
            "There are 2n - 1 centres: n letters and n - 1 gaps. Expand left and right while the characters match.",
            "Each successful expansion is one more palindrome, so add 1 to count inside the while loop.",
        ),
        approaches=[
            (
                "Check every substring",
                "Slice all substrings and compare with the reverse.",
                "O(n^3)",
                "O(n)",
                False,
            ),
            (
                "Expand around centres",
                "Grow outwards from each of the 2n - 1 centres.",
                "O(n^2)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Even-numbered centres start with left == right (a single letter); odd-numbered centres start between two neighbouring letters.",
                False,
            ),
        ],
        predictions=[
            (
                10,
                'For "aaa", what is count when <code>return count</code> is reached?',
                "6.",
            ),
        ],
        patterns=["Expand Around Center", "Two Pointers"],
        techniques=["Accumulator", "String Indexing"],
    ),
    problem(
        slug="sum-of-numbers-in-text",
        title="Sum of Numbers in Text",
        topic="string-play",
        difficulty="easy",
        fn="sum_numbers_in_text",
        signature="(text: str) -> int",
        description=html(
            'Every run of consecutive digits in <code>text</code> is one whole number (so <code>"123"</code> is 123, not 1 + 2 + 3). Return the sum of all such numbers; return 0 if there are none.',
            "Numbers are non-negative; a minus sign is just an ordinary character.",
        ),
        examples=[
            ('text = "The numbers are 12 and 34"', "46", "12 + 34"),
        ],
        constraints=["0 <= len(text) <= 10^4"],
        todo="Build the current number digit by digit; add it to the total when a non-digit ends it.",
        solution="""
            def sum_numbers_in_text(text: str) -> int:
                total = 0
                current = 0
                for ch in text:
                    if ch.isdigit():
                        current = current * 10 + int(ch)
                    else:
                        total += current
                        current = 0
                return total + current
        """,
        trace=2,
        cases=[
            ('"The numbers are 12 and 34"', "46", False),
            ('"x7y25z"', "32", False),
            ('""', "0", True),
            ('"no digits"', "0", True),
            ('"007"', "7", True),
            ('"100 200"', "300", True),
        ],
        hints=(
            "How do you turn the digits '2' then '5' into the number 25?",
            "Keep a <code>current</code> number: multiply by 10 and add the new digit. A non-digit ends the number.",
            "On a non-digit add <code>current</code> to <code>total</code> and reset it; after the loop add whatever is left.",
        ),
        approaches=[
            (
                "Regular expression",
                "<code>re.findall(r'\\d+', text)</code> then sum the integers.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Build numbers digit by digit",
                "One pass with a running number.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                10,
                "A number is only flushed when a non-digit follows it, so one at the very end of the text is still waiting in current.",
                False,
            ),
        ],
        predictions=[
            (
                8,
                'For "x7y25z", what are ch and current the second time <code>total += current</code> is reached?',
                "ch = 'y' and current = 7.",
            ),
        ],
        patterns=["Strings"],
        techniques=["Accumulator", "String Methods"],
    ),
    problem(
        slug="count-a-word",
        title="Count a Word",
        topic="string-play",
        difficulty="easy",
        fn="count_word",
        signature="(text: str, word: str) -> int",
        description=html(
            'Count how many times <code>word</code> appears in <code>text</code> as a whole word. Words are separated by whitespace and matching is case-sensitive, so <code>"concat"</code> does not contain the word <code>"cat"</code>.',
        ),
        examples=[
            (
                'text = "hello world hello", word = "hello"',
                "2",
                "The word appears at positions 1 and 3",
            ),
        ],
        constraints=["0 <= len(text) <= 10^5", "word has no spaces"],
        todo="Split the text into words and count the ones equal to word.",
        solution="""
            def count_word(text: str, word: str) -> int:
                count = 0
                for token in text.split():
                    if token == word:
                        count += 1
                return count
        """,
        trace=1,
        cases=[
            ('"hello world hello", "hello"', "2", False),
            ('"to be or not to be", "be"', "2", False),
            ('"", "a"', "0", True),
            ('"cat concat cat", "cat"', "2", True),
            ('"Go go GO", "go"', "1", True),
            ('"one", "one"', "1", True),
        ],
        hints=(
            "What would <code>text.count(word)</code> get wrong for 'cat' in 'concat'?",
            "Split the text into whole words first.",
            "Loop over <code>text.split()</code> and add 1 whenever <code>token == word</code>.",
        ),
        approaches=[
            (
                "Substring count",
                "<code>text.count(word)</code> also matches inside longer words.",
                "O(n)",
                "O(1)",
                False,
            ),
            ("Split and compare", "Whole-word comparison.", "O(n)", "O(n)", True),
        ],
        notes=[
            (
                3,
                "split() with no argument splits on any run of whitespace, so each token is a whole word; 'concat' can no longer be mistaken for 'cat'.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                'For ("hello world hello", "hello"), what are token and count the second time <code>if token == word</code> is reached?',
                "token = 'world' and count = 1.",
            ),
        ],
        patterns=["Strings", "Hash Map"],
        techniques=["String Methods", "Accumulator"],
    ),
    problem(
        slug="repeated-block-string",
        title="Repeated Block String",
        topic="string-play",
        difficulty="medium",
        fn="is_repeated_block",
        signature="(s: str) -> bool",
        description=html(
            "Return <code>True</code> if <code>s</code> can be built by writing some shorter block of characters two or more times in a row, and <code>False</code> otherwise.",
            'For example <code>"abab"</code> is the block <code>"ab"</code> twice. A single character has no shorter block, so the answer is <code>False</code>.',
        ),
        examples=[
            ('s = "abab"', "True", "The block 'ab' repeated twice"),
        ],
        constraints=["1 <= len(s) <= 10^4"],
        todo="Try each block length that divides len(s) and check whether repeating that prefix rebuilds s.",
        solution="""
            def is_repeated_block(s: str) -> bool:
                n = len(s)
                for size in range(1, n // 2 + 1):
                    if n % size == 0 and s[:size] * (n // size) == s:
                        return True
                return False
        """,
        trace=2,
        cases=[
            ('"abab"', "True", False),
            ('"xyzxyz"', "True", False),
            ('"abcab"', "False", False),
            ('"a"', "False", True),
            ('"aaaa"', "True", True),
            ('"abaababaab"', "True", True),
        ],
        hints=(
            "A repeated block must fit into the string a whole number of times. Which lengths allow that?",
            "Only block lengths up to n // 2 that divide n can work. Compare the repeated prefix with s.",
            "<code>s[:size] * (n // size) == s</code> for any size where <code>n % size == 0</code>.",
        ),
        approaches=[
            (
                "Try every block length",
                "Rebuild the string from each possible prefix.",
                "O(n * d(n))",
                "O(n)",
                True,
            ),
            (
                "Search in the doubled string",
                "s is repeated exactly when it appears inside <code>(s + s)[1:-1]</code>.",
                "O(n)",
                "O(n)",
                False,
            ),
        ],
        notes=[
            (
                4,
                "Only block sizes that divide the length can tile the string; checking n % size first skips the string building for every other size.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                'For "xyzxyz", what is size when <code>return True</code> is reached?',
                "3 (the block is 'xyz').",
            ),
        ],
        patterns=["Strings"],
        techniques=["Slicing", "String Repetition"],
    ),
    problem(
        slug="count-words-in-text",
        title="Count Words in Text",
        topic="string-play",
        difficulty="easy",
        fn="count_words",
        signature="(text: str) -> int",
        description=html(
            "Return how many words <code>text</code> contains. A word is a maximal run of non-whitespace characters, so extra spaces, tabs and newlines never create extra words.",
        ),
        examples=[
            ('text = "Hello world"', "2", "Two words"),
        ],
        constraints=["0 <= len(text) <= 10^5"],
        todo="Count each place where a word starts: a non-space right after a space (or at the start).",
        solution="""
            def count_words(text: str) -> int:
                count = 0
                in_word = False
                for ch in text:
                    if not ch.isspace() and not in_word:
                        count += 1
                    in_word = not ch.isspace()
                return count
        """,
        trace=1,
        cases=[
            ('"Hello world"', "2", False),
            ('"  many   spaces here "', "3", False),
            ('""', "0", True),
            ('"   "', "0", True),
            ('"one"', "1", True),
            ('"a\\tb\\nc"', "3", True),
        ],
        hints=(
            "What distinguishes the first letter of a word from the others?",
            "A word starts where a non-space follows a space or the start. Remember whether the previous character was inside a word.",
            "Add 1 when <code>not ch.isspace() and not in_word</code>, then update <code>in_word</code>.",
        ),
        approaches=[
            (
                "split()",
                "<code>len(text.split())</code> does the job in one call.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Count word starts",
                "One pass with a flag; no list is built.",
                "O(n)",
                "O(1)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "A word starts exactly where a non-space follows a space (or the start); in_word remembers what the previous character was.",
                False,
            ),
        ],
        predictions=[
            (
                6,
                'For "Hello world", which character is ch the second time <code>count += 1</code> is reached?',
                "'w', the first letter of 'world'.",
            ),
        ],
        patterns=["Strings"],
        techniques=["State Flag", "String Methods"],
    ),
    problem(
        slug="anagram-pairs",
        title="Anagram Pairs",
        topic="string-play",
        difficulty="medium",
        fn="anagram_pairs",
        signature="(words: list[str]) -> list[list[str]]",
        description=html(
            "Two words are anagrams if they use exactly the same letters the same number of times. Return every pair <code>[words[i], words[j]]</code> with <code>i < j</code> whose words are anagrams, ordered by <code>i</code> and then <code>j</code>.",
            "Identical words at different positions count as an anagram pair.",
        ),
        examples=[
            (
                'words = ["listen", "silent", "hello", "world"]',
                '[["listen", "silent"]]',
                "Only 'listen' and 'silent' share the same letters",
            ),
        ],
        constraints=["0 <= len(words) <= 500", "Words are lowercase letters"],
        todo="Give each word a key (its sorted letters) and compare keys for every pair i < j.",
        solution="""
            def anagram_pairs(words: list[str]) -> list[list[str]]:
                keys = [sorted(w) for w in words]
                pairs = []
                for i in range(len(words)):
                    for j in range(i + 1, len(words)):
                        if keys[i] == keys[j]:
                            pairs.append([words[i], words[j]])
                return pairs
        """,
        trace=2,
        cases=[
            ('["listen", "silent", "hello", "world"]', '[["listen", "silent"]]', False),
            (
                '["rat", "art", "tar"]',
                '[["rat", "art"], ["rat", "tar"], ["art", "tar"]]',
                False,
            ),
            ("[]", "[]", True),
            ('["a"]', "[]", True),
            ('["ab", "ba", "ab"]', '[["ab", "ba"], ["ab", "ab"], ["ba", "ab"]]', True),
            ('["abc", "abd"]', "[]", True),
        ],
        hints=(
            "What do two anagrams have in common once their letters are sorted?",
            "Precompute each word's sorted letters, then compare those keys.",
            "Loop i over words and j from i + 1 so every unordered pair is seen once.",
        ),
        approaches=[
            (
                "Sort inside the pair loop",
                "Sort both words for every pair.",
                "O(n^2 * k log k)",
                "O(k)",
                False,
            ),
            (
                "Precompute keys",
                "Sort each word once, then compare keys.",
                "O(n * k log k + n^2)",
                "O(n * k)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Starting j at i + 1 visits every unordered pair exactly once and never pairs a word with itself.",
                False,
            ),
        ],
        predictions=[
            (
                7,
                'For ["rat", "art", "tar"], what are i and j the second time <code>pairs.append(...)</code> is reached?',
                "i = 0 and j = 2 (the pair 'rat' and 'tar').",
            ),
        ],
        patterns=["Sorting", "Hash Map"],
        techniques=["Precomputed Keys", "Nested Loops"],
    ),
    problem(
        slug="character-frequency",
        title="Character Frequency",
        topic="string-play",
        difficulty="easy",
        fn="char_frequency",
        signature="(s: str) -> dict[str, int]",
        description=html(
            "Return a dictionary that maps each character of <code>s</code> to the number of times it occurs. Case matters and spaces count as characters. Key order does not matter.",
        ),
        examples=[
            (
                's = "hello"',
                "{'h': 1, 'e': 1, 'l': 2, 'o': 1}",
                "'l' occurs twice, the others once",
            ),
        ],
        constraints=["0 <= len(s) <= 10^5"],
        todo="Walk through the string and bump a counter in a dictionary for each character.",
        solution="""
            def char_frequency(s: str) -> dict[str, int]:
                counts = {}
                for ch in s:
                    counts[ch] = counts.get(ch, 0) + 1
                return counts
        """,
        trace=1,
        cases=[
            ('"hello"', "{'h': 1, 'e': 1, 'l': 2, 'o': 1}", False),
            ('"banana"', "{'b': 1, 'a': 3, 'n': 2}", False),
            ('""', "{}", True),
            ('"aaa"', "{'a': 3}", True),
            ('"a b a"', "{'a': 2, ' ': 2, 'b': 1}", True),
            ('"Aa"', "{'A': 1, 'a': 1}", True),
        ],
        hints=(
            "A dictionary can hold one counter per character. What if the character has not been seen yet?",
            "<code>counts.get(ch, 0)</code> returns 0 when ch is missing.",
            "<code>counts[ch] = counts.get(ch, 0) + 1</code> for each character.",
        ),
        approaches=[
            (
                "collections.Counter",
                "<code>dict(Counter(s))</code> does it in one call.",
                "O(n)",
                "O(k)",
                False,
            ),
            (
                "Counting with dict.get",
                "One pass, one dictionary update per character.",
                "O(n)",
                "O(k)",
                True,
            ),
        ],
        notes=[
            (
                4,
                "get(ch, 0) supplies 0 the first time a character appears, so no separate 'is it in the dictionary yet' branch is needed.",
                False,
            ),
        ],
        predictions=[
            (
                4,
                "For \"hello\", what is counts['l'] on the fourth arrival at <code>counts[ch] = ...</code> (the second 'l'), before the line runs?",
                "1.",
            ),
        ],
        patterns=["Hash Map"],
        techniques=["Dict Counting"],
    ),
    problem(
        slug="longest-word-length",
        title="Longest Word Length",
        topic="string-play",
        difficulty="easy",
        fn="longest_word_length",
        signature="(text: str) -> int",
        description=html(
            "Words are separated by whitespace. Return the length of the longest word in <code>text</code>, or 0 if there are no words.",
        ),
        examples=[
            ('text = "Find the longest word"', "7", "'longest' has 7 letters"),
        ],
        constraints=["0 <= len(text) <= 10^5"],
        todo="Split into words and keep the largest length seen.",
        solution="""
            def longest_word_length(text: str) -> int:
                longest = 0
                for word in text.split():
                    if len(word) > longest:
                        longest = len(word)
                return longest
        """,
        trace=1,
        cases=[
            ('"Find the longest word"', "7", False),
            ('"a bb ccc bb"', "3", False),
            ('""', "0", True),
            ('"   "', "0", True),
            ('"supercalifragilistic"', "20", True),
            ('"ab cd ef"', "2", True),
        ],
        hints=(
            "You only need a number, not the word itself. What should you remember while scanning?",
            "Split the text, then compare each word's length with the best length so far.",
            "Start <code>longest</code> at 0 and set it to <code>len(word)</code> when that is larger.",
        ),
        approaches=[
            (
                "max over lengths",
                "<code>max(map(len, text.split()), default=0)</code>.",
                "O(n)",
                "O(n)",
                False,
            ),
            (
                "Running maximum",
                "One pass keeping the best length.",
                "O(n)",
                "O(n)",
                True,
            ),
        ],
        notes=[
            (
                5,
                "Only the best length so far is stored, since the answer is a number and not the word itself.",
                False,
            ),
        ],
        predictions=[
            (
                5,
                "For \"Find the longest word\", what is longest just before <code>longest = len(word)</code> runs the second time (word = 'longest')?",
                "4, from 'Find'; it is about to become 7.",
            ),
        ],
        patterns=["Strings"],
        techniques=["Running Maximum", "String Methods"],
    ),
]
