#!/usr/bin/env python3
"""
Static site build for Toronto Millworks.

    python3 scripts/build_site.py          build everything
    python3 scripts/audit.py               then check it (the CI gate runs both)

Content lives in site_content.py, locations.py and guides.py. Page compositions
live in pages.py, blocks in components.py, everything a crawler reads in seo.py.
This file only renders, writes, and refuses to ship anything with an em dash.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import components as C            # noqa: E402
import pages as P                 # noqa: E402
import seo                        # noqa: E402
from site_content import BUILD_DATE, SITE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = "\u2014"                     # written as an escape so a dash cleanup cannot clobber the guard
UNIT = re.compile(r"(\d) (km|mm|minutes)\b")   # a figure stays with its unit


def _hash(*paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(open(p, "rb").read())
    return h.hexdigest()[:10]


def build_css():
    """css/src/*.css, in filename order, into the one stylesheet the site loads."""
    parts = sorted(glob.glob(os.path.join(ROOT, "css", "src", "*.css")))
    out = ["/* Toronto Millworks. Generated from css/src by scripts/build_site.py. Edit the sources. */"]
    for p in parts:
        out.append(f"\n/* ── {os.path.basename(p)} ── */\n" + open(p).read())
    css = "\n".join(out)
    open(os.path.join(ROOT, "css", "style.css"), "w").write(css)
    return len(parts), len(css)


def render(page, v):
    js = (f'<script src="/assets/js/gsap.min.js?v={v["gsap"]}" defer></script>\n'
          f'<script src="/assets/js/ScrollTrigger.min.js?v={v["gsap"]}" defer></script>\n'
          f'<script src="/js/main.js?v={v["js"]}" defer></script>')
    attrs = f' class="{page.get("body_class", "")}"'
    if page.get("three"):
        attrs += f' data-three="{page["three"]}" data-three-src="/js/scenes.js?v={v["scenes"]}"'
    body = "\n".join([
        f"<body{attrs}>",
        '<a class="skip" href="#main">Skip to content</a>',
        C.nav(page.get("active", "")),
        f'<main id="main" tabindex="-1">\n{page["body"]}\n</main>',
        C.footer(BUILD_DATE[:4]),
        "" if page.get("no_dock") else C.dock(),
        js,
        "</body>",
        "</html>",
    ])
    body = UNIT.sub("\\1\u00a0\\2", body)
    doc = seo.head(page, v["css"]) + "\n" + body + "\n"
    if EM in doc:
        bad = [l.strip()[:120] for l in doc.splitlines() if EM in l]
        raise SystemExit(f"em dash in {page['path']}: {bad[:3]}")
    return doc


def write(path, text):
    if path == "/":
        dest = os.path.join(ROOT, "index.html")
    elif path.endswith(".html"):
        dest = os.path.join(ROOT, path)
    else:
        dest = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(text)
    return dest


