/* ============================================================
   doc-slides.js — page-through viewer for a slide deck / document
   rendered as images.
   Markup:
   <figure class="doc-slides" data-doc-slides aria-roledescription="carousel" aria-label="…">
     <div class="ds-stage"><img …>×N</div>
     <div class="ds-bar"><button data-ds-prev>…</button><span data-ds-count></span><button data-ds-next>…</button></div>
     <ol class="ds-thumbs"><li><button data-ds-go="0">…</button></li>…</ol>
   </figure>
   Without JS every page is simply shown one under another.
   ============================================================ */
(function () {
  "use strict";
  function wire(fig) {
    if (fig.__wired) return; fig.__wired = true;
    var pages = [].slice.call(fig.querySelectorAll(".ds-stage img"));
    var thumbs = [].slice.call(fig.querySelectorAll("[data-ds-go]"));
    var count = fig.querySelector("[data-ds-count]");
    var prev = fig.querySelector("[data-ds-prev]"), next = fig.querySelector("[data-ds-next]");
    var i = 0, n = pages.length;
    if (!n) return;
    fig.classList.add("is-ready");
    function show(k, focusThumb) {
      i = Math.max(0, Math.min(n - 1, k));
      pages.forEach(function (p, j) { if (j === i) { p.setAttribute("data-active", ""); p.removeAttribute("aria-hidden"); p.loading = "eager"; } else { p.removeAttribute("data-active"); p.setAttribute("aria-hidden", "true"); } });
      if (pages[i + 1]) pages[i + 1].loading = "eager";
      thumbs.forEach(function (t, j) { t.setAttribute("aria-current", j === i ? "true" : "false"); });
      if (count) count.textContent = (i + 1) + " / " + n;
      if (prev) prev.disabled = i === 0;
      if (next) next.disabled = i === n - 1;
      if (focusThumb && thumbs[i]) thumbs[i].scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
    }
    if (prev) prev.addEventListener("click", function () { show(i - 1, true); });
    if (next) next.addEventListener("click", function () { show(i + 1, true); });
    thumbs.forEach(function (t, j) { t.addEventListener("click", function () { show(j, true); }); });
    fig.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); show(i + 1, true); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); show(i - 1, true); }
    });
    var x0 = null;
    var stage = fig.querySelector(".ds-stage");
    stage.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener("touchend", function (e) {
      if (x0 == null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1), true);
    });
    show(0);
  }
  function init() { document.querySelectorAll("[data-doc-slides]").forEach(wire); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
