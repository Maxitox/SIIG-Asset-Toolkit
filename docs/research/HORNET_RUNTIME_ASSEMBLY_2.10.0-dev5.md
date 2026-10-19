# HORNET runtime assembly — 2.10.0-dev5

## Result

HORNET is not one native GMX and is not a small fixed child set. The recovered runtime architecture is:

| runtime | model | runtime count | role |
|---|---|---:|---|
| `0xA1` | `bos_008.gmx` | 1 | visible core/root |
| `0xBF` | `bos_008a.gmx` | 125 | armor-cube pool |
| `0xC0` | `bos_008b.gmx` | 125 | parallel prism/weapon pool |
| `0xC1` | `bos_008c.gmx` | 1 | invisible formation/animation rig |

The dev5 built-in preset `hornet_full_armor` represents the deterministic **fully revealed armor state after the entrance formation opens**. It exports exactly **126 visible instances**: A1 plus 125 BF armor cubes. The meshless C1 controller is not added as visual clutter, and the C0 pool is intentionally omitted because it is dormant in this state.

The 125 BF translations are the exact Cartesian product

`{-31.68000030517578, -15.84000015258789, 0, 15.84000015258789, 31.68000030517578}^3`.

Every BF instance has identity rotation and unit scale in this static formation. A1 is baked at native animation sample 0.

## `bos_008c.gmx` is a real animation-only rig

Older observational material left C1 unresolved because the normal mesh-oriented glTF preview contains no visible surface. Dev5 resolves that ambiguity:

- retail `bos_008c.gmx` has 128 BONE records, zero MESH records, and 126 MOTN/ANIM tracks;
- the tracks target `c_001` through `c_125` plus `lt_001`;
- all `c_001..c_125` tracks have 126 samples;
- sample 0 places the 125 formation nodes at the complete 5×5×5 lattice above with identity rotation and unit scale;
- after sample 0, the cube-node scale collapses during the entrance controller sequence;
- `enemy.anm` defines `bos_008c` as one non-looping `0→125` segment.

Therefore C1 is an intentional runtime transform controller, not a corrupt or invalid model.

## June 10 Xbox evidence

The retained June Ghidra export has SHA-256 `987cf607e4164dde06b980718a6169791d81e064d4b5e46ecb35f45176076f66`. The class retains the original source spelling `Honet.cpp`.

Key anchors:

- `0x82137AE0`: part construction. It resolves BF (`0xBF`), C1 (`0xC1`) and C0 (`0xC0`), creates **125 BF + 125 C0** objects in parallel pools, then creates one C1 rig.
- `0x821379C0`: one-time setup/reset path; invokes the state reset and formation update.
- `0x82137628`: common state reset for the 125 records and A1/C1 animation state.
- `0x82136AA8`: multipart placement/update. In record state 0 it obtains transforms from the C1 `c_001..c_125` locator table; states 1/2 render the BF object, while states 3/4 use the corresponding C0 object from the parallel pool.
- `0x82136ED8`: entrance state. The formation rig is driven from the end of its `0→125` clip toward sample 0, producing the fully revealed lattice at the end of the entrance.
- `0x82136178`: later prism attack phase; exactly 45 records transition into the C0-backed state.
- `0x82135958`: the 45-slot C0 target-grid helper, with X=`(index mod 9)*46 + 29.5`, Y=`0`, Z=`(index div 9)*46 + 28`.
- `0x82138568`: high-level HORNET state dispatcher.

The source string `c_001` is referenced by the runtime placement family and the executable pointer table beginning at `0x82573F58`.

## Retail Xbox cross-check

The retained retail Xbox Ghidra export has SHA-256 `444ea2b9cf85f201cd160f935ea890bc473b6d541cb9d8cecb849ae462c53499`.

The stripped retail constructor at `0x8211DAB0` repeats the BF/C1/C0 lookup and exact 125-object dual-pool loop. Retail placement code retains the `c_001..c_125` formation-node lookup and the state-dependent BF-versus-C0 object selection. This independently confirms that the June architecture was retained for retail.

The retail model hashes used for the external real-asset export are:

- `bos_008.gmx`: `0d73ffe9744fdd635c6480836734576f715b3037d2aa90737682912ab88cd516`
- `bos_008a.gmx`: `7d9d44813cd5327c91218e477e8be8e8d71915425d4067b01729078d37edfd55`
- `bos_008b.gmx`: `e4be18e2da142cc65504456c16d5464cb9064636a621c78d57878f144b8b47e5`
- `bos_008c.gmx`: `7e0601f6048a38ce49fe4a6ebc6319619ae99037ba3c0bf93ba643ac03041ad1`

June and retail `enemy.anm` are byte-identical in the retained corpus, SHA-256 `c3100a85d279af220e3f2b1f8b51650acf2e3c536ecac1f918d5174f88570cb4`.

## Retail PS3 cross-check

The retained PS3 Ghidra export has SHA-256 `e7af0cd5940268c4697470ca58d55010b45a50706dfc10ead552d4ee4ce55d6d`.

PS3 `_opd_FUN_001b33dc` independently constructs the same 125 BF objects, 125 C0 parallel objects and one C1 rig. `c_001` is present at `0x004BABC8`, the locator pointer table begins at `0x005348B8`, and `_opd_FUN_001afa08` reproduces the state-dependent C1-locator attachment plus BF/C0 object selection. The PS3 C0 attack-phase family also repeats the 45-record transition and the 46 / 29.5 / 28 grid constants.

## Real-retail assembly validation

The dev5 catalog was also run against the actual retained retail A1/BF GMXs outside the source release. The export produced:

- 126 GMX instances;
- 252 meshes;
- 504 nodes;
- A1 source hash matching the value above, baked at pose sample 0;
- all 125 BF roots at the recovered lattice positions;
- overall visible bounds approximately `(-39.44554,-39.44554,-39.44554)` to `(39.44554,39.44554,39.44554)`.

These proprietary validation inputs and outputs are not bundled.

## Evidence boundary

`hornet_full_armor` is one deterministic static state, not a claim that HORNET always uses 125 BF cubes. The C0 pool is real and becomes visible in later attack states, including a separate 45-slot moving prism formation. That phase is deliberately **not** promoted into dev5 because it is dynamic and state-dependent. The meshless C1 controller is also not exported as a visible instance; its sample-0 locator field is represented by the recovered BF matrices instead.
