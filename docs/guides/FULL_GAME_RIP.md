# One-click full-game rip

`rip-game` accepts the original outer package directly, an extracted game directory, or a ZIP containing an extracted game. Input type is detected from the header and contents rather than the filename extension.

```text
Xbox 360 STFS package: CON / LIVE / PIRS
PlayStation 3 type-1 PKG
Extracted game directory
ZIP containing an extracted game
```

## Before the first rip

```bat
python siig_toolkit.py selftest
python siig_toolkit.py doctor "C:\path\to\game-package"
```

`doctor` reports Python/runtime status, bundled-table integrity, optional FFmpeg availability, and any recognizable input issues without extracting the game.

## Fastest Windows method

Drag the package, extracted ZIP, or extracted folder onto `SIIG_Rip_Game.bat`.

The output is created beside the input as `SIIG_Ripped`. The launcher uses `--resume`; unchanged archives are skipped only when their source hash, conversion profile, and toolkit version match.

With package/ZIP inputs, resume also keeps a content-addressed `.SIIG_Ripped.siig_outer_cache` sidecar beside the rip. It is safe to delete because it contains only reusable unpacked source data, not unique rip/mod edits; doing so only means a later resume may need to unpack the original source package again. GUI 0.52.0-dev24 exposes its size, a compact keep-cache preference, and a warning-protected **Clear cache…** action without sacrificing the rip console height.

## Command-line examples

### Xbox 360

```bat
python siig_toolkit.py rip-game "C:\Games\SIIG_X360" -o "C:\Rips\SIIG_X360" --resume
```

### PlayStation 3

```bat
python siig_toolkit.py rip-game "C:\Games\SIIG_PS3.pkg" -o "C:\Rips\SIIG_PS3" --resume
```

The outer PKG and SIIG's six inner NPDRM SDAT resources are handled internally for the supplied retail package. `--ps3-sdat-dir` remains a fallback for pre-decrypted `*.bin.gz.dat` payloads.

### Previously extracted input

```bat
python siig_toolkit.py rip-game "C:\Games\Space Invaders IG X360.zip" -o "C:\Rips\SIIG_X360" --resume
python siig_toolkit.py rip-game "C:\Games\Extracted SIIG PS3" -o "C:\Rips\SIIG_PS3" --resume
```

### Outer-container-only mode

```bat
python siig_toolkit.py unpack-container "C:\Games\SIIG.pkg" -o "C:\Rips\SIIG_Installed_Files" --clean
```

This stops after STFS/PKG extraction and writes `SIIG_CONTAINER_MANIFEST.json`.

## Default processing sequence

1. Detect input type by magic/content.
2. Extract ZIP, STFS, or PKG into a bounded workspace; with `--resume`, reuse exact-hash content-addressed staging when available.
3. Detect Xbox 360 or PS3 from `default.xex` or `EBOOT.BIN`.
4. Internally decrypt/authenticate SIIG PS3 SDATs; fall back to supplied decrypted outputs only if necessary.
5. Normalize gzip-wrapped BBX archives with bounded expansion.
6. Extract BBX resources recursively with hash validation and entry/depth budgets.
7. Convert supported textures, models, font, audio, localization, DAT, MAP, COL, and ANM resources.
8. Build the offline Stage Explorer when its required data is present.
9. Build the linked-data offline Asset Viewer unless disabled.
10. Write privacy-safe reports and a deterministic SHA-256 output manifest.
11. Remove transient outer-container working files. When resume caching is enabled, keep the content-addressed source-package sidecar beside the rip for future reuse.

## Output layout

```text
SIIG_Ripped\
├── assets\
├── decompressed_bbx\
├── audio\
├── localization\
├── ready_files\
├── stage_explorer\
├── asset_viewer\
├── structured\
│   ├── dat\
│   └── map\
├── systemfont\
└── validation\
    ├── RIP_REPORT.json
    ├── RIP_REPORT.txt
    ├── OUTPUT_MANIFEST.json
    └── OUTPUT_MANIFEST.sha256
```

The exact folders depend on the source platform and available resources.

## Stage Explorer generation

The explorer is generated automatically unless `--no-stageviz` is supplied. It embeds available verified MAP atlases and creates:

```text
stage_explorer\SIIG_Stage_Explorer.html
stage_explorer\STAGE_MANIFEST.json
stage_explorer\README.txt
```

The explorer is offline and self-contained. Because it may embed game-derived images and stage data, treat it as a private research artifact.

## Verification

After extraction:

```bat
python siig_toolkit.py verify-output "C:\Rips\SIIG_X360"
```

Checks include:

