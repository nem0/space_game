"""Generates an Evox script that (re)assembles a parts-kit demo module in the active Studio world (run with any python; prints Evox source).
The layout is models/<kit>/demo_layout.json, written by the kit's builder (build_parts_trim.py -> parts, build_central_kit.py -> central_kit).
Earlier demo entities are destroyed first, so it can be re-run and the kits replace each other.
Usage: python gen_parts_demo.py [--kit parts|central_kit] [--json] [--yaw DEG] [--pivot X] [--move X Z] [--lift M] [--sun DEG] [--only PREFIX] [--skip PART] [--nofill] [--noshadow]
--json wraps the source in the MCP tools/call body for evox_execute (curl -d @file). The Studio scene camera cannot be moved remotely, so the module
is turned (--yaw, about module x = --pivot), shifted (--move, engine x z; --lift) and lit (--sun) to suit wherever the camera was left.
Blender -> engine: (x, y, z) -> (x, z, -y); rotations about Blender X/Z = engine X/Y."""
import json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def arg(name, default, n=1):
    if name not in sys.argv: return default
    v = [float(a) for a in sys.argv[sys.argv.index(name) + 1:sys.argv.index(name) + 1 + n]]; return v[0] if n == 1 else v
KIT = sys.argv[sys.argv.index('--kit') + 1] if '--kit' in sys.argv else 'parts'
LAYOUT = json.loads((ROOT / 'models' / KIT / 'demo_layout.json').read_text())
YAW = math.radians(arg('--yaw', 5.0)); SUN = math.radians(arg('--sun', 128.0))
hx = [e['loc'][0] for e in LAYOUT if e['part'].startswith('hull_')]
CX = arg('--pivot', (max(hx) + min(hx))/2 if hx else 0.0)      # module x that stays put when it is turned (default: its middle); -0.5 = the habitat's dock end
LIFT = arg('--lift', 0.0); MOVE = arg('--move', [0.0, 0.0], 2)
calls = []; SKIP = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--skip']      # --skip PART leaves a part type out (debugging)
ONLY = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--only']      # --only PREFIX keeps just the parts whose name starts with it
for e in [e for e in LAYOUT if e['part'] not in SKIP and (not ONLY or any(e['part'].startswith(o) for o in ONLY))]:
    (x, y, z), (rx, _, rz) = e['loc'], e['rot']
    x, y, rz = CX + (x - CX)*math.cos(YAW) - y*math.sin(YAW), (x - CX)*math.sin(YAW) + y*math.cos(YAW), rz + YAW
    calls.append('	put(world, "%s/%s.fbx", %.4f, %.4f, %.4f, %.5f, %.5f);' % (e.get('dir', 'models/' + KIT), e['part'], x + MOVE[0], z + LIFT, -y + MOVE[1], rx, rz))
OLD = ['Demo sun', 'Demo camera', 'Demo fill', 'demo_part']
src = '''import "core:world"
import "core:entity"
import "core:vec3"
import "core:quat" as quat
import "core:dvec3"
import "std:math" as math
import "core:renderer/module"
import "core:renderer/environment"
import "core:renderer/point_light"
import "core:renderer/model_instance"

fn clear(world : World, name : []const u8) : void {
	for i in 0..400 {
		if const e = world.findByName(name) { e.destroy(); } else { return; }
	}
}

fn put(world : World, path : []const u8, x : f32, y : f32, z : f32, rx : f32, ry : f32) : void {
	const e = world.createEntity();
	e.setName("demo_part");
	e.setPosition(DVec3 { x as f64, y as f64, z as f64 });
	const qx = quat.Quat { math.sin(rx * 0.5), 0.0, 0.0, math.cos(rx * 0.5) };
	e.setRotation(quat.makeQuatFromYaw(ry) * qx);
	if const mi = e.createModelInstance() {
		mi.setPath(path);
	}
}

fn fill(world : World, x : f32, y : f32, z : f32, cr : f32, cg : f32, cb : f32, intensity : f32) : void {
	const e = world.createEntity();
	e.setName("Demo fill");
	e.setPosition(DVec3 { x as f64, y as f64, z as f64 });
	if const l = e.createPointLight() {
		l.setColor(Vec3 { cr, cg, cb });
		l.setIntensity(intensity);
		l.setRange(200.0);
		l.setAttenuationParam(0.05);
		l.setCastShadows(false);
	}
}

fn main(world : World) : void {
	var r = world.renderer() else return;
''' + '\n'.join('\tclear(world, "%s");' % n for n in OLD) + '''
	const sun = world.createEntity();
	sun.setName("Demo sun");
	sun.setRotation(quat.makeQuatFromYaw(SUN_YAW) * quat.makeQuatFromPitch(-0.7));
	if const env = sun.createEnvironment() {
		env.setDirectIntensity(3.5);
		env.setIndirectIntensity(0.6);
		env.setSkyIntensity(0.0);
		env.setSunlightStrength(1.0);
		env.setAtmoEnabled(false);
		env.setCastShadows(true);
		r.setActiveEnvironment(sun);
	}
	sun.setPosition(DVec3 { 2.5, 30.0, 0.0 });	// keeps the editor icon out of the picture
	// the sun has no sky light, so shadows are pitch black: a blue earthshine fill from below and a weak neutral bounce stand in for the planet.
	// Keep the module off the lights' axis planes and 45 deg diagonals: surfaces on those planes render as thin black lines.
	fill(world, 9.0, -40.0, 17.0, 0.45, 0.62, 1.0, 5.0);
	fill(world, 34.0, 9.0, 14.0, 1.0, 0.95, 0.9, 0.8);
''' + '\n'.join(calls) + '''
}'''
src = src.replace('SUN_YAW', '%.4f' % SUN)
if '--nofill' in sys.argv: src = src.replace('	fill(world, ', '	// fill(world, ')
if '--noshadow' in sys.argv: src = src.replace('env.setCastShadows(true)', 'env.setCastShadows(false)')      # debugging shadow artefacts
if '--json' in sys.argv: print(json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'evox_execute', 'arguments': {'code': src}}}))
else: print(src)
