# GIGANTIC UFO runtime assembly — 2.10.0-dev15

## Result

GIGANTIC UFO is a locator-driven multipart visual entity. The canonical visual assembly is one main/root GMX plus thirty-six identical subordinate GMXs. No screenshot-based placement is required.

- Root: runtime type `0x9E`, `bos_003.gmx`, count 1.
- Children: runtime type `0xB5`, `bos_003a.gmx`, count 36.
- Child attachment locators: `lt_001` through `lt_036`, in strict numeric order.
- Additional renderer slots: three `0xB4` helper/control slots; they are not model assets and are excluded.

The child local matrix is identity. At runtime the renderer evaluates the named locator on the root and applies that transform to the matching B5 child. The toolkit preserves that relationship using `attach_to`, so the assembly is hierarchy-backed rather than a set of guessed world coordinates.

## Evidence

The retail Xbox visual class allocates one 0x9E root, three B4 helper/control slots, and thirty-six 0xB5 child entries. Its per-child update uses the root's native locator pointer/name table to resolve the transform for the matching subordinate model. June 10 Xbox retains the same 1/3/36 renderer layout, and retail PS3 independently retains the same root/child counts and locator-driven update pattern.

Fresh extraction of the retained retail Xbox package confirms that `bos_003.gmx` has exactly thirty-six `lt_001..lt_036` native locators and that `bos_003a.gmx` is the subordinate model used by B5. Neither GMX has native animation clips.

## Real-retail validation

- `bos_003.gmx`: 414,192 bytes; SHA-256 `047a469fd571611b67703d7af1287407302dc5f35a6fd4d0af0241748771a154`.
- `bos_003a.gmx`: 26,368 bytes; SHA-256 `e35c716606a38196639304a4cd3737be02d9dc5dc243800b5b4f067984c3d830`.
- Exported scene: 37 GMX instances, 74 meshes, 185 nodes, 0 animations.
- Bounds: X `-269.5926307..269.5926307`; Y `-269.5926307..269.5926307`; Z `-66.1033579..61.1107164`.

## Preset boundary

`gigantic_ufo_complete` is the evidence-backed complete visual hierarchy. It does not include B4 helper/control slots and it does not invent alternate activation-state presets because the persistent multipart construction itself is deterministic.

## Distribution boundary

No proprietary GMX files or generated retail glTFs are bundled in the source-only toolkit release.
