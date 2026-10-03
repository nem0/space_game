"""Modular central module (lens-shaped hub) in the damaged parts style, on the parts sheet. Code shared with
the habitat kit lives in parts_lib.py.   Run:   blender --background --python build_central_kit.py
The module is a 16-sided lens: a vertical band of 16 facets, a sloping roof and underside of 16 sectors each, and two hubs. Every sector piece is
built for the facet facing +X with its origin at the MODULE CENTRE, so a piece goes on facet k by placing it at the module origin turned k * 22.5 deg
about the vertical axis. Any wall facet can be swapped for another wall variant or for a port; roofs and undersides swap the same way.
Sizes (m): band apothem 3.0, band height 1.5, overall 3.5 high without masts, port flange face at 4.0 from the centre (same dock as hull_enddock)."""
import sys; sys.path.insert(0, 'C:/projects/space_game/tools')
import importlib, parts_lib; importlib.reload(parts_lib)
from parts_lib import *
OUT = ROOT / 'models/central_kit'
N = 16; STEP = math.tau/N; TA = math.tan(math.pi/N)                # facets, sector angle, half-width of a facet per metre of apothem
A = 3.0; ZB = .75                                                  # band apothem, band half-height
ST = (A - .15, .90); SB = (A - .20, -.95)                          # (apothem, z) where the shoulders end and roof / underside begin
RI = (1.25, 1.40); UI = (1.30, -1.50)                              # (apothem, z) where roof / underside meet the hubs
THRUST_X = 3.40; THRUST_Y = .30; THRUST_Z = -.15                                  # thruster nozzle exit plane, half spacing, height
PORT_X = 3.40                                                      # x = 0 of the dock frame: the flange face (0.6 further out) sits at 4.0
Y = V((0, 1, 0)); Zv = V((0, 0, 1))

def edge(r, z, s): return V((r, s*r*TA, z))                        # point on the sector edge (s = -1 / +1) at apothem r
def bil(c, u, v): return (c[0]*(1 - u) + c[1]*u)*(1 - v) + (c[3]*(1 - u) + c[2]*u)*v
def normal(c, up): n = (c[1] - c[0]).cross(c[3] - c[0]).normalized(); return n if n.z*up > 0 else -n
def edge_ribs(b, c, n):
    """half a rib along both radial edges of a roof / underside sector (the neighbour brings the other half)"""
    for e0, e1, s in ((c[0], c[3], 1), (c[1], c[2], -1)):
        d = e1 - e0; dn = d.normalized(); side = n.cross(dn)*s                               # `side` points into the sector
        b.box((e0 + e1)/2 + side*.03 + n*.02, (.06, d.length, .06), rot(dn.cross(n), dn, n), maps={'+z': STRIP('BEAM', 'y')}, default=SW('SW_WHITE'))
def slab(b, c, n, u0, u1, v0, v1, h, top, skirt='SW_WHITE'):
    """raised panel on a sector: corners of the inset quad, lifted by h; top(d) draws the face, the four skirts are flat swatches"""
    d = [bil(c, u, v) + n*h for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]; top(d); mid = sum(d, V())/4; sw = sw_uv(b, skirt)
    for i in range(4): p, q = d[i], d[(i + 1) % 4]; b.face([p, q, q - n*h, p - n*h], [sw]*4, (p + q)/2 - mid)
    return d

