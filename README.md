# Space Invaders Infinity Gene Asset Toolkit

**Current development checkpoint: `v2.10.0-dev25` — unsealed development checkpoint.** The latest sealed release remains `v2.10.0-dev23` and is immutable. This branch is a public-review staging branch; the default `main` branch has not been updated by this staging work.

The development notes below preserve historical checkpoint records from the dev24 work. Their WIP labels describe those historical checkpoints, not the current package version.

### WIP199 — exact Xbox replacement wrappers + single deployment tree

Project-owner testing exposed that `message.bin.gz.sdat` could be rebuilt only as a decompressed `message.bin`, while raw `sound.bin` was duplicated across multiple build folders. The root cause was twofold: the Mod Workspace incorrectly treated every `.sdat` suffix as PS3 NPDRM, even though SIIG's Xbox `.bin.gz.sdat` files are ordinary gzip streams; and the Xbox build retained legacy intermediate mirrors that were unnecessary for deployment. WIP199 emits Xbox package replacements exactly once under `build/xbox360_replacements/`, preserving raw `sound.bin` as raw BBX and gzip-wrapping `.bin.gz` / `.bin.gz.sdat` archives at their original package-relative filenames. Existing workspaces can repair known Xbox retail wrapper paths that older Update Rip passes collapsed to `.bin`, and future asset refreshes preserve the original manifest source label.

### WIP197 — stable desktop layout, faster Visualizer rebuilds, TSV localization, generic Xbox deployment

Project-owner testing after WIP196 exposed four usability problems. GUI **0.55.0-dev24** gives the global and Utilities-local **What does this do?** surfaces fixed geometry so hover text cannot resize/shake the notebook, and the GMX Workbench explicitly recomputes its canvas scrollregion and returns to the top when Advanced mode is switched back to Simple.

Visualizer dataset **v24** keeps WIP195's direct target-pixel Position mapping and now backs it with June 10 executable code: `Function_82177DF0` feeds X/640 and Y/360 to the 1280×720 renderer. The simulator adds a non-rendering native-anchor/source-bounds overlay for hardware comparison instead of guessing another global multiplier. Stage BGM playback keeps the recovered adaptive VOL SCALE behavior, but delayed browser frames now sample a distinct playback-time meter quantum for each 60 Hz catch-up step instead of repeating one audio sample across several steps. Rebuilds reuse a content/stat-bound `BGM_PREVIEW_CACHE.json`, including the expensive 256-sample peak envelope, so unchanged game BGM no longer has to be decoded by FFmpeg again. A stale resume check that still expected an old Visualizer dataset was also removed.

For localization, `text_strings.tsv` / `text_strings_raw.tsv` are now the recommended editable `text.bin` sheets. Tabs avoid the locale-dependent comma parsing that can make CSV appear as one giant first column; legacy CSV and JSON exports remain for compatibility/research. Mod Workspace now uses the editor-neutral `build/xbox360_replacements/` + `XBOX360_REPLACEMENTS.json` naming and describes Velocity, Horizon and Le Fluffie only as examples of compatible external Xbox package editors.

### WIP196 — Blender editing defaults + Xbox replacement Mod Workspace

Blender add-on **0.4.0** makes normal editing imports solid-first: raw GMX defaults to the native solid pass, assembled `_E` outline objects are hidden non-destructively after import, and the optional white-outline/scanline Style Preview no longer auto-applies unless the user opts in. The compositor helper now supports Blender 5's `Scene.compositing_node_group` / Group Output model while retaining the Blender 3.6/4.x `Scene.node_tree` path.

WIP196 first promoted complete Xbox replacement containers as the beginner-facing output. WIP197 keeps that deployment model but supersedes WIP196's Velocity-specific folder/label names with the editor-neutral `build/xbox360_replacements/` + `XBOX360_REPLACEMENTS.json` contract. `.siigmod` remains an optional baseline-dependent sharing delta, not a file to inject into STFS. The desktop GUI reports pack failures visibly and confirms the exact `.siigmod` save path when sharing succeeds.


### WIP195 — Visualizer position regression + always-visible GUI help

Project-owner testing exposed two regressions. First, many authored Visualizers became screen-filling gradients after WIP191. Retail stage 4-5 `SEQUENCE_12 / PARAM_7` provides the decisive geometry check: its free Y=+360, 1× 128×128 `WhiteCircle2` source is completely above the feedback target under the WIP191 1.5× multiplier, so it cannot seed the structured recurrence seen on real hardware. Dataset **v23** therefore restores direct target-pixel Position mapping (`target_x=640+X`, `target_y=360-Y`) while retaining the WIP191 viewport UI/fullscreen controls and display-only smooth resolve.

Second, the global **What does this do?** area could be packed below the usable Mod Workspace viewport. WIP195 makes contextual help an always-visible wrapped strip above the main tabs and moves the general task log into a separate **Task log…** window. This avoids trading help visibility for Game Rip console height. GUI **0.53.0-dev24** was live-smoked at 1120×780 and 1744×868.



### WIP193 — compact Game Rip / GMX Workbench layout

Game Rip now protects a readable rip/update console instead of letting newly added option panels squeeze it to a single line. The drag/drop target, source-package cache, live progress and action rows are vertically compact, the long footer explanation moved out of the data-dense path, and the console row has a 150-pixel layout floor plus normal expansion weight. GMX Workbench Simple mode is also substantially denser: export/rebuild/inspect/open-folder actions share one row, model/output assembly folders are shared once, **Bosses** and **Enemies / sub-bosses** occupy nested tabs instead of stacked panels, and CENTIPEDE-only segment overrides appear only when CENTIPEDE is selected. Advanced import checkboxes use two columns to reduce vertical travel without hiding any option.

### WIP192 — visible source-package cache controls and guarded clearing

The Game Rip tab now makes the persistent `.SIIG_Ripped.siig_outer_cache` sidecar explicit instead of leaving it as unexplained hidden-looking output. **Keep source-package cache for faster resume/update** is a remembered GUI preference; disabling it forwards the existing `--no-outer-cache` behavior. The tab reports whether the cache exists and its current disk usage, with **Refresh info** for manual rescans. **Clear cache…** always opens a warning that states the rip and Mod Workspaces are not deleted, while also warning that a later resume/full rip may need to unpack the original ZIP/STFS/PKG again and therefore take longer. The cache remains outside the rip manifest/viewer tree and contains no unique mod edits.

### WIP191 — Visualizer viewport UI, off-screen centers and smooth display resolve

Visualizer dataset **v22** replaces the old long scrolling simulator layout with a viewport-first June 10-inspired **VISUALIZER CHECK MODE** overlay. Stage/boss authored events are permanently reachable from the top bar, apply immediately, and reset feedback; the rest of the controls are grouped into **PRESETS / CHECK MODE / ADVANCED** tabs while the live canvas stays visible. Fullscreen (`F`) and menu hide/show (`M`) are built in.

WIP191 historically introduced a **1.5× logical-to-target Position scale** while preserving the recovered axes/fixed-position table. **WIP195 supersedes that scale inference** after stage 4-5 proved it can move the complete authored source off-target; current builds use direct target-pixel Position mapping. WIP191's viewport UI and **display-only 640×360 smooth resolve** remain retained, and the recursive feedback sampler remains executable-backed point filtering. See `reference/research/VISUALIZER_UI_RUNTIME_OVERHAUL_DEV24.md` plus `reference/research/VISUALIZER_POSITION_GRADIENT_REGRESSION_DEV24_WIP195.md`.

### WIP183 — Visualizer polished proof of concept

Project-owner testing of WIP182 confirmed that the browser Visualizer remained useful but visibly too blocky/dark and could produce silent generated BGM playback. Dataset **v21** now labels the simulator explicitly as a **proof of concept** and improves only the browser-side presentation/audio bridge: the recovered recursive point-filtered feedback math is unchanged, while the final display uses a brighter base plus a separate soft screen/bloom layer. Raw recovered RGB remains available at softness `0`, intensity `1`, bloom `0`.

Generated Xbox WMA / PS3 AT3 previews are no longer routed through `MediaElementAudioSourceNode`. FFmpeg creates both the browser-safe audible preview and a compact stereo peak envelope at the recovered **256-sample / 48 kHz** XAudio2 quantum. The native `<audio>` element stays directly audible and the Visualizer meter follows the precomputed envelope by playback time. User-loaded browser audio is decoded only to build an equivalent envelope; it is not inserted into the playback graph. Exact Xenos final-composite behavior and meter-query phase remain explicit boundaries. See `reference/research/VISUALIZER_POC_POLISH_DEV24.md`.

### WIP182 — effect-model bomb lifecycle

The living `est_*` audit now has five confirmed usages: `est_012` shared JOLYNE/UNKNOWN target cube, `est_013` PROGRESSIVE UFO missiles, `est_015` WATER STRIDER trail spikes, `est_020` shared OCTOPUS/GLUTTONY live bomb, and `est_021` its explosion/detonation model. Six other `est_*` rows remain speculative or unidentified.

## WIP165 highlight — one-click retail Rip + verify workflow

WIP165 turns the existing extraction/research toolchain into a practical first-run workflow without pretending every remaining research boundary is solved. Desktop GUI **0.42.0-dev24** now centers Game Rip on **Check input → Rip + verify → Open Asset Viewer**. Working folders/options persist in per-user local settings outside rip/project outputs, a successful rip is handed directly to Mod Workspace, and the viewer can open automatically after the built-in completion gate passes.

Resume is substantially hardened: outer ZIP/STFS/PKG and nested-package staging is content-addressed; unchanged ordinary archives fast-skip before decompression; PS3 SDAT plaintext caches are accepted only when both encrypted-source and plaintext SHA-256 bindings match; Stage Explorer/Visualizer/Asset Viewer can be reused on a safe unchanged-package resume; and Asset Viewer preserves already-valid generated thumbnails. Output-manifest and explicit verification hashing now use a bounded deterministic thread pool, while `verify-rip` is an alias for the existing full-byte `verify-output` integrity check.

Canonical retail validation passed on both platforms. Xbox 360 produced **2,593 resources / 1,351 PNG / 486 glTF / 86 WAV**, a 9,407-file Asset Viewer with **8,669/8,669 previewable thumbnails**, and a **16,567/16,567** full SHA-256 re-hash. PS3 produced **2,593 resources / 1,285 PNG / 486 glTF / 84 WAV**, internally authenticated/decrypted all **6 SDATs / 18 blocks** with no fallback, a 9,340-file Asset Viewer with **8,626/8,626 previewable thumbnails**, and a **16,422/16,422** full re-hash. Both had zero integrity/privacy issues. Proprietary retail packages and generated retail rips are validation inputs only and are not bundled.

Start with [`docs/guides/QUICK_START.md`](docs/guides/QUICK_START.md). Detailed evidence is in `reference/research/USABLE_PREVIEW_WIP165.md` and `validation/USABLE_PREVIEW_RETAIL_2.10.0-dev24.json`.


- THE SUN controller timing closure: GUI 0.41.0-dev24 adds the exact synchronized opening-state preset (`body frame 0 + 48 B3 protection barriers`) and the `the-sun-controller` sampler. Retail and June 10 both prove body interpolation belongs to states 9/10/11, so native sample 40 is no longer conflated with the opening barrier ramp.
- MANDALA Workbench fidelity: `mandala_all_members_phase0` now exposes all 72 allocated members, including the 32 `bos_005f.gmx` center circles in executable-exact phase-0 geometry. The BC circles remain explicitly marked as state-8-activated, so the complete inspection preset does not falsely claim simultaneous gameplay activity. GUI 0.40.0-dev24 makes this the default complete MANDALA assembly while retaining the separate state-7/state-8 presets.
### Visualizer real-hardware BGM response (dev24 WIP167)

Real Xbox 360 footage of the June 10 build's stages 4-2, 4-4 and 4-5 exposed the normal gameplay `VOL / MIN / MAX / VOL SCALE / AVE RAW / AVE SCALE` debug state while BGM response was functioning. Executable tracing now separates two paths: dedicated Visualizer Check Mode consumes the raw stereo XAudio2 peak mean directly, while normal stage playback uses an adaptive normalized `VOL SCALE`. The constructor default adaptive window is 300 frames, but `VL_VOLUME_SCALE`/opcode `0xCE` reconfigures it; all three reference stages author **180 frames**. The exact mapping is `(VOL-MIN)/max(abs(MAX-MIN),0.001)` inside the range, clamped to 0/1 outside it. RAW and SCALE diagnostics use 180-frame histories.

Visualizer dataset v13 implements both response models, automatically uses the authored stage window when a decoded timeline is selected, and exposes hardware-style diagnostics for direct footage comparison. WIP174 later resolves the Xbox 360 processing window itself to 256 samples / 5 1/3 ms at 48 kHz; only browser/native snapshot phase remains bounded. The recovered game-side post-meter normalizer is not approximate. See `reference/research/VISUALIZER_GAMEPLAY_BGM_NORMALIZER_DEV24.md`.

