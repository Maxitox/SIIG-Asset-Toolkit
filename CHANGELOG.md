# 2.10.0-dev25

- Atlas research: recovered iOS `texture.tzip` plist contents, `mapUVTable`, `endingTextureUV`, texture tables, and explicit native sprite-command UV arguments.
- Atlas Inspector remains conservative until Xbox `common512` caller-level UV/allocation records are recovered.
- Development checkpoint naming returns to `devNN`; WIP-style checkpoint names are now historical only.
- GUI version: 0.57.0-dev25.

## 2.10.0-dev24 WIP199

- **Xbox `.bin.gz.sdat` replacement fix:** Xbox SIIG `.bin.gz.sdat` archives are ordinary gzip streams, not PS3 NPDRM SDAT. Mod Workspace now emits changed `message.bin.gz.sdat`, `text.bin.gz.sdat`, `script.bin.gz.sdat`, `shader.bin.gz.sdat`, `generator.bin.gz.sdat`, and `visualizerSet.bin.gz.sdat` directly at their original package-relative paths.
- **Single Xbox deployment tree:** Xbox `mod-build` no longer duplicates rebuilt archives under `build/decompressed_bbx/` and `build/game_patch/`. The deployment copy appears once under `build/xbox360_replacements/`; that tree is recreated each build so stale replacements cannot survive a reverted change.
- **Archive wrapper provenance repair:** loading an existing Xbox Mod Workspace repairs known retail paths whose `.gz` / `.gz.sdat` suffix was lost by older `update-rip` asset regeneration. Future `update-rip` asset refreshes preserve the prior manifest source label instead of replacing it with the retained decompressed `.bin` path.
- **Verification follows the deployable artifact:** Xbox `mod-verify` now decompresses gzip/gzip-sdat replacements (or reads raw `.bin` replacements), parses the resulting BBX, and compares its SHA-256 to the build report without requiring a duplicate raw BBX copy.

## 2.10.0-dev24 WIP198

- **Update Rip final-gate recovery:** a WIP197 update that completed component swaps/manifest refresh but failed the last scoped verification can now resume from that refreshed manifest instead of falling back to a whole-rip rehash. The recovery journal is cleared after a successful retry.
- **Asset Viewer update regression:** updater staging no longer lets the new Asset Viewer inventory the previous `asset_viewer/` directory. The old behavior indexed its own HTML/data/thumbnails and could make later rebuilds progressively slower/bloated. Asset Viewer internal version advances to **2.2.1**.
- **Viewer dependency cleanup:** Stage Explorer and Visualizer Simulator are sibling tools rather than game-asset sources, so changing either no longer forces Asset Viewer reconstruction. Viewer rebuilds are limited to actual indexed-source changes or viewer-generator changes. Generator-only rebuilds seed only reusable thumbnails instead of cloning the complete previous viewer tree.
- **Windows/macOS host metadata tolerance:** `Thumbs.db`, `desktop.ini`, and `.DS_Store` are ignored by output-manifest/incremental verification because they can be created opportunistically by the host file browser and are not game/toolkit payload.
- **Actionable updater failures:** runtime `FormatError`/I/O failures no longer route through `argparse.error()`, so the desktop console does not dump the entire CLI command list. Final verification failures print each issue kind/path before the concise error.

## 2.10.0-dev24 WIP197

- **Desktop layout stability:** fixed-size global/Utilities contextual-help surfaces stop hover text from resizing the notebook; GMX Workbench refreshes its scrollregion after mode changes and resets to the top when returning to Simple mode. GUI 0.55.0-dev24.
- **Visualizer rebuild cache:** dataset v24 stores a privacy-safe, content/stat-bound BGM preview + 256-sample peak-envelope cache. Unchanged tracks skip repeat hashing/transcoding/envelope decoding, and retained-source updates seed the old preview cache into the new simulator staging directory. The stale hard-coded Visualizer resume version check now follows the current dataset constant.
- **Visualizer timing/position diagnostics:** browser catch-up steps sample the BGM envelope at their corresponding playback times instead of reusing one requestAnimationFrame sample. Native stage adaptive VOL SCALE behavior is preserved. June 10 `Function_82177DF0` closes the global Position scale as X/640, Y/360 on the 1280×720 target; a host-only native-anchor/source-bounds overlay helps measure remaining presentation differences without inventing offsets.
- **Localization editing:** `text_strings.tsv` and `text_strings_raw.tsv` are generated and accepted by `text-build`; Mod Workspace now chooses the readable TSV as the canonical editable `text.bin` file. Legacy CSV/JSON remain supported.
- **Editor-neutral Xbox deployment:** primary output is `build/xbox360_replacements/` with `XBOX360_REPLACEMENTS.json`; UI/docs describe compatible package editors generically, with Velocity/Horizon/Le Fluffie as examples only.

## 2.10.0-dev24 WIP196

- **Blender add-on 0.4.0:** raw GMX import defaults to **Solid only** for editing, assembled native `_E` edge objects are hidden non-destructively after import, Hide/Show Native _E controls are exposed in the sidebar, and automatic Style Preview is a new opt-in defaulting off.
- **Blender 5 compositor compatibility:** scene scanline preview no longer assumes `Scene.node_tree`; Blender 5 uses `Scene.compositing_node_group` and Group Output, while Blender 3.6/4.x keep the legacy branch. Unified-node fallback uses `ShaderNodeMixRGB` where the legacy compositor node is unavailable.
- **Historical WIP196 deployment naming (superseded by WIP197):** Xbox builds introduced complete rebuilt `.bin.gz`/`.bin` replacement containers under `build/velocity_replacements/` with `VELOCITY_REPLACEMENTS.json`; WIP197 renames this generic mechanism to `build/xbox360_replacements/` / `XBOX360_REPLACEMENTS.json` and removes editor-specific primary wording.
- `.siigmod` is relabeled as an optional shareable baseline-dependent delta rather than the primary deployment result. Successful packs show the exact saved path; failed background commands surface a popup with recent task output instead of disappearing into the detached task log.

## 2.10.0-dev24 WIP195

- **Visualizer gradient regression fix:** project-owner testing showed many WIP191+ authored visualizers collapsing into screen-filling gradients while several control stages remained structured. Retail stage 4-5 `SEQUENCE_12 / PARAM_7` proves the WIP191 1.5× Position multiplier is invalid for authored rendering: free Y=+360 would put the complete 128×128 source above the target, leaving no SHAPE pixels to seed feedback. WIP195 restores direct target-pixel Position mapping (`x=640+X`, `y=360-Y`) and advances the Visualizer dataset to **v23**. The viewport-first UI, fullscreen/preset controls, point-sampled recurrence and display-only 640×360 smooth resolve remain intact.
- **Mod Workspace help visibility:** the global **What does this do?** surface is now a compact always-visible strip above the Notebook instead of an off-screen footer. The general task log moves to a separate on-demand **Task log…** window, so making help visible cannot flatten the Game Rip console.
- **Desktop geometry regression:** live Tk/X smoke at 1120×780 and 1744×868 confirms populated Mod Workspace help, an available detached 900×380 task-log window, and a readable Game Rip console. GUI advances to `0.53.0-dev24`.


## 2.10.0-dev24 WIP194

- **Update Rip performance overhaul after WIP192 hands-on timing:** removed the remaining whole-rip filesystem passes from the normal migration path. An exact-profile rerun now returns through a zero-scan no-op instead of inventory/stat-cache walking thousands of output files before reporting that nothing changed.
- **Changed-scope manifest/cache maintenance:** routine migrations now carry untouched manifest/stat-cache rows forward in memory and enumerate/hash only rebuilt component directories plus the handful of changed validation files. Full-tree enumeration/hashing is reserved for explicit `Verify Rip` and forced/recovery cases where the old manifest cannot be trusted.
- **Cached destructive guards:** component overwrite protection now accepts a previously verified manifest-bound size/mtime/hash stat-cache row and re-hashes only changed-stat files. Legacy/no-cache components still fall back to real SHA-256 reads before replacement; `--force-modified` remains the explicit override.
- **Retained BBX hash reuse:** unchanged `decompressed_bbx/` archives reuse their verified manifest/stat-cache SHA-256 rather than being re-read simply to compare `.siig_source_state`. Changed-stat or legacy BBXs still receive a real SHA-256 read.
- **Report/privacy accounting is scoped too:** extension counts are projected from the old manifest plus changed scopes, and privacy checks re-scan only JSON generated by changed components. The updater console now states when the scoped path is active; GUI progress-stage prefixes remain compatible.
- Source-only updater regression now locks the zero-scan exact-profile path, scoped overwrite safety, changed-scope manifest/cache refresh, and retained-BBX smart reuse. GUI remains `0.52.0-dev24`.

## 2.10.0-dev24 WIP193

- Fixed the Game Rip layout regression where the WIP192 source-cache controls could squeeze the dedicated rip/update console to almost one line on common screen heights. Game Rip now uses a compact drop strip/cache/progress arrangement and reserves a 150-pixel minimum grid row for the console while still allowing it to expand.
- Compressed GMX Workbench Simple mode without removing functionality: core workflow actions share one row; model/output assembly folders are shared once; Boss and Enemy/Sub-boss assemblers live in nested tabs instead of being stacked; CENTIPEDE-only overrides are conditional; and Advanced import checkboxes use two columns. GUI advances to `0.52.0-dev24`.

## 2.10.0-dev24 WIP192

- Made the Game Rip outer-container sidecar cache visible in the GUI instead of leaving `.SIIG_Ripped.siig_outer_cache` unexplained. The tab now shows cache presence/size, offers **Refresh info**, and exposes a remembered **Keep source-package cache for faster resume/update** preference that maps to the existing `--no-outer-cache` behavior when disabled.
- Added **Clear cache…** with a mandatory warning/confirmation. The warning explicitly states that only cached unpacked ZIP/STFS/PKG source files are deleted, the verified rip and Mod Workspaces are left untouched, and later resume/rip work may take longer because the source package may need to be unpacked again. GUI advances to `0.51.0-dev24`.

## 2.10.0-dev24 WIP191

- **Visualizer Simulator UI overhaul:** the generated HTML is now viewport-first instead of a long scrolling two-column page. The 1280×720 canvas remains visible while a June 10-inspired translucent **VISUALIZER CHECK MODE** panel exposes **PRESETS / CHECK MODE / ADVANCED** tabs. The Stage/boss authored-event selector is always available in the top bar, applies immediately, and resets accumulated feedback so preset changes are watchable without scrolling.
- **Fullscreen + compact controls:** browser Fullscreen API support is available from the top bar or `F`; `M` hides/shows the control panel. Native Check Mode-style `X` reset and `Y` info-toggle shortcuts remain. Detailed ParameterSet/SequenceSet, BGM, schema and decoded DAT timeline controls remain available rather than being removed.
- **Hardware-derived position correction:** June 10 Position Free footage plus the retail-hardware stage 4-4 concentric-feedback center show that Check Mode position values need a **1.5× logical-to-1280×720 target scale**. The bridge is now `x=640+logical_x*1.5`, `y=360-logical_y*1.5`. This places fixed edge/corner centers just outside the visible target (`X=-32/640/1312`, `Y=-102/360/822`) instead of incorrectly forcing them inside. The +X-right/+Y-up axes and WIP171 ±448/±308 runtime table remain valid; only the direct-pixel scale is superseded. Exact upstream executable scale-call location remains bounded.
- **Chunky-feedback presentation fix without changing recovered sampler math:** recursive feedback remains point-filtered. The default host presentation adds a display-only high-quality **640×360 resolve → 1280×720** pass before the base/bloom composite, substantially softening large point-sampled blocks without feeding interpolation back into the Visualizer state. **Raw recovered RGB** remains selectable. Defaults become `0.8 px / 0.90 base / 0.46 bloom`.
- Visualizer dataset advances to **v22**. A retail-derived generation smoke retains **49 ParameterSets / 57 SequenceSets / 30 timelines / 243 commands / 39 authored events / 10 SHAPE images** and the generated JavaScript passes Node syntax validation.

## 2.10.0-dev24 WIP190

- **Utilities guidance fix:** Utilities now has its own always-visible **What does this utility do?** box inside the tab. Hovering or keyboard-focusing any Utilities field/button updates this local box directly instead of depending only on the global help area below the notebook.
- Renamed the ambiguous GUI button **Doctor** to **Diagnose toolkit / input** and the input field to **Diagnostic input (optional)**. The underlying CLI command remains `doctor`; behavior is still read-only diagnostics.
- Rewrote Utilities help text to state which actions are read-only reports (**Diagnose**, **Run selftests**, **Asset capabilities**, **Boss matrix**) and which write generated output (**Build viewer**, **Visualizer simulator**). GUI advances to `0.50.0-dev24`.

## 2.10.0-dev24 WIP189

- **Fast incremental Update Rip:** the updater no longer performs two whole-rip SHA-256 passes for routine migrations. Preflight always checks inventory/sizes; a manifest-bound stat cache reuses unchanged verified hashes and re-hashes only files whose stat fingerprint changed.
- **Scoped overwrite safety:** on legacy rips without the new cache, any component that is about to be replaced is cryptographically checked byte-for-byte against the old output manifest first, including same-size edits and edits whose timestamp was preserved. `--force-modified` remains the explicit override.
- **Incremental manifest refresh:** unchanged output hashes are carried forward from the prior manifest; only rebuilt components, changed validation metadata, new files, or size-changed files are hashed. `verify-output` / **Verify existing rip** remains the explicit full SHA-256 audit.
- **Fewer tree walks:** rip output extension counts are collected in one traversal instead of six independent recursive scans, and the updater reuses the already-computed privacy audit for its final inventory gate.
- Fresh `rip-game` outputs now create `validation/OUTPUT_STAT_CACHE.json` immediately from the just-hashed manifest, so their first future Update Rip can use the fast path. The stat cache is control-plane metadata and is excluded from the content manifest.
- Fixed `--refresh-assets` so it cannot be bypassed by the exact-profile `already_current` shortcut. Also fixed modern rip option inference: an explicit saved `convert_obj: false` now stays authoritative instead of being overridden by unrelated aggregate `.obj` outputs, which previously could trigger a full 23-archive reconversion. GUI advances to `0.49.0-dev24`.
- **Retail performance validation:** on the retained project-owner Xbox retail package, a complete WIP189 rip took **301.09 s** in this environment; the first fully reusable Update Rip took **9.98 s**, an exact-profile no-op rerun took **1.90 s**, and an explicit independent full SHA-256 Verify Rip took **9.70 s**. The fast update reused all **23/23 BBX archives / 2,593 resources** plus every higher-level generated component and computed only **5** new manifest hashes while reusing **16,666**. Timings are environment-specific; retail inputs/outputs are not bundled.

## 2.10.0-dev24 WIP188

- **Blender SIIG Style Preview (dev24 WIP188):** Blender add-on 0.3.0 renders preserved native `_E` line-pass geometry as removable white emissive curve previews and adds adjustable compositor-level scanlines after the existing final-image source. Refresh/remove operations leave imported GMX/assembly data untouched and restore the previous Composite input; auto-apply after SIIG import is optional. Exact native line rasterization/scanout remains explicitly unclaimed pending real-Blender/hardware comparison.

- **Flexible Xbox audio authoring:** Mod Workspace WAV replacements may now change duration and sample rate. Standard XWB entry duration/format/play-region metadata is rewritten, existing loop regions are remapped proportionally, and changed payloads are repacked while untouched XMA2 streams remain byte-identical.
- **Flexible channel input:** Xbox PCM16 keeps 1–6 input channels natively; 7–64-channel WAVs are accepted and downmixed to stereo. Native XMA2 encoding remains outside the toolkit.
- **Flexible PS3 SBlk authoring:** replacement WAVs may change duration and sample rate. The clean-room builder repacks the complete SIIG SBlk audio data section, rewrites stream offsets/sizes and center-note/fine pitch metadata, and regenerates PS-ADPCM loop/end flags while preserving untouched stream payloads. Multichannel input is accepted and downmixed to the bank's native mono stream form.
- **Retail structural validation:** a supplied retail Xbox looped XMA2 slot was rebuilt as 3-channel/32 kHz/different-duration PCM16 and reparsed successfully; a supplied retail PS3 stream was rebuilt from stereo/32 kHz/different-duration PCM16 with all 84 stream regions remaining contiguous and untouched stream bytes preserved. Retail payloads are not bundled.
- GUI advances to `0.48.0-dev24`; source-only regressions cover variable duration/rate/channel authoring. Retail runtime acceptance remains an external emulator/hardware test.

## 2.10.0-dev24 WIP186

- **Mod Workspace audio editing:** Xbox 360 `media/sound` is now an editable archive instead of a listen-only preview. **Open selected** exports only canonical WAV edit files; baseline hashes drive Exported -> Edited, and `mod-build` rebuilds the nested XACT/BBX path automatically.
- **Xbox XACT rebuild:** edited WAVs must preserve the original channels, sample rate, and sample count. Untouched streams remain byte-identical XMA2; edited slots are rewritten as XACT-supported PCM16. Xbox big-endian 16-bit PCM payloads are byte-swapped correctly. Native XMA2 re-encoding is still not claimed.
- **PS3 SBlk Mod Workspace integration:** supported `.bnk` resources now export canonical mono PCM16 WAVs and rebuild edited fixed-slot streams through the existing clean-room PS-ADPCM encoder.
- **Status semantics:** audio now behaves like other editable assets: Untouched -> Exported -> Edited -> Staged/Staged archive. GUI advances to `0.47.0-dev24`.
- Added source-only Xbox/PS3 Mod Workspace regressions. Runtime acceptance of edited audio on retail hardware/emulators remains an external validation step; variable-duration/topology-changing audio authoring remains open.

