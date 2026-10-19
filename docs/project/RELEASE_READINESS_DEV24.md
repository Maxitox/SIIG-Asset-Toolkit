# Dev24 release-readiness audit


### WIP197 current checkpoint

- GUI 0.56.0-dev24 retains the WIP197 help/scroll fixes and adds the Atlas Inspector utility; GUI 0.55.0-dev24 fixed content-driven contextual-help resizing in Utilities/global help and stale GMX Workbench scrolling after Advanced → Simple mode changes.
- Visualizer dataset v24 caches unchanged browser BGM previews and native-quantum peak envelopes; unchanged tracks avoid repeat FFmpeg decode work. Browser catch-up simulation now samples the audio envelope at each logical 60 Hz step instead of repeating one requestAnimationFrame meter value.
- June 10 `Function_82177DF0` independently resolves the global Visualizer position bridge as X/640 and Y/360 on the 1280×720 target. WIP191's 1.5× interpretation remains historical/superseded; remaining owner-perceived position differences are an explicit capture/pivot/presentation comparison boundary, not grounds for another guessed multiplier.
- `text_strings.tsv` is the Mod Workspace canonical `text.bin` edit surface; legacy CSV/JSON remain accepted.
- Xbox Mod Workspace deployment is package-editor-neutral: `build/xbox360_replacements/` plus `XBOX360_REPLACEMENTS.json`; Velocity/Horizon/Le Fluffie are examples only.

This is a **WIP readiness audit**, not a sealed release decision. Sealed v2.10.0-dev23 remains immutable.

## WIP196 Blender / Mod Workspace deployment corrections

- Blender add-on 0.4.0 defaults raw imports to Solid only, hides preserved native `_E` objects after assembly import without deleting them, and keeps the Style Preview opt-in. The compositor path branches between legacy `Scene.node_tree` and Blender 5 `Scene.compositing_node_group` / Group Output.
- Xbox Mod Workspace builds now emit complete `build/xbox360_replacements/` containers plus `XBOX360_REPLACEMENTS.json` for explicit manual replacement inside a copy of the STFS package using any compatible Xbox 360 package editor. `.siigmod` remains an optional baseline-dependent sharing delta.
- GUI 0.54.0-dev24 introduced Build replacement files → Verify build → Open Xbox replacements, reports background-command failures visibly, and confirms the exact path of successful optional `.siigmod` saves. WIP197 advances the GUI to 0.55.0-dev24 with the help/scroll fixes above.

## WIP195 Visualizer / desktop regression corrections

- Visualizer dataset v23 restores direct target-pixel Position mapping after retail stage 4-5 proved WIP191's 1.5× multiplier could move the complete PARAM_7 source off-target and collapse feedback into BG-color gradients. WIP191's viewport UI and display-only smooth resolve remain.
- Global **What does this do?** help is now an always-visible strip above the Notebook. The general task log is a separate on-demand window, so help visibility no longer competes with Game Rip console height.
- Live Tk/X checks at 1120×780 and 1744×868 confirm populated Mod Workspace help and a readable Game Rip console.

## WIP193 compact desktop layout

- Game Rip reserves a readable console floor while compacting drag/drop, cache, action and progress controls; WIP192 cache functionality and warning behavior are unchanged.
- GMX Workbench Simple mode uses one-row core actions, shared assembly paths, Boss/Enemy nested assembler tabs and conditional CENTIPEDE-only overrides. Advanced import switches use two columns.
- A real Tk/X smoke run at the default 1120×780 geometry confirmed the Game Rip console remains multi-line and the complete GMX Simple workflow fits without initial scrolling.

## WIP192 source-package-cache UX

- Game Rip now exposes the persistent outer-container source cache, its size/status, a remembered keep-cache switch, and a warning-protected clear action.
- Clearing affects only the sidecar cache and never the verified rip or Mod Workspace. Disabling caching forwards the existing `--no-outer-cache` CLI contract.
- Confirmation text explicitly warns that subsequent resume/full-rip work may need to unpack the original source package again.

## WIP191 Visualizer UI/runtime overhaul

