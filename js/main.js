/* Toronto Millworks, progressive enhancement only.
   Nothing here is required for a page to render or to be read: every page is
   complete HTML before this runs, and every feature below degrades to that. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── navigation: the services menu, and the phone sheet ───────
     The Services link always goes to the hub. On a desk the panel opens on
     hover with a short intent delay, or from the caret beside the link; on a
     phone the caret folds the list open inside the menu. */
  (function nav () {
    var bar    = document.querySelector(".nav");
    var burger = document.querySelector(".nav__burger");
    var menu   = document.getElementById("nav-menu");
    if (!bar || !burger || !menu) return;

    var sub   = bar.querySelector(".has-sub");
    var caret = sub && sub.querySelector(".nav__caret");
    var phone = window.matchMedia("(max-width: 860px)");
    var root  = document.documentElement;

    function setMenu (open) {
      menu.classList.toggle("is-shown", open);
      bar.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", String(open));
      burger.querySelector(".sr-only").textContent = open ? "Close menu" : "Menu";
      root.classList.toggle("is-locked", open);
    }
    function setSub (open) {
      if (!sub) return;
      sub.classList.toggle("is-open", open);
      caret.setAttribute("aria-expanded", String(open));
    }
    function isOpen () { return burger.getAttribute("aria-expanded") === "true"; }

    burger.addEventListener("click", function () { setMenu(!isOpen()); });

    if (sub && caret) {
      caret.addEventListener("click", function (e) {
        e.stopPropagation();
        setSub(caret.getAttribute("aria-expanded") !== "true");
      });
      var t = 0;
      sub.addEventListener("pointerenter", function (e) {
        if (phone.matches || e.pointerType !== "mouse") return;
        clearTimeout(t); t = setTimeout(function () { setSub(true); }, 90);
      });
      sub.addEventListener("pointerleave", function (e) {
        if (phone.matches || e.pointerType !== "mouse") return;
        clearTimeout(t); t = setTimeout(function () { setSub(false); }, 240);
      });
      sub.addEventListener("focusout", function (e) {
        if (!phone.matches && !sub.contains(e.relatedTarget)) setSub(false);
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        if (sub && sub.classList.contains("is-open")) { setSub(false); if (!phone.matches) caret.focus(); }
        if (isOpen()) { setMenu(false); burger.focus(); }
      }
      /* keep Tab inside the open phone menu */
      if (e.key === "Tab" && isOpen()) {
        var f = [burger].concat([].slice.call(menu.querySelectorAll("a, button")).filter(function (el) {
          return el.offsetParent !== null;
        }));
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
      }
    });
    document.addEventListener("click", function (e) {
      if (bar.contains(e.target)) return;
      setSub(false);
      if (isOpen()) setMenu(false);
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) { setMenu(false); setSub(false); }
    });
    phone.addEventListener("change", function () { setMenu(false); setSub(false); });
  })();

  /* ══════════════════════════════════════════════════════════
     REEL, scroll-scrubbed frame sequence
     ══════════════════════════════════════════════════════════ */
  (function reel () {
    var section = document.querySelector(".reel");
    if (!section || reduced) return;

    var track  = section.querySelector(".reel__track");
    var cv     = section.querySelector(".reel__canvas");
    if (!track || !cv) return;

    var ctx = cv.getContext("2d", { alpha: false });
    if (!ctx) return;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";

    var COUNT  = 118;
    var SMOOTH = 0.15;    /* damped follow, lower is silkier, slower to settle */

    /* ── which tier this device should pull ─────────────────
       Encoded weight is ~11/22/30/43 MB. Decoded frames are handed to the
       browser's own image cache (HTMLImageElement, not ImageBitmap) so it
       can evict under pressure instead of us pinning gigabytes of pixels.
       The 3840 tier is gated hard: it is only worth its weight on a large
       high density display with the memory to hold it. */
    function pickTier () {
      var c = navigator.connection || {};
      if (c.saveData) return 1280;
      if (/(^|-)2g$/.test(c.effectiveType || "")) return 1280;

      var dpr  = Math.min(window.devicePixelRatio || 1, 2);
      var need = Math.max(window.innerWidth, 1) * dpr;
      var mem  = navigator.deviceMemory || 4;

      if (need >= 4200 && mem >= 8) return 3840;
      if (need >= 2400 && mem >= 8) return 2560;
      if (need >= 1500) return 1920;
      return 1280;
    }

    var TIER  = pickTier();
    var frames = new Array(COUNT);
    var ready  = 0;

    function src (i) {
      return "assets/millwork-fit-out-sequence/" + TIER + "/" + String(i + 1).padStart(3, "0") + ".webp";
    }

    /* nearest already-decoded frame, so early scrubbing never blanks out */
    function frameAt (i) {
      var f = frames[i];
      if (f && f.ok) return f.el;
      for (var d = 1; d < COUNT; d++) {
        var a = frames[i - d], b = frames[i + d];
        if (a && a.ok) return a.el;
        if (b && b.ok) return b.el;
      }
      return null;
    }

    /* ── paint ──────────────────────────────────────────────── */
    function cover (img) {
      var cw = cv.width, ch = cv.height;
      var iw = img.naturalWidth, ih = img.naturalHeight;
      if (!iw || !ih) return;
      var s = Math.max(cw / iw, ch / ih);
      var w = iw * s, h = ih * s;
      ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
    }

    var cur = 0;

    function render (p) {
      var f = p * (COUNT - 1);
      var i = Math.floor(f);
      var frac = f - i;

      var a = frameAt(i);
      if (!a) return;

      ctx.globalAlpha = 1;
      cover(a);

      /* cross-fade into the next frame so motion is continuous rather than
         102 discrete steps, this is what makes the scrub read as smooth */
      if (frac > 0.004) {
        var b = frameAt(Math.min(i + 1, COUNT - 1));
        if (b && b !== a) {
          ctx.globalAlpha = frac;
          cover(b);
          ctx.globalAlpha = 1;
        }
      }

    }

    function resize () {
      var r = cv.getBoundingClientRect();
      if (!r.width || !r.height) return;
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = Math.round(r.width * dpr), h = Math.round(r.height * dpr);
      if (cv.width !== w || cv.height !== h) {
        cv.width = w; cv.height = h;
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "high";
        render(cur);
      }
    }

    /* ── scroll → progress ──────────────────────────────────── */
    function progress () {
      var r = track.getBoundingClientRect();
      var span = r.height - window.innerHeight;
      if (span <= 0) return 0;
      var p = -r.top / span;
      return p < 0 ? 0 : p > 1 ? 1 : p;
    }

    var raf = 0, running = false, live = false;

    function loop () {
      var t = progress();
      var d = t - cur;
      cur += d * SMOOTH;
      if (Math.abs(d) < 0.00015) cur = t;
      render(cur);
      raf = requestAnimationFrame(loop);
    }

    function run (on) {
      if (on === running) return;
      running = on;
      if (on) { resize(); raf = requestAnimationFrame(loop); }
      else cancelAnimationFrame(raf);
    }

    /* ── load ───────────────────────────────────────────────── */
    function loadOne (i) {
      return new Promise(function (resolve) {
        var el = new Image();
        el.decoding = "async";
        var rec = { el: el, ok: false };
        frames[i] = rec;
        el.onload = function () {
          var done = function () { rec.ok = true; ready++; resolve(); };
          if (el.decode) el.decode().then(done, done); else done();
        };
        el.onerror = function () { resolve(); };
        el.src = src(i);
      });
    }

    /* coarse pass first (every 6th frame) so the whole span is scrubbable
       early, then fill in the gaps */
    function order () {
      var seen = {}, out = [], i;
      for (i = 0; i < COUNT; i += 6) { seen[i] = 1; out.push(i); }
      if (!seen[COUNT - 1]) out.push(COUNT - 1);
      for (i = 0; i < COUNT; i++) if (!seen[i] && i !== COUNT - 1) out.push(i);
      return out;
    }

    function pump (queue, width, onCoarse, coarseN) {
      var next = 0, active = 0, fired = false;
      return new Promise(function (resolve) {
        function done () {
          active--;
          if (!fired && ready >= coarseN) { fired = true; if (onCoarse) onCoarse(); }
          step();
        }
        function step () {
          if (next >= queue.length && active === 0) return resolve();
          while (active < width && next < queue.length) {
            active++;
            loadOne(queue[next++]).then(done);
          }
        }
        step();
      });
    }

    function goLive () {
      if (live) return;
      live = true;
      section.classList.add("is-live");
      resize();
      render(cur);
    }

    var started = false;
    function start () {
      if (started) return;
      started = true;

      var q = order();
      var coarseN = Math.ceil(COUNT / 6) + 1;
      pump(q, 8, goLive, coarseN).then(goLive);
    }

    /* begin fetching well before the section arrives, and only spin the rAF
       loop while it is actually near the viewport */
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) start();
      }, { rootMargin: "150% 0px" }).observe(section);

      new IntersectionObserver(function (es) {
        run(es[0].isIntersecting);
      }, { rootMargin: "20% 0px" }).observe(section);
    } else {
      start(); run(true);
    }

    window.addEventListener("resize", resize, { passive: true });
    window.addEventListener("orientationchange", resize, { passive: true });
  })();
})();

