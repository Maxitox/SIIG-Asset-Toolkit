# Quick Start — SIIG Asset Toolkit 2.10.0-dev24

This is the shortest supported path from an original **Space Invaders Infinity Gene** package/folder to a verified local asset rip.

## What you need

- Python 3 with Tkinter available.
- Your own Xbox 360/PS3 game package, ZIP, or already-extracted game folder.
- FFmpeg is optional but recommended for Xbox 360 XACT/XMA audio -> WAV and for Visualizer browser previews of Xbox WMA / PS3 AT3 BGM. The toolkit does not bundle FFmpeg.

The toolkit is local-only. It does not upload game data.

## Recommended Windows workflow

1. Double-click `SIIG_GUI.bat`.
2. Open **Game Rip**.
3. Choose or drag in one game/package/folder.
4. Choose the output folder. The default `SIIG_Ripped` name is fine.
5. Leave **Resume/reuse unchanged work** enabled. This makes interrupted/repeated runs reuse verified work.
6. Leave **Separate solid + outline (native/default)** selected unless you specifically want another GMX display pass.
7. Optional: click **Check input** for a non-destructive preflight.
8. Click **Rip + verify**.

A normal successful run ends with `verification passed` and `rip completed successfully`. The GUI can then open the generated Asset Viewer automatically. It also fills **Mod Workspace → Verified game rip** with the completed output folder.

## What Rip + verify produces

The exact contents depend on platform, but the important top-level outputs are:

- `assets/` — extracted native resources plus converted resources next to their source archive.
- `converted_assets/` — conversion-oriented copies where applicable.
- `audio/` — decoded WAV output while retaining original extracted banks/resources.
- `structured/` — decoded DAT/MAP/stage/shader inspection exports.
- `systemfont/` — recovered font atlas/metadata helpers.
- `stage_explorer/SIIG_Stage_Explorer.html` — offline stage/timeline/route explorer.
- `visualizer_simulator/SIIG_Visualizer_Simulator.html` — offline Visualizer reconstruction.
- `asset_viewer/SIIG_Asset_Viewer.html` — browsable model/image/audio/text/data index.
- `validation/RIP_REPORT.txt` — human-readable completion report.
- `validation/OUTPUT_MANIFEST.json` and `.sha256` — deterministic SHA-256 inventory of the rip.
- `validation/RIP_VERIFICATION.json` — automatic completion-gate result.

The generated Asset Viewer should normally be your first stop after a rip.

## Resume safety

Resume is designed to fail closed rather than assume a changed input is safe:

- outer ZIP/STFS/PKG staging is content-addressed by source SHA-256;
- ordinary gzip/BBX archives are skipped only when their source hash and conversion profile still match;
- PS3 SDAT plaintext is reused only when a sidecar matches both the encrypted SDAT SHA-256 and cached plaintext SHA-256;
- safe unchanged-package resumes may reuse Stage Explorer, Visualizer Simulator and Asset Viewer outputs;
- Asset Viewer resume preserves already-valid generated thumbnails instead of rebuilding every thumbnail unnecessarily.

If you want a completely fresh run, disable Resume or use `--clean` from the CLI.

## Verify an existing rip later

GUI: **Game Rip → Verify existing rip**.

CLI:

```text
python siig_toolkit.py verify-rip SIIG_Ripped
```

`verify-rip` is an alias of `verify-output`. This explicit verification re-hashes every tracked file and checks privacy metadata, missing/untracked files, sizes and partial-file state.

## Start a mod workspace

After a successful Game Rip, switch to **Mod Workspace**. The verified rip field should already point at the finished rip.

Typical flow:

1. Choose a workspace folder.
2. Create/initialize the workspace.
3. Export/edit/import supported assets or use the GMX Workbench.
4. **Build**.
5. **Verify**.
6. **Pack** to create a baseline-dependent `.siigmod` delta package.

`.siigmod` is designed not to redistribute complete clean source assets.

## Command-line equivalent

```text
python siig_toolkit.py rip-game GAME_PACKAGE_OR_FOLDER -o SIIG_Ripped --resume
python siig_toolkit.py verify-rip SIIG_Ripped
```

The first command already creates a fresh SHA-256 manifest and performs the automatic completion gate. The second command is the later independent full-byte re-hash.

## Current boundaries

A usable rip does not mean every reverse-engineering question is solved. The living dev24 boundary registry still documents evidence-absent shader/GMX/runtime semantics, exact names not present in name-bearing evidence, edited-asset runtime-acceptance questions, and external Blender UI validation. Those are research boundaries, not blockers for normal extraction/browsing.

The project license is intentionally still unselected pending the project owner's later decision. See `docs/project/PROJECT_LICENSE_STATUS.md`, `docs/project/CREDITS.md`, `docs/project/THIRD_PARTY_NOTICES.md`, and `docs/project/AI_DISCLOSURE.md` before redistribution.
