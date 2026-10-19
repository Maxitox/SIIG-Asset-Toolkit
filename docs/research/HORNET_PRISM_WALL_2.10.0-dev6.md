# HORNET prism-wall runtime variants — 2.10.0-dev6

## Result

The later HORNET C0 prism-wall phase is now recovered as an exact **13-variant runtime family**, not one canonical static arrangement.

The phase uses 45 motion records laid out as a 5×9 grid:

- `X = (index mod 9) * 46 + 29.5`
- `Y = 0`
- `Z = (index div 9) * 46 + 28`
- indices run from 0 through 44.

At phase entry the game randomly chooses one of exactly 13 grid records for A1 itself:

`0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44`.

The selected subordinate object is hidden, A1 copies that record and moves into the selected cell, and the remaining 44 records display their parallel C0 prism objects. The settled visible formation is therefore **1×A1 + 44×C0**, never 45 C0 plus an extra root.

There is deliberately no unqualified `hornet_prism_wall` catalog preset. The built-in variants are named `hornet_prism_wall_00`, `..._02`, through `..._44` using only the runtime-valid slots above. Choosing one explicitly represents one possible random retail outcome without pretending it is uniquely canonical.

A1 does **not** receive `pose_sample` in these presets. Its native `bos_008.gmx` `0→20` loop remains active during the prism-wall state, so freezing an arbitrary internal sample would add evidence the executable does not provide. C0 instances are static at the recovered outer grid transforms.

## Allowed A1 cells

| slot | row | column | X | Y | Z |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 29.5 | 0 | 28 |
| 2 | 0 | 2 | 121.5 | 0 | 28 |
| 6 | 0 | 6 | 305.5 | 0 | 28 |
| 8 | 0 | 8 | 397.5 | 0 | 28 |
| 18 | 2 | 0 | 29.5 | 0 | 120 |
| 20 | 2 | 2 | 121.5 | 0 | 120 |
| 22 | 2 | 4 | 213.5 | 0 | 120 |
| 24 | 2 | 6 | 305.5 | 0 | 120 |
| 26 | 2 | 8 | 397.5 | 0 | 120 |
| 36 | 4 | 0 | 29.5 | 0 | 212 |
| 38 | 4 | 2 | 121.5 | 0 | 212 |
| 42 | 4 | 6 | 305.5 | 0 | 212 |
| 44 | 4 | 8 | 397.5 | 0 | 212 |

## June 10 Xbox evidence

Retained June Ghidra export SHA-256: `987cf607e4164dde06b980718a6169791d81e064d4b5e46ecb35f45176076f66`.

Key anchors:

- `0x82136178` — prism-wall phase. Substate 0 selects one of 13 entries with a random range of 13; substate 1 sends all 45 records toward the wall and substitutes A1 into the selected record; the settled substate waits about 30 authored ticks before transition.
- `0x82135958` — exact 45-cell target helper: spacing `46.0`, X origin `29.5`, Z origin `28.0`.
- `0x82010678` — exact 13-entry selected-root table.
- `0x82135C70` — subordinate display/update path; record states 3/4 enable the parallel C0 object and disable the normal BF part.
- `0x82136A48` — subordinate hide path used for the selected A1 cell, so the C0 child for that cell is not simultaneously visible.
- `0x82138568` — high-level HORNET state dispatcher.

The common HORNET reset zeroes the relevant outer rotation fields; the prism-wall state also assigns zero angle. Settled A1/C0 outer transforms therefore use identity rotation and unit scale.

## Retail Xbox cross-check

Retained retail Ghidra export SHA-256: `444ea2b9cf85f201cd160f935ea890bc473b6d541cb9d8cecb849ae462c53499`.

Retail `0x8211C1C8` is the stripped counterpart of the June prism-wall state and repeats the 45-record logic. The target helper retains the same `46.0 / 29.5 / 28.0` constants, and `DAT_8200A094` contains the same exact 13 slots ending in 44.

## Retail PS3 cross-check

Retained PS3 Ghidra export SHA-256: `e7af0cd5940268c4697470ca58d55010b45a50706dfc10ead552d4ee4ce55d6d`.

PS3 `_opd_FUN_001b1fd0` reproduces the same prism-wall state; `_opd_FUN_001b1f00` reproduces the 45-cell target helper; `DAT_004bafb0` contains the same 13 selected-root indices. The PS3 path explicitly copies the chosen motion record into the A1 root and hides the corresponding subordinate child while showing C0 for the other records.

## Real-retail assembly validation

Outside the source-only package, `hornet_prism_wall_22` was exported against the retained retail GMXs:

- 45 visible GMX instances;
- 90 meshes;
- 180 nodes;
- A1 at slot 22 = `(213.5, 0, 120)`;
- 44 C0 instances fill every other wall cell;
- A1 source SHA-256 `0d73ffe9744fdd635c6480836734576f715b3037d2aa90737682912ab88cd516`;
- C0 source SHA-256 `e4be18e2da142cc65504456c16d5464cb9064636a621c78d57878f144b8b47e5`;
- A1 native animations remain in the assembled glTF.

Proprietary validation inputs and generated real-asset output are not bundled.

## State-6 boundary

HORNET's following state uses a separate 45-record neighborhood/propagation mechanism. It is **not** the same formation and is not represented by these prism-wall variants. That later attack remains a separate research target.
