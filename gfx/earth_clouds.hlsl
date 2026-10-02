// Cloud shell of the Earth: a second sphere CLOUD_ALTITUDE above the ground (see gfx/earth_noise.hlsli), so the clouds shift against the
// surface as the station moves and stack up towards the horizon. The clouds are procedural: fractal noise thresholded by the map's cloud
// coverage (splatmap B), shaded from the sun side.
// The shell is opaque geometry with holes (it has to be: the atmosphere shell is concentric with it, and two transparent spheres around
// the same centre cannot be depth sorted). Soft cloud edges are dithered, the dither pattern changes every frame and TAA averages it.
// "Planet radius", "Map warp", "Map sharpness" and "Cloud amount" must equal those of gfx/earth.mat, or the clouds drift off the map's
// cloud areas and their shadows on the ground no longer match them.
//@surface
//@define "ALPHA_CUTOUT"
//@texture_slot "Splat", "engine/textures/red.tga"
//@uniform "Planet radius", "float", 3000
//@uniform "Map warp", "float", 3.5
//@uniform "Map sharpness", "float", 0.45
//@uniform "Cloud amount", "float", 0.72
#include "engine/shaders/common.hlsli"
#include "engine/shaders/surface_base.hlsli"
#include "gfx/earth_noise.hlsli"

Surface getSurface(VSOutput input, uint material_index) {
	MaterialData material = getMaterialData(material_index);
	Surface s;
	float3 N = normalize(input.normal);
	float2 uv = input.uv;
	float3 P = N * material.u_planet_radius;   // the ground point straight below: the coordinates the ground shader uses
	float footprint = max(length(ddx(P)), length(ddy(P)));

	// the map's cloud coverage, looked up exactly like the ground does
	float2 map_size;
	bindless_textures[material.t_splat].GetDimensions(map_size.x, map_size.y);
	float2 warp = mapWarp(P, footprint);
	float2 dx = ddx(uv) * 0.7, dy = ddy(uv) * 0.7;
	float magnified = 1.0 - saturate(max(length(dx), length(dy)) * map_size.x);
	float cos_lat = max(sin(uv.y * 3.14159265), 0.25);
	float2 wuv = uv + warp * material.u_map_warp / map_size / float2(cos_lat, 1.0);
	float2 muv = sharpenUV(wuv, map_size, material.u_map_sharpness * magnified);
	float pole = smoothstep(0.72, 0.9, abs(uv.y * 2.0 - 1.0));
	float covered = bindless_textures[material.t_splat].SampleGrad(LinearSampler, muv, dx, dy).b * (1.0 - pole);

	float3 L = Global_light_dir.xyz;
	float3 to_sun = L - N * dot(N, L);
	to_sun /= max(length(to_sun), 0.2);
	float puff = cloudPuff(P, warp, footprint, 8);
	float puff_near = cloudPuff(P + to_sun * CLOUD_RELIEF, warp, footprint, 8);   // towards the sun: the difference shades the cloud tops
	float density = puff + cloudBias(P, footprint, covered, material.u_cloud_amount);
	float cloud = cloudOpacity(density);

	// interleaved gradient noise, shifted every frame
	float2 pixel = input.position.xy + 5.588238 * float(Global_frame_index & 63u);
	float dither = frac(52.9829189 * frac(0.06711056 * pixel.x + 0.00583715 * pixel.y));

	float thickness = saturate((density - 0.5) * 4.0);   // thin edges are grey, the thick middle is white
	float relief = saturate(0.55 + 0.3 * thickness + (puff - puff_near) * 9.0);
	s.albedo = float3(0.86, 0.88, 0.92) * relief;
	s.alpha = cloud > 0.02 + 0.96 * dither ? 1.0 : 0.0;
	s.N = N;
	s.roughness = 1.0;
	s.metallic = 0.0;
	s.ao = 1.0;
	s.emission = 0.0;
	s.translucency = 0.0;
	s.shadow = 1.0;
	return s;
}
