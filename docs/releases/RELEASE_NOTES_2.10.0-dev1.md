# SIIG Asset Toolkit 2.10.0-dev1

This release opens the 2.10 development line with rigid non-identity inverse-bind rebaking for Blender/glTF skins.

## New

- Rigid single-joint `JOINTS_0` / `WEIGHTS_0` imports may use an affine non-identity selected `inverseBindMatrices` entry.
- `POSITION` is rebaked into joint bind-local space through the selected inverse-bind matrix.
- `NORMAL` is transformed with the inverse-transpose 3×3 and renormalized.
- Singular bind transforms are rejected when a valid normal transform cannot be computed.
- The same path works for template-backed native layouts and fully synthesized MESH/ARRY schemas.
- Compiler reports expose whether geometry was rebaked and retain the selected inverse-bind matrix as structural provenance.

## Evidence boundary

This does not add or claim native blended skinning. Retail evidence continues to show rigid BONE→MESH attachment, no JOINT/WEIGHT ARRY streams, and `MESH.skin_index = 0xFFFF` in the checked player/enemy corpus. Multi-joint/blended weights remain rejected.

## Validation

The dependency-free suite is **82/82**. The new regression numerically verifies translated/non-uniformly-scaled POSITION rebaking, inverse-transpose NORMAL handling, root AABB repair, report provenance, rigid re-export, and explicit singular-matrix rejection. External dev25 306/306 retail no-op evidence remains inherited rather than rerun from proprietary inputs.
