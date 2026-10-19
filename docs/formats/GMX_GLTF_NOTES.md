# GMX → glTF notes

Version 1.5 adds a glTF 2.0 exporter for the game's GMX scene/model files. Unlike the older OBJ exporter, this path preserves the GMX scene graph, material assignments, vertex colors, and embedded transform animation tracks.

## Confirmed GMX relationships

GMX is a sequential big-endian chunk stream. The exporter uses these confirmed links:

- `TXIF` records name texture resources such as `ptn_001.dds`.
- `SHAD` records name the material shader (`no_texture` or `texture` in the supplied corpus).
- `MTRL` records reference one `SHAD` and contain typed parameters.
- `PARE` records store a signed parent bone index followed by its child bone indices.
- `BONE` records contain a 4×4 local transform and encoded material/mesh attachments.
- `MESH` records reference position, normal, UV, color and index `ARRY` records.
- `MOTN` records describe one motion track and its duration.
- `ANIM` records target one bone and store key times followed by one 4×4 transform per key.

### BONE attachment references

The final 16 bytes of a `BONE` record contain an attachment count and encoded references:

```text
high 16 bits  2  → MTRL index
high 16 bits  3  → MESH index
low  16 bits     → referenced record index
```

Every mesh-bearing bone in the supplied corpus has one material reference and one mesh reference.

### PARE hierarchy

```text
+0x10  u32  child count
+0x14  s32  parent bone index (-1 means scene root)
+0x18  u32[] child bone indices
```

### Material parameters

After the fixed MTRL header, each parameter has a 48-byte name and two 32-bit fields:

```text
type 0  float scalar/vector; second field is component count
type 1  4×4 matrix array; second field is matrix count
type 2  texture sampler; second field is TXIF index
```

Observed parameters are `mWVP`, `DiffuseSampler`, `DiffuseColor`, `DiffuseAlpha`, and `EmissiveColor`.

### Animation tracks

```text
ANIM +0x08  encoded motion index (index in upper 16 bits)
ANIM +0x10  target BONE index
ANIM +0x14  channel type (12 in every supplied file)
ANIM +0x18  key count
ANIM +0x1C  values per key (16 in every supplied file)
ANIM +0x20  float32 key times
             followed immediately by key_count × 16 float32 matrices
```

BONE matrices use the engine's row-vector storage convention. ANIM matrices use the transposed conventional row-major form. The exporter normalizes both conventions and decomposes each animation matrix into glTF translation, quaternion rotation, and scale channels.

## glTF output

For each input GMX, the exporter writes:

```text
model.gltf       JSON scene description
model.gltf.bin   geometry and animation buffers
model.gltf.json  conversion summary/diagnostics
_textures/       converted texture dependencies when present
```

The glTF contains:

- indexed triangles and lines;
- positions, normals, UVs and vertex colors;
- GMX bone hierarchy as glTF nodes;
- mesh attachment to the correct bone;
- diffuse color, alpha, emissive color and texture assignment;
- `KHR_materials_unlit` materials, matching the simple SIIG shader parameter set;
- one glTF animation per GMX `ANIM`/`MOTN` track.

The supplied textured GMX files all reference `ptn_001.dds`, an uncompressed 128×128 ARGB8888 DDS. The exporter converts it to PNG automatically when the DDS is available in the GMX directory or a `--texture-root` search directory.

## Usage

```bat
python siig_toolkit.py gmx2gltf "C:\path\to\extracted" -o gltf
```

When texture files live elsewhere:

```bat
python siig_toolkit.py gmx2gltf "C:\path\to\gmx" -o gltf --texture-root "C:\path\to\all_extracted_assets"
```

Directly during BBX extraction:

```bat
python siig_toolkit.py extract "C:\path\to\3ddata" -o extracted --convert-gltf
```

Add `--flip-v` only when the destination application expects inverted V coordinates.

## Validation

The final exporter was run over the complete supplied `3ddata` corpus:

