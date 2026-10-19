# SIIG Asset Toolkit 2.9.0-dev6

## Headline: fully template-free GMX compilation

`gltf2gmx-new` can now compile a native GMX from glTF **without supplying or reading an original GMX template**. Dev6 formalizes the canonical decoded 0x30-byte root and composes the previously proven native schema/scene/texture-reference/animation builders on top of it.

The canonical root sets `GMX\0`, root size `0x30`, final total stream size, and the proven minXYZ/maxXYZ geometry AABB. The still-unnamed `+0x08` word and `+0x28..+0x2F` tail default to zero. Advanced glTF extras may carry empirical values for those bytes, and the exporter records them, but the toolkit intentionally does not assign speculative semantics.

A new dependency-free regression starts from a plain glTF with no SIIG-native IDs and verifies a synthesized root plus TXIF, SHAD, MTRL, BONE, MOTN/ANIM, MESH and ARRY records; material/texture/mesh/bone links; 31-frame 30 Hz animation; total-size/AABB repair; glTF root provenance; and explicit unknown-root-byte overrides. The suite is **80/80**.

GMX Workbench adds **Create new GMX**. The existing template-backed import remains available and should still be preferred for fidelity-sensitive edits where preserving opaque bytes/chunks matters.

## Validation boundaries

- This is a structural/native compiler proof, not yet a hardware/emulator claim for arbitrary original scenes.
- Platform shader microcode compilation remains unresolved; SHAD synthesis covers the proven fixed metadata record only.
- Standard glTF skin/joint-weight import is not yet mapped.
- Remaining opaque/unnamed GMX fields are preserved in template mode or explicitly zero/overridden in canonical-root mode.
- The external dev25 306/306 mesh-bearing retail GMX no-op evidence remains inherited and proprietary corpus files are not bundled.
- Audio replacement/rebuilding remains intentionally deferred.
