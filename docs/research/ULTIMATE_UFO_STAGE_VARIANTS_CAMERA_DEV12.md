# Ultimate UFO stage variants and late camera — dev12

Dev12 separates the normal 5-3 Ultimate UFO fight from DLC Bonus 5-6 instead of treating the two retail DAT occurrences as equivalent.

## Normal 5-3 versus Bonus 5-6

`level5_stage3.dat` is the normal full encounter. `extra5_stage6.dat` is the DLC Bonus 5-6 stage that presents the stage-5 bosses in sequence. The gameplay-order description comes from project-owner observation; the distinct destruction policy below is directly executable-backed.

### Normal 5-3

- `ULTIMATE_UFO`: authored DAT frame 781.
- following `3D Camera Change 01 [4,0]`: frame 912 (delta 131 authored ticks).
- no Extra-5 `(5,6)` fast-destroy branch is selected.
- normal late route remains available: state 10 -> state 11 airlock sequence -> later destruction/final phases.

### Bonus 5-6

- `ULTIMATE_UFO`: authored DAT frame 33749.
- following `3D Camera Change 01 [4,0]`: frame 34779 (delta 1030 authored ticks).
- retail Xbox `0x8212DCB0` and PS3 `0x001D3380` contain the same special selector: stage category 5, state `+0x218 == 5`, state `+0x21C == 6`.
- when part 1/core enters a nonzero destruction state, the branch mirrors that state immediately to part 0, invokes part-0 destruction, and clears pending byte `+0x1EE`.

This is a real executable fast-destruction policy for Bonus 5-6 and matches the observed need to abbreviate the UFO cleanup before the following boss. It should not be generalized to normal 5-3.

The full Bonus 5-6 stage is a gameplay boss rush, but the DAT's explicit `BOSS_RUSH` / `BOSS_RUSH_END` opcodes only bracket portions of its script. Dev12 therefore does not use the opcode flag as a synonym for the stage's overall gameplay identity.

## Mframe directly drives fld015

Ultimate UFO's Mframe is written to the active field animation frame in every analyzed build:

| Build | MoveMain | Route-frame setter |
|---|---|---|
| May 9 | `0x82142008` | `0x820FCA08` |
| May 11 | `0x821431D0` | `0x820FCC30` |
| June 10 | `0x82149DF8` | `0x820FDD68` |
| Xbox retail | `0x8212EC50` | `0x820EAED8` |
| PS3 retail | `0x001D2988` | `0x0015A2DC` |

The active Ultimate UFO field model is `fld015.gmx`, descriptor 0..6300 non-loop. The supplied retail asset contains 6,301 logical matrices, so boss Mframe and field-animation frame are directly synchronized.

Important late anchors are therefore literal field samples: 5897 core hold, 5898 destruction bridge, 5902 airlock start, retail 6030 destruction/explosion phase, 6200 final phase, and terminal sample 6300.

## PA camera lifecycle

Retail PS3 gives the cleanest camera lifecycle:

1. `0x001580DC` successfully invokes `Route::SetPaRoute` and sets animated-camera flag `+0x108`.
2. While the flag is set, `0x00157A10 -> 0x0015B094` samples `cam1`/`int1` from `cam01_op1.gmx` and adds current FieldPos.
3. `0x00157A10 -> 0x0015B1C8` advances the animation and clears the flag when it reaches the controller end.
4. `0x0015ABCC -> 0x00159D58` continuously samples the field GMX matrix. Translation is extracted into FieldPos and then zeroed from the matrix, leaving orientation.
5. After the animated flag clears, `0x00157A10` resumes the normal procedural camera, transforming the current preset through that field orientation and FieldPos.

`cam01_op1.gmx` is therefore a temporary introductory camera, not the camera resource for the entire 6300-frame boss route.

## Preset 4 is not an HP-zero switch

The stage-script clock trace rejects the earlier hypothesis that the post-UFO preset-4 command is delayed until destruction. The explicit script-clock stall applies to active `BOSS_RUSH` state; neither retail UFO spawn is waiting under that condition until HP zero. Preset 4 is part of ordinary encounter setup/progression.

For normal 5-3, preset 4 is nevertheless the last authored DAT preset before the long Ultimate UFO route. The UFO's MoveMain contains no late stage-camera preset setter. A non-DAT external preset write has not been exhaustively ruled out, so dev12 calls the late preset identity strong rather than absolute.

## Late rear-follow geometry

Preset 4 has local procedural eye offset `(0,40,60)`. From Mframe 5897 through 6300, real `fld015.gmx` is at a stable +90-degree X orientation. The runtime row-vector transform therefore maps the preset eye offset to:

`(0,-60,+40)` relative to FieldPos.

During the same interval, `fld015` travels strongly in +Y. Examples:

| Mframe | FieldPos Y/Z | Base eye Y/Z |
|---:|---:|---:|
| 5902 | 97.412 / 31.983 | 37.412 / 71.983 |
| 6030 | 196.291 / -14.158 | 136.291 / 25.842 |
| 6200 | 606.117 / -16.442 | 546.117 / 23.558 |
| 6300 | 950.808 / -18.754 | 890.808 / 21.246 |

The procedural eye is therefore approximately 60 route units behind the target and 40 units above it during the late escape. Preset 4's dynamic response only introduces local-X displacement; with this +90-degree-X route orientation it remains a lateral X adjustment and does not change the rear/above relationship.

Dev12 classifies this as **rear-follow geometry** with `strong_executable_asset_chain` confidence. This is substantially stronger than a visual guess, but it is deliberately not worded as an exhaustive proof of every rendered camera input.

## Remaining camera work

- Exhaustively search non-DAT camera-preset writers reachable during Ultimate UFO to either close or preserve the preset-4 caveat.
- Recover a proven retail activation callsite for `cam02_op1.gmx`, if one exists.
- Runtime fog-profile switching and camera preset word 11 remain separate unresolved topics.

## Direct preset-writer audit

Retail PS3 preset setter `0x0015B524` has five direct callers in the complete decompiled export: the DAT camera-change handler (`0x0014F604`), three stage camera initialization/refresh paths (`0x00160E10`, `0x00161380`, `0x00161BD8`), and one boss-specific `SetCameraPreset(0,120)` path at `0x001D8690`. The latter is structurally equivalent to June `0x8214D698`, whose prototype debug xrefs place it in `Vertebrate.cpp`.

No direct caller is in Ultimate UFO. This tightens the normal-5-3 preset-4 conclusion: there is no direct static `SetCameraPreset` call from Ultimate UFO that replaces it during the late route. Dev12 still reserves a narrow caveat for indirect/function-pointer or otherwise unresolved external writes.


## Dev13 continuation

Dev13 converts this strong late-camera result into a full frame-by-frame `field-camera` reconstruction. All 404 real `fld015` samples from Mframe 5897 through 6300 classify as rear-follow, and the GMX serialized-matrix → runtime row-matrix representation bridge is modeled explicitly. See `ULTIMATE_UFO_CAMERA_RECONSTRUCTION_DEV13.md`.
