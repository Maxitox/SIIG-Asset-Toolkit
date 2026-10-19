# SIIG Asset Toolkit 2.4.0 release notes

Version 2.4.0 advances the remaining stage, animation, and shader research while preserving conservative confidence labels.

## New decoders

- Corrected standalone ANM records to `name[16] + start frame + end frame + loop flag` and exports runtime groups/clips.
- Added `stage3dmap` for 0x118-byte Bmap/Xmap/map4/map5 path cells, four GMX placements, 800-unit bounds, five auxiliary vectors, CSV, JSON, and OBJ path output.
- Added `stagewall` for wall/Xwall repeat strips and `stage_generate.bin` enabled candidates.
- Added `shader-info` for Xbox 360 Xenos stage detection, bounded microcode extraction, header inventory, profile/compiler metadata, and hashes.
- `scan` recognizes all of these formats.
- `rip-game` exports all four automatically into `structured/`.

## DAT refinement

- `SCROLL_01` and `SCROLL_02` now expose the actually read 8.8 fixed-point value rather than speculative timing labels.
- `SCROLL_03` is documented as a diagnostic-only no-op in the June 10 analyzer.

## Validation

- 15/15 built-in tests pass.
- 3 ANM files / 160 records / 130 groups parsed.
- 47 3D path files / 19,563 active records / 23,830 placements parsed.
- All 77 unique referenced placement models resolve to supplied GMX files.
- 30 wall/generator tables parsed.
- 16/16 compiled shaders inventoried.
- All 77 stage table files are byte-identical between the June 10 prototype and retail corpus.

## Remaining limits

- Xenos microcode is preserved but not instruction-disassembled.
- Auxiliary vector roles and complete runtime stage playback remain unresolved.
- The three 2D MAP layers still lack complete frame-by-frame scroll reconstruction.
