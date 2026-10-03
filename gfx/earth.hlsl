// Stylised Earth. The colour map (earth.png) gives the large shapes, a splatmap decides which detail texture shows where:
//  * splatmap (earth_splat.ltct, a texture recipe classifying the colour map): R ocean, G land, B ice / cloud, A scorched;
//  * four tiling detail textures, one per class, sampled triplanar on the sphere direction (no UV stretching, no pole pinch). Each one is divided
//    by its own mean colour, so only its variation is applied and an unassigned slot (neutral grey) changes nothing;
//  * the splatmap also drives roughness (glossy ocean, matte land);
//  * towards the colour map's own poles the equirectangular projection stretches into a starburst: there the colour of the latitude is used;
//  * the emissive map (fires, lava) glows fully on the night side and dimly by day, with a warmer rim at the terminator.
// The maps are small (one texel is ~10 world units, ~100 screen pixels straight below the station), so the scales between a map texel and the
// detail textures are made up procedurally instead of stored:
//  * the map lookup is displaced by fractal noise and its bilinear filter is sharpened, which turns the blurry texel borders into crisp, ragged
//    coastlines and patch edges (the geography stays where the map has it);
//  * clouds are a separate shell (earth_clouds.hlsl); this shader draws their shadow and darkens away the clouds painted in the colour map;
//  * the emissive map marks burning ground: there the surface is a dark lava crust with glowing cracks between its plates.
//@surface
//@texture_slot "Albedo", "engine/textures/white.tga"
//@texture_slot "Emissive", "engine/textures/black.tga"
//@texture_slot "Splat", "engine/textures/red.tga"
//@texture_slot "Detail ocean", "engine/textures/gray.tga"
//@texture_slot "Detail land", "engine/textures/gray.tga"
//@texture_slot "Detail ice", "engine/textures/gray.tga"
//@texture_slot "Detail burnt", "engine/textures/gray.tga"
// A color uniform must start at a multiple of 16 bytes (the engine aligns it in the material data, but the generated getMaterialData
// does not): keep it first, before the floats. Otherwise every uniform and texture after it is read from the wrong place.
//@uniform "Ocean color", "color", {1.0, 1.0, 1.0, 1.0}
//@uniform "Detail tiling", "float", 0.004
//@uniform "Detail strength", "float", 0.7
//@uniform "Night glow", "float", 1.2
//@uniform "Day glow", "float", 0.15
//@uniform "Planet radius", "float", 3000
//@uniform "Map warp", "float", 3.5
//@uniform "Map sharpness", "float", 0.45
//@uniform "Coast detail", "float", 0.3
//@uniform "Cloud amount", "float", 0.72
//@uniform "Cloud shadow", "float", 0.75
//@uniform "Ocean roughness", "float", 0.36
#include "engine/shaders/common.hlsli"
#include "engine/shaders/surface_base.hlsli"
#include "gfx/earth_noise.hlsli"

static const float COAST_SCALE = 12.0;   // world units of the largest bays and headlands added to the coastline
static const float RIFT_SIZE = 24.0;     // world units between the big lava rifts
static const float PLATE_SIZE = 6.0;     // world units of a lava crust plate
static const float FINE_SIZE = 1.5;      // world units of the small cracks inside a plate

// detail texture on the sphere: three planar projections blended by the surface direction, divided by the texture's mean colour
float3 detail(uint tex, float3 p, float3 w) {
	float3 c = bindless_textures[tex].SampleBias(LinearSampler, p.zy, -0.5).rgb * w.x
		+ bindless_textures[tex].SampleBias(LinearSampler, p.xz, -0.5).rgb * w.y
		+ bindless_textures[tex].SampleBias(LinearSampler, p.xy, -0.5).rgb * w.z;
	float3 mean = bindless_textures[tex].SampleLevel(LinearSampler, float2(0.5, 0.5), 12).rgb;
	return c / max(mean, 0.02);
}

// 3D Voronoi cells of size 1: distance from x to the nearest border between two cells (0 on the border). Slicing it with the sphere gives
// the cracked-plate pattern of a lava crust
float cellBorder(float3 x) {
	float3 fl = floor(x);
	int3 b = (int3)fl;
	float3 f = x - fl;
	float f1 = 8.0, f2 = 8.0;
	for (int k = -1; k <= 1; ++k) for (int j = -1; j <= 1; ++j) for (int i = -1; i <= 1; ++i) {
		int3 o = int3(i, j, k);
		float3 site = float3(latticeHash(b + o), latticeHash(b + o + int3(37, 17, 59)), latticeHash(b + o + int3(71, 113, 29)));
		float3 r = float3(o) + site - f;
		float dist = dot(r, r);
		if (dist < f1) { f2 = f1; f1 = dist; }
		else if (dist < f2) { f2 = dist; }
	}
	return sqrt(f2) - sqrt(f1);
}

