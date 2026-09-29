/* ============================================================
   meal-plan.js — interactivity for the 10-day meal plan
   (markup generated from pathway/data/meal-plan.json by
   tools/render_meal_plan.py; one copy per language block).
   - Food-sorting game with instant feedback and a score.
   - Day tabs (one day at a time), "I tried this day" ticks.
   - Grocery-list builder: pick days → combined list by store section,
     tick items off, print just the list.
   Remembers ticks on this device only. Works without JS as a plain page.
   ============================================================ */
(function () {
  "use strict";
  var KEY_DONE = "b4h-mealplan-done", KEY_HAVE = "b4h-mealplan-have", KEY_DAY = "b4h-mealplan-day";
  function load(k, d) { try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function icons(el) { if (window.B4H_renderIcons) window.B4H_renderIcons(el); }

  function wire(root) {
    if (root.__wired) return; root.__wired = true;
    root.classList.add("is-ready");
    var T = root.dataset;

    /* ---- food-sorting game: one food at a time ---- */
    var game = root.querySelector("[data-food-sort]");
    if (game) {
      var items = [].slice.call(game.querySelectorAll(".fs-item"));
      var rightEl = game.querySelector("[data-fs-right]"), again = game.querySelector("[data-fs-again]");
      var cur = 0, total = items.length;
      var prog = document.createElement("p"); prog.className = "fs-progress"; game.insertBefore(prog, game.querySelector(".fs-list"));
      var bar = document.createElement("div"); bar.className = "fs-bar"; bar.innerHTML = "<span></span>"; game.insertBefore(bar, prog);
      var summary = document.createElement("div"); summary.className = "fs-summary"; summary.hidden = true; game.insertBefore(summary, again);
      function nRight() { return game.querySelectorAll('.fs-item[data-result="right"]').length; }
      function score() { rightEl.textContent = nRight(); }
      function show(k) {
        cur = k;
        items.forEach(function (it, j) { it.hidden = j !== k; });
        prog.textContent = T.tFood + " " + (k + 1) + " / " + total;
        bar.firstChild.style.width = Math.round((k / total) * 100) + "%";
        summary.hidden = true; again.hidden = true;
      }
      function finish() {
        items.forEach(function (it) { it.hidden = true; });
        bar.firstChild.style.width = "100%"; prog.textContent = "";
        summary.innerHTML = '<p class="fs-result">' + T.tResult.replace("{n}", nRight()).replace("{t}", total) + "</p>";
        summary.hidden = false; again.hidden = false; summary.setAttribute("tabindex", "-1"); summary.focus();
      }
      items.forEach(function (it, idx) {
        var why = it.querySelector(".fs-why"), ans = it.querySelector(".fs-answer"), label = ans ? ans.textContent : "";
        it.__label = label;
        var nx = document.createElement("button"); nx.type = "button"; nx.className = "btn btn-primary fs-next"; nx.hidden = true;
        nx.innerHTML = "<span>" + (idx === total - 1 ? T.tFinish : T.tNext) + '</span><span data-icon="arrow-right"></span>';
        nx.addEventListener("click", function () { if (idx === total - 1) finish(); else { show(idx + 1); var b = items[idx + 1].querySelector("[data-pick]"); if (b) b.focus(); } });
        it.appendChild(nx);
        it.querySelectorAll("[data-pick]").forEach(function (b) {
          b.addEventListener("click", function () {
            if (it.hasAttribute("data-result")) return;
            var ok = b.getAttribute("data-pick") === it.getAttribute("data-bin");
            it.setAttribute("data-result", ok ? "right" : "wrong");
            b.setAttribute("data-picked", "");
            it.querySelectorAll("[data-pick]").forEach(function (x) { x.disabled = true; if (x.getAttribute("data-pick") === it.getAttribute("data-bin")) x.setAttribute("data-correct", ""); });
            if (ans) ans.textContent = (ok ? T.tRight : T.tWrong) + " " + label;
            why.hidden = false; nx.hidden = false; nx.focus(); score();
          });
        });
        why.hidden = true;
      });
      if (again) again.addEventListener("click", function () {
        items.forEach(function (it) {
          it.removeAttribute("data-result");
          it.querySelectorAll("[data-pick]").forEach(function (x) { x.disabled = false; x.removeAttribute("data-picked"); x.removeAttribute("data-correct"); });
          var ans = it.querySelector(".fs-answer"); if (ans) ans.textContent = it.__label;
          it.querySelector(".fs-why").hidden = true; it.querySelector(".fs-next").hidden = true;
        });
        score(); show(0); var b = items[0].querySelector("[data-pick]"); if (b) b.focus();
      });
      show(0);
    }

    /* ---- day tabs + done ticks ---- */
    var dayBtns = [].slice.call(root.querySelectorAll("[data-day-btn]"));
    var panels = [].slice.call(root.querySelectorAll(".mp-day"));
    var done = load(KEY_DONE, []);
    function paintDone() {
      dayBtns.forEach(function (b) { b.toggleAttribute("data-done", done.indexOf(+b.dataset.dayBtn) > -1); });
      root.querySelectorAll("[data-day-done]").forEach(function (b) {
        var on = done.indexOf(+b.dataset.dayDone) > -1;
        b.setAttribute("aria-pressed", on ? "true" : "false");
        var l = b.querySelector("[data-done-label]"); if (l) l.textContent = on ? T.tDoneOn : T.tDone;
      });
      var c = root.querySelector("[data-days-done]"); if (c) c.textContent = done.length;
    }
    function showDay(n, focus) {
      panels.forEach(function (p) { p.hidden = +p.dataset.day !== n; });
      dayBtns.forEach(function (b) { var on = +b.dataset.dayBtn === n; b.setAttribute("aria-selected", on ? "true" : "false"); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); });
      save(KEY_DAY, n);
    }
    dayBtns.forEach(function (b, i) {
      b.addEventListener("click", function () { showDay(+b.dataset.dayBtn); });
      b.addEventListener("keydown", function (e) {
        var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
        if (j == null) return; e.preventDefault(); j = (j + dayBtns.length) % dayBtns.length; showDay(+dayBtns[j].dataset.dayBtn, true);
      });
    });
    root.querySelectorAll("[data-day-done]").forEach(function (b) {
      b.addEventListener("click", function () {
        var n = +b.dataset.dayDone, i = done.indexOf(n);
        if (i > -1) done.splice(i, 1); else done.push(n);
        done.sort(function (a, c) { return a - c; }); save(KEY_DONE, done); paintAll();
      });
    });
    if (panels.length) showDay(Math.min(Math.max(+load(KEY_DAY, 1) || 1, 1), panels.length));

    /* ---- grocery list ---- */
    var gro = root.querySelector("[data-grocery]");
    var have = load(KEY_HAVE, []);
    function buildList() {
      if (!gro) return;
      var days = [].slice.call(gro.querySelectorAll(".mp-gdays input:checked")).map(function (i) { return +i.value; });
      var seen = {};
      gro.querySelectorAll(".mp-aisle ul").forEach(function (u) { u.innerHTML = ""; });
      panels.forEach(function (p) {
        if (days.indexOf(+p.dataset.day) < 0) return;
        p.querySelectorAll(".mp-ings li").forEach(function (li) {
          var item = li.dataset.item, aisle = li.dataset.aisle, k = aisle + "|" + item.toLowerCase();
          if (seen[k]) { seen[k].days.push(+p.dataset.day); return; }
          seen[k] = { item: item, aisle: aisle, days: [+p.dataset.day] };
        });
      });
      Object.keys(seen).sort().forEach(function (k) {
        var s = seen[k], ul = gro.querySelector('.mp-aisle[data-aisle-id="' + s.aisle + '"] ul');
        if (!ul) return;
        var id = "g-" + k.replace(/[^a-z0-9]+/gi, "-");
        var li = document.createElement("li");
        var checked = have.indexOf(k) > -1 ? " checked" : "";
        li.innerHTML = '<label><input type="checkbox" data-k="' + k.replace(/"/g, "&quot;") + '"' + checked + '><span>' +
          s.item.replace(/</g, "&lt;") + '</span><span class="mp-gd">' + (T.tDay || "") + " " + s.days.join(", ") + "</span></label>";
        ul.appendChild(li);
      });
      gro.querySelectorAll(".mp-aisle").forEach(function (sec) { sec.hidden = !sec.querySelector("li"); });
      var list = gro.querySelector("[data-glist]"), empty = list.querySelector(".mp-gempty");
      if (!days.length) { if (!empty) { empty = document.createElement("p"); empty.className = "mp-gempty"; list.prepend(empty); } empty.textContent = T.tEmpty; }
      else if (empty) empty.remove();
      gro.querySelectorAll("[data-k]").forEach(function (c) {
        c.addEventListener("change", function () {
          var k = c.dataset.k, i = have.indexOf(k);
          if (c.checked && i < 0) have.push(k); else if (!c.checked && i > -1) have.splice(i, 1);
          save(KEY_HAVE, have);
        });
      });
    }
    if (gro) {
      gro.querySelectorAll(".mp-gdays input").forEach(function (i) { i.addEventListener("change", buildList); });
      var pr = gro.querySelector("[data-gprint]");
      if (pr) pr.addEventListener("click", function () {
        document.documentElement.classList.add("print-grocery"); gro.classList.add("is-printing");
        window.print();
        setTimeout(function () { document.documentElement.classList.remove("print-grocery"); gro.classList.remove("is-printing"); }, 500);
      });
      var cl = gro.querySelector("[data-gclear]");
      if (cl) cl.addEventListener("click", function () { have = []; save(KEY_HAVE, have); buildList(); });
      buildList();
    }
    root.__paint = paintDone;
    paintDone(); icons(root);
  }

  var roots = [];
  function paintAll() { roots.forEach(function (r) { r.__paint && r.__paint(); }); }
  function init() { document.querySelectorAll("[data-meal-plan]").forEach(function (r) { roots.push(r); wire(r); }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
