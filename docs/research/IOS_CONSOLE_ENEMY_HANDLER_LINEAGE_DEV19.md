# iOS → console boss and enemy-handler lineage — dev19

This checkpoint moves the iOS→console work from broad subsystem ancestry into **specific gameplay-code ancestry**. It is source-only: it records derived addresses, pool layouts, fingerprints, and stage chronology, but no executable bytes or decompiled proprietary code.

## Six original Stage-3 bosses

The iOS constructors and console descendants preserve the same subordinate entity-pool architecture with **29 of 30 type/capacity slots unchanged**.

| Boss | iOS pools | Console pools | Preserved |
|---|---|---|---:|
| THE MOON | 70×5; 36×20 | identical | 2/2 |
| THE SUN | 71×9; 37×8; 38×36; 39×20; 46×4 | 71×9; 37×8; **38×60**; 39×20; 46×4 | 4/5 |
| GIGANTIC UFO | 72×59; 40×20; 41×20; 42×4; 43×2; 44×2; 23×10; 28×10; 60×30; 29×30; 80×4 | identical | 11/11 |
| LADYBUG | 73×5; 45×40; 46×20; 47×4 | identical | 4/4 |
| MANDALA | 74×72; 48×100; 49×10; 50×40 | identical | 4/4 |
| UNKNOWN | 75×11; 51×30; 52×30; 53×80 | identical | 4/4 |

The only changed slot is THE SUN type 38, the mobile `dischargeTheSunWaveShot` pool, whose capacity increases from **36 to 60**. Retail PS3 independently reproduces the console layouts, including that 60-object pool. This is strong direct ancestry evidence rather than merely thematic reuse.

Machine-readable table: `reference/tables/IOS_CONSOLE_BOSS_POOL_LINEAGE_DEV19.csv`.

## Constructor evolution across Xbox builds

Mnemonic-sequence fingerprints provide a clean development boundary:

- May 9 → May 11: **100%** for all six constructors.
- May 11 → June 10: still high, roughly **86–93%** across the six, but functions become smaller.
- June 10 → retail: **100%** for all six.

THE MOON explains the middle transition. Its entity structure grows from `0x10C` to `0x120`, fields move, and repeated runtime-rate virtual calls are replaced by the later centralized frame-multiplier mechanism. The transformed constants preserve equivalent timing mathematics. The evidence therefore points to an engine/layout cleanup around preserved gameplay logic, not six simultaneous boss rewrites.

The exact per-boss May 11→June 10 percentages were not retained in the chat-5 continuity checkpoint. dev19 records the surviving 86–93% range and does **not** invent per-boss values.

Machine-readable table: `reference/tables/XBOX_BOSS_CONSTRUCTOR_EVOLUTION_DEV19.csv`.

## Console-only 0x96..0xAB enemy language

The local `0x96..0xAB` dispatcher was reconstructed across May 9, May 11, June 10, and retail. Almost the whole framework is already present by May 9. Slot `0x9F` is deliberately **NULL in every build** and does not occur in the available DAT corpus.

Three implementation retunes stand out:

- **GLUTTONY `0x9C`**: one 56-object helper changes type **55 → 72** between May 9 and May 11.
- **ULTIMATE UFO `0xA8`**: a type-55 helper pool doubles **20 → 40** between May 11 and June 10.
- **VERTEBRATE `0xAA`**: one pool grows **4 → 20**, while an 80-object pool changes helper type **72 → 62**, also between May 11 and June 10.

The raw handler pointer values from the prior interactive analysis were not retained in the continuity record. The dev19 source table therefore preserves the reconstructed slot/name status and exact surviving retunes while explicitly marking the missing pointer layer.

`0xA7` remains machine-readably unnamed. Gameplay identification points to **CRAB**, and the executables contain extensive `Crab.cpp` implementation evidence, but this release intentionally does not rename the opcode until the explicit code connection is demonstrated.

Machine-readable table: `reference/tables/XBOX_ENEMY_HANDLER_LINEAGE_DEV19.csv`.

## World 5 integration chronology

Stage DATs separate “code already exists” from “boss is integrated into the campaign”:

- **May 9:** WATER STRIDER exists in trial 5-1 but not normal 5-1. The 5-2 boss slot and ULTIMATE UFO in normal 5-3 already exist.
- **May 11:** WATER STRIDER moves into normal 5-1.
- **June 10:** SQUID, VERTEBRATE, and NO_NAME first appear in normal 5-4, 5-5, and 5-6.
- **NO_NAME:** May 9 and May 11 only retain the hidden `3Db_026.dat` generator test; June 10 is the first preserved normal-stage integration.

Machine-readable table: `reference/tables/WORLD5_BOSS_INTEGRATION_DEV19.csv`.

## Authored DAT loader address gap closed

The dev18 structural `Invinf_LoadScript` correspondence now has exact cross-build anchors:

| Build | Address |
|---|---:|
| Xbox May 9 | `0x8222C3B8` |
| Xbox May 11 | `0x8222DE78` |
| Xbox June 10 | `0x82239790` |
| Xbox retail | `0x82212888` |
| PS3 retail | OPD `0x000DF5C0` |

The June loader visibly retains the compact iOS-style DAT representation: one flattened big-endian 16-bit word stream plus per-command starting-word indices.

## Evidence boundary and next target

The pool layouts, address anchors, build chronology, and stated retunes above are retained executable/resource findings. The missing raw handler pointers and exact individual middle-refactor percentages are explicitly marked as unavailable rather than reconstructed from guesswork. Gameplay identification of `0xA7` as CRAB remains observational/correlative until its code connection is pinned.

After dev19 is sealed, the next reverse-engineering target is the six mobile `moveTheMoon` / `moveTheSun` / corresponding state machines and their console descendants, followed by the console-only World 4/5 enemy families. That should locate the boundary between directly extended mobile gameplay code and the console-specific 3D combat layer.