/* ── site search, on /search/ only ───────────────────────────── */
(function () {
  "use strict";
  var input = document.getElementById("q");
  var out = document.getElementById("results");
  if (!input || !out) return;
  var count = document.querySelector(".srch__n");
  var data = [];

  function esc (s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function mark (s, terms) {
    var h = esc(s);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      h = h.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    });
    return h;
  }
  function run () {
    var q = input.value.trim().toLowerCase();
    if (!q) { out.innerHTML = ""; count.textContent = ""; return; }
    var terms = q.split(/\s+/);
    var hits = data.map(function (d) {
      var hay = (d.t + " " + d.d + " " + d.k + " " + d.g).toLowerCase();
      if (!terms.every(function (t) { return hay.indexOf(t) !== -1; })) return null;
      var score = terms.reduce(function (s, t) { return s + (d.t.toLowerCase().indexOf(t) !== -1 ? 3 : 1); }, 0);
      return { d: d, s: score };
    }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).slice(0, 20);
    count.textContent = hits.length ? hits.length + (hits.length === 1 ? " result" : " results") : "No results";
    out.innerHTML = hits.length
      ? hits.map(function (h) {
          return '<li><a href="' + esc(h.d.u) + '"><span class="srch__g">' + esc(h.d.g) + '</span>' +
                 '<span class="srch__t">' + mark(h.d.t, terms) + '</span>' +
                 '<span class="srch__d">' + mark(h.d.d, terms) + "</span></a></li>";
        }).join("")
      : '<li><span class="srch__d" style="padding:1.2em 0;display:block">Nothing matched. Try kitchens, panelling, a bar, or the name of your town.</span></li>';
  }
  fetch("/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (j) { data = j; run(); })
    .catch(function () { data = []; });
  input.addEventListener("input", run);
  document.querySelector(".srch__form").addEventListener("submit", function (e) { e.preventDefault(); run(); });
  var qs = new URLSearchParams(location.search).get("q");
  if (qs) input.value = qs;
})();

/* ── copy the email address on the contact page ──────────────── */
(function () {
  "use strict";
  var btn = document.querySelector(".cx__copy");
  if (!btn || !navigator.clipboard) { if (btn) btn.hidden = true; return; }
  var idle = btn.textContent, timer;
  btn.addEventListener("click", function () {
    navigator.clipboard.writeText(btn.getAttribute("data-copy") || "").then(function () {
      btn.textContent = "Copied"; btn.classList.add("is-done");
      clearTimeout(timer);
      timer = setTimeout(function () { btn.textContent = idle; btn.classList.remove("is-done"); }, 2000);
    }).catch(function () { /* clipboard blocked; the mailto link still works */ });
  });
})();