# ----------------------------------------------------------------------------------------------------------------- band facets
def wall(paint='HULL_WHITE', feature=None, seed=1, bare=False):
    """one band facet: 2 x 3 plates, shoulders, half posts with clamp blocks at both edges, rim beams, yellow rim pipes and cable runs.
    feature: vent / porthole / locker / panel. bare = no pipes and cables (the port barrel takes their place)"""
    b = Builder(seed=seed); w = A*TA
    patch(b, (edge(A, -ZB, -1), edge(A, -ZB, 1), edge(A, ZB, 1), edge(A, ZB, -1)), 2, 3, paint, X)
    for z0, (r1, z1) in ((ZB, ST), (-ZB, SB)):                                                  # shoulders up to the roof / down to the underside
        b.quad_spec([edge(A, z0, -1), edge(A, z0, 1), edge(r1, z1, 1), edge(r1, z1, -1)], STRIP('DOCK', 'x'), X*abs(z1 - z0) + Zv*math.copysign(A - r1, z0), 2*w)
    for s in (-1, 1):
        b.box((A + .035, s*(w - .03), 0), (.07, .06, 2*ZB), maps={'+x': STRIP('RIB', 'z')}, default=SW('SW_STEEL'))
        for z in (-.52, 0, .52): b.box((A + .05, s*(w - .045), z), (.10, .09, .13), maps={'+x': FIT('BRACKET', 'x')}, default=SW('SW_STEEL'))
    for z in (-ZB + .04, ZB - .04): b.box((A + .03, 0, z), (.06, 2*w - .12, .08), maps={'+x': STRIP('BEAM', 'y')}, default=SW('SW_WHITE'))
    if not bare:
        for z, sg in ((ZB + .09, 1), (-ZB - .10, -1)):                                          # rim pipes meet the neighbours' pipes at the corners
            d = .10; ye = (A + d)*TA; hbar(b, [V((A + d, -ye, z)), V((A + d, 0, z)), V((A + d, ye, z))], .017, 'PIPE_YELLOW', 6)
            for y in (-.3, .3): b.box((A + d - .045, y, z - sg*.05), (.05, .05, .12), maps={'+x': FIT('BRACKET', 'x')}, default=SW('SW_STEEL'))
        for z, strip, r_ in ((.625, 'CABLE_RED', .012), (.655, 'CABLE_DARK', .010), (-.63, 'CABLE_RED', .012)):
            pts = []                                                                            # cable along the band, hopping over the posts
            for k in range(15):
                y = (A + .12)*TA*(k/7 - 1); hop = max(0.0, 1 - (w - abs(y))/.14); pts.append(V((A + .02 + r_ + .088*hop, y, z + .012*math.sin(k*1.7))))
            hbar(b, pts, r_, strip, 5)
    if feature == 'vent':
        b.box((A + .07, 0, .0), (.14, .64, .50), maps=faces('BOX', px='BOX_VENT')); b.box((A + .145, 0, .0), (.015, .68, .54), maps={'+x': FIT('BOX_VENT', 'x')}, default=SW('SW_WHITE'))
        hbar(b, [V((A + .07, .32, .1)), V((A + .05, .42, .2)), V((A + .03, .46, .45)), V((A + .03, .44, .62))], .011, 'CABLE_RED', 5)
    if feature == 'porthole':
        c = V((A + .01, 0, .05)); b.box(c, (.02, .64, .64), maps={'+x': FIT('BOX', 'x')}, default=SW('SW_WHITE'))
        hbar(b, [c + X*.03 + (Y*math.cos(a) + Zv*math.sin(a))*.23 for a in [k*math.tau/24 for k in range(25)]], .035, 'SW_STEEL', 6)
        for k in range(8): a = k*math.tau/8 + .39; rivet(b, c + X*.06 + (Y*math.cos(a) + Zv*math.sin(a))*.23, X, .018, .012, 'SW_BARE')
        b.revolve(c + X*.025, X, Y, Zv, [(.20, 0, 'SW_WINDOW'), (0, 0, 'SW_WINDOW')], 20)                 # lit from inside
        b.box((A + .13, 0, -ZB - .05), (.30, .74, .34), maps=faces('CRATE', pz='BOX'))             # equipment box hung under the window
        b.box((A + .13, 0, -ZB + .13), (.32, .78, .02), maps={'+z': FIT('BOX', 'x')}, default=SW('SW_WHITE'))
        for s in (-1, 1): b.box((A + .05, s*.3, -ZB + .2), (.10, .05, .16), maps={'+x': FIT('BRACKET', 'x')}, default=SW('SW_STEEL'))
    if feature == 'locker':
        b.box((A + .10, 0, .02), (.20, .46, .96), maps=faces('BOX', px='BOX_ELEC'))
        for z in (-.40, .44): b.box((A + .10, 0, z), (.22, .50, .04), default=SW('SW_STEEL'))
        hbar(b, [V((A + .10, -.23, -.3)), V((A + .06, -.34, -.4)), V((A + .03, -.42, -.55)), V((A + .03, -.44, -.62))], .011, 'CABLE_DARK', 5)
    if feature == 'panel':
        b.box((A + .025, -.04, .02), (.05, .62, .84), maps=faces('BOX', px='BOX')); b.box((A + .07, .12, .22), (.06, .16, .22), maps=faces('BOX', px='BOX_ELEC'))
        for sy in (-1, 1):
            for sz in (-1, 1): rivet(b, V((A + .05, -.04 + sy*.27, .02 + sz*.38)), X, .018, .012, 'SW_BARE')
    return b
