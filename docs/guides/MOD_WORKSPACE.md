# Mod workspace workflow

`2.9.0-dev2` extends the mod-workspace project layer above the native asset builders. The goal is to remove manual BBX path surgery from ordinary modding experiments while keeping the original rip immutable.

## 1. Create a workspace

Start from a clean `rip-game` output:

```text
python siig_toolkit.py mod-init SIIG_Ripped -o My_SIIG_Mod --name "My SIIG Mod"
```

The workspace stores the source-rip path and a baseline SHA-256 for every top-level BBX archive. The game assets themselves remain in the user's rip; the toolkit release does not bundle them.

Use `mod-list` to discover stable archive/resource keys:

```text
python siig_toolkit.py mod-list My_SIIG_Mod
python siig_toolkit.py mod-list My_SIIG_Mod --archive <archive-key>
```

If the rip is moved later, pass `--rip <new-path>` to workspace commands.

## 2. Export an editable resource

For a supported native resource inside a BBX:

```text
python siig_toolkit.py mod-export My_SIIG_Mod <archive-key> <resource-path>
```

The command chooses the proven round-trip representation automatically:

- GMX -> fixed-layout edit JSON
- TEX -> PNG
- system-font CRP -> PNG
- DAT -> CSV
- MAP -> editable JSON plus previews
- ANM -> CSV
- COL -> PNG
- Bmap/Xmap/map4/map5 -> stage3D editable JSON
- wall/Xwall/stage_generate -> stagewall editable JSON

Edit the file under `editable/`. `mod-build` notices when the canonical editable file differs from its export baseline, compiles it back to the native format, and stages it automatically.

## 3. Edit whole localization archives

`text.bin` and `message.bin` are BBX archives whose human-editable representation describes the whole archive. Use:

```text
python siig_toolkit.py mod-export-archive My_SIIG_Mod <text-archive-key>
python siig_toolkit.py mod-export-archive My_SIIG_Mod <message-archive-key>
```

For `text.bin`, edit the recommended `text_strings.tsv` (legacy CSV/JSON exports remain available). For `message.bin`, edit the six `message_<language>_readable.nut` files. The build step recompiles the complete native localization BBX when any tracked file changes.

### Audio editing in Mod Workspace (dev24 WIP187)

**Xbox 360:** selecting `sound.bin` / `media/sound` in the Simple tree shows **AUDIO · EDIT**. **Open selected** exports only the named WAV files that feed `mod-build`. The replacement may change duration and sample rate. PCM16 WAVs with 1–6 channels are preserved natively; 7–64-channel input is accepted and downmixed to stereo. After **Refresh marks**, `mod-build` rewrites the XWB duration/format/play-region fields, remaps an existing loop region proportionally to the new sample count, repacks the wave-data segment, preserves untouched XMA2 streams byte-for-byte, and rebuilds the nested BBX archive. FFmpeg is required to decode editable WAVs from XMA2 source slots. Native XMA2 encoding is not bundled or claimed.

**PS3:** supported SBlk/989SND `.bnk` resources export their PS-ADPCM entries as PCM16 WAV files through ordinary `mod-export`. Replacements may change duration and sample rate. Multichannel input is accepted and downmixed to mono because SIIG's SBlk v3 records are natively mono. `mod-build` re-encodes PS-ADPCM, repacks the complete audio data section, rewrites subsequent stream offsets/sizes, selects the nearest representable SCREAM center-note/fine pitch for the requested rate, and regenerates loop/end frame-control flags while leaving untouched stream payloads unchanged.

Both paths use persistent baseline hashes, so audio status survives GUI restarts just like text/model edits. Structurally valid rebuilt banks are not proof of runtime acceptance; test the generated patch on an emulator or hardware copy. Large variable-size `sound.bin` changes can also exceed the existing conservative `.siigmod` whole-archive delta limit even though normal `mod-build` succeeds.

## 4. Stage an already-native replacement

If a format is not integrated into `mod-export`, or another tool produced the native file, stage it directly:

```text
python siig_toolkit.py mod-stage My_SIIG_Mod <archive-key> <resource-path> replacement.bin
```

A complete rebuilt BBX can be staged with:

```text
python siig_toolkit.py mod-stage-archive My_SIIG_Mod <archive-key> rebuilt_archive.bin
```

## Integrated glTF model + texture + animation import (2.9.0-dev6)

For a GMX already present in the source rip, the workspace can now compile an edited glTF and stage its linked native texture payloads in one operation:

```text
python siig_toolkit.py mod-import-gltf My_SIIG_Mod <archive-key> <model.gmx> edited.gltf
```

The command enables the GMX animation/texture/scene/mesh synchronization stack, stages the rebuilt GMX, compiles glTF translation/rotation/scale channels—including multi-bone clips and CUBICSPLINE samplers—into synchronized native 30 Hz `MOTN`/`ANIM` tracks, follows material `baseColorTexture` PNGs, and builds native TEX payloads. Existing same-layout TEX resources still use the byte-preserving template encoder first. If dimensions differ, or a genuinely new TXIF has no native TEX donor at all, `2.9.0-dev3` synthesizes a canonical layout from the workspace platform and can append the result as a new named BBX member.

Xbox synthesis follows the corpus-proven tiled 8_8_8_8 layout and therefore removes the previous same-dimension donor restriction. PS3 synthesis creates the understood linear A8R8G8B8 wrapper structurally; newly synthesized PS3 wrappers still require emulator/hardware validation before runtime compatibility is claimed. `--allow-reference-only` remains available for research cases where a native payload is intentionally omitted.

Because BBX entry count/name tables change when a member is added, `.siigmod` packaging switches that archive to a baseline-dependent **archive-level delta**. The clean BBX is still not redistributed.

## 5. Build and verify

```text
python siig_toolkit.py mod-build My_SIIG_Mod --clean
python siig_toolkit.py mod-verify My_SIIG_Mod
```

The build writes:

- `build/xbox360_replacements/` — **the Xbox 360 deployment output**, mirroring each changed original package path and containing one complete replacement per changed archive;
- `build/xbox360_replacements/XBOX360_REPLACEMENTS.json` — exact package path → replacement-file mapping plus rebuilt hashes/wrapper type;
- `build/xbox360_replacements/README.txt` — short deployment instructions;
- `build/MOD_BUILD_REPORT.json` — exact original/rebuilt hashes, affected resources, package status, and limitations.

Xbox builds no longer duplicate the same archive into `build/decompressed_bbx/` or `build/game_patch/`. Ordinary `.bin.gz` files are deterministic gzip streams; SIIG's Xbox `.bin.gz.sdat` files are also ordinary gzip streams and are emitted with that exact original filename. Raw archives such as `Media/sound.bin` remain raw BBX. These are complete replacement containers, not deltas. PS3 builds still retain decompressed BBX output where NPDRM/SDAT re-encryption is not implemented.

### Xbox 360 package-editor deployment

The desktop Simple workflow is now **Build replacement files → Verify build → Open Xbox replacements**. To deploy manually:

1. Work on a **copy** of the original Xbox 360 STFS package.
2. Open that copy in a compatible Xbox 360 package editor (for example Velocity, Horizon or Le Fluffie).
3. Open `build/xbox360_replacements/XBOX360_REPLACEMENTS.json`.
4. For each row, locate the listed `stfs_game_path` inside the STFS package.
5. Replace that file with the corresponding file under `build/xbox360_replacements/`. The replacement keeps the original game-relative path and wrapper (`.bin`, `.bin.gz`, or Xbox `.bin.gz.sdat`).
6. Save the modified STFS as a new file and test it before replacing any known-good package.

The toolkit deliberately does not edit the STFS container in place. This keeps the native-asset/BBX rebuild boundary separate from the external package-editor step and gives the user an explicit replacement set that can be inspected first.

## Optional: share a workspace as a baseline-dependent `.siigmod`

`.siigmod` is **not** the file to insert into an STFS package or other game container. It is an optional SIIG-to-SIIG sharing format: a compact baseline-dependent delta that another toolkit user can apply to the same clean rip to reconstruct the staged native changes.

Dev24 adds this distribution format without bundling clean source resources:

```text
python siig_toolkit.py mod-pack My_SIIG_Mod -o My_Mod.siigmod
python siig_toolkit.py mod-package-info My_Mod.siigmod
python siig_toolkit.py mod-apply My_Mod.siigmod SIIG_Ripped Applied_Mod --build
```

