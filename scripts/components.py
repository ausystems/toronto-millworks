#!/usr/bin/env python3
"""
Every reusable block on the site, as small functions that return HTML.

Conventions
  * Root-relative URLs everywhere, so a page works at any depth, including the
    404 served under an arbitrary missing path.
  * One <h1> per page lives in the page header; sections open with an <h2>;
    items inside a section use <h3>. The audit enforces it.
  * Imagery is registered as it is used, so the sitemap's image entries are
    exactly the images on the page.
"""
import glob
import html
import json
import os
import re

import drawings
import maps
from build_library import PLATES as LIB
from guides import GUIDES
from locations import LOCATIONS, REGION_ORDER
from seo import ADDR_LINE, MAP_DIRECTIONS, MAP_EMBED
from site_content import PROCESS, SERVICES, SITE

E = lambda s: html.escape(str(s), quote=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LQIP = json.load(open(os.path.join(ROOT, "scripts", "data", "lqip.json")))

ARROW = ('<svg viewBox="0 0 14 14" fill="none" aria-hidden="true" focusable="false">'
         '<path d="M4 10L10 4M10 4H4.9M10 4v5.1" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')

def cx(*names):
    """Join class names, skipping empties."""
    return " ".join(n for n in names if n)


# ── image registry, read back by the page builder for the image sitemap ─────
IMAGES = []


def reset_images():
    IMAGES.clear()


def _widths(name, kind):
    found = glob.glob(os.path.join(ROOT, "assets/img/lib", f"{name}-{kind}-*.webp"))
    return sorted(int(re.search(r"-(\d+)\.webp$", f).group(1)) for f in found)


# ══════════════════════════════════════════════════════════════════════════════
#  atoms
# ══════════════════════════════════════════════════════════════════════════════
def pill(text, tone="line"):
    return f'<span class="pill pill--{tone}"><i class="dot" aria-hidden="true"></i>{E(text)}</span>'


def btn(href, label, kind="brass", lg=False, attrs=""):
    return (f'<a class="btn btn--{kind}{" btn--lg" if lg else ""}" href="{E(href)}"{attrs}>'
            f'<span>{E(label)}</span><i class="btn__arrow" aria-hidden="true">{ARROW}</i></a>')


def lnk(href, label, cls=""):
    """A text link that underlines itself from the left and nudges its arrow."""
    return (f'<a class="{cx("lnk", cls)}" href="{E(href)}"><span>{E(label)}</span>'
            f'<i aria-hidden="true">{ARROW}</i></a>')


def ext(href, label, cls="lnk"):
    return (f'<a class="{cls}" href="{E(href)}" target="_blank" rel="noopener noreferrer">'
            f'<span>{E(label)}</span><i aria-hidden="true">{ARROW}</i>'
            '<span class="sr-only"> (opens in a new tab)</span></a>')


def crumbs(trail):
    if not trail:
        return ""
    li = ['<li><a href="/">Home</a></li>']
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            li.append(f'<li><span aria-current="page">{E(name)}</span></li>')
        else:
            li.append(f'<li><a href="/{path.strip("/")}/">{E(name)}</a></li>')
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(li) + '</ol></nav>'


def sec_head(h2, hid, eyebrow=None, lede=None, cls=""):
    out = [f'<div class="{cx("sh", cls)}">']
    if eyebrow:
        out.append(pill(eyebrow))
    out.append(f'<h2 class="sh__t" id="{hid}">{h2}</h2>')
    if lede:
        out.append(f'<p class="sh__l">{E(lede)}</p>')
    out.append('</div>')
    return "".join(out)


# ══════════════════════════════════════════════════════════════════════════════
#  imagery
# ══════════════════════════════════════════════════════════════════════════════
def figure(name, wide="100vw", tall="100vw", cls="", eager=False, caption=None, force=None):
    """A plate with a different composition per breakpoint, a blur-up placeholder,
    and intrinsic dimensions so it never shifts layout.

    force="tall" or "wide" pins one composition at every size (galleries)."""
    if name not in LIB:
        raise SystemExit(f"unknown plate {name}")
    alt = LIB[name][4]
    w, t = _widths(name, "wide"), _widths(name, "tall")
    if not w or not t:
        raise SystemExit(f"missing library plate: {name}")
    ss = lambda kind, ws: ", ".join(f"/assets/img/lib/{name}-{kind}-{x}.webp {x}w" for x in ws)
    load = ('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"')
    lq = LQIP.get(f"{name}-wide") or LQIP.get(f"{name}-tall")
    klass = ("fig " + cls).strip()
    if force == "tall":
        src = (f'<img src="/assets/img/lib/{name}-tall-{t[0]}.webp" srcset="{ss("tall", t)}" '
               f'sizes="{tall}" width="{t[-1]}" height="{round(t[-1] * 5 / 4)}" {load} decoding="async" '
               f'alt="{E(alt)}">')
        klass += " fig--t"
        IMAGES.append((f"/assets/img/lib/{name}-tall-{t[-1]}.webp", alt))
    elif force == "wide":
        src = (f'<img src="/assets/img/lib/{name}-wide-{w[0]}.webp" srcset="{ss("wide", w)}" '
               f'sizes="{wide}" width="{w[-1]}" height="{round(w[-1] * 2 / 3)}" {load} decoding="async" '
               f'alt="{E(alt)}">')
        klass += " fig--w"
        IMAGES.append((f"/assets/img/lib/{name}-wide-{w[-1]}.webp", alt))
    else:
        src = (f'<picture><source media="(min-width: 760px)" srcset="{ss("wide", w)}" sizes="{wide}">'
               f'<img src="/assets/img/lib/{name}-tall-{t[0]}.webp" srcset="{ss("tall", t)}" '
               f'sizes="{tall}" width="{t[-1]}" height="{round(t[-1] * 5 / 4)}" {load} decoding="async" '
               f'alt="{E(alt)}"></picture>')
        IMAGES.append((f"/assets/img/lib/{name}-wide-{w[-1]}.webp", alt))
    cap = f'<figcaption class="fig__c">{E(caption)}</figcaption>' if caption else ""
    return f'<figure class="{klass}" style="--lq:url({lq})">{src}{cap}</figure>'


def sheet(key, caption=None, cls="", uid=""):
    """A shop drawing set as a figure."""
    cap = f'<figcaption class="dwfig__c">{E(caption)}</figcaption>' if caption else ""
    return f'<figure class="{cx("dwfig", cls)}">{drawings.drawing(key, uid=uid)}{cap}</figure>'


# ══════════════════════════════════════════════════════════════════════════════
#  page header
# ══════════════════════════════════════════════════════════════════════════════
def page_header(page, visual=None, actions=None, note=None, tone=""):
    chip = pill(page["label"]) if page.get("label") else ""
    act = f'<div class="ph__a">{actions}</div>' if actions else ""
    met = f'<p class="ph__note">{E(note)}</p>' if note else ""
    vis = f'<div class="ph__v">{visual}</div>' if visual else ""
    return (f'<header class="{cx("ph", "ph--split" if visual else "", tone)}">'
            + '<div class="shell">' + crumbs(page.get("crumbs")) + '<div class="ph__g"><div class="ph__main">'
            + chip + f'<h1 class="ph__t">{E(page["h1"])}</h1>'
            + f'<p class="ph__l">{E(page["lede"])}</p>' + act + met + '</div>' + vis
            + '</div></div></header>')


def bleed(name, eager=False):
    return '<div class="bleed">' + figure(name, cls="fig--bleed", eager=eager) + '</div>'


def say(text, cls=""):
    return (f'<section class="{cx("say", cls)}"><div class="shell"><p class="say__t">{E(text)}</p>'
            '</div></section>')


# ══════════════════════════════════════════════════════════════════════════════
#  sections
# ══════════════════════════════════════════════════════════════════════════════
def builds(items, h2, hid, eyebrow=None, lede=None, intro=None):
    li = "".join(f'<li class="bld__i"><h3 class="bld__t">{E(t)}</h3><p class="bld__d">{E(d)}</p></li>'
                 for t, d in items)
    intro_html = f'<p class="bld__intro">{E(intro)}</p>' if intro else ""
    return (f'<section class="bld" aria-labelledby="{hid}"><div class="shell bld__g">'
            f'<div class="bld__head">{sec_head(h2, hid, eyebrow, lede)}{intro_html}</div>'
            f'<ul class="bld__list">{li}</ul></div></section>')


def process(stages, h2, hid, lede=None, eyebrow="Process", sid="process"):
    """Stages read down the right; their drawings hold still on the left and change
    as each stage reaches the middle of the screen. On a phone the drawing rides
    along at the top of the section."""
    keys = ["measure", "draw", "build", "install"]
    sheets = "".join(
        f'<div class="prc__sheet{" is-on" if i == 0 else ""}" data-step="{i}">'
        f'{drawings.drawing(keys[i % 4], uid=f"-{sid}")}</div>' for i in range(len(stages)))
    items = "".join(
        f'<li class="prc__i{" is-on" if i == 0 else ""}" data-step="{i}">'
        f'<h3 class="prc__t">{E(t)}</h3><p class="prc__d">{E(d)}</p></li>'
        for i, st in enumerate(stages) for t, d in [st[:2]])
    return (f'<section class="prc" id="{sid}" aria-labelledby="{hid}"><div class="shell">'
            + sec_head(h2, hid, eyebrow, lede)
            + f'<div class="prc__g"><div class="prc__stage" aria-hidden="true">{sheets}</div>'
            f'<ol class="prc__list">{items}</ol></div></div></section>')


def index_list(items, h2, hid, eyebrow=None, lede=None, cls=""):
    """A Swiss index rather than a card grid. Desktop shows the hovered row's
    drawing in a standing panel; phones get a photo thumbnail in each row.

    items: dicts with href, title, text, drawing, plate"""
    rows, peeks = [], []
    for i, it in enumerate(items):
        thumb = ""
        if it.get("plate"):
            n = it["plate"]
            t = _widths(n, "tall")
            thumb = (f'<span class="idx__th" aria-hidden="true"><img src="/assets/img/lib/{n}-tall-{t[0]}.webp" '
                     f'width="{t[0]}" height="{round(t[0] * 5 / 4)}" loading="lazy" decoding="async" alt=""></span>')
        rows.append(
            f'<li class="idx__i" data-peek="{i}"><a class="idx__a" href="{E(it["href"])}">'
            f'{thumb}'
            f'<h3 class="idx__t">{E(it["title"])}</h3><p class="idx__d">{E(it["text"])}</p>'
            f'<i class="idx__go" aria-hidden="true">{ARROW}</i></a></li>')
        if it.get("drawing"):
            peeks.append(f'<div class="idx__pk{" is-on" if i == 0 else ""}" data-peek="{i}">'
                         f'{drawings.drawing(it["drawing"], uid=f"-pk{hid}{i}")}</div>')
    peek = f'<div class="idx__peek" aria-hidden="true">{"".join(peeks)}</div>' if peeks else ""
    return (f'<section class="{cx("idx", cls)}" aria-labelledby="{hid}">'
            + f'<div class="shell">{sec_head(h2, hid, eyebrow, lede)}'
            f'<div class="idx__g{" idx__g--peek" if peek else ""}"><ul class="idx__list">{"".join(rows)}</ul>'
            f'{peek}</div></div></section>')


def service_items(slugs=None, drawing=True):
    from site_content import SERVICE_BY_SLUG
    out = []
    for s in (SERVICE_BY_SLUG[x] for x in slugs) if slugs else SERVICES:
        out.append({"href": f"/services/{s['slug']}/", "title": s["nav"], "text": s["blurb"],
                    "drawing": s["drawing"] if drawing else None,
                    "plate": s["plates"][0]})
    return out


def gallery(names, h2=None, hid=None, eyebrow=None, lede=None, captions=True, cls=""):
    """An editorial wall in a four-beat rhythm: wide, tall, tall, wide. Each beat
    has its own column span and offset, so the wall staggers without gaps."""
    figs = []
    for i, n in enumerate(names):
        beat = i % 4
        tall = beat in (1, 2)
        figs.append(figure(n, wide="(min-width: 900px) 52vw, 100vw",
                           tall="(min-width: 900px) 30vw, 100vw",
                           cls=f"gal__f gal__f--p{beat}", force="tall" if tall else "wide",
                           caption=LIB[n][4] if captions else None))
    head = sec_head(h2, hid, eyebrow, lede) if h2 else ""
    lab = f' aria-labelledby="{hid}"' if h2 else ""
    return (f'<section class="{cx("gal", cls)}"{lab}>'
            + f'<div class="shell">{head}<div class="gal__g">{"".join(figs)}</div></div></section>')


def pair(a, b, caption_a=None, caption_b=None):
    return ('<section class="pair"><div class="shell pair__g">'
            + figure(a, wide="52vw", cls="pair__a", caption=caption_a)
            + figure(b, wide="38vw", cls="pair__b", caption=caption_b)
            + '</div></section>')


def figsay(plate, h2, hid, body, flip=False, extra=""):
    return (f'<section class="fs{" fs--flip" if flip else ""}" aria-labelledby="{hid}">'
            '<div class="shell fs__g">' + figure(plate, wide="50vw", cls="fs__f")
            + f'<div class="fs__t"><h2 class="fs__h" id="{hid}">{E(h2)}</h2>'
            f'<p class="fs__p">{E(body)}</p>{extra}</div></div></section>')


SWATCH = [("paint", "#ECE8E1"), ("white oak", "#C8A27A"), ("oak", "#C8A27A"),
          ("walnut", "#5A3D2B"), ("cherry", "#8E4B35"), ("veneer", "#B58A5C"),
          ("poplar", "#D9CDB2"), ("mdf", "#E3DED6"), ("hardwood", "#9C7149"),
          ("laminate", "#D6D2CA"), ("solid surface", "#F1EEE8"), ("quartz", "#E9E6E1"),
          ("stone", "#CFCAC2"), ("tops", "#CFCAC2"), ("metal", "#8B8A86"), ("hardware", "#8B8A86"),
          ("acoustic", "#7B6A58"), ("lighting", "#C08A3C"), ("finish", "#2A2621"),
          ("profile", "#E5E0D8"), ("cabinetry", "#D8CBB8"), ("trim", "#EEEAE4"),
          ("surfaces", "#CFCAC2")]


def _swatch(name):
    n = name.lower()
    for k, c in SWATCH:
        if k in n:
            return c
    return "#D8CBB8"


def materials(items, h2, hid, eyebrow="Materials", lede=None):
    li = "".join(
        f'<li class="mat__i"><span class="mat__sw" style="--sw:{_swatch(t)}" aria-hidden="true"></span>'
        f'<h3 class="mat__t">{E(t)}</h3><p class="mat__d">{E(d)}</p></li>' for t, d in items)
    return (f'<section class="mat" aria-labelledby="{hid}"><div class="shell">'
            + sec_head(h2, hid, eyebrow, lede) + f'<ul class="mat__list">{li}</ul></div></section>')


def nearby(places, h2, hid, lede=None):
    li = "".join(
        f'<li><a class="near__a" href="/service-areas/{p["slug"]}/"><span class="near__n">'
        f'Custom millwork in {E(p["name"])}</span><i aria-hidden="true">{ARROW}</i></a></li>'
        for p in places)
    return (f'<section class="near" aria-labelledby="{hid}"><div class="shell">'
            + sec_head(h2, hid, "Nearby", lede) + f'<ul class="near__list">{li}</ul></div></section>')


def area_links(places, h2, hid, lede=None, label=None, all_link=True):
    """Location links with descriptive anchors, used on service pages."""
    label = label or (lambda p: f"Custom millwork in {p['name']}")
    li = "".join(f'<li><a href="/service-areas/{p["slug"]}/">{E(label(p))}</a></li>' for p in places)
    more = (f'<p class="arl__more">{lnk("/service-areas/", "Every town and city we serve")}</p>'
            if all_link else "")
    return (f'<section class="arl" aria-labelledby="{hid}"><div class="shell arl__g">'
            + sec_head(h2, hid, "Where we work", lede) + f'<div><ul class="arl__list">{li}</ul>{more}</div>'
            '</div></section>')


def region_index(prefix_heading=3):
    """Every place grouped by region, nearest first."""
    groups = []
    for region in REGION_ORDER:
        places = sorted((p for p in LOCATIONS if p["region"] == region), key=lambda p: p["km"])
        li = "".join(
            f'<li><a class="rx__a" href="/service-areas/{p["slug"]}/" data-slug="{p["slug"]}">'
            f'<span class="rx__n">{E(p["name"])}</span></a></li>'
            for p in places)
        groups.append(f'<div class="rx__g"><h{prefix_heading} class="rx__h">{E(region)}</h{prefix_heading}>'
                      f'<ul class="rx__list">{li}</ul></div>')
    return '<div class="rx">' + "".join(groups) + '</div>'


def areas_section(h2, hid, lede, teaser=False):
    if teaser:
        top = ["toronto", "mississauga", "brampton", "vaughan", "oakville", "hamilton", "markham",
               "richmond-hill", "burlington", "kitchener", "barrie", "st-catharines"]
        from locations import BY_SLUG
        li = "".join(f'<li><a href="/service-areas/{s}/">{E(BY_SLUG[s]["name"])}</a></li>' for s in top)
        side = (f'<ul class="arx__top">{li}</ul>'
                f'<p class="arx__more">{btn("/service-areas/", "See every area", "paper")}</p>')
    else:
        side = region_index()
    return (f'<section class="arx{" arx--teaser" if teaser else ""}" aria-labelledby="{hid}">'
            f'<div class="shell">{sec_head(h2, hid, "Service area", lede)}'
            f'<div class="arx__g"><div class="arx__map">{maps.hub_map()}'
            f'<p class="arx__src">Shorelines © OpenStreetMap contributors</p></div><div class="arx__side">{side}</div></div></div></section>')


# ══════════════════════════════════════════════════════════════════════════════
#  questions and the shop
# ══════════════════════════════════════════════════════════════════════════════
def _faq_rows(items):
    return "".join(
        '<details class="faq__row"><summary class="faq__q">'
        f'<h3 class="faq__q-t">{E(q)}</h3><span class="faq__ico" aria-hidden="true"></span>'
        f'</summary><div class="faq__panel"><p class="faq__a">{E(a)}</p></div></details>'
        for q, a in items)


def faq(items=None, groups=None, h2="Frequently<br> asked", note=None, map_after=True, hid="faq-h",
        more=True):
    """Native <details>, so the answers are in the DOM and open without script."""
    note = note or ("Straight answers on cost, lead time and how a job actually runs. If "
                    "something is not covered here, ask and we will answer it the same way.")
    if groups:
        body = "".join(f'<div class="faq__grp"><p class="faq__gh">{E(g)}</p>'
                       f'<div class="faq__list">{_faq_rows(rows)}</div></div>' for g, rows in groups)
    else:
        body = f'<div class="faq__list">{_faq_rows(items)}</div>'
    return (f'<section class="faq" aria-labelledby="{hid}"><div class="shell faq__grid">'
            f'<div class="faq__aside">{pill("Questions")}<h2 class="faq__h" id="{hid}">{h2}</h2>'
            f'<p class="faq__note">{E(note)}</p>{lnk("/faq/", "Every question we get asked") if more else ""}</div>'
            f'<div class="faq__body">{body}</div></div></section>'
            + (shop_map() if map_after else ""))


def shop_map(hid="map-h"):
    return (f'<section class="map" aria-labelledby="{hid}"><div class="shell map__grid">'
            f'<div class="map__aside">{pill("The shop")}'
            f'<h2 class="map__h" id="{hid}">Come and see<br> the bench.</h2>'
            '<p class="map__note">Drawings, samples and work in progress all live in one building '
            'near Pearson. Visits are by appointment so someone is free to walk you through what '
            'is on the floor.</p>'
            f'<address class="map__addr"><span>{E(SITE["street"])}</span>'
            f'<span>{E(SITE["locality"])}, {E(SITE["region"])} {E(SITE["postal"])}</span>'
            '<span>Canada</span></address>'
            '<div class="map__acts">'
            + btn(MAP_DIRECTIONS, "Get directions", attrs=' target="_blank" rel="noopener noreferrer"')
            + lnk("/contact/?visit=1", "Book a shop visit")
            + '</div></div>'
            '<div class="map__frame"><iframe class="map__embed" src="' + E(MAP_EMBED) + '" '
            f'title="Map showing {E(SITE["name"])} at {E(ADDR_LINE)}" loading="lazy" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
            '</div></section>')


# ══════════════════════════════════════════════════════════════════════════════
#  conversion
# ══════════════════════════════════════════════════════════════════════════════
QUOTE_TYPES = [("custom-kitchens", "A kitchen"), ("cabinetry-and-built-ins", "Built-ins"),
               ("architectural-millwork", "Panelling or trim"),
               ("restaurant-and-bar-millwork", "A restaurant or bar"),
               ("office-millwork", "An office"), ("commercial-fit-outs", "A commercial package"),
               ("interior-renovation", "A renovation")]


def quote_starter(h2="Tell us about the room.", text=None, area=None, hid="qs-h", lead=None):
    """The closing ask on every page: one tap on what you are planning opens the
    quote form with that answer already filled in."""
    text = text or ("Send drawings, a photo or just the dimensions. We come back with a "
                    "measured quote, not a per foot guess.")
    q = f"&area={area}" if area else ""
    chips = "".join(f'<li><a class="chip" href="/contact/?type={k}{q}#quote">{E(v)}</a></li>'
                    for k, v in QUOTE_TYPES)
    lead_html = f'<p class="qs__lead">{E(lead)}</p>' if lead else ""
    return (f'<section class="qs" aria-labelledby="{hid}"><div class="shell qs__g">'
            f'<div class="qs__head">{lead_html}<h2 class="qs__t" id="{hid}">{E(h2)}</h2>'
            f'<p class="qs__l">{E(text)}</p></div>'
            '<div class="qs__side"><p class="qs__k" id="' + hid + '-k">What are you planning?</p>'
            f'<ul class="qs__chips" aria-labelledby="{hid}-k">{chips}</ul>'
            + btn(f"/contact/{'?area=' + area if area else ''}#quote", "Start a project", lg=True)
            + '</div></div></section>')


def quote_form():
    """Works without script as a single form that composes an email. With script it
    steps through three short screens, validates as you go, and sends to the form
    endpoint when one is configured."""
    from locations import BY_SLUG
    opts_type = "".join(
        f'<label class="opt"><input type="radio" name="type" value="{k}" required>'
        f'<span>{E(v)}</span></label>' for k, v in QUOTE_TYPES + [("other", "Something else")])
    region_opts = []
    for region in REGION_ORDER:
        o = "".join(f'<option value="{p["slug"]}">{E(p["name"])}</option>'
                    for p in sorted((p for p in LOCATIONS if p["region"] == region), key=lambda p: p["name"]))
        region_opts.append(f'<optgroup label="{E(region)}">{o}</optgroup>')
    action = SITE["form_endpoint"] or f"mailto:{SITE['email']}"
    enctype = "multipart/form-data" if SITE["form_endpoint"] else "text/plain"

    def sel(name, label, options, hint=None, required=False):
        h = f'<span class="fld__h" id="{name}-h">{E(hint)}</span>' if hint else ""
        desc = f' aria-describedby="{name}-h"' if hint else ""
        return (f'<div class="fld"><label class="fld__l" for="{name}">{E(label)}</label>{h}'
                f'<div class="fld__sel"><select id="{name}" name="{name}"{desc}{" required" if required else ""}>'
                f'{options}</select></div></div>')

    when = "".join(f'<option value="{v}">{v}</option>' for v in
                   ("As soon as possible", "In one to three months", "In three to six months",
                    "Later than that", "Not sure yet"))
    stage = "".join(f'<option value="{v}">{v}</option>' for v in
                    ("Just an idea so far", "Designer or architect drawings exist",
                     "Under construction now", "Replacing existing millwork"))
    budget = "".join(f'<option value="{v}">{v}</option>' for v in
                     ("Prefer not to say", "Under $25,000", "$25,000 to $50,000",
                      "$50,000 to $100,000", "Over $100,000"))
    return f'''<form class="qf" id="quote" action="{E(action)}" method="post" enctype="{enctype}" novalidate data-endpoint="{E(SITE['form_endpoint'])}" data-email="{E(SITE['email'])}">
<div class="qf__progress" aria-hidden="true"><span class="qf__bar"></span></div>
<p class="qf__count" aria-live="polite"><span class="qf__now">Step 1</span> of 3</p>
<fieldset class="qf__step is-on" data-step="0">
<legend class="qf__legend">What are you planning?</legend>
<div class="opts" role="radiogroup" aria-required="true">{opts_type}</div>
<p class="fld__err" data-for="type" hidden>Choose the closest match. You can explain the rest later.</p>
</fieldset>
<fieldset class="qf__step" data-step="1">
<legend class="qf__legend">Where, and when?</legend>
{sel("area", "Town or city", '<option value="">Choose a location</option>' + "".join(region_opts) + '<option value="other">Somewhere else in Ontario</option>', required=True)}
<p class="fld__err" data-for="area" hidden>Choose where the work is, or pick somewhere else.</p>
{sel("timing", "When would you like it finished?", when)}
{sel("stage", "Where is the project now?", stage)}
{sel("budget", "Budget, if you have one", budget, hint="Optional. It helps us suggest materials that fit.")}
</fieldset>
<fieldset class="qf__step" data-step="2">
<legend class="qf__legend">How do we reach you?</legend>
<div class="fld"><label class="fld__l" for="name">Name</label><input class="fld__i" id="name" name="name" autocomplete="name" required maxlength="120"><p class="fld__err" data-for="name" hidden>Please add your name.</p></div>
<div class="fld"><label class="fld__l" for="email">Email</label><input class="fld__i" id="email" name="email" type="email" autocomplete="email" required maxlength="200" inputmode="email"><p class="fld__err" data-for="email" hidden>That email address does not look complete.</p></div>
<div class="fld"><label class="fld__l" for="phone">Phone <span class="fld__opt">optional</span></label><input class="fld__i" id="phone" name="phone" type="tel" autocomplete="tel" maxlength="40" inputmode="tel"></div>
<div class="fld"><label class="fld__l" for="message">About the room <span class="fld__opt">optional</span></label><textarea class="fld__i fld__ta" id="message" name="message" rows="4" maxlength="4000" aria-describedby="message-h"></textarea><span class="fld__h" id="message-h">Rough dimensions, what is there now, the finish you have in mind. Photos and drawings can follow by email.</span></div>
<div class="hp" aria-hidden="true"><label for="company_site">Leave this empty</label><input id="company_site" name="company_site" tabindex="-1" autocomplete="off"></div>
<input type="hidden" name="visit" value="">
<p class="qf__legal">We use these details only to reply about your project. <a href="/privacy-policy/">Privacy policy</a></p>
</fieldset>
<div class="qf__nav">
<button class="qf__back" type="button" hidden>Back</button>
<button class="btn btn--brass btn--lg qf__next" type="button"><span>Continue</span><i class="btn__arrow" aria-hidden="true">{ARROW}</i></button>
<button class="btn btn--brass btn--lg qf__send" type="submit"><span>Send the details</span><i class="btn__arrow" aria-hidden="true">{ARROW}</i></button>
</div>
<div class="qf__done" tabindex="-1" hidden>
<h2 class="qf__done-t">Thank you. It is on its way.</h2>
<p class="qf__done-p" data-mail-copy>Your email app should have opened with everything filled in. If it did not, send the summary below to <a href="mailto:{E(SITE['email'])}">{E(SITE['email'])}</a>.</p>
<pre class="qf__sum" hidden></pre>
<button class="lnk qf__copy" type="button" hidden><span>Copy the summary</span></button>
</div>
</form>'''


# ══════════════════════════════════════════════════════════════════════════════
#  articles
# ══════════════════════════════════════════════════════════════════════════════
def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def article(guide):
    """Guide body: a standing contents list beside the sections. Returns html and words."""
    toc = "".join(f'<li><a href="#{_slug(t)}">{E(t)}</a></li>' for t, _ in guide["sections"])
    words = 0
    secs = []
    for i, (title, blocks) in enumerate(guide["sections"]):
        parts = [f'<h2 class="art__h" id="{_slug(title)}">{E(title)}</h2>']
        for b in blocks:
            if isinstance(b, str):
                parts.append(f'<p>{E(b)}</p>')
                words += len(b.split())
            elif b[0] == "ul":
                parts.append('<ul>' + "".join(f'<li>{E(x)}</li>' for x in b[1]) + '</ul>')
                words += sum(len(x.split()) for x in b[1])
            elif b[0] == "table":
                head = "".join(f'<th scope="col">{E(h)}</th>' for h in b[1])
                rows = "".join('<tr>' + "".join(
                    (f'<th scope="row">{E(c)}</th>' if j == 0 else f'<td>{E(c)}</td>')
                    for j, c in enumerate(r)) + '</tr>' for r in b[2])
                parts.append(f'<div class="art__tw" tabindex="0" role="region" aria-label="{E(title)} table">'
                             f'<table class="art__tb"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        if i == 1 and guide.get("drawing"):
            parts.append(sheet(guide["drawing"], caption=drawings.alt(guide["drawing"]), cls="art__fig",
                               uid="-art"))
        secs.append('<section class="art__s">' + "".join(parts) + '</section>')
    html_ = (f'<div class="shell art"><aside class="art__toc" aria-label="On this page">'
             f'<p class="art__toc-h">On this page</p><ol>{toc}</ol>'
             f'<div class="art__progress" aria-hidden="true"><span></span></div></aside>'
             f'<div class="art__body">{"".join(secs)}</div></div>')
    return html_, words


# ══════════════════════════════════════════════════════════════════════════════
#  chrome
# ══════════════════════════════════════════════════════════════════════════════
def nav(active=""):
    def a(href, label, key):
        cur = ' class="is-active" aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{E(label)}</a>'
    sub = "".join(
        f'<li><a class="nsub__a" href="/services/{s["slug"]}/" data-peek="{i}">'
        f'<span class="nsub__t">{E(s["nav"])}</span><span class="nsub__d">{E(s["blurb"])}</span></a></li>'
        for i, s in enumerate(SERVICES))
    return f'''<header class="nav-wrap">
<nav class="nav" aria-label="Primary">
<a class="brand" href="/" aria-label="Toronto Millworks, home">
<span class="brand__mark" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="9.5" fill="currentColor"/><path d="M7.5 22.6h17M10.4 18.9h14.1M13.3 15.2h11.2M16.2 11.5h8.3" stroke="#C08A3C" stroke-width="1.7" stroke-linecap="round"/></svg></span>
<span class="brand__name">Toronto Millworks Logo</span>
</a>
<div class="nav__menu" id="nav-menu">
<ul class="nav__links">
<li>{a("/", "Home", "home")}</li>
<li>{a("/about/", "About Us", "about")}</li>
<li class="has-sub">{a("/services/", "Services", "services")}<button class="nav__caret" type="button" aria-expanded="false" aria-controls="nav-sub"><span class="sr-only">Show services</span><i aria-hidden="true"></i></button>
<div class="nsub" id="nav-sub">
<div class="nsub__in">
<ul class="nsub__list">{sub}</ul>
<div class="nsub__aside">
<p class="nsub__k">Every piece is measured on site, drawn, and built in our shop.</p>
<a class="nsub__more" href="/services/">All services</a>
<a class="nsub__more" href="/service-areas/">Where we work</a>
<a class="nsub__more" href="/guides/">Guides</a>
</div>
</div>
</div>
</li>
<li>{a("/projects/", "Projects", "projects")}</li>
<li>{a("/contact/", "Contact", "contact")}</li>
</ul>
{btn("/contact/#quote", "Get a Quote").replace('class="btn btn--brass"', 'class="btn btn--brass nav__cta"')}
</div>
<button class="nav__burger" type="button" aria-expanded="false" aria-controls="nav-menu"><span class="sr-only">Menu</span><i aria-hidden="true"></i><i aria-hidden="true"></i></button>
</nav>
</header>'''


def footer(year):
    svc = " ".join(f'<a href="/services/{s["slug"]}/">{E(s["nav"])}</a>' for s in SERVICES)
    top_places = ["toronto", "mississauga", "brampton", "vaughan", "oakville", "burlington", "hamilton",
                  "markham", "richmond-hill", "pickering", "kitchener", "barrie"]
    from locations import BY_SLUG
    areas = " ".join(f'<a href="/service-areas/{s}/">{E(BY_SLUG[s]["name"])}</a>' for s in top_places)
    phone = (f'<p><a href="tel:{E(SITE["phone"])}">{E(SITE["phone"])}</a></p>' if SITE["phone"] else "")
    idx = [("/services/", "Services"), ("/projects/", "Projects"), ("/about/", "About Us"),
           ("/service-areas/", "Service Areas"), ("/guides/", "Guides"), ("/faq/", "FAQ"),
           ("/contact/", "Contact")]
    rows = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in idx)
    cta = btn("/contact/#quote", "Start a project", "paper", lg=True)
    return f'''<footer class="foot">
<div class="foot__main">
<div class="foot__lead">
<h2 class="foot__title">Bring us a room.</h2>
{cta}
</div>
<div class="foot__aside">
<ul class="foot__index">{rows}</ul>
<div class="foot__reach">
<address><p>{E(SITE["street"])}<br>{E(SITE["locality"])}, {E(SITE["region"])} {E(SITE["postal"])}</p></address>
<div><p><a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></p>{phone}</div>
</div>
</div>
</div>
<nav class="foot__links" aria-label="Services and areas">
<p><span class="foot__label">Services</span> {svc}</p>
<p><span class="foot__label">Areas</span> {areas} <a href="/service-areas/">Every area</a></p>
</nav>
<p class="foot__legal">© {year} Toronto Millworks · <a href="/privacy-policy/">Privacy</a></p>
<div class="foot__mark">
<svg class="foot__wordmark foot__wordmark--wide" viewBox="0 26 1120 76" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Toronto Millworks"><text x="0" y="100" textLength="1120" lengthAdjust="spacingAndGlyphs">TORONTO MILLWORKS</text></svg>
<svg class="foot__wordmark foot__wordmark--stack" viewBox="0 26 602 164" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Toronto Millworks"><text x="0" y="100" textLength="498" lengthAdjust="spacingAndGlyphs">TORONTO</text><text x="0" y="188" textLength="602" lengthAdjust="spacingAndGlyphs">MILLWORKS</text></svg>
</div>
</footer>'''


def dock():
    """A quiet quote bar for phones, shown once the first screen has passed."""
    second = (f'<a class="dock__b" href="tel:{E(SITE["phone"])}">Call</a>' if SITE["phone"] else
              f'<a class="dock__b" href="mailto:{E(SITE["email"])}">Email</a>')
    return (f'<div class="dock" data-dock><a class="dock__q" href="/contact/#quote"><span>Get a quote</span>'
            f'<i aria-hidden="true">{ARROW}</i></a>{second}</div>')
