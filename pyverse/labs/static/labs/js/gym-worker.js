/* Gym worker: private Pyodide interpreter per tab. Nothing is persisted.
   main -> {t:"init", version, packages} | {t:"run", setup, code, check}
   worker -> {t:"status"|"ready"|"out"|"err"|"result"|"fatal"} */
let py = null;
const loaded = new Set();
const post = (m) => self.postMessage(m);

const HELPERS = String.raw`
import ast, base64, io, json, sys, traceback

def _gym_show(o):
    if o is None or type(o).__module__.startswith("matplotlib"):
        return None
    h = getattr(o, "_repr_html_", None)
    if callable(h):
        try:
            s = h()
            if s:
                return {"kind": "html", "body": s}
        except Exception:
            pass
    return {"kind": "text", "body": repr(o)}

def _gym_exec(code, ns):
    tree = ast.parse(code, "<code>")
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = ast.Expression(tree.body.pop().value)
    exec(compile(tree, "<code>", "exec"), ns)
    if last is None:
        return None
    return _gym_show(eval(compile(last, "<code>", "eval"), ns))

def _gym_figs():
    plt = sys.modules.get("matplotlib.pyplot")
    out = []
    if plt:
        for n in plt.get_fignums():
            b = io.BytesIO()
            plt.figure(n).savefig(b, format="png", dpi=110, bbox_inches="tight")
            out.append(base64.b64encode(b.getvalue()).decode())
        plt.close("all")
    return out

def _gym_tb(e):
    keep = ("<code>", "<setup>", "<check>")
    fr = [f for f in traceback.extract_tb(e.__traceback__) if f.filename in keep]
    head = "Traceback (most recent call last):\n" + "".join(traceback.format_list(fr)) if fr else ""
    return head + "".join(traceback.format_exception_only(type(e), e))

def _gym_run(setup, code, check):
    plt = sys.modules.get("matplotlib.pyplot")
    if plt:
        plt.close("all")
    ns = {"__name__": "__main__"}
    want = bool(check.strip())
    res = {"ok": True, "passed": None, "show": None, "err": "", "figs": []}
    stage = "setup"
    try:
        if setup.strip():
            exec(compile(setup, "<setup>", "exec"), ns)
        stage = "code"
        res["show"] = _gym_exec(code, ns)
        if want:
            stage = "check"
            exec(compile(check, "<check>", "exec"), ns)
            res["passed"] = True
    except BaseException as e:
        res["passed"] = False if want else None
        if stage == "check" and isinstance(e, Exception):
            res["err"] = str(e) if isinstance(e, AssertionError) and str(e) else "Not quite: " + type(e).__name__ + ": " + str(e)
        else:
            res["ok"] = False
            res["err"] = _gym_tb(e)
    try:
        res["figs"] = _gym_figs()
    except Exception:
        pass
    return json.dumps(res)
`;

async function ensure(pkgs) {
  const need = pkgs.filter((p) => !loaded.has(p));
  if (!need.length) return;
  post({ t: "status", s: "Loading " + need.join(", ") + "…" });
  await py.loadPackage(need).catch(() => {});
  const missing = need.filter((p) =>
    py.runPython(`__import__("importlib.util").util.find_spec(${JSON.stringify(p)}) is None`)
  );
  if (missing.length) {
    await py.loadPackage("micropip");
    const mp = py.pyimport("micropip");
    for (const p of missing) await mp.install(p);
  }
  need.forEach((p) => loaded.add(p));
}

self.onmessage = async ({ data }) => {
  try {
    if (data.t === "init") {
      importScripts(`https://cdn.jsdelivr.net/pyodide/v${data.version}/full/pyodide.js`);
      py = await self.loadPyodide();
      py.setStdout({ batched: (s) => post({ t: "out", s }) });
      py.setStderr({ batched: (s) => post({ t: "err", s }) });
      py.runPython('import os\nos.environ["MPLBACKEND"] = "AGG"');
      await ensure(data.packages);
      py.runPython(HELPERS);
      post({ t: "ready" });
    } else if (data.t === "run") {
      const f = py.globals.get("_gym_run");
      const r = f(data.setup, data.code, data.check);
      f.destroy();
      post({ t: "result", r: JSON.parse(r) });
    }
  } catch (e) {
    post({ t: "fatal", s: String(e) });
  }
};