Visualizer dataset **v22** keeps the recovered point-filtered ping-pong recurrence intact while replacing the old scrolling HTML with a viewport-first June 10-inspired control overlay, an always-visible Stage/boss selector, immediate preset application/reset, fullscreen (`F`) and menu hide/show (`M`). WIP191 historically applied a **1.5× logical-to-target position scale**; WIP195 supersedes that scale inference after stage 4-5 demonstrated complete source loss for PARAM_7. The current bridge is direct target-pixel mapping. A display-only 640×360 high-quality resolve softens host-visible point-sampled blocks without entering the recursive feedback loop; Raw RGB remains available. WIP197 subsequently located the upstream June 10 scale call in `Function_82177DF0`, independently confirming X/640 and Y/360 for the 1280×720 target. Pivot/transform presentation and the bit-exact final Xenos composite remain bounded.

## Current consistency gates

- Toolkit version: `2.10.0-dev24`.
- Desktop GUI: `0.56.0-dev24`.
- Boss matrix: 18 total = 14 deep runtime + 3 exact gameplay-pose + 1 native-inspection-only.
- THE MOON is the sole native-only boss and exposes the exact `the-moon-controller` sampler without fake node scaling.
- Root `RELEASE_MANIFEST.json` is regenerated from the current source tree and checked by selftest; the current dev24 WIP199 readiness tree contains **779** root-manifest-tracked source files (the manifest excludes itself).
- Built-in regression gate: **175/175 passed** on the finalized working tree; the checkpoint builder must repeat this from a fresh extracted package before the WIP is accepted.
- `reference/provenance/PROVENANCE.json`, `SOURCES.csv`, Credits, third-party notices and AI disclosure are current-facing.
- TrueAncestor EDAT Rebuilder is represented explicitly as a historical external fallback; it is not bundled and no code is copied.
- Source-only packaging contains no game binaries/assets and no external executable/library payloads.
- Historical dev20–dev23 release notes/validation files retain their period-correct counts; current docs carry explicit dev24 follow-ups instead of rewriting sealed history.

## Publication gates that remain human decisions

- Original project code still has **no selected public license**. Choose one before public redistribution.
- Preserve the Xenia BSD-3-Clause notice and all provenance/AI disclosure files.
- In-Blender UI/operator validation remains a documented external-environment gap.
- Do not seal dev24 merely because readiness checks pass; sealing/version promotion remains an explicit project-owner decision.

### WIP164 route compatibility follow-up

The current route-playback regression additionally checks explicit Bmap13/Bmap15 DAT compatibility against the proven WARNING special-resource requests while preserving the separate unresolved canonical-ownership/route-initialization boundary. At the WIP164 checkpoint this added no source files and the source manifest remained 712 entries; WIP165 supersedes that package-count state with the usable-preview additions above.


### WIP165 usable-preview gate

WIP165 adds the first explicit end-to-end usability gate on the canonical retail outer packages, while remaining an unsealed dev24 checkpoint. Xbox 360 and PS3 both complete direct-package extraction/conversion, Stage Explorer, Visualizer Simulator, Asset Viewer and SHA-256 output-manifest generation. Independent later re-hash verification passes **16,567/16,567 Xbox files** and **16,422/16,422 PS3 files** with zero integrity/privacy issues. PS3 internally authenticates/decrypts all six SIIG SDAT resources / 18 blocks with no external fallback.

GUI 0.42.0-dev24 makes Rip + verify the primary first-run action, persists convenience settings outside project outputs, opens the verified Asset Viewer optionally, and forwards the completed rip to Mod Workspace. Resume adds source/plaintext SHA-bound PS3 SDAT caching and safe reuse of unchanged Stage Explorer/Visualizer/Asset Viewer output. Manifest and explicit verification hashing are deterministic in sorted output order while using a bounded standard-library thread pool for independent file reads.

These usability results do not convert the living research-boundary registry into release blockers. Evidence-absent runtime/shader/GMX semantics and external Blender UI validation remain documented limitations. Project license selection and sealing remain owner decisions.


### WIP166 Visualizer presentation/audio follow-up

