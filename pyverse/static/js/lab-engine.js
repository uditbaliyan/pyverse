/* PyVerse Labs engine — one tracer, two views.
 *
 * The Python side (`templates/includes/tracer_runtime.html`) records the steps;
 * this file is only rendering and transport. A step is
 * `{line, fn, depth, out, vars, returned?}` and every value in `vars` is a node
 * from the tracer's serializer, so both views read the same stream:
 *
 *   line   — source lines, executed/current marking, variables, stdout, timeline
 *   memory — the same nodes as a Graphviz record diagram (references by `oid`)
 *
 * Graphviz (viz-js) is fetched only when the memory view is first opened, so a
 * line-trace reader never pays for the WASM download.
 */
(function () {
  "use strict";

  var VIZ_URL = "https://cdn.jsdelivr.net/npm/@viz-js/viz@3.11.0/lib/viz-standalone.js";
  var FUNC_COLORS = ["#7c6af7", "#3dd68c", "#5aacf7", "#f0a140", "#f26d6d", "#c94090", "#0aabbc", "#9ba3bc"];

  var root = document.getElementById("lab-root");
  if (!root) return;

  var el = {
    run: document.getElementById("lab-run"),
    status: document.getElementById("lab-status"),
    source: document.getElementById("lab-source"),
    where: document.getElementById("lab-where"),
    vars: document.getElementById("lab-vars"),
    stdout: document.getElementById("lab-stdout"),
    timeline: document.getElementById("lab-timeline"),
    error: document.getElementById("lab-error"),
    stepCur: document.getElementById("lab-step-cur"),
    stepTot: document.getElementById("lab-step-tot"),
    progress: document.getElementById("lab-progress"),
    speed: document.getElementById("lab-speed"),
    viewport: document.getElementById("lab-viewport"),
    graph: document.getElementById("lab-graph"),
    tabs: Array.prototype.slice.call(document.querySelectorAll(".lab-tab")),
    transport: ["first", "back", "play", "next", "last"].map(function (name) {
      return document.getElementById("lab-" + name);
    }),
  };

  var state = {
    trace: null,
    steps: [],
    cursor: 0,
    timer: null,
    mode: root.getAttribute("data-mode") === "memory" ? "memory" : "line",
    viz: null,
    vizLoading: false,
    funcs: [],
    lineEls: {},
    segments: [],
    pan: { x: 0, y: 0, scale: 1, dragging: false, sx: 0, sy: 0, ox: 0, oy: 0 },
  };

  var editor = null;

  // ── Formatting ─────────────────────────────────────────────────────────
  function fmt(node) {
    if (!node) return "?";
    switch (node.k) {
      case "none":
        return "None";
      case "bool":
        return node.v ? "True" : "False";
      case "int":
        return String(node.v);
      case "float":
        return String(node.v);
      case "str":
        return '"' + node.v + '"';
      case "seq": {
        var open = node.t === "list" ? "[" : node.t === "tuple" ? "(" : "{";
        var close = node.t === "list" ? "]" : node.t === "tuple" ? ")" : "}";
        var body = (node.items || []).map(fmt).join(", ");
        if (node.n > (node.items || []).length) body += ", …";
        return open + body + close;
      }
      case "dict": {
        var pairs = (node.entries || []).map(function (entry) {
          return fmt(entry.k) + ": " + fmt(entry.v);
        });
        if (node.n > (node.entries || []).length) pairs.push("…");
        return "{" + pairs.join(", ") + "}";
      }
      case "obj": {
        var attrs = Object.keys(node.attrs || {}).map(function (name) {
          return name + "=" + fmt(node.attrs[name]);
        });
        return node.t + "(" + attrs.join(", ") + ")";
      }
      case "cycle":
        return "↻ " + (node.t || "cycle");
      case "deep":
        return (node.t || "…") + "(…)";
      default:
        return node.v === undefined ? "?" : String(node.v);
    }
  }

  function typeLabel(node) {
    switch (node.k) {
      case "seq":
        return node.t + " · " + node.n;
      case "dict":
        return "dict · " + node.n;
      case "obj":
        return node.t;
      case "cycle":
        return "↻ " + (node.t || "cycle");
      case "deep":
        return (node.t || "…") + " · " + (node.n === undefined ? "" : node.n);
      default:
        return node.k;
    }
  }

  function isRef(node) {
    return node && (node.k === "seq" || node.k === "dict" || node.k === "obj");
  }

  function funcColor(name) {
    var index = state.funcs.indexOf(name);
    if (index < 0) index = 0;
    return FUNC_COLORS[index % FUNC_COLORS.length];
  }

  // ── Editor ─────────────────────────────────────────────────────────────
  function initEditor() {
    var host = document.getElementById("lab-new-editor");
    var source = document.getElementById("lab-code");
    if (!host || !source) return;
    if (window.CodeMirror) {
      editor = CodeMirror(host, {
        value: source.value,
        mode: "python",
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        styleActiveLine: true,
      });
      source.classList.add("hidden");
    } else {
      // Offline: CodeMirror never arrives, so the plain textarea is the editor.
      host.classList.add("hidden");
      source.classList.remove("hidden");
    }
  }

  function currentCode() {
    if (editor) return editor.getValue();
    var source = document.getElementById("lab-code");
    return source ? source.value : "";
  }

  // ── Trace ──────────────────────────────────────────────────────────────
  function setStatus(cls, text) {
    if (!el.status) return;
    el.status.className = "lab-status " + cls;
    el.status.textContent = text;
  }

  function runTrace() {
    if (typeof window._pvTrace !== "function") return;
    setStatus("busy", "Tracing…");
    window._pendingLabCode = currentCode();
    var raw;
    try {
      raw = window._pvTrace();
    } catch (error) {
      setStatus("err", "Tracer failed: " + error);
      return;
    }
    showTrace(raw);
  }

  // Render a finished trace (the JSON string from `_pvTrace` / `_pvTraceCall`).
  // Split from runTrace so an embedding page can drive the tracer itself and
  // hand the result over through `window.PyverseLab.show`.
  function showTrace(raw) {
    var trace = JSON.parse(raw);
    state.trace = trace;
    state.steps = trace.steps || [];
    state.cursor = 0;
    state.funcs = [];
    state.steps.forEach(function (step) {
      if (state.funcs.indexOf(step.fn) < 0) state.funcs.push(step.fn);
    });
    buildSource();
    buildTimeline();
    render();
    var summary = state.steps.length + " steps";
    if (trace.truncated) summary += " (stopped at the 400-step cap)";
    setStatus(trace.error ? "err" : "ok", trace.error ? "Stopped — " + trace.error : summary);
  }

  function buildSource() {
    var lines = (state.trace.source || "").split("\n");
    el.source.innerHTML = "";
    state.lineEls = {};
    lines.forEach(function (text, index) {
      var row = document.createElement("div");
      row.className = "lab-line";
      row.setAttribute("data-line", String(index + 1));
      // Lines the page appended to drive the learner's code (Practice's
      // "watch it execute" call) are drawn dimmed: they are not the learner's.
      if (state.trace.harness_from && index + 1 >= state.trace.harness_from) {
        row.className += " lab-line-harness";
      }
      var num = document.createElement("span");
      num.className = "lab-line-num";
      num.textContent = String(index + 1);
      var code = document.createElement("code");
      code.textContent = text || " ";
      row.appendChild(num);
      row.appendChild(code);
      el.source.appendChild(row);
      state.lineEls[index + 1] = row;
    });
  }

  function buildTimeline() {
    el.timeline.innerHTML = "";
    state.segments = [];
    state.steps.forEach(function (step, index) {
      var cell = document.createElement("button");
      cell.type = "button";
      cell.className = "lab-seg";
      cell.style.background = funcColor(step.fn);
      cell.title = "step " + (index + 1) + " · " + step.fn + " line " + step.line;
      cell.addEventListener("click", function () {
        seek(index);
      });
      el.timeline.appendChild(cell);
      state.segments.push(cell);
    });
    el.timeline.classList.toggle("hidden", state.steps.length === 0);
  }

  function executedLines() {
    var seen = {};
    for (var i = 0; i <= state.cursor && i < state.steps.length; i += 1) {
      seen[state.steps[i].line] = true;
    }
    return seen;
  }

  function render() {
    var step = state.steps[state.cursor];
    var executed = executedLines();

    Object.keys(state.lineEls).forEach(function (line) {
      var row = state.lineEls[line];
      row.classList.toggle("executed", Boolean(executed[line]));
      row.classList.toggle("active", Boolean(step) && String(step.line) === line);
      row.classList.toggle(
        "error",
        Boolean(state.trace.error_line) && String(state.trace.error_line) === line
      );
    });
    if (step && state.lineEls[step.line]) {
      state.lineEls[step.line].scrollIntoView({ block: "nearest" });
    }

    state.segments.forEach(function (cell, index) {
      cell.classList.toggle("current", index === state.cursor);
      cell.classList.toggle("past", index < state.cursor);
    });

    renderWhere(step);
    renderVars(step);
    renderStdout(step);

    el.stepCur.textContent = state.steps.length ? String(state.cursor + 1) : "0";
    el.stepTot.textContent = String(state.steps.length);
    var pct = state.steps.length ? ((state.cursor + 1) / state.steps.length) * 100 : 0;
    el.progress.style.width = pct.toFixed(2) + "%";

    var has = state.steps.length > 0;
    el.transport[0].disabled = !has || state.cursor === 0;
    el.transport[1].disabled = !has || state.cursor === 0;
    el.transport[3].disabled = !has || state.cursor >= state.steps.length - 1;
    el.transport[4].disabled = !has || state.cursor >= state.steps.length - 1;

    if (state.mode === "memory") renderMemory(step);
  }

  function renderWhere(step) {
    if (!step) {
      el.where.textContent = root.getAttribute("data-empty") || "Press Trace to record the program.";
      return;
    }
    el.where.innerHTML = "";
    var fn = document.createElement("span");
    fn.className = "lab-badge";
    fn.style.borderColor = funcColor(step.fn);
    fn.textContent = step.fn === "<module>" ? "module level" : step.fn + "()";
    el.where.appendChild(fn);

    var depth = document.createElement("span");
    depth.className = "lab-badge plain";
    depth.textContent = "depth " + step.depth;
    el.where.appendChild(depth);

    var line = document.createElement("span");
    line.className = "lab-badge plain";
    line.textContent = "line " + step.line;
    el.where.appendChild(line);

    if (step.returned) {
      var back = document.createElement("span");
      back.className = "lab-badge ret";
      back.textContent = "↩ returns " + fmt(step.returned);
      el.where.appendChild(back);
    }
  }

  function renderVars(step) {
    var previous = state.cursor > 0 ? state.steps[state.cursor - 1].vars : null;
    el.vars.innerHTML = "";
    var names = step ? Object.keys(step.vars) : [];
    if (!names.length) {
      var empty = document.createElement("div");
      empty.className = "lab-empty";
      empty.textContent = step ? "No variables yet." : "";
      el.vars.appendChild(empty);
      return;
    }
    names.forEach(function (name) {
      var node = step.vars[name];
      var row = document.createElement("div");
      row.className = "lab-var";
      var key = document.createElement("span");
      key.className = "lab-var-name";
      key.textContent = name;
      var value = document.createElement("span");
      value.className = "lab-var-value";
      value.textContent = fmt(node);
      if (previous && (!previous[name] || JSON.stringify(previous[name]) !== JSON.stringify(node))) {
        row.classList.add("changed");
      }
      row.appendChild(key);
      row.appendChild(value);
      el.vars.appendChild(row);
    });
  }

  function renderStdout(step) {
    var text = state.trace ? state.trace.stdout || "" : "";
    // `step.out` is how much had been printed *before* this line ran, so the
    // output produced by the current line is the next step's count — or the
    // whole buffer once the program has finished.
    var upto = 0;
    if (step) {
      var next = state.steps[state.cursor + 1];
      upto = next ? next.out : text.length;
    }
    el.stdout.textContent = text.slice(0, upto);
    if (state.trace && state.trace.error) {
      el.error.textContent = state.trace.error;
      el.error.classList.remove("hidden");
    } else {
      el.error.classList.add("hidden");
    }
    el.stdout.scrollTop = el.stdout.scrollHeight;
  }

  // ── Memory graph (DOT → SVG) ───────────────────────────────────────────
  function loadViz() {
    if (window.Viz) return window.Viz.instance();
    if (state.vizLoading) return state.vizLoading;
    state.vizLoading = new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = VIZ_URL;
      script.onload = function () {
        window.Viz.instance().then(resolve, reject);
      };
      script.onerror = function () {
        reject(new Error("viz-js failed to load"));
      };
      document.head.appendChild(script);
    });
    return state.vizLoading;
  }

  function escapeLabel(text) {
    return String(text).replace(/([\\{}|<>])/g, "\\$1").replace(/"/g, '\\"');
  }

  function buildDot(step) {
    if (!step) return null;
    var objects = {};
    var lines = [];

    function objectNode(node) {
      var key = String(node.oid);
      if (objects[key]) return objects[key];
      var rows = [];
      objects[key] = "o" + key;
      if (node.k === "seq") {
        (node.items || []).forEach(function (item, index) {
          if (isRef(item)) {
            rows.push({ port: "r" + index, text: index + " → " + typeLabel(item) });
            lines.push('"' + objects[key] + '":r' + index + ' -> "' + objectNode(item) + '"');
          } else {
            rows.push({ port: null, text: index + ": " + fmt(item) });
          }
        });
        if (node.n > (node.items || []).length) rows.push({ port: null, text: "…" });
      } else if (node.k === "dict") {
        (node.entries || []).forEach(function (entry, index) {
          var label = fmt(entry.k) + " → ";
          if (isRef(entry.v)) {
            rows.push({ port: "r" + index, text: label + typeLabel(entry.v) });
            lines.push('"' + objects[key] + '":r' + index + ' -> "' + objectNode(entry.v) + '"');
          } else {
            rows.push({ port: null, text: label + fmt(entry.v) });
          }
        });
        if (node.n > (node.entries || []).length) rows.push({ port: null, text: "…" });
      } else {
        Object.keys(node.attrs || {}).forEach(function (name, index) {
          var value = node.attrs[name];
          if (isRef(value)) {
            rows.push({ port: "r" + index, text: name + " → " + typeLabel(value) });
            lines.push('"' + objects[key] + '":r' + index + ' -> "' + objectNode(value) + '"');
          } else {
            rows.push({ port: null, text: name + ": " + fmt(value) });
          }
        });
      }
      var label = typeLabel(node) + (rows.length ? "|" : "");
      label += rows
        .map(function (row) {
          return row.port ? "<" + row.port + "> " + escapeLabel(row.text) : escapeLabel(row.text);
        })
        .join("|");
      lines.unshift('"' + objects[key] + '" [label="' + label + '"]');
      return objects[key];
    }

    var localRows = Object.keys(step.vars).map(function (name) {
      var node = step.vars[name];
      if (isRef(node)) {
        var target = objectNode(node);
        lines.push('"locals":' + "p_" + name + ' -> "' + target + '"');
        return "<p_" + name + "> " + escapeLabel(name + "  " + typeLabel(node));
      }
      return escapeLabel(name + "  " + fmt(node));
    });
    if (!localRows.length) localRows.push("(no variables yet)");
    lines.unshift('"locals" [label="{locals|' + localRows.join("|") + '}"]');

    return (
      'digraph lab {\n' +
      '  graph [bgcolor="transparent", rankdir="LR", nodesep="0.4", ranksep="0.8", fontname="JetBrains Mono", fontcolor="#9ba3bc"];\n' +
      '  node [shape="record", style="filled,rounded", fillcolor="#181c25", color="#252b3b", fontname="JetBrains Mono", fontsize="10", fontcolor="#e8ecf5", margin="0.14,0.07"];\n' +
      '  edge [color="#5aacf7", arrowsize="0.7", fontname="JetBrains Mono", fontsize="9", fontcolor="#9ba3bc"];\n  ' +
      lines.join("\n  ") +
      "\n}\n"
    );
  }

  function renderMemory(step) {
    if (!state.trace || !step) {
      el.graph.innerHTML = '<p class="lab-empty">Press Trace to draw memory.</p>';
      return;
    }
    var dot = buildDot(step);
    loadViz().then(
      function (viz) {
        if (state.mode !== "memory") return;
        var svg = viz.renderString(dot, { format: "svg", engine: "dot" });
        el.graph.innerHTML = svg;
        var background = el.graph.querySelector("g.graph > polygon");
        if (background) background.removeAttribute("fill");
        if (state.cursor === 0) fitGraph();
      },
      function (error) {
        el.graph.innerHTML =
          '<p class="lab-empty">Memory graph unavailable — ' + error.message + "</p>";
      }
    );
  }

  function applyTransform() {
    el.graph.style.transform =
      "translate(" + state.pan.x + "px," + state.pan.y + "px) scale(" + state.pan.scale + ")";
  }

  function fitGraph() {
    var svg = el.graph.querySelector("svg");
    var box = el.viewport.getBoundingClientRect();
    if (!svg || !box.width) return;
    var width = svg.width.baseVal.value || svg.viewBox.baseVal.width;
    var height = svg.height.baseVal.value || svg.viewBox.baseVal.height;
    if (!width || !height) return;
    var scale = Math.min((box.width - 40) / width, (box.height - 40) / height, 1.2);
    state.pan.scale = Math.max(scale, 0.1);
    state.pan.x = (box.width - width * state.pan.scale) / 2;
    state.pan.y = (box.height - height * state.pan.scale) / 2;
    applyTransform();
  }

  function zoomBy(factor, cx, cy) {
    var box = el.viewport.getBoundingClientRect();
    var x = cx === undefined ? box.width / 2 : cx - box.left;
    var y = cy === undefined ? box.height / 2 : cy - box.top;
    var next = Math.min(Math.max(state.pan.scale * factor, 0.1), 6);
    var ratio = next / state.pan.scale;
    state.pan.x = x - (x - state.pan.x) * ratio;
    state.pan.y = y - (y - state.pan.y) * ratio;
    state.pan.scale = next;
    applyTransform();
  }

  // ── Transport ──────────────────────────────────────────────────────────
  function seek(index) {
    if (!state.steps.length) return;
    state.cursor = Math.min(Math.max(index, 0), state.steps.length - 1);
    render();
  }

  function stepBy(delta) {
    seek(state.cursor + delta);
  }

  function stopPlay() {
    if (state.timer) window.clearInterval(state.timer);
    state.timer = null;
    if (el.transport[2]) el.transport[2].textContent = "▶";
  }

  function togglePlay() {
    if (state.timer) {
      stopPlay();
      return;
    }
    if (!state.steps.length) return;
    if (state.cursor >= state.steps.length - 1) seek(0);
    el.transport[2].textContent = "❚❚";
    var delay = 1500 - Number(el.speed.value || 5) * 150;
    state.timer = window.setInterval(function () {
      if (state.cursor >= state.steps.length - 1) {
        stopPlay();
        return;
      }
      stepBy(1);
    }, delay);
  }

  function setMode(mode) {
    state.mode = mode;
    root.setAttribute("data-mode", mode);
    el.tabs.forEach(function (tab) {
      var active = tab.getAttribute("data-mode") === mode;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    document.getElementById("lab-panel-line").classList.toggle("hidden", mode !== "line");
    document.getElementById("lab-panel-memory").classList.toggle("hidden", mode !== "memory");
    if (mode === "memory") renderMemory(state.steps[state.cursor]);
  }

  // ── Wiring ─────────────────────────────────────────────────────────────
  function ready() {
    if (el.run) el.run.disabled = false;
    setStatus("ok", "Python ready");
  }

  function waitForRuntime() {
    if (document.body.dataset.labReady === "1") {
      ready();
      return;
    }
    var tries = 0;
    var poll = window.setInterval(function () {
      if (document.body.dataset.labReady === "1") {
        window.clearInterval(poll);
        ready();
      } else if (++tries > 450) {
        window.clearInterval(poll);
        setStatus("err", "Python runtime failed to load");
      }
    }, 100);
  }

  // Hooks for a page that hosts the engine without its own editor (Practice).
  window.PyverseLab = {
    show: function (raw) {
      stopPlay();
      showTrace(raw);
    },
    setStatus: setStatus,
    setMode: setMode,
    retrace: null, // the host assigns this; Ctrl/⌘+Enter calls it when embedded
  };

  initEditor();
  setMode(state.mode);
  render();
  waitForRuntime();

  if (el.run) el.run.addEventListener("click", runTrace);
  el.transport[0].addEventListener("click", function () {
    stopPlay();
    seek(0);
  });
  el.transport[1].addEventListener("click", function () {
    stopPlay();
    stepBy(-1);
  });
  el.transport[2].addEventListener("click", togglePlay);
  el.transport[3].addEventListener("click", function () {
    stopPlay();
    stepBy(1);
  });
  el.transport[4].addEventListener("click", function () {
    stopPlay();
    seek(state.steps.length - 1);
  });
  el.tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      setMode(tab.getAttribute("data-mode"));
    });
  });
  el.speed.addEventListener("input", function () {
    if (state.timer) {
      stopPlay();
      togglePlay();
    }
  });
  document.getElementById("lab-zoom-in").addEventListener("click", function () {
    zoomBy(1.18);
  });
  document.getElementById("lab-zoom-out").addEventListener("click", function () {
    zoomBy(0.85);
  });
  document.getElementById("lab-zoom-fit").addEventListener("click", fitGraph);

  el.viewport.addEventListener(
    "wheel",
    function (event) {
      event.preventDefault();
      zoomBy(event.deltaY < 0 ? 1.1 : 0.91, event.clientX, event.clientY);
    },
    { passive: false }
  );
  el.viewport.addEventListener("mousedown", function (event) {
    state.pan.dragging = true;
    state.pan.sx = event.clientX;
    state.pan.sy = event.clientY;
    state.pan.ox = state.pan.x;
    state.pan.oy = state.pan.y;
    el.viewport.classList.add("dragging");
  });
  window.addEventListener("mousemove", function (event) {
    if (!state.pan.dragging) return;
    state.pan.x = state.pan.ox + (event.clientX - state.pan.sx);
    state.pan.y = state.pan.oy + (event.clientY - state.pan.sy);
    applyTransform();
  });
  window.addEventListener("mouseup", function () {
    state.pan.dragging = false;
    el.viewport.classList.remove("dragging");
  });

  // Shortcuts are scoped to the lab: the page may host other widgets, and a
  // document-wide Space/arrow handler would hijack them.
  document.addEventListener("keydown", function (event) {
    if (!root.contains(event.target)) return;
    var tag = (event.target.tagName || "").toLowerCase();
    if (tag === "textarea" || tag === "input" || tag === "select" || event.target.isContentEditable) return;
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      if (root.hasAttribute("data-embedded")) {
        if (window.PyverseLab && window.PyverseLab.retrace) window.PyverseLab.retrace();
      } else {
        runTrace();
      }
      return;
    }
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      stopPlay();
      stepBy(1);
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      stopPlay();
      stepBy(-1);
    } else if (event.key === " ") {
      event.preventDefault();
      togglePlay();
    }
  });
})();