/* ── the About statement writes itself in as you scroll ────────
   The sentence ships as one clean paragraph. It is split into words and
   characters here, at runtime, so the markup a crawler or a reader without
   JS sees is untouched. The split copy is then hidden from assistive tech
   and the original sentence put back beside it, so a screen reader still
   hears one sentence rather than two hundred and ninety letters.

   Reveal runs on scrub, finishing as the section's middle reaches the middle
   of the screen, which is about halfway through reading it. */
(function () {
  "use strict";

  var p = document.querySelector(".about__text");
  if (!p) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!window.gsap || !window.ScrollTrigger) return;   /* text stays visible */

  var sentence = p.textContent.replace(/\s+/g, " ").trim();
  var chars = [];

  (function split(node) {
    Array.prototype.slice.call(node.childNodes).forEach(function (n) {
      if (n.nodeType === 1) { split(n); return; }
      if (n.nodeType !== 3) return;

      var frag = document.createDocumentFragment();
      n.nodeValue.split(/(\s+)/).forEach(function (tok) {
        if (!tok) return;
        if (/^\s+$/.test(tok)) {              /* keep one real break opportunity */
          frag.appendChild(document.createTextNode(" "));
          return;
        }
        var word = document.createElement("span");
        word.className = "sw";
        for (var i = 0; i < tok.length; i++) {
          var c = document.createElement("span");
          c.className = "sc";
          c.textContent = tok.charAt(i);
          word.appendChild(c);
          chars.push(c);
        }
        frag.appendChild(word);
      });
      node.replaceChild(frag, n);
    });
  })(p);

  if (!chars.length) return;

  var split = document.createElement("span");
  split.className = "about__split";
  split.setAttribute("aria-hidden", "true");
  while (p.firstChild) split.appendChild(p.firstChild);

  var sr = document.createElement("span");
  sr.className = "sr-only";
  sr.textContent = sentence;

  p.appendChild(sr);
  p.appendChild(split);

  gsap.registerPlugin(ScrollTrigger);

  /* under scrub only the ratio of duration to stagger matters: each character
     fades over eight neighbours' worth of scroll, which is short enough to
     read as letter by letter and long enough not to look like a stepper */
  gsap.fromTo(chars, { opacity: 0.13 }, {
    opacity: 1,
    ease: "none",
    duration: 0.4,
    stagger: { each: 0.05, from: "start" },
    scrollTrigger: {
      trigger: p.closest(".about") || p,
      start: "top 84%",
      end: "center 58%",
      scrub: 0.4
    }
  });

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  }
})();

/* ── FAQ accordions ───────────────────────────────────────────
   <details> already toggles and is keyboard accessible on its own, so this
   only takes over to ease the height. If it never runs, the accordions still
   work, just without the animation. */
(function () {
  "use strict";
  var rows = document.querySelectorAll(".faq__row");
  if (!rows.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!Element.prototype.animate) return;

  var DUR = 420;
  var EASE = "cubic-bezier(.22,.61,.36,1)";

  Array.prototype.forEach.call(rows, function (row) {
    var summary = row.querySelector(".faq__q");
    var panel = row.querySelector(".faq__panel");
    if (!summary || !panel) return;

    var anim = null;
    var closing = false;

    function run(from, to, dur, done) {
      if (anim) anim.cancel();
      anim = panel.animate(
        [{ height: from + "px", opacity: from ? 1 : 0 },
         { height: to + "px", opacity: to ? 1 : 0 }],
        { duration: dur, easing: EASE }
      );
      anim.onfinish = function () { anim = null; if (done) done(); };
      anim.oncancel = function () { anim = null; };
    }

    function open() {
      /* read the live height before cancelling, so reversing mid-close
         continues from where it actually is instead of snapping */
      var from = anim ? panel.getBoundingClientRect().height : 0;
      closing = false;
      row.open = true;
      run(from, panel.scrollHeight, DUR);
    }

    function close() {
      var from = panel.getBoundingClientRect().height;
      closing = true;
      run(from, 0, Math.round(DUR * 0.85), function () {
        row.open = false;
        closing = false;
      });
    }

    summary.addEventListener("click", function (e) {
      e.preventDefault();
      if (row.open && !closing) close();
      else open();
    });
  });
})();

/* ── drawings and maps: constant line weight, and the draw-on ─────
   A sheet scales with its column but its labels and hairlines should not,
   so its current scale is written into --dws for the CSS to divide by. */
