# Mobile SIIG lineage research — dev15

## Scope and evidence policy

dev15 adds clean-room inspection of the user-supplied iOS 4.1.0 IPA and Android 1.0.4 APK. Both packages have altered distribution provenance, so package/signing observations are kept separate from hashed game-resource observations. No IPA, APK, executable, extracted game asset, prototype footage, or copyrighted stage payload is included in the toolkit release.

## Package provenance

The iOS copy declares bundle `jp.co.taito.infinitygene`, version/build 4.1.0. Both Mach-O slices have `LC_ENCRYPTION_INFO cryptid=0`; `overdrive.dylib` and `SF_Info` are present, so this is treated as a decrypted/modified distribution copy rather than an untouched App Store package. Nevertheless, all 514 ordinary resources covered by the retained CodeResources SHA-1 entries match.

The Android copy declares package `jp.co.taito.am.siInfinityGene`, version 1.0.4 / versionCode 6, `android:debuggable=true`, contains no native `.so`, and is therefore implemented in `classes.dex` plus resources. Its signing certificate SHA-1 is `61ed377e85d386a8dfee6b864bd85b0bfaa5af81`; distribution provenance is treated as modified/resigned. All 249 files covered by `META-INF/MANIFEST.MF` match their stored SHA-1 digests, and the DEX header SHA-1/Adler-32 checks both pass.

## TZIP

All six `.tzip` files use one simple wrapper: a zlib stream whose decompressed payload is an Apple binary plist dictionary mapping resource names to raw data blobs. `generator.tzip` contains 912 entries (581 DAT, 330 MAP, one version marker). The new `tzip-extract` command extracts this form with bounded expansion and traversal protection.

## DAT continuity

The existing console DAT parser accepts all 78 iOS authored DAT files, all 581 iOS generator DAT files, and all 78 Android DAT files with zero failures. This is not a newly invented mobile parser: mobile preserves the same big-endian 16-bit command-stream serialization. Android executable tracing additionally shows a little-endian primitive read followed by an explicit byte swap for each DAT word.

## MAP evolution

Mobile MAP begins with `MAP\0`, then little-endian 32-bit layer count and per-layer width/height followed by byte cells. Console MAP uses the corresponding big-endian integer headers. Mobile must preserve the declared layer count: 25 authored placeholders on both supplied mobile builds declare six empty layers, while nonempty authored maps use three layers.

The iOS generator corpus has 330 MAPs, 645 nonempty layers, 121,472 cells and 38,253 nonzero cells. Console research independently found 330 generator MAPs, 645 nonempty layers and 242,944 cells. The exact 330/645 identity is strong lineage evidence. Console cell capacity is exactly twice iOS, but nonzero content is not simply doubled; the transformation remains unresolved.

## iOS / Android authored-stage relationship

There are 158 DAT/MAP names common to both supplied mobile builds. 146 are byte-identical. All 12 differences are the DAT/MAP pairs `level9_stage1EX` through `level9_stage6EX`. Android replaces every associated map with the same 32-byte three-empty-layer placeholder and shortens every script. Each Android replacement script ends in one consecutive opcode: 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51. Direct tracing of the ARMv7 `analyzeScript` jump table proves these are `THE_MOON_V2`, `THE_SUN_V2`, `GIGANTIC_UFO_V2`, `LADYBUG_V2`, `MANDALA_V2`, and `UNKNOWN_V2`, tail-calling the correspondingly named `set*V2` functions. iOS additionally carries `level9_stage1EX_b.map`, `level9_stage2EX_b.map`, and `level9_stage3EX_b.map`.

`MOBILE_LEVEL9_OPCODE_HANDLERS.csv` records the jump-table entries, case addresses, and retained handler symbols. The shared DAT opcode table now uses these executable-backed mobile names even though the six opcodes are absent from the June 10 console corpus.

## iOS executable as a naming oracle

The iOS Mach-O symbol table retains names for the ancestral 2D engine including `Invinf_LoadScript`, `Invinf_LoadMap`, `analyzeScript`, map setup functions, `setNormalInvader`, `setGiganticUfo`, generator functions, 30/60-Hz script analyzers, and explicit Survival routines/tables. `MOBILE_IOS_SYMBOL_ANCHORS.csv` records ARMv7 values without bundling executable bytes.

This is particularly useful because prior console executable research independently located the descendant `Invinf_LoadMap` path and the generator MAP append/select routines but without the original mobile symbol names.

## Safe conclusions

1. Mobile DAT is directly compatible with the console DAT parser and is strong evidence for code/data continuity in the 2D half.
2. Mobile MAP is an ancestral/sibling form using little-endian headers; the console form uses big-endian headers.
3. The generator MAP corpus has exact file/nonempty-layer count continuity between iOS and console, with a later console capacity expansion.
4. iOS and Android authored resources are overwhelmingly the same branch; the six Level-9 extra stages are the isolated major data split in the supplied builds.
5. The supplied wrappers are unsuitable as pristine store-distribution evidence, but their internally hashed ordinary resources are coherent enough for clean-room gameplay-format research.

## Next executable targets

- Trace the six V2 boss handlers themselves and compare their parameters/behavior with the original 0x46..0x4B versions and the Android implementations.
- Recover Survival stage conversion/selection semantics from the named iOS routines and tables.
- Trace `stageGenerateMapInit`, `stageGenerateScriptInit`, and `stageGenerateMap` against the 330-block generator corpus and the console descendant.
- Correlate mobile 2D opcode handlers with the anonymous console handler families to improve field semantics without guessing.
