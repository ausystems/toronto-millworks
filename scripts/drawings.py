#!/usr/bin/env python3
"""
Shop drawings, as inline SVG.

Millwork starts as a drawing, so the site's illustrations are drawings too:
hairline elevations, sections and plans in the house palette. They stand in
where photography does not exist yet, and they say something true about the
work instead of decorating it.

Every primitive carries pathLength="1" and an order index, so CSS can draw the
sheet on in sequence. Without script, or with reduced motion, the drawing is
simply there.

Units are tenths of a millimetre scaled to taste: one unit is 10 mm unless a
drawing says otherwise. Dimensions printed on a sheet are in millimetres.
"""
import html
import math

E = lambda s: html.escape(str(s), quote=True)


DRAWN = {"l", "t", "h", "d", "e", "led"}


def _pl(c):
    return ' pathLength="1"' if c in DRAWN else ""


class Sheet:
    def __init__(self, key, w, h, title, note="Typical, not to scale", alt=""):
        self.key, self.w, self.h = key, w, h
        self.title, self.note, self.alt = title, note, alt or title
        self.parts = []          # (order, svg)
        self.order = 0

    # ── ordering: one index per component so each piece draws as a unit ───
    def next(self, step=1):
        self.order += step
        return self

    def _add(self, svg):
        self.parts.append((self.order, svg))

    # ── primitives ────────────────────────────────────────────────────────
    def line(self, x1, y1, x2, y2, c="l"):
        self._add(f'<line class="dw-{c}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"{_pl(c)}/>')

    def rect(self, x, y, w, h, c="l", rx=0):
        r = f' rx="{rx:g}"' if rx else ""
        self._add(f'<rect class="dw-{c}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{r}{_pl(c)}/>')

    def path(self, d, c="l"):
        self._add(f'<path class="dw-{c}" d="{d}"{_pl(c)}/>')

    def poly(self, pts, c="l", closed=True):
        d = "M" + " L".join(f"{x:g},{y:g}" for x, y in pts) + (" Z" if closed else "")
        self.path(d, c)

    def circle(self, cx, cy, r, c="l"):
        self._add(f'<circle class="dw-{c}" cx="{cx:g}" cy="{cy:g}" r="{r:g}"{_pl(c)}/>')

    def fill(self, x, y, w, h, c="f"):
        self._add(f'<rect class="dw-{c}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"/>')

    def fillpath(self, d, c="f"):
        self._add(f'<path class="dw-{c}" d="{d}"/>')

    def text(self, x, y, s, c="x", anchor="start", minor=False):
        k = f"dw-{c}" + (" dw-minor" if minor else "")
        self._add(f'<text class="{k}" x="{x:g}" y="{y:g}" text-anchor="{anchor}">{E(s)}</text>')

    # ── composites ────────────────────────────────────────────────────────
    def door(self, x, y, w, h, stile=5.5, handle="v", hside="r"):
        """Shaker door: frame and recessed panel, with a pull."""
        self.rect(x, y, w, h)
        self.rect(x + stile, y + stile, w - 2 * stile, h - 2 * stile, "t")
        if handle == "v":
            hx = x + w - 3.2 if hside == "r" else x + 3.2
            self.line(hx, y + h * .42 - 6, hx, y + h * .42 + 6, "h")
        elif handle == "top":
            self.line(x + w / 2 - 6, y + 3.4, x + w / 2 + 6, y + 3.4, "h")

    def drawer(self, x, y, w, h):
        self.rect(x, y, w, h)
        self.rect(x + 4, y + 3.5, w - 8, h - 7, "t")
        self.line(x + w / 2 - 7, y + h / 2, x + w / 2 + 7, y + h / 2, "h")

    def dim(self, x1, y1, x2, y2, label, off=10, minor=False):
        """Horizontal or vertical dimension with extension lines and slashes."""
        horiz = abs(y2 - y1) < abs(x2 - x1)
        if horiz:
            y = y1 - off
            self.line(x1, y1 - 2, x1, y - 3, "e")
            self.line(x2, y2 - 2, x2, y - 3, "e")
            self.line(x1 - 3, y, x2 + 3, y, "d")
            for x in (x1, x2):
                self.line(x - 2.2, y + 2.2, x + 2.2, y - 2.2, "d")
            self.text((x1 + x2) / 2, y - 3, label, "n", "middle", minor)
        else:
            x = x1 + off
            self.line(x1 + 2, y1, x + 3, y1, "e")
            self.line(x2 + 2, y2, x + 3, y2, "e")
            self.line(x, y1 - 3, x, y2 + 3, "d")
            for y in (y1, y2):
                self.line(x - 2.2, y + 2.2, x + 2.2, y - 2.2, "d")
            cy = (y1 + y2) / 2
            self._add(f'<text class="dw-n{" dw-minor" if minor else ""}" x="{x - 3:g}" y="{cy:g}" '
                      f'text-anchor="middle" transform="rotate(-90 {x - 3:g} {cy:g})">{E(label)}</text>')

    def callout(self, x, y, tx, ty, label, anchor="start", minor=False):
        """Leader from a dot on the work to a label off it."""
        self.circle(x, y, .9, "dot")
        if anchor == "middle":
            ex, ey = tx, (ty - 9 if ty > y else ty + 3)
        else:
            ex, ey = (tx - 4 if anchor == "start" else tx + 4), ty - 3
        self.path(f"M{x:g},{y:g} L{ex:g},{ey:g}", "e")
        self.text(tx, ty, label, "x", anchor, minor)

    def hatch(self, d):
        self.fillpath(d, "hx")

    # ── output ────────────────────────────────────────────────────────────
    def svg(self, uid="", cls=""):
        pid = f"dwh-{self.key}{uid}"
        tid = f"dwt-{self.key}{uid}"
        n_max = max(o for o, _ in self.parts) or 1
        body = []
        for o, s in self.parts:
            # order index drives the stagger; capped so a busy sheet still lands in time
            body.append(s.replace("/>", f' style="--i:{round(o * 46 / n_max)}"/>', 1)
                        if s.endswith("/>") else
                        s.replace(">", f' style="--i:{round(o * 46 / n_max)}">', 1))
        tb = self.h - 26
        return (
            f'<svg class="{("dw " + cls).strip()}" viewBox="0 0 {self.w:g} {self.h:g}" role="img" '
            f'aria-labelledby="{tid}" preserveAspectRatio="xMidYMid meet" data-draw>'
            f'<title id="{tid}">{E(self.alt)}</title>'
            f'<defs><pattern id="{pid}" width="3.2" height="3.2" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="3.2" class="dw-hl"/></pattern></defs>'
            f'<g class="dw-g" style="--hatch:url(#{pid})">' + "".join(body) + '</g>'
            f'<g class="dw-tb"><line x1="{self.w - 170:g}" y1="{tb:g}" x2="{self.w - 8:g}" y2="{tb:g}" class="dw-e"/>'
            f'<text class="dw-tt" x="{self.w - 8:g}" y="{tb + 11:g}" text-anchor="end">{E(self.title)}</text>'
            f'<text class="dw-tn" x="{self.w - 8:g}" y="{tb + 21:g}" text-anchor="end">{E(self.note)}</text></g>'
            '</svg>')