var TM = (function () {
  "use strict";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var svgs = document.querySelectorAll("svg.dw, svg.mp");

  function fit (svg) {
    var vb = svg.viewBox && svg.viewBox.baseVal;
    var w = svg.getBoundingClientRect().width;
    if (!vb || !vb.width || !w) return;
    svg.style.setProperty("--dws", (w / vb.width).toFixed(4));
  }
  if ("ResizeObserver" in window) {
    var ro = new ResizeObserver(function (es) { es.forEach(function (e) { fit(e.target); }); });
    svgs.forEach(function (s) { ro.observe(s); });
  } else {
    svgs.forEach(fit);
    window.addEventListener("resize", function () { svgs.forEach(fit); });
  }

  /* draw a sheet from blank; switchers call this when they change sheet */
  function draw (svg) {
    if (!svg || reduced) return;
    svg.classList.add("is-armed");
    svg.classList.remove("is-drawn");
    void svg.getBoundingClientRect();
    svg.classList.add("is-drawn");
  }

  /* Only a sheet marked data-draw sketches itself in, once, as it arrives. A
     process stage draws when it is picked, and a page title's own sheet draws
     with the title; both are left to their sections. Sheets that arrive
     together go left to right, a beat apart, as one gesture. */
  if (!reduced && "IntersectionObserver" in window) {
    var solo = [].filter.call(document.querySelectorAll("svg.dw[data-draw]"), function (s) {
      return !s.closest(".prc__sheet, .ph__sheet");
    });
    solo.forEach(function (s) { s.classList.add("is-armed"); });
    var io = new IntersectionObserver(function (es) {
      es.filter(function (e) { return e.isIntersecting; })
        .sort(function (a, b) { return a.boundingClientRect.left - b.boundingClientRect.left; })
        .forEach(function (e, k) {
          if (k) e.target.style.setProperty("--dd", k * 150 + "ms");
          e.target.classList.add("is-drawn"); io.unobserve(e.target);
        });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    solo.forEach(function (s) { io.observe(s); });
    /* anything already scrolled past is simply finished */
    window.addEventListener("load", function () {
      solo.forEach(function (s) {
        if (s.getBoundingClientRect().bottom < 0) { s.classList.add("is-drawn"); io.unobserve(s); }
      });
    });
  }
  if (!reduced && "IntersectionObserver" in window) {
    var mo = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-live"); mo.unobserve(e.target); }
      });
    }, { threshold: 0.3 });
    document.querySelectorAll("svg.mp").forEach(function (m) { mo.observe(m); });
  }
  return { draw: draw, reduced: reduced };
})();

/* ── the service-area map talks to the list beside it ─────────── */
(function () {
  "use strict";
  var hub = document.querySelector(".mp--hub");
  if (!hub) return;
  var list = document.querySelector(".rx");
  var NS = "http://www.w3.org/2000/svg";
  var tip = null;

  function set (slug, on) {
    var town = hub.querySelector('.mp-town[data-slug="' + slug + '"]');
    var name = hub.querySelector('.mp-name[data-for="' + slug + '"]');
    if (town) town.classList.toggle("is-on", on);
    if (name) name.classList.toggle("is-on", on);
    if (list) {
      var a = list.querySelector('.rx__a[data-slug="' + slug + '"]');
      if (a) a.classList.toggle("is-on", on);
    }
    /* towns without a printed label get a quiet one while pointed at */
    if (tip) { tip.remove(); tip = null; }
    var shown = name && getComputedStyle(name).display !== "none";
    if (on && town && !shown) {
      var c = town.querySelector(".mp-dot");
      tip = document.createElementNS(NS, "text");
      tip.setAttribute("class", "mp-name is-on");
      tip.setAttribute("x", +c.getAttribute("cx") + 2.4);
      tip.setAttribute("y", +c.getAttribute("cy") - 2.2);
      tip.textContent = town.getAttribute("aria-label");
      hub.appendChild(tip);
    }
  }
  hub.querySelectorAll(".mp-town[data-slug]").forEach(function (t) {
    var s = t.getAttribute("data-slug");
    t.addEventListener("pointerenter", function () { set(s, true); });
    t.addEventListener("pointerleave", function () { set(s, false); });
  });
  if (list) list.querySelectorAll(".rx__a[data-slug]").forEach(function (a) {
    var s = a.getAttribute("data-slug");
    a.addEventListener("pointerenter", function () { set(s, true); });
    a.addEventListener("pointerleave", function () { set(s, false); });
    a.addEventListener("focus", function () { set(s, true); });
    a.addEventListener("blur", function () { set(s, false); });
  });
})();

/* ── images: fade in over their placeholder; features rise into place ── */
(function () {
  "use strict";
  document.querySelectorAll(".fig img").forEach(function (img) {
    var done = function () { img.classList.add("is-in"); };
    if (img.complete && img.naturalWidth) done();
    else { img.addEventListener("load", done, { once: true }); img.addEventListener("error", done, { once: true }); }
  });
  if (TM.reduced || !("IntersectionObserver" in window)) return;

  /* the shutter is for single feature images; galleries and pairs simply arrive */
  var figs = [].slice.call(document.querySelectorAll(".fs__f, .case__f, .loc__f"));
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add("is-shown"); io.unobserve(e.target);
    });
  }, { rootMargin: "0px 0px -6% 0px" });
  figs.forEach(function (f) {
    /* only what starts below the fold, so nothing on screen at load flickers */
    if (f.getBoundingClientRect().top < window.innerHeight * 0.94) return;
    f.classList.add("is-clip"); io.observe(f);
  });
  /* a jump past a figure never intersects it; reveal anything left above */
  var queued = false;
  window.addEventListener("scroll", function () {
    if (queued) return; queued = true;
    requestAnimationFrame(function () {
      queued = false;
      figs.forEach(function (f) {
        if (f.classList.contains("is-clip") && !f.classList.contains("is-shown") &&
            f.getBoundingClientRect().bottom < 0) { f.classList.add("is-shown"); io.unobserve(f); }
      });
    });
  }, { passive: true });
})();

/* ── headings: four quick reveals, each played once ─────────────
   rise   page titles: characters lift out of their own word, ~10 ms apart
   write  section titles: words uncovered left to right at a pen's pace,
          the ink settling from brass
   focus  the closing asks: characters pull into focus
   ghost  statements: words darken from a faint first pass
   A heading is split only while it moves. Where each character really
   sits, kerning included, is measured first and kept, and the heading's
   own markup goes back the moment it lands, so the page keeps its text. */
