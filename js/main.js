/* Toronto Millworks, progressive enhancement only.
   Nothing here is required for the page to render or be readable. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── mobile menu ─────────────────────────────────────────── */
  var nav    = document.querySelector(".nav");
  var burger = document.querySelector(".nav__burger");
  var menu   = document.querySelector(".nav__menu");

  if (nav && burger && menu) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      menu.classList.toggle("is-shown", open);
      burger.setAttribute("aria-expanded", String(open));
    };

    burger.addEventListener("click", function () {
      setOpen(burger.getAttribute("aria-expanded") !== "true");
    });

    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });

    document.addEventListener("click", function (e) {
      if (!nav.contains(e.target)) setOpen(false);
    });
  }

  /* ── scroll reveal ───────────────────────────────────────── */
  if (!reduced && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(
      ".about__label, .about__text, .craft__media, .craft__body > *"
    );

    Array.prototype.forEach.call(targets, function (el) { el.classList.add("rv"); });

    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;

        /* stagger against ready siblings so a group arrives as one gesture */
        var peers = el.parentElement
          ? Array.prototype.filter.call(el.parentElement.children, function (c) {
              return c.classList.contains("rv");
            })
          : [];
        var i = peers.indexOf(el);
        if (i > 0) el.style.transitionDelay = Math.min(i, 5) * 80 + "ms";

        el.classList.add("rv-on");
        rio.unobserve(el);
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0 });

    Array.prototype.forEach.call(targets, function (el) { rio.observe(el); });

    /* Safety net. IntersectionObserver reports changes in intersection, so an
       element that goes from below the viewport to above it without ever
       intersecting (a jump scroll, an End keypress, a restored scroll position,
       a deep link) never fires and would stay at opacity 0 for good. Sweep for
       anything already scrolled past and reveal it outright. */
    var pending = Array.prototype.slice.call(targets);
    var queued = false;

    function sweep() {
      queued = false;
      pending = pending.filter(function (el) {
        if (el.classList.contains("rv-on")) return false;
        if (el.getBoundingClientRect().bottom <= 0) {
          el.style.transition = "none";
          el.classList.add("rv-on");
          rio.unobserve(el);
          return false;
        }
        return true;
      });
      if (!pending.length) window.removeEventListener("scroll", onScroll);
    }

    function onScroll() {
      if (queued) return;
      queued = true;
      requestAnimationFrame(sweep);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("load", sweep);
    sweep();
  }

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

    var COUNT  = 102;
    var SMOOTH = 0.15;    /* damped follow, lower is silkier, slower to settle */

    /* ── which tier this device should pull ─────────────────
       Encoded weight is ~12/22/30 MB. Decoded frames are handed to the
       browser's own image cache (HTMLImageElement, not ImageBitmap) so it
       can evict under pressure instead of us pinning ~1 GB of pixels. */
    function pickTier () {
      var c = navigator.connection || {};
      if (c.saveData) return 1280;
      if (/(^|-)2g$/.test(c.effectiveType || "")) return 1280;

      var dpr  = Math.min(window.devicePixelRatio || 1, 2);
      var need = Math.max(window.innerWidth, 1) * dpr;
      var mem  = navigator.deviceMemory || 4;

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

/* ── site search (only runs on /search/) ───────────────────────── */
(function () {
  "use strict";
  var input = document.getElementById("q");
  var out = document.getElementById("results");
  if (!input || !out) return;

  var data = [];
  var ready = fetch("/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (j) { data = j; })
    .catch(function () { data = []; });

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function run() {
    var q = input.value.trim().toLowerCase();
    if (!q) { out.innerHTML = ""; return; }
    var terms = q.split(/\s+/);
    var hits = data.filter(function (d) {
      var hay = (d.t + " " + d.d + " " + d.k).toLowerCase();
      return terms.every(function (t) { return hay.indexOf(t) !== -1; });
    }).slice(0, 12);

    out.innerHTML = hits.length
      ? hits.map(function (h) {
          return '<li><a href="' + esc(h.u) + '">' + esc(h.t) + "</a><p>" + esc(h.d) + "</p></li>";
        }).join("")
      : "<li><p>No matches. Try kitchens, panelling, fit-outs or a place name.</p></li>";
  }

  input.addEventListener("input", run);

  var qs = new URLSearchParams(location.search).get("q");
  if (qs) { input.value = qs; }
  ready.then(function () { if (input.value) run(); });
})();
