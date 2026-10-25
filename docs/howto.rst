How To - Project Documentation
======================================================================

Get Started
----------------------------------------------------------------------

Documentation can be written as rst files in `pyverse/docs`.


To build and serve docs, use the command::

    uv run make livehtml

from inside the `pyverse/docs` directory.


Changes to files in `docs/_source` will be picked up and reloaded automatically.

`Sphinx <https://www.sphinx-doc.org/>`_ is the tool used to build documentation.

Docstrings to Documentation
----------------------------------------------------------------------

The sphinx extension `apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ is used to automatically document code using signatures and docstrings.

Numpy or Google style docstrings will be picked up from project files and available for documentation. See the `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension for details.

For an in-use example, see the `page source <_sources/users.rst.txt>`_ for :ref:`users`.

To compile all docstrings automatically into documentation source files, use the command:
    ::

        uv run make apidocs


Updating vendored assets
------------------------

Pyodide, CodeMirror and viz-js are served from ``pyverse/static/vendor/`` rather
than a CDN, so Practice keeps working when a CDN is down. The only place their
versions are chosen is the ``ASSETS`` table in ``utility/vendor_assets.py``.

1. Edit the version (and the destination folder name, which contains it) in
   ``ASSETS``.
2. ``python utility/vendor_assets.py`` downloads the npm package and copies only
   the listed files (needs ``npm``). ``--check`` verifies they exist, offline.
3. Update the same version string where it is referenced:
   ``coding/problem_page.html`` (CodeMirror, Pyodide), ``labs/lab_page.html``
   (CodeMirror) and the ``data-viz`` attribute in ``includes/trace_panel.html`` and
   ``labs/lab_page.html``. ``pyverse/tests/test_vendor.py`` fails until every
   reference points at a file that exists.
4. Update ``pyverse/static/vendor/README.md`` (version, licence) and run
   ``uv run pytest`` and the browser smoke test (see below).

Still on a CDN: Tailwind play CDN, Alpine, Mermaid, Lucide and Google Fonts.
PyScript is no longer used by any page: Practice, Labs and lesson notebooks all run
Python in the Web Worker (see below).

Browser smoke test
------------------

``pyverse/tests/e2e/`` drives headless Chromium through the learner loop: a
``while True:`` run must come back as "Time limit exceeded" while the page's own
timers keep firing, and a passing run must open a trace that steps. It is skipped
unless ``PYVERSE_E2E_URL`` points at a running site::

   uv run python manage.py runserver 127.0.0.1:8000 &
   uv pip install playwright && uv run playwright install chromium
   PYVERSE_E2E_URL=http://127.0.0.1:8000 uv run pytest -m e2e

The default ``pytest`` run deselects it (``-m "not e2e"``); CI runs it in the
``e2e`` job.

Where learner Python runs
-------------------------

Every page that runs learner code (Practice problems, Labs, lesson notebooks)
includes the Python partials with ``embedded=True`` (inert ``<script type="py">``
text) plus ``js/pyverse-runtime.js``, which hands that text to a Web Worker
(``js/pyverse-runner.js``) and kills the worker if a call exceeds its budget:
Run 5 s, Submit 10 s, Trace 8 s, Lab trace 8 s, notebook Run all 10 s. A killed
worker restarts in the background and the page shows "Time limit exceeded".
Labs additionally stop after 200,000 executed lines, which ends a Python-level
``while True:`` in well under a second; the watchdog covers loops that never
reach a new line (a single huge C call). A timed-out notebook run loses that run's
partial cell output.