## 2.10.0-dev24 WIP185

- **Mod Workspace localization cleanup:** whole-archive localization exports now expose only rebuild-driving files inside the workspace: `text_strings.csv` for `text.bin` and the six `message_<language>_readable.nut` files for `message.bin`. Raw scripts, TXT summaries, combined CSV/JSON sheets and metadata remain available from standalone localization extraction but no longer clutter new/re-exported mod edit folders. Existing workspaces are not destructively pruned.
- **Mod Workspace Xbox sound preview:** `media/sound`/`sound.bin` is now recognized as listen-only XACT audio. **Open selected** extracts WAV/XACT preview material through the existing `xact2wav` path into `view/audio/<archive-key>` and opens that folder. Preview extraction deliberately leaves the asset **Untouched** because Xbox XACT/XMA rebuilding remains unsupported.
- **Simple GUI polish:** the action is renamed from **Open / edit selected** to **Open selected**, and sound archives are labeled `AUDIO · VIEW` so view-only extraction is not confused with an editable native round trip. GUI advances to `0.46.0-dev24`.

## 2.10.0-dev24 WIP184

- Promoted **List Assets** into the Simple Mod Workspace workflow and replaced the old log-only listing with an embedded archive/resource tree below the Mod Workspace controls.
- Double-click / **Open / edit selected** exports a supported untouched resource on demand and opens its editable representation; localization archive rows can export/open their whole editable text/message representation.
- Added persistent workspace-derived resource marks: **Untouched**, **Exported**, **Edited**, **Staged**, and **Added**. Marks are recalculated from edit-baseline hashes and staged/addition state, so they survive GUI restarts and are not session-only decorations.
- Added **Refresh marks** for changes saved by external editors; Build/Verify automatically refresh an already-open tree. Selecting a GMX also fills the advanced archive/resource fields for a smooth Simple-to-Advanced handoff.
- Added the `mod-browser` read-only backend report, GUI 0.45.0-dev24 diagnostics, and a regression that locks the Untouched -> Exported -> Edited -> Staged state transition.

## 2.10.0-dev24 WIP183

- Reclassified the browser Visualizer Simulator as a **polished proof of concept** instead of implying final-output hardware equivalence.
- Kept the recovered 1280x720 point-filtered recursive feedback recurrence unchanged, but replaced the overly dark `5.5 px / 0.32` host presentation with a brighter `1.4 px / 0.88` base plus `0.52` screen/bloom layer. Raw recovered RGB remains available at softness `0`, intensity `1`, bloom `0`.
- Removed `MediaElementAudioSourceNode` from generated BGM playback. FFmpeg now precomputes compact stereo peak envelopes at the native 256-sample / 48 kHz XAudio2 quantum while the HTML media element plays the browser preview directly.
- User-loaded browser audio is decoded only to create the same peak envelope and is never routed through the metering graph, removing the local-file/CORS muting failure mode.
- Advanced Visualizer dataset to **v21**, added dedicated WIP183 research/validation/regression coverage, and retained exact Xenos final-composite and browser/native meter-phase boundaries.

## 2.10.0-dev24 WIP182

- Promoted `est_020.gmx` to the project-owner-confirmed shared **OCTOPUS / GLUTTONY pre-detonation bomb** model.
- Promoted `est_021.gmx` to the project-owner-confirmed **detonation / explosion** model produced by that bomb.
- Added independent executable corroboration for the bomb family: `Gluttony::DischargeBomb` asserts `EShotManager::eENEMY_SHOT_TYPE_ID_SG_BOMB`; the retained `EShotSg` subsystem supplies the 3D enemy-shot state machinery.
- Kept the evidence boundary precise: the direct `SG_BOMB -> est_020 -> est_021` filename/resource binding and exact OCTOPUS shot-type trace are still unisolated, so those points are not overclaimed.
- Updated the living `est_*` identity split to **5 confirmed effect usages / 6 speculative entries** and added dedicated WIP182 research/validation/regression coverage.

## 2.10.0-dev24 WIP181

- Promoted `est_012.gmx` from an unidentified cube to a project-owner-confirmed **shared interactive target cube**, backed by direct JOLYNE and UNKNOWN executable resource loads.
- JOLYNE setup creates ten line helpers and then loads `est_012` (`0xE6` retail / `0xE7` May prototypes); its update path drives the orthogonal segment chain and endpoint object, matching the project owner's fuse-end cube observation.
- UNKNOWN's retail visual-controller setup (`Function_82130190`) independently loads `0xE6 -> est_012.gmx` and provisions up to 120 helpers; its separate runtime `0xBD` resource is a primitive/texture resource rather than another GMX.
- Cross-build UNKNOWN confirmation: May 11 factory case `0x4C` constructs `Function_821441B0`; setup `Function_82144298` repeats the 120-helper pattern and loads shifted `0xE7 -> est_012.gmx`. This also corrects a transient nearby-string misattribution to VERTEBRATE before packaging.
- Updated the living model-identity/effect audit to 3 confirmed `est_*` effect usages and 8 speculative entries, with dedicated WIP181 validation/regression coverage.

## 2.10.0-dev24 WIP180

- Added a reproducible `est_011`...`est_021` effect-model audit with derived native/converted geometry fingerprints and explicit ownership confidence.
- Proved `est_012` is the only audited `est_*` resource with a top-level runtime-registry slot across all five retained builds (`0xE6` retail-lineage, `0xE7` May prototypes).
- Proved `est_011` and `est_014` share byte-identical converted geometry while retaining distinct native GMX containers, corroborating their matching hexagon silhouette without inventing ownership.
- Preserved `est_013`/`est_015` as project-owner-confirmed usages and all other `est_*` mappings as unresolved/speculative.
- Added regression coverage; no external Blender or game-runtime claims are changed.

## 2.10.0-dev24 WIP178

- **Entity model identity catalog:** added 82 project-owner model-stem identifications spanning players, enemies, sub-bosses, bosses, and `est_*` effect/projectile shapes. Confirmed identities and speculative interpretations are stored separately; friendly labels are not misrepresented as executable-internal strings.
- **Asset Viewer 2.2.0:** native GMX and converted glTF cards can now expose/search friendly identities, entity class, 2D/3D or console-only scope, and confidence status. Speculative `est_*` labels are visibly marked rather than silently normalized.
- **CELL/LUST/SHUTTER reconciliation:** the five-build runtime registry independently confirms `emy_044` at runtime `0x97`, `emy_051` at `0x9D`, and `emy_052` at both `0x5A`/`0x5B` in every retained build. The catalog remains project-owner identification evidence; these names are not claimed as recovered executable strings.
- **Visualizer Check Mode follow-up sweep:** a second ten-segment June 10 hardware batch confirms that BG RGB remains visibly active with `BG:A = 0`, while ordinary source scale, feedback magnify, Stick VolumeSet, Add Rotation, and SHAPE ordering remain consistent with dataset v20. No renderer-math or dataset-version change is required. Exact Xenos render-target alpha/final-composite semantics and browser/native BGM snapshot phase remain open. Capture media stays external and unbundled.

## 2.10.0-dev24 WIP177

- **Visualizer Check Mode hardware feature sweep:** ten trimmed project-owner June 10 Xbox 360 captures isolate Position Free/Fix, source Scale X/Y, Magnify Scale X/Y, SHAPE RGBA, BG RGBA, rotation override, and SHAPE selection. Capture media remains external and unbundled.
- Visualizer Simulator dataset **v20** keeps recovered renderer math unchanged but makes the hardware-confirmed control relationships explicit: min/max fields are VolumeSet endpoints, ordinary Scale X/Y affects the new SHAPE source while Magnify X/Y affects prior feedback, Position Free is inactive when Position Fix is nonzero, and Rotation Base/Add are inactive while Fix Rotation is nonzero.
- BG RGBA is now labeled as direct clear controls. The BG:A sweep is recorded as evidence that native alpha is independently controllable, while exact Xenos render-target alpha storage/final-composite equivalence remains an explicit boundary rather than being guessed with Canvas alpha.
- Live simulator status now reports effective source scale and SHAPE tint for direct hardware comparison. Added `VISUALIZER_CHECK_FEATURE_SWEEP_DEV24.md`, WIP177 validation, and a dedicated regression.

## 2.10.0-dev24 WIP176

- **Visualizer native min/max contract:** project-owner real-hardware Magnify A testing triggered the June 10 build's own `VisualizerMain::SetMagnifyAlpha` assertion (`a1 >= a0`, source line 446). Executable cross-checks prove the same max≥min rule for Magnify Scale X/Y and SHAPE R/G/B/A ranges.
- Visualizer Simulator dataset **v19** keeps exactly those proven pairs valid during interactive edits and ParameterSet application instead of reproducing the native debug assertion. Ordinary SHAPE Scale X/Y is deliberately not generalized: its recovered setter stores all four values without the sibling ordering assertion.
- The same eight-capture hardware batch corroborates existing Add Rotation × volume, signed Fix Rotation, raw BGM meter, and strong Magnify X/Y interpolation semantics; browser/native XAudio2 snapshot phase remains an explicit boundary.
- Added `VISUALIZER_NATIVE_RANGE_CONTRACT_DEV24.md`, WIP176 machine-readable validation, and a dedicated regression. Project-owner MKV capture media remains external and unbundled.

## 2.10.0-dev24 WIP175

- **GIGANTIC UFO presentation correction:** project-owner clarification establishes that SIIG model assets share one native facing convention under the top-down game view. Removed the dev23-era GIGANTIC-UFO-only `-90°` X presentation root from `gigantic_ufo_complete` instead of rotating every other boss to match it.
- Preserved the exact native GIGANTIC UFO hierarchy unchanged: 1× `bos_003.gmx` root + 36× `bos_003a.gmx` children attached to `lt_001..lt_036`; child-local matrices remain identity and the three non-model `0xB4` helper slots remain excluded.
- Generic GMX→glTF axis handling is unchanged. This is a presentation-policy correction only; it does not alter runtime transforms, animations, locators, or boss behavior.
- Added a dedicated orientation research note and WIP175 validation artifact; the existing GIGANTIC UFO regression now rejects any reintroduction of special-case presentation metadata.

## 2.10.0-dev24 WIP174

- **Visualizer Xbox 360 BGM quantum recovery:** Microsoft XAudio2 documentation fixes the Xbox 360 audio-graph quantum at **5 1/3 ms** and defines `pPeakLevels` as maximum absolute channel level during one processing pass. At SIIG's 48 kHz BGM rate this is exactly **256 samples**.
- Visualizer Simulator dataset **v18** requests a 48 kHz `AudioContext`, uses a 256-sample unsmoothed analyser window per channel, computes `max(abs(sample))`, and keeps the recovered left/right arithmetic mean. A browser that refuses 48 kHz is visibly marked as an approximate-duration fallback.
- Narrowed `VISUALIZER_BGM_PROCESSING_CADENCE`: native window size/duration is resolved; only host/browser snapshot phase and scheduling relative to native XAudio2 quantum boundaries remain bounded.
- Private project-owner hardware footage independently cross-checks the 256-sample window (first supplied capture: 9 overlay samples, ~0.9967 correlation / ~0.0080 RMSE after one capture gain + A/V alignment fit). Capture media remains external and is not bundled.
- Added `VISUALIZER_BGM_QUANTUM_DEV24.md`, machine-readable WIP174 validation, Microsoft XAudio2 Audio Graph provenance, and a dedicated regression.

- **Stage Explorer maturity correction / UX de-jank (dev24 WIP172):** project-owner testing confirmed that the browser Stage Explorer is not yet a faithful or accurate gameplay map viewer: converted atlas presentation can still look jittery, the motion control integrates only recovered SCROLL_01/02/03 vectors rather than executing the full DAT sequence, and the old layout overemphasized experimental previews. Dataset v8 now declares `proof_of_concept` / `research_inspector_not_gameplay_renderer`, shows decoded MAP layers and DAT records before motion/3D previews, labels those previews experimental, and removes fidelity language that implied complete stage playback. Timeline search/category filtering now updates only the command table instead of rebuilding all canvases/resetting the motion frame on every change. Existing executable-backed MAP/DAT/route/placement evidence is retained.
- **Visualizer Position Fix runtime-initializer correction (dev24 WIP171):** project-owner June 10 Check footage disproved WIP170's alias interpretation. The static float2 table is only a pre-startup image: June 10 `0x82564470` loads `-308.0`, patches **+308** into raw 1..3 Y slots and **-308** into raw 7..9, leaving 4..6 at Y=0. Retail and May 11 repeat the same six-store patch. Dataset **v16** now exposes the full native grid: upper `1/2/3`, middle `4/5/6`, lower `7/8/9` across X `-448/0/+448`; raw 0 remains Free X/Y. Raw 5 is fixed center and is no longer collapsed with raw 0. The WIP170 +Y-up Canvas bridge remains correct.

## 2.10.0-dev24 WIP173

- Recovered exact `VL_CHANGETIME` (`0xCD`) semantics from the June 10 VisualizerScript path. The command stores a SequenceSet change-time minimum/maximum, immediately rolls the current threshold, and uses an exclusive upper bound when the span is nonzero.
- Recovered the exact SequenceSet stepping order: current dirty row applies first; `threshold < counter` arms the next slot; `-1` wraps to slot zero; the new row applies on the following active update. Constructor change-time defaults are 18000/18000.
- Recovered the Visualizer RNG path: two Microsoft-CRT `rand15` calls are concatenated by `Function_8249A9D8`; the underlying LCG is `state = state*0x343FD + 0x269EC3` modulo 2^32. Hardware seed is timer-derived.
- Visualizer Simulator dataset v17 now performs executable-backed SequenceSet timing during decoded DAT playback, rebuilds state deterministically when seeking, and exposes a sim-only RNG seed/reroll control plus live threshold/counter/RNG diagnostics.
- Corrected DAT semantic labeling for `VL_CHANGETIME`; the earlier WIP168-era “interpolation” wording is historical/superseded, not a current unresolved boundary.

- **Visualizer coordinate/Position Fix correction (dev24 WIP170):** project-owner same-stage hardware/simulator comparison exposed a vertical mirror in the browser bridge. The retained `SEQUENCE_4 -> PARAM_3` row uses free position `(10, +360)`; native Visualizer coordinates are center-origin with **+X right / +Y up**, so that anchor belongs at `(650, 0)` on the 1280×720 target, not `(650, 720)`. Dataset **v15** now converts with `canvas_x = 640 + game_x; canvas_y = 360 - game_y` for both SHAPE and recursive-feedback anchor transforms. Its Position Fix alias interpretation was later superseded by WIP171 after tracing the startup initializer that patches the upper/lower Y rows; WIP170 remains period-correct as a historical checkpoint, while WIP171 carries the corrected runtime grid.
- **Retained-source rip updater (dev24 WIP169):** desktop GUI **0.44.0-dev24** adds **Update existing rip** plus the `update-rip` CLI and `SIIG_Update_Rip.bat`. The updater requires only a completed rip with `decompressed_bbx/`, fingerprints updater-relevant toolkit modules so same-version WIP changes are detectable, and now performs a component-aware migration: archive conversions are SHA/options/schema checked and reused when already current, while localization/systemfont/audio/structured outputs and Stage Explorer/Visualizer/Asset Viewer rebuild only when their schema/generator or an upstream dependency changed. `--refresh-assets` remains an explicit full-conversion override. The updater writes `RIP_UPDATE_STATE.json` + `RIP_UPDATE_REPORT.json`, refreshes the deterministic output manifest, and runs the completion verification gate. Clean old-manifest integrity is required by default; an excluded recovery journal makes interrupted updates rerunnable without the original package.
- **GMX Workbench/rip-console + Visualizer hardware-presentation/audio correction (dev24 WIP168):** desktop GUI **0.43.0-dev24** makes the full GMX Workbench vertically scrollable (scrollbar + mouse wheel) and gives Game Rip its own console-style, append-only per-file stream with vertical/horizontal scrollbars, copy and clear controls while retaining the compact phase/count summary. Visualizer dataset **v14** synchronizes decoded `VL_SEQUENCESET` stage events to their active ParameterSet row, exposes `SEQ/PARAM` in the status line, and can advance authored DAT frames at the logical 60 Hz rate. Project-owner hardware-vs-simulator screenshots recalibrate the explicitly host-only final presentation to **5.5 px softness + 0.32 intensity** by default (raw recovered RGB remains available at 0 px / 1.0), without changing the proven point-sampled recurrence. Browser WMA/AT3 previews no longer reroute the media element into a suspended Web Audio graph: analyser routing occurs only after a user-unlocked running `AudioContext`, so native playback stays audible; FFmpeg previews are normalized to stereo 48 kHz and the selftest now rejects silent generated previews.
- **Visualizer real-hardware BGM normalizer fidelity (dev24 WIP167):** project-owner Xbox 360 recordings of June 10 stages 4-2/4-4/4-5 exposed working `VOL / MIN / MAX / VOL SCALE / AVE RAW / AVE SCALE` diagnostics. Executable tracing recovers the normal scripted-stage post-meter path: `Function_82177510` defaults the adaptive window to 300 frames; `VL_VOLUME_SCALE`/0xCE calls `Function_82177300` to replace that window (all three reference stages author 180); `Function_821773F0` derives MIN/MAX with a 0.001 minimum span and maps raw VOL to normalized VOL SCALE; `Function_82177648` drives normal parameter interpolation with VOL SCALE; and `Function_82175FA8` exposes 180-frame RAW/SCALE history averages. Visualizer dataset v13 now keeps dedicated Check Mode on raw BGM while stage playback uses the adaptive model and hardware-style diagnostics. Upstream browser-vs-XAudio2 meter-window cadence remains explicitly approximate.
- **Visualizer presentation softness + console-native BGM previews (dev24 WIP166):** Visualizer dataset v12 adds a display-only softness pass (default 0.65 px, adjustable 0..2 px) after the recovered point-sampled feedback recurrence, preserving the executable-backed Xenos sampler semantics while matching the softer in-game presentation more closely. The simulator now discovers Xbox 360 `.wma` and PS3 `.at3`/ATRAC3+ BGM from a user rip and uses FFmpeg to create source-hash-cached browser-safe MP3 previews (AAC/M4A fallback) without modifying native files. Real retail validation generated 53/53 Xbox WMA and 56/56 PS3 AT3 previews while retaining the known 30 timelines / 243 Visualizer commands on both platforms.

