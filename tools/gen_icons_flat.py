"""Draws the HUD icon set into ui/icons2/ (96x96 PNG + .spr each): resources, status, toast and time-control glyphs. Everything is vector shapes
rasterised here with numpy (supersampled distance fields); no source art.
Run (from the project root) with any Python that has numpy, e.g. Blender's:  "C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" tools/gen_icons_flat.py
tools/gen_hud.py refers to the icons by name (cut_<name> for the top bar and resource table, plain <name> for the cost lines, alert_* and t_* elsewhere)."""
import struct, zlib
from pathlib import Path
import numpy as np

OUT = Path('ui/icons2'); OUT.mkdir(exist_ok=True)
N, SS = 96, 3
GRID = 24.0   # logical units: icons are drawn on a 24 x 24 grid

def hexc(h): h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
LIGHT, MUTED = hexc('#d6e0ea'), hexc('#8b97a3')
ORANGE, AMBER, RED, GREEN, BLUE, TEAL, PURPLE, LEAF, FLAME = hexc('#e8952a'), hexc('#ffb02e'), hexc('#ff6a6a'), hexc('#6fe3a0'), hexc('#4cc2ff'), hexc('#5ed1c4'), hexc('#b79cff'), hexc('#6fd08a'), hexc('#ff7a45')

def write_png(path, rgba):
    h, w, _ = rgba.shape
    raw = b''.join(b'\x00' + rgba[y].tobytes() for y in range(h))
    def chunk(t, d): c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

