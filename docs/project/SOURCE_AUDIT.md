# Source-provenance audit report

Audit date: 2026-09-18  
Development tree reviewed: SIIG Asset Toolkit 2.10.0-dev24 WIP release-readiness tree

## Scope

Reviewed bundled Python/Java source, launchers, add-on source, documentation, provenance tables, and release-layout files for vendored dependencies, copied/adapted logic, external-process calls, game assets, and unresolved attribution.

## Findings

- No third-party Python package, executable, shared library, emulator, decompiler, OpenSSL binary, FFmpeg binary, or vgmstream binary/source is bundled.
- One direct code adaptation remains identified: `xg_address_2d_tiled_offset`, an independent Python translation/adaptation of Xenia's Xenos tiled-texture addressing. The BSD 3-Clause notice remains bundled. The historical exact Xenia commit/file consulted was not preserved; that limitation remains explicit.
- The XMA2 RIFF wrapper is locally written against public Microsoft/DirectXTK structure documentation.
- The Visualizer BGM meter uses executable-derived logic; Microsoft Learn XAudio2 volume-meter documentation is consulted only to identify the public `XAUDIO2FX_VOLUMEMETER_LEVELS` field names. No Microsoft implementation code is copied.
- AES-128, STFS, PS3 PKG, debug package streaming, extraction-safety policy, and NPDRM SDAT handling are locally authored clean-room code. FIPS-197 is the AES normative/known-answer reference.
- Finalized PS3 PKG extraction may invoke an installed OpenSSL executable as an optional acceleration backend. OpenSSL is external and not bundled; Python AES-CTR remains the fallback and is equivalence-tested.
- The new Sony SBlk v3/PS-ADPCM implementation is locally authored for the supplied SIIG bank. vgmstream `src/meta/bnk_sony.c` and `src/coding/psx_decoder.c` were explicitly consulted as behavioral/field-layout cross-checks. No vgmstream code was copied or vendored.
- BBX, GMX, SIIG TEX wrappers, system font, localization, COL, ANM, DAT, MAP, stage tables, atlas mapping, Bmap/Xmap, wall/generator, and shader-container work remains based on user-supplied binaries, Ghidra exports, synthetic fixtures, and corpus validation.
- Stage Explorer v5 source was reconstructed from the project's own retained validated generated explorer plus current executable-backed semantics; no third-party UI code was introduced.
- The Blender add-on, Asset Viewer, BBX repacker, localhost server, and resume-cache implementation are locally authored.
- WIP175 removes a project-local GIGANTIC-UFO-only presentation rotation after project-owner visual-convention correction; no third-party source, code, or new dependency is involved.
- TCRF/The Cutting Room Floor remains explicitly excluded.

## Real-package validation

The project now possesses and has directly exercised the supplied original retail Xbox 360 LIVE STFS and PS3 type-1 PKG. This supersedes older notes claiming those exact packages were unavailable. Retail regressions reach 2,593 resources with zero BBX hash mismatches/archive failures on both platforms; PS3 validates six internally decrypted SDATs / 18 authenticated blocks and 84 Sony WAV streams, while Xbox validates 86 XACT WAV streams.

## Current source-only validation

The dev24 WIP release-readiness tree passes **175/175** built-in tests after fresh-package extraction. Its root `RELEASE_MANIFEST.json` is regenerated for `2.10.0-dev24` and self-validated against every packaged source file except the manifest itself. Packaging gates report zero proprietary game-asset payloads, zero bundled external executables/libraries, and no Python bytecode/cache files. `reference/provenance/SOURCES.csv` contains **29 explicit source/reference rows** with a consistent 10-column schema, including a dedicated TrueAncestor historical-fallback row rather than relying on an indirect mention.


Dev2 adds executable-derived runtime registry, route-source, GMX animation-track, route-descriptor, and raw camera-preset outputs. These additions were derived from the retained five-build Ghidra exports and supplied retail corpus; no new third-party code was copied or vendored. The changed paths were revalidated on all 47 retail Bmap/Xmap-layout files and all four route/camera GMXs.