```text
486 GMX files
1,938 meshes/primitives
3,298 hierarchy nodes
776 materials
913 animation tracks
0 conversion failures
0 hierarchy cycles or unreachable nodes
0 missing texture references
```

Representative static, textured, multi-mesh and animated files were also loaded with an independent glTF reader.

## Limitations

- The GMX files do not contain per-vertex skin weights; geometry is attached rigidly to scene nodes rather than exported as a skinned mesh.
- Each `ANIM` chunk is exported as its own animation. The engine may trigger several tracks together during gameplay; that higher-level grouping is not stored explicitly in the GMX chunk stream recovered so far.
- The source shader programs are not translated to equivalent custom glTF shaders. Materials use standard unlit PBR fields so they remain portable.
- Standalone `.anm` resources, if encountered outside GMX, are not handled by this exporter.

## Metadata privacy

As of toolkit v1.5.1, companion `.gltf.json` files contain only the glTF filename,
not the absolute source or output directory. The glTF document itself uses relative
URIs for `.bin` buffers and textures.


## Native template editing (dev22)

Dev22 adds a conservative reverse path for an **existing fixed-layout GMX**:

```bat
python siig_toolkit.py gmx-edit-export model.gmx -o model.gmx.edit.json
python siig_toolkit.py gmx-build model.gmx.edit.json --template model.gmx -o model_mod.gmx
```

The `SIIG_GMX_TEMPLATE_EDIT_V1` document exposes fixed-count float/ushort arrays, TXIF names, material parameter values, bone names/matrices, motion durations, animation key times, and serialized animation matrices. The builder patches those proven fields in place while retaining chunk order, sizes, references, padding, and all unexposed bytes.

This is deliberately narrower than a general glTF/Blender compiler. Array counts/types, mesh/material attachment topology, shader indices, animation target/channel/frame counts, and new chunk-graph construction remain fixed. The template SHA-256 is enforced by default.

The new native-builder regression uses a structurally representative synthetic GMX fixture. Previous corpus validation still covers reading/exporting 486 supplied GMX files, but a native byte-roundtrip over that real corpus and runtime acceptance of modified GMX files are not claimed by dev22.

## Topology-changing glTF template compiler (dev25)

Dev25 adds the first topology-changing reverse path:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx
```

Unlike `gmx-build`, this path may change the **vertex and index counts** of existing GMX meshes. The compiler maps glTF meshes back to native `MESH` identities (using `extras.gmxMeshIndex` written by `gmx2gltf`), rebuilds the referenced position/normal/UV/color/index `ARRY` chunks, preserves 0x10 chunk alignment, updates `MESH.index_count`, reassembles the sequential GMX chunk stream, updates the root total-size field, and recalculates the root geometry AABB.

The AABB interpretation at GMX root `+0x10..+0x27` was checked against all 13 retail `player.bin` GMXs: the six floats exactly equal min XYZ / max XYZ of decoded `IN.position` arrays in every file.

### Retail no-op validation

The new path was exercised on the external user-supplied retail corpus used by dev24. Of 307 GMX files, 306 contain native `MESH` geometry and are applicable to glTF topology import; **all 306/306 rebuilt byte-for-byte identically after GMX -> glTF -> GMX import with no edits**. The remaining `bos_008c.gmx` contains no `MESH` chunks and is explicitly classified as not applicable rather than a failed geometry import. Proprietary corpus inputs are not bundled.

A separate topology smoke edit on retail `plr_001.gmx` increased one mesh from 328 to 329 vertices and 656 to 658 indices. The native GMX resized from 49,600 to 49,680 bytes, reparsed successfully, and the root max-X bound changed to the injected 20.0 coordinate. This proves structural topology/count rewriting; it does **not** by itself prove arbitrary edited-model runtime acceptance by the retail executable.

### Remaining compiler boundary

The compiler still inherits the template's:

- number and identity of `MESH` / `ARRY` chunks;
- material/shader graph;
- bone attachment graph;
- primitive mode;
- uint16 index representation;
- motion/animation chunk graph.

Therefore dev25 is a topology-changing **template compiler**, not yet a from-scratch GMX graph authoring system. Adding/removing whole native meshes/chunks, synthesizing material/bone graphs, and broader glTF animation import remain the next GMX research targets.
## Whole MESH/ARRY graph synchronization (dev26)

Dev26 extends the topology compiler with an explicit graph-synchronization mode:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx --sync-mesh-graph
```

