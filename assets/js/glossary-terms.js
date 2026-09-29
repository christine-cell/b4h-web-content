/* ============================================================
   glossary-terms.js — in-context glossary tooltips.
   Auto-links the FIRST mention of each glossary term inside lesson
   body text (per language), wrapping it in a .gloss popover sourced
   from data/glossary.json. Works on hover, tap, and keyboard.

   Design guardrails:
   - Body prose only; never headings, links, buttons, callout titles,
     the glossary page, quizzes, code, or existing .gloss spans.
   - First occurrence per term per page (no dotted-underline soup).
   - Text-node walking only — it never rewrites markup, so it can't
     corrupt attributes or tags.
   ============================================================ */
(function () {
  var BASE = window.B4H_BASE || "/";
  var SKIP_SEL = "a,h1,h2,h3,h4,h5,h6,button,script,style,code,pre,.gloss,.callout-title,.eyebrow,.label,.status-chip,.btn,.quiz,.video,.file-card,.pager,figcaption,dt";
  // Terms we deliberately do NOT auto-link (too frequent / style phrases).
  var EXCLUDE = { "Person living with Parkinson's": 1 };

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  // Derive the searchable surface phrases from a display term.
  function matchPhrases(display) {
    if (!display) return [];
    var out = [];
    // Acronym in parentheses, e.g. "(FOG)" -> case-sensitive match.
    var acr = display.match(/\(([A-Z][A-Z0-9&\-]{1,})\)/);
    // Core: strip parentheticals and quote marks.
    var core = display.replace(/\s*\([^)]*\)/g, "").replace(/[«»""]/g, "").trim();
    // Split only on a spaced slash ("a / b" = alternatives), not "On/Off".
    core.split(/\s+\/\s+/).forEach(function (p) {
      p = p.trim();
      if (p.length >= 4) out.push({ p: p, cs: false });
    });
    if (acr && acr[1].length >= 2) out.push({ p: acr[1], cs: true });
    return out;
  }

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  function buildEntries(terms, lang) {
    var entries = [];
    terms.forEach(function (t) {
      if (EXCLUDE[t.en]) return;
      var def = t["def_" + lang];
      var name = t[lang];
      if (!def || !name) return;
      matchPhrases(t[lang]).forEach(function (ph) {
        var flags = "u" + (ph.cs ? "" : "i");
        var re;
        try {
          re = new RegExp("(?<![\\p{L}\\p{N}])" + escapeRe(ph.p) + "(?![\\p{L}\\p{N}])", flags);
        } catch (e) {
          re = new RegExp("\\b" + escapeRe(ph.p) + "\\b", ph.cs ? "" : "i");
        }
        entries.push({ re: re, len: ph.p.length, term: t.en, name: name, def: def, cat: t.cat });
      });
    });
    entries.sort(function (a, b) { return b.len - a.len; }); // longest first
    return entries;
  }

  var popId = 0;
  function makeGloss(text, entry) {
    var span = document.createElement("span");
    span.className = "gloss";
    span.setAttribute("data-cat", entry.cat);
    span.setAttribute("tabindex", "0");
    span.setAttribute("role", "button");
    span.textContent = text;
    var pop = document.createElement("span");
    pop.className = "gloss-pop";
    pop.id = "glosspop-" + (++popId);
    pop.setAttribute("role", "tooltip");
    pop.textContent = entry.def;
    span.setAttribute("aria-describedby", pop.id);
    span.setAttribute("aria-label", entry.name);
    span.appendChild(pop);
    span.__wired = true;
    wire(span, pop);
    return span;
  }

  function position(span, pop) {
    pop.style.transform = "translate(-50%,0)";
    var r = pop.getBoundingClientRect(), pad = 10, shift = 0;
    if (r.left < pad) shift = pad - r.left;
    else if (r.right > window.innerWidth - pad) shift = (window.innerWidth - pad) - r.right;
    if (shift) pop.style.transform = "translate(calc(-50% + " + Math.round(shift) + "px),0)";
  }

  var openEls = [];
  function closeAll(except) {
    openEls = openEls.filter(function (el) {
      if (el !== except) { el.setAttribute("data-open", "false"); return false; }
      return true;
    });
  }
  function wire(span, pop) {
    function set(open) {
      span.setAttribute("data-open", open ? "true" : "false");
      if (open) { closeAll(span); openEls.push(span); position(span, pop); }
      else closeAll(null);
    }
    span.addEventListener("click", function (e) { e.stopPropagation(); set(span.getAttribute("data-open") !== "true"); });
    span.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); set(span.getAttribute("data-open") !== "true"); }
      else if (e.key === "Escape") { set(false); span.blur(); }
    });
    span.addEventListener("mouseenter", function () { position(span, pop); });
    span.addEventListener("blur", function () { set(false); });
  }

  // Walk one language block, wrapping first mention of each unused term.
  function glossScope(rootEl, entries) {
    var used = {};
    var active = entries.slice();
    var walker = document.createTreeWalker(rootEl, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        var pe = n.parentElement;
        if (!pe || pe.closest(SKIP_SEL)) return NodeFilter.FILTER_REJECT;
        // Never gloss text whose direct parent lays out its children with flex or
        // grid — inserting a <span> there creates a stray flex/grid item and breaks
        // the layout (e.g. the checkmark grid in .check-list objectives/takeaways).
        var disp = getComputedStyle(pe).display;
        if (disp === "flex" || disp === "grid" || disp === "inline-flex" || disp === "inline-grid") return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);

    nodes.forEach(function (node) {
      var current = node;
      var guard = 0;
      while (current && guard++ < 40) {
        var text = current.nodeValue;
        var best = null, bestIdx = Infinity, bestLen = 0;
        for (var i = 0; i < active.length; i++) {
          if (used[active[i].term]) continue;
          var m = active[i].re.exec(text);
          if (m && m.index < bestIdx) { best = active[i]; bestIdx = m.index; bestLen = m[0].length; }
        }
        if (!best) break;
        used[best.term] = 1;
        var after = current.splitText(bestIdx);
        var rest = after.splitText(bestLen);
        var span = makeGloss(after.nodeValue, best);
        after.parentNode.replaceChild(span, after);
        current = rest; // keep scanning the remainder of this node
      }
    });
  }

  ready(function () {
    var scopes = document.querySelectorAll(".lesson-body");
    if (!scopes.length) return;
    fetch(BASE + "data/glossary.json").then(function (r) { return r.json(); }).then(function (data) {
      var terms = data.terms || [];
      var byLang = { en: buildEntries(terms, "en"), fr: buildEntries(terms, "fr") };
      scopes.forEach(function (scope) {
        ["en", "fr"].forEach(function (L) {
          var blocks = scope.querySelectorAll('[data-lang-block="' + L + '"]');
          var list = blocks.length ? blocks : (scope.getAttribute("data-lang-block") === L ? [scope] : []);
          list.forEach(function (b) { glossScope(b, byLang[L]); });
        });
      });
      document.addEventListener("click", function () { closeAll(null); });
    }).catch(function () {});
  });
})();
