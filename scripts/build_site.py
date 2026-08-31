#!/usr/bin/env python3
"""
Static site generator for Toronto Millworks.

Owns every <head>, the nav, the breadcrumbs, the footer and the JSON-LD graph so
all pages stay consistent. Also emits sitemap.xml, robots.txt, llms.txt,
llms-full.txt, the 404 page and the host redirect configs.

    python3 scripts/build_site.py
"""
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_content import SITE, SERVICES, AREA_PAGES, AREAS, FAQ, BUILD_DATE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART = os.path.join(ROOT, "src", "partials")
O = SITE["origin"].rstrip("/")

NAV_HTML = open(os.path.join(PART, "nav.html")).read()
FOOT_HTML = open(os.path.join(PART, "footer.html")).read()
HOME_MAIN = open(os.path.join(PART, "home-main.html")).read()

# indexed imagery, keyword-named, fed to the image sitemap
HERO_IMG = "assets/img/toronto-custom-millwork-coffered-ceiling-1920.webp"
CRAFT_IMG = "assets/img/toronto-custom-cabinetry-wall-panelling-1600.webp"
OG_IMG = HERO_IMG

E = lambda s: html.escape(str(s), quote=True)


def url(path):
    """Absolute canonical URL for a site path."""
    if path in ("", "/"):
        return O + "/"
    return O + "/" + path.strip("/") + "/"


def rel_prefix(path):
    """How many levels up the assets live from this page."""
    if path in ("", "/"):
        return ""
    p = path.strip("/")
    parts = p.split("/")
    # a root-level file such as 404.html sits beside the asset folders
    if parts[-1].endswith(".html"):
        parts = parts[:-1]
    return "../" * len(parts)


# ══════════════════════════════════════════════════════════════════════════════
#  SCHEMA
# ══════════════════════════════════════════════════════════════════════════════
def org_node():
    node = {
        "@type": ["Organization", "HomeAndConstructionBusiness", "LocalBusiness"],
        "@id": f"{O}/#organization",
        "name": SITE["name"],
        "url": O + "/",
        "description": SITE["tagline"],
        "email": SITE["email"],
        "image": f"{O}/{HERO_IMG}",
        "logo": {"@type": "ImageObject", "@id": f"{O}/#logo",
                 "url": f"{O}/assets/img/favicon.svg", "caption": SITE["name"]},
        "address": {
            "@type": "PostalAddress",
            "addressLocality": SITE["locality"],
            "addressRegion": SITE["region"],
            "addressCountry": SITE["country"],
        },
        "geo": {"@type": "GeoCoordinates",
                "latitude": SITE["lat"], "longitude": SITE["lon"]},
        "areaServed": [{"@type": "City", "name": a} for a in AREAS],
        "knowsAbout": [
            "Custom millwork", "Custom cabinetry", "Architectural millwork",
            "Kitchen cabinetry", "Wall panelling", "Commercial fit-outs",
            "Interior renovation",
        ],
        "contactPoint": [{
            "@type": "ContactPoint",
            "contactType": "sales",
            "email": SITE["email"],
            "areaServed": SITE["country"],
            "availableLanguage": ["English"],
            "url": url("contact"),
        }],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {
                "@type": "Service", "@id": url("services/" + s["slug"]) + "#service",
                "name": s["h1"]}}
            for s in SERVICES
        ],
    }
    if SITE["street"]:
        node["address"]["streetAddress"] = SITE["street"]
    if SITE["postal"]:
        node["address"]["postalCode"] = SITE["postal"]
    if SITE["phone"]:
        node["telephone"] = SITE["phone"]
    if SITE["founded"]:
        node["foundingDate"] = SITE["founded"]
    if SITE["same_as"]:
        node["sameAs"] = SITE["same_as"]
    return node


def website_node():
    return {
        "@type": "WebSite",
        "@id": f"{O}/#website",
        "url": O + "/",
        "name": SITE["name"],
        "description": SITE["tagline"],
        "inLanguage": SITE["lang"],
        "publisher": {"@id": f"{O}/#organization"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint",
                       "urlTemplate": f"{O}/search/?q={{search_term_string}}"},
            "query-input": "required name=search_term_string",
        },
    }


def breadcrumb_node(page):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": O + "/"}]
    for i, (name, path) in enumerate(page.get("crumbs", []), start=2):
        items.append({"@type": "ListItem", "position": i, "name": name,
                      "item": url(path)})
    return {"@type": "BreadcrumbList", "@id": url(page["path"]) + "#breadcrumb",
            "itemListElement": items}


def webpage_node(page):
    u = url(page["path"])
    node = {
        "@type": page.get("page_type", "WebPage"),
        "@id": u + "#webpage",
        "url": u,
        "name": page["title"],
        "description": page["desc"],
        "isPartOf": {"@id": f"{O}/#website"},
        "about": {"@id": f"{O}/#organization"},
        "breadcrumb": {"@id": u + "#breadcrumb"},
        "inLanguage": SITE["lang"],
        "datePublished": BUILD_DATE,
        "dateModified": BUILD_DATE,
        "primaryImageOfPage": {"@type": "ImageObject", "url": f"{O}/{page.get('image', OG_IMG)}"},
    }
    if page.get("faq"):
        node["mainEntity"] = {"@id": u + "#faq"}
    return node


def faq_node(page):
    return {
        "@type": "FAQPage",
        "@id": url(page["path"]) + "#faq",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in page["faq"]
        ],
    }


def service_node(page):
    s = page["service"]
    return {
        "@type": "Service",
        "@id": url(page["path"]) + "#service",
        "name": s["h1"],
        "description": s["desc"],
        "serviceType": s["nav"],
        "provider": {"@id": f"{O}/#organization"},
        "areaServed": [{"@type": "City", "name": a} for a in AREAS],
        "url": url(page["path"]),
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": s["h1"],
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": item}}
                for sec in s["sections"] for item in sec[1]
            ][:12],
        },
    }


