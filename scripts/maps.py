#!/usr/bin/env python3
"""
Service-area maps, drawn from data rather than tiles.

Everything is projected into kilometres around the shop (+x east, +y south),
so the SVG viewBox is literally a map in km. Shorelines come from
scripts/data/lakes_km.json (OpenStreetMap, ODbL), towns from locations.py.

    hub_map()          the whole 120 km radius, every town a linked dot
    place_map(slug)    one town, the shop, and the straight line between them

Type and strokes are divided by --dws exactly as the shop drawings are, so a
label is the same size on a phone as on a desktop. Labels are placed greedily
against everything already on the sheet and dropped rather than overlapped.
"""
import html
import json
import math
import os

from locations import LOCATIONS, BY_SLUG, SHOP, nearest

E = lambda s: html.escape(str(s), quote=True)
HERE = os.path.dirname(os.path.abspath(__file__))
_LAKES = json.load(open(os.path.join(HERE, "data", "lakes_km.json")))["lakes"]
KX = math.cos(math.radians(SHOP[0])) * 111.32
KY = 110.574


def proj(lat, lon):
    return ((lon - SHOP[1]) * KX, -(lat - SHOP[0]) * KY)


def _ring_path(ring):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + " Z"


def _lakes_in(x0, y0, w, h):
    out = []
    for name, rings in _LAKES.items():
        for r in rings:
            xs = [p[0] for p in r]; ys = [p[1] for p in r]
            if max(xs) < x0 or min(xs) > x0 + w or max(ys) < y0 or min(ys) > y0 + h:
                continue
            out.append(f'<path class="mp-lake" d="{_ring_path(r)}"/>')
    return "".join(out)


class Labeller:
    """Greedy label placement in km space at an assumed render scale."""

    def __init__(self, px_per_km, font_px=9.2):
        self.k = px_per_km
        self.h = font_px * 1.15 / px_per_km          # label height in km
        self.cw = font_px * .66 / px_per_km          # average character width in km
        self.boxes = []

    def _free(self, b):
        x0, y0, x1, y1 = b
        return all(x1 < a0 or x0 > a1 or y1 < b0 or y0 > b1 for a0, b0, a1, b1 in self.boxes)

    def block(self, x, y, r):
        self.boxes.append((x - r, y - r, x + r, y + r))

    def place(self, x, y, text, gap=1.9, force=False):
        w = len(text) * self.cw + .6
        h = self.h
        d = gap * .72
        cands = (
                ("start", x + gap, y + h * .34, (x + gap - .3, y - h * .55, x + gap + w, y + h * .5)),
                ("end", x - gap, y + h * .34, (x - gap - w, y - h * .55, x - gap + .3, y + h * .5)),
                ("middle", x, y - gap - h * .2, (x - w / 2, y - gap - h * 1.05, x + w / 2, y - gap + .2)),
                ("middle", x, y + gap + h * .82, (x - w / 2, y + gap - .2, x + w / 2, y + gap + h * 1.02)),
                ("start", x + d, y - d, (x + d - .3, y - d - h * .9, x + d + w, y - d + .3)),
                ("end", x - d, y - d, (x - d - w, y - d - h * .9, x - d + .3, y - d + .3)),
                ("start", x + d, y + d + h * .7, (x + d - .3, y + d - .2, x + d + w, y + d + h * .9)),
                ("end", x - d, y + d + h * .7, (x - d - w, y + d - .2, x - d + .3, y + d + h * .9)),
        )
        for anchor, tx, ty, box in cands:
            if self._free(box):
                self.boxes.append(box)
                return anchor, tx, ty
        if force:
            anchor, tx, ty, box = cands[0]
            self.boxes.append(box)
            return anchor, tx, ty
        return None


MAJOR = {"toronto", "hamilton", "barrie", "kitchener", "guelph", "oshawa", "st-catharines",
         "niagara-falls", "orillia", "collingwood", "brantford", "newmarket", "orangeville"}


