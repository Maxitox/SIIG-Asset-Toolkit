# VERTEBRATE structural reconstruction — 2.10.0-dev13

Dev13 resolves the two persistent body configurations requested for VERTEBRATE from retail Xbox, June 10 Xbox and retail PS3 executable behavior, then validates them against freshly extracted retail `bos_017*` GMXs. No screenshot/symmetry placement is used.

## Phase 1 — immense tower

The structural body contains exactly **32 visible model instances**: two `bos_017.gmx` endcaps (runtime root family `0xAA`) plus thirty `bos_017a.gmx` pillar sections (`0xDB`). The pillar loop is `Y = -630 + 70*i` for `i=0..29`, so it spans `-630..1400`. The lower endcap is at `(0,-608,0)` with a 180-degree Z rotation; the upper endcap is at `(0,1448,0)` at native orientation.

A fresh retail export produces 32 instances, 64 meshes and 128 nodes. Its world bounds are approximately `X/Z ±63.8553`, `Y -715.5933..1483`.

## Phase 2 — endcaps only

During the transition all thirty DB pillar records are removed/shrunk. After the 120-frame collapse/rebase, the two remaining `bos_017.gmx` endcaps occupy the same boss-local origin. Their effective final Z rotations are **90° and 270°**; the 180° separation is inherited from the phase-1 lower-cap orientation.

A fresh retail export produces 2 instances, 4 meshes and 8 nodes, centered around the origin.

## Why `bos_017b..j` are excluded

The remaining files are separate runtime attack auxiliaries, not persistent tower sections. Fresh retail inspection shows `bos_017c..j` are large authored rigs carrying 22–25 native animation tracks each. The structural presets therefore include only the body membership proven by construction/collapse code.

See `reference/tables/VERTEBRATE_BODY_ASSEMBLY_DEV13.csv`, `reference/tables/VERTEBRATE_ASSET_ROLES_DEV13.csv`, `reference/tables/VERTEBRATE_PHASE_TRANSITION_DEV13.csv`, and `validation/VERTEBRATE_RUNTIME_ASSEMBLY_2.10.0-dev13.json`.
