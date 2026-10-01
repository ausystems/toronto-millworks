#!/usr/bin/env python3
"""
Everything a crawler reads: <head>, the JSON-LD graph, sitemap.xml, robots.txt,
llms.txt, llms-full.txt, the search index, redirects and response headers.

One rule runs through all of it: describe only what is true. Nothing here
emits a rating, a review, opening hours, a phone number or a founding year
unless site_content.py actually has one.
"""
import base64
import hashlib
import html
import json
import re
import urllib.parse as _Q

from site_content import SITE, SERVICES, FAQ, BUILD_DATE
from locations import LOCATIONS, REGION_ORDER, BY_SLUG
from guides import GUIDES

E = lambda s: html.escape(str(s), quote=True)
O = SITE["origin"].rstrip("/")
ORG = f"{O}/#organization"

# pages that existed at the first launch keep that as their publish date
FIRST_LAUNCH = "2026-08-31"
LAUNCHED = {"/", "/services/", "/projects/", "/about/", "/contact/", "/faq/", "/service-areas/",
            "/guides/how-custom-millwork-is-made/"} | {
    f"/services/{s}/" for s in ("custom-kitchens", "cabinetry-and-built-ins",
                                "architectural-millwork", "commercial-fit-outs",
                                "interior-renovation")} | {
    f"/service-areas/{s}/" for s in ("toronto", "north-york", "etobicoke", "scarborough",
                                     "vaughan", "mississauga")}

ADDR_LINE = f'{SITE["street"]}, {SITE["locality"]}, {SITE["region"]} {SITE["postal"]}'
MAP_Q = _Q.quote_plus(ADDR_LINE + ", Canada")
MAP_LINK = f"https://www.google.com/maps/search/?api=1&query={MAP_Q}"
MAP_DIRECTIONS = f"https://www.google.com/maps/dir/?api=1&destination={MAP_Q}"
MAP_EMBED = f"https://maps.google.com/maps?q={MAP_Q}&z=14&output=embed"

# the only inline script on the site: it marks <html> before first paint so
# reveal states never flash. Its hash goes in the CSP instead of 'unsafe-inline'.
BOOT_JS = "document.documentElement.classList.add('js')"
BOOT_HASH = "sha256-" + base64.b64encode(hashlib.sha256(BOOT_JS.encode()).digest()).decode()


def url(path):
    path = path or "/"
    if path == "/":
        return O + "/"
    return O + "/" + path.strip("/") + "/"


# ══════════════════════════════════════════════════════════════════════════════
#  JSON-LD
# ══════════════════════════════════════════════════════════════════════════════
def _address():
    a = {"@type": "PostalAddress", "streetAddress": SITE["street"],
         "addressLocality": SITE["locality"], "addressRegion": SITE["region"],
         "postalCode": SITE["postal"], "addressCountry": SITE["country"]}
    return {k: v for k, v in a.items() if v}


def org_node(full=False):
    n = {
        "@type": ["Organization", "LocalBusiness", "HomeAndConstructionBusiness"],
        "@id": ORG,
        "name": SITE["name"],
        "url": O + "/",
        "logo": {"@type": "ImageObject", "@id": f"{O}/#logo",
                 "url": f"{O}/assets/brand/logo-512.png", "width": 512, "height": 512,
                 "caption": SITE["name"]},
        "image": f"{O}/assets/og/home.jpg",
        "email": SITE["email"],
        "address": _address(),
    }
    if SITE["phone"]:
        n["telephone"] = SITE["phone"]
    if full:
        n.update({
            "description": SITE["tagline"],
            "geo": {"@type": "GeoCoordinates", "latitude": SITE["lat"], "longitude": SITE["lon"]},
            "hasMap": MAP_LINK,
            "areaServed": [
                {"@type": "GeoCircle",
                 "geoMidpoint": {"@type": "GeoCoordinates", "latitude": SITE["lat"],
                                 "longitude": SITE["lon"]},
                 "geoRadius": str(SITE["radius_km"] * 1000)},
            ] + [{"@type": "City", "name": p["name"], "url": url(f"service-areas/{p['slug']}")}
                 for p in LOCATIONS],
            "knowsAbout": ["Custom millwork", "Custom cabinetry", "Kitchen cabinetry",
                           "Built-in cabinetry", "Architectural millwork", "Wall panelling",
                           "Coffered ceilings", "Restaurant and bar millwork",
                           "Office millwork", "Commercial fit-outs", "Interior renovation"],
            "makesOffer": [{"@type": "Offer", "itemOffered": {
                "@type": "Service", "@id": url(f"services/{s['slug']}") + "#service",
                "name": s["h1"]}} for s in SERVICES],
            "contactPoint": [{"@type": "ContactPoint", "contactType": "sales",
                              "email": SITE["email"], "areaServed": "CA-ON",
                              "availableLanguage": ["English"], "url": url("contact")}],
        })
        if SITE["founded"]:
            n["foundingDate"] = SITE["founded"]
        if SITE["same_as"]:
            n["sameAs"] = SITE["same_as"]
    return n