- report presence and format;
- privacy-safe metadata;
- manifest path uniqueness;
- file existence and exact sizes;
- SHA-256 hashes unless `--quick` is used;
- unexpected `.siig-part` files left by interrupted atomic writes.

To intentionally rebuild the manifest after adding or removing files:

```bat
python siig_toolkit.py verify-output "C:\Rips\SIIG_X360" --write-manifest
```

Do not use `--write-manifest` merely to make an unexpected verification error disappear; inspect the change first.

## Useful options

```text
--clean                 delete the existing output before starting
--resume                reuse matching archive/conversion results and exact-hash outer-package staging
--ps3-sdat-dir DIR      optional fallback directory for decrypted PS3 SDAT outputs; repeatable
--convert-obj           also write legacy OBJ models
--no-gltf               skip glTF conversion
--no-textures           skip TEX/font PNG conversion
--no-audio              skip Xbox 360 XACT and PS3 Sony SBlk WAV conversion
--ffmpeg PATH           select a particular FFmpeg executable
--flip-v                flip model texture V coordinates
--no-outer-cache        force outer extraction even with --resume
--no-stageviz           skip automatic Stage Explorer generation
--no-asset-viewer       skip automatic Asset Viewer generation
--viewer-no-hash        omit viewer SHA-256 inventory
--viewer-max-text-preview-kib  bound each deferred text excerpt
--viewer-page-size      set initial cards per viewer page
--viewer-max-embed-mib  deprecated compatibility option; previews are linked
--no-output-manifest    skip final deterministic SHA-256 manifest
--max-files N           outer-container file-count limit
--max-total-bytes N     outer-container total expanded-byte limit
--max-file-bytes N      outer-container per-file expanded-byte limit
--max-zip-ratio N       ZIP per-member expansion-ratio limit
```

## Platform behavior

### Xbox 360

- STFS is unpacked internally.
- Ordinary gzip wrappers are detected by magic.
- BBX resources are extracted recursively.
- TEX files are untiled and converted to PNG.
- GMX files are exported to glTF by default.
- XACT/XMA2 banks are converted to WAV when FFmpeg is installed.
- Existing WMA media is copied unchanged.

### PlayStation 3

- Type-1 outer PKG is unpacked internally.
- Ordinary gzip files are decompressed directly.
- Inner `NPD\0` SIIG SDAT payloads are decrypted and authenticated internally; external `.bin.gz.dat` files are fallback-only.
- PS3 TEX uses its RSX wrapper and linear pixel layout.
- Shared GMX resources use the same glTF exporter.
- Sony 989SND/SCREAM SBlk v3 audio is preserved and decoded internally to 84 named WAV streams on the retail bank.
- AT3 and other ready-to-use media is copied unchanged.

## Failure and recovery behavior

Writes use temporary `.siig-part` files and are renamed only after success. An interrupted rip can normally be restarted with `--resume`. Verification reports leftover partial files so they are not mistaken for valid output.

Use `--clean` when changing source packages, PS3 decryption sets, or output policy substantially. Keep the original game package unchanged and use a separate output directory.

See `docs/guides/CONTAINER_INPUT_NOTES.md`, `docs/guides/SECURITY_NOTES.md`, and `docs/guides/TESTING.md`.


## Automatic asset viewer

Version 2.5.0 creates `asset_viewer/SIIG_Asset_Viewer.html` plus an adjacent `viewer_assets` directory. Disable it with `--no-asset-viewer` or skip viewer hashing with `--viewer-no-hash`. Media is linked and lazy-loaded rather than embedded; `--viewer-max-embed-mib` is retained only for compatibility. Use `--viewer-max-text-preview-kib` and `--viewer-page-size` to tune deferred text excerpts and card pagination. Keep the HTML and `viewer_assets` directory together. `python siig_toolkit.py serve SIIG_Ripped` can be used when a browser restricts local files.

## New structured stage research outputs (2.4.0)

Full rips now additionally create:

- `structured/stage3d/`: Bmap/Xmap/map4/map5 JSON, path CSV, placement CSV, and OBJ path lines.
- `structured/stagewall/`: wall/Xwall strip and stage-generator CSV/JSON.
- `structured/shaders/`: Xenos shader header/metadata JSON and raw microcode.
- corrected `.anm.csv` / `.anm.csv.json` files beside extracted ANM resources.

These outputs preserve unknown auxiliary vectors and raw values rather than assigning unsupported gameplay labels.

## Modding the completed rip

After `rip-game` has produced a clean verified rip, use [`MOD_WORKSPACE.md`](MOD_WORKSPACE.md) to create a tracked mod workspace, export editable assets, rebuild only changed native resources/BBX archives, and verify the resulting patch tree.

