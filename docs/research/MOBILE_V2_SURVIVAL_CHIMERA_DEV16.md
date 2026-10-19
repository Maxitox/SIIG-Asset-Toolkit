# Mobile V2, Survival, and Chimera research — dev16

## Scope and evidence policy

dev16 continues from the sealed dev15 mobile-format checkpoint. The user-supplied iOS 4.1.0 IPA and Android 1.0.4 APK remain research copies with modified distribution wrappers; executable/resource claims below come from their inspected contents, while third-party gameplay footage is used only as observational corroboration. No IPA, APK, executable, extracted game asset, audio, or footage is bundled.

Three gameplay videos supplied by the project owner are credited to **MaxTheMurdererV2**: the six V2/DELETION bosses, Survival Mode and its eight endings, and the Chimera/crossover stages. These videos are not treated as executable evidence and are not redistributed.

## Correction to the dev15 Level-9 interpretation

dev15 correctly isolated the six iOS/Android differences at `level9_stage1EX` through `level9_stage6EX` and proved that Android's replacement scripts terminate in V2 opcodes `0x4C..0x51`. dev16 resolves the missing iOS identity: the full iOS Level-9 resources are the six **Chimera crossover stages**, not the DELETION stages.

The DELETION missions instead occupy `level8_stage3EX` through `level8_stage8EX`. `MOBILE_LEVEL9_SPLIT.csv` has been revised to make the iOS-Chimera / Android-stub distinction explicit.

## DELETION and V2 bosses

The fixed mission-title table and `pScriptDataFileName` order tie Extra missions 23..28 to six consecutive Level-8 scripts:

| Extra | Mission | Script | V2 boss |
|---:|---|---|---|
| 23 | POINT DELETION | `level8_stage3EX.dat` | THE_MOON_V2 |
| 24 | INTERSTITIAL DELETION | `level8_stage4EX.dat` | THE_SUN_V2 |
| 25 | TERMINAL DELETION | `level8_stage5EX.dat` | GIGANTIC_UFO_V2 |
| 26 | NUCLEOTIDE DELETION | `level8_stage6EX.dat` | LADYBUG_V2 |
| 27 | GENE DELETION | `level8_stage7EX.dat` | MANDALA_V2 |
| 28 | CHROMOSOMAL DELETION | `level8_stage8EX.dat` | UNKNOWN_V2 |

`level8_stage9EX.dat` contains all six V2 boss opcodes in sequence.

The iOS `analyzeScript` jump table proves opcodes `0x4C..0x51` tail-call `_setTheMoonV2`, `_setTheSunV2`, `_setGiganticUfoV2`, `_setLadybugV2`, `_setMandalaV2`, and `_setUnknownV2`. Their main entity types are 100..105. The original Stage-3 bosses use opcodes `0x46..0x4B` and main entity types 70..75.

The central enemy-movement dispatcher routes each original/V2 pair into the same corresponding boss movement engine. V2 behavior is therefore implemented through alternate entity types, helper pools, data, and explicit branches inside the original boss families rather than six unrelated replacement engines.

Five V2 scripts pass exactly the same boss arguments as the corresponding Stage-3 originals. UNKNOWN is the exception: the original call is `[0,10000,1,20]`, while UNKNOWN_V2 receives `[0,10000,1,60]`. The final field remains deliberately unnamed until its consumer is fully resolved.

`MOBILE_V2_ENTITY_POOLS.csv` records every `ES_Init2(type, capacity)` allocation seen in the twelve original/V2 constructors. The helper-pool changes are substantial; LADYBUG_V2 is the largest constructor expansion, while UNKNOWN_V2 also has explicit V2-only branches and a `_setVer2Destroy` action. These facts support the project-owner description of the V2 bosses as upgraded versions without reducing the upgrade to an unsupported single difficulty multiplier.

## Survival selection graph

The iOS constant `tSurvivalStageParam` at ARMv7 `0x002E9708` is exactly 36 records of three signed 32-bit values. `_initSurvivalSelect` indexes it with a 12-byte stride and iterates all 36 records. `_selectSurvivalSelectButtonDecide` uses field 0 as the selected stage ID after passing it through `_checkSurvivalStage`.

Fields 1 and 2 form graph links. `_initSurvivalSelect` compares them against all 36 selection nodes to mark linked choices. Nodes 28..35 have `-1,-1`, making them the eight terminal nodes. `MOBILE_SURVIVAL_GRAPH.csv` preserves the complete 36-node graph.

When Survival finishes, `_InvinfSys_Calc` takes the terminal selection-node index, subtracts 28, masks with 7, and calls `checkSurvivalModeEnding(int)`. That function masks with 7 again, adds 52, and invokes the achievement-unlock selector. The executable's achievement strings at indices 52..59 are `SURVIVAL_01_CLEAR` through `SURVIVAL_08_CLEAR`.

The executable's ending text is in the same 1..8 order:

1. LINK
2. CIRCLE
3. VIRTUAL
4. ETERNITY
5. CUT OFF
6. IMMORTALITY
7. PHANTASM
8. PARALLEL

Therefore terminal nodes 28..35 map directly to those eight endings in order. This executable result is independently consistent with the MaxTheMurdererV2 Survival footage supplied by the project owner.

