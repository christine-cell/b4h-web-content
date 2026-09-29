/* ============================================================
   audio-slides.js — an audio recording with pictures that change in
   step with it (the original was a voice-over slideshow).
   Markup (written by tools/wix_slides.py):
   <figure class="audio-slides" data-audio-slides>
     <div class="as-stage"><img data-at="0" data-active …><img data-at="18.8" …>…</div>
     <figcaption>…</figcaption>
     <audio controls src="…"></audio>
     <ol class="as-thumbs"><li><button data-seek="18.8">…</button></li>…</ol>
   </figure>
   Without JS the first picture and the audio player still work.
   ============================================================ */
(function () {
  "use strict";
  function wire(fig) {
    if (fig.__wired) return; fig.__wired = true;
    var audio = fig.querySelector("audio");
    var slides = [].slice.call(fig.querySelectorAll(".as-stage img"));
    var buttons = [].slice.call(fig.querySelectorAll("[data-seek]"));
    if (!audio || !slides.length) return;
    var times = slides.map(function (s) { return parseFloat(s.getAttribute("data-at")) || 0; });
    var current = -1;
    function show(i) {
      if (i === current) return;
      current = i;
      slides.forEach(function (s, k) { if (k === i) s.setAttribute("data-active", ""); else s.removeAttribute("data-active"); });
      buttons.forEach(function (b, k) { b.setAttribute("aria-current", k === i ? "true" : "false"); });
    }
    function sync() {
      var t = audio.currentTime, i = 0;
      for (var k = 0; k < times.length; k++) if (t + 0.05 >= times[k]) i = k;
      show(i);
    }
    audio.addEventListener("timeupdate", sync);
    audio.addEventListener("seeked", sync);
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        var at = parseFloat(b.getAttribute("data-seek")) || 0;
        try { audio.currentTime = at; } catch (e) {}
        show(buttons.indexOf(b));
        var p = audio.play(); if (p && p.catch) p.catch(function () {});
      });
    });
    show(0);
  }
  function init() { document.querySelectorAll("[data-audio-slides]").forEach(wire); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
