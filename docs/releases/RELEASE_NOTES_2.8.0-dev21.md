# SIIG Asset Toolkit 2.8.0-dev21

Dev21 starts the native asset-functionalization phase. The goal is no longer only to extract and decode SIIG resources, but to make every extracted family useful for viewing, editing, native rebuilding, replay, or archival.

## Native round-trip editing

- Added `png2tex`: edited PNG -> native Xbox 360 tiled TEX or PS3 RSX TEX using the original file as a layout/header template.
- Added `dat-build`: edited DAT CSV/JSON -> native DAT command stream.
- Added `map-build`: lossless editable MAP JSON -> native MAP byte grids. `map2png` now emits `*.map.edit.json` automatically.
- Added `anm-build`: edited ANM CSV/JSON -> native 28-byte animation-range tables.
- Added `png2col`: edited black/white PNG -> native one-bit COL mask using the original 16-byte header as a template.
- Added `png2font`: edited system-font atlas PNG -> XOR-obfuscated native `systemfont.crp` using the original font resource as the TEX layout template.

The builders are deliberately template-preserving where platform/GPU-specific layout metadata exists. An unchanged editable export is required to rebuild byte-identically before arbitrary edits are considered supported.

## Capability tracking

- Added `asset-capabilities`, a machine-readable matrix separating structural decode, view/export, editable interchange, native rebuild, and remaining gaps for 14 known asset families.
- Full-game rips now emit `validation/ASSET_CAPABILITIES.json`.
- Added `docs/guides/NATIVE_ASSET_ROUNDTRIP.md` with end-to-end modding workflows from package -> BBX -> editable file -> native resource -> BBX repack.

## Validation

- Added byte-identical native round-trip gates for TEX, DAT, MAP, ANM, and COL.
- Added a capability-matrix regression gate.
- The dependency-free self-test suite now contains 62 tests.

## Remaining high-value reverse-build targets

- glTF/Blender -> GMX compiler.
- JSON/CSV -> Bmap/Xmap/map4/map5 3D route-table compiler.
- CSV/JSON -> wall/Xwall/stage-generator compiler.
- Dedicated text/message localization compilers.
- Xbox XACT/XMA2 and PS3 SBlk/VAG replacement-bank builders.
- Xenos shader disassembly/translation or a compatible compiler path.

No game binaries or extracted copyrighted resources are bundled.