- **Usable-preview one-click retail workflow (dev24 WIP165):** desktop GUI 0.42.0-dev24 promotes **Rip + verify** as the normal Game Rip action, remembers working folders/options in a per-user settings file outside rip/project outputs, can open the verified Asset Viewer automatically, and forwards the finished rip into Mod Workspace. Resume now caches nested outer packages, fast-skips unchanged gzip/BBX inputs, reuses PS3 SDAT plaintext only when encrypted-source and plaintext SHA-256 bindings both match, safely reuses Stage Explorer/Visualizer/Asset Viewer output, and preserves valid viewer thumbnails incrementally. The rip completion gate writes a fresh deterministic SHA-256 manifest then independently checks inventory/sizes/partial files/privacy; `verify-rip` aliases the explicit later full-byte verifier. Manifest/verification hashing uses a bounded thread pool while preserving sorted deterministic output. Canonical retail validation passes 16,567/16,567 Xbox and 16,422/16,422 PS3 full re-hashes with zero integrity/privacy issues; PS3 confirms six internally authenticated SDATs / 18 blocks with no fallback. Proprietary inputs/outputs remain external and the project license remains intentionally unselected.

- **Explicit Bmap/DAT WARNING-request compatibility validation (dev24 WIP164):** route playback now cross-checks caller-supplied `Bmap13`/`Bmap15` DATs against the proven `WARNING[12]`/`WARNING[14]` special reload requests. Reports expose matching authored request frame(s), competing special WARNING requests, resource/descriptor selection, and normalized reload frame 130 while explicitly refusing to infer a unique canonical DAT owner or route-object initialization/start frame. The living boundary registry now separates this resolved compatibility check from the still-open ownership/activation question.

# v2.10.0-dev24
- **LUST identity closure + Blender add-on 0.2.1 headless validation (dev24 WIP179):** synchronized the living runtime-0x9D boundary with the project-owner `emy_051 = LUST` catalog while preserving the absence of an executable-internal `LUST` token; fixed the add-on's unpacked-source toolkit auto-discovery so it walks past `addons/` to the actual toolkit root; added a minimal headless `bpy` import/register/discovery/logical-part regression while retaining the external real-Blender UI gate.

- **Generator output-capacity mechanism + final MAP current-note sync (dev24 WIP163):** recovered retail PS3 `stageGenerateMapInit` at `0x001327E8`: its three capacity factors are `0x20`, each multiplied by `0x180`, so every generated MAP layer receives `0x3000` (12,288) bytes; the `0x001329DC` append path bounds writes against the same product. Against the retained iOS `0x1800` (6,144-byte) layer capacity, the runtime output buffer is proven to have doubled exactly 2×. The living boundary is narrowed to the still-unknown *authoring/design rationale* for the console resource corpus's 2× stored-cell total rather than allocator mechanics. Also removed the last stale current `MAP_RENDERER_NOTES.md` claim that per-layer scroll state still needed recovery and extended the regression guard to cover that note.

- **Current-facing MAP/Stage Explorer accuracy sync (dev24 WIP162):** removed three stale pre-v7/pre-WIP159 limitations that survived in live documentation/output metadata. MAP SCROLL_01/02/03 runtime trajectories are already reconstructed at the logical 30 Hz timebase, so only player-facing layer names and exact gameplay viewport composition remain open; the capability matrix no longer lists “full scroll playback” as future work. Stage Explorer metadata now states that GMX AABB proxies use the recovered native `S * Rz * Rx * Ry * T` placement transform instead of claiming they are unrotated. Regressions block both stale boundary wordings from returning.

- **PS3 SBlk fixed-slot native audio replacement (dev24 WIP161):** added a clean-room Sony PS-ADPCM encoder plus `sblk-replace`. A mono PCM16 WAV with the selected slot's exact sample rate/sample count can replace that existing stream while preserving bank size, stream offsets/capacity, table/name bytes, and every original frame control byte. Synthetic encode/decode + one-stream SBlk regressions verify bounded PCM error and unchanged structural bytes. Variable-duration/topology SBlk authoring, edited-bank PS3 runtime acceptance, and Xbox XACT/XMA2 replacement remain explicit boundaries.

- **Normal-stage route/DAT filename inference (dev24 WIP160):** `route-playback` and `route-camera-playback` can now omit the DAT argument (or use `auto`) for deterministic `XmapW_S.bin` and `map4_/map5_` resources. The inferred `levelW_stageS.dat` is cross-checked against the executable-backed stage/script registry and resolved from the nearby game layout. Explicit DAT arguments remain supported. `Bmap13`/`Bmap15` retain their proven WARNING-driven reload chains without inventing a unique owning DAT; all boss/special `Bmap` ownership and route-object activation frames remain explicit.

- **Stage placement Euler-order closure (dev24 WIP159):** retained retail Xbox 360 and PS3 transform consumers prove the fixed `0x118` stage-placement model path as row-vector `S * Rz(z) * Rx(x) * Ry(y) * T`. Stage Explorer now transforms all eight GMX root-AABB corners with runtime scale, stored degree rotations, and placement origin in orbit/top-down/POV views. The former axis-aligned proxy approximation is removed; a non-symmetric 90°-Y fixture regression-locks the result. Route↔DAT activation, collision, and unrelated scene-control effects remain explicitly bounded.

- **Living unresolved-boundary registry (dev24 WIP158):** added a machine-checked current-facing audit that separates genuinely open research/implementation/runtime gates from superseded historical “unresolved” notes. It explicitly keeps opaque GPU/GMX/transform/name semantics open instead of guessing, while marking later closures such as Survival status bytes, route Hermite resampling, template-free GMX, camera `face_bias`, and the four recovered Visualizer sampler/blend/shader boundaries as no longer current. Also corrected current README/provenance drift (rigid skin import is implemented; route Hermite resampling is closed) without rewriting sealed historical validation.

- **Visualizer ScreenSprite SHAPE shader closed (dev24 WIP157):** private retail 60-byte `ScreenSpritePS` Xenos microcode decodes to one 2D SHAPE texture sample followed by a four-channel multiply with the runtime float4 RGBA tint; the ordinary source pass uses Add(SrcAlpha, OneMinusSrcAlpha). Real user-rip SHAPE PNGs now retain native RGBA, multiply all four channels by the runtime tint, stay point-sampled, and draw source-over. The former luminance×alpha mask / `source-in` approximation is removed and regression-blocked; proprietary shader bytes and SHAPE pixels remain unbundled. Visualizer dataset v11.

- **Visualizer EffectBlur pixel shader closed (dev24 WIP156):** private retail 72-byte Xenos microcode decodes to one 2D feedback sample, `r0.w = Alpha.w`, and direct color export; sampled texture alpha does not weight feedback RGB. Simulator feedback buffers now use an opaque RGB working model so Canvas `lighter` matches the recovered RGB recurrence without an extra source-alpha factor. Proprietary shader bytes remain unbundled.

- Visualizer EffectBlur blend closure (dev24 WIP155): retail `Function_821595F0` immediately before `Function_82159CB8` enables blending and sets Xenos source factor 6 (`SrcAlpha`) plus destination factor 1 (`One`), producing packed `RB_BLENDCONTROL` `0x01060106` with Add operations. Recursive feedback now uses Canvas `lighter` instead of the incorrect `source-over` approximation. Corrected `DAT_8200E3C8`/`DAT_82569008` from the earlier "render-state block" assumption to its actual two-element vertex declaration. Exact EffectBlur pixel-shader sample/color math remains bounded.

- THE SUN timing/synchronization closure (dev24 WIP154): retail `Function_8212BE00` + `Function_8223AEC0` prove the opening 48-slot B3 protection field reaches full during root state 0 while the native body is forced to clip 0/frame 0. States 9/10/11 alone drive the 0..0x16900 body-progress law (step 0x600; 61 updates out, 60-update hold at frame 40, 61 back). GUI 0.41.0-dev24 exposes the synchronized opening preset and `the-sun-controller`; June 10 independently preserves the same timing law.
### Visualizer SHAPE sampler closure + generic TEX sampler decode (dev24 WIP153)

- Closed the independent Visualizer SHAPE texture-sampler boundary from the private retail TEX resources themselves. All ten resources are `0x10034` bytes with byte-identical 0x34-byte serialized resource headers; the six-dword fetch constant is `81000002 00000086 000FE07F 00000C14 00000000 00000A00`.
- Cross-checking Xenia's public `xe_gpu_texture_fetch_t` field layout proves repeat X/Y/Z addressing, point min/mag/mip filtering, disabled anisotropy, 2D dimension, and the already-known 128×128 size. Xenia remains documentation-only here; no new upstream implementation code is copied.
- Visualizer Simulator dataset v8 now disables Canvas image smoothing around transformed real user-rip SHAPE draws, independently from the recursive feedback draw. Procedural fallback geometry remains approximate and no proprietary pixels are bundled.
- Extended the generic Xbox TEX parser/inspection metadata with decoded clamp modes, min/mag/mip filters and anisotropy so serialized sampler state is no longer opaque outside the Visualizer path.
- Added dedicated SHAPE-sampler research/validation plus generic TEX and Visualizer sampler regressions. Exact original sprite-shader color/mask math and EffectBlur blend equation/factors remain deliberately unresolved.

### Visualizer Xenos feedback sampler closure (dev24 WIP151)

- Recovered the previous-feedback render-target fetch constant through May11 `Function_821AA630 -> Function_8226F240 -> Function_8226EA98 -> Function_8226F5C0`; fetch dword 3 is `0x00001414`.
- Xenia's public `xe_gpu_texture_fetch_t` layout identifies the feedback sampler as repeat addressing with point min/mag/mip filtering and anisotropy disabled. Xenia is used here as documentation only; no new upstream implementation code is copied.
- The browser disables `imageSmoothingEnabled` around the recursive feedback draw and restores it immediately afterward. WIP153 independently closes SHAPE-source filtering; the EffectBlur fixed-function blend is now recovered as additive SrcAlpha/One; exact pixel-shader sample/color math remains bounded.
- Corrected stale standalone-ANM format notes to the already-proven `char[16] + start_frame + end_frame + loop_flag` 28-byte record layout.
- Added dedicated sampler research/validation and regression coverage.

### Systemfont alias-scale closure (dev24 WIP150)

- Closed the derived-font alias-scale approximation through retail `Function_8215ACB0`: all recovered ASCII aliases (letters, digits, space and punctuation) use exact runtime scale **0.5**, while the 85-entry halfwidth-katakana path retains exact native scale **1.0**.
- Added `reference/systemfont/systemfont_aliases.csv` with all 152 recovered alias entries and their executable-backed lookup path/scale, plus dedicated research and validation reports.
- Real-retail local generation now produces 6,879 cmap entries (6,730 native + 149 unique aliases), with 94 unique half-scale aliases, 55 unique native-scale aliases and **0 approximate aliases**. Generated font binaries remain local-only and are not bundled.

- MANDALA Workbench fidelity: `mandala_all_members_phase0` now exposes all 72 allocated members, including the 32 `bos_005f.gmx` center circles in executable-exact phase-0 geometry. The BC circles remain explicitly marked as state-8-activated, so the complete inspection preset does not falsely claim simultaneous gameplay activity. GUI 0.40.0-dev24 makes this the default complete MANDALA assembly while retaining the separate state-7/state-8 presets.

### Camera preset word 11 resolved (dev24 WIP148)

- Closed the long-standing `shared_model_material_scalar_unresolved` field: retail preset word 11 is **`face_bias`**.
- Xbox raw PPC proves material virtual `+0x18` stores the scalar at wrapper `+0x60`; the renderer uploads it for `collada_face1`, and embedded vertex shader `0x8208D408` names c9 `faceBias` and offsets vertices by `-Normal * faceBias.x`.
- Renamed the semantic camera table/API field to `face_bias`, added a dedicated validation report/research note, and regression-checked all 32 retail presets at the authored value `0.2`.

### Real Visualizer SHAPE input (dev24 WIP147)

- Retail validation confirms all ten `visualizer.bin` SHAPE textures convert to exact 128×128 PNGs in the recovered resource order.
- Visualizer Simulator dataset v6 now discovers those PNGs from a user-supplied full rip and embeds them only in the locally generated HTML; no proprietary pixels are bundled in the toolkit.
- The browser derives a luminance×alpha mask from each real texture before applying recovered runtime color/alpha, preserving real sprite morphology while keeping unresolved Xenos shader/blend behavior explicitly bounded.
- Procedural shapes remain the source-only fallback when a rip does not contain the real Visualizer PNGs.

### Visualizer BGM peak-meter fidelity (dev24 WIP146)

- Resolved the former host-audio approximation: June 10 executable tracing proves VolumeSet/BGM is the arithmetic mean of two XAudio2 per-channel **peak** levels, consumed directly as a linear 0..1 float.
- Replaced the browser's RMS/−60..0 dBFS remap with left/right time-domain peak sampling and stereo averaging; mono falls back to its single channel.
- Browser analysis-window cadence remains explicitly approximate; no claim of XAudio2 processing-pass timing identity is made.
- Added `VISUALIZER_BGM_METER_DEV24.md`, machine-readable validation, and an explicit Microsoft Learn API-documentation provenance row.

