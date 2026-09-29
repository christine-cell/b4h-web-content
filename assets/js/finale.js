/* ============================================================
   finale.js — the program's closing celebration.
   Markup: <section class="finale" data-finale> … <button data-finale-celebrate> …
           <span data-finale-done></span> (filled with lessons completed) … </section>
   - Confetti cannons fire from both bottom corners when the finale first
     scrolls into view, and again on the Celebrate button.
   - Respects prefers-reduced-motion (no confetti; the page still works).
   - Colours come from the design tokens, so it matches light/dark themes.
   ============================================================ */
(function () {
  "use strict";
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  function tokens() {
    var cs = getComputedStyle(document.documentElement);
    var names = ["--warm", "--gold", "--blue-400", "--blue-600", "--azure", "--success", "--coral"];
    var out = names.map(function (n) { return cs.getPropertyValue(n).trim(); }).filter(Boolean);
    out.push("rgba(255,255,255,.95)");
    return out;
  }

  function burst() {
    if (reduce) return;
    var cv = document.createElement("canvas");
    cv.setAttribute("aria-hidden", "true");
    cv.className = "finale-canvas";
    document.body.appendChild(cv);
    var ctx = cv.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
    function size() { cv.width = innerWidth * dpr; cv.height = innerHeight * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    size();
    var colors = tokens(), parts = [], W = innerWidth, H = innerHeight;
    function cannon(x, dir, n) {
      for (var i = 0; i < n; i++) {
        var ang = (-Math.PI / 2) + dir * (0.15 + Math.random() * 0.55);
        var spd = (H / 55) * (0.55 + Math.random() * 0.6);
        parts.push({ x: x, y: H + 10, vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd,
          w: 6 + Math.random() * 8, h: 4 + Math.random() * 10, r: Math.random() * 6.28, vr: (Math.random() - 0.5) * 0.35,
          c: colors[(Math.random() * colors.length) | 0], shape: Math.random() < 0.25 ? 1 : (Math.random() < 0.5 ? 2 : 0), life: 0 });
      }
    }
    var n = W < 600 ? 70 : 120;
    cannon(W * 0.04, 1, n); cannon(W * 0.96, -1, n);
    var start = performance.now();
    function frame(t) {
      var el = t - start;
      ctx.clearRect(0, 0, W, H);
      parts.forEach(function (p) {
        p.vy += 0.32; p.vx *= 0.992; p.vy *= 0.992; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.life++;
        var sway = Math.sin((p.life + p.w) / 9) * 0.8; p.x += sway;
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c;
        ctx.globalAlpha = el > 3200 ? Math.max(0, 1 - (el - 3200) / 900) : 1;
        if (p.shape === 1) { ctx.beginPath(); ctx.arc(0, 0, p.w / 2.4, 0, 6.28); ctx.fill(); }
        else if (p.shape === 2) { ctx.fillRect(-p.w / 2, -1.5, p.w * 1.6, 3); }
        else { ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.life / 6))); }
        ctx.restore();
      });
      if (el < 4200) requestAnimationFrame(frame); else cv.remove();
    }
    requestAnimationFrame(frame);
  }

  function fillCount(root) {
    var out = root.querySelectorAll("[data-finale-done]");
    if (!out.length) return;
    var P = window.B4H_progress, n = 0;
    try { n = Object.keys((P && P.data && P.data.completed) || {}).length; } catch (e) {}
    out.forEach(function (el) { el.textContent = n; });
  }

  function init() {
    document.querySelectorAll("[data-finale]").forEach(function (fin) {
      if (fin.__wired) return; fin.__wired = true;
      fin.querySelectorAll("[data-finale-celebrate]").forEach(function (b) { b.addEventListener("click", burst); });
      fillCount(fin);
      document.addEventListener("b4h:progress", function () { fillCount(fin); });
      if (!reduce && "IntersectionObserver" in window) {
        var fired = false;
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) { if (e.isIntersecting && !fired && fin.offsetParent !== null) { fired = true; setTimeout(burst, 250); io.disconnect(); } });
        }, { threshold: 0.35 });
        io.observe(fin);
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
