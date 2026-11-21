"""The verifier child must not see the parent's secrets or write into the repo."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from pyverse.ai_content.verify import verify
from pyverse.common.sandbox import run_python
from pyverse.common.sandbox import scrubbed_env

PROBE = "import os,sys; sys.stdout.write(repr(sorted(os.environ)) + '|' + os.getcwd())"


def test_scrubbed_env_drops_secrets():
    env = scrubbed_env(
        {"PATH": "/bin", "OPENAI_API_KEY": "sk-x", "DATABASE_URL": "x", "LANG": "C"},
        "/tmp/w",  # noqa: S108
    )
    assert "OPENAI_API_KEY" not in env
    assert "DATABASE_URL" not in env
    assert env["PATH"] == "/bin"
    assert env["HOME"] == "/tmp/w"  # noqa: S108


def test_child_does_not_inherit_secrets_or_cwd(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    done = run_python(
        [sys.executable, "-c", PROBE],
        stdin="",
        timeout=20,
        parent_env=os.environ,
    )
    assert done.returncode == 0, done.stderr
    names, cwd = done.stdout.split("|")
    assert "API_KEY" not in names
    assert Path(cwd) != Path.cwd()


def test_generated_solution_cannot_read_provider_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    result = verify(
        function_name="leak",
        solution_code=(
            "import os\n"
            "def leak():\n"
            "    return os.environ.get('OPENAI_API_KEY', 'absent')\n"
        ),
        comparator="exact",
        cases=[{"input": "", "expected": "'absent'"}],
    )
    assert result.ok, result.failure_report()
