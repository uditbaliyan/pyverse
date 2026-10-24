"""What every content type's generator has in common.

A generator turns one free-text description into one saved, unpublished draft.
The shape is fixed — ``generate(style_prompt, description)`` for the model call,
``pre_create`` for checks that must pass before anything is written, ``create``
for the Wagtail side — so the menu, the style-guide loading and the refusal
handling are written once.

The field *schema* lives in Python, next to the ``create`` that consumes it,
because it mirrors model fields that must not drift. Tone, formatting and
examples live in ``styles/*.md`` instead, where they can be tuned without a code
change.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import ClassVar

from pyverse.ai_content.exceptions import GenerationError
from pyverse.ai_content.llm import generate_json

STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"

#: How a generator narrates itself: the command prints, tests collect.
Report = Callable[[str], None]


def _silent(_message: str) -> None:
    """Default reporter for callers that do not want progress output."""


@dataclass(frozen=True)
class Draft:
    """A saved, unpublished draft, plus how to review it."""

    label: str
    title: str
    review_url: str
    notes: tuple[str, ...] = field(default=())


class Generator(ABC):
    """One content type: generate JSON, check it, build the draft."""

    #: Menu key and identity.
    slug: ClassVar[str]
    #: How the menu names this type, e.g. "DSA problem".
    menu_label: ClassVar[str]
    #: What the CLI calls the created object, e.g. "CodingProblem".
    label: ClassVar[str]
    #: Markdown style guide prepended to every call.
    style_file: ClassVar[str]
    #: Field-by-field description of the JSON the model must return, when it is
    #: a constant. Anything that depends on the database overrides
    #: :meth:`build_schema` instead.
    schema: ClassVar[str] = ""
    #: Reminders printed after creation — the parts a human must still check.
    review_notes: ClassVar[tuple[str, ...]] = ()

    def run(
        self,
        description: str,
        *,
        parent: Any = None,
        report: Report = _silent,
    ) -> Draft:
        data = self.generate(self.style_prompt(), description)
        self.pre_create(data, report)
        return self.create(data, parent)

    def style_prompt(self) -> str:
        return (STYLES_DIR / self.style_file).read_text(encoding="utf-8")

    def build_schema(self) -> str:
        return self.schema

    def generate(self, style_prompt: str, description: str) -> dict[str, Any]:
        return generate_json(
            style_prompt=style_prompt,
            schema=self.build_schema(),
            description=description,
        )

    def parent_queryset(self) -> tuple[str, Any] | None:
        """Where this type has to be attached, as ``(label, queryset)``.

        ``None`` for the standalone types — snippets, which are reviewed on
        their own and attached to a topic afterwards.
        """
        return None

    # A no-op by default: most content types have nothing that can be checked
    # mechanically. DsaGenerator is the exception.
    def pre_create(  # noqa: B027 - deliberately optional hook, not abstract
        self,
        data: dict[str, Any],
        report: Report,
    ) -> None:
        """Refuse unusable generation before anything is written to the DB."""

    @abstractmethod
    def create(self, data: dict[str, Any], parent: Any) -> Draft:
        """Build and save the draft, then say where to review it."""


# ── Reading the model's JSON ─────────────────────────────────────────────
# Every failure below names the field: the only person who reads these messages
# is the person who can fix the style guide or the schema.


def required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        message = f"the model returned no usable {key!r}"
        raise GenerationError(message)
    return value.strip()


def optional_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    return value.strip() if isinstance(value, str) else ""


def choice(
    data: dict[str, Any],
    key: str,
    allowed: list[str],
    *,
    default: str = "",
) -> str:
    value = data.get(key)
    value = value.strip().lower() if isinstance(value, str) else ""
    if value in allowed:
        return value
    if not value and default:
        return default
    options = ", ".join(allowed)
    message = f"the model returned {key}={data.get(key)!r}; expected one of: {options}"
    raise GenerationError(message)


def rows(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """The model's list-of-objects field, with unusable entries rejected here."""
    value = data.get(key)
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        message = f"the model returned {key!r} as something other than a list"
        raise GenerationError(message)
    return value


def flag(data: dict[str, Any], key: str, *, default: bool = False) -> bool:
    """A boolean field, tolerating the strings models write for booleans."""
    value = data.get(key, default)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}
    return bool(value)


def whole_number(
    data: dict[str, Any],
    key: str,
    *,
    default: int,
    minimum: int,
    maximum: int | None = None,
) -> int:
    """An integer field, clamped to what the model field will accept."""
    value = data.get(key, default)
    try:
        number = int(value)
    except TypeError, ValueError:
        return default
    number = max(number, minimum)
    return number if maximum is None else min(number, maximum)


def require_parent(parent: Any, label: str) -> Any:
    """The page a draft hangs off, refusing rather than saving an orphan."""
    if parent is None:
        message = f"a {label} has to be attached to an existing page"
        raise GenerationError(message)
    return parent
