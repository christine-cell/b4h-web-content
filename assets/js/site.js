/* ============================================================
   site.js — core behaviour for every page.
   Depends on icons.js + i18n.js (loaded before this).
   ============================================================ */
(function () {
  "use strict";

  // Resolve the site base URL from this script's own src, so every
  // relative path (partials, assets, links) works at any URL depth
  // and under the /repo/ GitHub Pages subpath.
  var thisScript = document.currentScript;
  var BASE = (function () {
    try {
      var src = thisScript.src;
      return src.slice(0, src.indexOf("/assets/js/site.js") + 1);
    } catch (e) { return "/"; }
  })();
  window.B4H_BASE = BASE;
  var LS = window.localStorage;

  function $(s, r) { return (r || document).querySelector(s); }
  function $all(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function get(k, d) { try { return LS.getItem(k) != null ? LS.getItem(k) : d; } catch (e) { return d; } }
  function set(k, v) { try { LS.setItem(k, v); } catch (e) {} }

  /* ---------- Icons ---------- */
  function renderIcons(root) {
    var dict = window.B4H_ICONS || {};
    $all("[data-icon]", root).forEach(function (el) {
      if (el.__iconDone) return;
      var name = el.getAttribute("data-icon");
      var inner = dict[name];
      if (!inner) return;
      var svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + inner + "</svg>";
      el.insertAdjacentHTML("afterbegin", svg);
      el.__iconDone = true;
    });
  }
  window.B4H_renderIcons = renderIcons;

  /* ---------- Theme / reading controls ---------- */
  var root = document.documentElement;
  function setTheme(t) { root.setAttribute("data-theme", t); set("b4h-theme", t); syncControls(); }
  function setContrast(on) { if (on) root.setAttribute("data-contrast", "high"); else root.removeAttribute("data-contrast"); set("b4h-contrast", on ? "high" : "normal"); syncControls(); }
  function setFont(scale) { root.style.setProperty("--font-scale", scale); set("b4h-font", scale); syncControls(); }
  function setLine(mult) { root.style.setProperty("--line-mult", mult); set("b4h-line", mult); syncControls(); }
  function setLang(lang) {
    root.setAttribute("lang", lang);
    set("b4h-lang", lang);
    if (window.B4H_applyI18n) window.B4H_applyI18n(document, lang);
    syncControls();
    // let features re-render language-dependent UI
    document.dispatchEvent(new CustomEvent("b4h:langchange", { detail: { lang: lang } }));
  }
  window.B4H_setLang = setLang;

  function syncControls() {
    var theme = root.getAttribute("data-theme") || "light";
    var contrast = root.getAttribute("data-contrast") === "high";
    var font = get("b4h-font", "1");
    var line = get("b4h-line", "1");
    var lang = root.getAttribute("lang") || "en";
    $all("[data-ctl='theme'] button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.val === theme); });
    $all("[data-ctl='font'] button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.val === font); });
    $all("[data-ctl='line'] button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.val === line); });
    $all("[data-ctl='contrast'] button").forEach(function (b) { b.setAttribute("aria-pressed", (b.dataset.val === "high") === contrast); });
    $all("[data-ctl='lang'] button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.val === lang); });
  }

  function wireControls(root) {
    $all("[data-ctl='theme'] button", root).forEach(function (b) { b.onclick = function () { setTheme(b.dataset.val); }; });
    $all("[data-ctl='font'] button", root).forEach(function (b) { b.onclick = function () { setFont(b.dataset.val); }; });
    $all("[data-ctl='line'] button", root).forEach(function (b) { b.onclick = function () { setLine(b.dataset.val); }; });
    $all("[data-ctl='contrast'] button", root).forEach(function (b) { b.onclick = function () { setContrast(b.dataset.val === "high"); }; });
    $all("[data-ctl='lang'] button", root).forEach(function (b) { b.onclick = function () { setLang(b.dataset.val); }; });
  }

  /* ---------- Reader menu open/close ---------- */
  function wireReaderMenu(root) {
    var toggle = $("[data-reader-toggle]", root);
    var panel = $("[data-reader-panel]", root);
    if (!toggle || !panel) return;
    toggle.onclick = function (e) {
      e.stopPropagation();
      var open = panel.getAttribute("data-open") === "true";
      panel.setAttribute("data-open", (!open).toString());
      toggle.setAttribute("aria-expanded", (!open).toString());
    };
    document.addEventListener("click", function (e) {
      if (panel.getAttribute("data-open") === "true" && !panel.contains(e.target) && e.target !== toggle) {
        panel.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") panel.setAttribute("data-open", "false"); });
  }

  /* ---------- Mobile nav ---------- */
  function wireNav(root) {
    var toggle = $("[data-nav-toggle]", root);
    var nav = $("#primary-nav", root);
    if (!toggle || !nav) return;
    toggle.onclick = function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", (!open).toString());
      toggle.setAttribute("aria-expanded", (!open).toString());
    };
    // mark current page
    var here = location.pathname.replace(/index\.html$/, "").replace(/\/$/, "");
    $all("a.nav-link", nav).forEach(function (a) {
      var href = a.getAttribute("href") || "";
      var path = a.pathname ? a.pathname.replace(/index\.html$/, "").replace(/\/$/, "") : "";
      if (path && here.indexOf(path) === 0 && path.length > 1) a.setAttribute("aria-current", "page");
      else if (here === path) a.setAttribute("aria-current", "page");
    });
  }

  /* ---------- Partials (header/footer) ---------- */
  function loadPartials() {
    var slots = $all("[data-include]");
    return Promise.all(slots.map(function (slot) {
      var name = slot.getAttribute("data-include");
      return fetch(BASE + "partials/" + name + ".html")
        .then(function (r) { return r.ok ? r.text() : ""; })
        .then(function (html) {
          if (!html) return;
          // fix relative asset/link hrefs (marked with data-base) to BASE
          html = html.replace(/\{\{base\}\}/g, BASE);
          slot.outerHTML = html;
        })
        .catch(function () {});
    }));
  }

  /* ---------- Reveal on scroll ---------- */
  function wireReveal() {
    var els = $all("[data-reveal]");
    if (!els.length) return;
    if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) {
      els.forEach(function (el) { el.setAttribute("data-revealed", "true"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.setAttribute("data-revealed", "true"); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Reading progress + back to top ---------- */
  function wireScrollUI() {
    var bar = $(".read-progress");
    var top = $(".to-top");
    function onScroll() {
      var h = document.documentElement;
      var scrolled = h.scrollTop;
      var max = h.scrollHeight - h.clientHeight;
      if (bar) bar.style.width = (max > 0 ? (scrolled / max) * 100 : 0) + "%";
      if (top) top.setAttribute("data-show", (scrolled > 500).toString());
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    if (top) top.onclick = function () { window.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); };
    onScroll();
  }

  /* ---------- Build + spy the on-page TOC ---------- */
  function wireTOC() {
    var tocNav = $("[data-toc]");
    var content = $("[data-lesson-content]");
    if (!tocNav || !content) return;
    var heads = $all("h2[id], h3[id]", content).filter(function (h) {
      // only visible-language headings
      var block = h.closest("[data-lang-block]");
      return !block || block.getAttribute("data-lang-block") === (root.getAttribute("lang") || "en");
    });
    if (heads.length < 2) { var wrap = tocNav.closest(".toc"); if (wrap) wrap.style.display = "none"; return; }
    tocNav.innerHTML = heads.map(function (h) {
      var pad = h.tagName === "H3" ? ' style="padding-left:1.4rem"' : "";
      return '<a href="#' + h.id + '"' + pad + '>' + h.textContent + "</a>";
    }).join("");
    var links = $all("a", tocNav);
    if ("IntersectionObserver" in window) {
      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            links.forEach(function (l) { l.setAttribute("data-active", (l.getAttribute("href") === "#" + en.target.id).toString()); });
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      heads.forEach(function (h) { spy.observe(h); });
    }
  }

  /* ---------- Accordions ---------- */
  function wireAccordions(root) {
    $all(".accordion", root).forEach(function (acc) {
      var trig = $(".acc-trigger", acc);
      var panel = $(".acc-panel", acc);
      if (!trig || !panel || trig.__wired) return;
      trig.__wired = true;
      trig.setAttribute("aria-expanded", acc.getAttribute("data-open") === "true" ? "true" : "false");
      function refresh() { panel.style.maxHeight = acc.getAttribute("data-open") === "true" ? panel.scrollHeight + "px" : "0px"; }
      trig.onclick = function () {
        var open = acc.getAttribute("data-open") === "true";
        acc.setAttribute("data-open", (!open).toString());
        trig.setAttribute("aria-expanded", (!open).toString());
        refresh();
      };
      if (acc.getAttribute("data-open") === "true") refresh();
    });
  }

  /* ---------- Tabs ---------- */
  function wireTabs(root) {
    $all(".tabs", root).forEach(function (tabs) {
      var btns = $all(".tablist button", tabs);
      var panels = $all(".tabpanel", tabs);
      btns.forEach(function (b, i) {
        b.onclick = function () {
          btns.forEach(function (x, j) { x.setAttribute("aria-selected", (j === i).toString()); });
          panels.forEach(function (p, j) { p.hidden = j !== i; });
        };
      });
    });
  }

  /* ---------- Flip cards ---------- */
  function wireFlips(root) {
    $all(".flip", root).forEach(function (f) {
      f.setAttribute("tabindex", "0");
      f.setAttribute("role", "button");
      function toggle() { f.setAttribute("data-flipped", (f.getAttribute("data-flipped") !== "true").toString()); }
      f.onclick = toggle;
      f.onkeydown = function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } };
    });
  }

  /* ---------- Glossary popovers (tap on touch) ---------- */
  function wireGlossary(root) {
    $all(".gloss", root).forEach(function (g) {
      g.setAttribute("tabindex", "0");
      g.onclick = function () { g.setAttribute("data-open", (g.getAttribute("data-open") !== "true").toString()); };
      g.onblur = function () { g.setAttribute("data-open", "false"); };
    });
  }

  /* ---------- Video click-to-load ---------- */
  function wireVideos(root) {
    $all(".video[data-yt]", root).forEach(function (v) {
      if (v.__wired) return; v.__wired = true;
      v.setAttribute("role", "button");
      v.setAttribute("tabindex", "0");
      function load() {
        var id = v.getAttribute("data-yt");
        var start = v.getAttribute("data-start");
        var src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1&playsinline=1" + (start ? "&start=" + start : "");
        v.innerHTML = '<iframe src="' + src + '" title="' + (v.getAttribute("data-title") || "Video") + '" allow="accelerated-motion; autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
      }
      v.onclick = load;
      v.onkeydown = function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); load(); } };
    });
  }
  window.B4H_wireDynamic = function (root) {
    renderIcons(root); wireAccordions(root); wireTabs(root); wireFlips(root); wireGlossary(root); wireVideos(root);
  };

  /* ---------- Boot ---------- */
  function boot() {
    loadPartials().then(function () {
      renderIcons(document);
      if (window.B4H_applyI18n) window.B4H_applyI18n(document);
      $all("[data-year]").forEach(function (e) { e.textContent = new Date().getFullYear(); });
      wireControls(document);
      wireReaderMenu(document);
      wireNav(document);
      syncControls();
      wireReveal();
      wireScrollUI();
      wireTOC();
      wireAccordions(document);
      wireTabs(document);
      wireFlips(document);
      wireGlossary(document);
      wireVideos(document);
      document.dispatchEvent(new CustomEvent("b4h:ready"));
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
