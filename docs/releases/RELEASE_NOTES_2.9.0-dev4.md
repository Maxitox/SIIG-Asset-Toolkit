# SIIG Asset Toolkit 2.9.0-dev4

`2.9.0-dev4` removes the GMX animation-donor requirement for the supported matrix-track family. The toolkit can now compile ordinary glTF translation/rotation/scale channels into new native `MOTN` + `ANIM` records at the 30 Hz logical-frame cadence proven from the SIIG runtime.

## New animation compiler

- `gltf2gmx-template --sync-animation-graph` creates fresh native motion identities and matrix tracks.
- New animated glTF nodes may simultaneously synthesize their native BONE records.
- LINEAR and STEP TRS channels are supported; rotations use shortest-path quaternion interpolation.
- `extras.rawMotionDuration` controls the MOTN duration when supplied.
- Existing exported animations remain byte-preserved unless `extras.gmxReplaceNativeAnimation=true` opts into replacement.
- `mod-import-gltf` enables the animation compiler automatically alongside the existing GMX/TEX/BBX pipeline.
- `gmx-scene-report` now includes MOTN/ANIM target/frame/duration relationships.

## Regression proof

A root-only synthetic GMX with no BONE/MOTN/ANIM donors receives a new animated bone and a new 31-frame native track from three glTF keys over one second. The midpoint/final native matrices reproduce the authored translation keys, the track exports back to glTF, and the exported animation then reimports byte-identically when left untouched.

The built-in dependency-free suite contains 78 tests. Existing dev3 TEX synthesis and all earlier release gates remain inherited and regression-covered.

## Remaining boundaries

Animation import currently supports one target BONE per glTF animation and LINEAR/STEP TRS channels. Multi-bone glTF clips, CUBICSPLINE interpolation, fully template-free GMX root construction, and platform shader compilation remain future work. Audio replacement remains deliberately deferred.