- GUI 0.39.0-dev24 updates the compact 18-family Boss Assembler to expose the exact OCTOPUS and WATER STRIDER retail spawn poses plus NO_NAME main/Bonus and Extra 2-8 approach actions, while THE MOON remains explicitly native-inspection-only. The Utilities boss matrix reports the current 14 deep / 3 gameplay-pose / 1 native-only evidence split.
- Corrected THE MOON's retail visual-controller interpretation: `Function_8212B760` preserves RGB and writes only the fourth/material-alpha component for `collada_edge1`, `collada_face1`, and `collada_face2`; slot 0 also performs the exact ten-step 36-degree Z rotation. State-0 edge alpha is 0.9, face alpha ramps 0→1 over controller timers 131..262, strict partial alpha selects visual resource `+0x1A8`, full opacity restores `+0x1A4`, and nonzero visual slots use alpha 0.4. Added the `the-moon-controller` exact sampler/report, regression coverage, and dev24 research/validation artifacts while keeping the canonical Workbench representation native-inspection-only until controller visual slots/materials are mapped to exact exported GMX render nodes.
- Audited all six originally requested Enemy/Sub-boss Workbench families (ENVY, KEEPER, OPPRESSOR, GLUTTONY, VANITY, TELEPORTER) against the accumulated dev24 runtime evidence. No new guessed transforms were justified: the Workbench now explicitly preserves exact static hierarchies, deterministic runtime actions, normalized exact relationships, inspection-only ownership sets, and unresolved live behavior as separate evidence classes. Added `reference/research/ENEMY_SUBBOSS_WORKBENCH_AUDIT_DEV24.md` plus source-only validation.
- GUI 0.38.0-dev24 fixes the Entity Assembler family-count mismatch (8 total families: the six requested families plus GREED/WRATH), adds **Assemble + preview** for compact Boss/Entity workflows using the existing local Asset Viewer model preview, and makes Advanced one-click assembly actions reuse the same remembered model/output folders with deterministic filenames instead of reopening directory + Save As navigation for each family.
- Game Rip live progress is now structured into a phase line, latest-detail line and running `Assets / glTF / PNG / errors` counters while preserving the full unbuffered task log. Container decryption/decompression, BBX extraction, per-resource extraction and GMX/TEX conversion phases are recognized directly from the CLI progress stream.
- Reworked the Visualizer Simulator around the recovered runtime render pipeline instead of the old dev23 visual approximation. May 11/June-era executable tracing proves a 1280×720 ping-pong render target, ten 128×128 SHAPE sources, exact Position Fix X/Y anchors, SHAPE-first draw order, source-only accumulated/fixed rotation, and scale/alpha-only previous-frame feedback around the same anchor. The browser still uses procedural stand-ins for proprietary SHAPE pixels and explicitly marks GPU filtering/blend-state details as unresolved. See `reference/research/VISUALIZER_RUNTIME_RENDER_PIPELINE_DEV24.md`.
- Completed the contiguous retail boss/enemy DAT semantic pass for runtime opcodes `0xA2..0xAB`: PROGRESSIVE_UFO, OCTOPUS, BUTTERFLY, AXON, WATER_STRIDER, CRAB, ULTIMATE_UFO, SQUID, VERTEBRATE and NO_NAME. Generic `param_N` tails are replaced with executable-backed HP, shot/discharge timing, route, selector/type and target fields; variable-length WATER_STRIDER/CRAB records remain valid. June 10 retained class/debug strings independently resolve semantic identities `0xA5 = AXON` and `0xA7 = CRAB` without falsifying the executable opcode-name table. OCTOPUS's one-short class boundary read is intentionally not promoted because every authored retail/June record ends after the five common fields. See `reference/research/BOSS_DAT_RUNTIME_A2_AB_DEV24.md`.
- Resolved adjacent runtime `0x9D` ownership and DAT boundary: `emy_051.gmx` maps through runtime+1 switch case `0x9E` to `Function_82106F78`; its +0x5C DAT-tail vtable slot is a no-op, so all 80 retail records are exactly the five common fields (spawn condition, body HP, raw/512 speed, X, Z). The script/gameplay name remains unresolved and no invented Workbench family is added.
- Reconstructed GLUTTONY runtime 0x9C DAT semantics from `Function_820E7CE0`, raw vtable copy stub `0x82102F58`, `Function_82103380` and `Function_821031A0`: arg1 is body HP, arg2 is raw/512 route speed, args3..22 encode up to ten X/Z route points, arg23 is point count, and arg24 is the shared HP value for both `emy_050a` helpers. All seven retail records are regression-covered; the old generic `param_6..param_24` labels are removed for 0x9C.
- Reconstructed LINE_INVADER runtime 0x9A as a procedural polyline entity rather than a missing GMX: DAT args3/4 + args5..22 define up to ten X/Z path points, arg23 is total point count, arg24 selects the path resource mode, arg25 is active-member count and arg26 is a 30 Hz spawn interval scaled to 60 Hz. Retail contains no `emy_047.gmx`/`emy_048.gmx`, so no fake GMX assembly is added.

- Repaired the dev24 WIP ENVY/GREED off-by-one interpretation: retail `Function_821489F8` switches on `runtime_type + 1`, so ENVY `0x98` / `emy_045.gmx` selects case `0x99` -> `Function_82102898`, while GREED `0x99` / `emy_046.gmx` selects case `0x9A` -> `Function_82103C58`. ENVY retains its exact 10-unit/±2 chain geometry; GREED gains exact Level 4-1 spawn and first-hover-entry anchors plus executable-backed state/timer metadata.
- Replaced the discarded early-dev24 ENVY lattice interpretation with the raw-PPC-correct runtime 0x98 chain controller: exact retail Level 4-2 count 20 / heading 3, 10-unit ordinal spacing, alternating ±2-unit perpendicular offsets and alternating −30°/+30° yaw. The compact six-member form remains an explicitly parameter-chosen inspection reference, not a universal pose.
- Added WRATH runtime 0x9B reconstruction from `Function_8210CFE8`: exact Level 4-4 body spawn `(213,-500,280)`, 55-sample/60-Hz state-0 approach and exact snap to anchor `(213,0,80)`, plus executable-backed live state-1 X/Z rates and attack timing. The linked 0x39/0x38 allocations are now proven transient attack/procedural-effect pools (`Function_8213CBC0` / `Function_8213D708`), not permanent multipart GMX body pieces.
- **WIP:** branched from sealed v2.10.0-dev23 for further enemy/sub-boss runtime-layout reconstruction; dev23 remains immutable.
- Corrected TELEPORTER's early dev24 WIP timing interpretation from raw retail PPC. State 2 resets its activation timer with `(step*30)/30`, so normal `step=1` starts one new helper every update. The renderer therefore has 14 reachable state-2 snapshots, not a tick-152 midpoint. The unreachable tick-152 catalogs were removed.
- Added exact Stage 5-4 TELEPORTER left/right state 0→4 actions: 20 state-0 split-root samples, 30 center-root state-1 samples, 14 state-2 helper-transfer samples, 30 destination-center state-3 samples and 20 state-4 split-root samples. Each non-looping action contains 114 samples at 30 Hz and stops before the next state-0 random-X selection.
- Added executable-reachable TELEPORTER state-2 tick-7 snapshots using mode table `[0,0,1,2,3,4,5,-1,-1]`, preserving the retail renderer's hidden newest-zero helper, destination stack, active 1/3→full→1/3 stretched members, and source stack.
- Promoted VANITY placement from ownership-only metadata: retail opcode 0x38 initializes the two B1 helper records at primary X−74 / X+74 with matching Z, and main-game rows resolve the arrival formation to primary `(213,32)` with helpers `(139,32)` / `(287,32)`.
- Added `vanity_state2_primary_descent_local`: retail state 2 decrements the hardcoded 1000 counter by 10 to 500 and `FUN_820fa5b8` maps that exactly to local Y 0→−100 over 50 updates. Live state-2 X/Z steering and B1 helper activity remain explicitly unresolved and are not synthesized.
- Added `reference/research/VANITY_TELEPORTER_RUNTIME_DEV24.md` and `reference/tables/VANITY_TELEPORTER_RUNTIME_DEV24.csv`; DAT semantic labels for TELEPORTER/VANITY coordinates are corrected in the decoder/reference schema.

# v2.10.0-dev23

- fixed one-click outer ZIP handling for original Xbox 360 distributions that contain an extensionless LIVE/CON/PIRS STFS payload (and analogous nested PS3 PKG payloads). Game Rip now content-detects exactly one nested package after bounded ZIP extraction, continues into that package automatically, and rejects ambiguous multi-package ZIPs instead of guessing. Fresh original-retail validation completed ZIP -> extensionless STFS -> game files -> BBX extraction/conversion with 23/23 archives, 2,593 resources, 0 errors, followed by full output verification of 16,540 hashes.
- added an optional non-core `tools/systemfont_derived_font.py` experiment for local TTF/OTF/WOFF/WOFF2 bitmap-outline derivatives from the decoded 32 px systemfont atlas + recovered glyph table. It preserves the recovered 32 px line height / 28 px baseline and 0.5 ASCII alphanumeric alias scale, marks unresolved alias scaling as approximate, and deliberately never bundles generated fonts because they embed game glyph artwork.
- Stage Explorer v7 replaces whole-corridor-only 3D inspection with route-local views: World 4 defaults to top-down route follow, World 5 to forward POV, with route progress, a final-route arena inspection window, pixel-stable 2D scroll drawing, and clearly provenance-tagged gameplay-reference background presets. Known boss background observations are attached only to boss spawn names/frames decoded from DAT, keeping owner-observed visuals separate from executable-derived semantics.
- Asset Viewer now navigates the full `SIIG_Ripped` folder hierarchy with breadcrumbs/Up/child-folder controls and recursive scope, while converted glTF cards already serving as native-GMX previews are hidden as duplicates by default but remain indexed and optionally visible. Real-retail validation indexed 12,240 files with 8,985/8,985 previewable thumbnails and identified all 486 converted GMX duplicates.
- fixed Game Rip progress repaint starvation: the Tk queue consumer now processes bounded batches instead of draining an always-growing resource stream in one callback, and the Game Rip tab adds a live latest-message panel/indeterminate activity bar while retaining the full per-resource log.
- corrected `progressive_ufo_classic` C3 barrier direction by removing the old dev16 side-sign override; the two outer rotations now match retail `Function_82536720` exactly: +1.74532926 rad at X=+115 and -1.74532926 rad at X=-115.
- reconstructed June 10 Visualizer Check Mode controls: X resets the feedback surface, Y toggles debug text, VolumeSet selects exact `from BGM`/`from Stick` sources, Fix Rotation is a signed numeric angle, and the simulator now parses external ParameterSet/SequenceSet rows plus decoded `VL_SEQUENCESET` quick presets without bundling proprietary game data.
- Blender add-on 0.2.0 adds assembled glTF/GLB import and one hideable `SIIG_PART_*` collection per logical assembly master, fixing the apparent per-part visibility failure caused by overlapping native `_F` solid and `_E` outline objects while preserving hierarchy/animation.
- expanded the GMX Workbench beyond bosses with a separate six-family Enemy/Sub-boss Assembler for the project-owner identifications ENVY (`emy_045`), KEEPER (`emy_032`), OPPRESSOR (`emy_043`), GLUTTONY (`emy_050`), VANITY (`sbs_002`), and TELEPORTER (`sbs_003`). KEEPER exports the exact root + 8 locator-helper hierarchy with odd-index 180° Y rotation; OPPRESSOR exports the exact AD×1/AE×2/AF×8 helper allocation on `lt_001..lt_011`; GLUTTONY exports the root + paired B0 locator helpers while leaving live target-facing yaw unbaked. VANITY and TELEPORTER remain clearly labelled dynamic owned-set inspection exports instead of invented gameplay poses.
- added an ENVY six-member zig-zag gameplay-reference preview. Retail controller evidence independently recovers alternating -30°/+30° member facing, 10-unit index spacing, one-at-a-time chain growth, and the later fly-away state. The ENVY display name remains explicitly user-identified because no matching internal retail name string has been recovered.
- corrected GMX Visual Pass semantics so Solid/Outline/Combined only apply when a model genuinely contains both detected solid and outline passes. Single-pass GMXs now export normally and preserve requested/effective mode metadata; regression coverage added.
- added `reference/research/CONSOLE_ENEMY_SUBBOSS_ASSEMBLY_DEV23.md` to preserve controller addresses, model/runtime membership, naming provenance, dynamic-layout boundaries, and the unresolved `emy_045` 0..60 ANM vs 31-matrix-track sampling question.

- Completed the dev22 primary-controller trace for the five intentionally conservative boss families. THE MOON is controller-internal; LADYBUG owns four dynamic field-space `bos_004a.gmx` helpers rather than proven rigid attachments; OCTOPUS has no second local registry-model lookup; WATER STRIDER binds `lt_001..003` then `lzr_001..004` and owns the 0..1440 timed loop; NAMELESS/NO_NAME owns `bos_018a.gmx` but has no local ownership path for retail `bos_018.gmx`. `boss-matrix` now records evidence grade, finding, promotion gate, and evidence functions for all five.
- The compact Simple-mode Boss Assembler now covers all **18 main-game boss families** in the project-owner order, displaying 5-6 as **NAMELESS** while retaining internal/runtime family `NO_NAME`.
- GUI 0.35.0-dev22 replaces the long Simple-mode stack of repeated boss assembly buttons with a compact Boss/Variant selector, a remembered model folder and remembered output folder, plus deterministic `Assemble selected` / `Save manifest` actions. Switching bosses no longer forces the user through two folder/file-dialog navigation chains for every export; specialist HORNET propagation and other low-level controls remain in Advanced mode.
- Stage Explorer v6 defaults to separate, fit-to-panel MAP previews so the optional three-layer zero-scroll overlay no longer makes the first view look visually dense or force horizontal scrolling.
- Clicking any MAP cell now shows the selected atlas tile at its exact native **96×96** source resolution plus a separate pixel-inspection magnifier, preserving X/Y flip flags without conflating the enlarged inspection view with native resolution.
- Main level 4/5 entries now include an executable-backed 3D route/placement preview with yaw/pitch inspection controls. When extracted stage GMXs are present, Stage Explorer reads their proven root AABBs and recovered runtime scale to draw clickable model-size wire proxies and expose model/record/slot/position/scale/rotation metadata. Proxy boxes intentionally remain unrotated until stage-placement matrix order is proven; this is explicitly not a textured gameplay render.
- Rebuilt `visualizer-sim` around the **June 10 Visualizer Check Mode** footage: a ping-pong feedback/trailing-copy renderer magnifies/rotates the previous image and injects a fresh SHAPE stamp, matching the observed outward-growing translucent copies instead of the old procedural-ring approximation. The simulator now exposes the recovered **49 ParameterSet presets / 57 SequenceSet entries / 29-value parameter schema** and exact ten-resource SHAPE order (`WhiteCircle`, `line`, `3line`, `square`, `triangle`, then the five `*2` variants), while unresolved sprite pixels, Position Fix/Fix Rotation semantics and exact compositing order remain explicitly labeled approximate.
- Added `reference/tables/MAIN_GAME_BOSS_SUBBOSS_ORDER_DEV22.csv` from the project-owner main-game list, preserving its possible-error caveat and excluding bonus stages. `UNKNOWN` and `NAMELESS` are kept distinct; NAMELESS maps to executable/toolkit family `NO_NAME`.
- Asset Viewer now gives text/code assets generated thumbnail cards, writes a lightweight SVG DAT timeline instead of expensive raster DAT previews, and exposes a localhost-only desktop bridge so GUI-launched **Open file** actions use the operating system default application; direct offline HTML use retains the browser-compatible fallback. Both GUI callbacks now open the real `SIIG_Asset_Viewer.html` entry point.
- Added four end-to-end GMX visual-pass modes: **Separate solid+outline** (default), **Solid only**, **Outline only**, and **Combined**. Selection follows native `_F` face/solid and `_E` edge/outline bones first, with material/primitive fallback for atypical files. Combined retains both visual passes while merging selected native tracks into one glTF animation clip. The same selection is threaded through single-GMX export, boss assembly, Game Rip, and the GUI.
- Game Rip child processes now run unbuffered and emit per-archive, per-resource, and per-conversion progress messages suitable for the GUI task log, including extraction, converted-output creation, completion counts, and errors.
- Strengthened GUI regression coverage after catching and repairing a dev22 structural regression that had folded GMX Workbench controls into Mod Workspace. The final GUI restores separate `Game Rip`, `Mod Workspace`, `GMX Workbench`, and `Utilities` tabs while retaining the compact Boss Assembler.
- Fresh supplied Xbox retail validation completed on the final dev22 code: 2,593 extracted resources, 1,351 PNGs, 486 glTF models, 86 decoded WAV streams plus 53 retained WMAs, 92 Stage Explorer entries / 17,335 commands, 30 Visualizer timelines / 243 commands, and a 9,384-file Asset Viewer with 8,669/8,669 previewable thumbnails. Output verification checked 16,544 hashes with zero issues.
- Dependency-free regression suite is **106/106** at sealing.

## 2.10.0-dev20

## 2.10.0-dev21

- Corrected the retail visual-controller factory index rule: `Function_821489F8` switches on `runtime_type + 1`; added corrected constructor/object-size mapping for all 18 boss families.
- Reattributed factory case `0x47` / `Function_8212B638` to THE MOON (`0x46`) and case `0x48` / `Function_8212BA68` to THE SUN (`0x47`). THE SUN now correctly owns its `Function_8212BB58` B2/B3 allocation and `Function_8212BBF0` long-wave update path.
- Added a parallel controller audit for THE MOON, LADYBUG, OCTOPUS, WATER STRIDER, and NO_NAME while preserving their conservative native-only assembly boundary until static gameplay transforms are proven.
- Extended `boss-matrix` with visual-controller runtime type, factory case, constructor and object size for every boss.
- GUI 0.32.0-dev21 adds stdlib-only Windows Explorer drag-and-drop for one Game Rip source file or folder. Dropping selects the input but never auto-starts extraction; Browse remains the fallback.
- Added drag/drop safety regression coverage and the cross-boss `factory_case = runtime_type + 1` invariant to the dependency-free selftest.


- Unified the console boss roster into one audited **18-family** registry with one canonical catalog per boss and a machine-readable `boss-matrix` command.
- Classified coverage without overclaiming: **13 families** have deep executable-backed runtime reconstruction; **5 families** remain native-inspection-only pending deeper state/auxiliary tracing.
- Added conservative native-body catalogs for THE MOON (`0x46`/`bos_001.gmx`), LADYBUG (`0x49`/`bos_004.gmx`), OCTOPUS (`0xA3`/`bos_010.gmx`), WATER STRIDER (`0xA6`/`bos_014.gmx`), and NO_NAME (`0xAB`/`bos_018a.gmx`).
- Fresh retail validation confirmed all **18/18 canonical root GMXs**, including native animation-track preservation for the five new catalogs: 0/8/12/10/1 tracks respectively.
- Added cross-boss reconstruction/reference matrices, canonical catalog resolution checks, fresh-retail root hashes/structure metadata, GUI diagnostics, and a Utilities-tab Boss matrix action.
- Preserved all prior evidence boundaries: native-inspection identity matrices are inspection-space transforms only; dynamic/random boss states are not collapsed into invented canonical gameplay poses.
- GUI 0.31.0-dev20 and dependency-free regression suite pass **102/102**.

## 2.10.0-dev19