### Visualizer presentation/audio bridge (dev24 WIP166)

The offline Visualizer Simulator now defaults to a subtle **0.65 px display-only softness** pass, adjustable from 0 to 2 px. This deliberately leaves the recovered point-filtered SHAPE and recursive-feedback samplers unchanged. When generated from a console rip, it also discovers Xbox 360 WMA and PS3 AT3/ATRAC3+ BGM and, when FFmpeg is available, creates cached browser-safe local previews for direct playback/metering. Native game audio is never modified.

### Visualizer BGM peak-meter fidelity (dev24 WIP146)
### Real Visualizer SHAPE input (dev24 WIP147)
### Camera preset word 11 resolved (dev24 WIP148)

- Closed the long-standing `shared_model_material_scalar_unresolved` field: retail preset word 11 is **`face_bias`**.
- Xbox raw PPC proves material virtual `+0x18` stores the scalar at wrapper `+0x60`; the renderer uploads it for `collada_face1`, and embedded vertex shader `0x8208D408` names c9 `faceBias` and offsets vertices by `-Normal * faceBias.x`.
- Renamed the semantic camera table/API field to `face_bias`, added a dedicated validation report/research note, and regression-checked all 32 retail presets at the authored value `0.2`.


- Retail validation confirms all ten `visualizer.bin` SHAPE textures convert to exact 128×128 PNGs in the recovered resource order.
- Visualizer Simulator dataset v6 now discovers those PNGs from a user-supplied full rip and embeds them only in the locally generated HTML; no proprietary pixels are bundled in the toolkit.
- The browser preserves each real texture's RGBA and applies the recovered `ScreenSpritePS` equation (`sampled_shape.rgba × runtime_tint.rgba`) before source-over compositing with the exact SrcAlpha/OneMinusSrcAlpha source-pass blend. The prior luminance×alpha mask bridge is retired.
- Procedural shapes remain the source-only fallback when a rip does not contain the real Visualizer PNGs.


- Resolved the former host-audio approximation: June 10 executable tracing proves VolumeSet/BGM is the arithmetic mean of two XAudio2 per-channel **peak** levels, consumed directly as a linear 0..1 float.
- Replaced the browser's RMS/−60..0 dBFS remap with left/right time-domain peak sampling and stereo averaging; mono falls back to its single channel.
- WIP174 later resolves the native Xbox 360 window to 256 samples / 5 1/3 ms at 48 kHz. Browser snapshot phase relative to native processing-pass boundaries remains explicitly bounded.
- Added `VISUALIZER_BGM_METER_DEV24.md`, machine-readable validation, and an explicit Microsoft Learn API-documentation provenance row.


**Current development line: 2.10.0-dev24. Historical release highlights follow below.**

## Dev24 WIP177 highlight — Visualizer Check Mode feature sweep

Ten trimmed project-owner June 10 Xbox 360 captures isolate the Check Mode controls instead of relying on complex stage footage. Dataset **v20** keeps the recovered renderer math intact and clarifies what each similarly named control actually targets: **Scale X/Y** scales the newly injected SHAPE stamp, while **Magnify Scale X/Y** transforms the previous feedback surface; both use the recovered `min + (max-min) × VolumeSet` interpolation. SHAPE RGBA uses the same endpoint model for source tint. Position Free is visibly marked inactive when a nonzero Position Fix selects a fixed anchor, and Rotation Base/Add are visibly marked inactive when nonzero Fix Rotation overrides the accumulated rotation path.

The hardware BG sweep confirms BG R/G/B/A are direct single clear controls rather than VolumeSet ranges. RGB is reproduced directly. BG:A remains exposed but deliberately does **not** trigger speculative browser-alpha feedback: exact Xenos render-target alpha storage/final-composite equivalence remains an explicit research boundary. The live status line now reports effective source scale and SHAPE tint for direct comparison against Check Mode footage. See `reference/research/VISUALIZER_CHECK_FEATURE_SWEEP_DEV24.md`.

## Dev24 WIP176 highlight — Visualizer native min/max range contract

Eight new project-owner Xbox 360 Visualizer Check recordings provide a hardware-side failure case that the simulator previously did not model: while testing Magnify A, the June 10 build entered its own assertion screen at `VisualizerMain::SetMagnifyAlpha`, line 446, with condition **`a1 >= a0`**. Re-reading the executable confirms the same max≥min rule for **Magnify Scale X/Y** and all four **SHAPE RGBA** min/max pairs. Visualizer dataset **v19** now keeps exactly those native-constrained pairs valid during manual edits and ParameterSet loading rather than reproducing the debug assertion.

The rule is not blindly applied to every UI min/max pair. The recovered setter for ordinary SHAPE Scale X/Y stores its four ParameterSet values without the sibling ordering assertion, so those controls remain unconstrained beyond their documented numeric bounds. The same capture batch also corroborates the existing Add Rotation × volume, signed Fix Rotation, raw Check Mode BGM response and strong Magnify X/Y interpolation paths. The remaining browser/native XAudio2 snapshot-phase boundary stays open. See `reference/research/VISUALIZER_NATIVE_RANGE_CONTRACT_DEV24.md`.

## Dev24 WIP175 highlight — GIGANTIC UFO common native facing restored

Project-owner clarification supersedes the dev23-era interpretation that GIGANTIC UFO needed a unique Blender-facing correction. SIIG's model assets share the same native facing convention under the game's top-down presentation; rotating only GIGANTIC UFO therefore made its assembled export inconsistent with the rest of the model corpus. WIP175 removes the special **-90° X presentation root** from `gigantic_ufo_complete` and leaves its recovered 37-model locator hierarchy untouched.

This deliberately chooses the conservative correction: **restore GIGANTIC UFO to the common native model orientation**, rather than applying a new global boss rotation. Generic GMX→glTF axis conversion remains exporter-wide and is not changed. No runtime locator, child transform, animation, or gameplay orientation is modified. See `reference/research/GIGANTIC_UFO_PRESENTATION_ORIENTATION_DEV24.md`.

## Dev24 WIP174 highlight — Xbox 360 Visualizer BGM quantum

The native Visualizer BGM peak window is no longer an unspecified browser approximation. Microsoft documents Xbox 360 XAudio2 graph processing at **5 1/3 ms per quantum**, and `XAUDIO2FX_VOLUMEMETER_LEVELS.pPeakLevels` as the maximum absolute channel level during one processing pass. At SIIG's 48 kHz preview rate, one native pass is exactly **256 samples**. Visualizer Simulator dataset **v18** now requests a 48 kHz Web Audio context, uses a 256-sample unsmoothed time-domain peak window per channel, and keeps the already recovered left/right arithmetic mean. If a browser refuses 48 kHz, the UI marks the duration as approximate.

The remaining timing boundary is narrower: Web Audio snapshots are host-scheduled and are not claimed sample-phase aligned to Xbox 360 XAudio2 processing-pass boundaries. Private project-owner hardware footage independently favors the same 256-sample window after capture A/V/gain alignment, but that media remains external and is not bundled. See `reference/research/VISUALIZER_BGM_QUANTUM_DEV24.md`.

## Dev24 WIP173 highlight — exact Visualizer SequenceSet timing

`VL_CHANGETIME` is no longer treated as an unresolved interpolation control. June 10 executable tracing closes it as the VisualizerScript **SequenceSet row-change timing range**: `Function_82175DB0` stores minimum/maximum bounds and immediately selects a threshold; `Function_82175CC0` uses `min + Random30() % (max-min)`, making the upper bound exclusive when the span is nonzero, while equal bounds are fixed. `Function_82177648` applies a dirty SequenceSet slot, increments a change counter, arms the next slot only once `threshold < counter`, wraps at `-1`, and applies the newly armed ParameterSet on the following active Visualizer update. The constructor default is 18000/18000.

The RNG is recovered too: `Function_8249A9D8` concatenates two Microsoft-CRT `rand15` calls, and `Function_824A9E88` uses `state = state*0x343FD + 0x269EC3` modulo 2^32. Hardware seeds that state from a timer-derived value, so Visualizer Simulator dataset **v17** exposes a simulator-only 32-bit seed for reproducible stochastic playback. Seeking a DAT frame now rebuilds SequenceSet state from frame zero, while live 60 Hz timeline following advances the recovered sequence/counter/threshold state instead of permanently pinning the first ParameterSet. See `reference/research/VISUALIZER_SEQUENCE_TIMING_DEV24.md`.

## Dev24 WIP172 highlight — Stage Explorer reclassified as proof of concept

Project-owner testing showed that the Stage Explorer's browser presentation still looks visibly wrong in places: converted atlas sprites can appear jittery, the motion controls do not reproduce the complete stage sequence, and the combined UI gives a stronger impression of gameplay fidelity than the implementation can support. WIP172 therefore **stops presenting Stage Explorer as a faithful/accurate map viewer**. Dataset v8 identifies itself as `proof_of_concept` / `research_inspector_not_gameplay_renderer`, and the generated HTML carries the same boundary prominently.

The exact/decoded inspection surfaces are now shown first: individual MAP layers and DAT timeline records. The SCROLL panel is explicitly an **experimental SCROLL preview** that integrates only recovered `SCROLL_01/02/03` vectors; it does not execute other DAT commands, native camera/render behavior, entity lifecycle, or gameplay sequencing. The 3D panel is likewise an experimental route/placement inspector. Timeline text filtering no longer rebuilds all canvas panels or resets the motion frame on every keystroke, removing one concrete source of UI jank. Existing decoded data, runtime pairing, tile IDs/flips, route/placement records, and the recovered native placement transform remain available for research.

This reclassification is deliberate: future Stage Explorer work should improve evidence and inspection quality first, and only regain stronger fidelity wording if native behavior is demonstrated rather than approximated.

## Dev24 WIP171 highlight — complete runtime Position Fix 3×3 grid

The project-owner June 10 Visualizer Check capture exposed an error in WIP170's Position Fix interpretation. WIP170 correctly fixed the centered **+Y-up** coordinate bridge, but it read the fixed-position table before a startup initializer had patched its vertical rows. June 10 code at `0x82564470` loads `-308.0`, writes **+308** into the Y components for raw 1..3, and **-308** into raw 7..9; raw 4..6 remain Y=0. Retail Xbox 360 and May 11 use the same patch pattern.

Visualizer dataset **v16** therefore restores all ten raw values: 0 = Free X/Y; 1/2/3 = upper left/center/right at X `-448/0/+448`, Y `+308`; 4/5/6 = middle left/center/right at Y `0`; 7/8/9 = lower left/center/right at Y `-308`. Raw 0 and raw 5 can both appear centered when Position Free is `(0,0)`, but they are semantically different: 0 follows Position Free, while 5 is fixed center. The simulator no longer collapses any Position Fix values.

The WIP170 coordinate-axis correction remains valid: native Visualizer coordinates are center-origin with **+X right and +Y up**, so Canvas uses `x = 640 + game_x`, `y = 360 - game_y`. The fixed 3×3 anchors therefore land at Canvas X `192/640/1088` and Y `52/360/668`. See `reference/research/VISUALIZER_POSITION_COORDINATES_DEV24.md`.

## Dev24 WIP169 highlight — retained-source rip updater

Desktop GUI **0.52.0-dev24** includes a fast **Update existing rip** path in the Game Rip tab. A completed `SIIG_Ripped` folder can be refreshed to the current converter/viewer/simulator feature profile **without the original STFS, PKG, ZIP, or extracted game directory**. The updater treats `decompressed_bbx/` as the retained authoritative archive source and performs a component-aware migration. Expensive BBX/GMX/TEX outputs are reused when their retained-source SHA-256, conversion options and conversion schema still match; localization/systemfont/audio/structured exports and Stage Explorer/Visualizer/Asset Viewer are refreshed only when their own schema/generator or an upstream dependency changed.

WIP194 supersedes the remaining WIP189 filesystem overhead discovered in hands-on WIP192 testing. An exact-profile Update Rip is now a true zero-scan no-op. When a migration is needed, the updater validates only component scopes it is about to replace, carries untouched manifest/stat-cache rows forward without statting the whole rip, hashes/enumerates only changed scopes, and reuses verified manifest-bound hashes for unchanged retained `decompressed_bbx/` files. Changed-stat or legacy files still fall back to real SHA-256 reads before destructive replacement. Modern saved rip options remain authoritative: an explicit `convert_obj: false` is not overridden just because unrelated generated OBJ files exist elsewhere in the rip. **Verify existing rip** / `verify-output` remains the separate explicit whole-tree SHA-256 integrity pass.

The update profile is a SHA-256 fingerprint of the updater-relevant toolkit modules rather than only the public version string, so WIP changes inside the same `2.10.0-dev24` line are detectable. `validation/RIP_UPDATE_STATE.json` records the installed profile; `validation/RIP_UPDATE_REPORT.json` records each successful refresh. A small in-rip recovery journal is excluded from the content manifest and lets a rerun recover safely if an update is interrupted after one component has already been swapped. By default the updater refuses to overwrite a rip that no longer matches its old output manifest; `--force-modified` exists only as an explicit advanced override.

