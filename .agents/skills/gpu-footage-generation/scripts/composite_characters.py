#!/usr/bin/env python3
"""Cut stylized characters out of a converted source frame and place them on a separately generated environment plate.

usage: composite_characters.py --characters conv.png --plate plate.png --out comp.png [--mask-out mask.png]
       [--mask-from source.png] [--regen-mask-out regen.png] [--grow 10 | -6] [--model birefnet-general] [--feather 2] [--match 0.35]
--mask-from segments the original photo (crisper outlines than a stylized frame; same geometry after low-denoise conversion).
--regen-mask-out writes the inverse (white = environment to regenerate) with the characters grown by --grow px and protected.
Both images are resized to the plate size; character placement follows the source framing exactly.
--match blends the character layer's mean colour toward the plate (0 = none) so a later low-denoise pass has less to fix.
Run with the tools venv (rembg, pillow, numpy).
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove

ap = argparse.ArgumentParser()
ap.add_argument("--characters", required=True); ap.add_argument("--plate", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--mask-out"); ap.add_argument("--model", default="birefnet-general")
ap.add_argument("--mask-from"); ap.add_argument("--regen-mask-out"); ap.add_argument("--grow", type=int, default=10)
ap.add_argument("--erode", type=int, default=0, help="shrink the cut-out by N px before compositing (drops background fringe)")
ap.add_argument("--char-mask-out", help="white = characters grown by --grow (for masked restyling of the characters only)")
ap.add_argument("--feather", type=float, default=2.0); ap.add_argument("--match", type=float, default=0.35)
a = ap.parse_args()

plate = Image.open(a.plate).convert("RGB")
def fit(im, size):
    """scale-to-cover then centre-crop: never stretch people to a different aspect ratio"""
    from PIL import ImageOps
    return ImageOps.fit(im, size, Image.LANCZOS)


chars = fit(Image.open(a.characters).convert("RGB"), plate.size)
seg_src = fit(Image.open(a.mask_from).convert("RGB"), plate.size) if a.mask_from else chars
cut = remove(seg_src, session=new_session(a.model))
hard = cut.split()[-1]
if a.erode > 0:
    hard = hard.filter(ImageFilter.MinFilter(2 * a.erode + 1))
alpha = hard.filter(ImageFilter.GaussianBlur(a.feather))
if a.char_mask_out:
    k = 2 * (abs(a.grow) // 2) + 1
    hard.point(lambda v: 255 if v > 64 else 0).filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.GaussianBlur(a.feather * 2)).save(a.char_mask_out)
if a.regen_mask_out:
    core = hard.point(lambda v: 255 if v > 64 else 0)
    k = 2 * (abs(a.grow) // 2) + 1
    # positive grow protects a margin around the characters; negative shrinks it so the edge band is repainted (removes halos)
    grown = core.filter(ImageFilter.MaxFilter(k) if a.grow >= 0 else ImageFilter.MinFilter(k))
    Image.eval(grown.filter(ImageFilter.GaussianBlur(a.feather * 2)), lambda v: 255 - v).save(a.regen_mask_out)
if a.mask_out:
    alpha.save(a.mask_out)
c = np.asarray(chars).astype(np.float32); p = np.asarray(plate).astype(np.float32)
m = np.asarray(alpha).astype(np.float32)[..., None] / 255.0
if a.match > 0 and m.sum() > 0:
    cm = (c * m).sum((0, 1)) / m.sum(); pm = p.mean((0, 1))
    c = c + a.match * (pm - cm)
out = c * m + p * (1 - m)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.out)
print({"out": a.out, "coverage": round(float(m.mean()), 3)})
