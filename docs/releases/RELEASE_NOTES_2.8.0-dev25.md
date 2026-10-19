# SIIG Asset Toolkit 2.8.0-dev25

Dev25 makes GMX the primary technical target and introduces the first unified desktop GUI. Audio replacement/rebuilding is intentionally deferred.

## GMX topology compiler

- Added `gltf2gmx-template` for edited glTF -> native GMX geometry import while preserving an existing GMX chunk/material/bone graph.
- Vertex and index counts may now change. The compiler rebuilds native `ARRY` chunks, preserves 0x10 alignment, updates `MESH.index_count`, GMX total size, and root geometry AABB.
- A no-edit GMX -> glTF -> GMX sweep passes byte-identically on **306/306 mesh-bearing retail GMXs**. The 307th corpus GMX (`bos_008c.gmx`) contains no `MESH` chunk and is not applicable to geometry import.
- A retail `plr_001.gmx` topology smoke edit changed one mesh from 328->329 vertices and 656->658 indices, resized the native file 49,600->49,680 bytes, and correctly expanded the root AABB.
- The remaining boundary is explicit: mesh/chunk graph creation/removal, from-scratch material/bone graph synthesis, and broader animation import are not yet implemented.

## Desktop GUI

- Added `siig_gui.py` and `SIIG_GUI.bat`, using only standard-library Tkinter.
- Added four workflow tabs: **Game Rip**, **Mod Workspace**, **GMX Workbench**, and **Utilities**.
- Long toolkit tasks run in a background thread and stream the existing CLI output into a shared task log instead of freezing the window.
- The GMX workbench exposes inspection, GMX->glTF, topology-changing glTF->GMX, editable JSON export/build, and UV-flip control.
- The GUI remains a thin wrapper over the same audited CLI/parser/builder code; no duplicate format implementation is introduced.

## Validation

- Expanded the dependency-free suite from 69 to **71 tests** with GMX topology-compiler and GUI smoke gates.
- Added derived external-retail GMX import validation; proprietary test inputs remain outside the release.
- Existing dev24 `.siigmod`, mod-workspace, 2,197 no-edit asset round-trip checks, and source-only constraints are inherited.
