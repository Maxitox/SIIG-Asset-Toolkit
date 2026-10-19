# Visualizer native min/max range contract — dev24 WIP176

Status: **hardware-observed Magnify A assertion + executable-backed sibling range rules**.

## Why this checkpoint exists

The project owner supplied eight new Xbox 360 real-hardware Visualizer Check recordings on 2026-09-20. During the dedicated Magnify A experiment, the June 10 build visibly entered its native blue assertion screen when the edited minimum crossed above the maximum.

The assertion identifies:

- source method: `VisualizerMain::SetMagnifyAlpha`
- source file: `VisualizerMain.cpp`
- source line: 446 (`0x1BE`)
- condition: `a1 >= a0`
- message: `Magnify Alpha is invalid`

The capture is private validation input and is not bundled.

## Executable cross-check

June 10 executable decompilation independently confirms the hardware observation.

### Magnify A

`Function_821751B0(a0, a1, ...)` asserts when `a1 < a0`, then stores the pair. The native contract is therefore:

`Magnify A max >= Magnify A min`

### Magnify Scale X/Y

`Function_821750F8(...)` contains two sibling assertions:

- X: `x1 >= x0` (`Magnify Sclae X is invalid` in the original string)
- Y: `y1 >= y0` (`Magnify Sclae Y is invalid`)

The native contracts are:

- `Magnify Scale X max >= min`
- `Magnify Scale Y max >= min`

### SHAPE RGBA ranges

`Function_82174E88(...)` validates all four min/max color pairs before storing them. Each channel requires its maximum to be no lower than its minimum:

- `R max >= R min`
- `G max >= G min`
- `B max >= B min`
- `A max >= A min`

`Function_82174FA8(...)` applies the same ordering rule to the internal clear-color range setter. Dedicated June 10 Check Mode exposes BG R/G/B/A as single values, so no browser min/max guard is needed for those four controls.

## Important non-generalization: SHAPE Scale X/Y

The four ParameterSet values at indices 17..20 are passed directly to `FUN_821750e0`, which stores four floats without the sibling max>=min assertion. The simulator therefore **does not** impose the Magnify/Color range rule on ordinary SHAPE Scale X/Y merely because those fields are presented as min/max controls.

This distinction is deliberate and evidence-bounded.

## Simulator behavior

Visualizer Simulator dataset **v19** adds native-safe pair guards for exactly the proven pairs:

- Magnify Scale X
- Magnify Scale Y
- Magnify A
- SHAPE R
- SHAPE G
- SHAPE B
- SHAPE A

When an interactive edit would invert one of these ranges, the browser moves the opposite endpoint to the edited value so the pair remains valid. ParameterSet application runs the same normalization after loading a row.

The browser intentionally does **not** reproduce the native debug assertion/crash. It preserves the valid-domain contract while keeping the research tool usable.

## Other findings from the same eight-capture batch

The same real-hardware batch independently corroborates existing simulator semantics rather than changing them:

- Add Rotation responds to Stick volume and reverses direction for negative values, consistent with `Rotation Base + Add Rotation * volume`.
- Fix Rotation is a direct signed degree override when nonzero; the project-owner sweep through approximately 360 degrees returns to the starting orientation modulo one full turn.
- Strong Magnify X/Y ranges make the raw BGM-driven interpolation visibly obvious and remain consistent with linear min→max interpolation.
- Quiet→loud BGM experiments produce raw Check Mode meter values spanning near zero to approximately 0.95 in the supplied capture set, consistent with the existing linear 0..1 XAudio2 peak-mean model.

These captures do **not** resolve the remaining Web Audio snapshot phase/scheduling boundary relative to the native 256-sample Xbox 360 XAudio2 processing quantum.

## Source-only boundary

No project-owner video/audio, game executable bytes, textures, music, or other proprietary payload is included in this repository. This note records derived behavior only.