# ══════════════════════════════════════════════════════════════════════════════
#  Sheets
# ══════════════════════════════════════════════════════════════════════════════
def kitchen():
    s = Sheet("kitchen", 530, 372, "Kitchen, elevation A",
              alt="Shop drawing of a kitchen elevation: drawer stack, range with hood, "
                  "base and wall cabinets, a tall pantry and a panelled fridge.")
    F, C = 300, 32                                   # floor, ceiling
    s.line(18, F, 452, F, "l"); s.line(18, C, 452, C, "c")
    s.next()
    # toe kick and counter
    s.line(40, F - 10, 251, F - 10, "t")
    s.next()
    # drawer stack 600
    for i, (y, h) in enumerate(((213, 18), (231, 28), (259, 31))):
        s.drawer(40, y, 60, h)
    s.next()
    # range 760
    s.rect(100, 213, 76, 77)
    s.line(100, 222, 176, 222, "t")
    for kx in (110, 124, 152, 166):
        s.circle(kx, 217.5, 1.6, "t")
    s.rect(106, 228, 64, 46, "t"); s.rect(114, 236, 48, 26, "t")
    s.line(122, 231, 154, 231, "h")
    s.next()
    # base pair 750
    s.door(176, 222, 37.5, 68, hside="r"); s.door(213.5, 222, 37.5, 68, hside="l")
    s.drawer(176, 213, 75, 9)
    s.next()
    # counter, hatched in section at its end
    s.rect(38, 208, 215, 5, "l")
    s.next()
    # hood
    s.poly([(102, 165), (174, 165), (160, 112), (116, 112)], "l")
    s.rect(124, C, 28, 80, "l")
    s.line(102, 160, 174, 160, "t")
    s.next()
    # uppers
    s.door(40, 73, 60, 90, handle="v", hside="r")
    s.door(176, 73, 37.5, 90, hside="r"); s.door(213.5, 73, 37.5, 90, hside="l")
    s.line(38, 73, 253, 73, "l"); s.rect(38, 66, 215, 7, "t")
    s.next()
    # tall pantry 600
    s.door(251, 50, 60, 135, hside="l"); s.door(251, 185, 60, 105, hside="l")
    s.next()
    # panelled fridge 890
    s.door(311, 50, 89, 168, hside="l", stile=6.5)
    s.door(311, 218, 89, 72, handle="top", stile=6.5)
    s.rect(249, 43, 153, 7, "t"); s.line(249, 50, 402, 50, "l")
    s.next()
    # scribe strip at the wall
    s.line(402, 43, 402, F, "l"); s.line(404.5, 43, 404.5, F, "t")
    s.next()
    # dimensions
    s.dim(40, 43, 404.5, 43, "3,645", off=24)
    s.next()
    for x1, x2, lab in ((40, 100, "600"), (100, 176, "760"), (176, 251, "750"),
                        (251, 311, "600"), (311, 404.5, "935")):
        s.dim(x1, F + 2, x2, F + 2, lab, off=-14)
    s.next()
    s.dim(405, 208, 405, F, "910", off=9)
    s.next()
    s.callout(370, 132, 434, 120, "Fridge panel", "start", minor=True)
    s.callout(296, 150, 434, 160, "Tall pantry", "start", minor=True)
    s.callout(150, 126, 162, 52, "Hood", "start", minor=True)
    s.callout(403, 250, 434, 262, "Scribe strip", "start", minor=True)
    return s