class Canvas:
    def __init__(self):
        M = N * SS
        ys, xs = np.mgrid[0:M, 0:M]
        self.px = (xs + 0.5) / M * GRID
        self.py = (ys + 0.5) / M * GRID
        self.col = np.zeros((M, M, 4), np.float32)   # premultiplied
    def paint(self, mask, color, alpha=1.0):
        src = np.array([color[0] / 255 * alpha, color[1] / 255 * alpha, color[2] / 255 * alpha, alpha], np.float32)
        m = mask.astype(np.float32)[..., None]
        self.col = src * m + self.col * (1 - alpha * m)
    # shapes (grid units)
    def seg_dist(self, x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0; l2 = dx * dx + dy * dy
        t = np.clip(((self.px - x0) * dx + (self.py - y0) * dy) / l2, 0, 1) if l2 > 0 else 0
        return np.hypot(self.px - (x0 + t * dx), self.py - (y0 + t * dy))
    def line(self, pts, w, color, alpha=1.0, closed=False):
        d = None
        n = len(pts)
        for i in range(n if closed else n - 1):
            s = self.seg_dist(*pts[i], *pts[(i + 1) % n])
            d = s if d is None else np.minimum(d, s)
        self.paint(d <= w / 2, color, alpha)
    def ring(self, cx, cy, r, w, color, alpha=1.0):
        self.paint(np.abs(np.hypot(self.px - cx, self.py - cy) - r) <= w / 2, color, alpha)
    def disc(self, cx, cy, r, color, alpha=1.0):
        self.paint(np.hypot(self.px - cx, self.py - cy) <= r, color, alpha)
    def poly(self, pts, color, alpha=1.0):
        inside = np.zeros(self.px.shape, bool)
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
            cond = (y0 > self.py) != (y1 > self.py)
            xi = (x1 - x0) * (self.py - y0) / (y1 - y0 + 1e-12) + x0
            inside ^= cond & (self.px < xi)
        self.paint(inside, color, alpha)
    def rect(self, x, y, w, h, color, alpha=1.0):
        self.paint((self.px >= x) & (self.px <= x + w) & (self.py >= y) & (self.py <= y + h), color, alpha)
    def rrect(self, x, y, w, h, r, sw, color, alpha=1.0):
        cx, cy = x + w / 2, y + h / 2
        qx = np.abs(self.px - cx) - (w / 2 - r); qy = np.abs(self.py - cy) - (h / 2 - r)
        sdf = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
        self.paint((sdf <= 0) & (sdf > -sw), color, alpha)
    def image(self):
        M = N * SS
        col = self.col.reshape(N, SS, N, SS, 4).mean(axis=(1, 3))
        a = col[..., 3:4]
        rgb = np.where(a > 1e-6, col[..., :3] / np.maximum(a, 1e-6), 0.0)
        return np.concatenate([np.clip(rgb * 255 + 0.5, 0, 255), np.clip(a * 255 + 0.5, 0, 255)], axis=2).astype(np.uint8)

def bez(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p = (1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1) + 3 * (1 - t) * t ** 2 * np.array(p2) + t ** 3 * np.array(p3)
    return [tuple(q) for q in p]

def arc(cx, cy, rx, ry, a0, a1, n=32):
    a = np.radians(np.linspace(a0, a1, n))
    return [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in a]

# ---- glyphs --------------------------------------------------------------------------------------------------------------------------------

def steel(c, col=LIGHT):
    # one bold ingot (reads at small sizes): lit top, mid front
    c.poly([(2.5, 19.5), (21.5, 19.5), (18.2, 11.5), (5.8, 11.5)], (170, 185, 202))
    c.poly([(5.8, 11.5), (18.2, 11.5), (16.2, 5.5), (7.8, 5.5)], (234, 241, 248))
    c.line([(6.5, 16), (17.5, 16)], 1.3, (120, 135, 152))

def polymers(c, col=TEAL):
    hexa = [(12 + 6 * np.cos(np.radians(60 * k - 90)), 12 + 6 * np.sin(np.radians(60 * k - 90))) for k in range(6)]
    c.line(hexa, 1.9, col, closed=True)
    for k in (0, 2, 4): c.disc(hexa[k][0], hexa[k][1], 2.1, col)

def electronics(c, col=PURPLE):
    c.rrect(7, 7, 10, 10, 1.6, 1.9, col)
    c.rect(10, 10, 4, 4, col)
    for k in (9.5, 12, 14.5):
        c.line([(k, 3.6), (k, 7)], 1.5, col); c.line([(k, 17), (k, 20.4)], 1.5, col)
        c.line([(3.6, k), (7, k)], 1.5, col); c.line([(17, k), (20.4, k)], 1.5, col)

def parts(c, col=LIGHT):
    for k in range(8):
        a = np.radians(45 * k)
        c.line([(12 + 5 * np.cos(a), 12 + 5 * np.sin(a)), (12 + 8.4 * np.cos(a), 12 + 8.4 * np.sin(a))], 2.8, col)
    c.ring(12, 12, 5.4, 2.4, col)
    c.disc(12, 12, 1.7, col)

def food(c, col=LEAF, vein=(8, 14, 20)):
    c.poly(bez((5, 19), (3.5, 8), (12, 3.5), (19.5, 4.5)) + bez((19.5, 4.5), (20.5, 12), (12, 20.5), (5, 19)), col)
    c.line([(4.5, 19.5), (14, 10)], 1.5, vein)

def oxygen(c, col=BLUE):
    # "O2": a big O and a small subscript 2
    c.ring(9.2, 11.6, 6.6, 2.4, col)
    c.line(arc(18.2, 15.4, 2.1, 2.1, 180, 400, 20) + [(16.1, 21.4), (20.6, 21.4)], 1.7, col)

def water(c, col=BLUE):
    pts = bez((12, 2.8), (14.6, 6.8), (19, 10.5), (19, 15)) + arc(12, 15, 7, 7, 0, 180) + bez((5, 15), (5, 10.5), (9.4, 6.8), (12, 2.8))
    c.poly(pts, col)
    c.line(arc(12, 15, 4.2, 4.2, 20, 80, 12), 1.3, (255, 255, 255), 0.55)

def co2(c, col=LIGHT):
    # "CO2" like the O2 glyph: C, O and a subscript 2
    c.line(arc(5.4, 11.2, 4.4, 4.4, 55, 305, 24), 2.2, col)
    c.ring(15, 11.2, 4.4, 2.2, col)
    c.line(arc(20.8, 16.0, 1.9, 1.9, 180, 400, 20) + [(18.8, 21.4), (22.8, 21.4)], 1.5, col)

def power(c, col=AMBER):
    c.poly([(13.6, 2.4), (5.8, 13.4), (11, 13.4), (9.6, 21.6), (18.2, 10), (12.6, 10)], col)

def altitude(c, col=LIGHT):
    c.line(arc(12, 33, 15.5, 15.5, 235, 305, 24), 1.9, col)
    c.line([(12, 19), (12, 5.2)], 2.1, ORANGE)
    c.line([(7.3, 9.8), (12, 5.2), (16.7, 9.8)], 2.1, ORANGE)

def crew(c, col=LIGHT):
    c.ring(12, 8, 3.5, 2.1, col)
    c.line(arc(12, 21, 7.6, 7.6, 180, 360, 24), 2.1, col)

def research(c, col=LIGHT, liquid=PURPLE):
    c.poly([(7.4, 14), (16.6, 14), (19.3, 19.2), (18.4, 20.6), (5.6, 20.6), (4.7, 19.2)], liquid, 0.9)
    c.line([(9.5, 3.2), (9.5, 9), (4.6, 19), (5.6, 21), (18.4, 21), (19.4, 19), (14.5, 9), (14.5, 3.2)], 1.8, col, closed=True)
    c.line([(8, 3.2), (16, 3.2)], 2.0, col)

def fuel(c, col=FLAME):
    c.poly([(12, 2.4), (17.6, 9), (19, 14), (16.6, 19.6), (12, 21.6), (7.4, 19.6), (5, 14), (7.2, 9.4), (9.6, 11.6), (10, 6.4)], col)
    c.poly([(12, 13), (15.2, 17), (12, 20.2), (8.8, 17)], (255, 214, 140))

def mixed(c, col=LIGHT):
    c.rrect(4, 6, 16, 13, 1.8, 1.9, col)
    c.line([(4, 12.5), (20, 12.5)], 1.7, col)
    c.line([(12, 6), (12, 19)], 1.7, col)

def heat(c, col=LIGHT):
    c.rrect(9.4, 2.8, 5.2, 13.2, 2.6, 1.9, col)
    c.ring(12, 17.6, 4.1, 1.9, col)
    c.line([(12, 9.5), (12, 17.6)], 2.2, RED)
    c.disc(12, 17.6, 2.5, RED)

def battery(c, col=LIGHT):
    c.rrect(3.5, 7.6, 15.5, 9, 1.8, 1.9, col)
    c.line([(20.6, 10.8), (20.6, 13.4)], 2.0, col)
    c.rect(6, 10, 3, 4.2, AMBER); c.rect(10.5, 10, 3, 4.2, AMBER)

def wrench(c, col=AMBER):
    c.line([(5.6, 18.4), (13.4, 10.6)], 3.2, col)
    c.ring(16.6, 7.4, 3.4, 2.4, col)
    c.line([(16.6, 3.2), (16.6, 6.4)], 3.0, (0, 0, 0), 0.0)

def ok(c, col=GREEN):
    c.ring(12, 12, 8.6, 2.0, col)
    c.line([(7.6, 12.6), (10.8, 15.8), (16.8, 8.8)], 2.2, col)

def pause(c, col=LIGHT):
    c.rect(6, 5, 4, 14, col); c.rect(14, 5, 4, 14, col)

def play(c, col=LIGHT):
    c.poly([(7, 5), (19.5, 12), (7, 19)], col)

def ff(c, col=LIGHT):
    c.poly([(3.5, 6), (12, 12), (3.5, 18)], col); c.poly([(12, 6), (20.5, 12), (12, 18)], col)

def fff(c, col=LIGHT):
    for x in (2.5, 9, 15.5): c.poly([(x, 6.5), (x + 6.5, 12), (x, 17.5)], col)

# ---- rack and attachment thumbnails ---------------------------------------------------------------------------------------------------------

def bed(c, col=LIGHT):
    c.rect(3.5, 15, 17, 2.4, col); c.rect(3.5, 7, 2.2, 13, col); c.rect(18.3, 12, 2.2, 8, col)
    c.rrect(7, 10.4, 6, 3.6, 1.6, 1.8, BLUE); c.rect(13.5, 12.2, 5, 2.4, col, 0.55)

def snowflake(c, col=BLUE):
    for k in range(3):
        a = np.radians(60 * k + 90)
        dx, dy = 8.6 * np.cos(a), 8.6 * np.sin(a)
        c.line([(12 - dx, 12 - dy), (12 + dx, 12 + dy)], 1.9, col)
        for s in (-1, 1):
            for e in (1, -1):
                bx, by = 12 + e * 5.2 * np.cos(a), 12 + e * 5.2 * np.sin(a)
                b = a + s * np.radians(50)
                c.line([(bx, by), (bx + e * 2.6 * np.cos(b), by + e * 2.6 * np.sin(b))], 1.5, col)

def cross(c, col=GREEN):
    c.rrect(3.5, 3.5, 17, 17, 3, 1.9, LIGHT, 0.55)
    c.rect(10.3, 6, 3.4, 12, col); c.rect(6, 10.3, 12, 3.4, col)

def dumbbell(c, col=LIGHT):
    c.line([(7, 12), (17, 12)], 2.2, col)
    for x in (4.6, 19.4): c.line([(x, 7), (x, 17)], 3.2, ORANGE)
    for x in (7.2, 16.8): c.line([(x, 8.4), (x, 15.6)], 3.0, col)

def recycle(c, col=TEAL):
    for a0 in (200, 320, 80):
        pts = arc(12, 12, 7, 7, a0, a0 + 80, 16)
        c.line(pts, 2.3, col)
        (x, y), (x2, y2) = pts[-1], pts[-2]
        d = np.arctan2(y - y2, x - x2)
        c.poly([(x + 3 * np.cos(d), y + 3 * np.sin(d)), (x + 2.2 * np.cos(d + 2.2), y + 2.2 * np.sin(d + 2.2)), (x + 2.2 * np.cos(d - 2.2), y + 2.2 * np.sin(d - 2.2))], col)

def solar(c, col=BLUE):
    c.poly([(5.5, 6), (20, 6), (18.5, 17), (4, 17)], col, 0.28)
    c.line([(5.5, 6), (20, 6), (18.5, 17), (4, 17)], 1.8, col, closed=True)
    for t in (1 / 3, 2 / 3):
        c.line([(5.5 - 1.5 * t + 14.5 * 0 + 0, 6 + 11 * t), (20 - 1.5 * t, 6 + 11 * t)], 1.3, col)
        c.line([(5.5 + 14.5 * t, 6), (4 + 14.5 * t, 17)], 1.3, col)
    c.line([(11.5, 17), (11.5, 21)], 1.9, LIGHT); c.line([(8, 21), (15, 21)], 1.9, LIGHT)

def vent(c, col=LIGHT):
    c.rrect(4, 5, 16, 14, 2, 1.9, col)
    for y in (8.5, 12, 15.5): c.line([(7, y), (17, y)], 1.7, ORANGE)

def tank(c, col=FLAME):
    c.rrect(3.5, 7, 17, 10, 4.6, 1.9, LIGHT)
    c.rect(8.4, 7.9, 1.4, 8.2, col); c.rect(14.2, 7.9, 1.4, 8.2, col)
    c.line([(20.5, 12), (22.2, 12)], 2.0, LIGHT)

def lamp(c, col=AMBER):
    c.disc(12, 10, 5.4, col, 0.35); c.ring(12, 10, 5.4, 1.9, col)
    c.rect(9.6, 16, 4.8, 2.4, LIGHT); c.rect(10.4, 19, 3.2, 1.6, LIGHT)
    for a in (-60, -30, 0, 30, 60):
        t = np.radians(a - 90)
        c.line([(12 + 7.8 * np.cos(t), 10 + 7.8 * np.sin(t)), (12 + 9.8 * np.cos(t), 10 + 9.8 * np.sin(t))], 1.3, col)

def antenna(c, col=LIGHT):
    c.line([(12, 9), (12, 21)], 2.0, col); c.line([(8, 21), (16, 21)], 2.0, col)
    c.disc(12, 8, 1.8, ORANGE)
    for r in (4.5, 7.5):
        c.line(arc(12, 8, r, r, -150, -30, 12), 1.6, ORANGE)
        c.line(arc(12, 8, r, r, 30, 150, 12), 1.6, ORANGE, 0.0)

def dish(c, col=LIGHT):
    c.line(arc(11, 8, 8, 8, 20, 160, 20), 2.2, col)
    c.line([(11, 12), (11, 21)], 2.0, col); c.line([(7.5, 21), (14.5, 21)], 2.0, col)
    c.line([(11, 8), (17.5, 3.5)], 1.6, ORANGE); c.disc(17.8, 3.3, 1.5, ORANGE)

def radar(c, col=GREEN):
    c.ring(12, 12, 8.6, 1.8, col, 0.8); c.ring(12, 12, 4.6, 1.5, col, 0.5)
    c.poly([(12, 12), (12 + 8.6 * np.cos(np.radians(-80)), 12 + 8.6 * np.sin(np.radians(-80))), (12 + 8.6 * np.cos(np.radians(-20)), 12 + 8.6 * np.sin(np.radians(-20)))], col, 0.35)
    c.disc(12, 12, 1.4, col); c.disc(16.4, 15.5, 1.2, ORANGE)

def leaf_sun(c, col=LEAF):
    food(c, col, (8, 14, 20)); c.ring(18.5, 5, 2.2, 1.6, AMBER)

# thumbnails of the racks (scripts/config.evox RackKind order) and the attachments (AttachKind order): rack_<n> / att_<n>
RACKS = [bed, oxygen, co2, food, leaf_sun, mixed, snowflake, battery, research, parts, cross, dumbbell, recycle, fuel]
def rtg(c, col=AMBER):
    c.rrect(5, 8, 14, 9, 2, 1.9, LIGHT)
    for k in range(3):
        a = np.radians(90 + 120 * k)
        c.poly([(12.5, 12.5), (12.5 + 3.6 * np.cos(a - 0.5), 12.5 - 3.6 * np.sin(a - 0.5)), (12.5 + 3.6 * np.cos(a + 0.5), 12.5 - 3.6 * np.sin(a + 0.5))], col)
    c.disc(12.5, 12.5, 1.0, LIGHT)
    c.line([(12, 17), (12, 21)], 1.9, LIGHT); c.line([(8, 21), (16, 21)], 1.9, LIGHT)

ATTACHMENTS = [solar, vent, mixed, lambda c: tank(c, FLAME), lambda c: tank(c, BLUE), co2, lamp, antenna, dish, radar, rtg]

# name -> glyph; the resource icons exist as cut_<name> (spr) and <name> (png used directly in the cost lines)
GLYPHS = {
    'steel': steel, 'polymers': polymers, 'electronics': electronics, 'parts': parts, 'food': food, 'oxygen': oxygen, 'water': water, 'co2': co2,
    'power': power, 'altitude': altitude, 'crew': crew, 'research': research, 'fuel': fuel, 'mixed': mixed, 'heat': heat, 'battery': battery,
}
OTHER = {
    'alert_low_oxygen': lambda c: oxygen(c, RED), 'alert_low_food': lambda c: food(c, AMBER, (30, 20, 8)), 'alert_no_power': lambda c: power(c, RED),
    'alert_repair': wrench, 'alert_crew': lambda c: crew(c, LIGHT), 'alert_ok': ok, 't_pause': pause, 't_play': play, 't_ff': ff, 't_fff': fff,
}

def save(name, glyph):
    c = Canvas(); glyph(c)
    write_png(OUT / (name + '.png'), c.image())
    (OUT / (name + '.png.meta')).write_text('srgb = true\ncompress = false\nmips = false\n')
    (OUT / (name + '.spr')).write_text('type = simple\ntop = 0\nbottom = 0\nleft = 0\nright = 0\ntexture = "ui/icons2/%s.png"\n' % name)

for name, g in GLYPHS.items():
    save(name, g); save('cut_' + name, g)
for name, g in OTHER.items(): save(name, g)
for i, g in enumerate(RACKS): save("rack_%d" % (i + 1), g)
for i, g in enumerate(ATTACHMENTS): save("att_%d" % (i + 1), g)
# a contact sheet to look at
sheet = np.zeros((N * 5, N * 13, 4), np.uint8); sheet[..., :3] = 12; sheet[..., 3] = 255
names = list(GLYPHS) + list(OTHER)
extra = [("rack_%d" % (i + 1), g) for i, g in enumerate(RACKS)] + [("att_%d" % (i + 1), g) for i, g in enumerate(ATTACHMENTS)]
allg = [(n, GLYPHS.get(n) or OTHER[n]) for n in names] + extra
for i, (name, g) in enumerate(allg):
    c = Canvas(); g(c); im = c.image().astype(np.float32); a = im[..., 3:4] / 255
    r, col = divmod(i, 13)
    tile = sheet[r * N:(r + 1) * N, col * N:(col + 1) * N]
    tile[..., :3] = (im[..., :3] * a + tile[..., :3] * (1 - a)).astype(np.uint8)
write_png(OUT / '_sheet.png', sheet)
print("icons written to", OUT, len(allg), "glyphs")
