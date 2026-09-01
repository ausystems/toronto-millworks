#!/usr/bin/env python3
"""
Art-directed image library.

Every image is declared as a focal point plus a coverage scale, not as a fixed
box. The crop for each orientation is then computed around that focal point, so
the portrait variant a phone gets is a real composition of the same subject
rather than a wide plate squeezed into a tall hole.

    python3 scripts/build_library.py
"""
import os, sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "lib")

RESI = os.path.join(ROOT, "assets/img/toronto-custom-millwork-interior-7680.webp")
SEQ = os.path.join(ROOT, "assets/millwork-fit-out-sequence/3840")

# name -> (source, focal x, focal y, coverage, alt)
# coverage is the fraction of source height the crop spans at 3:2.
PLATES = {
    "cornice":    ("resi", 0.31, 0.21, 0.40,
                   "Gilded ornamental cornice and cove lighting on a tray ceiling"),
    "coffer":     ("resi", 0.70, 0.26, 0.46,
                   "Coffered ceiling, crown moulding and recessed lighting"),
    "doors":      ("resi", 0.15, 0.70, 0.54,
                   "French doors with divided lights framed by raised wall panelling"),
    "panel-corner":("resi", 0.38, 0.68, 0.54,
                   "Raised panel wall meeting a cased window opening"),
    "archway":    ("resi", 0.58, 0.70, 0.54,
                   "A cased archway opening onto a panelled room"),
    "sconce":     ("resi", 0.76, 0.73, 0.48,
                   "A wall sconce washing light across raised wall panelling"),
    "room":       ("resi", 0.52, 0.56, 0.58,
                   "Panelled room with coffered ceiling, gilded cornice and tall windows"),
    "base":       ("resi", 0.50, 0.84, 0.26,
                   "Panel base, plinth and skirting meeting a hardwood floor"),

    "shell":      (1,   0.50, 0.55, 0.86,
                   "Bare brick and concrete shell before the fit-out begins"),
    "lit":        (24,  0.50, 0.55, 0.86,
                   "The shell cleaned back and the floor laid"),
    "feature":    (48,  0.50, 0.55, 0.86,
                   "A black feature wall and filament lighting installed"),
    "carcass":    (71,  0.46, 0.64, 0.78,
                   "The reclaimed timber bar counter installed against the brick"),
    "finished":   (118, 0.48, 0.60, 0.84,
                   "The finished bar with counter, shelving and equipment in place"),
    "counter":    (118, 0.44, 0.78, 0.42,
                   "Reclaimed timber boards laid up in a running bond on the bar front"),
}

ASPECTS = {
    "wide": (3 / 2, [1000, 1600, 2400]),
    "tall": (4 / 5, [640, 1000, 1500]),
}


def box(W, H, fx, fy, cover, aspect):
    """Crop box of the given aspect, centred on the focal point, clamped in."""
    h = cover * H
    w = h * aspect
    if w > W:
        w = W
        h = w / aspect
    if h > H:
        h = H
        w = h * aspect
    x0 = min(max(fx * W - w / 2, 0), W - w)
    y0 = min(max(fy * H - h / 2, 0), H - h)
    return (round(x0), round(y0), round(x0 + w), round(y0 + h))


def main():
    os.makedirs(OUT, exist_ok=True)
    resi = Image.open(RESI)
    cache = {}
    total = 0

    for name, (src, fx, fy, cover, _alt) in PLATES.items():
        if src == "resi":
            im = resi
        else:
            p = os.path.join(SEQ, f"{src:03d}.webp")
            if p not in cache:
                cache[p] = Image.open(p).convert("RGB")
            im = cache[p]
        W, H = im.size

        for key, (aspect, widths) in ASPECTS.items():
            crop = im.crop(box(W, H, fx, fy, cover, aspect))
            for w in widths:
                h = round(w / aspect)
                # these crops come off an already reconstructed master, so a
                # modest resample holds up. Past 1.5x it does not, so stop there.
                if w > crop.width * 1.5:
                    continue
                out = crop.resize((w, h), Image.LANCZOS)
                path = os.path.join(OUT, f"{name}-{key}-{w}.webp")
                out.save(path, "WEBP", quality=86, method=6)
                total += os.path.getsize(path)
        print(f"  {name:<14} done")

    print(f"\n{len(os.listdir(OUT))} files, {total/1e6:.1f} MB -> assets/img/lib")


if __name__ == "__main__":
    main()