def builtin():
    s = Sheet("builtin", 530, 372, "Built-in wall, elevation",
              alt="Shop drawing of a built-in wall: a fireplace with mantel and surround, "
                  "flanked by bookcases over cabinets, with crown moulding at the ceiling.")
    F, C = 300, 32
    s.line(18, F, 452, F); s.line(18, C, 452, C, "c")
    s.next()
    # crown band
    for y in (C + 8, C + 13, C + 18, C + 26):
        s.line(40, y, 400, y, "t" if y != C + 26 else "l")
    s.next()
    for x0 in (40, 280):
        # lower cabinets
        s.rect(x0, 220, 120, 70)
        s.door(x0 + 2, 222, 58, 66, hside="r"); s.door(x0 + 60, 222, 58, 66, hside="l")
        s.rect(x0 - 1, 215, 122, 5, "l")
        s.line(x0, F - 10, x0 + 120, F - 10, "t")
        s.next()
        # shelving, two bays
        s.rect(x0, 58, 120, 157)
        s.line(x0 + 60, 58, x0 + 60, 215, "l")
        for y in (90, 122, 154, 186):
            s.rect(x0 + 2, y, 56, 2.4, "t"); s.rect(x0 + 62, y, 56, 2.4, "t")
        for x in (x0 + 30, x0 + 90):
            s.circle(x, 61.5, 1.1, "dot")
        s.next()
    # fireplace surround and opening
    s.rect(160, 196, 120, 104)
    s.rect(150, 192, 140, 4.5, "l")
    s.rect(176, 226, 88, 74, "l")
    s.rect(180, 230, 80, 70, "t")
    s.next()
    # overmantel frame
    s.rect(182, 104, 76, 64, "c")
    s.rect(160, 58, 120, 134, "t")
    s.next()
    s.dim(40, C, 400, C, "3,600", off=14)
    s.next()
    s.dim(402, C, 402, F, "2,700", off=11)
    s.next()
    s.callout(220, 194, 220, 330, "Mantel", "middle")
    s.callout(70, 140, 70, 330, "Adjustable shelves", "middle", minor=True)
    s.callout(340, 256, 434, 262, "Vented door", "start", minor=True)
    s.callout(400, 150, 434, 150, "Scribed", "start", minor=True)
    return s