def brand_assets():
    """The mark as PNGs for the touch icon, the manifest and the Organization logo.
    Drawn rather than rasterised from the SVG so there is no SVG renderer to depend on."""
    from PIL import Image, ImageDraw
    out = os.path.join(ROOT, "assets", "brand")
    os.makedirs(out, exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, "assets", "img", "favicon.svg"), os.path.join(out, "favicon.svg"))

    def mark(size, pad=0.0, bg=None):
        S = 4 * size                                        # supersample, then reduce
        im = Image.new("RGBA", (S, S), bg or (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        inset = round(S * pad)
        box = (inset, inset, S - inset, S - inset)
        side = box[2] - box[0]
        d.rounded_rectangle(box, radius=round(side * 9.5 / 32), fill=(23, 20, 15, 255))
        k = side / 32
        w = max(1, round(1.7 * k))
        for y, x0 in ((22.6, 7.5), (18.9, 10.4), (15.2, 13.3), (11.5, 16.2)):
            yy = box[1] + y * k
            d.line((box[0] + x0 * k, yy, box[0] + 24.5 * k, yy), fill=(192, 138, 60, 255), width=w)
        return im.resize((size, size), Image.LANCZOS)

    mark(32).save(os.path.join(out, "favicon-32.png"))
    mark(180, pad=.1, bg=(255, 255, 255, 255)).convert("RGB").save(os.path.join(out, "apple-touch-icon.png"))
    mark(192, pad=.1, bg=(255, 255, 255, 255)).save(os.path.join(out, "icon-192.png"))
    mark(512, pad=.1, bg=(255, 255, 255, 255)).save(os.path.join(out, "icon-512.png"))
    mark(512).save(os.path.join(out, "logo-512.png"))


def og_spec(pages):
    """What each social card should show; scripts/og_cards.mjs renders them.
    Drawings and maps are embedded as SVG so the renderer needs no Python."""
    import drawings
    import maps
    spec = []
    for p in pages:
        og = p.get("og") or {}
        kind = og.get("kind", "drawing")
        svg = None
        if kind == "drawing":
            svg = drawings.drawing(og.get("drawing") or "draw", uid="-og")
        elif kind == "map":
            svg = maps.place_map(og["slug"]) if og.get("slug") else maps.hub_map()
        spec.append({"slug": seo.og_slug(p), "kind": kind,
                     "kicker": og.get("kicker", SITE["name"]), "title": UNIT.sub("\\1\u00a0\\2", og.get("title", p["h1"])),
                     "img": og.get("img"), "svg": svg, "path": p["path"]})
    json.dump(spec, open(os.path.join(ROOT, "scripts", "data", "og_spec.json"), "w"), indent=1)


def clean_stale(pages):
    """Remove generated directories for pages that no longer exist."""
    keep = {os.path.join(ROOT, p["path"].strip("/"), "index.html") for p in pages if p["path"] != "/"}
    for f in glob.glob(os.path.join(ROOT, "*", "**", "index.html"), recursive=True):
        rel = os.path.relpath(f, ROOT)
        if rel.split(os.sep)[0] in ("assets", "src", "scripts", "node_modules", ".git"):
            continue
        if f not in keep:
            os.remove(f)
            print("  removed stale", rel)


def main():
    n_css, css_len = build_css()
    brand_assets()
    v = {"css": _hash(os.path.join(ROOT, "css", "style.css")),
         "js": _hash(os.path.join(ROOT, "js", "main.js")),
         "gsap": _hash(os.path.join(ROOT, "assets", "js", "gsap.min.js"),
                       os.path.join(ROOT, "assets", "js", "ScrollTrigger.min.js")),
         "scenes": _hash(os.path.join(ROOT, "js", "scenes.js")) if os.path.exists(
             os.path.join(ROOT, "js", "scenes.js")) else "0"}

    pages = P.all_pages()
    seen = {}
    for p in pages:
        for k in ("title", "desc"):
            if not p.get("noindex"):
                if p[k] in seen:
                    raise SystemExit(f"duplicate {k}: {p[k]} ({seen[p[k]]} and {p['path']})")
                seen[p[k]] = p["path"]

    clean_stale(pages)
    for p in pages:
        write(p["path"], render(p, v))

    files = {
        "sitemap.xml": seo.sitemap(pages),
        "robots.txt": seo.robots_txt(),
        "llms.txt": seo.llms_txt(),
        "llms-full.txt": seo.llms_full_txt(),
        "search-index.json": seo.search_index(pages),
        "site.webmanifest": seo.manifest(),
        "vercel.json": seo.vercel_json(),
        ".vercelignore": seo.vercelignore(),
    }
    ht, nl, simple = seo.other_hosts()
    files.update({".htaccess": ht, "netlify.toml": nl, "_redirects": simple})
    for name, text in files.items():
        if EM in text:
            raise SystemExit(f"em dash in {name}")
        open(os.path.join(ROOT, name), "w").write(text)
    og_spec(pages)

    idx = sum(1 for p in pages if not p.get("noindex"))
    print(f"{len(pages)} pages ({idx} indexable), css from {n_css} parts ({css_len // 1024} KB)")
    print("sitemap.xml robots.txt llms.txt llms-full.txt search-index.json site.webmanifest")
    print("vercel.json .vercelignore netlify.toml .htaccess _redirects, scripts/data/og_spec.json")


if __name__ == "__main__":
    main()
