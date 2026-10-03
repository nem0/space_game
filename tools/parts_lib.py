"""Shared code of the damaged parts kits (build_parts_trim.py, build_central_kit.py): everything maps onto the parts sheet (parts_sheet/, texgen/parts.evox).
Contents: geometry helpers (shell, rev, hbar, patch, faces ...), the hull hardware and
hull / end pieces of the cylindrical habitat kit, the small attachments, and build_kit() (AO bake + FBX export + parts_trim.mat).
Hull frame: half cylinders (top half, R = 1.0 m, L = 1.0 m) centred on X; attachments stand on Z = 0."""
import sys; sys.path.insert(0, 'C:/projects/space_game/tools')
import bpy, bmesh, math, json, time, random, importlib
import trim_lib as T; importlib.reload(T)
PSHEET = T.SHEET
from trim_lib import *
from mathutils import noise as mnoise
T0 = time.time(); V = Vector
R = 1.0; L = 1.0; MM = 8; NN = 30; PBX = 4; PBY = 5              # hull radius, segment length, cell grid, cells per sheet plate (0.5 x 0.52 m)
X = V((1, 0, 0))

def polar(x, th, r): return V((x, r*math.cos(th), r*math.sin(th)))
def nrm(th): return V((0, math.cos(th), math.sin(th)))
def tang(th): return V((0, -math.sin(th), math.cos(th)))
def frame(th): return rot(tang(th), X, nrm(th))                    # local x = around the hull, y = along the hull, z = out of the hull
def rad(deg): return math.radians(deg)

class Dmg:
    """analytic dents + soft buckling + peeled edges, evaluated on shell points so inner/outer surfaces and neighbours stay continuous"""
    def __init__(s, seed, dents=5, amt=.01, peel=()):
        r = random.Random(seed); s.amt = amt; s.peel = peel
        s.d = [(r.uniform(-.4, .4), r.uniform(.15*math.pi, .85*math.pi), r.uniform(.14, .28), r.uniform(.02, .045)) for _ in range(dents)]
    def __call__(s, p):
        rd = V((0, p.y, p.z)).normalized(); q = V((p.x, rd.y*R, rd.z*R)); off = 0.0
        for cx, th, rr, dd in s.d:
            d = (q - polar(cx, th, R)).length
            if d < rr: off -= dd*(1 - d/rr)**2
        for c, rr, dd in s.peel:
            d = (q - c).length
            if d < rr: off += dd*(1 - d/rr)
        off += mnoise.noise(V((p.x*2.3, p.y*2.3 + 3, p.z*2.3)))*s.amt
        return p + rd*off

def sw_uv(b, name): return b.spec_uv(SW(name), 0, 0, 1)
ALL = ('+x', '-x', '+y', '-y', '+z', '-z')
def faces(region, **over):
    """box maps: every face shows `region`, keyword overrides like px='BOX_VENT' / mz='SW_DARK' replace single faces"""
    m = {k: FIT(region, 'x') for k in ALL}
    for k, v in over.items(): key = ('+' if k[0] == 'p' else '-') + k[1]; m[key] = SW(v) if v.startswith('SW_') else FIT(v, 'x')
    return m

def shell(b, Ro, Lr, x0, t, Mn, Nn, uv_out, skip=(), keep=None, ends=True, dmg=None, inner='SW_DARK', rim='SW_STEEL'):
    """half-cylinder shell (top half, axis X), outer faces mapped by uv_out(i, j) -> 4 uvs, inner/rim faces flat swatches"""
    Ri = Ro - t
    def P(i, j, r):
        p = polar(x0 + Lr*i/Mn, math.pi*j/Nn, r); return dmg(p) if dmg else p
    def on(i, j):
        if not (0 <= i < Mn and 0 <= j < Nn): return None
        return (keep is None or (i, j) in keep) and (i, j) not in skip
    su = sw_uv(b, inner); sr = sw_uv(b, rim)
    for i in range(Mn):
        for j in range(Nn):
            if not on(i, j): continue
            thm = math.pi*(j + .5)/Nn
            b.face([P(i, j, Ro), P(i+1, j, Ro), P(i+1, j+1, Ro), P(i, j+1, Ro)], uv_out(i, j), nrm(thm))
            b.face([P(i, j, Ri), P(i+1, j, Ri), P(i+1, j+1, Ri), P(i, j+1, Ri)], [su]*4, -nrm(thm))
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ni, nj = i + di, j + dj; inr = (0 <= ni < Mn and 0 <= nj < Nn)
                if (inr and not on(ni, nj)) or (not inr and ends):
                    if di:
                        e = i if di < 0 else i + 1; b.face([P(e, j, Ro), P(e, j+1, Ro), P(e, j+1, Ri), P(e, j, Ri)], [sr]*4, V((di, 0, 0)))
                    else:
                        e = j if dj < 0 else j + 1; b.face([P(i, e, Ro), P(i+1, e, Ro), P(i+1, e, Ri), P(i, e, Ri)], [sr]*4, tang(math.pi*e/Nn)*dj)