def panelling():
    s = Sheet("panelling", 470, 372, "Panelling and sections",
              alt="Shop drawing of raised panel wainscot and upper panels with a built-up "
                  "cornice, beside hatched sections through the cornice and the baseboard.")
    F, C = 300, 40
    s.line(18, F, 300, F); s.line(18, C, 300, C, "c")
    s.next()
    # cornice
    for y, c in ((C, "l"), (C + 6, "t"), (C + 11, "t"), (C + 17, "t"), (C + 22, "l")):
        s.line(26, y, 300, y, c)
    s.next()
    # baseboard and rail
    s.rect(26, 285, 274, 15); s.line(26, 288, 300, 288, "t")
    s.rect(26, 206, 274, 7); s.line(26, 209.5, 300, 209.5, "t")
    s.next()
    xs = [30 + i * 54 for i in range(5)]
    for x in xs:
        # wainscot panel, raised field
        s.rect(x, 220, 46, 58); s.rect(x + 6, 226, 34, 46, "t")
        s.next(0)
    s.next()
    for x in xs:
        s.rect(x, 72, 46, 126); s.rect(x + 6, 78, 34, 114, "t")
    s.next()
    # sections, larger scale
    W = 330
    s.line(W, 46, W, 150, "l"); s.line(W, 46, 452, 46, "l")
    crown = (f"M{W},140 L{W + 6},140 L{W + 6},128 "
             f"C{W + 22},128 {W + 18},104 {W + 40},100 "
             f"C{W + 62},96 {W + 58},70 {W + 82},64 "
             f"L{W + 82},52 L{W + 96},52 L{W + 96},46 L{W},46 Z")
    s.hatch(crown); s.path(crown, "l")
    s.text(W + 6, 164, "Cornice, matched", "x")
    s.next()
    s.line(W, 196, W, F, "l"); s.line(W, F, 452, F, "l")
    base = (f"M{W},{F} L{W + 16},{F} L{W + 16},226 "
            f"C{W + 16},218 {W + 9},216 {W + 9},210 L{W + 9},200 L{W},200 Z")
    s.hatch(base); s.path(base, "l")
    s.text(W + 26, 236, "Base section", "x")
    s.next()
    s.dim(W + 96, 46, W + 96, 140, "180", off=18, minor=True)
    s.dim(W + 16, 200, W + 16, F, "200", off=26, minor=True)
    s.next()
    s.callout(77, 250, 77, 330, "Raised field", "middle", minor=True)
    return s


