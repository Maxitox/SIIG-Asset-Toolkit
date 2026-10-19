# SIIG Asset Toolkit 2.9.0-dev5

`2.9.0-dev5` extends the donor-free MOTN/ANIM compiler introduced in dev4 from one target bone per glTF animation to full multi-bone authoring clips, while adding glTF `CUBICSPLINE` interpolation.

## New in dev5

- One glTF animation may contain translation/rotation/scale channels for several BONE nodes. The importer expands that authoring clip into synchronized native MOTN/ANIM pairs, one per target BONE, using one shared 30 Hz runtime timeline.
- `CUBICSPLINE` samplers are supported for translation, rotation and scale. The importer evaluates glTF Hermite curves with interval-scaled tangents; quaternion cubic samples are normalized after component-wise Hermite evaluation.
- Import reports record the source clip name, per-clip track index/count and interpolation set. This is provenance only: no native SIIG named clip container has been proven, so the toolkit does not invent one.
- Existing exporter-generated native tracks still preserve their MOTN/ANIM bytes by default through `extras.gmxMotionIndex`. Explicit replacement remains single-track because a scalar native identity cannot safely designate several per-bone tracks.
- Mod Workspace `mod-import-gltf` and the GUI animation-sync path inherit the new behavior automatically.

## Validation

The new root-only regression creates two BONEs and one two-bone glTF clip. The root uses CUBICSPLINE translation/rotation and the child uses LINEAR translation. Import produces two 31-frame native tracks, verifies the cubic Hermite midpoint (`x = 1.5` at 0.5 s), verifies normalized cubic quaternion output, exports both tracks to glTF, and proves the untouched animation-aware reimport is byte-identical. The dependency-free suite is **79/79**.

## Remaining boundary

The native format is still template-hosted at the GMX root/opaque-chunk level, and no native named animation-clip container has been proven. Platform shader compilation and remaining opaque GMX semantics are unresolved. Runtime acceptance of arbitrary synthesized animations remains an external emulator/hardware gate. Audio replacement/rebuilding remains deliberately deferred.
