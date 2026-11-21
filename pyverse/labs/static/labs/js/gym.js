/* Gym page controller. No localStorage/sessionStorage/cookies/network writes: by design. */
(() => {
  const D = JSON.parse(document.getElementById("gym-data").textContent);
  const $ = (id) => document.getElementById(id);
  const code = $("gym-code"), out = $("gym-out"), status = $("gym-status"), verdict = $("gym-verdict");
  const btns = ["gym-run", "gym-check"].map($);
  let worker = null, ready = null, pending = null, busy = false, pre = null;

  const say = (s) => (status.textContent = s);
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };
  const PRE = "whitespace-pre-wrap break-words font-mono text-sm p-3 border-2 border-black bg-white";

  function append(s, kind) {
    if (!pre || pre.dataset.kind !== kind) {
      pre = el("pre", PRE + (kind === "err" ? " text-red-700" : ""));
      pre.dataset.kind = kind;
      out.append(pre);
    }
    pre.textContent += s + "\n";
  }

  function boot() {
    say("Loading Python…");
    const w = (worker = new Worker(D.worker));
    ready = new Promise((res, rej) => {
      w.onmessage = ({ data: m }) => {
        if (w !== worker) return;
        if (m.t === "ready") { say(""); res(); }
        else if (m.t === "status") say(m.s);
        else if (m.t === "out" || m.t === "err") append(m.s, m.t);
        else if (m.t === "result" && pending) pending(m.r);
        else if (m.t === "fatal") { rej(new Error(m.s)); if (pending) pending({ fatal: m.s }); }
      };
      w.onerror = (e) => rej(new Error(e.message || "worker failed"));
    });
    ready.catch(() => {});
  }

  function showHtml(html) {
    const f = el("iframe", "w-full border-2 border-black bg-white");
    f.setAttribute("sandbox", "allow-same-origin"); // no scripts; same-origin only to measure height
    f.srcdoc = html;
    f.onload = () => { f.style.height = f.contentDocument.documentElement.scrollHeight + 8 + "px"; };
    out.append(f);
  }

  function render(r, check) {
    if (r.timeout) {
      out.append(el("pre", PRE + " text-red-700", `Timed out after ${D.timeout}s: infinite loop? Python was restarted.`));
      return;
    }
    if (r.fatal) { out.append(el("pre", PRE + " text-red-700", r.fatal)); return; }
    if (r.show) r.show.kind === "html" ? showHtml(r.show.body) : out.append(el("pre", PRE, r.show.body));
    for (const b64 of r.figs) {
      const img = el("img", "max-w-full border-2 border-black bg-white");
      img.src = "data:image/png;base64," + b64;
      img.alt = "figure";
      out.append(img);
    }
    if (!r.ok) out.append(el("pre", PRE + " text-red-700", r.err));
    if (check) {
      const good = r.passed === true;
      verdict.textContent = good ? "✓ Passed" : r.ok ? "✗ " + r.err : "✗ Fix the error above first";
      verdict.className = "font-bold " + (good ? "text-green-700" : "text-red-700");
    }
  }

  async function run(check) {
    if (busy) return;
    busy = true;
    btns.forEach((b) => (b.disabled = true));
    out.replaceChildren();
    pre = null;
    verdict.textContent = "";
    try {
      if (!worker) boot();
      await ready;
      say("Running…");
      const r = await new Promise((resolve) => {
        const t = setTimeout(() => { worker.terminate(); worker = null; resolve({ timeout: true }); }, D.timeout * 1000);
        pending = (m) => { clearTimeout(t); resolve(m); };
        worker.postMessage({ t: "run", setup: D.setup, code: code.value, check: check ? D.check : "" });
      });
      pending = null;
      render(r, check);
    } catch (e) {
      if (worker) worker.terminate();
      worker = null;
      out.append(el("pre", PRE + " text-red-700", "Could not start Python (offline?): " + e.message));
    } finally {
      busy = false;
      btns.forEach((b) => (b.disabled = false));
      say("");
    }
  }

  code.value = D.starter;
  $("gym-run").onclick = () => run(false);
  $("gym-check").onclick = () => run(true);
  $("gym-reset").onclick = () => { code.value = D.starter; out.replaceChildren(); verdict.textContent = ""; };
  code.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); run(e.shiftKey); }
    else if (e.key === "Tab") {
      e.preventDefault();
      const { selectionStart: s, selectionEnd: t } = code;
      code.setRangeText("    ", s, t, "end");
    }
  });

  let shown = 0;
  const hintBtn = $("gym-hint");
  if (!D.hints.length) hintBtn.hidden = true;
  hintBtn.onclick = () => {
    if (shown < D.hints.length) $("gym-hints").append(el("li", "", D.hints[shown++]));
    if (shown === D.hints.length) hintBtn.hidden = true;
  };
  const sol = $("gym-solution");
  if (D.solution) sol.querySelector("pre").textContent = D.solution; else sol.hidden = true;

  (window.requestIdleCallback || ((f) => setTimeout(f, 800)))(() => { if (!worker) boot(); });
})();
