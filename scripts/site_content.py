#!/usr/bin/env python3
"""
Site content and SEO model for Toronto Millworks.

Everything the generator needs lives here: the business entity, the page tree,
per-page metadata, copy and schema hints. Edit this file, then run

    python3 scripts/build_site.py

No em dashes anywhere in this file. Copy uses commas, full stops or "and".
"""

# ── the one place the domain is declared ─────────────────────────────────────
# The one place the live origin is declared. Everything downstream (canonicals,
# sitemap, schema, Open Graph, llms.txt) is derived from it, so pointing the site
# at a custom domain later is this single line plus a rebuild.
ORIGIN = "https://toronto-millworks.vercel.app"

BUILD_DATE = "2026-08-31"          # feeds <lastmod> and dateModified

SITE = {
    "name": "Toronto Millworks",
    "legal": "Toronto Millworks",
    "origin": ORIGIN,
    "lang": "en-CA",
    "email": "hello@torontomillworks.ca",        # PLACEHOLDER
    "locality": "Toronto",
    "region": "ON",
    "region_name": "Ontario",
    "country": "CA",
    "lat": 43.6532,
    "lon": -79.3832,
    "tagline": "Custom millwork, cabinetry and interior renovation in Toronto.",
    "founded": "",                               # PLACEHOLDER: add founding year
    "street": "",                                # PLACEHOLDER: add street address
    "postal": "",                                # PLACEHOLDER: add postal code
    "phone": "",                                 # PLACEHOLDER: add phone number
    # PLACEHOLDER: real profile URLs make these entity connections work.
    # Leave empty and the generator omits sameAs rather than emitting dead links.
    "same_as": [],
}

AREAS = [
    "Toronto", "North York", "Etobicoke", "Scarborough", "East York",
    "Vaughan", "Richmond Hill", "Markham", "Mississauga", "Oakville",
]

