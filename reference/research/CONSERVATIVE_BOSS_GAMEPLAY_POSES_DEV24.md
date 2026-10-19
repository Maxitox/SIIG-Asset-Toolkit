# Conservative boss gameplay-pose promotions — dev24

## Scope

This pass revisits the four boss families that still lacked a gameplay-space canonical Workbench pose after the dev22 controller audit: THE MOON, OCTOPUS, WATER STRIDER, and NAMELESS / internal `NO_NAME`.

The promotion rule is intentionally conservative. A family is promoted only when retail DAT arguments and the executable prove the root transform or movement directly. A gameplay-pose reconstruction is **not** treated as a deep multipart/runtime reconstruction, and no adjacent registered GMX is added without a controller ownership/attachment path.

## Coverage result

The 18-family Boss Workbench now has three evidence grades:

- **14 deep runtime reconstructions** — membership/state/attachment behavior recovered far enough for the existing runtime-backed catalogs.
- **3 gameplay-pose reconstructions** — OCTOPUS, WATER STRIDER, and NO_NAME have exact retail gameplay-space root placement, while deeper multipart/state ownership remains deliberately bounded.
- **1 native-inspection-only family** — THE MOON remains in native GMX-local inspection space because its authored command does not supply a root X/Z transform and its visual state is controller-internal.

This changes the old dev20/dev22 13/5 or 14/4 conservative split without rewriting those historical findings.

## OCTOPUS (`0xA3` / `bos_010.gmx`)

All six recovered retail opcode `0xA3` records contain only the five common fields. Every record authors root X/Z as **213 / 100**. The common entity initializer consumes those fields as the root position.

The OCTOPUS class callback has a nearby one-short boundary read, but no recovered retail or June command authors a sixth value. That read therefore remains outside the semantic/assembly contract rather than being synthesized.

Canonical dev24 Workbench pose:

- model: `bos_010.gmx`
- root transform: **(213, 0, 100)**
- catalog: `octopus_retail_spawn`
- coverage: `gameplay_pose_reconstruction`

Native animation and internal articulation remain inside `bos_010.gmx`; no auxiliary GMX is invented.

## WATER STRIDER (`0xA6` / `bos_014.gmx`)

All four recovered retail opcode `0xA6` records author root X/Z as **213 / 100**. The common initializer consumes those coordinates before the WATER STRIDER controller/attack state machine.

Canonical dev24 Workbench pose:

- model: `bos_014.gmx`
- root transform: **(213, 0, 100)**
- catalog: `water_strider_retail_spawn`
- coverage: `gameplay_pose_reconstruction`

The separate `fld014.gmx` system is intentionally not baked into this body transform. The recovered PA-route evidence shows `fld014` is a separately frame-driven field asset with a `0..1440` descriptor and a 1441-frame repeating route. WATER STRIDER's locator/controller relationship to that stage system does not make the field matrix the boss-root matrix.

## NAMELESS / internal `NO_NAME` (`0xAB` / `bos_018a.gmx`)

Retail main/Bonus records prove a stationary gameplay root:

- `level5_stage6.dat`, command 208, frame 237210: `[0,3000,256,213,120,213,120]`
- `extra5_stage6.dat`, command 292, frame 860201: `[0,3000,256,213,120,213,120]`

The common fields establish start **(213, 0, 120)**. Raw DAT-tail stub `0x8211F1A0` copies the final two shorts as target X/Z, and `Function_8211F370` consumes them. Because start and target are identical in both records, `no_name_retail_main_spawn` is an exact gameplay-root pose rather than a guessed state.

Extra 2-8 provides a real point-to-point action:

- `extra2_stage8.dat`, command 24, frame 954: `[0,100,512,213,-100,213,80]`
- start: **(213, 0, -100)**
- target: **(213, 0, 80)**
- raw speed: `512` => common speed `1`
- normal controller step: **2 units/update**

`Function_8211F370` computes a normalized target vector and moves by `(arg2/512)*60/(frame_multiplier*30)`. Completion is tested against the **pre-update** distance using strict `< step`. The 180-unit Extra 2-8 move is exactly divisible by the 2-unit step, so the root lands on the target after 90 movement updates and repeats the target once on the following completion update. Including the initial sample yields **92 samples**, with the final two translations both `(213,0,80)`.

The glTF action exported by `no_name_extra2_stage8_approach` preserves that quirk instead of shortening the track.

`bos_018.gmx` remains separately registered but unowned by the traced retail NO_NAME controller. It is not stacked into either scene. The discarded May-only `bos_018b/c` assets likewise remain excluded.

## THE MOON (`0x46` / `bos_001.gmx`)

THE MOON remains the sole `native_inspection_only` family.

Recovered retail opcode `0x46` records contain three authored values and no X/Z root coordinate. Runtime+1 visual-controller case `0x47` constructs `Function_8212B638`. Dev24 now resolves its update (`Function_8212B760`) more precisely: it does **not** apply the previously assumed dynamic scale. Slot 0 writes a ten-step 36-degree Z rotation and changes only the fourth/material-alpha components of `collada_edge1`, `collada_face1`, and `collada_face2`; nonzero visual slots write alpha 0.4. State 0 uses edge alpha 0.9 and a face-alpha ramp from 0 to 1 across controller timers 131..262, with a strict-partial resource switch to `+0x1A8` and restore to `+0x1A4` at full opacity. See `THE_MOON_VISUAL_CONTROLLER_DEV24.md`.

The correct Workbench boundary is therefore still `the_moon_native_body`: identity outer matrix, native GMX animation/articulation intact, and no claimed world-origin placement. The controller law is now exactly sampleable through `the-moon-controller`, but a material-animated export still requires mapping the controller visual slots/material vectors to exact exported GMX render nodes/materials. Reaching an arbitrary 18/18 count is not evidence.

## Resulting matrix

| Evidence grade | Families | Count |
| --- | --- | ---: |
| Deep runtime reconstruction | existing deep-runtime families | 14 |
| Gameplay-pose reconstruction | OCTOPUS, WATER STRIDER, NO_NAME | 3 |
| Native inspection only | THE MOON | 1 |

The matrix and GUI expose these grades separately so an exact root placement is useful without being mislabeled as a recovered multipart/state reconstruction.
