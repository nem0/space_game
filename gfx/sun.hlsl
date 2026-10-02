// Texture-free sun disk: fixed albedo and self-illumination, independent of light/shadow.
//@surface
//@uniform "Sun color", "color", {1.0, 0.9, 0.7, 1.0}
//@uniform "Brightness", "float", 50
#include "engine/shaders/common.hlsli"
#include "engine/shaders/surface_base.hlsli"

Surface getSurface(VSOutput input, uint material_index) {
	MaterialData material = getMaterialData(material_index);
	Surface s;
	s.N = normalize(input.normal);
	s.albedo = max(material.u_sun_color.rgb, float3(0.001, 0.001, 0.001));
	s.alpha = 1.0;
	s.roughness = 1.0;
	s.metallic = 0.0;
	s.ao = 0.0;
	s.emission = max(material.u_brightness, 0.0);
	s.translucency = 0.0;
	s.shadow = 0.0; // suppress ordinary sunlight; the disk supplies its own emission
	return s;
}