def bar():
    s = Sheet("bar", 470, 372, "Bar, section",
              alt="Shop drawing in section through a bar: guest side with footrail and "
                  "timber bar die, the working aisle, and back bar cabinets and shelving.")
    F, C = 300, 30
    s.line(10, F, 460, F); s.line(10, C, 460, C, "c")
    s.next()
    # bar top, hatched
    top = "M38,193 L140,193 L140,198 L38,198 Z"
    s.hatch(top); s.path(top)
    s.next()
    # die with boards
    s.rect(64, 198, 7, 92)
    for y in range(206, 288, 9):
        s.line(57, y, 64, y, "t")
    s.rect(57, 198, 7, 92, "t")
    s.rect(56, 290, 15, 10, "l")
    s.next()
    # footrail on bracket
    s.circle(49, 280, 3.4)
    s.path("M52,280 L57,280", "l")
    s.next()
    # underbar
    s.rect(76, 214, 62, 76)
    s.rect(76, 208, 62, 6, "t")
    s.rect(132, 218, 5, 12, "l")
    for x in (82, 96, 110):
        s.line(x, 230, x, 284, "t")
    s.next()
    # back bar cabinet with undercounter fridge
    s.rect(196, 208, 62, 82)
    s.rect(195, 204, 64, 4, "l")
    s.rect(201, 214, 52, 70, "t")
    for y in range(219, 280, 6):
        s.line(205, y, 249, y, "t")
    s.next()
    # shelving and lighting
    s.line(258, 70, 258, 204, "l")
    for y in (176, 146, 116, 86):
        s.rect(226, y, 32, 2.4, "l")
        s.line(230, y + 3.6, 254, y + 3.6, "led")
    for x, h in ((232, 20), (240, 24), (248, 18)):
        s.path(f"M{x - 2.4},{176} L{x - 2.4},{176 - h + 6} C{x - 2.4},{176 - h + 2} {x - 1},{176 - h} {x - 1},{176 - h - 4} "
               f"L{x + 1},{176 - h - 4} C{x + 1},{176 - h} {x + 2.4},{176 - h + 2} {x + 2.4},{176 - h + 6} L{x + 2.4},{176}", "t")
    s.next()
    s.dim(24, 193, 24, F, "1,070", off=0)
    s.dim(43, 280, 43, F, "200", off=-14, minor=True)
    s.next()
    s.dim(138, F + 2, 196, F + 2, "900 aisle", off=-14)
    s.next()
    s.callout(67, 240, 120, 150, "Timber bar die", "middle")
    s.callout(134, 224, 168, 186, "Speed rail", "middle", minor=True)
    s.callout(226, 250, 300, 250, "Undercounter fridge", "start", minor=True)
    s.callout(254, 146, 300, 136, "Lit shelving", "start", minor=True)
    s.callout(49, 277, 60, 334, "Footrail", "middle", minor=True)
    return s


def reception():
    s = Sheet("reception", 470, 372, "Reception desk",
              alt="Shop drawing of a reception desk: slatted front with a signage panel, "
                  "a raised transaction ledge, a lowered accessible counter, and a section.")
    F = 300
    s.line(10, F, 460, F)
    s.next()
    # main desk front, slatted
    s.rect(40, 190, 230, 110)
    for x in range(46, 268, 6):
        s.line(x, 196, x, 294, "t")
    s.next()
    s.rect(120, 216, 70, 40, "l"); s.rect(124, 220, 62, 32, "c")
    s.next()
    # ledge
    s.rect(36, 184, 238, 6, "l")
    s.next()
    # accessible counter
    s.rect(270, 214, 72, 86)
    s.rect(268, 209, 76, 5, "l")
    s.next()
    # section
    X = 380
    ledge = f"M{X},184 L{X + 40},184 L{X + 40},190 L{X},190 Z"
    s.hatch(ledge); s.path(ledge)
    s.rect(X + 4, 190, 6, 110, "l")
    work = f"M{X + 10},226 L{X + 70},226 L{X + 70},231 L{X + 10},231 Z"
    s.hatch(work); s.path(work)
    s.rect(X + 14, 236, 30, 8, "t")
    s.line(X + 66, 231, X + 66, F, "t")
    s.next()
    s.dim(24, 184, 24, F, "1,100", off=0)
    s.dim(352, 209, 352, F, "860", off=0)
    s.dim(X + 76, 226, X + 76, F, "740", off=0, minor=True)
    s.next()
    s.callout(155, 236, 155, 160, "Signage panel", "middle")
    s.callout(306, 211, 306, 170, "Accessible counter", "middle")
    s.callout(X + 29, 240, X + 52, 206, "Cable tray", "middle", minor=True)
    s.callout(X + 20, 187, X + 20, 160, "Ledge", "middle", minor=True)
    return s


