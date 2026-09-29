/* ============================================================
   read-aloud.js — reads the page's main content aloud using the
   browser's built-in SpeechSynthesis (no external service).
   Reads only the currently-visible language.
   ============================================================ */
(function () {
  "use strict";
  var synth = window.speechSynthesis;
  var speaking = false;

  function lang() { return document.documentElement.getAttribute("lang") || "en"; }
  function voiceFor(l) {
    var want = l === "fr" ? "fr" : "en";
    var voices = synth.getVoices() || [];
    var caPref = voices.find(function (v) { return v.lang && v.lang.toLowerCase().indexOf(want + "-ca") === 0; });
    return caPref || voices.find(function (v) { return v.lang && v.lang.toLowerCase().indexOf(want) === 0; }) || null;
  }

  function collectText() {
    var main = document.querySelector("[data-lesson-content]") || document.querySelector("main");
    if (!main) return "";
    var cur = lang();
    var parts = [];
    main.querySelectorAll("h1,h2,h3,h4,p,li,.callout-body,.quiz-q,.lead").forEach(function (el) {
      if (el.closest(".video, .quiz-nav, .toc, [data-quiz-questions]")) return;
      var block = el.closest("[data-lang-block]");
      if (block && block.getAttribute("data-lang-block") !== cur) return;
      var txt = el.textContent.replace(/\s+/g, " ").trim();
      if (txt) parts.push(txt);
    });
    return parts.join(". ");
  }

  function setBtn(active) {
    document.querySelectorAll("[data-readaloud-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", active.toString());
      b.setAttribute("aria-label", window.B4H_t(active ? "reader.stopreading" : "reader.readaloud"));
      b.querySelector("[data-icon]") && b.classList.toggle("is-active", active);
    });
  }

  function stop() { try { synth.cancel(); } catch (e) {} speaking = false; setBtn(false); }
  function start() {
    if (!("speechSynthesis" in window)) { alert("Read-aloud isn't supported in this browser."); return; }
    stop();
    var text = collectText();
    if (!text) return;
    // chunk to avoid engine limits
    var chunks = text.match(/[^.!?]+[.!?]*/g) || [text];
    var l = lang(), v = voiceFor(l);
    var idx = 0;
    function next() {
      if (idx >= chunks.length) { speaking = false; setBtn(false); return; }
      var u = new SpeechSynthesisUtterance(chunks[idx++].trim());
      u.lang = l === "fr" ? "fr-CA" : "en-US";
      if (v) u.voice = v;
      u.rate = 0.96; u.pitch = 1;
      u.onend = next;
      u.onerror = function () { speaking = false; setBtn(false); };
      synth.speak(u);
    }
    speaking = true; setBtn(true); next();
  }

  function toggle() { if (speaking) stop(); else start(); }
  window.B4H_toggleReadAloud = toggle;

  function wire() {
    document.querySelectorAll("[data-readaloud-toggle]").forEach(function (b) { b.onclick = toggle; });
  }
  // voices may load async
  if (window.speechSynthesis) { window.speechSynthesis.onvoiceschanged = function () {}; }
  document.addEventListener("b4h:ready", wire);
  document.addEventListener("b4h:langchange", stop);
  window.addEventListener("beforeunload", stop);
})();
