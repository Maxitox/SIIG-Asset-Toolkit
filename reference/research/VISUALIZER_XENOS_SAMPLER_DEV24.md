# Visualizer Xenos feedback sampler — dev24

Status: **high-confidence executable-backed**

This note isolates the sampler used when `Function_8216DC18` draws the previous 1280×720 feedback target. The current-SHAPE sampler is now independently recovered from its serialized retail TEX resources; see `VISUALIZER_SHAPE_SAMPLER_DEV24.md`.

## Constructor chain

- `Function_821AA630` creates the ping-pong render target and its sampleable texture.
- The texture call is `Function_8226F240(width, height, 1, 1, 0, 0x28280106, 0, 3)`.
- `Function_824AB1B0(..., 0x64800000)` zero-initializes the 0x34-byte resource allocation.
- Raw PPC around `Function_8226F240` maps the constructor arguments passed into `Function_8226EA98`; the hidden stack fields relevant to filter construction are zero.
- `Function_8226F5C0` binds six dwords from resource offsets `+0x1C..+0x30`, matching one Xenos texture-fetch constant.

## Exact result

The relevant fetch dword 3 is `0x00001414`. Xenia's public `xe_gpu_texture_fetch_t` layout places `mag_filter` at bits 19–20, `min_filter` at 21–22, `mip_filter` at 23–24, and `aniso_filter` at 25–27. All are zero here: point / point / point / anisotropy disabled. The clamp fields in fetch dword 0 remain zero from the zero-initialized resource, and Xenia's `ClampMode` enum names zero `kRepeat`.

Reference used for field names only: Xenia `src/xenia/gpu/xenos.h`, BSD-3-Clause, https://github.com/xenia-project/xenia. The toolkit already credits Xenia for its separately documented texture-addressing adaptation; this sampler trace adds documentation use only and copies no new upstream implementation code.

## Browser bridge

Canvas2D interpolation is disabled (`imageSmoothingEnabled=false`) for the recursive previous-feedback `drawImage`, then restored immediately afterward. The SHAPE source uses a separate, independently proven point-filtered path around its own transformed `drawImage`.

## Residual boundary

The EffectBlur fixed-function blend is now decoded as SrcAlpha/One Add, and its pixel shader is instruction-decoded separately. The browser uses `lighter` with opaque RGB feedback working canvases so sampled Canvas alpha does not add an extra attenuation term.
