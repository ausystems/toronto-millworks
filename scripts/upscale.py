#!/usr/bin/env python3
"""
Maximum-quality upscale of the Toronto Millworks hero plate.

Pipeline
  1. decode -> float32, sRGB -> linear light
  2. progressive Lanczos-3 upscale in linear light (1024 -> 2048 -> 4096)
  3. iterative back-projection against the true 1024 source  (real SR refinement)
  4. edge-aware unsharp, linear -> sRGB, tiny dither to kill webp banding
  5. final Lanczos step to 8K + light detail pass
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

def linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055).astype(np.float32)


# ---------- float resize (per channel, mode 'F', full precision) ----------
def resize_f(arr, size):
    h, w = size[1], size[0]
    out = np.empty((h, w, arr.shape[2]), np.float32)
    for c in range(arr.shape[2]):
        im = Image.fromarray(arr[:, :, c], mode="F")
        out[:, :, c] = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32)
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
    blur = np.empty_like(lin)
    for c in range(3):
        blur[:, :, c] = ndimage.gaussian_filter(lin[:, :, c], sigma)
    detail = lin - blur
    return np.clip(lin + detail * amount * edge_mask(lin), 0, None)


# ---------- load ----------
src_img = Image.open(SRC).convert("RGB")
SW, SH = src_img.size
log(f"source {SW}x{SH}")

src8 = np.asarray(src_img, np.float32) / 255.0
src_lin = srgb_to_linear(src8)

# ---------- 2. progressive upscale in linear light ----------
cur = src_lin
for target in (2048, 4096):
    cur = resize_f(cur, (target, target))
    cur = sharpen(cur, 0.28, 0.9)
    log(f"lanczos -> {target}")

# ---------- 3. iterative back-projection ----------
# HR is correct when downsampling it reproduces the original 1024 plate.
ITERS = 8
for i in range(ITERS):
    down = resize_f(cur, (SW, SH))
    err = src_lin - down
    cur = cur + resize_f(err, (4096, 4096)) * 0.62
    cur = np.clip(cur, 0.0, None)
    rms = float(np.sqrt((err ** 2).mean()))
    log(f"back-projection {i+1}/{ITERS}  residual rms={rms:.6f}")

cur = sharpen(cur, 0.34, 1.1)

# ---------- 4. back to sRGB with dither ----------
srgb = linear_to_srgb(cur)
del cur
rng = np.random.default_rng(7)
srgb += rng.normal(0.0, 0.7 / 255.0, srgb.shape).astype(np.float32)   # anti-banding
master4k = Image.fromarray(np.clip(srgb * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")
del srgb
log("4K master built")

# ---------- 5. final step to 8K ----------
master8k = master4k.resize((7680, 7680), Image.LANCZOS)
master8k = master8k.filter(ImageFilter.UnsharpMask(radius=1.6, percent=48, threshold=3))
log("8K master built")

# ---------- 6. encode ----------
def enc(img, path, q):
    img.save(path, "WEBP", quality=q, method=6)
    return os.path.getsize(path)

# full-frame square ladder
sizes = [7680, 5120, 3840, 2560, 1920, 1280]
for w in sizes:
    im = master8k if w == 7680 else master8k.resize((w, w), Image.LANCZOS)
    q = 92 if w >= 5120 else 88
    p = os.path.join(OUT, f"toronto-custom-millwork-interior-{w}.webp")
    log(f"  square {w:>5} -> {enc(im, p, q)/1e6:6.2f} MB")

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
    q = 92 if w >= 5120 else 88
    p = os.path.join(OUT, f"toronto-custom-millwork-coffered-ceiling-{w}.webp")
    log(f"  wide   {w:>5} -> {enc(im, p, q)/1e6:6.2f} MB")

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
