/* PyVerse practice progress store (Practice spec §7).
 *
 * One IndexedDB store, shared by every Practice surface: the Landing table and
 * stats strip read it, Sheets and Tracks read it, and only the problem page
 * writes to it. `problem_status` is derived from `submissions` so it can be
 * recomputed rather than trusted — a drifted copy is never the source of truth.
 *
 * Everything degrades gracefully: if IndexedDB is unavailable (private mode,
 * blocked storage) the pages still render, they just show no progress.
 */
window.PyverseProgress = (function () {
  const DB_NAME = "pyverse_progress";
  const DB_VERSION = 1;
  const STORE_SUBMISSIONS = "submissions";
  const STORE_STATUS = "problem_status";
  const STORE_STREAK = "streak_meta";
  const STREAK_KEY = "single";

  let dbPromise = null;

  function open() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise((resolve, reject) => {
      if (!("indexedDB" in window)) {
        reject(new Error("IndexedDB unavailable"));
        return;
      }
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE_SUBMISSIONS)) {
          const store = db.createObjectStore(STORE_SUBMISSIONS, {
            keyPath: "id",
            autoIncrement: true,
          });
          store.createIndex("slug", "slug", { unique: false });
        }
        if (!db.objectStoreNames.contains(STORE_STATUS)) {
          db.createObjectStore(STORE_STATUS, { keyPath: "slug" });
        }
        if (!db.objectStoreNames.contains(STORE_STREAK)) {
          db.createObjectStore(STORE_STREAK, { keyPath: "id" });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    return dbPromise;
  }

  async function withStore(storeName, mode, fn) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, mode);
      const store = tx.objectStore(storeName);
      let result;
      try {
        result = fn(store);
      } catch (err) {
        reject(err);
        return;
      }
      tx.oncomplete = () => resolve(result && result.result !== undefined ? result.result : result);
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
  }

  function getRequest(store, key) {
    return new Promise((resolve, reject) => {
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function getAll(store) {
    return new Promise((resolve, reject) => {
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  function today() {
    return new Date().toISOString().slice(0, 10);
  }

  async function touchStreak() {
    const db = await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_STREAK, "readwrite");
      const store = tx.objectStore(STORE_STREAK);
      const req = store.get(STREAK_KEY);
      req.onsuccess = () => {
        const meta = req.result || {
          id: STREAK_KEY,
          last_active_date: null,
          current_streak: 0,
          longest_streak: 0,
        };
        const day = today();
        if (meta.last_active_date !== day) {
          const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
          meta.current_streak = meta.last_active_date === yesterday ? meta.current_streak + 1 : 1;
          meta.last_active_date = day;
          meta.longest_streak = Math.max(meta.longest_streak || 0, meta.current_streak);
        }
        store.put(meta);
      };
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  /** Record one Run/Submit attempt and refresh the derived status. */
  async function recordSubmission(entry) {
    const row = {
      slug: entry.slug,
      status: entry.status,
      latency: entry.latency || 0,
      title: entry.title || entry.slug,
      timestamp: Date.now(),
    };
    const db = await open();
    await new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_SUBMISSIONS, STORE_STATUS], "readwrite");
      tx.objectStore(STORE_SUBMISSIONS).add(row);

      const statusStore = tx.objectStore(STORE_STATUS);
      const existing = statusStore.get(row.slug);
      existing.onsuccess = () => {
        const previous = existing.result ? existing.result.status : "todo";
        let next = previous;
        if (row.status === "ACCEPTED") next = "solved";
        else if (previous !== "solved") next = "attempted";
        statusStore.put({ slug: row.slug, status: next, updated: row.timestamp });
      };

      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
    await touchStreak().catch(() => {});
    return true;
  }

  /** `{ slug: "solved" | "attempted" }` — absent means untouched. */
  async function statusMap() {
    try {
      const rows = await withStore(STORE_STATUS, "readonly", (store) => getAll(store));
      const list = Array.isArray(rows) ? rows : [];
      return Object.fromEntries(list.map((row) => [row.slug, row.status]));
    } catch (err) {
      return {};
    }
  }

  async function stats() {
    const map = await statusMap();
    const values = Object.values(map);
    return {
      available: true,
      solved: values.filter((s) => s === "solved").length,
      attempted: values.filter((s) => s === "attempted").length,
      tracked: values.length,
    };
  }

  async function streak() {
    try {
      const meta = await withStore(STORE_STREAK, "readonly", (store) =>
        getRequest(store, STREAK_KEY),
      );
      return (meta && meta.current_streak) || 0;
    } catch (err) {
      return 0;
    }
  }

  /** Most recent attempts for one problem, newest first. */
  async function submissionsFor(slug, limit = 20) {
    try {
      const rows = await withStore(STORE_SUBMISSIONS, "readonly", (store) =>
        getAll(store.index("slug")),
      );
      return (Array.isArray(rows) ? rows : [])
        .filter((row) => row.slug === slug)
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, limit);
    } catch (err) {
      return [];
    }
  }

  async function clear() {
    const db = await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(
        [STORE_SUBMISSIONS, STORE_STATUS, STORE_STREAK],
        "readwrite",
      );
      tx.objectStore(STORE_SUBMISSIONS).clear();
      tx.objectStore(STORE_STATUS).clear();
      tx.objectStore(STORE_STREAK).clear();
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  return { recordSubmission, statusMap, stats, streak, submissionsFor, clear };
})();