Dev3 adds a locally authored executable-backed route resampler and runtime camera-preset tables. The route implementation is derived directly from the retained PS3 retail PPC listing/decompilation at functions `0x00158790`, `0x00158A28`, `0x00158D38`, `0x00159298`, `0x00159560`, and `0x0015A338`; no external spline library/code is used. The camera runtime table applies the 160 initializer writes traced at `0x0015C7F0` and preserves uncertain semantics structurally. No new third-party source or binary dependency was introduced.

Dev4 adds locally authored runtime route state and DAT-coupling code derived from the same retained PS3 retail executable: SCROLL_02 conversion at `0x0014E408`, route advancement at `0x00159560`, and route initialization at `0x0015A338`. No external spline, animation, or timing library is used. The new state machine was stress-stepped on all 46 resampleable retail route tables in both non-loop and loop modes, and DAT coupling was additionally exercised on explicit filename-correspondence candidates without claiming a complete global pairing map. No new third-party source or binary dependency was introduced.

Dev5 adds locally authored camera-preset semantic helpers derived directly from retained PS3 retail consumers at `0x00155300`, `0x00157540`, `0x00157A10`, `0x0015B910`, `0x0020D69C`, and `0x0020E984`, plus the renderer `fogRange`/`vFogColor` paths. The untouched raw preset table remains bundled for auditability. No third-party camera/math package or copied implementation was introduced. Word 11 remains explicitly unresolved rather than receiving a guessed material-property name.

Dev6 adds locally authored procedural route-orientation matrix/state helpers and combined procedural camera-world playback derived from the retained PS3 retail route/camera consumers. No third-party matrix, camera, scenegraph, or animation library is used. The combined command requires caller-supplied route/DAT/preset/runtime-coordinate inputs and explicitly excludes animated `cam1`/`int1` and `fld014`/`fld015` modes rather than inferring unsupported activation state.

Dev7 corrects matrix-animation timing and adds animated camera/field evaluators derived directly from the retained PS3 retail executable. Channel-type-12 matrix sampling is implemented as the executable's direct `logical_frame % frame_count` lookup; the raw float timestamp table is preserved as metadata rather than treated as runtime time. No third-party animation/interpolation library or copied code was introduced.

Dev8 adds locally authored PA-route research helpers and four machine-readable cross-build tables derived only from the retained user-supplied PS3 retail, Xbox 360 retail, June 10, May 11, and May 9 Ghidra exports plus the supplied retail DAT corpus. No new third-party source, executable, library, emulator, or online code was introduced. Prototype debug strings are used to recover names such as `Route::SetPaRoute`, while retail/PS3 correspondences are recorded by executable address and function/vtable shape. Strong correlations are explicitly labeled as such rather than promoted to direct-call proof.

Independent post-processing validation also passed on both supplied retail rips: Stage Explorer v5 generated 92 entries / 78 runtime pairings on both Xbox `Media` and PS3 `USRDIR` layouts; Asset Viewer coverage reached 3,520/3,520 Xbox and 3,991/3,991 PS3 previewable thumbnails with zero missing; full hash/privacy verification checked 9,855 Xbox files and 11,195 PS3 files with zero issues.

Dev24 adds locally authored `.siigmod` binary-delta packaging and application code using only Python's standard library. The format stores source/target hashes, copy/sparse instructions, and changed target-byte payloads; it does not bundle clean source assets. External retail corpus validation expanded to 2,197 completed byte-identical no-edit rebuild checks across GMX/TEX/DAT/MAP/ANM/stage tables/COL/systemfont/localization, while proprietary corpus files remain outside the release. No new third-party code, package, executable, or binary dependency was introduced.

Dev26 extends the locally authored GMX reverse compiler with opt-in whole `MESH`/`ARRY` graph synchronization. New native mesh/array records are synthesized only by cloning field layouts already proven from the supplied corpus; no third-party model-format or scene-graph code was introduced. Removal uses explicit cross-reference accounting and existing BONE attachment encoding already documented by this project. The default dev25-compatible path remains unchanged unless the user explicitly enables graph synchronization.

