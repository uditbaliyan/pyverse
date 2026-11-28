"""
Seed "Programming Basics with Python" into the PyVerse Wagtail LMS.

Install : pyverse/lms/management/commands/seed_python_basics.py
          (needs __init__.py in management/ and management/commands/)
Run     : python manage.py seed_python_basics [--dry-run] [--update] [--draft] [--export DIR]

Tree    : LMSIndexPage -> TrackPage "Python" -> CoursePage -> 18 x LessonPage
Safe    : idempotent (skips existing slugs unless --update), atomic, --dry-run rolls back.
Adapt   : everything repo-specific lives in CONFIG below; first failing field
          is reported by name, fix CONFIG / EXTRA and re-run.
"""

import html
import re
from datetime import timedelta
from pathlib import Path

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.utils.text import slugify
from wagtail.blocks import RichTextBlock, StructBlock
from wagtail.fields import StreamField
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

# ───────────────────────── CONFIG ─────────────────────────
MODELS = {  # class name (any app) or "app_label.ClassName"; index/track optional, course/lesson required
    "index": "LMSIndexPage",
    "track": "TrackPage",
    "course": "CoursePage",
    "lesson": "LessonPage",
}
# first existing model field wins
FIELDS = {
    "summary": ("summary", "intro", "description", "excerpt", "subtitle", "tagline"),
    "body": ("body", "content", "lesson_body", "text"),
    "minutes": (
        "estimated_minutes",
        "duration_minutes",
        "minutes",
        "duration",
        "reading_time",
    ),
    "level": ("level", "difficulty"),
    "kind": ("course_type", "kind", "type"),
}
RICH_BLOCKS = (
    "rich_text",
    "richtext",
    "paragraph",
    "text",
    "html",
    "content",
    "markdown",
)
CODE_BLOCKS = ("code", "code_block", "python", "snippet")
CODE_KEYS, LANG_KEYS = ("code", "source", "text", "content"), ("language", "lang")
# kwargs for required fields this script doesn't know, e.g. {"course": {"order": 1}}
EXTRA = {"index": {}, "track": {}, "course": {}, "lesson": {}}

SITE_TITLE = "PyVerse"
TRACK = ("Python", "python", "Learn Python from first print() to real projects.")
COURSE = dict(
    title="Programming Basics with Python",
    slug="programming-basics-python",
    summary=(
        "Zero to confident beginner: variables, control flow, data structures, functions, "
        "errors, files and modules, finishing with a guessing-game capstone."
    ),
)
COURSE_MD = r"""
A hands-on introduction to programming using Python 3. No prior experience needed: every lesson is a short idea, runnable code, and a practice task.

## What you will learn

- Read and write Python programs line by line
- Store and transform data with variables, strings, lists, tuples, sets and dicts
- Control flow with `if`, `while` and `for`
- Organise code with functions, modules and error handling
- Read and write files and finish with a complete small game

## How to use this course

Type every example yourself, change one thing, and predict the result before running it. Then do the practice task at the end of each lesson without looking back.
"""

