/* LMS lesson progress — the course/lesson half of `PyverseProgress`.
 *
 * Lessons complete into the same IndexedDB store the practice surfaces read
 * (`js/pyverse-progress.js`), so one browser profile has one progress record
 * rather than one per half of the site. Nothing here is required for the page
 * to render: without the store, the course page shows no ticks and the lesson
 * page hides its controls instead of pretending a write happened.
 *
 * DOM contract
 *   course page  [data-course-progress][data-total]  + #course-progress-count,
 *                #course-progress-bar, and one [data-lesson-slug] row per
 *                lesson with an optional [data-lesson-state] slot inside.
 *   lesson page  #lesson-complete[data-lesson-slug][data-course-slug]
 *                [data-lesson-title], #lesson-complete-done, #lesson-undo, and
 *                an optional [data-lesson-list] whose [data-lesson-slug] links
 *                get marked too.
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
    document.querySelectorAll("[data-lesson-slug]").forEach(function (element) {
      // The lesson page's own control carries the slug too; it has its own
      // completed/not-completed state, so it is not a list row.
      if (element.id === "lesson-complete") return;
      var slug = element.getAttribute("data-lesson-slug");
      markElement(element, Boolean(map[slug]));
    });
  }

  function paintCourseProgress(map) {
    if (!courseBlock) return;
    var slugs = Array.prototype.map.call(
      courseBlock.querySelectorAll("[data-lesson-slug]"),
      function (element) {
        return element.getAttribute("data-lesson-slug");
      },
    );
    if (!slugs.length) return;
    var done = slugs.filter(function (slug) {
      return Boolean(map[slug]);
    }).length;
    var total = Number(courseBlock.getAttribute("data-total")) || slugs.length;
    var count = document.getElementById("course-progress-count");
    var bar = document.getElementById("course-progress-bar");
    if (count) count.textContent = done + " of " + total + " complete";
    if (bar) bar.style.width = ((done / total) * 100).toFixed(1) + "%";
  }

  function paintLessonButton(map) {
    if (!completeButton) return;
    var slug = completeButton.getAttribute("data-lesson-slug");
    var done = Boolean(map[slug]);
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

  if (completeButton) {
    completeButton.addEventListener("click", function () {
      var slug = completeButton.getAttribute("data-lesson-slug");
      completeButton.disabled = true;
      store
        .completeLesson({
          slug: slug,
          course: completeButton.getAttribute("data-course-slug") || "",
          title: completeButton.getAttribute("data-lesson-title") || slug,
        })
        .then(function () {
          return store.lessonMap();
        })
        .then(function (map) {
          completeButton.disabled = false;
          paint(map);
        })
        .catch(fail);
    });
  }

  var undo = document.getElementById("lesson-undo");
  if (undo && completeButton) {
    undo.addEventListener("click", function () {
      var slug = completeButton.getAttribute("data-lesson-slug");
      undo.disabled = true;
      store
        .uncompleteLesson(slug)
        .then(function () {
          return store.lessonMap();
        })
        .then(function (map) {
          undo.disabled = false;
          paint(map);
        })
        .catch(fail);
    });
  }
})();
