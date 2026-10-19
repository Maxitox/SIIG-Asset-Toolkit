# CRAB runtime assembly — 2.10.0-dev4

## Result

CRAB is a nine-object runtime assembly. The executable/model evidence resolves the object order and the deterministic **first-visible** formation:

| index | runtime | model | role | native pose sample | assembly translation | assembly rotation |
|---:|---|---|---|---:|---|---|
| 0 | `0xA7` | `bos_013.gmx` | leg/root assembly | 167 | `(0, 0, 0)` | `(0, 180, 0)` |
| 1 | `0xCD` | `bos_013b.gmx` | body shell | 0 | `(0, 422.0840835571289, 0)` | `(0, 0, 0)` |
| 2 | `0xCC` | `bos_013a.gmx` | central cannon/core | — | `(0, 422.0840835571289, 0)` | `(0, 0, 0)` |
| 3 | `0xCE` | `bos_013c.gmx` | propodus | — | `(81, 422.0840835571289, 0)` | `(0, 0, 0)` |
| 4 | `0xCE` | `bos_013c.gmx` | propodus | — | `(-81, 422.0840835571289, 0)` | `(0, 0, 0)` |
| 5 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(81, 445.0840835571289, 0)` | `(0, 0, 0)` |
| 6 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(81, 399.0840835571289, 0)` | `(0, 0, 0)` |
| 7 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(-81, 445.0840835571289, 0)` | `(0, 0, 0)` |
| 8 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(-81, 399.0840835571289, 0)` | `(0, 0, 0)` |

The values are not screenshot measurements or symmetry guesses. `pose_sample` is a dev4 assembly feature: the selected native GMX sample is baked into the exported node hierarchy and that instance's animation channels are omitted, producing one stable snapshot of a multipart runtime state.

## Explicit `0xA7 = CRAB` resolution

Earlier dev19 lineage files deliberately left opcode `0xA7` machine-readably unnamed. Dev4 resolves that historical boundary without rewriting the old artifacts:

- the runtime entity registry maps `0xA7` to `bos_013.gmx` on May 9, May 11, June 10, Xbox retail and PS3 retail;
- June `Crab.cpp` part construction at `0x8213BB00` walks the child count/type table at `0x8200FA04` and creates `1×CD`, `1×CC`, `2×CE`, `4×CF`;
- the Crab runtime family consistently treats part index 8 as the separately created root and indices 0–7 as those children;
- the root/child model names and named locator tables in `bos_013*.gmx` agree with the code path.

Together these establish the explicit code connection that dev19 required before naming `0xA7` CRAB.

## June 10 Xbox evidence

The project-owner Ghidra export used for this work has SHA-256 `987cf607e4164dde06b980718a6169791d81e064d4b5e46ecb35f45176076f66`.

Key anchors:

- `Crab.cpp` child creation: `0x8213BB00`; table: `0x8200FA04`.
- root setup `0x821315D8` binds the named locator set and initializes the CE/CF angular controllers to π/2; it also applies the root's 180° runtime Y rotation.
- shared multipart updater `0x82134338` dispatches the CD/CC, CE and CF placement routines `0x82133DC8`, `0x82132740`, `0x821321A8`.
- first-visible state routine `0x82132C90` enables all nine parts, selects root animation segment 3, jumps the root to native sample `0xA7 = 167`, then updates the formation.
- static locator/offset initializer `0x82562448` materializes the relevant vectors, including `(0,+23,+25)`, `(0,-23,+25)`, `(+81,0,0)`, `(-81,0,0)`.

The `+25` components belong to the named locator support data; the first-visible child placement routines resolve the exported formation above, with the CE pair at ±81 X and CF pairs at ±23 Y relative to their CE parent positions.

## Model and ANM evidence

The June and retail Xbox `enemy.anm` payloads are byte-identical for this corpus (SHA-256 `c3100a85d279af220e3f2b1f8b51650acf2e3c536ecac1f918d5174f88570cb4`). Its CRAB records define:

- `bos_013`: `0→0`, `1→60` loop, `61→100`, `101→239`, `240→279`;
- `bos_013b`: `0→0`, `1→30`, `31→60`.

Therefore root animation index 3 is exactly the `101→239` segment and the explicit frame write selects sample 167. The shell has not yet been switched to its later open/close clips at first visibility, so its first-visible snapshot remains clip 0/sample 0; later shell transitions are driven by June routines `0x82132658` and `0x821326C8`.

The June and retail CRAB GMXs are also byte-identical in the retained corpus. `bos_013.gmx` exposes the root-side `lt_000` attachment used by the code; subordinate CRAB GMXs expose the other named locators referenced by the runtime.

At native sample 167:

- `bos_013` track translation Y = `376.09698486328125`, local rotation = 180° around Y;
- `lt_000` local translation Y = `45.987098693847656`;
- combined attachment center Y = `422.0840835571289`.

The runtime root adds another 180° Y rotation, cancelling the root track's 180° orientation for the child attachment frame in this formation. The root assembly container itself retains the runtime 180° Y transform while its native animation sample is baked internally.

## Retail Xbox cross-check

The stripped retail state routine at `0x821190D0` repeats the same first-visible sequence: enable nine objects, select segment 3 for part 8, set sample `0xA7`, then update multipart placement. Retail static initializer `0x82536458` contains the same named-locator support vectors and ±23/±81 constants. The retained June/retail `enemy.anm` and all five `bos_013*.gmx` inputs used for this analysis are byte-identical.

## Retail PS3 cross-check

The retained `SIIGPS3GHIDRA.zip` input has SHA-256 `e7af0cd5940268c4697470ca58d55010b45a50706dfc10ead552d4ee4ce55d6d`.

PS3 state routine `0x001AAA5C` independently performs the same first-visible root operations: animation segment 3 followed by sample `0xA7`. PS3 static initializer `0x001AD900` independently materializes the same ±23 and ±81 vectors. The PS3 runtime family also uses the same 180° root rotation and nine-part child logic.

## Exporter behavior and evidence boundary

CRAB needs more than outer XYZ matrices because two source GMXs are animated at the chosen state. Dev4 therefore adds optional per-instance `pose_sample` to `SIIG_GMX_ASSEMBLY_V1`:

1. select one native ANIM sample for every track in that GMX;
2. decompose the sample matrix and bake it into the corresponding glTF node's static TRS;
3. omit that instance's animation channels from the combined assembly;
4. then apply the recovered outer runtime assembly matrix.

This creates a static, editable snapshot of the executable-defined first-visible CRAB formation. It does **not** claim that SIIG stores the nine objects in one native GMX, nor that this one snapshot represents all later attack/damage formations. No executable, Ghidra export, `enemy.anm`, GMX asset or footage is bundled in the source-only release.
