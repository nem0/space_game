"""Draws the flat HUD skin into ui/flat/: dark glass panels with a thin light border, rounded buttons, cards, navigation plates, tabs, toasts and
tech-tree nodes, each a small nine-slice sprite (.spr patch9 + .png). Everything is computed here (no source art).
Run (from the project root) with any Python that has numpy, e.g. Blender's:  "C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" tools/gen_flat.py
tools/gen_hud.py refers to these sprites by name."""
import struct, zlib
from pathlib import Path
import numpy as np

OUT = Path('ui/flat'); OUT.mkdir(exist_ok=True)
SS = 4   # supersampling

def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

WHITE = (255, 255, 255)
ORANGE = hexc('#e8952a')
RED, AMBER, BLUE, GREEN = hexc('#e5484d'), hexc('#e8952a'), hexc('#3a9ad9'), hexc('#3fbf7f')

def write_png(path, rgba):
    h, w, _ = rgba.shape
    raw = b''.join(b'\x00' + rgba[y].tobytes() for y in range(h))
    def chunk(t, d): c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

def sprite(name, size, r, fill, border, bw=1.0, bar=None, bar_w=0, fill2=None, inner=None):
    """fill / border / bar: (r, g, b, alpha 0..1); fill2 = colour at the bottom (vertical gradient); inner = (rgba, width) second line inside the border"""
    W = H = size
    ys, xs = np.mgrid[0:H * SS, 0:W * SS]
    px = (xs + 0.5) / SS; py = (ys + 0.5) / SS
    cx = cy = size / 2.0
    qx = np.abs(px - cx) - (cx - r); qy = np.abs(py - cy) - (cy - r)
    sdf = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    inside = sdf <= 0
    col = np.zeros((H * SS, W * SS, 4), np.float32)   # premultiplied
    def paint(mask, rgba, t=None):
        a = rgba[3]
        c = np.array(rgba[:3], np.float32) / 255.0
        if t is not None:   # gradient factor array
            c = c[None, None, :]
        alpha = np.where(mask, a, 0.0)
        col[..., :3] = np.where(mask[..., None], c * a if t is None else c * a, col[..., :3])
        col[..., 3] = np.where(mask, alpha, col[..., 3])
    if fill2 is None:
        paint(inside, fill)
    else:
        t = (py / H)[..., None]
        c1 = np.array(fill[:3], np.float32) / 255.0; c2 = np.array(fill2[:3], np.float32) / 255.0
        a = (fill[3] * (1 - t) + fill2[3] * t)
        c = c1 * (1 - t) + c2 * t
        col[..., :3] = np.where(inside[..., None], c * a, 0.0)
        col[..., 3] = np.where(inside, a[..., 0], 0.0)
    if bar is not None and bar_w > 0:
        paint(inside & (px < bar_w), bar)
    if inner is not None:
        irgba, iw = inner
        paint(inside & (sdf > -bw - iw) & (sdf <= -bw), irgba)
    paint(inside & (sdf > -bw), border)
    # downsample the premultiplied colour
    col = col.reshape(H, SS, W, SS, 4).mean(axis=(1, 3))
    a = col[..., 3:4]
    rgb = np.where(a > 1e-6, col[..., :3] / np.maximum(a, 1e-6), 0.0)
    out = np.concatenate([np.clip(rgb * 255 + 0.5, 0, 255), np.clip(a * 255 + 0.5, 0, 255)], axis=2).astype(np.uint8)
    write_png(OUT / (name + '.png'), out)
    (OUT / (name + '.png.meta')).write_text('srgb = true\ncompress = false\nmips = false\n')
    m = int(np.ceil(r + bw)) + 2
    (OUT / (name + '.spr')).write_text('type = patch9\ntop = %d\nbottom = %d\nleft = %d\nright = %d\ntexture = "ui/flat/%s.png"\n' % (m, size - m, m, size - m, name))

LINE = hexc('#ffffff', 0.14)
GLASS = hexc('#03060a', 0.97)
GLASS2 = hexc('#05090e', 0.97)

