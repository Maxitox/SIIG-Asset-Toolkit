# SIIG Asset Toolkit 2.10.0-dev23

Dev23 implements the project-owner feedback pass over GMX assembly, Game Rip, Visualizer Simulator, Asset Viewer, and Stage Explorer while preserving the sealed dev22 line unchanged.

## Highlights

- Corrected GMX visual-pass applicability and authored ANM clip grouping.
- Added Enemy/Sub-boss assembly support for ENVY, KEEPER, OPPRESSOR, GLUTTONY, VANITY, and TELEPORTER.
- Recovered/updated MANDALA, CENTIPEDE, AXON, CRAB, LADYBUG, ULTIMATE UFO, VERTEBRATE, GIGANTIC UFO presentation, and PROGRESSIVE UFO assembly behavior with executable/native evidence boundaries recorded in research notes.
- Blender add-on 0.2.0 groups logical assembly parts so paired native face/outline meshes can be hidden together without flattening hierarchy.
- Reconstructed June 10 Visualizer Check Mode controls, including X reset, Y debug-text toggle, exact VolumeSet source selection, Fix Rotation range, external preset loading, and decoded sequence quick presets.
- Fixed GUI live-rip repaint starvation and added a dedicated progress display.
- Asset Viewer now supports folder navigation, recursive scoping, and default hiding of redundant converted-model cards.
- Stage Explorer v7 adds World-4 top-down route following, World-5 POV route following, route progress/final-area inspection, pixel-stable 2D rendering, and clearly provenance-tagged gameplay-reference backgrounds.
- One-click Game Rip now continues from an outer ZIP into a single content-detected extensionless Xbox LIVE/CON/PIRS STFS package or PS3 PKG, while ambiguous multi-package ZIPs are rejected.
- Added an optional source-only systemfont-derived local font generator; generated fonts are not distributed.

## Fresh retail validation

Starting from the original Xbox retail ZIP, dev23 completed ZIP -> extensionless STFS -> extracted game -> BBX extraction/conversion with 23/23 archives, 2,593 resources, 1,351 PNGs, 486 glTFs, 86 WAVs, 53 retained WMAs, 92 Stage Explorer entries / 17,335 DAT commands, and 30 Visualizer timelines / 243 commands. `verify-output` checked 16,540 hashes with zero issues.

## Validation boundaries

- Blender add-on 0.2.0 is source/package regression-tested, but a Blender GUI runtime is not available in the release-build environment for manual interaction testing.
- Stage route cameras/backgrounds are inspection aids; gameplay-reference visuals remain separately attributed from executable-derived stage semantics.
- Host-audio Visualizer volume normalization remains an approximation of the game's upstream meter transfer.
- Derived systemfont files are convenience reconstructions, not the original vector authoring font, and are not bundled.