def website_node():
    return {"@type": "WebSite", "@id": f"{O}/#website", "url": O + "/", "name": SITE["name"],
            "description": SITE["tagline"], "inLanguage": SITE["lang"],
            "publisher": {"@id": ORG},
            "potentialAction": {"@type": "SearchAction",
                                "target": {"@type": "EntryPoint",
                                           "urlTemplate": f"{O}/search/?q={{search_term_string}}"},
                                "query-input": "required name=search_term_string"}}


def breadcrumb_node(page):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": O + "/"}]
    for i, (name, path) in enumerate(page.get("crumbs", []), start=2):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": url(path)})
    return {"@type": "BreadcrumbList", "@id": url(page["path"]) + "#breadcrumb",
            "itemListElement": items}


def webpage_node(page):
    u = url(page["path"])
    n = {"@type": page.get("page_type", "WebPage"), "@id": u + "#webpage", "url": u,
         "name": page["title"], "description": page["desc"],
         "isPartOf": {"@id": f"{O}/#website"}, "about": {"@id": ORG},
         "inLanguage": SITE["lang"],
         "datePublished": FIRST_LAUNCH if page["path"] in LAUNCHED else BUILD_DATE,
         "dateModified": BUILD_DATE,
         "primaryImageOfPage": {"@type": "ImageObject", "url": og_url(page),
                                "width": 1200, "height": 630}}
    if page.get("crumbs"):
        n["breadcrumb"] = {"@id": u + "#breadcrumb"}
    if page.get("faq"):
        n["mainEntity"] = {"@id": u + "#faq"}
    return n


def faq_node(page):
    return {"@type": "FAQPage", "@id": url(page["path"]) + "#faq",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in page["faq"]]}


def service_node(page):
    s = page["service"]
    return {"@type": "Service", "@id": url(page["path"]) + "#service", "name": s["h1"],
            "description": s["desc"], "serviceType": s["nav"], "url": url(page["path"]),
            "provider": {"@id": ORG},
            "areaServed": {"@type": "GeoCircle",
                           "geoMidpoint": {"@type": "GeoCoordinates", "latitude": SITE["lat"],
                                           "longitude": SITE["lon"]},
                           "geoRadius": str(SITE["radius_km"] * 1000)},
            "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["h1"],
                                "itemListElement": [
                                    {"@type": "Offer", "itemOffered": {"@type": "Service",
                                                                       "name": t, "description": d}}
                                    for t, d in s["builds"]]}}


def place_service_node(page):
    p = page["place"]
    return {"@type": "Service", "@id": url(page["path"]) + "#service",
            "name": f"Custom millwork and cabinetry in {p['name']}",
            "serviceType": "Custom millwork", "url": url(page["path"]),
            "provider": {"@id": ORG},
            "areaServed": {"@type": "City", "name": p["name"],
                           "geo": {"@type": "GeoCoordinates", "latitude": p["lat"],
                                   "longitude": p["lon"]},
                           "containedInPlace": {"@type": "AdministrativeArea",
                                                "name": p["region"] + ", Ontario"}}}


