# SIIG Asset Toolkit 2.8.0-dev15

**Mobile lineage / package-format checkpoint**

- Branched from finalized dev14; frozen dev8-dev14 history is not modified.
- Added dependency-free `siig_mobile.py`.
- Added `mobile-inventory` for IPA/APK metadata, resource-integrity and DEX/Mach-O inspection.
- Added `mobile-compare` for authored iOS/Android DAT/MAP byte comparison.
- Added bounded/path-safe `tzip-extract` for the iOS zlib + binary-plist resource wrapper.
- Added `mobile-map-info` for the little-endian mobile MAP variant while preserving the existing big-endian console MAP parser.
- Added five synthetic mobile regressions; the suite now contains 51 tests.
- Validated the shared DAT parser on 737 supplied mobile DAT files with zero failures.
- Validated mobile MAP structure on 493 supplied MAP files with zero failures.
- Documented 330-generator-MAP / 645-nonempty-layer continuity from iOS to console.
- Documented the isolated Android Level-9 replacement block and proved opcodes 0x4C..0x51 as `THE_MOON_V2`, `THE_SUN_V2`, `GIGANTIC_UFO_V2`, `LADYBUG_V2`, `MANDALA_V2`, and `UNKNOWN_V2` from the iOS ARMv7 `analyzeScript` jump table.
- Added iOS ARMv7 symbol anchors for `Invinf_LoadScript`, `Invinf_LoadMap`, generator, Survival and representative enemy/boss functions.
- Retained strict provenance language: supplied IPA/APK wrappers are modified research copies; game resources are never bundled.