def article_node(page):
    u = url(page["path"])
    return {
        "@type": "Article",
        "@id": u + "#article",
        "headline": page["h1"],
        "description": page["desc"],
        "articleSection": "Guides",
        "mainEntityOfPage": {"@id": u + "#webpage"},
        "image": [f"{O}/{page.get('image', OG_IMG)}"],
        "datePublished": BUILD_DATE,
        "dateModified": BUILD_DATE,
        "inLanguage": SITE["lang"],
        "author": {"@id": f"{O}/#organization"},
        "publisher": {"@id": f"{O}/#organization"},
    }


def graph_for(page):
    g = [org_node(), website_node(), webpage_node(page), breadcrumb_node(page)]
    if page.get("faq"):
        g.append(faq_node(page))
    if page.get("service"):
        g.append(service_node(page))
    if page.get("is_article"):
        g.append(article_node(page))
    return {"@context": "https://schema.org", "@graph": g}


# ══════════════════════════════════════════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════════════════════════════════════════
def head(page):
    u = url(page["path"])
    p = rel_prefix(page["path"])
    img = f"{O}/{page.get('image', OG_IMG)}"
    robots = page.get("robots", "index, follow, max-image-preview:large, "
                                "max-snippet:-1, max-video-preview:-1")
    ld = json.dumps(graph_for(page), ensure_ascii=False, separators=(",", ":"))

    parts = [
        '<!doctype html>',
        f'<html lang="{SITE["lang"]}">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{E(page["title"])}</title>',
        f'<meta name="description" content="{E(page["desc"])}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{u}">',
    ]
    if not page.get("noindex"):
        parts += [
            f'<link rel="alternate" hreflang="en-ca" href="{u}">',
            f'<link rel="alternate" hreflang="x-default" href="{u}">',
        ]
    if page.get("keywords"):
        parts.append(f'<meta name="keywords" content="{E(page["keywords"])}">')

    parts += [
        '',
        f'<meta property="og:type" content="{page.get("og_type", "website")}">',
        f'<meta property="og:site_name" content="{E(SITE["name"])}">',
        f'<meta property="og:locale" content="en_CA">',
        f'<meta property="og:url" content="{u}">',
        f'<meta property="og:title" content="{E(page["title"])}">',
        f'<meta property="og:description" content="{E(page["desc"])}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1920">',
        '<meta property="og:image:height" content="1080">',
        f'<meta property="og:image:alt" content="{E(page.get("image_alt", SITE["tagline"]))}">',
        '',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{E(page["title"])}">',
        f'<meta name="twitter:description" content="{E(page["desc"])}">',
        f'<meta name="twitter:image" content="{img}">',
        f'<meta name="twitter:image:alt" content="{E(page.get("image_alt", SITE["tagline"]))}">',
        '',
        '<meta name="theme-color" content="#ffffff">',
        f'<meta name="geo.region" content="CA-{SITE["region"]}">',
        f'<meta name="geo.placename" content="{E(SITE["locality"])}">',
        '',
        f'<link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">',
    ]
    if page.get("preload_hero"):
        parts.append(
            f'<link rel="preload" as="image" href="{p}{HERO_IMG}" fetchpriority="high" media="(min-width: 760px)">')
    parts += [
        f'<link rel="stylesheet" href="{p}css/style.css">',
        '',
        f'<script type="application/ld+json">{ld}</script>',
        '</head>',
    ]
    return "\n".join(parts)


def nav_for(page):
    p = rel_prefix(page["path"])
    n = NAV_HTML
    n = n.replace('href="/"', f'href="{p or "/"}"')
    n = n.replace('href="#"', f'href="{p or "/"}"')
    for token, dest in (("#about", "about/"), ("#services", "services/"),
                        ("#projects", "projects/"), ("#contact", "contact/")):
        n = n.replace(f'href="{token}"', f'href="{p}{dest}"')

    # mark the section the visitor is in, for both crawlers and screen readers
    own = page["path"].strip("/")
    section = ""
    if own in ("", "404.html"):
        section = p or "/"
    elif own.startswith("services"):
        section = f"{p}services/"
    elif own.startswith("projects"):
        section = f"{p}projects/"
    elif own.startswith("about"):
        section = f"{p}about/"
    elif own.startswith("contact"):
        section = f"{p}contact/"
    if section:
        n = n.replace(f'<a href="{section}">',
                      f'<a href="{section}" class="is-active" aria-current="page">', 1)
    return n


def footer_for(page):
    p = rel_prefix(page["path"])
    f = FOOT_HTML
    f = f.replace('href="#main"', f'href="{p or "/"}"')
    for token, dest in (("#about", "about/"), ("#services", "services/"),
                        ("#projects", "projects/"), ("#areas", "service-areas/"),
                        ("#faq", "faq/"), ("#contact", "contact/")):
        f = f.replace(f'href="{token}"', f'href="{p}{dest}"')
    return f


def crumbs_html(page):
    if not page.get("crumbs"):
        return ""
    p = rel_prefix(page["path"])
    li = [f'<li><a href="{p or "/"}">Home</a></li>']
    trail = page["crumbs"]
    for i, (name, path) in enumerate(trail):
        last = i == len(trail) - 1
        if last:
            li.append(f'<li><span aria-current="page">{E(name)}</span></li>')
        else:
            li.append(f'<li><a href="{p}{path.strip("/")}/">{E(name)}</a></li>')
    return ('<nav class="crumbs" aria-label="Breadcrumb">\n  <ol>\n    '
            + "\n    ".join(li) + '\n  </ol>\n</nav>')


