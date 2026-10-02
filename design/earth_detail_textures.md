# Earth detail textures - brief for the image generator

Four seamless, tileable detail textures. The Earth shader tiles them over the planet (triplanar, no UV stretching) and a splatmap
(`gfx/earth/earth_splat.png`, classified from `earth.png`) decides where each one shows. They add close-up grain to the low-resolution
world map, so they must NOT carry any large-scale structure, lighting or colour cast of their own.

## Rules for all four

- Square, **2048 x 2048** (1024 is acceptable), **perfectly seamless** on all four edges (tile it 2x2 to check).
- **Top-down satellite view**, orthographic, as if photographed from orbit at roughly 50-200 m per pixel. No horizon, no perspective, no sky.
- **Flat, neutral lighting**: no cast shadows, no sun direction, no vignette, no bright spots. The game lights the planet itself.
- **Mid-tone and low contrast**: the average brightness should sit around 50 % grey, features vary about +/-25 % around it.
  The shader divides by the texture mean, so only the variation is used, but strong dark/bright blobs will look like repeating polka dots.
- **Uniform detail**: no single recognisable landmark (one crater, one river, one road), because it will repeat many times.
- Post-apocalyptic, scorched-Earth mood to match `gfx/earth/earth.png` (dust, ash, soot, dead vegetation), not a lush green planet.
- No text, no watermark, no borders, no cloud shadows.
- PNG, sRGB, 3 channels (an alpha channel is not used).

## The four images

1. **detail_ocean.png** - dark ocean surface seen from orbit: very fine wind ripples and swell streaks, a few faint foam lines, subtle
   slick/oil-like patches. Dark grey-blue tone but keep the average mid-grey after grading; tiny, low-contrast variation.

2. **detail_land.png** - dry, dead continental terrain from above: dust plains, cracked earth, dry riverbeds, low ridges and erosion
   gullies, sparse dead scrub. Warm brown/tan/grey. Fine to medium scale grain, no mountains bigger than a few pixels.

3. **detail_ice.png** - ice sheet and thick cloud deck: broken pack ice, pressure ridges, thin cracks and wind-blown snow texture; soft
   cloud puffs for the cloud areas. Near-white with subtle blue-grey variation; keep contrast even lower than the others.

4. **detail_burnt.png** - scorched wasteland: ash fields, soot streaks, charred ground, glassy black patches and faint thin crack lines
   (no glowing lava, the lights come from the emissive map). Very dark grey/brown with fine grain.

## Prompt template

> Seamless tileable texture, top-down orbital satellite photograph of <SURFACE FROM THE LIST ABOVE>, flat neutral lighting, no shadows,
> uniform detail, low contrast, mid-tone, ultra sharp, 2048x2048, photorealistic, post-apocalyptic scorched Earth, no text, no borders.

Where to put the results: `gfx/earth/detail_ocean.png`, `detail_land.png`, `detail_ice.png`, `detail_burnt.png` (same folder as `earth.png`).
Then tell me and I will hook them up (they are already wired in the shader; until they exist it uses a neutral grey and shows no detail).
