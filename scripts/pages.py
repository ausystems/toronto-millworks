#!/usr/bin/env python3
"""
Page compositions. Each function returns one page dict for the builder:

    path, title, desc, keywords, h1, lede, label, crumbs, body, faq, service,
    place, guide, itemlist, page_type, og (card spec), images, changefreq,
    priority, body_class, active (nav), preload, search_group

Copy lives in site_content.py, locations.py and guides.py; this file only
decides what goes where and in what order.
"""
import html
import os

import components as C
import drawings
import maps
from build_library import PLATES as LIB
from guides import GUIDES, GUIDE_BY_SLUG
from locations import BY_SLUG, LOCATIONS, REGION_ORDER, nearest
from seo import MAP_DIRECTIONS
from site_content import (FAQ, FAQ_GROUPS, PROCESS, SERVICE_BY_SLUG, SERVICES, SITE,
                          faq_pick)

E = lambda s: html.escape(str(s), quote=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_MAIN = (open(os.path.join(ROOT, "src", "partials", "home-main.html")).read()
             .replace('<main id="main">', "").replace("</main>", ""))


def _fit(cands, lo, hi):
    """First candidate whose length lands in [lo, hi]; the audit enforces the same."""
    for c in cands:
        if lo <= len(c) <= hi:
            return c
    raise SystemExit(f"nothing fits {lo}-{hi}: {[ (len(c), c) for c in cands ]}")


def _page(**kw):
    kw.setdefault("images", [])
    return kw


# ══════════════════════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════════════════════
def home():
    C.reset_images()
    body = (HOME_MAIN
            + C.index_list(C.service_items(), "What we make", "svc-h", "Services",
                           "Seven kinds of work, one shop, the same way of building every one of "
                           "them.", cls="idx--home")
            + C.process(PROCESS, "How a project runs", "prc-h",
                        "Four stages, in this order, every time. Skipping one is how filler strips "
                        "and site fixes happen.")
            + C.gallery(["frieze", "espresso", "transom", "pendants", "plinth", "shelving"],
                        "From the shop floor", "gal-h", "Work",
                        "Residential panelling and a commercial bar, photographed as built.")
            + C.areas_section("Within 120 km of the bench", "arx-h",
                              "Toronto and the region around it, from Hamilton and Niagara to Barrie "
                              "and Durham, measured, built and installed by the same team.",
                              teaser=True)
            + C.faq(faq_pick("How much does custom millwork cost?",
                             "How long does a custom millwork project take?",
                             "Do you build in your own shop?",
                             "Which areas do you serve?",
                             "Do you work on commercial projects as well as homes?",
                             "Do you provide drawings before work starts?"))
            + C.quote_starter())
    imgs = [("/assets/img/toronto-custom-millwork-coffered-ceiling-1920.webp",
             "Coffered ceiling with gilded cornice and raised wall panelling"),
            ("/assets/img/toronto-custom-cabinetry-wall-panelling-1600.webp",
             "Panelled walls, a cased archway and a wall sconce")] + C.IMAGES[:]
    return _page(
        path="/", active="home", body_class="pg-home",
        title="Custom Millwork Toronto | Cabinetry, Kitchens & Bars",
        desc=("Custom millwork and cabinetry for Toronto and the GTA: kitchens, built-ins, "
              "panelling, bars and offices, measured on site and built in our own shop."),
        keywords="custom millwork Toronto, custom cabinetry Toronto, custom kitchens Toronto, millwork company GTA",
        h1="Custom Millwork, Masterfully Crafted",
        image_alt="A panelled interior with a coffered ceiling and gilded crown moulding",
        page_type="WebPage", body=body, images=imgs,
        faq=faq_pick("How much does custom millwork cost?",
                     "How long does a custom millwork project take?",
                     "Do you build in your own shop?", "Which areas do you serve?",
                     "Do you work on commercial projects as well as homes?",
                     "Do you provide drawings before work starts?"),
        og={"kind": "photo", "img": "/assets/img/toronto-custom-millwork-coffered-ceiling-1920.webp",
            "kicker": "Toronto Millworks", "title": "Custom millwork, masterfully crafted."},
        preload=['<link rel="preload" as="image" href="/assets/img/toronto-custom-millwork-coffered-ceiling-1920.webp" '
                 'imagesrcset="/assets/img/toronto-custom-millwork-coffered-ceiling-1280.webp 1280w, '
                 '/assets/img/toronto-custom-millwork-coffered-ceiling-1920.webp 1920w, '
                 '/assets/img/toronto-custom-millwork-coffered-ceiling-2560.webp 2560w, '
                 '/assets/img/toronto-custom-millwork-coffered-ceiling-3840.webp 3840w" '
                 'imagesizes="100vw" fetchpriority="high" media="(min-width: 760px)">'],
        changefreq="weekly", priority="1.0", search_group="Home")


# ══════════════════════════════════════════════════════════════════════════════
#  SERVICES
# ══════════════════════════════════════════════════════════════════════════════
def services_hub():
    C.reset_images()
    p = {"path": "/services/", "label": "Services", "crumbs": [("Services", "services")],
         "h1": "Everything we make, made to measure.",
         "lede": ("Seven kinds of work for homes, restaurants and offices, all templated from "
                  "your walls and built in our own shop before anything reaches the room.")}
    split = ('<section class="two" aria-labelledby="two-h"><div class="shell">'
             + C.sec_head("For homes, and for businesses", "two-h", "Who we build for")
             + '<div class="two__g">'
             '<article class="two__c">' + C.figure("room", wide="46vw", cls="two__f")
             + '<h3 class="two__t">Homeowners and their designers</h3>'
             '<p class="two__p">Kitchens, built-ins, panelling and renovations for houses and condos, '
             'measured on site and drawn for your approval before anything is cut.</p>'
             + C.lnk("/services/custom-kitchens/", "Custom kitchens")
             + C.lnk("/services/cabinetry-and-built-ins/", "Cabinetry and built-ins")
             + C.lnk("/services/architectural-millwork/", "Panelling and trim") + '</article>'
             '<article class="two__c">' + C.figure("finished", wide="46vw", cls="two__f")
             + '<h3 class="two__t">Restaurants, offices and contractors</h3>'
             '<p class="two__p">Bars, counters, reception desks and full millwork packages, shop '
             'drawn for approval and installed in the window your programme allows.</p>'
             + C.lnk("/services/restaurant-and-bar-millwork/", "Restaurant and bar millwork")
             + C.lnk("/services/office-millwork/", "Office millwork")
             + C.lnk("/services/commercial-fit-outs/", "Commercial fit-outs") + '</article>'
             '</div></div></section>')
    body = (C.page_header(p, visual=C.sheet("build", cls="ph__sheet", uid="-ph"),
                          actions=C.btn("/contact/#quote", "Get a quote", lg=True)
                          + C.lnk("#process", "How a project runs"))
            + C.index_list(C.service_items(), "What we make", "svc-h", None,
                           "Choose a service to see what it includes, how it is built and what it "
                           "costs to get right.")
            + split
            + C.process(PROCESS, "How every project runs", "prc-h",
                        "Measure, draw, build, install. The order never changes, whatever the room.")
            + C.gallery(["coffer", "counter", "panel-detail", "lounge"], "Recent detail", "gal-h",
                        "Work", None)
            + C.faq(faq_pick("How do you prepare a quote?", "Is custom millwork more expensive than stock cabinets?",
                             "Do you work with designers, architects and contractors?",
                             "Can you work to a fixed opening or move-in date?"))
            + C.quote_starter())
    return _page(
        **p, active="services", body_class="pg-services",
        title="Millwork Services Toronto | Kitchens, Built-Ins & Bars",
        desc=("Custom millwork services for Toronto and the GTA: kitchens, built-ins, panelling, "
              "restaurant and bar millwork, office joinery, fit-outs and renovation."),
        keywords="millwork services Toronto, custom cabinetry services, joinery Toronto, commercial millwork GTA",
        page_type="CollectionPage", body=body, images=C.IMAGES[:],
        itemlist=[(s["nav"], f"services/{s['slug']}") for s in SERVICES],
        faq=faq_pick("How do you prepare a quote?", "Is custom millwork more expensive than stock cabinets?",
                     "Do you work with designers, architects and contractors?",
                     "Can you work to a fixed opening or move-in date?"),
        og={"kind": "drawing", "drawing": "build", "kicker": "Services",
            "title": "Everything we make, made to measure."},
        changefreq="monthly", priority="0.9", search_group="Services")


TOP_AREAS = ["toronto", "mississauga", "brampton", "vaughan", "oakville", "markham",
             "richmond-hill", "burlington", "hamilton", "etobicoke", "north-york", "pickering"]
SERVICE_GUIDES = {
    "custom-kitchens": ["custom-cabinetry-cost", "custom-vs-semi-custom-vs-stock-cabinets",
                        "choosing-wood-for-cabinetry"],
    "cabinetry-and-built-ins": ["choosing-wood-for-cabinetry", "paint-grade-vs-stain-grade-millwork",
                                "custom-cabinetry-cost"],
    "architectural-millwork": ["paint-grade-vs-stain-grade-millwork", "how-custom-millwork-is-made",
                               "choosing-wood-for-cabinetry"],
    "restaurant-and-bar-millwork": ["planning-restaurant-bar-millwork", "how-custom-millwork-is-made",
                                    "custom-cabinetry-cost"],
    "office-millwork": ["how-custom-millwork-is-made", "planning-restaurant-bar-millwork",
                        "choosing-wood-for-cabinetry"],
    "commercial-fit-outs": ["planning-restaurant-bar-millwork", "how-custom-millwork-is-made",
                            "paint-grade-vs-stain-grade-millwork"],
    "interior-renovation": ["custom-cabinetry-cost", "custom-vs-semi-custom-vs-stock-cabinets",
                            "how-custom-millwork-is-made"],
}
SERVICE_AREA_LABEL = {
    "custom-kitchens": "Custom kitchens in {}", "cabinetry-and-built-ins": "Built-ins in {}",
    "architectural-millwork": "Panelling and trim in {}",
    "restaurant-and-bar-millwork": "Restaurant and bar millwork in {}",
    "office-millwork": "Office millwork in {}", "commercial-fit-outs": "Commercial millwork in {}",
    "interior-renovation": "Interior renovation in {}",
}


def guide_items(slugs):
    return [{"href": f"/guides/{g['slug']}/", "title": g["h1"], "text": g["lede"],
             "drawing": g["drawing"]} for g in (GUIDE_BY_SLUG[s] for s in slugs)]


def service(s):
    C.reset_images()
    path = f"/services/{s['slug']}/"
    p = {"path": path, "label": s["kind"],
         "crumbs": [("Services", "services"), (s["nav"], f"services/{s['slug']}")],
         "h1": s["h1"], "lede": s["lede"]}
    a, b, c = (s["plates"] + s["plates"])[:3]
    label = SERVICE_AREA_LABEL[s["slug"]]
    body = (C.page_header(p, visual=C.sheet(s["drawing"], cls="ph__sheet", uid="-ph"),
                          actions=C.btn(f"/contact/?type={s['slug']}#quote", "Get a quote", lg=True)
                          + C.lnk("#process", "How it comes together"))
            + C.say(s["statement"])
            + C.builds(s["builds"], "What we build", "bld-h", "Scope", None, s["intro"])
            + C.pair(a, b)
            + C.process(s["process"], "How it comes together", "prc-h",
                        "The same four stages as every piece we make, with the details that matter "
                        "for this kind of work.")
            + C.materials(s["materials"], "Materials and finishes", "mat-h", lede=(
                "Chosen for where the piece lives and how hard it works. We bring samples to the "
                "site measure."))
            + C.bleed(c)
            + C.area_links([BY_SLUG[x] for x in TOP_AREAS], f"Where we build {s['nav'].lower()}",
                           "arl-h", f"From our shop in Mississauga to every town within 120 km.",
                           label=lambda pl, lab=label: lab.format(pl["name"]))
            + C.faq(s["faq"], h2="Questions about<br> " + E(s["nav"].lower()), hid="faq-h")
            + C.index_list(C.service_items(s["related"]), "Related services", "rel-h", "Also", None,
                           cls="idx--small")
            + C.index_list(guide_items(SERVICE_GUIDES[s["slug"]]), "Read before you start", "gd-h",
                           "Guides", None, cls="idx--small idx--guides")
            + C.quote_starter(f"Planning {s['nav'].lower()}?",
                              "Send drawings, a photo or the dimensions, and we will come back with a "
                              "measured quote."))
    return _page(
        **p, active="services", body_class="pg-service", title=s["title"], desc=s["desc"],
        keywords=s["keywords"], service=s, faq=s["faq"], body=body, images=C.IMAGES[:],
        page_type="WebPage",
        og={"kind": "drawing", "drawing": s["drawing"], "kicker": s["nav"], "title": s["h1"]},
        changefreq="monthly", priority="0.9", search_group="Services")


# ══════════════════════════════════════════════════════════════════════════════
#  PROJECTS, ABOUT, CONTACT, FAQ
# ══════════════════════════════════════════════════════════════════════════════
def projects():
    C.reset_images()
    p = {"path": "/projects/", "label": "Projects", "crumbs": [("Projects", "projects")],
         "h1": "A shell, and then a room.",
         "lede": ("A commercial bar recorded from bare brick to finished room, and the "
                  "residential panelling, ceilings and casings running through the same shop.")}
    strip = ('<section class="strip" aria-labelledby="st-h"><div class="shell">'
             + C.sec_head("The fit-out, in order", "st-h", "Case study",
                          "Bare shell, lights live, the feature wall in, the counter against the "
                          "brick, and the finished room.")
             + '</div><div class="strip__r">'
             + "".join(C.figure(n, wide="34vw", tall="80vw", cls="strip__f", caption=cap) for n, cap in (
                 ("shell", "The shell as handed over"), ("lit", "Floor laid, services live"),
                 ("feature", "Feature wall and filament lighting"),
                 ("carcass", "The counter set against the brick"), ("finished", "Open for service")))
             + '</div></section>')
    case1 = ('<section class="case" aria-labelledby="c1-h"><div class="shell case__g">'
             '<div class="case__t">' + C.sec_head("A bar, built off site", "c1-h", "Commercial")
             + '<p>The counter front is reclaimed boards of varying tone, laid in a running bond so '
             'no two courses line up. The top is a single slab. Both were dry fitted in the shop '
             'before anything went to site, so the install fitted inside the window the rest of '
             'the fit-out allowed.</p>'
             + C.lnk("/services/restaurant-and-bar-millwork/", "Restaurant and bar millwork")
             + '</div>' + C.figure("counter", wide="50vw", cls="case__f") + '</div></section>')
    case2 = ('<section class="case case--flip" aria-labelledby="c2-h"><div class="shell case__g">'
             '<div class="case__t">' + C.sec_head("A panelled house", "c2-h", "Residential")
             + '<p>Raised panel walls, cased openings and coffered ceilings with a gilded cornice, '
             'milled to a profile taken from the original house. Every panel was laid out from the '
             'real walls so the reveals land evenly in every corner.</p>'
             + C.lnk("/services/architectural-millwork/", "Architectural millwork")
             + '</div>' + C.figure("cornice", wide="50vw", cls="case__f") + '</div></section>')
    drawn = ('<section class="drawn" aria-labelledby="dr-h"><div class="shell">'
             + C.sec_head("Drawn, then built", "dr-h", "Shop drawings",
                          "Every project starts as a set of drawings like these. They are where "
                          "changes are cheap, and they are what you approve.")
             + '<div class="drawn__g">'
             + "".join(f'<a class="drawn__i" href="/services/{s}/">{C.sheet(k, uid="-pj")}'
                       f'<span class="drawn__t">{E(t)}</span></a>'
                       for k, s, t in (("kitchen", "custom-kitchens", "Kitchen elevation"),
                                       ("reception", "office-millwork", "Reception desk"),
                                       ("builtin", "cabinetry-and-built-ins", "Built-in wall")))
             + '</div></div></section>')
    body = (C.page_header(p, actions=C.btn("/contact/#quote", "Start a project", lg=True))
            + C.bleed("finished", eager=True)
            + strip + case1 + case2
            + C.gallery(["frieze", "transom", "pendants", "plinth", "espresso", "cove", "shelving",
                         "panel-detail", "pipes", "archway", "lounge", "sconce"],
                        "From the bench", "gal-h", "Gallery",
                        "Details from both projects, photographed as built.")
            + drawn
            + C.index_list(C.service_items(), "The services behind this work", "svc-h", "Services",
                           None, cls="idx--small")
            + C.quote_starter("Have a room like these?"))
    return _page(
        **p, active="projects", body_class="pg-projects",
        title="Millwork Projects | Bar Fit-Out & Panelled Interiors",
        desc=("Custom millwork projects: a commercial bar fit-out from bare shell to finished room, "
              "and a panelled house with coffered ceilings and matched profiles."),
        keywords="millwork projects Toronto, bar fit out Toronto, wall panelling project, cabinetry portfolio",
        page_type="CollectionPage", body=body, images=C.IMAGES[:],
        og={"kind": "photo", "img": "/assets/img/lib/finished-wide-1600.webp", "kicker": "Projects",
            "title": "A shell, and then a room."},
        changefreq="monthly", priority="0.8", search_group="Projects")


def about():
    C.reset_images()
    p = {"path": "/about/", "label": "About", "crumbs": [("About", "about")],
         "h1": "One shop, start to finish.",
         "lede": ("We measure, draw, build, install and finish our own work in Mississauga, so no "
                  "dimension goes missing in a handover between companies.")}
    bench = ('<section class="bench" id="bench" aria-labelledby="bench-h"><div class="bench__pin">'
             '<div class="shell bench__g"><div class="bench__t">'
             + C.sec_head("Built on the bench", "bench-h", "The shop",
                          "Every carcass is made, assembled and checked in the shop before it is "
                          "taken apart again for delivery. Scroll to put one together.")
             + '<ol class="bench__steps">'
             '<li class="is-on">Sides cut and edged</li><li>Bottom and top fixed</li>'
             '<li>Back panel squares the box</li><li>Shelf and door fitted</li></ol></div>'
             '<div class="bench__stage"><canvas class="bench__cv" aria-hidden="true"></canvas>'
             + C.sheet("build", cls="bench__fallback", uid="-bench")
             + '</div></div></div></section>')
    who = ('<section class="who" aria-labelledby="who-h"><div class="shell">'
           + C.sec_head("Who we work with", "who-h", "Clients")
           + '<ul class="who__g">' + "".join(
               f'<li class="who__i"><h3 class="who__t">{E(t)}</h3><p class="who__d">{E(d)}</p></li>'
               for t, d in (
                   ("Homeowners", "Kitchens, built-ins and panelling, with drawings to approve "
                                  "before anything is built."),
                   ("Designers and architects", "Your design, resolved into shop drawings and "
                                                "built to the detail you drew."),
                   ("Builders and contractors", "Millwork packages priced from tender drawings "
                                                "and installed to your programme."),
                   ("Restaurants and offices", "Bars, counters and reception desks that open on "
                                               "time and stand up to daily use.")))
           + '</ul></div></section>')
    wont = ('<section class="wont" aria-labelledby="wont-h"><div class="shell wont__g">'
            + C.sec_head("What we will not do", "wont-h", "Principles",
                         "A few things that keep the work honest.")
            + '<ul class="wont__list">' + "".join(
                f'<li><h3 class="wont__t">{E(t)}</h3><p class="wont__d">{E(d)}</p></li>' for t, d in (
                    ("Quote per foot", "A price per linear foot describes an average room, not "
                                       "yours. We price from measured drawings."),
                    ("Cut before you approve", "Nothing goes through a saw until you have signed "
                                               "off the drawings, finishes and hardware."),
                    ("Hide a bad measure", "No filler strip doing the work a site measure should "
                                           "have done. We scribe to the wall."),
                    ("Hand the install to strangers", "The people who built it install it, so "
                                                      "the drawing and the room meet in one head.")))
            + '</ul></div></section>')
    body = (C.page_header(p, actions=C.btn("/contact/?visit=1#quote", "Book a shop visit", lg=True)
                          + C.lnk("#bench", "Inside the shop"))
            + C.bleed("sconce", eager=True)
            + C.say("Most joinery passes through four companies before it is hung. Every handover is "
                    "a chance for a dimension to drift.")
            + bench
            + C.process(PROCESS, "How we work", "prc-h", None, "Process")
            + who + wont
            + C.pair("archway", "base")
            + C.faq(faq_pick("Do you build in your own shop?", "Can I visit the shop?",
                             "Do you handle installation and finishing?",
                             "Do you work with designers, architects and contractors?"))
            + C.quote_starter())
    return _page(
        **p, active="about", body_class="pg-about",
        title="About Toronto Millworks | Custom Millwork Shop, GTA",
        desc=("Toronto Millworks is a custom millwork and cabinetry shop in Mississauga serving the "
              "GTA. We measure, draw, build, install and finish our own work."),
        keywords="Toronto millwork shop, millwork company Mississauga, custom joinery GTA, about Toronto Millworks",
        page_type="AboutPage", body=body, images=C.IMAGES[:],
        faq=faq_pick("Do you build in your own shop?", "Can I visit the shop?",
                     "Do you handle installation and finishing?",
                     "Do you work with designers, architects and contractors?"),
        og={"kind": "photo", "img": "/assets/img/lib/sconce-wide-1600.webp", "kicker": "About",
            "title": "One shop, start to finish."},
        three="bench", changefreq="monthly", priority="0.7", search_group="About")


def contact():
    C.reset_images()
    p = {"path": "/contact/", "label": "Contact", "crumbs": [("Contact", "contact")],
         "h1": "Tell us about the room.",
         "lede": ("Three short steps. Send what you know, and we come back with a measured quote "
                  "rather than a guess.")}
    steps = [("We read what you sent", "Drawings, photos or rough dimensions are enough to start a "
                                       "conversation about scope and finish."),
             ("We measure and draw", "We template the real room, then draw elevations showing "
                                     "every door, panel and handle."),
             ("You get a measured quote", "Priced from the approved drawings, so the number "
                                          "reflects your room and not an average.")]
    side = ('<aside class="cx__side" aria-label="Other ways to reach us">'
            '<div class="cx__block"><span class="cx__block-h">Write to us</span>'
            f'<a class="cx__mail" href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a>'
            f'<button class="cx__copy" type="button" data-copy="{E(SITE["email"])}">Copy address</button>'
            + (f'<span class="cx__block-h">Call</span><a class="cx__mail" href="tel:{E(SITE["phone"])}">'
               f'{E(SITE["phone"])}</a>' if SITE["phone"] else "")
            + '<span class="cx__block-h">The shop</span>'
            f'<address class="cx__addr">{E(SITE["street"])}<br>{E(SITE["locality"])}, {E(SITE["region"])} '
            f'{E(SITE["postal"])}<br>Canada</address>'
            + C.ext(MAP_DIRECTIONS, "Directions") +
            '<p class="cx__note">Visits by appointment, so someone is free to walk you through '
            'drawings and samples.</p></div></aside>')
    body = ('<section class="cx"><div class="shell">' + C.crumbs(p["crumbs"])
            + '<div class="cx__grid"><div class="cx__lead">' + C.pill("Contact")
            + f'<h1 class="cx__title">{E(p["h1"])}</h1><p class="cx__lede">{E(p["lede"])}</p>'
            + C.quote_form() + '</div>' + side + '</div>'
            '<div class="cx__next"><h2 class="cx__next-h" id="next-h">What happens next</h2>'
            '<ol class="cx__steps">' + "".join(
                f'<li class="cx__step"><h3 class="cx__step-h">{E(t)}</h3><p class="cx__step-p">{E(d)}</p></li>'
                for t, d in steps) + '</ol></div></div></section>'
            + C.faq(faq_pick("How do you prepare a quote?", "How much does custom millwork cost?",
                             "Which areas do you serve?", "Can I visit the shop?",
                             "Do you work with designers, architects and contractors?")))
    return _page(
        **p, active="contact", body_class="pg-contact",
        title="Contact Toronto Millworks | Request a Millwork Quote",
        desc=("Request a custom millwork or cabinetry quote for Toronto and the GTA. Tell us about "
              "the room in three short steps and get a measured price, not a guess."),
        keywords="millwork quote Toronto, custom cabinetry quote, contact Toronto Millworks, joinery estimate GTA",
        page_type="ContactPage", body=body, images=C.IMAGES[:],
        faq=faq_pick("How do you prepare a quote?", "How much does custom millwork cost?",
                     "Which areas do you serve?", "Can I visit the shop?",
                     "Do you work with designers, architects and contractors?"),
        og={"kind": "drawing", "drawing": "draw", "kicker": "Contact", "title": "Tell us about the room."},
        changefreq="monthly", priority="0.9", search_group="Contact", no_dock=True)


def faq_page():
    C.reset_images()
    p = {"path": "/faq/", "label": "FAQ", "crumbs": [("FAQ", "faq")],
         "h1": "Questions, answered plainly.",
         "lede": ("What custom millwork costs, how long it takes, what it is made from, and how a "
                  "project actually runs.")}
    body = (C.page_header(p, actions=C.btn("/contact/#quote", "Ask about your project", lg=True))
            + C.faq(groups=FAQ_GROUPS, h2="Every question<br> we get asked", more=False)
            + C.index_list(guide_items([g["slug"] for g in GUIDES]), "Go deeper", "gd-h", "Guides",
                           None, cls="idx--small idx--guides")
            + C.quote_starter())
    return _page(
        **p, active="", body_class="pg-faq",
        title="Custom Millwork FAQ | Cost, Timing & Materials",
        desc=("Answers to common questions about custom millwork: what it costs, how long it takes, "
              "materials, matching existing trim and the areas we serve."),
        keywords="millwork FAQ, custom cabinetry cost, millwork questions, custom kitchen timeline",
        page_type="FAQPage", body=body, images=C.IMAGES[:], faq=FAQ,
        og={"kind": "drawing", "drawing": "measure", "kicker": "FAQ", "title": "Questions, answered plainly."},
        changefreq="monthly", priority="0.7", search_group="FAQ")


# ══════════════════════════════════════════════════════════════════════════════
#  SERVICE AREAS
# ══════════════════════════════════════════════════════════════════════════════
def areas_hub():
    C.reset_images()
    p = {"path": "/service-areas/", "label": "Service areas",
         "crumbs": [("Service areas", "service-areas")],
         "h1": "Toronto, and 120 km around it.",
         "lede": (f"Every town and city within about 120 km of our shop in Mississauga, measured, "
                  f"built and installed by the same team.")}
    body = (C.page_header(p, actions=C.btn("/contact/#quote", "Get a quote", lg=True))
            + C.areas_section("Every town we serve", "arx-h",
                              "Pick a place for local detail, or find it on the map.")
            + C.say("Almost no wall in this region is square. That is the whole reason anything "
                    "worth fitting is templated on site.")
            + C.index_list(C.service_items(), "What we build across the region", "svc-h", "Services",
                           None, cls="idx--small")
            + C.faq(faq_pick("Which areas do you serve?", "How long are you on site?",
                             "Can you work to a fixed opening or move-in date?"))
            + C.quote_starter("Not on the list?", "If you are within about 120 km of Mississauga we "
                              "can almost certainly come to you. Tell us where."))
    return _page(
        **p, active="", body_class="pg-areas",
        title="Service Areas | Custom Millwork Within 120 km of Toronto",
        desc=("Custom millwork and cabinetry across 50 towns and cities within 120 km of our "
              "Mississauga shop, from Hamilton and Niagara to Barrie, Durham and Waterloo."),
        keywords="millwork service area, custom cabinetry GTA, millwork Hamilton Niagara Barrie, Toronto millwork near me",
        page_type="CollectionPage", body=body, images=C.IMAGES[:],
        itemlist=[(f"Custom millwork in {x['name']}", f"service-areas/{x['slug']}") for x in LOCATIONS],
        faq=faq_pick("Which areas do you serve?", "How long are you on site?",
                     "Can you work to a fixed opening or move-in date?"),
        og={"kind": "map", "slug": None, "kicker": "Service areas",
            "title": "Toronto, and 120 km around it."},
        changefreq="monthly", priority="0.8", search_group="Areas")


AREA_PLATES = ["room", "doors", "archway", "panel-corner", "coffer", "sconce", "transom",
               "plinth", "cornice", "base", "frieze", "panel-detail"]
AREA_PLATES_COM = ["espresso", "pendants", "shelving", "counter", "finished", "lounge", "pipes",
                   "feature"]


def _a(word):
    """The indefinite article a town name takes when it is used as an adjective."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def _area_faq(pl):
    near = ", ".join(pl["areas"][:-1]) + " and " + pl["areas"][-1] if len(pl["areas"]) > 1 else pl["areas"][0]
    if pl["kind"] == "home-base":
        dist = ("Our shop is in Malton, Mississauga, so this is home ground. Site visits, deliveries "
                "and installs are a short drive.")
    else:
        dist = (f"Our shop at {SITE['street']} in Mississauga is about {pl['km']} km from {pl['name']} "
                f"in a straight line. We plan the measure, deliveries and install so the travel never "
                f"holds a job up.")
    kind_q = {
        "heritage": (f"Can you match the original trim in an older {pl['name']} house?",
                     "Yes. We take a section from the existing profile on site, grind a knife to match "
                     "and run new stock from it, so new work sits beside the original without a visible join."),
        "hospitality": (f"Do you build restaurant and bar millwork in {pl['name']}?",
                        "Yes. Bars, back bars, counters and banquettes are shop drawn for approval, built "
                        "in our shop while the space is finished, and installed in a short window."),
        "office": (f"Do you build office millwork in {pl['name']}?",
                   "Yes. Reception desks, meeting room storage, staff kitchens and storage walls, "
                   "scheduled around your move-in date and the building's rules."),
        "lakeside": ("Can you help turn a cottage into a year-round home?",
                     "Yes. Converting a cottage usually means rethinking storage, the kitchen and the "
                     "trim together, in rooms that were never square, and finishes that cope with lake "
                     "humidity."),
        "condo": ("Do you work in condo buildings?",
                  "Yes. Condo installs are planned around elevator bookings, delivery windows and the "
                  "building's rules on noise, which we confirm with management first."),
        "rural": ("Do you take on larger country properties?",
                  "Yes. Farmhouse kitchens, mudrooms and libraries in homes that have often been "
                  "extended more than once, which makes a careful site measure even more important."),
    }.get(pl["kind"], (f"What do you build most often in {pl['name']}?",
                       "Kitchens and built-in storage are the most common requests, followed by wall "
                       "panelling, trim and renovations. Commercial work covers restaurants, bars and "
                       "offices."))
    return [(f"Do you work in {near}?",
             f"Yes. We work across {pl['name']}, including {near}, and the rest of the region within "
             f"about 120 km of our shop."),
            (f"How far is {pl['name']} from your shop?", dist),
            kind_q]


def area(pl, i):
    C.reset_images()
    path = f"/service-areas/{pl['slug']}/"
    p = {"path": path, "label": pl["region"],
         "crumbs": [("Service areas", "service-areas"), (pl["name"], f"service-areas/{pl['slug']}")],
         "h1": f"Custom Millwork in {pl['name']}", "lede": pl["lede"]}
    com = pl["focus"][0] in ("restaurant-and-bar-millwork", "office-millwork", "commercial-fit-outs")
    pool = AREA_PLATES_COM if com else AREA_PLATES
    plate = pool[i % len(pool)]
    plate2 = (AREA_PLATES if com else AREA_PLATES_COM)[(i * 3) % len((AREA_PLATES if com else AREA_PLATES_COM))]
    hood = "".join(f"<li>{E(a)}</li>" for a in pl["areas"])
    svc_items = [{"href": f"/services/{s}/", "title": SERVICE_AREA_LABEL[s].format(pl["name"]),
                  "text": SERVICE_BY_SLUG[s]["blurb"],
                  "plate": SERVICE_BY_SLUG[s]["plates"][0]} for s in pl["focus"]]
    km_line = ("" if pl["kind"] == "home-base" else
               f" {pl['name']} is about {pl['km']} km from the shop, so we book the site measure, "
               f"deliveries and the install as planned trips, and the work arrives finished rather "
               f"than being assembled from scratch in your room.")
    process_note = (f"Every {pl['name']} project follows the same four stages: we measure the room as "
                    f"it really is, draw it for your approval, build and dry fit it in our shop, then "
                    f"install, scribe and finish it on site.{km_line}")
    body = (C.page_header(p, visual=f'<div class="ph__map">{maps.place_map(pl["slug"])}</div>',
                          actions=C.btn(f"/contact/?area={pl['slug']}#quote", "Get a quote", lg=True)
                          + C.lnk("#local", f"Working in {pl['name']}"), tone="ph--place")
            + '<section class="loc" id="local" aria-labelledby="loc-h"><div class="shell loc__g">'
            + C.figure(plate, wide="46vw", cls="loc__f")
            + '<div class="loc__t">' + C.sec_head(pl["name"] + ", as it is built", "loc-h", "Local")
            + f'<p class="loc__p">{E(pl["body"])}</p><h3 class="loc__h3">Neighbourhoods we work in</h3>'
            f'<ul class="loc__hoods">{hood}</ul></div></div></section>'
            + C.index_list(svc_items, f"What we build in {pl['name']}", "svc-h", "Services",
                           None, cls="idx--small")
            + C.figsay(plate2, f"How {_a(pl['name'])} {pl['name']} project runs", "how-h", process_note, flip=True,
                       extra=C.lnk("/guides/how-custom-millwork-is-made/", "How custom millwork is made"))
            + C.faq(_area_faq(pl), h2=f"Questions from<br> {E(pl['name'])}", map_after=True)
            + C.nearby(nearest(pl["slug"], 6), "Nearby areas we serve", "near-h")
            + C.quote_starter(f"Planning a project in {pl['name']}?", area=pl["slug"]))
    areas_txt = pl["areas"]
    hub = "our shop in Malton" if pl["kind"] == "home-base" else f"our Mississauga shop, {pl['km']} km away"
    desc_c = []
    for n in (3, 2, 1):
        a = areas_txt[:n]
        a_txt = (", ".join(a[:-1]) + " and " + a[-1]) if len(a) > 1 else a[0]
        desc_c += [f"Custom millwork, kitchens and built-ins in {pl['name']}, including {a_txt}. "
                   f"Measured on site and built in {hub}.",
                   f"Custom millwork and cabinetry in {pl['name']}, including {a_txt}. Measured on "
                   f"site, built in {hub}."]
    title = _fit([f"Custom Millwork & Cabinetry in {pl['name']} | Toronto Millworks",
                  f"Custom Millwork & Cabinetry {pl['name']} | Toronto Millworks",
                  f"Custom Millwork in {pl['name']} | Toronto Millworks",
                  f"Custom Millwork & Cabinetry in {pl['name']}",
                  f"Custom Millwork in {pl['name']}, Ontario"], 30, 60)
    return _page(
        **p, active="", body_class="pg-area", title=title, desc=_fit(desc_c, 120, 160),
        keywords=(f"custom millwork {pl['name']}, custom cabinetry {pl['name']}, custom kitchens "
                  f"{pl['name']}, millwork near {pl['name']}"),
        place=pl, faq=_area_faq(pl), body=body, images=C.IMAGES[:], page_type="WebPage",
        og={"kind": "map", "slug": pl["slug"], "kicker": f"Service area · {pl['region']}",
            "title": f"Custom millwork in {pl['name']}."},
        changefreq="monthly", priority="0.7", search_group="Areas")


# ══════════════════════════════════════════════════════════════════════════════
#  GUIDES
# ══════════════════════════════════════════════════════════════════════════════
def guides_hub():
    C.reset_images()
    p = {"path": "/guides/", "label": "Guides", "crumbs": [("Guides", "guides")],
         "h1": "Read this before you buy cabinetry.",
         "lede": ("Plain guides to cost, materials, finishes and planning, written from the bench "
                  "rather than the showroom.")}
    body = (C.page_header(p, visual=C.sheet("draw", cls="ph__sheet", uid="-ph"))
            + C.index_list(guide_items([g["slug"] for g in GUIDES]), "All guides", "gd-h", None,
                           None, cls="idx--guides")
            + C.quote_starter("Rather talk it through?"))
    return _page(
        **p, active="", body_class="pg-guides",
        title="Millwork & Cabinetry Guides | Cost, Materials, Planning",
        desc=("Guides to custom millwork and cabinetry: what affects the cost, choosing wood, paint "
              "or stain, custom versus stock, and planning restaurant millwork."),
        keywords="millwork guides, cabinetry buying guide, custom cabinet cost guide, wood for cabinets",
        page_type="CollectionPage", body=body, images=C.IMAGES[:],
        itemlist=[(g["h1"], f"guides/{g['slug']}") for g in GUIDES],
        og={"kind": "drawing", "drawing": "draw", "kicker": "Guides",
            "title": "Read this before you buy cabinetry."},
        changefreq="monthly", priority="0.7", search_group="Guides")


def guide(g):
    C.reset_images()
    path = f"/guides/{g['slug']}/"
    p = {"path": path, "label": "Guide",
         "crumbs": [("Guides", "guides"), (g["h1"], f"guides/{g['slug']}")],
         "h1": g["h1"], "lede": g["lede"]}
    art, words = C.article(g)
    others = [x["slug"] for x in GUIDES if x["slug"] != g["slug"]][:3]
    body = (C.page_header(p, note="By Toronto Millworks · Updated October 2026", tone="ph--article")
            + art
            + C.faq(g["faq"], h2="Quick<br> answers", map_after=False)
            + C.index_list(C.service_items(g["services"]), "Where this applies", "rel-h", "Services",
                           None, cls="idx--small")
            + C.index_list(guide_items(others), "More guides", "more-h", "Guides", None,
                           cls="idx--small idx--guides")
            + C.quote_starter())
    return _page(
        **p, active="", body_class="pg-guide", title=g["title"], desc=g["desc"],
        keywords=g["keywords"], guide=g, faq=g["faq"], words=words, body=body,
        images=C.IMAGES[:], page_type="WebPage", og_type="article",
        og={"kind": "drawing", "drawing": g["drawing"], "kicker": "Guide", "title": g["h1"]},
        changefreq="yearly", priority="0.6", search_group="Guides")


# ══════════════════════════════════════════════════════════════════════════════
#  PRIVACY, SEARCH, 404
# ══════════════════════════════════════════════════════════════════════════════
def privacy():
    C.reset_images()
    p = {"path": "/privacy-policy/", "label": "Privacy", "crumbs": [("Privacy policy", "privacy-policy")],
         "h1": "Privacy policy", "lede": "What we collect through this site, why, and what we do with it."}
    secs = [
        ("What we collect", [
            "When you send an enquiry we receive what you choose to tell us: your name, email "
            "address, phone number if you give one, the location and type of your project, and "
            "anything you write about it.",
            "This site does not use advertising or analytics cookies, and it does not track you "
            "across other sites."]),
        ("How we use it", [
            "Only to reply to your enquiry, prepare a quote and carry out work you ask us to do. We "
            "do not sell or rent personal information, and we do not use it for marketing you have "
            "not asked for."]),
        ("Third parties", [
            "Pages that show our shop on a map load an embedded Google map, which is subject to "
            "Google's own privacy policy. If a form service is used to deliver enquiries, it "
            "processes your message only to pass it to us."]),
        ("How long we keep it", [
            "We keep enquiry details for as long as they are needed to respond and to keep records "
            "of work we carry out, and no longer than the law requires."]),
        ("Your choices", [
            f"You can ask what we hold about you, ask us to correct it, or ask us to delete it, by "
            f"writing to {SITE['email']}. We handle personal information in line with Canada's "
            f"Personal Information Protection and Electronic Documents Act."]),
    ]
    g = {"h1": p["h1"], "sections": secs, "drawing": None}
    art, _ = C.article(g)
    body = C.page_header(p, note="Updated October 2026", tone="ph--article") + art
    return _page(
        **p, active="", body_class="pg-guide pg-privacy",
        title="Privacy Policy | Toronto Millworks",
        desc=("How Toronto Millworks collects, uses and protects the personal information you send "
              "through this site, and how to ask us to correct or delete it."),
        keywords="", page_type="WebPage", body=body, images=[],
        og={"kind": "drawing", "drawing": "draw", "kicker": "Privacy", "title": "Privacy policy"},
        changefreq="yearly", priority="0.2", search_group="Page")


def search():
    C.reset_images()
    p = {"path": "/search/", "label": "Search", "crumbs": [("Search", "search")], "h1": "Search",
         "lede": "Find a service, a town, a guide or an answer."}
    body = (C.page_header(p, tone="ph--search")
            + '<section class="srch"><div class="shell">'
            '<form class="srch__form" role="search" action="/search/" method="get">'
            '<label class="sr-only" for="q">Search this site</label>'
            '<input id="q" name="q" type="search" placeholder="Try kitchens, panelling or Oakville" '
            'autocomplete="off" spellcheck="false">'
            '<button class="srch__go" type="submit"><span class="sr-only">Search</span>'
            f'<i aria-hidden="true">{C.ARROW}</i></button></form>'
            '<p class="srch__n" aria-live="polite"></p><ol id="results" class="srch__out"></ol>'
            '</div></section>')
    return _page(**p, active="", body_class="pg-search", title="Search | Toronto Millworks",
                 desc=("Search Toronto Millworks for custom millwork services, the towns and cities "
                       "we serve, guides and answers to common questions."),
                 noindex=True, body=body, images=[],
                 og={"kind": "drawing", "drawing": "draw", "kicker": "Search", "title": "Search"},
                 search_group="Page")


def not_found():
    C.reset_images()
    p = {"path": "404.html", "h1": "This piece was never milled.",
         "lede": ("The page you were after is not in the shop. It may have moved, or the link may "
                  "be mistyped. Everything that is here is one click away.")}
    links = "".join(f'<li><a href="{h}">{E(t)}</a></li>' for h, t in (
        ("/services/", "Services"), ("/projects/", "Projects"), ("/service-areas/", "Service areas"),
        ("/guides/", "Guides"), ("/faq/", "FAQ"), ("/contact/", "Contact")))
    body = ('<section class="nf" aria-labelledby="nf-h"><div class="nf__stage">'
            '<canvas class="nf__cv" aria-hidden="true"></canvas>'
            + C.sheet("panelling", cls="nf__fallback", uid="-nf") + '</div>'
            '<div class="shell nf__g"><div class="nf__t"><p class="nf__code">Error 404</p>'
            f'<h1 class="nf__h" id="nf-h">{E(p["h1"])}</h1><p class="nf__l">{E(p["lede"])}</p>'
            '<form class="nf__s" role="search" action="/search/" method="get">'
            '<label class="sr-only" for="nfq">Search this site</label>'
            '<input id="nfq" name="q" type="search" placeholder="Search the site">'
            f'<button type="submit"><span class="sr-only">Search</span><i aria-hidden="true">{C.ARROW}</i></button>'
            '</form><div class="nf__a">' + C.btn("/", "Back to the home page", lg=True) + '</div>'
            f'<ul class="nf__links" aria-label="Popular pages">{links}</ul></div></div></section>')
    return _page(**p, active="", body_class="pg-404", title="Page Not Found | Toronto Millworks",
                 desc=("The page you asked for does not exist. Browse custom millwork services, the "
                       "areas we serve, or request a measured quote."),
                 noindex=True, body=body, images=[], three="panel", no_dock=True,
                 og={"kind": "drawing", "drawing": "panelling", "kicker": "404",
                     "title": "This piece was never milled."},
                 anywhere=True)


def all_pages():
    pages = [home(), services_hub()] + [service(s) for s in SERVICES]
    pages += [projects(), about(), contact(), faq_page(), areas_hub()]
    pages += [area(pl, i) for i, pl in enumerate(LOCATIONS)]
    pages += [guides_hub()] + [guide(g) for g in GUIDES] + [privacy(), search(), not_found()]
    return pages
