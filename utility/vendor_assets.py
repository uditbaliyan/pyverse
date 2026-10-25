# ruff: noqa: INP001
"""Download the pinned third-party browser assets into pyverse/static/vendor/.

    uv run python utility/vendor_assets.py          # fetch + copy (needs npm)
    uv run python utility/vendor_assets.py --check  # verify files exist, no network

Versions live ONLY in `ASSETS` below; templates and JS reference the vendored
paths. To upgrade: change a version here, run the script, commit the result,
and update the same version string in the templates/JS (the tests tell you
which, see pyverse/tests/test_vendor.py).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "pyverse" / "static" / "vendor"

# npm package -> (version, {path inside the package: destination under VENDOR})
_CM = "codemirror/5.65.17/"

ASSETS: dict[str, tuple[str, dict[str, str]]] = {
    "pyodide": (
        "0.27.7",
        {  # MPL-2.0. Everything the grader/tracer need (stdlib only, no wheels).
            "pyodide.js": "pyodide/0.27.7/pyodide.js",
            "pyodide.asm.js": "pyodide/0.27.7/pyodide.asm.js",
            "pyodide.asm.wasm": "pyodide/0.27.7/pyodide.asm.wasm",
            "python_stdlib.zip": "pyodide/0.27.7/python_stdlib.zip",
            "pyodide-lock.json": "pyodide/0.27.7/pyodide-lock.json",
        },
    ),
    "codemirror": (
        "5.65.17",  # MIT
        {
            "lib/codemirror.js": "codemirror/5.65.17/lib/codemirror.js",
            "lib/codemirror.css": "codemirror/5.65.17/lib/codemirror.css",
            "mode/python/python.js": "codemirror/5.65.17/mode/python/python.js",
            "addon/edit/closebrackets.js": _CM + "addon/edit/closebrackets.js",
            "addon/edit/matchbrackets.js": _CM + "addon/edit/matchbrackets.js",
            "addon/selection/active-line.js": _CM + "addon/selection/active-line.js",
            "addon/comment/comment.js": "codemirror/5.65.17/addon/comment/comment.js",
        },
    ),
    "@viz-js/viz": (
        "3.11.0",  # MIT (bundles Graphviz, EPL-2.0)
        {"lib/viz-standalone.js": "viz/3.11.0/viz-standalone.js"},
    ),
}


def expected_files() -> list[Path]:
    return [VENDOR / dest for _, files in ASSETS.values() for dest in files.values()]


def fetch() -> None:
    npm = shutil.which("npm")
    if npm is None:
        sys.exit("npm is required to download the vendored assets")
    with tempfile.TemporaryDirectory() as tmp:
        for package, (version, files) in ASSETS.items():
            subprocess.run(  # noqa: S603
                [npm, "pack", f"{package}@{version}", "--silent"],
                cwd=tmp,
                check=True,
                capture_output=True,
            )
            tarball = next(Path(tmp).glob("*.tgz"))
            with tarfile.open(tarball) as archive:
                for source, dest in files.items():
                    member = archive.extractfile(f"package/{source}")
                    if member is None:
                        sys.exit(f"{package}@{version}: {source} not in the package")
                    target = VENDOR / dest
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(member.read())
                licence = next(
                    (
                        m
                        for m in archive.getmembers()
                        if m.name.upper().startswith("PACKAGE/LICENSE")
                    ),
                    None,
                )
                if licence is not None:
                    root = VENDOR.joinpath(*Path(next(iter(files.values()))).parts[:2])
                    (root / "LICENSE").write_bytes(archive.extractfile(licence).read())
            tarball.unlink()
            print(f"vendored {package}@{version} ({len(files)} files)")  # noqa: T201


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only verify files exist")
    args = parser.parse_args()
    if args.check:
        missing = [path for path in expected_files() if not path.is_file()]
        if missing:
            sys.exit("missing vendored files:\n" + "\n".join(f"  {p}" for p in missing))
        print(f"{len(expected_files())} vendored files present")  # noqa: T201
        return
    fetch()


if __name__ == "__main__":
    main()