def retail():
    s = Sheet("retail", 530, 372, "Display wall, elevation",
              alt="Shop drawing of a retail display wall: four bays of adjustable "
                  "shelving over storage drawers, with a lit header band.")
    F, C = 300, 32
    s.line(10, F, 460, F); s.line(10, C, 460, C, "c")
    s.next()
    s.rect(30, 54, 400, 18, "l"); s.line(34, 68, 426, 68, "led")
    s.next()
    bays = [30 + i * 100 for i in range(4)]
    for x in bays:
        s.rect(x, 72, 100, 178)
        s.line(x + 4, 76, x + 4, 246, "t"); s.line(x + 96, 76, x + 96, 246, "t")
        s.next(0)
    s.next()
    import random
    rnd = random.Random(7)
    for i, x in enumerate(bays):
        ys = (110, 150, 196) if i % 2 == 0 else (124, 178)
        for y in ys:
            s.rect(x + 4, y, 92, 2.6, "l")
            # product silhouettes, quiet
            px = x + 10
            while px < x + 86:
                w = rnd.choice((8, 10, 12)); h = rnd.choice((12, 16, 20))
                if px + w > x + 90:
                    break
                s.rect(px, y - h, w, h, "c")
                px += w + 4
        s.next()
    for x in bays:
        s.drawer(x + 2, 252, 96, 22); s.drawer(x + 2, 274, 96, 20)
    s.next()
    s.dim(30, 54, 430, 54, "4,000", off=12)
    s.next()
    s.dim(432, 54, 432, F, "2,460", off=9)
    s.next()
    s.callout(230, 62, 300, 22, "Lit header", "start", minor=True)
    s.callout(400, 150, 452, 150, "Adjustable", "start", minor=True)
    s.callout(180, 284, 180, 334, "Storage drawers", "middle")
    return s