(function () {
  "use strict";
  if (TM.reduced || !("IntersectionObserver" in window)) return;
  var KINDS = [
    ["rise", ".hero__title, .ph__t, .cx__title, .nf__h"],
    ["write", ".sh__t, .faq__h, .map__h, .fs__h, .craft__title, .cx__next-h"],
    ["focus", ".qs__t, .foot__title"],
    ["ghost", ".say__t"]
  ];
  var CHARS = { rise: true, focus: true };
  var FOLLOW = ".ph__l, .ph__a, .ph__note, .hero__lede, .hero__cta";

  function texts (root) {
    var out = [];
    (function walk (n) {
      [].forEach.call(n.childNodes, function (c) {
        if (c.nodeType === 3) out.push(c);
        else if (c.nodeType === 1 && c.tagName !== "BR") walk(c);
      });
    })(root);
    return out;
  }

  /* the left edge of every visible character, as the browser set it */
  function lefts (h) {
    var xs = [], r = document.createRange();
    texts(h).forEach(function (t) {
      for (var i = 0; i < t.nodeValue.length; i++) {
        if (/\s/.test(t.nodeValue.charAt(i))) continue;
        r.setStart(t, i); r.setEnd(t, i + 1);
        xs.push(r.getBoundingClientRect().left);
      }
    });
    return xs;
  }

  function split (h, chars) {
    var words = [];
    texts(h).forEach(function (t) {
      var frag = document.createDocumentFragment();
      t.nodeValue.split(/(\s+)/).forEach(function (tok) {
        if (!tok) return;
        if (/^\s+$/.test(tok)) { frag.appendChild(document.createTextNode(" ")); return; }
        /* a hyphen is a place the line may break, so it ends a unit too */
        tok.match(/[^-]+-?|-/g).forEach(function (part) {
          var w = document.createElement("span");
          w.className = "tx-w";
          if (chars) {
            for (var i = 0; i < part.length; i++) {
              var c = document.createElement("span");
              c.className = "tx-c";
              c.textContent = part.charAt(i);
              w.appendChild(c);
            }
          } else w.textContent = part;
          frag.appendChild(w);
          words.push(w);
        });
      });
      t.parentNode.replaceChild(frag, t);
    });
    return words;
  }

  function prepare () {
    var items = [];
    KINDS.forEach(function (k) {
      document.querySelectorAll(k[1]).forEach(function (h) {
        if (!h.classList.contains("tx")) items.push({ h: h, kind: k[0], chars: !!CHARS[k[0]] });
      });
    });
    /* after the safety net has shown the headings, leave them be */
    if (performance.now() > 2200) {
      items.forEach(function (it) { it.h.classList.add("tx"); });
      return [];
    }
    /* reads, then writes, then reads, then writes: four layouts, not hundreds.
       Widths are read before the effect's class goes on, while nothing is
       turned or scaled, so they are the characters' true advances. */
    items.forEach(function (it) { it.orig = it.h.innerHTML; if (it.chars) it.xs = lefts(it.h); });
    items.forEach(function (it) {
      it.words = split(it.h, it.chars);
      it.h.setAttribute("aria-label", it.h.textContent.replace(/\s+/g, " ").trim());
    });
    items.forEach(function (it) {
      it.fs = parseFloat(getComputedStyle(it.h).fontSize) || 16;
      if (!it.chars) return;
      it.cs = [].slice.call(it.h.querySelectorAll(".tx-c"));
      it.ws = it.cs.map(function (c) { return c.getBoundingClientRect().width; });
    });
    items.forEach(function (it) {
      if (it.chars && it.xs.length === it.cs.length) {
        var k = 0;
        it.words.forEach(function (w) {
          for (var j = 0; j < w.children.length; j++, k++) {
            if (!j) continue;
            var m = (it.xs[k] - it.xs[k - 1]) - it.ws[k - 1];
            if (Math.abs(m) > 0.05) it.cs[k].style.marginLeft = (m / it.fs).toFixed(4) + "em";
          }
        });
      }
      it.h.classList.add("tx", "tx--" + it.kind);
    });
    return items;
  }

  function play (it) {
    var h = it.h, t0 = h.classList.contains("hero__title") ? 160 : 0, end;
    if (it.chars) {
      var n = it.cs.length, rise = it.kind === "rise";
      var st = Math.min(rise ? 11 : 16, (rise ? 380 : 420) / Math.max(n, 1));
      it.cs.forEach(function (c, i) { c.style.setProperty("--t", Math.round(t0 + i * st) + "ms"); });
      end = t0 + (n - 1) * st + (rise ? 620 : 800);
    } else if (it.kind === "write") {
      var t = t0;
      it.words.forEach(function (w) {
        var d = Math.max(70, w.getBoundingClientRect().width / it.fs / 30 * 1000);   /* 30 em a second */
        w.style.setProperty("--t", Math.round(t) + "ms");
        w.style.setProperty("--d", Math.round(d) + "ms");
        t += d + 8;
      });
      end = t + 800;
    } else {
      var gs = Math.min(30, 700 / Math.max(it.words.length, 1));
      it.words.forEach(function (w, i) { w.style.setProperty("--t", Math.round(t0 + i * gs) + "ms"); });
      end = t0 + (it.words.length - 1) * gs + 550;
    }
    h.classList.add("tx-in");
    if (it.kind === "rise") follow(h, t0);
    setTimeout(function () {
      h.innerHTML = it.orig;
      h.removeAttribute("aria-label");
      h.classList.remove("tx--" + it.kind, "tx-in");
    }, end + 80);
  }

  /* a page title brings its lede, its actions and its drawing in behind it */
  function follow (h, t0) {
    var scope = h.closest(".ph, .hero");
    if (!scope) return;
    [].forEach.call(scope.querySelectorAll(FOLLOW), function (el, i) {
      el.classList.add("tx-follow");
      el.style.setProperty("--t", t0 + 220 + i * 90 + "ms");
      requestAnimationFrame(function () { el.classList.add("tx-in"); });
    });
    var dw = scope.querySelector(".ph__sheet svg.dw[data-draw]");
    if (dw) {
      dw.style.setProperty("--dd", t0 + 340 + "ms");
      requestAnimationFrame(function () { dw.classList.add("is-drawn"); });
    }
  }

  function start () {
    var items = prepare();
    if (!items.length) return;
    document.querySelectorAll(".ph__sheet svg.dw[data-draw]").forEach(function (s) { s.classList.add("is-armed"); });
    var map = new Map(items.map(function (it) { return [it.h, it]; }));
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting || !map.has(e.target)) return;
        io.unobserve(e.target);
        var it = map.get(e.target);
        map.delete(e.target);
        requestAnimationFrame(function () { play(it); });
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (it) { io.observe(it.h); });
    /* a heading flung past between two frames is never seen to arrive; put it
       back as it is, rather than leave it waiting above the reader */
    var queued = false;
    window.addEventListener("scroll", function () {
      if (queued || !map.size) return;
      queued = true;
      requestAnimationFrame(function () {
        queued = false;
        map.forEach(function (it, h) {
          if (h.getBoundingClientRect().bottom >= 0) return;
          io.unobserve(h);
          map.delete(h);
          h.innerHTML = it.orig;
          h.removeAttribute("aria-label");
          h.classList.remove("tx--" + it.kind);
        });
      });
    }, { passive: true });
  }

  /* Measure with the real face, never the fallback: fonts.ready can resolve
     before a preloaded face is in use, so wait for the face itself. If it is
     not here in time, the headings simply stay as they are. */
  var FACE = "400 1em 'Instrument Sans'";
  var begun = false;
  var go = function (loaded) {
    if (begun) return;
    begun = true;
    if (loaded) start();
    else document.querySelectorAll(KINDS.map(function (k) { return k[1]; }).join(", "))
      .forEach(function (h) { h.classList.add("tx"); });
  };
  if (document.fonts && document.fonts.load) {
    document.fonts.load(FACE).then(function () { go(document.fonts.check(FACE)); }, function () { go(false); });
    setTimeout(function () { go(false); }, 1500);
  } else go(false);
})();

