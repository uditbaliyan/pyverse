/* Shared browse behaviour for the Practice surfaces (spec §2, §3, §4, §7).
 *
 * The Landing table, Sheet trees and Track lists all read the same IndexedDB
 * progress store and render status with the same icons, so a problem solved on
 * its own page shows as solved everywhere.
 */
window.PyverseBrowse = (function () {
  const DIFFICULTY_RANK = { easy: 0, medium: 1, hard: 2 };
  const STATUS_RANK = { solved: 0, attempted: 1, todo: 2 };
  const state = {
    difficulty: new Set(),
    topic: "",
    status: "all",
    query: "",
    companies: "",
    patterns: "",
    techniques: "",
    sort: "default",
    asc: true,
  };

  function statusIcon(status) {
    if (status === "solved") return "✓";
    if (status === "attempted") return "◐";
    return "○";
  }

  async function statusMap() {
    if (!window.PyverseProgress) return {};
    try {
      return await window.PyverseProgress.statusMap();
    } catch (err) {
      return {};
    }
  }

  /** Tag every [data-slug] element with its status and fill progress widgets. */
  async function decorate(map) {
    const statuses = map || (await statusMap());

    document.querySelectorAll("[data-slug]").forEach((el) => {
      const status = statuses[el.dataset.slug] || "todo";
      el.dataset.status = status;
      const icon = el.querySelector("[data-status-icon]");
      if (icon) icon.textContent = statusIcon(status);
    });

    document.querySelectorAll("[data-progress-scope]").forEach((scope) => {
      const rows = Array.from(scope.querySelectorAll("[data-slug]"));
      const solved = rows.filter((r) => r.dataset.status === "solved").length;
      const total = rows.length;
      const pct = total ? Math.round((solved / total) * 100) : 0;

      const bar = scope.querySelector("[data-progress-bar]");
      if (bar) bar.style.width = pct + "%";

      const label = scope.querySelector("[data-progress-label]");
      if (label) label.textContent = solved + "/" + total;

      const dots = scope.querySelector("[data-progress-dots]");
      if (dots) {
        dots.innerHTML = "";
        for (let i = 0; i < total; i += 1) {
          const dot = document.createElement("span");
          dot.className = "pe-dot" + (i < solved ? " on" : "");
          dots.appendChild(dot);
        }
      }
    });

    document.querySelectorAll("[data-progress-ring]").forEach((ring) => {
      const scope = ring.closest("[data-progress-scope]") || document;
      const rows = Array.from(scope.querySelectorAll("[data-slug]"));
      const solved = rows.filter((r) => r.dataset.status === "solved").length;
      const pct = rows.length ? Math.round((solved / rows.length) * 100) : 0;
      ring.style.setProperty("--pct", pct);
      ring.dataset.label = pct + "%";
      ring.setAttribute("aria-label", pct + "% complete");
    });

    return statuses;
  }

  /** "Continue where you left off": first unsolved problem in tree order. */
  async function initContinue(map) {
    const button = document.querySelector("[data-continue]");
    if (!button) return;
    const statuses = map || (await statusMap());
    const next = Array.from(document.querySelectorAll("[data-slug]")).find(
      (el) => (statuses[el.dataset.slug] || "todo") !== "solved",
    );
    if (!next) {
      button.classList.add("pe-hidden");
      return;
    }
    const link = next.querySelector("a") || next;
    button.href = link.getAttribute("href") || link.href;
    button.textContent = "Continue: " + (next.dataset.title || next.textContent.trim());
  }

  function fillStats(rows) {
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };
    const count = (fn) => rows.filter(fn).length;

    set("stat-solved", count((r) => r.dataset.status === "solved"));
    set("stat-attempted", count((r) => r.dataset.status === "attempted"));
    set("stat-total", rows.length);
    ["easy", "medium", "hard"].forEach((level) => {
      set(
        "stat-" + level,
        count((r) => r.dataset.difficulty === level && r.dataset.status === "solved"),
      );
    });

    // Quizzes are progress too (Quiz Suite): counted separately, because the
    // challenge breakdown above is per-difficulty.
    const quizCards = Array.from(document.querySelectorAll('a.pe-card[href^="/practice/quiz/"]'));
    if (document.getElementById("stat-quizzes")) {
      set("stat-quizzes", quizCards.filter((card) => card.dataset.status === "solved").length);
      set("stat-quiz-total", quizCards.length);
    }

    const tracked = rows.filter((r) => r.dataset.status !== "todo").length;
    const cta = document.getElementById("stat-cta");
    if (cta) cta.classList.toggle("pe-hidden", tracked > 0);
  }

  async function fillStreak() {
    const el = document.getElementById("stat-streak");
    if (!el || !window.PyverseProgress) return;
    try {
      el.textContent = await window.PyverseProgress.streak();
    } catch (err) {
      el.textContent = "0";
    }
  }

  function axisValues(row, axis) {
    return (row.dataset[axis] || "").split(",").filter(Boolean);
  }

  function matches(row) {
    if (state.difficulty.size && !state.difficulty.has(row.dataset.difficulty)) return false;
    if (state.topic && row.dataset.topic !== state.topic) return false;
    if (state.status !== "all" && row.dataset.status !== state.status) return false;
    if (state.companies && !axisValues(row, "companies").includes(state.companies)) return false;
    if (state.patterns && !axisValues(row, "patterns").includes(state.patterns)) return false;
    if (state.techniques && !axisValues(row, "techniques").includes(state.techniques)) return false;
    if (state.query) {
      const haystack = (row.dataset.title + " " + (row.dataset.topic || "")).toLowerCase();
      if (!haystack.includes(state.query.toLowerCase())) return false;
    }
    return true;
  }

  function compare(a, b) {
    if (state.sort === "title") return a.dataset.title.localeCompare(b.dataset.title);
    if (state.sort === "difficulty") {
      return DIFFICULTY_RANK[a.dataset.difficulty] - DIFFICULTY_RANK[b.dataset.difficulty];
    }
    if (state.sort === "status") {
      return STATUS_RANK[a.dataset.status] - STATUS_RANK[b.dataset.status];
    }
    return 0;
  }

  function initLanding() {
    const table = document.querySelector("[data-practice-table]");
    if (!table) return;
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr[data-slug]"));
    if (!rows.length) return;
    state.sort = table.dataset.defaultSort || "default";

    const apply = () => {
      const visible = rows.filter(matches);
      if (state.sort !== "default") {
        const dir = state.asc ? 1 : -1;
        visible
          .slice()
          .sort((a, b) => compare(a, b) * dir)
          .forEach((row) => tbody.appendChild(row));
      } else {
        rows.forEach((row) => tbody.appendChild(row));
      }
      rows.forEach((row) => row.classList.toggle("pe-hidden", !matches(row)));

      const countEl = document.getElementById("table-count");
      if (countEl) {
        countEl.textContent =
          visible.length === rows.length
            ? rows.length + " problems"
            : visible.length + " of " + rows.length + " problems";
      }
      table.querySelectorAll("th[data-sort]").forEach((th) => {
        if (th.dataset.sort === state.sort) {
          th.setAttribute("aria-sort", state.asc ? "ascending" : "descending");
        } else {
          th.removeAttribute("aria-sort");
        }
      });
    };

    document.querySelectorAll("[data-difficulty-chip]").forEach((chip) => {
      chip.addEventListener("click", () => {
        const level = chip.dataset.difficultyChip;
        const pressed = chip.getAttribute("aria-pressed") === "true";
        chip.setAttribute("aria-pressed", pressed ? "false" : "true");
        if (pressed) state.difficulty.delete(level);
        else state.difficulty.add(level);
        apply();
      });
    });

    const topicFilter = document.getElementById("filter-topic");
    if (topicFilter) {
      topicFilter.addEventListener("change", () => {
        state.topic = topicFilter.value;
        apply();
      });
    }

    const statusFilter = document.getElementById("filter-status");
    if (statusFilter) {
      statusFilter.addEventListener("change", () => {
        state.status = statusFilter.value;
        apply();
      });
    }

    [
      ["filter-company", "companies"],
      ["filter-pattern", "patterns"],
      ["filter-technique", "techniques"],
    ].forEach(([elementId, axis]) => {
      const select = document.getElementById(elementId);
      if (!select) return;
      select.addEventListener("change", () => {
        state[axis] = select.value;
        apply();
      });
    });

    const search = document.getElementById("filter-q");
    if (search) {
      search.addEventListener("input", () => {
        state.query = search.value.trim();
        apply();
      });
    }

    table.querySelectorAll("th[data-sort]").forEach((th) => {
      th.querySelector("button").addEventListener("click", () => {
        const key = th.dataset.sort;
        if (state.sort === key) state.asc = !state.asc;
        else {
          state.sort = key;
          state.asc = true;
        }
        apply();
      });
    });

    const clear = document.getElementById("filter-clear");
    if (clear) {
      clear.addEventListener("click", () => {
        state.difficulty.clear();
        state.topic = "";
        state.status = "all";
        state.query = "";
        state.companies = "";
        state.patterns = "";
        state.techniques = "";
        document
          .querySelectorAll("[data-difficulty-chip]")
          .forEach((chip) => chip.setAttribute("aria-pressed", "false"));
        ["filter-topic", "filter-status", "filter-company", "filter-pattern", "filter-technique"].forEach((id) => {
          const el = document.getElementById(id);
          if (el) el.value = id === "filter-status" ? "all" : "";
        });
        if (search) search.value = "";
        apply();
      });
    }

    return decorate().then((map) => {
      fillStats(rows);
      fillStreak();
      apply();
      return map;
    });
  }

  // Sheets: collapse/expand categories, remembering the choice per sheet.
  function initTree() {
    const key = "pyverse_tree_" + (document.body.dataset.treeKey || location.pathname);
    let collapsed = {};
    try {
      collapsed = JSON.parse(localStorage.getItem(key) || "{}");
    } catch (err) {
      collapsed = {};
    }

    document.querySelectorAll("[data-tree-head]").forEach((head) => {
      const id = head.dataset.treeHead;
      const body = document.querySelector('[data-tree-body="' + id + '"]');
      if (!body) return;

      const setState = (isCollapsed) => {
        body.classList.toggle("collapsed", isCollapsed);
        head.querySelector(".pe-caret").textContent = isCollapsed ? "▸" : "▾";
        head.setAttribute("aria-expanded", String(!isCollapsed));
      };

      setState(Boolean(collapsed[id]));
      head.addEventListener("click", () => {
        const next = !body.classList.contains("collapsed");
        setState(next);
        collapsed[id] = next;
        try {
          localStorage.setItem(key, JSON.stringify(collapsed));
        } catch (err) {
          /* storage full or blocked: collapse state is a nicety, not state */
        }
      });
    });
  }

  async function init() {
    const map = await decorate();
    if (document.querySelector("[data-practice-table]")) {
      initLanding();
    } else if (document.getElementById("stat-total")) {
      // Track pages: same stats strip, no filter bar to bind.
      fillStats(Array.from(document.querySelectorAll("[data-slug]")));
      fillStreak();
    }
    initTree();
    initContinue(map);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  return { decorate, statusMap, init, initLanding, initTree };
})();