def article_node(page):
    u = url(page["path"])
    g = page["guide"]
    return {"@type": "Article", "@id": u + "#article", "headline": g["h1"],
            "description": g["desc"], "articleSection": "Guides",
            "mainEntityOfPage": {"@id": u + "#webpage"}, "image": [og_url(page)],
            "datePublished": FIRST_LAUNCH if page["path"] in LAUNCHED else BUILD_DATE,
            "dateModified": BUILD_DATE, "inLanguage": SITE["lang"],
            "wordCount": page.get("words", 0),
            "author": {"@id": ORG}, "publisher": {"@id": ORG}}


def itemlist_node(page):
    return {"@type": "ItemList", "@id": url(page["path"]) + "#list",
            "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "url": url(p)}
                                for i, (n, p) in enumerate(page["itemlist"], 1)]}


def graph_for(page):
    # the 404 answers at whatever address was asked for, so it describes no page
    if page.get("anywhere"):
        return {"@context": "https://schema.org", "@graph": [org_node()]}
    full = page["path"] in ("/", "/about/", "/contact/", "/service-areas/")
    g = [org_node(full=full), webpage_node(page)]
    if page["path"] == "/":
        g.insert(1, website_node())
    if page.get("crumbs"):
        g.append(breadcrumb_node(page))
    if page.get("faq"):
        g.append(faq_node(page))
    if page.get("service"):
        g.append(service_node(page))
    if page.get("place"):
        g.append(place_service_node(page))
    if page.get("guide"):
        g.append(article_node(page))
    if page.get("itemlist"):
        g.append(itemlist_node(page))
    return {"@context": "https://schema.org", "@graph": g}


# ══════════════════════════════════════════════════════════════════════════════
#  HEAD
# ══════════════════════════════════════════════════════════════════════════════
def og_slug(page):
    p = page["path"].strip("/")
    return (p.replace("/", "--") or "home") if p != "404.html" else "404"


def og_url(page):
    return f"{O}/assets/og/{og_slug(page)}.jpg"


