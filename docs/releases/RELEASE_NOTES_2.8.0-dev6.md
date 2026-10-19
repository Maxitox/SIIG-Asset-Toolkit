# SIIG Asset Toolkit 2.8.0-dev6 release notes

Dev6 connects the executable-backed route runtime from dev4/dev5 to the proven procedural camera semantics from dev5. It still does **not** infer camera-preset activation, route-object creation time, animated-camera mode, or field-model animation.

## Procedural route orientation

- `RouteRuntimeState` now tracks pitch, yaw, roll, additive rotation offsets, previous FieldPos, pitch-lock state, and the row-vector 3×3 route orientation matrix.
- Moving samples produced by Hermite segments update orientation before any next segment is prepared on that same runtime update. The Hermite `t=0` sample repeats the existing FieldPos and therefore produces no orientation update.
- Retail composition is reproduced as `Rz(roll+offsetZ) × Rx(pitch+offsetX) × Ry(yaw+offsetY)`.
- The procedural path updates yaw from `atan2(-ΔZ, ΔX) - π/2` when ΔX is nonzero and pitch from `atan2(ΔY, -ΔZ)` when ΔZ is nonzero and pitch lock is clear.

## Camera world state

- Added `camera_world_state()` for the normal procedural camera path.
- Camera eye begins at `FieldPos + transform(camera_eye_offset, route_orientation)`.
- Camera target begins at `FieldPos`.
- The proven word-8/9/10 dynamic local-X response is scaled by the uniform scene/view scale, transformed by the same active orientation matrix, and added separately to eye and target.
- FOV, scale, scene/view translation, three fog profiles, and the unresolved word-11 scalar remain exposed in the report.

## Combined playback

- Added `route-camera-playback <stage3d> <dat> --preset N --runtime-x X --runtime-y Y`.
- Route/DAT pairing, route start frame, preset index, and runtime coordinates remain explicit caller inputs.
- `--emit-every N` decimates written CSV rows while every runtime update is still simulated.
- Animated `cam1`/`int1` camera mode and `fld014`/`fld015` orientation mode remain outside this command.

## Validation

- 31/31 dependency-free self-tests pass.
- At deterministic 100-unit analysis spacing, six real retail route files exercise procedural Hermite orientation for 356 orientation updates total.
- Explicit validation input `Xmap3_1.bin + level3_stage1.dat`, camera preset 0, runtime coordinates `(213,233)`, frame multiplier 2:
  - 265,020 runtime updates simulated;
  - seven SCROLL_02 changes applied;
  - normal route completion;
  - `--emit-every 60` produces 4,418 written camera rows without changing simulation state.
- Preset 0 and `(213,233)` are deterministic validation inputs only; this is not a claim that they are the stage's authentic activation state.

## Remaining boundaries

- Authoritative route/DAT object-instantiation and camera-preset activation timing remain unresolved.
- Animated field-model orientation and animated `cam1`/`int1` camera playback are not yet integrated.
- Fog-profile selection over time remains unresolved.
- Camera word 11 remains an unresolved shared model/material scalar.
- Instruction-level RSX/Xenos shader analysis remains future work.
- Original toolkit code still requires an owner-selected publication license.
