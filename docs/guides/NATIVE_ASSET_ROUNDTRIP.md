# Native asset round-trip editing

`2.10.0-dev24` continues the asset-functionalization phase: extracted files are not only decoded for inspection, but can increasingly be edited in ordinary desktop formats and compiled back to native SIIG resources.

The design rule is conservative. When a format contains platform/GPU-specific or still-unproven structure, the builder uses an **original file as a template** and preserves bytes the edit does not need to change. Deterministic full synthesis is used only where the record layout is fully accounted for.

For project-level orchestration of these builders, see [`MOD_WORKSPACE.md`](MOD_WORKSPACE.md).

## Current native-build paths

### TEX: PNG -> native Xbox 360 / PS3 TEX

Template-preserving edits remain the safest path when replacing an existing texture:

```bat
python siig_toolkit.py tex2png ptn_001.tex -o texture_edit
python siig_toolkit.py png2tex texture_edit\ptn_001.png --template ptn_001.tex -o ptn_001_mod.tex
```

`2.9.0-dev3` also supports donor-free layout synthesis for genuinely new textures or changed dimensions:

```bat
python siig_toolkit.py png2tex new_albedo.png --platform xbox360 -o new_albedo.tex
python siig_toolkit.py png2tex new_albedo.png --platform ps3 -o new_albedo_ps3.tex
```

Xbox synthesis uses the one layout confirmed across all supplied retail textures: tiled Xenos `8_8_8_8`, endian 8-in-32, Z/Y/X/W swizzle, 32-pixel pitch alignment and 32-row tiled allocation. Template mode still preserves every original header/padding byte and remains byte-identical for unchanged pixels. PS3 synthesis emits the understood 0x80-byte linear A8R8G8B8 wrapper; its decoder/encoder round-trip is structurally validated, while runtime acceptance of unknown wrapper fields for newly invented textures remains a separate hardware/emulator gate.

### System font: edited atlas -> native CRP

```bat
python siig_toolkit.py font2png systemfont.bin.gz -o font_edit
python siig_toolkit.py png2font font_edit\systemfont_atlas.png --template systemfont.bin.gz -o systemfont_mod.crp
```

This currently edits atlas pixels only; executable glyph metrics are not rewritten.

### DAT: CSV/JSON -> native script

```bat
python siig_toolkit.py dat2csv level5_stage3.dat -o dat_edit
python siig_toolkit.py dat-build dat_edit\level5_stage3.dat.csv -o level5_stage3_mod.dat
```

Raw numeric opcodes/parameters remain editable even when their higher-level semantics are unresolved. Unchanged parse/build is byte-identical.

### MAP: editable JSON -> native byte grid

```bat
python siig_toolkit.py map2png level1_stage1.map -o map_edit --csv
python siig_toolkit.py map-build map_edit\level1_stage1.map.edit.json -o level1_stage1_mod.map
```

Cell bytes preserve the one-based tile ID plus X/Y reflection bits. Unchanged parse/build is byte-identical.

### ANM: CSV/JSON -> native range table

```bat
python siig_toolkit.py anm2csv enemy.anm -o anm_edit
python siig_toolkit.py anm-build anm_edit\enemy.anm.csv -o enemy_mod.anm
```

Model/group name, start/end frame and loop value can be edited.

### COL: PNG -> native one-bit collision mask

```bat
python siig_toolkit.py col2png wall.col -o col_edit
python siig_toolkit.py png2col col_edit\wall.png --template wall.col -o wall_mod.col
```

The original header is preserved and edited pixels are repacked into the native bit mask.

### Stage wall / Xwall / generator tables: CSV/JSON -> native table

Export a table with the existing `stagewall` command, edit the generated CSV or `*.stagewall.edit.json`, then rebuild:

```bat
python siig_toolkit.py stagewall wall.bin -o wall_edit
python siig_toolkit.py stagewall-build wall_edit\wall.bin.stagewall.edit.json -o wall_mod.bin
```