# ── services ─────────────────────────────────────────────────────────────────
SERVICES = [
    {
        "slug": "custom-kitchens",
        "nav": "Custom Kitchens",
        "h1": "Custom Kitchens in Toronto",
        "title": "Custom Kitchens Toronto | Kitchen Cabinetry | Toronto Millworks",
        "desc": ("Custom kitchen cabinetry in Toronto, milled and installed by "
                 "our own shop. Islands, pantries and appliance surrounds built "
                 "to your measured drawings."),
        "lede": ("We build kitchen cabinetry to the room rather than to a catalogue. "
                 "Every carcass, door and panel is milled in our Toronto shop from "
                 "drawings measured on your site."),
        "keywords": "custom kitchens Toronto, kitchen cabinetry Toronto, custom kitchen cabinets",
        "sections": [
            ("What we build", [
                "Full kitchen cabinetry, uppers and lowers, in painted or veneered finishes.",
                "Islands and peninsulas with integrated seating, storage and power.",
                "Walk in and reach in pantries with adjustable shelving.",
                "Appliance surrounds and integrated panels for fridges, dishwashers and hoods.",
                "Open shelving, plate racks, spice pull outs and cutlery inserts.",
            ]),
            ("How a kitchen comes together", [
                "We measure the room on site and draw it before anything is cut.",
                "You approve elevations, finishes and hardware from those drawings.",
                "The cabinetry is milled and dry fitted on our bench.",
                "We install, scribe to the walls and finish on site.",
            ]),
        ],
        "faq": [
            ("How much does a custom kitchen cost in Toronto?",
             "Cost depends on the size of the room, the materials and the finish. "
             "We quote from measured drawings rather than a generic per foot rate, "
             "so the number reflects your actual kitchen."),
            ("Can you match existing millwork in my home?",
             "Yes. We template profiles from the trim and cabinetry already in the "
             "house so new work reads as part of the original build."),
            ("Do you install the kitchen as well as build it?",
             "Yes. The same shop that mills the cabinetry installs it, scribes it "
             "to the walls and finishes it on site."),
        ],
    },
    {
        "slug": "cabinetry-and-built-ins",
        "nav": "Cabinetry & Built-Ins",
        "h1": "Custom Cabinetry and Built-Ins",
        "title": "Custom Cabinetry Toronto | Built-In Storage | Toronto Millworks",
        "desc": ("Custom built-in cabinetry in Toronto. Wall units, wardrobes, "
                 "libraries, media walls and storage designed around the room and "
                 "installed by our own team."),
        "lede": ("Built-ins should look like part of the architecture, not like "
                 "furniture pushed against a wall. We design storage around the "
                 "room it lives in."),
        "keywords": "custom cabinetry Toronto, built-ins Toronto, custom wardrobes Toronto",
        "sections": [
            ("What we build", [
                "Living room wall units, media walls and fireplace surrounds.",
                "Libraries and home office joinery with integrated desks.",
                "Wardrobes, walk in closets and mudroom benches.",
                "Under stair storage and awkward alcove cabinetry.",
                "Bathroom vanities and linen towers.",
            ]),
            ("Designed around the room", [
                "Every built in is drawn against the real wall, including the out of "
                "square corners, the baseboard returns and the service runs behind it. "
                "That is why the finished piece sits flush instead of showing a gap "
                "you have to fill with trim.",
            ]),
        ],
        "faq": [
            ("Do built-ins add value to a Toronto home?",
             "Well made built-ins use space that furniture cannot, particularly in "
             "older Toronto houses with narrow footprints and irregular walls."),
            ("Can you work around existing wiring and radiators?",
             "Yes. We locate services during the site measure and design the "
             "carcass around them, with access panels where they are needed."),
        ],
    },
    {
        "slug": "architectural-millwork",
        "nav": "Architectural Millwork",
        "h1": "Architectural Millwork and Panelling",
        "title": "Architectural Millwork Toronto | Panelling and Trim",
        "desc": ("Architectural millwork in Toronto. Wall panelling, coffered "
                 "ceilings, crown moulding, wainscoting, stair details and custom "
                 "trim profiles milled to match."),
        "lede": ("The work that makes a room feel finished. Panelling, cornice, "
                 "casing and ceiling detail, milled to profile and fitted to the "
                 "space."),
        "keywords": "architectural millwork Toronto, wall panelling Toronto, crown moulding Toronto",
        "sections": [
            ("What we build", [
                "Raised and flat panel wall panelling, full height or wainscot.",
                "Coffered and tray ceilings with cove lighting details.",
                "Crown moulding, cornice and ceiling medallions.",
                "Door and window casing, plinth blocks and baseboard.",
                "Stair parts, newels, handrail and balustrade.",
                "Custom knife profiles milled to match existing trim.",
            ]),
            ("Matching what is already there", [
                "In a heritage Toronto house the trim rarely matches anything you "
                "can buy off a rack. We take a profile from the existing moulding, "
                "grind a knife to it and run new stock that sits alongside the old "
                "work without a visible join.",
            ]),
        ],
        "faq": [
            ("Can you reproduce heritage trim profiles?",
             "Yes. We take a section from the existing profile, grind a matching "
             "knife and run new stock from it."),
            ("Do you install panelling on out of square walls?",
             "That is the normal case in older houses. Panels are scribed to the "
             "wall on site so the reveals stay even."),
        ],
    },
    {
        "slug": "commercial-fit-outs",
        "nav": "Commercial Fit-Outs",
        "h1": "Commercial Millwork and Fit-Outs",
        "title": "Commercial Millwork Toronto | Restaurant & Office Fit-Outs",
        "desc": ("Commercial millwork in Toronto for restaurants, bars, cafes, "
                 "offices and retail. Built to spec in our shop and installed on "
                 "schedule with minimal downtime."),
        "lede": ("Bars, back bars, service counters, banquettes and retail joinery, "
                 "built to spec and installed on a schedule that keeps the "
                 "handover date."),
        "keywords": "commercial millwork Toronto, restaurant millwork Toronto, office fit out Toronto",
        "sections": [
            ("What we build", [
                "Bars, back bars and service counters.",
                "Banquette seating, booths and fixed furniture.",
                "Host stands, retail displays and shelving systems.",
                "Reception desks and office joinery.",
                "Feature walls, slat walls and ceiling rafts.",
            ]),
            ("Built to a programme", [
                "Commercial work lives or dies on the schedule. We build off site "
                "while the trades ahead of us finish, then install in a defined "
                "window so the space is not held open longer than it needs to be. "
                "Shop drawings go out for approval before anything is cut.",
            ]),
        ],
        "faq": [
            ("Do you work from an architect's drawings?",
             "Yes. We take architectural drawings, produce shop drawings from them "
             "and submit those for approval before fabrication."),
            ("Can you work overnight to avoid closing a business?",
             "Install windows can be scheduled around trading hours where the site "
             "and the building allow it."),
        ],
    },
    {
        "slug": "interior-renovation",
        "nav": "Interior Renovation",
        "h1": "Interior Renovation in Toronto",
        "title": "Interior Renovation Toronto | Millwork-Led Renovations",
        "desc": ("Millwork-led interior renovation in Toronto. One team handling "
                 "the joinery, surfaces and finishing so the cabinetry and the "
                 "room are built to the same standard."),
        "lede": ("Full room renovations where the joinery, the surfaces and the "
                 "finishing are handled by one team, so nothing is coordinated "
                 "across three trades that never met."),
        "keywords": "interior renovation Toronto, millwork renovation Toronto, home renovation Toronto",
        "sections": [
            ("What is included", [
                "Kitchen and bathroom renovation with cabinetry built in house.",
                "Basement and attic conversions with fitted storage.",
                "Wall and ceiling detail, trim replacement and finishing.",
                "Flooring, tiling and surface coordination.",
            ]),
            ("Why millwork led matters", [
                "When the joinery is designed last it gets squeezed into whatever "
                "space is left. Starting from the millwork means the cabinetry, "
                "the services and the finishes are resolved on the same drawing "
                "instead of on site.",
            ]),
        ],
        "faq": [
            ("Do you handle permits?",
             "We advise on what a project needs and work with the drawings and "
             "consultants a permit application requires."),
            ("Can you renovate one room at a time?",
             "Yes. Single room projects are common, particularly kitchens and "
             "principal bathrooms."),
        ],
    },
]

