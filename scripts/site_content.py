#!/usr/bin/env python3
"""
Site content and SEO model for Toronto Millworks.

Every fact, page and line of copy the generator needs lives here (services,
FAQ, process) or beside it (locations.py, guides.py). Edit, then run

    python3 scripts/build_site.py

Rules for this file
  * No em dashes. Copy uses commas, full stops or "and".
  * No invented numbers: no years in business, project counts, ratings,
    percentages or prices. Anything the business has not confirmed stays
    empty and the generator leaves it out.
"""

# The one place the live origin is declared. Canonicals, sitemap, schema,
# Open Graph and llms.txt are all derived from it.
ORIGIN = "https://toronto-millworks.vercel.app"

BUILD_DATE = "2026-10-01"          # feeds <lastmod>, dateModified and the footer

SITE = {
    "name": "Toronto Millworks",
    "legal": "Toronto Millworks",
    "origin": ORIGIN,
    "lang": "en-CA",
    # UNCONFIRMED. This address has never been verified with the business and
    # every enquiry the site generates goes to it. Confirm before launch.
    "email": "hello@torontomillworks.ca",
    "street": "2585 Drew Rd Unit 7",
    "locality": "Mississauga",
    "neighbourhood": "Malton",
    "region": "ON",
    "region_name": "Ontario",
    "postal": "L4T 1G1",
    "country": "CA",
    "lat": 43.7015416,
    "lon": -79.6576688,
    "tagline": "Custom millwork, cabinetry and interior renovation for Toronto and the GTA.",
    # Left empty on purpose. Fill these in and the generator adds them to the
    # page, the schema and llms.txt; leave them and nothing is guessed.
    "phone": "",
    "founded": "",
    "same_as": [],
    # A form backend (Formspree, Basin, Getform or your own). While empty, the
    # quote form composes a complete email in the visitor's mail app instead.
    "form_endpoint": "",
    "radius_km": 120,
}


