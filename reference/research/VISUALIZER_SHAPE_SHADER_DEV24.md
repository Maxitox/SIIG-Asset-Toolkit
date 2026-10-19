# Visualizer SHAPE ScreenSprite shader closure — dev24

## Result

The Visualizer's ordinary SHAPE draw uses **ScreenSpritePS variant 0**. The retail Xbox 360 shader container is 232 bytes and its Xenos pixel microcode is **60 bytes**. Private instruction decoding shows a deliberately small path: one 2D texture sample followed by one vector multiply before color export.

The recovered pixel equation is:

`output.rgba = sampled_shape.rgba * runtime_tint.rgba`

The runtime color supplied to the sprite path is a four-component floating-point RGBA value. The texture's RGB is therefore real source color, not merely a mask, and the sampled texture alpha is multiplied by the runtime alpha instead of being replaced by it.

No proprietary shader bytes are bundled. The shader identity/size and derived instruction semantics are recorded only as source-only validation metadata.

## SHAPE blend state

The ordinary ScreenSprite source pass uses fixed-function alpha blending with:

- RGB/alpha source factor: **SrcAlpha**;
- RGB/alpha destination factor: **OneMinusSrcAlpha**;
- operation: **Add**.

For the source SHAPE pass this is the normal source-over equation. It is intentionally separate from the Visualizer EffectBlur feedback pass, which uses SrcAlpha/One additive blending.

## Browser bridge

When exact SHAPE PNGs are available from a user-supplied rip, the dev24 simulator now:

1. reads the original 128×128 PNG RGBA values;
2. multiplies R, G, B and A independently by the current runtime tint RGBA;
3. draws the tinted result with Canvas `source-over`;
4. keeps image smoothing disabled for the transformed draw, preserving the independently recovered point sampler behavior.

This replaces the older luminance-times-alpha mask bridge. That approximation discarded source hue and used `source-in` to paint a synthetic solid tint; it is no longer used for real SHAPE textures.

Procedural source-only stand-ins remain approximate when no real user-rip PNG is available, because they reproduce only the named geometric motif rather than proprietary texture pixels.

## Evidence boundary

This closes the previously explicit **ScreenSprite color/mask math** boundary for the real-texture path. Remaining Visualizer browser boundaries are narrower: host audio analysis-window timing is not cycle-equivalent to XAudio2, and the Canvas bridge does not claim exact Xenos alpha-target storage behavior outside the recovered RGB recurrence/compositing equations.