# ── service areas ────────────────────────────────────────────────────────────
AREA_PAGES = [
    {
        "slug": "toronto",
        "name": "Toronto",
        "title": "Custom Millwork Toronto | Cabinetry and Joinery",
        "desc": ("Custom millwork and cabinetry across Toronto, from downtown "
                 "condos to Forest Hill and the Annex. Measured, milled and "
                 "installed by our own shop."),
        "lede": ("We work across the old city, from downtown condo interiors to "
                 "the century houses of the Annex, Forest Hill and Riverdale."),
        "notes": ("Toronto housing stock runs from narrow Victorian semis to new "
                  "build towers, and almost none of it is square. Everything we "
                  "make is templated from the wall it is going against, which is "
                  "the only way trim and cabinetry sit flush in a house that has "
                  "moved for a hundred years."),
    },
    {
        "slug": "north-york",
        "name": "North York",
        "title": "Custom Millwork North York | Cabinetry & Built-Ins",
        "desc": ("Custom cabinetry and architectural millwork in North York, "
                 "including Willowdale, Bayview Village and York Mills. "
                 "Kitchens, built-ins, panelling and interior renovation."),
        "lede": ("Postwar bungalows, mid century splits and new builds around "
                 "Willowdale, Bayview Village and York Mills."),
        "notes": ("A lot of North York work is renovation of large postwar houses, "
                  "where ceiling heights and long straight walls suit full height "
                  "panelling and generous built in storage."),
    },
    {
        "slug": "etobicoke",
        "name": "Etobicoke",
        "title": "Custom Millwork Etobicoke | Kitchens & Cabinetry",
        "desc": ("Custom kitchens, cabinetry and architectural millwork in "
                 "Etobicoke, from Mimico and The Kingsway to the Humber Bay "
                 "waterfront. Built and installed by our own shop."),
        "lede": ("From the lakeshore condos of Humber Bay to the older streets of "
                 "The Kingsway and Mimico."),
        "notes": ("Waterfront condo work has its own constraints, including service "
                  "elevator bookings, tight install windows and building rules on "
                  "noise. We plan the install around those before we start."),
    },
    {
        "slug": "scarborough",
        "name": "Scarborough",
        "title": "Custom Millwork Scarborough | Cabinetry & Renovation",
        "desc": ("Custom cabinetry, built-in storage and interior renovation in "
                 "Scarborough and the Bluffs. Measured on site, milled in our "
                 "own shop and installed by the same team."),
        "lede": ("Bungalows, backsplit houses and family homes across Scarborough "
                 "and the Bluffs."),
        "notes": ("Scarborough projects often involve opening up a compartmented "
                  "postwar plan, where the millwork has to carry storage that the "
                  "removed walls used to provide."),
    },
    {
        "slug": "vaughan",
        "name": "Vaughan",
        "title": "Custom Millwork Vaughan | Kitchens, Panelling & Built-Ins",
        "desc": ("Custom kitchens, wall panelling and built-in cabinetry in "
                 "Vaughan, Woodbridge, Maple, Kleinburg and Thornhill. Measured "
                 "on site and milled in our own Toronto shop."),
        "lede": ("Larger new build homes across Woodbridge, Maple, Kleinburg and "
                 "Thornhill."),
        "notes": ("New build houses in Vaughan often have the volume for coffered "
                  "ceilings, full height panelling and a proper scullery behind "
                  "the main kitchen."),
    },
    {
        "slug": "mississauga",
        "name": "Mississauga",
        "title": "Custom Millwork Mississauga | Cabinetry & Fit-Outs",
        "desc": ("Custom millwork and cabinetry in Mississauga for homes and "
                 "commercial spaces, including restaurants, offices and retail."),
        "lede": ("Residential work across Port Credit, Lorne Park and Erin Mills, "
                 "plus commercial fit-outs along the Mississauga corridor."),
        "notes": ("The commercial side of Mississauga work is mostly offices and "
                  "restaurants, where the install has to fit a fixed opening date "
                  "and a landlord's building rules."),
    },
]

