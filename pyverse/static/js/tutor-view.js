/* Step-through view of a trace, laid out like Python Tutor:
 * code with "just ran" / "runs next" arrows on the left; print output, Frames
 * (global + every active call) and Objects (lists, dicts, instances, drawn once
 * and pointed at) on the right.
 *
 * It renders the JSON of `includes/tracer_runtime.html` (`steps[].stack`,
 * `final`, `stdout`, `error`, `harness_from`) and nothing else — no Python, no
 * network. A host drives it through `window.PyverseLab`:
 *     show(traceJson)  setStatus(kind, text)  setMode(_)  retrace (host-assigned)
 * the same surface the Labs engine exposes, so problem-trace.js is unchanged.
 */
(function () {
  "use strict";

  var root = document.getElementById("lab-root");
  if (!root) return;

  function $(id) {
    return document.getElementById(id);
  }
  var el = {
    code: $("tv-code"),
    status: $("tv-status"),
    note: $("tv-note"),
    out: $("tv-out"),
    error: $("tv-error"),
    frames: $("tv-frames"),
    objects: $("tv-objects"),
    inner: $("tv-vizin"),
    svg: $("tv-arrows"),
    slider: $("tv-slider"),
    first: $("tv-first"),
    prev: $("tv-prev"),
    next: $("tv-next"),
    last: $("tv-last"),
    pill: $("lab-status"),
  };

  var state = { trace: null, steps: [], i: 0, lines: [] };

  // ── helpers ──────────────────────────────────────────────────────────────
  function esc(text) {
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function make(tag, cls, html) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (html !== undefined) node.innerHTML = html;
    return node;
  }

  // ── syntax highlighting (small, line-safe) ───────────────────────────────
  var KEYWORDS = /^(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|None|True|False)$/;
  var BUILTINS = /^(print|len|range|enumerate|sum|min|max|sorted|reversed|list|dict|set|tuple|str|int|float|bool|abs|zip|map|filter|any|all|isinstance|type|input|open)$/;
  var TOKEN = /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)|(#[^\n]*)|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_]\w*\b)|([\s\S])/g;

  function highlight(source) {
    var lines = [""];
    var afterDef = false;
    function push(cls, text) {
      text.split("\n").forEach(function (part, index) {
        if (index > 0) lines.push("");
        if (part === "") return;
        var safe = esc(part);
        lines[lines.length - 1] += cls ? '<span class="' + cls + '">' + safe + "</span>" : safe;
      });
    }
    var m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(source)) !== null) {
      if (m[1]) push("tv-s", m[1]);
      else if (m[2]) push("tv-c", m[2]);
      else if (m[3]) push("tv-n", m[3]);
      else if (m[4]) {
        if (afterDef) {
          push("tv-f", m[4]);
          afterDef = false;
        } else if (KEYWORDS.test(m[4])) {
          push("tv-k", m[4]);
          afterDef = m[4] === "def" || m[4] === "class";
        } else if (BUILTINS.test(m[4])) push("tv-b", m[4]);
        else push("", m[4]);
      } else {
        push("", m[5]);
        if (!/\s/.test(m[5])) afterDef = false;
      }
    }
    return lines;
  }

  // ── turn a trace into display steps ──────────────────────────────────────
  // Each display step has: kind, next (line about to run), exec (line that just
  // ran), stack [{fn,line,vars,ret?}], out (chars of stdout printed so far).
  function buildSteps(trace) {
    var out = [];
    var raw = trace.steps || [];
    raw.forEach(function (s) {
      var stack = s.stack && s.stack.length ? s.stack : [{ fn: s.fn, line: s.line, vars: s.vars }];
      out.push({ kind: "line", next: s.line, stack: stack, out: s.out, depth: s.depth });
      if (s.returned !== undefined) {
        // The function is about to hand back its value: show it in the frame,
        // and point the red arrow at the line the caller resumes on.
        var withRet = stack.map(function (frame, index) {
          return index === stack.length - 1 ? Object.assign({}, frame, { ret: s.returned }) : frame;
        });
        var caller = stack.length > 1 ? stack[stack.length - 2].line : null;
        out.push({ kind: "return", next: caller, stack: withRet, out: s.out, depth: s.depth });
      }
    });
    if (!trace.truncated) {
      if (trace.error) {
        var last = raw.length ? raw[raw.length - 1] : null;
        out.push({
          kind: "error",
          next: trace.error_line || (last && last.line) || null,
          stack: last && last.stack ? last.stack : [{ fn: "<module>", line: null, vars: trace.final || {} }],
          out: (trace.stdout || "").length,
          error: trace.error,
        });
      } else {
        out.push({
          kind: "done",
          next: null,
          stack: [{ fn: "<module>", line: null, vars: trace.final || {} }],
          out: (trace.stdout || "").length,
        });
      }
    }
    out.forEach(function (step, index) {
      step.exec = index ? out[index - 1].next : null;
    });
    return out;
  }

  // ── values ───────────────────────────────────────────────────────────────
  function isContainer(node) {
    return node && (node.k === "seq" || node.k === "dict" || node.k === "obj") && node.oid !== undefined;
  }

  function primitive(node) {
    switch (node.k) {
      case "none":
        return '<span class="tv-v tv-none">None</span>';
      case "bool":
        return '<span class="tv-v tv-bool">' + (node.v ? "True" : "False") + "</span>";
      case "int":
      case "float":
        return '<span class="tv-v tv-num">' + esc(node.v) + "</span>";
      case "str":
        return '<span class="tv-v tv-str">"' + esc(node.v) + '"</span>';
      case "func":
        return '<span class="tv-v tv-func" title="' + esc(node.v) + '">function ' + esc(node.v) + "</span>";
      case "cycle":
        return '<span class="tv-v tv-dim">↺ ' + esc(node.t || "") + " (cycle)</span>";
      case "deep":
        return '<span class="tv-v tv-dim">' + esc(node.t || "") + " …</span>";
      default:
        return '<span class="tv-v tv-str">' + esc(node.v !== undefined ? node.v : node.t || "?") + "</span>";
    }
  }

  // A value cell: primitives inline; containers become a dot that an arrow
  // leaves from (the object itself is drawn once, in the Objects column).
  function valueHtml(node, heap) {
    if (isContainer(node)) {
      collect(node, heap);
      return '<span class="tv-ptr" data-target="' + node.oid + '" title="' + esc(node.t || node.k) + '"></span>';
    }
    return primitive(node);
  }

  function collect(node, heap) {
    if (!isContainer(node) || heap.map[node.oid]) return;
    heap.map[node.oid] = node;
    heap.order.push(node.oid);
    if (node.k === "seq") node.items.forEach(function (item) { collect(item, heap); });
    else if (node.k === "dict")
      node.entries.forEach(function (entry) {
        collect(entry.k, heap);
        collect(entry.v, heap);
      });
    else Object.keys(node.attrs).forEach(function (name) { collect(node.attrs[name], heap); });
  }

  function objectBox(node, heap) {
    var box = make("div", "tv-obj");
    box.setAttribute("data-oid", node.oid);
    var label, body;
    if (node.k === "seq") {
      label = node.t;
      var ordered = node.t === "list" || node.t === "tuple";
      body = '<div class="tv-cells">';
      if (!node.items.length) body += '<span class="tv-empty">empty</span>';
      node.items.forEach(function (item, index) {
        body += '<div class="tv-cell">' + (ordered ? '<div class="tv-idx">' + index + "</div>" : "") +
          '<div class="tv-val">' + valueHtml(item, heap) + "</div></div>";
      });
      if (node.n > node.items.length) body += '<span class="tv-empty">… ' + (node.n - node.items.length) + " more</span>";
      body += "</div>";
    } else if (node.k === "dict") {
      label = "dict";
      body = '<table class="tv-kv">';
      if (!node.entries.length) body += '<tr><td class="tv-empty">empty</td></tr>';
      node.entries.forEach(function (entry) {
        body += '<tr><td class="tv-key">' + valueHtml(entry.k, heap) + '</td><td class="tv-val">' + valueHtml(entry.v, heap) + "</td></tr>";
      });
      if (node.n > node.entries.length) body += '<tr><td class="tv-empty" colspan="2">… ' + (node.n - node.entries.length) + " more</td></tr>";
      body += "</table>";
    } else {
      label = node.t + " instance";
      body = '<table class="tv-kv">';
      var names = Object.keys(node.attrs);
      if (!names.length) body += '<tr><td class="tv-empty">no attributes</td></tr>';
      names.forEach(function (name) {
        body += '<tr><td class="tv-key">' + esc(name) + '</td><td class="tv-val">' + valueHtml(node.attrs[name], heap) + "</td></tr>";
      });
      body += "</table>";
    }
    box.innerHTML = '<div class="tv-label">' + esc(label) + "</div>" + body;
    return box;
  }

  // ── rendering ────────────────────────────────────────────────────────────
  function renderCode(trace) {
    state.lines = highlight(trace.source || "");
    el.code.innerHTML = "";
    state.lines.forEach(function (html, index) {
      var row = make("div", "tv-line");
      row.setAttribute("data-line", String(index + 1));
      if (trace.harness_from && index + 1 >= trace.harness_from) row.className += " tv-harness";
      row.innerHTML = '<span class="tv-arrow"></span><span class="tv-no">' + (index + 1) + '</span><code class="tv-src">' + (html || " ") + "</code>";
      el.code.appendChild(row);
    });
  }

  function renderFrames(step, heap) {
    el.frames.innerHTML = "";
    var shownFrames = step.stack.length;
    var hidden = step.depth !== undefined ? step.depth - shownFrames : 0;
    step.stack.forEach(function (frame, index) {
      var isGlobal = index === 0 && frame.fn === "<module>";
      var current = index === shownFrames - 1 && step.kind !== "done";
      var box = make("div", "tv-frame" + (current ? " tv-frame-cur" : ""));
      var rows = "";
      Object.keys(frame.vars || {}).forEach(function (name) {
        rows += '<tr><td class="tv-name">' + esc(name) + '</td><td class="tv-val">' + valueHtml(frame.vars[name], heap) + "</td></tr>";
      });
      if (frame.ret !== undefined)
        rows += '<tr class="tv-ret"><td class="tv-name">Return value</td><td class="tv-val">' + valueHtml(frame.ret, heap) + "</td></tr>";
      if (!rows) rows = '<tr><td class="tv-empty" colspan="2">no variables yet</td></tr>';
      box.innerHTML = '<div class="tv-label">' + (isGlobal ? "Global frame" : esc(frame.fn)) + "</div><table>" + rows + "</table>";
      el.frames.appendChild(box);
      if (index === 0 && hidden > 0 && shownFrames > 1)
        el.frames.appendChild(make("div", "tv-hidden", "… " + hidden + " more frames …"));
    });
  }

  function renderObjects(heap) {
    el.objects.innerHTML = "";
    var added = {};
    // The heap grows while boxes render (a list of lists), so walk it live.
    for (var k = 0; k < heap.order.length; k += 1) {
      var oid = heap.order[k];
      if (added[oid]) continue;
      added[oid] = true;
      el.objects.appendChild(objectBox(heap.map[oid], heap));
    }
    if (!heap.order.length) el.objects.appendChild(make("div", "tv-none-yet", "no lists, dicts or objects yet"));
  }

  function drawArrows() {
    var svg = el.svg;
    var inner = el.inner;
    var box = inner.getBoundingClientRect();
    svg.setAttribute("width", inner.scrollWidth);
    svg.setAttribute("height", inner.scrollHeight);
    var paths = '<defs><marker id="tv-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#1a1a1a"/></marker></defs>';
    Array.prototype.forEach.call(inner.querySelectorAll(".tv-ptr"), function (dot) {
      var target = inner.querySelector('.tv-obj[data-oid="' + dot.getAttribute("data-target") + '"]');
      if (!target) return;
      var a = dot.getBoundingClientRect();
      var b = target.getBoundingClientRect();
      var x1 = a.left + a.width / 2 - box.left + inner.scrollLeft;
      var y1 = a.top + a.height / 2 - box.top + inner.scrollTop;
      var x2 = b.left - box.left + inner.scrollLeft - 1;
      var y2 = b.top + 13 - box.top + inner.scrollTop;
      var reach = Math.max(34, Math.abs(x2 - x1) / 2);
      paths += '<path d="M' + x1 + " " + y1 + " C" + (x1 + reach) + " " + y1 + " " + (x2 - reach) + " " + y2 + " " + x2 + " " + y2 +
        '" fill="none" stroke="#1a1a1a" stroke-width="1.6" marker-end="url(#tv-head)"/>';
    });
    svg.innerHTML = paths;
  }

  function render() {
    var trace = state.trace;
    if (!trace) return;
    var step = state.steps[state.i];
    var total = state.steps.length;

    // code arrows
    Array.prototype.forEach.call(el.code.children, function (row) {
      var line = Number(row.getAttribute("data-line"));
      var isNext = step.next === line;
      var isExec = step.exec === line && !isNext;
      row.className = row.className.replace(/ tv-(next|exec)\b/g, "") + (isNext ? " tv-next" : isExec ? " tv-exec" : "");
      row.firstChild.textContent = isNext ? "➜" : isExec ? "➜" : "";
    });
    var focus = el.code.querySelector(".tv-next") || el.code.querySelector(".tv-exec");
    if (focus) {
      var top = focus.offsetTop;
      if (top < el.code.scrollTop + 20 || top > el.code.scrollTop + el.code.clientHeight - 40)
        el.code.scrollTop = Math.max(0, top - el.code.clientHeight / 2);
    }

    // status + controls
    el.status.innerHTML = "<b>Step " + (state.i + 1) + "</b> of " + total;
    var note = "";
    if (step.kind === "done") note = "Done running (" + (total - 1) + " steps)";
    else if (step.kind === "error") note = "Program stopped by an uncaught exception";
    else if (step.kind === "return") note = "Returning to the caller";
    else if (state.i === total - 1 && trace.truncated) note = "Trace stopped at " + (trace.steps || []).length + " steps — use a smaller input to see the end";
    el.note.textContent = note;
    el.note.className = "tv-note" + (step.kind === "error" ? " tv-note-bad" : "");
    el.slider.max = String(Math.max(0, total - 1));
    el.slider.value = String(state.i);
    el.first.disabled = el.prev.disabled = state.i === 0;
    el.next.disabled = el.last.disabled = state.i >= total - 1;

    // output
    var text = (trace.stdout || "").slice(0, step.out);
    el.out.textContent = text;
    el.out.parentNode.scrollTop = el.out.parentNode.scrollHeight;
    if (step.kind === "error" && step.error) {
      el.error.textContent = step.error;
      el.error.classList.remove("tv-hide");
    } else {
      el.error.classList.add("tv-hide");
    }

    // frames + objects (+ pointer arrows once laid out)
    var heap = { map: {}, order: [] };
    renderFrames(step, heap);
    renderObjects(heap);
    window.requestAnimationFrame(drawArrows);
  }

  function go(index) {
    if (!state.steps.length) return;
    state.i = Math.max(0, Math.min(state.steps.length - 1, index));
    render();
  }

  // ── host surface ─────────────────────────────────────────────────────────
  function setStatus(kind, text) {
    if (!el.pill) return;
    el.pill.className = "lab-status tv-pill tv-pill-" + kind;
    el.pill.textContent = text;
  }

  function show(raw) {
    var trace = JSON.parse(raw);
    state.trace = trace;
    state.steps = buildSteps(trace);
    state.i = 0;
    root.classList.remove("tv-empty-state");
    if (!state.steps.length) {
      // Nothing ran (bad arguments, syntax error): show the code and the reason.
      state.steps = [{ kind: "error", next: trace.error_line || null, exec: null, stack: [{ fn: "<module>", line: null, vars: {} }], out: 0, error: trace.error }];
    }
    renderCode(trace);
    var count = (trace.steps || []).length;
    if (trace.error) setStatus("err", "Stopped — " + trace.error);
    else setStatus("ok", "Traced — " + count + (trace.truncated ? "+" : "") + " steps");
    render();
  }

  window.PyverseLab = {
    show: show,
    setStatus: setStatus,
    setMode: function () {},
    retrace: null, // the host assigns this; Ctrl/⌘+Enter calls it
  };

  // ── input ────────────────────────────────────────────────────────────────
  el.first.addEventListener("click", function () { go(0); });
  el.prev.addEventListener("click", function () { go(state.i - 1); });
  el.next.addEventListener("click", function () { go(state.i + 1); });
  el.last.addEventListener("click", function () { go(state.steps.length - 1); });
  el.slider.addEventListener("input", function () { go(Number(el.slider.value)); });
  root.addEventListener("keydown", function (event) {
    if (event.target && /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName) && event.target !== el.slider) return;
    if (event.key === "ArrowRight") go(state.i + 1);
    else if (event.key === "ArrowLeft") go(state.i - 1);
    else if (event.key === "Home") go(0);
    else if (event.key === "End") go(state.steps.length - 1);
    else if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      if (window.PyverseLab.retrace) window.PyverseLab.retrace();
    } else return;
    event.preventDefault();
  });
  if (window.ResizeObserver) new ResizeObserver(function () { if (state.trace) drawArrows(); }).observe(el.inner);
  window.addEventListener("resize", function () { if (state.trace) drawArrows(); });

  setStatus("busy", "Waiting for the Python runtime…");
})();
