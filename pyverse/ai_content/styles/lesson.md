# PyVerse lesson style guide

Prepended to every lesson generation. Tone and conventions only — the block
schema is in the schema that follows this file.

## What a lesson is

One step in a course: a single idea, shown with a runnable example and a
warning about the mistake learners actually make. A lesson is read in five to
ten minutes and ends by pointing at something to practise. It is not a
reference page, not a cheat sheet, and never covers two ideas because they are
related.

## Structure, in block order

1. **text** — a `##` heading and one or two short paragraphs naming the idea in
   concrete terms. Never start with a code block; the reader needs to know what
   they are looking at first.
2. **code_example** — the idea in under 15 lines, with a filename and an
   inline comment on the one line that matters.
3. **callout** — one thing that catches people out, phrased as the mistake
   rather than the rule.
4. **text** — a sentence or two inviting the reader to change the example.
5. **mermaid** — only when the lesson describes control flow or a data
   structure that is genuinely easier to see than to read. Otherwise omit it.
6. **text** — a closer pointing at the graded version: a link to an existing
   practice problem (`/practice/problem/<slug>/`) or the next lesson's idea.

Four to eight blocks. Skip `video` and `image` entirely: those need assets a
human supplies.

## Voice

- Second person, present tense, plain words. "You keep a running total", not
  "a running total is maintained".
- Address the reader's likely belief before correcting it.
- No motivational filler, no "as we all know", no exclamation marks.
- American spelling, sentence case in headings.

## HTML in text and callout blocks

- One `##` heading per text block, paragraphs in `<p>`, identifiers and values
  in `<code>`, emphasis in `<em>` where a word carries the point.
- Do not repeat the heading as the first sentence of the paragraph.
- Callout titles are short and concrete ("print is not return"), not labels
  ("Important"). Choose the style that matches the content: `tip` for the
  technique, `warning`/`danger` for a mistake that silently breaks code, `note`
  for a caveat, `info` otherwise.

## Code

- Runs as written, prints something the reader can check, and keeps to the
  vocabulary the lesson has taught so far.
- Show the output as a trailing comment rather than a second code block.
- Filenames are lowercase and describe the example (`greet.py`, `total.py`).

## Good and bad

Bad text block: "<p>Functions are an important concept in Python. In this
lesson we will learn about them.</p>"

Good text block: "<h2>Everything is a value</h2><p>A function takes values in,
does something, and hands a value back with <code>return</code>. That returned
value is what a grader checks — not what the function prints.</p>"

Bad callout: style `info`, title "Remember", body "Use return instead of
print."

Good callout: style `tip`, title "print is not return", body "<p><code>print</code>
shows a value to you. <code>return</code> gives it back to whoever called the
function, which is the only one a grader can see.</p>"

Bad mermaid diagram: a three-node diagram that says "start → example → end".

Good mermaid diagram: the loop and accumulator of the example, showing which
line updates which variable.