CLI: `python siig_toolkit.py update-rip "C:\path\to\SIIG_Ripped"`. Use `--check` for a non-destructive current-profile check, `--refresh-assets` only when you intentionally want to force all retained BBX/GMX/TEX conversions to run again, or drag the rip folder onto `SIIG_Update_Rip.bat`.

## Dev24 WIP168 highlight — scrollable Workbench, per-file rip console, Visualizer presentation/audio fix

Desktop GUI **0.43.0-dev24** fixes the two long-output usability problems reported during hands-on testing. GMX Workbench now scrolls vertically as one work surface, including mouse-wheel support, so lower controls and long explanatory text remain reachable on smaller windows. Game Rip keeps its compact phase/count summary but also has a dedicated console-style output box that appends **every** `rip-game` line rather than replacing the previous message; it has vertical/horizontal scrollbars plus copy/clear controls. The global Task log still records all toolkit commands.

Visualizer Simulator dataset **v14** incorporates the new same-stage hardware comparison without changing recovered Xenos semantics. `VL_SEQUENCESET` events now synchronize the selected SequenceSet to its active ParameterSet automatically, the status line exposes `SEQ`/`PARAM`, and an optional checked-by-default timeline follower advances the authored DAT frame once per logical 60 Hz simulator step. The project-owner hardware reference showing `SEQ=4 PARAM=3` cross-checks the recovered retail `SEQUENCE_4 -> PARAM_3` mapping. Final visible-canvas presentation is explicitly host-only: **5.5 px softness** and **0.32 intensity** are the new capture-calibrated defaults; **0 px / 1.0** displays the raw recovered feedback RGB.

The browser-audio path also fixes the “WMA preview plays but is silent” failure mode. Track selection no longer calls `createMediaElementSource()` pre-emptively. The normal HTML audio path remains audible until a direct user gesture has resumed a Web Audio context, and analyser routing is installed only after that context reports `running`. FFmpeg previews are normalized to stereo 48 kHz before MP3/AAC encoding. The synthetic regression fixture now contains non-zero audio and, when FFmpeg is present, the generated preview is decoded and checked for non-silent PCM. Native WMA/AT3 files remain untouched and unbundled. See `reference/research/VISUALIZER_PRESENTATION_AUDIO_WIP168.md`.

SIIG Asset Toolkit is a dependency-light Python toolkit for researching and extracting assets from the Xbox 360, PlayStation 3, iOS, and Android releases of **Space Invaders Infinity Gene**. It accepts original outer packages, extracted game folders, or ZIP archives; extracts nested BBX resources; converts supported assets; builds a self-contained Stage Explorer proof of concept for MAP/DAT research; and records enough metadata to audit the result.

The toolkit is based on user-supplied retail/prototype files, cross-platform comparisons, and Ghidra exports from `default.xex`. It does not include game binaries or extracted copyrighted assets.


## Dev24 WIP187 highlight — flexible Mod Workspace audio editing

Audio replacements are no longer forced to match the original duration, sample rate, or input channel count. On Xbox 360, **Open selected** exports `sound.bin` / `media/sound` as named WAVs and **Build changes** rewrites the XWB entry duration, mini-wave format, play region and loop region while rebuilding the nested BBX archive. PCM16 replacements with 1–6 channels are preserved natively; 7–64-channel inputs are accepted and downmixed to stereo. Untouched streams remain their original XMA2 bytes, while edited streams use XACT-supported PCM16 because no XMA2 encoder is bundled. Existing loop points are remapped proportionally to the replacement duration.

On PS3, SBlk/989SND WAV replacements may likewise use a different duration and sample rate. The bank is repacked, later stream offsets/sizes are rewritten, and pitch metadata is set to the nearest representable SCREAM rate. SIIG's SBlk v3 stream records are mono, so multichannel PCM16 inputs are accepted but deliberately downmixed to mono rather than pretending the retail format exposes a native per-stream channel-count field. PS3 SDAT re-encryption and game-runtime acceptance remain external validation steps; native XMA2 encoding and true multichannel PS3 bank-topology synthesis remain open.

## Dev24 WIP184 highlight — Simple Mod Workspace asset tree

Desktop GUI **0.45.0-dev24** turns **List Assets** into the missing beginner-facing middle step between Create Workspace and Build. It opens a compact archive/resource tree inside the Mod Workspace tab; double-clicking a supported file exports it through the existing round-trip builder and opens the editable representation. Persistent **Untouched / Exported / Edited / Staged / Added** marks are recalculated from workspace metadata and edit-baseline hashes, so edited resources remain visibly distinct after GUI restarts. **Refresh marks** picks up saves made by external editors, while Build/Verify refresh the tree automatically when it is already open. The tree is intentionally a modding browser, not a duplicate thumbnail/model viewer.

## 2.10.0-dev21 highlight — corrected all-boss controller map + drag-and-drop Game Rip

Dev21 corrects a cross-boss visual-controller indexing mistake uncovered by the unified dev20 audit. Retail `Function_821489F8` dispatches with `switch(runtime_type + 1)`, while caller `Function_820E7AE8` passes that same runtime type to the model-resource resolver. The toolkit now records the corrected visual-controller constructor and allocation size for all 18 boss families. Most importantly, THE MOON runtime `0x46` owns factory case `0x47` / `Function_8212B638`, while THE SUN runtime `0x47` owns case `0x48` / `Function_8212BA68`; THE SUN therefore directly owns the B2/B3 long-wave allocation path. The five dev20 native-only bosses are traced in parallel without inventing unproven static states.

GUI 0.32.0-dev21 adds dependency-free Windows Explorer drag-and-drop to **Game Rip**. Drop one supported game/package file or already-extracted game folder into the Game Rip drop box; the source field is filled immediately, but extraction still requires an explicit **Rip game** click. The normal Browse button remains available. See `docs/research/BOSS_VISUAL_CONTROLLER_INDEX_CORRECTION_DEV21.md`, `docs/research/FIVE_BOSS_CONTROLLER_AUDIT_DEV21.md`, and `docs/guides/DESKTOP_GUI.md`.

## 2.10.0-dev20 highlight — unified 18-family boss matrix

The current cross-boss registry covers all 18 console boss families: 14 have deep executable-backed runtime reconstructions, OCTOPUS/WATER STRIDER/NO_NAME have exact gameplay-pose reconstructions, and THE MOON remains the sole native-inspection-only family. `boss-matrix` can validate all canonical root GMXs from a fresh extraction in one pass. THE MOON's controller-time material/rotation behavior is independently available through `the-moon-controller` without pretending it is a glTF node-scale animation.

## 2.10.0-dev18 highlight — AXON exact two-ring runtime assembly

Dev18 reconstructs AXON without visually guessing its petal count or layout. Retail allocates a standalone A5 / `bos_012.gmx` whole-body representation and a separate 17-record pool containing one CA / `bos_012a.gmx` core plus sixteen CB / `bos_012b.gmx` petals. The CBs form two executable-defined staggered rings of eight. At the stable expanded phase-angle-0 snapshot, ring 1 is radius 75 at Y -3.0 with 0°/45°/.../315° table angles; ring 2 is radius 220 at Y -5.5 with 22.5°/67.5°/.../337.5°. `axon_native_body`, `axon_expanded_petals`, and `axon_exposed_core` keep the mutually exclusive runtime representations separate. Fresh retail validation gives 1/17/1 instances, 42/34/2 meshes, 76/84/20 nodes, and 32/0/0 animations. GUI 0.29.0-dev18 adds the form selector and manifest/export workflow. See `docs/research/AXON_RUNTIME_ASSEMBLY_2.10.0-dev18.md`.

## 2.10.0-dev17 highlight — SQUID two-phase native-locator assembly

Dev17 reconstructs SQUID as one animated A9 / `bos_016.gmx` body plus eight DA / `bos_016a.gmx` legs attached in strict runtime-record order to native `lt_000..lt_007` locators. Retail state 8 disables exactly those eight leg records and leaves the body active; June 10 independently retains the same eight-record disable transition. The toolkit exposes `squid_phase1_legs` and `squid_phase2_body`, preserving all eight native body animation clips rather than baking approximate transforms. Fresh retail exports validate 9 / 1 instances, 18 / 2 meshes, 44 / 12 nodes, and 8 animations in both phases. GUI 0.28.0-dev17 adds the phase selector and manifest/export workflow. See `docs/research/SQUID_RUNTIME_ASSEMBLY_2.10.0-dev17.md`.

## 2.10.0-dev16 highlight — PROGRESSIVE UFO classic formation

Dev16 adds the requested second PROGRESSIVE UFO pose as a separate `progressive_ufo_classic` catalog while leaving the original dev3 `progressive_ufo` preset unchanged. Retail Xbox major states 5 and 8 apply the same five-part table initialized at `0x82568180`; June 10 contains a byte-equivalent table at `0x825D95B0`, and retail PS3 independently preserves the same records. The classic pose uses the original A2+C2+C2+C3+C3 membership with exact runtime Euler composition rather than screenshot approximation. Fresh retail export validates 5 instances / 10 meshes / 20 nodes / 10 preserved native animations. GUI 0.27.0-dev16 adds an Original/Classic formation selector. See `docs/research/PROGRESSIVE_UFO_CLASSIC_FORMATION_2.10.0-dev16.md`.

## 2.10.0-dev15 highlight — GIGANTIC UFO complete locator hierarchy

Dev15 reconstructs GIGANTIC UFO's complete persistent visual hierarchy from retail Xbox, June 10 Xbox and retail PS3 renderer logic. `gigantic_ufo_complete` contains exactly one 0x9E / `bos_003.gmx` root plus thirty-six 0xB5 / `bos_003a.gmx` weapon modules attached in order to native `lt_001..lt_036` locators. Three 0xB4 renderer slots are helper/control slots, not model assets, and are deliberately excluded. Fresh retail export validates 37 instances / 74 meshes / 185 nodes / 0 animations with bounds about X/Y ±269.593 and Z -66.103..61.111. GUI 0.26.0-dev15 adds one-click GIGANTIC UFO manifest/export actions. See `docs/research/GIGANTIC_UFO_RUNTIME_ASSEMBLY_2.10.0-dev15.md`.

## 2.10.0-dev14 highlight — CENTIPEDE initial-combat ring assembly

Dev14 resolves CENTIPEDE as a fixed 32-link runtime chain with role-driven model swapping rather than 32 pairs rendered simultaneously. The canonical `centipede_initial_combat_ring` preset contains exactly **2× `bos_007.gmx` A0 endpoint forms + 30× `bos_007a.gmx` BE body forms** on the executable's radius-80 ring at 11.25° intervals. Destroying a body link severs the chain and promotes newly exposed ends to A0; destroying an existing endpoint enters the reform path. When fewer than six links remain, all survivors enter the independent runtime-randomized final phase, so dev14 deliberately does not invent static split/reform/final layouts. Retail Xbox, June 10 Xbox and retail PS3 preserve the same construction/threshold logic. Fresh retail export validates 32 instances / 64 meshes / 128 nodes. GUI 0.25.0-dev14 adds one-click CENTIPEDE assembly and manifest actions. See `docs/research/CENTIPEDE_RUNTIME_ASSEMBLY_DEV14.md`.

## 2.10.0-dev13 highlight — VERTEBRATE two-phase structural assembly

Dev13 reconstructs the two persistent VERTEBRATE body states from retail Xbox, June 10 Xbox and retail PS3 runtime behavior, then validates them against freshly extracted retail GMXs. `vertebrate_phase1_tower` contains exactly two `bos_017.gmx` endcaps plus thirty `bos_017a.gmx` pillar sections on the executable's 70-unit Y ladder. `vertebrate_phase2_endcaps` removes every pillar and rebases the two endcaps at the boss-local origin with effective Z rotations 90°/270°. The separate `bos_017b..j` attack auxiliaries are intentionally excluded. GUI 0.24.0-dev13 exposes both structural phases. See `docs/research/VERTEBRATE_RUNTIME_ASSEMBLY_2.10.0-dev13.md`.

## 2.10.0-dev12 highlight — UNKNOWN internal forms

Dev12 resolves UNKNOWN as one `bos_006.gmx` containing 14 named `uk01..uk14` branches with no native GMX animation. Retail Xbox, June 10 and retail PS3 independently preserve the same runtime form-selector architecture. Fresh retail-GMX validation proves `uk08` is visually identical to `uk01`, so the file contains 14 named branches but 13 unique visuals. Normal console gameplay cycles `uk01..uk12` at normalized 30 Hz (12 named selections / 11 unique visuals); state 0 forces `uk01`, while `uk13/uk14` remain registered but outside the normal cycle. GUI 0.23.0-dev12 exports any exact native form subtree without inventing multipart placement or a fake native animation. See `docs/research/UNKNOWN_INTERNAL_FORMS_2.10.0-dev12.md`.

