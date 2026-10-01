#!/usr/bin/env python3
"""
Guides: evergreen articles that answer the questions people search before they
ask for a quote. Informational intent, so they teach first and sell last.

Section bodies are lists. A plain string is a paragraph; ("ul", [...]) is a
list; ("table", header, rows) is a table. No em dashes, no invented prices.
"""

GUIDES = [
    {
        "slug": "how-custom-millwork-is-made",
        "title": "How Custom Millwork Is Made | From Measure to Install",
        "h1": "How custom millwork is made",
        "desc": ("A step by step guide to how custom millwork is made: the site measure, shop "
                 "drawings, milling, finishing, dry fitting and installation."),
        "lede": ("What happens between the first site visit and the day the joinery is "
                 "finished in your room, and why the order matters."),
        "keywords": "how custom millwork is made, millwork process, shop drawings, scribing cabinetry",
        "drawing": "draw",
        "sections": [
            ("It starts with the room", [
                "Custom millwork is made for one space and nowhere else. A stock cabinet is "
                "designed for an ideal room with plumb walls, a level floor and square corners. "
                "Real rooms, particularly older ones, have none of those, so everything that "
                "follows depends on recording the room as it actually is.",
            ]),
            ("The site measure", [
                "A proper site measure records far more than overall dimensions. We take "
                "readings at several heights because walls lean, check diagonals because "
                "corners are rarely square, and find the floor's high point because cabinets "
                "are levelled from it.",
                ("ul", [
                    "Overall dimensions at floor, counter and ceiling height.",
                    "Plumb and level readings on every wall the work touches.",
                    "Positions of outlets, switches, pipes, vents and radiators.",
                    "Window and door openings, sills and casings.",
                    "Sections of any existing trim that new work has to match.",
                ]),
            ]),
            ("Shop drawings", [
                "The measurements become drawings: plans, elevations and sections that show "
                "every door, drawer, shelf, reveal and handle position at scale, with a "
                "schedule of materials and finishes. This is the stage where changes are cheap. "
                "Moving a drawer on paper costs a few minutes; moving it after it is built "
                "costs a new cabinet.",
                "Nothing is cut until the drawings are approved. For commercial work they also "
                "go to the designer and the contractor, often with finish samples.",
            ]),
            ("Milling and machining", [
                "Sheet goods are cut to size and edged. Solid timber is dimensioned: flattened, "
                "squared and planed to thickness so it stays straight. Profiles such as "
                "mouldings and door edges are run on a moulder or shaper, and where new trim "
                "has to match old, a knife is ground to the profile taken on site.",
            ]),
            ("Finishing in the shop", [
                "Spraying in a shop gives a cleaner, harder and more even finish than brushing "
                "on site, because dust, temperature and curing time can be controlled. Doors and "
                "panels are finished before assembly so edges and backs are sealed as well as "
                "faces. Only fills and touch-ups are left for the room.",
            ]),
            ("Dry fitting", [
                "Before anything leaves, the assembly is put together on the bench. Reveals "
                "are checked, doors are hung and adjusted, drawers are run and hardware is "
                "tested. Problems found here are solved with tools to hand, instead of in your "
                "kitchen with the counter fabricator waiting.",
            ]),
            ("Installation and scribing", [
                "On site the work is levelled from the floor's high point, fixed to the "
                "structure and scribed: the edge that meets a wall is traced from the wall "
                "itself and cut to match it, so the gap disappears. Scribing is the reason a "
                "fitted piece looks built in rather than pushed against a wall.",
                "Counters are templated once the cabinets are fixed, doors and hardware are "
                "fitted and adjusted, and the last fills and touch-ups are done in place.",
            ]),
            ("Why the order matters", [
                "Each stage depends on the one before it. A careless measure produces wrong "
                "drawings, wrong drawings produce wrong parts, and wrong parts get fixed on site "
                "with filler strips and caulk. Doing the stages properly, in order, is most of "
                "what separates custom millwork from furniture that merely fits.",
            ]),
        ],
        "faq": [
            ("Why can't cabinets just be built from a floor plan?",
             "Floor plans show the room as designed, not as built. Walls lean, floors slope and "
             "services move, and only a site measure records those differences."),
            ("What is scribing?",
             "Scribing is tracing the shape of a wall onto the edge of a cabinet or panel and "
             "cutting it to match, so the joinery meets an uneven surface without a gap."),
            ("Why are shop drawings worth approving carefully?",
             "Because changes cost almost nothing on paper and a great deal once parts are "
             "built. The drawings are the last cheap moment to change your mind."),
        ],
        "services": ["custom-kitchens", "cabinetry-and-built-ins", "architectural-millwork"],
    },
    {
        "slug": "custom-cabinetry-cost",
        "title": "What Affects the Cost of Custom Cabinetry | Toronto Guide",
        "h1": "What affects the cost of custom cabinetry",
        "desc": ("The factors that decide what custom cabinetry costs: size, materials, finish, "
                 "door style, interiors, hardware and site conditions, and how to plan for them."),
        "lede": ("Why two kitchens of the same length can be priced very differently, and how "
                 "to spend where it shows."),
        "keywords": "custom cabinetry cost, custom kitchen cost Toronto, cabinet pricing factors, millwork quote",
        "drawing": "kitchen",
        "sections": [
            ("Why there is no honest per foot price", [
                "Per linear foot pricing is convenient and almost always misleading. Two "
                "kitchens of identical length can differ in materials, finish, the number of "
                "drawers, the height of the cabinets and the condition of the room, and each of "
                "those changes the work. A quote built from measured drawings is the only kind "
                "that describes your project.",
            ]),
            ("Size and complexity", [
                "The number of cabinets matters, but so does their shape. Tall units, corner "
                "solutions, angled ends, curved pieces and cabinets that run to a high ceiling "
                "all take more material and more labour than a straight run of standard boxes. "
                "Islands with seating, power and finished backs are effectively furniture "
                "finished on every side.",
            ]),
            ("Materials", [
                "Painted cabinetry is usually built from MDF or paint-grade hardwood. Stained or "
                "clear finished work needs timber selected for grain and colour, and the price "
                "moves with the species: white oak and walnut cost more than maple or poplar. "
                "Veneer on a stable core can deliver a premium species across wide panels at a "
                "lower cost than solid stock.",
                "The cabinet boxes matter too. Plywood and MDF cores, edge banding and back "
                "thickness all affect how a cabinet performs and what it costs.",
            ]),
            ("Door style and finish", [
                "A flat slab door is the simplest to make. A shaker door adds a frame and a "
                "panel, and a raised panel door adds profiles and more steps. Finish is often "
                "the larger cost: a sprayed paint finish in several coats, a stain and topcoat, "
                "or a high gloss lacquer each take different amounts of time, and two-tone "
                "kitchens double some of that work.",
            ]),
            ("What goes inside", [
                "Drawers cost more than doors because each one carries slides and its own box. "
                "Pull-outs, dividers, spice racks, waste systems, lift mechanisms and integrated "
                "lighting are all worth having, and all add up. Deciding which ones you will "
                "really use is one of the easiest ways to keep a budget under control.",
            ]),
            ("Hardware", [
                ("ul", [
                    "Hinges and drawer slides: soft close and full extension are standard on "
                    "good work; specialist mechanisms cost more.",
                    "Lift systems for upper cabinets and pocket door mechanisms for appliance "
                    "garages.",
                    "Handles and pulls, which range from modest to very expensive per piece.",
                ]),
            ]),
            ("Site conditions", [
                "Older houses take longer to fit because walls and floors are further from "
                "true, and every scribe takes time. Access matters too: a third floor walk-up "
                "or a condo with booked elevators changes how the work is delivered and how "
                "long the install takes.",
            ]),
            ("Changes after approval", [
                "Once drawings are approved and parts are cut, a change means redrawing and "
                "remaking. Settling finishes, appliances and hardware before approval is the "
                "single most effective way to keep both the price and the schedule steady.",
            ]),
            ("Spending where it shows", [
                ("ul", [
                    "Put the premium species and the best finish where they are seen every day.",
                    "Use paint-grade construction where a stained finish adds nothing.",
                    "Keep layouts simple where nobody will notice the difference.",
                    "Choose interior fittings for the way you cook, not the catalogue.",
                    "Ask for options in the quote so you can compare like with like.",
                ]),
            ]),
        ],
        "faq": [
            ("Why won't you quote a price per foot?",
             "Because it would describe an average kitchen rather than yours. Materials, finish, "
             "interiors and site conditions change the work more than length does."),
            ("What is the biggest single cost driver?",
             "It varies by project, but finish and materials together usually outweigh layout. "
             "A sprayed paint finish or a premium hardwood moves the price more than a few extra "
             "cabinets."),
            ("How can I reduce the cost without lowering quality?",
             "Settle every decision before approval, use paint-grade construction where stain "
             "adds nothing, and be selective about specialist interior fittings."),
        ],
        "services": ["custom-kitchens", "cabinetry-and-built-ins", "interior-renovation"],
    },
    {
        "slug": "paint-grade-vs-stain-grade-millwork",
        "title": "Paint-Grade vs Stain-Grade Millwork Explained",
        "h1": "Paint-grade vs stain-grade millwork",
        "desc": ("Paint-grade and stain-grade millwork compared: the materials each uses, how "
                 "they are built and finished, how they age, and where each one belongs."),
        "lede": ("Two ways of building the same piece, chosen by the finish it will wear. "
                 "Here is what changes and how to choose."),
        "keywords": "paint grade vs stain grade, paint grade millwork, stain grade cabinets, millwork materials",
        "drawing": "panelling",
        "sections": [
            ("What the terms mean", [
                "Paint-grade millwork is made from materials chosen to take paint well. Joints "
                "and small defects are filled before finishing, because paint hides the "
                "material underneath. Stain-grade millwork is made from timber selected for "
                "its grain and colour, because the finish shows the wood. There is nowhere to "
                "hide a fill, so every joint has to be tight and every board has to match its "
                "neighbour.",
            ]),
            ("Paint-grade materials", [
                ("ul", [
                    "MDF: dense, flat and stable, with no grain to telegraph through paint. "
                    "Ideal for panels and mouldings, though its edges must be sealed against water.",
                    "Poplar: a soft hardwood that machines cleanly and holds a profile, used for "
                    "frames and trim.",
                    "Hard maple: very hard and fine grained, a durable choice for painted doors "
                    "that will see heavy use.",
                ]),
            ]),
            ("Stain-grade materials", [
                ("ul", [
                    "White oak: rift sawn for straight, quiet grain or quarter sawn for its ray "
                    "fleck. Takes clear finishes and stains well.",
                    "Walnut: rich brown and naturally dark, usually finished clear.",
                    "Cherry: fine grained and warm, and it darkens noticeably with light.",
                    "Maple: pale and hard, but it can stain unevenly without care.",
                    "Veneers: real timber on a stable core, used for wide flat panels where solid "
                    "wood would move.",
                ]),
            ]),
            ("How they are built differently", [
                "Stain-grade work takes longer. Boards are selected and arranged so grain and "
                "colour flow across a run of doors, and offcuts that do not match are set aside. "
                "Joinery has to be tight because a gap cannot be filled invisibly. Paint-grade "
                "work can use stable sheet materials for panels and fill small imperfections, "
                "which makes it faster and usually less expensive.",
            ]),
            ("How they age", [
                "Painted frames can show hairline lines at their joints as timber expands and "
                "contracts with the seasons. It is cosmetic and normal, and touch-ups are "
                "straightforward. Stained wood changes colour instead: cherry deepens to a "
                "red-brown, walnut can lighten in strong sun, and oak warms slightly. Scratches "
                "on stained work tend to blend into the grain, while scratches on paint show "
                "the material underneath.",
            ]),
            ("Which to choose", [
                ("table", ["Piece", "Usually", "Why"], [
                    ["Trim and casings", "Paint", "Long runs, many joints, and paint suits most interiors"],
                    ["Kitchens", "Either", "Paint for colour, stain for warmth, or both"],
                    ["Libraries and studies", "Stain", "Timber is the point of the room"],
                    ["Wall panelling", "Usually paint", "Stable materials across large areas"],
                    ["Bathroom vanities", "Either", "Seal every edge whichever you choose"],
                ]),
                "Mixing is common and often the best answer: a painted kitchen with a stained "
                "island, or painted panelling with a walnut bar.",
            ]),
        ],
        "faq": [
            ("Is paint-grade millwork lower quality?",
             "No. It uses different materials for a different finish. Well built paint-grade "
             "work is as durable as stain-grade, and often more stable."),
            ("Can paint-grade millwork be stained later?",
             "Not well. MDF cannot be stained, and paint-grade timber is not selected for "
             "matching grain. Decide on the finish before the work is built."),
            ("Why does painted trim crack at the corners?",
             "Solid timber moves with humidity, and the paint film across a joint shows that "
             "movement as a fine line. It is normal and easily touched up."),
        ],
        "services": ["architectural-millwork", "custom-kitchens", "cabinetry-and-built-ins"],
    },
    {
        "slug": "choosing-wood-for-cabinetry",
        "title": "Choosing Wood for Custom Cabinetry | Species Guide",
        "h1": "Choosing wood for custom cabinetry",
        "desc": ("A practical guide to wood for custom cabinetry: white oak, walnut, maple, "
                 "cherry, ash and poplar, plus plywood, MDF and veneer, and where each belongs."),
        "lede": ("How the common cabinet woods compare on hardness, colour and ageing, and "
                 "why sheet goods and veneer deserve a fair hearing."),
        "keywords": "wood for cabinets, best wood for kitchen cabinets, white oak cabinets, walnut cabinetry, cabinet materials",
        "drawing": "builtin",
        "sections": [
            ("Start with where the piece lives", [
                "The right wood depends on the room. A kitchen door is opened thousands of "
                "times a year, a vanity lives in humidity, a library sits in sunlight, and a "
                "bar front takes boots and stools. Hardness, stability, how the colour changes "
                "with light and how the finish wears all matter more than which species is "
                "fashionable.",
            ]),
            ("How the common species compare", [
                ("table", ["Species", "Janka hardness", "Colour", "With age"], [
                    ["Hard maple", "about 1,450 lbf", "Pale cream", "Yellows slightly"],
                    ["White oak", "about 1,360 lbf", "Light brown", "Warms to amber"],
                    ["White ash", "about 1,320 lbf", "Pale, oak-like grain", "Yellows slightly"],
                    ["Black walnut", "about 1,010 lbf", "Rich brown", "Can lighten in sun"],
                    ["Black cherry", "about 950 lbf", "Pinkish brown", "Darkens markedly"],
                    ["Yellow poplar", "about 540 lbf", "Cream with green streaks", "Used under paint"],
                ]),
                "Janka hardness is the force needed to press a steel ball halfway into the "
                "wood. Higher numbers resist dents better, though a good finish matters as much "
                "as the timber underneath.",
            ]),
            ("White oak", [
                "The most requested cabinet wood of recent years, and for good reason. It is "
                "hard, stable and, unlike red oak, has closed pores that resist water. Rift "
                "sawn boards give a straight, quiet grain; quarter sawn boards show the ray "
                "fleck that Arts and Crafts furniture made famous. It takes clear finishes and "
                "stains well.",
            ]),
            ("Walnut", [
                "Dark, warm and naturally rich, walnut rarely needs stain. It is softer than "
                "oak, so it suits doors, panels and furniture pieces more than a heavily used "
                "work surface. Veneered slab doors make the most of its figure across a run of "
                "cabinets.",
            ]),
            ("Maple and cherry", [
                "Hard maple is one of the most durable cabinet woods and one of the best for "
                "painted doors, because its fine grain gives a smooth surface. It can blotch "
                "under stain, so stained maple needs care. Cherry is fine grained and "
                "traditional, and it darkens markedly over its first years, which many people "
                "choose it for.",
            ]),
            ("Ash and poplar", [
                "Ash looks much like oak in a paler tone. In Ontario its supply has been "
                "affected by the emerald ash borer, so availability is worth checking early. "
                "Poplar is a soft, inexpensive hardwood that machines cleanly and is the "
                "standard for painted frames and trim.",
            ]),
            ("Plywood, MDF and particleboard", [
                ("ul", [
                    "Plywood: strong, relatively light and good at holding screws. A common "
                    "choice for cabinet boxes and shelves.",
                    "MDF: flat, stable and smooth, the best substrate for paint and for veneer, "
                    "but heavy and weak at holding screws in its edges.",
                    "Particleboard: economical and stable when faced with melamine or veneer, "
                    "widely used for cabinet boxes.",
                ]),
            ]),
            ("Veneer is not a compromise", [
                "Veneer is real wood sliced thin and laid on a stable core. Because the core "
                "does not move with the seasons, veneered panels stay flat where wide solid "
                "boards would cup. Veneer also allows sequence and book matching, so a whole "
                "wall of doors can show continuous grain. Most fine furniture and high end "
                "cabinetry relies on it.",
            ]),
        ],
        "faq": [
            ("What is the most durable wood for kitchen cabinets?",
             "Hard maple and white oak are both very hard and stable. The finish matters as "
             "much as the species, so choose them together."),
            ("Is white oak better than red oak?",
             "For cabinetry, usually. White oak has closed pores that resist water and a quieter "
             "grain when rift sawn. Red oak is porous and has a pinker tone."),
            ("Why do cherry cabinets get darker?",
             "Cherry reacts to light and oxygen and deepens in colour over its first years. It is "
             "a natural patina, not a defect."),
        ],
        "services": ["custom-kitchens", "cabinetry-and-built-ins", "architectural-millwork"],
    },
    {
        "slug": "custom-vs-semi-custom-vs-stock-cabinets",
        "title": "Custom vs Semi-Custom vs Stock Cabinets Compared",
        "h1": "Custom vs semi-custom vs stock cabinets",
        "desc": ("Custom, semi-custom and stock cabinets compared on fit, materials, choice, "
                 "lead time and cost, with an honest look at when each is the right call."),
        "lede": ("Three ways to buy cabinets, what you get with each, and when paying for "
                 "custom work is genuinely worth it."),
        "keywords": "custom vs semi custom cabinets, stock cabinets vs custom, custom cabinets worth it, kitchen cabinet options",
        "drawing": "kitchen",
        "sections": [
            ("Three ways to buy cabinets", [
                "Stock, semi-custom and custom cabinets are not grades of quality so much as "
                "different ways of fitting cabinetry to a room. Stock cabinets ask the room to "
                "fit the boxes. Custom cabinets make the boxes fit the room. Semi-custom sits "
                "in between.",
            ]),
            ("Stock cabinets", [
                "Stock cabinets are built in advance in standard widths, heights and depths, "
                "with a limited choice of door styles and finishes. Gaps between the boxes and "
                "the walls are closed with filler strips. They are the fastest and least "
                "expensive option, and for a rental, a laundry room or a tight budget they can "
                "be the right one.",
            ]),
            ("Semi-custom cabinets", [
                "Semi-custom cabinets start from a manufacturer's catalogue but allow "
                "modifications: different widths and depths, more finishes and more interior "
                "options. They are built to order, so lead times are longer than stock. The "
                "boxes still come in set increments, so fillers and panels still do some of the "
                "fitting.",
            ]),
            ("Custom cabinets", [
                "Custom cabinets are designed and built for one room. Any dimension, any "
                "material and any detail is possible, the cabinetry can be scribed to walls "
                "that are not straight, and it can match millwork already in the house. It "
                "takes the longest and usually costs the most, because nothing is drawn from a "
                "standard.",
            ]),
            ("Side by side", [
                ("table", ["", "Stock", "Semi-custom", "Custom"], [
                    ["Sizes", "Fixed increments", "Catalogue, modified", "Any dimension"],
                    ["Fit at walls", "Filler strips", "Fillers and panels", "Scribed to the wall"],
                    ["Materials", "Limited", "Wider range", "Anything suitable"],
                    ["Finishes", "A few", "Many", "Any, including matches"],
                    ["Lead time", "Shortest", "Weeks", "Longest"],
                    ["Relative cost", "Lowest", "Middle", "Highest"],
                ]),
            ]),
            ("When stock or semi-custom makes sense", [
                ("ul", [
                    "A rental or a house you expect to sell soon.",
                    "A standard room with straight walls and common dimensions.",
                    "A utility space where finish matters less than function.",
                    "A schedule that cannot wait for custom fabrication.",
                ]),
            ]),
            ("When custom earns its cost", [
                ("ul", [
                    "Older houses where walls, floors and ceilings are out of true.",
                    "Rooms with unusual dimensions, high ceilings or awkward corners.",
                    "Kitchens that need to match existing trim or cabinetry.",
                    "Designs that integrate appliances, lighting and storage closely.",
                    "Homes you plan to stay in, where fit and durability pay back over years.",
                ]),
            ]),
        ],
        "faq": [
            ("Are custom cabinets better quality than semi-custom?",
             "Not automatically. Quality depends on materials and construction. Custom work's "
             "real advantage is fit and flexibility."),
            ("Are custom cabinets worth it in an older house?",
             "Usually. Older rooms are rarely square, and custom cabinetry can be scribed to the "
             "walls instead of relying on filler strips."),
            ("Can custom and stock cabinets be mixed?",
             "Yes. A custom kitchen with stock cabinets in a laundry room is a sensible way to "
             "spend where it shows."),
        ],
        "services": ["custom-kitchens", "cabinetry-and-built-ins", "interior-renovation"],
    },
    {
        "slug": "planning-restaurant-bar-millwork",
        "title": "Planning Restaurant & Bar Millwork | Fit-Out Guide",
        "h1": "Planning millwork for a restaurant or bar",
        "desc": ("How to plan restaurant and bar millwork: when to involve the millworker, "
                 "equipment schedules, shop drawings, durable finishes and the install window."),
        "lede": ("What owners, designers and contractors can do early to make a hospitality "
                 "fit-out faster, cheaper and better on opening night."),
        "keywords": "restaurant millwork planning, bar construction, restaurant fit out, bar millwork Toronto, hospitality millwork",
        "drawing": "bar",
        "sections": [
            ("Bring the millwork in early", [
                "The bar is usually the most complicated piece of joinery in a restaurant, and "
                "its position decides where floor drains, water lines, conduit and data have "
                "to go. When the millwork is drawn early, those rough-ins land in the right "
                "places. When it is drawn late, something has to be moved, and it is rarely "
                "cheap.",
            ]),
            ("The equipment schedule sets the bar", [
                "Undercounter fridges, ice wells, glass washers, draft systems and POS stations "
                "each come with a specification sheet that gives dimensions, clearances and "
                "ventilation needs. The bar is built around those sheets, so the equipment "
                "schedule should be settled before the shop drawings are approved.",
                ("ul", [
                    "Confirm every unit's model and its ventilation direction.",
                    "Plan access for servicing compressors and drains.",
                    "Allow for the draft system's lines, cooling and towers.",
                    "Locate power and data for every POS and card terminal.",
                ]),
            ]),
            ("Shop drawings and approvals", [
                "Shop drawings show how each piece is built: materials, finishes, construction, "
                "equipment openings and fixing details. They go to the designer, the owner and "
                "the general contractor for approval, usually with finish samples. Changes made "
                "at this stage are cheap. Changes made after fabrication starts are not.",
            ]),
            ("Build for the service, not the rendering", [
                "A rendering shows the guest's side. The staff side decides whether the room "
                "works on a busy night: where the speed rail sits, how far the bartender walks "
                "for ice, where clean glasses go and how the floor drains.",
                ("table", ["Element", "Typical height"], [
                    ["Bar top for standing guests", "about 42 in (1,070 mm)"],
                    ["Counter height seating", "about 36 in (915 mm)"],
                    ["Dining table height", "about 30 in (760 mm)"],
                    ["Footrail above the floor", "about 7 to 9 in (180 to 230 mm)"],
                ]),
                "Accessible sections of counters and bars are required in many settings under "
                "the building code, and are worth planning from the start.",
            ]),
            ("Surfaces that last", [
                "Restaurant millwork is cleaned constantly and kicked often. Tops in stone, "
                "quartz or solid surface, catalysed finishes on the faces and protection at kick "
                "and footrail height keep it looking new for longer. Ontario's food premises "
                "rules expect surfaces in food areas to be smooth, durable and easy to clean, "
                "and your public health inspector is the final word on what passes.",
            ]),
            ("Fitting the install into the fit-out", [
                "Millwork is built in the shop while the space is finished, then installed in "
                "a defined window. A typical sequence:",
                ("ul", [
                    "Rough-ins for plumbing, electrical and data, positioned from the shop drawings.",
                    "Walls closed, primed and floors finished where the millwork sits on them.",
                    "Millwork installed, then tops templated and fitted.",
                    "Equipment set and connected by the installers.",
                    "Final paint, touch-ups and inspection.",
                ]),
            ]),
        ],
        "faq": [
            ("When should we contact a millworker for a restaurant?",
             "As soon as the layout is settled, and before rough-ins are placed. The bar and "
             "counters decide where drains, water and power have to go."),
            ("How long does restaurant millwork take?",
             "It depends on scope and approvals. Most of the work happens in the shop while the "
             "space is being finished, so the install itself is the short part."),
            ("Who is responsible for health code requirements?",
             "Your designer specifies surfaces and your public health inspector approves them. "
             "We build to the approved specification."),
        ],
        "services": ["restaurant-and-bar-millwork", "commercial-fit-outs", "office-millwork"],
    },
]

GUIDE_BY_SLUG = {g["slug"]: g for g in GUIDES}
