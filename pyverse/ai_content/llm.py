"""The one place content generators call a model.

Provider and model come from wagtail-ai's ``WAGTAIL_AI["PROVIDERS"]``, so the
``ai_create`` command and the admin AI panels share a single configuration and
a single set of credentials. Nothing here knows about Wagtail content types:
callers hand over a prompt and get text back, or hand over a schema and get a
parsed ``dict``.
"""

from __future__ import annotations

import json
import re
from typing import Any

from django.conf import settings
from wagtail_ai.agents.base import get_llm_service

from .exceptions import ModelError

#: Fenced code block, with or without a language tag. Models reach for these
#: even when told not to.
_FENCE = re.compile(r"```(?:[a-zA-Z]+)?\s*(.*?)```", re.DOTALL)

_RETRY_INSTRUCTION = (
    "That reply could not be parsed as JSON. Reply again with the same content "
    "as a single valid JSON object: no prose, no markdown fence, no comments, "
    "no trailing commas."
)


def complete(prompt: str) -> str:
    """Send one prompt through the configured provider and return its text."""
    alias = settings.AI_CONTENT_PROVIDER_ALIAS
    try:
        service = get_llm_service(alias)
        response = service.completion(
            messages=[{"role": "user", "content": prompt}],
            **settings.AI_CONTENT_COMPLETION_KWARGS,
        )
    except Exception as exc:
        # Everything here is environmental — a missing API key, an unknown
        # provider alias, a transport failure — and the reviewer needs to read
        # what the provider said, not a traceback.
        message = f"the {alias!r} provider is not usable — {type(exc).__name__}: {exc}"
        raise ModelError(message) from exc

    content: str | None = response.choices[0].message.content
    if not content or not content.strip():
        message = "The model returned an empty reply."
        raise ModelError(message)
    return content


def extract_json(reply: str) -> dict[str, Any]:
    """Read the JSON object out of a model reply.

    Tolerates the two shapes models actually emit when asked for JSON — a
    fenced block, or the object wrapped in a sentence — and refuses anything
    else rather than guessing at a repair.
    """
    candidates = [reply, *_FENCE.findall(reply)]
    start, end = reply.find("{"), reply.rfind("}")
    if start != -1 and end > start:
        candidates.append(reply[start : end + 1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            return parsed

    snippet = reply.strip()[:400]
    message = f"The model's reply contained no JSON object. It began: {snippet!r}"
    raise ModelError(message)


def generate_json(
    *,
    style_prompt: str,
    schema: str,
    description: str,
) -> dict[str, Any]:
    """Generate one JSON object from a style guide, a schema and a description.

    Retries once with the parse error in tow: malformed JSON is the one failure
    the model can fix itself, and one extra call is cheaper than making Udit
    describe the thing again.
    """
    prompt = build_prompt(
        style_prompt=style_prompt,
        schema=schema,
        description=description,
    )
    reply = complete(prompt)
    try:
        return extract_json(reply)
    except ModelError as first_attempt:
        retry_prompt = (
            f"{prompt}\n\n{_RETRY_INSTRUCTION}\n\nYour previous reply:\n{reply}"
        )
        second_reply = complete(retry_prompt)
        try:
            return extract_json(second_reply)
        except ModelError as second_attempt:
            message = f"{first_attempt}\nRetried once, same problem: {second_attempt}"
            raise ModelError(message) from second_attempt


def build_prompt(*, style_prompt: str, schema: str, description: str) -> str:
    return (
        f"{style_prompt.strip()}\n\n"
        "---\n\n"
        f"## What to write\n\n{description.strip()}\n\n"
        f"## Reply format\n\n{schema.strip()}\n\n"
        "Reply with the JSON object only."
    )