def hub_map(prefix=""):
    """The whole service radius. Dots link to their pages; the list beside the map
    carries the same links for keyboards and crawlers, so the SVG stays out of the
    tab order."""
    F = 142
    x0, y0, w, h = -F, -F, 2 * F, 2 * F
    lab = Labeller(px_per_km=640 / (2 * F))        # tuned for the desktop column
    parts = [f'<rect class="mp-bg" x="{x0}" y="{y0}" width="{w}" height="{h}"/>',
             _lakes_in(x0, y0, w, h)]

    # water names, set quietly in the lake
    for name, (lx, ly), minor in (("Lake Ontario", (104, 22), False), ("Lake Simcoe", (34, -66), True),
                                  ("Lake Erie", (-24, 131), False), ("Georgian Bay", (-74, -128), False)):
        parts.append(f'<text class="mp-water{" mp-minor" if minor else ""}" x="{lx}" y="{ly}" '
                     f'text-anchor="middle">{E(name)}</text>')

    # distance rings, labelled out over the lake where nothing else lives
    for r in (30, 60, 90, 120):
        parts.append(f'<circle class="mp-ring{" mp-ring--edge" if r == 120 else ""}" cx="0" cy="0" r="{r}"/>')
        a = math.radians(38)
        parts.append(f'<text class="mp-rl" x="{r * math.cos(a) + 1.5:.1f}" y="{r * math.sin(a) + 1:.1f}">{r} km</text>')

    # the shop first, so towns are placed around it
    lab.block(0, 0, 4.5)
    lab.boxes.append((-1, -11.5, 31, -4.5))
    dots, labels = [], []
    order = sorted(LOCATIONS, key=lambda p: (p["slug"] not in MAJOR, -p["km"]))
    for p in LOCATIONS:
        x, y = proj(p["lat"], p["lon"])
        lab.block(x, y, 1.6)
    for p in order:
        x, y = proj(p["lat"], p["lon"])
        dots.append(
            f'<a href="{prefix}service-areas/{p["slug"]}/" class="mp-town" data-slug="{p["slug"]}" '
            f'tabindex="-1" aria-label="{E(p["name"])}"><circle class="mp-dot" cx="{x:.1f}" cy="{y:.1f}" r="1.25"/>'
            f'<circle class="mp-hit" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/></a>')
        if p["slug"] in ("north-york", "etobicoke", "east-york", "scarborough"):
            continue                                     # the city's own districts sit under "Toronto"
        spot = lab.place(x, y, p["name"])
        if spot:
            anchor, tx, ty = spot
            minor = "" if p["slug"] in MAJOR else " mp-minor"
            labels.append(f'<text class="mp-name{minor}" data-for="{p["slug"]}" x="{tx:.1f}" y="{ty:.1f}" '
                          f'text-anchor="{anchor}">{E(p["name"])}</text>')

    shop = ('<g class="mp-shop"><circle class="mp-halo" cx="0" cy="0" r="4.2"/>'
            '<circle class="mp-core" cx="0" cy="0" r="1.9"/>'
            '<text class="mp-shopl" x="2.6" y="-6">Our shop</text></g>')

    # north point and a 25 km scale bar, bottom left
    furniture = (f'<g class="mp-furn" transform="translate({x0 + 12} {y0 + h - 14})">'
                 '<path class="mp-n" d="M0,-12 L3,-4 L0,-6 L-3,-4 Z"/>'
                 '<text class="mp-rl" x="0" y="-14.5" text-anchor="middle">N</text>'
                 '<line class="mp-scale" x1="10" y1="0" x2="35" y2="0"/>'
                 '<line class="mp-scale" x1="10" y1="-1.6" x2="10" y2="1.6"/>'
                 '<line class="mp-scale" x1="35" y1="-1.6" x2="35" y2="1.6"/>'
                 '<text class="mp-rl" x="22.5" y="-3" text-anchor="middle">25 km</text></g>')

    return (f'<svg class="mp mp--hub" viewBox="{x0} {y0} {w} {h}" role="img" '
            f'aria-labelledby="mp-hub-t" data-map>'
            f'<title id="mp-hub-t">Map of the {len(LOCATIONS)} towns and cities we serve within '
            f'120 km of our shop in Mississauga, with Lake Ontario to the south.</title>'
            + "".join(parts) + "".join(dots) + "".join(labels) + shop + furniture + '</svg>')