sprite('panel', 40, 7, GLASS, LINE, fill2=GLASS2, inner=(hexc('#ffffff', 0.04), 1.0))
sprite('panel_flat', 40, 5, hexc('#020406', 0.96), hexc('#ffffff', 0.10))
sprite('btn', 32, 5, hexc('#ffffff', 0.06), hexc('#ffffff', 0.22))
sprite('btn_h', 32, 5, hexc('#e8952a', 0.22), hexc('#e8952a', 0.95))
sprite('btn_on', 32, 5, hexc('#e8952a', 0.34), hexc('#f0a548', 1.0))
sprite('card', 40, 6, hexc('#070c12', 0.97), hexc('#ffffff', 0.14), fill2=hexc('#05090e', 0.97))
sprite('card_h', 40, 6, hexc('#1c1710', 0.96), hexc('#e8952a', 0.95), fill2=hexc('#14100b', 0.96))
sprite('navb', 32, 6, hexc('#03060a', 0.94), hexc('#ffffff', 0.12))
sprite('navb_a', 32, 6, hexc('#e8952a', 0.20), hexc('#e8952a', 1.0), bar=hexc('#e8952a', 1.0), bar_w=3)
sprite('tab', 32, 5, hexc('#ffffff', 0.05), hexc('#ffffff', 0.14))
sprite('tab_a', 32, 5, hexc('#e8952a', 0.95), hexc('#f0a548', 1.0))
sprite('toast_red', 32, 6, hexc('#120a0c', 0.94), hexc('#e5484d', 0.55), bar=RED, bar_w=3.5)
sprite('toast_amber', 32, 6, hexc('#120e08', 0.94), hexc('#e8952a', 0.55), bar=AMBER, bar_w=3.5)
sprite('toast_blue', 32, 6, hexc('#080e14', 0.94), hexc('#3a9ad9', 0.55), bar=BLUE, bar_w=3.5)
sprite('toast_green', 32, 6, hexc('#08120d', 0.94), hexc('#3fbf7f', 0.55), bar=GREEN, bar_w=3.5)
sprite('toast_dark', 32, 6, hexc('#080c12', 0.90), hexc('#ffffff', 0.12), bar=hexc('#ffffff', 0.25), bar_w=3.5)
sprite('node_l', 32, 5, hexc('#06090d', 0.90), hexc('#ffffff', 0.08))
sprite('node_a', 32, 5, hexc('#0a1520', 0.94), hexc('#3a9ad9', 0.70))
sprite('node_x', 32, 5, hexc('#1c1409', 0.96), hexc('#e8952a', 1.0), inner=(hexc('#e8952a', 0.25), 1.0))
sprite('node_u', 32, 5, hexc('#08170f', 0.94), hexc('#3fbf7f', 0.70))
print('flat skin written to', OUT)

# ---- main menu sprites: horizontal gradients (simple sprites stretch to the box) ---------------------------------------------------------------
def hgradient(name, w, h, rgb, a0, a1, bar=None, hold=0.0, stop=1.0):
    x = np.linspace(0, 1, w)[None, :, None]
    t = np.clip((x - hold) / (stop - hold), 0.0, 1.0); a = a0 + (a1 - a0) * (t * t * (3 - 2 * t))
    img = np.zeros((h, w, 4), np.float32)
    img[..., :3] = np.array(rgb, np.float32)
    img[..., 3:4] = np.repeat(a, h, axis=0) * 255.0
    if bar is not None:
        img[:, :3, :3] = np.array(bar[:3], np.float32); img[:, :3, 3] = 255.0
    write_png(OUT / (name + '.png'), np.clip(img + 0.5, 0, 255).astype(np.uint8))
    (OUT / (name + '.png.meta')).write_text('srgb = true\ncompress = false\nmips = false\n')
    (OUT / (name + '.spr')).write_text('type = simple\ntop = 0\nbottom = 0\nleft = 0\nright = 0\ntexture = "ui/flat/%s.png"\n' % name)

hgradient("menu_grad", 256, 4, (2, 5, 10), 0.93, 0.0, hold=0.25, stop=0.62)
hgradient('menu_hover', 256, 4, (232, 149, 42), 0.30, 0.0, bar=(232, 149, 42))
print('menu sprites written')
hgradient('menu_none', 8, 4, (255, 255, 255), 0.05, 0.05)   # the resting look of a menu item (the hover image replaces it)