For CSV input, the kind can be forced explicitly:

```bat
python siig_toolkit.py stagewall-build stage_generate.csv --kind generator_candidates -o stage_generate_mod.bin
```

Each native record is completely accounted for as a 16-byte name plus a big-endian 32-bit value. Canonical unchanged records rebuild byte-identically.

### Bmap / Xmap / map4 / map5: editable 3D route/placement JSON -> native table

```bat
python siig_toolkit.py stage3dmap Bmap15.bin -o stage3d_edit
python siig_toolkit.py stage3d-build stage3d_edit\Bmap15.bin.stage3d.edit.json -o Bmap15_mod.bin
```

Every active record is exactly `0x118` bytes: four placement slots, one cell-step vector, and five route/control-point vectors. A fully described edit document can synthesize these records deterministically. To retain any inactive records or tail bytes from an original file, supply the original as a template:

```bat
python siig_toolkit.py stage3d-build Bmap15.bin.stage3d.edit.json --template Bmap15.bin -o Bmap15_mod.bin
```

A zero cell-step remains the native end sentinel and is rejected for active synthesized records.

### GMX: fixed-layout native template editing

Export a native GMX edit document:

```bat
python siig_toolkit.py gmx-edit-export bos_015k.gmx -o bos_015k.gmx.edit.json
```

After editing supported fields, rebuild against the exact original GMX:

```bat
python siig_toolkit.py gmx-build bos_015k.gmx.edit.json --template bos_015k.gmx -o bos_015k_mod.gmx
```

The edit document is `SIIG_GMX_TEMPLATE_EDIT_V1` and carries the template SHA-256 by default. Supported edits preserve counts, chunk order, chunk sizes, and the proprietary chunk graph while allowing changes to:

- fixed-count float/ushort `ARRY` data, including geometry and indices;
- `TXIF` texture-reference names;
- editable `MTRL` float/vector/matrix/texture parameter values;
- BONE names and 4×4 static matrices;
- MOTN durations;
- ANIM key-time values and 4×4 serialized matrices.

Changing array counts/types, material shader indices, attachment topology, animation target/channel/frame count, or constructing arbitrary new chunk graphs is **not** claimed. `--ignore-template-hash` exists only for deliberately applying a document to another structurally compatible template.

The current automated GMX rebuild gate uses structurally representative synthetic fixtures. The supplied retail GMX corpus was previously validated for parsing/export, but dev22 does **not** claim a real-corpus byte-roundtrip or runtime-mod acceptance test for the new builder.

### GMX: topology and whole mesh-graph import

For ordinary geometry edits, use the conservative template importer:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx
```

This may resize vertex/index arrays but preserves native mesh identities. To deliberately synchronize the full native `MESH`/`ARRY` set to the glTF mesh set, opt in explicitly:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx --sync-mesh-graph
```

In mesh-sync mode, omitted native meshes are deleted and new glTF meshes receive synthesized native MESH/ARRY nodes cloned from a compatible template layout. Use `extras.gmxCloneMeshIndex` to choose a donor layout and `extras.gmxAttachBoneIndex` when a synthesized mesh should replace/occupy an existing bone's mesh attachment.