### Conditional Survival stage substitutions

`survivalStageConvertTable` at ARMv7 `0x002E96C0` contains six records:

`(49,30,31)`, `(50,31,40)`, `(51,32,36)`, `(52,33,27)`, `(53,34,46)`, `(54,35,30)`.

`_checkSurvivalStage` matches field 0 against the requested stage ID, reads a status byte indexed by field 1, and if that byte is not `1`, substitutes field 2 as the stage ID. The meaning of the status byte is still unresolved and is not labeled as a particular unlock/clear condition. `_setVer2Destroy` writes a different flag and must not be conflated with this status array.

## Chimera / crossover stages

The iOS mission-title table and `pScriptDataFileName` entries 48..53 align in exact order:

| iOS resource | Chimera stage | Mission | Source game | Boss opcode / handler |
|---|---|---|---|---|
| `level9_stage1EX` | C-1A | CAPTAIN NEO | Darius | `0x52 KING_FOSSIL` / `_setKingFossil` |
| `level9_stage2EX` | C-2A | URBAN TRAIL | Night Striker | `0x53 TWILIGHT_MIRAGE` / `_setTwilightMirage` |
| `level9_stage3EX` | C-3A | BORN TO BE FREE | Metal Black | `0x54 APARTHEAD` / `_setApartHead` |
| `level9_stage4EX` | C-1B | I CAN NOT APE | Darius | `0x52 KING_FOSSIL` / `_setKingFossil` |
| `level9_stage5EX` | C-2B | BURN ALT AIR | Night Striker | `0x53 TWILIGHT_MIRAGE` / `_setTwilightMirage` |
| `level9_stage6EX` | C-3B | BEFORE TEN ORB | Metal Black | `0x54 APARTHEAD` / `_setApartHead` |

The `analyzeScript` jump entries at `0x00011DE8`, `0x00011DEC`, and `0x00011DF0` lead to cases `0x0001254C`, `0x00012568`, and `0x00012588`, which tail-call those three retained constructors. dev16 therefore adds `KING_FOSSIL`, `TWILIGHT_MIRAGE`, and `APARTHEAD` to the shared DAT opcode-name table.

The second boss has two names in the executable lineage: the script handler is `_setTwilightMirage`, while the embedded display-name block says `GREAT DESTROYER`. External franchise/gameplay references describe Great Destroyer and Twilight Mirage as the two phases of the fight. The toolkit keeps `TWILIGHT_MIRAGE` as the internal opcode label and records the display relationship separately rather than collapsing the distinction.

Likewise, the executable spells the third internal name `APARTHEAD`, while external franchise references call the Metal Black boss Apartheid. The parser preserves the executable spelling and the reference table records the public/franchise name separately.

The constructors establish consecutive main entity types and capacities:

- King Fossil: type 106, capacity 5
- Twilight Mirage: type 107, capacity 12
- ApartHead: type 108, capacity 21

All three have retained FPS60 constructors and named attack/subentity functions. The iOS package also physically carries dedicated Darius, Night Striker, and Metal Black music assets. Historical release coverage from 4Gamer and TouchArcade independently describes three paid crossover packs, one ship and two stages per pack; these references are attribution/corroboration only, not sources of the binary mappings.

## Android Level-9 replacement behavior

Android 1.0.4 contains the same six Level-9 filenames but not the iOS Chimera content. Every corresponding MAP is the same 32-byte empty three-layer placeholder, and the scripts are short replacements ending in `THE_MOON_V2` through `UNKNOWN_V2` respectively. Android `classes.dex` also lacks the iOS crossover boss/music naming evidence.

The reason the Android placeholders chose exactly the six V2 boss opcodes is still unresolved. dev16 records them as replacement/stub behavior and does **not** relabel them as DELETION stages.

## Evidence files

- `reference/tables/MOBILE_DELETION_V2_MAPPING.csv`
- `reference/tables/MOBILE_V2_ENTITY_POOLS.csv`
- `reference/tables/MOBILE_SURVIVAL_GRAPH.csv`
- `reference/tables/MOBILE_SURVIVAL_ENDINGS.csv`
- `reference/tables/MOBILE_SURVIVAL_CONVERSION.csv`
- `reference/tables/MOBILE_CHIMERA_MAPPING.csv`
- `reference/tables/MOBILE_CHIMERA_BOSS_HANDLERS.csv`
- `reference/tables/MOBILE_LEVEL9_SPLIT.csv`
- `reference/tables/MOBILE_LEVEL9_OPCODE_HANDLERS.csv`
- `validation/MOBILE_EXCLUSIVES_DEV16.json`

## Remaining mobile targets

- Resolve the exact gameplay meaning of the six Survival status bytes used by `survivalStageConvertTable`.
- Continue attack-level original/V2 diffs, especially timing, projectile-rate and phase-branch differences inside the shared boss movers.
- Explain why Android's Level-9 placeholders deliberately use the six V2 opcodes.
- Trace the three Chimera boss movers/attack state machines in more detail and compare the A/B-stage parameter changes, especially King Fossil's differing final two arguments.
- Continue `stageGenerate*` lineage work against the console generator descendant.
