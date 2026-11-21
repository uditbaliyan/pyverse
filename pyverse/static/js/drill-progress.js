/* Fills "n of N solved" into every [data-drill-slugs] element from localStorage
 * (the key in data-drill-store, which parsons.js / drill-quiz.js write). Idempotent: safe to load more than once. */
(() => {
  "use strict";
  if (window.__pvDrillProgress) return;
  window.__pvDrillProgress = true;
  const run = () => {
    const read = (key) => {
      try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; }
    };
    document.querySelectorAll("[data-drill-slugs]").forEach((node) => {
      const done = read(node.dataset.drillStore || "pv:parsons:solved");
      const slugs = node.dataset.drillSlugs.split(",").filter(Boolean);
      if (!slugs.length) return;
      const solved = slugs.filter((s) => done[s]).length;
      node.textContent = solved
        ? `${solved} of ${slugs.length} solved`
        : `${slugs.length} item${slugs.length === 1 ? "" : "s"}`;
    });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