WIP166 keeps the recovered Xenos SHAPE and recursive-feedback samplers point-filtered, but adds an explicitly host-only final display-softness control (default 0.65 px) so the simulator can better resemble the softer game presentation without altering the recovered feedback recurrence. Console-native BGM is now usable in the static browser simulator through locally generated FFmpeg previews: canonical retail validation produced **53/53 Xbox WMA** and **56/56 PS3 AT3/ATRAC3+** previews while preserving 30 Visualizer timelines / 243 commands on both platforms. Native audio remains external/user-owned and untouched.

### WIP167 Visualizer real-hardware BGM follow-up

WIP167 uses project-owner June 10 real-hardware captures of stages 4-2, 4-4 and 4-5 to validate the executable-recovered normal-stage BGM state. The simulator now separates dedicated Check Mode raw-peak behavior from normal gameplay adaptive `VOL SCALE`, applies decoded `VL_VOLUME_SCALE`/0xCE window overrides (180 frames for all three reference stages), and exposes the hardware `VOL / MIN / MAX / VOL SCALE / AVE RAW / AVE SCALE` diagnostics. The game-side post-meter normalizer is now regression-locked; only the upstream browser-vs-XAudio2 meter processing cadence remains open. The video captures themselves are not packaged.

### WIP168 project-owner usability / Visualizer follow-up

WIP168 moves the desktop GUI to **0.43.0-dev24**. GMX Workbench is now vertically scrollable as a whole, and Game Rip has a dedicated console-style per-file stream with both scrollbars while preserving the existing compact phase/count summary and global Task log.

Visualizer dataset **v14** uses the project-owner same-stage comparison to separate two issues. First, stage timeline selection now actually synchronizes decoded `VL_SEQUENCESET` events to their active ParameterSet row and can advance the authored DAT frame at the logical 60 Hz rate; the status line exposes `SEQ/PARAM` so comparisons against the hardware debug overlay are direct. Second, final visible-canvas presentation is recalibrated to 5.5 px softness / 0.32 intensity by default, explicitly as a host-only capture match rather than a new Xenos constant. The recursive recovered RGB path is unchanged and remains inspectable at 0 px / 1.0.

The WMA/AT3 mute issue is addressed by delaying `MediaElementAudioSourceNode` creation until Web Audio has been user-unlocked and is running. Until then, the native HTML media path remains untouched/audible. FFmpeg browser previews are normalized to stereo 48 kHz. WIP174 additionally mirrors the documented Xbox 360 XAudio2 5 1/3-ms processing quantum with a 256-sample analyser window; only browser/native snapshot phase remains bounded. The selftest uses non-zero synthetic audio plus a decoded-preview silence check when FFmpeg is available.

### WIP169 retained-source rip updater

WIP169 moves the desktop GUI to **0.44.0-dev24** and adds a first-class retained-source rip migration path. `update-rip` uses the completed rip's own `decompressed_bbx/`, so normal feature evolution no longer requires the project owner to feed the original STFS/PKG/game tree back into the toolkit. Migration is component-aware: retained BBX outputs are checked by source SHA-256 + conversion options + schema and reused when current; higher-level outputs use component schemas or exact generator-module hashes and rebuild only when stale or when an upstream dependency changed. `--refresh-assets` explicitly overrides conversion reuse. Exact-build update state is keyed by an updater-module SHA-256 profile rather than the public version string alone. A manifest-integrity preflight protects edited/incomplete rips by default, while an excluded recovery journal makes interrupted component swaps recoverable on rerun. The final refreshed tree receives a new deterministic output manifest and completion verification.

### WIP173 — Visualizer SequenceSet timing

WIP173 closes the previously bounded `VL_CHANGETIME` behavior. June 10 `Function_82175DB0` stores minimum/maximum SequenceSet change thresholds and re-rolls immediately; `Function_82175CC0` selects `[min,max)` using the recovered CRT RNG, and `Function_82177648` reproduces the dirty-slot / `threshold < counter` / `-1` wrap cadence. Visualizer dataset v17 executes this state machine during decoded DAT timeline playback with a simulator-controlled deterministic seed because the native seed is timer-derived. This removes the old first-ParameterSet pinning behavior without claiming a captured hardware run's unknowable seed.

