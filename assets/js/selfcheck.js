/* ============================================================
   selfcheck.js — scored self-assessment (no right/wrong answers).
   Markup:
   <div class="selfcheck" data-selfcheck>
     <script type="application/json" data-selfcheck-data>
       { "points":[3,2,1,0],
         "questions":[{ "q":{"en":"…","fr":"…"}, "options":[{"en":"…"},…] }, …],
         "bands":[{ "min":30, "title":{"en":"…"}, "body":{"en":"…"} }, …] }
     </script>
   </div>
   Option i scores points[i]. The result band is the first whose `min` the
   total reaches (list bands from highest to lowest). Answers stay on this
   device only (nothing is sent anywhere).
   ============================================================ */
(function () {
  "use strict";
  function t(k) { return window.B4H_t ? window.B4H_t(k) : k; }
  function lang() { return document.documentElement.getAttribute("lang") || "en"; }
  function L(v) { return v && typeof v === "object" ? (v[lang()] != null ? v[lang()] : v.en) : v; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var n = 0;

  function build(box) {
    var dataEl = box.querySelector("[data-selfcheck-data]");
    if (!dataEl) return;
    var data;
    try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var pts = data.points || [3, 2, 1, 0];
    var id = "sc" + (++n);
    var answers = {};

    function render() {
      var qs = data.questions.map(function (q, qi) {
        var name = id + "-q" + qi;
        var opts = q.options.map(function (o, oi) {
          var checked = answers[qi] === oi ? " checked" : "";
          return '<label class="sc-opt"><input type="radio" name="' + name + '" value="' + oi + '"' + checked + "><span>" + esc(L(o)) + "</span></label>";
        }).join("");
        return '<fieldset class="sc-q"><legend><span class="sc-num">' + (qi + 1) + "</span>" + esc(L(q.q)) + "</legend>" + opts + "</fieldset>";
      }).join("");
      box.innerHTML = '<div class="sc-list">' + qs + "</div>" +
        '<div class="sc-bar"><span class="sc-count" data-sc-count></span>' +
        '<button type="button" class="btn btn-primary" data-sc-score><span data-icon="clipboard-check"></span><span>' + esc(t("selfcheck.score")) + "</span></button></div>" +
        '<div class="sc-result" data-sc-result aria-live="polite"></div>';
      box.appendChild(dataEl);
      box.querySelectorAll("input[type=radio]").forEach(function (inp) {
        inp.addEventListener("change", function () {
          answers[parseInt(inp.name.split("-q")[1], 10)] = parseInt(inp.value, 10);
          update();
        });
      });
      box.querySelector("[data-sc-score]").addEventListener("click", score);
      if (window.B4H_renderIcons) window.B4H_renderIcons(box);
      update();
    }

    function answeredCount() { return Object.keys(answers).length; }
    function update() {
      var c = box.querySelector("[data-sc-count]");
      if (c) c.textContent = answeredCount() + " / " + data.questions.length + " " + t("selfcheck.answered");
    }
    function score() {
      var res = box.querySelector("[data-sc-result]");
      if (answeredCount() < data.questions.length) {
        res.innerHTML = '<p class="sc-note">' + esc(t("selfcheck.incomplete")) + "</p>";
        var first = data.questions.findIndex(function (_, i) { return answers[i] == null; });
        var fs = box.querySelectorAll(".sc-q")[first];
        if (fs) { fs.scrollIntoView({ behavior: "smooth", block: "center" }); var r = fs.querySelector("input"); if (r) r.focus({ preventScroll: true }); }
        return;
      }
      var total = 0;
      Object.keys(answers).forEach(function (k) { total += pts[answers[k]] || 0; });
      var max = data.questions.length * Math.max.apply(null, pts);
      var band = (data.bands || []).find(function (b) { return total >= b.min; }) || {};
      res.innerHTML = '<div class="sc-score"><span class="sc-total">' + total + '</span><span class="sc-max">/ ' + max + "</span></div>" +
        '<h4 class="sc-band">' + esc(L(band.title)) + "</h4><p>" + esc(L(band.body)) + "</p>" +
        '<button type="button" class="btn btn-secondary" data-sc-reset><span data-icon="rotate-cw"></span><span>' + esc(t("selfcheck.again")) + "</span></button>";
      res.querySelector("[data-sc-reset]").addEventListener("click", function () { answers = {}; render(); box.scrollIntoView({ behavior: "smooth", block: "start" }); });
      if (window.B4H_renderIcons) window.B4H_renderIcons(res);
      res.setAttribute("tabindex", "-1"); res.focus();
    }
    render();
    document.addEventListener("b4h:langchange", render);
  }

  function init() { document.querySelectorAll("[data-selfcheck]").forEach(build); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
