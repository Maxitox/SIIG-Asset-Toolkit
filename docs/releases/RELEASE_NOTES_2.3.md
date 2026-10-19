# SIIG Asset Toolkit 2.3.0 release notes

Version 2.3.0 adds the three most requested expansion features and a group of workflow improvements.

## New features

### BBX repacker

- New `repack-bbx` command rebuilds archives from `extract` output and `manifest.json`.
- Preserves order, internal names, unnamed identifiers, mode, seed, reserved header bytes, sorted hash index, and 16-byte layout.
- Recomputes named hashes by default and supports intentional identifier preservation.
- Supports deterministic gzip output, extra-file appending, atomic writes, and post-build verification.
- Existing extraction manifests now record payload/archive SHA-256 values and layout metadata.
- The unchanged retail `map.bin` test is byte-for-byte identical after extract/repack.

### Blender add-on 0.1.0

- Imports individual or multiple GMX files.
- Recursive folder import from a sidebar panel.
- Uses the toolkit's verified glTF exporter and Blender's built-in glTF importer.
- Supports texture roots, V flip, collection grouping, missing-texture notices, and source custom properties.

### Offline HTML asset viewer

- New `asset-viewer` command indexes full rips or arbitrary extracted folders.
- Search, filters, size/hash inventory, image and browser-audio previews, text previews, glTF summaries, and interactive wireframes.
- Single HTML file with bounded embedded previews and no network requests.
- `rip-game` generates it automatically.
- New local-only `serve` command avoids browser `file://` restrictions.

## QoL

- New Windows drag-and-drop launchers for BBX extraction, BBX repacking, asset-viewer generation, and local serving.
- Full-rip reports now include asset-viewer status.
- `selftest` expands from 9 to 11 checks with BBX repacking and HTML viewer coverage.
- Added dedicated repacker, viewer, Blender, and source-exclusion documentation.

## Cautions

- Modified BBX archives require in-game or emulator testing. Byte-identical unchanged round trips do not guarantee that every edit is semantically valid.
- The Blender add-on was not executed inside Blender in the build environment.
- Generated asset viewers may embed game-derived media and should remain private unless redistribution is permitted.