## WIP171 Visualizer Position Fix runtime-initializer correction

WIP171 preserves WIP170's corrected center-origin, +Y-up Canvas bridge but supersedes its incomplete Position Fix interpretation. The June 10 executable's writable Position Fix table is initialized in two stages: the file image supplies the repeating X columns, then startup code at `0x82564470` loads `-308.0`, writes `+308.0` into raw 1..3 Y slots, and writes `-308.0` into raw 7..9 Y slots. May 11 and retail Xbox repeat the same six-store pattern. The runtime contract is therefore the full native 3×3 grid at X `-448/0/+448` and Y `+308/0/-308`, plus raw 0's separate Free X/Y path. Raw 0 at free `(0,0)` and raw 5 fixed `(0,0)` may look identical but are semantically distinct. Visualizer dataset **v16** restores all ten raw choices and the retained-source rip updater treats older simulator datasets as stale without requiring heavy BBX/GMX/TEX reconversion. The project-owner June 10 capture used for the visual cross-check remains an external validation input and is not packaged.


### WIP175 — GIGANTIC UFO presentation-orientation correction

Project-owner review clarified that SIIG's GMX assets share the same native facing convention under the game's top-down presentation. The dev23-era GIGANTIC-UFO-only `-90°` X presentation root is therefore superseded. WIP175 removes that special transform from `gigantic_ufo_complete` rather than rotating every other boss to match it. The recovered hierarchy remains exactly 1× `bos_003.gmx` + 36× `bos_003a.gmx` on `lt_001..lt_036`, child-local matrices remain identity, and generic GMX→glTF axis conversion is unchanged. This is a presentation-policy correction, not a runtime transform change.

### WIP177 Visualizer Check Mode hardware-sweep follow-up

WIP177 consumes ten trimmed project-owner June 10 Xbox 360 Check Mode segments as controlled external validation. Visualizer dataset v20 does not alter recovered renderer math; it exposes the confirmed native precedence and endpoint relationships in the simulator UI. Position Free is active only for raw Position Fix 0, nonzero Fix Rotation bypasses Rotation Base/Add accumulation, ordinary Scale X/Y scales the newly injected SHAPE while Magnify Scale X/Y scales the previous feedback surface, and SHAPE RGBA min/max values are VolumeSet tint endpoints. BG RGBA is a direct single-value clear control.

The BG:A footage is deliberately not used to invent Xenos alpha behavior. Exact render-target alpha storage/final-composite equivalence remains open, as does browser/native XAudio2 snapshot phase/scheduling. Capture media is not packaged. The WIP177 regression gate is 164/164 and the finalized root manifest tracks 739 source files.
### WIP178 — model-identity catalog / Visualizer follow-up

WIP178 adds an 82-row project-owner model identity catalog and Asset Viewer **2.2.0** integration. The browser can search and display friendly player/enemy/sub-boss/boss/effect identities while preserving evidence status: 71 entity rows are owner-confirmed, two `est_*` usage rows are owner-confirmed effects, and nine `est_*` interpretations remain visibly speculative. The five-build runtime registry independently reconciles CELL (`emy_044` / `0x97`), LUST (`emy_051` / `0x9D`), and SHUTTER (`emy_052` / `0x5A` + `0x5B`) without claiming that their friendly names are executable-internal strings.

The second ten-segment June 10 Check Mode batch adds a narrower Visualizer constraint: BG RGB remains visibly active when BG:A is zero. This directly supports the existing dataset-v20 browser choice to preserve clear RGB independently of Canvas alpha; it does not establish exact Xenos render-target alpha storage or final presentation behavior. Ordinary source Scale X/Y, feedback Magnify Scale X/Y, Stick VolumeSet, Add Rotation, and SHAPE order also remain consistent with the recovered pipeline, so renderer math and dataset version stay unchanged. Hardware capture media is external and unbundled. The finalized WIP178 regression gate is **166/166** and the root manifest tracks **744** source files.


### WIP179 LUST boundary sync + Blender/modding headless validation