Without this flag, dev25 behavior is preserved: native `MESH`/`ARRY` identities are inherited from the template. With the flag enabled, the glTF mesh list becomes the desired native mesh set. Existing meshes carrying `extras.gmxMeshIndex` are retained/updated; existing native meshes omitted from the glTF are deleted; and glTF meshes without an existing native identity are synthesized as new `MESH` plus owned `ARRY` nodes.

A synthesized mesh clones one compatible template mesh's proven native vertex declaration/header fields. `extras.gmxCloneMeshIndex` can select the donor explicitly. Fresh uint16 `MESH` and `ARRY` identities are allocated, while geometry payloads come from the new glTF primitive. ARRY deletion is reference-counted, so an array shared by a retained mesh is never removed merely because another mesh was deleted.

Existing `BONE` records are repaired when their mesh target is deleted. A new mesh can request attachment to one existing bone with `extras.gmxAttachBoneIndex`; if the bone already owns a retained different mesh, the compiler rejects the request rather than silently changing scene ownership. New BONE/PARE/MTRL/SHAD records are not created yet.

The final graph verifier rejects duplicate native identities, dangling MESH→ARRY links, mismatched index counts, and dangling BONE→MESH links before emitting success. The built-in dev26 regression proves a byte-identical graph-sync no-op, addition of a second complete mesh graph with fresh identities, and replacement/deletion of an attached mesh with BONE repair.

### Current boundary after dev26

Dev26 is now a **template-hosted mesh-graph compiler**, not merely a fixed mesh-count compiler. It still depends on an original GMX for non-geometry graph/layout knowledge. The next major steps are new BONE/PARE hierarchy nodes, MTRL/SHAD/TXIF relationship synthesis, arbitrary vertex-declaration construction instead of cloning, then eventual from-scratch GMX creation.


## Material/bone/shader scene synchronization (dev27)

Dev27 adds a second, more structural opt-in mode:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx --sync-scene-graph
```

`--sync-scene-graph` implies `--sync-mesh-graph`. The exported glTF now records native `gmxMaterialIndex`, `gmxMaterialFlags`, `gmxShaderIndex`, shader name/flags, `gmxBoneIndex`, `gmxParentBoneIndex`, material/mesh attachments, and the existing mesh identity metadata. In this mode the glTF scene can therefore drive more than geometry.

New materials use a **cloned native MTRL parameter schema** selected with `extras.gmxCloneMaterialIndex` or a deterministic compatible donor. Known glTF PBR values map back to `DiffuseColor`, `DiffuseAlpha`, `EmissiveColor`, and `DiffuseSampler` when those parameters exist in the donor schema. The compiler does not invent unknown native parameter record types or layouts.

A material may reuse an existing native shader or request a new fixed-layout SHAD identity with `extras.gmxShaderIndex`; `extras.gmxCloneShaderIndex` selects a donor record when needed. This synthesizes the known GMX SHAD name/index/flags record only. It does **not** compile Xbox Xenos or PS3 RSX shader microcode.

New glTF nodes attached to synthesized meshes can become native BONE records automatically; an explicit new identity can be requested with `extras.gmxBoneIndex`, and `extras.gmxCloneBoneIndex` selects flags/layout provenance. Material and mesh attachments come from the node's glTF mesh/material relationship. New child nodes extend the native PARE hierarchy. Existing native BONE transforms stay byte-identical unless `extras.gmxImportTransform` is true, which avoids needless float decomposition/recomposition in no-edit round trips.

`gmx-scene-report` writes a self-contained HTML relationship view plus JSON sidecar:

```bat
python siig_toolkit.py gmx-scene-report model.gmx -o model.scene.html
```

The dev27 structural fixture proves a byte-identical full scene-sync no-op and then synthesizes a new SHAD→MTRL→BONE→MESH/ARRY chain, changes the cloned material diffuse color, and inserts the new bone beneath an existing parent through PARE. Final verification rejects duplicate SHAD/MTRL/BONE identities and dangling material→shader, bone→material/mesh, or PARE→BONE references.

### Current boundary after dev27

The compiler is now a **template-hosted scene-graph compiler**. It still depends on an existing GMX for proven mesh vertex declarations, material parameter schemas, opaque PARE prefix bytes, and any animation graph. TXIF creation, arbitrary MTRL parameter-schema construction, arbitrary vertex declarations, MOTN/ANIM synthesis/import, platform shader compilation, and fully template-free GMX creation remain future work. External dev25 retail no-op evidence is inherited; dev27 does not claim that the new arbitrary scene synthesis has yet been runtime-tested on retail hardware/emulator.


## Texture-reference synchronization (dev28)

Dev28 adds the next explicit synchronization level:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx --sync-texture-graph
```

