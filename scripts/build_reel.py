#!/usr/bin/env python3
"""
Build the scroll-scrubbed fit-out sequence.

Source frames are 1280x720. Each frame is reconstructed to 2560x1440 with the
same linear-light + iterative-back-projection method used for the hero plate
(scripts/upscale.py), then the 1920 and 1280 tiers are supersampled down from
that master so all three tiers share one look.

Why not 8K here: a 102-frame sequence must be fully resident in memory for the
scrub to stay smooth. At 7680px that is roughly half a gigabyte of webp, so the
ladder is capped at 2560 and the runtime picks a tier from viewport, DPR and
connection instead.

    python3 scripts/build_reel.py <frames_dir> <out_dir>
"""
import os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
from concurrent.futures import ProcessPoolExecutor

SRC_DIR = sys.argv[1]
OUT_DIR = sys.argv[2]

TIERS = [(3840, 80), (2560, 84), (1920, 84), (1280, 82)]   # (width, webp quality)
MASTER_W = 3840
IBP_ITERS = 8


def srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4).astype(np.float32)


def linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055).astype(np.float32)


def resize_f(arr, w, h):
    out = np.empty((h, w, arr.shape[2]), np.float32)
    for c in range(arr.shape[2]):
        out[:, :, c] = np.asarray(
            Image.fromarray(arr[:, :, c]).resize((w, h), Image.LANCZOS), np.float32)
    return out


def edge_mask(lin):
    lum = lin[:, :, 0] * 0.2126 + lin[:, :, 1] * 0.7152 + lin[:, :, 2] * 0.0722
    g = np.hypot(ndimage.sobel(lum, 0), ndimage.sobel(lum, 1))
    g /= (g.max() + 1e-8)
    return np.clip(g * 3.2, 0, 1).astype(np.float32)[:, :, None]


def sharpen(lin, amount, sigma):
    blur = np.empty_like(lin)
    for c in range(3):
        blur[:, :, c] = ndimage.gaussian_filter(lin[:, :, c], sigma)
    return np.clip(lin + (lin - blur) * amount * edge_mask(lin), 0, None)


def build_frame(job):
    idx, path = job
    src = Image.open(path).convert("RGB")
    SW, SH = src.size
    MW, MH = MASTER_W, round(MASTER_W * SH / SW)

    src_lin = srgb_to_linear(np.asarray(src, np.float32) / 255.0)

    cur = resize_f(src_lin, MW, MH)
    cur = sharpen(cur, 0.26, 0.9)

    # iterative back-projection: the master is right when it downsamples back
    # onto the true 1280 frame.
    for _ in range(IBP_ITERS):
        err = src_lin - resize_f(cur, SW, SH)
        cur = np.clip(cur + resize_f(err, MW, MH) * 0.62, 0.0, None)

    cur = sharpen(cur, 0.32, 1.1)

    srgb = linear_to_srgb(cur)
    rng = np.random.default_rng(idx)                      # deterministic per frame
    srgb += rng.normal(0.0, 0.7 / 255.0, srgb.shape).astype(np.float32)
    master = Image.fromarray(np.clip(srgb * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")

    total = 0
    for w, q in TIERS:
        h = round(w * SH / SW)
        im = master if w == MW else master.resize((w, h), Image.LANCZOS)
        p = os.path.join(OUT_DIR, str(w), f"{idx:03d}.webp")
        im.save(p, "WEBP", quality=q, method=6)
        total += os.path.getsize(p)
    return idx, total


def main():
    frames = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(".png"))
    if not frames:
        sys.exit("no frames found")
    for w, _ in TIERS:
        os.makedirs(os.path.join(OUT_DIR, str(w)), exist_ok=True)

    jobs = [(i + 1, os.path.join(SRC_DIR, f)) for i, f in enumerate(frames)]
    t0 = time.time()
    done = 0
    per_tier = {w: 0 for w, _ in TIERS}

    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 4) - 2)) as ex:
        for idx, total in ex.map(build_frame, jobs):
            done += 1
            if done % 10 == 0 or done == len(jobs):
                print(f"[{time.time()-t0:6.1f}s] {done}/{len(jobs)} frames", flush=True)

    print(f"\n{len(jobs)} frames -> {OUT_DIR}")
    for w, q in TIERS:
        d = os.path.join(OUT_DIR, str(w))
        b = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d))
        print(f"  {w:>5}px  q{q}  {b/1e6:6.1f} MB  ({b/len(jobs)/1024:5.1f} KB/frame)")


if __name__ == "__main__":
    main()
