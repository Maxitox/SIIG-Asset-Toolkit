# Metadata Privacy

SIIG Asset Toolkit v1.5.1 removes absolute local filesystem routes from generated JSON metadata.

Privacy-safe behavior includes:

- BBX `manifest.json` stores only the source archive filename.
- glTF companion `.gltf.json` stores only the glTF filename.
- XACT `xwb_manifest.json` stores only the XWB filename and FFmpeg executable basename.
- Localization summaries store only input filenames.
- Diagnostic errors written to JSON have absolute routes redacted.
- glTF buffer and image URIs remain relative as required by the glTF package layout.

## Cleaning old exports

To sanitize JSON metadata created by toolkit v1.5 or earlier:

```bat
python siig_toolkit.py sanitize-json "C:\path\to\old_export" --backup
```

The command edits `.json` files in place. `--backup` preserves each changed original as
`filename.json.bak`. It does not modify `.gltf`, `.bin`, `.obj`, `.png`, `.wav`, or source assets.

If you do not need companion diagnostic metadata, files ending in `.gltf.json` or `.obj.json`
may also be deleted without affecting the corresponding model.
