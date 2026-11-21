"""Run untrusted Python in a throwaway child process with a reduced blast radius.

Used by the authoring-time verifiers (``ai_content.verify``, ``labs.gym``). It is
hardening, not a security boundary: the child still runs as the same OS user.
What it does stop is the cheap, likely failure, generated code reading the LLM
provider key (or any other secret) out of the parent's environment, or littering
the repository.

* environment: an allow-list, nothing inherited by default;
* working directory: a fresh temp dir, deleted afterwards;
* limits (POSIX): CPU seconds, address space, written-file size, open files.
"""

from __future__ import annotations

import contextlib
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

try:  # not available on Windows
    import resource
except ImportError:  # pragma: no cover
    resource = None  # type: ignore[assignment]

# Only these survive from the parent; secrets (``*_API_KEY``, ``DATABASE_URL``,
# ``DJANGO_*``, cloud credentials ...) never do.
ENV_ALLOWLIST = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "SYSTEMROOT")

MEGABYTE = 1024 * 1024
DEFAULT_MEMORY_MB = 1024
DEFAULT_FILE_MB = 16
DEFAULT_OPEN_FILES = 64


def scrubbed_env(
    parent: Mapping[str, str],
    workdir: str,
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """A minimal environment: allow-listed variables, ``HOME`` inside ``workdir``."""
    env = {key: parent[key] for key in ENV_ALLOWLIST if key in parent}
    env.update(
        HOME=workdir,
        TMPDIR=workdir,
        MPLCONFIGDIR=workdir,
        PYTHONHASHSEED="0",
        PYTHONDONTWRITEBYTECODE="1",
    )
    env.update(extra or {})
    return env


def _limiter(cpu_seconds: int, memory_mb: int, file_mb: int, open_files: int):
    def apply() -> None:
        def cap(which: int, value: int) -> None:
            # a platform that refuses one limit still gets the others
            with contextlib.suppress(ValueError, OSError):
                resource.setrlimit(which, (value, value))

        cap(resource.RLIMIT_CPU, cpu_seconds)
        cap(resource.RLIMIT_AS, memory_mb * MEGABYTE)
        cap(resource.RLIMIT_FSIZE, file_mb * MEGABYTE)
        cap(resource.RLIMIT_NOFILE, open_files)
        cap(resource.RLIMIT_CORE, 0)

    return apply


def run_python(  # noqa: PLR0913
    argv: Sequence[str],
    *,
    stdin: str,
    timeout: int,
    parent_env: Mapping[str, str],
    extra_env: Mapping[str, str] | None = None,
    memory_mb: int = DEFAULT_MEMORY_MB,
    file_mb: int = DEFAULT_FILE_MB,
    open_files: int = DEFAULT_OPEN_FILES,
) -> subprocess.CompletedProcess[str]:
    """``subprocess.run`` with a scrubbed env, temp cwd and resource limits.

    ``argv[0]`` should be ``sys.executable``. Raises ``subprocess.TimeoutExpired``
    and ``OSError`` exactly like ``subprocess.run`` does.
    """
    with tempfile.TemporaryDirectory(prefix="pyverse-sandbox-") as workdir:
        return subprocess.run(  # noqa: S603 - argv list, no shell
            list(argv),
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=workdir,
            env=scrubbed_env(parent_env, workdir, extra_env),
            preexec_fn=(
                _limiter(timeout + 5, memory_mb, file_mb, open_files)
                if resource is not None and sys.platform != "win32"
                else None
            ),
        )
