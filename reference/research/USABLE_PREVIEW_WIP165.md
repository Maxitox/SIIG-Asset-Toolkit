# Usable-preview retail validation — dev24 WIP165

WIP165 turns the existing research/development toolkit into a practical first-run workflow without claiming that every remaining reverse-engineering boundary is solved.

## Canonical retail end-to-end validation

Two project-owner retail inputs were exercised locally with the current dev24 workflow. The proprietary packages and generated outputs are validation inputs only and are **not bundled**.

### Xbox 360

- Direct ZIP -> nested LIVE/STFS -> game filesystem path.
- 2,593 BBX resources; 0 BBX hash mismatches.
- 1,351 PNG textures, 486 glTF models, 94 OBJ compatibility exports, 86 WAV streams and 53 ready WMA files.
- Stage Explorer: 92 entries / 17,335 DAT commands.
- Visualizer Simulator: 30 timelines / 243 commands.
- Asset Viewer: 9,407 indexed files; 8,669 previewable items; 0 missing preview thumbnails.
- Output manifest: 16,567 tracked files.
- Independent full re-hash: 16,567/16,567 checked, 0 integrity/privacy issues.

### PlayStation 3

- Direct retail PKG input.
- All six SIIG SDAT resources internally authenticated/decrypted: 18 authenticated blocks, no external fallback.
- 2,593 BBX resources; 0 BBX hash mismatches.
- 1,285 PNG textures, 486 glTF models, 94 OBJ compatibility exports and 84 WAV streams.
- Stage Explorer: 92 entries / 17,335 DAT commands.
- Visualizer Simulator: 30 timelines / 243 commands.
- Asset Viewer: 9,340 indexed files; 8,626 previewable items; 0 missing preview thumbnails.
- Output manifest: 16,422 tracked files.
- Independent full re-hash: 16,422/16,422 checked, 0 integrity/privacy issues.

## WIP165 usability hardening

- Desktop GUI 0.42.0-dev24 uses **Rip + verify** as the normal full-game action.
- User-selected working folders/options persist in per-user local GUI settings; they are never written into rip or mod outputs.
- A verified rip is handed directly to Mod Workspace and may automatically open the already-generated Asset Viewer.
- Outer ZIP/STFS/PKG staging is content-addressed for resume; nested packages use the same cache.
- Ordinary BBX/gzip inputs can fast-skip before decompression when their SHA-bound conversion profile is unchanged.
- PS3 SDAT resume now reuses a plaintext only when a sidecar matches both the exact encrypted-source SHA-256 and cached-plaintext SHA-256. A changed source or plaintext fails closed to normal authenticated decryption.
- Stage Explorer, Visualizer Simulator and Asset Viewer are reused on a safe unchanged-package resume; Asset Viewer can retain already-valid generated thumbnails.
- Output-manifest and explicit verification hashing use a bounded thread pool while preserving deterministic sorted manifest order.
- The automatic completion gate does not immediately hash every byte twice: the fresh manifest is authoritative, then inventory/sizes/partial files/privacy are independently checked. `verify-output` / `verify-rip` remains the explicit later full re-hash path.

## What this does not claim

WIP165 does not close evidence-absent research items merely to call the build usable. Runtime-only shader/compiler questions, opaque GMX semantics, exact gameplay names without name-bearing evidence, arbitrary edited-scene runtime acceptance, and other living boundary-registry items remain documented separately. In-Blender UI testing also remains an external-environment validation item.

The project license remains intentionally unselected until the project owner decides meaningful development/research work is exhausted.