For dev27 scene-graph authoring, opt in one level further:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx --sync-scene-graph
```

This mode implies mesh sync and can clone/create native material/shader relationships, create BONE records, and extend PARE hierarchy relationships. New MTRL records still require a proven donor parameter schema. Use `gmx-scene-report` to inspect the resulting hierarchy and attachments visually before staging a mod.

For dev28 texture-reference authoring, opt in one level further:

```bat
python siig_toolkit.py gltf2gmx-template edited.gltf --template original.gmx -o edited.gmx --sync-texture-graph
```

This mode additionally creates/updates native TXIF records and maps glTF `baseColorTexture` to a compatible MTRL `DiffuseSampler`. It creates the GMX reference/binding only; create or replace the actual native TEX/DDS resource through the separate texture workflow. Animation-graph synthesis remains unsupported.

### GMX: fully template-free glTF -> native GMX (2.9.0-dev6)

For a substantially new scene, no original GMX is required:

```bat
python siig_toolkit.py gltf2gmx-new new_scene.gltf -o new_scene.gmx
```

This path synthesizes the canonical decoded 0x30-byte GMX root, MESH/ARRY declarations, SHAD/MTRL records, TXIF references, BONE/PARE relationships, and MOTN/ANIM tracks as needed. Root total size and geometry AABB are recalculated from the final stream. The root fields at `+0x08` and `+0x28..+0x2F` remain semantically unnamed and default to zero; advanced `extras.gmxRootUnknown08` and `extras.gmxRootReserved28Hex` values can carry research-derived bytes without reintroducing a GMX template.

The template-backed `gltf2gmx-template` command remains the fidelity-first option for modifying an existing game model because it preserves still-opaque chunks/bytes. `gltf2gmx-new` is the independence-first option. Runtime acceptance of arbitrary original scenes and platform shader microcode are external/unresolved gates.

### `text.bin`: TSV/CSV/JSON -> native localization BBX

Decode first:

```bat
python siig_toolkit.py text2csv text.bin -o localization
```

Then rebuild from the recommended `text_strings_raw.tsv` / `text_strings.tsv`, or the legacy CSV / JSON exports:

```bat
python siig_toolkit.py text-build localization\text\text_strings.tsv --template text.bin -o text_mod.bin
```

The native BBX mode, seed/header/identifiers, payload order, newline convention, and trailing-newline behavior come from the template. Readable values collapse real line breaks/tabs back to the game's literal source escapes. Use `--raw` or `--no-raw` to override filename-based raw/readable inference. TSV is preferred for ordinary spreadsheet editing because the tab delimiter does not depend on the system's comma/decimal locale; CSV remains a compatibility/research export.

### `message.bin`: readable Squirrel scripts -> native localization BBX

After `text2csv` produces six `message_<language>_readable.nut` files:

```bat
python siig_toolkit.py message-build localization\message --template message.bin -o message_mod.bin
```

Readable Unicode accents are converted back to SIIG's language-specific single-byte glyph substitutions and then encoded as Shift-JIS. `--raw` instead consumes `message_<language>_raw.nut`. Group/order/count consistency is checked across all six languages before packing.

The current builder byte-identity regressions use canonical synthetic localization fixtures; arbitrary runtime text changes still require emulator/hardware validation.

### PS3 SBlk: flexible WAV -> repacked native PS-ADPCM bank

```bat
python siig_toolkit.py sblk2wav sound.bnk -o ps3_audio
python siig_toolkit.py sblk-replace sound.bnk 12 ps3_audio\edited.wav -o sound_mod.bnk
```

WIP187 extends the original WIP161 fixed-slot encoder into a variable-size bank repacker. Replacement PCM16 WAVs may change duration and sample rate; multichannel input is downmixed to SIIG's native mono stream form. The builder regenerates PS-ADPCM control flags, rewrites the selected stream's pitch metadata, repacks the contiguous audio section, and updates later stream offsets/sizes while preserving untouched stream payload bytes. Structural rebuild does not by itself prove game acceptance, so test modified banks on an emulator/hardware copy.

## Putting edited resources back into BBX

Replace the corresponding native resource inside the directory produced by `extract`, then run:

```bat
python siig_toolkit.py repack-bbx extracted_archive -o modified.bin
```

Use the original `manifest.json`. The repacker preserves/reconstructs named hashes, unnamed identifiers, resource order, BBX mode/seed/reserved header, sorted lookup index, and alignment.

This yields the current modding loop:

```text
original package
  -> BBX extraction
  -> native resource
  -> editable PNG/CSV/JSON/NUT
  -> native resource rebuild
  -> BBX repack
  -> game/emulator test
