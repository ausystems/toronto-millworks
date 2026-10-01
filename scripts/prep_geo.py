#!/usr/bin/env python3
"""
One-off preprocessing for the service-area maps.

Takes raw OpenStreetMap shoreline polygons (via Nominatim) and projects them
into kilometres around the shop, clips them to the map frame and simplifies
them, so the repository carries a few kilobytes of drawing data rather than
megabytes of survey points.

    python3 scripts/prep_geo.py RAW_LAKES.json  ->  scripts/data/lakes_km.json

Shorelines (c) OpenStreetMap contributors, ODbL.
"""
import json, math, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOP = (43.7015416, -79.6576688)
KX = math.cos(math.radians(SHOP[0])) * 111.32     # km per degree of longitude here
KY = 110.574                                        # km per degree of latitude
FRAME = 150.0                                       # km either side of the shop


def proj(lon, lat):
    return ((lon - SHOP[1]) * KX, -(lat - SHOP[0]) * KY)


def clip(poly, lo, hi):
    """Sutherland-Hodgman against an axis aligned square."""
    def inside(p, edge):
        x, y = p
        return {"l": x >= lo, "r": x <= hi, "t": y >= lo, "b": y <= hi}[edge]

    def cross(a, b, edge):
        (x1, y1), (x2, y2) = a, b
        if edge in "lr":
            x = lo if edge == "l" else hi
            t = (x - x1) / (x2 - x1)
            return (x, y1 + t * (y2 - y1))
        y = lo if edge == "t" else hi
        t = (y - y1) / (y2 - y1)
        return (x1 + t * (x2 - x1), y)

    out = poly
    for edge in "lrtb":
        src, out = out, []
        if not src:
            break
        prev = src[-1]
        for cur in src:
            if inside(cur, edge):
                if not inside(prev, edge):
                    out.append(cross(prev, cur, edge))
                out.append(cur)
            elif inside(prev, edge):
                out.append(cross(prev, cur, edge))
            prev = cur
    return out


def dp(pts, eps):
    """Douglas-Peucker, iterative. A closed ring (first point repeated as the
    last) has a zero length base segment, which scores every point at zero
    and throws the whole shoreline away, so a ring is split at the point
    farthest from its start and each half simplified as an open line."""
    if len(pts) < 3:
        return pts
    if math.dist(pts[0], pts[-1]) < 1e-9:
        body = pts[:-1]
        far = max(range(len(body)), key=lambda i: math.dist(body[0], body[i]))
        a = dp(body[:far + 1], eps)
        b = dp(body[far:] + [body[0]], eps)
        return a[:-1] + b[:-1]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1e-9
        best, idx = 0.0, -1
        for i in range(a + 1, b):
            x0, y0 = pts[i]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / n
            if d > best:
                best, idx = d, i
        if best > eps and idx > 0:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def main(raw_path):
    raw = json.load(open(raw_path))
    out = {}
    for name, g in raw.items():
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = []
        for poly in polys:
            ring = [proj(lon, lat) for lon, lat in poly[0]]       # outer ring only
            ring = clip(ring, -FRAME, FRAME)
            if len(ring) < 3:
                continue
            ring = dp(ring, 0.35)
            area = 0.5 * abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2)
                                 in zip(ring, ring[1:] + ring[:1])))
            if area < 2:          # drop specks under 2 km2
                continue
            rings.append([[round(x, 2), round(y, 2)] for x, y in ring])
        if rings:
            out[name] = rings
            print(f"{name:8s} rings={len(rings)} pts={sum(len(r) for r in rings)}")
    dest = os.path.join(ROOT, "scripts", "data", "lakes_km.json")
    json.dump({"_note": "Shorelines (c) OpenStreetMap contributors, ODbL. "
                        "Kilometres from the shop, +x east, +y south.",
               "frame_km": FRAME, "shop": SHOP, "lakes": out},
              open(dest, "w"), separators=(",", ":"))
    print("->", dest, os.path.getsize(dest) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