/* ── service index: the row you are on shows its drawing ─────── */
(function () {
  "use strict";
  document.querySelectorAll(".idx__g--peek").forEach(function (g) {
    var pks = g.querySelectorAll(".idx__pk");
    var cur = -1;
    /* a quiet cross-fade: the drawing is there, it does not draw itself again */
    function show (i) {
      if (i === cur) return;
      cur = i;
      pks.forEach(function (p) { p.classList.toggle("is-on", p.getAttribute("data-peek") === String(i)); });
    }
    g.querySelectorAll(".idx__i").forEach(function (r) {
      var i = +r.getAttribute("data-peek");
      r.addEventListener("pointerenter", function () { show(i); });
      r.addEventListener("focusin", function () { show(i); });
    });
    if ("IntersectionObserver" in window) {
      var o = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { show(0); o.disconnect(); }
      }, { threshold: 0.2 });
      o.observe(g);
    } else show(0);
  });
})();

/* ── process: the stage nearest the middle of the screen is live ── */
(function () {
  "use strict";
  var phone = window.matchMedia("(max-width: 899px)");
  document.querySelectorAll(".prc").forEach(function (sec) {
    var items = sec.querySelectorAll(".prc__i");
    var sheets = sec.querySelectorAll(".prc__sheet");
    var stage = sec.querySelector(".prc__stage");
    if (!items.length) return;
    var cur = -1, live = false, queued = false, drawn = [];
    if (!TM.reduced) sheets.forEach(function (s) { var d = s.querySelector("svg.dw[data-draw]"); if (d) d.classList.add("is-armed"); });

    /* each stage draws the first time it is reached; after that it cross-fades */
    function set (i) {
      if (i === cur) return;
      cur = i;
      items.forEach(function (it, k) { it.classList.toggle("is-on", k === i); });
      sheets.forEach(function (s, k) {
        s.classList.toggle("is-on", k === i);
        if (k === i && !drawn[k]) { drawn[k] = true; TM.draw(s.querySelector("svg.dw[data-draw]")); }
      });
    }
    function pick () {
      queued = false;
      var mid = window.innerHeight / 2;
      if (phone.matches && stage) mid = (stage.getBoundingClientRect().bottom + window.innerHeight) / 2;
      var best = 0, bd = Infinity;
      items.forEach(function (it, k) {
        var r = it.getBoundingClientRect();
        var d = Math.abs(r.top + Math.min(r.height, 220) / 2 - mid);
        if (d < bd) { bd = d; best = k; }
      });
      set(best);
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { live = es[0].isIntersecting; if (live) pick(); }).observe(sec);
    } else live = true;
    window.addEventListener("scroll", function () {
      if (!live || queued) return; queued = true; requestAnimationFrame(pick);
    }, { passive: true });
  });
})();

/* ── measurement: every step toward a quote is counted ─────────
   Events go to window.dataLayer, so a tag manager or analytics added later
   sees them without touching this file. Nothing leaves the page until one
   is. Where a click came from is read off the section it sits in. */
var track = function (event, data) {
  var o = { event: event };
  for (var k in data) o[k] = data[k];
  (window.dataLayer = window.dataLayer || []).push(o);
};
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest('a[href*="/contact/"], a[href^="mailto:"], a[href^="tel:"]');
  if (!a) return;
  var h = a.getAttribute("href");
  var where = a.closest(".nav, .dock, .hero, .ph, .ask, .qs, .foot, .nf, .cx, .map, .idx, section");
  track(h.indexOf("tel:") === 0 ? "call_click" : h.indexOf("mailto:") === 0 ? "email_click" : "quote_click", {
    cta_location: where ? where.className.split(" ")[0] || "section" : "page",
    cta_text: a.textContent.replace(/\s+/g, " ").trim().slice(0, 60)
  });
});

/* ── the quote form ─────────────────────────────────────────────
   Three short screens, validated as you go. Sends to the configured form
   endpoint; without one, or if it fails, it composes a complete email in
   the visitor's mail app and shows the same summary to copy. */