def port(seed=20):
    """a facet carrying a docking port: a barrel a little wider than the dock flange, then the same flange as hull_enddock (face 4.0 m from the centre)"""
    b = wall('HULL_WHITE', None, seed, bare=True)
    n0 = len(b.bm.verts); port_half(b); n1 = len(b.bm.verts); port_half(b); xform(b, n1, Matrix.Rotation(math.pi, 3, 'X'))        # both halves ...
    xform(b, n0, Matrix.Rotation(math.pi, 3, 'Z'), (PORT_X, 0, 0))                                                         # ... turned to face +X
    for s in (-1, 1): hbar(b, [V((3.12, s*.62, .66)), V((3.06, s*.66, .64)), V((A + .12, s*(A + .12)*TA, .625))], .012, 'CABLE_RED', 5)
    return b

def eva(seed=21):
    """a facet with a visual EVA hatch: a short barrel standing out of the hull, steel flange ring, a closed round door with a handwheel, grab rails and a lamp"""
    b = wall('HULL_WHITE', None, seed, bare=True); R0 = .50; L = .55; c = V((A - .05, 0, -.02)); E = A - .05 + L                  # barrel from inside the hull to x = E
    b.revolve(c, X, Y, Zv, [(R0, 0, 'TANK_WHITE'), (R0, L - .06, 'TANK_WHITE'), (R0 + .07, L - .06, 'SW_STEEL'), (R0 + .07, L, 'SW_STEEL'), (R0 - .06, L, 'SW_STEEL'), (R0 - .06, L - .05, 'SW_STEEL'), (0, L - .05, 'SW_STEEL')], 28)   # barrel, flange, door
    b.revolve(c + X*(L - .05), X, Y, Zv, [(R0 - .10, 0, 'RIB'), (R0 - .10, .02, 'RIB'), (R0 - .16, .02, 'SW_WHITE'), (0, .02, 'SW_WHITE')], 28)                                   # raised door panel
    for k in range(12): a = k*math.tau/12 + .13; rivet(b, c + X*L + (Y*math.cos(a) + Zv*math.sin(a))*(R0 + .035), X, .017, .014, 'SW_BARE')
    for k in range(3): a = k*math.tau/3 + math.pi/2; hbar(b, [c + X*(L + .01), c + X*(L + .05) + (Y*math.cos(a) + Zv*math.sin(a))*.17], .016, 'SW_STEEL', 6)   # handwheel spokes
    hbar(b, [c + X*(L + .05) + (Y*math.cos(k*math.tau/24) + Zv*math.sin(k*math.tau/24))*.17 for k in range(25)], .016, 'SW_STEEL', 6); cyl(b, c + X*(L + .03), .05, .06, 'x', 'SW_STEEL', 10)
    for sy in (-1, 1): hbar(b, [V((E - .30, sy*.80, -.40)), V((E - .12, sy*.80, -.40)), V((E - .12, sy*.80, .36)), V((E - .30, sy*.80, .36))], .02, 'PIPE_YELLOW', 6)
    b.box((E - .15, -.52, .56), (.08, .12, .08), default=SW('SW_LIGHT'))
    return b

def thruster(seed=22):
    """a facet with two small reboost thrusters: bells on short housings, exit plane THRUST_X from the centre (boost_fx.evox starts the plume there), propellant lines and a clamp plate"""
    b = wall('HULL_WHITE', None, seed, bare=True); x0 = A + .04
    b.box((A + .05, 0, -.15), (.10, 1.0, .56), maps=faces('BOX', px='BOX_ELEC'))                                          # mounting plate
    for sy in (-1, 1):
        c = V((x0 + .05, sy*THRUST_Y, THRUST_Z)); b.box((x0 + .02, sy*THRUST_Y, THRUST_Z), (.06, .34, .34), maps={'+x': FIT('BRACKET', 'x')}, default=SW('SW_STEEL'))
        b.revolve(c, X, Y, Zv, [(.15, 0, ''), (.15, .17, 'TANK_WHITE'), (.10, .17, 'SW_STEEL'), (.19, THRUST_X - x0 - .05, 'SW_STEEL'), (.155, THRUST_X - x0 - .05, 'SW_STEEL'), (.07, .17, 'SW_DARK'), (0, .17, 'SW_DARK')], 20)
        hbar(b, [V((A + .1, sy*.50, .06)), V((x0 + .08, sy*(THRUST_Y + .17), -.02)), V((x0 + .08, sy*(THRUST_Y + .17), THRUST_Z + .1))], .012, 'PIPE_YELLOW', 6)
    hbar(b, [V((A + .1, -.5, .06)), V((A + .1, 0, .12)), V((A + .1, .5, .06))], .012, 'CABLE_RED', 5)
    return b