# ── FAQ (site level) ─────────────────────────────────────────────────────────
FAQ = [
    ("What is millwork?",
     "Millwork is woodwork made to measure for a specific building, as opposed to "
     "stock items bought off a shelf. It covers cabinetry, panelling, trim, "
     "stairs, doors and fitted furniture."),
    ("How much does custom millwork cost in Toronto?",
     "It depends on size, material and finish. We quote from measured drawings "
     "rather than a per foot rate, so the price reflects the actual room. A "
     "painted poplar built in and a rift white oak kitchen are not comparable "
     "jobs even at the same linear footage."),
    ("How long does a custom millwork project take?",
     "The schedule is set by four stages: site measure and drawings, approval, "
     "shop fabrication, then install. Approval is usually the stage that moves "
     "most, because it depends on how quickly finishes and hardware are decided."),
    ("Do you build in your own shop?",
     "Yes. Everything is milled and dry fitted on our own bench before it goes to "
     "site, and the same team installs it."),
    ("Do you work on commercial projects as well as homes?",
     "Yes. Roughly half our work is commercial, including restaurants, bars, "
     "cafes, offices and retail."),
    ("Which areas do you serve?",
     "Toronto and the surrounding Greater Toronto Area, including North York, "
     "Etobicoke, Scarborough, Vaughan, Richmond Hill, Markham, Mississauga and "
     "Oakville."),
    ("Do you provide drawings before work starts?",
     "Yes. Nothing is cut until you have approved elevations showing the layout, "
     "the finishes and the hardware."),
    ("Can you match existing trim and cabinetry?",
     "Yes. We take a section from the existing profile, grind a knife to match "
     "and run new stock from it, which is how new work disappears into an older "
     "house."),
    ("What materials do you work with?",
     "Solid hardwood, veneered panel, painted poplar and MDF, and engineered "
     "substrates where stability matters more than grain. The right choice "
     "depends on the piece and where it sits."),
    ("Do you handle installation and finishing?",
     "Yes. We install, scribe to the walls and finish on site rather than "
     "handing a flat pack to somebody else."),
]
