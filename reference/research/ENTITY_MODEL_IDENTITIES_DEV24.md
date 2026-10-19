# Player / enemy / sub-boss / boss model identities — dev24 WIP182 update

## Scope and provenance

This reference promotes the project owner's complete model-identification pass into a machine-readable toolkit table without pretending those friendly names were recovered from executable strings. The source table is `reference/tables/ENTITY_MODEL_IDENTITIES_DEV24.csv`.

The table contains **82 identity patterns**:

- 10 player patterns;
- 36 enemy patterns;
- 7 sub-boss patterns;
- 18 boss patterns;
- 11 `est_*` effect/projectile patterns.

Of those, **71** are project-owner-confirmed player/entity identities, **5** are project-owner-confirmed effect usages (`est_012`, `est_013`, `est_015`, `est_020`, `est_021`), and **6** remain explicitly speculative `est_*` effect hypotheses. Wildcards are used only where the project owner explicitly said a model has related variants (for example `emy_032*` for KEEPER or `bos_003*` for GIGANTIC UFO).

The friendly-name catalog is now consumed by Asset Viewer 2.2.0. Native `.gmx` files and same-stem converted model files can be found by either filename or friendly identity (for example `emy_044` or `CELL`). The viewer displays the source/evidence status, and speculative effect rows are visibly marked **speculative** instead of being silently promoted to resolved identities.

## CELL / LUST / SHUTTER reconciliation

Three previously unnamed late enemy resources are now reconciled cleanly while keeping the distinction between *resource/runtime identity* and *friendly project-owner name*:

| Friendly identity | GMX | Runtime evidence | Result |
| --- | --- | --- | --- |
| CELL | `emy_044.gmx` | runtime type `0x97` in Xbox retail, June 10, May 11, May 9, and PS3 retail | model/runtime pairing is executable-backed across all five retained builds; `CELL` is the project-owner friendly identification |
| LUST | `emy_051.gmx` | runtime type `0x9D` in all five retained builds | model/runtime pairing is executable-backed across all five retained builds; `LUST` is the project-owner friendly identification |
| SHUTTER | `emy_052.gmx` | runtime types/opcodes `0x5A` and `0x5B` point to the same model in all five retained builds; DAT tables independently label these paths `SHUTTER1` / `SHUTTER2` | strongest name reconciliation of the three: project-owner identification agrees with the already recovered DAT/runtime family |

This closes the *catalog identity* gap for CELL/LUST/SHUTTER. It does **not** claim that `CELL` or `LUST` are internal executable strings where no such retained string evidence has been recovered.

## `est_*` effect/projectile boundary

The project owner identified:

- `est_012` as the transparent, shootable target cube used at the end of JOLYNE's orthogonal fuse and in UNKNOWN's first-phase cube patterns;
- `est_013` as PROGRESSIVE UFO missiles;
- `est_015` as WATER STRIDER trail spikes;
- `est_020` as the shared OCTOPUS / GLUTTONY bomb before detonation;
- `est_021` as the resulting OCTOPUS / GLUTTONY bomb explosion/detonation model.

`est_012` now has unusually strong executable corroboration. In Xbox retail, the JOLYNE-lineage setup creates ten line helpers and then loads runtime `0xE6`, which the retained model registry maps to `est_012.gmx`; its update path drives those ten line segments and the extra endpoint object. UNKNOWN's retail visual-controller setup (`Function_82130190`) independently loads the same `0xE6 -> est_012.gmx` resource and provisions up to 120 helper objects. May 11 `Jolyne::Init` (`Function_82119D68`) repeats the relationship using the prototype-shifted runtime `0xE7`. May 11 UNKNOWN independently repeats the relationship: factory case `0x4C` constructs `Function_821441B0`, whose setup `Function_82144298` loads shifted `0xE7 -> est_012.gmx` and provisions the same 120-helper pool. Thus the cube is a **shared JOLYNE/UNKNOWN interaction target resource** across retained retail/prototype lineage. The exact internal engine name remains unrecovered.

`est_013`, `est_015`, `est_020`, and `est_021` remain confirmed project-owner observations whose precise per-file executable controller bindings are not yet isolated. For the bomb pair, executable strings independently corroborate the gameplay family: `Gluttony::DischargeBomb` asserts `EShotManager::eENEMY_SHOT_TYPE_ID_SG_BOMB`, while `EShotSg` exposes the 3D enemy-shot state machinery. This supports the bomb lifecycle context without pretending the executable has yet yielded a direct `est_020`/`est_021` filename reference. The remaining `est_*` descriptions are preserved as shape/usage hypotheses and are marked `project_owner_speculative`. The `est_` prefix should therefore be treated as an observed effect/projectile-oriented resource family, **not** as proof that every file is merely an unregistered child or bullet mesh.

## Asset Viewer integration

Asset Viewer 2.2.0 loads the CSV at generation time and adds the following derived metadata to matching model entries:

- friendly identity;
- entity kind;
- 2D/3D versus 3D-only scope where supplied;
- console-exclusive player note for FIELD / OPTION / VARIABLE;
- evidence status and notes.

Search includes all of these fields. This keeps the filename-centric reverse-engineering identity intact while making the recovered model corpus substantially easier to browse by in-game names.