```

A structurally valid native file is not proof that every semantic edit is accepted by the game. Runtime acceptance remains a separate validation step.

## Capability matrix

```bat
python siig_toolkit.py asset-capabilities
python siig_toolkit.py asset-capabilities -o ASSET_CAPABILITIES.json
```

Full-game rips also write `validation/ASSET_CAPABILITIES.json`. The current matrix keeps 11 families at full native round-trip status and gives **12 of 14** families at least one native builder, with Xbox XACT and PS3 SBlk now supporting flexible PCM-input replacement; all 14 remain viewable/exportable.

## Remaining reverse-build targets

The remaining major one-way/native-generation gap is Xenos compiled shaders: instruction-level disassembly/translation or a compatible compiler path. Xbox XACT/XWB and PS3 SBlk now have native replacement-bank paths for PCM WAV edits. Native Xbox XMA2 encoding, true multichannel PS3 SBlk topology synthesis, and emulator/hardware runtime acceptance remain open.

GMX topology-changing and template-free glTF -> GMX synthesis is now implemented. The remaining GMX boundaries are evidence/runtime driven: true blended native skinning has no proven representation in the checked corpus, platform shader microcode compilation is absent, some native fields remain opaque, and fully original scenes still need broader runtime acceptance testing.

## Dev24 retail no-edit round-trip evidence

The external retail corpus validation now records 2,197 completed byte-identical no-edit rebuild checks across GMX, TEX, DAT, MAP, ANM, stage3D, stagewall, COL, systemfont, and localization paths. See `validation/REAL_CORPUS_ROUNDTRIP_DEV24.json` for exact counts and evidence boundaries. Retail payloads are not bundled.


### Donor-free GMX schema synthesis (2.9.0-dev2)

Use `--synthesize-native-schemas` when a new glTF mesh/material has no compatible native vertex declaration or MTRL parameter schema. This implies all structural synchronization layers. The compiler builds standard decoded ARRY declarations and MESH records directly from glTF and can build MTRL parameter records from `extras.gmxParameterSchema`. Keep this as an advanced option: known native donors are still preferred when available, and runtime acceptance of novel semantic/shader combinations remains a separate validation question.


### GMX: rigid glTF skin compatibility (2.9.0-dev7)

For template-backed imports, add `--sync-rigid-skins` when the glTF contains `skins`, `JOINTS_0`, and `WEIGHTS_0`. The skin is accepted only when all vertices share one joint at weight 1.0; the importer converts that to a native BONE→MESH attachment. `gltf2gmx-new` enables this check automatically. Blended weights are intentionally rejected because no corresponding native per-vertex weight stream has been confirmed in the supplied SIIG corpus. Selected inverse-bind matrices may be affine non-identity matrices; positions and normals are rebaked as described below.


### GMX: rigid inverse-bind rebaking (2.10.0-dev1)

`--sync-rigid-skins` no longer requires the selected inverse bind matrix to be identity. For a rigid one-joint skin, an affine non-identity inverse bind is applied directly to imported positions; normals are rebuilt with the inverse-transpose normal matrix. `gltf2gmx-new` and Mod Workspace enable this path automatically. Blended weights remain rejected.

If the inverse-bind linear 3×3 is singular and the mesh has normals, import stops with a format error because a valid normal transform does not exist. This is preferable to silently emitting malformed native geometry.


### GMX: multi-joint rigid partitions (2.10.0-dev2)

A single Blender mesh may contain multiple disjoint rigid pieces assigned to different armature joints. `gltf2gmx-new` and `--sync-rigid-skins` split triangle islands by joint, compact their vertex arrays, perform each joint's bind-space rebake, and synthesize separate native MESH/BONE attachments. A triangle that spans multiple joints remains unsupported and fails explicitly.

For bosses/entities assembled from separate GMX resources, use `gmx-assembly-template` / `gmx-assemble`; see `GMX_ASSEMBLIES.md`.
