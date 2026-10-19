# Dev24 current unresolved-boundary audit

Status: **living WIP179 audit** for unsealed `2.10.0-dev25`. Historical versioned release notes and validation reports may retain period-correct unresolved statements. Sealed historical release notes and validation files remain period-correct and are **not** rewritten merely because later work resolved an item. The machine-readable companion is `validation/UNRESOLVED_BOUNDARIES_2.10.0-dev25.json`.

## Why this exists

The project has accumulated several generations of research notes. A phrase such as “unresolved” in a dev16, dev22, or earlier validation report describes the state **at that checkpoint**; it is not automatically a current limitation. This registry is the current-facing source of truth for what still lacks evidence, implementation, or external runtime validation.

The strongest rule is unchanged: an opaque field, transform, GPU state, or gameplay name stays open rather than being guessed. Conversely, once later evidence closes a boundary, it should not be repeatedly rediscovered just because historical documents retain the old wording.

## Current open boundaries

| ID | Class | Current boundary | What would close it |
|---|---|---|---|
| `VISUALIZER_RT_ALPHA_STORAGE` | External runtime semantics | Visualizer RGB recurrence is recovered, and WIP178 hardware footage shows clear RGB remains visible with BG:A=0; Canvas is still not claimed bit-identical to Xenos render-target alpha storage/compositing or final presentation. | Controlled Xenos/runtime evidence for the alpha path. |
| `VISUALIZER_BGM_PROCESSING_CADENCE` | External runtime semantics | Raw BGM = stereo peak mean; Check Mode uses it directly; normal stages use the recovered adaptive VOL SCALE normalizer. WIP174 resolves the native Xbox 360 meter window to one 5 1/3 ms XAudio2 processing pass = 256 samples at 48 kHz. Only browser/native analyser **phase/scheduling alignment** remains approximate. | Controlled sample-phase/runtime instrumentation if bit-identical browser/native polling alignment is ever required. |
| `ROUTE_DAT_PAIRING_AND_ACTIVATION` | Research semantics | Normal `XmapW_S` and `map4_/map5_` names deterministically select `levelW_stageS.dat`; explicit `Bmap13`/`Bmap15` DATs are now cross-checked against authored `WARNING[12]`/`WARNING[14]` request frames. Canonical Bmap ownership and the route-object initialization frame remain explicit. | Scene-level/canonical Bmap ownership plus exact object-instantiation timing; WARNING request compatibility is resolved. |
| `MAP_SCROLL_LAYER_PLAYER_NAMES` | Nomenclature | SCROLL_01/02/03 behavior is known; player-facing layer names are not. | Trustworthy name-bearing source. |
| `GMX_NATIVE_BLENDED_SKINNING` | Evidence-absent feature | True multi-joint weights remain rejected; 901 checked player/enemy MESH records use `skin_index=0xFFFF` with no JOINT/WEIGHT ARRY streams. | Genuine native weighted-skin evidence. |
| `GMX_SKIN_INDEX_NONFFFF_SEMANTICS` | Research semantics | `skin_index` is only bounded by the repeated `0xFFFF` no-vertex-skin observation. | Native sample/consumer using another value. |
| `GMX_PLATFORM_SHADER_COMPILATION` | Implementation gap | Targeted shader semantics can be researched, but new Xenos/RSX microcode is not compiled by the toolkit. | Justified compiler/assembler path plus runtime validation. |
| `GMX_OPAQUE_FIELD_SEMANTICS` | Research semantics | Remaining unnamed GMX/root fields are preserved/defaulted without invented meanings. | Field-specific executable/corpus evidence. |
| `GMX_NATIVE_NAMED_CLIP_CONTAINER` | Research semantics | Multi-bone MOTN/ANIM tracks exist; no native named animation-clip container is proven. | Name-bearing native animation container/consumer. |
| `GMX_ARBITRARY_ORIGINAL_SCENE_RUNTIME_ACCEPTANCE` | External validation | Template-free GMX construction is structural; arbitrary original scenes are not claimed retail-safe. | Representative Xenia/console/devkit execution. |
| `TEX_COMPRESSED_MIPMAPPED_AUTHORING` | Implementation gap | Canonical uncompressed donor-free TEX path is implemented; general compressed/mipmapped authoring is not. | Per-layout format evidence, encoder, and runtime tests. |
| `PS3_SYNTH_TEX_UNKNOWN_WRAPPER_RUNTIME_ACCEPTANCE` | External validation | New PS3 A8R8G8B8 wrapper synthesis is structurally valid; unknown-wrapper-field runtime acceptance remains unproven. | PS3 runtime test of genuinely new textures. |
| `PS3_NPDRM_SDAT_REENCRYPTION` | Implementation gap | SDAT decryption/authentication works; signed/encrypted replacement wrapper generation does not. | Justified re-encryption/signing implementation and verification. |
| `AUDIO_REPLACEMENT_REBUILD` | Implementation gap | Mod Workspace supports variable-duration/rate Xbox XWB PCM16 rebuild with channel/loop metadata rewrite and variable-size PS3 SBlk repacking with multichannel-input downmix; native XMA2 encoding, true multichannel PS3 topology, and runtime acceptance remain open. | Runtime validation plus optional codec/topology work. |
| `BLENDER_UI_RUNTIME_VALIDATION` | External validation | Add-on source contracts are tested; in-Blender UI/operator execution is not part of the release environment. | Run the validation in supported Blender. |
| `ANDROID_LEVEL9_PLACEHOLDER_RATIONALE` | Low-priority research | Mobile Level-9 split is mapped; Android placeholder-script rationale is not. | Additional mobile code/content rationale evidence. |
| `CONSOLE_GENERATOR_2X_CAPACITY_RATIONALE` | Low-priority research | Runtime output capacity is now proven as iOS `0x1800` → PS3 retail `0x3000` per generated layer; only the authoring/design reason for the console resource corpus totaling exactly 2× iOS stored cells remains open. | Per-file authored-dimension lineage or source/design evidence; allocator mechanics are resolved. |