- Resolved THE SUN's native `bos_002.gmx` extended-arm motion: six 41-sample matrix tracks target `c1/d1/d2` on both E/F sides, with exact sample 40 exposed as a static inspection pose.
- Corrected visual-controller ownership: retail `0x47` drives the body internally; `0xB2/0xB3` auxiliary allocation is performed by neighboring `0x48` setup.
- Identified `bos_002b.gmx` / runtime `0xB3` as THE SUN's repeated long-wave segment visual. Retail allocates 48 and the full ramp activates all 48 as four groups of twelve.
- Recovered exact full-ramp transforms from fixed-point executable state: X `69/165/261/357`, Z `176..198` in steps of 2.
- Added `the_sun_native_body`, `the_sun_extended_arms`, and `the_sun_long_wave`. Extended arms and maximum wave remain intentionally separate because exact temporal synchronization is unproven.
- GUI 0.30.0-dev19 adds THE SUN form selection and manifest/export actions in Simple and Advanced modes.
- Added THE SUN research, reference tables, real-retail validation, and dedicated regression. Dependency-free suite is **101/101**.

## 2.10.0-dev18

- Reconstructed AXON's runtime model pool as a standalone **0xA5 `bos_012.gmx` native whole-body representation** plus a 17-record subordinate pool: **1×0xCA `bos_012a.gmx` core + 16×0xCB `bos_012b.gmx` petals/blades**.
- Recovered the exact retail two-ring CB layout from `Function_82110378` / `Function_8210EF00`: eight petals at 45° spacing, followed by eight staggered by 22.5°; stable expanded radii are 75 and 220 with Y offsets -3.0 and -5.5.
- Reproduced the runtime per-petal orientation `Y = -90 - runtime_angle - phase` and position `X/Z = radius * sin/cos(runtime_angle + phase)` at the canonical phase-angle-0 expanded snapshot.
- Added `axon_native_body`, `axon_expanded_petals`, and `axon_exposed_core`; the mutually exclusive A5 and CA/CB representations are deliberately kept separate instead of being stacked into a false 18-model scene.
- Fresh retail exports validate native A5 as **1 instance / 42 meshes / 76 nodes / 32 animations**, expanded CA+CB as **17 / 34 / 84 / 0**, and exposed CA as **1 / 2 / 20 / 0**.
- GUI 0.29.0-dev18 adds an AXON form selector in Simple and Advanced modes plus manifest export.
- Added AXON runtime-layout/transform reference data, real-retail validation, research documentation, and a dedicated regression. Dependency-free suite is **100/100** through development gating.

## 2.10.0-dev17

- Reconstructed SQUID as **1×0xA9 `bos_016.gmx` animated body + 8×0xDA `bos_016a.gmx` legs** in its first modeled phase.
- Recovered the exact retail attachment table `0x8200A5D4..0x8200A5F0`, mapping leg records 1–8 to native body locators `lt_000..lt_007`; records 9–13 are non-GMX helper/control objects and are excluded.
- Proved the phase transition: retail state 8 `Function_8212AE30` disables records 1–8 through virtual `+0x54` -> `Function_820FC270`, leaving the A9 body active; June 10 independently preserves the same eight-record disable loop in `Function_82145E68`.
- Added `squid_phase1_legs` and `squid_phase2_body`; locator parenting preserves all 8 native body animation clips without baking guessed transforms.
- Fresh retail export validates phase 1 as **9 instances / 18 meshes / 44 nodes / 8 animations** and phase 2 as **1 / 2 / 12 / 8**, with the retained retail GMX hashes re-confirmed from a fresh STFS extraction.
- GUI 0.28.0-dev17 adds a Phase 1 / Phase 2 SQUID selector in Simple and Advanced modes plus manifest export.
- Added SQUID runtime/phase reference tables, research and real-retail validation records, and a dedicated regression. Dependency-free suite is **99/99** through development gating.

## 2.10.0-dev16

- Added `progressive_ufo_classic` as a second evidence-backed five-part PROGRESSIVE UFO formation while preserving the original `progressive_ufo` catalog unchanged.
- Recovered retail pose table `0x82568180` and proved runtime use through `Function_82127018` in major states 5 and 8; June 10 table `0x825D95B0` and retail PS3 independently preserve the same five records.
- Reproduced SIIG's exact Euler path (`Rz * Rx * Ry * T`, runtime Y-sign convention) for the classic formation instead of using simplified screenshot rotations.
- Fresh retail export validates 5 instances / 10 meshes / 20 nodes / 10 preserved native animations with bounds about X ±144.283, Y -40.270..40.233, Z -60.613..58.204.
- Added an Original/Classic PROGRESSIVE UFO selector to Simple and Advanced GUI modes, formal reference/validation artifacts, and a compatibility regression guarding the original dev3 formation.
- Dependency-free suite is **98/98** through development gating.

## 2.10.0-dev15

- Reconstructed GIGANTIC UFO's dedicated visual hierarchy as exactly **1×0x9E `bos_003.gmx` root + 36×0xB5 `bos_003a.gmx` children**.
- Recovered the exact native child attachment order `lt_001..lt_036`; the runtime renderer evaluates the corresponding root locator for each B5 child rather than using guessed/baked offsets.
- Cross-checked the same 1+36 hierarchy in retail Xbox, June 10 Xbox and retail PS3.
- Classified the three intervening 0xB4 renderer slots as helper/control slots rather than model assets and explicitly excluded them from the assembly.
- Fresh retail export validates `gigantic_ufo_complete` as **37 instances / 74 meshes / 185 nodes / 0 animations**, with bounds approximately X/Y ±269.5926 and Z -66.1034..61.1107.
- Added GIGANTIC UFO manifest/export actions to Simple and Advanced GUI mode, formal reference tables/validation, and a dedicated regression.
- Dependency-free suite is **97/97** through development gating.

## 2.10.0-dev14

- Corrected CENTIPEDE's runtime model semantics: each of the 32 links preallocates A0/BE handles, but role-driven display selects exactly one visible form per link rather than rendering both simultaneously.
- Reconstructed the canonical initial ring as **2×A0 `bos_007.gmx` endpoints + 30×BE `bos_007a.gmx` bodies**, radius 80, 11.25° spacing, starting at -90°, with exact per-link Y orientation and doubly linked topology.
- Proved body destruction severs both neighbor links and promotes the newly exposed ends to head/tail roles, which automatically swaps them to A0. Endpoint destruction takes the alternate reform path.
- Recovered the final-phase threshold as fewer than six surviving links (≤5). Survivors are unlinked and promoted to independent A0 movers; runtime destinations are randomized, so dev14 intentionally does not publish fabricated static split/reform/final presets.
- Cross-checked the ring math and ≤5 threshold on June 10 Xbox and retail PS3.
- Fresh retail export validates `centipede_initial_combat_ring` as 32 instances, 64 meshes and 128 nodes, with bounds approximately ±102.3733 X/Z and ±2.88236 Y.
- Added the CENTIPEDE assembly catalog, topology table, research/validation reports, Simple/Advanced GUI manifest/export actions, and a dedicated regression.
- Dependency-free suite is **96/96** through development gating.

## 2.10.0-dev13

- Reconstructed VERTEBRATE's persistent phase-1 body as **2×AA `bos_017.gmx` endcaps + 30×DB `bos_017a.gmx` pillars** from retail Xbox, June 10 Xbox and retail PS3 runtime construction logic.
- Recovered the exact tower transform ladder: pillars at `Y=-630+70*i` for `i=0..29`, lower cap at `Y=-608` with Z=180°, upper cap at `Y=1448` at native orientation.
- Recovered the 120-frame collapse/rebase transition and phase-2 body as **two co-located `bos_017.gmx` endcaps only**, at boss-local origin with effective Z rotations 90° and 270°.
- Confirmed from fresh retail assets that `bos_017c..j` are heavily animated attack auxiliaries (22–25 native tracks each), so they are deliberately excluded from the persistent structural presets; `bos_017b` is likewise kept separate.
- Added `vertebrate_phase1_tower` and `vertebrate_phase2_endcaps`, exact reference tables, real-retail export validation, Simple/Advanced GUI selection, and a dedicated regression.
- Fixed the CLI `TOOLKIT_VERSION` constant to track the sealed release version again; dev13 reports `2.10.0-dev13` consistently.
- Dependency-free suite is **95/95** through development gating.

## 2.10.0-dev12

- Resolved UNKNOWN as one `bos_006.gmx` with 14 named internal form branches (`uk01..uk14`), no native MOTN/ANIM, and executable-driven visibility switching rather than a multipart boss.
- Proved from fresh retail GMX geometry/material payloads that **uk08 is an exact visual duplicate of uk01**, yielding 14 named branches / 13 unique visuals.
- Recovered the retail Xbox normal gameplay selector: states 1..22 cycle `uk01..uk12` at normalized 30 Hz using a 12-tick counter, state 0 forces `uk01`, and state 23 freezes the current selector. `uk13/uk14` are registered but outside that normal cycle.
- Cross-checked the same 14-name renderer and 12-tick counter architecture in June 10 Xbox and retail PS3.
- Added `unknown_form_01..14`, `unknown_all_forms`, Simple/Advanced GUI selection, runtime-cycle reference metadata, two machine-readable tables, real-asset validation, and a dedicated regression.
- Project-owner observation that the 2D UNKNOWN counterpart also duplicates its first form is retained as corroboration only; the 3D duplicate is independently asset-proven.
- Dependency-free suite is **94/94** through development gating.

## 2.10.0-dev11

- Reconstructed all four BUTTERFLY forms from retail Xbox loader `0x82111F48`, its 10-record phase/component table, the A4/C4-C9 model table, and the exact `lt_001..lt_048` locator pointer range.
- Proved `bos_011d/e/f.gmx` are repeated wing modules rather than extra boss phases: C7 is the large square module, C8 the small square module, and C9 the elongated rectangle.
- Added `butterfly_phase_1` through `butterfly_phase_4`: 1, 5, 19, and 49 model instances respectively, with every module parented under the executable-selected native `lt_*` node.
- Cross-checked the complete 10-record phase table in June 10 Xbox (`0x8212B490`, table `0x8200F1A0..0x8200F23C`) and the A4/C4-C9 identities against retail PS3 registry evidence.
- Re-extracted the seven real retail `bos_011*.gmx` files from the project owner's retained Xbox package and recorded hashes, native locator counts, and module geometry roles.
- Real-retail glTF exports validate phase 1/2/3/4 as 1/5/19/49 instances, 2/18/60/150 meshes, and 4/32/116/296 nodes. Phases 2–4 retain all three native body animations so wing modules follow their parent locators.
- Added a four-phase BUTTERFLY selector plus manifest/assembly actions to Simple and Advanced GUI 0.22.0-dev11.
- Added executable/GMX research, a 20-row retail+June component table, real-asset validation, and a dedicated regression. Dependency-free suite is **93/93** through development gating.

## 2.10.0-dev10

- Proved HORNET high-level state 3 has a deterministic A1-only exposed-core entry: the common transition reset restores `bos_008.gmx` at native motion 0/sample 0 while all 125 subordinate BF/C0 records are reset to state `-1`.
- Cross-checked the same state/reset architecture in retail Xbox, June 10 Xbox and retail PS3.
- Added `hornet_exposed_core` and a dedicated regression; full-armor, 13 prism-wall variants and state-6 propagation remain separate evidence-backed workflows.
- Re-extracted the project owner's re-uploaded original Xbox retail STFS and confirmed the HORNET `bos_008*` plus `enemy.anm` SHA-256 values match the historical dev5 corpus exactly.
- Real-retail exposed-core export validates 1 instance, 2 meshes, 4 glTF nodes and native local bounds of approximately ±13.8054.
- GUI 0.21.0-dev10 adds separate Simple/Advanced exposed-core actions instead of conflating the state with full armor.
- Dependency-free regression suite is **92/92** through development gating.

## 2.10.0-dev9

- Reconstructed ULTIMATE UFO's complete retail allocated GMX pool as A8 + D0–D9 families: **126 allocated model instances**, while keeping simultaneous phase visibility distinct from allocation.
- Recovered exact named-locator attachment hierarchy: D5→A8 `lt_002..003`, D4→A8 `lt_004..024`, D6→D0/D1 `lt_226..257`, and D7→D2/D3 `lt_258..321`.
- Recovered opposite runtime Y-rotation metadata for the D0/D1 FAN and D2/D3 RING parent GMXs and preserved those parents/children as a true glTF hierarchy instead of baking guessed XYZ offsets.
- Added eight retail phase catalogs: states 2/3/6/7/8/9/11/12, with exact Mframe metadata and D8 airlock / D9 core identities.
- Added ULTIMATE UFO state selector, manifest export and one-click assembly to Simple/Advanced GUI 0.20.0-dev9.
- Added attachment/phase tables, research/validation provenance, and ULTIMATE UFO regression coverage; suite is **91/91** through development gating.
- No fresh real-retail `bos_015*.gmx` export is claimed in dev9 because those proprietary GMXs were not present in the persistent research Library; runtime attachment resolution is performed against the user's own extracted GMXs and rejects missing/ambiguous locators.

## 2.10.0-dev8

- Added `mandala_initial_combat`: exact state-7 activation snapshot with 40 visible instances (20×B7, 2×B8/B9/BA/BB, 12×4A); later 32×BC intentionally excluded.
- Recovered five-build MANDALA formation evidence, native signed 8.8 trig convention, exact slot-to-model dispatch, and structural scales 40/56/82/109/4×29/4×20.
- Added Simple/Advanced MANDALA GUI assembly actions in GUI 0.19.0-dev8.
- Added 40-row transform table, research/validation provenance, and MANDALA regression; suite is now 90/90 through development gating.

## 2.10.0-dev7

- Recovered HORNET state 6 as a deterministic 13-seed propagation family inherited from the dev6 prism-wall A1 slot; no second random seed is chosen.
- Proved state 5 clears all 45 record flags and hides A1 before propagation, so each inherited seed has a deterministic wave sequence.
- Reconstructed seed-only activation followed by alternating orthogonal/diagonal 9×5 expansion to full 45-cell coverage, cross-checked in June Xbox, retail Xbox and retail PS3.
- Added procedural `hornet_propagation_SS_wave_WW` assembly catalogs using reached C0 prisms only at the wave activation instant; invalid seeds/waves and an unqualified default are rejected.
- Added Advanced GUI propagation seed/wave controls and assembly/manifest actions in GUI 0.18.0-dev7.
- Added cross-platform research/table/validation provenance plus a representative real-retail 29-prism export validation.
- Added the HORNET propagation regression; suite is now 89/89 through development gating.

## 2.10.0-dev6

- Resolved HORNET's state-4 C0 prism wall as exactly 13 runtime-valid variants: one animated A1 root occupying the selected 5×9 grid slot plus 44 C0 prisms.
- Added the 13 `hornet_prism_wall_XX` catalogs and Advanced GUI selector while deliberately rejecting an unqualified random default.
- Cross-checked the exact root-slot table and wall geometry in June Xbox, retail Xbox and retail PS3.
- Added representative real-retail wall export validation and raised the suite to 88/88.

## 2.10.0-dev5

- Changed the beginner/default CRAB catalog from the dev4 airborne first-visible root sample 167 to the executable/ANM-backed first landed combat-loop sample 1; preserved the old formation as `crab_first_visible`.
- Confirmed project-owner Blender validation of CRAB and PROGRESSIVE UFO; documented that PROGRESSIVE UFO's slight barrier tilt is authored inside `bos_009b.gmx` rather than an outer C3 transform error.
- Resolved HORNET C1 / `bos_008c.gmx` as a genuine meshless 126-track formation rig rather than a questionable/corrupt model.
- Recovered HORNET runtime construction as A1 + 125×BF armor + 125×C0 prism pool + 1×C1 controller across June Xbox, retail Xbox and retail PS3.
- Added `hornet_full_armor`: A1 sample 0 plus 125 BF cubes on the exact C1 sample-0 5×5×5 lattice, with real-retail external export validation.
- Added one-click **Assemble HORNET** and advanced HORNET manifest actions to GUI 0.16.0-dev5.
- Kept native SIIG assembly scale/units unchanged and documented Blender Frame All/Selected navigation rather than introducing an unproven unit conversion.
- Added the HORNET assembly regression; suite is now 87/87 through final release gating.

## 2.10.0-dev4

- Reworked the desktop GUI for beginners without removing expert functionality. Simple mode is now the default; Advanced mode restores the full Mod Workspace and GMX Workbench controls.
- Added a persistent **What does this do?** help box. Hovering or focusing fields, Browse buttons, action buttons and advanced checkboxes explains the control in plain language.
- Simplified Mod Workspace into a numbered Create → Open/Edit → Build → Verify → Pack workflow in Simple mode.
- Simplified GMX Workbench into the common Original GMX → Export for Blender → Edit glTF → Rebuild GMX workflow, while keeping one-click PROGRESSIVE UFO and CRAB assembly visible.
- Advanced GMX graph/schema/JSON/skin/animation controls remain available unchanged behind the mode switch; Simple mode does not silently enable aggressive synchronization options.
- Resolved console opcode `0xA7` as CRAB through the explicit `bos_013.gmx` registry + `Crab.cpp` construction/update linkage; historical dev19 unresolved records remain unchanged as historical artifacts.
- Recovered CRAB's deterministic first-visible nine-part formation across June Xbox, retail Xbox and retail PS3: A7 root animation segment 3, native sample 167, runtime 180° Y root rotation, `CD/CC + 2×CE + 4×CF` locator-driven children, ±81 propodus and ±23 dactyl offsets.
- Added per-instance `pose_sample` to multi-GMX assembly export. Posed GMXs bake one native animation sample into static node transforms and suppress that instance's animation channels so separately instantiated children cannot drift out of sync.
- Added the built-in `crab` assembly catalog, `gmx-assemble-catalog crab`, GUI one-click **Assemble CRAB**, and a synthetic nine-instance pose/export regression. Suite: 86/86.

