// Shared by the Earth surface (earth.hlsl) and its cloud shell (earth_clouds.hlsl): fractal noise, the displaced map lookup and the cloud
// field. Both shaders work on the same coordinates (the direction from the planet centre scaled to the planet radius), so the cloud shell
// finds the map's cloud coverage where the ground has it.

static const float WARP_SCALE = 14.0;      // world units of the largest map displacement wave (a bit more than a map texel, so the texel grid does not show)
static const float CLOUD_SCALE = 45.0;     // world units of the largest cloud puff
static const float CLOUD_ALTITUDE = 8.0;   // height of the cloud shell above the ground, world units; the "Earth clouds" entity in scripts/orbit.evox is scaled to match
static const float CLOUD_RELIEF = 0.6;     // distance of the sample that shades the cloud tops, world units

float latticeHash(int3 i) {
	uint n = (uint)i.x * 1597334677u ^ (uint)i.y * 3812015801u ^ (uint)i.z * 2798796415u;
	n = (n ^ (n >> 15)) * 2246822519u;
	n ^= n >> 13;
	return (n & 0xffffffu) * (1.0 / 16777215.0);
}

float valueNoise(float3 x) {
	float3 i = floor(x);
	float3 f = x - i;
	f = f * f * (3.0 - 2.0 * f);
	int3 b = (int3)i;
	return lerp(
		lerp(lerp(latticeHash(b), latticeHash(b + int3(1, 0, 0)), f.x), lerp(latticeHash(b + int3(0, 1, 0)), latticeHash(b + int3(1, 1, 0)), f.x), f.y),
		lerp(lerp(latticeHash(b + int3(0, 0, 1)), latticeHash(b + int3(1, 0, 1)), f.x), lerp(latticeHash(b + int3(0, 1, 1)), latticeHash(b + int3(1, 1, 1)), f.x), f.y),
		f.z);
}

// fractal noise around 0.5; `footprint` is the pixel size in units of p, octaves finer than a pixel fade to their mean instead of aliasing.
// `gain` is the amplitude ratio of successive octaves: 0.5 is smooth, more is rougher
float fbm(float3 p, float footprint, int octaves, float gain) {
	float a = 0.5, sum = 0.0, norm = 0.0;
	for (int i = 0; i < octaves; ++i) {
		float visible = 1.0 - smoothstep(0.3, 0.8, footprint);
		sum += a * lerp(0.5, valueNoise(p), visible);
		norm += a;
		p = p * 2.03 + 19.7;
		footprint *= 2.03;
		a *= gain;
	}
	return sum / norm;
}

// bilinear lookup position with a steeper blend between texels: flat inside a texel, a narrow transition at its border
float2 sharpenUV(float2 uv, float2 size, float sharpness) {
	float2 t = uv * size - 0.5;
	float2 i = floor(t);
	float2 f = t - i;
	float k = 0.45 * sharpness;
	f = lerp(f, smoothstep(k, 1.0 - k, f), saturate(sharpness * 4.0));
	return (i + 0.5 + f) / size;
}

// displacement of the map lookup at surface position P, about -0.5 .. 0.5 per axis
float2 mapWarp(float3 P, float footprint) {
	float3 wp = P / WARP_SCALE;
	return float2(fbm(wp, footprint / WARP_SCALE, 5, 0.6), fbm(wp + 41.3, footprint / WARP_SCALE, 5, 0.6)) - 0.5;
}

// the fine structure of the clouds at surface position P; with cloudBias added, above 0.5 is cloud
float cloudPuff(float3 P, float2 warp, float footprint, int octaves) {
	return fbm(P / CLOUD_SCALE + float3(warp, warp.x - warp.y) * 0.5, footprint / CLOUD_SCALE, octaves, 0.6);
}

// how much cloud there is around P: `covered` is the map's cloud coverage (splatmap B), on top of it come cloudy and clear regions a few
// hundred units across. `amount` is the material's "Cloud amount"
float cloudBias(float3 P, float footprint, float covered, float amount) {
	float weather = fbm(P / 260.0 + 7.7, footprint / 260.0, 3, 0.5) - 0.5;
	return lerp(-0.16, 0.26, covered) + weather * 0.7 + (amount - 0.5) * 0.6;
}

float cloudOpacity(float density) {
	return smoothstep(0.50, 0.62, density);
}
