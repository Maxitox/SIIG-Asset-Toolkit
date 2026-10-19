# Visualizer EffectBlur blend-state closure — dev24

## Result

Retail Xbox 360 code closes the final fixed-function blend-factor ambiguity for the recursive Visualizer feedback pass. `Function_821595F0` executes immediately before `Function_82159CB8` through the EffectBlur virtual draw path and performs:

- `FUN_8224B188(device, 1)` — enable blending;
- `FUN_8224B2A8(device, 6)` — write source factor 6 into the low five bits of the blend-control staging word;
- `FUN_8224B338(device, 1)` — write destination factor 1 into bits 8..12.

With independent-alpha mode disabled, the device expands the staged value to `0x01060106`, duplicating the same factor pair into the alpha half of `RB_BLENDCONTROL`. The operation fields remain zero, which is Xenos `Add`. Xenia's public Xenos enum documentation identifies blend factor 6 as `SrcAlpha`, factor 1 as `One`, and blend op 0 as `Add`. No Xenia implementation code is copied.

The recovered hardware equation is therefore:

- RGB: `source * source_alpha + destination * 1`
- Alpha: `source_alpha * source_alpha + destination_alpha * 1`

This is additive, alpha-weighted feedback—not ordinary source-over compositing.

## Browser bridge

The simulator now uses Canvas `lighter` for the recursive previous-feedback draw, with `globalAlpha` carrying the recovered magnify alpha. This reproduces the recovered additive RGB accumulation far more closely than the former `source-over` approximation. Canvas compositing uses premultiplied-alpha storage, so exact alpha-channel equivalence to Xenos is still not claimed.

## Corrected earlier assumption

`DAT_8200E3C8` / `DAT_82569008` is a two-element vertex declaration created by `Function_82253B98` and installed by `FUN_82253A90`; it is **not** a two-record render/blend-state block. The old wording is superseded by this trace.

## Residual boundary

The pixel shader is now instruction-decoded: sampled feedback RGB is exported unchanged and sampled alpha is discarded in favor of uniform `Alpha.w`. Exact Canvas/Xenos alpha-channel storage equivalence remains deliberately unclaimed.