Dev27 extends that same clean-room GMX compiler with opt-in `BONE`/`PARE`/`MTRL`/`SHAD` relationship synchronization and a self-contained scene-graph report. New material parameter schemas, mesh vertex declarations, PARE prefixes, and fixed shader records are synthesized only by cloning compatible native layouts already represented by the template; no external scene-graph, material, shader, or model-format library is used. Existing bone transform bytes remain preserved unless transform import is explicitly requested. The release does not claim TXIF synthesis, arbitrary material-schema invention, shader-bytecode compilation, or template-free GMX creation.

Dev28 extends the same locally authored clean-room compiler with fixed-layout TXIF reference synthesis and glTF texture-binding resolution. The implementation uses the already decoded 0x30-byte TXIF index/flags/name layout and standard glTF image/texture metadata; no external texture/material library or copied implementation is introduced. The source-only release creates only GMX references/bindings and does not bundle proprietary TEX/DDS payloads or claim arbitrary texture payload generation.

## AI disclosure

OpenAI ChatGPT assisted with analysis, code drafting, tests, documentation, and packaging. The project can enumerate explicit sources intentionally consulted, but cannot enumerate the model's full training corpus or latent influences. See `AI_DISCLOSURE.md`.

## Remaining publication gates

- Select a license for original project code before public redistribution.
- Preserve Xenia's BSD notice and all provenance records.
- Keep proprietary game packages/assets and generated game-data viewers out of a source-only public release.
- Perform in-Blender UI/operator validation when Blender is available.
- Continue source-overlap/license review whenever future code is copied or adapted.
- Record exact upstream commit/file whenever feasible for all future external code references.

Dev9 adds only locally authored tables/helpers/documentation derived from the retained five-build Ghidra exports. No executable bytes or proprietary game assets are bundled. Retail Xbox and PS3 literal boss-route tables were byte-matched against June 10 during validation; prototype timing deltas remain documentary data only.

Dev14 adds a locally authored Ultimate UFO final-reset audit table, helper, regression test, and research note derived from retained Xbox 360 retail and PS3 executable listings plus retail DAT records. It records the exact camera-gate clear precondition and separates proven negative results at Mframes 6030/6200 from the still-unresolved ordinary higher-level reset caller. No footage or executable bytes are bundled.


Dev15 adds locally authored mobile package/format inspection and comparison code derived from the user-supplied iOS 4.1.0 IPA and Android 1.0.4 APK research copies. The packages themselves and all extracted assets/executables are excluded from the source-only release. TZIP, mobile MAP, DEX-header, binary-AXML, Mach-O metadata and package-integrity helpers use Python's standard library only.

Dev16 adds locally authored mobile-exclusive research tables, shared DAT opcode labels, and a Chimera opcode regression derived from retained iOS executable symbols/resources plus user-supplied research packages. Third-party MaxTheMurdererV2 gameplay videos are credited as observational corroboration only and are not bundled. No video, crossover music, stage data, mobile executable, IPA, or APK content is included.

Dev17 adds locally authored Survival Evolution Tree gating/substitution references, V2 enemy-shot dispatch/attack-pool mappings, conservative V2 mover-branch summaries, and Chimera A/B boss-argument documentation derived from retained iOS executable/resource analysis. No new third-party code or binary dependency was introduced; existing gameplay-video references remain observational provenance only and no footage is bundled.


Dev18 adds locally authored iOS→console MAP/DAT/timing/generator lineage metadata derived from retained user-supplied iOS ARMv7 and console Ghidra exports plus decoded resource tables. No executable bytes, decompiled proprietary code, IPA/APK content, or stage payloads are bundled.

Dev19 extends that source-only lineage into six original Stage-3 boss constructor/pool ancestry, the Xbox 0x96..0xAB enemy-handler family, World-5 integration chronology, and exact authored-DAT-loader anchors. The release explicitly preserves the continuity boundary where raw handler pointer values and exact per-boss May11→June10 similarity scores were not retained instead of reconstructing them speculatively. No new third-party source or binary dependency was introduced.
Dev20 extends the source-only lineage into the six original mobile boss gameplay movers using re-supplied project-owner Ghidra exports for May 9, May 11, June 10, retail Xbox and retail PS3 plus the retained iOS ARMv7 research copy. Only derived addresses, instruction fingerprints, constants, equations and semantic summaries are included. No XEX/EBOOT/Mach-O bytes or decompiled proprietary code are bundled. The local Mach-O metadata repair used to disassemble the modified iOS research copy is an analysis-only working file and is excluded from the package. No new third-party source or binary dependency was introduced.