# ----------------------------------------------------------------------------------------------------------------- roof / underside sectors
def roof(kind='solar', seed=30):
    """roof sector: plates + edge ribs; solar = two columns of cells down the slope, vent = short solar row + an air handler near the hub, plain = plates only"""
    b = Builder(seed=seed); c = (edge(*ST, -1), edge(*ST, 1), edge(*RI, 1), edge(*RI, -1)); n = normal(c, 1)
    patch(b, c, 2, 3, 'HULL_WHITE', n); edge_ribs(b, c, n)
    if kind in ('solar', 'vent'):
        rows = 3 if kind == 'solar' else 1
        slab(b, c, n, .09, .91, .05, .05 + .29*rows, .045, lambda d: patch(b, d, 2, rows, 'SOLAR', n, 1, True))
    if kind == 'vent':
        r = 1.95; z = ST[1] + (ST[0] - r)/(ST[0] - RI[0])*(RI[1] - ST[1])                       # roof height under the unit's centre
        b.box((r, 0, z + .30), (.74, .66, .42), maps=faces('BOX', px='BOX_VENT', py='BOX_VENT', my='BOX_VENT', pz='BOX_VENT'))
        b.box((r, 0, z + .52), (.78, .70, .025), maps={'+z': FIT('BOX_VENT', 'x')}, default=SW('SW_WHITE'))
        for sy in (-1, 1):
            b.box((r + .32, sy*.28, z + .0), (.06, .06, .22), default=SW('SW_STEEL'))             # legs on the low side of the slope
            hbar(b, [V((r - .40, sy*.36, z + .16)), V((r - .40, sy*.36, z + .56)), V((r + .40, sy*.36, z + .56)), V((r + .40, sy*.36, z - .06))], .013, 'PIPE_YELLOW', 6)
        hbar(b, [V((r + .37, .1, z + .3)), V((r + .46, .14, z + .2)), V((r + .5, .2, z - .1))], .011, 'CABLE_RED', 5)
    return b
def under(seed=40):
    """underside sector: plates + edge ribs + three dark radiator panels"""
    b = Builder(seed=seed); c = (edge(*SB, -1), edge(*SB, 1), edge(*UI, 1), edge(*UI, -1)); n = normal(c, -1)
    patch(b, c, 2, 3, 'HULL_WHITE', n); edge_ribs(b, c, n)
    for k in range(3):
        slab(b, c, n, .10, .90, .05 + .31*k, .33 + .31*k, .035, lambda d: b.quad_spec(d, STRIP('DOCK_DARK', 'x'), n, (d[1] - d[0]).length), 'SW_DARK')
    return b

# ----------------------------------------------------------------------------------------------------------------- hubs (whole pieces)
def ngon(b, prof, segs=N):
    """16-sided revolve about the vertical axis with facets lined up with the sectors; radii are apothems"""
    k = 1/math.cos(math.pi/segs); rev(b, [(r*k, h, s) for r, h, s in prof], segs, n=Zv, t1=(1, 0, 0), a0=-math.pi/segs)
def ring_rail(b, r, z, z0, posts=8):
    hbar(b, [V((r*math.cos(a), r*math.sin(a), z)) for a in [k*math.tau/32 for k in range(33)]], .016, 'PIPE_YELLOW', 6)
    for k in range(posts): a = (k + .5)*math.tau/posts; hbar(b, [V((r*math.cos(a), r*math.sin(a), z0)), V((r*math.cos(a), r*math.sin(a), z))], .012, 'SW_STEEL', 5)
def around(b, r, z, size, maps, count, a0=0.0, default=SW('SW_STEEL')):
    for k in range(count): a = a0 + k*math.tau/count; b.box((r*math.cos(a), r*math.sin(a), z), size, Matrix.Rotation(a, 3, 'Z'), maps=maps, default=default)
