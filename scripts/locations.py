#!/usr/bin/env python3
"""
Service areas: every major municipality within 120 km of the shop.

Coordinates come from scripts/data/geocoded_raw.json (OpenStreetMap Nominatim),
never typed by hand. Distances are straight-line from 2585 Drew Rd, Mississauga
and are computed, not written.

Each place carries its own copy. A location page that only swaps the town name
is a doorway page, so every entry below says something true about that place:
the housing stock, the commercial streets, and what that means for joinery.

No em dashes anywhere in this file.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SHOP = (43.7015416, -79.6576688)
RADIUS_KM = 120

_RAW = {r["name"]: r for r in json.load(open(os.path.join(HERE, "data", "geocoded_raw.json")))}

# service slugs, so each place can lead with the work it actually asks for
K, B, A, R, O, C, I = ("custom-kitchens", "cabinetry-and-built-ins", "architectural-millwork",
                       "restaurant-and-bar-millwork", "office-millwork",
                       "commercial-fit-outs", "interior-renovation")
HOME = [K, B, A, I, R, O, C]
HERITAGE = [A, B, K, I, R, O, C]
HOSPITALITY = [R, K, A, B, C, I, O]
OFFICE = [O, K, B, C, R, A, I]
LAKESIDE = [B, K, I, A, R, O, C]


def km(a, b):
    r = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def bearing(a, b):
    """Compass point from the shop, for copy like 'north of the shop'."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return ["north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest"][int((deg + 22.5) // 45) % 8]


def place(slug, name, region, geo, areas, lede, body, focus, kind="home"):
    raw = _RAW[geo]
    lat, lon = raw["lat"], raw["lon"]
    d = km(SHOP, (lat, lon))
    if d > RADIUS_KM:
        raise SystemExit(f"{name} is {d:.1f} km from the shop, outside the radius")
    return {"slug": slug, "name": name, "region": region, "lat": lat, "lon": lon,
            "km": round(d), "km_exact": round(d, 1), "dir": bearing(SHOP, (lat, lon)),
            "areas": areas, "lede": lede, "body": body, "focus": focus, "kind": kind}