def head(page, asset_v):
    u = url(page["path"])
    robots = ("noindex, follow" if page.get("noindex") else
              "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
    ld = json.dumps(graph_for(page), ensure_ascii=False, separators=(",", ":"))
    img = og_url(page)
    alt = page.get("image_alt") or page["title"]
    lines = [
        '<!doctype html>',
        f'<html lang="{SITE["lang"]}">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f'<title>{E(page["title"])}</title>',
        f'<meta name="description" content="{E(page["desc"])}">',
        f'<meta name="robots" content="{robots}">',
    ]
    # a page served at any address has no address of its own to declare
    if not page.get("anywhere"):
        lines.append(f'<link rel="canonical" href="{u}">')
    if not page.get("noindex"):
        lines += [f'<link rel="alternate" hreflang="en-ca" href="{u}">',
                  f'<link rel="alternate" hreflang="x-default" href="{u}">']
    if page.get("keywords"):
        lines.append(f'<meta name="keywords" content="{E(page["keywords"])}">')
    lines += [
        f'<meta property="og:type" content="{page.get("og_type", "website")}">',
        f'<meta property="og:site_name" content="{E(SITE["name"])}">',
        '<meta property="og:locale" content="en_CA">',
    ]
    if not page.get("anywhere"):
        lines.append(f'<meta property="og:url" content="{u}">')
    lines += [
        f'<meta property="og:title" content="{E(page.get("og_title", page["title"]))}">',
        f'<meta property="og:description" content="{E(page["desc"])}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:type" content="image/jpeg">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{E(alt)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{E(page.get("og_title", page["title"]))}">',
        f'<meta name="twitter:description" content="{E(page["desc"])}">',
        f'<meta name="twitter:image" content="{img}">',
        f'<meta name="twitter:image:alt" content="{E(alt)}">',
    ]
    if page.get("og_type") == "article":
        lines += [f'<meta property="article:modified_time" content="{BUILD_DATE}">',
                  '<meta property="article:section" content="Guides">']
    lines += [
        '<meta name="theme-color" content="#FFFFFF">',
        '<meta name="color-scheme" content="light">',
        '<meta name="format-detection" content="telephone=no">',
        f'<meta name="geo.region" content="CA-{SITE["region"]}">',
        f'<meta name="geo.placename" content="{E(SITE["locality"])}">',
        f'<meta name="geo.position" content="{SITE["lat"]};{SITE["lon"]}">',
        f'<meta name="ICBM" content="{SITE["lat"]}, {SITE["lon"]}">',
        '<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">',
        '<link rel="icon" href="/assets/brand/favicon-32.png" sizes="32x32" type="image/png">',
        '<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        '<link rel="preload" href="/assets/fonts/instrument-sans-latin.woff2" as="font" type="font/woff2" crossorigin>',
    ]
    for pre in page.get("preload", []):
        lines.append(pre)
    lines += [
        f'<link rel="stylesheet" href="/css/style.css?v={asset_v}">',
        f'<script>{BOOT_JS}</script>',
        f'<script type="application/ld+json">{ld}</script>',
        '</head>',
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
#  SITE FILES
# ══════════════════════════════════════════════════════════════════════════════
def sitemap(pages):
    rows = []
    for pg in pages:
        if pg.get("noindex"):
            continue
        r = ["  <url>", f"    <loc>{url(pg['path'])}</loc>", f"    <lastmod>{BUILD_DATE}</lastmod>",
             f"    <changefreq>{pg.get('changefreq', 'monthly')}</changefreq>",
             f"    <priority>{pg.get('priority', '0.6')}</priority>"]
        seen = set()
        for src, cap in pg.get("images", []):
            if src in seen:
                continue
            seen.add(src)
            r += ["    <image:image>", f"      <image:loc>{O}{src}</image:loc>",
                  f"      <image:title>{E(cap)}</image:title>",
                  f"      <image:caption>{E(cap)}</image:caption>", "    </image:image>"]
        r.append("  </url>")
        rows.append("\n".join(r))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def robots_txt():
    return f"""# robots.txt for {SITE['name']}
# Everything public is crawlable. Search results and the 404 carry their own
# noindex, which a crawler can only see if it is allowed to fetch them.
User-agent: *
Allow: /

# AI and answer engines are welcome; structured summaries live in /llms.txt
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: {O}/sitemap.xml
"""


def llms_txt():
    L = [f"# {SITE['name']}", "",
         f"> {SITE['tagline']} We measure on site, draw every piece, build it in our own "
         f"shop at {ADDR_LINE}, then install and finish it. Residential and commercial work "
         f"within about {SITE['radius_km']} km of the shop.", "",
         "## Core pages", "",
         f"- [Home]({url('/')}): Custom millwork, cabinetry and interior renovation for Toronto and the GTA.",
         f"- [Services]({url('services')}): The seven things we make.",
         f"- [Projects]({url('projects')}): A commercial bar fit-out, shell to finished room, and residential panelling.",
         f"- [About]({url('about')}): One shop that measures, draws, builds and installs.",
         f"- [Contact]({url('contact')}): Request a measured quote.",
         f"- [FAQ]({url('faq')}): Cost, timing, process, materials and service area.",
         f"- [Service areas]({url('service-areas')}): Every town within {SITE['radius_km']} km of the shop.",
         f"- [Guides]({url('guides')}): Cost, materials, finishes and planning.",
         "", "## Services", ""]
    L += [f"- [{s['nav']}]({url('services/' + s['slug'])}): {s['desc']}" for s in SERVICES]
    L += ["", "## Guides", ""]
    L += [f"- [{g['h1']}]({url('guides/' + g['slug'])}): {g['desc']}" for g in GUIDES]
    L += ["", "## Service areas", ""]
    for region in REGION_ORDER:
        places = [p for p in LOCATIONS if p["region"] == region]
        L.append(f"- {region}: " + ", ".join(
            f"[{p['name']}]({url('service-areas/' + p['slug'])})" for p in places))
    L += ["", "## Contact", "", f"- Shop: {ADDR_LINE}, Canada", f"- Email: {SITE['email']}"]
    if SITE["phone"]:
        L.append(f"- Phone: {SITE['phone']}")
    L += [f"- Visits by appointment.", ""]
    return "\n".join(L)


def llms_full_txt():
    L = [f"# {SITE['name']}: full content", "", f"> {SITE['tagline']}", "",
         f"Source: {O}/ | Updated {BUILD_DATE} | Shop: {ADDR_LINE}, Canada", "", "---", ""]
    for s in SERVICES:
        L += [f"## {s['h1']}", "", f"URL: {url('services/' + s['slug'])}", "", s["lede"], "",
              s["intro"], "", "### What we build", ""]
        L += [f"- {t}: {d}" for t, d in s["builds"]]
        L += ["", "### How it comes together", ""]
        L += [f"- {t}: {d}" for t, d in s["process"]]
        L += ["", "### Questions", ""]
        for q, a in s["faq"]:
            L += [f"**{q}**", "", a, ""]
        L += ["---", ""]
    for g in GUIDES:
        L += [f"## {g['h1']}", "", f"URL: {url('guides/' + g['slug'])}", "", g["lede"], ""]
        for title, blocks in g["sections"]:
            L += [f"### {title}", ""]
            for b in blocks:
                if isinstance(b, str):
                    L += [b, ""]
                elif b[0] == "ul":
                    L += [f"- {i}" for i in b[1]] + [""]
                elif b[0] == "table":
                    L += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])]
                    L += ["| " + " | ".join(r) + " |" for r in b[2]] + [""]
        L += ["---", ""]
    L += ["## Service areas", ""]
    for p in LOCATIONS:
        L += [f"### {p['name']} ({p['region']}), about {p['km']} km {p['dir']} of the shop",
              f"URL: {url('service-areas/' + p['slug'])}", "", p["lede"], "", p["body"], "",
              "Neighbourhoods: " + ", ".join(p["areas"]), ""]
    L += ["---", "", "## Frequently asked questions", ""]
    for q, a in FAQ:
        L += [f"**{q}**", "", a, ""]
    L += ["---", "", "## Contact", "", f"- Shop: {ADDR_LINE}, Canada", f"- Email: {SITE['email']}", ""]
    return "\n".join(L)


