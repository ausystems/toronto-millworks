# Toronto Millworks

**Live:** https://toronto-millworks.vercel.app
**Repo:** https://github.com/ausystems/toronto-millworks

Pushing to `main` auto-deploys to Vercel. No build step runs on Vercel: the
generated HTML is committed, so what is in the repo is exactly what ships.
Run `python3 scripts/build_site.py` locally before committing content changes.

Static site, 21 pages. Generated from `src/partials/` and
`scripts/site_content.py`, so every head, nav, footer and JSON-LD graph stays
consistent.

```bash
python3 scripts/build_site.py      # rebuild all pages + sitemap/robots/llms
python3 -m http.server 4173        # serve
```

Edit copy and metadata in `scripts/site_content.py`, not in the generated HTML.
The homepage body lives in `src/partials/home-main.html`.

SEO status, the placeholders that still need real values, and the schema that is
deliberately not live are all in [SEO.md](SEO.md).

## Imagery

`scripts/build_library.py` builds the art-directed library in `assets/img/lib`.
Each plate is declared as a focal point plus a coverage scale, not a fixed box,
so the wide and portrait crops are both composed around the same subject. A
phone gets a real portrait composition rather than a wide plate squeezed into a
tall hole, and the CSS box aspect matches the served crop at every breakpoint,
so `object-fit` never has anything to throw away. That is also why CLS is 0.

14 plates: eight from the residential master, six from the fit-out sequence.

## Motion

GSAP with ScrollTrigger, self hosted in `assets/js`. It runs one shared scroll
listener, refreshes on font load and resize, and eases reveals and a slow drift
inside each frame. Figures being parallaxed get `.fig--px`, which adds the
headroom the drift needs, so the no-JS layout stays exact. Everything falls back
to fully visible if GSAP is absent or `prefers-reduced-motion` is set.

Three.js is deliberately not used. Nothing on these pages is a 3D problem, and
the homepage sequence already carries the heavy visual moment on a 2D canvas.

## Pages

```
/                                        /about/
/services/                               /contact/
/services/custom-kitchens/               /faq/
/services/cabinetry-and-built-ins/       /service-areas/  + 6 GTA pages
/services/architectural-millwork/        /guides/how-custom-millwork-is-made/
/services/commercial-fit-outs/           /search/     (noindex)
/services/interior-renovation/           /404.html    (noindex)
/projects/
```

## Layout reference

The nav, hero and the About block directly below it are matched to the supplied
reference composition. Measured at a 1440px viewport:

| | reference | built |
|---|---|---|
| hero aspect | 1.775 | 1.778 |
| hero inner padding (left) | ~54px | 54px |
| hero content → bottom edge | ~82px | 80px |
| nav bar height | ~67px | 66px |
| nav CTA height | ~51px | 51px |
| h1 size / line-height | ~77px / 1.06 | 76.6px / 1.055 |
| About column split | ~32 / 68 | 32.7 / 67.3 |

Type is Instrument Sans. Accent is brass `#C08A3C` on a warm near-black `#17140F`.

## Hero plate

Source supplied: `assets/img/_source-millwork.webp`, **1024×1024**.

A true 8K capture cannot be recovered from a 1024px original; what is shipped is
a genuine 7680px reconstruction, not a naive stretch. Pipeline
(`scripts/upscale.py`):

1. decode → float32, sRGB → **linear light** (correct resampling, no gamma darkening)
2. progressive Lanczos-3 1024 → 2048 → 4096
3. **iterative back-projection** ×8 against the true 1024 source, the real
   super-resolution step. Residual RMS converged 0.0113 → 0.0014, i.e. the 8K
   result downsamples back to almost exactly the original plate.
4. edge-aware unsharp (gradient-masked, so flat ceiling planes stay clean)
5. linear → sRGB + 0.7/255 dither to kill webp banding on the smooth ceiling
6. final Lanczos to 7680 + detail pass, encoded webp `method=6`

Two ladders, all webp, selected by `<picture>` / `srcset`:

| set | crop | widths | top rung |
|---|---|---|---|
| `millwork-*` | full square 1:1 | 1280 → **7680** | 4.76 MB |
| `millwork-wide-*` | 16:9 hero | 1280 → **7680** | 2.40 MB |

The 8K rungs exist so nothing is lost on an 8K/high-DPR display. A typical
1440px×2DPR desktop pulls the 3840w file (~760 KB), and a phone pulls ~300 KB -
so the page stays fast without capping the ceiling.

To re-run after replacing the source:

```bash
python3 scripts/upscale.py assets/img/_source-millwork.webp assets/img
```

## The reel

The section below About is a scroll-scrubbed frame sequence: a commercial
fit-out going from bare brick shell to finished bar. 102 frames, built by
`scripts/build_reel.py` from the supplied 1280x720 PNG export.

