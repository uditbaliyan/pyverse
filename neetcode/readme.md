
I am building a standalone browser-based LeetCode-style coding platform using:

* HTML
* TailwindCSS
* CodeMirror
* PyScript 
* Pyodide / WebAssembly
* Vanilla JavaScript [minimal]

The project is currently standalone/local-first and NOT connected to any backend. Later, I may extend it into a full backend-powered system (possibly Django[Django-distill]), but the architecture is fully frontend/browser-native.

I am thinking of using this architecture:

* PyScript + Pyodide workers (`type="py" worker"`) for code execution

The idea was:

* PyScript handles UI because it is lightweight and fast
* Pyodide handles arbitrary Python execution
* Everything runs locally in-browser

However, I encountered serious browser/runtime architecture problems.

# Current Problems

1. `file://` Origin & Worker Failures

---

Opening the HTML directly from the filesystem caused:

* cross-origin worker failures
* module import failures
* WASM loading issues
* PyScript runtime bootstrap failures

Example errors:

```text id="v9cbmn"
Refused to cross-origin redirects of the top-level worker script
```

```text id="2oq0pv"
Unsafe attempt to load URL file:///...
```

I now understand the app must be served through HTTP, for example:

```bash id="snffw6"
python -m http.server 8000
```

instead of opening HTML directly via `file://`.

2. Worker DOM Access Errors

---

Inside:

```html id="hxh52m"
<script type="py" worker>
```

I attempted:

```python id="4r7p84"
from pyscript import window, document
```

and tried updating UI state from the worker.

This caused:

```text id="p4w0zu"
AttributeError: Unable to use `window` or `document`
```

I now understand browser Web Workers cannot access:

* DOM
* window
* document
* CodeMirror
* canvas
* browser UI APIs

Workers are isolated execution threads.

3. PyScript Runtime Architecture Problems

---

I also used APIs similar to:

```js id="l5msq5"
pyscript.interpreter.run_harness(...)
```

which appear unstable or non-public in modern PyScript versions.

The architecture became brittle because:

* PyScript internals changed
* runtime APIs were unstable
* MicroPython and Pyodide runtimes conflicted
* JS bridge assumptions broke
* Worker/runtime communication became unreliable

# What I Need

Please redesign this into a production-grade standalone browser coding platform architecture.

# Requirements

## Frontend Stack

Use:

* HTML
* TailwindCSS
* Vanilla JavaScript
* CodeMirror
* Chart.js
* Pyodide

Avoid:

* PyScript runtime abstractions
* MicroPython DOM logic
* unstable runtime bridges

## Execution Requirements

Need:

* isolated Python execution
* async execution
* browser-based execution
* responsive UI
* sandboxed execution
* support for arbitrary LeetCode-style code
* local-first execution

Use:

* Pyodide inside a dedicated Web Worker

## Architecture Goals

The platform should support:

* multi-tab editor UI
* testcase runner
* submission system
* runtime benchmarks
* complexity visualization
* benchmark charts
* hints/editorials
* keyboard shortcuts
* responsive layout
* async worker execution
* large testcase handling
* browser-native execution

# What I Want From You

Please provide:

1. Correct browser architecture
2. Proper separation between:

   * UI thread
   * Worker thread
   * execution layer
3. Recommended folder structure
4. Recommended file structure
5. Worker communication pipeline
6. `postMessage` architecture
7. Pyodide worker implementation
8. Frontend execution flow
9. Recommended JS architecture
10. Security considerations
11. Performance considerations
12. Browser sandbox limitations
13. How to benchmark safely
14. How to avoid freezing the UI thread
15. How to structure CodeMirror integration
16. How to structure Chart.js updates
17. Recommended build/dev setup
18. How to later extend this into a backend-powered system

Also explain deeply:

* WHY the previous PyScript + MicroPython architecture failed
* WHY workers cannot access DOM APIs
* WHY Pyodide should live inside a dedicated worker
* WHY vanilla JavaScript should control the UI layer
* WHY browser-native worker architecture is more stable

The explanation should be technical, production-oriented, scalable, and suitable for building a real browser IDE/coding platform.