`--sync-texture-graph` implies `--sync-scene-graph`, which in turn implies `--sync-mesh-graph`. The exported glTF records every native TXIF in top-level `extras.gmxTextureRefs` as `{index, flags, name}` regardless of whether the referenced texture image can be found. When a source image is available, the corresponding glTF image and texture also carry `gmxTextureIndex`, `gmxTextureFlags`, and `gmxTextureName`.

During import, `pbrMetallicRoughness.baseColorTexture` is resolved first. Existing native texture metadata is reused when present; otherwise an exact TXIF name match is reused, and a genuinely new Blender/glTF image receives a fresh uint16 TXIF identity. The compiler then patches a compatible donor MTRL's type-2 `DiffuseSampler` to that native TXIF index. A new texture therefore requires a donor MTRL schema that already contains the understood sampler parameter.

The dev28 regression proves a byte-identical TXIF-aware no-op even when the referenced image file is absent, then simulates a Blender-authored `baseColorTexture` with no SIIG identity metadata. The import allocates a new TXIF, rewires `DiffuseSampler`, verifies all type-2 MTRL references, and exposes the relationship in `gmx-scene-report`.

### Current boundary after dev28

The compiler is now a **template-hosted texture/material/scene/mesh graph compiler**. TXIF creation means creation of the GMX texture-reference record only; the external native TEX/DDS payload named by that record remains a separate asset. The remaining structural GMX boundaries are arbitrary vertex declarations, arbitrary MTRL parameter schemas, MOTN/ANIM graph synthesis/import, platform shader compilation, and fully template-free GMX construction. External dev25 retail no-op evidence remains inherited; dev28 does not claim retail runtime acceptance of arbitrary synthesized texture/scene graphs.


## Integrated payload staging (2.9.0-dev2)

`mod-import-gltf` bridges the dev28 TXIF graph compiler to the native TEX and mod-workspace builders. For each glTF `baseColorTexture` that participates in a native material binding, the command resolves the PNG image, chooses an existing TEX payload as the layout donor, rebuilds platform-native TEX bytes, and stages them with the rebuilt GMX.

If the resolved TXIF name is new, the target BBX can gain a new named member. The BBX builder recomputes the entry identifier from the archive hash seed, rebuilds count/name/hash tables and alignment, then reparses the result. `.siigmod` represents this variable-layout archive change as a baseline-dependent archive delta.

This removes the previous dev28 split between “TXIF reference creation” and “manual texture payload workflow” for compatible TEX donors. It does **not** remove the donor constraint: arbitrary TEX layout/header synthesis, arbitrary GMX vertex declarations/material parameter schemas, MOTN/ANIM synthesis, shader compilation, and template-free GMX creation remain future work.