## 2.10.0-dev11 highlight — BUTTERFLY four-phase assembly

Dev11 reconstructs all four BUTTERFLY forms from the retail executable loader table and the original retail GMXs. Phase 1 is `bos_011.gmx` alone; phases 2–4 attach exact C7/C8/C9 wing-module counts under native `lt_*` locators: 4 large squares; then 8 large + 10 small squares; then 8 large + 32 small squares + 8 elongated rectangles. The same ten loader records are independently present in June 10. Real-retail exports validate 1 / 5 / 19 / 49 instances while preserving the native body animations in phases 2–4. GUI 0.22.0-dev11 adds a four-phase selector and manifest/assembly actions. See `docs/research/BUTTERFLY_RUNTIME_ASSEMBLY_2.10.0-dev11.md`.

## 2.10.0-dev10 highlight — HORNET exposed core

Dev10 proves and exposes `hornet_exposed_core`, the deterministic high-level state-3 entry snapshot: one A1 / `bos_008.gmx` at native motion 0, sample 0, with all 125 subordinate records reset to state `-1` so neither BF armor nor C0 prisms are selected. Retail Xbox, June 10 Xbox and retail PS3 preserve the same reset architecture. The project owner re-supplied the original retail Xbox package, allowing direct extraction and real-GMX validation: one instance, two meshes, four glTF nodes, native bounds about ±13.8054. GUI 0.21.0-dev10 exposes full armor and exposed core separately. See `docs/research/HORNET_EXPOSED_CORE_2.10.0-dev10.md`.

## 2.10.0-dev9 highlight — ULTIMATE UFO assembly

Dev9 reconstructs ULTIMATE UFO's complete retail allocation hierarchy as **126 model instances** across A8 + D0–D9, with exact named `lt_###` attachment chains. The default `ultimate_ufo_complete` catalog is explicitly an allocation/hierarchy snapshot, not a simultaneous render-visibility claim. Eight additional state catalogs expose the controller families active under the retail collision/destructibility phase table. GUI 0.20.0-dev9 defaults to the complete hierarchy and keeps those activity subsets selectable. See `docs/research/ULTIMATE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev9.md`.

## 2.10.0-dev8 highlight — MANDALA assembly

Dev8 adds `mandala_initial_combat`, the five-build executable-backed 40-instance MANDALA state-7 activation snapshot. It preserves native animations, excludes the later 32×BC phase, and is exposed as one-click **Assemble MANDALA** in GUI 0.19.0-dev8. See `docs/research/MANDALA_RUNTIME_ASSEMBLY_2.10.0-dev8.md`.

## 2.10.0-dev7 highlight — HORNET propagation

Dev7 adds the evidence-backed `hornet_propagation_SS_wave_WW` family for HORNET state 6. The seed is inherited from the same 13-way prism-wall choice; A1 is hidden, reached C0 prisms expand deterministically across the exact 5×9 grid, and Advanced GUI exposes explicit seed/wave controls. See `docs/research/HORNET_PROPAGATION_2.10.0-dev7.md`.

## Highlights through 2.10.0-dev14

- **New in 2.10.0-dev14:** CENTIPEDE adds `centipede_initial_combat_ring`, exactly 2×A0 `bos_007` endpoints + 30×BE `bos_007a` body links on a radius-80, 11.25° ring. Role transitions prove body cuts promote newly exposed ends to A0; endpoint destruction enters the reform path; at ≤5 survivors the game switches to independent randomized movers, so no fake static later-phase preset is provided. Real retail export validates 32 instances / 64 meshes / 128 nodes and GUI 0.25.0-dev14 exposes the canonical ring.
- **New in 2.10.0-dev13:** VERTEBRATE adds two exact structural catalogs. Phase 1 is 2×AA `bos_017` endcaps + 30×DB `bos_017a` pillars at Y `-630..1400` in 70-unit steps, with caps at Y `-608`/`1448`; phase 2 removes all pillars and rebases the two endcaps to origin at effective Z rotations 90°/270°. Real retail exports validate 32/2 instances and GUI 0.24.0-dev13 exposes both phases.
- **New in 2.10.0-dev12:** UNKNOWN exposes all 14 native `uk01..uk14` branches from one `bos_006.gmx`; real-retail comparison proves 13 unique visuals because `uk08 == uk01`. The normal console runtime cycles `uk01..uk12` at normalized 30 Hz, while state 0 forces `uk01`; `uk13/uk14` are renderer-registered but outside the traced normal 12-tick cycle. GUI 0.23.0-dev12 exports exact form subtrees.
- **New in 2.10.0-dev11:** BUTTERFLY adds four exact phase catalogs. Retail loader `0x82111F48` and June loader `0x8212B490` independently encode the same 10 records. Phase 1 is body-only; phase 2 is C4 + 4×C7 on `lt_001..004`; phase 3 is C5 + 8×C7 + 10×C8 on `lt_001..018`; phase 4 is C6 + 8×C7 + 32×C8 + 8×C9 on `lt_001..048`. Real retail exports validate 1/5/19/49 instances and preserve all three native body animations in phases 2–4. GUI 0.22.0-dev11 exposes the phase selector.
- **New in 2.10.0-dev10:** HORNET adds `hornet_exposed_core`, the executable-backed state-3 entry snapshot. Common reset restores A1 at motion 0/sample 0 and sets all 125 BF/C0 subordinate records to state `-1`; the result is independently cross-checked on retail Xbox, June 10 Xbox and retail PS3. Fresh extraction from the re-uploaded original retail Xbox STFS exactly matches the historical HORNET GMX/ANM hashes, and a real retail export validates 1 instance / 2 meshes / 4 nodes with bounds about ±13.8054. GUI 0.21.0-dev10 separates armor and exposed-core assembly.
- **New in 2.10.0-dev9:** ULTIMATE UFO adds `ultimate_ufo_complete`, the 126-instance constructor-baseline allocation hierarchy, plus eight state-specific controller-activity subsets (2, 3, 6, 7, 8, 9, 11, 12), exact D4/D5/D6/D7 `lt_###` hierarchy, D8/D9 late-state identities, and GUI selection. Retail and June executable structure are cross-checked; no real retail GMX export is claimed in this checkpoint because the proprietary `bos_015*.gmx` inputs are not bundled or present in the persistent research Library.
- **New in 2.10.0-dev8:** MANDALA adds the 40-instance executable-backed state-7 activation assembly with 20×B7, 2×B8/B9/BA/BB, and 12 structural 4A pieces; later 32×BC is excluded.
- **New in 2.10.0-dev7:** HORNET state 6 is recovered as a deterministic 13-seed propagation family. State 5 hides A1 and resets all 45 grid records; state 6 starts from the inherited dev6 prism-wall seed and alternates orthogonal/diagonal C0 expansion until full coverage. Procedural `hornet_propagation_SS_wave_WW` catalogs and Advanced GUI seed/wave controls expose exact activation snapshots without inventing a canonical random outcome.
- **New in 2.10.0-dev6:** HORNET prism-wall state 4 is an exact 13-outcome family: A1 occupies one recovered 5×9 grid cell and 44 C0 prisms occupy the others. Advanced mode exposes the runtime-valid slot selector.
- The dependency-free regression suite is now **96/96**.
- **New in 2.10.0-dev5:** HORNET now has an executable/model-backed full-armor assembly preset: A1 core plus exactly **125 BF armor cubes** on the sample-0 C1 5×5×5 formation lattice. C1 is now resolved as a real meshless animation rig; the parallel 125-object C0 prism pool is documented but omitted from this static state. GUI **Assemble HORNET** exports the 126 visible instances directly.
- **New in 2.10.0-dev5:** CRAB's beginner-facing `crab` preset now uses the deterministic first **landed/combat-ready** root sample 1. The dev4 airborne sample-167 reconstruction is preserved as `crab_first_visible`; no arbitrary recentering is applied.
- **New in 2.10.0-dev5:** project-owner Blender validation confirmed PROGRESSIVE UFO's slight C3 barrier tilt is native `bos_009b.gmx` bind orientation, not an assembly error. Native SIIG boss scale/units continue to be preserved; Blender Frame All/Selected is recommended rather than silent rescaling.
- Dev5 sealed at **87/87**; current dev7 regression coverage is **89/89**.
- **New in 2.10.0-dev4:** the desktop GUI now starts in **Simple mode**, with a Simple/Advanced switch and plain-language hover/focus help for Mod Workspace and GMX Workbench controls. Advanced mode preserves the full expert interface.
- **New in 2.10.0-dev4:** CRAB now has an executable/model-backed first-visible assembly preset. The root `bos_013.gmx` is baked at native sample **167**, the animated body shell `bos_013b.gmx` at sample **0**, and the remaining `CC/CE/CF` children are placed from the runtime locator/offset logic. `gmx-assemble-catalog crab` and GUI **Assemble CRAB** export the nine-part static formation.
- **New in 2.10.0-dev2:** disjoint rigid joint islands inside one glTF mesh are partitioned into separate native MESH/ARRY graphs, each inverse-bind rebaked and attached to its own BONE. Cross-joint triangles remain explicit errors.
- **New in 2.10.0-dev3:** the PROGRESSIVE UFO catalog now contains its executable-backed five-part runtime formation: body `(0,0,0)`, laser machines `(-90,0,-10)` / `(90,0,-10)`, and barrier machines `(-160,0,-50)` / `(160,0,-50)`, with zero local rotation. The result is cross-checked across June Xbox, retail Xbox, and retail PS3. `gmx-assemble-catalog progressive_ufo` exports the fully assembled scene directly.

- **New in 2.10.0-dev1:** rigid single-joint glTF skins may use a non-identity affine `inverseBindMatrices` entry. The compiler rebakes `POSITION` into joint bind-local space and transforms `NORMAL` with the correct inverse-transpose matrix before collapsing the result to SIIG's proven BONE→MESH representation.
- Singular bind transforms that cannot produce a valid normal matrix are rejected. Genuine blended/multi-joint weights remain unsupported because the retail GMX evidence still contains no per-vertex weight stream.
- The same rigid-bind compiler path remains shared by `gltf2gmx-new`, Mod Workspace, and the GMX Workbench.
- **New in dev7:** standard glTF `skins` / `JOINTS_0` / `WEIGHTS_0` can be imported when the mesh is truly rigid: every vertex must resolve to the same one-weight joint. The importer maps that safely to SIIG's proven BONE→MESH attachment representation.
- **No speculative blended skinning:** genuine multi-joint weights and secondary JOINTS/WEIGHTS sets are rejected. Non-identity affine inverse binds are now rebaked safely; supplied player/enemy GMXs (901 MESH records) still all use `skin_index=0xFFFF` and have no joint/weight ARRY semantics.
- **Template-free path includes rigid skins:** `gltf2gmx-new` can synthesize the joint BONE hierarchy and attach a rigidly skinned mesh without any original GMX.
- **New in dev6:** `gltf2gmx-new` compiles a native GMX directly from glTF without reading an original GMX template. It synthesizes the canonical decoded 0x30-byte root and enables the mesh/material/texture-reference/bone/animation builders proven in earlier checkpoints.
- The synthesized root recomputes total stream size and minXYZ/maxXYZ bounds. Still-unnamed root fields at `+0x08` and `+0x28..+0x2F` default to zero; advanced glTF extras can preserve empirically discovered values without claiming semantics.
- GMX Workbench now exposes **Create new GMX**. Template-backed import remains available and preferable when preserving opaque bytes from an existing model matters.
- External dev25 **306/306 mesh-bearing retail GMX** no-op evidence remains inherited and is not re-run from proprietary inputs.

- **New in dev5:** one glTF animation may drive several bones. The importer expands the clip into synchronized per-bone native `MOTN`/`ANIM` tracks on SIIG's proven 30 Hz runtime cadence.
- glTF `CUBICSPLINE` translation/rotation/scale channels are now accepted using spec-style Hermite interpolation; quaternion cubic samples are normalized after interpolation.
- Existing exported native animations remain byte-preserved during animation-aware imports unless `extras.gmxReplaceNativeAnimation=true` explicitly requests resampling/replacement.
- `mod-import-gltf` carries multi-bone animation clips through the same integrated GMX/TEX/BBX workspace flow. The built-in regression suite is now **80 tests**.

- **New in dev4:** donor-free `MOTN`/`ANIM` creation from ordinary glTF TRS channels established the native 30 Hz matrix compiler used by dev5.

- **New in dev3:** PNGs can synthesize canonical native Xbox 360/PS3 TEX wrappers without a same-layout TEX donor. Mod Workspace uses this automatically for new TXIF resources or dimension-changing texture edits.

- **New in dev2:** GMX import can synthesize native `MESH`/`ARRY` vertex declarations and `MTRL` parameter streams when no compatible donor exists. The Mod Workspace uses this automatically as a fallback during glTF import.