def faq_html(items):
    """Native <details> so the answers are in the DOM, toggle without JS and
    carry summary's button semantics for free. JS only adds the easing."""
    rows = []
    for q, a in items:
        rows.append(
            '    <details class="faq__row">\n'
            '      <summary class="faq__q">\n'
            f'        <h3 class="faq__q-t">{E(q)}</h3>\n'
            '        <span class="faq__ico" aria-hidden="true"></span>\n'
            '      </summary>\n'
            '      <div class="faq__panel">\n'
            f'        <p class="faq__a">{E(a)}</p>\n'
            '      </div>\n'
            '    </details>')
    return ('<section class="faq" aria-labelledby="faq-h">\n'
            '  <div class="shell">\n'
            '    <span class="pill pill--line"><i class="dot" aria-hidden="true"></i>Questions</span>\n'
            '    <h2 class="sec-title" id="faq-h">Frequently asked</h2>\n'
            '  </div>\n'
            '  <div class="shell faq__list">\n' + "\n".join(rows) + '\n  </div>\n'
            '</section>')


def cta_html(page):
    p = rel_prefix(page["path"])
    return (
        '<section class="band">\n'
        '  <div class="shell band__inner">\n'
        '    <h2 class="band__title">Tell us about the room.</h2>\n'
        '    <p class="band__text">Send drawings, a photo or just the dimensions. '
        'We come back with a measured quote.</p>\n'
        f'    <a class="btn btn--brass btn--lg" href="{p}contact/">'
        '<span>Start a project</span>'
        '<i class="btn__arrow" aria-hidden="true">'
        '<svg viewBox="0 0 14 14" fill="none"><path d="M4 10L10 4M10 4H4.9M10 4v5.1" '
        'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        'stroke-linejoin="round"/></svg></i></a>\n'
        '  </div>\n'
        '</section>')


def page_head_block(page):
    label = page.get("label", "")
    chip = (f'<span class="pill pill--line"><i class="dot" aria-hidden="true"></i>{E(label)}</span>'
            if label else "")
    return (
        '<header class="phead">\n'
        f'  <div class="shell">\n'
        f'    {crumbs_html(page)}\n'
        f'    {chip}\n'
        f'    <h1 class="phead__title">{E(page["h1"])}</h1>\n'
        f'    <p class="phead__lede">{E(page["lede"])}</p>\n'
        '  </div>\n'
        '</header>')


def render(page):
    body = page.get("body", "")
    out = [
        head(page),
        '<body>',
        '<a class="skip" href="#main">Skip to content</a>',
        nav_for(page),
        '<main id="main">',
        body,
        '</main>',
        footer_for(page),
        f'<script src="{rel_prefix(page["path"])}js/main.js" defer></script>',
        '</body>',
        '</html>',
    ]
    doc = "\n".join(out) + "\n"
    # written as an escape so a global dash cleanup cannot clobber the guard
    EM = "\u2014"
    if EM in doc:
        bad = [l for l in doc.splitlines() if EM in l]
        raise SystemExit(f"em dash found in {page['path']}: {bad[:3]}")
    return doc


def write(path, text):
    if path in ("", "/"):
        dest = os.path.join(ROOT, "index.html")
    elif path.endswith(".html"):
        dest = os.path.join(ROOT, path)
    else:
        dest = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(text)
    return dest


# ══════════════════════════════════════════════════════════════════════════════
#  BODY BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def prose(sections):
    out = []
    for title, items in sections:
        if isinstance(items, list) and len(items) and isinstance(items[0], str) and \
           any(len(i) > 160 for i in items):
            inner = "".join(f'<p class="prose__p">{E(i)}</p>' for i in items)
        else:
            inner = ('<ul class="ticks">'
                     + "".join(f'<li>{E(i)}</li>' for i in items) + '</ul>')
        out.append(
            '  <div class="prose__block">\n'
            f'    <h2 class="prose__h">{E(title)}</h2>\n'
            f'    <div class="prose__body">{inner}</div>\n'
            '  </div>')
    return '<section class="prose">\n  <div class="shell prose__grid">\n' \
           + "\n".join(out) + '\n  </div>\n</section>'


def media_block(page, src_base, alt, ratio="16 / 9"):
    p = rel_prefix(page["path"])
    widths = [800, 1200, 1600, 2400, 3200] if "cabinetry" in src_base else [1280, 1920, 2560, 3840]
    srcset = ", ".join(f'{p}assets/img/{src_base}-{w}.webp {w}w' for w in widths)
    return (f'<figure class="pmedia" style="--r:{ratio}">\n'
            f'  <img src="{p}assets/img/{src_base}-{widths[1]}.webp" srcset="{srcset}" '
            f'sizes="(max-width: 860px) 100vw, 90vw" loading="lazy" decoding="async" '
            f'alt="{E(alt)}">\n</figure>')


def links_grid(page, items, heading):
    p = rel_prefix(page["path"])
    rows = []
    for i, (name, path, blurb) in enumerate(items, start=1):
        rows.append(
            f'    <li class="lrow"><a href="{p}{path.strip("/")}/">\n'
            f'      <span class="lrow__n">{i:02d}</span>\n'
            f'      <span class="lrow__t">{E(name)}</span>\n'
            f'      <span class="lrow__d">{E(blurb)}</span>\n'
            f'      <i class="lrow__a" aria-hidden="true"><svg viewBox="0 0 14 14" fill="none">'
            f'<path d="M4 10L10 4M10 4H4.9M10 4v5.1" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg></i>\n'
            f'    </a></li>')
    return ('<section class="lgrid">\n  <div class="shell">\n'
            f'    <h2 class="sec-title">{E(heading)}</h2>\n'
            '    <ol class="lrows">\n' + "\n".join(rows) + '\n    </ol>\n'
            '  </div>\n</section>')


# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════
def build_pages():
    pages = []

    # ── home ────────────────────────────────────────────────────────────────
    pages.append({
        "path": "/",
        "title": "Custom Millwork Toronto | Cabinetry, Kitchens & Joinery",
        "desc": ("Custom millwork and cabinetry in Toronto. Custom kitchens, "
                 "built-ins, panelling, bars and commercial fit-outs, measured "
                 "on site and milled in our own shop."),
        "keywords": "custom millwork Toronto, custom cabinetry Toronto, custom kitchens Toronto, millwork company Toronto",
        "image": HERO_IMG,
        "image_alt": "Interior with a coffered ceiling, gilded crown moulding and raised wall panelling in Toronto",
        "preload_hero": True,
        "body": HOME_MAIN.replace('<main id="main">', "").replace("</main>", "")
                + "\n" + faq_html(FAQ[:6]) + "\n" + cta_html({"path": "/"}),
        "faq": FAQ[:6],
        "changefreq": "weekly", "priority": "1.0",
    })

    # ── services hub ────────────────────────────────────────────────────────
    svc_items = [(s["nav"], "services/" + s["slug"], s["desc"].split(".")[0] + ".")
                 for s in SERVICES]
    pages.append({
        "path": "/services/",
        "label": "Services",
        "h1": "Millwork and Cabinetry Services in Toronto",
        "title": "Millwork Services Toronto | Cabinetry, Kitchens & Fit-Outs",
        "desc": ("Custom millwork services in Toronto: kitchens, built-in "
                 "cabinetry, architectural panelling, commercial fit-outs and "
                 "millwork-led interior renovation."),
        "keywords": "millwork services Toronto, custom cabinetry services, joinery Toronto",
        "lede": ("Five things we make, all measured on site and milled in our own "
                 "shop before anyone brings a screwdriver to your walls."),
        "crumbs": [("Services", "services")],
        "page_type": "CollectionPage",
        "body": (page_head_block({"path": "/services/", "label": "Services",
                                  "h1": "Millwork and Cabinetry Services in Toronto",
                                  "lede": "Five things we make, all measured on site and milled in our own shop before anyone brings a screwdriver to your walls.",
                                  "crumbs": [("Services", "services")]})
                 + "\n" + links_grid({"path": "/services/"}, svc_items, "What we make")
                 + "\n" + media_block({"path": "/services/"},
                                      "toronto-custom-millwork-coffered-ceiling",
                                      "Gilded cornice and coffered ceiling millwork in a Toronto home")
                 + "\n" + faq_html(FAQ[:4]) + "\n" + cta_html({"path": "/services/"})),
        "faq": FAQ[:4],
        "changefreq": "monthly", "priority": "0.9",
    })

    # ── service pages ───────────────────────────────────────────────────────
    for s in SERVICES:
        path = "/services/" + s["slug"] + "/"
        ph = {"path": path, "label": s["nav"], "h1": s["h1"], "lede": s["lede"],
              "crumbs": [("Services", "services"), (s["nav"], "services/" + s["slug"])]}
        others = [(o["nav"], "services/" + o["slug"], o["desc"].split(".")[0] + ".")
                  for o in SERVICES if o["slug"] != s["slug"]]
        pages.append({
            "path": path, "label": s["nav"], "h1": s["h1"], "lede": s["lede"],
            "title": s["title"], "desc": s["desc"], "keywords": s["keywords"],
            "crumbs": ph["crumbs"], "service": s, "faq": s["faq"],
            "body": (page_head_block(ph) + "\n" + prose(s["sections"]) + "\n"
                     + media_block(ph, "toronto-custom-cabinetry-wall-panelling",
                                   f"{s['nav']} by Toronto Millworks, panelled interior detail",
                                   "4 / 3")
                     + "\n" + faq_html(s["faq"])
                     + "\n" + links_grid(ph, others, "Other services")
                     + "\n" + cta_html(ph)),
            "changefreq": "monthly", "priority": "0.8",
        })

    # ── projects ────────────────────────────────────────────────────────────
    pp = {"path": "/projects/", "label": "Projects",
          "h1": "Millwork Projects in Toronto",
          "lede": ("A commercial fit-out taken from bare brick shell to finished "
                   "bar, and the residential joinery that runs alongside it."),
          "crumbs": [("Projects", "projects")]}
    pages.append({
        **pp,
        "title": "Millwork Projects Toronto | Fit-Outs and Cabinetry",
        "desc": ("Millwork projects in Toronto, including a commercial bar "
                 "fit-out from bare shell to opening and residential panelling, "
                 "cabinetry and coffered ceilings."),
        "keywords": "millwork projects Toronto, restaurant fit out Toronto, cabinetry portfolio",
        "page_type": "CollectionPage",
        "body": (page_head_block(pp) + "\n"
                 + prose([
                     ("Commercial fit-out, bare shell to opening", [
                         "The sequence on our home page is a single room recorded across "
                         "the whole build. It starts as a bare brick and concrete shell "
                         "with no services, and ends as a working bar with a reclaimed "
                         "timber counter, a black feature wall and the lighting live.",
                         "The counter front is laid up from reclaimed boards of varying "
                         "tone, set in a running bond so no two courses line up. The bar "
                         "top is a solid slab, the back counter is a separate carcass, and "
                         "both were dry fitted in the shop before anything went to site.",
                     ]),
                     ("Residential millwork", [
                         "The panelled interiors shown across the site are the residential "
                         "side of the same shop: raised panel walls, a cased archway, "
                         "coffered ceilings with a gilded cornice and cove lighting, and "
                         "trim run to a profile matched from the original house.",
                     ]),
                 ])
                 + "\n" + media_block(pp, "toronto-custom-millwork-coffered-ceiling",
                                      "Coffered ceiling with gilded cornice and cove lighting, Toronto residential millwork")
                 + "\n" + links_grid(pp, svc_items, "The services behind this work")
                 + "\n" + cta_html(pp)),
        "changefreq": "monthly", "priority": "0.8",
    })

    # ── about ───────────────────────────────────────────────────────────────
    ap = {"path": "/about/", "label": "About", "h1": "About Toronto Millworks",
          "lede": ("A millwork shop in Toronto that measures, draws, mills and "
                   "installs its own work."),
          "crumbs": [("About", "about")]}
    pages.append({
        **ap,
        "title": "About Toronto Millworks | Custom Millwork Shop in Toronto",
        "desc": ("Toronto Millworks is a custom millwork and cabinetry shop "
                 "serving Toronto and the GTA. We measure, draw, mill, install "
                 "and finish our own work."),
        "keywords": "Toronto millwork shop, about Toronto Millworks, custom joinery company",
        "page_type": "AboutPage",
        "body": (page_head_block(ap) + "\n"
                 + prose([
                     ("One shop, start to finish", [
                         "Most joinery on a job site passes through several hands: one "
                         "company draws it, another builds it, a third hangs it and a "
                         "fourth paints it. Every handover is a chance for a dimension to "
                         "drift. We keep all four in the same shop, which is why the "
                         "reveals stay even and the doors line up.",
                     ]),
                     ("How we work", [
                         "We measure the room on site, not from a floor plan.",
                         "We draw elevations and you approve them before anything is cut.",
                         "We mill and dry fit the whole assembly on our own bench.",
                         "We install, scribe to the walls and finish in place.",
                     ]),
                     ("What we work on", [
                         "Kitchens, built-in cabinetry and wardrobes.",
                         "Panelling, cornice, casing and stair details.",
                         "Bars, banquettes, counters and retail joinery.",
                         "Millwork-led interior renovation.",
                     ]),
                 ])
                 + "\n" + media_block(ap, "toronto-custom-cabinetry-wall-panelling",
                                      "Raised wall panelling and a cased archway built by Toronto Millworks",
                                      "4 / 3")
                 + "\n" + faq_html(FAQ[3:7]) + "\n" + cta_html(ap)),
        "faq": FAQ[3:7],
        "changefreq": "monthly", "priority": "0.7",
    })

    # ── contact ─────────────────────────────────────────────────────────────
    cp = {"path": "/contact/", "label": "Contact", "h1": "Tell us about the room.",
          "lede": ("Send drawings, a photo or just the dimensions. We come back "
                   "with a measured quote rather than a guess."),
          "crumbs": [("Contact", "contact")]}

    block_rows = [
        ("Scope", "Residential and commercial"),
        ("Service area", "Toronto and the GTA"),
        ("Drawings", "Measured on site"),
        ("Build", "In our own shop"),
    ]
    rows_html = "\n".join(
        f'        <div class="cx__row"><dt>{E(k)}</dt><dd>{E(v)}</dd></div>'
        for k, v in block_rows)

    steps = [
        ("Send what you have",
         "Rough dimensions or a floor plan, photos of the space as it is now, "
         "and any reference for the finish or profile you want."),
        ("We measure and draw",
         "We come out and template from the real walls, then draw elevations "
         "showing every door, reveal and hardware position."),
        ("You get a measured quote",
         "Priced from the approved drawings, so the number reflects your actual "
         "room instead of a per foot rate."),
    ]
    steps_html = "\n".join(
        f'      <li class="cx__step">\n'
        f'        <span class="cx__step-n">{i:02d}</span>\n'
        f'        <h2 class="cx__step-h">{E(t)}</h2>\n'
        f'        <p class="cx__step-p">{E(d)}</p>\n'
        f'      </li>'
        for i, (t, d) in enumerate(steps, start=1))

    pages.append({
        **cp,
        "title": "Contact | Custom Millwork Quote in Toronto | Toronto Millworks",
        "desc": ("Contact Toronto Millworks for a custom millwork or cabinetry "
                 "quote in Toronto and the GTA. Send drawings, a photo or the "
                 "room dimensions for a measured price."),
        "keywords": ("contact Toronto Millworks, millwork quote Toronto, custom "
                     "cabinetry quote, joinery estimate Toronto"),
        "page_type": "ContactPage",
        "body": (
            '<section class="cx">\n'
            '  <div class="shell">\n'
            f'    {crumbs_html(cp)}\n'
            '\n'
            '    <div class="cx__grid">\n'
            '      <div class="cx__lead">\n'
            '        <span class="pill pill--line"><i class="dot" aria-hidden="true"></i>Contact</span>\n'
            f'        <h1 class="cx__title">{E(cp["h1"])}</h1>\n'
            f'        <p class="cx__lede">{E(cp["lede"])}</p>\n'
            '\n'
            '        <div class="cx__mail">\n'
            '          <span class="cx__mail-k">Write to us</span>\n'
            f'          <a class="cx__mail-a" href="mailto:{SITE["email"]}">{SITE["email"]}</a>\n'
            f'          <button class="cx__copy" type="button" data-copy="{SITE["email"]}" '
            'aria-label="Copy the email address">\n'
            '            <span class="cx__copy-t">Copy</span>\n'
            '          </button>\n'
            '        </div>\n'
            '      </div>\n'
            '\n'
            '      <aside class="cx__block" aria-label="At a glance">\n'
            '        <span class="cx__block-h">Toronto Millworks</span>\n'
            '        <dl class="cx__rows">\n'
            f'{rows_html}\n'
            '        </dl>\n'
            '        <address class="cx__addr">\n'
            f'          {SITE["locality"]}, {SITE["region_name"]}<br>Canada\n'
            '        </address>\n'
            '      </aside>\n'
            '    </div>\n'
            '  </div>\n'
            '\n'
            '  <div class="shell">\n'
            '    <ol class="cx__steps">\n'
            f'{steps_html}\n'
            '    </ol>\n'
            '  </div>\n'
            '</section>'
            + "\n" + faq_html(FAQ[:5])),
        "faq": FAQ[:5],
        "changefreq": "monthly", "priority": "0.9",
    })

    # ── FAQ ─────────────────────────────────────────────────────────────────
    fp = {"path": "/faq/", "label": "FAQ",
          "h1": "Custom Millwork FAQ",
          "lede": ("The questions we are asked most about cost, timing, materials "
                   "and how a millwork project actually runs."),
          "crumbs": [("FAQ", "faq")]}
    pages.append({
        **fp,
        "title": "Custom Millwork FAQ | Cost, Timing & Materials | Toronto",
        "desc": ("Answers to common questions about custom millwork in Toronto: "
                 "what it costs, how long it takes, materials, matching existing "
                 "trim and which areas we serve."),
        "keywords": "millwork FAQ, custom cabinetry cost Toronto, millwork questions",
        "body": (page_head_block(fp) + "\n" + faq_html(FAQ) + "\n" + cta_html(fp)),
        "faq": FAQ,
        "changefreq": "monthly", "priority": "0.7",
    })

    # ── service areas ───────────────────────────────────────────────────────
    area_items = [(a["name"], "service-areas/" + a["slug"], a["lede"]) for a in AREA_PAGES]
    sp = {"path": "/service-areas/", "label": "Service areas",
          "h1": "Millwork Service Areas Across the GTA",
          "lede": ("We measure, build and install across Toronto and the "
                   "surrounding Greater Toronto Area."),
          "crumbs": [("Service areas", "service-areas")]}
    pages.append({
        **sp,
        "title": "Millwork Service Areas | Toronto & GTA | Toronto Millworks",
        "desc": ("Custom millwork and cabinetry across Toronto, North York, "
                 "Etobicoke, Scarborough, Vaughan and Mississauga. Measured on "
                 "site and installed by our own shop."),
        "keywords": "millwork Toronto GTA, cabinetry service area Toronto",
        "page_type": "CollectionPage",
        "body": (page_head_block(sp) + "\n"
                 + links_grid(sp, area_items, "Where we work") + "\n" + cta_html(sp)),
        "changefreq": "monthly", "priority": "0.7",
    })

    for a in AREA_PAGES:
        path = "/service-areas/" + a["slug"] + "/"
        h = {"path": path, "label": a["name"],
             "h1": f"Custom Millwork in {a['name']}", "lede": a["lede"],
             "crumbs": [("Service areas", "service-areas"), (a["name"], "service-areas/" + a["slug"])]}
        pages.append({
            **h, "title": a["title"], "desc": a["desc"],
            "keywords": f"custom millwork {a['name']}, cabinetry {a['name']}, joinery {a['name']}",
            "body": (page_head_block(h) + "\n"
                     + prose([
                         (f"Working in {a['name']}", [a["notes"]]),
                         ("What we build here", [
                             "Custom kitchens and kitchen cabinetry.",
                             "Built-in storage, wardrobes and media walls.",
                             "Wall panelling, cornice and trim matched to the house.",
                             "Commercial bars, counters and office joinery.",
                         ]),
                     ])
                     + "\n" + links_grid(h, svc_items, "Services available in " + a["name"])
                     + "\n" + cta_html(h)),
            "changefreq": "monthly", "priority": "0.6",
        })

    # ── guide (Article) ─────────────────────────────────────────────────────
    gp = {"path": "/guides/how-custom-millwork-is-made/", "label": "Guide",
          "h1": "How Custom Millwork Is Measured, Milled and Installed",
          "lede": ("What actually happens between the first site visit and the "
                   "day the joinery is finished in your room."),
          "crumbs": [("Guides", "guides"), ("How custom millwork is made", "guides/how-custom-millwork-is-made")]}
    pages.append({
        **gp,
        "title": "How Custom Millwork Is Made | Measure, Mill, Install | Guide",
        "desc": ("A step by step guide to how custom millwork is made, from the "
                 "site measure and shop drawings through milling, dry fitting, "
                 "installation and on site finishing."),
        "keywords": "how custom millwork is made, millwork process, shop drawings millwork",
        "is_article": True, "og_type": "article", "page_type": "WebPage",
        "body": (page_head_block(gp) + "\n"
                 + prose([
                     ("1. The site measure", [
                         "Nothing useful can be drawn from a floor plan alone. Walls in "
                         "older Toronto houses are rarely plumb, corners are rarely square "
                         "and floors run away from you. We measure the real opening at "
                         "several heights, record the out of square and find the services "
                         "behind the wall before anything is drawn.",
                     ]),
                     ("2. Shop drawings", [
                         "The measurements become elevations: every door, drawer, reveal, "
                         "shelf and hardware position drawn to scale. This is the stage "
                         "where changes are cheap. Once you approve the drawings they "
                         "become the instruction the shop cuts to.",
                     ]),
                     ("3. Milling", [
                         "Sheet goods and solid stock are cut, edged and machined. Profiles "
                         "that have to match existing trim are run with a ground knife "
                         "rather than approximated with a stock router bit.",
                     ]),
                     ("4. Dry fitting", [
                         "The assembly is put together on the bench before it leaves. This "
                         "is the difference between millwork and a flat pack: problems are "
                         "found in the shop where there are tools, not in your kitchen.",
                     ]),
                     ("5. Installation and scribing", [
                         "On site the carcasses are levelled, fixed and scribed to the "
                         "walls so the gaps disappear. Scribing is the reason a fitted "
                         "piece looks built in rather than pushed against a wall.",
                     ]),
                     ("6. Finishing", [
                         "Filling, sanding and final finish happen in place, so the joins "
                         "made during install disappear into the finished surface.",
                     ]),
                 ])
                 + "\n" + media_block(gp, "toronto-custom-cabinetry-wall-panelling",
                                      "Finished wall panelling and cased archway showing scribed millwork detail",
                                      "4 / 3")
                 + "\n" + faq_html(FAQ[6:]) + "\n" + cta_html(gp)),
        "faq": FAQ[6:],
        "changefreq": "yearly", "priority": "0.6",
    })

    return pages