## 2.10.0-dev3

- Recovered PROGRESSIVE UFO runtime part order `A2,C2,C2,C3,C3` and the first five-part formation directly from executable initialization/state code.
- Filled the assembly catalog with exact local translations: body `(0,0,0)`, lasers `(-90,0,-10)` / `(90,0,-10)`, barriers `(-160,0,-50)` / `(160,0,-50)`; rotations are zero and scale is identity.
- Cross-checked the same constants/formation in June Xbox, retail Xbox, and retail PS3.
- Added `gmx-assemble-catalog progressive_ufo` and GUI 0.14.0-dev3 **Assemble PROGRESSIVE UFO**.
- Added source-only research/table/validation provenance and a five-instance matrix/export regression. Regression suite: 85/85.

## 2.10.0-dev2

- Added rigid mesh partitioning by joint: one glTF mesh may contain several disjoint unit-weight rigid islands. Triangle groups are compacted into separate native MESH/ARRY graphs and attached to their corresponding BONEs after per-joint inverse-bind rebaking. Triangles spanning more than one joint are rejected.
- Added manifest-driven multi-GMX glTF assembly export (`gmx-assemble`) with explicit per-instance transforms, hierarchy/material/animation remapping, combined buffers, texture copying, source hashes, and an assembly report.
- Added `gmx-assembly-template progressive_ufo`: evidence proves one bos_009.gmx body, two bos_009a.gmx laser machines, and two bos_009b.gmx barrier machines. Exact side-component runtime matrices remain unresolved and are deliberately not guessed.
- Desktop GUI 0.13.0-dev2 exposes the PROGRESSIVE UFO manifest and generic assembly exporter.
- Regression suite: 84/84.

# Changelog

## 2.10.0-dev1

- Opened the 2.10 feature line with **rigid inverse-bind geometry rebaking** for standard glTF skins. Single-joint `JOINTS_0`/`WEIGHTS_0` bindings may now carry a non-identity affine selected `inverseBindMatrices` transform.
- Rebaked `POSITION` values use the selected inverse-bind affine transform; `NORMAL` values use the inverse-transpose of its linear 3x3 and are renormalized. Translation is excluded from normals as required.
- Singular linear transforms are rejected when normals are present instead of emitting invalid geometry.
- Rigid skin validation now happens before MESH/ARRY compilation so both donor-layout and fully synthesized-schema paths receive the same bind-space correction. The later BONE/PARE pass reuses the exact same binding record.
- True blended/multi-joint skinning remains intentionally unsupported: no retail per-vertex weight representation has been confirmed, and `MESH.skin_index` remains evidence-bounded to the observed `0xFFFF` no-vertex-skin value.
- Added an independent non-identity-bind regression with translated/non-uniformly-scaled geometry, inverse-transpose normal verification, repaired root AABB, report provenance, rigid export, and singular-matrix rejection. Suite is now **82/82**.
- GUI advanced rigid-skin control now advertises inverse-bind rebaking. GUI version is **0.12.0-dev1**.

## 2.9.0-dev7

- Added an evidence-bounded **rigid glTF skin compatibility importer**. `--sync-rigid-skins` accepts `JOINTS_0`/`WEIGHTS_0` only when every vertex has the same single unit-weight joint and collapses that binding to SIIG's proven `BONE -> MESH` attachment model.
- True blended/multi-joint weights are rejected explicitly instead of inventing unsupported native weight streams. Secondary JOINTS/WEIGHTS sets and non-identity selected inverse-bind matrices are also rejected in this checkpoint.
- New synthesized MESH records now default `skin_index` to the corpus-observed `0xFFFF` unless a donor or explicit override says otherwise.
- Skin joint nodes are synthesized as native BONEs, hierarchy lookup crosses non-bone armature/container nodes, and the skinned mesh/material attachment is transferred to the selected joint BONE rather than creating a fake BONE for the glTF mesh-object node.
- `gltf2gmx-new` and Mod Workspace enable rigid-skin compatibility automatically; template-backed import exposes it through `--sync-rigid-skins` and a GMX Workbench checkbox.
- Added a positive/negative regression: a two-joint glTF skin with all vertices rigidly weighted to the child becomes two native BONEs plus one attached MESH, while a 50/50 blended vertex is rejected. Suite is now **81/81**.
- External corpus cross-check: 150 supplied retail player/enemy GMXs containing 901 MESH records all use `skin_index = 0xFFFF` and only POSITION/NORMAL/UV/COLOR + index ARRY semantics; this agrees with the earlier 486-GMX finding that SIIG geometry is rigidly attached to scene nodes rather than carrying per-vertex skin weights. Proprietary inputs are not bundled.
- Under the project's versioning policy, dev7 is the last planned feature checkpoint before the mandatory minor-version review; the next substantial feature line should move to 2.10.0 rather than accumulating another long 2.9 dev suffix.

## 2.9.0-dev6

- Added **fully template-free GMX root/scene compilation** through `gltf2gmx-new`; the command does not read or require an original `.gmx` file.
- Formalized the canonical decoded GMX root as a locally synthesized 0x30-byte record: `GMX\0`, root size, total stream size, proven minXYZ/maxXYZ geometry AABB, plus explicitly unnamed `+0x08` and `+0x28..+0x2F` fields. Unknown root bytes default to zero and can be carried through advanced glTF extras without assigning speculative semantics.
- `gltf2gmx-new` enables the previously proven decoded builders together: MESH/ARRY declaration synthesis, SHAD/MTRL construction, TXIF binding, BONE/PARE scene graph creation, and MOTN/ANIM import.
- glTF export now records `gmxRootUnknown08` and `gmxRootReserved28Hex` provenance so research-derived root bytes can survive a no-template recompile.
- Added a GUI **Create new GMX** action that compiles the selected glTF without requiring the Native GMX template field.
- Added a dependency-free regression that starts from a plain glTF with no SIIG-native IDs and verifies synthesized GMX root, TXIF/SHAD/MTRL/BONE/MOTN/ANIM/MESH/ARRY graph, repaired AABB/size, texture/material/mesh/bone links, 30 Hz animation, exporter root provenance, and explicit root-byte overrides.
- Dependency-free regression suite is now **80 tests**.
- Remaining high-value GMX work is glTF skin/joint-weight import, runtime validation of fully original scenes, platform shader microcode compilation, and semantics for still-opaque/unnamed fields.

## 2.9.0-dev5

- Expanded `--sync-animation-graph` so one glTF animation can target multiple BONE nodes. The compiler now expands a multi-bone clip into synchronized per-BONE native `MOTN`/`ANIM` pairs on one shared 30 Hz timeline.
- Added glTF `CUBICSPLINE` import for translation, rotation and scale. Cubic sampling follows the glTF Hermite definition with interval-scaled tangents; quaternion results are normalized after component-wise Hermite evaluation.
- Retained byte-identical preservation for exporter-generated native tracks via `extras.gmxMotionIndex`; explicit native replacement remains single-track to avoid ambiguous identity mapping.
- Animation import reports now preserve clip provenance (`clip_name`, track index/count, interpolation set) even though no native SIIG named-clip container has been proven.
- Added a root-only two-bone regression: one CUBICSPLINE+LINEAR glTF clip becomes two 31-frame native tracks, verifies Hermite midpoint/quaternion normalization, exports to glTF, and reimports byte-identically.
- Dependency-free regression suite is now **79 tests**.
- Remaining GMX animation work is clip metadata beyond per-bone native tracks plus broader template/root independence; shader compilation and opaque chunk semantics remain unresolved.

## 2.9.0-dev4

- Added opt-in `gltf2gmx-template --sync-animation-graph`; it implies scene synchronization and can create native `MOTN`/`ANIM` matrix tracks from ordinary glTF translation/rotation/scale channels.
- New tracks are sampled at SIIG's proven 30 Hz logical-frame cadence, with LINEAR/STEP interpolation and shortest-path quaternion interpolation for rotation.
- Existing exporter-produced animations remain byte-preserved by default through `extras.gmxMotionIndex`; `extras.gmxReplaceNativeAnimation=true` explicitly opts into resampling/replacement.
- Added donor-free MOTN and ANIM builders plus structural verification of motion identities, BONE targets, key payloads and fresh glTF re-export.
- `mod-import-gltf` enables animation synthesis automatically alongside the existing schema/TXIF/TEX/BBX pipeline.
- `gmx-scene-report` now includes native motion targets, frame counts, runtime duration and raw MOTN duration.
- Added a root-only regression that synthesizes BONE + MOTN + 31-frame ANIM from glTF and proves animation-aware no-op byte identity; suite is now **78 tests**.
- Remaining animation gaps are multi-bone clips and CUBICSPLINE import; broader GMX gaps remain shader compilation, opaque chunk semantics and fully template-free root construction.

## 2.9.0-dev3

- Added donor-free native TEX layout synthesis. `png2tex` now accepts `--platform xbox360|ps3` without `--template`, while retaining the existing template-preserving path for exact no-op/edit round trips.
- Xbox synthesis uses the layout confirmed across all 54 supplied textures: tiled Xenos 8_8_8_8, endian 8-in-32, Z/Y/X/W swizzle, 32-pixel-aligned pitch, and 32-row-aligned tiled allocation. New dimensions therefore no longer require a same-size donor.
- Added structural PS3 0x80-byte linear A8R8G8B8 wrapper synthesis from the understood data-offset/payload-size/dimension fields. Runtime acceptance of newly synthesized PS3 wrapper unknown fields remains a separate validation boundary.
- `mod-import-gltf` now falls back to native TEX synthesis when a new TXIF has no texture donor, or when an existing donor is the correct platform but has incompatible dimensions.
- Upgraded the integrated regression to remove the TEX donor entirely: a 37x19 PNG becomes a new tiled Xbox TEX, is appended to BBX, and round-trips exactly through `.siigmod`.
- Added standalone 37x19 Xbox and 5x3 PS3 donor-free TEX synthesis regressions; dependency-free suite is now **77 tests**.
- Remaining high-value texture work is compressed/mipmapped native variants plus runtime validation of newly synthesized wrappers; the next GMX structural frontier is MOTN/ANIM creation/import and further root/template independence.

## 2.9.0-dev2

- Added opt-in `gltf2gmx-template --synthesize-native-schemas`; it implies texture/scene/mesh sync and removes two major donor requirements when no compatible native schema exists.
- GMX can now build decoded `MESH` and `ARRY` declarations directly from glTF `POSITION`, `NORMAL`, `TEXCOORD_0`, `COLOR_0`, and uint16 indices instead of requiring a cloned native vertex declaration.
- Added native `MTRL` parameter-stream construction. `extras.gmxParameterSchema` can describe arbitrary decoded type-0 float, type-1 matrix, and type-2 TXIF parameters; when omitted, the compiler synthesizes the standard SIIG `mWVP`/Diffuse PBR schema.
- A donor-free structural regression starts from a root-only GMX with no MESH/ARRY/MTRL/SHAD records and creates a complete SHAD→MTRL→BONE→MESH/ARRY scene from glTF, including an arbitrary `CustomScalar` material parameter and repaired root bounds.
- Mod Workspace `Import glTF + TEX` enables schema synthesis automatically as a fallback, while retaining proven native donors whenever compatible ones exist.
- GMX Workbench adds an explicit **Synthesize native vertex/material schemas** advanced checkbox.
- Dependency-free regression suite is now **76 tests**.
- Remaining major donor constraints are native TEX header/layout synthesis, MOTN/ANIM graph synthesis/import, opaque/unknown vertex semantics, platform shader compilation, and fully from-scratch GMX root/animation construction.

## 2.8.0-dev28

- Added opt-in `gltf2gmx-template --sync-texture-graph`; it implies dev27 scene synchronization and extends import into native `TXIF` texture-reference creation/binding.
- glTF export now preserves complete native TXIF index/flags/name metadata independently of whether the referenced TEX/DDS image can be located, and also annotates converted glTF images/textures when available.
- Blender-style `baseColorTexture` edits can now reuse an existing TXIF by native metadata/name or allocate a fresh native TXIF identity, then wire compatible `DiffuseSampler` type-2 MTRL parameters to it.
- Added fixed-layout TXIF synthesis/update plus post-build verification rejecting duplicate TXIF identities and dangling MTRL sampler references.
- Expanded `gmx-scene-report` to show TXIF records and MTRL→TXIF bindings.
- Added a structural regression proving byte-identical texture-sync no-op plus a new Blender-style baseColorTexture→TXIF→DiffuseSampler chain; suite is now 74 tests.
- Texture *reference* synthesis is now supported; native TEX/DDS payload creation/replacement remains a separate asset workflow. Remaining GMX boundaries include arbitrary vertex declarations, arbitrary MTRL parameter schemas, animation-graph synthesis/import, platform shader compilation, and fully template-free GMX creation.

## 2.8.0-dev27

- Added opt-in `gltf2gmx-template --sync-scene-graph`, which implies dev26 mesh synchronization and extends import into native SHAD/MTRL/BONE/PARE relationships.
- glTF material export now retains native material/shader indices and flags; bone nodes also retain native parent provenance.
- Added fixed-layout SHAD synthesis, cloned-schema MTRL synthesis/editing, fixed-layout BONE synthesis, BONE material/mesh rewiring, and PARE parent/child group extension.
- Existing BONE transforms stay byte-preserved by default; `extras.gmxImportTransform` explicitly imports glTF node transforms when desired.
- Added cross-reference verification for duplicate BONE/MTRL/SHAD identities, dangling material→shader and bone→material/mesh links, and invalid/duplicate PARE children.
- Added `gmx-scene-report`, a self-contained HTML + JSON relationship view for bone hierarchy, meshes, materials, and shaders; exposed it in the GMX Workbench.
- Added a structural regression proving byte-identical scene-sync no-op plus synthesized SHAD→MTRL→BONE→MESH/ARRY wiring, edited material color, and new PARE hierarchy linkage; suite is now 73 tests.
- Remaining GMX boundaries include TXIF creation, arbitrary vertex declarations, arbitrary MTRL parameter schemas, animation-graph synthesis/import, platform shader compilation, and fully template-free GMX creation.

## 2.8.0-dev26

- Added opt-in whole GMX mesh-graph synchronization to `gltf2gmx-template` with `--sync-mesh-graph`.
- New glTF meshes can synthesize fresh native `MESH` plus owned `ARRY` nodes by cloning a compatible proven native layout; omitted native meshes are removed only in sync mode.
- Added ARRY ownership/reference accounting so deletion removes only arrays no longer referenced by retained meshes.
- Added BONE mesh-attachment repair for deleted/replacement meshes and optional `extras.gmxAttachBoneIndex` attachment of one synthesized mesh to an existing bone.
- Added post-build graph validation for duplicate identities, dangling MESH->ARRY links, index-count mismatch, and dangling BONE->MESH links.
- Exposed graph synchronization in the GMX Workbench as an explicit advanced checkbox while keeping normal dev25 template-preserving behavior as the default.
- Added a dependency-free regression proving byte-identical graph-sync no-op, complete MESH/ARRY creation, complete deletion, fresh native identities, and BONE attachment repair; suite is now 72 tests.
- New BONE/MTRL/SHAD/PARE creation, arbitrary vertex-declaration synthesis, and from-scratch GMX construction remain future work.

## 2.8.0-dev25

- Added `gltf2gmx-template`, allowing edited glTF vertex/index counts to resize existing native GMX geometry arrays while preserving the template graph.
- Added GMX ARRY 0x10-alignment preservation/synthesis, MESH index-count repair, total-size repair, and root geometry AABB recomputation.
- Proved root +0x10..+0x27 as exact minXYZ/maxXYZ geometry bounds across all 13 retail player GMXs.
- Validated byte-identical GMX->glTF->GMX no-op import on 306/306 mesh-bearing retail GMXs; one additional corpus GMX is meshless/not applicable.
- Added a topology-changing retail `plr_001.gmx` smoke edit (328->329 vertices, 656->658 indices, 49,600->49,680 bytes).
- Added the first unified standard-library Tkinter desktop GUI with Game Rip, Mod Workspace, GMX Workbench, Utilities, asynchronous command execution, and shared logging.
- Expanded the dependency-free regression suite to 71 tests.
- Deferred audio replacement/rebuilding by project priority; GMX and GUI are the active focus.

## 2.8.0-dev24

