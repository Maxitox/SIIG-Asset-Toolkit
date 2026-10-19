# SIIG Asset Toolkit 2.8.0-dev17

**Survival DLC gating / V2 attack behavior / Chimera A/B checkpoint**

- Branched from sealed dev16; dev16 and earlier frozen release artifacts are not modified.
- Resolved the six `survivalStageConvertTable` status bytes as Evolution Tree stage-node statuses at `infSystem+0xD6E`.
- Proved Survival's conditional Chimera policy: requested Extra 31..36 stages are used when their Evolution nodes are unlocked; otherwise six predetermined existing Extra stages are substituted.
- Proved the crossover unlock chain: purchase states pair SILVER HAWK/INTER GRAY/BLACK FLY with Chimera A-stage nodes; clearing stage IDs 49..51 unlocks the corresponding B-stage nodes.
- Added `mobile-exclusives-info`, which reports the executable-backed Survival substitution policy/endings plus conservative V2 behavior and attack-pool mappings without requiring game files.
- Traced the global `dischargeEnemyShot_FPS60` type dispatcher and mapped constructor pool IDs to named retained attack routines.
- Established concrete original→V2 projectile repertoire swaps for THE MOON, THE SUN, GIGANTIC UFO, LADYBUG, MANDALA, and UNKNOWN.
- Recorded explicit V2 behavior branches in THE SUN, GIGANTIC UFO, and UNKNOWN; UNKNOWN_V2 doubles several helper fields and invokes `setVer2Destroy` on defeat.
- Proved C-1A/C-1B King Fossil boss-argument differences: one internal reload/countdown source changes 48→96 and another still-unnamed parameter changes 6→3; Twilight Mirage and ApartHead reuse identical boss arguments between A/B stages.
- Added five dev17 reference tables plus `MOBILE_SURVIVAL_V2_BEHAVIOR_DEV17.md` and `MOBILE_BEHAVIOR_DEV17.json`.
- Expanded the dependency-free regression suite to 53 tests.
- Retains source-only packaging: no IPA/APK, executable, extracted mobile resources, game assets, or third-party footage is bundled.

## Evidence boundary

The supplied iOS 4.1.0 IPA and Android 1.0.4 APK remain modified-distribution research copies. Executable/resource findings are kept separate from wrapper-authenticity claims. MaxTheMurdererV2 footage remains credited observational corroboration only. Unnamed internal helper fields are not assigned gameplay semantics until their consumers prove those names.
