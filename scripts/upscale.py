#!/usr/bin/env python3
"""
Maximum-quality upscale of the Toronto Millworks hero plate.

Pipeline
  1. decode -> float32, sRGB -> linear light
  2. progressive Lanczos-3 upscale in linear light (1024 -> 2048 -> 4096 -> 8192)
  3. iterative back-projection against the true 1024 source, run at 4096 AND
     again at 8192, so the 8K plate is itself consistent with the source under
     downsampling rather than a naive stretch of a 4K reconstruction
  4. edge-aware unsharp, linear -> sRGB, tiny dither to kill webp banding
  5. supersample 8192 -> 7680, which is where the ladder is cut
  6. encode webp, method 6 (slowest / best), plus responsive ladder
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None

SRC = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

t0 = time.time()
def log(m): print(f"[{time.time()-t0:6.1f}s] {m}", flush=True)


# ---------- colour transfer ----------
def srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4).astype(np.float32)

def linear_to_srgb_blocks(a, rows=512):
    """In-place, block by block. At 8192 a whole-array np.where would spawn
    several 800 MB temporaries at once."""
    for y in range(0, a.shape[0], rows):
        b = np.clip(a[y:y + rows], 0.0, 1.0)
        a[y:y + rows] = np.where(b <= 0.0031308, b * 12.92,
                                 1.055 * np.power(b, 1 / 2.4) - 0.055)
    return a


# ---------- float resize (per channel, mode 'F', full precision) ----------
def resize_f(arr, size):
    h, w = size[1], size[0]
    out = np.empty((h, w, arr.shape[2]), np.float32)
    for c in range(arr.shape[2]):
        im = Image.fromarray(np.ascontiguousarray(arr[:, :, c]), mode="F")
        out[:, :, c] = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32)
        del im
    return out


# ---------- edge-aware unsharp in linear light ----------
def edge_mask(lin):
    lum = lin[:, :, 0] * 0.2126 + lin[:, :, 1] * 0.7152 + lin[:, :, 2] * 0.0722
    gx = ndimage.sobel(lum, 0)
    gy = ndimage.sobel(lum, 1)
    g = np.hypot(gx, gy)
    g /= (g.max() + 1e-8)
    # push mid/strong edges to 1, leave flat ceiling planes near 0
    return np.clip(g * 3.2, 0, 1).astype(np.float32)[:, :, None]


def sharpen(lin, amount, sigma):
    m = edge_mask(lin)
    for c in range(3):
        blur = ndimage.gaussian_filter(lin[:, :, c], sigma)
        lin[:, :, c] += (lin[:, :, c] - blur) * amount * m[:, :, 0]
        del blur
    np.clip(lin, 0, None, out=lin)
    return lin


def backproject(cur, src_lin, size, iters, gain=0.62):
    """HR is correct when downsampling it reproduces the original plate."""
    SW, SH = src_lin.shape[1], src_lin.shape[0]
    for i in range(iters):
        down = resize_f(cur, (SW, SH))
        err = src_lin - down
        del down
        rms = float(np.sqrt((err ** 2).mean()))
        up = resize_f(err, size)
        del err
        np.multiply(up, gain, out=up)
        cur += up
        del up
        np.clip(cur, 0.0, None, out=cur)
        log(f"  back-projection @{size[0]} {i+1}/{iters}  residual rms={rms:.6f}")
    return cur


# ---------- load ----------
src_img = Image.open(SRC).convert("RGB")
SW, SH = src_img.size
log(f"source {SW}x{SH}")

src8 = np.asarray(src_img, np.float32) / 255.0
src_lin = srgb_to_linear(src8)
del src8

# ---------- 2/3. progressive upscale with back-projection at each octave ----
cur = src_lin
for target in (2048, 4096):
    cur = resize_f(cur, (target, target))
    cur = sharpen(cur, 0.28, 0.9)
    log(f"lanczos -> {target}")

cur = backproject(cur, src_lin, (4096, 4096), 8)
cur = sharpen(cur, 0.30, 1.0)

# the 8K octave. Going straight to encode from 4096 was a plain 1.875x stretch;
# reconstructing here is what actually puts detail in the shipped plate.
cur = resize_f(cur, (8192, 8192))
log("lanczos -> 8192")
cur = backproject(cur, src_lin, (8192, 8192), 6)
cur = sharpen(cur, 0.34, 1.6)

# ---------- 4. back to sRGB with dither ----------
linear_to_srgb_blocks(cur)
rng = np.random.default_rng(7)
for y in range(0, cur.shape[0], 512):                      # anti-banding
    cur[y:y + 512] += rng.normal(0.0, 0.7 / 255.0, cur[y:y + 512].shape).astype(np.float32)

master = Image.fromarray(np.clip(cur * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")
del cur
log("8192 master built")

# ---------- 5. supersample down to the ladder's top rung ----------
master8k = master.resize((7680, 7680), Image.LANCZOS)
del master
master8k = master8k.filter(ImageFilter.UnsharpMask(radius=1.3, percent=34, threshold=3))
log("7680 master built")

# ---------- 6. encode ----------
def enc(img, path, q):
    img.save(path, "WEBP", quality=q, method=6)
    return os.path.getsize(path)

def q_for(w):
    return 93 if w >= 5120 else (90 if w >= 2560 else 88)

# full-frame square ladder
for w in [7680, 5120, 3840, 2560, 1920, 1280]:
    im = master8k if w == 7680 else master8k.resize((w, w), Image.LANCZOS)
    p = os.path.join(OUT, f"toronto-custom-millwork-interior-{w}.webp")
    log(f"  square {w:>5} -> {enc(im, p, q_for(w))/1e6:6.2f} MB")

# wide 16:9 hero crop: keeps the full gilded cornice while opening up the
# room (windows, panelling, archway beam, sconce)
W8 = 7680
CH = round(W8 * 9 / 16)                 # 4320
CENTRE = float(os.environ.get("CROP_CENTRE", "0.54"))   # shipped framing
top = round(CENTRE * W8 - CH / 2)
top = max(0, min(W8 - CH, top))
wide8k = master8k.crop((0, top, W8, top + CH))
log(f"wide crop y={top}..{top+CH}")

for w in [7680, 5120, 3840, 2560, 1920, 1280]:
    h = round(w * 9 / 16)
    im = wide8k if w == W8 else wide8k.resize((w, h), Image.LANCZOS)
    p = os.path.join(OUT, f"toronto-custom-millwork-coffered-ceiling-{w}.webp")
    log(f"  wide   {w:>5} -> {enc(im, p, q_for(w))/1e6:6.2f} MB")

# 4:5 portrait panel for the craft section, archway, sconce and layered
# panelling. Native region is 4064px wide, so no rung upscales past the master.
PL, PT, PW, PH = 3600, 2400, 4064, 5080
panel = master8k.crop((PL, PT, PL + PW, PT + PH))
log(f"craft panel {panel.size}")

for w in [3200, 2400, 1600, 1200, 800]:
    h = round(w * 5 / 4)
    im = panel.resize((w, h), Image.LANCZOS)
    q = 90 if w >= 2400 else 88
    p = os.path.join(OUT, f"toronto-custom-cabinetry-wall-panelling-{w}.webp")
    log(f"  craft  {w:>5} -> {enc(im, p, q)/1e6:6.2f} MB")

log("done")
