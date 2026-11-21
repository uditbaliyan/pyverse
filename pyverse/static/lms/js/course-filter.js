/* Topic page course filter.
 *
 * The site is exported as static files: a topic page is one HTML file holding
 * every live course, and there is no server to read a query string. So the
 * filtering happens here. Nothing is required for the page to work: until this
 * script enables it the filter bar stays `hidden`, and without it the learner
 * simply sees every course and no control that cannot keep its promise.
 *
 * DOM contract
 *   [data-course-filter]        the bar, `hidden` in the markup
 *     [data-filter][data-value] toggle buttons. `data-filter` is "difficulty",
 *                               "type" or "free" and names the `data-*` attribute
 *                               to compare on each card; the buttons are the one
 *                               list of filters and values that exist.
 *     [data-filter-status]      live region: "Showing 2 of 5 courses"
 *   [data-course-grid] > [data-course][data-difficulty][data-type][data-free]
 *   [data-filter-empty]         shown when nothing matches; holds
 *                               [data-filter-clear]
 *
 * The active filters are mirrored into the query string with replaceState
 * (?difficulty=beginner&free=1) so a filtered view can be linked, and read back
 * on load. Unknown parameters and values are ignored.
 */
(function () {
  "use strict";

  var bar = document.querySelector("[data-course-filter]");
  var grid = document.querySelector("[data-course-grid]");
  if (!bar || !grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll("[data-course]"));
  var buttons = Array.prototype.slice.call(bar.querySelectorAll("[data-filter]"));
  var status = bar.querySelector("[data-filter-status]");
  var empty = document.querySelector("[data-filter-empty]");
  var clear = document.querySelector("[data-filter-clear]");

  var allowed = {};
  buttons.forEach(function (button) {
    var name = button.getAttribute("data-filter");
    (allowed[name] = allowed[name] || []).push(button.getAttribute("data-value"));
  });
  var names = Object.keys(allowed);
  var active = {};
  names.forEach(function (name) {
    active[name] = "";
  });

  function readQuery() {
    var params = new URLSearchParams(window.location.search);
    names.forEach(function (name) {
      var value = params.get(name);
      active[name] = allowed[name].indexOf(value) === -1 ? "" : value;
    });
  }

  function writeQuery() {
    var params = new URLSearchParams(window.location.search);
    names.forEach(function (name) {
      if (active[name]) params.set(name, active[name]);
      else params.delete(name);
    });
    var query = params.toString();
    try {
      window.history.replaceState(
        null,
        "",
        window.location.pathname + (query ? "?" + query : "") + window.location.hash,
      );
    } catch (error) {
      // e.g. a sandboxed frame: filtering still works, it just cannot be linked.
    }
  }

  function matches(card) {
    return names.every(function (name) {
      return !active[name] || card.getAttribute("data-" + name) === active[name];
    });
  }

  function render() {
    var shown = 0;
    cards.forEach(function (card) {
      var show = matches(card);
      card.hidden = !show;
      if (show) shown += 1;
    });
    buttons.forEach(function (button) {
      var on = active[button.getAttribute("data-filter")] === button.getAttribute("data-value");
      button.setAttribute("aria-pressed", on ? "true" : "false");
      button.classList.toggle("btn-secondary", !on);
    });
    if (empty) empty.hidden = shown !== 0;
    if (status) {
      var filtered = names.some(function (name) {
        return active[name];
      });
      status.textContent = filtered
        ? "Showing " + shown + " of " + cards.length + " courses"
        : cards.length + " courses";
    }
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var name = button.getAttribute("data-filter");
      var value = button.getAttribute("data-value");
      active[name] = active[name] === value ? "" : value;
      writeQuery();
      render();
    });
  });

  if (clear) {
    clear.addEventListener("click", function () {
      names.forEach(function (name) {
        active[name] = "";
      });
      writeQuery();
      render();
      // The empty-state button just disappeared; hand focus to the filters.
      buttons[0].focus();
    });
  }

  // Anything that throws before this point leaves the bar hidden: the learner
  // gets the plain list of every course rather than a half-working control.
  readQuery();
  render();
  bar.hidden = false;
})();
