# DAT and MAP reverse-engineering notes

## Corrected MAP interpretation

The June 10 XEX draw path confirms that `Media/map` and `Media/generator` MAP files are independently scrolling **2D tile/sprite layers**, not tables that place 3D wall GMX models.

Each cell is encoded as:

```text
base_code = cell & 0x3F
flip_x    = bool(cell & 0x40)
flip_y    = bool(cell & 0x80)
```

- `0` is empty.
- `1..49` are one-based tile IDs.
- `0x40` reflects X.
- `0x80` reflects Y.
- both bits may be combined.

Runtime tile-set resources are now resolved:

| Resource ID | Texture resource |
|---:|---|
| 6 | `fence1_512` |
| 7 | `fence2_512` |
| 8 | `fence6_512a` |
| 9 | `fence3_512` |

Each atlas is interpreted as a 7×7 row-major table of 49 tile slots with a 144-pixel pitch and a 96×96 source region. The game places tile centers on a 30-unit grid. See `docs/formats/MAP_RENDERER_NOTES.md`, `docs/formats/MAP_TILE_LOOKUP.md`, `reference/tables/TILE_SET_TEXTURES.csv`, and `reference/tables/STAGE_TILE_SETS.csv`.

The exact gameplay labels for the three independently scrolling layers remain unresolved. Their SCROLL_01/02/03 X/Y velocity timelines and 30 Hz runtime integration are available in the Stage Explorer v8 proof-of-concept preview; the optional static combined view remains explicitly a zero-scroll composite because it is an inspection overlay, not the live viewport.

## Evidence used

The June 10, 2010 DebugOpt executable retained source-path, assertion, and diagnostic strings around the original loaders:

```text
StageGenerator:script is too large(index)
StageGenerator:script is too large(data)
scriptTime is over signed 16bit:%d
stageScriptBlockLoad
stageGenerate2DMap
WARNING:NO MAP BLOCK DATA:%s
```

The relevant loader functions are near `0x8226BC48` (DAT) and `0x8226CB28` (MAP). The stage executor at `0x820FB578` dispatches the decoded opcode in command word 1.

## DAT layout

```text
+0x00  u8      format version (observed: 1)
+0x01  be u16  command count

Repeated command:
        u8      word count
        be s16  delta frame
        be u16  opcode
        be s16  arguments[word_count - 2]
```

The loader accumulates each signed delta frame into an absolute frame number. The second word selects an opcode-specific handler. Remaining words are preserved both as signed values and exact hexadecimal words.

`dat2csv` exports record index, source offset, word count, delta/absolute frame, opcode ID/name, semantic category/summary/confidence where supported, and all raw arguments.

## MAP layout

```text
+0x00  char[4]  "MAP\0"
+0x04  be u32   layer count

Repeated layer:
        be u32   width
        be u32   height
        u8       cells[width * height]
```

Every supplied file has three layer descriptors, although a layer may have zero dimensions. Cells are row-major and are not compressed inside the MAP resource.

`map2png` can write:

- exact categorical cells;
- raw grayscale values;
- numeric CSV grids;
- actual tile images when a verified atlas PNG is supplied;
- a zero-scroll composite in draw order 2, 1, 0.

## Corpus validation

| Build | DAT files | Commands | MAP files | Layers | Failures |
|---|---:|---:|---:|---:|---:|
| May 9 prototype | 1,288 | 22,191 | 394 | 1,182 | 0 |
| May 11 prototype | 1,288 | 23,365 | 394 | 1,182 | 0 |
| June 10 prototype | 1,334 | 25,597 | 394 | 1,182 | 0 |
| Retail Xbox 360 | 1,334 | 25,597 | 394 | 1,182 | 0 |
| **Combined** | **5,244** | **96,750** | **1,576** | **4,728** | **0** |

The June/retail sets contain 1,258 generator DAT fragments plus 76 stage scripts, and 330 generator MAP blocks plus 64 stage MAP files.

## Remaining semantic work

- Additional opcode parameter names, units, and enums.
- Stable names for active unnamed opcodes.
- Exact gameplay role and frame-by-frame scroll trajectory of each MAP layer.
- Timed placement of selected DAT entities over the MAP only after their coordinate systems are proven.
- Complete 3D-stage reconstruction from stage/map/wall GMX, route, camera, collision, and DAT 3D-control resources.
