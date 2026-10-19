# SIIG Asset Toolkit 2.9.0-dev3

## Donor-free native TEX synthesis

`2.9.0-dev3` removes the same-layout TEX donor requirement for newly imported textures. `png2tex` now has two modes: `--template` preserves an existing native layout byte-for-byte outside edited texels, while `--platform xbox360|ps3` synthesizes a canonical native wrapper directly from PNG dimensions and RGBA pixels.

Xbox 360 synthesis is grounded in the uniform layout observed across all 54 supplied textures: Xenos format 6 (`8_8_8_8`), endian mode 2, tiled addressing, Z/Y/X/W swizzle, 32-pixel pitch alignment and a 32-row-aligned tiled allocation. The new regression uses 37x19 pixels specifically so neither pitch nor allocation can be inherited from the previous 2x2 fixture.

PS3 synthesis creates the understood 0x80-byte linear A8R8G8B8 wrapper with recalculated data offset, payload size and dimensions. It passes structural RGBA round-trip testing; runtime acceptance of arbitrary newly synthesized PS3 wrapper unknown fields remains explicitly unclaimed.

## Mod Workspace integration

`mod-import-gltf` still prefers an existing compatible TEX for replacements because that preserves every unknown byte. When the PNG dimensions no longer match, it falls back to canonical synthesis for the donor's platform. When no TEX donor exists at all, the workspace platform from the verified rip selects the native layout.

The integrated selftest now starts with a BBX containing only the GMX—no TEX payload. An edited glTF introduces `new_albedo.png` at 37x19; the toolkit creates `new_albedo.tex`, adds it to BBX, verifies the GMX TXIF relationship, packages the BBX member addition as a baseline-dependent archive delta, and reproduces the exact rebuilt BBX in a fresh workspace.

## Validation

- 77/77 dependency-free selftests.
- Donor-free Xbox 37x19 TEX encode/decode equality.
- Structural donor-free PS3 5x3 wrapper encode/decode equality.
- End-to-end glTF -> GMX/TXIF -> synthesized TEX -> BBX -> `.siigmod` proof with no source TEX donor.
- Dev25 external retail GMX 306/306 no-op evidence remains inherited rather than re-run from proprietary inputs.

## Remaining boundaries

Compressed/mipmapped native texture variants are not synthesized. Newly invented PS3 wrappers need runtime validation. GMX animation graph creation (`MOTN`/`ANIM`), platform shader compilation, opaque chunk semantics and fully from-scratch GMX root construction remain future work. Audio replacement remains deferred.