# ══════════════════════════════════════════════════════════════════════════════
#  TECHNICAL SEO FILES
# ══════════════════════════════════════════════════════════════════════════════
SITEMAP_IMAGES = {
    "/": [(HERO_IMG, "Coffered ceiling with gilded cornice and raised wall panelling, custom millwork in Toronto"),
          (CRAFT_IMG, "Panelled walls and a cased archway built by Toronto Millworks")],
    "/projects/": [(HERO_IMG, "Coffered ceiling and gilded cornice, Toronto millwork project")],
    "/about/": [(CRAFT_IMG, "Raised wall panelling and cased archway by Toronto Millworks")],
}


def sitemap(pages):
    rows = []
    for pg in pages:
        if pg.get("noindex"):
            continue
        u = url(pg["path"])
        r = ['  <url>', f'    <loc>{u}</loc>',
             f'    <lastmod>{BUILD_DATE}</lastmod>',
             f'    <changefreq>{pg.get("changefreq", "monthly")}</changefreq>',
             f'    <priority>{pg.get("priority", "0.6")}</priority>']
        for src, cap in SITEMAP_IMAGES.get(pg["path"], []):
            r += ['    <image:image>',
                  f'      <image:loc>{O}/{src}</image:loc>',
                  f'      <image:title>{E(cap)}</image:title>',
                  f'      <image:caption>{E(cap)}</image:caption>',
                  '    </image:image>']
        r.append('  </url>')
        rows.append("\n".join(r))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + "\n".join(rows) + '\n</urlset>\n')


