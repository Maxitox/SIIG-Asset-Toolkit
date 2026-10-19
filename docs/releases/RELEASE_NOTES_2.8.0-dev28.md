# SIIG Asset Toolkit 2.8.0-dev28

## GMX texture-reference graph compiler

- Added `gltf2gmx-template --sync-texture-graph`; it implies dev27 `--sync-scene-graph` and dev26 `--sync-mesh-graph`.
- Added fixed-layout native `TXIF` synthesis/update for the fully decoded 0x30-byte index/flags/name record.
- glTF export now stores complete native texture-reference provenance in top-level `extras.gmxTextureRefs` even when the image payload cannot be found. Converted glTF images/textures also carry `gmxTextureIndex`, `gmxTextureFlags`, and `gmxTextureName`.
- In texture-sync mode, a glTF `baseColorTexture` may reuse a TXIF by native metadata or exact native name, or allocate a new native TXIF identity when no match exists.
- Compatible donor MTRL schemas with a type-2 `DiffuseSampler` are rewired to the resolved TXIF identity automatically.
- Post-build guards now reject duplicate TXIF identities and dangling type-2 MTRL→TXIF references.

## Workbench / inspection

- GMX Workbench adds a third default-off advanced checkbox: **Sync TXIF texture bindings (dev28, advanced)**.
- `gmx-scene-report` now includes TXIF inventory and per-material texture-binding relationships.
- GUI version is `0.4.0-dev28`.

## Validation

- Dependency-free suite: **74 tests**.
- Dev28 synthetic structural gate: byte-identical TXIF-aware no-op; a Blender-style replacement `baseColorTexture` with no SIIG native identity extras allocates TXIF 1 and rewires the existing MTRL `DiffuseSampler` from TXIF 0 to TXIF 1; the scene report exposes the new binding.
- Dev25 external retail evidence remains inherited: 306/306 mesh-bearing GMXs no-op round-trip byte-identically plus the `plr_001.gmx` topology smoke. Proprietary corpus inputs are not bundled or re-run as part of this source-only dev28 package.

## Remaining boundary

- TXIF *reference* creation is implemented, but the corresponding native TEX/DDS texture payload must still be created/replaced through the toolkit's separate texture asset workflow.
- MTRL synthesis still clones an existing proven parameter layout; arbitrary material parameter schemas are not invented.
- MESH synthesis still clones a compatible native vertex declaration.
- MOTN/ANIM scene/animation graph synthesis and broader glTF animation import remain future work.
- Xenos/RSX shader microcode compilation is not implemented.
- Full template-free GMX creation and runtime acceptance of arbitrary synthesized scenes remain unproven.
- Audio replacement/rebuilding remains intentionally deferred.
