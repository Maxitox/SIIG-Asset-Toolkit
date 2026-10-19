# SIIG Asset Toolkit 2.10.0-dev7

## Main result

Dev7 resolves HORNET's following **state-6 propagation attack** as a deterministic procedural family across June Xbox, retail Xbox and retail PS3.

State 6 inherits the earlier prism-wall A1 slot from the same 13 runtime-valid choices. State 5 first resets all 45 grid-record selection/display flags and hides A1. State 6 then starts with the inherited seed only and alternates **orthogonal → diagonal → orthogonal → diagonal** expansion until every cell has been reached.

Visible activation snapshots contain reached **C0 prisms only**. A1 remains hidden. Snapshot transforms use the exact recovered 5×9 grid and zero extra Y rotation at activation; transient beam effects and the subsequent turn toward 45° are not frozen into arbitrary static geometry.

Catalog keys are procedural: `hornet_propagation_SS_wave_WW`. Invalid seeds, out-of-range waves and unqualified `hornet_propagation` are rejected rather than silently selecting a runtime outcome.

## GUI

GUI `0.18.0-dev7` keeps deterministic full-armor HORNET in Simple mode and the dev6 13-way prism wall in Advanced mode. Advanced GMX Workbench now also exposes **Propagation seed** and **Propagation wave** selectors plus propagation-manifest/assembly actions. The seed selector is limited to the same 13 runtime values.

## Validation

- dependency-free regression suite: **89/89**;
- all 13 propagation families are checked for exact wave counts, monotonic reachability and complete 45-cell termination;
- representative synthetic `seed 22 / wave 3` export verifies 29 C0 roots, exact grid positions, hidden A1 and no accidental animation;
- external real-retail representative export: **29 instances / 58 meshes / 116 nodes**, no animation, real `bos_008b.gmx` hash retained;
- source-only release policy remains unchanged; executable/Ghidra/retail GMX inputs are validation evidence only and are not bundled.

## Remaining boundary

The propagation assembly captures each wave's **activation instant**. Runtime laser/beam effects and transient 0→45° prism rotation are not static GMX instances and remain intentionally outside the assembly snapshot.