## 2.9.0-dev2 — native schema synthesis

`gltf2gmx-template --synthesize-native-schemas` is the first mode that can create native geometry/material schemas without a corresponding `MESH`/`ARRY` or `MTRL` donor. The option implies texture, scene and mesh graph synchronization, but donor-backed reconstruction remains preferred when a compatible native record exists.

For geometry, standard glTF `POSITION`, `NORMAL`, `TEXCOORD_0`, and `COLOR_0` attributes are mapped to decoded SIIG `IN.position`, `IN.normal`, `IN.texuv`, and `IN.color` ARRY records. A big-endian uint16 index ARRY and a native MESH reference list are generated from scratch. `extras.gmxMeshFlags`, `extras.gmxMeshUnknown14`, and `extras.skinIndex` may override understood header fields. Other/unknown native vertex semantics are still outside the synthesis contract.

For materials, `extras.gmxParameterSchema` may contain a list of decoded parameter descriptors using native type `0` (float scalar/vector), type `1` (one or more 4×4 matrices), or type `2` (TXIF reference). When no explicit schema is supplied, the compiler emits a standard SIIG PBR-oriented schema containing `mWVP`, optional `DiffuseSampler`, `DiffuseColor`, and `DiffuseAlpha`, plus `EmissiveColor` when needed. Novel parameter names are structurally representable, but whether a selected game shader reads them is a runtime/shader-semantic question.

The dev2 regression starts with a root-only GMX and proves creation of SHAD, MTRL, BONE, MESH and ARRY records plus root-AABB repair without any vertex/material donor. This materially reduces template dependence, but does not yet make the compiler fully template-free: TEX platform layouts, MOTN/ANIM graphs, shader microcode, and some opaque/unknown chunk semantics remain donor/runtime dependent.

## 2.9.0-dev3 — donor-free TEX payload synthesis

The Mod Workspace no longer requires a resolvable same-layout TEX donor for a newly created TXIF. When the project platform is known, a linked PNG can be encoded directly into a canonical native TEX. Xbox 360 synthesis uses the tiled `8_8_8_8` / endian-2 / Z,Y,X,W layout confirmed across all supplied Xbox textures, with physical pitch and tiled allocation recalculated from the new dimensions. Existing compatible TEX resources still take the template-preserving encoder first.

PS3 donor-free synthesis emits the understood 0x80-byte linear A8R8G8B8 wrapper and passes structural decode/encode tests, but unknown wrapper bytes have less corpus evidence than the Xbox layout. Treat arbitrary new PS3 textures as structurally synthesized until runtime validation is obtained.

The integrated regression deliberately removes every TEX donor from the source BBX, introduces a 37x19 PNG through glTF, synthesizes a new Xbox TEX, appends it as a BBX member and reproduces the final BBX exactly through the baseline-dependent `.siigmod` path.

## 2.9.0-dev4 — MOTN/ANIM synthesis and glTF animation import

`gltf2gmx-template --sync-animation-graph` can now create native motion tracks without a `MOTN`/`ANIM` donor. The mode implies scene synchronization so every animated glTF node must resolve to a native BONE. Ordinary glTF translation, rotation and scale channels are sampled onto SIIG's proven 30 Hz logical-frame clock and composed into the native channel-type-12 4x4 matrix stream. LINEAR and STEP interpolation are supported; quaternion LINEAR interpolation uses shortest-path spherical interpolation.

A new native track receives a fresh 16-bit motion identity, a fixed 0x20-byte MOTN descriptor, and a fully synthesized ANIM key payload. `extras.rawMotionDuration` may preserve/author the MOTN duration independently of the runtime sample count. `extras.gmxFrameCount` can explicitly control the sampled frame count when a project needs it.