# ───────────────────────── CONTENT ─────────────────────────
# (title, minutes, summary, markdown)  - only ```python fences, ## headings, - lists, `code`, **bold**
LESSONS = [
    (
        "Hello, World: How Programs Run",
        15,
        "Write and run your first Python program and learn what print, strings and comments are.",
        r"""
A program is a list of instructions a computer follows from top to bottom. Python reads your file line by line and runs each statement in order.

```python
print("Hello, world!")
print("Python runs me line by line.")
```

`print()` is a **function** that shows text on screen. Text inside quotes is a **string**. Anything after `#` is a comment and is ignored by Python.

```python
# this line does nothing
print(2 + 3)  # 5
```

When something is wrong Python stops and shows a **traceback**. Read the last line first: it names the error and the line number.

## Practice

Print your name, then your favourite number on the next line. Then break the program on purpose (delete a closing quote) and read the error message.
""",
    ),
    (
        "Variables and Data Types",
        20,
        "Name values with variables and meet int, float, str and bool, plus type conversion.",
        r"""
A **variable** is a name that refers to a value. `=` assigns; it does not mean "equals".

```python
age = 21
price = 19.99
name = "Asha"
is_student = True
print(type(age), type(price), type(name), type(is_student))
```

The four core types are `int`, `float`, `str` and `bool`. Use `snake_case` names, no spaces, and never start with a digit. Convert between types with `int()`, `float()` and `str()`.

```python
count = "5"
total = int(count) + 1
print(total)  # 6
```

## Practice

Store your birth year in a variable, compute your age, and print `I am N years old`.
""",
    ),
    (
        "Numbers and Operators",
        20,
        "Arithmetic, floor division, modulo, powers, augmented assignment and float surprises.",
        r"""
Python has `+ - * / // % **`. `/` always gives a float, `//` is floor division, `%` is the remainder.

```python
print(7 / 2)    # 3.5
print(7 // 2)   # 3
print(7 % 2)    # 1
print(2 ** 10)  # 1024
x = 10
x += 5
print(x)        # 15
```

Operator order follows maths: `**`, then `* / // %`, then `+ -`. Use parentheses to be explicit. Floats are binary approximations:

```python
print(0.1 + 0.2)           # 0.30000000000000004
print(round(0.1 + 0.2, 2)) # 0.3
print(divmod(17, 5))       # (3, 2)
```

## Practice

Convert 3725 seconds into hours, minutes and seconds using only `//` and `%`.
""",
    ),
    (
        "Strings",
        25,
        "Index, slice and transform text with string methods; strings are immutable.",
        r"""
A string is a sequence of characters. Index from 0, or from the end with negatives; slice with `[start:stop:step]`.

```python
s = "Python"
print(s[0], s[-1])   # P n
print(s[1:4])        # yth
print(s[::-1])       # nohtyP
print(s.upper(), len(s))
```

Common methods return **new** strings, because strings cannot be changed in place.

```python
print("  hi  ".strip())
print("a,b,c".split(","))
print("-".join(["x", "y"]))
print("banana".replace("a", "o"))
print("py" in "python")  # True
```

## Practice

Turn `"  Hello, World  "` into `"dlrow olleh"` using strip, lower, replace and a slice.
""",
    ),
    (
        "Input and Formatted Output",
        20,
        "Read user input and build output with f-strings and format specifiers.",
        r"""
`input()` shows a prompt and always returns a **string**. Convert it before doing maths.

```python
name = input("Name? ")
age = int(input("Age? "))
print(f"{name} will be {age + 1} next year")
```

An **f-string** evaluates expressions inside `{}`. Add a format spec after a colon.

```python
pi = 3.14159
print(f"{pi:.2f}")       # 3.14
print(f"{1234567:,}")    # 1,234,567
print(f"{7:03d}")        # 007
print(f"{'left':<8}|")   # left    |
```

## Practice

Ask for a bill amount and a tip percentage, then print the tip and total to 2 decimals.
""",
    ),
    (
        "Booleans and Comparisons",
        20,
        "Compare values, combine conditions with and/or/not, and learn truthiness.",
        r"""
Comparisons produce `True` or `False`: `== != < <= > >=`. Combine with `and`, `or`, `not`. Python allows chained comparisons.

```python
x = 7
print(x > 3 and x < 10)  # True
print(3 < x < 10)        # True
print(not x == 7)        # False
```

`==` compares; `=` assigns. Every value has a **truthiness**: zero, empty containers, `""` and `None` are falsy, everything else is truthy.

```python
print(bool(0), bool(""), bool([]), bool("0"))  # False False False True
```

## Practice

Write one expression that is `True` for leap years (divisible by 4, except centuries unless divisible by 400). Test 1900, 2000 and 2024.
""",
    ),
    (
        "Conditionals: if, elif, else",
        20,
        "Branch your program with if/elif/else and conditional expressions.",
        r"""
Indentation is part of Python's syntax: the indented block runs only when the condition holds. Conditions are checked top to bottom and the first match wins.

```python
score = 72
if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "F"
print(grade)  # C
```

For a simple choice between two values use a conditional expression.

```python
n = 8
label = "even" if n % 2 == 0 else "odd"
print(label)
```

## Practice

Read a number. Print `FizzBuzz` if divisible by 3 and 5, `Fizz` if by 3, `Buzz` if by 5, otherwise the number.
""",
    ),
    (
        "while Loops",
        20,
        "Repeat work while a condition holds, with break and continue.",
        r"""
A `while` loop repeats as long as its condition is true. Make sure something inside changes the condition, or it never ends.

```python
n = 5
while n > 0:
    print(n)
    n -= 1
print("liftoff")
```

`break` leaves the loop; `continue` skips to the next iteration. `while True` plus `break` is the standard way to keep asking until input is valid.

```python
while True:
    text = input("Type q to quit: ")
    if text == "q":
        break
    print("you typed", text)
```

## Practice

Sum the digits of a positive integer using `while`, `%` and `//` (1234 gives 10).
""",
    ),
    (
        "for Loops and range()",
        25,
        "Iterate over sequences, use range and enumerate, and nest loops.",
        r"""
`for` walks over any iterable. `range(start, stop, step)` generates numbers and excludes `stop`.

```python
for i in range(3):
    print(i)             # 0 1 2
for ch in "abc":
    print(ch)
for i in range(2, 10, 3):
    print(i)             # 2 5 8
for i, ch in enumerate("hey", start=1):
    print(i, ch)
```

Loops can nest; the inner loop runs fully for every step of the outer one.

```python
for row in range(1, 4):
    for col in range(1, 4):
        print(row * col, end=" ")
    print()
```

## Practice

Print the multiplication table of a number, then a right triangle of stars with a given height.
""",
    ),
    (
        "Lists",
        30,
        "Store ordered, mutable collections; slice, mutate, sort and build lists with comprehensions.",
        r"""
Lists are ordered and **mutable**.

```python
nums = [3, 1, 2]
nums.append(5)
nums.insert(0, 9)
nums.remove(1)
print(nums)                    # [9, 3, 2, 5]
print(sorted(nums), nums[1:3], len(nums))
```

A **list comprehension** builds a list in one expression.

```python
squares = [n * n for n in range(5)]
evens = [n for n in range(10) if n % 2 == 0]
print(squares, evens)
```

Assignment never copies a list; two names can point at the same one.

```python
a = [1, 2]
b = a
b.append(3)
print(a)         # [1, 2, 3]
c = a.copy()
```

## Practice

Find the largest and the second largest value in a list without using `max()` or `sorted()`.
""",
    ),
    (
        "Tuples and Sets",
        20,
        "Use immutable tuples, unpacking, and sets for uniqueness and fast membership.",
        r"""
A **tuple** is an immutable sequence, good for fixed groups of values. **Unpacking** splits one into names.

```python
point = (3, 4)
x, y = point
a, b = 1, 2
a, b = b, a        # swap
print(x, y, a, b)
```

A **set** holds unique, unordered items and supports maths-style operations and fast `in` checks.

```python
seen = {1, 2, 2, 3}
print(seen)                              # {1, 2, 3}
print({1, 2} | {2, 3}, {1, 2} & {2, 3}, {1, 2} - {2, 3})
print(2 in seen)
```

## Practice

Remove duplicates from a list while keeping the original order.
""",
    ),
    (
        "Dictionaries",
        30,
        "Map keys to values, iterate with items(), and count things.",
        r"""
A **dict** maps keys to values. Lookups are fast; keys must be immutable.

```python
user = {"name": "Asha", "age": 21}
user["city"] = "Delhi"
print(user.get("email", "n/a"))
for key, value in user.items():
    print(key, value)
```

Counting is the classic dict pattern.

```python
counts = {}
for ch in "banana":
    counts[ch] = counts.get(ch, 0) + 1
print(counts)   # {'b': 1, 'a': 3, 'n': 2}
```

`user["email"]` raises `KeyError` for a missing key; `.get()` returns a default instead.

## Practice

Count word frequencies in a sentence and print the most common word.
""",
    ),
    (
        "Functions",
        30,
        "Define reusable code with parameters, defaults, return values and docstrings.",
        r"""
A function packages code under a name. `return` sends a value back; without it a function returns `None`.

```python
def greet(name, punctuation="!"):
    return f"Hello, {name}{punctuation}"

print(greet("Asha"))
print(greet("Asha", punctuation="?"))
```

Return several values as a tuple and unpack them.

```python
def stats(nums):
    return min(nums), max(nums), sum(nums) / len(nums)

lo, hi, avg = stats([4, 8, 6])
print(lo, hi, avg)
```

Keep functions small, name them as verbs, and do one thing each.

## Practice

Write `is_prime(n)`, then `primes_up_to(n)` that reuses it.
""",
    ),
    (
        "Scope and Common Function Pitfalls",
        20,
        "Understand local vs global names and the mutable default argument trap.",
        r"""
Names assigned inside a function are **local**; they do not change globals of the same name.

```python
total = 0

def add(n):
    total = n       # new local variable

add(5)
print(total)        # 0
```

Default values are created **once**, when the function is defined. A mutable default is shared across calls.

```python
def bad(item, bucket=[]):
    bucket.append(item)
    return bucket

print(bad(1), bad(2))   # [1, 2] [1, 2]

def good(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

## Practice

Predict the output of `print(good(1), good(2))` and of `print(bad(3))` after the lines above, then run to check.
""",
    ),
    (
        "Errors and Exceptions",
        25,
        "Handle failures with try/except/else/finally and raise your own errors.",
        r"""
Exceptions signal that something went wrong. Catch **specific** exceptions you can handle.

```python
try:
    n = int(input("Number: "))
    print(10 / n)
except ValueError:
    print("not a number")
except ZeroDivisionError:
    print("cannot divide by zero")
else:
    print("ok")
finally:
    print("done")
```

`else` runs only when nothing was raised; `finally` always runs. Raise your own when input breaks a rule.

```python
def set_age(age):
    if age < 0:
        raise ValueError("age must be >= 0")
    return age
```

Avoid a bare `except:`; it hides bugs.

## Practice

Write `ask_int(prompt)` that keeps asking until the user enters a valid integer.
""",
    ),
    (
        "Working with Files",
        25,
        "Read and write text files with open() and pathlib.",
        r"""
Always open files with `with`, which closes them for you. Modes: `r` read, `w` write (overwrites), `a` append.

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("line 1\nline 2\n")

with open("notes.txt", encoding="utf-8") as f:
    for line in f:
        print(line.rstrip())
```

`pathlib` gives a tidier API for simple cases.

```python
from pathlib import Path

p = Path("notes.txt")
print(p.read_text(encoding="utf-8").splitlines())
print(p.exists(), p.suffix)
```

In the PyVerse browser labs the file system is virtual and resets on reload.

## Practice

Write a function that returns the number of lines and words in a text file.
""",
    ),
    (
        "Modules and the Standard Library",
        20,
        "Import code, use math, random and datetime, and write your own module.",
        r"""
A **module** is a `.py` file. `import` makes its names available.

```python
import math
import random
from datetime import date

print(math.sqrt(16), math.pi)
print(random.choice(["a", "b"]), random.randint(1, 6))
print(date.today().year)
```

Your own file works the same way. Guard script-only code so importing does not run it.

```python
def main():
    print("running as a script")

if __name__ == "__main__":
    main()
```

Third-party packages install with `pip` inside a virtual environment: `python -m venv .venv`.

## Practice

Create `dice.py` with `roll(sides=6)` and import it from a second file to roll three dice.
""",
    ),
    (
        "Capstone: Number Guessing Game",
        40,
        "Combine loops, conditionals, input, functions, errors and files in one project.",
        r"""
Time to combine everything. This is the minimal version; read it, run it, then improve it.

```python
import random

secret = random.randint(1, 100)
tries = 0
while True:
    guess = int(input("Guess 1-100: "))
    tries += 1
    if guess < secret:
        print("higher")
    elif guess > secret:
        print("lower")
    else:
        print(f"Got it in {tries} tries")
        break
```

## Practice

Extend it step by step:

- Validate input with `try/except` so letters do not crash the game
- Limit the player to 7 attempts
- Wrap the game in `play()` and add a replay loop
- Save the best score to a file and show it at start
""",
    ),
]


