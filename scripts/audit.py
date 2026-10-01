#!/usr/bin/env python3
"""
Quality gate. Reads the built site and fails loudly on anything that breaks
the contract in SPEC.md. Run after every build; CI runs it on every push.

    python3 scripts/audit.py            exit 0 if clean, 1 with a report if not
    python3 scripts/audit.py --quiet    only the summary line and failures
"""
import glob
import json
import os
import re
import sys
import urllib.parse as U
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from site_content import ORIGIN, SERVICES          # noqa: E402
from locations import LOCATIONS, RADIUS_KM          # noqa: E402
from seo import PRIVATE                             # noqa: E402

EM = "\u2014"
# case matters: an input's placeholder attribute is fine, a PLACEHOLDER left in copy is not
BANNED = re.compile(r"(?i:lorem ipsum|example\.com)|\bTODO\b|\bFIXME\b|\bTBD\b|\bPLACEHOLDER\b")


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headings, self.links, self.imgs, self.sources, self.ids = [], [], [], [], []
        self.meta, self.scripts, self.title, self.lang = {}, [], "", None
        self.canonical, self.labels_for, self.fields, self.inline_handlers = None, set(), [], []
        self.labelledby, self.buttons, self._in, self._buf = [], [], None, ""
        self._stack = []
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in a:
            if k.startswith("on"):
                self.inline_handlers.append(f"<{tag} {k}>")
        if "id" in a:
            self.ids.append(a["id"])
        if a.get("aria-labelledby"):
            self.labelledby += a["aria-labelledby"].split()
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        if tag == "a":
            self.links.append(a)
        if tag == "img":
            self.imgs.append(a)
        if tag == "source":
            self.sources.append(a)
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        if tag in ("input", "select", "textarea"):
            self.fields.append(a)
        if tag == "script":
            self._in = ("script", a)
            self._buf = ""
        if tag == "title" and not self.in_body:
            self._in = ("title", a)
            self._buf = ""
        if tag == "body":
            self.in_body = True
        if tag == "button":
            self._stack.append(["button", a, ""])

    def handle_endtag(self, tag):
        if self._in and tag == self._in[0]:
            if tag == "script":
                self.scripts.append((self._in[1], self._buf))
            else:
                self.title = self._buf.strip()
            self._in = None
        if tag == "button" and self._stack:
            _, a, text = self._stack.pop()
            self.buttons.append((a, text.strip()))

    def handle_data(self, data):
        if self._in:
            self._buf += data
        for s in self._stack:
            s[2] += data


def page_files():
    out = sorted(glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True))
    out = [f for f in out if not os.path.relpath(f, ROOT).split(os.sep)[0] in
           ("assets", "scripts", "src", "node_modules", ".git")]
    return out + [os.path.join(ROOT, "404.html")]


def url_for(f):
    rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    if rel == "404.html":
        return "/404.html"
    return "/" + rel[:-len("index.html")]


def resolves(path):
    path = U.unquote(path.split("#")[0].split("?")[0])
    if not path or path == "/":
        return os.path.exists(os.path.join(ROOT, "index.html"))
    p = os.path.join(ROOT, path.lstrip("/"))
    if path.endswith("/"):
        return os.path.exists(os.path.join(p, "index.html"))
    return os.path.isfile(p) or os.path.exists(os.path.join(p, "index.html"))


