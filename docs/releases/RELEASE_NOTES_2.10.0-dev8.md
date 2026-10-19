# SIIG Asset Toolkit 2.10.0-dev8

## Main result

Dev8 adds the first fully evidence-backed **MANDALA runtime assembly**. `mandala_initial_combat` freezes the boss at the exact state-7 activation boundary before its first rotational update: **20×B7 + 2×B8 + 2×B9 + 2×BA + 2×BB + 12×4A = 40 visible instances**. The later 32×BC inner phase is intentionally excluded.

The transform reconstruction is cross-checked across May 9 Xbox, May 11 Xbox, June 10 Xbox, retail Xbox and retail PS3. June proves the native signed 8.8 sine/cosine convention; retail proves the slot-to-model dispatch. Structural scale targets are exactly **40 / 56 / 82 / 109 / 4×29 / 4×20**. No speculative radial-facing rotation is applied.

Native GMX animations are preserved. The preset does not bake an arbitrary internal pose sample.

## GUI

GUI `0.19.0-dev8` adds **Assemble MANDALA** to Simple mode and **MANDALA manifest / Assemble MANDALA** to Advanced mode.

## Validation

- dependency-free regression suite: **90/90**;
- exact 40-member runtime-type counts and state-7 membership checked;
- native signed 8.8 trig anchors and radius-109/radius-69 placement checked;
- exact structural scale/position set checked;
- BC exclusion and no invented radial rotation checked;
- source-only release policy unchanged.

During development, the preset was also exercised against the actual retail Xbox GMXs and produced **40 instances / 104 meshes / 240 nodes / 38 preserved native animations**. Proprietary inputs are not bundled.

## Remaining boundary

This is a deterministic **initial-combat snapshot**, not a claim that every later MANDALA phase is represented by one static assembly. The 32 BC pieces belong to a later inner phase and remain outside this preset.