- Added deterministic baseline-dependent `.siigmod` distribution with `mod-pack`, `mod-package-info`, and `mod-apply`.
- Added `SIIG_BINARY_PATCH_V1`: sparse equal-size byte deltas and bounded copy/data deltas for length-changing resources.
- Package application verifies archive/resource baselines, patch payload hashes, reconstructed target hashes, platform compatibility, and write conflicts without modifying the clean rip.
- Added package security limits for path traversal, duplicate/colliding ZIP members, member size, total uncompressed size, and baseline mismatch rejection.
- Added a real retail localization package validation: one `text.bin` character change produced a 1,184-byte `.siigmod` with a one-byte delta payload, reapplied exactly in a fresh workspace.
- Optimized the common opaque black/white `png2col` path to pack eight mask pixels at a time while retaining the exact threshold fallback for arbitrary grayscale/alpha edits.
- Expanded external retail no-edit native round-trip validation to 2,197 completed byte-identical checks, including 307 GMXs, 1,258 DAT scripts, 394 MAPs, all 47 stage3D tables, all 30 stagewall tables, TEX/ANM/systemfont/localization, and all 153 COL PNG/native round-trips across 78,643,200 collision pixels.
- Expanded the dependency-free regression suite to 69 tests.

## 2.8.0-dev23

- Added a project-level mod workspace: `mod-init`, `mod-list`, `mod-export`, `mod-export-archive`, `mod-stage`, `mod-stage-archive`, `mod-build`, and `mod-verify`.
- Workspaces fingerprint the original rip, track editable/native replacements separately, rebuild only affected BBX archives, and emit exact change/hash reports without modifying the source rip.
- Added deterministic Xbox `.gz` patch output at original game-relative paths; PS3 NPDRM/SDAT re-encryption remains explicitly unsupported and produces verified decompressed BBX output instead.
- Added integrated editable-resource orchestration for GMX, TEX, system font, DAT, MAP, ANM, COL, stage3D, stagewall, plus whole-archive text/message localization edits.
- Upgraded native round-trip evidence using user-supplied retail Xbox inputs: 13/13 `player.bin` GMXs, 542-string `text.bin`, and 284-group / 1295-string-per-language `message.bin` rebuild byte-identically. Proprietary inputs are not bundled.
- Expanded the dependency-free regression suite to 68 tests with a full editable-DAT -> BBX -> gzip patch workspace gate.

## 2.8.0-dev22

- Promoted stagewall/Xwall/stage-generator tables to native round-trip resources with `stagewall-build`; unchanged canonical records rebuild byte-identically and edited values survive reparsing.
- Promoted Bmap/Xmap/map4/map5 route/placement tables with `stage3d-build`; fully described `0x118` records can be synthesized deterministically, while an optional native template preserves inactive/tail bytes.
- Added `gmx-edit-export` and template-preserving `gmx-build` for fixed-count GMX arrays/indices, texture references, material parameters, bone transforms, motion durations, and matrix-animation samples without rewriting the proprietary chunk graph.
- Added dedicated localization compilers: `text-build` for the seven-payload UTF-8 `text.bin` BBX and `message-build` for six Shift-JIS Squirrel payloads, including reverse mapping from readable Unicode accents to SIIG glyph bytes.
- Expanded `asset-capabilities` from 7 to 11 native-round-trip families out of 14 known families; Xbox XACT/XMA2, PS3 SBlk/VAG, and Xenos compiled shaders remain one-way.
- Added five new native-builder regression gates; the dependency-free self-test suite now contains 67 tests.
- Kept full topology-changing/new-chunk-graph glTF/Blender→GMX synthesis explicitly outside the claimed GMX support boundary.

## 2.8.0-dev21

- Started the native asset-functionalization phase so extracted resources are classified by viewing, editing, native rebuild, replay, or archival capability.
- Added `png2tex` and `png2font` template-preserving rebuilders for Xbox 360 / PS3 TEX and the XOR-obfuscated system font.
- Added `dat-build`, `map-build`, `anm-build`, and `png2col` native compilers; `map2png` now emits lossless editable JSON.
- Added `asset-capabilities` plus automatic `validation/ASSET_CAPABILITIES.json` output in full-game rips.
- Added byte-identical native round-trip regression gates for TEX, DAT, MAP, ANM and COL, plus a capability-matrix gate (62 tests total).
- Added `docs/guides/NATIVE_ASSET_ROUNDTRIP.md` documenting the package -> BBX -> editable asset -> native rebuild -> BBX repack modding loop.

## 2.8.0-dev20

- Traced the six original iOS `moveTheMoon` / `moveTheSun` / `moveGiganticUfo` / `moveLadybug` / `moveMandala` / `moveUnknown` routines into dedicated console movers across May 9, May 11, June 10, retail Xbox, and retail PS3.
- Proved exact dispatcher-ID continuity: mobile boss types 70..75 are console cases `0x46..0x4B`.
- Added direct per-boss gameplay anchors and original-vs-V2 lineage tests; GIGANTIC UFO and UNKNOWN specifically retain the original mobile branches.
- Recovered exact six-boss constructor fingerprint percentages and addresses from the re-supplied raw Ghidra exports.
- Identified LADYBUG's substantive May9→May11 state-`0x14` global-state guard and separated it from compiler/relocation noise.
- Added two source-only dev20 tables, a research report, machine-readable validation, and a new regression check (56 total).

## 2.8.0-dev19

- Extended iOS→console lineage into direct Stage-3 boss constructor/pool ancestry and console World-4/5 enemy-handler evolution.
- Established 29/30 subordinate pool type/capacity slots unchanged across the six original bosses; THE SUN type 38 grows 36→60.
- Fingerprinted all six constructors across May 9, May 11, June 10 and retail, locating the structural refactor between May 11 and June 10.
- Added the complete `0x96..0xAB` slot lineage, deliberate `0x9F` null, and concrete GLUTTONY / ULTIMATE UFO / VERTEBRATE retunes.
- Added World-5 normal-stage integration chronology and exact cross-build `Invinf_LoadScript` addresses.
- Added four dev19 tables, the enemy-handler lineage report/validation, and expanded selftests to 55 checks.
- Kept sealed dev18 and earlier checkpoints unchanged.

## 2.8.0-dev18

- Added executable-backed iOS→console code-lineage mappings and `ios-console-lineage-info`.
- Matched mobile MAP loading, runtime scrolling/visibility, cell decoding, and 24-block generator assembly to their recovered console counterparts.
- Proved the shared 30 Hz authored-time equations on iOS and related them to the console frame-multiplier architecture.
- Corrected the effective mobile script-dispatch frontier to 0x8D and documented the console expansion through 0xCE.
- Added 18-stage opcode-structure comparison showing strong skeleton continuity with extensive parameter/content retuning.
- Added dev18 lineage tables/report/validation and expanded the selftest suite to 54 tests.
- Kept sealed dev17 and earlier checkpoints unchanged.

## 2.8.0-dev17

- Resolved `survivalStageConvertTable` gating as Evolution Tree stage-node status checks rather than a Survival-private status array.
- Proved the six Chimera Survival substitutions and their exact fallback stages, plus the purchase/clear unlock chain for Extra 31..36.
- Added `mobile-exclusives-info` with source-only Survival ending/substitution and V2 behavior/attack-pool reference data.
- Traced `dischargeEnemyShot_FPS60` and mapped original/V2 constructor pool type IDs to named retained projectile handlers, establishing concrete attack-repertoire swaps for all six V2 bosses.
- Documented explicit main-type behavior branches in THE SUN, GIGANTIC UFO, and UNKNOWN, including UNKNOWN_V2 helper doubling sites and `setVer2Destroy`.
- Proved King Fossil C-1A/C-1B boss-argument differences and the 48→96 executable-backed reload/countdown source.
- Added dev17 research tables/report/validation and expanded the dependency-free selftest suite to 53 tests.
- Kept dev16 sealed/frozen; dev17 is branched from the validated dev16 release.

## 2.8.0-dev16 — 2026-09-10

- Corrected the six iOS Level-9 resources as Chimera crossover stages and documented Android's V2-based replacement stubs separately from DELETION.
- Proved script opcodes 0x52/0x53/0x54 as KING_FOSSIL / TWILIGHT_MIRAGE / APARTHEAD from iOS ARMv7 executable dispatch.
- Added executable-backed DELETION V2 mappings, original/V2 entity-pool diffs, and the all-six-V2 `level8_stage9EX` observation.
- Reconstructed the 36-node Survival selection graph, terminal-node ending mapping, achievement indices, and six conditional stage substitutions.
- Added Chimera resource/title/boss mappings and retained crossover constructor/attack-symbol anchors.
- Credited MaxTheMurdererV2 gameplay videos as third-party observational evidence; no footage is bundled.
- Expanded the synthetic regression suite from 51 to 52 tests.

## 2.8.0-dev15 — 2026-09-10

- Added iOS/Android mobile lineage research and four mobile commands: `mobile-inventory`, `mobile-compare`, `tzip-extract`, and `mobile-map-info`.
- Added a dependency-free TZIP parser for SIIG's zlib + Apple binary-plist resource dictionaries.
- Added little-endian mobile MAP parsing while keeping console MAP parsing separate and big-endian.
- Validated 737 mobile DAT and 493 mobile MAP files with zero parse failures.
- Documented iOS/Android package provenance boundaries, 330/645 generator continuity, Level-9 replacement opcodes 0x4C..0x51, and iOS executable symbol anchors.
- Expanded the synthetic regression suite from 46 to 51 tests.

## 2.8.0-dev14 — 2026-09-10

- Audited the June/retail Ultimate UFO ending after Mframe 6200 and separated destruction, owned-object shutdown, entity removal, and part-0/state-0 reset.
- Proved that retail camera gate `+0x11C` is not cleared by the 6030 or 6200 phase actions; the clear remains conditional on a later part-0 `+0x48` reset through `0x8212DCB0` (`0x8212DD20` store).
- Excluded Normal 5-3 DAT cleanup, `DEL_ZAKO`, destructor-only manager removal, and the 25,200-unit lifetime watchdog as established ordinary route-end callers.
- Added the machine-readable final-reset audit and one regression check.
- Finalized the static-analysis boundary: no ordinary Normal 5-3 post-6200 `+0x48` caller is proven, so part-0/state-0 is documented as a conditional clear mechanism rather than an assumed ordinary-ending event.
- Added the June 10 project-owner footage boundary (~427.367–427.400 s in Normal seg6) showing the Ultimate UFO debug registration disappearing with the stage-completion white-out; retained it strictly as observational evidence.

## 2.8.0-dev13 — 2026-09-07

- Added `field-camera` for frame-by-frame procedural camera reconstruction from fld014/fld015 GMX matrices and an explicit camera preset.
- Added the executable/asset-backed GMX serialized-affine to runtime row-vector matrix conversion.
- Validated all 404 normal-5-3 late fld015 frames 5897..6300 as rear-follow for preset 4; measured 59.859..72.111 units behind the route tangent.
- Confirmed extreme dynamic horizontal-response values change lateral framing without breaking rear-follow classification in the late route.
- Decoded retail camera controller +0x11C as a timed-preset-transition acceptance gate and proved Ultimate UFO normal part-0/state-0 reset clears it on Xbox and PS3.
- Recovered May 9/May 11 phase-12 Mframe-6200 direct UltimateUfo::Vanish(part 0) behavior and documented the later 6030/6200 ending split.
- Added three machine-readable dev13 research tables and expanded self-tests to 45 checks.

## 2.8.0-dev12 — 2026-09-07

- Corrected dev11's prototype runtime-registry interpretation: May 9/May 11 ID `0xD9` is `bos_015k.gmx`; later builds use ID `0xD8` for the same model.
- Decoded the May 9 Ultimate UFO debug HUD (`Mframe`, `Sframe`, `state`, `L2:SKIP`) and named the eight phase bytes as Umb/Tow/Fan/Ring `col`/`dis` pairs.
- Proved `L2:SKIP` clears Sframe and recovered the Mframe/Sframe advance relationship.
- Added distinct normal 5-3 and DLC Bonus 5-6 Ultimate UFO profiles; proved the Bonus 5-6 immediate main-body destruction shortcut on retail Xbox and PS3.
- Closed direct Mframe -> `fld015.gmx` frame synchronization across all five executable builds.
- Reconstructed the PA animated-camera -> procedural-camera fallback and rejected preset 4 as an HP-zero-triggered switch.
- Evaluated real late `fld015` matrices with preset 4 and classified the normal late route as rear-follow geometry, with explicit remaining caveats.
- Audited all five direct PS3 camera-preset setter callers; none is Ultimate UFO, tightening preset-4 persistence while retaining an indirect-call caveat.
- Expanded the dependency-free regression suite to 43 tests.

## 2.8.0-dev11 — 2026-09-06

- Closed the special-stage reload parameter chain: retail DAT opcode `0x78` (`WARNING`) writes its first argument into transition state; values 12 and 14 select Bmap13/fld014 and Bmap15/fld015 respectively.
- Verified real retail scripts place `WARNING [12]` before Water Strider and `WARNING [14]` before Ultimate UFO, upgrading the former boss/field correlations to direct script→executable→reload evidence.
- Traced common HP-zero dispatch into Ultimate UFO's part-state/destruction lifecycle and recovered the May-prototype debug symbol `UltimateUfo::Vanish`.
- Documented executable-backed Ultimate UFO late-phase destruction actions at frames 6030 and 6200 while retaining airlock/rear-camera gameplay labels as unresolved.
- Added machine-readable special-stage reload and Ultimate UFO death-chain tables plus regression coverage.

## 2.8.0-dev9 — 2026-09-06

- Recovered executable-backed Water Strider 0..1440 looping route table and Ultimate UFO finite retail/prototype phase tables.
- Added cross-build boss function mapping, hold/resume documentation, helpers, CSV tables, and regression coverage.
- Preserved unresolved camera-angle semantics and cam02 activation as explicit limits.


## 2.8.0-dev8

- Added `pa-route-info` for executable-backed PA-route gate, camera-selection, and DAT boss-correlation inspection.
- Cross-mapped `Route::SetPaRoute` across PS3 retail, Xbox retail, June 10, May 11, and May 9 using prototype debug strings plus function/vtable shape.
- Proved retail Xbox/PS3 and June 10 require category 0 plus runtime state `+0x218 == 4` / `+0x21C == 1`; May 11 uses the state-only gate; the corresponding May 9 setup does not activate the branch.
- Added `PA_ROUTE_BUILD_GATES.csv`, `PA_ROUTE_FUNCTIONS.csv`, `PA_ROUTE_CAMERA_SELECTIONS.csv`, and `PA_ROUTE_BOSS_MAPPING.csv`.
- Proved known retail stage setup selects PA-route camera index 0 (`cam01_op1.gmx`); index 1/cam02 remains unproven as a retail activation callsite.
- Added conservative Water Strider -> fld014/Bmap13 and Ultimate UFO -> fld015/Bmap15 boss-field correlations, explicitly labeled strong correlation rather than direct callsite proof.
- Real retail PS3 validation scans all 76 DAT files and identifies six Water Strider/Ultimate UFO occurrences with zero parse failures.
- Expanded the dependency-free regression suite to 35 tests.

## 2.8.0-dev7

- Corrected channel-type-12 GMX matrix-animation timing from raw authoring timestamps to the retail logical-frame sampler: `matrices[logical_frame % frame_count]` at the engine's 30 Hz logical clock.
- `gmxtrack` now separates `runtime_seconds_30hz` from `raw_authoring_time`; glTF animation keys use sample-index/30 while preserving the raw float table in metadata.
- Decoded the 0x1C route/field animation descriptor as `{name[16], start_frame, end_frame, loop_flag}`.
- Added `camera-animation` for the explicit retail `cam1`/`int1` 0..199 non-loop camera controller, including `FieldPos` translation and frame-multiplier update cadence.
- Added `field-animation` for explicit `fld014`/`fld015` descriptor-frame matrix evaluation without inferring stage activation.
- Proved `fld015` is 0..6300 non-loop (6,301 samples) and `fld014` is 0..1440 loop with frame 1440 wrapping to sample 0 (1,440 samples).
- Proved both `cam01_op1` and `cam02_op1` use the same camera descriptor end 200; this path never reaches cam02 samples 200..299.
- Expanded the dependency-free regression suite to 34 tests.
- Real retail validation covers all four camera/field GMXs and corrected glTF runtime spans.

## 2.8.0-dev6

- Added executable-backed procedural route orientation state to `RouteRuntimeState`, preserving Hermite-sample update ordering before same-update next-segment preparation.
- Reconstructed row-vector route orientation as `Rz(roll+offsetZ) × Rx(pitch+offsetX) × Ry(yaw+offsetY)` with retail pitch/yaw updates from moving Hermite samples.
- Added `camera_world_state()` for the proven procedural camera path: route/stage-frame eye-offset transform, FieldPos target, and transformed word-8/9/10 dynamic local-X response.
- Added `route-camera-playback`, explicitly combining caller-supplied route/DAT/preset/runtime-coordinate inputs without inferring activation timelines.
- Added `--emit-every` output decimation to combined playback; every runtime update is still simulated.
- Expanded route-playback CSV state with procedural pitch/yaw/roll and row-vector orientation matrix columns.
- Expanded the dependency-free regression suite to 31 tests.
- Real-corpus orientation stress at 100-unit analysis spacing: six route files exercise Hermite orientation for 356 total orientation updates.
- Explicit `Xmap3_1.bin + level3_stage1.dat` combined-camera validation simulates 265,020 runtime updates, applies seven SCROLL_02 events, and terminates normally; preset 0 / runtime (213,233) are validation inputs, not inferred gameplay activation.

