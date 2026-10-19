# SIIG Asset Toolkit 2.5.1 release notes

Version 2.5.1 is a release-layout and documentation-maintenance update.

## Organized root

The toolkit root now contains only the command-line modules, Windows launchers, README, changelog, version file, and integrity manifest. Documentation and supporting data are grouped under:

- `docs/` — guides, format notes, project records, research notes, and release history
- `reference/` — CSV tables, provenance JSON/CSV, system-font data, and samples
- `validation/` — validation reports
- `tools/` — the Ghidra label helper
- `addons/` — the Blender add-on package and source

No research files were removed. The root was reduced from 75 files to 18.

## Compatibility

Runtime lookups use the new locations and retain fallbacks for legacy root-level stage tables and system-font support files. Existing command syntax and Windows launchers are unchanged.

## Documentation

`docs/README.md` is the central index for all guides, format notes, provenance, tables, validations, tools, and add-ons.
