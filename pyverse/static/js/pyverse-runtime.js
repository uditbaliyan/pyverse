/* Page side of the Practice Python runtime: owns the worker and its watchdog.
 *
 *   PyverseRuntime.exec(code, isSubmit, customJson) -> Promise<[metaJson, log]>
 *   PyverseRuntime.trace(code, fn, args)            -> Promise<traceJson>
 *   PyverseRuntime.labTrace(code)                   -> Promise<traceJson>   (Labs)
 *   PyverseRuntime.notebook(cells)                  -> Promise<resultJson>  (lessons)
 *   PyverseRuntime.ready()                          -> boolean
 *
 * Both calls always resolve (never reject): a run that exceeds its time budget
 * is killed — the worker is terminated and a new one boots in the background —
 * and the promise resolves with a normal-looking "time limit exceeded" result,
 * so the page's existing result handling shows it without special cases.
 *
 * Python source is read from the page's `<script type="py">` blocks. PyScript's
 * loader is NOT on this page, so the browser treats them as inert text.
 *
 * Page flags kept for existing pollers: body.dataset.pyverseReady / labReady are
 * "1" while a worker is ready and "" while it (re)starts. Every change is also
 * dispatched as `pyverse:runtime` {state: loading | ready | restarting | failed}.
 */
(function () {
  "use strict";

  var script = document.currentScript;
  var WORKER_URL = script ? script.getAttribute("data-worker") : "";
  // Optional: where pyodide.js lives (self-hosting). The worker defaults to the CDN.
  var PYODIDE_URL = (script && script.getAttribute("data-pyodide")) || "";
  var BUDGET = { run: 5000, submit: 10000, trace: 8000, lab: 8000, notebook: 10000 }; // ms per call, after ready

  var worker = null;
  var readyPromise = null;
  var isReady = false;
  var seq = 0;
  var pending = null; // the one in-flight call: {id, resolve, reject}
  var chain = Promise.resolve();

  function sources() {
    return Array.prototype.map.call(document.querySelectorAll('script[type="py"]'), function (el) {
      return el.textContent;
    });
  }

  function payloadText() {
    var el = document.getElementById("pyverse-payload");
    return el ? el.textContent : "";
  }

  function setState(state, detail) {
    isReady = state === "ready";
    document.body.dataset.pyverseReady = isReady ? "1" : "";
    document.body.dataset.labReady = isReady ? "1" : "";
    document.dispatchEvent(new CustomEvent("pyverse:runtime", { detail: { state: state, error: detail || null } }));
  }

  function boot(state) {
    setState(state);
    worker = new Worker(WORKER_URL);
    readyPromise = new Promise(function (resolve) {
      worker.onmessage = function (event) {
        var msg = event.data;
        if (msg.type === "ready") {
          setState("ready");
          resolve(true);
        } else if (msg.type === "fatal") {
          setState("failed", msg.error);
          resolve(false);
        } else if (pending && msg.id === pending.id) {
          var call = pending;
          pending = null;
          if (msg.type === "result") call.resolve(msg.value);
          else call.reject(new Error(msg.error));
        }
      };
      worker.onerror = function (event) {
        setState("failed", event.message || "worker error");
        resolve(false);
      };
    });
    worker.postMessage({ type: "init", sources: sources(), payload: payloadText(), pyodideUrl: PYODIDE_URL });
  }

  // Run one message through the worker under a wall-clock budget. Resolves with
  // {ok:true, value} | {ok:false, timeout:true} | {ok:false, error}.
  function call(message, budget) {
    var job = chain.then(function () {
      return readyPromise.then(function (up) {
        if (!up) return { ok: false, error: "The Python runtime is not available." };
        return new Promise(function (resolve) {
          var id = (seq += 1);
          var timer = window.setTimeout(function () {
            pending = null;
            worker.terminate();
            boot("restarting");
            resolve({ ok: false, timeout: true });
          }, budget);
          pending = {
            id: id,
            resolve: function (value) {
              window.clearTimeout(timer);
              resolve({ ok: true, value: value });
            },
            reject: function (error) {
              window.clearTimeout(timer);
              resolve({ ok: false, error: error.message });
            },
          };
          message.id = id;
          worker.postMessage(message);
        });
      });
    });
    chain = job;
    return job;
  }

  function seconds(ms) {
    return Math.round(ms / 100) / 10;
  }

  function exec(code, isSubmit, customJson) {
    var budget = isSubmit ? BUDGET.submit : BUDGET.run;
    return call({ type: "exec", code: code, isSubmit: isSubmit, customJson: customJson }, budget).then(function (r) {
      if (r.ok) return r.value;
      var total = 0;
      try {
        total = (JSON.parse(payloadText()).cases || []).length;
      } catch (error) {
        total = 0;
      }
      var log = r.timeout
        ? "Time limit exceeded (" + seconds(budget) + " s).\n\nYour code ran for too long — most often a loop that never ends " +
          "(check the loop condition and that something inside it changes). The Python runtime was restarted; " +
          "your editor is untouched."
        : "RuntimeError: " + r.error;
      return [JSON.stringify({ status: "RUNTIME_ERROR", latency: 0, passed: 0, total: total }), log];
    });
  }

  function trace(code, fn, args) {
    return call({ type: "trace", code: code, fn: fn, args: args, limit: 200000 }, BUDGET.trace).then(function (r) {
      if (r.ok) return r.value;
      return JSON.stringify({
        steps: [],
        stdout: "",
        error: r.timeout
          ? "Time limit exceeded (" + seconds(BUDGET.trace) + " s) — this call never finished. The Python runtime was restarted."
          : "RuntimeError: " + r.error,
        error_line: null,
        truncated: false,
        source: code || "",
        harness_from: null,
      });
    });
  }

  // Labs: trace a whole program. Same JSON as `trace`, minus the call harness.
  function labTrace(code) {
    return call({ type: "lab", code: code, limit: 200000 }, BUDGET.lab).then(function (r) {
      if (r.ok) return r.value;
      return JSON.stringify({
        steps: [],
        stdout: "",
        error: r.timeout
          ? "Time limit exceeded (" + seconds(BUDGET.lab) + " s) — the program never finished " +
            "(an endless loop?). The Python runtime was restarted; your editor is untouched."
          : "RuntimeError: " + r.error,
        error_line: null,
        truncated: false,
        source: code || "",
      });
    });
  }

  // Lesson notebooks: run every code cell in order. `{cells:[{stdout,error}], ok}`;
  // on a timeout `cells` is empty and `error` says why (the worker, and with it
  // the cells' partial output, is gone).
  function notebook(cells) {
    return call({ type: "notebook", cells: cells }, BUDGET.notebook).then(function (r) {
      if (r.ok) return r.value;
      return JSON.stringify({
        cells: [],
        ok: false,
        error: r.timeout
          ? "Time limit exceeded (" + seconds(BUDGET.notebook) + " s) — a cell never finished " +
            "(an endless loop?). The Python runtime was restarted; nothing was changed on the page."
          : "RuntimeError: " + r.error,
      });
    });
  }

  window.PyverseRuntime = {
    exec: exec,
    trace: trace,
    labTrace: labTrace,
    notebook: notebook,
    ready: function () {
      return isReady;
    },
  };

  if (WORKER_URL) boot("loading");
  else setState("failed", "no worker url");
})();
