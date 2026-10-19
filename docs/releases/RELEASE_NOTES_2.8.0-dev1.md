# SIIG Asset Toolkit 2.8.0-dev1 development notes

This development build consolidates the previously separate package/PS3/runtime-explorer research into the maintained source tree.

## Completed

- Direct original retail Xbox 360 LIVE and PS3 PKG validation.
- Internal authenticated SIIG SDAT decryption.
- Built-in PS3 Sony SBlk v3 / PS-ADPCM WAV export (84 streams).
- Optional OpenSSL finalized-PKG acceleration with Python fallback.
- Content-addressed outer-package resume cache.
- STFS CON initialization fix.
- Stage Explorer v5 runtime scrolling (92 entries, 78 runtime pairings, 468 scroll events).
- PS3 EBOOT-derived placement/route/scroll/timing corrections.
- 23/23 dependency-free self-tests.
- Asset Viewer retained-native placeholders for WMA/XACT data; zero missing preview thumbnails on both retail validation rips.
- Cross-platform Stage Explorer root detection for Xbox `Media` and PS3 `USRDIR`.

## Current retail validation

Xbox resumed regression: 94 outer files, 23 BBX archives skipped as exact matches, 2,593 resources, 899 PNGs, 47 OBJs retained, 86 WAVs, 53 WMA files, zero errors/hash mismatches/privacy findings. Stage Explorer v5: 92 entries / 78 runtime pairings. Asset Viewer: 7,355 indexed files and 3,520/3,520 previewable thumbnails. Verified output manifest: 9,855 files / 897,687,346 bytes, all hashes checked.

PS3 resumed regression: 88 outer files, 2,593 resources, 84 WAVs, six internally decrypted SDATs / 18 authenticated blocks, zero fallback decryptions, zero unsupported resources/errors/privacy findings. Stage Explorer v5: 92 entries / 78 runtime pairings. Asset Viewer: 8,264 indexed files and 3,991/3,991 previewable thumbnails. Verified output manifest: 11,195 files / 886,220,630 bytes, all hashes checked.

## Not yet a final release

Original project licensing remains undecided; Blender UI validation and deeper runtime/shader research remain open. Source-only release packaging and final manifest validation are performed separately before publication.
