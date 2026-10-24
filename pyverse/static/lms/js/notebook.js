/* Client-side notebook runner (LMS lesson bodies).
 *
 * Markdown cells arrive already rendered (`wagtailmarkdown`); this file drives
 * only the code cells, through the shared PyScript runtime
 * (`includes/pyscript_runtime.html` → `window._pyNotebook`), which executes them
 * in order in one namespace, in the learner's browser. Nothing runs on the
 * server, exactly like Labs and the Practice grader.
 *
 * DOM contract
 *   [data-notebook]                    one notebook
 *     [data-notebook-status]           "Loading Python runtime…" → Ready / failed
 *     [data-notebook-run]              Run button, disabled until the runtime loads
 *     [data-cell][data-cell-type=code] one code cell
 *       [data-cell-source]             its source (<pre>, read as text)
 *       [data-cell-out]                where stdout / the traceback is written
 * A lesson may hold several notebooks; each run re-executes that notebook from a
 * clean namespace, so the cells in it see each other but not another notebook's.
 */
(function () {
  "use strict";

  var notebooks = Array.prototype.slice.call(document.querySelectorAll("[data-notebook]"));
  if (!notebooks.length) return;

  var started = Date.now();

  function cellsOf(notebook) {
    return Array.prototype.map.call(
      notebook.querySelectorAll('[data-cell][data-cell-type="code"]'),
      function (cell) {
        var source = cell.querySelector("[data-cell-source]");
        return { type: "code", source: source ? source.textContent : "" };
      },
    );
  }

  function outputsOf(notebook) {
    return Array.prototype.slice.call(
      notebook.querySelectorAll('[data-cell][data-cell-type="code"] [data-cell-out]'),
    );
  }

  function paintStatus(notebook, text) {
    var status = notebook.querySelector("[data-notebook-status]");
    if (status) status.textContent = text;
  }

  function paintResult(notebook, result) {
    var outputs = outputsOf(notebook);
    var failures = 0;
    outputs.forEach(function (out) {
      out.textContent = "";
      out.classList.add("hidden");
    });
    (result.cells || []).forEach(function (cell, index) {
      var out = outputs[index];
      if (!out) return;
      var text = String(cell.stdout || "") + String(cell.error || "");
      out.textContent = text.trim() ? text : "(no output)";
      out.style.color = cell.error ? "#b91c1c" : "";
      out.classList.remove("hidden");
      if (cell.error) failures += 1;
    });
    paintStatus(
      notebook,
      failures ? failures + " cell" + (failures === 1 ? "" : "s") + " failed" : "Ran successfully",
    );
  }

  function run(notebook) {
    var button = notebook.querySelector("[data-notebook-run]");
    if (!window._pyNotebook || !button) return;
    button.disabled = true;
    paintStatus(notebook, "Running…");
    window._pendingNotebook = JSON.stringify({ cells: cellsOf(notebook) });

    // Yield so "Running…" paints before the synchronous Python call.
    setTimeout(function () {
      try {
        paintResult(notebook, JSON.parse(window._pyNotebook()));
      } catch (err) {
        paintStatus(notebook, "Execution bridge error: " + String(err));
      }
      button.disabled = false;
    }, 20);
  }

  notebooks.forEach(function (notebook) {
    var button = notebook.querySelector("[data-notebook-run]");
    if (button) {
      button.addEventListener("click", function () {
        run(notebook);
      });
    }
  });

  // Pyodide loads asynchronously; offline it never arrives, so stop waiting and
  // say so instead of leaving Run greyed out forever.
  (function waitForRuntime() {
    if (document.body.dataset.pyverseReady === "1") {
      notebooks.forEach(function (notebook) {
        var button = notebook.querySelector("[data-notebook-run]");
        if (button) button.disabled = false;
        paintStatus(notebook, "Ready");
      });
      return;
    }
    if (Date.now() - started > 45000) {
      notebooks.forEach(function (notebook) {
        paintStatus(notebook, "Python runtime failed to load");
      });
      return;
    }
    setTimeout(waitForRuntime, 200);
  })();
})();
