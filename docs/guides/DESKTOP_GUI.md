# Desktop GUI (current 2.10.0-dev24; introduced in dev21)

The current dev24 desktop control center is intentionally a **thin UI over the existing audited CLI**: format parsers/builders remain in `siig_toolkit.py`, while the GUI launches those same commands in background tasks and streams their output into a shared task log.

## Launch

On Windows, double-click:

```text
SIIG_GUI.bat
```

Or run directly:

```text
python siig_gui.py
```

The GUI uses Python's standard-library Tkinter only. No web service or network connection is required.

## Game Rip and drag-and-drop (current GUI 0.52.0-dev24; drag/drop introduced in 0.32.0-dev21)

On Windows, the **Game Rip** tab accepts Explorer drag-and-drop without bundling `tkdnd`, `tkinterdnd2`, or another binary dependency. Drop exactly one supported outer game/package file or one already-extracted game folder into the **Drop game input** strip. The GUI normalizes duplicate shell entries and rejects ambiguous multi-source drops.

A successful drop only fills the existing **Game/package** field and selects the Game Rip tab. It **does not start extraction automatically**; click **Rip + verify** when ready. This avoids launching a long extraction from an accidental drop. The normal **Browse…** button remains the keyboard/accessibility and non-Windows fallback.

The Windows implementation uses the standard `WM_DROPFILES` shell message through `ctypes`, restores the original Tk window procedure when the GUI closes, and keeps all actual extraction logic in the same audited `rip-game` CLI path.

## Tabs

### Game Rip

Choose an Xbox 360/PS3 package, ZIP, or extracted game input and an output folder. On Windows you can either Browse or drag one input file/folder into the drop box. The normal path is **Check input → Rip + verify → Open Asset Viewer**. `rip-game` creates the SHA-256 output manifest and performs the automatic completion gate; **Verify existing rip** (`verify-output` / `verify-rip`) performs a later full-byte re-hash. A successful rip can open the generated Asset Viewer automatically and fills Mod Workspace’s verified-rip field. Resume reuses SHA-bound outer/archive/SDAT work and safe post-process viewers when the package has not changed.

**Update existing rip** is intentionally faster than a fresh rip. It reuses current converted components, uses `validation/OUTPUT_STAT_CACHE.json` to avoid re-reading unchanged files, checks changed-stat files against the old manifest, hashes legacy component contents only when they are about to be overwritten, and refreshes the final manifest incrementally. The cache never replaces the cryptographic manifest: use **Verify existing rip** whenever you want a full independent SHA-256 pass over every tracked file.

The **Source-package cache** panel describes the separate outer-container staging cache created beside a rip when ZIP/STFS/PKG input is used with resume. **Keep for faster resume/update** is enabled by default and remembered locally. The panel shows whether the cache exists and its disk usage. **Clear cache…** always asks for confirmation and explains that clearing deletes only the unpacked source-package sidecar, never `SIIG_Ripped` or a Mod Workspace; the tradeoff is that a later resume/full rip may have to unpack the original source again.

GUI 0.52.0-dev24 compresses this panel to one row and protects the dedicated rip/update console with a minimum readable height, so cache controls cannot flatten the per-file log on shorter displays. The drag target and live-progress block are also compacted while retaining their full behavior.

### Mod Workspace

Choose a verified `SIIG_Ripped` tree and a mod-workspace directory. In Simple mode, **Create workspace → List Assets** opens an embedded archive/resource tree below the buttons. Double-click a supported resource (or press **Open / edit selected**) to export it through the normal round-trip builder and open its editable form. Persistent **Untouched / Exported / Edited / Staged / Added** marks make modified files easy to distinguish from untouched resources; **Refresh marks** picks up saves made by external editors. Build and Verify refresh an already-open tree automatically.

Advanced mode keeps `.siigmod` inspection/application plus **Import glTF + TEX**. Selecting a GMX in the tree fills the archive/resource fields automatically, so the beginner tree and specialist import path share one selection instead of requiring manual archive-key lookup.