In desktop GUI **0.44.0-dev24**, the Game Rip tab includes a dedicated **Rip/update console · complete per-file log**. It appends every emitted container/resource/conversion/verification line for the current rip and provides both scrollbars, Copy, and Clear. The smaller phase/count panel above it remains a quick summary; it no longer has to carry the full history.

### Visualizer native-BGM previews

When FFmpeg is available, Visualizer generation discovers console-native BGM in the rip (`.wma` on Xbox 360 and `.at3`/ATRAC3+ on PS3) and writes browser-safe previews under `visualizer_simulator/bgm_preview/`. Preview filenames include the native source SHA-256 prefix, so unchanged tracks are reused on rebuild. The original native BGM is never modified. Without FFmpeg, the simulator still builds and inventories the native tracks but explains that the browser cannot decode them directly.

The simulator's **Display softness** and **Display intensity** controls are presentation-only. WIP168 defaults to **5.5 px softness** and **0.32 intensity** from the project-owner real-hardware comparison; set softness **0** and intensity **1.0** to view the raw recovered feedback RGB. These controls are applied only after the recovered feedback recurrence and do not alter the proven point-filtered Xenos SHAPE/feedback samplers.

WIP168 also keeps console-native BGM audible while enabling the live meter: selecting a generated WMA/AT3 preview does **not** immediately reroute the `<audio>` element through Web Audio. The analyser graph is attached only after the browser has accepted a direct user gesture and the `AudioContext` is running. Generated previews are normalized to stereo 48 kHz; native files are unchanged.

For BGM response, the simulator now distinguishes the two June 10 runtime paths. **Check Mode · raw peak mean** mirrors the dedicated Check Mode control path. **Stage playback · adaptive VOL SCALE** mirrors normal scripted gameplay: the raw stereo peak mean is normalized against an adaptive MIN/MAX window before it drives parameter interpolation. The recovered constructor default is 300 frames, while decoded `VL_VOLUME_SCALE`/opcode `0xCE` events replace that window; stages 4-2, 4-4 and 4-5 author 180. Selecting/applying a stage timeline switches to the gameplay model automatically and shows hardware-style `VOL / MIN / MAX / VOL SCALE / AVE RAW / AVE SCALE` diagnostics.

## Updating an existing rip after the toolkit changes

A completed rip no longer needs to be recreated from the original game package simply because converters, structured exports, the Stage Explorer, Visualizer Simulator, or Asset Viewer changed. Use:

```text
python siig_toolkit.py update-rip "C:\path\to\SIIG_Ripped"
```

The updater reads the retained `decompressed_bbx/` archive sources already stored by `rip-game` and migrates the rip **selectively**. Before touching `assets/`, it compares every retained BBX SHA-256 plus the saved GMX/TEX conversion options and converter schema against each archive's `.siig_source_state`. Matching conversion trees are reused instead of spending minutes reconverting hundreds of models/textures. Localization/systemfont/audio/structured outputs and the Stage Explorer/Visualizer/Asset Viewer each have their own schema/generator checks. Asset Viewer follows only the asset trees it actually indexes; a Stage Explorer or Visualizer-only update does **not** force Viewer reconstruction. Staged Viewer rebuilds explicitly exclude the previous canonical `asset_viewer/` tree so the viewer cannot recursively index itself. It writes a fresh output manifest and performs the changed-scope inventory/size/privacy completion gate; **Verify Rip** remains the explicit whole-tree SHA-256 audit. Native ready files such as WMA/AT3 are retained; the original STFS/PKG/ZIP/game folder is not required.

`update-rip --check` is non-destructive and reports whether `validation/RIP_UPDATE_STATE.json` matches the exact current updater profile. The profile is a source fingerprint of updater-relevant toolkit modules, so it detects changes even when the public toolkit version string stays the same during a WIP series. `--force` runs the updater/profile migration even when that stored profile already matches, but still reuses heavy conversion outputs proven current. Use `--refresh-assets` when you deliberately want to force BBX extraction and GMX/TEX conversion again.

For safety, a normal update protects each component immediately before destructive replacement and refuses to overwrite content that differs from the recorded manifest unless `--force-modified` is explicitly used. If an update is interrupted after a component swap, `validation/RIP_UPDATE_IN_PROGRESS.json` allows the next run to recover. A pass that had already reached the final verification gate reuses its freshly written manifest instead of forcing an unnecessary whole-rip rehash. The journal and output stat cache are control-plane files and are excluded from output-manifest completeness checks. Host-created `Thumbs.db`, `desktop.ini`, and `.DS_Store` files are likewise ignored because they are not SIIG/game payload. Runtime failures print concise `ERROR:` lines; final update-verification failures also list their concrete issue kind/path.
