/* Fills "n of N solved" into every [data-drill-slugs] element from localStorage
 * (the same key parsons.js writes). Idempotent: safe to load more than once. */
(() => {
  "use strict";
  if (window.__pvDrillProgress) return;
  window.__pvDrillProgress = true;
  const run = () => {
    let done = {};
    try { done = JSON.parse(localStorage.getItem("pv:parsons:solved")) || {}; } catch { /* ignore */ }
    document.querySelectorAll("[data-drill-slugs]").forEach((node) => {
      const slugs = node.dataset.drillSlugs.split(",").filter(Boolean);
      if (!slugs.length) return;
      const solved = slugs.filter((s) => done[s]).length;
      node.textContent = solved
        ? `${solved} of ${slugs.length} solved`
        : `${slugs.length} puzzle${slugs.length === 1 ? "" : "s"}`;
    });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
