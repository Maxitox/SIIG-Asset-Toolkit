# SIIG Asset Toolkit 2.8.0-dev5 release notes

Dev5 converts most of the previously structural 32 × 30 camera-preset table into evidence-backed runtime semantics without changing the frozen dev4 route implementation.

## Camera preset semantics

- Added `camera-preset <0..31>` for semantic JSON inspection.
- Optional `--runtime-x` / `--runtime-y` evaluates the retail dynamic horizontal-response path using single-precision-compatible arithmetic.
- Word 0 is perspective FOV in degrees.
- Word 1 is uniform scene/view scale.
- Words 2–4 are the camera-eye offset transformed through the active route/stage frame and added to current `FieldPos`.
- Words 5–7 are scene/view translation.
- Words 8–10 are dynamic horizontal-response gain, target local-X scale, and eye local-X scale.
- Words 12–29 are three fog profiles `{start, end, RGBA}`, proven through renderer `fogRange` and `vFogColor` consumers.
- Word 11 is retained as `shared_model_material_scalar_unresolved`: it is forwarded unchanged to `collada_edge1`, `collada_face1`, and `collada_face2`, but the virtual setter's exact property meaning is not yet established.

## Reference data

- Added `reference/tables/CAMERA_PRESETS_RUNTIME_SEMANTIC.csv`.
- Updated `CAMERA_PRESET_SCHEMA.csv` with evidence addresses, transition behavior, high-confidence names, and the explicit unresolved-word policy.
- Preserved `CAMERA_PRESETS_RAW.csv` unchanged as the executable-ground-truth table and retained the structural `CAMERA_PRESETS_RUNTIME.csv`.

## Validation

- 29/29 dependency-free self-tests pass.
- The semantic table contains all 32 presets and all 30 runtime words/roles.
- Dynamic-response regression checks the normalized-coordinate calculation and separate eye/target scaling.
- Dev4's direct retail package, route-runtime, DAT-coupling, Stage Explorer, Asset Viewer, and source-only gates remain inherited from the frozen dev4 checkpoint.

## Remaining boundaries

- Exact semantic identity of word 11's model/material virtual setter remains unresolved.
- Combined route orientation, route position, camera preset/animation state, and field-model animation are not yet one executable-faithful playback model.
- Complete authoritative route↔DAT activation/pairing remains unresolved.
- RSX/Xenos shader instruction-level analysis remains future work.
- Original toolkit code still requires an owner-selected publication license.
