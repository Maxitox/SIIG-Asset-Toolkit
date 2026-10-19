# SIIG Asset Toolkit 2.10.0-dev13

Dev13 resolves the persistent structural body of **VERTEBRATE** as two exact executable-backed phase presets.

## VERTEBRATE phase 1

`vertebrate_phase1_tower` exports the immense tower as **32 visible instances**: two `bos_017.gmx` endcaps (AA) plus thirty `bos_017a.gmx` pillar sections (DB). The pillar loop is `Y=-630+70*i` for `i=0..29`; lower/upper cap placements are `(0,-608,0), Z=180°` and `(0,1448,0), Z=0°`.

## VERTEBRATE phase 2

`vertebrate_phase2_endcaps` represents the post-collapse body. All thirty DB pillars are gone. The two AA endcaps are rebased at the boss-local origin with effective Z rotations **90° and 270°** after the 120-frame collapse transition.

## Attack auxiliaries stay separate

Fresh retail extraction confirms `bos_017c..j` are large authored attack rigs carrying 22–25 native animation tracks each. `bos_017b..j` are therefore not bundled into either structural body preset. This avoids turning transient attacks into fake persistent tower geometry.

## Real-asset validation

Fresh retail exports validate:

- phase 1: 32 instances, 64 meshes, 128 nodes, bounds approximately `X/Z ±63.8553`, `Y -715.5933..1483`;
- phase 2: 2 instances, 4 meshes, 8 nodes, centered at the origin.

GUI **0.24.0-dev13** adds VERTEBRATE phase selection and manifest/export actions in Simple and Advanced modes. The regression suite is **95/95** through development gating.