### GMX Workbench

GUI 0.52.0-dev24 gives Simple mode a compact layout: Export/Rebuild/Inspect/Open Folder share one row; the assembler keeps one shared Models/Output folder pair; **Bosses** and **Enemies / sub-bosses** are nested tabs rather than simultaneous stacked panels; and CENTIPEDE-only segment overrides stay hidden until CENTIPEDE is selected. Advanced import options are arranged in two columns to reduce scrolling while preserving every switch.

The GMX workbench is the main dev25 modeling surface. It exposes:

- native GMX inspection;
- GMX -> glTF export;
- **edited glTF -> native GMX topology-changing template import**;
- lossless fixed-layout editable JSON export/build for geometry/material/bone/animation values;
- UV-flip symmetry for applications that need inverted V coordinates.

The standalone glTF importer may change vertex/index counts. Dev26 mesh sync can create/delete MESH/ARRY records; dev27 scene sync can additionally clone/create MTRL/SHAD/BONE relationships and extend PARE hierarchy groups; dev28 texture sync can create TXIF references and bind glTF `baseColorTexture` through compatible MTRL samplers. In 2.9.0-dev5, **Sync MOTN/ANIM animation graph** accepts multi-bone glTF clips and LINEAR/STEP/CUBICSPLINE TRS channels. One authoring clip expands into synchronized per-bone native 30 Hz matrix tracks, while exported existing tracks are preserved unless replacement is explicitly requested. The Mod Workspace enables animation synthesis automatically alongside PNG -> native TEX rebuilding/donor-free layout synthesis and BBX staging/addition. These structural modes remain off by default in the standalone workbench. Existing BONE transforms are preserved unless transform import is explicitly requested in glTF extras. The **Scene graph report** action opens an HTML hierarchy/material/texture/mesh/shader/animation relationship view generated by the same toolkit parsers.

In 2.9.0-dev6, **Create new GMX** is a separate no-template action. It invokes `gltf2gmx-new`, synthesizes the canonical decoded GMX root, and enables the decoded schema/scene/texture-reference/animation builders automatically. The Native GMX template field is not read for this action. Use template-backed import instead when retaining unknown bytes from an existing model is more important than starting clean.

### Utilities

Utilities has its own always-visible **What does this utility do?** box. Hover or keyboard-focus a field/button to replace the box text with that control's exact purpose; leaving the control restores the Utilities overview.

- **Diagnose toolkit / input** (`doctor`) is read-only diagnostics for the toolkit and optional selected input. It checks the local environment/dependencies and recognizable input/platform details; it does not repair or modify files.
- **Run selftests** runs the internal regression suite and does not modify a rip or Mod Workspace.
- **Asset capabilities** prints the current view/edit/rebuild/synthesis support matrix.
- **Build viewer** reads the selected asset directory and writes an offline Asset Viewer to the selected Viewer output.
- **Boss matrix** prints the 18-family reconstruction/evidence report; it does not assemble models.
- **Visualizer simulator (PoC)** reads an optional rip and writes the standalone simulator to Visualizer output.

## Current GUI boundary

GUI **0.52.0-dev24** covers normal extraction, verification, the Simple Mod Workspace asset tree/status browser, GMX editing/assembly, browser preview, boss/entity Workbench and common utilities while retaining the CLI for research/specialist switches. Game Rip shows a structured phase/detail view plus running Assets/glTF/PNG/error counters and the full underlying task log. The GUI remains a thin local front-end over the same audited CLI paths rather than a separate parser implementation.

## Privacy and provenance

The GUI does not upload game files. It invokes the local source-only toolkit against user-selected local paths. The release continues to contain no proprietary SIIG assets or executables.


## Rigid glTF skins (dev7)

GMX Workbench adds **Import rigid glTF skins (single-joint JOINTS/WEIGHTS; dev7)**. Enable it for template-backed imports when a Blender/glTF mesh uses a skin but all vertices are rigidly weighted to one joint. Create new GMX enables the same safe compatibility layer automatically. The GUI does not offer a “force blended skinning” switch: multi-joint weights are rejected because the confirmed SIIG GMX corpus has no per-vertex joint/weight arrays.


