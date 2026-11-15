/* PyVerse "pop" layer: behaviour.
 *
 * Today this only drives the scroll-progress rule (.pv-prog). It writes one CSS
 * custom property, --p (0..1), and nothing else; the look lives in
 * css/pyverse-pop.css. Safe to omit: with no script the rule just stays empty.
 */
(function () {
  "use strict";

  var bar = document.querySelector(".pv-prog");
  if (!bar) return;

  var queued = false;

  function paint() {
    queued = false;
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    bar.style.setProperty("--p", String(p));
  }

  function schedule() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(paint);
  }

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule, { passive: true });
  paint();
})();
