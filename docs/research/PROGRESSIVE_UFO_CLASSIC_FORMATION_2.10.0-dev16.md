# PROGRESSIVE UFO classic formation — 2.10.0-dev16

## Scope

This checkpoint adds a second, separately named PROGRESSIVE UFO assembly without changing the original `progressive_ufo` preset introduced in dev3. The human-facing label **classic UFO formation** is project-owner terminology; the membership, transforms and runtime state use below are executable-backed.

## Runtime pose table

Retail Xbox initializes the second five-part pose table in `Function_82536720` at `0x82568180`. Retail state helper `Function_82127018` applies the table as the completed target in major states **5** and **8**. June 10 independently initializes the same table in `Function_82562710` at `0x825D95B0` and its corresponding helper `Function_82141B38`. Retail PS3 independently initializes the same records in `_opd_FUN_001c51e8` at `DAT_0054b610..DAT_0054b67c` and applies them through `_opd_FUN_001c064c`.

The five parts are the existing runtime membership `A2,C2,C2,C3,C3`:

| Part | Model | Position XYZ | Runtime Euler XYZ (radians) |
|---|---|---:|---:|
| 0 | `bos_009.gmx` | `(0,0,0)` | `(3.1415927410,0,0)` |
| 1 | `bos_009a.gmx` | `(-78.5,0,5)` | `(0.0610865243,0,1.4049900770)` |
| 2 | `bos_009a.gmx` | `(78.5,0,5)` | `(0.0610865243,0,-1.3962634802)` |
| 3 | `bos_009b.gmx` | `(115,0,3)` | `(0,0,1.7453292608)` |
| 4 | `bos_009b.gmx` | `(-115,0,3)` | `(0,0,-1.7453292608)` |

## Matrix convention

The runtime Euler setter negates Y and the model path composes row-vector transforms as `Rz * Rx * Ry * T`. The toolkit reproduces that order exactly and emits the numerically equivalent glTF column-major local-to-assembly matrix. No screenshot-derived orientation correction is applied.

## Compatibility boundary

`progressive_ufo` remains the original first formation exactly as shipped in earlier releases. Dev16 adds `progressive_ufo_classic` as a separate catalog key. Another later pose table participates in dynamic/randomized attack behavior and is deliberately **not** mislabeled as a canonical classic formation.

## Fresh retail validation

Fresh export from the retained retail Xbox `bos_009.gmx`, `bos_009a.gmx`, and `bos_009b.gmx` succeeds as **5 instances / 10 meshes / 20 nodes / 10 preserved native animations**. Combined bounds are approximately `X -144.2833..144.2833`, `Y -40.2699..40.2327`, `Z -60.6128..58.2041`. The release remains source-only; no proprietary GMX or generated retail glTF is bundled.