## 2.10 rigid bind rebake

The GMX Workbench rigid-skin checkbox now also permits affine non-identity inverse bind matrices for otherwise rigid single-joint skins. The toolkit rebakes mesh geometry before native BONE attachment. Mod Workspace and Create new GMX use the same behavior automatically.


## Multi-GMX assemblies (2.10.0-dev3)

GMX Workbench includes **Assemble PROGRESSIVE UFO** for direct five-instance export using the executable-backed runtime formation recovered across June Xbox, retail Xbox, and retail PS3. **PROGRESSIVE UFO manifest** writes the same completed catalog as editable JSON, while **Assemble GMXs…** remains the generic manifest workflow. Unknown transforms in other manifests remain a hard error rather than receiving guessed placements.


## Simple and Advanced modes (2.10.0-dev4)

The desktop app now starts in **Simple mode**. A header switch changes to **Advanced mode** without changing any project data or automatically enabling expert compiler options.

Simple Mod Workspace emphasizes Create → List Assets → Open/Edit selected → Build → Verify → Pack, with persistent resource-status marks in the embedded tree. Simple GMX Workbench emphasizes Original GMX → Export for Blender → edit → Rebuild GMX and keeps the evidence-backed one-click boss assemblies visible.

Hovering the mouse over, or keyboard-focusing, supported fields/buttons/check boxes updates the persistent **What does this do?** box with a plain-language explanation. The separate task log remains available for command output and errors.

Advanced mode restores the low-level archive identifiers, JSON paths, native graph/schema/texture/animation/skin synchronization controls, template-free GMX creation, manifest authoring and other specialist functions.

## Evidence-backed boss assemblies (2.10.0-dev4)

GMX Workbench exposes one-click **Assemble PROGRESSIVE UFO** and **Assemble CRAB**. CRAB exports its nine-part first-visible formation with the A7 root baked at native sample 167 and the CD body shell at sample 0. Advanced mode also exposes both catalog manifests and the generic custom-assembly workflow.


## 2.10.0-dev5 boss-viewing refinements

Simple GMX Workbench now exposes one-click **Assemble HORNET** in addition to PROGRESSIVE UFO and CRAB. HORNET exports the executable/model-backed fully revealed A1 + 125 BF armor lattice; its invisible C1 formation rig and dormant C0 prism pool are deliberately omitted from this viewing preset.

**Assemble CRAB** now defaults to the first deterministic landed/combat-ready sample instead of dev4's correctly recovered but airborne first-visible intro sample. Advanced/CLI users can still select the historical `crab_first_visible` catalog.

Assembly export deliberately preserves native SIIG coordinates and scale. Bosses can therefore appear very large in Blender. Use Blender's **Frame All** or **Frame Selected** navigation instead of assuming the authoritative scene should be rescaled. The GUI does not apply a hidden meter conversion.


## 2.10.0-dev6 HORNET prism-wall variants

Advanced GMX Workbench adds a **HORNET prism root slot** selector plus **Prism-wall manifest** and **Assemble prism wall** actions. The selector contains only the 13 values actually present in the Xbox/PS3 runtime random table: `0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44`.

The GUI deliberately does not put a random prism-wall default in Simple mode. Simple **Assemble HORNET** continues to export the deterministic full-armor state. Advanced users may choose any exact retail-valid prism-wall outcome explicitly. Each selected wall exports one animated A1 root plus 44 C0 prisms; the selected C0 slot is omitted because A1 occupies it in the game.


## HORNET propagation controls (dev7)

Advanced GMX Workbench adds **Propagation seed** and **Propagation wave** selectors plus manifest/assembly buttons for the evidence-backed HORNET state-6 family. Seeds are restricted to `0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44`. Wave validity depends on the selected seed and is checked by the CLI; choosing a wave beyond complete grid coverage is an error.

