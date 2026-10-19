# Visualizer EffectBlur pixel-shader closure — dev24

## Result

The retail Xbox 360 `EffectBlurPS` blob is 292 bytes and contains **72 bytes of Xenos pixel microcode** (SHA-256 `550328d21de6af38fde4a0814bd71aa68352667c826b0d7b1f172796c3db8116`). The proprietary blob/microcode is used only as private research input and is not bundled.

Decoding the instruction stream against the public Xenia `ucode.h` layouts yields a minimal program:

1. control flow executes one 2D texture fetch;
2. that fetch samples texture constant 0 into `r0.xyz` while the destination swizzle keeps `r0.w`;
3. one scalar ALU writes `r0.w = Alpha.w` (the encoded scalar `max` reads the same constant-W operand twice);
4. the final ALU exports `r0` unchanged as pixel color 0.

Therefore the shader source value for the recursive pass is:

`src.rgb = sample(previous_feedback).rgb`

`src.a = feedback_alpha`

The sampled feedback texture alpha does **not** participate in source RGB. Retail PS3 independently supports this interpretation: `EffectBlurPS` exposes only `TextureSampler` and `Alpha`, and the draw path uploads `(0,0,0,alpha)` to `Alpha`.

Combined with the separately recovered fixed-function `SrcAlpha / One / Add` blend, the RGB recurrence is:

`dst.rgb += sample(previous_feedback).rgb * feedback_alpha`

## Browser bridge

Canvas `lighter` normally includes the Canvas source alpha in premultiplied source RGB. That would incorrectly add the sampled feedback alpha as another attenuation term. The simulator therefore treats the two recursive feedback working canvases as opaque RGB surfaces (`alpha:false`) and always clears their RGB to the configured clear color. `globalAlpha` supplies the recovered uniform feedback alpha. This is an RGB-domain emulation of the recovered game path; exact Xenos alpha-channel storage is not claimed.

## Public documentation boundary

Xenia `ucode.h` is used only as public documentation of the Xenos control-flow, texture-fetch, ALU, swizzle and export encodings. No Xenia implementation code or proprietary shader bytes are copied into the toolkit.
