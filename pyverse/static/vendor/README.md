# Vendored browser assets

Pinned third-party files served from this site instead of a CDN, so Practice and
Labs keep working when a CDN is down. Do not edit by hand: change the version in
`utility/vendor_assets.py`, run it, and see `docs/howto.rst` ("Updating vendored
assets").

| Asset | Version | Licence | Upstream |
|---|---|---|---|
| Pyodide (core, stdlib only) | 0.27.7 | MPL-2.0 | https://github.com/pyodide/pyodide |
| CodeMirror 5 | 5.65.17 | MIT (see `codemirror/5.65.17/LICENSE`) | https://github.com/codemirror/codemirror5 |
| @viz-js/viz | 3.11.0 | MIT (bundles Graphviz, EPL-2.0) | https://github.com/mdaines/viz-js |

Not vendored: Tailwind play CDN, Alpine, Mermaid, Lucide and Google Fonts.
PyScript is no longer loaded by any page.
