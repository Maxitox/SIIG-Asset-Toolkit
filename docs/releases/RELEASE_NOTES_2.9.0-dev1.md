# SIIG Asset Toolkit 2.9.0-dev1

`2.9.0-dev1` starts a new minor feature line after the unusually long `2.8.0-dev1..dev28` sequence. The project now requires a minor-version review no later than `dev8`.

## Main milestone

The dev28 GMX TXIF compiler is now connected to the native texture and mod-package workflow through `mod-import-gltf`. An edited glTF can compile to native GMX while linked PNG `baseColorTexture` images are rebuilt to Xbox 360/PS3 TEX and staged in the same mod workspace operation.

When a texture reuses an existing TXIF filename, the existing TEX BBX member is replaced. When the glTF allocates a new TXIF name, the workspace can append a new named BBX member using a compatible donor TEX layout. The BBX hash identifier is recomputed, the archive's count/name/hash tables are rebuilt, and the result is reparsed before it is accepted.

`.siigmod` packages containing BBX member additions use one baseline-dependent archive-level binary delta. This preserves the package rule that clean original assets are not redistributed.

The desktop GUI Mod Workspace now exposes an **Import glTF + TEX** action over the same CLI/compiler path.

## Validation

The new synthetic regression proves edited glTF -> new TXIF -> PNG -> native TEX -> new BBX member -> mod build/verify -> `.siigmod` -> exact fresh-workspace reconstruction. The dependency-free suite contains **75 tests**. External dev25 306/306 retail GMX no-op evidence remains inherited and is not re-run from proprietary inputs in this source package.

## Boundaries

- New TEX payloads still clone a compatible native TEX layout and therefore retain donor dimension/format constraints.
- Arbitrary GMX vertex declarations and material parameter schemas remain donor-dependent.
- MOTN/ANIM graph synthesis/import, platform shader compilation, and fully template-free GMX construction remain unresolved.
- PS3 NPDRM/SDAT re-encryption remains unresolved.
- Audio replacement/rebuilding remains intentionally deferred.
