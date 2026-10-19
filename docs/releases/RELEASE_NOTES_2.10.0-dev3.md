# SIIG Asset Toolkit 2.10.0-dev3

## Highlights

- Recovered the actual first runtime formation for PROGRESSIVE UFO from executable code rather than visual approximation.
- Confirmed runtime object order `A2, C2, C2, C3, C3` and exact local transforms: body `(0,0,0)`, lasers `(-90,0,-10)` / `(90,0,-10)`, barriers `(-160,0,-50)` / `(160,0,-50)`, all with zero local rotation and unit scale.
- Cross-checked the formation independently in June 10 Xbox, retail Xbox, and retail PS3 executable/Ghidra evidence.
- Filled the built-in `progressive_ufo` assembly catalog with the recovered glTF column-major matrices.
- Added `gmx-assemble-catalog progressive_ufo` for direct export without manually creating/editing a manifest.
- GUI 0.14.0-dev3 adds one-click **Assemble PROGRESSIVE UFO**.
- Added a five-instance export regression that verifies all recovered matrices survive through the combined glTF scene. Suite: 85/85.

## Evidence boundary

The preset represents the first recovered five-part formation targeted by the boss state machine over 60 frames. Later dynamic Progressive UFO formations/movement targets are not collapsed into this static preset. Assembly export remains a viewing/editing scene; it does not claim the retail game stores or accepts one merged native GMX.

No executable, Ghidra export, GMX asset, screenshot, or other proprietary game payload is bundled. The release retains only derived addresses, constants, normalized fingerprints, matrices, documentation, and synthetic regression fixtures.
