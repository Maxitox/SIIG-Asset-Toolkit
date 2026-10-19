# THE MOON visual controller correction — dev24

## Scope

This note supersedes the old dev22 interpretation that THE MOON's retail visual controller used a dynamic **scale** path. The outer Workbench assembly boundary does **not** change: `bos_001.gmx` remains native-inspection-only because opcode `0x46` supplies no root X/Z placement and the controller's visual slots have not yet been mapped to exact exported GMX render nodes/materials.

## Retail controller chain

- Runtime `0x46` -> runtime+1 factory case `0x47` -> `Function_8212B638`.
- Setup: `Function_8212B6F8`.
- Per-visual-slot update: `Function_8212B760`.
- Euler setter: `FUN_8214b6e8`; slot 0 receives Z rotation in ten 36-degree steps.
- Material vector read/write: `FUN_8214da68` / `Function_8214D9B0`.
- Material forwarding: `Function_8214E120`. It walks `collada_edge1`, `collada_face1`, `collada_face2` in that order and forwards four-component vectors to the material objects.

`Function_8212B760` reads each current vector, preserves RGB, and changes only the fourth component. Those values are therefore material alpha, not node scale.

## Exact slot behavior

### Visual slot 0

Outside primary state 0, all three material alphas are 1.0. Z rotation is:

`((rotation_timer // frame_multiplier) % 10) * 36 degrees`

During primary state 0:

- `collada_edge1` alpha = **0.9**.
- Before `131 * frame_multiplier`, both face alphas are **0** and the rotation step is overridden by `fade_timer % 10`.
- From `131 * frame_multiplier` through the strict partial interval before `262 * frame_multiplier`, face alpha is `float32((timer-start)/(end-start))`. At the exact start boundary the value is still 0; the first positive authored runtime value is the next integer timer tick.
- At or after `262 * frame_multiplier`, both face alphas are **1**.

The controller's local resource flag starts at 0. For slot 0 it selects the visual resource referenced at engine offset `+0x1A8` only while face alpha is strictly between 0 and 1, then restores resource `+0x1A4` once face alpha becomes exactly 1.

### Nonzero visual slots

`Function_8212B6F8` assigns resource `+0x1A8` to setup slots 1..N-1. Their per-slot update writes alpha **0.4** to all three named material vectors and does not execute the slot-0 rotation write.

## Toolkit implementation

`the_moon_visual_controller_sample()` reproduces one retail update without game assets. `the-moon-controller` emits a JSON report with exact boundary samples and honors the runtime frame multiplier. The sampler intentionally does **not** synthesize glTF scale animation.

## Remaining promotion gate

The runtime law itself is now exact, but the controller visual-slot/material objects are not yet proven to correspond one-to-one with particular exported glTF nodes/materials in `bos_001.gmx`. Until that mapping is recovered, `the_moon_native_body` remains the canonical Workbench representation with identity **outer inspection transform** only.