def hub_top():
    """top hub: drum closing the roof, deck with a railing, turret with four vent faces (antenna / dish parts stand on the turret, z = 1.98)"""
    b = Builder(seed=50)
    ngon(b, [(0, 1.98, ''), (.62, 1.98, 'TANK_WHITE'), (.62, 1.64, 'DOCK'), (RI[0] + .03, 1.64, 'TANK_WHITE'), (RI[0] + .03, RI[1] - .03, 'DOCK')])
    around(b, .64, 1.81, (.10, .42, .24), faces('BOX', px='BOX_VENT'), 4); around(b, .64, 1.81, (.06, .20, .28), faces('BOX', px='BOX_ELEC'), 4, math.pi/4)
    around(b, .98, 1.665, (.13, .13, .05), {'+z': FIT('BRACKET', 'x')}, 8, math.pi/8); ring_rail(b, 1.20, 1.80, 1.64)
    b.box((0, 0, 2.0), (.5, .5, .04), maps={'+z': FIT('BRACKET', 'x')})
    for sx in (-1, 1): b.box((sx*.52, 0, 2.02), (.06, .06, .08), default=SW('SW_LED_RED'))          # beacons either side of the mast base
    return b
def hub_bottom():
    """bottom hub: drum, vent block and a sensor mast hanging below"""
    b = Builder(seed=51)
    ngon(b, [(UI[0] + .03, UI[1] + .03, ''), (UI[0] + .03, -1.74, 'DOCK'), (.60, -1.74, 'TANK_WHITE'), (.60, -2.06, 'DOCK'), (0, -2.06, 'TANK_WHITE')])
    around(b, .62, -1.90, (.10, .44, .24), faces('BOX', px='BOX_VENT'), 4); around(b, 1.0, -1.765, (.13, .13, .05), {'-z': FIT('BRACKET', 'x')}, 8, math.pi/8)
    ring_rail(b, 1.24, -1.88, -1.74)
    hbar(b, [V((0, 0, -2.06)), V((0, 0, -2.5)), V((.01, .0, -2.95))], .035, 'RAIL', 8)
    for a in (0.3, 2.4, 4.5): hbar(b, [V((.42*math.cos(a), .42*math.sin(a), -2.06)), V((0, 0, -2.42))], .012, 'SW_STEEL', 5)
    b.box((0, 0, -2.30), (.18, .18, .12), maps=faces('BOX')); b.box((.12, 0, -2.68), (.16, .15, .18), maps=faces('BOX', px='BOX_ELEC'))
    hbar(b, [V((0, -.22, -2.52)), V((0, .22, -2.52))], .01, 'RAIL', 5); b.box((0, .22, -2.52), (.07, .07, .09), maps=faces('BOX')); b.box((0, 0, -2.98), (.09, .09, .07), default=SW('SW_LED_RED'))
    hbar(b, [V((.04, 0, -2.06)), V((.07, .03, -2.3)), V((.05, .02, -2.58))], .009, 'CABLE_RED', 5)
    return b

# ----------------------------------------------------------------------------------------------------------------- build / export
KIT = [('cen_wall_white', lambda: wall('HULL_WHITE', None, 1)), ('cen_wall_green', lambda: wall('HULL_GREEN', None, 2)), ('cen_wall_red', lambda: wall('HULL_RED', None, 3)),
       ('cen_wall_blue', lambda: wall('HULL_BLUE', None, 4)), ('cen_wall_green_vent', lambda: wall('HULL_GREEN', 'vent', 5)), ('cen_wall_red_vent', lambda: wall('HULL_RED', 'vent', 6)),
       ('cen_wall_blue_vent', lambda: wall('HULL_BLUE', 'vent', 7)), ('cen_wall_porthole', lambda: wall('HULL_WHITE', 'porthole', 8)), ('cen_wall_locker', lambda: wall('HULL_WHITE', 'locker', 9)),
       ('cen_wall_panel', lambda: wall('HULL_WHITE', 'panel', 10)), ('cen_wall_scrap', lambda: wall('HULL_SCRAP', None, 11)), ('cen_port', port), ('cen_eva', eva), ('cen_thruster', thruster),
       ('cen_roof_solar', lambda: roof('solar')), ('cen_roof_vent', lambda: roof('vent', 31)), ('cen_roof_plain', lambda: roof('plain', 32)), ('cen_under', under),
       ('cen_hub_top', hub_top), ('cen_hub_bottom', hub_bottom)]
OBJ, log, mat = build_kit(KIT, OUT)

print('CENTRAL KIT DONE', round(time.time() - T0, 1))