# ───────────────────────── MARKDOWN → SEGMENTS ─────────────────────────
_CODE, _B = re.compile(r"`([^`]+)`"), re.compile(r"\*\*([^*]+)\*\*")


def _inline(s):
    return _B.sub(
        r"<b>\1</b>", _CODE.sub(r"<code>\1</code>", html.escape(s, quote=False))
    )


def parse(md):
    """-> [("html", str) | ("code", str)], adjacent html merged."""
    segs = []
    for i, part in enumerate(
        re.split(r"```python\n(.*?)```", md.strip("\n"), flags=re.S)
    ):
        if i % 2:
            segs.append(("code", part.rstrip("\n")))
            continue
        for blk in re.split(r"\n\s*\n", part.strip()):
            blk = blk.strip()
            if not blk:
                continue
            if blk.startswith("## "):
                h = f"<h2>{_inline(blk[3:])}</h2>"
            elif blk.startswith("- "):
                h = (
                    "<ul>"
                    + "".join(f"<li>{_inline(l[2:])}</li>" for l in blk.splitlines())
                    + "</ul>"
                )
            else:
                h = f"<p>{_inline(' '.join(blk.split()))}</p>"
            if segs and segs[-1][0] == "html":
                segs[-1] = ("html", segs[-1][1] + h)
            else:
                segs.append(("html", h))
    return segs