(function () {
  "use strict";
  var f = document.querySelector("form.qf");
  if (!f) return;
  var steps = f.querySelectorAll(".qf__step");
  var bar = f.querySelector(".qf__bar"), now = f.querySelector(".qf__now");
  var next = f.querySelector(".qf__next"), back = f.querySelector(".qf__back");
  var done = f.querySelector(".qf__done"), sum = f.querySelector(".qf__sum"), copy = f.querySelector(".qf__copy");
  var endpoint = f.getAttribute("data-endpoint"), email = f.getAttribute("data-email");
  var cur = 0;

  var KEY = "tm-quote", seen = 0;
  function save () {
    try {
      var o = { _step: cur };
      new FormData(f).forEach(function (v, k) { if (k !== "company_site") o[k] = v; });
      sessionStorage.setItem(KEY, JSON.stringify(o));
    } catch (e) {}
  }
  function restore () {
    try {
      var o = JSON.parse(sessionStorage.getItem(KEY) || "null");
      if (!o) return 0;
      Object.keys(o).forEach(function (k) {
        if (k === "_step" || !o[k]) return;
        if (k === "type") {
          var r = f.querySelector('input[name="type"][value="' + o[k] + '"]');
          if (r) r.checked = true;
        } else if (f.elements[k] && f.elements[k].tagName) f.elements[k].value = o[k];
      });
      return Math.min(o._step || 0, steps.length - 1);
    } catch (e) { return 0; }
  }
  f.addEventListener("input", save);
  f.addEventListener("change", save);

  function show (i, focus) {
    cur = i;
    if (i > seen) { seen = i; track("quote_step", { step: i + 1 }); }
    save();
    steps.forEach(function (s, k) { s.classList.toggle("is-on", k === i); });
    bar.style.width = ((i + 1) / steps.length * 100) + "%";
    now.textContent = "Step " + (i + 1);
    back.hidden = i === 0;
    f.classList.toggle("is-last", i === steps.length - 1);
    if (focus) {
      var first = steps[i].querySelector("input:checked, input:not([type=hidden]):not([tabindex='-1']), select, textarea");
      if (first) first.focus({ preventScroll: true });
      var top = f.getBoundingClientRect().top;
      if (top < 80) window.scrollBy({ top: top - 120, behavior: TM.reduced ? "auto" : "smooth" });
    }
  }
  function flag (name, bad) {
    var p = f.querySelector('.fld__err[data-for="' + name + '"]');
    if (p) p.hidden = !bad;
    var el = f.querySelector("#" + name);
    if (el) {
      el.setAttribute("aria-invalid", bad ? "true" : "false");
      if (p) { p.id = p.id || name + "-err"; el.setAttribute("aria-describedby", bad ? p.id : (el.getAttribute("aria-describedby") || "").replace(p.id, "").trim()); }
    }
  }
  function valid (i) {
    var first = null;
    if (i === 0) {
      var chosen = f.querySelector('input[name="type"]:checked');
      flag("type", !chosen);
      if (!chosen) first = f.querySelector('input[name="type"]');
    }
    if (i === 1) {
      var a = f.querySelector("#area");
      flag("area", !a.value);
      if (!a.value) first = a;
    }
    if (i === 2) {
      var n = f.querySelector("#name"), e = f.querySelector("#email");
      var nb = !n.value.trim(), eb = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e.value.trim());
      flag("name", nb); flag("email", eb);
      first = nb ? n : eb ? e : null;
    }
    if (first) first.focus();
    return !first;
  }

  next.addEventListener("click", function () { if (valid(cur)) show(cur + 1, true); });
  back.addEventListener("click", function () { show(cur - 1, true); });
  f.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && cur < steps.length - 1) {
      e.preventDefault(); next.click();
    }
  });
  f.querySelectorAll('input[name="type"]').forEach(function (r) {
    r.addEventListener("change", function () {
      flag("type", false);
      setTimeout(function () { if (cur === 0) show(1, true); }, 280);
    });
  });
  ["area", "name", "email"].forEach(function (n) {
    var el = f.querySelector("#" + n);
    if (el) el.addEventListener("change", function () { if (el.getAttribute("aria-invalid") === "true") valid(cur); });
  });

  /* arrive with what was typed before, then whatever the link tells us */
  var start = restore();
  var qs = new URLSearchParams(location.search);
  var t = qs.get("type"), area = qs.get("area");
  if (t) {
    var r = [].filter.call(f.querySelectorAll('input[name="type"]'), function (x) { return x.value === t; })[0];
    if (r) { r.checked = true; start = Math.max(start, 1); }
  }
  if (area) {
    var sel = f.querySelector("#area");
    if ([].some.call(sel.options, function (o) { return o.value === area; })) sel.value = area;
  }
  if (qs.get("visit")) {
    f.querySelector('input[name="visit"]').value = "yes";
    var m = f.querySelector("#message");
    if (m && !m.value) m.value = "I would like to visit the shop.";
  }

  function label (input) { return input ? input.parentNode.textContent.trim() : ""; }
  function summary () {
    var type = f.querySelector('input[name="type"]:checked');
    var a = f.querySelector("#area");
    var place = a.value ? a.options[a.selectedIndex].text : "";
    var v = function (id) { var el = f.querySelector("#" + id); return el ? el.value.trim() : ""; };
    var lines = ["Project: " + label(type), "Location: " + place, "Timing: " + v("timing"),
                 "Stage: " + v("stage"), "Budget: " + v("budget"), "",
                 "Name: " + v("name"), "Email: " + v("email"), "Phone: " + (v("phone") || "not given")];
    if (v("message")) lines.push("", v("message"));
    if (f.querySelector('input[name="visit"]').value) lines.push("", "Would like to visit the shop.");
    return { subject: "Quote request: " + (label(type) || "a project") + (place ? ", " + place : ""),
             body: lines.join("\n") };
  }
  function finish (viaMail, s) {
    f.classList.add("is-sent");
    done.hidden = false;
    try { sessionStorage.removeItem(KEY); } catch (e) {}
    var type = f.querySelector('input[name="type"]:checked');
    track("quote_submit", { method: viaMail ? "email_app" : "form", project: type ? type.value : "",
                            area: f.querySelector("#area").value });
    if (viaMail) {
      var t = done.querySelector(".qf__done-t");
      t.textContent = t.getAttribute("data-mail-title");
      sum.hidden = false; sum.textContent = s.subject + "\n\n" + s.body;
      if (navigator.clipboard) copy.hidden = false;
    } else {
      done.querySelector("[data-mail-copy]").textContent =
        "We have your details and will reply by email. If anything changes, simply reply to that message.";
    }
    done.focus();
  }
  copy.addEventListener("click", function () {
    navigator.clipboard.writeText(sum.textContent).then(function () {
      copy.querySelector("span").textContent = "Copied";
    }).catch(function () {});
  });
  f.addEventListener("submit", function (e) {
    e.preventDefault();
    if (f.querySelector("#company_site").value) return;            /* a bot filled the honeypot */
    for (var i = 0; i < steps.length; i++) { if (!valid(i)) { show(i, true); return; } }
    var s = summary();
    var mail = function () {
      window.location.href = "mailto:" + email + "?subject=" + encodeURIComponent(s.subject) +
                             "&body=" + encodeURIComponent(s.body);
      finish(true, s);
    };
    if (!endpoint) return mail();
    f.classList.add("is-busy");
    var data = new FormData(f);
    data.append("_subject", s.subject);
    fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); finish(false, s); })
      .catch(mail)
      .then(function () { f.classList.remove("is-busy"); });
  });

  show(start, false);
})();