LOCATIONS = [
    # ── City of Toronto ──────────────────────────────────────────────────
    place("toronto", "Toronto", "Toronto", "Toronto",
          ["The Annex", "Rosedale", "Forest Hill", "Cabbagetown", "Leslieville", "The Beaches"],
          "From bay-and-gable Victorians in Cabbagetown to downtown condo suites, Toronto "
          "gives us the widest range of rooms we work in.",
          "Most of the old city was built before anyone expected a wall to be plumb. "
          "Victorian and Edwardian houses in the Annex and Riverdale have plaster that has "
          "moved for a century, and condo suites downtown have no plaster at all, just "
          "concrete that has to be cored before anything is fixed to it. Both get templated "
          "on site before a panel is cut, which is why built-ins sit flush and trim meets the "
          "ceiling without a filler strip.",
          HERITAGE, "heritage"),
    place("north-york", "North York", "Toronto", "North York",
          ["Willowdale", "Bayview Village", "York Mills", "Hoggs Hollow", "Don Mills", "Armour Heights"],
          "Postwar lots rebuilt as large custom homes, mid-century Don Mills, and the "
          "towers along Yonge and Sheppard.",
          "A lot of North York work happens in houses that were rebuilt rather than "
          "renovated, where the ceilings are high and the walls are long and straight. That "
          "suits full height panelling, deep pantries and built-in libraries that would "
          "overwhelm a narrow Victorian. In Don Mills the brief is usually the opposite: keep "
          "the low mid-century lines and make the joinery do more with less height.",
          HOME),
    place("etobicoke", "Etobicoke", "Toronto", "Etobicoke",
          ["The Kingsway", "Humber Valley Village", "Mimico", "Humber Bay Shores", "Long Branch", "Islington Village"],
          "Tudor-revival houses in the Kingsway, lakeside streets in Mimico and Long Branch, "
          "and the condo towers of Humber Bay Shores.",
          "The Kingsway's houses from the 1930s carry heavy casings, plaster cornice and "
          "leaded windows, and new joinery there has to read as original. At Humber Bay "
          "Shores the constraints change completely: service elevator bookings, short install "
          "windows and building rules on noise. We plan both kinds of job around what the "
          "building allows before anything leaves the shop.",
          HERITAGE, "condo"),
    place("scarborough", "Scarborough", "Toronto", "Scarborough",
          ["Cliffside", "Birch Cliff", "Guildwood", "Highland Creek", "Agincourt", "Wexford"],
          "Bungalows and backsplits across Scarborough, larger lots along the Bluffs, and "
          "restaurant plazas on every major road.",
          "Opening up a compartmented postwar plan is the most common Scarborough brief we "
          "see. Once a wall comes out, the storage it used to carry has to go somewhere, and "
          "fitted cabinetry is usually the answer. On the commercial side, the plazas along "
          "Sheppard and Kennedy are full of family restaurants that need counters and seating "
          "built to survive a full service every day.",
          [I, B, K, R, A, O, C]),
    place("east-york", "East York", "Toronto", "East York",
          ["Leaside", "Governor's Bridge", "Bennington Heights", "Woodbine Heights", "Thorncliffe Park", "Pape Village"],
          "Leaside's solid brick houses from the 1930s and 40s, and the compact postwar "
          "bungalows across the rest of East York.",
          "Leaside houses tend to have good bones and small kitchens, so the work is usually "
          "about finding storage without losing the original character: built-ins under the "
          "stairs, panelled dining rooms, kitchens that borrow space from a pantry. Further "
          "east, the storey-and-a-half bungalows are often being opened up or extended, and "
          "the millwork has to tie the old and new parts of the house together.",
          [B, K, A, I, R, O, C], "heritage"),

    # ── Peel ─────────────────────────────────────────────────────────────
    place("mississauga", "Mississauga", "Peel", "Mississauga",
          ["Port Credit", "Mineola", "Lorne Park", "Streetsville", "Erin Mills", "Meadowvale", "Malton"],
          "Our shop is in Mississauga, near Pearson, so this is home ground: lakeside houses "
          "in Port Credit and Mineola through to offices along the airport corridor.",
          "Mineola and Lorne Park have big ravine lots and older houses that are being "
          "renovated or replaced, which is where full kitchens, panelled rooms and coffered "
          "ceilings come in. Streetsville keeps a village main street with its own heritage "
          "character. The commercial side is offices, restaurants and showrooms, where "
          "installs have to fit a fixed opening date and a landlord's building rules.",
          [K, O, B, A, R, C, I], "home-base"),
    place("brampton", "Brampton", "Peel", "Brampton",
          ["Downtown Brampton", "Peel Village", "Heart Lake", "Castlemore", "Springdale", "Bramalea"],
          "Large new homes in Castlemore, older streets around downtown and Peel Village, "
          "and a short drive from our shop.",
          "New builds in Castlemore and Springdale usually arrive with generous ceilings and "
          "builder-grade finishes, which makes them ideal for coffered ceilings, wall "
          "panelling and kitchens upgraded to proper custom cabinetry. Around downtown "
          "Brampton and Peel Village the houses are older and smaller, and fitted storage "
          "does more of the work.",
          HOME),
    place("caledon", "Caledon", "Peel", "Caledon",
          ["Bolton", "Caledon East", "Caledon Village", "Inglewood", "Belfountain", "Palgrave"],
          "Country properties, estate homes and converted farmhouses across Caledon, from "
          "Bolton to the hills around Belfountain.",
          "Caledon jobs tend to be large and individual: a farmhouse kitchen in an old stone "
          "house, a mudroom built for boots and dogs, a library in a new estate home on the "
          "Oak Ridges Moraine. Older houses here have often been extended more than once, so "
          "the site measure matters even more than usual.",
          [K, B, A, I, R, O, C], "rural"),

    # ── Halton ───────────────────────────────────────────────────────────
    place("oakville", "Oakville", "Halton", "Oakville",
          ["Old Oakville", "Bronte", "Glen Abbey", "Joshua Creek", "Eastlake", "Morrison"],
          "Lakefront estates in Eastlake and Morrison, heritage houses in Old Oakville, and "
          "family homes across Glen Abbey and Joshua Creek.",
          "Old Oakville's heritage streets ask for trim and panelling that respect the "
          "original house, and that usually means matching a profile rather than buying one. "
          "South of the QEW, larger homes take full height panelling, coffered ceilings and "
          "kitchens with a working scullery behind them. Further north, the newer "
          "subdivisions are where built-ins and kitchen upgrades are most common.",
          [K, A, B, I, R, O, C], "heritage"),
    place("burlington", "Burlington", "Halton", "Burlington",
          ["Downtown Burlington", "Roseland", "Aldershot", "Shoreacres", "Tyandaga", "Millcroft"],
          "Lakeshore homes in Roseland and Shoreacres, escarpment views around Tyandaga, and "
          "established family streets in Millcroft and Aldershot.",
          "Roseland and Shoreacres have some of Burlington's most established houses, with "
          "mature lots and rooms that suit traditional panelling and fitted libraries. The "
          "suburbs built through the 1980s and 90s are where we see the most kitchen "
          "replacements, often pairing new cabinetry with a reworked island and a built-in "
          "bench where a breakfast table used to be.",
          HOME),
    place("milton", "Milton", "Halton", "Milton",
          ["Old Milton", "Timberlea", "Dempsey", "Beaty", "Hawthorne Village", "Campbellville"],
          "A heritage main street in Old Milton, a great deal of new housing around it, and "
          "rural properties toward Campbellville and the escarpment.",
          "Much of Milton's housing is recent, so the work is often about turning a builder's "
          "kitchen and an empty great room into something that feels designed: a proper "
          "island, a media wall, a mudroom with real storage. In Old Milton and out toward "
          "Campbellville the houses are older and the brief leans toward matching existing "
          "trim and keeping a period feel.",
          [K, B, I, A, R, O, C]),
    place("halton-hills", "Halton Hills", "Halton", "Halton Hills",
          ["Georgetown", "Acton", "Glen Williams", "Limehouse", "Terra Cotta"],
          "Georgetown, Acton and the hamlets of Glen Williams, Limehouse and Terra Cotta, "
          "along the Credit River and the escarpment.",
          "Glen Williams and the older parts of Georgetown have heritage houses where new "
          "millwork needs to sit quietly beside original work. Rural properties around "
          "Limehouse and Terra Cotta bring larger projects: kitchens for big families, boot "
          "rooms, and built-ins in additions that have to look as though they were always "
          "there.",
          [A, K, B, I, R, O, C], "heritage"),

    # ── Hamilton ─────────────────────────────────────────────────────────
    place("hamilton", "Hamilton", "Hamilton", "Hamilton",
          ["Durand", "Kirkendall", "Westdale", "Corktown", "James Street North", "Locke Street"],
          "Century homes in Durand, Kirkendall and Westdale, and the restaurants and shops "
          "along James Street North and Locke Street.",
          "Hamilton has a remarkable stock of Victorian and Edwardian brick houses, many with "
          "original trim that is worth saving and plaster that is far from square. Restoring "
          "and extending that trim is precise work. On the commercial side, the independent "
          "restaurants, bars and cafes along James North and Locke are exactly the kind of "
          "fit-out where good millwork carries the whole room.",
          [A, R, K, B, I, O, C], "heritage"),
    place("ancaster", "Ancaster", "Hamilton", "Ancaster",
          ["Ancaster Village", "Meadowlands", "Fiddler's Green", "the Dundas Valley edge"],
          "Stone buildings in the old village, large family homes in Meadowlands, and estate "
          "properties along the edge of the Dundas Valley.",
          "Ancaster combines nineteenth century stone architecture with some of the area's "
          "larger modern homes, and both reward careful joinery. In the older houses that "
          "usually means deep window casings and trim matched to what survives. In newer "
          "homes it means scale: tall pantries, panelled studies and kitchens designed around "
          "a big family table.",
          [K, A, B, I, R, O, C], "heritage"),
    place("dundas", "Dundas", "Hamilton", "Dundas",
          ["Downtown Dundas", "King Street West", "Spencer Creek", "the Dundas Valley"],
          "A small town set in its own valley, with a heritage main street and houses that "
          "climb the escarpment on either side.",
          "Dundas houses are often older than they look from the street, with additions from "
          "several decades stitched together. Fitting cabinetry and trim to rooms like that is "
          "mostly a matter of measuring properly and scribing on site. The independent shops "
          "and cafes along King Street West bring the occasional small commercial job where "
          "the millwork has to suit a heritage storefront.",
          HERITAGE, "heritage"),
    place("stoney-creek", "Stoney Creek", "Hamilton", "Stoney Creek",
          ["Old Stoney Creek", "Battlefield", "Fruitland", "Winona", "Upper Stoney Creek"],
          "Newer subdivisions on the mountain and along the lake, the older core around "
          "Battlefield, and orchards and vineyards out toward Winona.",
          "Stoney Creek's growth means plenty of newer homes where the kitchen and the family "
          "room are the first things people want to improve. Along the lake and in the older "
          "streets near Battlefield, the houses are earlier and the work tends toward trim, "
          "built-ins and renovations that keep what is worth keeping.",
          HOME),

    # ── Niagara ──────────────────────────────────────────────────────────
    place("grimsby", "Grimsby", "Niagara", "Grimsby",
          ["Downtown Grimsby", "Grimsby Beach", "Grimsby on the Lake", "the escarpment"],
          "A lakeside town under the escarpment, from the painted Victorian cottages of "
          "Grimsby Beach to new condos on the lake.",
          "Grimsby Beach's cottages began as summer places and many have since become "
          "year-round homes, which means small rooms where every inch of storage counts. "
          "Newer houses and lakeside condos bring more standard projects: kitchens, vanities "
          "and built-ins. Wineries and restaurants along the bench of the escarpment are "
          "commercial work we take on too.",
          LAKESIDE, "lakeside"),
    place("lincoln", "Lincoln", "Niagara", "Lincoln",
          ["Beamsville", "Vineland", "Jordan Village", "Campden"],
          "Beamsville, Vineland and Jordan Village, in the middle of the Twenty Valley wine "
          "region.",
          "Lincoln's wineries, tasting rooms and inns are some of the most interesting "
          "commercial work in the region: tasting bars, retail walls and dining rooms that "
          "have to look good for visitors and survive a busy weekend. On the residential side "
          "there are century farmhouses and newer homes in Beamsville and Vineland, each with "
          "its own kind of kitchen.",
          HOSPITALITY, "hospitality"),
    place("st-catharines", "St. Catharines", "Niagara", "St. Catharines",
          ["Downtown St. Catharines", "Port Dalhousie", "Old Glenridge", "Western Hill", "Martindale"],
          "Niagara's largest city: older homes in Old Glenridge and Western Hill, Port "
          "Dalhousie on the lake, and a downtown full of restaurants.",
          "Old Glenridge and the streets around Montebello Park have some of the finest older "
          "houses in Niagara, and they deserve trim and cabinetry that match the original "
          "craftsmanship. Downtown and in Port Dalhousie, restaurants and bars make up much of "
          "the commercial work, where counters and back bars have to cope with a summer of "
          "full patios.",
          [A, R, K, B, I, O, C], "heritage"),
    place("niagara-on-the-lake", "Niagara-on-the-Lake", "Niagara", "Niagara-on-the-Lake",
          ["Old Town", "Queenston", "Virgil", "St. Davids", "Glendale"],
          "A heritage town, a wine region and a hospitality destination, from Old Town's "
          "early houses to the wineries around St. Davids.",
          "Old Town's heritage district has some of the best preserved early nineteenth "
          "century architecture in Ontario, and work there has to respect it, often matching "
          "profiles that no catalogue carries. Inns, restaurants and winery tasting rooms "
          "around Virgil and St. Davids are a large share of the commercial work, built to be "
          "photographed and built to last.",
          [A, R, K, B, C, I, O], "hospitality"),
    place("niagara-falls", "Niagara Falls", "Niagara", "Niagara Falls",
          ["Downtown Queen Street", "Stamford", "Chippawa", "Lundy's Lane", "Fallsview"],
          "Hotels, restaurants and attractions in the tourist district, and quieter "
          "residential streets in Stamford and Chippawa.",
          "Commercial millwork in Niagara Falls is mostly hospitality: hotel lobbies, "
          "restaurant interiors, bars and retail counters that see heavy daily use and need "
          "finishes chosen to cope with it. Residential work is spread across older "
          "neighbourhoods like Stamford and Chippawa, where houses often need storage and "
          "kitchens brought up to date.",
          HOSPITALITY, "hospitality"),
    place("welland", "Welland", "Niagara", "Welland",
          ["Downtown Welland", "Dain City", "North Welland", "the recreational canal"],
          "A canal city with older housing stock, a revitalised downtown and neighbourhoods "
          "on both sides of the old waterway.",
          "Welland's older homes are often well built and ready for updating, which is where "
          "a new kitchen, fitted storage and refreshed trim make the biggest difference. "
          "Restaurants and shops in the downtown bring smaller commercial projects, often in "
          "buildings that have their own quirks to measure around.",
          [K, B, I, A, R, O, C]),

    # ── York Region ──────────────────────────────────────────────────────
    place("vaughan", "Vaughan", "York Region", "Vaughan",
          ["Woodbridge", "Maple", "Kleinburg", "Thornhill", "Concord", "Vellore Village"],
          "Large new homes in Woodbridge, Maple and Vellore Village, the village of "
          "Kleinburg, and offices and showrooms around Concord.",
          "Vaughan's newer houses often have the volume for coffered ceilings, full height "
          "panelling and a proper scullery behind the main kitchen, and those are the "
          "projects we see most. Kleinburg's village core has a more traditional character. "
          "Commercial work clusters around Concord and the Vaughan Metropolitan Centre, from "
          "office reception areas to restaurant fit-outs.",
          [K, A, B, O, R, C, I]),
    place("richmond-hill", "Richmond Hill", "York Region", "Richmond Hill",
          ["Mill Pond", "Oak Ridges", "Bayview Hill", "South Richvale", "Jefferson", "Richmond Hill Village"],
          "Large homes in Bayview Hill and South Richvale, the Mill Pond neighbourhood, and "
          "the lakes and moraine trails around Oak Ridges.",
          "Bayview Hill and South Richvale are known for big custom homes, where the millwork "
          "brief is usually about scale and finish: two storey panelled foyers, libraries, "
          "dressing rooms and kitchens with integrated appliances. Around Mill Pond and the "
          "old village on Yonge Street the houses are smaller and older, and built-in storage "
          "and trim do the heavy lifting.",
          [K, A, B, I, O, R, C]),
    place("markham", "Markham", "York Region", "Markham",
          ["Unionville", "Markham Village", "Cornell", "Cathedraltown", "Berczy Village", "Thornhill"],
          "Heritage Main Street Unionville, Markham Village, newer communities like Cornell "
          "and Cathedraltown, and a large technology office market.",
          "Unionville's heritage district and the older streets of Markham Village call for "
          "joinery that respects the original buildings. Newer neighbourhoods like Cornell and "
          "Berczy Village are where kitchens, built-ins and media walls make the biggest "
          "difference. On the commercial side, Markham's office parks bring reception desks, "
          "meeting rooms and staff kitchens.",
          [K, O, B, A, R, C, I], "office"),
    place("aurora", "Aurora", "York Region", "Aurora",
          ["Aurora Village", "Aurora Highlands", "Hills of St. Andrew", "Bayview Wellington", "Aurora Heights"],
          "Established neighbourhoods around the historic downtown, estate homes in the Hills "
          "of St. Andrew, and family homes across Aurora Highlands.",
          "Aurora's older streets have houses with real character that only need the right "
          "joinery to bring it out. Estate homes in the Hills of St. Andrew take on larger "
          "projects: libraries, dressing rooms and panelled studies. Across the newer "
          "neighbourhoods, kitchens and built-ins are the most common requests.",
          HOME),
    place("newmarket", "Newmarket", "York Region", "Newmarket",
          ["Main Street", "Stonehaven", "Woodland Hill", "Glenway", "Summerhill Estates", "Armitage"],
          "Historic Main Street, family neighbourhoods like Stonehaven and Woodland Hill, and "
          "plenty of 1980s and 90s homes ready for a new kitchen.",
          "Newmarket has a lot of houses from the 1980s and 90s with original kitchens, "
          "dated trim and closets that never quite worked. Replacing the kitchen, fitting "
          "proper wardrobes and updating the trim usually transforms them. The shops and "
          "restaurants along Main Street bring smaller commercial projects with a heritage "
          "feel.",
          [K, B, I, A, R, O, C]),
    place("king", "King", "York Region", "King",
          ["King City", "Nobleton", "Schomberg", "Kettleby", "Laskay"],
          "Estate properties, horse farms and country homes across King, from King City to "
          "Nobleton and Schomberg.",
          "King's large lots and country homes make for some of the most ambitious "
          "residential work we do: kitchens built for entertaining, panelled great rooms, wine "
          "rooms and mudrooms that have to cope with real mud. Many properties sit on the Oak "
          "Ridges Moraine, and the houses are designed to feel at home in the landscape, "
          "which shapes the materials and finishes we suggest.",
          [K, A, B, I, R, O, C], "rural"),
    place("whitchurch-stouffville", "Whitchurch-Stouffville", "York Region", "Whitchurch-Stouffville",
          ["Stouffville", "Ballantrae", "Musselman's Lake", "Vandorf", "Gormley"],
          "Stouffville's Main Street and growing neighbourhoods, and country properties "
          "around Ballantrae, Vandorf and Musselman's Lake.",
          "Stouffville has grown quickly, and many of its newer homes are ready for kitchens "
          "and built-ins that feel less standard than the builder's options. North of town, "
          "rural properties and lakeside houses bring a different set of projects, often "
          "larger and more individual.",
          HOME, "rural"),
    place("east-gwillimbury", "East Gwillimbury", "York Region", "East Gwillimbury",
          ["Holland Landing", "Mount Albert", "Queensville", "Sharon"],
          "Holland Landing, Mount Albert, Queensville and Sharon: small communities, new "
          "subdivisions and plenty of countryside in between.",
          "East Gwillimbury is a mix of rural properties, historic hamlets and new "
          "subdivisions, which means everything from farmhouse kitchens to built-in storage "
          "in brand new homes. Sharon is home to the Sharon Temple, a reminder that careful "
          "woodworking in this part of York Region goes back a long way.",
          HOME, "rural"),
    place("georgina", "Georgina", "York Region", "Georgina",
          ["Keswick", "Sutton", "Jackson's Point", "Pefferlaw", "Port Bolster"],
          "Lake Simcoe shoreline communities, from Keswick to Sutton and Jackson's Point, "
          "where many cottages have become year-round homes.",
          "Converting a cottage into a year-round home usually means rethinking storage, the "
          "kitchen and the trim all at once, in rooms that were never built square. Waterfront "
          "houses also bring practical concerns, like finishes that cope with humidity and "
          "mudrooms that can handle a Lake Simcoe winter.",
          LAKESIDE, "lakeside"),

    # ── Durham ───────────────────────────────────────────────────────────
    place("pickering", "Pickering", "Durham", "Pickering",
          ["Frenchman's Bay", "Rosebank", "Dunbarton", "Liverpool", "Amberlea", "Claremont", "Seaton"],
          "Lakeside streets around Frenchman's Bay, established neighbourhoods like Rosebank "
          "and Dunbarton, and the new Seaton community to the north.",
          "Pickering's houses from the 1970s and 80s are prime candidates for kitchen and "
          "built-in upgrades, while lakeside homes near Frenchman's Bay often involve larger "
          "renovations. New homes in Seaton arrive as a blank slate, which suits owners who "
          "want built-ins and better kitchens rather than builder options.",
          HOME),
    place("ajax", "Ajax", "Durham", "Ajax",
          ["Pickering Village", "the waterfront", "Central Ajax", "North Ajax"],
          "The heritage streets of Pickering Village, family neighbourhoods across Ajax, and "
          "homes along the Lake Ontario waterfront.",
          "Ajax is mostly family housing from the last few decades, which makes kitchens, "
          "mudrooms and basement built-ins the most common projects. In Pickering Village "
          "the older houses carry trim and proportions worth matching, and we take profiles "
          "on site rather than approximating them.",
          [K, B, I, A, R, O, C]),
    place("whitby", "Whitby", "Durham", "Whitby",
          ["Downtown Whitby", "Brooklin", "Port Whitby", "Williamsburg", "Rolling Acres"],
          "Downtown Whitby's heritage core, the village of Brooklin, lakeside Port Whitby "
          "and established neighbourhoods in between.",
          "Brooklin and downtown Whitby both keep historic main streets and older houses that "
          "suit traditional joinery. Newer neighbourhoods around Williamsburg and north "
          "Brooklin are where kitchens and built-ins come up most. Restaurants and shops in "
          "the downtown core bring smaller commercial projects.",
          HOME),
    place("oshawa", "Oshawa", "Durham", "Oshawa",
          ["Downtown Oshawa", "Northglen", "Kedron", "Lakeview", "Eastdale", "McLaughlin"],
          "Older brick houses near downtown, newer neighbourhoods in the north end, and a "
          "downtown that keeps adding restaurants and offices.",
          "Oshawa's older neighbourhoods have solid houses from the early and middle twentieth "
          "century that respond well to new kitchens, built-ins and restored trim. The newer "
          "subdivisions in north Oshawa bring the usual requests for upgraded kitchens and "
          "finished basements with fitted storage.",
          [K, B, I, A, R, O, C]),
    place("clarington", "Clarington", "Durham", "Clarington",
          ["Bowmanville", "Courtice", "Newcastle", "Orono"],
          "Bowmanville's heritage downtown, fast growing Courtice and Newcastle, and the "
          "countryside around Orono.",
          "Bowmanville has a well kept historic core with Victorian houses that suit "
          "traditional trim and panelling. Courtice and Newcastle are growing quickly, with "
          "new homes ready for kitchens and built-ins. Farther out, rural properties around "
          "Orono bring individual projects, often in houses extended over many years.",
          HOME),
    place("uxbridge", "Uxbridge", "Durham", "Uxbridge",
          ["Uxbridge", "Goodwood", "Leaskdale", "Zephyr"],
          "A small town with a historic downtown, surrounded by countryside, trails and estate "
          "properties on the Oak Ridges Moraine.",
          "Uxbridge projects are often in country homes and older town houses that have been "
          "added to over the years, which makes the site measure especially important. "
          "Kitchens, mudrooms and built-ins designed around a rural life are the most common "
          "requests.",
          [K, B, A, I, R, O, C], "rural"),

    # ── Simcoe ───────────────────────────────────────────────────────────
    place("bradford-west-gwillimbury", "Bradford West Gwillimbury", "Simcoe", "Bradford West Gwillimbury",
          ["Bradford", "Bond Head", "the Holland Marsh"],
          "Bradford's growing neighbourhoods, the village of Bond Head and farm properties "
          "along the Holland Marsh.",
          "Bradford has grown quickly, and its newer homes are where we see requests for "
          "upgraded kitchens, media walls and built-in storage. Older houses and farm "
          "properties around Bond Head and the Holland Marsh bring larger, more individual "
          "projects.",
          HOME),
    place("innisfil", "Innisfil", "Simcoe", "Innisfil",
          ["Alcona", "Lefroy", "Cookstown", "Stroud", "Friday Harbour"],
          "Alcona and Lefroy on Lake Simcoe, the village of Cookstown, and the resort "
          "community at Friday Harbour.",
          "Much of Innisfil's lakeside housing began as cottages, and turning them into "
          "year-round homes means rethinking storage and kitchens in rooms that were never "
          "square. Newer homes in Alcona and the resort condos at Friday Harbour bring more "
          "straightforward kitchen and built-in projects.",
          LAKESIDE, "lakeside"),
    place("barrie", "Barrie", "Simcoe", "Barrie",
          ["Downtown Barrie", "Allandale", "the East End", "Painswick", "Innishore", "Holly"],
          "Older houses near Kempenfelt Bay and downtown, the historic Allandale "
          "neighbourhood, and large family suburbs to the south.",
          "Barrie's east end and the streets near Kempenfelt Bay have older homes with "
          "character worth keeping, where restored trim and fitted cabinetry make the most of "
          "it. The southern suburbs around Painswick and Holly are newer, and kitchens and "
          "built-ins are the main requests. Downtown restaurants and offices bring commercial "
          "work.",
          HOME),
    place("new-tecumseth", "New Tecumseth", "Simcoe", "New Tecumseth",
          ["Alliston", "Tottenham", "Beeton"],
          "Alliston, Tottenham and Beeton: small towns surrounded by farmland, each with its "
          "own historic main street.",
          "New Tecumseth's towns mix older houses in the historic cores with newer "
          "subdivisions on their edges. Some projects are about matching period trim and "
          "others are about turning a builder's kitchen into something better. Rural "
          "properties around the towns bring larger, more individual work.",
          HOME, "rural"),
    place("collingwood", "Collingwood", "Simcoe", "Collingwood",
          ["Downtown Collingwood", "the harbour", "Cranberry", "the Blue Mountain area"],
          "A historic downtown on Georgian Bay, waterfront homes along the harbour, and "
          "chalets and four season houses toward Blue Mountain.",
          "Collingwood's chalets and lakeside homes are built for weekends with a crowd: big "
          "kitchens, mudrooms for wet gear and a lot of storage. The historic downtown along "
          "Hurontario Street has heritage buildings where restaurants and shops need millwork "
          "that suits the setting.",
          [K, B, R, A, I, O, C], "lakeside"),
    place("orillia", "Orillia", "Simcoe", "Orillia",
          ["Downtown Orillia", "the Lake Couchiching waterfront", "West Ridge", "Atherley"],
          "The gateway to cottage country, with a historic downtown, homes along Lake "
          "Couchiching and newer neighbourhoods on the West Ridge.",
          "Orillia projects range from century homes near the downtown to waterfront houses on "
          "Lake Couchiching and newer homes on the West Ridge. Cottage conversions and "
          "lakefront houses benefit from storage designed around life at the lake, and the "
          "downtown's restaurants and shops bring commercial work.",
          LAKESIDE, "lakeside"),

    # ── Dufferin, Wellington, Waterloo, Brant ────────────────────────────
    place("orangeville", "Orangeville", "Dufferin", "Orangeville",
          ["Downtown Orangeville", "Broadway", "Mono", "the Hockley Valley"],
          "The historic Broadway main street, established neighbourhoods around it, and "
          "estate properties in Mono and the Hockley Valley.",
          "Orangeville's older houses near Broadway suit traditional trim and cabinetry, while "
          "the newer neighbourhoods are where kitchens and built-ins are most in demand. "
          "Country properties in Mono and the Hockley Valley bring larger projects in homes "
          "designed around the landscape.",
          HOME, "rural"),
    place("guelph", "Guelph", "Wellington", "Guelph",
          ["Downtown Guelph", "Old University", "Exhibition Park", "The Ward", "the South End"],
          "A city built in local limestone, with century houses in Old University and "
          "Exhibition Park and a lively downtown.",
          "Guelph's limestone houses and Victorian brick homes have thick walls and deep window "
          "reveals that new millwork has to respect. Matching existing trim and fitting "
          "cabinetry to walls that are far from square is routine here. Downtown's restaurants "
          "and independent shops bring commercial projects, and the newer South End is where "
          "kitchens and built-ins are most requested.",
          HERITAGE, "heritage"),
    place("centre-wellington", "Centre Wellington", "Wellington", "Centre Wellington",
          ["Fergus", "Elora", "Belwood", "Salem"],
          "The stone villages of Fergus and Elora on the Grand River, and the countryside "
          "around Belwood and Salem.",
          "Fergus and Elora have some of the finest nineteenth century stone buildings in "
          "Ontario, and both towns draw visitors to inns, restaurants and shops that want "
          "interiors to match. Residential projects range from heritage houses to new homes "
          "on the edges of town.",
          [A, R, K, B, I, C, O], "heritage"),
    place("kitchener", "Kitchener", "Waterloo Region", "Kitchener",
          ["Downtown Kitchener", "Victoria Park", "Westmount", "Doon", "Forest Heights"],
          "Victoria Park's older homes, established Westmount, and a downtown where former "
          "factories have become offices and restaurants.",
          "Kitchener's converted industrial buildings are home to technology companies whose "
          "offices want reception desks, meeting rooms and kitchens built with real character. "
          "In Victoria Park and Westmount the older houses suit traditional joinery, while "
          "newer neighbourhoods around Doon bring kitchen and built-in projects.",
          OFFICE, "office"),
    place("waterloo", "Waterloo", "Waterloo Region", "Waterloo",
          ["Uptown Waterloo", "Beechwood", "Westvale", "Laurelwood", "Columbia Forest"],
          "Uptown Waterloo, two universities, a technology sector, and established "
          "neighbourhoods like Beechwood and Westvale.",
          "Waterloo's office market brings commercial work in reception areas, meeting rooms "
          "and kitchens for teams that care about their workplace. Residential projects are "
          "concentrated in established neighbourhoods like Beechwood and Westvale, where "
          "houses from the 1970s through the 90s are being updated.",
          OFFICE, "office"),
    place("cambridge", "Cambridge", "Waterloo Region", "Cambridge",
          ["Galt", "Preston", "Hespeler", "Blair"],
          "Galt, Preston and Hespeler, three historic towns now one city, with stone "
          "buildings along the Grand River.",
          "Galt's downtown has some of the region's finest stone architecture, and its older "
          "houses suit carefully matched trim and panelling. Preston and Hespeler have their "
          "own historic cores and many newer neighbourhoods where kitchens and built-ins are "
          "the main requests.",
          HERITAGE, "heritage"),
    place("brantford", "Brantford", "Brant", "Brantford",
          ["Downtown Brantford", "Holmedale", "Eagle Place", "West Brant", "Terrace Hill"],
          "Victorian homes in Holmedale and Terrace Hill, a downtown on the Grand River, and "
          "newer neighbourhoods in West Brant.",
          "Brantford's older neighbourhoods have solid brick houses with original trim worth "
          "matching and kitchens worth replacing. West Brant's newer homes bring requests for "
          "upgraded kitchens and fitted storage. The downtown's restaurants and offices add "
          "commercial projects.",
          HOME),
]

