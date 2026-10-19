# SIIG Asset Toolkit 2.8.0-dev24

Dev24 adds a shareable, baseline-dependent mod distribution layer and substantially expands real-corpus native round-trip evidence.

## Shareable `.siigmod` packages

New commands:

- `mod-pack` — materialize tracked workspace edits and build a deterministic `.siigmod`;
- `mod-package-info` — inspect package metadata and affected resources without applying it;
- `mod-apply` — verify a matching user-owned rip, reconstruct native replacements from binary deltas, and stage them into a normal mod workspace.

The package format intentionally avoids bundling clean source archives/resources. Equal-size replacements use sparse changed-byte runs. Length-changing resources use source-copy plus package-data operations, bounded so a large whole-archive edit is rejected instead of silently turning into a giant replacement package. Baseline, delta payload, and target SHA-256 values are checked during application.

A package application never modifies the clean rip in place. V1 treats overlapping package changes to the same staged resource as a conflict unless the user explicitly supplies `--force`; baseline hashes are never bypassed.

## Retail package validation

The external retail Xbox `text.bin` corpus was used for a distribution-layer test. One readable localization character was changed, compiled to native BBX, packed, applied to a fresh workspace, rebuilt, and verified. The resulting package was 1,184 bytes with a **one-byte binary-delta payload**, and the fresh-workspace rebuilt BBX matched the source workspace byte-for-byte. The retail archive itself is not bundled.

## Expanded native round-trip evidence

The native COL inverse path was also optimized for ordinary opaque black/white mask PNGs by packing eight pixels at a time; arbitrary grayscale/alpha edits retain the original threshold fallback. This made a complete retail wall-collision sweep practical.

`validation/REAL_CORPUS_ROUNDTRIP_DEV24.json` records **2,197 completed byte-identical no-edit rebuild checks** against user-supplied retail files:

- GMX: 307/307 across `player.bin`, `enemy.bin`, `wall.bin`, `route.bin`, and `camera.bin`;
- DAT: 1,258/1,258 from `generator.bin`;
- MAP: 394/394 across generator and level-map archives;
- stage3D route/placement tables: 47/47 from `stage.bin`;
- stagewall/Xwall tables: 30/30 from `stage.bin`;
- TEX: 3/3 from `image.bin`;
- ANM: 2/2;
- COL: 153/153 complete PNG/native builder round-trips across 78,643,200 collision pixels, covering both observed retail layouts/variants;
- systemfont CRP: 1/1 full PNG/native round-trip;
- `text.bin` and `message.bin`: 1/1 each from readable localization exports.

These are losslessness tests, not claims that every arbitrary edit is accepted by retail runtime code. GMX remains fixed-layout/template-preserving and the completed COL sweep covers all 153 retail masks.

## Validation

- dependency-free self-test: 69/69;
- source-only audit remains mandatory before release packaging;
- proprietary retail inputs used for validation remain outside the source release.

## Remaining major boundaries

- PS3 NPDRM/SDAT re-encryption;
- native Xbox XACT/XMA2 replacement-bank authoring;
- native PS3 SBlk/989SND replacement-bank authoring;
- Xenos shader compilation;
- topology/count/chunk-graph-changing glTF/Blender -> GMX synthesis;
- automatic multi-mod semantic merging beyond v1 conflict detection.