**Why this is not 8K.** A scrubbed sequence has to keep every frame resident so
the scrub does not stall. At 7680px that is roughly half a gigabyte of webp for
one section. The ladder is capped at 2560 and the runtime picks a tier instead:

| tier | picked when | weight |
|---|---|---|
| 2560px | viewport x DPR >= 2400 **and** `deviceMemory` >= 8 | 30.3 MB |
| 1920px | viewport x DPR >= 1500 | 22.0 MB |
| 1280px | everything else, plus Save-Data / 2G | 11.6 MB |

Each frame is still reconstructed to 2560 with the same linear-light +
back-projection method as the hero plate, then the smaller tiers are
supersampled down from that master so all three share one look.

**What makes the scrub smooth**

- Frames are cross-faded, not switched. At scroll position *n.4* the canvas
  draws frame *n* at full alpha and frame *n+1* at 0.4, so motion is
  continuous rather than 102 discrete steps. Verified: the midpoint between
  two frames renders as a value between them.
- Scroll progress drives a damped follow (`SMOOTH = 0.15` in a rAF loop), so
  jumpy wheel or trackpad input still renders as fluid motion.
- Frames load in a coarse pass first (every 6th), so the full span is
  scrubbable early; gaps fill in behind. Until a frame arrives the canvas draws
  the nearest one that has, so it never blanks.
- Loading starts 1.5 viewports before the section arrives, and the rAF loop
  only runs while it is near the viewport.
- Frames are held as `HTMLImageElement`, not `ImageBitmap`, so the browser can
  evict decoded pixels under pressure instead of us pinning ~1 GB.

The 520vh track gives ~4vh of scroll per frame. Change `--reel-scroll` in the
tokens block to make the sequence longer or shorter.

**No frame.** The sequence is full-bleed with no card, border or rail. It is
masked with a vertical gradient so it feathers into the page top and bottom
rather than ending on a hard rectangle edge, that is what makes it read as
part of the page instead of a widget dropped into it.

A 16:9 plate cover-cropped to full height throws away most of its width on a
portrait screen, so the band is capped per breakpoint: it sits at ~66-80% of
viewport height on phones (60% crop, framed on the bar itself), ~72% on tablet
(41% crop), and uncropped from laptop up.

**Reduced motion.** `prefers-reduced-motion: reduce` collapses the track, drops
the pin, and shows a single still, and skips the sequence download entirely
(1 request instead of 103).

To rebuild after replacing the frames:

```bash
python3 scripts/build_reel.py <frames_dir> assets/reel
```

Update `COUNT` in `js/main.js` if the frame count changes.

## Craft section

Sits directly under the reel: a 4:5 plate cropped from the 8K master that runs
off the left edge of the viewport, with the copy set against it. Stacks to
full-bleed image over text below 860px. Its own ladder is `craft-*.webp`
(800 → 3200), generated by the same `scripts/upscale.py` run.

## Footer

Deep brass ground with white type, built on the reference layout: meta rule →
statement + CTA + stat row / site index + contact → meta rule → oversized
wordmark.

**Contrast.** The gradient (`#8A5E25` → `#714E1E`) is deliberately kept dark
enough that plain white clears 5.66:1 and the smallest 10px tracked labels
clear 4.54:1, composited over the real painted background. Every text colour in
the footer passes WCAG AA, nothing is dimmed to the point of fading out.

**The wordmark cannot overflow or clip.** It is SVG text with `textLength` set
to the viewBox width, and the viewBox widths are the *measured* natural widths
of the glyphs in Instrument Sans at 100px (1120 / 498 / 602 units). Because the
declared length matches the natural length, `textLength` holds the fit without
stretching a single glyph, and it still holds if the webfont fails to load.
Verified fitting the footer exactly at 320 → 2560px.

Below 860px the mark stacks to two lines, so the letters stay large on a phone
instead of shrinking to a hairline: `MILLWORKS` defines the viewBox width and
`TORONTO` sits at its natural width beneath it, both at the same glyph size.

## Replace before launch

This copy is placeholder and states things about the business that were not
supplied, check every line:

- **Email**, `hello@torontomillworks.ca` is a guess. It is used by Contact
  and by both Get a Quote buttons.
- **Nav links**, Services and Projects both point at the reel, and their
  carets imply dropdowns that do not exist yet.
- **Craft section copy**, the process described (templating from your walls,
  dry-fitting before delivery) is plausible for a millwork shop but was not
  supplied; confirm it is how you actually work. "Greater Toronto Area" is an
  assumed service area.
- **Footer contact details**, the shop location is only "Toronto, Ontario"
  because no street address was supplied, and there is deliberately no phone
  number rather than an invented one. The coordinates in the top rule are
  Toronto's actual coordinates.
- **Footer stat row**, Work / Region / Built / Drawings are drawn from copy
  already on the page, not from supplied figures.
