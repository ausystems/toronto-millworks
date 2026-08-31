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
        f'<script src="{rel_prefix(page["path"])}assets/js/gsap.min.js" defer></script>',
        f'<script src="{rel_prefix(page["path"])}assets/js/ScrollTrigger.min.js" defer></script>',
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
#  Neo-Swiss composition: a strict grid, oversized type, generous air, and
#  imagery that is art directed per breakpoint rather than cropped by luck.
# ══════════════════════════════════════════════════════════════════════════════
import glob
from build_library import PLATES as LIB

_WIDTHS = {}


def lib_widths(name, kind):
    key = (name, kind)
    if key not in _WIDTHS:
        found = glob.glob(os.path.join(ROOT, "assets/img/lib", f"{name}-{kind}-*.webp"))
        _WIDTHS[key] = sorted(int(re.search(r"-(\d+)\.webp$", f).group(1)) for f in found)
    return _WIDTHS[key]


def fig(page, name, cls="", wide="100vw", tall="100vw", eager=False):
    """A picture with a genuinely different composition per breakpoint. The
    phone gets a portrait crop built around the same focal point, so nothing is
    ever squeezed or beheaded."""
    p = rel_prefix(page["path"])
    alt = LIB[name][4]
    w, t = lib_widths(name, "wide"), lib_widths(name, "tall")
    if not w or not t:
        raise SystemExit(f"missing library plate: {name}")
    ss_w = ", ".join(f"{p}assets/img/lib/{name}-wide-{x}.webp {x}w" for x in w)
    ss_t = ", ".join(f"{p}assets/img/lib/{name}-tall-{x}.webp {x}w" for x in t)
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    klass = ("fig " + cls).strip()
    return (f'<figure class="{klass}">\n'
            f'  <picture>\n'
            f'    <source media="(min-width: 760px)" srcset="{ss_w}" sizes="{wide}">\n'
            f'    <img src="{p}assets/img/lib/{name}-tall-{t[0]}.webp" srcset="{ss_t}" '
            f'sizes="{tall}" width="{t[-1]}" height="{round(t[-1]*5/4)}" '
            f'{load} decoding="async" alt="{E(alt)}">\n'
            f'  </picture>\n'
            f'</figure>')


def phead(page, plate=None):
    """Oversized editorial header. The breadcrumb sits quietly above it."""
    chip = (f'<span class="pill pill--line"><i class="dot" aria-hidden="true"></i>'
            f'{E(page["label"])}</span>' if page.get("label") else "")
    out = ['<header class="ph">',
           '  <div class="shell">',
           f'    {crumbs_html(page)}',
           f'    {chip}',
           f'    <h1 class="ph__t">{E(page["h1"])}</h1>',
           '    <div class="ph__l">',
           f'      <p>{E(page["lede"])}</p>',
           '    </div>',
           '  </div>',
           '</header>']
    if plate:
        out.append(fig(page, plate, "fig--bleed", wide="100vw", tall="100vw", eager=True))
    return "\n".join(out)


def say(text, small=False):
    """One large statement, standing alone. No rule, no number, no ornament."""
    return ('<section class="say">\n  <div class="shell">\n'
            f'    <p class="say__t{" say__t--s" if small else ""}">{E(text)}</p>\n'
            '  </div>\n</section>')


def cols(blocks):
    """Swiss two column body: label left, prose right, aligned to one baseline."""
    out = []
    for title, items in blocks:
        long = any(len(i) > 150 for i in items)
        inner = ("".join(f'<p>{E(i)}</p>' for i in items) if long
                 else '<ul>' + "".join(f'<li>{E(i)}</li>' for i in items) + '</ul>')
        out.append('    <div class="cols__row">\n'
                   f'      <h2 class="cols__h">{E(title)}</h2>\n'
                   f'      <div class="cols__b">{inner}</div>\n'
                   '    </div>')
    return ('<section class="cols">\n  <div class="shell">\n'
            + "\n".join(out) + '\n  </div>\n</section>')


def figpair(page, a, b):
    """Two plates at deliberately unequal weight, the way a spread is set."""
    return ('<section class="pair">\n  <div class="shell pair__g">\n'
            + fig(page, a, "pair__a", wide="52vw", tall="100vw") + "\n"
            + fig(page, b, "pair__b", wide="38vw", tall="100vw") + "\n"
            '  </div>\n</section>')