Exporter-generated animations already contain `extras.gmxMotionIndex`. Under animation sync these existing tracks are preserved byte-for-byte by default rather than decomposed and requantized. To deliberately replace one, set `extras.gmxReplaceNativeAnimation=true`; the compiler then resamples the glTF channels and replaces the understood MOTN/ANIM payload for that identity.

The dev4 regression begins with a root-only GMX containing no BONE, MOTN or ANIM records, creates a new animated BONE and 31-frame motion from three one-second glTF keys, exports the result back to glTF, and proves that an untouched animation-aware reimport is byte-identical.

## 2.9.0-dev5 — multi-bone clips and CUBICSPLINE

One glTF animation may now target several BONE nodes. Because the decoded native format exposes one MOTN/ANIM pair per target BONE and no proven named clip container, the importer expands one glTF clip into multiple synchronized native tracks that share the same sampled 30 Hz frame timeline and raw MOTN duration. Clip name/track ordering is retained in the import report rather than invented as a native record.

`CUBICSPLINE` samplers are decoded according to glTF 2.0's in-tangent/value/out-tangent triplets. Translation and scale use cubic Hermite interpolation with tangents multiplied by the key interval; rotation uses the same component-wise Hermite formula followed by quaternion normalization. LINEAR rotation continues to use shortest-path SLERP and STEP behavior is unchanged.

The dev5 regression begins with a root-only GMX, creates two BONEs, imports one two-bone clip whose root uses CUBICSPLINE translation/rotation while the child uses LINEAR translation, and verifies two synchronized 31-frame MOTN/ANIM pairs. The Hermite midpoint is checked numerically, cubic quaternion normalization is verified, and exporting/reimporting the two native tracks remains byte-identical. Explicit `gmxMotionIndex` replacement remains intentionally single-track because a scalar native identity cannot unambiguously name several tracks.
## 2.9.0-dev6 — fully template-free root/scene compilation

Dev6 adds a second compiler entry point for scenes that should not inherit an original GMX at all:

```bat
python siig_toolkit.py gltf2gmx-new new_scene.gltf -o new_scene.gmx
```

`gltf2gmx-new` constructs a canonical 0x30-byte root locally and then runs the decoded schema/graph builders with mesh, scene, texture-reference, native-schema and animation synthesis enabled. No `.gmx` template is opened. The canonical root contract is intentionally limited to fields that are structurally established by the parser/compiler:

- `+0x00`: `GMX\0`
- `+0x04`: root chunk size (`0x30`)
- `+0x08`: still-unnamed 32-bit word; zero by default
- `+0x0C`: total sequential GMX stream size, rebuilt after compilation
- `+0x10..+0x27`: proven min XYZ / max XYZ geometry AABB, rebuilt from `IN.position` arrays
- `+0x28..+0x2F`: still-unnamed eight-byte tail; zero by default

Advanced research can provide `extras.gmxRootUnknown08` and `extras.gmxRootReserved28Hex`; `gmx2gltf` exports those fields as provenance. The option is deliberately named as unknown/reserved data rather than assigning speculative gameplay meaning.

The dev6 regression begins with a plain glTF containing a mesh, PBR material/base-color texture reference, scene node and TRS animation with **no GMX template and no native GMX IDs**. It verifies creation of TXIF/SHAD/MTRL/BONE/MOTN/ANIM/MESH/ARRY records, texture/material/mesh/bone references, 31-frame 30 Hz animation, total-size repair, root AABB, root provenance on glTF export, and explicit unknown-root-byte overrides. The dependency-free suite reaches **80/80**.

### Current boundary after dev6

The decoded GMX container/root is no longer a mandatory donor. Template-backed compilation remains valuable because unknown chunks/bytes can be preserved exactly, whereas a new GMX contains only structures the toolkit knows how to synthesize. Platform shader microcode is still not compiled. Standard glTF skin/joint-weight (`skins`, `JOINTS_0`, `WEIGHTS_0`) import is not yet mapped to SIIG's native skinning structures, and runtime acceptance of fully original scenes remains an external emulator/hardware validation gate.



