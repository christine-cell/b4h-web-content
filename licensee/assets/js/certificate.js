/* ============================================================
   certificate.js — printable completion certificate.
   Unlock state is set by progress.js via [data-cert-gate].
   ============================================================ */
(function () {
  "use strict";
  function init() {
    var gate = document.querySelector("[data-cert-gate]");
    if (!gate) return;
    var nameInput = gate.querySelector("[data-cert-name]");
    var nameOut = gate.querySelectorAll("[data-cert-name-display]");
    var printBtn = gate.querySelector("[data-cert-print]");
    var dateOut = gate.querySelectorAll("[data-cert-date]");

    var saved = (window.B4H_progress && window.B4H_progress.data && window.B4H_progress.data.name) || "";
    if (nameInput) nameInput.value = saved;
    function paint() {
      var n = (nameInput && nameInput.value.trim()) || saved || "—";
      nameOut.forEach(function (el) { el.textContent = n; });
    }
    paint();
    var lang = document.documentElement.getAttribute("lang") || "en";
    var d = new Date();
    var dstr = d.toLocaleDateString(lang === "fr" ? "fr-CA" : "en-CA", { year: "numeric", month: "long", day: "numeric" });
    dateOut.forEach(function (el) { el.textContent = dstr; });

    if (nameInput) nameInput.addEventListener("input", function () {
      paint();
      if (window.B4H_progress) window.B4H_progress.setName(nameInput.value.trim());
    });
    if (printBtn) printBtn.onclick = function () { window.print(); };

    document.addEventListener("b4h:langchange", function () {
      var l = document.documentElement.getAttribute("lang") || "en";
      var s = new Date().toLocaleDateString(l === "fr" ? "fr-CA" : "en-CA", { year: "numeric", month: "long", day: "numeric" });
      dateOut.forEach(function (el) { el.textContent = s; });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
