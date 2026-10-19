# SIIG Asset Toolkit 2.8.0-dev27

## GMX scene-graph compiler

- Added `gltf2gmx-template --sync-scene-graph`; it implies dev26 whole MESH/ARRY synchronization.
- New SHAD records can be synthesized from the known fixed native record.
- New MTRL records clone a proven template parameter schema and can import known PBR diffuse/alpha/emissive/sampler values.
- New BONE records can be created from glTF nodes and wired to native material/mesh identities.
- PARE child lists can be extended/rebuilt for glTF node hierarchy changes.
- Existing BONE transform bytes remain untouched unless `extras.gmxImportTransform` opts into transform import.
- Final graph checks now cover SHAD/MTRL/BONE identity uniqueness plus MTRL→SHAD, BONE→MTRL/MESH, and PARE→BONE validity.

## Workbench / inspection

- GMX Workbench adds a separate **Sync BONE/PARE + material/shader scene graph** advanced checkbox.
- Added `gmx-scene-report` and a Workbench action producing a self-contained HTML scene relationship report plus JSON sidecar.
- GUI version is `0.3.0-dev27`.

## Validation

- Dependency-free suite: **73 tests**.
- Dev27 synthetic structural gate: byte-identical scene-sync no-op; new SHAD 6; new MTRL 5; new BONE 9; new MESH 7 with fresh ARRY nodes; edited cloned material diffuse color; new BONE 9 attached below BONE 0 through PARE.
- Dev25 external retail evidence remains inherited: 306/306 mesh-bearing GMXs no-op round-trip byte-identically plus the `plr_001.gmx` topology smoke. Proprietary corpus inputs are not bundled or re-run as part of this source-only dev27 package.

## Remaining boundary

- TXIF creation is not implemented.
- MTRL synthesis clones an existing proven parameter layout rather than inventing arbitrary native parameter schemas.
- MESH synthesis still clones a compatible native vertex declaration.
- MOTN/ANIM scene/animation graph synthesis and broader glTF animation import remain future work.
- Xenos/RSX shader microcode compilation is not implemented.
- Full template-free GMX creation and runtime acceptance of arbitrary synthesized scenes remain unproven.
- Audio replacement/rebuilding remains intentionally deferred.