REGION_ORDER = ["Toronto", "Peel", "Halton", "Hamilton", "Niagara", "York Region",
                "Durham", "Simcoe", "Dufferin", "Wellington", "Waterloo Region", "Brant"]

BY_SLUG = {p["slug"]: p for p in LOCATIONS}


def nearest(slug, n=6):
    """The n closest other places, for the 'nearby' links on each page."""
    me = BY_SLUG[slug]
    others = [p for p in LOCATIONS if p["slug"] != slug]
    others.sort(key=lambda p: km((me["lat"], me["lon"]), (p["lat"], p["lon"])))
    return others[:n]


def _selfcheck():
    slugs = [p["slug"] for p in LOCATIONS]
    assert len(slugs) == len(set(slugs)), "duplicate slug"
    ledes = [p["lede"] for p in LOCATIONS]
    bodies = [p["body"] for p in LOCATIONS]
    assert len(set(ledes)) == len(ledes) and len(set(bodies)) == len(bodies), "copy repeats"
    for p in LOCATIONS:
        assert p["region"] in REGION_ORDER, p["region"]
        assert "\u2014" not in p["lede"] + p["body"], p["slug"]


_selfcheck()

if __name__ == "__main__":
    for p in sorted(LOCATIONS, key=lambda p: p["km"]):
        print(f'{p["km"]:4d} km  {p["dir"]:9s} {p["name"]:28s} {p["region"]}')
    print(len(LOCATIONS), "places")
