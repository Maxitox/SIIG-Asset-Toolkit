# Project versioning policy

The toolkit keeps the existing `MAJOR.MINOR.PATCH-devN` naming style, but development suffixes are no longer allowed to grow indefinitely.

- **MAJOR**: a compatibility/project-era break or a fundamental redefinition of the toolkit.
- **MINOR**: a coherent new user-facing capability track (for example, moving from low-level GMX graph synthesis to an integrated Blender/glTF -> native mod workflow).
- **PATCH**: stabilization, bug-fix, validation, packaging, or documentation releases that do not open a new feature track.
- **`devN`**: short-lived checkpoints inside the current target version.

## Development checkpoint rule

A minor-version review is required **no later than `dev8`**. If the active work has already crossed into a materially different user-facing capability, the minor version should be advanced earlier rather than continuing `dev9`, `dev10`, and so on. The suffix resets to `dev1` after a minor bump.

This is a project convention rather than a claim of strict SemVer prerelease syntax. The existing `-devN` form is retained for continuity with older toolkit packages.

## Current transition

`2.8.0-dev28` is the final sealed checkpoint of the unusually long 2.8 development line. The next feature line began at **2.9.0-dev1**. The 2.9 feature line ended at **2.9.0-dev7**; the current checkpoint is **2.10.0-dev2**.


### 2.9 review status after dev7

Dev7 completes the planned investigation immediately before the mandatory dev8 review. Because the next meaningful work would be another substantial capability track rather than a small stabilization patch, the preferred next development version is **2.10.0-dev1**. A `2.9.0-dev8` should be used only if needed for stabilization/release-gate fixes rather than new feature expansion.


### 2.10 feature line

`2.10.0-dev1` opens the next substantial GMX authoring track. Its first capability is rigid non-identity inverse-bind rebaking for Blender/glTF armatures. The same dev8 review rule applies to 2.10.


### 2.10.0-dev2

Dev2 extends the rigid-authoring track with joint-island partitioning and adds a separate evidence-bounded multi-GMX assembly/viewing workflow. This remains within the 2.10 capability line.