- New `mod-import-gltf` turns an edited glTF into a mod-workspace operation: it compiles the GMX/TXIF graph, rebuilds linked PNGs as native TEX, and stages everything without manual BBX surgery.
- When a new glTF texture creates a new TXIF filename, the workspace can append a new named BBX member. BBX identifiers/name tables/counts are rebuilt deterministically and verified.
- `.siigmod` packaging supports those member additions by emitting a baseline-dependent archive delta instead of redistributing a clean archive.
- The GUI Mod Workspace now exposes **Import glTF + TEX** alongside build/verify/package actions.
- The built-in suite is now **80 tests**. The external dev25 **306/306 mesh-bearing retail GMX** no-op gate remains inherited evidence rather than being re-run from proprietary inputs.
- Versioning policy has been formalized: feature-line minor versions are reviewed no later than `dev8`, so a single minor version should no longer accumulate dozens of development suffixes.

- `gltf2gmx-template --sync-texture-graph` extends dev27 scene synchronization into native `TXIF` texture references. A glTF `baseColorTexture` can now reuse or allocate a native TXIF and bind a compatible `DiffuseSampler` parameter automatically.
- glTF export preserves every TXIF index/flags/name even when the referenced texture image is unavailable, and annotates converted images/textures with native provenance when a TEX/DDS/PNG/JPEG can be located.
- The dev27 `SHAD`/`MTRL`/`BONE`/`PARE` scene compiler and dev26 `MESH`/`ARRY` graph compiler remain separate lower synchronization levels. Texture sync is a third, default-off advanced mode and implies both scene and mesh synchronization.
- `gmx-scene-report` now shows TXIF records and material texture bindings alongside BONE hierarchy, MTRL, MESH and SHAD relationships.
- The built-in suite is now **74 tests**. Dev25's external **306/306 mesh-bearing retail GMX** byte-identical no-op gate remains inherited evidence; dev28's new TXIF synthesis is structurally regression-tested without bundling proprietary corpus inputs.
- Dev28 creates GMX texture *references/bindings*, not the underlying console texture payload. Existing TEX/DDS conversion/rebuild workflows remain responsible for the referenced resource itself.
- Audio replacement/rebuilding remains deliberately deferred while GMX compiler/GUI work is prioritized.

- Added deterministic `.siigmod` packages with `mod-pack`, `mod-package-info`, and `mod-apply`. Packages store baseline-dependent binary deltas and metadata rather than clean source assets.
- Equal-size replacements use sparse changed-byte ranges; variable-size replacements use copy/data delta streams. Source, payload, and reconstructed target SHA-256 values are verified during application.
- Exercised the package layer against external retail `text.bin`: a one-character localization edit produced a 1,184-byte package with a **1-byte delta payload**, then rebuilt identically in a fresh workspace and passed `mod-verify`.
- Expanded external no-edit retail round-trip evidence to **2,197 completed byte-identical checks**, including **307/307 GMX**, **1,258/1,258 DAT**, **394/394 MAP**, **47/47 stage3D**, **30/30 stagewall**, 3/3 TEX, 2/2 ANM, 153/153 COL, systemfont, and localization.
- Optimized `png2col` for SIIG's normal opaque black/white masks while retaining the exact threshold fallback for arbitrary edited images.
- Expanded the dependency-free regression suite to **69 tests**.

- Added an integrated mod workspace: `mod-init`, `mod-list`, `mod-export`, `mod-export-archive`, `mod-stage`, `mod-stage-archive`, `mod-build`, and `mod-verify` now connect editable assets to native rebuilders and affected-BBX-only patch builds.
- Workspaces fingerprint the clean source rip, track editable baselines separately from staged native replacements, rebuild only changed BBX archives, and emit a machine-readable `MOD_BUILD_REPORT.json`.
- Xbox `.gz` BBX changes can be emitted as deterministic game-relative gzip patch files; raw BBX replacements are emitted directly. PS3 NPDRM/SDAT re-encryption remains an explicit packaging boundary.
- Upgraded GMX/localization evidence from synthetic-only fixtures to user-supplied retail corpus validation: **13/13** `player.bin` GMXs rebuilt byte-identically, retail `text.bin` rebuilt from **542 strings**, and retail `message.bin` rebuilt from **284 groups / 1295 strings per language**. Proprietary validation inputs are not bundled.
- Added a complete mod-workspace regression and expanded the dependency-free suite to **68 tests**.

- Expanded native asset functionalization from **7 to 11 of 14 known asset families** while keeping all 14 viewable/exportable.
- Added `stagewall-build` for deterministic wall/Xwall/stage-generator table compilation from CSV/JSON.
- Added `stage3d-build` for native Bmap/Xmap/map4/map5 `0x118` route/placement records, with optional template preservation of inactive/tail bytes.
- Added `gmx-edit-export` + `gmx-build`, a conservative fixed-layout GMX native editor for geometry/index arrays, texture references, material values, bone matrices, motion durations, and matrix-animation samples while preserving the original chunk graph.
- Added `text-build` and `message-build` for dedicated native localization compilation, including Unicode-readable message scripts mapped back to SIIG's language-specific glyph bytes before Shift-JIS repacking.
- Added byte-identical/synthetic structural regression gates for the new builders; the dependency-free suite now contains **67 tests**.
- Template-free GMX root/scene construction, native vertex/material schema synthesis, multi-bone animation import, rigid single-joint glTF skin compatibility, and donor-free TEX creation are implemented structurally. Remaining major GMX gaps include **true blended/multi-joint native skinning evidence**, platform shader microcode compilation, opaque field semantics, compressed/mipmapped TEX authoring, and runtime validation of fully original scenes. Dev24 WIP187 adds variable-duration/rate Mod Workspace audio rebuilding for Xbox XACT/XWB and PS3 SBlk, with flexible input-channel handling. Native XMA2 encoding, true multichannel PS3 SBlk topology synthesis, and runtime acceptance remain open. The current boundary registry is `reference/research/DEV24_UNRESOLVED_BOUNDARY_AUDIT.md`; the generator runtime-capacity closure is documented in `reference/research/CONSOLE_GENERATOR_OUTPUT_CAPACITY_DEV24.md`.

- Began the native asset-functionalization phase: extraction targets now have explicit viewing/editing/rebuild capability levels rather than a binary decoded/unknown status.
- `png2tex` supports both template-preserving rebuilds and donor-free canonical Xbox 360/PS3 TEX synthesis; Xbox synthesis follows the single layout confirmed across all supplied textures.
- Added `dat-build`, `map-build`, `anm-build`, and `png2col` for native script, map, animation-table, and collision-mask editing.
- Added `png2font` for rebuilding the XOR-obfuscated system-font CRP from an edited atlas.
- `map2png` now emits a lossless `*.map.edit.json`; full rips emit `validation/ASSET_CAPABILITIES.json`.
- Added `asset-capabilities` and byte-identical round-trip regression gates for TEX, DAT, MAP, ANM, and COL.
- Expanded the dependency-free regression suite to 62 tests.

- Traced all six named iOS `moveThe*` boss state machines to dedicated Xbox and PS3 console movers; the console dispatcher keeps the original mobile IDs **70..75 = 0x46..0x4B** exactly.
- Added direct semantic anchors for every original boss: THE MOON event sequencing, THE SUN's four-pair ±512→6144 ramp, GIGANTIC UFO's original +4096 path, LADYBUG's May-11 guard, MANDALA's 109/69 geometry coefficients, and UNKNOWN's original ±2560 motion.
- Recovered the exact May11→June10 constructor fingerprints lost at the dev19 continuity boundary: 87.947883%, 86.072423%, 87.995050%, 89.208633%, 92.691316%, and 92.075472%.
- Distinguished raw relocation-induced mnemonic changes from gameplay changes in June→retail GIGANTIC UFO/UNKNOWN, while isolating a genuine LADYBUG behavior retune between May 9 and May 11.
- Expanded the dependency-free regression suite to 56 tests.

- Extended `ios-console-lineage-info` with direct six-boss constructor/pool ancestry, the console `0x96..0xAB` enemy-handler family, World-5 integration chronology, and exact cross-build `Invinf_LoadScript` anchors.
- Preserved **29/30** Stage-3 subordinate pool type/capacity slots from iOS to console; only THE SUN type 38 changes from 36 to 60 objects, independently matching retail PS3.
- Located the major six-boss constructor refactor at May 11→June 10 while May9→May11 and June10→retail remain 100% mnemonic-sequence matches.
- Recorded concrete GLUTTONY, ULTIMATE UFO, and VERTEBRATE pool retunes and kept `0x9F` as the deliberate all-build null slot.
- Expanded the dependency-free regression suite to 55 tests.

- Added `ios-console-lineage-info` and source-only iOS→console function correspondence data for MAP loading/update/rendering, DAT timing/dispatch, and generator assembly.
- Proved iOS command timing as `authored_delta * runtime_fps / 30` and scroll speed as `authored_speed * 30 / runtime_fps`, establishing the same 30 Hz authored-time invariant later used by the console frame-multiplier model.
- Matched iOS `Invinf_LoadMap`, `calcMap`, and `drawMap2` to the console MAP subsystem, including the same 49-tile + X/Y reflection encoding.
- Corrected the effective iOS command frontier to `0x8D` (`analyzeScript2` extends beyond the primary `0x83` analyzer); console expands the language through `0xCE`.
- Matched the 24-block iOS generator to the console selection/append routines and decoded iOS generated-layer capacity as `6144 = 24×8×32` bytes per layer.
- Compared normal stages 1-1..3-6: 91.7% aggregate opcode-sequence LCS, with widespread parameter retuning and a major 3-6 rewrite.
- Expanded the dependency-free regression suite to 54 tests.

- Resolved the six Survival substitution gates as Evolution Tree stage-node status checks: unlocked Chimera Extra 31..36 stages run normally, while locked nodes substitute six predetermined existing Extra stages.
- Proved the crossover unlock chain: SILVER HAWK / INTER GRAY / BLACK FLY purchase states unlock Chimera A stages, and clearing each A stage unlocks its B counterpart.
- Traced `dischargeEnemyShot_FPS60` to map boss helper-pool type IDs to named projectile handlers, proving concrete original→V2 attack repertoire swaps for all six Stage-3 bosses.
- Recovered explicit V2-only behavior branches in THE SUN, GIGANTIC UFO, and UNKNOWN; UNKNOWN_V2 doubles several internal helper values and invokes the dedicated `setVer2Destroy` defeat action.
- Proved a C-1A/C-1B King Fossil boss-parameter difference: an executable-backed reload/countdown source changes 48→96, while another unresolved parameter changes 6→3.
- Added `mobile-exclusives-info`, a source-only JSON reference command for Survival/Chimera substitutions, terminal endings, and conservative V2 behavior/attack-pool mappings.
- Expanded the dependency-free regression suite to 53 tests.

- Corrected and closed the mobile Level-9 split: iOS `level9_stage1EX..6EX` are the six Chimera crossover stages; Android substitutes V2-based placeholder scripts/maps in those slots.
- Proved iOS DAT opcodes `0x52..0x54` as `KING_FOSSIL`, `TWILIGHT_MIRAGE`, and `APARTHEAD` from the ARMv7 `analyzeScript` jump table and retained constructors.
- Mapped Extra 23..28 / `level8_stage3EX..8EX` to the six DELETION missions and their Stage-3 V2 boss counterparts.
- Reconstructed the full 36-node Survival selection graph, terminal nodes 28..35, eight ending names, and achievement indices 52..59.
- Recorded six conditional Survival stage substitutions while leaving the controlling status-byte meaning unresolved.
- Added exact original/V2 entity-pool diffs plus Chimera boss constructor/helper/attack symbol tables and third-party gameplay-footage provenance.
- Expanded the dependency-free regression suite to 52 tests.

- Added clean-room mobile package research for the supplied iOS 4.1.0 IPA and Android 1.0.4 APK without bundling either package or extracted assets.
- Added `mobile-inventory`, `mobile-compare`, `tzip-extract`, and `mobile-map-info`, plus the dependency-free `siig_mobile.py` helper.
- Proved all 737 supplied mobile DAT files parse with the existing console DAT parser and documented the little-endian mobile MAP header variant across 493 MAP files.
- Matched the iOS and console generator MAP corpora at exactly 330 files / 645 nonempty layers; console cell capacity is exactly 2× while populated content is not simply duplicated.
- Isolated the iOS/Android authored-content split to the six Level-9 DAT/MAP pairs and proved their terminal opcodes 0x4C..0x51 as THE_MOON_V2, THE_SUN_V2, GIGANTIC_UFO_V2, LADYBUG_V2, MANDALA_V2, and UNKNOWN_V2.
- Recovered iOS symbol anchors for `Invinf_LoadScript`, `Invinf_LoadMap`, generator, Survival, map, and representative enemy/boss functions.
- Expanded the dependency-free regression suite to 51 tests.

