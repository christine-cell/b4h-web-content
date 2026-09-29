/* ============================================================
   workbook.js — the interactive Action Plan Workbook.
   Markup comes from pathway/data/workbook.json via tools/render_workbook.py
   (one copy per language block; both share the same saved answers).
   - Every [data-wb] input autosaves to this device (localStorage).
   - Week tabs 1–11 with a "x/y done" count per week.
   - Before/after comparison of the baseline tests (Week 1 vs Week 11).
   - Print (filled or blank), backup to a file, restore from a file, clear.
   ============================================================ */
(function () {
  "use strict";
  var KEY = "b4h-workbook-pathway", KEY_WEEK = "b4h-workbook-week";
  var roots = [];
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  var data = load();
  function persist() { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {} }
  function num(v) { if (v == null || v === "") return null; var n = parseFloat(String(v).replace(",", ".")); return isNaN(n) ? null : n; }
  function fmt(n) { return (Math.round(n * 10) / 10).toString(); }

  function fill(root) {
    root.querySelectorAll("[data-wb]").forEach(function (el) {
      var v = data[el.getAttribute("data-wb")];
      if (el.type === "checkbox") el.checked = !!v; else el.value = v == null ? "" : v;
    });
  }

  function counts(root) {
    root.querySelectorAll("[data-wb-week]").forEach(function (sec) {
      var todos = sec.querySelectorAll("[data-wb-todo]"), n = 0;
      todos.forEach(function (c) { if (c.checked) n++; });
      var out = root.querySelector('[data-wb-count="' + sec.getAttribute("data-wb-week") + '"]');
      if (out) { out.textContent = todos.length ? n + "/" + todos.length : ""; out.parentNode.toggleAttribute("data-complete", todos.length > 0 && n === todos.length); }
    });
  }

  function compare(root) {
    var T = root.dataset;
    root.querySelectorAll("[data-wb-compare]").forEach(function (tr) {
      var id = tr.getAttribute("data-wb-compare"), better = tr.getAttribute("data-better"), u = tr.getAttribute("data-unit");
      var unit = u === "s" ? " " + T.tUnitS : " " + T.tUnitSteps;
      var b = num(data["test.baseline." + id]), a = num(data["test.retest." + id]);
      tr.querySelector('[data-c="b"]').textContent = b == null ? "—" : fmt(b) + unit;
      tr.querySelector('[data-c="a"]').textContent = a == null ? "—" : fmt(a) + unit;
      var d = tr.querySelector('[data-c="d"]');
      tr.removeAttribute("data-trend");
      if (b == null || a == null) { d.textContent = "—"; return; }
      var diff = a - b;
      if (Math.abs(diff) < 0.05) { d.textContent = T.tSame; tr.setAttribute("data-trend", "same"); return; }
      var improved = better === "lower" ? diff < 0 : diff > 0;
      var arrow = improved ? "▲ " : "▼ ", n = fmt(Math.abs(diff));
      if (u === "s") d.textContent = arrow + n + unit + " " + (better === "lower" ? (diff < 0 ? T.tFaster : T.tSlower) : (diff > 0 ? T.tLonger : T.tShorter));
      else d.textContent = arrow + (diff > 0 ? T.tMore : T.tFewer).replace("{n}", n);
      tr.setAttribute("data-trend", improved ? "better" : "worse");
    });
  }

  var savedTimer;
  function flash(root) {
    var el = root.querySelector("[data-wb-saved]"); if (!el) return;
    el.textContent = root.dataset.tSaved; clearTimeout(savedTimer);
    savedTimer = setTimeout(function () { roots.forEach(function (r) { var s = r.querySelector("[data-wb-saved]"); if (s) s.textContent = ""; }); }, 1800);
  }

  function refreshAll() { roots.forEach(function (r) { fill(r); counts(r); compare(r); }); }

  function showWeek(root, n, focus) {
    root.querySelectorAll("[data-wb-week]").forEach(function (s) { s.hidden = +s.getAttribute("data-wb-week") !== n; });
    root.querySelectorAll("[data-wb-week-btn]").forEach(function (b) {
      var on = +b.getAttribute("data-wb-week-btn") === n;
      b.setAttribute("aria-selected", on ? "true" : "false"); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus();
    });
    try { localStorage.setItem(KEY_WEEK, n); } catch (e) {}
  }

  function wire(root) {
    if (root.__wired) return; root.__wired = true; roots.push(root);
    root.classList.add("is-ready");
    var T = root.dataset;
    root.addEventListener("input", onChange); root.addEventListener("change", onChange);
    function onChange(e) {
      var el = e.target, k = el.getAttribute && el.getAttribute("data-wb");
      if (!k) return;
      var v = el.type === "checkbox" ? el.checked : el.value;
      if (v === "" || v === false) delete data[k]; else data[k] = v;
      persist(); counts(root); compare(root); flash(root);
    }
    var btns = [].slice.call(root.querySelectorAll("[data-wb-week-btn]"));
    btns.forEach(function (b, i) {
      b.addEventListener("click", function () { showWeek(root, +b.getAttribute("data-wb-week-btn")); });
      b.addEventListener("keydown", function (e) {
        var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
        if (j == null) return; e.preventDefault(); j = (j + btns.length) % btns.length; showWeek(root, +btns[j].getAttribute("data-wb-week-btn"), true);
      });
    });
    var start = 1;
    var m = location.hash.match(/week-(\d+)/); if (m) start = +m[1];
    else { try { start = +localStorage.getItem(KEY_WEEK) || 1; } catch (e) {} }
    showWeek(root, Math.min(Math.max(start, 1), btns.length || 1));

    function doPrint(blank) {
      var html = document.documentElement;
      html.classList.add("print-workbook"); if (blank) html.classList.add("print-blank");
      root.classList.add("is-printing");
      window.print();
      setTimeout(function () { html.classList.remove("print-workbook", "print-blank"); root.classList.remove("is-printing"); }, 600);
    }
    var p = root.querySelector("[data-wb-print]"); if (p) p.addEventListener("click", function () { doPrint(false); });
    var pb = root.querySelector("[data-wb-print-blank]"); if (pb) pb.addEventListener("click", function () { doPrint(true); });

    var bk = root.querySelector("[data-wb-backup]");
    if (bk) bk.addEventListener("click", function () {
      var blob = new Blob([JSON.stringify({ type: "b4h-pathway-workbook", saved: new Date().toISOString(), data: data }, null, 1)], { type: "application/json" });
      var a = document.createElement("a"); a.href = URL.createObjectURL(blob);
      a.download = "my-action-plan-workbook-" + new Date().toISOString().slice(0, 10) + ".json";
      document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    });
    var rs = root.querySelector("[data-wb-restore]");
    if (rs) rs.addEventListener("change", function () {
      var f = rs.files && rs.files[0]; if (!f) return;
      var rd = new FileReader();
      rd.onload = function () {
        try {
          var j = JSON.parse(rd.result);
          if (!j || j.type !== "b4h-pathway-workbook" || typeof j.data !== "object") throw 0;
          data = j.data; persist(); refreshAll(); alert(T.tRestored);
        } catch (e) { alert(T.tBadfile); }
        rs.value = "";
      };
      rd.readAsText(f);
    });
    var cl = root.querySelector("[data-wb-clear]");
    if (cl) cl.addEventListener("click", function () {
      if (!confirm(T.tClearQ)) return;
      data = {}; persist(); refreshAll();
    });
    fill(root); counts(root); compare(root);
  }

  function init() { document.querySelectorAll("[data-workbook]").forEach(wire); }
  // the other language copy re-reads the latest answers when the language changes
  document.addEventListener("b4h:langchange", refreshAll);
  window.addEventListener("hashchange", function () {
    var m = location.hash.match(/week-(\d+)/); if (m) roots.forEach(function (r) { showWeek(r, +m[1]); });
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
