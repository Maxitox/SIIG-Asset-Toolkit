# Mobile Survival gating and V2 behavior research — dev17

## Scope

dev17 continues from sealed dev16 and resolves the six previously unnamed Survival conversion status bytes. It also tightens the original-versus-V2 boss comparison and records the Chimera A/B boss-script parameter differences. The user-supplied iOS 4.1.0 package remains a decrypted research copy; executable/resource conclusions are limited to its inspected contents. No game binary or extracted asset is bundled.

## Survival's six conditional substitutions are Evolution Tree DLC gates

`checkSurvivalStage` at ARMv7 `0x00096BDC` iterates the six records in `survivalStageConvertTable` (`0x002E96C0`). For a matching requested stage it loads the record's second word as an index into the byte array at `infSystem + 0xD6E`. If that byte is not exactly `1`, the third word replaces the requested stage ID.

The same `+0xD6E` byte array is read/written by the Evolution Tree implementation (`presetEvolutionTree`, `initEvolutionTree`, `drawEvolutionTree`, `secretEvolutionHelpCheck`, `initEvolutionPurchase`, and `checkEvolution`). The fixed `TXT_EVOLUTION_TITLE` table at `0x002EB4FA` identifies indices 30..35 as `EXTRA 31`..`EXTRA 36`. Therefore the Survival bytes are **Evolution Tree stage-node status**, not a Survival-private state array.

The six requested stage IDs 49..54 are the six Chimera missions (Extra 31..36). Survival uses them only when their Evolution Tree stage node is unlocked/status 1; otherwise it substitutes a non-DLC stage:

| Requested | Evolution gate | Fallback |
|---|---|---|
| C-1A / Extra 31 / CAPTAIN NEO | node 30 `EXTRA 31` | stage 31 / Extra 13 / PROOF-READING REPAIR |
| C-2A / Extra 32 / URBAN TRAIL | node 31 `EXTRA 32` | stage 40 / Extra 22 / TELEOMORPH |
| C-3A / Extra 33 / BORN TO BE FREE | node 32 `EXTRA 33` | stage 36 / Extra 18 / GENETIC DRIFT |
| C-1B / Extra 34 / I CAN NOT APE | node 33 `EXTRA 34` | stage 27 / Extra 9 / REPLICATION FORK |
| C-2B / Extra 35 / BURN ALT AIR | node 34 `EXTRA 35` | stage 46 / Extra 28 / CHROMOSOMAL DELETION |
| C-3B / Extra 36 / BEFORE TEN ORB | node 35 `EXTRA 36` | stage 30 / Extra 12 / ALLELE |

This explains why the Survival route can remain structurally fixed even when crossover content is unavailable: stage selection passes through a compatibility/substitution gate before play begins.

## How the Chimera Evolution nodes unlock

`initEvolutionPurchase` at `0x0009F168` copies a six-word constant table at `0x002E98CC`: `[88,30, 89,31, 90,32]`. It processes three purchase slots; when the purchase result is 3 it adds both paired Evolution nodes and writes their status bytes to 1. The title table identifies the pairs as:

- node 88 `SILVER HAWK` + node 30 `EXTRA 31`
- node 89 `INTER GRAY` + node 31 `EXTRA 32`
- node 90 `BLACK FLY` + node 32 `EXTRA 33`

`checkEvolution` at `0x0009F394` handles the three B-stage nodes separately. In its special mode-15 path, clearing stage IDs 49, 50, and 51 adds nodes 33, 34, and 35 respectively and writes their status bytes to 1. Thus the purchased A stage unlocks with its crossover ship, and clearing that A stage unlocks the corresponding B stage.

## Original versus V2 implementation strategy

All six original/V2 pairs share the same family mover, but the upgrade mechanism is not uniform.

### Constructor/helper-driven pairs

`THE_MOON`, `LADYBUG`, and `MANDALA` have no direct comparison against their original/V2 main type IDs inside the corresponding shared mover. Their constructors instead replace helper families/capacities and alter initialization/randomization. Examples include THE MOON helper `36 x 20` becoming `55 x 80`, and LADYBUG expanding three helper pools into four with capacities 40/48/40/80.

### THE SUN

At `moveTheSun + 0x84` (`0x000D8084`), only original type 71 enters a block that moves four paired internal values by `+512` / `-512` toward a threshold of `6144`. V2 type 101 bypasses this original-only ramp and proceeds directly into the following state logic. The exact visual property controlled by these fields is intentionally unnamed.

### GIGANTIC UFO