Dev22 adds locally authored native rebuilders for the completely mapped stagewall/generator and `0x118` stage3D table records, a template-preserving fixed-layout GMX field editor, and dedicated `text.bin` / `message.bin` localization compilers. These builders are derived from the project's existing clean-room parsers, supplied-corpus structure research, and synthetic byte-roundtrip fixtures. The release does not bundle a GMX, localization archive, audio bank, game executable, or other proprietary validation input. GMX native rebuild and localization byte-identity regression claims in dev22 are intentionally limited to synthetic structural fixtures unless separately noted; real runtime acceptance remains outside the source-only release gate. No new third-party dependency or copied external implementation was introduced.

Dev23 adds the locally authored mod-workspace orchestration layer above the existing clean-room native builders. Its real-corpus round-trip validation used user-supplied retail `player.bin`, `text.bin`, and `message.bin` as external test inputs only: all 13 player GMXs and both localization archives passed byte-identical no-op rebuild checks. Only derived hashes/counts are retained in the source-only validation report; proprietary inputs, extracted assets, and rebuilt test payloads are excluded. The workspace project file may intentionally store the user's local source-rip path at runtime, but no such runtime workspace or private path is bundled in the release. Xbox gzip patch generation is locally authored; PS3 NPDRM/SDAT re-encryption remains unsupported. No new third-party dependency or copied external implementation was introduced.
Dev6 adds locally authored canonical GMX-root synthesis and a no-template glTF compiler entry point. The 0x30-byte root builder uses only fields already decoded by this project: tag/size, total stream size, the dev25-proven geometry AABB, and explicitly unnamed/reserved bytes that default to zero. It composes the project's existing clean-room MESH/ARRY, SHAD/MTRL, TXIF, BONE/PARE, and MOTN/ANIM builders; no external model compiler, scene graph, shader library, or copied implementation was added. The release does not claim semantics for the root +0x08/+0x28 fields, platform shader microcode compilation, glTF skinning import, or runtime acceptance of arbitrary original scenes.



Dev7 rigid-skin compatibility is locally authored from the already-decoded glTF accessor reader and native BONE/MESH graph compiler. No external skinning library or copied implementation is introduced. The feature intentionally refuses blended weights because the supplied GMX evidence contains no per-vertex joint/weight streams; the user-supplied player/enemy corpus was used only for validation statistics and is not bundled.


### 2.10.0-dev1

The inverse-bind rebake implementation is locally authored from the glTF affine skinning contract and the project's previously decoded rigid SIIG BONE→MESH representation. It uses only standard-library matrix arithmetic. No third-party skinning library, copied renderer code, proprietary model payload, or executable code is bundled. The retail player/enemy inputs used for the dev7 corpus cross-check remain external and are not included in the release tree.


### 2.10.0-dev2

Dev2 adds only clean-room Python/Tkinter logic for rigid joint-island partitioning and explicit-transform multi-GMX glTF assembly. The built-in PROGRESSIVE UFO catalog records filenames/runtime IDs/counts already established in project research but contains no proprietary model bytes and deliberately leaves four unrecovered placement matrices null.


### 2.10.0-dev3

Dev3 adds locally authored catalog/GUI/CLI/documentation logic for the PROGRESSIVE UFO five-part assembly. Runtime order and transforms were derived from user-supplied June/retail Xbox executable analysis and the project-owner PS3 Ghidra export, with the PS3 input hash matched to the previously recorded research corpus. Only derived addresses, normalized instruction fingerprints, constants and matrices are retained. No XEX/EBOOT bytes, Ghidra export, GMX payload, screenshot, or decompiled proprietary code is bundled. The glTF coordinate application reuses the toolkit's existing clean-room GMX exporter convention; no new external code dependency or copied implementation was introduced.

