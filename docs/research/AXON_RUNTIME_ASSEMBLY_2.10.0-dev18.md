# AXON runtime assembly — 2.10.0-dev18

## Result

AXON uses a standalone whole-body model plus a separate subordinate core/petal pool. Dev18 deliberately keeps these runtime representations separate instead of stacking them into an unsupported 18-model composite.

- A5 / `bos_012.gmx`: one standalone animated whole-body representation.
- CA / `bos_012a.gmx`: subordinate record 0, core/weak-spot form.
- CB / `bos_012b.gmx`: subordinate records 1–16, sixteen petal/blade armor pieces.

The subordinate pool contains exactly **17 model records**. The sixteen CB petals are two rings of eight, not an estimated visual count.

## Retail executable evidence

Retail `Function_8210D808` creates A5 separately, then creates CA for subordinate record 0 and CB for every remaining subordinate record. `FUN_8210D930` returns `0x11`, and `Function_82110378` initializes exactly 17 subordinate records.

The angle table begins at retail `DAT_820093F8`: record 0 is 0°, records 1–8 use `0,45,90,135,180,225,270,315`, and records 9–16 use `22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5`. The constructor stores each record angle as the negative of the table value.

`Function_82110378` assigns group 0 to records 1–8 and group 1 to records 9–16. It sets expanded targets to 75 (`0x42960000`) and 220 (`0x435C0000`). Group-0 retraction target is 0; group-1 retraction target is 18.5 (`0x41940000`). The per-group Y offsets consumed by the visual update are -3.0 and -5.5 at retail `DAT_8200943C`.

Retail `Function_8210EF00` evaluates every subordinate record each frame. For a visible CB record, at runtime phase term `p` and stored runtime angle `a` it applies:

- Y rotation: `-90 - a - p` degrees.
- X offset from the CA core: `radius * sin(a + p)`.
- Z offset from the CA core: `radius * cos(a + p)`.
- Y offset from the CA core: the group table value (-3.0 or -5.5).

`axon_expanded_petals` freezes the deterministic stable expanded target at `p = 0`, preserving native SIIG axes and units.

The A5/CA-CB separation is also explicit in runtime control. Retail `Function_8210E280` disables the subordinate records and enables the separately stored A5 model for its whole-body representation. The toolkit therefore does not combine A5 with CA/CB in one default scene.

## June 10 cross-check

The June 10 debug build independently retains the same structure in `Axon.cpp`. `Function_82126878` asserts `param_3 == 0x11`, creates A5, then CA for subordinate slot 0 and CB for slots 1–16. Its data at `0x8200EB88..0x8200EBE7` reproduces the same angle sequence, -3.0/-5.5 Y offsets, 75/220 expanded targets, and 18.5 group-1 retraction target. This is a cross-build confirmation rather than a retail-only inference.

## Catalogs

- `axon_native_body` — standalone A5 / `bos_012.gmx`, preserving all native animation clips.
- `axon_expanded_petals` — CA core plus all sixteen CB petals at the exact stable expanded phase-angle-0 snapshot.
- `axon_exposed_core` — CA core only for weak-spot/core inspection; no guessed placement is added.

## Fresh retail validation

The retained Xbox retail package was freshly extracted with dev18 before validation.

- `bos_012.gmx`: 172,256 bytes; SHA-256 `09931a245a532e33eb1e540f025a43bc6f79c2f4a4545aa4a30c1f237246dbc7`.
- `bos_012a.gmx`: 12,576 bytes; SHA-256 `73b655a542ed12836810b703f9ae3e36254251492da87e868a3df833b15cffa0`.
- `bos_012b.gmx`: 7,568 bytes; SHA-256 `b299396e134105e890c7449618e62380d08b8412077a3b9fa23a2d79ea07e057`.

Fresh combined-glTF exports:

| Catalog | instances | meshes | nodes | animations |
| --- | ---: | ---: | ---: | ---: |
| `axon_native_body` | 1 | 42 | 76 | 32 |
| `axon_expanded_petals` | 17 | 34 | 84 | 0 |
| `axon_exposed_core` | 1 | 2 | 20 | 0 |

The native A5 carries 32 animation clips. CA and CB are static in these retail assets, so the expanded/core exports add no fabricated animation.

## Evidence boundary

The expanded preset is a stable phase-angle-0 runtime snapshot, not a claim that AXON remains frozen there during gameplay. Retraction/expansion timing is dynamic and remains represented as metadata rather than baked into a fake animation. No proprietary GMX, executable, Ghidra export, or generated retail glTF is bundled in the release.