def _pre(code):
    return f'<pre><code class="language-python">{html.escape(code)}</code></pre>'


# ───────────────────────── MODEL HELPERS ─────────────────────────
def _field(model, names):
    for n in names:
        try:
            return model._meta.get_field(n)
        except FieldDoesNotExist:
            continue


def _set(obj, key, value):
    """Set first matching field; handles choices, ints, durations, max_length."""
    f = _field(type(obj), FIELDS[key])
    if f is None or f.is_relation:
        return False
    vals = value if isinstance(value, tuple) else (value,)
    if getattr(f, "choices", None):
        want = [str(v).lower() for v in vals]
        hit = next(
            (
                k
                for k, lab in f.flatchoices
                if str(k).lower() in want or str(lab).lower() in want
            ),
            None,
        )
        if hit is None:
            return False
        value = hit
    else:
        value = vals[0]
        if isinstance(f, models.DurationField):
            value = timedelta(minutes=value)
        elif isinstance(f, models.CharField) and f.max_length:
            value = str(value)[: f.max_length]
    setattr(obj, f.name, value)
    return True


def _code_value(block, code):
    if isinstance(block, StructBlock):
        d = {n: code for n in block.child_blocks if n in CODE_KEYS}
        d.update({n: "python" for n in block.child_blocks if n in LANG_KEYS})
        return block.to_python(d)
    return code


