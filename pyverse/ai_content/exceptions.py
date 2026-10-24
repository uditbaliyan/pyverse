"""Refusals, not failures.

Every exception here means the same thing to the caller: **nothing was written**
and the message is fit to print for Udit. A generator either returns a saved
draft or raises one of these; there is no half-created state in between.
"""


class GenerationError(Exception):
    """The draft was refused. The message explains why, in reviewer terms."""


class ModelError(GenerationError):
    """The model call failed, or its reply could not be read as the required JSON."""


class VerificationError(GenerationError):
    """The generated solution does not reproduce the generated test cases."""
