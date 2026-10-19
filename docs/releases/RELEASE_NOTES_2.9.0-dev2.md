# SIIG Asset Toolkit 2.9.0-dev2

## Main milestone

This checkpoint removes two of the largest remaining GMX donor dependencies. `gltf2gmx-template --synthesize-native-schemas` can construct native `MESH`/`ARRY` vertex declarations and native `MTRL` parameter streams directly from glTF when no compatible template schema exists.

The mesh path supports standard `POSITION`, `NORMAL`, `TEXCOORD_0`, and `COLOR_0` attributes plus uint16 indices. The material path supports explicit `extras.gmxParameterSchema` records for decoded float, matrix and TXIF parameter types, or an inferred standard SIIG PBR schema when the extras are omitted.

The Mod Workspace glTF importer enables this mode automatically as a fallback while still preferring compatible native donors. The GMX Workbench exposes it as a separate advanced checkbox.

## Validation

The new dependency-free structural regression begins with a root-only GMX containing no MESH, ARRY, MTRL or SHAD donor records. From one glTF scene it synthesizes a new shader, material with a custom parameter, bone, mesh and arrays, repairs the root AABB, reparses the result, and verifies all attachments. The full source-only suite contains **76 tests**. The external dev25 **306/306** retail no-op evidence remains inherited and is not re-run from proprietary inputs.

## Boundaries

- Standard decoded vertex declarations can now be synthesized, but unknown/custom native vertex semantics are not invented.
- Decoded MTRL records can be synthesized, but novel parameter names only have runtime meaning if the selected game shader recognizes them.
- Native TEX payloads still require a compatible platform layout/header donor.
- MOTN/ANIM graph synthesis/import and platform shader microcode compilation remain unresolved.
- Fully template-free GMX creation is closer, but the current command still uses an existing GMX root/container as its host.
- PS3 NPDRM/SDAT re-encryption remains unresolved; audio replacement remains intentionally deferred.
