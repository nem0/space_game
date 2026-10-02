"""Damaged habitat kit: hull segments + exterior attachments on the parts sheet (parts_sheet/, make_parts_sheet.py). The code lives in parts_lib.py.
Run after make_parts_sheet.py:   blender --background --python build_parts_trim.py
Look target: concept_art/new_style.png. Material: parts_trim + per-vertex AO (COLOR_0). Damage = geometry (dents, tears, bent parts, patch plates),
flaking paint in the sheet and vertex AO grime. No rust: chipped paint shows the white primer / bare metal."""
import sys; sys.path.insert(0, 'C:/projects/space_game/tools')
import importlib, parts_lib; importlib.reload(parts_lib)
from parts_lib import *
OUT = ROOT / 'models/parts'
# ----------------------------------------------------------------------------------------------------------------- build / export / demo
KIT = [('hull_basic', lambda: hull('basic', 'HULL_WHITE', 1, ('HULL_SCRAP', .35), wrap=(.2, 60, 150))), ('hull_window', lambda: hull('window', 'HULL_WHITE', 2)),
       ('hull_hatch', lambda: hull('hatch', 'HULL_WHITE', 3, loop=.36)), ('hull_plain_white', lambda: hull('plain', 'HULL_WHITE', 4, loop=-.36, wrap=(.25, 27, 120))),
       ('hull_plain_green', lambda: hull('plain', 'HULL_GREEN', 5)), ('hull_plain_red', lambda: hull('plain', 'HULL_RED', 6, wrap=(-.2, 66, 141))),
       ('hull_plain_blue', lambda: hull('plain', 'HULL_BLUE', 7)), ('hull_porthole_green', lambda: hull('porthole', 'HULL_GREEN', 8)),
       ('hull_porthole_white', lambda: hull('porthole', 'HULL_WHITE', 9, wrap=(.3, 66, 141), lit=True)), ('hull_grille_red', lambda: hull('grille', 'HULL_RED', 10)),
       ('hull_frame', hull_frame), ('hull_endclosed', end_closed), ('hull_enddock', end_dock),
       ('part_crate', crate), ('part_gastank', lambda: tank('TANK_BLUE', 'SW_YELLOW')), ('part_gastank_white', lambda: tank('TANK_WHITE', 'SW_RED')), ('part_handrail', handrail),
       ('part_light', light), ('part_antenna', antenna), ('part_dish', dish), ('part_vent', vent), ('part_elec', elec), ('part_solar', solar), ('part_radar', radar), ('ship_shuttle', shuttle), ('part_pad', pad),
       ('node_ports', node_ports), ('wing_mount', wing_mount), ('wing_boom', wing_boom), ('wing_solar', lambda: wing_panel('SOLAR')), ('wing_solar_torn', lambda: wing_panel('SOLAR', True, 73)),
       ('wing_radiator', lambda: wing_panel('GRILLE', False, 74)), ('wing_radiator_torn', lambda: wing_panel('GRILLE', True, 75))]
OBJ, log, mat = build_kit(KIT, OUT)

# demo module: also written to demo_layout.json (Blender coordinates) for tools/gen_parts_demo.py, which spawns the same thing in Studio
demo = Demo(OBJ, OUT); put = demo.put
def surf(x, deg, off=.04):
    t = rad(deg); return (x, (R + off)*math.cos(t), (R + off)*math.sin(t)), (t - math.pi/2, 0, 0)
RING = [('hull_plain_white', 'hull_basic'), ('hull_plain_green', 'hull_plain_green'), ('hull_porthole_white', 'hull_plain_white'), ('hull_grille_red', 'hull_plain_red'),
        ('hull_plain_blue', 'hull_plain_blue'), ('hull_hatch', 'hull_window')]
NR = len(RING)
for k, (top, bot) in enumerate(RING): put(top, (k, 0, 0)); put(bot, (k, 0, 0), (math.pi, 0, 0))
put('hull_enddock', (-.5, 0, 0)); put('hull_enddock', (-.5, 0, 0), (math.pi, 0, 0)); put('hull_endclosed', (NR - .5, 0, 0), (0, 0, math.pi)); put('hull_endclosed', (NR - .5, 0, 0), (math.pi, 0, math.pi))
Z = R + .03
put('part_crate', (.15, 0, Z)); put('part_vent', (.85, .2, Z), (0, 0, math.pi)); put('part_light', (.9, -.3, Z), (0, 0, math.pi)); put('part_gastank', (1.75, 0, Z))
put('part_elec', (2.55, -.28, Z)); put('part_solar', (2.75, .17, Z)); put('part_solar', (3.45, .17, Z)); put('part_gastank_white', (3.5, -.28, Z), (0, 0, .12))
put('part_antenna', (4.25, .3, Z)); put('part_dish', (4.5, -.3, Z), (0, 0, math.pi)); put('part_vent', (4.0, -.25, Z), (0, 0, .3))
for x, deg, nm in ((.0, 41, 'part_elec'), (1.0, 41, 'part_vent'), (4.0, 41, 'part_elec'), (4.75, 41, 'part_vent'), (5.2, 41, 'part_elec'),
                   (.2, 139, 'part_vent'), (1.2, 139, 'part_elec'), (4.4, 139, 'part_vent')):
    loc, r_ = surf(x, deg, .03); put(nm, loc, r_)
for x, deg in ((.6, 9), (2.0, 9), (3.4, 9), (4.8, 9), (.9, 100), (5.0, 60)): loc, r_ = surf(x, deg); put('part_handrail', loc, r_)
for x, deg in ((1.5, 238), (2.6, 238), (3.7, 238), (1.5, 302), (2.6, 302), (3.7, 302)): loc, r_ = surf(x, deg, .03); put('part_gastank_white', loc, r_)
for x, deg in ((.3, 270), (4.7, 270)): loc, r_ = surf(x, deg, .03); put('part_crate', loc, r_)
demo.save()
T.preview(OUT / 'parts_trim_preview.png', (-4.6, -6.6, 3.4), 40, (2.4, 0, .1), (1600, 900))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'parts_trim.blend'))
(OUT / 'manifest.json').write_text(json.dumps({'sheet': '../parts_sheet (own sheet: make_parts_sheet.py) + per-vertex AO (COLOR_0)',
    'material': 'parts_trim (habitat_trim.mat layout, parts_* textures)', 'triangles': log,
    'note': 'hull segments: half cylinder R=1.0 m, L=1.0 m, axis X, centred on X (rotate 180 deg about X for the lower half); attachments stand on Z=0'}, indent=1))
print('PARTS TRIM DONE', round(time.time() - T0, 1))
