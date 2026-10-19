# SIIG Asset Toolkit 2.8.0-dev26

Dev26 advances the GMX reverse compiler from topology changes *inside* fixed native meshes to opt-in creation/deletion of whole native mesh graph nodes.

## GMX mesh graph

- `gltf2gmx-template --sync-mesh-graph` treats the glTF mesh list as the desired native MESH set.
- Existing `extras.gmxMeshIndex` meshes are rebuilt in place.
- Omitted native meshes are deleted only in explicit sync mode.
- New glTF meshes synthesize fresh MESH plus ARRY nodes by cloning a compatible native layout; `extras.gmxCloneMeshIndex` can force the donor.
- ARRY deletion respects cross-mesh references.
- Existing BONE mesh attachments are removed/replaced when necessary; `extras.gmxAttachBoneIndex` may attach a new mesh to an existing bone when that does not conflict with a retained mesh.
- Final verification detects duplicate identities and dangling MESH/ARRY/BONE references.

The default importer remains dev25-compatible and does not synchronize graph identities unless requested.

## GUI

The GMX Workbench now exposes an advanced **Sync native MESH/ARRY graph** checkbox. The GUI still delegates all parsing/building to `siig_toolkit.py`.

## Validation

- Built-in regression suite: **72/72**.
- Dev26 structural graph fixture: byte-identical sync no-op; complete mesh addition with fresh ARRY identities; complete attached-mesh replacement/deletion; BONE reference repair.
- Dev25 external retail evidence is inherited: 306/306 applicable GMX no-op glTF round-trips byte-identical, plus the real `plr_001.gmx` vertex/index-count topology smoke.

## Remaining GMX boundary

New BONE/PARE/MTRL/SHAD graph nodes are not synthesized. New geometry still clones a compatible template vertex declaration, and arbitrary from-scratch GMX construction remains future work. Runtime acceptance of arbitrary heavily modified models on retail executable/hardware also remains a separate validation gate.

Audio replacement/rebuilding remains deferred by current project priority.
