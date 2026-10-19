# SIIG Asset Toolkit 2.8.0-dev16

**Mobile exclusives: DELETION / Survival / Chimera checkpoint**

- Branched from sealed dev15; frozen dev8-dev15 release artifacts are not modified.
- Corrected the Level-9 interpretation: full iOS `level9_stage1EX..6EX` resources are the six Chimera crossover stages; Android substitutes V2-based stubs in those filenames.
- Proved DAT opcodes `0x52`, `0x53`, and `0x54` as `KING_FOSSIL`, `TWILIGHT_MIRAGE`, and `APARTHEAD` from the iOS ARMv7 `analyzeScript` jump table and retained constructor symbols.
- Added a dedicated synthetic regression for the Chimera opcode map; dependency-free selftest count is now 52.
- Proved Extra 23..28 / `level8_stage3EX..8EX` as the six DELETION missions and tied them to V2 boss opcodes `0x4C..0x51`.
- Recorded exact original/V2 `ES_Init2(type, capacity)` pool differences and the shared original/V2 boss-mover architecture.
- Reconstructed the 36-node `tSurvivalStageParam` selection graph and mapped terminal nodes 28..35 to the eight ending strings and achievement IDs.
- Recorded the six conditional `survivalStageConvertTable` substitutions while keeping the status-byte meaning unresolved.
- Added exact Chimera resource/title/boss mappings, iOS MAP metrics, Android replacement behavior, and crossover constructor/attack symbol anchors.
- Added third-party observational footage credits for MaxTheMurdererV2's V2-boss, Survival-ending, and Chimera videos; no footage is bundled.
- Retained source-only packaging and the modified-wrapper evidence boundary for the supplied IPA/APK research copies.
