"""Damaged habitat kit: hull segments + exterior attachments on the parts sheet (parts_sheet/, texgen/parts.evox). The code lives in parts_lib.py.
Run:   blender --background --python build_parts_trim.py
Material: parts_trim + per-vertex AO (COLOR_0). Damage = geometry (dents, tears, bent parts, patch plates),
flaking paint in the sheet and vertex AO grime. No rust: chipped paint shows the white primer / bare metal."""
import sys; sys.path.insert(0, 'C:/projects/space_game/tools')
import importlib, parts_lib; importlib.reload(parts_lib)
from parts_lib import *
OUT = ROOT / 'models/parts'
# ----------------------------------------------------------------------------------------------------------------- build / export
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

print('PARTS TRIM DONE', round(time.time() - T0, 1))
