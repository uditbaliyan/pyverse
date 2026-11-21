/* Instant-feedback quiz questions: click an option, see right/wrong and why.
 * Progress ("solved" = answered correctly at least once) is kept in
 * localStorage under pv:drillquiz:solved. No dependencies. */
(() => {
  "use strict";
  const KEY = "pv:drillquiz:solved";
  const read = () => {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; }
  };
  const write = (value) => {
    try { localStorage.setItem(KEY, JSON.stringify(value)); } catch { /* private mode */ }
  };

  const progress = () => {
    const done = read();
    document.querySelectorAll("[data-page-progress]").forEach((node) => {
      const slugs = (node.dataset.slugs || "").split(",").filter(Boolean);
      node.textContent = `${slugs.filter((s) => done[s]).length} of ${slugs.length} solved on this page`;
    });
  };

  const mount = (item) => {
    const opts = [...item.querySelectorAll(".pv-q__opt")];
    const result = item.querySelector(".pv-q__result");
    const verdict = item.querySelector(".pv-q__verdict");
    const retry = item.querySelector(".pv-q__retry");

    const reset = () => {
      opts.forEach((b) => {
        b.disabled = false;
        b.removeAttribute("aria-pressed");
        b.classList.remove("is-right", "is-wrong", "is-answer");
      });
      result.hidden = true;
      opts[0]?.focus();
    };

    opts.forEach((button) => {
      button.addEventListener("click", () => {
        const right = button.dataset.correct === "1";
        opts.forEach((b) => {
          b.disabled = true;
          if (b.dataset.correct === "1") b.classList.add("is-answer");
        });
        button.setAttribute("aria-pressed", "true");
        button.classList.add(right ? "is-right" : "is-wrong");
        verdict.textContent = right ? "Correct." : "Not quite. The right answer is highlighted.";
        verdict.dataset.kind = right ? "ok" : "bad";
        result.hidden = false;
        if (right) {
          const done = read();
          done[item.dataset.slug] = true;
          write(done);
          progress();
        }
      });
    });
    retry.addEventListener("click", reset);
  };

  const start = () => {
    document.querySelectorAll("[data-qitem]").forEach(mount);
    progress();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