def paint_uv(b, name, seed, mix=None):
    """cells -> sheet plates: one random plate of the HULL_* region per 4 x 5 cells; mix = (other region, probability) swaps in odd plates"""
    rng = random.Random(seed); blocks = {}
    def f(i, j):
        bi, bj = i//PBX, j//PBY; a0, a1 = (i % PBX)/PBX, (i % PBX + 1)/PBX; c0, c1 = (j % PBY)/PBY, (j % PBY + 1)/PBY
        if (bi, bj) not in blocks:
            reg = mix[0] if mix and rng.random() < mix[1] else name; x, y, w, h = T.RECTS[reg]
            blocks[(bi, bj)] = (reg, w//256, h//256, rng.randrange(w//256), rng.randrange(h//256))
        reg, nx, ny, pi, pj = blocks[(bi, bj)]; u0, v0, u1, v1 = rect(reg)
        q = lambda fa, fb: (u0 + (pi + fa)/nx*(u1 - u0), v0 + (pj + fb)/ny*(v1 - v0))
        return [q(a0, c0), q(a1, c0), q(a1, c1), q(a0, c1)]
    return f
def strip_uv(b, name, ulen):
    b._us = b.rng.uniform(0, .2)
    return lambda i, j: [b.spec_uv(STRIP(name, 'x'), (j + db)/NN, i + da, ulen) for da, db in ((0, 0), (1, 0), (1, 1), (0, 1))]
def fit_uv(b, name, i0, j0, ni, nj):
    return lambda i, j: [b.spec_uv(FIT(name, 'x'), (j - j0 + db)/nj, (i - i0 + da)/ni, 1) for da, db in ((0, 0), (1, 0), (1, 1), (0, 1))]
def flat_uv(b, name): u = sw_uv(b, name); return lambda i, j: [u]*4

def rev(b, prof, segs, c=(0, 0, 0), n=X, t1=None, arc=math.tau, a0=0.0):
    """revolve about axis n through c over `arc`, starting at t1: prof = [(r, h, region)], a point's region maps the band that ENDS at it.
    Walk the profile with the outside on the LEFT (outer walls run towards -n). Strips follow the circumference at sheet scale (U),
    V runs along the profile over all bands of the same region; SW_* regions are flat."""
    c = V(c); n = V(n).normalized(); t1 = (V(t1) if t1 is not None else n.orthogonal()).normalized(); t2 = n.cross(t1); tot = {}; run = {}
    for (r0, h0, _), (r1, h1, sp) in zip(prof[:-1], prof[1:]): tot[sp] = tot.get(sp, 0) + math.hypot(r1 - r0, h1 - h0)
    for (r0, h0, _), (r1, h1, sp) in zip(prof[:-1], prof[1:]):
        ln = math.hypot(r1 - r0, h1 - h0)
        if ln < 1e-6: continue
        u0, v0, u1, v1 = rect(sp); eps = 1.0/T.S; span = min(u1 - u0, arc*max(r0, r1)/4); us = u0 + b.rng.uniform(0, (u1 - u0) - span)
        s0 = run.get(sp, 0)/tot[sp]; run[sp] = run.get(sp, 0) + ln; s1 = run[sp]/tot[sp]
        va, vb = v0 + eps + s0*(v1 - v0 - 2*eps), v0 + eps + s1*(v1 - v0 - 2*eps)
        for k in range(segs):
            ta, tb = a0 + arc*k/segs, a0 + arc*(k + 1)/segs
            ea, eb = t1*math.cos(ta) + t2*math.sin(ta), t1*math.cos(tb) + t2*math.sin(tb)
            ua, ub = us + span*k/segs, us + span*(k + 1)/segs
            pts = [c + n*h0 + ea*r0, c + n*h0 + eb*r0, c + n*h1 + eb*r1, c + n*h1 + ea*r1]; uvs = [(ua, va), (ub, va), (ub, vb), (ua, vb)]
            if sp.startswith('SW_'): uvs = [sw_uv(b, sp)]*4
            if r0 < 1e-6: pts, uvs = pts[1:], uvs[1:]
            elif r1 < 1e-6: pts, uvs = pts[:3], uvs[:3]
            b.face(pts, uvs, (ea + eb).normalized()*(-(h1 - h0)) + n*(r1 - r0))
def hrev(b, prof): rev(b, prof, NN, n=X, t1=(0, 1, 0), arc=math.pi)                        # top half about the hull axis, h = x

def rivet(b, p, n, r=.022, h=.016, strip='SW_STEEL'):
    n = V(n).normalized(); t1 = n.orthogonal().normalized(); t2 = n.cross(t1)
    b.revolve(V(p), n, t1, t2, [(r, 0, strip), (r*.55, h, strip), (0, h, strip)], 5)
def cyl(b, c, r, d, axis, strip, segs=10):
    n = {'x': V((1, 0, 0)), 'y': V((0, 1, 0)), 'z': V((0, 0, 1))}[axis]; t1 = n.orthogonal().normalized(); t2 = n.cross(t1)
    b.revolve(V(c) - n*d/2, n, t1, t2, [(r, 0, strip), (r, d, strip), (0, d, strip)], segs)
def hbar(b, pts, r, strip, segs=6):
    """tube along a polyline with mitred joints. Strip regions run along the tube (U = length at sheet scale, V = around), SW_* are flat"""
    pts = [V(p) for p in pts]; n = len(pts); sw = strip.startswith('SW_'); u0, v0, u1, v1 = rect(strip); eps = 1.0/T.S
    total = sum((q - p).length for p, q in zip(pts[:-1], pts[1:])); us = u0 + b.rng.uniform(0, max(0.0, (u1 - u0) - total/4)); flat = sw_uv(b, strip) if sw else None
    t1 = (pts[1] - pts[0]).normalized().orthogonal().normalized(); rings = []; dist = 0.0
    for k in range(n):
        t = (pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)]).normalized(); t1 = (t1 - t*t1.dot(t)).normalized(); t2 = t.cross(t1)
        if k: dist += (pts[k] - pts[k - 1]).length
        rings.append(([pts[k] + (t1*math.cos(math.tau*i/segs) + t2*math.sin(math.tau*i/segs))*r for i in range(segs)], us + dist/4))
    for k in range(n - 1):
        (ra, ua), (rb, ub) = rings[k], rings[k + 1]; mid = (pts[k] + pts[k + 1])/2
        for i in range(segs):
            A, B, C, D = ra[i], ra[(i + 1) % segs], rb[(i + 1) % segs], rb[i]; va, vb = v0 + eps + (v1 - v0 - 2*eps)*i/segs, v0 + eps + (v1 - v0 - 2*eps)*(i + 1)/segs
            b.face([A, B, C, D], [flat]*4 if sw else [(ua, va), (ua, vb), (ub, vb), (ub, va)], (A + B + C + D)/4 - mid, smooth=True)
def onhull(b, x, th, r, size, maps, default=SW('SW_STEEL'), yaw=0.0):
    fr = frame(th) @ Matrix.Rotation(yaw, 3, 'Z')
    b.box(polar(x, th, r), size, fr, maps=maps, default=default)
def arc(b, x, d0, d1, r, tube, strip, steps=None):
    """tube around the hull at station x from d0 to d1 degrees"""
    steps = steps or max(3, int(abs(d1 - d0)/6)); hbar(b, [polar(x, rad(d0 + (d1 - d0)*k/steps), r) for k in range(steps + 1)], tube, strip, 5)

# ----------------------------------------------------------------------------------------------------------------- hull hardware
RIB_W = .04; RIB_X = (-(L/2 - .05), L/2 - .05)                     # rib centres sit 5 cm inside the segment ends, so a joint between two segments reads as a double ring
STN = (25, 41.5, 58, 74, 90, 106, 122, 138.5, 155)                                       # bracket stations around the hull (deg); rails run through 25/155 (steel) and 58/122 (yellow)
def ribs(b, xs=RIB_X):
    for x in xs: shell(b, R + .05, RIB_W, x - RIB_W/2, .07, 1, NN, strip_uv(b, 'RIB', math.pi*R), ends=True)
def brackets(b, xs=(-(L/2 - .035), L/2 - .035)):
    """bolted blocks straddling the ribs, flush with the segment end: two neighbours make one 14 cm clamp across the joint"""
    for x in xs:
        for deg in STN: onhull(b, x, rad(deg), R + .035, (.10, .07, .07), {'+z': FIT('BRACKET', 'x')})
def rails(b):
    for deg, strip in ((25, 'RAIL'), (155, 'RAIL'), (58, 'PIPE_YELLOW'), (122, 'PIPE_YELLOW')):
        th = rad(deg); hbar(b, [polar(-L/2, th, R + .085), polar(0, th, R + .085), polar(L/2, th, R + .085)], .013, strip, 6)
        onhull(b, 0, th, R + .035, (.035, .035, .08), {}, SW('SW_STEEL'))                        # mid-span standoff