Dev5 adds only locally authored assembly-catalog/data-flow code, GUI wiring, tests and derived research metadata. HORNET/CRAB/PROGRESSIVE validation used user-supplied Xbox/PS3 executables, Ghidra exports, ANM and GMX files as external research inputs; no proprietary bytes or generated retail assemblies are bundled. HORNET's C1 locator lattice and pool counts, CRAB's landed sample, and PROGRESSIVE barrier bind orientation are retained only as derived constants/hashes/addresses. No new third-party code, binary dependency, or copied implementation was introduced. Native game units are preserved rather than converted through an external DCC/unit library.

### 2.10.0-dev6

Dev6 adds only locally authored assembly-catalog generation, Tkinter wiring, regression tests and derived HORNET runtime research metadata. The 45-record prism-wall grid, 13-entry A1 random-slot table, A1/C0 substitution semantics and phase-state boundaries were derived from the retained project-owner June Xbox, retail Xbox and retail PS3 Ghidra exports. The real retail A1/C0 GMXs were exercised externally only to validate one representative slot-22 assembly. No XEX/EBOOT, Ghidra export, GMX, ANM, generated retail glTF, third-party binary, or copied external implementation is bundled. HORNET state 6 remains explicitly unresolved rather than being inferred from the recovered state-4 wall.


### 2.10.0-dev9 ULTIMATE UFO assembly evidence

Dev9 adds only locally authored assembly metadata/code derived from project-owner Ghidra exports and prior model-registry research. The source-only package contains exact runtime type counts, phase/state metadata, named locator ranges and controller semantics, but no XEX/EBOOT bytes or `bos_015*.gmx` assets. The exporter resolves `lt_###` nodes from user-selected local GMXs at runtime and rejects missing or ambiguous locators rather than embedding proprietary transforms or guessed geometry. No new third-party dependency or copied external implementation was introduced.
## 2.10.0-dev10 addendum

Dev10 adds only locally authored assembly metadata/UI/test/documentation around HORNET state-3 behavior recovered from the retained user-supplied five-build Ghidra exports. The project owner re-supplied the original retail Xbox package, which was used externally to verify the historical HORNET GMX/ANM hashes and run a real `hornet_exposed_core` export. Those proprietary package/GMX/glTF bytes remain outside the source release. No new third-party source, library, executable or copied implementation was introduced. The built-in suite is 92/92 before release sealing.
### 2.10.0-dev22

Dev22 adds locally authored Tkinter/HTML/Python presentation and orchestration logic plus derived executable/footage-backed research metadata. The Visualizer feedback renderer is based on the project-owner June 10 Visualizer Check Mode footage and recovered game parameters/timelines; no footage frames are bundled. The Stage Explorer GMX-size proxies use only decoded native root AABBs/runtime placement metadata and deliberately do not invent unresolved placement rotation order. The five-boss controller audit retains only derived addresses/function identifiers/findings from the supplied Xbox/PS3 Ghidra exports.

The four GMX visual-pass modes classify native `_F` face/solid and `_E` edge/outline bones and reuse the project's existing clean-room glTF exporter; no third-party rendering/model library was added. The Asset Viewer OS-default Open-file bridge is localhost-only and implemented with the Python standard library/OS shell facilities; no protocol-handler executable or third-party server is bundled. Full retail Xbox validation inputs and the generated ~GiB rip remain external to the source release.


### Dev24 release-readiness audit

The current dev24 release-readiness gate is **166/166** and validates the current root source manifest before checkpoint packaging. Fresh-package validation is required again by the WIP checkpoint builder.

The current dev24 pass re-audits the living release metadata after the extended runtime/Workbench/Visualizer research cycle. `reference/provenance/PROVENANCE.json` now identifies dev24 rather than the obsolete dev4 candidate gate, the root release manifest is current, GUI documentation identifies the current 0.56.0-dev24, the current boss matrix is 14 deep runtime / 3 gameplay-pose / 1 native-only, and THE MOON's old “scale” description is superseded by the material-alpha/rotation trace. Historical release notes and versioned validation artifacts remain unchanged as historical records. No new third-party implementation code was introduced by the dev24 runtime traces, Visualizer correction, Workbench QoL, or THE MOON sampler, SHAPE/TEX sampler closure, camera face-bias trace, MANDALA all-membership preset, and THE SUN timing closure.