def place_map(slug, prefix=""):
    """One town and the shop, framed so both sit comfortably, with the straight line
    and its length. Unique to each page because the geography is."""
    p = BY_SLUG[slug]
    cx, cy = proj(p["lat"], p["lon"])
    mx, my = cx / 2, cy / 2
    span = max(abs(cx), abs(cy) * 1.5, 28) * 1.65 + 18
    w, h = span, span / 1.5
    x0, y0 = mx - w / 2, my - h / 2
    lab = Labeller(px_per_km=620 / w)
    parts = [f'<rect class="mp-bg" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}"/>',
             _lakes_in(x0, y0, w, h)]

    # neighbours for context, faint, labelled only where there is room
    far = []
    for n in nearest(slug, 8):
        nx, ny = proj(n["lat"], n["lon"])
        if x0 < nx < x0 + w and y0 < ny < y0 + h and math.hypot(nx, ny) > 3:
            parts.append(f'<a href="{prefix}service-areas/{n["slug"]}/" tabindex="-1" aria-label="{E(n["name"])}" class="mp-town">'
                         f'<circle class="mp-dot mp-dot--far" cx="{nx:.1f}" cy="{ny:.1f}" r="{w / 300:.2f}"/></a>')
            lab.block(nx, ny, w / 300 * 1.4)
            far.append((nx, ny, n["name"]))

    r = w / 180
    lab.block(0, 0, r * 2.4); lab.block(cx, cy, r * 1.8)
    route = (f'<line class="mp-route" x1="0" y1="0" x2="{cx:.1f}" y2="{cy:.1f}"/>')
    dot = (f'<circle class="mp-halo" cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 2:.2f}"/>'
           f'<circle class="mp-core mp-core--town" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}"/>')
    shop = (f'<circle class="mp-halo" cx="0" cy="0" r="{r * 2:.2f}"/>'
            f'<circle class="mp-core" cx="0" cy="0" r="{r * .85:.2f}"/>')

    labels = []
    for (x, y, text, cls) in ((cx, cy, p["name"], "mp-name mp-name--town"),
                              (0, 0, "Our shop", "mp-shopl")):
        anchor, tx, ty = lab.place(x, y, text, gap=r * 2.6, force=True)
        labels.append(f'<text class="{cls}" x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}">{E(text)}</text>')
    for nx, ny, name in far:
        spot = lab.place(nx, ny, name, gap=w / 300 * 2.6)
        if spot:
            anchor, tx, ty = spot
            labels.append(f'<text class="mp-name mp-minor mp-name--far" x="{tx:.1f}" y="{ty:.1f}" '
                          f'text-anchor="{anchor}">{E(name)}</text>')

    # the distance, set on the line itself
    ang = math.degrees(math.atan2(cy, cx))
    if ang > 90 or ang < -90:
        ang += 180
    km = f'{p["km_exact"]:.0f} km' if p["km_exact"] >= 10 else f'{p["km_exact"]:.1f} km'
    if p["km_exact"] >= 16:
        dist = (f'<g transform="translate({mx:.1f} {my:.1f}) rotate({ang:.1f})">'
                f'<text class="mp-km" x="0" y="{-r * 1.6:.2f}" text-anchor="middle">{km}</text></g>')
    else:
        # a short route has no room along it, so the figure sits wherever is free
        spot = lab.place(mx, my, km, gap=r * 2.2)
        dist = (f'<text class="mp-km" x="{spot[1]:.1f}" y="{spot[2]:.1f}" text-anchor="{spot[0]}">{km}</text>'
                if spot else "")

    return (f'<svg class="mp mp--place" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" role="img" '
            f'aria-labelledby="mp-{slug}-t" data-map>'
            f'<title id="mp-{slug}-t">Map showing {E(p["name"])}, about {p["km"]} km {p["dir"]} '
            f'of our shop in Mississauga.</title>'
            + "".join(parts) + route + dist + shop + dot + "".join(labels) + '</svg>')


if __name__ == "__main__":
    s = hub_map()
    print("hub", len(s) // 1024, "KB,", s.count('class="mp-name'), "labels of", len(LOCATIONS))
    for slug in ("mississauga", "toronto", "orillia", "niagara-falls", "kitchener"):
        print(slug, len(place_map(slug)) // 1024, "KB")
