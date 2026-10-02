// Thin spherical atmosphere: integrate exponentially thinning density along the view ray.
// The forward transparent pass keeps it out of sun-shadow rendering.
//@surface
//@uniform "Rayleigh color", "color", {0.08, 0.35, 1.0, 1.0}
//@uniform "Planet radius", "float", 3000
//@uniform "Shell radius", "float", 3030
//@uniform "Density", "float", 0.75
//@uniform "Glow", "float", 1.1
//@uniform "Nadir haze", "float", 0.3
#include "engine/shaders/common.hlsli"
#include "engine/shaders/surface_base.hlsli"

Surface getSurface(VSOutput input, uint material_index) {
	MaterialData material = getMaterialData(material_index);
	Surface s;
	float3 N = normalize(input.normal);
	float3 V = normalize(-input.pos_ws.xyz);
	float mu = saturate(dot(N, V));
	float outer_radius = max(material.u_shell_radius, 1.0);
	float inner_radius = clamp(material.u_planet_radius, 0.0, outer_radius - 0.01);
	float thickness = outer_radius - inner_radius;
	float impact_squared = outer_radius * outer_radius * saturate(1.0 - mu * mu);
	float outer_half = outer_radius * mu;
	float inner_half = sqrt(max(inner_radius * inner_radius - impact_squared, 0.0));
	// Outside the planet's silhouette, both halves of the shell contribute.
	// Over its surface, the opaque planet hides the rear half.
	float path = impact_squared >= inner_radius * inner_radius
		? 2.0 * outer_half : max(outer_half - inner_half, 0.0);
	// A constant-density shell makes a neon outline. Instead, density falls
	// by e every 1/6 shell height and approaches zero at the outer boundary.
	const int STEPS = 16;
	float scale_height = max(thickness / 6.0, 0.01);
	float step_length = path / STEPS;
	float column_density = 0.0;
	float lit_density = 0.0;
	float3 entry = N * outer_radius;
	[unroll] for (int i = 0; i < STEPS; ++i) {
		float3 p = entry - V * ((i + 0.5) * step_length);
		float radius = length(p);
		float altitude = max(radius - inner_radius, 0.0);
		float density = exp(-altitude / scale_height);
		// Smoothly extinguish density at the outer edge, not a visible shell cut.
		density *= 1.0 - smoothstep(thickness * 0.7, thickness, altitude);
		float day = smoothstep(-0.02, 0.16, dot(p / max(radius, 0.01), Global_light_dir.xyz));
		column_density += density * step_length;
		lit_density += density * day * step_length;
	}
	float grazing_path = sqrt(max(2.0 * outer_radius * scale_height, 1.0));
	// Preserve the soft limb while giving the short, straight-down air
	// column visible optical depth. Everything is composited by this shell.
	float nadir_weight = pow(mu, 4.0);
	float optical_depth = material.u_density * (
		column_density / grazing_path
		+ material.u_nadir_haze * nadir_weight * column_density / scale_height);
	float opacity = 1.0 - exp(-max(optical_depth, 0.0));
	float daylight = saturate(lit_density / max(column_density, 0.001));
	float sunward = pow(saturate(dot(V, Global_light_dir.xyz)), 8.0);
	float3 blue = material.u_rayleigh_color.rgb;
	float3 color = lerp(blue, float3(0.38, 0.66, 1.0), sunward * 0.2);
	s.N = N;
	s.albedo = color;
	s.alpha = saturate(opacity * daylight * 0.65);
	s.roughness = 1.0;
	s.metallic = 0.0;
	s.ao = 0.0; // no environment reflections on the gaseous shell
	s.emission = material.u_glow * daylight;
	s.translucency = 0.0;
	s.shadow = 1.0;
	return s;
}