def _set_body(page, segs, required=True):
    f = _field(type(page), FIELDS["body"])
    if f is None:
        if not required:
            return False
        have = [
            x.name
            for x in type(page)._meta.get_fields()
            if getattr(x, "concrete", False) and not x.is_relation
        ]
        raise CommandError(
            f"{type(page).__name__}: no body field among {FIELDS['body']}; "
            f"add the right name to FIELDS['body']. Fields on model: {have}"
        )
    if not isinstance(f, StreamField):
        setattr(page, f.name, "".join(v if k == "html" else _pre(v) for k, v in segs))
        return
    blocks = f.stream_block.child_blocks
    rb = next((b for b in RICH_BLOCKS if b in blocks), None)
    if rb is None:
        raise CommandError(
            f"{type(page).__name__}.{f.name}: no rich-text block in {list(blocks)}; edit RICH_BLOCKS"
        )
    cb = next((b for b in CODE_BLOCKS if b in blocks), None)
    out = []
    for kind, val in segs:
        if kind == "code" and cb:
            out.append((cb, _code_value(blocks[cb], val)))
            continue
        h = val if kind == "html" else _pre(val)
        out.append((rb, RichText(h) if isinstance(blocks[rb], RichTextBlock) else h))
    setattr(page, f.name, out)