def cables(b, runs=((113, .018, 1, 'CABLE_RED'), (116.5, .018, 1, 'CABLE_RED'), (31, .02, 2, 'CABLE_DARK'), (35, .015, 1, 'CABLE_RED'))):
    """cable runs along the hull: (station deg, wander rad, whole waves per segment, strip). Ends stay on their station so neighbours line up; cables hop over the ribs"""
    for deg, amp, k, strip in runs:
        pts = []
        for s in range(17):
            t = s/16; x = -L/2 + L*t; hop = max(0.0, 1 - abs(abs(x) - (L/2 - .05))/.06)
            pts.append(polar(x, rad(deg) + amp*math.sin(math.tau*k*t), R + .016 + .052*hop))
        hbar(b, pts, .011, strip, 5)
def porthole(b, th, x=0.0, lit=False):
    C = polar(x, th, R); n = nrm(th); et = tang(th); ring = lambda a, rr: C + n*.03 + (X*math.cos(a) + et*math.sin(a))*rr
    hbar(b, [ring(k*math.tau/24, .19) for k in range(25)], .032, 'SW_STEEL', 6)
    for k in range(8): rivet(b, ring(k*math.tau/8, .19) + n*.025, n, .016, .012, 'SW_BARE')
    t1 = X; t2 = n.cross(t1)
    G = 'SW_WINDOW' if lit else 'SW_GLASS'; b.revolve(C + n*.016, n, t1, t2, [(.17, 0, G), (0, 0, G)], 18)                # glass sits proud of the curved plates, inside the ring

def hull(kind='plain', paint='HULL_WHITE', seed=1, mix=None, loop=None, wrap=None, lit=False):
    """loop = station x of a yellow pipe ring, wrap = (x, from deg, to deg) red cable wrapped around the hull, lit = the porthole glows (someone is home)"""
    b = Builder(seed=seed); hole = set(); peel = (); PT = rad(140)                                # porthole / tear / grille zone between the 122 and 155 deg rails
    if kind == 'basic': hole = {(1, 22), (1, 23), (2, 23), (2, 22), (1, 24), (0, 23)}; peel = ((polar(-.31, rad(141), R), .2, .05),)
    if kind == 'window': hole = {(i, j) for i in (3, 4) for j in range(12, 18)}
    if kind == 'porthole':
        Cp = polar(.0, PT, R)                                                                  # opening behind the glass
        hole = {(i, j) for i in range(MM) for j in range(NN) if (polar(-L/2 + L*(i + .5)/MM, math.pi*(j + .5)/NN, R) - Cp).length < .10}
    dmg = Dmg(seed, 8 if kind != 'window' else 4, .012, peel)
    shell(b, R, L, -L/2, .05, MM, NN, paint_uv(b, paint, seed, mix), skip=hole, dmg=dmg)
    ribs(b); brackets(b); rails(b); cables(b)
    if loop is not None:
        arc(b, loop, 0, 180, R + .045, .013, 'PIPE_YELLOW')
        for deg in (12, 45, 75, 105, 135, 168): onhull(b, loop, rad(deg), R + .025, (.05, .04, .055), {}, SW('SW_STEEL'))
    if wrap is not None: arc(b, wrap[0], wrap[1], wrap[2], R + .04, .011, 'CABLE_RED'); arc(b, wrap[0] + .03, wrap[1] + 3, wrap[2], R + .038, .009, 'CABLE_DARK')
    if kind == 'porthole': porthole(b, PT, lit=lit)
    if kind == 'basic':
        for base, th, yaw, sz, sp in ((.22, 80, .2, (.30, .24), 'HAZARD'), (-.28, 48, -.3, (.22, .16), 'BOX')):
            t_ = rad(th); onhull(b, base, t_, R + .02, (sz[0], sz[1], .022), {'+z': FIT(sp, 'x')}, SW('SW_BARE'), yaw)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    fr = frame(t_) @ Matrix.Rotation(yaw, 3, 'Z'); p = polar(base, t_, R + .03) + fr @ V((sx*(sz[0]/2 - .025), sy*(sz[1]/2 - .025), 0))
                    rivet(b, p, nrm(t_), .012, .01)
    if kind == 'window':
        fr_cells = {(i, j) for i in range(2, 6) for j in range(11, 19)} - hole
        shell(b, R + .025, L, -L/2, .07, MM, NN, flat_uv(b, 'SW_WHITE'), keep=fr_cells, ends=False, rim='SW_WHITE')
        shell(b, R - .02, L, -L/2, .012, MM, NN, flat_uv(b, 'SW_GLASS'), keep=hole, ends=False, inner='SW_GLASS')
        for i in (2, 6):
            for k in range(11, 20, 2): th = math.pi*k/NN; rivet(b, polar(-L/2 + L*i/MM, th, R + .05), nrm(th), .014, .012)
    if kind == 'hatch':
        fr_cells = {(i, j) for i in range(1, 7) for j in range(12, 18)}; inner = {(i, j) for i in range(2, 6) for j in range(13, 17)}
        shell(b, R + .03, L, -L/2, .08, MM, NN, flat_uv(b, 'SW_WHITE'), keep=fr_cells - inner, ends=False, rim='SW_WHITE')
        shell(b, R + .045, L, -L/2, .05, MM, NN, fit_uv(b, 'HATCH', 2, 13, 4, 4), keep=inner, ends=False, rim='SW_WHITE')
        for i in (1, 7):
            for k in range(12, 19, 2): th = math.pi*k/NN; rivet(b, polar(-L/2 + L*i/MM, th, R + .07), nrm(th), .014, .012)
        for sx in (-1, 1): onhull(b, sx*.33, rad(90), R + .06, (.10, .05, .05), {'+z': FIT('BRACKET', 'x')})          # hinge / latch blocks
    if kind == 'grille':                                                                         # radiator grille standing off the hull
        onhull(b, 0, PT, R + .035, (.44, .62, .05), {'+z': FIT('GRILLE', 'y')}, SW('SW_WHITE'))
        for sx in (-1, 1):
            for sy in (-1, 1): fr = frame(PT); rivet(b, polar(0, PT, R + .06) + fr @ V((sx*.2, sy*.29, 0)), nrm(PT), .014, .012)
    return b

def hull_frame():
    b = Builder(seed=2)
    ribs(b); brackets(b); rails(b)
    for th in [rad(a) for a in (10, 40, 75, 105, 140, 170)]: onhull(b, 0, th, R + .02, (.06, L - .13, .04), {'+z': STRIP('BEAM', 'y')}, SW('SW_WHITE'))
    for k in range(4):
        a0, a1 = rad(20 + 40*k), rad(50 + 40*k)
        hbar(b, [polar(-L/2 + .08, a0, R + .02), polar(0, (a0 + a1)/2, R - .02), polar(L/2 - .08, a1, R + .02)], .014, 'PIPE_YELLOW', 5)
    shell(b, R, L, -L/2, .05, MM, NN, paint_uv(b, 'HULL_SCRAP', 2), keep={(i, j) for i in range(0, 4) for j in range(19, 27)}, dmg=Dmg(2, 3, .01))
    return b
