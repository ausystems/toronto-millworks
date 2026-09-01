#!/usr/bin/env python3
"""
Stabilise a frame sequence so the camera never appears to move.

Method, and why each part is there:

  Landmarks, not whole frame correlation. A grid of small patches is tracked by
  normalised cross correlation with sub-pixel refinement.

  Consecutive frames, not frame 1. Across this sequence the lighting goes from
  off to fully lit and the room fills with furniture, so matching a late frame
  against frame 1 finds the wrong local optimum and reports motion that is not
  there. Neighbouring frames share almost all their content, so the fit is
  trustworthy. Per frame transforms are then chained to get each frame's
  position relative to the first.

  Robust fitting. While the wall is being painted and fittings appear, some
  patches land on content that genuinely changed and report tens of pixels of
  bogus motion. Residuals beyond a few median absolute deviations are dropped
  and the fit repeated, so those patches cannot drag the solution.

  No segmentation. An earlier version grouped frames into discrete camera
  positions and gave each group one transform. The drift is gradual, so that
  imposed a hard step at the group boundary and made the worst visible jump
  worse than it was in the source. Every frame now gets its own transform.

    python3 scripts/stabilise_frames.py <src_png_dir> <out_dir>
"""
import os, sys
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
frames = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".png"))

PATCH = 96
SEARCH = 30
MIN_NCC = 0.45
MIN_STD = 12.0          # a flat patch carries no positional information


def gray(p):
    return np.asarray(Image.open(os.path.join(SRC, p)).convert("L"), np.float32)


def track(img, tmpl, cx, cy):
    th, tw = tmpl.shape
    y0, x0 = max(0, cy - SEARCH), max(0, cx - SEARCH)
    win = img[y0:y0 + th + 2 * SEARCH, x0:x0 + tw + 2 * SEARCH]
    if win.shape[0] < th or win.shape[1] < tw:
        return None
    t = tmpl - tmpl.mean()
    tn = np.sqrt((t * t).sum()) + 1e-9
    H, W = win.shape[0] - th + 1, win.shape[1] - tw + 1
    sc = np.empty((H, W), np.float32)
    for yy in range(H):
        for xx in range(W):
            w = win[yy:yy + th, xx:xx + tw]
            w = w - w.mean()
            sc[yy, xx] = float((w * t).sum() / ((np.sqrt((w * w).sum()) + 1e-9) * tn))
    py, px = np.unravel_index(np.argmax(sc), sc.shape)
    if sc[py, px] < MIN_NCC:
        return None

    def sub(i, axis):
        n = sc.shape[axis]
        if i <= 0 or i >= n - 1:
            return float(i)
        if axis == 0:
            m1, c, p1 = sc[i - 1, px], sc[i, px], sc[i + 1, px]
        else:
            m1, c, p1 = sc[py, i - 1], sc[py, i], sc[py, i + 1]
        return i + (m1 - p1) / (2 * (m1 - 2 * c + p1) + 1e-9)

    return x0 + sub(px, 1), y0 + sub(py, 0)


def robust_similarity(P, Q):
    """Uniform scale + translation taking P onto Q, rejecting outliers."""
    keep = np.ones(len(P), bool)
    s, t = 1.0, np.zeros(2)
    for _ in range(4):
        A, B = P[keep], Q[keep]
        if len(A) < 3:
            break
        Am, Bm = A.mean(0), B.mean(0)
        U, V = A - Am, B - Bm
        s = float((U * V).sum() / ((U * U).sum() + 1e-12))
        t = Bm - s * Am
        res = np.linalg.norm(s * P + t - Q, axis=1)
        med = np.median(res)
        mad = np.median(np.abs(res - med)) + 1e-6
        new = res < med + 3.0 * mad
        if new.sum() < 3 or (new == keep).all():
            keep = new if new.sum() >= 3 else keep
            break
        keep = new
    return s, t, int(keep.sum())


W0, H0 = Image.open(os.path.join(SRC, frames[0])).size
GRID = [(x, y) for y in range(40, H0 - PATCH - 40, 110)
        for x in range(40, W0 - PATCH - 40, 165)]
print(f"{len(frames)} frames at {W0}x{H0}, {len(GRID)} candidate landmarks per pair")

# ── chain consecutive fits ──────────────────────────────────────────────────
cum_s, cum_t = [1.0], [np.zeros(2)]
prev = gray(frames[0])
for i in range(1, len(frames)):
    cur = gray(frames[i])
    P, Q = [], []
    for (x, y) in GRID:
        t = prev[y:y + PATCH, x:x + PATCH]
        if t.std() < MIN_STD:
            continue
        r = track(cur, t, x, y)
        if r:
            P.append([x + PATCH / 2, y + PATCH / 2])
            Q.append([r[0] + PATCH / 2, r[1] + PATCH / 2])
    if len(P) < 4:
        s, t, n = 1.0, np.zeros(2), 0
    else:
        s, t, n = robust_similarity(np.array(P, float), np.array(Q, float))
    # compose onto the running transform: p -> s*(S*p + T) + t
    cum_s.append(s * cum_s[-1])
    cum_t.append(s * cum_t[-1] + t)
    if i % 20 == 0:
        print(f"  paired {i+1}/{len(frames)}  ({n} inliers)  cumulative zoom "
              f"{(cum_s[-1]-1)*100:+.2f}%  drift {cum_t[-1][0]:+.1f},{cum_t[-1][1]:+.1f}px")
    prev = cur

S = np.array(cum_s)
T = np.array(cum_t)
print(f"  measured drift: zoom {(S.min()-1)*100:+.2f}%..{(S.max()-1)*100:+.2f}%   "
      f"x {T[:,0].min():+.1f}..{T[:,0].max():+.1f}px   y {T[:,1].min():+.1f}..{T[:,1].max():+.1f}px")

# ── common valid rectangle ──────────────────────────────────────────────────
L = R_ = TP = BT = 0.0
for s, t in zip(S, T):
    L = max(L, -t[0] / s)
    TP = max(TP, -t[1] / s)
    R_ = max(R_, W0 - (W0 - t[0]) / s)
    BT = max(BT, H0 - (H0 - t[1]) / s)
pad = 4
cw = W0 - max(0.0, L) - max(0.0, R_) - 2 * pad
ch = H0 - max(0.0, TP) - max(0.0, BT) - 2 * pad
target = W0 / H0
if cw / ch > target:
    cw = ch * target
else:
    ch = cw / target
CX, CY = W0 / 2, H0 / 2
print(f"  common crop {cw:.0f}x{ch:.0f} of {W0}x{H0}  "
      f"({(1 - cw/W0)*100:.1f}% trimmed, {W0/cw:.3f}x zoom)")

# ── render ──────────────────────────────────────────────────────────────────
for i, f in enumerate(frames):
    s, t = S[i], T[i]
    im = Image.open(os.path.join(SRC, f)).convert("RGB")
    x0 = s * (CX - cw / 2) + t[0]
    x1 = s * (CX + cw / 2) + t[0]
    y0 = s * (CY - ch / 2) + t[1]
    y1 = s * (CY + ch / 2) + t[1]
    im.transform((W0, H0), Image.EXTENT, (x0, y0, x1, y1), Image.BICUBIC) \
      .save(os.path.join(OUT, f), "PNG")
    if i % 25 == 0:
        print(f"  rendered {i+1}/{len(frames)}")

print(f"\nstabilised {len(frames)} frames -> {OUT}")