# ── services ─────────────────────────────────────────────────────────────────
SERVICES = [
    {
        "slug": "custom-kitchens",
        "nav": "Custom Kitchens",
        "h1": "Custom Kitchens in Toronto",
        "title": "Custom Kitchen Cabinets Toronto | Toronto Millworks",
        "desc": ("Custom kitchen cabinets for Toronto and GTA homes, measured on site, "
                 "drawn to scale, built in our Mississauga shop and installed by one team."),
        "lede": ("Kitchen cabinetry built to your room rather than a catalogue: measured on "
                 "site, drawn to scale, made in our shop and installed by the people who "
                 "built it."),
        "keywords": ("custom kitchens Toronto, custom kitchen cabinets Toronto, kitchen "
                     "cabinet maker Toronto, kitchen millwork GTA"),
        "blurb": "Cabinetry, islands, pantries and sculleries, built to the room.",
        "kind": "Residential",
        "statement": ("A kitchen is the hardest room in the house to get right, because it "
                      "is the one where every millimetre is already spoken for."),
        "intro": ("We start from the room, not from a catalogue of box sizes. The site "
                  "measure records how far the walls lean, where the floor falls and where "
                  "the plumbing and venting really run, so the drawings describe your "
                  "kitchen rather than an ideal one. Every door, drawer and panel is then "
                  "made for that one room, which is why no filler strip is left doing the "
                  "work a good measure should have done."),
        "builds": [
            ("Full kitchen cabinetry", "Uppers, lowers and tall units in painted, stained or "
             "veneered finishes, with interiors planned around what you actually keep."),
            ("Islands and peninsulas", "Seating, storage, power and waste in one piece, sized "
             "to the clearances around it."),
            ("Pantries and sculleries", "Walk-in, reach-in, or a working scullery behind the "
             "main kitchen with shelving set to your jars."),
            ("Integrated appliances", "Panel-ready fridges, dishwashers and hood surrounds, "
             "with panels made to match the doors beside them."),
            ("Fitted interiors", "Drawer dividers, spice pull-outs, plate racks and cutlery "
             "inserts in the same timber as the cabinet."),
            ("Coffee and bar stations", "A tall cabinet with its own water, power and "
             "lighting, so the counters stay clear."),
        ],
        "process": [
            ("Measure", "We template the room on site, including the lean of the walls, the "
             "fall of the floor and the real position of every service."),
            ("Draw", "Plans and elevations show every door, drawer, filler and handle. You "
             "approve them before anything is cut."),
            ("Build", "Carcasses, doors and panels are made and finished in our shop, then "
             "dry fitted on the bench."),
            ("Install", "We level, fix and scribe to the walls, coordinate the counter "
             "template, then fit doors, panels and hardware."),
        ],
        "materials": [
            ("Painted", "Hard maple or MDF doors, sprayed for a smooth, durable finish in any colour."),
            ("White oak", "Rift or quarter sawn for straight, quiet grain, finished clear or stained."),
            ("Walnut", "Dark and warm, at its best in veneered slab doors and island panels."),
            ("Veneers", "Sequence matched veneer on a stable core for long runs of flat doors."),
        ],
        "faq": [
            ("How much does a custom kitchen cost in Toronto?",
             "It depends on the size of the room, the materials, the finish and how much is "
             "built inside the cabinets. We quote from measured drawings rather than a per "
             "foot rate, so the number reflects your kitchen and not an average."),
            ("How long does a custom kitchen take?",
             "There are four stages: site measure and drawings, approval, shop fabrication, "
             "then installation. Approval usually moves the most, because it depends on how "
             "quickly finishes, hardware and appliances are chosen. You get a schedule with "
             "the quote."),
            ("Can you work from my designer's or architect's drawings?",
             "Yes. We take the design drawings, measure the room, and produce shop drawings "
             "that resolve the construction details. Your designer approves those before "
             "anything is built."),
            ("Do you supply countertops and appliances?",
             "We build and install the cabinetry, and coordinate with your counter "
             "fabricator and appliance supplier so templates, panels and clearances line up "
             "on the day."),
            ("Can new cabinets match the existing millwork in my house?",
             "Yes. We take profiles from existing trim and doors on site and make new work "
             "to match, so the kitchen reads as part of the house."),
        ],
        "drawing": "kitchen",
        "plates": ["base", "doors", "panel-corner"],
        "related": ["cabinetry-and-built-ins", "interior-renovation", "architectural-millwork"],
    },
    {
        "slug": "cabinetry-and-built-ins",
        "nav": "Cabinetry & Built-Ins",
        "h1": "Custom Cabinetry and Built-Ins",
        "title": "Custom Cabinetry & Built-Ins Toronto | Toronto Millworks",
        "desc": ("Custom built-in cabinetry for Toronto and GTA homes: media walls, "
                 "libraries, wardrobes, mudrooms and vanities, designed around the room."),
        "lede": ("Storage that reads as part of the architecture rather than furniture "
                 "pushed against a wall, designed around the room it lives in."),
        "keywords": ("custom cabinetry Toronto, built-ins Toronto, built-in cabinets, custom "
                     "wardrobes Toronto, media wall Toronto"),
        "blurb": "Media walls, libraries, wardrobes and mudrooms.",
        "kind": "Residential",
        "statement": "The best built-ins are the ones nobody can tell were added.",
        "intro": ("A built-in earns the name when it meets the floor, the walls and the "
                  "ceiling as if the house had been framed around it. That only happens when "
                  "it is drawn against the real room, out of square corners, baseboard "
                  "returns and the radiator behind it included, and scribed on site so there "
                  "is no gap left to hide with a strip of trim."),
        "builds": [
            ("Media walls and fireplace surrounds", "Cabinetry around the television and the "
             "fire, with ventilation, cable routes and speakers planned in."),
            ("Libraries and home offices", "Shelving at spans that never sag, desks with "
             "cable management, and lighting built in."),
            ("Wardrobes and dressing rooms", "Hanging, drawers and shelving arranged around "
             "what you own, with doors that close flush."),
            ("Mudrooms and entry benches", "Benches, boot storage and hooks built for wet "
             "coats and a family coming in at once."),
            ("Vanities and linen towers", "Bathroom cabinetry finished for humidity, with "
             "plumbing access designed in."),
            ("Under stair and alcove storage", "The awkward spaces stock furniture cannot "
             "use, made into drawers and cupboards."),
        ],
        "process": [
            ("Measure", "We record the room as it is: the lean of each wall, the floor level, "
             "and every outlet, vent and pipe the cabinetry has to work around."),
            ("Draw", "Elevations show shelving positions, door styles, lighting and hardware. "
             "You approve them before production."),
            ("Build", "Carcasses, shelving and faces are made and finished in our shop, then "
             "assembled and checked."),
            ("Install", "Built-ins are fixed, scribed to the walls and ceiling, and finished "
             "so the joins disappear."),
        ],
        "materials": [
            ("Painted", "Paint-grade hardwood and MDF for built-ins that take the room's colour."),
            ("Stained hardwood", "Oak, walnut or cherry for libraries and studies with warmth."),
            ("Veneered panels", "Stable, flat panels for wide doors and long runs of cabinetry."),
            ("Integrated lighting", "LED strips and shelf lights routed into the cabinetry, "
             "with drivers kept accessible."),
        ],
        "faq": [
            ("Do built-ins add value to a home?",
             "Well made built-ins use space furniture cannot, particularly in older houses "
             "with narrow footprints and irregular walls, and they stay with the house as "
             "part of the architecture."),
            ("Can you build around radiators, outlets and vents?",
             "Yes. We locate services during the site measure and design the cabinetry "
             "around them, with ventilated panels and access doors where they are needed."),
            ("Will long shelves sag over time?",
             "Not when they are designed for their load. We set shelf spans and thicknesses "
             "for what they will carry, and add support where books or records demand it."),
            ("Can built-ins be painted to match my walls?",
             "Yes. Paint-grade cabinetry can be finished in any colour, matched to a sample "
             "or a paint code."),
            ("Do you build closets as well as living room units?",
             "Yes. Wardrobes, walk-in closets and dressing rooms are built the same way as "
             "everything else: measured, drawn, made in our shop and fitted on site."),
        ],
        "drawing": "builtin",
        "plates": ["panel-corner", "sconce", "archway"],
        "related": ["custom-kitchens", "architectural-millwork", "interior-renovation"],
    },
    {
        "slug": "architectural-millwork",
        "nav": "Architectural Millwork",
        "h1": "Architectural Millwork and Panelling",
        "title": "Architectural Millwork Toronto | Panelling, Trim & Ceilings",
        "desc": ("Architectural millwork for Toronto and the GTA: wall panelling, coffered "
                 "ceilings, crown moulding, casings and stairs, with profiles milled to match."),
        "lede": ("The work that makes a room feel finished: panelling, cornice, casing and "
                 "ceiling detail, milled to profile and fitted to the space."),
        "keywords": ("architectural millwork Toronto, wall panelling Toronto, coffered "
                     "ceiling Toronto, crown moulding Toronto, custom trim profiles"),
        "blurb": "Panelling, coffered ceilings, cornice and trim.",
        "kind": "Residential",
        "statement": "Trim is where a house shows whether anyone was paying attention.",
        "intro": ("Architectural millwork is the joinery that belongs to the building rather "
                  "than to the furniture: wall panelling, ceilings, cornice, casings, "
                  "baseboard and stair details. In an older house it usually has to match "
                  "work that has been there for a century. In a new one it is often what "
                  "turns a set of rectangular rooms into architecture."),
        "builds": [
            ("Wall panelling", "Raised, flat or shaker panels, full height or as wainscot, "
             "laid out so the panels land evenly on every wall."),
            ("Coffered and tray ceilings", "Beam grids and tray details with cove lighting, "
             "set out from the room's real centre lines."),
            ("Crown moulding and cornice", "Built-up cornice in several members, sized to "
             "the height of the room."),
            ("Casings and baseboard", "Door and window casings, plinth blocks and baseboard "
             "in profiles that suit the house."),
            ("Stair details", "Newels, handrails, skirt boards and panelled stair walls."),
            ("Custom profiles", "Knives ground to match existing trim, so new runs sit beside "
             "the old without a visible join."),
        ],
        "process": [
            ("Measure", "We survey every wall, opening and ceiling, and take a section of any "
             "existing profile that has to be matched."),
            ("Draw", "Panel layouts, ceiling grids and moulding sections are drawn so the "
             "proportions are settled before production."),
            ("Build", "Profiles are run, panels are made and components are finished in the shop."),
            ("Install", "Panelling and trim are fitted, scribed to uneven walls and ceilings, "
             "then filled and finished in place."),
        ],
        "materials": [
            ("Paint-grade poplar", "Machines cleanly and holds a crisp profile under paint."),
            ("MDF mouldings", "Stable and smooth for long painted runs and wide panels."),
            ("Hardwood", "Oak, walnut or cherry where trim will be stained or left natural."),
            ("Matched profiles", "New trim shaped and sized to sit with original work."),
        ],
        "faq": [
            ("Can you reproduce heritage trim profiles?",
             "Yes. We take a section from the existing profile, grind a matching knife and "
             "run new stock from it."),
            ("Can panelling be installed on walls that are not straight?",
             "That is the normal case in older houses. Panels are laid out from the real "
             "wall and scribed on site so the reveals stay even."),
            ("Does a coffered ceiling need structural work?",
             "Usually not. Most coffered ceilings are a finished grid fixed to the existing "
             "framing. We check the framing, lighting and any sprinkler positions during the "
             "site measure."),
            ("Should trim be painted or stained?",
             "Painted trim is more forgiving and suits most interiors. Stained trim shows the "
             "timber and needs higher grade material and tighter joints."),
            ("Do you install panelling and ceilings in new builds?",
             "Yes. New homes are often where full height panelling and coffered ceilings make "
             "the biggest difference."),
        ],
        "drawing": "panelling",
        "plates": ["cornice", "coffer", "base"],
        "related": ["cabinetry-and-built-ins", "interior-renovation", "custom-kitchens"],
    },
    {
        "slug": "restaurant-and-bar-millwork",
        "nav": "Restaurant & Bar Millwork",
        "h1": "Restaurant and Bar Millwork",
        "title": "Restaurant & Bar Millwork Toronto | Toronto Millworks",
        "desc": ("Custom bars, back bars, service counters and banquettes for restaurants, "
                 "bars and cafes across the GTA, shop drawn and installed to your schedule."),
        "lede": ("Bars, back bars, service counters and banquettes that look right on opening "
                 "night and still hold up after thousands of services."),
        "keywords": ("restaurant millwork Toronto, bar millwork Toronto, custom bar Toronto, "
                     "restaurant fit out Toronto, banquette seating Toronto"),
        "blurb": "Bars, back bars, counters and banquettes.",
        "kind": "Commercial",
        "statement": ("A bar is furniture that has to survive a Saturday night, every Saturday "
                      "night."),
        "intro": ("Hospitality millwork is built for two audiences: the guests who see it and "
                  "the staff who work behind it. The front has to carry the design. The back "
                  "has to fit the equipment, the drainage and the way your team moves during "
                  "a rush. We work from your designer's drawings or help develop them, then "
                  "build in our shop while the other trades finish, so the install takes days "
                  "rather than weeks."),
        "builds": [
            ("Bars and back bars", "Bar dies, footrails, bottle displays and back bar "
             "cabinetry built around the equipment schedule."),
            ("Service counters and host stands", "Counters that hold the POS, the menus and "
             "the traffic of a full room."),
            ("Banquettes and booths", "Fixed seating on frames made for daily use, with the "
             "upholstery coordinated."),
            ("Cafe counters", "Coffee bars and pickup counters with room for the machine, the "
             "grinders and storage underneath."),
            ("Feature walls and shelving", "Display shelving, slatted walls and feature panels "
             "that give the room its character."),
            ("Washroom vanities", "Commercial vanities and panelling that cope with water and "
             "heavy use."),
        ],
        "process": [
            ("Design intent", "We work from your designer's drawings and the equipment "
             "schedule, or help develop the details while the design is early."),
            ("Shop drawings", "Every piece is drawn with construction, finishes and equipment "
             "openings, and submitted for approval."),
            ("Fabrication", "Built and finished in our shop while the other trades complete the "
             "space, so time on site is short."),
            ("Install", "Fitted in an agreed window, coordinated with the plumber, the "
             "electrician and the equipment installer."),
        ],
        "materials": [
            ("Tops", "Stone, quartz and solid surface, coordinated so the millwork is ready "
             "for the fabricator's template."),
            ("Hardwood faces", "Oak, walnut or reclaimed timber for bar fronts and feature panels."),
            ("Durable finishes", "Catalysed finishes chosen for cleaning, spills and wear."),
            ("Metal details", "Footrails, edge trims and kick plates coordinated with the "
             "metal fabricator."),
        ],
        "faq": [
            ("Can you build to our designer's drawings?",
             "Yes. We produce shop drawings from the design drawings and the equipment "
             "schedule, and submit them for approval before anything is built."),
            ("Can you work to our opening date?",
             "That is how hospitality work is planned. We build in the shop while the space "
             "is being finished, then install in a window agreed with your contractor."),
            ("Do you install fridges, glass washers and draft systems?",
             "We build the openings, ventilation and access to suit each unit's "
             "specifications, and coordinate with the installer who connects it."),
            ("What finishes stand up to restaurant use?",
             "Hard wearing catalysed finishes on the faces, durable tops, and protection at "
             "kick and footrail height where boots and stools wear surfaces down."),
            ("Do you work under general contractors?",
             "Yes. Hospitality millwork is often a package under a general contractor, and we "
             "work to their schedule and site rules."),
        ],
        "drawing": "bar",
        "plates": ["finished", "counter", "feature"],
        "related": ["commercial-fit-outs", "office-millwork", "custom-kitchens"],
    },
    {
        "slug": "office-millwork",
        "nav": "Office Millwork",
        "h1": "Office Millwork and Reception Desks",
        "title": "Office Millwork Toronto | Reception Desks & Boardrooms",
        "desc": ("Custom office millwork across Toronto and the GTA: reception desks, "
                 "boardroom credenzas, staff kitchens and storage walls, built in our shop."),
        "lede": ("Reception desks, meeting rooms, staff kitchens and storage walls that give "
                 "an office its character and make it easier to work in."),
        "keywords": ("office millwork Toronto, reception desk Toronto, boardroom millwork, "
                     "office cabinetry Toronto, office millwork Mississauga"),
        "blurb": "Reception desks, boardrooms and staff kitchens.",
        "kind": "Commercial",
        "statement": "The reception desk is the first handshake a company makes.",
        "intro": ("Office millwork does two jobs at once. It presents the company to clients "
                  "and visitors, and it makes daily work easier for the people who use the "
                  "space. We build reception desks, meeting room credenzas, staff kitchens, "
                  "storage walls and private office joinery, coordinated with your designer, "
                  "your furniture supplier and the building's rules."),
        "builds": [
            ("Reception desks", "Desks with a transaction ledge, cable management, the "
             "company's identity built in, and an accessible counter where the code calls for one."),
            ("Boardrooms and meeting rooms", "Credenzas, AV walls and storage that keep "
             "screens, cables and supplies out of sight."),
            ("Staff kitchens and coffee points", "Hard wearing cabinetry for kitchens that "
             "serve a whole floor."),
            ("Storage walls and lockers", "Full height storage, mail rooms and personal "
             "lockers for flexible workplaces."),
            ("Private offices", "Desks, shelving and wall units built to the room."),
            ("Feature and acoustic walls", "Slatted timber, panelling and acoustic finishes "
             "that soften an open plan."),
        ],
        "process": [
            ("Brief", "We review the design drawings, the furniture layout and the building's "
             "rules for deliveries and after hours work."),
            ("Shop drawings", "Each piece is drawn with materials, power and data positions, "
             "and submitted for approval."),
            ("Fabrication", "Built and finished in our shop so site work is mostly assembly."),
            ("Install", "Scheduled around your move-in date and the building, including after "
             "hours where the building requires it."),
        ],
        "materials": [
            ("High pressure laminates", "Hard wearing surfaces for kitchens, storage and busy areas."),
            ("Veneers", "Wood veneers for reception and boardroom pieces that need warmth."),
            ("Solid surface", "Seamless tops for reception desks and kitchens."),
            ("Acoustic panels", "Slatted and perforated timber over acoustic backing."),
        ],
        "faq": [
            ("Can you build a reception desk with our logo?",
             "Yes. Logos can be routed, inlaid or mounted on a reception desk, coordinated "
             "with your signage supplier where needed."),
            ("Can you work after hours in an occupied building?",
             "Yes, where the building allows it. We plan noisy work and deliveries around "
             "the building's rules and your team's hours."),
            ("Do you supply office furniture?",
             "We build the fitted millwork, such as desks, storage, credenzas and kitchens, "
             "and coordinate with your furniture supplier so fitted and loose pieces work "
             "together."),
            ("Can power and data be built into the millwork?",
             "Yes. Grommets, power modules and cable routes are drawn into the shop drawings "
             "and coordinated with your electrician."),
            ("Do you work on office renovations as well as new fit-outs?",
             "Yes. Many projects replace a reception desk, kitchen or storage in a working "
             "office, phased so the space stays in use."),
        ],
        "drawing": "reception",
        "plates": ["feature", "base", "doors"],
        "related": ["commercial-fit-outs", "restaurant-and-bar-millwork", "cabinetry-and-built-ins"],
    },
    {
        "slug": "commercial-fit-outs",
        "nav": "Commercial Fit-Outs",
        "h1": "Commercial Millwork and Fit-Outs",
        "title": "Commercial Millwork Toronto | Fit-Outs & Millwork Packages",
        "desc": ("Commercial millwork packages for contractors, designers and owners across "
                 "the GTA: shop drawings, fabrication and install for retail and hospitality."),
        "lede": ("Millwork packages for general contractors, designers and property owners: "
                 "shop drawn, built in our shop and installed to the programme."),
        "keywords": ("commercial millwork Toronto, millwork contractor Toronto, commercial fit "
                     "out Toronto, retail millwork Toronto, millwork shop drawings"),
        "blurb": "Millwork packages for contractors and designers.",
        "kind": "Commercial",
        "statement": ("Commercial work is judged on two things: how it looks at handover, and "
                      "whether handover happened on the day it was meant to."),
        "intro": ("We take on the millwork scope of commercial projects: retail, hospitality, "
                  "offices and amenity spaces. That means reading the architectural drawings, "
                  "producing shop drawings and samples for approval, building in our shop "
                  "while the site progresses, and installing in a defined window. One team "
                  "handles all of it, so questions are answered by the people building the work."),
        "builds": [
            ("Retail fixtures", "Cash desks, display walls, shelving systems and fitting rooms."),
            ("Hospitality packages", "Bars, counters, banquettes and feature walls for "
             "restaurants and hotels."),
            ("Office packages", "Reception, kitchens, storage and meeting room joinery."),
            ("Amenity spaces", "Lobbies, lounges, party rooms and fitness areas in "
             "residential buildings."),
            ("Shop drawings and samples", "Drawings, finish samples and submittals prepared "
             "for approval before fabrication."),
            ("Phased installs", "Work planned around occupied buildings, after hours windows "
             "and the other trades."),
        ],
        "process": [
            ("Tender", "We price from the architectural drawings and specifications, with "
             "clarifications wherever the drawings leave a question."),
            ("Submittals", "Shop drawings, samples and finish schedules go out for approval "
             "before production."),
            ("Fabrication", "Built and finished in our shop while the site progresses."),
            ("Install", "Delivered and installed in the agreed window, with deficiencies "
             "closed out quickly."),
        ],
        "materials": [
            ("Laminates and veneers", "Specified surfaces sourced to the finish schedule."),
            ("Solid surface and quartz", "Tops coordinated with the fabricator."),
            ("Hardwood", "Feature pieces in solid or reclaimed timber."),
            ("Hardware", "Specified hardware, locks and accessories fitted to the schedule."),
        ],
        "faq": [
            ("Do you price from tender drawings?",
             "Yes. We price from the architectural drawings and specifications, and list "
             "clarifications wherever the drawings leave a question open."),
            ("Do you provide shop drawings and samples?",
             "Yes. Shop drawings, finish samples and submittals are prepared and approved "
             "before fabrication."),
            ("Can you meet a fixed turnover date?",
             "That is how commercial programmes work. We build off site while the space is "
             "finished, then install in an agreed window."),
            ("Do you take on work outside Toronto?",
             "Yes, across the region within about 120 km of our Mississauga shop, from "
             "Hamilton and Niagara to Barrie and Durham."),
            ("Who answers our questions during the project?",
             "The same team that draws and builds the work answers site questions, which "
             "keeps decisions quick."),
        ],
        "drawing": "retail",
        "plates": ["shell", "carcass", "lit"],
        "related": ["restaurant-and-bar-millwork", "office-millwork", "interior-renovation"],
    },
    {
        "slug": "interior-renovation",
        "nav": "Interior Renovation",
        "h1": "Interior Renovation in Toronto",
        "title": "Interior Renovation Toronto | Millwork-Led Renovations",
        "desc": ("Millwork-led interior renovation for Toronto and GTA homes: kitchens, "
                 "bathrooms, basements and whole rooms, with the joinery built in our shop."),
        "lede": ("Renovations where the joinery, the surfaces and the finishing are planned "
                 "together, so the cabinetry and the room are built to the same standard."),
        "keywords": ("interior renovation Toronto, home renovation Toronto, kitchen "
                     "renovation Toronto, basement renovation, millwork renovation GTA"),
        "blurb": "Kitchens, bathrooms and whole rooms, millwork first.",
        "kind": "Residential",
        "statement": ("When the joinery is designed last, it gets squeezed into whatever space "
                      "is left."),
        "intro": ("A millwork-led renovation starts from the cabinetry and trim instead of "
                  "fitting them in at the end. The layout, the services and the finishes are "
                  "resolved on the same drawings, so the outlet lands where the cabinet needs "
                  "it and the ceiling height suits the cornice. We coordinate the trades the "
                  "joinery depends on, and build the millwork in our own shop."),
        "builds": [
            ("Kitchen renovations", "New layouts, cabinetry built in our shop, and the "
             "surfaces and lighting around them."),
            ("Bathroom renovations", "Vanities, linen storage and panelling, coordinated "
             "with tile and plumbing."),
            ("Basements and attics", "Finished spaces with fitted storage built into awkward "
             "heights and angles."),
            ("Trim and ceiling restoration", "New or matched trim, panelling and ceiling "
             "details throughout a house."),
            ("Room by room", "Single rooms done properly, from a dining room to a principal suite."),
            ("Finishing", "Filling, sanding and painting of the millwork in place."),
        ],
        "process": [
            ("Survey", "We measure the house, record existing services and agree what stays "
             "and what goes."),
            ("Drawings", "Layouts and elevations resolve millwork, services and finishes on "
             "the same set of drawings."),
            ("Build", "Cabinetry and trim are made in our shop while the site work proceeds."),
            ("Install and finish", "Millwork is fitted, scribed and finished in place, and "
             "the room is handed back complete."),
        ],
        "materials": [
            ("Cabinetry", "Painted, stained or veneered, built in our shop."),
            ("Trim", "Profiles chosen or matched to suit the house."),
            ("Surfaces", "Counters, tile and flooring coordinated with the millwork."),
            ("Lighting", "Integrated lighting planned with the cabinetry."),
        ],
        "faq": [
            ("Do you handle permits?",
             "We advise on what a project needs and work with the drawings and consultants a "
             "permit application requires. Interior work that leaves structure, plumbing and "
             "fire separations alone often needs none, and we confirm that early."),
            ("Can you renovate one room at a time?",
             "Yes. Single room projects are common, particularly kitchens, bathrooms and "
             "principal suites."),
            ("Can we live in the house during the renovation?",
             "Often, yes. Because the joinery is built in our shop, time on site is shorter "
             "and the dusty work is concentrated into fewer days."),
            ("Who manages the other trades?",
             "We coordinate the trades the millwork depends on, such as electrical, plumbing "
             "and tile, so the cabinetry and the room come together in the right order."),
            ("Do you renovate condos?",
             "Yes. Condo work is planned around the building's rules for elevators, "
             "deliveries and noise, which we confirm with management before the install."),
        ],
        "drawing": "plan",
        "plates": ["room", "doors", "sconce"],
        "related": ["custom-kitchens", "cabinetry-and-built-ins", "architectural-millwork"],
    },
]

SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}


# ── how every project runs (home, about, services hub) ──────────────────────
PROCESS = [
    ("Measure", "We come to the room and template it as it really is: the lean of every "
     "wall, the fall of the floor, and the services hidden behind them.", "measure"),
    ("Draw", "Plans and elevations show every door, panel, profile and handle. You approve "
     "them before a single board is cut, which is where changes are cheap.", "draw"),
    ("Build", "Everything is made, finished and dry fitted in our Mississauga shop, so "
     "problems are found on the bench instead of in your room.", "build"),
    ("Install", "The same team installs, scribes to the walls and finishes in place, then "
     "hands back a room that looks as if it was always that way.", "install"),
]


# ── FAQ, grouped ─────────────────────────────────────────────────────────────
FAQ_GROUPS = [
    ("Cost and quotes", [
        ("How much does custom millwork cost?",
         "It depends on the size of the piece, the materials, the finish and the work inside "
         "it. We quote from measured drawings rather than a per foot rate, so the price "
         "reflects the actual room. A painted poplar built-in and a rift white oak kitchen "
         "are different jobs even at the same length."),
        ("How do you prepare a quote?",
         "We start from your drawings, photos or dimensions, measure the room, and price from "
         "drawings that show exactly what will be built. If anything changes, the drawing and "
         "the price change together."),
        ("Is custom millwork more expensive than stock cabinets?",
         "Usually, because everything is made for one room. What the difference buys is fit, "
         "better materials and a piece that uses the space completely."),
    ]),
    ("Timing", [
        ("How long does a custom millwork project take?",
         "The schedule is set by four stages: site measure and drawings, approval, shop "
         "fabrication, then install. Approval is usually the stage that moves most, because it "
         "depends on how quickly finishes and hardware are decided."),
        ("Can you work to a fixed opening or move-in date?",
         "Yes. We plan drawings, fabrication and install backwards from the date, and tell you "
         "early what has to be decided by when."),
        ("How long are you on site?",
         "Because the work is built and dry fitted in our shop, time on site is a small part "
         "of the whole project. The schedule you receive with the quote sets out the install "
         "days."),
    ]),
    ("Process", [
        ("What is millwork?",
         "Millwork is woodwork made to measure for a specific building, as opposed to stock "
         "items bought off a shelf. It covers cabinetry, panelling, trim, stairs, doors and "
         "fitted furniture."),
        ("Do you provide drawings before work starts?",
         "Yes. Nothing is cut until you have approved elevations showing the layout, the "
         "finishes and the hardware."),
        ("Do you build in your own shop?",
         "Yes. Everything is made and dry fitted in our shop in Mississauga before it goes to "
         "site, and the same team installs it."),
        ("Do you handle installation and finishing?",
         "Yes. We install, scribe to the walls and finish on site rather than handing a flat "
         "pack to somebody else."),
        ("Can I visit the shop?",
         "Yes, by appointment, so someone is free to walk you through drawings, samples and "
         "the work on the bench."),
    ]),
    ("Materials", [
        ("What materials do you work with?",
         "Solid hardwood, veneered panel, painted poplar and MDF, and engineered substrates "
         "where stability matters more than grain. The right choice depends on the piece and "
         "where it sits."),
        ("Should my millwork be painted or stained?",
         "Paint suits most interiors and is more forgiving of seasonal movement. Stain shows "
         "the timber, so it needs higher grade material and tighter joints."),
        ("Can you match existing trim and cabinetry?",
         "Yes. We take a section from the existing profile, grind a knife to match and run new "
         "stock from it, which is how new work disappears into an older house."),
    ]),
    ("Where we work", [
        ("Which areas do you serve?",
         "Toronto and the region around it, up to about 120 km from our shop in Mississauga: "
         "Peel, Halton, Hamilton, Niagara, York, Durham, Simcoe, Dufferin, Wellington, "
         "Waterloo and Brant. Our service areas page lists every town."),
        ("Do you work on commercial projects as well as homes?",
         "Yes. Restaurants, bars, cafes, offices and retail, as well as kitchens, built-ins and "
         "architectural millwork for homes."),
        ("Do you work with designers, architects and contractors?",
         "Yes. We build from design drawings, produce shop drawings for approval, and work to "
         "the contractor's schedule and site rules."),
    ]),
]

FAQ = [qa for _, items in FAQ_GROUPS for qa in items]


def faq_pick(*questions):
    """A handful of site-level answers by question, for pages that need a few."""
    by_q = dict(FAQ)
    return [(q, by_q[q]) for q in questions]