def end_closed():
    b = Builder(seed=3); radii = (1.0, .84, .68, .52, .36, .2, 0.0); u0, v0, u1, v1 = rect('HULL_WHITE')      # 4 x 2 plates cover the 2 x 1 m half disc exactly
    def uvp(y, z): return (u0 + (y + R)/(2*R)*(u1 - u0), v0 + (z/R)*(v1 - v0))
    def P(i, k):
        p = polar(-.02, math.pi*k/NN, radii[i]); off = mnoise.noise(V((p.y*2, p.z*2, 1)))*.01
        return V((-.02 + off, p.y, p.z))
    for i in range(len(radii) - 1):
        for k in range(NN):
            pts = [P(i, k), P(i + 1, k), P(i + 1, k + 1), P(i, k + 1)]
            if i == len(radii) - 2: pts = [pts[0], pts[1], pts[3]]
            b.face(pts, [uvp(p.y, p.z) for p in pts], V((-1, 0, 0)))
    shell(b, R + .04, .07, -.04, .11, 1, NN, strip_uv(b, 'RIB', math.pi*R))
    b.box((-.05, 0, .30), (.03, 1.86, .06), maps={'-x': STRIP('BEAM', 'y')}, default=SW('SW_WHITE')); b.box((-.05, 0, .62), (.03, 1.5, .06), maps={'-x': STRIP('BEAM', 'y')}, default=SW('SW_WHITE'))
    for th in (rad(45), rad(135)): b.box(polar(-.05, th, .55), (.06, .03, .9), frame(th), maps={'-y': STRIP('BEAM', 'z')}, default=SW('SW_WHITE'))     # diagonal braces
    for k in range(1, 16): th = math.pi*k/16; rivet(b, polar(-.04, th, R - .03), -X, .02, .014, 'SW_BARE')
    t1 = V((0, 1, 0)); t2 = V((0, 0, 1)); cz = .42
    hbar(b, [V((-.07, .13*math.cos(a), cz + .13*math.sin(a))) for a in [k*math.pi/8 for k in range(17)]], .025, 'SW_STEEL', 6)
    b.revolve(V((-.075, 0, cz)), -X, t1, -t2, [(.12, 0, 'SW_GLASS'), (0, 0, 'SW_GLASS')], 16)
    arc(b, -.09, 8, 172, R - .12, .013, 'PIPE_YELLOW')
    for deg in (20, 55, 90, 125, 160): hbar(b, [polar(-.03, rad(deg), R - .12), polar(-.09, rad(deg), R - .12)], .011, 'SW_STEEL', 5)
    return b
def dock_flange(b):
    """the docking interface itself (top half, faces -X): neck at x = -0.42, a thick steel flange (r 0.80) standing proud of it with clamp lugs around its
    rim, bore stepping down in dark rings, sensor unit, approach lights, grab rail. Shared by hull_enddock and the central module's ports"""
    hrev(b, [(.74, -.42, ''), (.70, -.42, 'SW_STEEL'), (.70, -.47, 'GASKET'),
             (.80, -.47, 'SW_STEEL'), (.80, -.575, 'RIB'), (.775, -.60, 'SW_STEEL'), (.57, -.60, 'FLANGE'), (.57, -.52, 'SW_STEEL'), (.50, -.52, 'GASKET'),
             (.50, -.28, 'DOCK_DARK'), (.44, -.28, 'SW_DARK'), (.44, -.02, 'DOCK_DARK'), (.38, -.02, 'SW_DARK'), (.38, .22, 'DOCK_DARK'), (0, .22, 'SW_DARK')])
    for k in range(12):                                                                        # clamp lugs around the flange rim, teeth and bolts on its face
        th = rad(7.5 + 15*k); onhull(b, -.525, th, .80 + .012, (.075, .10, .05), {'+z': FIT('BRACKET', 'x')})
        if k % 2 == 0: b.box(polar(-.608, th, .745), (.07, .03, .05), frame(th), default=SW('SW_STEEL'))
        rivet(b, polar(-.60, th + rad(7.5), .68), -X, .02, .014, 'SW_BARE')
    onhull(b, -.53, rad(8), .80 + .075, (.15, .17, .13), faces('BOX', mz='SW_STEEL', py='BOX_ELEC'))              # sensor unit hanging off the rim
    for deg in (22, 28): b.box(polar(-.606, rad(deg), .70), (.035, .02, .08), frame(rad(deg)), default=SW('SW_LIGHT'))     # approach lights
    for d0, d1 in ((116, 146),):                                                               # bent grab rail standing off the rim
        hbar(b, [polar(-.525, rad(d0), .81), polar(-.525, rad(d0), .89)] + [polar(-.525, rad(d0 + (d1 - d0)*k/5), .91) for k in range(1, 5)]
                + [polar(-.525, rad(d1), .89), polar(-.525, rad(d1), .81)], .016, 'PIPE_YELLOW', 6)
