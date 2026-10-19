# SIIG Asset Toolkit 2.10.0-dev5

## Highlights

- Added executable/model-backed **HORNET — Full Armor / Revealed Lattice** assembly: A1 core plus exactly 125 BF armor cubes in the recovered C1 sample-0 5×5×5 formation.
- Resolved `bos_008c.gmx / C1` as a real meshless 126-track formation controller, not a corrupted model. The runtime also creates 125 C0 prism objects in a parallel pool; those remain excluded from the full-armor snapshot because they are dormant until later phases.
- Changed the beginner/default **CRAB** preset to its deterministic first landed/combat-ready sample 1. The dev4 airborne first-visible sample 167 remains available as `crab_first_visible` and its historical evidence files remain unchanged.
- Confirmed the slightly rotated PROGRESSIVE UFO barriers are intentionally authored inside `bos_009b.gmx`; the recovered outer C3 rotations remain zero.
- GUI 0.16.0-dev5 adds one-click **Assemble HORNET** while retaining Simple/Advanced mode and contextual help.
- Native game coordinates/scale remain authoritative. The docs now call out Blender **Frame All / Frame Selected** rather than applying a speculative unit conversion or hidden display scaling.
- Regression suite: 87/87; final release package independently re-verifies the suite.

## HORNET preset

`hornet_full_armor` exports 126 visible instances. A1 is baked at native sample 0. The 125 identical BF armor objects occupy every point in the Cartesian product of axis values ±31.68, ±15.84 and 0. Evidence is independently recovered from June Xbox, retail Xbox and retail PS3 runtime code plus the retail C1 animation rig.

The meshless C1 controller and dormant C0 pool are represented in research/provenance records rather than as useless/incorrect visible objects. The dynamic 45-slot C0 prism attack remains a later assembly target.

## CRAB preset refinement

Project-owner Blender validation confirmed the dev4 sample-167 reconstruction looked like the game but was far above the ground because it is genuinely an airborne intro frame. Dev5 chooses A7 sample 1—the first frame of the landed looping combat segment—as the default. This is a recovered runtime state, not manual recentering.

## Evidence boundary

No proprietary executable, Ghidra export, GMX/ANM asset, generated retail assembly or gameplay footage is bundled. The HORNET and CRAB catalogs are static snapshots of specifically documented runtime states; they do not claim to reconstruct every dynamic boss phase.
