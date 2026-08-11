/* ============================================================
   progress.js — open-but-tracked progression (per-device).
   Completion rule: quiz lessons complete on passing the quiz;
   other lessons complete when read to the end (scroll sentinel)
   or via an explicit "mark complete" button.
   State lives in localStorage: b4h-progress.
   ============================================================ */
(function () {
  "use strict";
  var KEY = "b4h-progress";
  var BASE = window.B4H_BASE || "/";

  function read() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function write(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) {} }

  var P = {
    data: read(),
    isComplete: function (id) { return !!(this.data.completed && this.data.completed[id]); },
    markComplete: function (id) {
      if (!id) return;
      this.data.completed = this.data.completed || {};
      if (!this.data.completed[id]) {
        this.data.completed[id] = Date.now();
        write(this.data);
        document.dispatchEvent(new CustomEvent("b4h:progress", { detail: { id: id } }));
        celebrate();
      }
      render();
    },
    uncomplete: function (id) {
      if (this.data.completed && this.data.completed[id]) {
        delete this.data.completed[id];
        if (this.data.quizzes) delete this.data.quizzes[id];
        write(this.data);
        document.dispatchEvent(new CustomEvent("b4h:progress", { detail: { id: id } }));
      }
      render();
    },
    setQuiz: function (id, score, passed) {
      this.data.quizzes = this.data.quizzes || {};
      this.data.quizzes[id] = { score: score, passed: passed, at: Date.now() };
      write(this.data);
      if (passed) this.markComplete(id);
      render();
    },
    setLast: function (id, url, title) {
      this.data.last = { id: id, url: url, title: title };
      write(this.data);
    },
    setName: function (n) { this.data.name = n; write(this.data); render(); },
    reset: function () { this.data = {}; write(this.data); render(); document.dispatchEvent(new CustomEvent("b4h:progress", {})); }
  };
  window.B4H_progress = P;

  /* ---------- Celebration (respects reduced motion) ---------- */
  function celebrate() {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var n = 26, box = document.createElement("div");
    box.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:500;overflow:hidden";
    var colors = ["#19679e", "#269aed", "#1e9e77", "#e2a32e", "#8dc8f3"];
    for (var i = 0; i < n; i++) {
      var p = document.createElement("i");
      var left = Math.random() * 100, delay = Math.random() * 0.2, dur = 1.6 + Math.random() * 1.2, size = 7 + Math.random() * 7;
      p.style.cssText = "position:absolute;top:-20px;left:" + left + "%;width:" + size + "px;height:" + size + "px;background:" + colors[i % colors.length] + ";border-radius:2px;opacity:.9;animation:b4hfall " + dur + "s " + delay + "s ease-in forwards;transform:rotate(" + (Math.random() * 360) + "deg)";
      box.appendChild(p);
    }
    document.body.appendChild(box);
    setTimeout(function () { box.remove(); }, 3200);
  }
  if (!document.getElementById("b4h-fall-kf")) {
    var st = document.createElement("style"); st.id = "b4h-fall-kf";
    st.textContent = "@keyframes b4hfall{to{transform:translateY(105vh) rotate(540deg);opacity:0}}";
    document.head.appendChild(st);
  }

  /* ---------- Modules manifest ---------- */
  var MODULES = null;
  function loadModules() {
    if (MODULES) return Promise.resolve(MODULES);
    return fetch(BASE + "data/modules.json").then(function (r) { return r.json(); }).then(function (m) { MODULES = m; window.B4H_MODULES = m; return m; }).catch(function () { return { modules: [] }; });
  }

  function allLessons(m) {
    var out = [];
    (m.modules || []).forEach(function (mod) { (mod.lessons || []).forEach(function (l) { out.push(Object.assign({ module: mod.slug, moduleTitle: mod.title }, l)); }); });
    return out;
  }

  /* ---------- Rendering ---------- */
  function render() {
    if (!MODULES) return;
    var lessons = allLessons(MODULES);
    var total = lessons.length;
    var done = lessons.filter(function (l) { return P.isComplete(l.id); }).length;
    var pct = total ? Math.round((done / total) * 100) : 0;

    // overall
    document.querySelectorAll("[data-progress-overall]").forEach(function (el) {
      var span = el.querySelector("[data-progress-fill]"); if (span) span.style.width = pct + "%";
      var lbl = el.querySelector("[data-progress-label]"); if (lbl) lbl.textContent = pct + "%";
      var cnt = el.querySelector("[data-progress-count]"); if (cnt) cnt.textContent = done + " / " + total;
    });

    // per-module
    document.querySelectorAll("[data-progress-module]").forEach(function (el) {
      var slug = el.getAttribute("data-progress-module");
      var mod = (MODULES.modules || []).find(function (m) { return m.slug === slug; });
      if (!mod) return;
      var t = mod.lessons.length, d = mod.lessons.filter(function (l) { return P.isComplete(l.id); }).length;
      var fill = el.querySelector("[data-progress-fill]"); if (fill) fill.style.width = (t ? (d / t) * 100 : 0) + "%";
      var c = el.querySelector("[data-progress-count]"); if (c) c.textContent = d + "/" + t;
      if (d === t && t > 0) el.setAttribute("data-module-complete", "true");
    });

    // lesson rows status
    var lang = document.documentElement.getAttribute("lang") || "en";
    var nextId = firstIncomplete(lessons);
    document.querySelectorAll("[data-lesson-ref]").forEach(function (el) {
      var id = el.getAttribute("data-lesson-ref");
      var chip = el.querySelector("[data-lesson-status]");
      var complete = P.isComplete(id);
      var status = complete ? "complete" : (id === nextId ? "next" : "not-started");
      if (chip) {
        chip.setAttribute("data-status", status);
        var map = { complete: "status.complete", next: "status.next", "not-started": "status.notstarted", "in-progress": "status.inprogress" };
        var icon = complete ? '<span data-icon="circle-check-big"></span>' : (status === "next" ? '<span data-icon="move-right"></span>' : "");
        chip.innerHTML = icon + '<span>' + (window.B4H_t ? window.B4H_t(map[status], lang) : status) + "</span>";
        if (window.B4H_renderIcons) window.B4H_renderIcons(chip);
      }
    });

    // continue / start button — label + target adapt to whether there's progress
    var cont = document.querySelector("[data-continue]");
    if (cont) {
      var started = !!P.data.last || done > 0;
      var target = P.data.last;
      if (!target) { var f = lessons[0]; target = f ? { url: f.url } : null; }
      if (target && target.url) cont.setAttribute("href", BASE + target.url);
      var lbl = cont.querySelector("[data-i18n]");
      if (lbl) {
        var key = started ? "hub.continue" : "hub.start";
        lbl.setAttribute("data-i18n", key);
        if (window.B4H_t) lbl.textContent = window.B4H_t(key, lang);
      }
    }

    // hide "reset my progress" until there's something to reset
    document.querySelectorAll("[data-reset-wrap]").forEach(function (el) {
      if (done > 0) el.removeAttribute("hidden"); else el.setAttribute("hidden", "");
    });

    // certificate gate
    document.querySelectorAll("[data-cert-gate]").forEach(function (el) {
      el.setAttribute("data-unlocked", (done === total && total > 0).toString());
    });
  }
  window.B4H_renderProgress = render;

  function firstIncomplete(lessons) {
    for (var i = 0; i < lessons.length; i++) if (!P.isComplete(lessons[i].id)) return lessons[i].id;
    return null;
  }

  /* ---------- Lesson page wiring ---------- */
  function wireLessonPage() {
    var body = document.body;
    var id = body.getAttribute("data-lesson-id");
    if (!id) return;
    // record as last visited
    P.setLast(id, body.getAttribute("data-lesson-url") || location.pathname.replace(BASE, ""), body.getAttribute("data-lesson-title") || document.title);

    // reflect completed state on the mark-complete button
    function refreshBtn() {
      document.querySelectorAll("[data-mark-complete]").forEach(function (btn) {
        var done = P.isComplete(id);
        btn.setAttribute("data-done", done.toString());
        var lbl = btn.querySelector("[data-mc-label]");
        if (lbl) lbl.textContent = window.B4H_t(done ? "lesson.done" : "lesson.markdone");
        if (window.B4H_renderIcons) window.B4H_renderIcons(btn);
      });
    }
    document.querySelectorAll("[data-mark-complete]").forEach(function (btn) {
      btn.onclick = function () { if (P.isComplete(id)) P.uncomplete(id); else P.markComplete(id); refreshBtn(); };
    });
    refreshBtn();

    // scroll-to-end completion for non-quiz lessons
    if (body.getAttribute("data-lesson-hasquiz") !== "true") {
      var sentinel = document.querySelector("[data-complete-sentinel]");
      if (sentinel && "IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) { if (en.isIntersecting) { P.markComplete(id); refreshBtn(); io.disconnect(); } });
        }, { threshold: 0.6 });
        io.observe(sentinel);
      }
    }
    document.addEventListener("b4h:progress", refreshBtn);
  }

  /* ---------- Reset buttons ---------- */
  function wireReset() {
    document.querySelectorAll("[data-progress-reset]").forEach(function (btn) {
      btn.onclick = function () {
        if (confirm(window.B4H_t("progress.resetconfirm"))) P.reset();
      };
    });
  }

  function init() {
    loadModules().then(function () {
      render();
      wireLessonPage();
      wireReset();
    });
    document.addEventListener("b4h:langchange", function () { setTimeout(render, 0); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