def search_index(pages):
    return json.dumps([{"t": p["h1"] if p.get("h1") else p["title"], "u": p["path"],
                        "d": p["desc"], "k": p.get("keywords", ""),
                        "g": p.get("search_group", "Page")}
                       for p in pages if not p.get("noindex")],
                      ensure_ascii=False, separators=(",", ":"))


def manifest():
    return json.dumps({
        "name": SITE["name"], "short_name": "Millworks", "lang": SITE["lang"],
        "start_url": "/", "display": "browser", "background_color": "#FFFFFF",
        "theme_color": "#FFFFFF",
        "icons": [{"src": "/assets/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/brand/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/assets/brand/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
#  HOSTING
# ══════════════════════════════════════════════════════════════════════════════
REDIRECTS = [("/home", "/"), ("/home/", "/"), ("/index.html", "/"),
             ("/services.html", "/services/"), ("/about.html", "/about/"),
             ("/contact.html", "/contact/"), ("/projects.html", "/projects/"),
             ("/faq.html", "/faq/"), ("/areas", "/service-areas/"), ("/areas/", "/service-areas/"),
             ("/locations", "/service-areas/"), ("/locations/", "/service-areas/"),
             ("/quote", "/contact/"), ("/quote/", "/contact/"),
             ("/privacy", "/privacy-policy/"), ("/privacy/", "/privacy-policy/")]

# Build inputs, tooling and docs belong to the repository, never to the site.
# One list keeps them off every host: .vercelignore here, and a hard 404 in the
# Apache and Netlify configs. A trailing slash marks a directory.
PRIVATE = ["/scripts/", "/src/", "/css/src/", "/ci/", "/.claude/", "/SPEC.md", "/SEO.md",
           "/README.md", "/.htaccess", "/_redirects", "/netlify.toml", "/assets/og/.hashes.json"]


def vercelignore():
    return ("# Written by scripts/build_site.py from seo.PRIVATE. The deployment is the\n"
            "# generated site; everything listed here stays in the repository.\n"
            + "\n".join(PRIVATE) + "\n")


def csp():
    ep = SITE["form_endpoint"]
    ep_origin = ""
    if ep:
        u = _Q.urlparse(ep)
        ep_origin = f" {u.scheme}://{u.netloc}"
    return "; ".join([
        "default-src 'self'",
        f"script-src 'self' '{BOOT_HASH}'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob:",
        "font-src 'self'",
        f"connect-src 'self'{ep_origin}",
        "frame-src https://www.google.com https://maps.google.com",
        "frame-ancestors 'none'",
        f"form-action 'self' mailto:{ep_origin}",
        "base-uri 'self'",
        "object-src 'none'",
        "manifest-src 'self'",
        "worker-src 'self' blob:",
        "upgrade-insecure-requests",
    ])


SECURITY_HEADERS = [
    ("Strict-Transport-Security", "max-age=63072000; includeSubDomains"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
                           "browsing-topics=()"),
    ("Cross-Origin-Opener-Policy", "same-origin"),
]


def vercel_json():
    return json.dumps({
        "cleanUrls": True,
        "trailingSlash": True,
        # trailingSlash normalises the path before redirects are matched, so both
        # forms are listed
        "redirects": [{"source": s, "destination": d, "permanent": True} for s, d in REDIRECTS],
        "headers": [
            {"source": "/(.*)", "headers": [{"key": k, "value": v} for k, v in SECURITY_HEADERS]
             + [{"key": "Content-Security-Policy", "value": csp()}]},
            {"source": "/assets/fonts/(.*)", "headers": [
                {"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/(css|js)/(.*)", "headers": [
                {"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/assets/(img|millwork-fit-out-sequence|og|brand|js)/(.*)", "headers": [
                {"key": "Cache-Control",
                 "value": "public, max-age=2592000, stale-while-revalidate=604800"}]},
            {"source": "/(search|404)/(.*)", "headers": [
                {"key": "X-Robots-Tag", "value": "noindex, follow"}]},
        ],
    }, indent=2) + "\n"


def other_hosts():
    """Equivalent configs for Netlify and Apache, kept in step so the site can move."""
    host = _Q.urlparse(O).netloc
    ht = ["# Apache: real 404 status, https, one canonical host, trailing slashes",
          "ErrorDocument 404 /404.html", "",
          "<IfModule mod_rewrite.c>", "  RewriteEngine On",
          "  RewriteCond %{HTTPS} !=on",
          "  RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]",
          f"  RewriteCond %{{HTTP_HOST}} !^{host.replace('.', chr(92) + '.')}$ [NC]",
          f"  RewriteRule ^(.*)$ https://{host}/$1 [R=301,L]",
          "  RewriteCond %{REQUEST_FILENAME} !-f",
          "  RewriteCond %{REQUEST_URI} !(/$|\\.[a-zA-Z0-9]{2,5}$)",
          "  RewriteRule ^(.*)$ /$1/ [R=301,L]", "</IfModule>", ""]
    ht += [f"Redirect 301 {s} {d}" for s, d in REDIRECTS if not s.endswith("/")]
    ht += ["", "# sources stay in the repository",
           'RedirectMatch 404 "^(?:' + "|".join(re.escape(p) + ("" if p.endswith("/") else "$")
                                               for p in PRIVATE) + ')"']
    ht += ["", "<IfModule mod_headers.c>"]
    ht += [f'  Header always set {k} "{v}"' for k, v in SECURITY_HEADERS]
    ht += [f'  Header always set Content-Security-Policy "{csp()}"', "</IfModule>", ""]

    nl = ["# Netlify", "[[headers]]", '  for = "/*"', "  [headers.values]"]
    nl += [f'    {k} = "{v}"' for k, v in SECURITY_HEADERS]
    nl += [f'    Content-Security-Policy = "{csp()}"', ""]
    hide = [p + "*" if p.endswith("/") else p for p in PRIVATE]
    for p in hide:
        nl += ["[[redirects]]", f'  from = "{p}"', '  to = "/404.html"', "  status = 404",
               "  force = true", ""]
    for s, d in REDIRECTS:
        nl += ["[[redirects]]", f'  from = "{s}"', f'  to = "{d}"', "  status = 301",
               "  force = true", ""]
    nl += ["[[redirects]]", '  from = "/*"', '  to = "/404.html"', "  status = 404", ""]

    simple = ([f"{p}  /404.html  404!" for p in hide] + [f"{s}  {d}  301" for s, d in REDIRECTS]
              + ["/*  /404.html  404", ""])
    return "\n".join(ht), "\n".join(nl), "\n".join(simple)
