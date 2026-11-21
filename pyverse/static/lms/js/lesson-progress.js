/* LMS lesson progress — the course/lesson half of `PyverseProgress`.
 *
 * Lessons complete into the same IndexedDB store the practice surfaces read
 * (`js/pyverse-progress.js`), so one browser profile has one progress record
 * rather than one per half of the site. Nothing here is required for the page
 * to render: without the store, the course page shows no ticks and the lesson
 * page hides its controls instead of pretending a write happened.
 *
 * A lesson is identified by its `progress_key` (`LessonPage.progress_key`, the
 * topic/course/lesson slugs, e.g. "python/basics/introduction"), carried in
 * `data-lesson-key`. Never the bare lesson slug: slugs are only unique inside one
 * course, so two courses that both have an `introduction` lesson would share a
 * record. The key is stored in the `slug` field of the `lesson_status` store (its
 * keyPath), so the shared store needs no change.
 *
 * DOM contract
 *   course page  [data-course-progress][data-total]  + #course-progress-count,
 *                #course-progress-bar, and one [data-lesson-key] row per
 *                lesson with an optional [data-lesson-state] slot inside.
 *   lesson page  #lesson-complete[data-lesson-key][data-course-slug]
 *                [data-lesson-title], #lesson-complete-done, #lesson-undo, and
 *                an optional [data-lesson-list] whose [data-lesson-key] links
 *                get marked too.
 *   lesson page  ... plus [data-checkpoint][data-checkpoint-slug]
 *                (optional [data-checkpoint-required], [data-checkpoint-state]),
 *                #lesson-next, #lesson-gate-note. A required checkpoint gates the
 *                next-lesson link until its slug reads "solved" in
 *                `PyverseProgress`; an unreadable store never gates.
 */
