# Console enemy / sub-boss GMX assembly research — dev23

Status: **development evidence note**. This document records what the dev23 GMX Workbench may export without turning runtime-controlled visuals into invented static poses.

## Naming provenance

The display names **ENVY**, **KEEPER**, **OPPRESSOR**, **GLUTTONY**, **VANITY**, and **TELEPORTER** are project-owner identifications supplied during dev23 review. The retained retail Xbox string table does not currently provide matching internal name strings for these six model families, so the toolkit keeps their model/runtime IDs as the primary machine identity. In particular, `emy_045` is displayed as ENVY because the supplied gameplay reference and the recovered controller behavior match the described zig-zag growth/fly-away enemy; this is not represented as an internally recovered name.

## ENVY — `emy_045.gmx`, runtime `0x98`

Primary retail controller: `Function_82102898` / vtable `PTR_Function_82102A10_82008288`.

Recovered behavior:

- `FUN_82101810` computes the member-facing angle from the configured cardinal heading and alternates **-π/6 / +π/6 (-30° / +30°)** by member parity.
- `Function_82102480` grows the active chain one member at a time until the encounter-configured member count is reached.
- `Function_82102058` derives each active member's chain offset from **member_index × 10.0** and reapplies the alternating orientation.
- `Function_82101E20` transitions a member out of the growth state after its delay, builds a flight controller from the member's current position/angle, updates that flight path against live world/player state, and removes the member once it leaves the active play region.
- `Function_82102510` switches the controller between the chain-growth update and fly-away update paths.

Dev23 export boundary:

- `envy_zigzag_preview_06` is a **six-member gameplay-reference preview**, not a universal fixed encounter pose.
- The alternating ±30° relative facing and 10-unit per-index spacing are executable-backed.
- Six members and canonical +Z base growth direction are preview choices because member count/cardinal heading are encounter parameters.
- The user-supplied screenshot is used as a visual acceptance reference but is **not bundled** in the source-only toolkit.

Animation caution: `enemy.anm` defines `emy_045` range 0..60 looped, while each retained GMX matrix track has 31 matrices. The exact out-of-range model-sampler behavior remains unresolved; dev23 must not fabricate modulo sampling merely to make a glTF clip fit.

## KEEPER — `emy_032.gmx`, helper `emy_032a.gmx`

Primary retail setup/update: `Function_821052B0`, `Function_82105340`.

Exact static hierarchy recovered:

- one `0x2B / emy_032.gmx` root,
- eight `0xAC / emy_032a.gmx` helpers,
- helper indices 1..8 attach to root locators `lt_001..lt_008`,
- odd helper indices receive a **180° local Y rotation** (`FUN_8214b6e8(0,180,0,...)`).

Dev23 catalog: `keeper_complete`. This is suitable for a canonical multipart assembly because membership, attachment order and local parity rotation are all recovered.

## OPPRESSOR — `emy_043.gmx`, helpers `emy_043a/b/c.gmx`

Primary retail setup/update: `Function_821088A0`, `Function_82108A10`, `Function_821087D0`.

Exact allocation and attachment order:

- one `0x2C / emy_043.gmx` root,
- one `0xAD / emy_043a.gmx`,
- two `0xAE / emy_043b.gmx`,
- eight `0xAF / emy_043c.gmx`,
- the eleven helper records map in that allocation order to `lt_001..lt_011`.

Dev23 catalog: `oppressor_complete`. The root's live world transform remains gameplay-controlled, but the internal multipart hierarchy is recovered.

## GLUTTONY — `emy_050.gmx`, helper `emy_050a.gmx`

Primary retail setup/update: `Function_82102F68`, `Function_82103A88`, `Function_821034D0`.

Recovered hierarchy:

- one `0x9C / emy_050.gmx` root,
- two `0xB0 / emy_050a.gmx` helpers,
- helpers bind through root locators `lt_001` and `lt_002`.

`Function_821034D0` changes helper yaw relative to live target/world state. Therefore `gluttony_complete` preserves the exact locator hierarchy but does **not** bake one arbitrary gameplay yaw as canonical.

## VANITY — `sbs_002.gmx`, helper `sbs_002a.gmx`

Primary retail setup/update: `Function_8210C9C8`, `Function_8210CAB8`.

Recovered ownership:

- primary `sbs_002` visual,
- a second root-derived `sbs_002` visual,
- one `0xB1 / sbs_002a` helper,
- all three are registered by the same controller.

`Function_8210CAB8` applies state-dependent visibility, position and scaling using live encounter state. Current evidence does not justify one fixed relative layout. Dev23 therefore exposes `vanity_owned_visual_set` as an **inspection-only owned set at identity**, clearly labelled non-canonical.

## TELEPORTER — `sbs_003.gmx`, helpers `sbs_003a..i.gmx`

Primary retail setup/update: `Function_8210B760`, `Function_8210B888`.

Exact helper allocation order is recovered from `DAT_8200902c = 0xE7..0xEF`:

1. `0xE7 sbs_003a` = `tel09`
2. `0xE8 sbs_003b` = `tel08`
3. `0xE9 sbs_003c` = `tel07`
4. `0xEA sbs_003d` = `tel06`
5. `0xEB sbs_003e` = `tel05`
6. `0xEC sbs_003f` = `tel04`
7. `0xED sbs_003g` = `tel03`
8. `0xEE sbs_003h` = `tel02`
9. `0xEF sbs_003i` = `tel01`

The controller also owns additional root-related `sbs_003` visuals. `Function_8210B888` proves the nine helpers are dynamically positioned/scaled/hidden according to encounter state and stage data; several branches depend on values in the live controller's `+0x10C` state table. Until those parameter semantics are fully reconstructed, `teleporter_owned_visual_set` intentionally exports the exact model order as an inspection set rather than inventing a canonical spatial pose.

## GMX Visual Pass rule (dev23 feedback correction)

`Solid`, `Outline`, and `Combined` are **pair controls**. They only alter a GMX when both a solid/face pass and an outline/edge pass are detected. A single-pass model ignores the global selection and exports normally. Metadata records both the requested mode and whether the pass selector was applicable.

## Promotion rule

A dev23 inspection-only entity may be promoted to a named gameplay pose only after the relevant controller branch supplies enough evidence to reproduce all required relative positions, rotations, scales, visibility choices, and state/parameter conditions. Ownership alone is not treated as placement evidence.
