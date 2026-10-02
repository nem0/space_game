// Star field and Milky Way, texture-free. Drawn on a huge sphere that scripts/orbit.evox keeps centred on the camera; everything is computed
// from the view direction in world space, so the sky stands still while the station and its camera go round the planet.
//  * stars: points scattered in a 3D grid, in two sizes of grid. The sphere of view directions cuts through that cloud of points, and each
//    point close to the sphere shows as a small disc - nearer the sphere, bigger and brighter. A star is never smaller than about a pixel
//    (it gets dimmer instead), otherwise it would flicker as the camera turns;
//  * Milky Way: a band around a tilted great circle, brighter towards the galactic centre, broken up by fractal noise, with dark dust lanes
//    along its middle; stars are denser inside it.
// The brightness is an artistic choice: real stars would be invisible next to the sunlit planet, here they are always on, and dimmed over
// the night side to make up for the exposure opening up there.
// It is in the transparent layer only to stay out of the shadow maps. The entity sits at the camera, so it is drawn after the atmosphere
// shell; alpha is the brightness, so empty sky leaves what is behind it untouched.
//@surface
//@uniform "Star brightness", "float", 12.0
//@uniform "Star density", "float", 1.6
//@uniform "Milky way", "float", 0.25
//@uniform "Night dimming", "float", 0.14
#include "engine/shaders/common.hlsli"
#include "engine/shaders/surface_base.hlsli"
#include "gfx/earth_noise.hlsli"

static const float3 GALAXY_POLE = float3(0.35, 0.62, 0.70);      // normal of the Milky Way's plane (normalised below)
static const float3 GALAXY_CENTRE = float3(0.80, -0.59, 0.12);   // roughly in that plane: where the band is widest and brightest
static const float MAX_RADIANCE = 40.0;
static const float3 PLANET_CENTRE = float3(0.0, -6600.0, -1800.0);   // EARTH_CENTER of scripts/station_orbit.evox

// one grid of stars. `cells` is the number of grid cells per unit of direction, `pixel` the size of a pixel in cells
float3 starLayer(float3 dir, float cells, float pixel, float chance, int seed) {
	float3 p = dir * cells;
	float3 fl = floor(p);
	int3 cell = (int3)fl + int3(seed * 7919, seed * 104729, seed * 1299709);
	float h = latticeHash(cell);
	// the star stays away from the cell walls, so it never has to be looked for from a neighbouring cell
	float3 star = fl + 0.2 + 0.6 * float3(latticeHash(cell + int3(37, 17, 59)), latticeHash(cell + int3(71, 113, 29)), latticeHash(cell + int3(11, 83, 47)));
	float radius = clamp(pixel * 1.6, 0.06, 0.2);
	float energy = min(1.0, 0.06 / (pixel * 1.6));
	float d = length(p - star) / radius;
	float disc = saturate(1.0 - d);
	float magnitude = h / chance;             // 0..1, independent of the position
	magnitude = 0.2 + 0.8 * pow(magnitude, 4.0);   // many faint stars, few bright ones
	float temperature = latticeHash(cell + int3(5, 3, 101));
	float3 colour = lerp(float3(1.0, 0.72, 0.50), float3(0.62, 0.78, 1.0), temperature);   // orange giants to blue-white
	colour = lerp(colour, float3(1, 1, 1), 0.45);
	return h > chance ? float3(0, 0, 0) : colour * (disc * magnitude * energy * energy);
}

Surface getSurface(VSOutput input, uint material_index) {
	MaterialData material = getMaterialData(material_index);
	Surface s;
	float3 dir = normalize(input.pos_ws.xyz);   // positions are relative to the camera
	float pixel = max(length(ddx(dir)), length(ddy(dir)));

	// Milky Way
	float3 pole = normalize(GALAXY_POLE);
	float3 centre = normalize(GALAXY_CENTRE - pole * dot(GALAXY_CENTRE, pole));
	float lat = dot(dir, pole);                           // sine of the galactic latitude
	float to_centre = dot(dir, centre) * 0.5 + 0.5;       // 1 towards the galactic centre, 0 opposite
	float width = lerp(0.10, 0.24, to_centre * to_centre);
	float band = exp(-lat * lat / (width * width));
	float clouds = fbm(dir * 5.0 + 11.0, pixel * 5.0, 5, 0.55);
	float dust = smoothstep(0.46, 0.62, fbm(dir * 9.0 + float3(3.1, 47.0, 19.0), pixel * 9.0, 5, 0.6)) * exp(-lat * lat / (width * width * 0.2));
	float glow = band * (0.25 + 0.75 * to_centre * to_centre) * smoothstep(0.30, 0.75, clouds + band * 0.2) * (1.0 - 0.8 * dust);
	float3 milky = lerp(float3(0.55, 0.65, 1.0), float3(1.0, 0.86, 0.68), to_centre * band) * (glow * material.u_milky_way);

	// stars: a fine grid of faint ones and a coarse grid of bright ones, both denser in the band
	float crowd = material.u_star_density * (1.0 + 1.6 * band * (1.0 - 0.6 * dust));
	float3 stars = starLayer(dir, 170.0, pixel * 170.0, 0.30 * crowd, 1) * 0.6
		+ starLayer(dir, 60.0, pixel * 60.0, 0.22 * crowd, 2) * 1.6;

	// the camera's exposure adapts: over the night side it opens up and the same sky comes out several times brighter. Counter that by
	// dimming the sky when the ground below the camera is dark
	float day = smoothstep(-0.3, 0.2, dot(normalize(Global_camera_world_pos.xyz - PLANET_CENTRE), Global_light_dir.xyz));
	float dim = lerp(material.u_night_dimming, 1.0, day);
	float3 radiance = milky * dim + stars * (material.u_star_brightness * sqrt(dim));
	float peak = max(radiance.r, max(radiance.g, radiance.b));
	s.albedo = radiance / max(peak, 1e-5);
	s.alpha = saturate(peak / MAX_RADIANCE);
	s.emission = MAX_RADIANCE;
	s.N = -Global_light_dir.xyz;
	s.roughness = 1.0;
	s.metallic = 0.0;
	s.ao = 0.0;       // no environment light
	s.translucency = 0.0;
	s.shadow = 0.0;   // no sunlight
	return s;
}