Dev24 also closes the Visualizer previous-feedback sampler statically: repeat addressing, point min/mag/mip filtering, and anisotropy disabled. Xenia xenos.h is used for public field/enum documentation only; no additional Xenia implementation code is copied.
Dev24 WIP157 closes the Visualizer source-SHAPE shader/composite boundary without adding proprietary material. Retail `ScreenSpritePS` is represented only by derived metadata: a 60-byte Xenos microcode path that samples one 2D texture and multiplies sampled RGBA by the runtime float4 tint. The source pass blend is documented as SrcAlpha/OneMinusSrcAlpha Add. No shader bytes or SHAPE pixels are bundled; exact pixels are still read only from a user-supplied rip into a locally generated simulator. The old luminance-mask/source-in browser approximation is removed.
### 2.10.0-dev24 WIP158

WIP158 adds only locally authored Markdown/JSON registry metadata and one dependency-free regression. The boundary registry summarizes already-retained project evidence; it does not bundle proprietary executable bytes, game assets, runtime captures, or new third-party code. Historical versioned reports are intentionally left unchanged, while current-facing README/provenance drift is corrected.

### 2.10.0-dev24 WIP159

WIP159 adds only locally authored Stage Explorer transform/projection code, regression assertions, and derived documentation/validation metadata. The stage-placement matrix order is derived from retained project-owner Xbox 360/PS3 executable analysis and the already-established SIIG model-transform convention; no XEX/EBOOT bytes, decompiled proprietary code, GMX payloads, screenshots, third-party implementation code, or new dependency are bundled.

### 2.10.0-dev24 WIP160

WIP160 adds only locally authored route/DAT filename-resolution logic, regression assertions, and derived documentation/validation metadata. The normal `XmapW_S` / `map4_/map5_` naming rule is cross-checked against the already-retained executable-backed `STAGE_PAIRING.csv`; no DAT, stage3d, XEX/EBOOT, decompiled proprietary code, or third-party implementation is bundled. The special `Bmap13`/`Bmap15` WARNING reload evidence remains bounded to its proven resource-transition meaning, and the toolkit refuses to guess a unique boss/special DAT owner or route-object activation frame.

### 2.10.0-dev24 WIP161

WIP161 adds a locally authored Sony PS-ADPCM encoder and fixed-capacity SBlk slot-replacement workflow. It reuses the existing independent SIIG SBlk parser/decoder and the five standard decoder coefficient pairs already documented in-tree; the encoder performs its own predictor/quantization search and does not copy vgmstream implementation code. Existing vgmstream BNK/PS-ADPCM references remain behavioral/field-layout cross-check credits only. No retail `.bnk`, WAV, VAG, Sony SDK material, external executable, or third-party source is bundled. The regression uses a synthetic one-stream SBlk fixture and a generated test tone.

### 2.10.0-dev24 WIP162

WIP162 is a current-facing accuracy/metadata correction only. It changes locally authored documentation, Stage Explorer descriptive metadata, capability text, and regression assertions; no new executable-derived data, game assets, third-party code, dependencies, or external binaries are added. The change removes stale statements contradicted by already-retained Stage Explorer v7 scroll reconstruction and WIP159 placement-transform evidence.
### 2.10.0-dev24 WIP163

WIP163 adds only locally authored derived metadata, documentation, validation, and regression assertions. The generator-capacity closure is derived from retained project-owner iOS lineage metadata plus the supplied retail PS3 Ghidra decompile/listing: the release records addresses/constants/arithmetic only and bundles no EBOOT/XEX bytes, decompiled proprietary source, MAP payloads, or third-party implementation code. The higher-level authored-corpus rationale remains explicitly open. The same checkpoint removes one final stale current MAP-renderer scroll-state sentence; historical versioned validation is unchanged.


### 2.10.0-dev24 WIP164