(function () {
  "use strict";

  var store = window.PyverseProgress;
  var courseBlock = document.querySelector("[data-course-progress]");
  var completeButton = document.getElementById("lesson-complete");
  if (!store || (!courseBlock && !completeButton)) return;

  function storageAvailable() {
    return "indexedDB" in window;
  }

  function checkMark() {
    var span = document.createElement("span");
    span.className = "lesson-check";
    span.setAttribute("aria-hidden", "true");
    span.textContent = "✓";
    return span;
  }

  function markElement(element, done) {
    var slot = element.querySelector("[data-lesson-state]");
    var existing = slot ? slot.querySelector(".lesson-check") : null;
    if (done && !existing) {
      (slot || element).appendChild(checkMark());
    } else if (!done && existing) {
      existing.remove();
    }
    element.classList.toggle("lesson-done", Boolean(done));
  }

  function paintList(map) {
    document.querySelectorAll("[data-lesson-key]").forEach(function (element) {
      // The lesson page's own control carries the key too; it has its own
      // completed/not-completed state, so it is not a list row.
      if (element.id === "lesson-complete") return;
      var key = element.getAttribute("data-lesson-key");
      markElement(element, Boolean(map[key]));
    });
  }

  function paintCourseProgress(map) {
    if (!courseBlock) return;
    var keys = Array.prototype.map.call(
      courseBlock.querySelectorAll("[data-lesson-key]"),
      function (element) {
        return element.getAttribute("data-lesson-key");
      },
    );
    if (!keys.length) return;
    var done = keys.filter(function (key) {
      return Boolean(map[key]);
    }).length;
    var total = Number(courseBlock.getAttribute("data-total")) || keys.length;
    var count = document.getElementById("course-progress-count");
    var bar = document.getElementById("course-progress-bar");
    if (count) count.textContent = done + " of " + total + " complete";
    if (bar) bar.style.width = ((done / total) * 100).toFixed(1) + "%";
    paintContinue(courseBlock.querySelectorAll("[data-lesson-key]"), map);
  }

  // "Start learning" becomes "Continue learning" once some lessons are done and
  // lands on the first one that is not; with every lesson done it reads "Review
  // course" and points back at the first lesson. The original href/label are kept
  // on the element so undoing a lesson restores them.
  function paintContinue(rows, map) {
    var cta = document.querySelector("[data-course-cta] a");
    if (!cta || !rows.length) return;
    if (!cta.hasAttribute("data-start-href")) {
      cta.setAttribute("data-start-href", cta.getAttribute("href"));
      cta.setAttribute("data-start-label", cta.textContent.trim());
    }
    var remaining = Array.prototype.filter.call(rows, function (row) {
      return !map[row.getAttribute("data-lesson-key")];
    });
    var href = cta.getAttribute("data-start-href");
    var label = cta.getAttribute("data-start-label");
    if (remaining.length && remaining.length < rows.length) {
      href = remaining[0].getAttribute("href");
      label = "Continue learning";
    } else if (!remaining.length) {
      label = "Review course";
    }
    cta.setAttribute("href", href);
    cta.textContent = label;
  }

  function paintLessonButton(map) {
    if (!completeButton) return;
    var key = completeButton.getAttribute("data-lesson-key");
    var done = Boolean(map[key]);
    var donePanel = document.getElementById("lesson-complete-done");
    completeButton.classList.toggle("hidden", done);
    if (donePanel) {
      donePanel.classList.toggle("hidden", !done);
      donePanel.classList.toggle("flex", done);
    }
    document.documentElement.setAttribute("data-lesson-done", done ? "1" : "0");
  }

  function paint(map) {
    paintList(map);
    paintCourseProgress(map);
    paintLessonButton(map);
  }

  function fail() {
    // Storage blocked (private mode, denied permission): drop the controls
    // rather than offer a button that cannot keep its promise.
    if (completeButton) completeButton.classList.add("hidden");
    var block = document.querySelector("[data-lesson-progress]");
    if (block) block.classList.add("hidden");
  }

  if (!storageAvailable()) {
    fail();
    return;
  }

  store
    .lessonMap()
    .then(paint)
    .catch(fail);

  var undo = document.getElementById("lesson-undo");

  if (completeButton) {
    completeButton.addEventListener("click", function () {
      var key = completeButton.getAttribute("data-lesson-key");
      completeButton.disabled = true;
      store
        .completeLesson({
          slug: key, // the store's keyPath; holds the lesson key (see above)
          course: completeButton.getAttribute("data-course-slug") || "",
          title: completeButton.getAttribute("data-lesson-title") || key,
        })
        .then(function () {
          return store.lessonMap();
        })
        .then(function (map) {
          completeButton.disabled = false;
          paint(map);
          // "Mark complete" is hidden now; keep keyboard focus on a live control.
          if (undo) undo.focus();
        })
        .catch(fail);
    });
  }

  if (undo && completeButton) {
    undo.addEventListener("click", function () {
      var key = completeButton.getAttribute("data-lesson-key");
      undo.disabled = true;
      store
        .uncompleteLesson(key)
        .then(function () {
          return store.lessonMap();
        })
        .then(function (map) {
          undo.disabled = false;
          paint(map);
          completeButton.focus();
        })
        .catch(fail);
    });
  }

  var checkpoints = Array.prototype.slice.call(
    document.querySelectorAll("[data-checkpoint]"),
  );
  var nextLink = document.getElementById("lesson-next");
  var gateNote = document.getElementById("lesson-gate-note");

  function paintCheckpoints(map) {
    checkpoints.forEach(function (element) {
      var done = map[element.getAttribute("data-checkpoint-slug")] === "solved";
      element.setAttribute("data-checkpoint-done", done ? "1" : "0");
      var slot = element.querySelector("[data-checkpoint-state]");
      if (slot) slot.textContent = done ? "✓ Done" : "Not started";
      // The block ships with the ink/paper pair (`practice_embed.html`); swap it
      // for the done pair rather than adding both, so the same border/background
      // properties never compete.
      element.classList.toggle("border-ink", !done);
      element.classList.toggle("bg-bg-2", !done);
      element.classList.toggle("border-ok", done);
      element.classList.toggle("bg-ok-bg", done);
    });
  }

  function paintGate() {
    if (!nextLink) return;
    var unmet = checkpoints.filter(function (element) {
      return (
        element.hasAttribute("data-checkpoint-required") &&
        element.getAttribute("data-checkpoint-done") !== "1"
      );
    });
    var locked = unmet.length > 0;
    nextLink.setAttribute("aria-disabled", locked ? "true" : "false");
    nextLink.classList.toggle("opacity-40", locked);
    nextLink.classList.toggle("pointer-events-none", locked);
    if (!gateNote) return;
    gateNote.classList.toggle("hidden", !locked);
    if (locked) {
      gateNote.textContent =
        unmet.length === 1
          ? "Finish the required checkpoint above to unlock the next lesson."
          : "Finish the " + unmet.length + " required checkpoints above to unlock the next lesson.";
    }
  }

  if (checkpoints.length || nextLink) {
    if (nextLink) {
      nextLink.addEventListener("click", function (event) {
        if (nextLink.getAttribute("aria-disabled") === "true") event.preventDefault();
      });
    }
    store
      .readStatus()
      .then(function (map) {
        paintCheckpoints(map);
        paintGate();
      })
      .catch(function () {
        // Storage unreadable: never lock navigation on the strength of a failed
        // read.
        if (gateNote) gateNote.classList.add("hidden");
        if (nextLink) nextLink.removeAttribute("aria-disabled");
      });
  }
})();