def end_dock(b=None):
    """docking end (faces -X, x = 0 is the end of the hull), a long plated cone narrows the hull to the neck
    of dock_flange()"""
    b = b or Builder(seed=4); CA, CB = V((-.05, R)), V((-.42, .74))                               # cone from the hull end to the neck, as (x, radius)
    hrev(b, [(R + .05, .0, ''), (R + .05, -.05, 'RIB'), (R, -.05, 'SW_STEEL'), (.74, -.42, 'TANK_WHITE')])
    sl = (CB - CA).normalized()
    def cone(th, t, off=0.0):                                                                  # point on the cone (t = 0 at the hull, 1 at the neck) and its frame
        p = CA.lerp(CB, t); out = nrm(th)*(-sl.x) + X*sl.y; along = X*sl.x + nrm(th)*sl.y
        return polar(p.x, th, p.y) + out*off, rot(tang(th), along, out)
    for k in range(6):                                                                         # ribs down the cone, dark service slots between them
        c, fr = cone(rad(15 + 30*k), .5, .012); b.box(c, (.05, .42, .03), fr, maps={'+z': STRIP('BEAM', 'y')}, default=SW('SW_WHITE'))
    for deg in (45, 105, 135):
        c, fr = cone(rad(deg), .42, .006); b.box(c, (.22, .10, .014), fr, default=SW('SW_DARK'))
        c, fr = cone(rad(deg), .42, .016); b.box(c, (.24, .018, .02), fr, default=SW('SW_STEEL'))
    for deg in (75, 165):                                                                      # latch mechanisms bridging cone and flange
        c, fr = cone(rad(deg), .62, .02); b.box(c, (.20, .26, .04), fr, maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL'))
        c, fr = cone(rad(deg), .78, .07); b.box(c, (.11, .16, .08), fr, maps=faces('BOX'))
        c, fr = cone(rad(deg), .50, .05); b.box(c, (.05, .10, .03), fr, default=SW('SW_YELLOW'))
    dock_flange(b)
    arc(b, -.11, 4, 176, R + .02, .017, 'PIPE_YELLOW')                                         # pipe hoop around the base of the cone on clamp blocks
    for deg in (20, 55, 90, 125, 160): c, fr = cone(rad(deg), .16, .035); b.box(c, (.07, .06, .09), fr, maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL'))
    arc(b, -.19, 30, 150, .925, .011, 'CABLE_RED')
    return b

def port_half(b):
    """top half of a port in the dock's own frame (axis X, outward = -X, x = 0 at PORT_X): barrel through the band, ring frame, pipe hoop, dock flange"""
    hrev(b, [(.86, .85, ''), (.86, .34, 'TANK_WHITE'), (.91, .34, 'SW_STEEL'), (.91, .26, 'RIB'), (.86, .26, 'SW_STEEL'), (.86, -.42, 'TANK_WHITE'), (.74, -.42, 'SW_STEEL')])
    for deg in STN[::2]: onhull(b, .30, rad(deg), .91 + .01, (.10, .12, .05), {'+z': FIT('BRACKET', 'x')})
    arc(b, .05, 5, 175, .86 + .05, .016, 'PIPE_YELLOW')
    for deg in (20, 55, 90, 125, 160): onhull(b, .05, rad(deg), .86 + .02, (.06, .05, .06), {'+z': FIT('BRACKET', 'x')})
    for deg in (40, 140): onhull(b, -.18, rad(deg), .86 + .012, (.26, .30, .03), faces('BOX'))          # access panels on the barrel
    arc(b, -.30, 30, 150, .86 + .015, .011, 'CABLE_RED'); dock_flange(b)
def node_ports():
    """the two side ports of a junction, one piece: barrels along +Y and -Y with dock flanges, faces 2.0 m from the hull axis.
    Spawn it at the middle of a two-ring hull; the barrels pass through the hull plates"""
    b = Builder(seed=60)
    for s in (1, -1):
        n0 = len(b.bm.verts); port_half(b); n1 = len(b.bm.verts); port_half(b); xform(b, n1, Matrix.Rotation(math.pi, 3, 'X'))
        xform(b, n0, Matrix.Rotation(-s*math.pi/2, 3, 'Z'), (0, s*1.4, 0))
    return b
def pad():
    """mounting pad for wings and other external units (stands on Z = 0, the unit bolts on at z = 0.10)"""
    b = Builder(seed=61)
    b.box((0, 0, .03), (.56, .56, .06), maps={'+z': FIT('BOX', 'x')}, default=SW('SW_WHITE')); cyl(b, V((0, 0, .08)), .16, .04, 'z', 'SW_STEEL', 12)
    for sx in (-1, 1):
        for sy in (-1, 1): b.box((sx*.2, sy*.2, .07), (.10, .10, .03), maps={'+z': FIT('BRACKET', 'x')})
    hbar(b, [V((.16, 0, .08)), V((.3, .1, .05)), V((.34, .2, .0))], .011, 'CABLE_RED', 5)
    return b

# ----------------------------------------------------------------------------------------------------------------- wings
# Frame: origin on the mounting plate, +X away from the host, panels in the XY plane. A wing = wing_mount (0.5 m) + 1 m sections placed at x = 0.5, 1.5, ...
def wing_mount():
    b = Builder(seed=70)
    b.box((.025, 0, 0), (.05, .46, .46), maps={'+x': FIT('BRACKET', 'x'), '-x': FIT('BRACKET', 'x')}); b.box((.17, 0, 0), (.22, .24, .24), maps=faces('BOX', py='BOX_ELEC'))
    hbar(b, [V((.05, 0, 0)), V((.5, 0, 0))], .05, 'RAIL', 8)
    for a in (.8, 2.4, 3.9, 5.5): hbar(b, [V((.05, .19*math.cos(a), .19*math.sin(a))), V((.44, .04*math.cos(a), .04*math.sin(a)))], .012, 'SW_STEEL', 5)
    hbar(b, [V((.28, .08, .1)), V((.36, .12, .12)), V((.5, .07, .04))], .011, 'CABLE_RED', 5)
    return b
def wing_boom(b=None):
    """1 m of boom: a main tube, two thin rails and clamp blocks at both ends"""
    b = b or Builder(seed=71)
    hbar(b, [V((0, 0, 0)), V((.5, 0, 0)), V((1, 0, 0))], .04, 'RAIL', 8)
    for s in (-1, 1): hbar(b, [V((0, s*.07, .035)), V((1, s*.07, .035))], .011, 'PIPE_YELLOW' if s > 0 else 'CABLE_RED', 5)
    for x in (.04, .96): b.box((x, 0, 0), (.08, .16, .12), maps={'+z': FIT('BRACKET', 'x'), '-z': FIT('BRACKET', 'x')})
    return b
def wing_panel(face='SOLAR', torn=False, seed=72):
    """1 m wing section: boom + a 0.9 m panel either side, the same face on top and underside. torn = the outer half of one panel is gone, its frame bent"""
    b = wing_boom(Builder(seed=seed)); cols, rows = (2, 2) if face == 'SOLAR' else (1, 2); sw = sw_uv(b, 'SW_WHITE')
    for s in (-1, 1):
        y0, y1 = s*.10, s*1.0
        if torn and s > 0: y1 = s*.55
        for z, n in ((.018, Zup), (-.018, -Zup)):
            c = (V((.03, y0, z)), V((.97, y0, z)), V((.97, y1, z)), V((.03, y1, z))); patch(b, c, cols, rows if abs(y1 - y0) > .6 else 1, face, n, 1, True)
        for p, q, o in ((V((.03, y0, 0)), V((.97, y0, 0)), V((0, -s, 0))), (V((.03, y1, 0)), V((.97, y1, 0)), V((0, s, 0))), (V((.03, y0, 0)), V((.03, y1, 0)), -X), (V((.97, y0, 0)), V((.97, y1, 0)), X)):
            b.face([p + Zup*.018, q + Zup*.018, q - Zup*.018, p - Zup*.018], [sw]*4, o)
        b.box((.5, s*.55, 0), (.05, .9, .05), default=SW('SW_STEEL'))                              # spar
        if torn and s > 0:
            hbar(b, [V((.06, .55, 0)), V((.08, .8, .05)), V((.16, .98, .16))], .014, 'SW_STEEL', 5); hbar(b, [V((.94, .55, 0)), V((.9, .78, -.06)), V((.8, .9, -.2))], .014, 'SW_STEEL', 5)
            hbar(b, [V((.5, .55, 0)), V((.52, .7, .03))], .012, 'CABLE_RED', 5)
    return b
Zup = V((0, 0, 1))

# ----------------------------------------------------------------------------------------------------------------- small parts
def feet(b, sx, sy, h=.04, s=.05):
    for ax in (-1, 1):
        for ay in (-1, 1): b.box((ax*sx, ay*sy, h/2), (s, s, h), default=SW('SW_STEEL'))
def crate():
    """two strapped cargo cubes on a pallet"""
    b = Builder(seed=6)
    b.box((0, 0, .035), (.70, .42, .03), maps={'+z': STRIP('BEAM', 'x'), '+y': STRIP('BEAM', 'x'), '-y': STRIP('BEAM', 'x')}, default=SW('SW_WHITE')); feet(b, .30, .16, .02, .06)
    for cx in (-.17, .17):
        b.box((cx, 0, .21), (.32, .36, .32), maps=faces('CRATE', pz='BOX'))
        b.box((cx, 0, .375), (.34, .38, .02), maps={'+z': FIT('BOX', 'x')}, default=SW('SW_WHITE'))
        for sy in (-1, 1): b.box((cx, sy*.183, .30), (.08, .012, .05), default=SW('SW_STEEL'))                 # latches
    for y in (-.11, .11): hbar(b, [V((-.355, y, .05)), V((-.355, y, .40)), V((.355, y, .40)), V((.355, y, .05))], .012, 'PIPE_YELLOW', 6)       # strap frames
    hbar(b, [V((-.355, -.11, .40)), V((-.355, .11, .40))], .012, 'PIPE_YELLOW', 6); hbar(b, [V((.355, -.11, .40)), V((.355, .11, .40))], .012, 'PIPE_YELLOW', 6)
    b.box((0, -.194, .17), (.12, .012, .09), maps={'-y': FIT('HAZARD', 'x')}, default=SW('SW_YELLOW'))
    return b
def tank(body='TANK_WHITE', band='SW_RED'):
    b = Builder(seed=7); c = (0, 0, .24); B = body; n = X; t1 = V((0, 1, 0))
    rev(b, [(0, .42, ''), (.07, .415, B), (.14, .39, B), (.18, .34, B), (.18, -.34, B), (.14, -.39, B), (.07, -.415, B), (0, -.42, B)], 24, c, n, t1)
    for x in (-.20, .20):
        rev(b, [(.18, x + .025, ''), (.192, x + .025, band), (.192, x - .025, band), (.18, x - .025, band)], 24, c, n, t1)          # clamp bands + saddles
        b.box((x, 0, .035), (.07, .32, .07), maps={'+x': STRIP('BEAM', 'y'), '-x': STRIP('BEAM', 'y')}, default=SW('SW_WHITE'))
        for sy in (-1, 1): rivet(b, V((x, sy*.175, .09)), V((0, sy, 0)), .014, .012)
    cyl(b, V((.43, 0, .24)), .04, .06, 'x', 'SW_STEEL', 10); cyl(b, V((-.43, 0, .24)), .03, .04, 'x', 'SW_STEEL', 8)
    cyl(b, V((.26, 0, .45)), .02, .08, 'z', 'SW_STEEL', 8); cyl(b, V((.26, 0, .50)), .05, .02, 'y', 'SW_YELLOW', 10)           # valve
    hbar(b, [V((.46, 0, .24)), V((.50, 0, .24)), V((.52, .04, .18)), V((.50, .12, .06)), V((.46, .16, .0))], .012, 'RAIL', 5)
    hbar(b, [V((-.34, .10, .37)), V((-.40, .2, .28)), V((-.36, .27, .12)), V((-.32, .3, .0))], .011, 'CABLE_RED', 5)
    return b
def handrail():
    b = Builder(seed=8)
    for x in (-.55, 0, .55):
        b.box((x, 0, .01), (.09, .09, .02), maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL')); hbar(b, [V((x, 0, .02)), V((x, 0, .20))], .014, 'SW_STEEL', 6)
    hbar(b, [V((-.62, 0, .14)), V((-.59, 0, .20)), V((-.2, 0, .20)), V((.15, 0, .18)), V((.4, 0, .205)), V((.59, 0, .20)), V((.62, 0, .14))], .017, 'PIPE_YELLOW', 7)   # slightly bent rail
    hbar(b, [V((.4, 0, .2)), V((.42, .02, .13)), V((.38, .05, .06)), V((.44, .08, .0))], .008, 'CABLE_RED', 5)
    return b
def light():
    b = Builder(seed=9)
    b.box((0, 0, .02), (.16, .16, .04), maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL')); cyl(b, V((0, 0, .10)), .025, .12, 'z', 'SW_STEEL', 8)
    b.box((0, 0, .22), (.20, .20, .15), maps=faces('BOX', py='BOX_ELEC', my='BOX_ELEC'))
    b.box((.115, 0, .22), (.04, .16, .12), default=SW('SW_WHITE')); b.box((.13, 0, .22), (.02, .13, .09), default=SW('SW_LIGHT'))
    for z in (.19, .22, .25): b.box((.145, 0, z), (.012, .15, .008), default=SW('SW_DARK'))
    b.box((0, 0, .305), (.24, .22, .02), maps={'+z': FIT('BOX', 'x')}, default=SW('SW_WHITE'))
    hbar(b, [V((-.1, 0, .2)), V((-.16, 0, .14)), V((-.1, 0, .04))], .008, 'CABLE_DARK', 5)
    return b
def antenna():
    """mast with two equipment boxes, cross arms and a slightly bent whip"""
    b = Builder(seed=10)
    b.box((0, 0, .03), (.22, .22, .06), maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL')); b.box((0, 0, .15), (.14, .14, .18), maps=faces('BOX', px='BOX_ELEC'))
    hbar(b, [V((0, 0, .24)), V((0, 0, .55)), V((.01, .01, .85)), V((.05, .02, 1.1)), V((.14, .03, 1.28))], .016, 'RAIL', 7)
    for z, l in ((.5, .3), (.72, .22)):
        hbar(b, [V((0, -l, z)), V((0, l, z))], .009, 'RAIL', 5)
        for sy in (-1, 1): b.box((0, sy*l, z), (.07, .07, .09), maps=faces('BOX'))
    b.box((.07, 0, .62), (.10, .12, .12), maps=faces('BOX', px='BOX_VENT'))
    for a in (0, 2.1, 4.2):
        hbar(b, [V((0, 0, .34)), V((math.cos(a)*.18, math.sin(a)*.18, .04))], .007, 'SW_STEEL', 5); rivet(b, V((math.cos(a)*.18, math.sin(a)*.18, .04)), V((0, 0, 1)), .012, .01)
    hbar(b, [V((.07, 0, .2)), V((.1, .04, .4)), V((.06, .03, .58))], .007, 'CABLE_RED', 5)
    return b
def dish():
    b = Builder(seed=11)
    b.box((0, 0, .03), (.24, .24, .06), maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL')); hbar(b, [V((0, 0, .06)), V((0, 0, .30))], .03, 'RAIL', 8)
    b.box((0, 0, .32), (.10, .15, .09), maps=faces('BOX', px='BOX_ELEC'))
    tilt = rad(35); n = V((math.cos(tilt), 0, math.sin(tilt))); t1 = V((0, 1, 0)); t2 = n.cross(t1); c = V((0, 0, .42))
    b.bm.faces.ensure_lookup_table(); n0 = len(b.bm.faces)
    front = [(.30, .10), (.24, .064), (.18, .036), (.12, .016), (.06, .004), (0.0, 0.0)]
    b.revolve(c, n, t1, t2, [(r_, h_, 'SW_WHITE') for r_, h_ in front], 24)
    b.revolve(c, n, t1, t2, [(r_, h_ - .008, 'SW_BARE') for r_, h_ in front[::-1]], 24)
    b.bm.faces.ensure_lookup_table(); kill = []
    for f in list(b.bm.faces)[n0:]:                                                              # a torn-out sector
        q = f.calc_center_median() - c; ang = math.atan2(q.dot(t2), q.dot(t1)) % math.tau; rr = math.hypot(q.dot(t1), q.dot(t2))
        if rr > .18 and 1.5 < ang < 2.4: kill.append(f)
    bmesh.ops.delete(b.bm, geom=kill, context='FACES')
    for a in range(0, 360, 45):
        ca, sa = math.cos(rad(a)), math.sin(rad(a))
        hbar(b, [c + t1*.03*ca + t2*.03*sa - n*.008, c + t1*.29*ca + t2*.29*sa + n*.092], .006, 'SW_STEEL', 4)
    hbar(b, [c + n*.0, c + n*.22], .008, 'SW_STEEL', 5); b.box(c + n*.24, (.05, .05, .05), default=SW('SW_YELLOW'))
    for a in (0.5, 2.6, 4.7): hbar(b, [c + (t1*math.cos(a) + t2*math.sin(a))*.28 + n*.09, c + n*.23], .005, 'SW_STEEL', 4)
    return b
def vent():
    b = Builder(seed=12)
    b.box((0, 0, .15), (.36, .24, .22), maps=faces('BOX', my='BOX_VENT', pz='BOX_VENT')); feet(b, .15, .09)
    b.box((0, 0, .265), (.38, .26, .015), maps={'+z': FIT('BOX_VENT', 'x')}, default=SW('SW_WHITE'))
    b.box((.19, .04, .15), (.03, .08, .10), default=SW('SW_STEEL')); hbar(b, [V((.205, .04, .15)), V((.25, .04, .13)), V((.26, .06, .0))], .011, 'CABLE_DARK', 5)
    return b
def elec():
    b = Builder(seed=13)
    b.box((0, 0, .13), (.30, .22, .18), maps=faces('BOX', my='BOX_ELEC', px='BOX', pz='BOX')); feet(b, .12, .08)
    b.box((0, -.116, .13), (.24, .012, .14), maps={'-y': FIT('BOX_ELEC', 'x')}, default=SW('SW_WHITE'))                     # door slab
    for x in (-.08, 0, .08): cyl(b, V((x, 0, .235)), .016, .03, 'z', 'SW_STEEL', 7)
    hbar(b, [V((-.08, 0, .25)), V((-.10, .06, .27)), V((-.16, .10, .16)), V((-.18, .12, .0))], .008, 'CABLE_RED', 5)
    hbar(b, [V((.08, 0, .25)), V((.12, .05, .26)), V((.18, .08, .14)), V((.19, .10, .0))], .008, 'CABLE_DARK', 5)
    return b
def solar():
    """panel tilted on a tube frame"""
    b = Builder(seed=14); tl = rad(18); Rm = Matrix.Rotation(tl, 3, 'X'); c = V((0, 0, .17))
    b.box(c, (.62, .40, .02), Rm, maps={'+z': FIT('SOLAR', 'y')}, default=SW('SW_STEEL'))
    b.box(c + Rm @ V((0, 0, -.018)), (.64, .42, .016), Rm, default=SW('SW_WHITE'))
    for sx in (-1, 1):
        for sy, h in ((-1, .105), (1, .225)):
            hbar(b, [V((sx*.26, sy*.17, 0)), V((sx*.26, sy*.17, h))], .011, 'SW_STEEL', 5); b.box((sx*.26, sy*.17, .008), (.06, .06, .016), default=SW('SW_STEEL'))
        hbar(b, [V((sx*.26, -.17, .03)), V((sx*.26, .17, .19))], .007, 'SW_STEEL', 4)
    hbar(b, [V((0, .19, .22)), V((.05, .23, .12)), V((.02, .24, .0))], .007, 'CABLE_RED', 5)
    return b
def radar():
    """search radar: drive housing on a short mast, a wide slotted array tilted back on a yoke, a feed box behind it (stands on Z = 0, ~0.75 m tall)"""
    b = Builder(seed=15)
    b.box((0, 0, .03), (.24, .24, .06), maps={'+z': FIT('BRACKET', 'x')}, default=SW('SW_STEEL')); hbar(b, [V((0, 0, .06)), V((0, 0, .26))], .035, 'RAIL', 8)
    rev(b, [(0, .38, ''), (.11, .38, 'SW_WHITE'), (.12, .34, 'SW_WHITE'), (.12, .27, 'TANK_WHITE'), (.08, .26, 'SW_STEEL'), (0, .26, 'SW_STEEL')], 16, (0, 0, 0), V((0, 0, 1)))   # turntable drum
    b.box((.13, 0, .31), (.05, .10, .06), maps=faces('BOX', px='BOX_ELEC'))
    for sy in (-1, 1): b.box((0, sy*.28, .43), (.05, .03, .14), default=SW('SW_STEEL')); hbar(b, [V((0, sy*.1, .38)), V((0, sy*.28, .38))], .016, 'SW_STEEL', 6)    # yoke
    tl = rad(-20); Rm = Matrix.Rotation(tl, 3, 'Y'); c = V((0, 0, .55))
    b.box(c, (.05, .78, .26), Rm, maps={'+x': FIT('GRILLE', 'y'), '-x': FIT('BOX', 'y')}, default=SW('SW_WHITE'))                              # the array
    b.box(c + Rm @ V((-.04, 0, 0)), (.03, .82, .30), Rm, default=SW('SW_STEEL'))                                                                # back frame
    for z in (-.1, 0, .1): b.box(c + Rm @ V((.027, 0, z)), (.006, .74, .012), Rm, default=SW('SW_DARK'))                                       # slot rows
    b.box(c + Rm @ V((-.11, 0, 0)), (.12, .16, .14), Rm, maps=faces('BOX', mx='BOX_VENT'))                                                    # feed / receiver box
    for sy in (-1, 1): b.box(c + Rm @ V((.03, sy*.40, .14)), (.03, .03, .03), Rm, default=SW('SW_LED_RED'))                                    # beacons on the tips
    hbar(b, [V((-.1, .05, .5)), V((-.12, .1, .38)), V((-.06, .12, .3))], .009, 'CABLE_RED', 5)
    return b
def shuttle():
    """small crew shuttle that berths at a Docking Hub. Origin on its dock face (the same flange as hull_enddock, facing -X), body along +X:
    a pressurised cabin with cockpit windows, a service section with saddle tanks, two fold-out solar panels and three engine bells at the back"""
    b = Builder(seed=16); n0 = len(b.bm.verts)
    for flip in (False, True):                                                                 # docking flange: both halves of dock_flange, moved so its face is at x = 0
        k = len(b.bm.verts); dock_flange(b); xform(b, k, Matrix.Rotation(math.pi if flip else 0.0, 3, 'X'), (.6, 0, 0))
    # body (outside on the left: walk from the stern plate forward)
    rev(b, [(0, 3.15, ''), (.45, 3.15, 'SW_DARK'), (.62, 3.0, 'SW_STEEL'), (.72, 2.85, 'TANK_WHITE'), (.80, 2.55, 'TANK_WHITE'), (.82, 2.5, 'RIB'), (.82, 2.42, 'SW_STEEL'),
            (.80, 2.38, 'RIB'), (.80, 1.15, 'TANK_WHITE'), (.83, 1.1, 'SW_STEEL'), (.83, 1.0, 'RIB'), (.80, .95, 'SW_STEEL'), (.80, .45, 'TANK_BLUE'), (.74, .18, 'TANK_WHITE')], 32, n=X, t1=(0, 1, 0))
    for deg in range(20, 161, 28):                                                            # cockpit windows, wrapping the top of the nose section
        th = rad(deg); b.box(polar(.68, th, .805), (.16, .2, .03), frame(th), default=SW('SW_WINDOW')); b.box(polar(.68, th, .80), (.2, .26, .02), frame(th), default=SW('SW_STEEL'))
    for deg in (200, 340): th = rad(deg); onhull(b, 1.75, th, .80 + .02, (.5, .6, .04), {'+z': FIT('HATCH', 'x')})                      # side hatches
    for deg in range(0, 360, 45): th = rad(deg); onhull(b, 2.47, th, .82 + .01, (.08, .1, .04), {'+z': FIT('BRACKET', 'x')})            # clamp blocks on the ring
    arc(b, 1.6, 15, 165, .82, .014, 'PIPE_YELLOW'); arc(b, 2.2, 195, 345, .82, .014, 'CABLE_RED')
    # saddle tanks under the service section, on short struts
    for sy in (-1, 1):
        c = V((1.95, sy*.62, -.5))
        rev(b, [(0, .55, ''), (.12, .54, 'SW_STEEL'), (.2, .48, 'TANK_BLUE'), (.2, -.48, 'TANK_BLUE'), (.12, -.54, 'TANK_BLUE'), (0, -.55, 'SW_STEEL')], 16, c, X, (0, 1, 0))
        for x in (1.65, 2.25): hbar(b, [V((x, sy*.5, -.38)), V((x, sy*.38, -.68))], .025, 'SW_STEEL', 6)
        hbar(b, [c + V((-.55, 0, 0)), c + V((-.65, -sy*.1, .1)), V((1.25, sy*.4, -.65))], .012, 'PIPE_YELLOW', 5)
    # solar panels on booms, one each side at the waist
    for sy in (-1, 1):
        hbar(b, [V((2.05, sy*.8, .1)), V((2.05, sy*1.2, .1))], .03, 'RAIL', 8); b.box((2.05, sy*.82, .1), (.14, .06, .14), maps=faces('BOX', px='BOX_ELEC'))
        for k in range(2):
            y0 = sy*(1.2 + .62*k); b.box((2.05, y0 + sy*.3, .1), (.5, .58, .025), maps={'+z': FIT('SOLAR', 'y'), '-z': FIT('SOLAR', 'y')}, default=SW('SW_STEEL'))
    # engine bells: outer wall, then the throat inside
    for y, z in ((0, .3), (-.27, -.16), (.27, -.16)):
        c = V((3.15, y, z))
        rev(b, [(.20, .42, ''), (.10, 0.0, 'SW_STEEL'), (.07, -.06, 'SW_STEEL')], 14, c, X, (0, 1, 0))
        rev(b, [(.04, .02, ''), (.18, .41, 'SW_DARK')], 14, c, X, (0, 1, 0))
    # RCS quads at nose and stern, antenna and beacon on top
    for x in (.62, 2.75):
        for deg in (45, 135, 225, 315):
            th = rad(deg); onhull(b, x, th, (.80 if x < 1 else .72) + .05, (.1, .1, .1), faces('BOX', pz='BOX_VENT'))
    hbar(b, [polar(1.45, rad(90), .8), polar(1.45, rad(90), 1.1), V((1.55, 0, 1.25))], .012, 'RAIL', 6); b.box((1.4, 0, .84), (.12, .12, .08), maps=faces('BOX', px='BOX_ELEC'))
    b.box((2.3, 0, .83), (.05, .05, .04), default=SW('SW_LED_RED')); b.box((.95, .3, .8), (.04, .04, .04), default=SW('SW_LED_GREEN'))
    return b

# ----------------------------------------------------------------------------------------------------------------- kit build / export
GAIN = .62          # Material colour < 1: the game sun (intensity 3.5, ACES tonemap) bleaches albedos authored at face value into pastels
# Lumix material (standard.hlsl slots: albedo, normal, roughness (.g), metallic (.b), ambient occlusion (.r), emissive): the packed ORM map fills slots 3-5.
# The editor writes a stub .mat when it first imports an FBX; the builder overwrites it with this.
MAT = '''shader "/engine/shaders/standard.hlsl"
backface_culling true
layer "default"
texture "/models/parts_sheet/parts_basecolor.ltct"
texture "/models/parts_sheet/parts_normal.ltct"
texture "/models/parts_sheet/parts_orm.ltct"
texture "/models/parts_sheet/parts_orm.ltct"
texture "/models/parts_sheet/parts_orm.ltct"
texture "/models/parts_sheet/parts_emissive.ltct"
uniform "Material color", { %.6f, %.6f, %.6f, 1.000000 }
uniform "Roughness", 1.000000
uniform "Metallic", 1.000000
uniform "Emission", 4.000000
uniform "Translucency", 0.000000'''
def xform(b, n0, M, t=(0, 0, 0)):
    """rotate (3x3 M) then move every vertex created since the builder had n0 vertices: lets a piece reuse another piece's geometry"""
    b.bm.verts.ensure_lookup_table()
    for v in list(b.bm.verts)[n0:]: v.co = M @ v.co + V(t)
def patch(b, c, nu, nv, region, out, sub=2, fit=False):
    """bilinear quad c = (c00, c10, c11, c01) split into nu x nv sheet plates, each sub x sub quads (for vertex AO).
    fit=True maps the whole region onto every plate, otherwise each plate is a random 0.5 m plate of a HULL_* region"""
    c = [V(p) for p in c]; P = lambda u, v: (c[0]*(1 - u) + c[1]*u)*(1 - v) + (c[3]*(1 - u) + c[2]*u)*v
    x, y, w, h = T.RECTS[region]; px, py = (1, 1) if fit else (w//256, h//256); u0, v0, u1, v1 = rect(region)
    for i in range(nu):
        for j in range(nv):
            pi, pj = b.rng.randrange(px), b.rng.randrange(py); q = lambda fa, fb: (u0 + (pi + fa)/px*(u1 - u0), v0 + (pj + fb)/py*(v1 - v0))
            for a in range(sub):
                for d in range(sub):
                    k = [((a + da)/sub, (d + dd)/sub) for da, dd in ((0, 0), (1, 0), (1, 1), (0, 1))]
                    b.face([P((i + fa)/nu, (j + fb)/nv) for fa, fb in k], [q(fa, fb) for fa, fb in k], out)
def build_kit(kit, out):
    """build, AO-bake and export every (name, builder fn) as <out>/<name>.fbx on the parts material; writes <out>/parts_trim.mat.
    Returns ({name: object}, {name: triangles}, material)"""
    out.mkdir(exist_ok=True)
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    mat = make_material('parts_trim', 'parts', PSHEET / 'textures'); objs = {}; log = {}
    for name, fn in kit:
        ob = make_object(name, fn()); ob.data.materials.append(mat); objs[name] = ob; log[name] = tri_count(ob)
        print('BUILT', name, log[name], round(time.time() - T0, 1), flush=True)
    for name, ob in objs.items(): export_fbx(out / (name + '.fbx'), ob)
    (out / 'parts_trim.mat').write_text(MAT % (GAIN, GAIN, GAIN))
    return objs, log, mat