// glowing crack of the given half-width (in cells) on a cell border; cracks thinner than a pixel keep their energy instead of flickering
float crackLine(float border, float width, float footprint) {
	float wpx = max(width, footprint * 1.2);
	return (1.0 - smoothstep(0.0, wpx, border)) * saturate(width / wpx) * (1.0 - smoothstep(0.35, 1.0, footprint));
}

Surface getSurface(VSOutput input, uint material_index) {
	MaterialData material = getMaterialData(material_index);
	Surface s;
	float3 N = normalize(input.normal);   // world-space direction from the planet centre; the planet does not move, so it is fixed to the surface
	float2 uv = input.uv;
	float3 P = N * material.u_planet_radius;
	float footprint = max(length(ddx(P)), length(ddy(P)));   // pixel size on the surface, world units

	// ragged, sharpened map lookup
	float2 map_size;
	bindless_textures[material.t_albedo].GetDimensions(map_size.x, map_size.y);
	float2 warp = mapWarp(P, footprint);
	float2 dx = ddx(uv) * 0.7, dy = ddy(uv) * 0.7;
	float magnified = 1.0 - saturate(max(length(dx), length(dy)) * map_size.x);   // 0 where a map texel is smaller than a pixel
	float cos_lat = max(sin(uv.y * 3.14159265), 0.25);
	float2 wuv = uv + warp * material.u_map_warp / map_size / float2(cos_lat, 1.0);
	float sharpness = material.u_map_sharpness * magnified;

	// coastline: the splatmap's ocean weight fades over several texels, which would make a blurred shore. Instead the shore is put where
	// that weight, roughened by fine noise, crosses one half, as an edge a pixel wide; the land side of it takes its colour and classes from
	// a point a bit inland, the sea side from a point a bit out to sea, so neither side shows the mixed colours of the map's own border
	float2 texel = 1.0 / map_size;
	float pole = smoothstep(0.72, 0.9, abs(uv.y * 2.0 - 1.0));   // latitude of the texture, wherever its poles point
	// the clouds painted in the map hide what is under them. Away from the poles that class counts as sea where the wider surroundings
	// (16 texels) are mostly sea, as land otherwise
	float4 around = bindless_textures[material.t_splat].SampleLevel(LinearSampler, wuv, 4);
	float2 as_sea = float2(1.0, (1.0 - pole) * smoothstep(0.35, 0.65, around.r / max(around.r + around.g, 1e-3)));   // weights of splat.rb
	float sea_weight = dot(bindless_textures[material.t_splat].SampleGrad(LinearSampler, wuv, dx, dy).rb, as_sea);
	float2 to_sea = float2(
		dot(bindless_textures[material.t_splat].SampleGrad(LinearSampler, wuv + float2(texel.x, 0.0), dx, dy).rb
			- bindless_textures[material.t_splat].SampleGrad(LinearSampler, wuv - float2(texel.x, 0.0), dx, dy).rb, as_sea),
		dot(bindless_textures[material.t_splat].SampleGrad(LinearSampler, wuv + float2(0.0, texel.y), dx, dy).rb
			- bindless_textures[material.t_splat].SampleGrad(LinearSampler, wuv - float2(0.0, texel.y), dx, dy).rb, as_sea));
	float slope = length(to_sea);
	float2 aside = to_sea / max(slope, 1e-4) * texel * (1.5 * saturate(slope * 8.0));   // nothing far from any shore
	float shore = sea_weight + (fbm(P / COAST_SCALE + 27.0, footprint / COAST_SCALE, 6, 0.55) - 0.5) * material.u_coast_detail;
	float edge = max(fwidth(shore) * 0.75, 1e-4);
	float sea = smoothstep(0.5 - edge, 0.5 + edge, shore);
	float2 land_uv = sharpenUV(wuv - aside, map_size, sharpness);
	float2 sea_uv = sharpenUV(wuv + aside, map_size, sharpness);

	float3 base = lerp(bindless_textures[material.t_albedo].SampleGrad(LinearSampler, land_uv, dx, dy).rgb,
		bindless_textures[material.t_albedo].SampleGrad(LinearSampler, sea_uv, dx, dy).rgb, sea);
	// one flat colour per pole (mean of four meridians of the map's polar rows, blurred): no rings, the ice detail texture gives it structure
	float polar_v = uv.y < 0.5 ? 0.03 : 0.97;
	float3 lat = 0.25 * (bindless_textures[material.t_albedo].SampleLevel(LinearSampler, float2(0.125, polar_v), 6).rgb
		+ bindless_textures[material.t_albedo].SampleLevel(LinearSampler, float2(0.375, polar_v), 6).rgb
		+ bindless_textures[material.t_albedo].SampleLevel(LinearSampler, float2(0.625, polar_v), 6).rgb
		+ bindless_textures[material.t_albedo].SampleLevel(LinearSampler, float2(0.875, polar_v), 6).rgb);
	float3 c = lerp(base, lat, pole);

	// splatmap: class weights (sum ~ 1); whatever is ocean, land or painted cloud is all ocean on the sea side of the shore and all land
	// on the other. `ice` is what is left of the ice / cloud class: the polar ice
	float4 splat = lerp(bindless_textures[material.t_splat].SampleGrad(LinearSampler, land_uv, dx, dy),
		bindless_textures[material.t_splat].SampleGrad(LinearSampler, sea_uv, dx, dy), sea);
	float painted_cloud = splat.b * (1.0 - pole);
	float ocean = (splat.r + splat.g + painted_cloud) * sea, land = (splat.r + splat.g + painted_cloud) * (1.0 - sea), ice = splat.b * pole, burnt = splat.a;

	// detail: tiles of material.u_detail_tiling per world unit, at two scales (the coarse one breaks the repetition of the fine one)
	float3 p = P * material.u_detail_tiling;
	float3 w = pow(abs(N), 4.0);
	w /= w.x + w.y + w.z;
	float3 d = detail(material.t_detail_ocean, p, w) * detail(material.t_detail_ocean, p * 0.27, w) * ocean
		+ detail(material.t_detail_land, p, w) * detail(material.t_detail_land, p * 0.27, w) * land
		+ detail(material.t_detail_ice, p, w) * detail(material.t_detail_ice, p * 0.27, w) * ice
		+ detail(material.t_detail_burnt, p, w) * detail(material.t_detail_burnt, p * 0.27, w) * burnt;
	float3 albedo = c * lerp(float3(1, 1, 1), d, material.u_detail_strength);

	// lighting terms
	float3 L = Global_light_dir.xyz;
	float NdL = dot(N, L);
	float night = 1.0 - smoothstep(-0.08, 0.12, NdL);
	float td = (NdL - 0.02) * 9.0;
	float terminator = exp(-td * td);

	// clouds are a separate shell (earth_clouds.hlsl); the ones painted in the colour map are darkened away, the procedural ones replace them
	albedo *= lerp(1.0, 0.3, painted_cloud);

	// ocean, after photos from orbit: deep blue water, turquoise shallows along some of the coasts, and a wide silvery sun glint. The
	// glint is the ordinary specular highlight; it is wide because the water is rough with waves, and uneven because the wind is: calm
	// patches are smoother (a smaller, brighter mirror of the sun), windy ones rougher
	float wind = fbm(P / 80.0 + 91.0, footprint / 80.0, 4, 0.55);
	float gusts = fbm(P / 7.0 + float3(warp, 33.0), footprint / 7.0, 4, 0.6);
	float sea_roughness = saturate(material.u_ocean_roughness + (wind - 0.5) * 0.4 + (gusts - 0.5) * 0.08);
	float shelf = (1.0 - smoothstep(0.5, 0.92, sea_weight)) * smoothstep(0.46, 0.60, fbm(P / 110.0 + 53.0, footprint / 110.0, 3, 0.5));
	float3 water = lerp(float3(0.009, 0.022, 0.050), float3(0.020, 0.140, 0.150), shelf) * material.u_ocean_color.rgb;
	water *= lerp(float3(1, 1, 1), d, 0.15 * material.u_detail_strength);
	albedo = lerp(albedo, water, ocean);

	// shadow of the cloud shell: the cloud field where the ray from this point to the sun crosses the shell. It dims the sunlight only
	// (diffuse and the sun glint), not the glow of the lava
	float3 shadow_p = normalize(P + L * (CLOUD_ALTITUDE / max(NdL, 0.12))) * material.u_planet_radius;
	float shadow = cloudOpacity(cloudPuff(shadow_p, warp, footprint, 6) + cloudBias(shadow_p, footprint, painted_cloud, material.u_cloud_amount));
	float sunlight = 1.0 - material.u_cloud_shadow * shadow;

	// lava: the emissive map only says where the ground burns (its lines are a texel wide, 10 world units); what is seen there is a dark
	// crust broken into plates, with the glow in the cracks between them. To keep it from looking like one even net, cracks come in three
	// sizes that are each open only in their own patches, the plates are bent (winding cracks, plates of different sizes), a crack changes
	// width and temperature along its length, and the hottest ground has open lava lakes
	float3 em = bindless_textures[material.t_emissive].SampleGrad(LinearSampler, wuv, dx, dy).rgb;   // unsharpened: no texel steps
	float hot = saturate(max(em.r, max(em.g, em.b))) * (1.0 - ocean);   // the map has faint lines over the oceans too: no lava at sea
	float heat = 0.0;
	[branch] if (hot > 0.02) {
		float field = smoothstep(0.30, 0.65, hot + warp.x * 0.3);   // ragged edge of the burning ground
		float3 bp = P / 38.0;
		float bf = footprint / 38.0;
		float3 bend = float3(fbm(bp + 5.1, bf, 3, 0.5), fbm(bp + 23.4, bf, 3, 0.5), fbm(bp + 61.9, bf, 3, 0.5)) - 0.5;
		float3 lp = P + bend * 26.0 + float3(warp.y, warp.x - warp.y, warp.x) * 4.0;
		float region = fbm(P / 55.0 + 3.1, footprint / 55.0, 3, 0.5);   // where the fine cracks are
		float patch = fbm(P / 13.0 + 9.4, footprint / 13.0, 3, 0.5);    // where the plate cracks are open
		float along = smoothstep(0.3, 0.7, fbm(lp / 3.0 + 17.0, footprint / 3.0, 2, 0.5));       // width along a crack
		float temper = smoothstep(0.3, 0.7, fbm(lp / 9.0 + 71.0, footprint / 9.0, 2, 0.5));     // hotter and cooler stretches
		float molten = smoothstep(0.85, 1.05, hot + warp.y * 0.5);   // the hottest ground: wide cracks and a dull glow through the crust

		float rift = crackLine(cellBorder(lp / RIFT_SIZE + 31.0), (0.012 + 0.03 * hot + 0.04 * molten) * (0.4 + 1.2 * along), footprint / RIFT_SIZE);
		float open = smoothstep(0.44, 0.56, patch + (hot - 0.65) * 0.3);
		float plates = open * crackLine(cellBorder(lp / PLATE_SIZE), (0.01 + 0.07 * hot * hot + 0.14 * molten) * (0.25 + 1.5 * along), footprint / PLATE_SIZE);
		float dense = smoothstep(0.50, 0.60, region + (hot - 0.7) * 0.25);
		float fine = 0.55 * dense * crackLine(cellBorder(lp / FINE_SIZE + 13.7), 0.03 + 0.05 * hot, footprint / FINE_SIZE);
		float lake = 0.85 * molten * smoothstep(0.56, 0.62, fbm(lp / 7.0 + 44.0, footprint / 7.0, 4, 0.55));
		heat = field * saturate(max(max(rift, plates), max(max(fine, lake), 0.12 * molten)) * (0.45 + 0.75 * temper));

		float3 crust = float3(0.045, 0.032, 0.028) * lerp(float3(1, 1, 1), d, material.u_detail_strength);
		albedo = lerp(albedo, crust, field * 0.7);   // also removes the glow painted into the colour map
		float3 lava = lerp(float3(0.55, 0.05, 0.008), float3(0.9, 0.42, 0.10), heat * heat);   // dull red at the crack edge, yellow in the middle
		albedo = lerp(albedo, lava, saturate(heat * 1.3));
	}

	s.albedo = albedo;
	s.alpha = 1.0;
	s.N = N;
	s.roughness = saturate(ocean * sea_roughness + land * 0.85 + ice * 0.6 + burnt * 0.9);
	s.metallic = 0.0;
	s.ao = 1.0;
	s.emission = heat * lerp(material.u_day_glow, 1.0, night) * material.u_night_glow * (1.0 + terminator * 0.25);
	s.translucency = 0.0;
	s.shadow = sunlight;
	return s;
}
