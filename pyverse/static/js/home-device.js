/* Home page: the device screen runs a live line-by-line trace.
 *
 * Progressive enhancement. The template ships a static fallback inside
 * [data-device-screen]; this script replaces it with a stepping trace and turns
 * the decorative controls on the device into real ones:
 *   left red button  -> previous step      right red button -> next step
 *   left grey pill   -> play / pause
 * With no JS the screen and controls simply stay as they were drawn.
 *
 * Content: if an editor filled in "Device code" in the CMS (#device-code), those
 * lines are shown with a moving highlight. Otherwise two built-in demo programs
 * run, each step carrying the values and output after that line executes.
 * All text is written with textContent, never innerHTML.
 */
(function () {
  "use strict";

  var screen = document.querySelector("[data-device-screen]");
  if (!screen) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* step = [line index, values, output?] shown after that line has run */
  var BUILTIN = [
    {
      name: "average",
      code: [
        "def average(nums):",
        "    total = 0",
        "    for n in nums:",
        "        total += n",
        "    return total / len(nums)",
        "average([1, 2, 3, 4])",
      ],
      steps: [
        [5, "nums=[1, 2, 3, 4]"], [1, "total=0"],
        [2, "n=1"], [3, "total=1"], [2, "n=2"], [3, "total=3"],
        [2, "n=3"], [3, "total=6"], [2, "n=4"], [3, "total=10"],
        [4, "total=10", "2.5"],
      ],
      values: true,
    },
    {
      name: "alias",
      code: ["a = [1, 2]", "b = a", "b.append(3)", "print(a)"],
      steps: [
        [0, "a=[1, 2]"], [1, "a is b -> True"],
        [2, "a=[1, 2, 3]"], [3, "a=[1, 2, 3]", "[1, 2, 3]"],
      ],
      values: true,
    },
  ];

  function readCustom() {
    var node = document.getElementById("device-code");
    if (!node) return null;
    var raw;
    try {
      raw = JSON.parse(node.textContent);
    } catch (e) {
      return null;
    }
    if (typeof raw !== "string") return null;
    var lines = raw.split(/\r?\n/).slice(0, 8);
    while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
    if (!lines.length) return null;
    return {
      name: "fn",
      code: lines,
      steps: lines.map(function (_, i) { return [i, ""]; }),
      values: false,
    };
  }

  var custom = readCustom();
  var PROGS = custom ? [custom] : BUILTIN;

  var pi = 0; /* program index */
  var si = 0; /* step index */
  var playing = !reduce;
  var visible = true;
  var timer = null;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function status(label, value) {
    var row = el("div", "pv-lcd-st");
    row.appendChild(el("b", null, label));
    row.appendChild(document.createTextNode(value));
    return row;
  }

  function draw() {
    var p = PROGS[pi];
    var s = p.steps[si];
    var frag = document.createDocumentFragment();

    frag.appendChild(el("div", "pv-lcd-hd", ">>> trace(" + p.name + ")"));
    var code = el("div", "pv-lcd-code");
    p.code.forEach(function (line, i) {
      code.appendChild(el("div", "pv-lcd-ln" + (i === s[0] ? " on" : ""), line + " "));
    });
    frag.appendChild(code);
    if (p.values) {
      frag.appendChild(status("values", s[1] || ""));
      frag.appendChild(status("output", s[2] || ""));
    }

    screen.replaceChildren(frag);
    screen.setAttribute("data-step", String(si + 1) + "/" + String(p.steps.length));
  }

  function step(d) {
    var n = PROGS[pi].steps.length;
    si += d;
    if (si >= n) si = 0;
    if (si < 0) si = n - 1;
    draw();
  }

  function nextProgram() {
    pi = (pi + 1) % PROGS.length;
    si = 0;
    draw();
  }

  function tick() {
    window.clearTimeout(timer);
    if (!playing || !visible || document.hidden) return;
    var last = si === PROGS[pi].steps.length - 1;
    timer = window.setTimeout(function () {
      if (last) {
        if (PROGS.length > 1) nextProgram();
        else { si = 0; draw(); }
      } else {
        step(1);
      }
      tick();
    }, last ? 2200 : 950);
  }

  /* ── controls: upgrade the decorative divs at runtime ── */
  var buttons = {};
  Array.prototype.forEach.call(document.querySelectorAll("[data-device-btn]"), function (b) {
    buttons[b.getAttribute("data-device-btn")] = b;
  });

  function label(b, text) {
    b.setAttribute("role", "button");
    b.setAttribute("tabindex", "0");
    b.setAttribute("aria-label", text);
    b.classList.add("pv-device-btn");
  }

  function activate(b, fn) {
    b.addEventListener("click", fn);
    b.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        fn();
      }
    });
  }

  function setPlaying(v) {
    playing = v;
    if (buttons.play) {
      buttons.play.setAttribute("aria-pressed", String(v));
      buttons.play.setAttribute("aria-label", v ? "Pause trace" : "Play trace");
      buttons.play.setAttribute("data-state", v ? "playing" : "paused");
    }
    tick();
  }

  if (buttons.prev) {
    label(buttons.prev, "Previous step");
    activate(buttons.prev, function () { step(-1); setPlaying(false); });
  }
  if (buttons.next) {
    label(buttons.next, "Next step");
    activate(buttons.next, function () { step(1); setPlaying(false); });
  }
  if (buttons.play) {
    label(buttons.play, "Pause trace");
    buttons.play.setAttribute("aria-pressed", String(playing));
    buttons.play.setAttribute("data-state", playing ? "playing" : "paused");
    activate(buttons.play, function () { setPlaying(!playing); });
  }

  /* Only run while on screen and the tab is in front. */
  document.addEventListener("visibilitychange", tick);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      tick();
    }).observe(screen);
  }

  screen.setAttribute("role", "group");
  screen.setAttribute("aria-label", "Live code trace");
  draw();
  tick();
})();