def robots_txt():
    return f"""# robots.txt for {SITE['name']}
User-agent: *
Allow: /
Disallow: /search/
Disallow: /404.html

# AI crawlers are welcome. Structured summaries live in /llms.txt
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {O}/sitemap.xml
"""


def llms_txt(pages):
    def group(prefix):
        return [p for p in pages
                if p["path"].startswith(prefix) and p["path"] != prefix
                and not p.get("noindex")]
    lines = [
        f"# {SITE['name']}",
        "",
        f"> {SITE['tagline']} We measure on site, draw it, mill it in our own "
        "shop, then install and finish it. Residential and commercial work across "
        "Toronto and the Greater Toronto Area.",
        "",
        "## Core pages",
        "",
        f"- [Home]({O}/): Custom millwork, cabinetry and interior renovation in Toronto.",
        f"- [Services]({url('services')}): The five things we make.",
        f"- [Projects]({url('projects')}): A commercial bar fit-out and residential joinery.",
        f"- [About]({url('about')}): One shop that measures, draws, mills and installs.",
        f"- [Contact]({url('contact')}): Get a measured quote.",
        f"- [FAQ]({url('faq')}): Cost, timing, materials and process.",
        "",
        "## Services",
        "",
    ]
    for s in SERVICES:
        lines.append(f"- [{s['nav']}]({url('services/' + s['slug'])}): {s['desc']}")
    lines += ["", "## Service areas", ""]
    for a in AREA_PAGES:
        lines.append(f"- [{a['name']}]({url('service-areas/' + a['slug'])}): {a['desc']}")
    lines += ["", "## Guides", "",
              f"- [How custom millwork is made]({url('guides/how-custom-millwork-is-made')}): "
              "Site measure, shop drawings, milling, dry fitting, install and finishing.",
              "", "## Contact", "",
              f"- Email: {SITE['email']}",
              f"- Location: {SITE['locality']}, {SITE['region_name']}, Canada",
              f"- Service area: {', '.join(AREAS)}", ""]
    return "\n".join(lines)


