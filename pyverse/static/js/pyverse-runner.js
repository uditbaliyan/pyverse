/* Dedicated worker that owns Pyodide for the Practice page.
 *
 * Why a worker: Python runs synchronously, so on the page's own thread a
 * learner's `while True: pass` freezes the tab and nothing can stop it. Here the
 * page keeps a watchdog and simply terminates this worker (see
 * pyverse-runtime.js), then starts a fresh one.
 *
 * What runs: the SAME Python the templates ship (`includes/pyscript_runtime.html`
 * — the grader — and `includes/tracer_runtime.html`), handed over as text. That
 * Python was written for PyScript on the main thread and talks to a handful of
 * browser objects; the shim below provides exactly those, so nothing is ported
 * and the grader/tracer stay single-sourced.
 *
 * Protocol (main -> worker):  {type:"init", sources:[py…], payload:"<json text>", pyodideUrl?}
 *                             {type:"exec",  id, code, isSubmit, customJson}
 *                             {type:"trace", id, code, fn, args, limit}
 *                             {type:"lab",   id, code, limit}      Labs: trace a whole program
 *                             {type:"notebook", id, cells}         lesson notebook: Run all
 *           (worker -> main): {type:"ready"} | {type:"fatal", error}
 *                             {type:"result", id, value} | {type:"error", id, error}
 */
"use strict";

var PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js";

var payloadText = "";

// The shipped Python does `from js import document, window` and only these calls:
//   document.createElement("style") / .head.appendChild / .body.dataset.<flag>
//   document.getElementById("pyverse-payload").textContent
//   window._pendingCode, js.window._pyExec = …, js.window._pvTraceCall = …,
//   js.window._pvTrace / _pyNotebook, window._pendingNotebook
self.window = self;
self.document = {
  createElement: function () {
    return {};
  },
  head: { appendChild: function () {} },
  body: { dataset: {} },
  getElementById: function (id) {
    return { textContent: id === "pyverse-payload" ? payloadText : "" };
  },
};

var pyodide = null;

function toPlain(value) {
  // Python tuples/lists come back as PyProxy objects; copy to plain JS and free.
  if (value && typeof value.toJs === "function") {
    var plain = value.toJs();
    value.destroy();
    return plain;
  }
  return value;
}

self.onmessage = async function (event) {
  var msg = event.data;
  try {
    if (msg.type === "init") {
      payloadText = msg.payload || "";
      importScripts(msg.pyodideUrl || PYODIDE_URL);
      pyodide = await self.loadPyodide();
      for (var i = 0; i < msg.sources.length; i += 1) {
        await pyodide.runPythonAsync(msg.sources[i]);
      }
      self.postMessage({ type: "ready" });
      return;
    }
    if (msg.type === "exec") {
      self._pendingCode = msg.code || "";
      var out = toPlain(self._pyExec(!!msg.isSubmit, msg.customJson || "{}"));
      self.postMessage({ type: "result", id: msg.id, value: [out[0], out[1]] });
      return;
    }
    if (msg.type === "trace") {
      var raw = self._pvTraceCall(msg.code || "", msg.fn || "", msg.args || "", msg.limit || null);
      self.postMessage({ type: "result", id: msg.id, value: String(raw) });
      return;
    }
    if (msg.type === "lab") {
      // Labs run a whole program, not one call: `trace(source, limit)`.
      var program = self._pvTrace(msg.code || "", msg.limit || null);
      self.postMessage({ type: "result", id: msg.id, value: String(program) });
      return;
    }
    if (msg.type === "notebook") {
      self._pendingNotebook = JSON.stringify({ cells: msg.cells || [] });
      self.postMessage({ type: "result", id: msg.id, value: String(self._pyNotebook()) });
      return;
    }
  } catch (error) {
    var text = String((error && error.message) || error);
    self.postMessage(
      msg.type === "init"
        ? { type: "fatal", error: text }
        : { type: "error", id: msg.id, error: text }
    );
  }
};