def plan():
    s = Sheet("plan", 470, 372, "Kitchen and living, plan",
              alt="Shop drawing of a floor plan: an L-shaped kitchen with island seating, "
                  "tall pantry and fridge, a window, a door swing and a media wall.")
    X0, Y0, X1, Y1 = 40, 40, 420, 296
    t = 9
    walls = (f"M{X0 - t},{Y0 - t} L{X1 + t},{Y0 - t} L{X1 + t},{Y1 + t} L{X0 - t},{Y1 + t} Z "
             f"M{X0},{Y0} L{X0},{Y1} L{X1},{Y1} L{X1},{Y0} Z")
    s._add(f'<path class="dw-wall" d="{walls}" fill-rule="evenodd"/>')
    s.next()
    # window in the top wall, door in the right
    s.rect(196, Y0 - t, 96, t, "win"); s.line(196, Y0 - t / 2, 292, Y0 - t / 2, "t")
    s.rect(X1, 206, t, 56, "win")
    s.path(f"M{X1},206 A56,56 0 0 0 {X1 - 56},262", "c"); s.line(X1, 262, X1 - 56, 262, "l")
    s.next()
    # L-shaped run
    s.rect(X0, Y0, 250, 40); s.rect(X0, Y0 + 40, 40, 116)
    s.line(X0 + 4, Y0 + 44, X0 + 246, Y0 + 44, "c")
    s.rect(150, 46, 34, 26, "t", rx=4)
    for cx, cy in ((216, 52), (230, 52), (216, 66), (230, 66)):
        s.circle(cx, cy, 4.2, "t")
    s.next()
    s.rect(X0, 136, 40, 60, "l"); s.line(X0, 136, X0 + 40, 196, "t"); s.line(X0 + 40, 136, X0, 196, "t")
    s.next()
    # island and stools
    s.rect(140, 128, 140, 56)
    s.line(140, 172, 280, 172, "c")
    for cx in (162, 192, 222, 252):
        s.circle(cx, 198, 8, "t")
    s.next()
    # media wall
    s.rect(290, Y1 - 22, 124, 22)
    s.rect(316, Y1 - 20, 72, 6, "c")
    s.next()
    s.dim(X0, Y0 - t, X1, Y0 - t, "6,100", off=12)
    s.dim(X0 - t, Y0, X0 - t, Y1, "4,200", off=-14)
    s.next()
    s.callout(210, 156, 210, 236, "Island, four seats", "middle")
    s.callout(60, 166, 96, 236, "Tall pantry", "start", minor=True)
    s.callout(352, Y1 - 11, 352, 240, "Media wall", "middle")
    return s


# ── process vignettes, smaller sheets ───────────────────────────────────────
def measure():
    s = Sheet("measure", 320, 236, "Site measure", note="Readings in mm",
              alt="Drawing of a room corner being measured: a leaning wall, a level line, "
                  "a plumb line and widths recorded at three heights.")
    s.line(20, 196, 300, 196)
    s.path("M40,196 L46,30", "l")
    s.path("M280,196 L279,30", "l")
    s.line(20, 30, 300, 30, "c")
    s.next()
    s.line(40, 120, 300, 120, "las")
    s.line(52, 30, 52, 196, "las")
    s.next()
    for y, lab in ((180, "2,417"), (120, "2,421"), (52, "2,426")):
        x1 = 40 + (196 - y) * 6 / 166
        s.line(x1, y, 280 - (196 - y) / 166, y, "d")
        s.text(160, y - 4, lab, "n", "middle")
        s.next()
    s.callout(44, 70, 98, 74, "Wall leans 6 mm", "start", minor=True)
    s.text(160, 214, "Floor falls 4 mm left to right", "x", "middle", minor=True)
    return s


def draw():
    s = Sheet("draw", 320, 236, "Shop drawing",
              alt="A small shop drawing of a cabinet: two doors over three drawers, "
                  "with a chain of dimensions.")
    s.line(30, 190, 290, 190)
    s.next()
    s.door(60, 50, 50, 80); s.door(110, 50, 50, 80, hside="l")
    s.next()
    for y, h in ((130, 18), (148, 20), (168, 22)):
        s.drawer(60, y, 100, h)
    s.next()
    s.door(176, 50, 84, 140, hside="l")
    s.next()
    s.dim(60, 50, 160, 50, "1,000", off=12)
    s.dim(176, 50, 260, 50, "840", off=12)
    s.dim(268, 50, 268, 190, "1,400", off=4)
    s.next()
    for y1, y2, lab in ((130, 148, "180"), (148, 168, "200"), (168, 190, "220")):
        s.dim(46, y1, 46, y2, lab, off=0, minor=True)
    s.next()
    s.callout(218, 120, 300, 20, "Approved before cutting", "end", minor=True)
    return s


