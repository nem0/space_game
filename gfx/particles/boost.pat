// Reboost burn exhaust (scripts/boost_fx.evox): two thin thruster jets from the small nozzles on the central module.
// Local space: the emitter entity sits between the two nozzles and its +Z axis points away from the station; the two nozzles are offset along local X.
// Each jet is a dense line of tiny glow sprites that fly fast and straight (so they read as one streak), white-yellow at the nozzle fading through
// orange to dark red, plus a small hot spot at the nozzle, a few sparks and a very faint haze cone. `thrust` (0..1) is ramped by the script.
global thrust : float

const NOZZLE_X = 0.30;      // half distance between the two nozzles (the thrusters on the central module, models/central_kit cen_thruster)
const NOZZLE_Z = -0.02;     // the emitter sits on the nozzle exit plane
const JET_LIFE = 0.42;
const JET_SPEED = 11;

fn saturate(x) {
	result = max(0, min(1, x));
}

// Colour ramp, written out in each emitter's output(): pale yellow-white at the nozzle (heat 1), through orange, to dark red (heat 0).
// (Helper functions that call saturate() inside their body compiled to wrong colours, so there are none.)

// which nozzle a particle belongs to: -1 or +1
fn side(i) {
	result = (i % 2) * 2 - 1;
}

emitter Jet {
	material "/gfx/particles/boost_glow.mat"
	init_emit_count 0
	emit_per_second 360

	out i_position : float3
	out i_scale : float
	out i_color : float4
	out i_rot : float
	out i_frame : float
	out i_emission : float

	var pos : float3
	var vel : float3
	var t : float
	var life : float

	fn emit() {
		t = 0;
		life = random(JET_LIFE * 0.8, JET_LIFE);
		// particles born in the same frame start at different points along the axis (about one frame of travel), or the jet shows as beads
		pos = {side(emit_index) * NOZZLE_X, 0, NOZZLE_Z + random(0, 0.2)};
		// almost straight: a hair of spread so the jet is a filament, not a laser
		vel = {random(-0.18, 0.18), random(-0.18, 0.18), random(JET_SPEED * 0.9, JET_SPEED)};
	}

	fn update() {
		t = t + time_delta;
		pos = pos + vel * time_delta;
		if t > life {
			kill();
		}
	}

	fn output() {
		let k = t / life;
		let h = saturate(1 - k);
		i_position = pos;
		// a slim body that widens a little as it cools
		i_scale = (0.07 + 0.11 * k) * thrust;
		let w = saturate(h * 2);
		let q = saturate(h * 2 - 1);
		i_color.x = 0.8 + 0.2 * w;
		i_color.y = 0.18 + 0.32 * w + 0.43 * q;
		i_color.z = 0.04 + 0.08 * w + 0.65 * q;
		i_color.a = saturate(1 - k * k) * 0.85 * thrust;
		i_rot = 0;
		i_frame = 0;
		i_emission = 6 + 8 * h;
	}
}

// the bright spot at each nozzle
emitter Flare {
	material "/gfx/particles/boost_glow.mat"
	init_emit_count 0
	emit_per_second 60

	out i_position : float3
	out i_scale : float
	out i_color : float4
	out i_rot : float
	out i_frame : float
	out i_emission : float

	var t : float
	var life : float
	var size : float
	var nx : float

	fn emit() {
		t = 0;
		life = random(0.06, 0.12);
		size = random(0.14, 0.22);
		nx = side(emit_index) * NOZZLE_X;
	}

	fn update() {
		t = t + time_delta;
		if t > life {
			kill();
		}
	}

	fn output() {
		let h = saturate(1 - t / life);
		i_position = {nx, 0, NOZZLE_Z + 0.04};
		i_scale = size * thrust;
		i_color = {1.0, 0.9, 0.65, h * thrust};
		i_rot = 0;
		i_frame = 0;
		i_emission = 14;
	}
}

// thin hot sparks that peel off the jet
emitter Sparks {
	material "/gfx/particles/boost_glow.mat"
	init_emit_count 0
	emit_per_second 26

	out i_position : float3
	out i_scale : float
	out i_color : float4
	out i_rot : float
	out i_frame : float
	out i_emission : float

	var pos : float3
	var vel : float3
	var t : float
	var life : float

	fn emit() {
		t = 0;
		life = random(0.4, 1.0);
		pos = {side(emit_index) * NOZZLE_X, 0, NOZZLE_Z + 0.1};
		let a = random(0, 6.28318);
		let spread = random(0.3, 1.6);
		vel = {cos(a) * spread, sin(a) * spread, random(8, 14)};
	}

	fn update() {
		t = t + time_delta;
		pos = pos + vel * time_delta;
		if t > life {
			kill();
		}
	}

	fn output() {
		let h = saturate(1 - t / life);
		i_position = pos;
		i_scale = 0.035 * thrust;
		let hc = 0.4 + 0.6 * h;
		let w = saturate(hc * 2);
		let q = saturate(hc * 2 - 1);
		i_color.x = 0.8 + 0.2 * w;
		i_color.y = 0.18 + 0.32 * w + 0.43 * q;
		i_color.z = 0.04 + 0.08 * w + 0.65 * q;
		i_color.a = saturate(h * 3) * thrust;
		i_rot = 0;
		i_frame = 0;
		i_emission = 10;
	}
}

// a faint warm cone of glowing gas around each jet, barely there: it only lifts the jet off the black
emitter Haze {
	material "/gfx/particles/boost_puff.mat"
	init_emit_count 0
	emit_per_second 24

	out i_position : float3
	out i_scale : float
	out i_color : float4
	out i_rot : float
	out i_frame : float
	out i_emission : float

	var pos : float3
	var vel : float3
	var t : float
	var rot : float

	fn emit() {
		t = 0;
		pos = {side(emit_index) * NOZZLE_X, 0, NOZZLE_Z + 0.08};
		let a = random(0, 6.28318);
		let spread = random(0, 0.9);
		vel = {cos(a) * spread, sin(a) * spread, random(5, 8)};
		rot = random(0, 6.28318);
	}

	fn update() {
		t = t + time_delta;
		pos = pos + vel * time_delta;
		if t > 0.8 {
			kill();
		}
	}

	fn output() {
		let k = t / 0.8;
		let h = saturate(1 - k);
		i_position = pos;
		i_scale = (0.25 + 0.9 * k) * thrust;
		let hc = 0.35 + 0.3 * h;
		let w = saturate(hc * 2);
		let q = saturate(hc * 2 - 1);
		i_color.x = 0.8 + 0.2 * w;
		i_color.y = 0.18 + 0.32 * w + 0.43 * q;
		i_color.z = 0.04 + 0.08 * w + 0.65 * q;
		i_color.a = saturate(k * 8) * h * 0.1 * thrust;
		i_rot = rot;
		i_frame = 0;
		i_emission = 3;
	}
}
