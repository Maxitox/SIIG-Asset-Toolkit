# SIIG Asset Toolkit 2.8.0-dev22

Dev22 expands the native asset-functionalization effort from 7 to 11 of 14 known asset families. The focus is editable level structure, safe native GMX modification, and dedicated localization compilation.

## Native stage editing

- Added `stagewall-build` for wall/Xwall/stage-generator tables. The complete 20-byte record (`name[16]` + big-endian `u32`) is represented in editable CSV/JSON and canonical unchanged rebuilds are byte-identical.
- Added `stage3d-build` for Bmap/Xmap/map4/map5 tables. The complete active `0x118` record is synthesized from four placements, a path step, and five route vectors; `--template` optionally preserves inactive/tail bytes.

## GMX native template editor

- Added `gmx-edit-export` and `gmx-build`.
- Supported in-place native edits include fixed-count float/ushort arrays and indices, TXIF names, material parameter values, bone names/matrices, motion duration, animation key times, and serialized animation matrices.
- The original chunk graph/order/sizes remain fixed. This release does not claim arbitrary topology changes or a general glTF/Blender→GMX compiler.
- The new rebuild regression is synthetic/structural. Existing real-corpus GMX parsing/glTF export validation remains inherited, but dev22 does not claim real-corpus native rebuild/runtime acceptance.

## Localization compilers

- Added `text-build` for the seven-payload UTF-8 `text.bin` mode-3 BBX.
- Added `message-build` for six Shift-JIS Squirrel payloads. Readable Unicode accent characters are mapped back into the game's language-specific single-byte glyph convention before encoding.
- Template BBX identifiers/header/seed/order and native newline conventions are preserved.
- Byte-identity tests use canonical synthetic localization fixtures.

## Functionalization status

- 14 known asset families classified.
- 14/14 have a view/export/archive path.
- 11/14 now have a native build/round-trip path.
- Remaining one-way families are Xbox XACT/XMA2 audio banks, PS3 SBlk/VAG/989SND audio banks, and Xenos compiled shaders.
- Full topology-changing/new-chunk-graph GMX synthesis remains a major sub-format gap even though fixed-layout GMX is now natively editable.

## Validation

- Added five new native-builder regression gates.
- Dependency-free self-test suite: **67/67**.
- Source-only packaging remains mandatory; no proprietary game binaries/assets or research executables are bundled.

Runtime acceptance of arbitrary modified resources still requires game/emulator testing.