def main():
    quiet = "--quiet" in sys.argv
    fails, warns = [], []
    F = lambda page, msg: fails.append(f"{page}: {msg}")
    titles, descs = {}, {}
    files = page_files()
    pages_ids = {}
    docs = {}

    for f in files:
        html_ = open(f, encoding="utf-8").read()
        d = Doc()
        d.feed(html_)
        u = url_for(f)
        docs[u] = (d, html_)
        pages_ids[u] = set(d.ids)

    sitemap = open(os.path.join(ROOT, "sitemap.xml")).read()
    in_map = set(re.findall(r"<loc>(.*?)</loc>", sitemap))

    for u, (d, html_) in docs.items():
        noindex = "noindex" in d.meta.get("robots", "")
        # ── copy hygiene
        if EM in html_:
            F(u, "contains an em dash")
        m = BANNED.search(re.sub(r"<script.*?</script>", "", html_, flags=re.S))
        if m:
            F(u, f"banned text: {m.group(0)!r}")
        if not d.lang:
            F(u, "missing <html lang>")
        # ── headings
        if d.headings.count(1) != 1:
            F(u, f"{d.headings.count(1)} h1 elements")
        prev = 0
        for lvl in d.headings:
            if prev and lvl > prev + 1:
                F(u, f"heading jumps from h{prev} to h{lvl}")
                break
            prev = lvl
        # ── head
        t, desc = d.title, d.meta.get("description", "")
        if not noindex:
            if not 30 <= len(t) <= 60:
                F(u, f"title length {len(t)}: {t!r}")
            if not 120 <= len(desc) <= 160:
                F(u, f"description length {len(desc)}: {desc!r}")
            if t in titles:
                F(u, f"title duplicates {titles[t]}")
            if desc in descs:
                F(u, f"description duplicates {descs[desc]}")
            titles[t], descs[desc] = u, u
            if ORIGIN + u not in in_map:
                F(u, "indexable page missing from sitemap")
        else:
            if (ORIGIN + u) in in_map:
                F(u, "noindex page listed in the sitemap")
        # the 404 answers at whatever address was asked for, so it may not claim one;
        # every other page, indexed or not, names itself
        anywhere = u == "/404.html"
        if anywhere:
            if d.canonical or d.meta.get("og:url"):
                F(u, "served at any address, so it must not declare a canonical or og:url")
        elif d.canonical != ORIGIN + u:
            F(u, f"canonical {d.canonical!r} should be {ORIGIN + u!r}")
        for k in ("og:title", "og:description", "og:image", "og:type",
                  "twitter:card", "twitter:image", "twitter:title") + (() if anywhere else ("og:url",)):
            if not d.meta.get(k):
                F(u, f"missing {k}")
        og = d.meta.get("og:image", "")
        if og.startswith(ORIGIN) and not resolves(og[len(ORIGIN):]):
            F(u, f"og:image file missing: {og}")
        # ── structured data
        boot = 0
        for attrs, body in d.scripts:
            if attrs.get("type") == "application/ld+json":
                try:
                    g = json.loads(body)
                except Exception as e:
                    F(u, f"JSON-LD does not parse: {e}")
                    continue
                types = []
                for n in g.get("@graph", []):
                    tt = n.get("@type")
                    types += tt if isinstance(tt, list) else [tt]
                if "Organization" not in types:
                    F(u, "JSON-LD lacks the Organization")
                if not noindex and u != "/" and "BreadcrumbList" not in types:
                    F(u, "JSON-LD lacks a BreadcrumbList")
                if "<div" in body or "</p>" in body:
                    F(u, "markup inside JSON-LD")
            elif attrs.get("src"):
                if not resolves(attrs["src"]):
                    F(u, f"script missing: {attrs['src']}")
            else:
                boot += 1
                if "classList.add('js')" not in body:
                    F(u, "unexpected inline script")
        if boot != 1:
            F(u, f"{boot} inline boot scripts")
        if d.inline_handlers:
            F(u, f"inline event handlers: {d.inline_handlers[:3]}")
        # ── links
        for a in d.links:
            href = a.get("href")
            if href is None:
                F(u, "anchor without href")
                continue
            if href in ("#", "") or href.lower().startswith("javascript:"):
                F(u, f"dead href {href!r}")
                continue
            if href.startswith("#"):
                if href[1:] not in pages_ids[u]:
                    F(u, f"fragment {href} has no target")
                continue
            if href.startswith(("mailto:", "tel:")):
                continue
            if href.startswith("http"):
                if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                    F(u, f"external link without noopener: {href}")
                continue
            if not href.startswith("/"):
                F(u, f"relative link {href!r}")
                continue
            if not resolves(href):
                F(u, f"broken link {href}")
            frag = href.split("#")[1] if "#" in href else None
            target = href.split("#")[0].split("?")[0]
            if frag and target in pages_ids and frag not in pages_ids[target]:
                F(u, f"fragment {href} missing on target page")
        # ── images
        for img in d.imgs:
            if img.get("alt") is None:
                F(u, f"img without alt: {img.get('src')}")
            if not (img.get("width") and img.get("height")):
                F(u, f"img without dimensions: {img.get('src')}")
            for src in [img.get("src", "")] + [s.strip().split(" ")[0] for s in img.get("srcset", "").split(",") if s.strip()]:
                if src and not src.startswith("data:") and not resolves(src):
                    F(u, f"image missing: {src}")
        for srcel in d.sources:
            for s in [x.strip().split(" ")[0] for x in srcel.get("srcset", "").split(",") if x.strip()]:
                if not resolves(s):
                    F(u, f"source image missing: {s}")
        # ── forms and buttons
        for fld in d.fields:
            if fld.get("type") in ("hidden", "submit", "radio"):
                continue
            if fld.get("id") not in d.labels_for and not fld.get("aria-label"):
                F(u, f"field without a label: {fld.get('name')}")
        for a, text in d.buttons:
            if not text and not a.get("aria-label"):
                F(u, "button without accessible text")
        # ── ids and references
        dup = {i for i in d.ids if d.ids.count(i) > 1}
        if dup:
            F(u, f"duplicate ids: {sorted(dup)[:5]}")
        for ref in d.labelledby:
            if ref not in pages_ids[u]:
                F(u, f"aria-labelledby points at missing id {ref}")

    # ── site files
    for loc in in_map:
        if not resolves(loc[len(ORIGIN):]):
            fails.append(f"sitemap: {loc} has no page")
    for img in re.findall(r"<image:loc>(.*?)</image:loc>", sitemap):
        if not resolves(img[len(ORIGIN):]):
            fails.append(f"sitemap: image {img} missing")
    robots = open(os.path.join(ROOT, "robots.txt")).read()
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots:
        fails.append("robots.txt: no Sitemap line")
    if re.search(r"^Disallow: /\s*$", robots, re.M):
        fails.append("robots.txt: disallows everything")
    llms = open(os.path.join(ROOT, "llms.txt")).read()
    for s in SERVICES:
        if f"/services/{s['slug']}/" not in llms:
            fails.append(f"llms.txt: missing service {s['slug']}")
    full = open(os.path.join(ROOT, "llms-full.txt")).read()
    if len(full) < 20000:
        fails.append("llms-full.txt looks truncated")
    vj = json.load(open(os.path.join(ROOT, "vercel.json")))
    hdrs = {h["key"] for block in vj["headers"] if block["source"] == "/(.*)" for h in block["headers"]}
    for need in ("Content-Security-Policy", "Strict-Transport-Security", "X-Content-Type-Options",
                 "Referrer-Policy", "Permissions-Policy", "X-Frame-Options"):
        if need not in hdrs:
            fails.append(f"vercel.json: missing {need}")
    for p in LOCATIONS:
        if p["km"] > RADIUS_KM:
            fails.append(f"location {p['slug']} is {p['km']} km away")
        if f"{ORIGIN}/service-areas/{p['slug']}/" not in in_map:
            fails.append(f"location {p['slug']} missing from the sitemap")
    # sources, not just output: a raw em dash in a script or stylesheet is the
    # first step to one in the copy
    for src in glob.glob(os.path.join(ROOT, "scripts", "*.py")) + glob.glob(os.path.join(ROOT, "scripts", "*.mjs")) \
            + glob.glob(os.path.join(ROOT, "js", "*.js")) + glob.glob(os.path.join(ROOT, "css", "src", "*.css")) \
            + glob.glob(os.path.join(ROOT, "src", "partials", "*.html")):
        if EM in open(src, encoding="utf-8").read():
            fails.append(f"raw em dash in source {os.path.relpath(src, ROOT)}")
    for leak in glob.glob(os.path.join(ROOT, "__*.html")):
        fails.append(f"scratch file in the site root: {os.path.basename(leak)}")
    # whatever sits at the top level either is the site or is kept off it
    shipped = {"index.html", "404.html", "sitemap.xml", "robots.txt", "llms.txt", "llms-full.txt",
               "search-index.json", "site.webmanifest", "vercel.json", ".vercelignore",
               "assets", "css", "js", ".git", ".gitignore", ".DS_Store"}
    for name in sorted(os.listdir(ROOT)):
        if name in shipped or os.path.isfile(os.path.join(ROOT, name, "index.html")) \
                or f"/{name}" in PRIVATE or f"/{name}/" in PRIVATE:
            continue
        fails.append(f"/{name} would be deployed with the site: list it in seo.PRIVATE or move it")
    ignored = open(os.path.join(ROOT, ".vercelignore")).read().split()
    for p in PRIVATE:
        if p not in ignored:
            fails.append(f".vercelignore does not exclude {p}")

    n = len(docs)
    print(f"audit: {n} pages, {len(in_map)} in sitemap, {len(fails)} failures")
    if fails:
        for x in fails[:200]:
            print("  FAIL", x)
        if len(fails) > 200:
            print(f"  ... {len(fails) - 200} more")
        sys.exit(1)


if __name__ == "__main__":
    main()
