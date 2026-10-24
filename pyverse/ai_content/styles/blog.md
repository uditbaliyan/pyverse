# PyVerse blog style guide

Prepended to every blog post generation. Tone and conventions only — the JSON
shape is in the schema that follows this file.

## What the blog is for

Longer-form explanations of the things that trip people up while learning
Python. Every post is one idea, taught with a runnable snippet and checked
against something the reader can do next. The posture is "here is the thing I
wish I had known", not "here is the documentation".

## Voice

- Second person, present tense, plain words. Address the reader as someone who
  has written a little Python and is now confused by something specific.
- Short paragraphs — two or three sentences. A post of 400-700 words.
- No throat-clearing opener. The first sentence states the problem, not the
  topic: "When you learn Python from a tutorial, every example ends with
  `print`." is good; "In this post we will explore the print function." is not.
- No headings before the second paragraph; no "Conclusion" section.
- Close with the next thing to do, ideally a link to an existing practice
  problem (`/practice/problem/<slug>/`), lesson or quiz.

## Markdown

- `##` for sections, `###` only if a section genuinely has two halves. Never a
  `#` heading — the title is already one.
- Fenced code blocks with a language tag. Snippets are short (under 15 lines)
  and must run as written.
- `code` for identifiers, values and function names. Bold for the single claim
  the post rests on, at most once or twice in the whole post.
- No tables, no HTML, no horizontal rules, no images, no emoji.

## Claims

- Only state things that are true of Python as it actually behaves. If a
  statement is about a specific version or a CPython detail, say so.
- Prefer one concrete example over three abstract ones, and show the mistake
  before the fix: wrong output first, then the correction, then why.
- Do not invent PyVerse URLs. `/practice/problem/<slug>/` is the shape; if you
  are not certain a problem exists, point at the practice hub (`/practice/`)
  instead.
- Do not write about PyVerse itself, pricing, courses or anything site-specific
  beyond the closing link.

## Excerpt and tags

- `excerpt` is one HTML `<p>` of at most two sentences, phrased as the reader's
  problem. It appears in listings, so it has to stand alone without the title.
- Tags: two to five short nouns or noun phrases ("Return values", "Dicts",
  "Loop bugs"). Title case, no `#`, no sentence-length tags.

## Good and bad

Bad opening: "Python is a versatile language used across many domains. In this
post we will look at return values."

Good opening: "When you learn Python from a tutorial, every example ends with
`print`. When you solve practice problems, almost none of them should."

Bad explanation: "Simply use `return` instead of `print` to fix the issue."

Good explanation: "`print` writes to the console; `return` hands the value back
to whoever called the function. A test case only ever sees the second one, so a
function that prints its answer returns `None`."

Bad code block (does not run, and hides the point):

    def double(n):
        return n * 2
        print(double(21))

Good code block:

    def double(n):
        return n * 2       # what the grader checks

    print(double(21))      # what you look at