`moveGiganticUfo` contains two explicit type-dependent differences. At `0x000D6C4C`, type 72 takes the original coordinate-copy path and adds `4096`; the alternate path used by V2 adds `18432`. At `0x000D7260`, type 102 selects multiplier 2 where other types select 1 before a `traceOption` update. Algebraically this changes the computed internal coordinate by another 92 units for V2. The affected coordinate/trace semantics are not promoted beyond what the instructions prove.

### UNKNOWN

UNKNOWN_V2 has the clearest explicit strength modifications. `moveUnknown` tests type 105 at `0x000D3A88` and `0x000D3E24` and doubles two helper objects' `+0x14` fields. At `0x000D4014` it doubles corresponding `+0x28` values. On defeat, the type-105 check at `0x000D47F8` invokes `setVer2Destroy`. These fields are proven multipliers but remain unnamed until their downstream consumers establish whether they are speed, rate, distance, or another quantity.

## Chimera A/B boss arguments

The paired crossover stages reuse identical boss arguments for Twilight Mirage and ApartHead. King Fossil is the exception:

- C-1A: `[0, 2000, 1, 1000, 1000, 150, 48, 6]`
- C-1B: `[0, 2000, 1, 1000, 1000, 150, 96, 3]`

`setKingFossil` copies the seventh displayed argument (48/96) into entity field `+0x98`. `moveKingFossil` later reloads its `+0x88` countdown from `+0x98`, proving that the A/B change doubles at least one internal countdown/reload value. The final 6/3 parameter is also halved, but its consumer has not yet been safely named. This is evidence that the B version is not solely a different stage layout even though the same King Fossil entity type is used.

## Enemy-shot dispatcher resolves the V2 attack repertoires

The constructor pool IDs can now be tied to named attacks rather than left as anonymous helpers. `dischargeEnemyShot_FPS60` at `0x0017B13C` reads each pool object's type ID, subtracts one, and dispatches through an 82-entry jump table. The exact IDs allocated by the boss constructors therefore map to retained `discharge*` symbols.

The primary original→V2 repertoire changes are:

- **THE MOON:** `TheMoonShot` (type 36, cap 20) → `TheMoonSearchLaser` (type 55, cap 80).
- **THE SUN:** Laser/Wave/Light Ball pools (37/38/39) → Gamma Laser/Rolling Laser/Sub-Speed pools (56/59/57); the type-46 shared pool remains present.
- **GIGANTIC UFO:** Homing/Light Ball/Laser01/Laser02/Laser03 (40..44) → Sub-Speed/Short Laser/Large Laser/Search Laser (63/60/61/62), with substantially larger capacities on several V2 pools. Additional generic/shared pools used by both constructors are kept separate from this changed dedicated block.
- **LADYBUG:** Homing/Add-Speed/Laser (45/46/47) → Light Ball/Sub-Speed/Laser 2/Sub-Speed 2 (66/65/64/67), growing from three dedicated pools to four.
- **MANDALA:** Beam/Light Ball/Shot-L (48/49/50) → Twin/Light Ball/Laser (68/49/71); Light Ball is retained.
- **UNKNOWN:** Shot-S/Light Ball/Sub-Speed (51/52/53) → Add-Speed/Homing/Add-Speed 2 (72/73/74).

This provides executable-backed substance to the gameplay description of the V2 bosses as upgraded counterparts: most of them do not merely fire the same patterns faster; their initialized projectile/attack pool types change to different named attack handlers. `MOBILE_V2_ATTACK_POOLS_DEV17.csv` preserves the exact pool IDs, capacities and dispatch targets.

## Toolkit integration

dev17 adds `mobile-exclusives-info`, a source-only JSON reference command containing the executable-backed Survival/Chimera substitution policy, eight Survival terminal endings, and conservative V2 behavior summaries. Its regression is fully synthetic/static and does not require the IPA.

## Evidence files

- `reference/tables/MOBILE_SURVIVAL_STAGE_SUBSTITUTIONS_DEV17.csv`
- `reference/tables/MOBILE_CHIMERA_EVOLUTION_UNLOCKS_DEV17.csv`
- `reference/tables/MOBILE_V2_BEHAVIOR_DIFF_DEV17.csv`
- `reference/tables/MOBILE_CHIMERA_AB_BOSS_ARGS_DEV17.csv`
- `reference/tables/MOBILE_V2_ATTACK_POOLS_DEV17.csv`
- `validation/MOBILE_BEHAVIOR_DEV17.json`

## Remaining targets

- Name the V2-specific helper fields only after their downstream attack consumers are proven.
- Trace V2 helper families into the named `discharge*` attack routines to quantify projectile cadence/pattern changes.
- Explain why Android's removed Chimera slots were replaced by the six V2 boss opcodes.
- Continue the mobile `stageGenerate*` implementation comparison against the console generator descendant.
