# VERTEBRATE phase correction — v2.10.0-dev23 WIP

## Scope

This note corrects the current toolkit interpretation without rewriting the sealed dev13 research record. The persistent structural ownership recovered in dev13 remains valid: VERTEBRATE allocates exactly two AA `bos_017.gmx` endcaps plus thirty DB `bos_017a.gmx` pillars. `bos_017b..j.gmx` remain separate attack auxiliaries.

## Retail Xbox executable evidence

### Construction / phase-1 base transforms

`Function_82134228` allocates the two AA roots and thirty DB pillar records. `Function_82133AE8` initializes their persistent phase-1 transform records:

- AA runtime slot 0: logical index 20, `Y=1448`, native/base orientation.
- AA runtime slot 1: logical index -9, `Y=-608`, with a native/base Z=180° rotation.
- DB runtime slots 2..31: logical indices -9..20 at `Y = logical_index * 70`.

`Function_82133120` identifies runtime slot 11 as the zero-height pillar. During major state 1, `Function_821319B8` advances structural-record runtime Y rotation at exactly 0.5° per update, alternating direction by logical-index parity. This yields:

- lower AA slot 1 / logical -9: +0.5° per tick;
- upper AA slot 0 / logical 20: -0.5° per tick;
- the thirty DB pillars alternate +0.5° / -0.5° per tick from pillar 0 onward.

The authored runtime cadence is 30 Hz, so the common full-turn loop is 720 ticks = 24 seconds. Dev23 exports this as one 32-channel glTF action named `VERTEBRATE phase-1 alternating piece rotation`.

### Phase-2 transition correction

The old dev13/dev22 static phase-2 preset preserved the runtime-record Z result but missed a direct model/base transform.

`Function_821322A0` performs the transition. At collapse start it clears the runtime-record rotations **and applies `FUN_82469670(pi/4)` directly to AA slot 0's model/base matrix**. `FUN_82469670` reaches the engine Y-axis matrix rotation path, so this is a native/base **+45° Y** transform.

The function then removes/shrinks all thirty DB pillars over 120 frames and rebases both AA records to the boss-local origin. In the following transition interval it ramps both AA runtime-record Z rotations from 0° to `DAT_82543624`; the retail constant is `0x3FC90FDB` = π/2 = **+90°**, over another 120 frames.

AA slot 1 retains the native/base Z=180° flip established earlier. `Function_8214B798` proves the draw path composes the model/base matrix before the runtime record matrix (`Base × Runtime` in SIIG row-matrix convention). Therefore the corrected static end state is:

- AA slot 0: `BaseY(+45°) × RuntimeZ(+90°)`.
- AA slot 1: `BaseZ(180°) × RuntimeZ(+90°)`.

The historical shorthand “effective Z 90° / 270°” is therefore incomplete for slot 0. It discarded the +45° Y component and caused the visibly misaligned dev22 phase-2 inspection assembly.

## Fresh retail validation

Using freshly extracted Xbox 360 retail GMXs:

- `vertebrate_phase1_tower`: 32 GMX instances, 64 meshes, 128 nodes, plus one 32-channel runtime-spin action.
- `vertebrate_phase2_endcaps`: 2 GMX instances, 4 meshes, 8 nodes. Slot 0 exports the mixed +45°Y/+90°Z matrix; slot 1 exports the 180° base-Z + 90° runtime-Z counterpart.

No proprietary GMX or executable data is bundled with the source-only toolkit.

## Deliberate boundary

Another retail controller path can drive a slot-0 full-turn Z behavior in a later timeline-driven state. Dev23 does not fabricate that as a universal phase-2 loop until the exact state/segment timing is completely bounded. The exported phase-1 spin and corrected phase-2 static end state are the portions currently promoted to the user-facing Workbench.
