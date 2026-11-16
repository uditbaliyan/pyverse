/* Home page behaviour: the terminal Game Boy, the square-dot easter egg and the
 * aliasing figure.
 *
 * Progressive enhancement throughout. The template ships a static frame inside
 * [data-device-screen], an inert square and Game Boy buttons, and hidden
 * controls; this script brings them to life. With no JS the page is simply the
 * still version.
 *
 *   Screen    a line-by-line trace, one step every ~1s while on screen
 *   Controls  Back / Next line / Pause / Next program (the .pvh-ctl row) and
 *             the Game Boy's own buttons: left red = back, right red = next,
 *             left grey pill = play / pause
 *   Egg       pressing the red square after "VERSE" prints hello, world on the
 *             screen, drops confetti in the five colours and shows a toast
 *   Figure    the b = a / b = a.copy() toggle in the Labs section
 *
 * Content: if an editor filled in "Device code" in the CMS (#device-code) those
 * lines are shown with a moving highlight; otherwise two built-in programs run,
 * each step carrying the values and output after that line executes. All text is
 * written with textContent, never innerHTML.
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
      title: "Sum a list in a loop",
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
      title: "Two names, one list",
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
      title: "Live trace",
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
  var eggTimer = null;

  var titleEl = document.querySelector("[data-device-title]");
  var stepEl = document.querySelector("[data-device-step]");
  var progEl = document.querySelector("[data-device-progress]");

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function status(label, value) {
    var row = el("div", "st");
    row.appendChild(el("b", null, label));
    row.appendChild(document.createTextNode(value));
    return row;
  }

  function chrome(title, stepText, fill) {
    if (titleEl) titleEl.textContent = title;
    if (stepEl) stepEl.textContent = stepText;
    if (progEl) progEl.style.setProperty("--w", String(fill));
  }

  function draw() {
    var p = PROGS[pi];
    var s = p.steps[si];
    var frag = document.createDocumentFragment();

    frag.appendChild(el("div", "hd", ">>> trace(" + p.name + ")"));
    var code = el("div", "code");
    p.code.forEach(function (line, i) {
      code.appendChild(el("div", "ln" + (i === s[0] ? " on" : ""), line + " "));
    });
    frag.appendChild(code);
    if (p.values) {
      frag.appendChild(status("values", s[1] || ""));
      frag.appendChild(status("output", s[2] || ""));
    }

    screen.replaceChildren(frag);
    chrome(p.title, "step " + (si + 1) + " of " + p.steps.length, (si + 1) / p.steps.length);
    screen.setAttribute("data-step", String(si + 1) + "/" + String(p.steps.length));
  }

  function go(d) {
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
        go(1);
      }
      tick();
    }, last ? 2200 : 950);
  }

  /* ── controls ── */
  var ctl = document.querySelector(".pvh-ctl");
  var hint = document.querySelector(".pvh-hint");
  var playBtn = document.querySelector('.pvh-ctl [data-k="play"]');
  var gbPlay = document.querySelector('[data-device-btn="play"]');

  function setPlaying(v) {
    playing = v;
    if (playBtn) {
      playBtn.setAttribute("aria-pressed", String(v));
      playBtn.textContent = v ? "Pause" : "Play";
    }
    if (gbPlay) {
      gbPlay.setAttribute("aria-pressed", String(v));
      gbPlay.setAttribute("aria-label", v ? "Pause trace" : "Play trace");
      gbPlay.setAttribute("data-state", v ? "playing" : "paused");
    }
    tick();
  }

  function press(kind) {
    window.clearTimeout(eggTimer);
    if (kind === "play") { setPlaying(!playing); return; }
    if (kind === "next") go(1);
    else if (kind === "back") go(-1);
    else nextProgram();
    setPlaying(false);
  }

  /* Make a decorative element behave as a button (role, focus, Enter/Space). */
  function activate(node, label, fn) {
    node.setAttribute("role", "button");
    node.setAttribute("tabindex", "0");
    node.setAttribute("aria-label", label);
    node.addEventListener("click", fn);
    node.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        fn();
      }
    });
  }

  if (ctl) {
    ctl.hidden = false;
    if (hint) hint.hidden = false;
    Array.prototype.forEach.call(ctl.querySelectorAll("[data-k]"), function (b) {
      var k = b.getAttribute("data-k");
      if (k === "prog" && PROGS.length < 2) { b.hidden = true; return; }
      b.addEventListener("click", function () { press(k); });
    });
  }

  var gb = { prev: "back", next: "next" };
  Array.prototype.forEach.call(document.querySelectorAll("[data-device-btn]"), function (b) {
    var k = b.getAttribute("data-device-btn");
    if (k === "play") {
      activate(b, playing ? "Pause trace" : "Play trace", function () { press("play"); });
    } else if (gb[k]) {
      activate(b, k === "prev" ? "Previous step" : "Next step", function () { press(gb[k]); });
    }
  });
  setPlaying(playing);

  /* Only run while on screen and the tab is in front. */
  document.addEventListener("visibilitychange", tick);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      tick();
    }).observe(screen);
  }

  /* ── easter egg: the red square after VERSE ── */
  var egg = document.getElementById("egg");
  var toast = el("div", "pvh-toast");
  toast.setAttribute("role", "status");
  document.body.appendChild(toast);

  function drawHello() {
    var frag = document.createDocumentFragment();
    frag.appendChild(el("div", "hd", '>>> print("hello")'));
    var code = el("div", "code");
    code.appendChild(el("div", "ln on", "hello, world "));
    code.appendChild(el("div", "ln", "You found the dot. "));
    code.appendChild(el("div", "ln", "Now go run something. "));
    frag.appendChild(code);
    frag.appendChild(status("output", "hello, world"));
    screen.replaceChildren(frag);
    chrome("Easter egg", "found it", 1);
    screen.setAttribute("data-step", "egg");
  }

  function confetti() {
    for (var i = 0; i < 60; i++) {
      var d = el("i", "pvh-cf");
      d.style.left = Math.random() * 100 + "vw";
      d.style.background = "var(--pop-" + ((i % 5) + 1) + ")";
      d.style.setProperty("--dx", Math.random() * 160 - 80 + "px");
      d.style.setProperty("--r", Math.random() * 720 - 360 + "deg");
      d.style.setProperty("--t", 1.6 + Math.random() * 1.4 + "s");
      d.style.animationDelay = Math.random() * 0.4 + "s";
      document.body.appendChild(d);
      window.setTimeout(d.remove.bind(d), 3600);
    }
  }

  if (egg) {
    activate(egg, "Surprise", function () {
      window.clearTimeout(eggTimer);
      setPlaying(false);
      drawHello();
      if (!reduce) confetti();
      toast.textContent = "hello, world. you found the dot.";
      toast.classList.add("on");
      window.setTimeout(function () { toast.classList.remove("on"); }, 3200);
      eggTimer = window.setTimeout(function () {
        si = 0;
        draw();
        setPlaying(!reduce);
      }, 4200);
    });
  }

  /* ── Labs figure: b = a  vs  b = a.copy() ── */
  Array.prototype.forEach.call(document.querySelectorAll(".pvh-fig"), function (fig) {
    var sw = fig.querySelector(".sw");
    var cap = fig.querySelector(".cap");
    if (sw) sw.hidden = false;
    Array.prototype.forEach.call(fig.querySelectorAll("[data-m]"), function (b) {
      b.addEventListener("click", function () {
        var alias = b.getAttribute("data-m") === "alias";
        fig.setAttribute("data-mode", b.getAttribute("data-m"));
        Array.prototype.forEach.call(fig.querySelectorAll("[data-m]"), function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        if (cap) {
          cap.textContent = alias
            ? "a is b: True. One list, two names. b.append(4) changes both."
            : "a is b: False. Two lists. b.append(4) leaves a alone.";
        }
      });
    });
  });

  draw();
  tick();
})();