WIP179 synchronizes the living 0x9D boundary with WIP178's project-owner catalog: `emy_051` is presented as **LUST**, while runtime `0x9D` -> `emy_051.gmx` remains independently executable-backed across all five retained builds. No executable-internal `LUST` string is claimed; the former neutral gameplay-name requirement is now superseded rather than left as a contradictory open boundary.

Blender add-on **0.2.1** fixes the unpacked-source auto-discovery fallback: instead of stopping at `addons/`, it walks upward until the real toolkit `siig_toolkit.py` can be found. A new dependency-free headless `bpy` contract imports and registers the add-on, verifies toolkit discovery, logical-master metadata/fallback behavior, nested-part traversal isolation, collection-label sanitation and clean unregister. Existing GMX scene/texture synchronization, rigid partitioning, donor-free synthesis, mod-gltf/TEX/BBX and `.siigmod` regressions remain in the same full self-test. Real Blender UI/Outliner execution remains an external-environment gate.


### WIP180 `est_*` effect-model ownership audit

WIP180 converts the remaining `est_011`...`est_021` identification problem into a reproducible evidence table. The range contains 11 resources: two project-owner-confirmed effect usages and nine explicitly speculative identities. `est_012` is the only member with a five-build top-level runtime-registry slot (`0xE6` retail-lineage, `0xE7` May prototypes). External retail-rip geometry fingerprints prove `est_011` and `est_014` have byte-identical converted geometry while their GMX containers differ. No controller ownership or speculative `est_016` beam attribution is promoted beyond the evidence.

### WIP181 / WIP182 — confirmed `est_*` semantic promotions

WIP181 promotes `est_012.gmx` to a project-owner-confirmed shared JOLYNE/UNKNOWN interactive target cube, with direct executable resource loads independently tying both bosses to the model across retail/prototype lineage. WIP182 promotes `est_020.gmx` / `est_021.gmx` to the shared OCTOPUS/GLUTTONY bomb-before-detonation and resulting explosion pair. GLUTTONY's executable `DischargeBomb` path independently corroborates the `SG_BOMB` family, while exact per-file shot-resource binding remains conservatively bounded.

### WIP183 — Visualizer polished proof-of-concept boundary

WIP183 responds to project-owner browser testing rather than new Xenos claims. Visualizer dataset **v21** explicitly presents the simulator as a polished PoC. The recovered recursive point-sampled feedback surfaces are unchanged; only the final browser presentation is adjusted from the overly dark WIP168/WIP182 `5.5 px / 0.32` pass to a brighter `1.4 px / 0.88` base plus `0.52` host-only screen/bloom layer. Raw recovered output remains available with all presentation polish disabled.

Generated WMA/AT3 browser previews no longer enter a `MediaElementAudioSourceNode`. FFmpeg now computes a compact left/right peak envelope at the recovered 256-sample, 48 kHz XAudio2 quantum while the native HTML media element remains directly audible. Host-selected browser audio is decoded only to build the same envelope. This removes the known file/local-origin analyser-routing mute mode without claiming exact browser-vs-XAudio2 query-phase alignment. Exact Xenos final composite, render-target alpha storage, and hardware display filtering remain open.
### WIP184 Simple Mod Workspace asset tree

WIP184 moves **List Assets** into Simple mode and changes it from a task-log dump into an embedded archive/resource tree. GUI 0.45.0-dev24 keeps the clean rip immutable while giving beginners the missing resource-selection step: an untouched supported resource is exported on demand, then opened in its editable representation. Persistent states are derived from workspace edit-baseline hashes and staged/addition files rather than GUI-session memory: Untouched, Exported, Edited, Staged and Added. Build/Verify refresh an open tree, and GMX selection feeds the existing Advanced import fields without duplicating the native builders in GUI code.



### WIP187 flexible audio authoring

WIP187 lifts the conservative equal-duration/rate/channel restrictions from Mod Workspace audio editing. Xbox XWB entries can now be repacked with new PCM16 duration/rate/channel metadata and proportionally remapped existing loop regions; 1–6 channels remain native and wider inputs are downmixed to stereo. PS3 SBlk can now repack variable-duration/rate replacements, update later stream offsets/sizes and pitch metadata, and accept multichannel input by downmixing to SIIG's native mono stream form. The supplied retail banks were used only as external structural validation inputs and are not packaged. Runtime acceptance remains an emulator/hardware validation boundary.

