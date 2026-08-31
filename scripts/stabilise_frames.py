#!/usr/bin/env python3
"""
Stabilise the fit-out sequence so every frame is shot from the same place.

For each frame it solves a similarity transform (uniform scale + translation)
against frame 1, by brute forcing scale and using phase correlation on edge
maps for translation at each candidate. Edge maps because the lighting changes
completely across the sequence; the correlation peak height picks the scale.

It then inverts that transform, computes the rectangle that stays valid across
every frame, and crops all frames to it. That crop is the small zoom in needed
to hide the drift.

    python3 stabilise.py <src_png_dir> <out_dir>
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from numpy.fft import fft2, ifft2

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
frames = sorted(f for f in os.listdir(SRC) if f.endswith(".png"))

WORK = 640          # analysis resolution
SCALES = np.arange(0.975, 1.0301, 0.0015)


def edge_map(img, size=WORK):
    a = np.asarray(img.convert("L").resize((size, round(size * img.height / img.width)),
                                           Image.LANCZOS), np.float32)
    g = np.hypot(ndimage.sobel(a, 0), ndimage.sobel(a, 1))
    return g / (g.std() + 1e-6)


def corr(a, b):
    """Phase correlation. Returns (dx, dy, peak) where shifting a by (dx,dy)
    lines it up with b."""
    wy = np.hanning(a.shape[0])[:, None]
    wx = np.hanning(a.shape[1])[None, :]
    A = fft2(a * wy * wx)
    B = fft2(b * wy * wx)
    R = A * np.conj(B)
    R /= (np.abs(R) + 1e-9)
    r = np.real(ifft2(R))
    pk = np.unravel_index(np.argmax(r), r.shape)
    H, W = r.shape

    def sub(axis, i):
        n = H if axis == 0 else W
        if axis == 0:
            m1, p1 = r[(i - 1) % n, pk[1]], r[(i + 1) % n, pk[1]]
        else:
            m1, p1 = r[pk[0], (i - 1) % n], r[pk[0], (i + 1) % n]
        c = r[pk]
        d = (m1 - p1) / (2 * (m1 - 2 * c + p1) + 1e-9)
        v = i + d
        return v - n if v > n / 2 else v

    return sub(1, pk[1]), sub(0, pk[0]), float(r[pk])


# ── solve ────────────────────────────────────────────────────────────────────
ref_img = Image.open(os.path.join(SRC, frames[0])).convert("RGB")
W0, H0 = ref_img.size
ref = edge_map(ref_img)
rh, rw = ref.shape

print(f"{len(frames)} frames, {W0}x{H0}, solving similarity transform per frame")
sol = []
for i, f in enumerate(frames):
    im = Image.open(os.path.join(SRC, f)).convert("RGB")

    def score(s):
        """Correlation peak for a candidate scale, plus its translation."""
        sw, sh = round(rw * s), round(rh * s)
        e = edge_map(im, size=round(WORK * s))
        e = e[:sh, :sw]
        canvas = np.zeros_like(ref)
        oy, ox = (sh - rh) // 2, (sw - rw) // 2
        if oy >= 0 and ox >= 0:
            canvas = e[oy:oy + rh, ox:ox + rw]
        else:
            py, px = max(0, -oy), max(0, -ox)
            canvas[py:py + e.shape[0], px:px + e.shape[1]] = e[:rh - py, :rw - px]
        dx, dy, pk = corr(canvas, ref)
        return (s, dx, dy, pk)

    best = max((score(s) for s in SCALES), key=lambda r: r[3])
    s, dx, dy, pk = best
    # convert analysis-resolution shift to source pixels
    k = W0 / rw
    sol.append((s, dx * k, dy * k, pk))
    if i % 12 == 0 or i == len(frames) - 1:
        print(f"  frame {i+1:>3}  scale {s:.4f}  dx {dx*k:+7.2f}  dy {dy*k:+7.2f}  peak {pk:.4f}")

S = np.array([r[0] for r in sol])
DX = np.array([r[1] for r in sol])
DY = np.array([r[2] for r in sol])
print(f"\n  raw solve: scale span {np.ptp(S)*100:.2f} %   dx span {np.ptp(DX):.1f} px   dy span {np.ptp(DY):.1f} px")

# The camera does not wander, it steps: locked for one run of frames, then a
# fixed offset for the next. Solving each frame independently therefore adds
# jitter that was never in the footage. Detect the runs and give every frame in
# a run the same transform, so within a segment the alignment is exact.
seg, segs = [0], []
for i in range(1, len(DX)):
    if abs(DX[i] - DX[i - 1]) > 3.0 or abs(DY[i] - DY[i - 1]) > 3.0:
        segs.append(seg); seg = []
    seg.append(i)
segs.append(seg)
segs = [g for g in segs if g]
print(f"  {len(segs)} camera position(s) detected:")
for g in segs:
    ms, mdx, mdy = np.median(S[g]), np.median(DX[g]), np.median(DY[g])
    print(f"    frames {g[0]+1:>3}-{g[-1]+1:<3}  scale {ms:.4f}  dx {mdx:+6.2f}  dy {mdy:+6.2f}")
    for i in g:
        sol[i] = (ms, mdx, mdy, sol[i][3])
S = np.array([r[0] for r in sol]); DX = np.array([r[1] for r in sol]); DY = np.array([r[2] for r in sol])

# ── closed loop refinement ───────────────────────────────────────────────────
# The segment medians leave a sub-pixel step at the seam between camera
# positions. Warp a representative frame from each segment the way the renderer
# will, measure what is still off against the warped reference, and fold that
# back in. Signs are resolved empirically rather than reasoned about.
def warp_edges(idx, s_, dx_, dy_):
    im = Image.open(os.path.join(SRC, frames[idx])).convert("RGB")
    cx_, cy_ = W0 / 2, H0 / 2
    x0 = cx_ + (0 - cx_) / s_ + dx_
    x1 = cx_ + (W0 - cx_) / s_ + dx_
    y0 = cy_ + (0 - cy_) / s_ + dy_
    y1 = cy_ + (H0 - cy_) / s_ + dy_
    return edge_map(im.transform((W0, H0), Image.EXTENT, (x0, y0, x1, y1), Image.BICUBIC))

ref_out = warp_edges(0, *sol[0][:3])
for it in range(3):
    moved = 0.0
    for g in segs:
        if g[0] == 0:
            continue                       # segment one defines the reference
        i = g[len(g) // 2]
        s_, dx_, dy_, pk_ = sol[i]
        rdx, rdy, _ = corr(warp_edges(i, s_, dx_, dy_), ref_out)
        k2 = W0 / rw
        best = None
        for sx in (1, -1):
            for sy in (1, -1):
                cdx, cdy = dx_ + sx * rdx * k2, dy_ + sy * rdy * k2
                _, _, pk = corr(warp_edges(i, s_, cdx, cdy), ref_out)
                nrdx, nrdy, _ = corr(warp_edges(i, s_, cdx, cdy), ref_out)
                err = abs(nrdx) + abs(nrdy)
                if best is None or err < best[0]:
                    best = (err, cdx, cdy)
        moved = max(moved, abs(best[1] - dx_) + abs(best[2] - dy_))
        for j in g:
            sol[j] = (s_, best[1], best[2], pk_)
    print(f"  refine pass {it+1}: adjusted by {moved:.3f} px")
    if moved < 0.02:
        break
S = np.array([r[0] for r in sol]); DX = np.array([r[1] for r in sol]); DY = np.array([r[2] for r in sol])
for g in segs:
    print(f"    frames {g[0]+1:>3}-{g[-1]+1:<3}  final dx {DX[g[0]]:+6.3f}  dy {DY[g[0]]:+6.3f}")

# ── common valid rectangle ───────────────────────────────────────────────────
# undoing scale s and shift (dx,dy) leaves each frame covering a different
# rectangle of the reference; keep only what every frame covers.
L = R_ = T = B = 0.0
for s, dx, dy, _ in sol:
    hw, hh = W0 / 2, H0 / 2
    # after inverse scaling about centre the frame spans +-hw/s
    l = hw - hw / s - dx
    r = hw + hw / s - dx
    t = hh - hh / s - dy
    b = hh + hh / s - dy
    L = max(L, l); R_ = max(R_, W0 - r); T = max(T, t); B = max(B, H0 - b)
pad = 3
L, R_, T, B = L + pad, R_ + pad, T + pad, B + pad
cw, ch = W0 - L - R_, H0 - T - B
# keep the original aspect
target = W0 / H0
if cw / ch > target:
    cw = ch * target
else:
    ch = cw / target
cx, cy = W0 / 2, H0 / 2
print(f"  common crop {cw:.0f}x{ch:.0f} of {W0}x{H0}  "
      f"({(1 - cw/W0)*100:.1f}% trimmed, a {W0/cw:.3f}x zoom)")

# ── render ───────────────────────────────────────────────────────────────────
for i, (f, (s, dx, dy, _)) in enumerate(zip(frames, sol)):
    im = Image.open(os.path.join(SRC, f)).convert("RGB")
    # inverse transform: scale about centre by 1/s, then translate by -(dx,dy).
    # Expressed as the source box that maps onto the wanted crop.
    x0 = cx + (cx - cw / 2 - cx) / s + dx
    x1 = cx + (cx + cw / 2 - cx) / s + dx
    y0 = cy + (cy - ch / 2 - cy) / s + dy
    y1 = cy + (cy + ch / 2 - cy) / s + dy
    out = im.transform((W0, H0), Image.EXTENT, (x0, y0, x1, y1), Image.BICUBIC)
    out.save(os.path.join(OUT, f), "PNG")
    if i % 20 == 0:
        print(f"  rendered {i+1}/{len(frames)}")

print(f"\nstabilised {len(frames)} frames -> {OUT}")