## Boundaries that are no longer current

- `RUNTIME_009D_EMY051_GAMEPLAY_NAME` — WIP178 project-owner identification resolves `emy_051` as **LUST**, while the five-build runtime registry independently fixes runtime `0x9D` to that model. WIP179 removes the stale neutral-name requirement. An executable-internal `LUST` token is still not claimed; that is a provenance distinction rather than an unresolved gameplay identity.

- The **window-size/duration portion** of `VISUALIZER_BGM_PROCESSING_CADENCE` — WIP174 fixes the Xbox 360 XAudio2 quantum at 5 1/3 ms, exactly 256 samples at 48 kHz, and Microsoft documents `pPeakLevels` as the maximum absolute level during a processing pass. The living boundary now covers only host/browser snapshot phase and scheduling relative to native quantum boundaries.

- `VISUALIZER_SEQUENCE_CHANGE_TIMING` — WIP173 proves `VL_CHANGETIME`/0xCD is a SequenceSet change-threshold range, not an interpolation opcode. The exact `[min,max)` threshold selection, 18000/18000 constructor default, `threshold < counter` cadence, `-1` wrap, delayed dirty-row application, Microsoft CRT LCG and two-rand 30-bit wrapper are reproduced. Hardware run seed remains timer-derived rather than DAT-authored.

- `VISUALIZER_GAMEPLAY_BGM_NORMALIZER` — WIP167 recovers the normal-stage adaptive post-meter path: constructor default 300 frames; `VL_VOLUME_SCALE`/0xCE reconfigures the window (4-2/4-4/4-5 author 180); exact MIN/MAX, 0.001 guard, VOL SCALE mapping, and 180-frame RAW/SCALE diagnostics are reproduced. Dedicated Check Mode remains raw.

These can still appear as unresolved in older checkpoint files, but later work supersedes them:

- `CONSOLE_GENERATOR_OUTPUT_BUFFER_CAPACITY` — PS3 retail `stageGenerateMapInit` allocates `0x20 * 0x180 = 0x3000` bytes for each of three generated layers, and the append path uses the same bound; retained iOS evidence is `0x1800` bytes/layer. Runtime generated-layer capacity therefore doubled exactly 2×.

- `BMAP_WARNING_REQUEST_COMPATIBILITY` — WIP164 validates explicitly supplied `Bmap13`/`Bmap15` DATs against the proven `WARNING[12]`/`WARNING[14]` special-resource request chains, reports authored request frame(s)/competing special requests, and deliberately does not infer a unique DAT owner or route-object initialization frame.


- Survival conversion status bytes → resolved in dev17 as Evolution Tree stage-node statuses.
- Retail route Hermite/resampling algorithm → reproduced; normal-stage DAT filename pairing is now deterministic, while Bmap ownership and route-object activation timing remain open.
- Template-free GMX root/scene construction → implemented.
- Donor-free GMX vertex/material schema synthesis → implemented.
- Multi-bone animation + glTF CUBICSPLINE import → implemented.
- Donor-free canonical TEX synthesis → implemented for the proven layouts.
- Camera preset word 11 → resolved as `face_bias`.
- Visualizer recursive feedback sampler → repeat + point min/mag/mip, anisotropy disabled.
- Visualizer SHAPE sampler → same exact sampling class recovered from all ten retail SHAPE resources.
- Visualizer EffectBlur fixed-function blend → Add(SrcAlpha, One).
- Visualizer EffectBlur pixel shader → sampled feedback RGB + uniform source alpha.
- Visualizer ScreenSprite SHAPE shader → sampled RGBA × runtime float4 tint; source-over SrcAlpha/OneMinusSrcAlpha.
- Stage placement Euler order → retail Xbox 360 and PS3 transform consumers prove row-vector `S * Rz(z) * Rx(x) * Ry(y) * T`; Stage Explorer now rotates/scales GMX AABB proxies with that native order.
- PS3 fixed-slot SBlk replacement → implemented in WIP161; WIP187 extends it to variable-size/rate repacking and extends Xbox XWB editing to variable duration/rate/channels with proportional loop remapping. Native XMA2 encoding, true multichannel PS3 topology synthesis, and runtime acceptance remain open.

## Human decisions are not technical unknowns

The original-project license remains intentionally unselected at the project owner's request while meaningful development/research remains. Dev24 sealing/promotion is also owner-controlled. Neither item should be “closed” by an automated audit.

## Practical priority

The registry separates tasks that can plausibly be advanced with retained source evidence from tasks that fundamentally need new runtime/corpus evidence. In particular, **do not manufacture native blended skinning, Xenos alpha behavior, executable-internal LUST naming, or opaque GMX meanings merely to make the open list shorter**. Implementation-only items such as compressed/mipmapped TEX authoring, audio rebuild, shader compilation, and PS3 SDAT re-encryption are real future features, but they are not evidence gaps in the existing decoders.