### WIP188 Blender SIIG Style Preview

Blender add-on **0.4.0** retains source-tree discovery and logical-part behavior, defaults normal imports to an editing-first solid pass, hides preserved native `_E` objects non-destructively after assembly import, and keeps the two presentation layers optional. Native `_E` line geometry can be copied into generated white emissive curve previews without altering imported meshes. Adjustable scanlines are inserted only at the compositor final-image path; Blender 3.6/4.x use the legacy scene node tree while Blender 5 uses the scene compositing node group and Group Output compatibility path. These are host-side preview features: native edge geometry is evidence-backed, while curve thickness and scanline appearance are not claimed exact Xenos/RSX rasterization/final-composite constants. Real Blender visual/UI validation remains external.

### WIP189 fast incremental Update Rip

WIP189 changes Update Rip from a repeated whole-tree hashing workflow into an incremental migration gate. Routine preflight always checks manifest inventory and sizes. Fresh WIP189 rips also carry a manifest-bound `OUTPUT_STAT_CACHE.json`; unchanged stat fingerprints reuse existing manifest hashes while changed-stat files are selectively re-hashed. Older rips bootstrap without trusting that cache for destructive writes: before replacing `assets/`, localization, systemfont, audio, structured output, Stage Explorer, Visualizer Simulator, or Asset Viewer, the updater hashes every tracked file in the affected existing component against the prior manifest, regardless of stat-cache hits. This preserves the default no-overwrite-of-edits rule while avoiding unrelated whole-rip reads.

The final manifest is also incremental: hashes for untouched, same-size files are carried forward; rebuilt component roots and changed validation metadata are hashed anew. The completion gate still checks inventory, size, partial-file and privacy state, while `verify-output` remains the explicit independent full-byte SHA-256 verification command. `--force-modified` intentionally falls back to re-hashing the complete current tree before blessing it, `--refresh-assets` now correctly bypasses the exact-profile no-op shortcut, and saved modern rip options no longer let aggregate `.obj` counts falsely force per-BBX OBJ reconversion.

External retained-retail timing validates the effect at full scale in this environment: a complete Xbox retail rip took **301.09 s**, the first WIP189 update with all generated components current took **9.98 s**, an exact-profile no-op rerun took **1.90 s**, and a separate full SHA-256 `verify-output` took **9.70 s**. The update reused **23/23 BBX archives / 2,593 resources**, reused localization/font/audio/structured/Stage Explorer/Visualizer/Asset Viewer, and computed only **5** new manifest hashes while carrying forward **16,666** unchanged hashes. These timings are environment-specific validation evidence rather than a guaranteed performance target; retail payloads remain external and unbundled.


## Dev24 WIP196 deployment/add-on gate

- Blender add-on package/source identity is checked at **0.4.0**, with a solid-only raw-GMX default, reversible native-outline visibility controls, opt-in Style Preview, and explicit Blender 5 compositor migration tokens.
- Mod Workspace synthetic regression now requires `build/xbox360_replacements/<original-path>` to contain a gzip wrapper that decompresses exactly to the verified rebuilt BBX, plus a `XBOX360_REPLACEMENTS.json` path mapping.
- Desktop GUI diagnostics require the package-editor-neutral Xbox replacement workflow, optional `.siigmod` labeling, visible task-failure popup, and exact save-path feedback for successful `.siigmod` sharing.
- Real Blender 5 visual/operator testing and retail STFS runtime acceptance remain external project-owner gates; source/package structure does not claim those external runtime tests occurred in the build environment.


## WIP200 Atlas safe-editing gate

WIP200 adds an Atlas Inspector / safe sprite-region workflow. Duplicate-looking regions retain independent technical slot IDs; semantic labels remain separate and evidence-driven; generated guide/preview PNGs carry a do-not-rebuild marker that `png2tex` rejects; exact-size region replacement and out-of-region pixel validation are regression-covered. Automatic rectangles are explicitly content-derived conservative regions, not claimed native UV allocations. Atlas repacking/new-slot work stays gated on authoritative UV/reference recovery.
