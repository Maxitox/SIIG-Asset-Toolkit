# SIIG MAP renderer findings

## Corrected interpretation

The `Media/map` and `Media/generator` `.map` resources are independently
scrolling 2D tile/sprite maps used by the Infinity Gene core renderer. They are
not tables that place 3D wall GMX models.

## MAP structure

```text
+0x00  char[4]  "MAP\0"
+0x04  be u32   layer count

Repeated layer:
        be u32   width
        be u32   height
        u8       cells[width * height]
```

`Function_82239190` allocates and copies the layers. The loader diagnostic is
`Invinf_LoadMap`, and the source path embedded in the prototype places the
subsystem in `InfinityGene/Game/invinfGame.cpp`.

## Cell encoding and draw path

`Function_8223AC28` reads each cell:

```text
base_code = cell & 0x3F
flip_bits = (cell >> 6) & 3
```

- `0` is empty.
- `1..49` are one-based tile codes; the renderer subtracts one and accepts
  indices `0..48`.
- `0x40` reflects X.
- `0x80` reflects Y.
- `0xC0` applies both reflections.

`Function_8223A1B0` selects base/X/Y variants and submits the sprite. Cells use
a 30-unit grid, with centers at `scroll_x + column*30 + 15` and
`scroll_y + row*30 + 15`.

## Resolved tile-set resources

`Function_822407D8` registers four consecutive resources through
`Function_821CEBA8(base=6, count=4, descriptor=0x820481C8)`:

| ID | Texture |
|---:|---|
| 6 | `fence1_512.png` |
| 7 | `fence2_512.png` |
| 8 | `fence6_512a.png` |
| 9 | `fence3_512.png` |

The 75-stage table at `0x8204BD50` selects IDs 6, 7, or 8. This closes the
previously unresolved numeric-ID-to-filename link.

## Atlas layout

The 49 tile codes map row-major to a 7×7 atlas. Each slot has a 144-pixel pitch
and a 96×96 source rectangle. The executable's 3× coordinate path implies a
32-unit logical sprite drawn on the confirmed 30-unit MAP step. See
`docs/formats/MAP_TILE_LOOKUP.md`, `reference/tables/MAP_TILE_LOOKUP.csv`, and
`validation/MAP_ATLAS_VALIDATION.json`.

## Layers and composite limits

The three arrays scroll independently and are submitted in order 2, 1, 0. Stage
Explorer v7 reconstructs the SCROLL_01/02/03 X/Y velocity timelines at the logical
30 Hz authored timebase. Its optional zero-scroll composite remains an inspection
overlay rather than a claimed live gameplay viewport; exact player-facing layer
labels and complete gameplay viewport/camera composition remain unresolved.

## Generator MAPs

`Function_8226CB28` appends small generator MAP blocks into larger buffers, and
`Function_8226CD30` selects blocks with names such as `a_000.map`. They are
reusable 2D tile-pattern blocks, not wall-model placement data.

## Corpus validation

Stage MAP archive: 64 files, 573,984 cells, 150,480 nonzero cells, 49 valid
base tile IDs, and no decoded ID above 49. Generator MAP archive: 330 files,
242,944 cells, 62,223 nonzero cells, and no decoded ID above 49.

## Remaining work

Runtime MAP motion now has recovered per-layer scroll state over time. Remaining
fidelity work is exact gameplay viewport/camera composition and trustworthy
player-facing layer labels. DAT spawn/object markers should remain a separate overlay until the
coordinate-bearing opcode fields are proven handler by handler. A true 3D
stage reconstruction follows the separate `3ddata/stage`, `3ddata/map`,
`3ddata/wall`, route, camera, collision, and DAT 3D-control paths.