def llms_full_txt(pages):
    out = [f"# {SITE['name']}, full content", ""]
    out[0] = f"# {SITE['name']} : full content"
    out += [f"> {SITE['tagline']}", "",
            f"Source: {O}/  |  Last updated: {BUILD_DATE}", "",
            "---", ""]
    for s in SERVICES:
        out += [f"## {s['h1']}", "", f"URL: {url('services/' + s['slug'])}", "",
                s["lede"], ""]
        for title, items in s["sections"]:
            out += [f"### {title}", ""]
            out += [f"- {i}" for i in items]
            out += [""]
        out += ["### Questions", ""]
        for q, a in s["faq"]:
            out += [f"**{q}**", "", a, ""]
        out += ["---", ""]
    out += ["## Service areas", ""]
    for a in AREA_PAGES:
        out += [f"### {a['name']}", "", f"URL: {url('service-areas/' + a['slug'])}", "",
                a["lede"], "", a["notes"], ""]
    out += ["---", "", "## Frequently asked questions", ""]
    for q, a in FAQ:
        out += [f"**{q}**", "", a, ""]
    out += ["---", "", "## Contact", "",
            f"- Email: {SITE['email']}",
            f"- Location: {SITE['locality']}, {SITE['region_name']}, Canada",
            f"- Service area: {', '.join(AREAS)}", ""]
    return "\n".join(out)


REDIRECTS = [
    ("/index.html", "/", 301),
    ("/home", "/", 301),
    ("/services.html", "/services/", 301),
    ("/contact.html", "/contact/", 301),
    ("/about.html", "/about/", 301),
]