/* ── guides: contents follow the reading, and a hairline fills ── */
(function () {
  "use strict";
  var toc = document.querySelector(".art__toc");
  if (!toc) return;
  var links = [].slice.call(toc.querySelectorAll("a"));
  var heads = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
  var prog = toc.querySelector(".art__progress");
  var body = document.querySelector(".art__body");
  var queued = false;
  function update () {
    queued = false;
    var y = window.innerHeight * 0.3, cur = 0;
    heads.forEach(function (h, i) { if (h && h.getBoundingClientRect().top < y) cur = i; });
    links.forEach(function (a, i) {
      var on = i === cur;
      a.classList.toggle("is-on", on);
      if (on) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current");
    });
    if (prog && body) {
      var r = body.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, (y - r.top) / Math.max(1, r.height - y)));
      prog.style.setProperty("--read", p.toFixed(3));
    }
  }
  window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();

/* ── the about page bench: steps light up as the carcass assembles ── */
(function () {
  "use strict";
  var b = document.querySelector(".bench");
  if (!b) return;
  var steps = b.querySelectorAll(".bench__steps li");
  var queued = false;
  function update () {
    queued = false;
    var r = b.getBoundingClientRect(), span = r.height - window.innerHeight;
    var p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 1;
    b.style.setProperty("--p", p.toFixed(4));
    var k = Math.min(steps.length - 1, Math.floor(p * steps.length * 0.999));
    steps.forEach(function (s, i) { s.classList.toggle("is-on", i <= k); });
  }
  window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();

/* ── the quote dock on phones ─────────────────────────────────── */
(function () {
  "use strict";
  var d = document.querySelector("[data-dock]");
  if (!d) return;
  var foot = document.querySelector(".foot"), nearFoot = false, on = false, queued = false;
  function update () {
    queued = false;
    var want = window.scrollY > window.innerHeight * 0.8 && !nearFoot;
    if (want !== on) { on = want; d.classList.toggle("is-on", on); }
  }
  if (foot && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) { nearFoot = es[0].isIntersecting; update(); }).observe(foot);
  }
  window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();

/* ── Three.js, only where it earns its weight ─────────────────────
   Loaded as a module on demand, and only when the browser can draw it. The
   page underneath already shows a drawing of the same thing. */
(function () {
  "use strict";
  var kind = document.body.getAttribute("data-three");
  var src = document.body.getAttribute("data-three-src");
  if (!kind || !src) return;
  var host = document.querySelector(kind === "bench" ? ".bench" : ".nf");
  if (!host) return;
  var probe = document.createElement("canvas");
  var ok = false;
  try { ok = !!(probe.getContext("webgl2") || probe.getContext("webgl")); } catch (e) { ok = false; }
  if (!ok) return;
  var go = function () {
    import(src).then(function (m) { m.mount(kind, host, { reduced: TM.reduced }); }).catch(function () {});
  };
  if (kind === "panel" || !("IntersectionObserver" in window)) return go();
  var o = new IntersectionObserver(function (es) {
    if (es[0].isIntersecting) { o.disconnect(); go(); }
  }, { rootMargin: "800px 0px" });
  o.observe(host);
})();

/* ── scroll choreography ──────────────────────────────────────────
   GSAP earns its place in two spots: the About statement above, and a slow
   drift inside each full-bleed plate here. Everything else holds still, so
   the moments that move have room to. */
(function () {
  "use strict";
  if (!window.gsap || !window.ScrollTrigger || TM.reduced) return;
  gsap.registerPlugin(ScrollTrigger);

  /* a slow drift inside each full-bleed plate; the image is oversized by the
     same amount it travels, so the crop never runs out of picture */
  document.querySelectorAll(".fig--bleed img").forEach(function (img) {
    gsap.fromTo(img, { scale: 1.08, yPercent: -3 }, {
      scale: 1, yPercent: 3, ease: "none",
      scrollTrigger: { trigger: img.closest(".fig"), start: "top bottom", end: "bottom top", scrub: true }
    });
  });

  window.addEventListener("load", function () { ScrollTrigger.refresh(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
})();