See [`MOD_PACKAGES.md`](MOD_PACKAGES.md) for the delta format, baseline checks, conflict policy, and distribution boundaries.

## Safety and current limits

- The source rip is treated as immutable. A source archive whose SHA-256 changed since `mod-init` is rejected until the workspace is recreated or pointed at the correct rip.
- Every rebuilt BBX is reparsed and verified before it is reported as built.
- `mod-verify` checks source baselines, rebuilt BBX hashes, and gzip payload identity.
- PS3 NPDRM/SDAT **re-encryption is not implemented**. PS3 SDAT-backed changes therefore remain available as rebuilt/decompressed BBX files for research or deployment methods that do not require recreating the signed/encrypted SDAT wrapper.
- A successfully rebuilt native asset or BBX does not automatically prove that every possible edit is accepted by the retail game. Keep changes small and test them in an appropriate emulator/test environment.
- GMX can synthesize mesh/scene/TXIF/MOTN/ANIM graph nodes, vertex/material schemas, canonical TEX payloads, and—through standalone `gltf2gmx-new`—a canonical GMX root without an original GMX. Mod Workspace `mod-import-gltf` remains replacement-oriented and still begins from the selected clean GMX resource. Remaining major boundaries include glTF skin/joint-weight import, compressed or mipmapped texture variants, platform shader compilation, opaque semantics, and runtime validation of fully original scenes.

## Retail corpus validation through dev24

The user-supplied retail Xbox corpus was used only as external validation input and is not bundled. Dev23 reproduced all 13 GMXs in `player.bin` byte-for-byte through the GMX editable/rebuild path. Retail `text.bin` (542 strings) and `message.bin` (284 groups, 1295 strings per language) also rebuilt byte-for-byte from their readable edit representations. Dev24 expands the same external validation to 307 GMXs and large retail DAT/MAP/stage-table corpora; see `validation/REAL_CORPUS_ROUNDTRIP_DEV24.json`. No retail payload is bundled.


### 2.9.0-dev2 schema fallback

`mod-import-gltf` now enables native schema synthesis as a fallback. Compatible original MESH/ARRY and MTRL schemas are still reused when present, but a genuinely new Blender mesh/material is no longer rejected solely because no matching donor declaration exists. The remaining texture payload step is still TEX-layout donor constrained.


### Rigid skin compatibility (2.9.0-dev7)

`Import glTF + TEX` now enables the rigid-skin compatibility pass automatically. A Blender/glTF skinned object may be staged when every vertex is assigned to the same single joint with unit weight; the mesh/material is attached to that native BONE. True blended weights are rejected before anything is staged. This keeps mod packages inside the representation confirmed by the retail GMX corpus.
## Desktop GUI Simple-mode asset tree (dev24 WIP184)

Desktop GUI **0.48.0-dev24** makes **List Assets** part of the beginner workflow. After creating or choosing a workspace, click **List Assets** to reveal an archive/resource tree directly below the Mod Workspace buttons.

The tree is intentionally a lightweight modding browser rather than a second Asset Viewer. It shows the archive hierarchy, resource name/type/size and one persistent workspace state:

- **Untouched** — no editable export or staged replacement exists.
- **Exported** — an editable representation exists and still matches its export baseline.
- **Edited** — the editable representation differs from its baseline.
- **Staged** — a native replacement has been staged/built for the resource.
- **Added** — the workspace contains a genuinely new archive member.

Double-click a resource, or select it and press **Open selected**. For a supported untouched resource the GUI runs the normal audited `mod-export` path, refreshes the tree, and opens the resulting editable file. Supported whole localization archives (`text.bin` / `message.bin`) can likewise be opened from their archive row. After saving a file in an external editor, press **Refresh marks** to recalculate its state. Build and Verify also refresh an already-open tree automatically.

The marks are derived from `meta/edits` baseline hashes plus staged/addition files. They therefore survive closing/reopening the GUI and do not depend on in-memory click history. Selecting a GMX row also fills the Advanced-mode archive/resource fields so the same selection can be used with **Import glTF + TEX**.