- Audited the retail post-6200 Ultimate UFO reset path and proved the 6030 state-1 destruction and 6200 `bos_015k` shutdown do not clear camera gate `+0x11C`.
- Located the exact Xbox clear instruction at `0x8212DD20`: it is reached only through part 0/state 0, normally via generic vtable `+0x48` at `0x820FBEE8`.
- Excluded Normal 5-3 DAT cleanup and the generic lifetime watchdog as established ordinary reset triggers, and proved manager removal itself is destructor-only. No ordinary Normal 5-3 post-6200 `+0x48` caller is proven; the normal-ending camera-gate clear therefore remains a runtime-only question rather than an assumed event.
- Bracketed June 10 prototype Ultimate UFO debug-registration removal to ~427.367–427.400 s at the 5-3 completion white-out, while keeping this footage result observational rather than executable proof.

- Added `field-camera` for frame-by-frame procedural eye/target reconstruction from real `fld014` / `fld015` matrix animation plus an explicit camera preset.
- Validated normal-5-3 Ultimate UFO Mframes 5897..6300: all 404 real `fld015` samples are rear-follow under preset 4, including dynamic-X stress cases.
- Modeled the GMX serialized affine → runtime row-vector matrix representation bridge and decoded the retail timed-camera-transition gate used by Ultimate UFO reset.
- Recovered May prototype phase-12 Mframe-6200 direct `UltimateUfo::Vanish` behavior and documented the later ending split.

- Added `pa-route-info` and four machine-readable cross-build PA-route reference tables, using PS3 retail plus Xbox retail/June 10/May 11/May 9 executable evidence.
- Recovered the prototype debug name `Route::SetPaRoute`, proved the retail/June category-0 + state `(4,1)` gate, identified May 11's earlier state-only gate, and documented the missing corresponding May 9 setup branch.
- Proved the known retail setup selects `cam01_op1.gmx`; `cam02_op1.gmx` remains supported by `SetPaRoute` but without a proven retail activation callsite.
- Closed the special-stage reload chain: DAT `WARNING [12]` directly requests Bmap13/fld014 and `WARNING [14]` requests Bmap15/fld015 through executable transition state writes; boss spawn alone is not the trigger.
- Traced the common HP-zero dispatch into Ultimate UFO destruction state, recovered prototype `UltimateUfo::Vanish`, and documented the executable late-phase destruction actions at frames 6030 and 6200.
- May 9 debug HUD evidence now names Ultimate UFO Mframe/Sframe/state plus Umb/Tow/Fan/Ring col/dis status; project-owner footage supplies corroborating gameplay-role labels.
- Corrected dev11: May 9/May 11 runtime ID 0xD9 is bos_015k.gmx, the same late asset moved to ID 0xD8 in June/retail.
- Separated normal 5-3 from DLC Bonus 5-6 and proved the Bonus 5-6 immediate main-body destruction shortcut in both retail Xbox and PS3.
- Proved Ultimate UFO Mframe directly drives fld015.gmx in all five builds and reconstructed cam01 animated-to-procedural PA camera fallback.
- Real late fld015 matrices plus preset 4 produce a stable `(0,-60,+40)` relative eye offset along the late +Y route, classified conservatively as rear-follow geometry.
- Added `camera-preset`, a semantic inspector for the 32 retail camera presets with optional executable-backed dynamic horizontal-response evaluation.
- Resolved camera preset word 0 as perspective FOV degrees, word 1 as uniform scene/view scale, words 2–4 as the camera-eye offset, and words 5–7 as scene/view translation.
- Resolved words 8–10 as dynamic horizontal-response gain plus target/eye local-X response scales using normalized runtime coordinates; gameplay labels remain deliberately unguessed.
- Proved words 12–29 are three renderer fog profiles `{start, end, RGBA}` through `fogRange` and `vFogColor` consumers.
- Traced word 11 as one shared scalar forwarded to `collada_edge1`, `collada_face1`, and `collada_face2`; its virtual-setter meaning remains explicitly unresolved.
- Added `CAMERA_PRESETS_RUNTIME_SEMANTIC.csv` while retaining the untouched raw executable table and structural runtime table.
- Added procedural route orientation and `route-camera-playback`; dev7 corrects matrix-animation playback to the retail 30 Hz logical-frame clock and adds explicit animated camera/field exporters; the current dependency-free regression suite passes 53 tests.
- Added `route-resample`, reproducing the retail PS3 non-loop route segment builder at a user-supplied constant spacing: equal-distance linear subdivision, the exact straight/curve classifier, six-state tangent-axis selection, and cubic Hermite interpolation.
- Added `route-playback`, which applies DAT SCROLL_02 timing to the executable-backed route state machine, including loop wrapping and linear mid-segment spacing rebuilds. WIP160 can deterministically infer `levelW_stageS.dat` for normal `XmapW_S` / `map4_/map5_` route names and cross-checks the stage/script registry. WIP164 additionally validates an explicitly supplied `Bmap13`/`Bmap15` DAT against authored `WARNING[12]`/`WARNING[14]` request frames and reports competing special requests; canonical Bmap ownership and route-object initialization timing remain explicit.
- Added runtime-initialized 32 × 30 camera-preset values plus a structural per-word schema derived from the camera initializer/consumer call chain; ambiguous gameplay labels remain unresolved.
- Added five-build executable-derived runtime entity/primitive registry tables with decoded 0x2C record fields and renderer-group selectors.
- `stage3dmap` exports the exact executable-ordered route-source control points and record-0 origin fallback as CSV/OBJ.
- Added `gmxtrack` for GMX matrix-animation CSV and translation-path OBJ export; validated the four retail route/camera GMXs and all six tracks.
- Validated direct extraction of the original retail Xbox 360 `LIVE` STFS and PS3 type-1 PKG supplied for this project.
- Added optional OpenSSL acceleration for finalized PS3 PKG AES-CTR with a dependency-free Python fallback and equivalence tests.
- Added internal authenticated decryption of SIIG's six NPDRM SDAT resources; TrueAncestor-style `.bin.gz.dat` files remain optional fallback inputs only.
- Added built-in Sony 989SND/SCREAM SBlk v3 parsing and PS-ADPCM WAV export for all 84 retail PS3 sound streams.
- Stage Explorer v8 is explicitly a **proof-of-concept research inspector**. Exact decoded MAP layers/DAT records are foregrounded; SCROLL_01/02/03 motion and Stage 4/5 route cameras remain experimental previews and are not described as faithful gameplay playback. Boss/background observations remain provenance-separated.
- Added content-addressed outer-package caching for `--resume`, avoiding repeated STFS/PKG/ZIP unpacking when the input hash is unchanged.
- Fixed the STFS `CON` first-hash-table initialization path and added a regression fixture.
- Integrated PS3 EBOOT-backed 3D placement, route-point, scroll, and timing corrections into the current source tree.

The linked-data Asset Viewer now includes full-tree folder navigation and hides converted glTF cards that duplicate a native GMX interactive preview by default; duplicates remain indexed and can be shown explicitly. This remains a development build while automatic PA-route activation timing, the word-11 material scalar, shader ISA work, and Blender runtime validation remain open. The project license decision is now recorded as The Unlicense, subject to source provenance and third-party license boundaries.

## Release folder layout

```text
SIIG_Asset_Toolkit_v2.8.0-dev26/
├── siig_toolkit.py and companion modules
├── SIIG_*.bat launchers
├── docs/          guides, format research, project records, release history
├── reference/     tables, provenance, samples, system-font support data
├── validation/    machine-readable validation reports
├── tools/         optional Ghidra helper
├── addons/        Blender add-on package and source
└── LICENSES/      required third-party notices
```

Use [`docs/README.md`](docs/README.md) as the central index.

## Requirements

- Python **3.10 or newer**.
- No third-party Python packages are required.
- FFmpeg is optional and only needed to decode Xbox 360 XMA2 streams to PCM WAV. Without FFmpeg, the toolkit still writes RIFF-wrapped `.xma` files and manifests.
- PS3 SIIG's six inner NPDRM SDAT resources are decrypted and authenticated internally. Matching `*.bin.gz.dat` files may still be supplied as a fallback for unsupported variants.

## Recommended first run

From Command Prompt or PowerShell in the toolkit folder:

```bat
python siig_toolkit.py --version
python siig_toolkit.py selftest
python siig_toolkit.py doctor "C:\path\to\game-package"
```

On Windows, `py -3` may be used instead of `python`.

## One-click full-game extraction

Drag an Xbox 360 STFS package, PS3 PKG, extracted game ZIP, or extracted game folder onto `SIIG_Rip_Game.bat`.

Command-line equivalent:

```bat
python siig_toolkit.py rip-game "C:\path\to\game-package" -o "C:\path\to\SIIG_Ripped" --resume
```

PS3 requires no external SDAT step for the supplied retail package:

```bat
python siig_toolkit.py rip-game "C:\Games\SIIG.pkg" -o "C:\Rips\SIIG_PS3" --resume
```

`--ps3-sdat-dir` remains available only as a fallback for pre-decrypted `.bin.gz.dat` payloads. `--rap` accepts a 16-byte RAP for workflow compatibility, but SIIG's six supplied SDAT resources do not require RAP-derived keys.

See `docs/guides/FULL_GAME_RIP.md` and `docs/guides/CONTAINER_INPUT_NOTES.md`. For native editing/rebuild workflows, see `docs/guides/NATIVE_ASSET_ROUNDTRIP.md`.

## Verify a completed rip

```bat
python siig_toolkit.py verify-output "C:\path\to\SIIG_Ripped"
```

Or drag the output folder onto `SIIG_Verify_Rip.bat`. Full verification checks report consistency, privacy, file sizes, SHA-256 hashes, and leftover partial files. Use `--quick` to omit hashing.

## Main capabilities

### Package and archive extraction

- Header-based Xbox 360 STFS detection: `CON `, `LIVE`, and `PIRS`.
- PlayStation 3 type-1 PKG extraction for finalized and non-finalized/debug packages.
- ZIP and extracted-directory inputs.
- BBX extraction for `01 42 42 58` containers, including unnamed resources, nested BBX archives, gzip wrappers, filename hierarchy, exact filename-hash verification, and CSV/JSON manifests.
- Configurable extraction limits and atomic writes.

### Repacking and modding research

- Rebuild edited TEX, DAT, MAP, ANM, COL, and system-font resources back to native game formats before BBX repacking.
- `asset-capabilities` reports which extracted families are viewable, editable, native-buildable, or still one-way.
- Rebuild extracted BBX directories from their manifests with canonical mode/hash/index/name/payload layout.
- Preserve unnamed resource identifiers and reserved header bytes.
- Recompute named hashes by default or preserve deliberate mismatches.
- Verify every output immediately and write a detailed repack report.
- Produce deterministic gzip-wrapped archives when requested.

### Asset browsing and Blender

- Generate a searchable offline asset browser with a small HTML shell and local linked payloads.
- Inspect images, browser-playable audio, text/CSV/JSON, hashes, GMX/glTF/OBJ structure, and interactive wireframes.
- Browse paginated cards with lazy thumbnails for converted and raw SIIG asset formats.
- Import GMX files into Blender 3.6+ with the bundled add-on, using the same exporter as the CLI.
- Serve an output directory on localhost when browsers restrict direct file access.

### Models and textures

- GMX → glTF 2.0 with indexed triangles/lines, positions, normals, UVs, vertex colors, hierarchy, rigid attachment, materials, textures, and transform animation.
- GMX → OBJ as a lightweight static-geometry option.
- Xbox 360 tiled TEX ↔ PNG using the original TEX as a rebuild template, preserving Xenos layout/padding/header fields.
- PS3 RSX-wrapped linear A8R8G8B8 TEX ↔ PNG using the original wrapper as a rebuild template.
- System-font XOR deobfuscation, 2048×3392 atlas export, native CRP pixel rebuild, 6,732-record glyph table, and AngelCode BMFont descriptor.

### Audio and localization

- Xbox 360 XACT3 XWB/XSB extraction, cue naming, XMA2 RIFF wrapping, and optional FFmpeg WAV decoding.
- Lossless preservation of ready-to-use WMA/AT3 media.
- PS3 Sony 989SND/SCREAM SBlk v3 parsing, stream naming, PS-ADPCM decoding, and built-in PCM WAV export; `sblk-replace` accepts arbitrary-duration/rate PCM16 WAV input, downmixes multichannel input to SIIG's native mono stream form, repacks stream payloads/offsets, and regenerates loop/end control flags.
- `text.bin` and `message.bin` localization export to UTF-8 CSV, JSON, corrected scripts, raw scripts, and per-language text.

### Structured gameplay data

