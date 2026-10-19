# SIIG Asset Toolkit 2.10.0-dev4

## Highlights

- Desktop GUI 0.15.0-dev4 now defaults to Simple mode, with an explicit Simple/Advanced switch and persistent hover/focus explanations for controls.
- Mod Workspace and GMX Workbench have beginner-focused flows while Advanced mode retains the full dev3 expert surface.
- Resolved console opcode `0xA7` as CRAB through explicit entity-registry + `Crab.cpp` construction/runtime linkage. Historical dev19 unresolved records are retained unchanged as historical artifacts.
- Recovered the executable-defined first-visible CRAB formation across June Xbox, retail Xbox and retail PS3.
- Added per-instance `pose_sample` to static multi-GMX assembly export so native animation samples can be baked before outer runtime transforms are applied.
- Added `gmx-assemble-catalog crab`, GUI **Assemble CRAB**, a CRAB manifest action in Advanced mode, and a nine-instance synthetic regression.
- Regression suite: 86/86 before release packaging.

## CRAB preset

The preset contains `1×A7`, `1×CD`, `1×CC`, `2×CE`, and `4×CF`. The A7 root is baked at sample 167 in its `101→239` animation segment and receives the runtime 180° Y transform. The body shell is baked at its still-closed/default sample 0. Child placement is derived from the runtime named-locator path, with the first-visible attachment center at Y `422.0840835571289`, CE offsets ±81 X, and CF offsets ±23 Y from the CE pair.

## Evidence boundary

The CRAB catalog is a static snapshot of one deterministic runtime formation, not a claim that SIIG stores a merged nine-part GMX or that every later combat pose has been reconstructed. Posed instances intentionally suppress their animation channels in the combined glTF so the snapshot remains coherent. No proprietary executable, Ghidra export, GMX/ANM asset, package or footage is bundled.
