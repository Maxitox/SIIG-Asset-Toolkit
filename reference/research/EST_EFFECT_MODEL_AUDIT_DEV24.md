# `est_*` effect-model audit — dev24 WIP182 update

This audit narrows the remaining `est_011` through `est_021` model-ownership problem without promoting visual guesses to executable facts. It combines the project-owner identity notes already retained by dev24, the five-build derived runtime registry, and geometry/hash metadata from an external project-owner retail rip. No GMX/glTF/game payload is bundled.

## Strong results

- The audited range contains **11 models** (`est_011` ... `est_021`).
- `est_012.gmx` is the **only** one with a top-level runtime-registry slot in any retained build. It is present in all five retained registries: runtime `0xE6` in Xbox retail, June 10 and PS3 retail; runtime `0xE7` in the May 9/May 11 prototypes. WIP181 now additionally confirms direct JOLYNE and UNKNOWN ownership paths: JOLYNE setup loads the resource after creating ten line helpers, while UNKNOWN's retail controller setup loads it before provisioning up to 120 helpers. The project owner's observed transparent shootable cube at those encounters is therefore promoted to a confirmed shared target-cube usage.
- `est_011` and `est_014` have **byte-identical converted geometry payloads** while their native GMX containers are different. This independently corroborates the project owner's visual note that both use the same hexagon silhouette, while showing that their native resources are not byte-identical files.
- No other pair in `est_011` ... `est_021` shares the same converted geometry payload hash.
- Project-owner-confirmed usage now includes `est_012` = shared interactive target cube, `est_013` = PROGRESSIVE UFO missiles, `est_015` = WATER STRIDER trail spikes, `est_020` = the shared OCTOPUS / GLUTTONY bomb before detonation, and `est_021` = that bomb's detonation/explosion model. The `est_012` JOLYNE/UNKNOWN executable paths are isolated; `est_013`/`est_015` and the exact per-file `est_020`/`est_021` executable bindings are still not isolated.
- `est_016` remains only a project-owner hypothesis for the ULTIMATE UFO / possibly WRATH giant beam. WIP180 does **not** promote that hypothesis.

## Architectural boundary

The executable has a distinct `EShotSg` / 3D enemy-shot subsystem, but that subsystem name alone does not establish a one-to-one filename mapping for these GMXs. Likewise, a runtime resource slot alone does not prove which gameplay controller owns or instantiates it. WIP181 closes that problem specifically for JOLYNE and UNKNOWN's use of `est_012`, with both retail and May-prototype controller paths now corroborated. An earlier nearby-string attribution to VERTEBRATE was rejected after tracing the May 11 factory: `Function_82144298` is UNKNOWN's prototype setup path. Exact controller ownership remains unresolved for `est_011`, `est_014`, and `est_016` through `est_019`; `est_013`/`est_015` retain project-owner-confirmed usages without isolated executable call paths. WIP182 additionally promotes `est_020`/`est_021` from visual guesses to project-owner-confirmed shared OCTOPUS / GLUTTONY bomb lifecycle models. The executable independently confirms `Gluttony::DischargeBomb` uses the `SG_BOMB` 3D enemy-shot family, but this is corroborating subsystem evidence rather than a direct per-file filename binding.

## Reproducible table

See `reference/tables/EST_EFFECT_MODEL_AUDIT_DEV24.csv`. Geometry fingerprints are derived from the toolkit-generated `*.gltf.bin` payloads in the external retail rip; native GMX hashes/sizes are retained only as derived validation metadata.