Simple mode intentionally continues to expose the deterministic full-armor HORNET action instead of presenting one runtime-random propagation result as canonical.

## 2.10.0-dev8 MANDALA assembly

Simple GMX Workbench adds **Assemble MANDALA**. Advanced mode adds **MANDALA manifest** plus **Assemble MANDALA**. Both use the same five-build executable-backed `mandala_initial_combat` catalog: 40 visible instances at state-7 activation, with later BC pieces excluded and native B7–BB animations preserved.


## 2.10.0-dev9 ULTIMATE UFO hierarchy/activity selector

Simple GMX Workbench adds an **ULTIMATE UFO state** selector and **Assemble ULTIMATE UFO**. The default is **COMPLETE — 126 allocated hierarchy**. This is explicitly an allocation/hierarchy view rather than a simultaneous-visibility claim. Advanced mode additionally exposes **ULTIMATE UFO manifest**.

The numbered choices are activity-focused subsets: 2 UMB, 3 TOW, 6 FAN + RING, 7 FAN + RING (second-fan progression), 8 RING, 9 CORE HOLD, 11 AIRLOCK and 12 AIRLOCK LATE. Umb/Tow/Fan/Ring phase bytes are collision/destructibility flags, so the GUI does not label zero-valued families as proven invisible.
## 2.10.0-dev10 HORNET exposed core

Simple GMX Workbench now presents separate **Assemble HORNET armor** and **Assemble HORNET exposed** actions. The exposed action uses `hornet_exposed_core`, the executable-backed state-3 entry snapshot: A1 / `bos_008.gmx` at motion 0/sample 0 with all 125 BF/C0 subordinate records reset to state `-1`. Advanced mode also provides **Exposed manifest** and **Assemble exposed**.

This does not replace the existing prism-wall or propagation controls. Those remain distinct attack-state families, and the GUI does not merge mutually incompatible HORNET presentations into one invented scene. Fresh real-retail export validation from the re-uploaded Xbox package confirms the exposed preset is one A1 instance with two meshes and four glTF nodes.


## dev24 compact Boss/Entity Workbench and gameplay-pose grades

The compact Boss Assembler covers all 18 main-game boss families and reuses one remembered model folder plus one remembered assembly-output folder. **Assemble + preview** writes the deterministic glTF, rebuilds the local Asset Viewer for that output folder, and opens its browser model/wireframe preview. Advanced one-click assembly actions reuse the same folders instead of reopening folder and Save As dialogs.

The Boss selector now exposes the evidence-backed gameplay-pose options for OCTOPUS, WATER STRIDER and NAMELESS/internal `NO_NAME`. NAMELESS includes both the main/Bonus stationary spawn and the Extra 2-8 point-to-point approach. These are exact root transforms/actions, not claims of recovered multipart ownership. THE MOON remains native inspection only. Current matrix coverage is **14 deep runtime + 3 gameplay-pose + 1 native-only**.

The compact Entity / Sub-boss Assembler exposes eight families: ENVY, GREED, WRATH, KEEPER, OPPRESSOR, GLUTTONY, VANITY and TELEPORTER. The diagnostic count matches those eight families.

Game Rip shows a current phase, latest detail and running **Assets / glTF / PNG / errors** counters while retaining the complete per-resource log underneath.


## WIP165 local preferences and verification

Game/package, output/workspace folders and normal workflow toggles are persisted in a per-user local settings file (`APPDATA` on Windows, Application Support on macOS, XDG config on Linux). This settings file is deliberately outside every rip and mod workspace and therefore cannot leak a local path through generated project JSON. Preference-write failure is non-fatal.

**Rip + verify** is not a cosmetic label: a successful normal rip writes `validation/OUTPUT_MANIFEST.json` / `.sha256`, then checks manifest inventory, file sizes, partial-file state and privacy metadata before returning success. `validation/RIP_VERIFICATION.json` records that completion gate. Use **Verify existing rip** / `verify-rip` later when you want every tracked file re-hashed independently.

See `QUICK_START.md` for the recommended first-run path.
