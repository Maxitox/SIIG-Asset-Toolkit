# SIIG MAP tile-to-atlas lookup

## Proven resource mapping

The June 10 DebugOpt executable registers four consecutive render resources in
`Function_822407D8`:

```text
Function_821CEBA8(resource_manager, base_id=6, count=4, descriptor=0x820481C8)
```

`Function_821CEBA8` walks the descriptor in order, so the four entries resolve
to:

| Resource ID | Texture |
|---:|---|
| 6 | `fence1_512.png` |
| 7 | `fence2_512.png` |
| 8 | `fence6_512a.png` |
| 9 | `fence3_512.png` |

The 75-stage runtime table selects IDs 6, 7, or 8. ID 9 is registered by the
same loader but is not selected by that stage table.

## Tile lookup

The MAP renderer masks a cell with `0x3F`, rejects zero, subtracts one, and
passes the resulting index `0..48` to the tile renderer. Atlas inspection and
full-stage rendering establish a row-major 7×7 table:

```text
index  = tile_id - 1
column = index % 7
row    = index // 7
source_x = column * 144
source_y = row * 144
source rectangle = 96 × 96 pixels
```

`reference/tables/MAP_TILE_LOOKUP.csv` expands this formula for all 49 IDs.

## Transform and placement

- `0x40`: horizontal reflection.
- `0x80`: vertical reflection.
- Both flags may be combined.
- MAP cell centers are 30 units apart at `column*30+15`, `row*30+15`, before
  the layer-specific scroll offset.
- The 96-pixel atlas region corresponds to a 32-unit logical sprite in the
  executable's 3× coordinate path, so adjacent 30-unit MAP cells overlap by
  two logical units. This explains the continuous fence joins.

The 32-unit size is a renderer inference supported by the executable scale and
the atlas geometry. The 30-unit MAP step, tile IDs, and flip bits are directly
confirmed by the load/draw path.

## Validation

All six converted fence atlases are 1152×1152. Every non-transparent pixel lies
inside the 96×96 source rectangle of its 144×144 pitch slot. See
`validation/MAP_ATLAS_VALIDATION.json` for hashes, occupied tile IDs, and per-tile alpha
bounds.