# ───────────────────────── COMMAND ─────────────────────────
class Command(BaseCommand):
    help = "Create the 'Programming Basics with Python' course (track, course, 18 lessons)."

    def add_arguments(self, p):
        p.add_argument(
            "--dry-run", action="store_true", help="run everything, then roll back"
        )
        p.add_argument(
            "--update",
            action="store_true",
            help="overwrite pages whose slug already exists",
        )
        p.add_argument("--draft", action="store_true", help="leave pages unpublished")
        p.add_argument(
            "--export",
            metavar="DIR",
            help="also write lessons as markdown files to DIR",
        )

    @staticmethod
    def _page_models():
        return [m for m in apps.get_models() if issubclass(m, Page) and m is not Page]

    def _resolve(self, name):
        if "." in name:
            try:
                return apps.get_model(name)
            except LookupError:
                return None
        return next(
            (m for m in self._page_models() if m.__name__.lower() == name.lower()), None
        )

    def handle(self, *a, dry_run, update, draft, export, **kw):
        self.m = {k: self._resolve(v) for k, v in MODELS.items()}
        missing = [k for k in ("course", "lesson") if self.m[k] is None]
        if missing:
            avail = "\n".join(
                f"  {m._meta.label}  (parents: {[p.__name__ for p in m.allowed_parent_page_models()]})"
                for m in self._page_models()
            )
            raise CommandError(
                f"no page model for {missing}. Set MODELS to one of:\n{avail}"
            )
        for k in ("index", "track"):
            if self.m[k] is None:
                self.stdout.write(f"  note: no {k} model, skipping that level")
        self.update, self.publish, self.stats = (
            update,
            not draft,
            dict(created=0, updated=0, skipped=0),
        )
        try:
            with transaction.atomic():
                self.seed()
                if dry_run:
                    transaction.set_rollback(True)
        except ValidationError as e:
            raise CommandError(
                f"validation failed: {getattr(e, 'message_dict', e)} -> set it via EXTRA"
            )
        if export:
            self.export(Path(export))
        tag = " (dry-run, rolled back)" if dry_run else ""
        self.stdout.write(self.style.SUCCESS(f"done{tag}: {self.stats}"))

    def seed(self):
        site = Site.objects.filter(is_default_site=True).first()
        parent = site.root_page if site else Page.get_first_root_node()
        if self.m["index"]:
            index = self.m["index"].objects.first()
            if index is None:
                index = self._upsert(
                    parent,
                    "index",
                    "Learn",
                    "learn",
                    {},
                    None,
                    "Learn Python and more on PyVerse.",
                )
            parent = index
        if self.m["track"]:
            parent = self._upsert(
                parent, "track", TRACK[0], TRACK[1], {}, None, TRACK[2]
            )
        total = sum(l[1] for l in LESSONS)
        course = self._upsert(
            parent,
            "course",
            COURSE["title"],
            COURSE["slug"],
            {
                "summary": COURSE["summary"],
                "level": ("beginner", "intro", "easy"),
                "kind": ("course",),
                "minutes": total,
            },
            parse(COURSE_MD),
            COURSE["summary"],
        )
        for title, mins, summ, md in LESSONS:
            self._upsert(
                course,
                "lesson",
                title,
                slugify(title),
                {"summary": summ, "minutes": mins},
                parse(md),
                summ,
                seo=f"{title} | {COURSE['title']}",
            )

    def _upsert(self, parent, key, title, slug, fields, segs, desc, seo=None):
        Model = self.m[key]
        existing = parent.get_children().filter(slug=slug).first()
        if existing and not self.update:
            self.stats["skipped"] += 1
            self.stdout.write(f"  skip    {key:6} {slug}")
            return existing.specific
        page = (
            existing.specific
            if existing
            else Model(title=title, slug=slug, **EXTRA[key])
        )
        page.title = title
        page.search_description = desc[:255]
        if seo:
            page.seo_title = seo[:255]
        for k, v in fields.items():
            _set(page, k, v)
        if segs:
            _set_body(page, segs, required=(key == "lesson"))
        if existing:
            page.save()
            self.stats["updated"] += 1
        else:
            page.live = self.publish
            parent.add_child(instance=page)
            self.stats["created"] += 1
        rev = page.save_revision()
        if self.publish:
            rev.publish()
        self.stdout.write(f"  {'update' if existing else 'create'}  {key:6} {slug}")
        return page

    def export(self, out):
        out.mkdir(parents=True, exist_ok=True)
        for i, (title, mins, summ, md) in enumerate(LESSONS, 1):
            fm = f'---\ntitle: "{title}"\nminutes: {mins}\nsummary: "{summ}"\n---\n'
            (out / f"{i:02d}-{slugify(title)}.md").write_text(
                fm + md.strip("\n") + "\n", encoding="utf-8"
            )
        (out / "00-course.md").write_text(
            f'---\ntitle: "{COURSE["title"]}"\nsummary: "{COURSE["summary"]}"\n---\n'
            + COURSE_MD.strip("\n")
            + "\n",
            encoding="utf-8",
        )
        self.stdout.write(f"exported {len(LESSONS) + 1} files -> {out}")