WIP164 adds only locally authored route-playback validation/reporting logic, regression assertions, and derived documentation/validation metadata. It reuses the already-retained direct `WARNING[12]`/`WARNING[14]` special reload-chain evidence for Bmap13/fld014 descriptor 1 and Bmap15/fld015 descriptor 0; no DAT, Bmap, GMX, XEX/EBOOT, decompiled proprietary source, runtime capture, third-party implementation code, or new dependency is bundled. Matching WARNING request frames are intentionally not represented as route-object initialization frames.


### 2.10.0-dev24 WIP165

WIP165 adds only locally authored Python/Tkinter/HTML orchestration, cache/verification performance work, documentation and derived validation metadata. Resume-side PS3 SDAT caching never bypasses authentication on first use: a cached plaintext is reused only when a locally written sidecar matches the exact encrypted-source SHA-256, source size, plaintext SHA-256 and plaintext size. A mismatch falls back to the existing authenticated SDAT decrypt path. Parallel output hashing uses only Python’s standard-library `ThreadPoolExecutor` and preserves sorted deterministic manifest order. No new third-party code, executable, library or network service is introduced.

Canonical retail Xbox 360 and PS3 packages were exercised externally to the source tree. The resulting retail rips, package bytes, decoded assets and audio are not bundled. Only aggregate validation counts are retained: 16,567/16,567 Xbox and 16,422/16,422 PS3 output-manifest entries independently re-hashed with zero integrity/privacy issues; PS3 also confirms six internally authenticated SDATs / 18 blocks with no fallback.


Dev24 WIP166 adds only locally authored Visualizer presentation/orchestration code. FFmpeg remains an optional external executable already supported by the toolkit; it is invoked to transcode user-owned WMA/AT3 BGM into browser-safe local previews and is not bundled. No codec implementation code or proprietary BGM is copied into the source package.

### 2.10.0-dev24 WIP167

WIP167 adds only locally authored Visualizer state-machine code, semantic annotations, regression assertions, and derived documentation/validation metadata. The recovery is based on already-retained project-owner June 10 Ghidra exports plus new project-owner real-hardware footage used as observational validation. The three MP4 captures are **not bundled**. The release records only function/address relationships, formulas, authored DAT values and rounded overlay cross-checks. No proprietary executable bytes/decompiled source, game audio, screenshots/video, new third-party code, dependency, or external binary is added. FFmpeg remains the optional unbundled codec bridge introduced by WIP166.
### 2.10.0-dev24 WIP178

WIP178 adds only locally authored CSV/Markdown/JSON identity metadata, Asset Viewer presentation/search logic, regression assertions, and derived runtime cross-checks. Friendly model names come from the project owner's supplied identification list and are explicitly labeled as that evidence class; nine uncertain `est_*` interpretations remain speculative. The five-build runtime reconciliation uses only already-retained derived registry rows. No GMX, executable, video frame, game asset, decompiled proprietary source, new third-party code, dependency, or external binary is bundled.

The second ten-segment June 10 Visualizer Check Mode capture batch is used only as external observational validation. The source package retains derived parameter/control findings, including the BG-RGB-with-BG:A=0 observation, but does not include the MKV media or extracted frames. Exact Xenos alpha/final-composite semantics remain explicitly unresolved rather than being inferred from Canvas behavior.



### 2.10.0-dev24 WIP179

WIP179 adds only locally authored documentation/validation synchronization, Blender add-on source changes, a rebuilt source-only add-on ZIP, and dependency-free regression assertions. The add-on 0.2.1 source-tree discovery fix walks parent directories to locate the toolkit root and is tested against a minimal local `bpy` shim; Blender itself and proprietary assets are not bundled. No game asset, executable/decompiled proprietary source, screenshot/video/audio, new third-party implementation code, dependency or external binary is added.


### 2.10.0-dev24 WIP180

WIP180 adds only locally authored CSV/Markdown/JSON derived metadata and regression assertions. Native GMX and converted glTF payloads remain external project-owner validation inputs; the package retains only filenames, sizes and SHA-256 fingerprints needed to establish registry presence and geometry-identity relationships. No GMX/glTF/game payload, executable/decompiled source, screenshot/video/audio, third-party implementation code, dependency or external binary is bundled.

## Dev24 WIP186 audio-authoring provenance

