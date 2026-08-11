/* ============================================================
   search.js — client-side, bilingual search over modules.json.
   Builds its own modal; any [data-search-open] button opens it.
   Keyboard: "/" opens, Esc closes, ↑/↓ navigate, Enter opens.
   ============================================================ */
(function () {
  "use strict";
  var BASE = window.B4H_BASE || "/";
  var index = [];
  var modal, input, results, activeIdx = -1, current = [];

  function lang() { return document.documentElement.getAttribute("lang") || "en"; }
  function L(v) { return v && typeof v === "object" ? (v[lang()] != null ? v[lang()] : v.en) : (v || ""); }

  function buildIndex(m) {
    index = [];
    (m.modules || []).forEach(function (mod) {
      (mod.lessons || []).forEach(function (l) {
        index.push({ url: l.url, title: l, summary: l.summary || "", keywords: l.keywords || "", module: mod });
      });
    });
    // include resources if present
    (m.resources || []).forEach(function (r) { index.push({ url: r.url, title: r, summary: r.summary || "", keywords: r.keywords || "", module: { title: { en: "Resources", fr: "Ressources" } } }); });
  }

  function makeModal() {
    modal = document.createElement("div");
    modal.className = "modal"; modal.setAttribute("role", "dialog"); modal.setAttribute("aria-modal", "true"); modal.setAttribute("aria-label", "Search");
    modal.innerHTML =
      '<div class="modal-scrim" data-close></div>' +
      '<div class="modal-box">' +
        '<div class="search-input"><span data-icon="search" aria-hidden="true"></span>' +
          '<input type="search" autocomplete="off" data-search-field aria-label="Search">' +
          '<button class="icon-btn" data-close aria-label="Close"><span data-icon="x" aria-hidden="true"></span></button>' +
        "</div>" +
        '<div class="search-results" data-search-results></div>' +
      "</div>";
    document.body.appendChild(modal);
    input = modal.querySelector("[data-search-field]");
    results = modal.querySelector("[data-search-results]");
    if (window.B4H_renderIcons) window.B4H_renderIcons(modal);

    modal.querySelectorAll("[data-close]").forEach(function (b) { b.onclick = close; });
    input.addEventListener("input", function () { run(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") { var a = results.querySelector('a[data-active="true"]') || results.querySelector("a"); if (a) location.href = a.href; }
    });
  }

  function open() {
    if (!modal) makeModal();
    input.setAttribute("placeholder", window.B4H_t("search.placeholder"));
    modal.setAttribute("data-open", "true");
    run("");
    setTimeout(function () { input.focus(); }, 30);
  }
  function close() { if (modal) modal.setAttribute("data-open", "false"); }

  function move(d) {
    var links = Array.prototype.slice.call(results.querySelectorAll("a"));
    if (!links.length) return;
    activeIdx = (activeIdx + d + links.length) % links.length;
    links.forEach(function (l, i) { l.setAttribute("data-active", (i === activeIdx).toString()); if (i === activeIdx) l.scrollIntoView({ block: "nearest" }); });
  }

  function run(q) {
    q = (q || "").trim().toLowerCase();
    activeIdx = -1;
    var lg = lang();
    current = index.filter(function (it) {
      if (!q) return true;
      var hay = (L(it.title) + " " + L(it.summary) + " " + (typeof it.keywords === "object" ? L(it.keywords) : it.keywords) + " " + L(it.module.title)).toLowerCase();
      return hay.indexOf(q) >= 0;
    }).slice(0, 40);
    if (!current.length) { results.innerHTML = '<p class="muted" style="padding:1rem">' + window.B4H_t("search.noresults") + "</p>"; return; }
    results.innerHTML = current.map(function (it) {
      var title = highlight(L(it.title), q);
      return '<a href="' + BASE + it.url + '"><span class="sr-title">' + title + "</span><span class=\"sr-mod\">" + L(it.module.title) + "</span></a>";
    }).join("");
  }

  function highlight(text, q) {
    if (!q) return text;
    var i = text.toLowerCase().indexOf(q);
    if (i < 0) return text;
    return text.slice(0, i) + "<mark>" + text.slice(i, i + q.length) + "</mark>" + text.slice(i + q.length);
  }

  function init() {
    fetch(BASE + "data/modules.json").then(function (r) { return r.json(); }).then(function (m) { buildIndex(m); }).catch(function () {});
    document.addEventListener("click", function (e) {
      var t = e.target.closest("[data-search-open]");
      if (t) { e.preventDefault(); open(); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
      else if (e.key === "/" && !/input|textarea|select/i.test((e.target.tagName || "")) && !e.metaKey && !e.ctrlKey) { e.preventDefault(); open(); }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
