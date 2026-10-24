"""``manage.py ai_create`` — one menu, then a free-text description.

One entrypoint rather than a command per content type with its own flags: the
interesting part (what the model is asked for, what is checked before saving)
differs per type, the interaction should not.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Any

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from pyverse.ai_content.exceptions import GenerationError
from pyverse.ai_content.generators import GENERATORS

if TYPE_CHECKING:
    from pyverse.ai_content.generators.base import Generator


class Command(BaseCommand):
    help = "Draft a problem, blog post, lesson or quiz with a language model."

    # Lets tests drive the menu with call_command(..., stdin=StringIO(...)).
    stealth_options = ("stdin",)

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdin = options.get("stdin", sys.stdin)

        generator = self._choose()
        parent = self._choose_parent(generator)
        description = self._ask("Describe it: ")
        if not description:
            message = "Nothing to generate from."
            raise CommandError(message)

        self.stdout.write("Generating...")
        try:
            draft = generator.run(description, parent=parent, report=self.stdout.write)
        except GenerationError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(f'✓ Draft ready: {draft.label} "{draft.title}"')
        self.stdout.write(f"  Review at {draft.review_url}")
        for note in draft.notes:
            self.stdout.write(f"  · {note}")

    def _choose(self) -> Generator:
        options = [generator() for generator in GENERATORS]
        self.stdout.write("What are we creating?")
        for index, option in enumerate(options, start=1):
            self.stdout.write(f"  {index}) {option.menu_label}")

        while True:
            answer = self._ask("> ").casefold()
            for index, option in enumerate(options, start=1):
                if answer in {str(index), option.slug, option.menu_label.casefold()}:
                    return option
            self.stdout.write(f"Pick 1-{len(options)}, or type a name.")

    def _choose_parent(self, generator: Generator) -> Any:
        """Where the draft hangs, for types that are not standalone snippets."""
        target = generator.parent_queryset()
        if target is None:
            return None

        label, queryset = target
        options = list(queryset)
        if not options:
            message = (
                f"There is no {label} to attach a {generator.menu_label.lower()} "
                "to — create one in /cms/ first."
            )
            raise CommandError(message)
        if len(options) == 1:
            self.stdout.write(f"{label}: {options[0].title}")
            return options[0]

        self.stdout.write(f"Which {label}?")
        for index, option in enumerate(options, start=1):
            self.stdout.write(f"  {index}) {option.title}")
        while True:
            answer = self._ask("> ")
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                return options[int(answer) - 1]
            self.stdout.write(f"Pick 1-{len(options)}.")

    def _ask(self, prompt: str) -> str:
        self.stdout.write(prompt, ending="")
        answer = self.stdin.readline()
        if not answer:
            message = "No answer given — nothing to do."
            raise CommandError(message)
        return answer.strip()