## 2.9.0-dev7 — rigid glTF skins mapped to native BONE attachment

The supplied GMX evidence does **not** support a conventional per-vertex weighted-skin representation. Earlier full-corpus export research found no per-vertex skin weights, and a dev7 cross-check of the supplied `player.bin` and `enemy.bin` covers 150 retail GMXs / 901 MESH records: every MESH has `skin_index = 0xFFFF`, and every vertex declaration is limited to `IN.position`, `IN.normal`, `IN.texuv`, `IN.color`, plus the uint16 index ARRY.

Accordingly, dev7 does not assign glTF skin semantics to `MESH.skin_index`. `gltf2gmx-template --sync-rigid-skins` and `gltf2gmx-new` accept a glTF skin only when `JOINTS_0`/`WEIGHTS_0` prove that every vertex belongs to the same single joint with weight 1.0. That skin is collapsed to the already-proven native representation: the target joint becomes/uses a BONE and the whole MESH (plus its MTRL) is attached to that BONE. Joint hierarchy reconstruction can skip non-bone armature/container nodes when finding the nearest native parent.

The compiler rejects true blended/multi-joint weights, differing rigid joints across vertices, JOINTS_1/WEIGHTS_1, and non-identity selected inverse-bind matrices. The latter is a deliberate safety boundary: rebaking geometry through inverse-bind transforms can be added later, but dev7 will not silently change vertex-space semantics. Newly synthesized MESH records default `skin_index` to the observed no-skin value `0xFFFF`.

The dev7 regression verifies both sides: a two-joint skin rigidly bound to the child becomes exactly two BONEs plus one child-attached MESH with no invented weight ARRY, while a 50/50 blend is rejected. Native export remains faithful to the resulting rigid scene graph rather than fabricating a weighted glTF skin on the way back out.


## 2.10.0-dev1 — rigid inverse-bind rebaking

The rigid-skin compatibility path now accepts a selected **non-identity affine** glTF `inverseBindMatrices` entry. SIIG still receives no JOINT/WEIGHT ARRY records: the skin is collapsed to BONE→MESH attachment exactly as in dev7, but the mesh is first converted from glTF mesh space into the selected joint's bind-local space.

For a selected inverse-bind matrix `M`, native positions are rebuilt as `M * position`. Native normals use `inverse(transpose(M3x3)) * normal` and are normalized afterward. Translation never affects normals. A singular 3×3 linear component is rejected when a NORMAL stream is present.

This is a rigid-armature compatibility feature, **not** evidence for native blended skinning. `JOINTS_1` / `WEIGHTS_1`, vertices with more than one active weight, and meshes whose vertices resolve to different joints remain errors. `MESH.skin_index` is still not reinterpreted as a glTF skin index; synthesized rigid meshes continue to use the corpus-observed `0xFFFF` no-vertex-skin value unless an existing donor/explicit override is being preserved.

The importer records `inverse_bind_identity`, `inverse_bind_matrix`, `geometry_rebaked`, and mode `rigid-collapse-rebake` in the compiler report. Template-backed donor declarations and donor-free schema synthesis both pass through the same rebake function.


## 2.10.0-dev2 — rigid partitioning and runtime assemblies

A glTF mesh whose triangles form independent rigid islands may assign different islands to different joints. The importer partitions triangles by resolved unit-weight joint, compacts each island's vertex streams, applies that joint's inverse-bind rebake, and emits one native MESH/ARRY graph per joint. Any triangle whose vertices resolve to different joints is rejected because the supplied SIIG corpus has no proven blended-weight representation.

Separate GMX resources can also be combined for viewing/editing with `gmx-assemble`. This is a glTF assembly layer, not a claim that the game stores a single combined GMX. Instance transforms are explicit manifest data and unresolved transforms are rejected. See `docs/guides/GMX_ASSEMBLIES.md`.
