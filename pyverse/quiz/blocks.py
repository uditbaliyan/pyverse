from wagtail import blocks


class FillBlankBlock(blocks.StructBlock):
    code_with_blank = blocks.TextBlock(
        required=True,
        help_text=(
            'The code snippet with a blank placeholder (e.g. "___") marking '
            "where the student must fill in the missing piece."
        ),
    )
    correct_answer = blocks.TextBlock(
        required=True,
        help_text="The exact text that correctly fills the blank. Used verbatim for grading, so keep it precise.",
    )

    class Meta:
        icon = "edit"
        label = "Fill in the Blank"
        template = "quiz/blocks/fill_blank.html"


class ComplexityBlock(blocks.StructBlock):
    code_snippet = blocks.TextBlock(
        required=True,
        help_text="The code snippet whose time complexity the student must identify.",
    )
    correct_complexity = blocks.ChoiceBlock(
        choices=[
            ("O(1)", "O(1)"),
            ("O(log n)", "O(log n)"),
            ("O(n)", "O(n)"),
            ("O(n log n)", "O(n log n)"),
            ("O(n^2)", "O(n^2)"),
        ],
        required=True,
        help_text="The correct Big-O complexity class for the snippet above.",
    )
    explanation = blocks.RichTextBlock(
        required=False,
        help_text="An explanation of why this is the correct complexity, revealed to the student after they answer.",
    )

    class Meta:
        icon = "time"
        label = "Complexity Analysis"
        template = "quiz/blocks/complexity.html"


class BugHuntBlock(blocks.StructBlock):
    buggy_code = blocks.TextBlock(
        required=True,
        help_text="The code snippet containing a single deliberate bug for the student to locate.",
    )
    bug_line_number = blocks.CharBlock(
        required=True,
        max_length=20,
        help_text='The line number of the bug as it appears in buggy_code, e.g. "7".',
    )
    fix_explanation = blocks.RichTextBlock(
        required=False,
        help_text="An explanation of the bug and how to fix it, revealed to the student after they answer.",
    )

    class Meta:
        icon = "warning"
        label = "Bug Hunt"
        template = "quiz/blocks/bug_hunt.html"


class TrueFalseBlock(blocks.StructBlock):
    statement = blocks.TextBlock(
        required=True,
        help_text="The statement the student must judge as true or false.",
    )
    is_true = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Check this box if the statement above is TRUE; leave it unchecked if it is FALSE.",
    )
    explanation = blocks.RichTextBlock(
        required=False,
        help_text="An explanation of why the statement is true or false, revealed to the student after they answer.",
    )

    class Meta:
        icon = "help"
        label = "True or False"
        template = "quiz/blocks/true_false.html"