- DAT command streams to timed semantic CSV/JSON with absolute frames, executable-derived opcode names, confidence labels, lossless raw words, and CSV/JSON → native DAT rebuilding.
- MAP parsing for all three independently sized tile/sprite layers, plus lossless editable JSON → native MAP rebuilding.
- Categorical, grayscale, and verified atlas-backed MAP PNG output.
- Offline Stage Explorer v8 **proof of concept** with runtime stage pairing, embedded atlases, exact MAP layer inspection, DAT timeline filtering, and clearly labeled experimental SCROLL/3D route previews. It is not a faithful or frame-accurate gameplay map viewer.
- Linked-data Asset Viewer **2.2.0** with full `SIIG_Ripped` folder navigation, breadcrumbs/recursive scope, deferred previews, default suppression of converted glTF cards already represented by a native-GMX interactive preview, and searchable project-owner friendly model identities with explicit speculative labels where confidence is limited.
- COL one-bit collision masks ↔ PNG using an original-header template.
- ANM model/group clip ranges ↔ CSV/JSON, including native rebuild of start/end frames and loop behavior.
- Bmap/Xmap/map4/map5 3D path and GMX-placement tables to JSON/CSV/OBJ, including exact runtime route-source control points.
- Wall/Xwall repeat strips and `stage_generate.bin` candidate tables to JSON/CSV.
- Xenos compiled-shader headers, metadata strings, hashes, and raw microcode extraction.

### Research support

- `scan` for JSON descriptions of known formats.
- `tools/ghidra/ApplySIIGFunctionNames.java` for optional confirmed Ghidra labels.
- `gmxtrack` for decomposed GMX animation matrices and translation trajectories.
- Machine-readable validation tables and format notes, including the five-build runtime entity registry, raw/runtime-initialized camera presets, and route-resampler evidence.
- Privacy sanitizer for older JSON metadata.
- Source, license, attribution, and AI-assistance records.

## Common commands

### Inspect the environment and input

```bat
python siig_toolkit.py doctor "C:\path\to\input"
```

### Extract only the outer STFS/PKG container

```bat
python siig_toolkit.py unpack-container "C:\path\to\package" -o outer_files --clean
```

### Extract a BBX archive

```bat
python siig_toolkit.py extract player.bin -o extracted --convert-gltf --convert-tex
```

### Recursively extract a directory of BBX archives

```bat
python siig_toolkit.py extract game_bins -o extracted --recursive --convert-gltf --convert-tex
```

### Build or rebuild the Stage Explorer proof of concept

```bat
python siig_toolkit.py stageviz "C:\path\to\SIIG_Ripped" -o stage_explorer
```

Open `stage_explorer\SIIG_Stage_Explorer.html`. The file is self-contained and makes no network requests.

### Render a MAP with a verified atlas

```bat
python siig_toolkit.py map2png level1_stage1.map -o map_preview ^
  --atlas fence1_512.png --atlas-step 30 --csv
```

Without `--atlas`, the command writes exact categorical or grayscale cell visualizations.

### Repack an extracted BBX

```bat
python siig_toolkit.py extract map.bin -o work
python siig_toolkit.py repack-bbx work\map -o map_repacked.bin
```

The second command reads `work\map\manifest.json`, writes atomically, verifies the new archive, and creates a `.repack.json` report. See `docs/guides/BBX_REPACK_NOTES.md` before modifying game data.

### Build and open the asset viewer

```bat
python siig_toolkit.py asset-viewer "C:\path\to\SIIG_Ripped" -o viewer
python siig_toolkit.py serve viewer
```

The server binds only to `127.0.0.1`. Keep `SIIG_Asset_Viewer.html` beside its generated `viewer_assets` directory; the viewer is intentionally no longer one giant self-contained file.

### Install the Blender add-on

Install `addons/SIIG_Blender_Addon_v0.4.0.zip` through Blender's Add-ons preferences. Raw GMX now defaults to **Solid only** for editing; preserved native `_E` outline objects in assembled imports are hidden non-destructively by default and can be shown again from the SIIG sidebar. The optional white-outline/scanline Style Preview is opt-in, and its compositor integration supports Blender 3.6/4.x plus the Blender 5 node-group API. See `docs/guides/BLENDER_ADDON_NOTES.md`.

### Decode 3D stage paths and placements

```bat
python siig_toolkit.py stage3dmap extracted\stage -o stage3d
```

### Export GMX animation tracks

```bat
python siig_toolkit.py gmxtrack extracted\route -o gmx_tracks
```

This writes one decomposed CSV and translation-path OBJ per supported ANIM track. ANIM timestamps are exported as seconds; the observed sample rate is derived from the data.

### Resample or play a 3D route

```bat
python siig_toolkit.py route-resample extracted\stage\Xmap3_1.bin -o route_fixed --spacing 100
python siig_toolkit.py route-playback extracted\stage\Xmap3_1.bin -o route_runtime --frame-multiplier 2
```

`route-resample` is the deterministic fixed-spacing analysis path. `route-playback` applies SCROLL_02 timing from the DAT to the executable-backed route runtime. For normal `XmapW_S` and `map4_/map5_` names, omitting the DAT (or passing `auto`) deterministically resolves `levelW_stageS.dat` from the nearby `script` layout and cross-checks the recovered stage/script registry. Explicit DAT paths still work. `Bmap` ownership and route-object activation are not guessed; use an explicit DAT plus `--start-frame`/`--loop` only when supported by the case being investigated.

### Decode wall strips and generator candidates

```bat
python siig_toolkit.py stagewall extracted\stage -o stagewall
```

### Inventory Xbox 360 compiled shaders

```bat
python siig_toolkit.py shader-info extracted\shader -o shader_metadata
```

### Decode localization

```bat
python siig_toolkit.py text2csv "C:\path\to\Media" -o localization
```

### Decode audio

```bat
python siig_toolkit.py xact2wav sound.bin -o audio
```

### Decode the system font

```bat
python siig_toolkit.py font2png systemfont.bin -o systemfont_decoded
```

### Optional derived desktop/web font experiment

The toolkit ships only the generator code, not generated fonts. With Pillow and fontTools installed, `tools/systemfont_derived_font.py` can convert `systemfont_atlas.png` + `systemfont_glyphs.csv` into local-use TTF/OTF/WOFF/WOFF2 bitmap-outline derivatives. These are convenience fonts traced from the 32 px game atlas, **not** recovered original vector font files. All recovered alias scales are now executable-backed: ASCII aliases (letters, digits, space and punctuation) use 0.5 runtime scale, while halfwidth-katakana aliases use native 1.0 scale. Generated fonts embed game glyph artwork and should not be redistributed without the necessary rights.

```bat
python tools\systemfont_derived_font.py --atlas systemfont_decoded\systemfont_atlas.png --glyphs reference\systemfont\systemfont_glyphs.csv --output derived_font
```

### Convert extracted models

```bat
python siig_toolkit.py gmx2gltf extracted -o gltf
python siig_toolkit.py gmx2obj extracted -o obj
```

### Run the built-in regression suite

```bat
python siig_toolkit.py selftest
```

## Typical full-rip output

```text
SIIG_Ripped\
├── assets\                  extracted resources and direct conversions
├── decompressed_bbx\        normalized BBX archives
├── audio\                   audio manifests and converted streams
├── localization\            combined UTF-8 exports
├── ready_files\             directly usable media copied unchanged
├── stage_explorer\
│   ├── SIIG_Stage_Explorer.html
│   ├── STAGE_MANIFEST.json
│   └── README.txt
├── asset_viewer\
│   ├── SIIG_Asset_Viewer.html
│   └── ASSET_VIEWER_REPORT.json
├── structured\
│   ├── dat\                  timed DAT CSV/JSON
│   └── map\                  MAP layers, metadata, and optional atlas renders
├── systemfont\              decoded atlas and glyph data
└── validation\
    ├── RIP_REPORT.json
    ├── RIP_REPORT.txt
    ├── OUTPUT_MANIFEST.json
    └── OUTPUT_MANIFEST.sha256
```

Output varies by platform and available source assets.

## Safety and reproducibility

The toolkit treats input packages as untrusted. Outer-container extraction is bounded by file-count, per-file, total-byte, and ZIP-ratio limits. Paths are normalized, traversal and symlink entries are rejected, collisions are detected case-insensitively, writes are atomic, gzip output is bounded, and nested BBX extraction has depth and entry budgets.

Defaults are intentionally generous for SIIG but can be lowered:

```bat
python siig_toolkit.py rip-game game.zip -o SIIG_Ripped ^
  --max-files 10000 --max-total-bytes 8589934592 ^
  --max-file-bytes 2147483648 --max-zip-ratio 200
```

See `docs/guides/SECURITY_NOTES.md`. Keep original packages read-only and verify output before archiving or sharing research results. Repacking never changes the extraction directory, but modified archives must be tested only on copies; it does not update outer-package metadata or executable references.

## Accuracy boundaries

Confirmed facts are separated from unresolved semantics. The living dev24 source of truth is `reference/research/DEV24_UNRESOLVED_BOUNDARY_AUDIT.md`; the generator runtime-capacity closure is documented in `reference/research/CONSOLE_GENERATOR_OUTPUT_CAPACITY_DEV24.md`; older versioned reports retain their period-correct wording and are not automatically current. In particular:

- MAP cells are confirmed 2D tile/sprite data, not 3D wall placements.
- MAP atlas mapping and flip behavior are confirmed. SCROLL_01/02/03 are confirmed as layer 0/1/2 X/Y velocity setters; player-facing names for those layers remain unresolved.
- Stage Explorer v8 is deliberately labeled **proof of concept**. Its experimental SCROLL panel integrates the confirmed vectors at the logical 30 Hz authoring timebase, but it does not execute the complete stage DAT or reproduce native camera/render timing. Route cameras and gameplay-reference backgrounds are inspection aids only; owner-observed boss visuals stay separate from DAT-backed encounter names/frames.
- The 3D stage path, placement, and wall-strip tables are decoded, including the native placement transform `S × Rz × Rx × Ry × T`; Stage Explorer applies it to GMX AABB wire proxies. The non-loop route resampler/runtime playback plus camera helpers are separately recovered. Normal `XmapW_S` / `map4_/map5_` DAT filename pairing is deterministic; boss/special `Bmap` ownership, exact route-object activation timing, collision, and unmodeled 3D-control side effects remain bounded where evidence is absent.
- Direct STFS/PKG readers have synthetic boundary tests and have been validated against the supplied original retail Xbox 360 LIVE package and PS3 type-1 PKG.

## Ethics, licenses, and redistribution

- Do not redistribute game packages, binaries, extracted textures/audio/models, or self-contained explorers containing embedded game atlases without permission.
- The source-only toolkit release contains no game assets.
- External tools such as FFmpeg, Ghidra, XEXLoaderWV, vgmstream, and TrueAncestor are not bundled.
- OpenAI ChatGPT assistance is disclosed in `docs/project/AI_DISCLOSURE.md`.
- Explicit sources and adaptations are recorded in `reference/provenance/SOURCES.csv`, `reference/provenance/PROVENANCE.json`, `docs/project/SOURCE_AUDIT.md`, and `docs/project/THIRD_PARTY_NOTICES.md`.
- TCRF/the Cutting Room Floor was not used and is an explicitly excluded research source; see `docs/project/SOURCE_EXCLUSIONS.md`.
- Original project-authored code and documentation are dedicated under The Unlicense only to the extent the project maintainer has the legal right to do so. See `UNLICENSE`, `LICENSES/PROJECT-LICENSING.md`, and `docs/project/PROJECT_LICENSE_STATUS.md`.

### Development note: 2.8.0-dev14

Retail Mframe 6030 uses part state 1 and Mframe 6200 only disables the owned `bos_015k` object. Neither action clears camera-controller `+0x11C`. The proven clear is conditional on a later part-0/state-0 reset through vtable `+0x48`; a destructor-only manager removal is not equivalent. See `docs/research/ULTIMATE_UFO_FINAL_RESET_DEV14.md` and `reference/tables/ULTIMATE_UFO_FINAL_RESET_AUDIT.csv`.

### Development note: 2.8.0-dev13

`field-camera` reconstructs the executable-backed procedural camera for an explicit field GMX/preset/frame range. It does not guess preset activation or player coordinates; optional runtime X/Y values apply the proven dynamic horizontal response. The supplied retail `fld015` validates all 404 frames 5897..6300 as rear-follow under preset 4.

Example:

```bash
python siig_toolkit.py field-camera fld015.gmx --preset 4 --start-frame 5897 --end-frame 6300 -o ufo_late.csv
```

### Development note: 2.8.0-dev12
Dev12 supersedes dev11's prototype registry interpretation: the late owned GMX is `bos_015k.gmx` in May as well as June/retail; only the runtime type shifts from May `0xD9` to later `0xD8`. Normal 5-3 and Bonus 5-6 destruction policies are now separated, and late preset-4 + `fld015` is classified as rear-follow geometry with explicit remaining camera-writer caveats.


Dev17 adds locally authored Survival Evolution-gating, V2 attack-pool/behavior, and Chimera A/B tables/helpers derived from the retained user-supplied iOS executable/resources. It does not add or redistribute game binaries/assets. Existing third-party gameplay videos remain observational corroboration only; no footage is bundled.


### THE SUN assembly presets (dev19)

