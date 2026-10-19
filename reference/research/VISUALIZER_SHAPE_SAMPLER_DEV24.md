# Visualizer SHAPE-source Xenos sampler — dev24

Status: **high-confidence retail-resource + executable-backed**

## Why this can now be closed

The ten Visualizer SHAPE resources are ordinary SIIG Xbox TEX resources. A private retail full-rip probe produced all ten original `.tex` files. Every file is exactly `0x10034` bytes: a **0x34-byte serialized D3D/Xenos resource header** followed by the `128 × 128 × 4 = 0x10000` byte texture payload.

Retail-lineage loader `Function_8248BEB0` copies exactly the first `0x34` bytes of this resource into the runtime texture object before relocation. `FUN_8248BDF0` returns that texture resource to the Visualizer source-image path, `Function_821AB320` retains it, and `Function_821AB6D8` later binds it with `Function_8226F5C0`. This makes the six dwords at serialized offsets `+0x1C..+0x30` the actual SHAPE texture fetch constant, not a format guess.

## Ten-resource header identity

All ten resources (`WhiteCircle`, `line`, `3line`, `square`, `triangle` and their `*2` variants) have the same 0x34-byte resource header. Its fetch dwords are:

```
81000002 00000086 000FE07F 00000C14 00000000 00000A00
```

The private header SHA-256 is recorded in the source-only validation JSON; no texture pixels are bundled.

## Fetch decode

Using the public `xe_gpu_texture_fetch_t` field layout in Xenia `src/xenia/gpu/xenos.h`:

- dword 0 clamp X/Y/Z fields are all `0` → **repeat**;
- dword 2 stores `(127,127)` → **128 × 128**;
- dword 3 is `0x00000C14`; mag/min/mip filter fields are all `0` → **point / point / point**;
- anisotropy field is `0` → **disabled**;
- dword 5 dimension field is `1` → **2D**.

Xenia is used only for public field/enum documentation. No new Xenia implementation code is copied.

## Browser bridge

When the simulator is generated from a user rip and therefore has the real SHAPE PNGs, Canvas2D image smoothing is disabled only around the transformed SHAPE `drawImage`, then restored immediately. This mirrors the proven point-filtered source fetch without changing unrelated canvas operations.

The procedural source-only fallback remains an approximation and is not presented as a texture-sampling emulation.

## Residual boundary

This closes SHAPE **texture filtering/addressing**. The separate `ScreenSpritePS` decode now closes the ordinary source color/tint/blend path as well: sampled RGBA is multiplied by runtime float4 tint RGBA and source-over blended with SrcAlpha/OneMinusSrcAlpha. EffectBlur shader/blend RGB semantics are independently closed. The remaining browser renderer caveat is exact Xenos render-target alpha storage/compositing, not an unknown SHAPE sampler or shader equation.