WIP186 adds only locally authored Mod Workspace orchestration and XWB reconstruction code. Public Microsoft XACT/DirectXTK documentation was consulted to confirm the standard 24-byte wave-bank entry layout, XACT support for PCM/XMA2 content, and the Xbox big-endian wave-bank/16-bit PCM byte-order caveat. No Microsoft SDK source, encoder, executable, or proprietary XMA implementation is copied or bundled. FFmpeg remains an external optional decoder only and is not used as an XMA encoder. The PS3 Mod Workspace path reuses the already-audited clean-room SBlk/PS-ADPCM encoder from WIP161.

## Dev24 WIP187 flexible audio-authoring provenance

WIP187 extends only locally authored XWB/SBlk reconstruction code. Microsoft Learn `WAVEBANKENTRY` / `WAVEBANKMINIWAVEFORMAT` documentation is used as the public field contract for duration, channel count, sample rate, play region and loop region. Public psx-spx SPU documentation is used only to cross-check Sony ADPCM loop-start/repeat/end control-bit meanings; the existing vgmstream reference remains the SBlk layout/decoder cross-check. No Microsoft SDK implementation, XMA encoder, psx-spx code, vgmstream code, proprietary bank, or test audio is bundled. Retail SIIG banks were used only as external validation inputs; the package retains derived counts/hashes/results rather than the game payloads.

### dev24 WIP188 Blender style-preview audit

WIP188 adds only locally authored Blender add-on Python, documentation, validation metadata and a rebuilt source-only add-on ZIP. White-outline preview geometry is generated at runtime from the user's imported native `_E` edges; no game model is bundled. The scanline overlay uses Blender compositor nodes plus an in-memory generated grayscale image; no external shader binary, texture or third-party implementation is copied into the toolkit. Blender remains optional and is not bundled.

### 2.10.0-dev24 WIP189

WIP189 adds only locally authored Python/Tkinter performance, integrity-cache, regression, documentation and validation metadata. The incremental updater uses standard-library filesystem stat calls, SHA-256 and `ThreadPoolExecutor`; it adds no dependency, network service, executable or third-party implementation. `OUTPUT_STAT_CACHE.json` contains only rip-relative paths, sizes, mtimes, expected SHA-256 values and verification flags, and is excluded from the content manifest as local control-plane metadata. Proprietary retail game payloads used for performance validation remain outside the source package. External Xbox retail benchmarking retains only aggregate timing/count evidence (301.09 s fresh rip, 9.98 s first incremental update, 1.90 s exact no-op, 9.70 s explicit full verification; 23/23 archives and 2,593 resources reused); no retail archive, decoded asset, audio, or generated rip output is packaged.


## WIP197 delta audit

WIP197 adds only source-side UI/layout, localization TSV, Visualizer cache/timing/diagnostic logic, documentation and validation metadata. The generated Visualizer BGM cache is created only inside a user's rip output and is not bundled in the toolkit package. Xbox package editors (Velocity, Horizon, Le Fluffie) are named only as external examples; no package-editor code or binary is bundled. No project-owner hardware video, proprietary executable, BGM track, game archive, or generated retail rip is included.


## WIP200 Atlas Inspector safe-editing pass

The WIP200 Atlas Inspector adds only toolkit-authored Python/HTML/documentation and uses the existing standard-library PNG path. No third-party implementation code, external binaries, or proprietary game/media payloads are bundled. Generated atlas guide/preview PNGs are user-output artifacts, not release assets. The inspector explicitly separates content-derived conservative regions from unresolved authoritative native UV/allocation metadata; it does not encode guessed native semantics. Desktop GUI is 0.56.0-dev24 and the built-in regression gate is 175/175 before final fresh-package verification.

## dev25 iOS atlas UV research

The dev25 research pass recovered the iOS `mapUVTable`, `endingTextureUV`, texture tables, and explicit sprite-command UV signatures. These are research evidence only; no iOS-only coordinates are promoted to Xbox `common512` metadata. See `reference/research/IOS_ATLAS_UV_RECOVERY_DEV25.md` and `validation/IOS_ATLAS_UV_RECOVERY_2.10.0-dev25.json`.