def host_configs():
    ht = ["# Apache: correct 404 status, canonical host, https and trailing slash",
          "ErrorDocument 404 /404.html", "",
          "<IfModule mod_rewrite.c>", "  RewriteEngine On", "",
          "  # force https", "  RewriteCond %{HTTPS} !=on",
          "  RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]", "",
          "  # single canonical host (www)",
          f"  RewriteCond %{{HTTP_HOST}} !^www\\. [NC]",
          "  RewriteRule ^(.*)$ https://www.%{HTTP_HOST}/$1 [R=301,L]", "",
          "  # add the trailing slash so canonicals and links agree",
          "  RewriteCond %{REQUEST_FILENAME} !-f",
          "  RewriteCond %{REQUEST_URI} !(/$|\\.[a-zA-Z0-9]{2,5}$)",
          "  RewriteRule ^(.*)$ /$1/ [R=301,L]", ""]
    for src, dst, code in REDIRECTS:
        ht.append(f"  RedirectMatch {code} ^{re.escape(src)}$ {dst}")
    ht += ["</IfModule>", ""]

    netlify = ["# Netlify", "[[headers]]", '  for = "/*"', "  [headers.values]",
               '    X-Content-Type-Options = "nosniff"',
               '    Referrer-Policy = "strict-origin-when-cross-origin"', ""]
    for src, dst, code in REDIRECTS:
        netlify += ["[[redirects]]", f'  from = "{src}"', f'  to = "{dst}"',
                    f"  status = {code}", "  force = true", ""]
    netlify += ["[[redirects]]", '  from = "/*"', '  to = "/404.html"',
                "  status = 404", ""]

    # cleanUrls already strips .html and index.html, so only genuinely legacy
    # paths need explicit redirects here.
    vercel = {
        "cleanUrls": True,
        "trailingSlash": True,
        # trailingSlash normalises the path before redirects are matched, so the
        # source has to carry the slash or it never fires
        "redirects": [
            {"source": "/home", "destination": "/", "permanent": True},
            {"source": "/home/", "destination": "/", "permanent": True},
        ],
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "X-Frame-Options", "value": "SAMEORIGIN"}]},
            # the image ladder and the 306 sequence frames are the bulk of the
            # payload and change only when regenerated
            {"source": "/assets/(.*)", "headers": [
                {"key": "Cache-Control",
                 "value": "public, max-age=2592000, stale-while-revalidate=604800"}]},
        ],
    }

    simple = [f"{s}  {d}  {c}" for s, d, c in REDIRECTS] + ["/*  /404.html  404", ""]

    return "\n".join(ht), "\n".join(netlify), json.dumps(vercel, indent=2) + "\n", "\n".join(simple)


def search_page():
    p = {"path": "/search/", "label": "Search", "h1": "Search",
         "lede": "Find a service, an area or an answer.",
         "title": "Search | Toronto Millworks",
         "desc": "Search custom millwork services, service areas and answers.",
         "crumbs": [("Search", "search")], "noindex": True,
         "robots": "noindex, follow"}
    p["body"] = (page_head_block(p) +
                 '\n<section class="shell srch">\n'
                 '  <form class="srch__form" role="search" onsubmit="return false">\n'
                 '    <label class="sr-only" for="q">Search this site</label>\n'
                 '    <input id="q" name="q" type="search" placeholder="Try kitchens, panelling, Etobicoke" autocomplete="off">\n'
                 '  </form>\n'
                 '  <ol id="results" class="srch__out"></ol>\n'
                 '</section>')
    return p


def main():
    pages = build_pages()
    pages.append(search_page())

    written = []
    for pg in pages:
        written.append(write(pg["path"], render(pg)))

    # 404 (served with a real 404 status by the host configs above)
    nf = {"path": "404.html", "label": "404", "h1": "That page is not here",
          "lede": ("The link may be old or mistyped. The pages below cover "
                   "everything on the site."),
          "title": "Page not found | Toronto Millworks",
          "desc": "The page you asked for does not exist. Browse custom "
                  "millwork services, service areas across the GTA, or get in "
                  "touch for a measured quote.",
          "crumbs": [], "noindex": True, "robots": "noindex, follow"}
    svc_items = [(s["nav"], "services/" + s["slug"], s["desc"].split(".")[0] + ".")
                 for s in SERVICES]
    nf["body"] = (page_head_block(nf) + "\n"
                  + links_grid({"path": "/"}, svc_items, "Services")
                  + "\n" + cta_html({"path": "/"}))
    written.append(write("404.html", render(nf)))

    # search index
    idx = [{"t": p["title"].split(" | ")[0], "u": url(p["path"]),
            "d": p["desc"], "k": p.get("keywords", "")}
           for p in pages if not p.get("noindex")]
    open(os.path.join(ROOT, "search-index.json"), "w").write(
        json.dumps(idx, ensure_ascii=False, separators=(",", ":")))

    open(os.path.join(ROOT, "sitemap.xml"), "w").write(sitemap(pages))
    open(os.path.join(ROOT, "robots.txt"), "w").write(robots_txt())
    open(os.path.join(ROOT, "llms.txt"), "w").write(llms_txt(pages))
    open(os.path.join(ROOT, "llms-full.txt"), "w").write(llms_full_txt(pages))

    ht, netlify, vercel, simple = host_configs()
    open(os.path.join(ROOT, ".htaccess"), "w").write(ht)
    open(os.path.join(ROOT, "netlify.toml"), "w").write(netlify)
    open(os.path.join(ROOT, "vercel.json"), "w").write(vercel)
    open(os.path.join(ROOT, "_redirects"), "w").write(simple)

    print(f"{len(written)} pages written")
    for w in written:
        print("  " + os.path.relpath(w, ROOT))
    print("\nsitemap.xml, robots.txt, llms.txt, llms-full.txt, search-index.json")
    print(".htaccess, netlify.toml, vercel.json, _redirects")


if __name__ == "__main__":
    main()
