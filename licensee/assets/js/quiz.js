/* ============================================================
   quiz.js — declarative, bilingual quizzes.
   Markup:
   <div class="quiz" data-quiz data-quiz-for="lesson-id" data-pass="0.7">
     <script type="application/json" data-quiz-questions>
       [{ "q":{"en":"…","fr":"…"},
          "options":[{"en":"…","fr":"…"}, …],
          "answer":0,
          "explain":{"en":"…","fr":"…"} }]
     </script>
   </div>
   ============================================================ */
(function () {
  "use strict";
  function t(k) { return window.B4H_t ? window.B4H_t(k) : k; }
  function lang() { return document.documentElement.getAttribute("lang") || "en"; }
  function L(v) { return v && typeof v === "object" ? (v[lang()] != null ? v[lang()] : v.en) : v; }

  function build(quiz) {
    var dataEl = quiz.querySelector("[data-quiz-questions]");
    if (!dataEl) return;
    var questions;
    try { questions = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var pass = parseFloat(quiz.getAttribute("data-pass") || "0.7");
    var forId = quiz.getAttribute("data-quiz-for");

    var state = { i: 0, answered: [], score: 0, done: false };

    quiz.innerHTML =
      '<div class="quiz-progress" data-dots></div>' +
      '<div data-body></div>' +
      '<div class="quiz-feedback" data-feedback></div>' +
      '<div class="quiz-nav" data-nav></div>';
    // re-attach data (innerHTML wiped it)
    quiz.appendChild(dataEl);

    var dots = quiz.querySelector("[data-dots]");
    var body = quiz.querySelector("[data-body]");
    var feedback = quiz.querySelector("[data-feedback]");
    var nav = quiz.querySelector("[data-nav]");

    function renderDots() {
      dots.innerHTML = questions.map(function (_, idx) {
        var s = "idle";
        if (state.answered[idx] != null) s = state.answered[idx] ? "correct" : "wrong";
        else if (idx === state.i) s = "active";
        return '<span class="quiz-dot" data-state="' + s + '"></span>';
      }).join("");
    }

    function renderQuestion() {
      var q = questions[state.i];
      feedback.setAttribute("data-show", "false");
      var opts = q.options.map(function (o, oi) {
        return '<button class="quiz-opt" data-oi="' + oi + '"><span>' + L(o) + "</span><span class=\"opt-mark\" data-mark></span></button>";
      }).join("");
      body.innerHTML =
        '<p class="quiz-q">' + (state.i + 1) + ". " + L(q.q) + "</p>" +
        '<div class="quiz-options">' + opts + "</div>";
      nav.innerHTML = "";
      renderDots();

      var already = state.answered[state.i];
      var btns = body.querySelectorAll(".quiz-opt");
      if (already != null) { lockQuestion(); }
      else {
        btns.forEach(function (b) {
          b.onclick = function () { choose(parseInt(b.getAttribute("data-oi"), 10)); };
        });
      }
    }

    function lockQuestion() {
      var q = questions[state.i];
      var btns = body.querySelectorAll(".quiz-opt");
      var chosen = state._lastChoice;
      btns.forEach(function (b) {
        var oi = parseInt(b.getAttribute("data-oi"), 10);
        b.setAttribute("disabled", "true");
        var mark = b.querySelector("[data-mark]");
        if (oi === q.answer) { b.setAttribute("data-state", "correct"); if (mark) mark.innerHTML = '<span data-icon="check"></span>'; }
        else if (oi === chosen) { b.setAttribute("data-state", "wrong"); if (mark) mark.innerHTML = '<span data-icon="x"></span>'; }
        if (window.B4H_renderIcons) window.B4H_renderIcons(b);
      });
      var correct = chosen === q.answer;
      feedback.setAttribute("data-kind", correct ? "correct" : "wrong");
      feedback.setAttribute("data-show", "true");
      feedback.innerHTML = "<strong>" + (correct ? t("quiz.correct") : t("quiz.incorrect")) + "</strong> " + (L(q.explain) || "");
      renderNav();
      renderDots();
    }

    function choose(oi) {
      if (state.answered[state.i] != null) return;
      var q = questions[state.i];
      var correct = oi === q.answer;
      state._lastChoice = oi;
      state.answered[state.i] = correct;
      if (correct) state.score++;
      lockQuestion();
    }

    function renderNav() {
      var last = state.i === questions.length - 1;
      nav.innerHTML = '<button class="btn btn-primary" data-next>' + (last ? t("quiz.finish") : t("quiz.next")) + "</button>";
      nav.querySelector("[data-next]").onclick = function () {
        if (last) finish();
        else { state.i++; state._lastChoice = state.answered[state.i] != null ? state._lastChoice : null; renderQuestion(); }
      };
    }

    function finish() {
      state.done = true;
      var total = questions.length;
      var ratio = total ? state.score / total : 0;
      var passed = ratio >= pass;
      body.innerHTML =
        '<div class="quiz-result">' +
          '<div class="quiz-score">' + state.score + " / " + total + "</div>" +
          '<p style="font-weight:700;margin:.4rem 0 0">' + t("quiz.yourscore") + "</p>" +
          '<p class="' + (passed ? "" : "muted") + '" style="margin-top:.6rem">' + (passed ? t("quiz.passed") : t("quiz.review")) + "</p>" +
        "</div>";
      feedback.setAttribute("data-show", "false");
      dots.innerHTML = "";
      nav.innerHTML = passed
        ? '<span class="badge badge-success"><span data-icon="circle-check-big"></span>' + t("status.complete") + "</span>"
        : '<button class="btn btn-secondary" data-retry><span data-icon="rotate-ccw"></span>' + t("quiz.retry") + "</button>";
      var retry = nav.querySelector("[data-retry]");
      if (retry) retry.onclick = function () { state = { i: 0, answered: [], score: 0, done: false }; renderQuestion(); };
      if (window.B4H_renderIcons) window.B4H_renderIcons(nav);
      if (window.B4H_progress && forId) window.B4H_progress.setQuiz(forId, state.score, passed);
    }

    renderQuestion();

    document.addEventListener("b4h:langchange", function () {
      if (state.done) return; // leave results
      renderQuestion();
    });
  }

  function init() { document.querySelectorAll("[data-quiz]").forEach(build); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