def build():
    s = Sheet("build", 320, 236, "Carcass, exploded", note="Dry fitted before delivery",
              alt="Exploded isometric drawing of a cabinet carcass: two sides, top, "
                  "bottom, back, a shelf and a door pulled apart along assembly lines.")
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    ox, oy = 150, 150

    def P(x, y, z):
        return (ox + (x - z) * c30, oy + (x + z) * s30 - y)

    def box(x, y, z, w, h, d, cls="l"):
        a = [P(x, y + h, z), P(x + w, y + h, z), P(x + w, y + h, z + d), P(x, y + h, z + d)]
        f = [P(x, y, z + d), P(x + w, y, z + d), P(x + w, y + h, z + d), P(x, y + h, z + d)]
        r = [P(x + w, y, z), P(x + w, y, z + d), P(x + w, y + h, z + d), P(x + w, y + h, z)]
        for face, c in ((a, "fa"), (r, "fb"), (f, "fc")):
            d_ = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in face) + " Z"
            s.fillpath(d_, c)
            s.path(d_, cls)

    W, H, D, t = 60, 76, 56, 3
    gap = 16
    box(t, 2, -gap - 4, W - 2 * t, H - 4, 1.5)         # back, farthest
    s.next()
    box(-gap, 0, 0, t, H, D)                           # left side, pulled out
    s.next()
    box(0, -gap, 0, W, t, D)                           # bottom
    s.next()
    box(t, H * .5, 3, W - 2 * t, t, D - 6)             # shelf
    s.next()
    box(0, H - t + gap, 0, W, t, D)                    # top
    s.next()
    box(W - t + gap, 0, 0, t, H, D)                    # right side
    s.next()
    box(-1, 0, D + gap + 6, W + 2, H, 3)               # door, nearest
    s.next()
    for a, b in (((-gap, H / 2, D / 2), (0, H / 2, D / 2)),
                 ((W + gap, H / 2, D / 2), (W, H / 2, D / 2)),
                 ((W / 2, H / 2, D + gap + 6), (W / 2, H / 2, D))):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        s.line(x1, y1, x2, y2, "c")
    return s


def install():
    s = Sheet("install", 320, 236, "Scribe at the wall, plan",
              alt="Plan detail of a cabinet meeting an uneven wall: the wall as built, "
                  "the scribe line traced from it, and the trimmed scribe strip.")
    wall = "M40,20 C52,60 34,96 46,132 C58,168 38,190 48,216"
    s.path(wall, "l")
    s.fillpath(wall + " L20,216 L20,20 Z", "hx")
    s.next()
    s.rect(70, 40, 190, 160)
    s.rect(74, 44, 182, 152, "t")
    s.next()
    scribe = "M56,40 C60,64 50,96 56,132 C62,168 54,186 58,200 L70,200 L70,40 Z"
    s.fillpath(scribe, "fc"); s.path(scribe, "l")
    s.next()
    s.path("M41,40 C52,64 40,96 47,132 C54,168 42,186 49,200", "las")
    s.next()
    s.callout(44, 110, 120, 222, "Wall as built", "middle", minor=True)
    s.callout(60, 76, 120, 26, "Scribe strip", "start")
    return s


SHEETS = {f.__name__: f for f in (kitchen, builtin, panelling, bar, reception, retail,
                                  plan, measure, draw, build, install)}
_CACHE = {}


def drawing(key, uid="", cls=""):
    """Inline SVG for a sheet. uid keeps ids unique if a page repeats a sheet."""
    if key not in _CACHE:
        _CACHE[key] = SHEETS[key]()
    return _CACHE[key].svg(uid=uid, cls=cls)


def alt(key):
    if key not in _CACHE:
        _CACHE[key] = SHEETS[key]()
    return _CACHE[key].alt


if __name__ == "__main__":
    import os
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "drawings.html")
    css = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "css", "style.css")).read()
    body = "".join(f'<figure style="margin:20px;max-width:720px">{drawing(k)}<figcaption>{k}</figcaption></figure>'
                   for k in SHEETS)
    open(out, "w").write(f"<!doctype html><meta charset=utf-8><style>{css}</style><body>{body}")
    print(out)