See `docs/research/THE_SUN_RUNTIME_ASSEMBLY_2.10.0-dev19.md`.

### All-boss matrix (dev20)

`boss-matrix` reports all 18 console boss families in one evidence-grade-aware view. Current dev24 coverage is 14 deep runtime reconstructions, 3 exact gameplay-pose reconstructions (OCTOPUS, WATER STRIDER, NO_NAME), and 1 native-inspection-only family (THE MOON). Supply `--root` with an extracted GMX folder to validate all root models from fresh bytes. THE MOON additionally exposes `controller_runtime_sampler = the-moon-controller`; the sampler reproduces its exact retail 36-degree-step rotation, material-alpha fade, and visual-resource transition without inventing a node mapping.


## dev22 additions

Simple-mode GMX Workbench now includes a compact Boss Assembler covering all 18 main-game boss families in the project-owner order. Choose the extracted boss-model folder once and the assembly-output folder once, then switch boss/variant from two compact selectors; exports and manifests use deterministic filenames in that output folder instead of reopening model/output navigation for every boss. The 5-6 boss is shown as NAMELESS while the established internal/runtime family remains `NO_NAME`. The exhaustive specialist controls remain available in Advanced mode.

The same remembered model/output folders are shared with the **Enemy / Sub-boss GMX Assembler**, which now exposes eight evidence-backed families: ENVY, GREED, WRATH, KEEPER, OPPRESSOR, GLUTTONY, VANITY and TELEPORTER. The six originally requested console families are explicitly audited in `reference/research/ENEMY_SUBBOSS_WORKBENCH_AUDIT_DEV24.md`; dynamic families keep live/RNG/player-dependent transforms unbaked instead of inventing canonical poses.

Both compact assemblers include **Assemble + preview**. This writes the deterministic glTF, regenerates the local Asset Viewer for the shared assembly-output folder, and opens its browser model/wireframe preview. Advanced one-click boss assembly actions also reuse the remembered folders and deterministic catalog filenames, so changing family no longer forces repeated folder and Save As navigation.

Game Rip keeps the full per-resource task log and additionally summarizes the live stream as a current phase plus running extracted-asset, glTF, PNG and error counters. This makes long one-click rips readable without hiding low-level extraction/conversion messages.

**dev23:** the same remembered-folder workflow added a separate **Enemy / Sub-boss GMX Assembler** for the project-owner identifications ENVY (`emy_045`), KEEPER (`emy_032`), OPPRESSOR (`emy_043`), GLUTTONY (`emy_050`), VANITY (`sbs_002`), and TELEPORTER (`sbs_003`). KEEPER, OPPRESSOR and GLUTTONY use recovered locator/allocation hierarchies; ENVY exposes an explicitly labelled six-piece zig-zag preview using the recovered alternating ±30° controller rule and 10-unit member spacing. See `reference/research/CONSOLE_ENEMY_SUBBOSS_ASSEMBLY_DEV23.md`.


**dev24 WIP182 `est_020` / `est_021` bomb lifecycle:** project-owner gameplay/model comparison identifies `est_020.gmx` as the shared OCTOPUS / GLUTTONY bomb before detonation and `est_021.gmx` as its resulting explosion. GLUTTONY's retained executable strings independently confirm a dedicated `DischargeBomb` path asserting the `SG_BOMB` 3D enemy-shot type. The exact per-file executable binding and OCTOPUS shot-type trace remain explicit boundaries; the friendly model identities are not presented as recovered source names. See `reference/research/EST_020_021_BOMB_LIFECYCLE_DEV24.md`.

**dev24 WIP:** VANITY and TELEPORTER now have stronger retail-runtime forms. VANITY has an exact main-game arrival formation (primary X=213/Z=32 with B1 helpers at X=139/287) plus a primary-only state-2 local-Y action from 0 to −100; state-2 X/Z/helper behavior is still deliberately left live/dynamic. TELEPORTER has exact Stage 5-4 left/right non-looping state 0→4 actions reconstructed from `Function_821AE858` / `Function_82235D50` / `Function_8210B888`: 114 samples at 30 Hz with a 14-sample state-2 transfer burst. The earlier dev24 WIP "tick 152" interpretation was disproven by raw PPC and removed. See `reference/research/VANITY_TELEPORTER_RUNTIME_DEV24.md`.

**dev24 ENVY/GREED ownership repair:** retail `Function_821489F8` switches on `runtime_type + 1`. Runtime `0x98` / `emy_045.gmx` therefore selects switch case `0x99` and `Function_82102898`, whose executable-backed ENVY geometry is the 10-unit chain with alternating ±2-unit perpendicular offsets and -30°/+30° member yaw. Runtime `0x99` / `emy_046.gmx` selects case `0x9A` and `Function_82103C58` (GREED). GREED now exposes exact Level 4-1 spawn and first-hover-entry anchors plus target/timer/exit/spin semantics without inventing the live state-1 oscillator. See `reference/research/ENVY_RUNTIME_CORRECTION_DEV24.md` and `reference/research/GREED_RUNTIME_DEV24.md`.

**dev24 WRATH:** runtime `0x9B` maps through the same `runtime_type + 1` factory to `Function_8210CFE8` (not neighboring `Function_82106378`). The Workbench exports the exact Level 4-4 55-sample state-0 body approach from `(213,-500,280)` to `(213,0,80)` at 60 Hz and retains live state-1 player tracking / auxiliary visibility as metadata. See `reference/research/WRATH_RUNTIME_DEV24.md`.
**dev24 LINE_INVADER:** runtime `0x9A` is now classified as a procedural polyline entity controlled by `Function_82106378`, not a missing GMX family. The DAT decoder exposes its 1..10 X/Z path points, resource mode, active-member count and 30 Hz spawn interval. The extracted retail model corpus has no `emy_047.gmx`/`emy_048.gmx`, so the Workbench deliberately does not invent one. See `reference/research/LINE_INVADER_RUNTIME_DEV24.md`.
**dev24 GLUTTONY DAT:** retail runtime `0x9C` now has a complete 25-word high-confidence schema: root/body HP, raw/512 route speed, up to ten authored X/Z route points, point count, and the shared HP value for the two `emy_050a` helpers. All seven retail records are decoded and regression-covered; repeated authored points are preserved. See `reference/research/GLUTTONY_DAT_RUNTIME_DEV24.md`.
**dev24 `est_*` effect-model audit:** WIP180 established geometry/registry structure for `est_011` through `est_021`; WIP181 resolves `est_012` as a project-owner-confirmed **shared interactive target cube**. JOLYNE directly loads it after creating ten orthogonal-line helpers, and UNKNOWN's visual controller independently loads it while provisioning up to 120 helpers; both relationships repeat in the May 11 lineage using shifted runtime `0xE7`. Runtime slot remains `0xE6` in retail/June10/PS3 and `0xE7` in May prototypes. `est_011`/`est_014` still share byte-identical geometry, `est_013` is PROGRESSIVE UFO missiles, and `est_015` is WATER STRIDER trail spikes; the remaining `est_*` identities stay unresolved/speculative. See `reference/research/EST_EFFECT_MODEL_AUDIT_DEV24.md` and `reference/research/EST_012_TARGET_CUBE_DEV24.md`.

**dev24 LUST / runtime 0x9D / `emy_051`:** the project-owner catalog resolves the player-facing identity as **LUST**, while ownership is independently fixed to runtime+1 case `0x9E` -> `Function_82106F78` across the retained runtime registry. Its DAT-tail vtable slot is a no-op and all 80 recovered retail records use exactly five common fields: spawn condition, body HP, raw/512 speed, X and Z. No executable-internal `LUST` script/debug string is claimed; the friendly name remains explicitly project-owner provenance. See `reference/research/UNKNOWN_009D_EMY051_RUNTIME_DEV24.md` and `reference/research/ENTITY_MODEL_IDENTITIES_DEV24.md`.
**dev24 boss/enemy DAT block 0xA2–0xAB:** the Stage Explorer semantic layer now decodes the full contiguous retail boss block with executable-backed fields rather than generic `param_N` tails. June 10 retained labels recover PROGRESSIVE_UFO `middle_hp/small_hp`, BUTTERFLY part HP/discharge times, AXON shot/hold timing + bit HP, WATER_STRIDER twin-beam/shock-wave intervals, CRAB fannel/pot HP/timing, ULTIMATE_UFO component HP/discharge timing, SQUID shot intervals, VERTEBRATE's 16-entry selector/type map + five HP/limit pairs, and NO_NAME's exact target X/Z. OCTOPUS remains deliberately five-field because no authored record contains the class callback's boundary-read short. See `reference/research/BOSS_DAT_RUNTIME_A2_AB_DEV24.md`.


**dev23 visual-pass rule:** Solid/Outline/Combined only filter a GMX when the exporter detects a genuine solid+outline pair. Ordinary single-pass models export unchanged even if a global rip/workbench pass preference is set. The output metadata records the requested mode separately from the effective mode.

**dev24 Visualizer runtime pipeline:** the offline simulator now combines the recovered June 10 X/Y/VolumeSet Check Mode surface with the executable-backed renderer: 1280×720 ping-pong feedback targets, ten 128×128 SHAPE sources, exact Position Fix anchors, SHAPE-first rendering, source-only accumulated/fixed rotation, and scale/alpha-only recursive feedback around the same anchor. External 49-row ParameterSet / 57-row SequenceSet loading and decoded `VL_SEQUENCESET` quick presets remain supported without bundling proprietary rows. Real SHAPE pixels are consumed locally from a user rip when available. Both the recursive feedback texture and the independently serialized retail SHAPE TEX resources are Xenos-exact for repeat addressing with point min/mag/mip filtering and anisotropy disabled. The ordinary `ScreenSpritePS` SHAPE path is also closed: sampled RGBA is multiplied by the runtime float4 tint and source-over blended with SrcAlpha/OneMinusSrcAlpha. EffectBlur sample/color and RGB blend semantics are independently recovered; the remaining browser boundary is exact Xenos render-target alpha storage plus host audio analysis-window timing. See `reference/research/VISUALIZER_RUNTIME_RENDER_PIPELINE_DEV24.md`, `reference/research/VISUALIZER_XENOS_SAMPLER_DEV24.md`, and `reference/research/VISUALIZER_SHAPE_SAMPLER_DEV24.md` (with historical dev23 controls in `docs/research/VISUALIZER_SIMULATOR_DEV23.md`).

**dev23 Blender visibility:** Blender add-on 0.2.0 imports toolkit assembly glTF/GLB files and groups each logical `siigAssemblyModel` master into a `SIIG_PART_*` collection. This fixes the apparent no-op eye toggle caused by overlapping native `_F` solid and `_E` outline objects without merging or rewriting those passes.

**dev23 PROGRESSIVE UFO correction:** `progressive_ufo_classic` now uses the retail C3 side signs literally (+Z rotation at X=+115, -Z rotation at X=-115), removing a dev16 presentation override that reversed both barriers. The native `bos_009b` internal bind tilt is preserved.

**dev23 Game Rip progress:** the desktop GUI now consumes the CLI output queue in bounded repaint batches and shows the newest live rip message in a dedicated Game Rip progress panel. This fixes the apparent frozen/no-progress log that could occur while per-resource output was arriving continuously.

**dev23 one-click nested package path:** after bounded outer-ZIP extraction, Game Rip now content-detects a single extensionless Xbox LIVE/CON/PIRS STFS payload or PS3 PKG and continues into it automatically. Ambiguous ZIPs containing more than one candidate are rejected instead of guessed. A fresh original Xbox retail ZIP completed the full ZIP -> STFS -> game -> BBX pipeline with 23/23 archives, 2,593 resources and 0 extraction errors; `verify-output` then checked 16,540 hashes successfully.

The Stage Explorer proof of concept fits MAP previews to their panels by default, keeps the all-layer overlay optional, and exposes a separate experimental 3D route/placement layout for main level 4/5 stage tables. When the corresponding extracted GMXs are available, it uses their proven root AABBs plus recovered runtime scale and the native `S × Rz × Rx × Ry × T` placement transform to draw clickable oriented wire proxies. `visualizer-sim` builds a self-contained offline Visualizer simulator from footage-backed controls plus the recovered executable render pipeline and, when pointed at a full rip, exact decoded `VL_*` DAT timelines and ParameterSet/SequenceSet rows. Check Mode uses the raw BGM peak mean; stage timeline playback uses the recovered adaptive `VOL SCALE` normalizer and authored `VL_VOLUME_SCALE` window. Proprietary SHAPE pixels are represented by labeled procedural stand-ins rather than being bundled.


The dev22 five-boss primary-controller audit now distinguishes conservative representation from missing research: THE MOON, LADYBUG, OCTOPUS, WATER STRIDER, and NAMELESS/`NO_NAME` each expose a machine-readable controller research grade, positive finding, promotion gate, and evidence-function list through `boss-matrix`. No static multipart scene is promoted unless membership, transform/attachment, and state/time behavior are all backed by native or executable evidence.