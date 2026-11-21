/* Parsons puzzles: build the program by placing, ordering and indenting lines.
 * No dependencies. Click/tap/keyboard only (every control is a <button>), so it
 * works on phones and for keyboard users. Line text is set with textContent. */
(() => {
  "use strict";
  const KEY = "pv:parsons:solved";
  const INDENT_PX = 22;
  const MAX_INDENT = 6;

  const read = () => {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; }
  };
  const write = (value) => {
    try { localStorage.setItem(KEY, JSON.stringify(value)); } catch { /* private mode */ }
  };

  const el = (tag, props = {}, ...kids) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "text") node.textContent = v;
      else if (k === "class") node.className = v;
      else if (k.startsWith("data-") || k.startsWith("aria-")) node.setAttribute(k, v);
      else node[k] = v;
    }
    kids.forEach((kid) => node.append(kid));
    return node;
  };

  const shuffled = (items) => {
    const out = items.slice();
    for (let attempt = 0; attempt < 5; attempt++) {
      for (let i = out.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [out[i], out[j]] = [out[j], out[i]];
      }
      if (out.some((line, i) => line !== items[i]) || out.length < 2) break;
    }
    return out;
  };

  const progress = () => {
    const done = read();
    document.querySelectorAll("[data-page-progress]").forEach((node) => {
      const slugs = (node.dataset.slugs || "").split(",").filter(Boolean);
      const solved = slugs.filter((s) => done[s]).length;
      node.textContent = `${solved} of ${slugs.length} solved on this page`;
    });
  };

  const mount = (root) => {
    const payload = JSON.parse(document.getElementById(root.dataset.payload).textContent);
    const lines = payload.lines;
    const byId = Object.fromEntries(lines.map((l) => [l.id, l]));
    const solution = lines.filter((l) => !l.distractor);
    const host = root.querySelector(".pv-parsons__mount");
    const state = { pool: [], answer: [], marks: {}, done: !!read()[payload.id] };

    const reset = () => {
      state.pool = shuffled(lines).map((l) => l.id);
      state.answer = [];
      state.marks = {};
    };
    reset();

    const status = el("span", { class: "pv-status", role: "status", "aria-live": "polite" });
    const setStatus = (text, kind = "") => {
      status.textContent = text;
      status.dataset.kind = kind;
    };

    const rowButton = (label, aria, onClick, id, act) =>
      el("button", { type: "button", text: label, "aria-label": aria, onclick: onClick, "data-id": id, "data-act": act });

    let refocus = null;
    const render = () => {
      host.replaceChildren();
      const pool = el("ul", { class: "pv-list", "aria-label": "Available lines" });
      state.pool.forEach((id) => {
        pool.append(el("li", { class: "pv-line" },
          el("code", { text: byId[id].text }),
          rowButton("Add →", `Add line: ${byId[id].text}`, () => {
            state.pool = state.pool.filter((x) => x !== id);
            const last = state.answer[state.answer.length - 1];
            state.answer.push({ id, indent: last ? last.indent : 0 });
            state.marks = {};
            setStatus("");
            render();
          }, id, "add")));
      });
      const answer = el("ol", { class: "pv-list", "aria-label": "Your program" });
      state.answer.forEach((row, i) => {
        const line = byId[row.id];
        const mark = state.marks[row.id];
        const item = el("li", { class: "pv-line", "data-state": mark ? mark.state : "" });
        item.style.marginLeft = `${row.indent * INDENT_PX}px`;
        item.append(el("code", { text: line.text }));
        const move = (delta) => () => {
          const j = i + delta;
          if (j < 0 || j >= state.answer.length) return;
          [state.answer[i], state.answer[j]] = [state.answer[j], state.answer[i]];
          state.marks = {};
          refocus = `[data-id="${row.id}"][data-act="${delta < 0 ? "up" : "down"}"]`;
          render();
        };
        const dent = (delta) => () => {
          row.indent = Math.max(0, Math.min(MAX_INDENT, row.indent + delta));
          state.marks = {};
          refocus = `[data-id="${row.id}"][data-act="${delta < 0 ? "out" : "in"}"]`;
          render();
        };
        item.append(
          rowButton("↑", `Move up: ${line.text}`, move(-1), row.id, "up"),
          rowButton("↓", `Move down: ${line.text}`, move(1), row.id, "down"),
          rowButton("⇤", `Indent less: ${line.text}`, dent(-1), row.id, "out"),
          rowButton("⇥", `Indent more: ${line.text}`, dent(1), row.id, "in"),
          rowButton("✕", `Remove: ${line.text}`, () => {
            state.answer.splice(i, 1);
            state.pool.push(row.id);
            state.marks = {};
            setStatus("");
            render();
          }, row.id, "remove"));
        if (mark && mark.note) item.append(el("span", { class: "pv-fb", text: mark.note }));
        answer.append(item);
      });
      const poolCol = el("div", { class: "pv-col" }, el("h3", { text: "Lines" }), pool);
      const answerCol = el("div", { class: "pv-col" }, el("h3", { text: "Your program" }), answer);
      const actions = el("div", { class: "pv-actions" },
        el("button", { type: "button", class: "primary", text: "Check", onclick: check }),
        el("button", { type: "button", text: "Reset", onclick: () => { reset(); setStatus(""); render(); } }),
        el("button", { type: "button", text: "Show solution", onclick: reveal }),
        status);
      host.append(poolCol, answerCol, actions);
      if (refocus) { host.querySelector(refocus)?.focus(); refocus = null; }
    };

    const check = () => {
      state.marks = {};
      let wrong = 0;
      state.answer.forEach((row, i) => {
        const line = byId[row.id];
        const want = solution[i];
        if (line.distractor) {
          wrong++;
          state.marks[row.id] = { state: "bad", note: line.feedback || "This line does not belong." };
        } else if (want && line.text === want.text && row.indent === want.indent) {
          state.marks[row.id] = { state: "ok", note: "" };
        } else if (want && line.text === want.text) {
          wrong++;
          state.marks[row.id] = { state: "bad", note: `Right line, wrong indent. ${line.feedback || ""}`.trim() };
        } else {
          wrong++;
          state.marks[row.id] = { state: "bad", note: `Wrong place. ${line.feedback || ""}`.trim() };
        }
      });
      const missing = solution.length - state.answer.filter((r) => !byId[r.id].distractor).length;
      if (!wrong && !missing && state.answer.length === solution.length) {
        const done = read();
        done[payload.id] = true;
        write(done);
        setStatus("Correct. Well done.", "ok");
        progress();
      } else if (missing > 0) {
        setStatus(`${wrong} line${wrong === 1 ? "" : "s"} wrong, ${missing} still to place.`, "bad");
      } else {
        setStatus(`${wrong} line${wrong === 1 ? "" : "s"} wrong.`, "bad");
      }
      render();
    };

    const reveal = () => {
      state.answer = solution.map((l) => ({ id: l.id, indent: l.indent }));
      state.pool = lines.filter((l) => l.distractor).map((l) => l.id);
      state.marks = {};
      setStatus("Solution shown. Reset to try again.", "");
      render();
    };

    render();
  };

  const start = () => {
    document.querySelectorAll("[data-parsons]").forEach(mount);
    progress();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
