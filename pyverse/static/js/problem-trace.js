/* Practice → Labs: "solve a problem, then watch it execute".
 *
 * Glue only. The problem page owns the editor and the grader; the tracer
 * (`includes/tracer_runtime.html`) and its views (`lab-engine.js`) are the
 * Labs'. This file reads the editor and the Testcase arguments, asks the tracer
 * to trace ONE call of the learner's function, and hands the result to the
 * views. Nothing is sent anywhere and no hidden test case is ever traced: only
 * what is in the Arguments box (a visible case, or what the learner typed).
 *
 * Contract with problem_page.html:
 *   reads    #pyverse-payload (fn), #pyverse-trace-reference (JSON string),
 *            #p-args, the CodeMirror inside #editor-host (or #editor-ta)
 *   listens  `pyverse:run-result` on document — {isSubmit, status, passed, total, log}
 *   emits    `pyverse:trace` on document — {slug, source, trigger, steps, error}
 *            (a hook for host-side analytics; the static site records nothing)
 */
(function () {
  "use strict";

  var section = document.getElementById("trace-section");
  if (!section) return;

  // Hard cap on executed lines for a traced call. Generous for any honest
  // solution, small enough that `while True:` stops in about a second.
  var LINE_LIMIT = 200000;

  var traceBtn = document.getElementById("trace-btn");
  var retraceBtn = document.getElementById("trace-retrace");
  var callEl = document.getElementById("trace-call");
  var prompt = document.getElementById("trace-prompt");
  var srcButtons = Array.prototype.slice.call(section.querySelectorAll(".pt-src"));

  var fn = "";
  try {
    fn = JSON.parse(document.getElementById("pyverse-payload").textContent).fn || "";
  } catch (error) {
    fn = "";
  }
  var reference = "";
  try {
    var refEl = document.getElementById("pyverse-trace-reference");
    reference = refEl ? JSON.parse(refEl.textContent) || "" : "";
  } catch (error) {
    reference = "";
  }

  var source = "mine"; // "mine" | "ref"
  var busy = false;

  function runtimeReady() {
    return document.body.dataset.labReady === "1" && typeof window._pvTraceCall === "function";
  }

  function learnerCode() {
    var host = document.querySelector("#editor-host .CodeMirror");
    if (host && host.CodeMirror) return host.CodeMirror.getValue();
    var ta = document.getElementById("editor-ta");
    return ta ? ta.value : "";
  }

  function argsEl() {
    return document.getElementById("p-args");
  }

  function setSource(next) {
    source = next === "ref" && reference ? "ref" : "mine";
    srcButtons.forEach(function (button) {
      button.classList.toggle("pt-src-on", button.getAttribute("data-src") === source);
    });
  }

  function setEnabled(on) {
    if (traceBtn) traceBtn.disabled = !on;
    if (retraceBtn) retraceBtn.disabled = !on;
    Array.prototype.forEach.call(prompt ? prompt.querySelectorAll("button") : [], function (button) {
      button.disabled = !on;
    });
  }

  function trace(trigger, opts) {
    opts = opts || {};
    if (busy || !runtimeReady()) return;
    if (opts.source) setSource(opts.source);
    if (typeof opts.args === "string" && argsEl()) argsEl().value = opts.args;

    var args = argsEl() ? argsEl().value.trim() : "";
    var code = source === "ref" ? reference : learnerCode();
    var label = fn + "(" + args + ")";

    busy = true;
    setEnabled(false);
    section.classList.remove("hidden");
    callEl.textContent = label;
    if (window.PyverseLab) window.PyverseLab.setStatus("busy", "Tracing…");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    // Yield once so "Tracing…" paints before the synchronous Python call.
    window.setTimeout(function () {
      var raw = null;
      try {
        raw = window._pvTraceCall(code, fn, args, LINE_LIMIT);
        window.PyverseLab.show(raw);
        window.PyverseLab.setMode(
          document.getElementById("lab-root").getAttribute("data-mode") === "memory" ? "memory" : "line"
        );
      } catch (error) {
        if (window.PyverseLab) window.PyverseLab.setStatus("err", "Tracer failed: " + error);
      }
      busy = false;
      setEnabled(true);

      var parsed = null;
      try {
        parsed = raw ? JSON.parse(raw) : null;
      } catch (error) {
        parsed = null;
      }
      document.dispatchEvent(
        new CustomEvent("pyverse:trace", {
          detail: {
            slug: document.body.dataset.problemSlug || "",
            source: source,
            trigger: trigger,
            steps: parsed ? (parsed.steps || []).length : 0,
            error: parsed ? parsed.error || null : "tracer failed",
          },
        })
      );
    }, 30);
  }

  // ── prompt shown under the console after Run / Submit ─────────────────────
  function failingVisibleArgs(log) {
    // The grader prints `[FAIL] case i/n  fn(args)` for visible cases and
    // `<hidden case>` for hidden ones, so a hidden input can never leak here.
    var lines = String(log || "").split("\n");
    var head = "  [FAIL] case ";
    for (var i = 0; i < lines.length; i += 1) {
      var line = lines[i];
      if (line.indexOf(head) !== 0) continue;
      var at = line.indexOf("  " + fn + "(", head.length);
      if (at < 0 || line.charAt(line.length - 1) !== ")") continue;
      return line.slice(at + 2 + fn.length + 1, line.length - 1);
    }
    return null;
  }

  function addButton(text, ghost, handler) {
    var button = document.createElement("button");
    button.type = "button";
    button.textContent = text;
    if (ghost) button.className = "pt-ghost";
    button.disabled = !runtimeReady() || busy;
    button.addEventListener("click", handler);
    prompt.appendChild(button);
  }

  function showPrompt(tone, message, call) {
    prompt.innerHTML = "";
    prompt.className = "pt-prompt pt-prompt-" + tone;
    var span = document.createElement("span");
    span.textContent = message + " ";
    prompt.appendChild(span);
    if (call) {
      var code = document.createElement("code");
      code.textContent = call;
      prompt.appendChild(code);
    }
  }

  function onRunResult(event) {
    var result = event.detail || {};
    if (!prompt) return;

    if (result.status === "ACCEPTED") {
      showPrompt("ok", "✓ Accepted. Now watch it execute:");
      addButton("Trace your solution", false, function () {
        trace("accepted", { source: "mine" });
      });
      if (reference) {
        addButton("Trace the reference solution", true, function () {
          trace("accepted", { source: "ref" });
        });
      }
    } else if (result.status === "WRONG_ANSWER" || result.status === "RUNTIME_ERROR") {
      var failing = failingVisibleArgs(result.log);
      var verb = result.status === "RUNTIME_ERROR" ? "⚠ It crashed" : "✗ Wrong answer";
      if (failing !== null) {
        showPrompt("bad", verb + " on", fn + "(" + failing + ").");
        addButton("Watch your code run on it", false, function () {
          trace("failing-case", { source: "mine", args: failing });
        });
      } else {
        showPrompt("bad", verb + " — the failing case is hidden. Trace the visible one:");
        addButton("Trace the selected case", false, function () {
          trace("failed-selected", { source: "mine" });
        });
      }
    } else if (result.status === "SUCCESS") {
      showPrompt("ok", "Ran. See how it got there:");
      addButton("Trace this call", false, function () {
        trace("run", { source: "mine" });
      });
    } else {
      prompt.className = "pt-prompt hidden";
    }
  }

  // ── wiring ────────────────────────────────────────────────────────────────
  if (traceBtn) {
    traceBtn.addEventListener("click", function () {
      trace("button", { source: "mine" });
    });
  }
  if (retraceBtn) {
    retraceBtn.addEventListener("click", function () {
      trace("retrace");
    });
  }
  srcButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      trace("source-toggle", { source: button.getAttribute("data-src") });
    });
  });
  document.addEventListener("pyverse:run-result", onRunResult);
  if (window.PyverseLab) {
    window.PyverseLab.retrace = function () {
      trace("retrace");
    };
  }

  // Pyodide loads asynchronously (and offline never does): enable on arrival,
  // leave the controls disabled otherwise — the page's own status pill already
  // tells the learner the runtime failed.
  setEnabled(false);
  var tries = 0;
  var poll = window.setInterval(function () {
    if (runtimeReady()) {
      window.clearInterval(poll);
      setEnabled(true);
    } else if (++tries > 450) {
      window.clearInterval(poll);
    }
  }, 100);
})();