## 2.8.0-dev5

- Added `camera-preset` for semantic inspection of retail camera presets and optional runtime-coordinate response evaluation.
- Proved preset word 0 is perspective FOV in degrees and word 1 is uniform scene/view scale.
- Proved words 2–4 form the camera-eye offset transformed by the active route/stage orientation and added to `FieldPos`; words 5–7 are scene/view translation.
- Resolved words 8–10 as dynamic horizontal-response gain, target local-X scale, and eye local-X scale in retail PS3 `0x00157540`.
- Proved words 12–29 are three fog profiles `{start, end, RGBA}` through renderer `fogRange` and `vFogColor` consumers.
- Traced word 11 as a shared scalar forwarded unchanged to `collada_edge1`, `collada_face1`, and `collada_face2`; its exact virtual-setter semantic remains unresolved.
- Added `CAMERA_PRESETS_RUNTIME_SEMANTIC.csv` and upgraded `CAMERA_PRESET_SCHEMA.csv` with evidence-backed names while preserving the untouched raw table.
- Expanded the dependency-free regression suite to 29 tests.

## 2.8.0-dev4

- Added executable-backed dynamic route runtime state (`RouteRuntimeState`) with non-loop termination, modulo loop wrapping, and per-update source/sample progression.
- Added exact signed SCROLL_02 Y-to-spacing conversion from PS3 retail `0x0014E408`, including PPC truncation-toward-zero behavior.
- Reproduced the retail linear mid-segment spacing-change path: remaining linear samples are discarded and rebuilt from current `FieldPos`; active Hermite segments intentionally do not rebuild on spacing changes.
- Added `route-playback`, explicitly coupling one caller-supplied stage3d route and DAT script through authored-frame → runtime-update SCROLL_02 timing.
- Added explicit `--start-frame`, `--end-frame`, `--frame-multiplier`, `--loop`, and `--max-updates` controls rather than guessing route-object activation or filename pairing.
- Expanded the dependency-free regression suite to 28 tests.
- Real-corpus runtime stress gate: all 46 resampleable retail route tables survive non-loop spacing-change and loop-wrap smoke stepping; the one route-empty file remains skipped.
- Explicit filename-correspondence examples `Xmap2_1 + level2_stage1.dat` and `Xmap3_1 + level3_stage1.dat` validate DAT-coupled playback, including seven live spacing rebuilds in the latter. These examples are validation candidates, not a claim that every route↔DAT pairing is solved.

## 2.8.0-dev3

- Added executable-backed fixed-spacing non-loop route resampling (`route-resample`).
- Reproduced linear write-after-step sampling, straight/curve classification, six-state tangent-axis transitions, cubic Hermite sampling, and the final look-ahead source-point rule.
- Added runtime-initialized camera presets reconstructed from all 160 initializer writes, while retaining the untouched raw 32 × 30 table.
- Added a 30-word structural camera-preset schema documenting vec3/group layouts, interpolation behavior, consumer addresses, confidence, and unresolved semantics.
- Real-corpus route validation at a deterministic 100-unit analysis spacing: 46 resampleable files, one route-empty file skipped, 19,471 segments, 155,690 samples, 62 Hermite segments, zero conversion failures.
- Expanded the built-in regression suite to 26 tests.
- Dynamic SCROLL_02 spacing changes and looping-route wrap behavior remain explicitly outside the fixed-spacing exporter.

## 2.8.0-dev2

- Added five-build executable-derived runtime entity/primitive registry tables and decoded 0x2C record fields.
- Resolved render-group selectors to Offset Opacity / Offset Translucent / Offset Terminate / Non Opacity.
- `stage3dmap` now exports executable-ordered runtime route-source control points plus record-0 origin fallback.
- Added `gmxtrack` for decomposed GMX matrix-animation CSV and translation trajectory OBJ export.
- Added raw 32 × 30 camera-preset table and two route-animation descriptors from PS3 retail.
- Expanded the dependency-free self-test suite to 24 checks.


## 2.8.0-dev1

- Validated the supplied original retail Xbox 360 LIVE STFS and PS3 type-1 PKG directly.
- Added optional OpenSSL AES-CTR acceleration for finalized PKG extraction with Python fallback/equivalence testing.
- Added internal authenticated decryption of SIIG's six NPDRM SDATs and standalone `sdat-decrypt`.
- Added built-in Sony 989SND/SCREAM SBlk v3 parsing plus PS-ADPCM WAV export and standalone `sblk2wav`; 84/84 retail PS3 streams decode.
- Restored Stage Explorer v5 runtime SCROLL_01/02/03 playback with 30 Hz controls and source-level regeneration.
- Added content-addressed outer-container staging for `--resume` and `--no-outer-cache` override.
- Fixed the STFS `CON` first-hash-table initialization path.
- Integrated PS3 EBOOT-backed Bmap/Xmap placement, route-point, scroll, and timing corrections.
- Expanded `selftest` to 23 dependency-free cases, including cross-platform Stage Explorer root detection.
- Added explicit retained-native placeholders for WMA/XMA/AT3 and XACT data so Asset Viewer coverage reports do not mislabel intentionally non-browser-native files as missing previews.
- Fixed Stage Explorer discovery for the PS3 `USRDIR/script` and `USRDIR/map` layout.
- Updated credits/provenance for OpenSSL acceleration and vgmstream Sony bank/PS-ADPCM cross-checks.

## 2.5.1

- Reorganized the release root into `docs/`, `reference/`, `validation/`, `tools/`, and `addons/`.
- Added a central documentation index and folder-level README files.
- Updated runtime resource lookups and all documentation references to the new paths.
- Retained fallbacks for legacy root-level data-table locations.
- Reduced root-level files from 75 to 18 with no content removed.

## 2.5.0

- Replaced the monolithic Asset Viewer with a linked-data layout: compact HTML, external inventory, thumbnails, and deferred preview shards.
- Removed base64 media embedding and added pagination plus intersection-based lazy loading.
- Added direct GMX/OBJ wireframes, TEX previews, MAP/DAT/ANM thumbnails, WAV waveforms, and explicit empty/animation-only placeholders.
- Added matching converted-asset previews for source TEX, GMX, OBJ, and audio files.
- Fixed related glTF payload keys and excluded viewer output during in-tree rebuilds.
- Added detailed viewer size/coverage reporting and validation of all generated relative references.
- Validated 1,016/1,016 previewable thumbnails and reduced the tested HTML document by 99.934%.

## 2.4.0

- Corrected standalone ANM parsing to 16-byte names, start/end frames, and loop flags; added group/clip indexes.
- Added `stage3dmap` for Bmap/Xmap/map4/map5 0x118-byte 3D path and placement records.
- Added `stagewall` for wall/Xwall repeat strips and `stage_generate.bin` enabled candidates.
- Added `shader-info` for Xenos shader stages, bounded microcode, metadata strings, and hashes.
- Added automatic full-rip structured exports and `scan` recognition for these formats.
- Corrected SCROLL_01/02 to 8.8 fixed-point values and documented SCROLL_03 as a June 10 no-op.
- Expanded the built-in regression suite from 11 to 15 tests.
- Added Ghidra-backed stage/ANM/shader notes and a real-corpus validation report.

## 2.3.0

- Added `repack-bbx` with canonical archive layout, named/unnamed resources, seeded hashes, sorted indexes, preserved reserved bytes, deterministic gzip, atomic output, and mandatory post-build verification.
- Extended extraction manifests with payload SHA-256, original archive SHA-256/size, reserved header bytes, alignment, and sorted-index metadata.
- Verified the unchanged supplied retail `map.bin` as a byte-for-byte extract/repack round trip.
- Added the SIIG Blender Add-on 0.1.0 for single, multi-file, and recursive-folder GMX import through the toolkit's existing glTF exporter.
- Added `asset-viewer`, a searchable offline HTML inventory with bounded media previews, text inspection, glTF summaries, and interactive wireframe views.
- Added `serve`, bound to localhost, for viewing generated HTML without `file://` restrictions.
- `rip-game` now generates an asset viewer automatically unless disabled.
- Added drag-and-drop launchers for BBX extraction/repacking, viewer generation, and local serving.
- Expanded `selftest` from 9 to 11 checks with BBX repacker and HTML viewer tests.
- Added dedicated repacker, asset viewer, Blender add-on, and excluded-source documentation.

## 2.2.0

- Integrated the verified MAP atlas renderer into the main toolkit. Resource IDs 6, 7, 8, and 9 resolve to `fence1_512`, `fence2_512`, `fence6_512a`, and `fence3_512`; tile IDs 1–49 use the confirmed 7×7 atlas layout and X/Y reflections.
- Upgraded `stageviz` to explorer format v4 with embedded game atlases, zero-scroll layer composites, cell inspection, safe HTML escaping, and categorical fallback when an atlas is absent.
- Added optional atlas-backed output to `map2png` through `--atlas`, `--atlas-step`, and `--no-atlas-composite`.
- `rip-game` now generates the offline stage explorer automatically unless `--no-stageviz` is used.
- Added deterministic `OUTPUT_MANIFEST.json` and `.sha256` files plus `verify-output` for privacy, size, hash, partial-file, and report validation.
- Added `doctor`, global `--version`, and a built-in `selftest` covering AES, BBX, DAT, MAP, bounded gzip, PNG/atlas rendering, ZIP safety, privacy redaction, and output tamper detection.
- Hardened ZIP, STFS, and PKG extraction with configurable file-count/size limits, duplicate-path checks, traversal and symlink rejection, and atomic `.siig-part` writes.
- Added bounded gzip expansion, nested-BBX depth/resource budgets, Windows-reserved-name handling, case-insensitive output collision avoidance, and stricter platform ambiguity detection.
- Resume profiles now include the toolkit version so changed converter behavior cannot silently reuse stale output.
- Restored and updated the credits, AI disclosure, provenance, source audit, third-party notices, project-license status, and attribution policy in the package.
- Added security and testing documentation and expanded full-rip reports with elapsed time, explorer status, extraction limits, and manifest status.

## 2.1

- Added direct Xbox 360 STFS input to `rip-game` for `CON `, `LIVE`, and `PIRS` packages.
- Added direct PlayStation 3 PKG input for finalized and non-finalized/debug type-1 packages.
- Added dependency-free STFS block-chain/hash-table extraction and PS3 PKG AES/debug-stream decryption.
- Added `unpack-container` for outer-package-only extraction and `container-selftest` for the AES known-answer test.
- Added magic-based input detection; package filenames no longer need a particular extension.
- Added outer-container totals and input type to full-game validation reports.
- Preserved the separate PS3 NPDRM SDAT step: TrueAncestor `.bin.gz.dat` files are still discovered beside the PKG or through `--ps3-sdat-dir`.
- Validated synthetic STFS level-0/1/2 boundaries, chained files, finalized/debug PKGs, and both supplied extracted retail releases.
- Added `docs/guides/CONTAINER_INPUT_NOTES.md` and updated the drag-and-drop launcher.


## 2.0

- Corrected the MAP interpretation using the June 10 XEX renderer path.
- Confirmed `0` as empty, tile IDs `1..49`, `0x40` as X flip, and `0x80` as Y flip.
- Confirmed a 30-unit tile grid and three independently scrolling layers.
- Added runtime tile-set resource IDs for all 75 stage-table entries.
- Updated the offline explorer with verified tile and flip views.
- Documented generator MAPs as reusable 2D tile-pattern blocks.
- Removed the unsupported assumption that these MAP cells place 3D wall models.
- Kept exact tile-set filenames and layer gameplay roles explicitly unresolved.

## 1.9

- Added conservative XEX-backed DAT semantic decoding with categories, summaries, confidence levels and proven field names.
- Added `stageviz`, a self-contained offline MAP/DAT explorer with searchable frame timelines and three MAP bit views.
- Reconstructed the 75 stage/script pairings, two MAP-only slots and trial variant from the June 10 executable tables.
- Added explicit reporting for 12 expected-but-absent level-4/5 MAP names and 14 package MAPs unreferenced by the runtime table.
- Added `reference/tables/STAGE_PAIRING.csv`, `reference/tables/DAT_SEMANTIC_SCHEMAS.csv` and `docs/guides/STAGE_EXPLORER_NOTES.md`.
- Validated semantic export on all 1,334 June 10 DAT files with zero failures; the explorer contains 17,335 commands from all 76 stage scripts and no absolute source paths.


## 1.8

- Confirmed the shared DAT format from the June 10 DebugOpt `stageScriptBlockLoad` routine.
- Added `dat2csv`, delta-to-absolute frame conversion, full signed/hex argument preservation, and the executable-derived 207-slot opcode-name table.
- Confirmed the MAP layer format from `stageGenerate2DMap`.
- Added `map2png` with categorical/grayscale palettes, optional nearest-neighbor scaling, numeric CSV grids, and JSON metadata.
- Added DAT/MAP recognition to `scan`.
- `rip-game` now converts all extracted DAT and MAP resources automatically.
- Validated 5,244 DAT files containing 96,750 commands and 1,576 MAP files containing 4,728 layers across May 9, May 11, June 10 and retail Xbox 360 builds with zero parse failures.

## 1.7

- Added `.col` collision-mask decoding to PNG.
- Added standalone `.anm` table decoding to CSV and JSON.
- `rip-game` now converts COL and ANM resources automatically.
- Added prototype-analysis notes based on the May 9, May 11 and June 10 Xbox 360 builds.

## 1.6.0

- Added `rip-game` for original Xbox 360/PS3 directories and ZIP archives.
- Added automatic platform detection from `default.xex` and `EBOOT.BIN`.
- Added PS3 RSX TEX to PNG support and PS3 system-font atlas decoding.
- Added TrueAncestor `.bin.gz.dat` discovery for NPDRM/SDAT payloads.
- Added deterministic archive ancestry, decompressed BBX preservation, resume-state hashes, ready-file copying, and privacy-safe validation reports.
- Added drag-and-drop `SIIG_Rip_Game.bat`.
- Xbox 360 WMA files are preserved unchanged; PS3 Sony SBlk audio banks are extracted losslessly as `.bnk` for vgmstream.

## 1.5.1

- Removed absolute input, output, FFmpeg, and glTF filesystem routes from generated JSON metadata.
- JSON manifests now retain only privacy-safe filenames and archive-relative paths.
- Added `sanitize-json` to clean metadata generated by v1.5 or earlier in place.
- Sanitized the bundled glTF samples.

## 1.5

- Added `gmx2gltf` and `extract --convert-gltf`.
- Decoded GMX `TXIF`, `SHAD`, `MTRL`, `PARE`, `BONE`, `MOTN`, and `ANIM` chunk relationships.
- Added glTF 2.0 hierarchy, rigid mesh attachment, materials, vertex colors, texture assignment, and transform-animation export.
- Added automatic conversion of the shared uncompressed `ptn_001.dds` texture to PNG.
- Added `docs/formats/GMX_GLTF_NOTES.md` and detailed GMX output in `scan`.
- Validated 486 GMX files, 1,938 meshes, 3,298 nodes, 776 materials, and 913 animation tracks with zero conversion failures.

## 1.4

- Added `text2csv` for direct decoding of `text.bin`, `message.bin`, or a directory containing both.
- Recovered the 542-row `text.bin` key/translation table across Japanese, English, French, Italian, German and Spanish.
- Parsed all 284 Squirrel-style `message.bin` arrays and 1,295 strings per language.
- Added Unicode correction for the legacy language-specific accented-glyph codes while retaining untouched raw scripts.
- Added combined CSV/JSON, per-language text files, metadata, and `docs/formats/LOCALIZATION_NOTES.md`.

## 1.3

- Added `xact2wav` for direct conversion from `sound.bin`, extracted XWB files, or XWB/XSB directories.
- Added standard big-endian XACT3 wave-bank parsing and XSB cue-name recovery.
- Added RIFF XMA2 wrapper generation and optional FFmpeg PCM WAV decoding.
- Validated all 86 SIIG streams: 83 SE cues plus BGM007, BGM008_MIX_C and BGM_XACT_SE33.
- Added per-bank CSV/JSON manifests with channels, sample rates, sample counts and loop metadata.

## 1.2

- Added `font2png` for `systemfont.bin`, `.gz`, or extracted `systemfont.crp`.
- Confirmed from `default.xex` that `systemfont.crp` is XOR-obfuscated bytewise with key `0xF1`.
- Added automatic CRP conversion when `extract --convert-tex` is used.
- Added `reference/systemfont/systemfont_glyphs.csv` with all 6,732 executable-resident glyph records, atlas coordinates, widths, left insets and known aliases.
- Added `reference/systemfont/systemfont.fnt` AngelCode BMFont descriptor for the 6,730 native Unicode mappings.
- Added CRP detection to `scan`.

## 1.1

- Fixed TEX untile addressing.
- Added the missing Y[3] XOR in the Xenos pipe selector.
- Eliminated repeating 8-row jitter/scrambling in converted PNG files.
- Revalidated all 54 supplied TEX files with zero conversion failures.

## 1.0

- Initial BBX extraction, GMX-to-OBJ and TEX-to-PNG release.
