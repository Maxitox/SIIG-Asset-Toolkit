# SIIG Asset Toolkit 2.10.0-dev2

## Highlights

- Partition disjoint rigid joint islands from one Blender/glTF mesh into separate native SIIG MESH/ARRY + BONE attachments.
- Preserve per-joint affine inverse-bind rebaking; reject cross-joint triangles and true blended weights.
- Assemble multiple GMX files into one glTF scene using explicit instance matrices.
- Add a PROGRESSIVE UFO assembly template with proven membership/count: 1 body + 2 laser machines + 2 barrier machines. Exact four side placements remain unresolved and are not guessed.
- GUI 0.13.0-dev2 adds assembly controls.
- 84/84 selftests before release packaging.

## Evidence boundary

The assembly exporter is structurally proven with synthetic transformed instances. The exact runtime transforms for PROGRESSIVE UFO side components are not yet recovered from an authored/executable source, so its built-in manifest intentionally cannot be exported until those matrices are filled.