def figsay(page, plate, heading, body, flip=False):
    """A plate held against a short statement. Alternates side to side."""
    return (f'<section class="fs{" fs--flip" if flip else ""}">\n'
            '  <div class="shell fs__g">\n'
            + fig(page, plate, "fs__f", wide="50vw", tall="100vw") + "\n"
            '    <div class="fs__t">\n'
            f'      <h2 class="fs__h">{E(heading)}</h2>\n'
            f'      <p class="fs__p">{E(body)}</p>\n'
            '    </div>\n  </div>\n</section>')


def cards(page, items, heading):
    """Link grid. Each card carries a plate, and no card carries a number."""
    p = rel_prefix(page["path"])
    out = []
    for name, path, blurb, plate in items:
        out.append(
            f'      <li class="cards__i"><a href="{p}{path.strip("/")}/">\n'
            + fig(page, plate, "cards__f", wide="30vw", tall="46vw") + "\n"
            f'        <h3 class="cards__t">{E(name)}</h3>\n'
            f'        <p class="cards__d">{E(blurb)}</p>\n'
            '      </a></li>')
    return ('<section class="cards">\n  <div class="shell">\n'
            f'    <h2 class="cards__h">{E(heading)}</h2>\n'
            '    <ul class="cards__g">\n' + "\n".join(out) + '\n    </ul>\n'
            '  </div>\n</section>')


def strip(page, plates, heading, caption=None):
    """A run of plates read left to right, for a sequence with a narrative."""
    inner = "\n".join(fig(page, n, "strip__f", wide="34vw", tall="80vw") for n in plates)
    cap = f'    <p class="strip__c">{E(caption)}</p>\n' if caption else ""
    return ('<section class="strip">\n  <div class="shell">\n'
            f'    <h2 class="strip__h">{E(heading)}</h2>\n'
            f'{cap}'
            '  </div>\n  <div class="strip__r">\n' + inner + '\n  </div>\n</section>')


# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════
def build_pages():
    pages = []

    # which plate carries which page. Nothing repeats as a hero.
    SVC_PLATE = {
        "custom-kitchens":         ("counter", "base", "doors"),
        "cabinetry-and-built-ins": ("panel-corner", "doors", "sconce"),
        "architectural-millwork":  ("cornice", "coffer", "base"),
        "commercial-fit-outs":     ("finished", "feature", "carcass"),
        "interior-renovation":     ("room", "archway", "panel-corner"),
    }
    AREA_PLATE = ["room", "doors", "archway", "panel-corner", "coffer", "sconce"]

    svc_cards = [(sv["nav"], "services/" + sv["slug"], sv["desc"].split(".")[0] + ".",
                  SVC_PLATE[sv["slug"]][0]) for sv in SERVICES]

    # home keeps its own composition
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

    # services hub
    sp = {"path": "/services/", "label": "Services",
          "h1": "Everything we make, made to measure.",
          "lede": ("Five things we build, all templated from your walls and milled "
                   "in our own shop before anything reaches your room."),
          "crumbs": [("Services", "services")]}
    pages.append({
        **sp,
        "title": "Millwork Services Toronto | Cabinetry, Kitchens & Fit-Outs",
        "desc": ("Custom millwork services in Toronto: kitchens, built-in "
                 "cabinetry, architectural panelling, commercial fit-outs and "
                 "millwork-led interior renovation."),
        "keywords": "millwork services Toronto, custom cabinetry services, joinery Toronto",
        "page_type": "CollectionPage",
        "body": (phead(sp, "room") + "\n"
                 + say("A kitchen and a bar are the same problem. A room that is "
                       "not square, and a piece that has to look like it grew there.")
                 + "\n" + cards(sp, svc_cards, "What we make")
                 + "\n" + figpair(sp, "cornice", "sconce")
                 + "\n" + faq_html(FAQ[:4]) + "\n" + cta_html(sp)),
        "faq": FAQ[:4],
        "changefreq": "monthly", "priority": "0.9",
    })

    # service pages
    for sv in SERVICES:
        path = "/services/" + sv["slug"] + "/"
        hero, second, third = SVC_PLATE[sv["slug"]]
        h = {"path": path, "label": sv["nav"], "h1": sv["h1"], "lede": sv["lede"],
             "crumbs": [("Services", "services"), (sv["nav"], "services/" + sv["slug"])]}
        others = [(o["nav"], "services/" + o["slug"], o["desc"].split(".")[0] + ".",
                   SVC_PLATE[o["slug"]][0]) for o in SERVICES if o["slug"] != sv["slug"]]
        sec_title, sec_items = sv["sections"][0]
        rest = sv["sections"][1:]
        pages.append({
            **h, "title": sv["title"], "desc": sv["desc"], "keywords": sv["keywords"],
            "service": sv, "faq": sv["faq"],
            "body": (phead(h, hero) + "\n"
                     + cols([(sec_title, sec_items)]) + "\n"
                     + figpair(h, second, third) + "\n"
                     + (cols(rest) + "\n" if rest else "")
                     + faq_html(sv["faq"]) + "\n"
                     + cards(h, others, "Other services") + "\n"
                     + cta_html(h)),
            "changefreq": "monthly", "priority": "0.8",
        })

    # projects
    pp = {"path": "/projects/", "label": "Projects",
          "h1": "A shell, and then a room.",
          "lede": ("One commercial fit-out recorded from bare brick to opening "
                   "night, and the residential joinery running alongside it."),
          "crumbs": [("Projects", "projects")]}
    pages.append({
        **pp,
        "title": "Millwork Projects Toronto | Fit-Outs and Cabinetry",
        "desc": ("Millwork projects in Toronto, including a commercial bar "
                 "fit-out from bare shell to opening and residential panelling, "
                 "cabinetry and coffered ceilings."),
        "keywords": "millwork projects Toronto, restaurant fit out Toronto, cabinetry portfolio",
        "page_type": "CollectionPage",
        "body": (phead(pp, "finished") + "\n"
                 + say("It arrives as brick, concrete and a ceiling full of "
                       "services. It leaves as somewhere you would sit down.")
                 + "\n"
                 + strip(pp, ["shell", "lit", "feature", "carcass", "finished"],
                         "The fit-out, in order",
                         "Bare shell, lighting live, the feature wall in, the bar "
                         "carcass against the brick, and the finished room.")
                 + "\n"
                 + figsay(pp, "counter", "The counter front",
                          "Reclaimed boards of varying tone, laid up in a running "
                          "bond so no two courses line up. The top is a solid slab. "
                          "Both were dry fitted on the bench before anything went "
                          "to site.")
                 + "\n"
                 + figsay(pp, "cornice", "The residential side",
                          "The same shop runs raised panel walls, cased openings "
                          "and coffered ceilings with a gilded cornice, milled to "
                          "a profile taken from the original house.", flip=True)
                 + "\n" + figpair(pp, "archway", "base")
                 + "\n" + cards(pp, svc_cards, "The services behind this work")
                 + "\n" + cta_html(pp)),
        "changefreq": "monthly", "priority": "0.8",
    })

    # about
    ap = {"path": "/about/", "label": "About", "h1": "One shop, start to finish.",
          "lede": ("We measure, draw, mill, install and finish our own work, so "
                   "no dimension goes missing in a handover."),
          "crumbs": [("About", "about")]}
    pages.append({
        **ap,
        "title": "About Toronto Millworks | Custom Millwork Shop in Toronto",
        "desc": ("Toronto Millworks is a custom millwork and cabinetry shop "
                 "serving Toronto and the GTA. We measure, draw, mill, install "
                 "and finish our own work."),
        "keywords": "Toronto millwork shop, about Toronto Millworks, custom joinery company",
        "page_type": "AboutPage",
        "body": (phead(ap, "sconce") + "\n"
                 + say("Most joinery passes through four companies before it is "
                       "hung. Every handover is a chance for a dimension to drift.")
                 + "\n"
                 + cols([
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
                 + "\n" + figpair(ap, "archway", "base")
                 + "\n"
                 + figsay(ap, "room", "Why it stays even",
                          "Walls in older Toronto houses are rarely plumb and "
                          "corners are rarely square. Scribing on site is what "
                          "closes the gap between a drawing and a hundred year "
                          "old wall.")
                 + "\n" + faq_html(FAQ[3:7]) + "\n" + cta_html(ap)),
        "faq": FAQ[3:7],
        "changefreq": "monthly", "priority": "0.7",
    })

    # contact keeps its own composition
    cp = {"path": "/contact/", "label": "Contact", "h1": "Tell us about the room.",
          "lede": ("Send drawings, a photo or just the dimensions. We come back "
                   "with a measured quote rather than a guess."),
          "crumbs": [("Contact", "contact")]}
    block_rows = [("Scope", "Residential and commercial"),
                  ("Service area", "Toronto and the GTA"),
                  ("Drawings", "Measured on site"),
                  ("Build", "In our own shop")]
    rows_html = "\n".join(
        '        <div class="cx__row"><dt>' + E(k) + '</dt><dd>' + E(v) + '</dd></div>'
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
        '      <li class="cx__step">\n'
        '        <h2 class="cx__step-h">' + E(t) + '</h2>\n'
        '        <p class="cx__step-p">' + E(d) + '</p>\n'
        '      </li>' for t, d in steps)
    pages.append({
        **cp,
        "title": "Contact | Custom Millwork Quote in Toronto | Toronto Millworks",
        "desc": ("Contact Toronto Millworks for a custom millwork or cabinetry "
                 "quote in Toronto and the GTA. Send drawings, a photo or the "
                 "room dimensions for a measured price."),
        "keywords": ("contact Toronto Millworks, millwork quote Toronto, custom "
                     "cabinetry quote, joinery estimate Toronto"),
        "page_type": "ContactPage",
        "body": ('<section class="cx">\n  <div class="shell">\n'
                 + "    " + crumbs_html(cp) + "\n\n    <div class=\"cx__grid\">\n"
                 '      <div class="cx__lead">\n'
                 '        <span class="pill pill--line"><i class="dot" aria-hidden="true"></i>Contact</span>\n'
                 '        <h1 class="cx__title">' + E(cp["h1"]) + '</h1>\n'
                 '        <p class="cx__lede">' + E(cp["lede"]) + '</p>\n\n'
                 '        <div class="cx__mail">\n'
                 '          <span class="cx__mail-k">Write to us</span>\n'
                 '          <a class="cx__mail-a" href="mailto:' + SITE["email"] + '">' + SITE["email"] + '</a>\n'
                 '          <button class="cx__copy" type="button" data-copy="' + SITE["email"] + '" '
                 'aria-label="Copy the email address">\n'
                 '            <span class="cx__copy-t">Copy</span>\n'
                 '          </button>\n        </div>\n      </div>\n\n'
                 '      <aside class="cx__block" aria-label="At a glance">\n'
                 '        <span class="cx__block-h">Toronto Millworks</span>\n'
                 '        <dl class="cx__rows">\n' + rows_html + '\n        </dl>\n'
                 '        <address class="cx__addr">\n'
                 '          ' + SITE["locality"] + ', ' + SITE["region_name"] + '<br>Canada\n'
                 '        </address>\n      </aside>\n    </div>\n  </div>\n\n'
                 '  <div class="shell">\n    <ol class="cx__steps">\n'
                 + steps_html + '\n    </ol>\n  </div>\n</section>'
                 + "\n" + faq_html(FAQ[:5])),
        "faq": FAQ[:5],
        "changefreq": "monthly", "priority": "0.9",
    })

    # faq
    fp = {"path": "/faq/", "label": "FAQ", "h1": "Questions, answered plainly.",
          "lede": ("What custom millwork costs, how long it takes, what it is "
                   "made from, and how a project actually runs."),
          "crumbs": [("FAQ", "faq")]}
    pages.append({
        **fp,
        "title": "Custom Millwork FAQ | Cost, Timing & Materials | Toronto",
        "desc": ("Answers to common questions about custom millwork in Toronto: "
                 "what it costs, how long it takes, materials, matching existing "
                 "trim and which areas we serve."),
        "keywords": "millwork FAQ, custom cabinetry cost Toronto, millwork questions",
        "body": (phead(fp, "doors") + "\n" + faq_html(FAQ) + "\n"
                 + figpair(fp, "coffer", "counter") + "\n"
                 + cards(fp, svc_cards, "Where to next") + "\n" + cta_html(fp)),
        "faq": FAQ,
        "changefreq": "monthly", "priority": "0.7",
    })

    # service areas
    area_cards = [(a["name"], "service-areas/" + a["slug"], a["lede"],
                   AREA_PLATE[i % len(AREA_PLATE)]) for i, a in enumerate(AREA_PAGES)]
    sap = {"path": "/service-areas/", "label": "Service areas",
           "h1": "Toronto, and the ground around it.",
           "lede": "We measure, build and install across the city and the wider GTA.",
           "crumbs": [("Service areas", "service-areas")]}
    pages.append({
        **sap,
        "title": "Millwork Service Areas | Toronto & GTA | Toronto Millworks",
        "desc": ("Custom millwork and cabinetry across Toronto, North York, "
                 "Etobicoke, Scarborough, Vaughan and Mississauga. Measured on "
                 "site and installed by our own shop."),
        "keywords": "millwork Toronto GTA, cabinetry service area Toronto",
        "page_type": "CollectionPage",
        "body": (phead(sap, "room") + "\n"
                 + say("Almost no wall in this city is square. That is the whole "
                       "reason anything worth fitting is templated on site.")
                 + "\n" + cards(sap, area_cards, "Where we work")
                 + "\n" + figpair(sap, "doors", "base") + "\n" + cta_html(sap)),
        "changefreq": "monthly", "priority": "0.7",
    })

    for i, a in enumerate(AREA_PAGES):
        path = "/service-areas/" + a["slug"] + "/"
        hero = AREA_PLATE[i % len(AREA_PLATE)]
        alt2 = AREA_PLATE[(i + 2) % len(AREA_PLATE)]
        alt3 = AREA_PLATE[(i + 4) % len(AREA_PLATE)]
        h = {"path": path, "label": a["name"], "h1": "Custom Millwork in " + a["name"],
             "lede": a["lede"],
             "crumbs": [("Service areas", "service-areas"),
                        (a["name"], "service-areas/" + a["slug"])]}
        pages.append({
            **h, "title": a["title"], "desc": a["desc"],
            "keywords": "custom millwork " + a["name"] + ", cabinetry " + a["name"] + ", joinery " + a["name"],
            "body": (phead(h, hero) + "\n"
                     + figsay(h, alt2, "Working in " + a["name"], a["notes"])
                     + "\n"
                     + cols([("What we build here", [
                         "Custom kitchens and kitchen cabinetry.",
                         "Built-in storage, wardrobes and media walls.",
                         "Wall panelling, cornice and trim matched to the house.",
                         "Commercial bars, counters and office joinery."])])
                     + "\n" + fig(h, alt3, "fig--bleed")
                     + "\n" + cards(h, svc_cards, "Services available in " + a["name"])
                     + "\n" + cta_html(h)),
            "changefreq": "monthly", "priority": "0.6",
        })

    # guide
    gp = {"path": "/guides/how-custom-millwork-is-made/", "label": "Guide",
          "h1": "How custom millwork is made.",
          "lede": ("What happens between the first site visit and the day the "
                   "joinery is finished in your room."),
          "crumbs": [("Guides", "guides"),
                     ("How custom millwork is made", "guides/how-custom-millwork-is-made")]}
    pages.append({
        **gp,
        "title": "How Custom Millwork Is Made | Measure, Mill, Install | Guide",
        "desc": ("A step by step guide to how custom millwork is made, from the "
                 "site measure and shop drawings through milling, dry fitting, "
                 "installation and on site finishing."),
        "keywords": "how custom millwork is made, millwork process, shop drawings millwork",
        "is_article": True, "og_type": "article",
        "body": (phead(gp, "shell") + "\n"
                 + figsay(gp, "panel-corner", "The site measure",
                          "Nothing useful can be drawn from a floor plan alone. We "
                          "measure the real opening at several heights, record the "
                          "out of square, and find the services behind the wall "
                          "before anything is drawn.")
                 + "\n"
                 + figsay(gp, "coffer", "Shop drawings",
                          "The measurements become elevations: every door, drawer, "
                          "reveal, shelf and hardware position drawn to scale. This "
                          "is the stage where changes are cheap.", flip=True)
                 + "\n"
                 + cols([("Milling and dry fitting", [
                     "Sheet goods and solid stock are cut, edged and machined. "
                     "Profiles that have to match existing trim are run with a "
                     "ground knife rather than approximated with a stock bit.",
                     "The assembly is then put together on the bench before it "
                     "leaves. Problems get found in the shop, where there are "
                     "tools, instead of in your kitchen."])])
                 + "\n" + figpair(gp, "carcass", "counter")
                 + "\n"
                 + figsay(gp, "sconce", "Installing and scribing",
                          "On site the carcasses are levelled, fixed and scribed to "
                          "the walls so the gaps disappear. Scribing is the reason "
                          "a fitted piece looks built in rather than pushed against "
                          "a wall. Filling and finishing happen in place.")
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
    p["body"] = (phead(p) +
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
    plate = {"custom-kitchens": "counter", "cabinetry-and-built-ins": "panel-corner",
             "architectural-millwork": "cornice", "commercial-fit-outs": "finished",
             "interior-renovation": "room"}
    svc_items = [(sv["nav"], "services/" + sv["slug"], sv["desc"].split(".")[0] + ".",
                  plate[sv["slug"]]) for sv in SERVICES]
    nf["body"] = (phead(nf) + "\n"
                  + cards({"path": "/"}, svc_items, "Services")
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
