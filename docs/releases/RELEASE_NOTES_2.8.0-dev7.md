# SIIG Asset Toolkit 2.8.0-dev7 release notes

Dev7 corrects the runtime timing model for GMX matrix animation and adds explicit animated-camera and animated-field analysis paths. The activation schedule remains caller-controlled; the toolkit does not infer when a stage switches into these modes.

## Runtime matrix-animation clock

Retail PS3 functions `_00380998`/`_003809C0`, `_003804A4`, and `_00380A60` show that channel-type-12 ANIM tracks are sampled by direct matrix index: `logical_frame % frame_count`. The float table stored before the matrices is not consulted by this runtime path.

- `gmxtrack` exports both 30 Hz runtime time and the untouched raw authoring-time value.
- glTF animation input keys now use `sample_index / 30.0`.
- Raw authoring-time extent and MOTN duration remain in metadata for auditability.

This fixes the previous ~30/24 playback stretch caused by treating the raw approximately-24-Hz-looking floats as runtime seconds.

## Animated camera

New `camera-animation` evaluates an explicitly supplied `cam01_op1.gmx` or `cam02_op1.gmx` using the retail controller semantics:

- descriptor `cam`, start 0, end 200, non-loop;
- current logical frame = `trunc(frame_accumulator)`;
- accumulator advances by `1 / frame_multiplier`;
- `cam1` translation is camera eye and `int1` translation is camera target;
- current `FieldPos` is added to both;
- animated mode exits at frame 200.

At frame multiplier 2 this produces 400 runtime updates sampling `0,0,1,1,...,199,199`. `cam02_op1` stores 300 matrices per track, but this controller path never reaches samples 200..299.

## Animated field models

New `field-animation` exports the executable descriptor frame domain for an explicitly supplied field GMX:

- `fld015`: start 0, end 6300, non-loop, 6,301 matrices.
- `fld014`: start 0, end 1440, loop, 1,440 matrices; descriptor frame 1440 modulo-wraps to sample 0.

The field route controller can be externally frame-driven, so this command deliberately evaluates descriptor frames without inventing a stage activation schedule.

## Validation

- 34/34 dependency-free self-tests pass.
- Real `cam01_op1` and `cam02_op1` each complete the explicit camera-controller gate with 200 distinct logical frames.
- Real `fld014` and `fld015` hit the expected descriptor endpoints/sample indices.
- Real glTF exports report runtime spans of 6.667 s (cam01 stored 200 samples), 10.0 s (cam02 stored 300 samples), 48.0 s (fld014), and 210.033 s (fld015), while retaining the original raw authoring-time extents separately.

## Remaining boundaries

- Exact DAT/opcode activation for animated camera and field modes is not yet mapped globally.
- `cam02` samples 200..299 may be used by another path; dev7 only proves they are unreachable through the traced `cam` controller.
- Field-model frame drivers are only partially mapped; no automatic stage timeline is claimed.
- Runtime fog-profile selection and camera preset word 11 remain unresolved.
- Instruction-level RSX/Xenos shader analysis remains future work.
- Original toolkit code still requires an owner-selected publication license.
