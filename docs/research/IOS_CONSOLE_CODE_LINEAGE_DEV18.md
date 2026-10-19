# iOS -> console code lineage — dev18

## Result

The supplied iOS 4.1.0 executable is sufficiently symbolized to identify direct ancestors of several console Infinity Gene subsystems. The strongest result is not merely that the mobile and console files look alike: the loaders, logical tile renderer, scroll opcodes, 30 Hz time normalization, and 24-block generator retain the same data model and control structure across the port.

This report distinguishes three things deliberately:

1. **code/system lineage** — shared algorithms, structures, command IDs, and timing rules;
2. **serialized-format evolution** — especially mobile little-endian MAP headers becoming big-endian on console while DAT remains big-endian;
3. **authored-content changes** — console stages were often retuned or rewritten even when the underlying opcode sequence stayed recognizable.

No iOS executable bytes, decompilation, game scripts, or extracted assets are bundled.

## Function correspondence

`reference/tables/IOS_CONSOLE_FUNCTION_LINEAGE_DEV18.csv` records the detailed mapping. The strongest current anchors are:

| iOS ARMv7 | Console Xbox 360 | Relationship |
|---|---|---|
| `Invinf_LoadMap` `0x900CC` | `0x82239190` | same layer allocation/ownership model; MAP integer byte order changed |
| `calcMap` `0x8D020` | `0x82239608` | same three-layer fixed-point scroll accumulation and visible-range calculation |
| `drawMap2` `0x8E5EC` | `0x8223AC28` + `0x8223A1B0` | same `cell&0x3F`, 49-tile, X/Y-reflection logical renderer |
| `analyzeScript2` + `setMapLayerSpeed` | console SCROLL handlers | same opcodes `0x6E..0x70`, layer channels and 30 Hz velocity normalization; console adds 3D side effects |
| `stageScriptBlockLoad` `0xDF89C` | around `0x8226BC48` | same generator DAT-block append/cumulative-timeline design |
| `stageGenerateMap` `0xE06D8` | `0x8226CB28` + `0x8226CD30` | same 24-block `a_%03d.map`..`j_%03d.map` generator family |
| `analyzeScript` / `analyzeScript_FPS60` / `analyzeScript2` | June dispatcher `0x820FB578` | same low-range command language, substantially reorganized timing/dispatch architecture |

The exact Xbox address of the ordinary authored-DAT loader is still unresolved in the retained source-only console references. This is intentionally not conflated with `0x820FB578`, which is the execution dispatcher.

## MAP loader and renderer ancestry

### Mobile loader

`Invinf_LoadMap` validates a 1..59 map resource ID, reads a layer count, allocates an array of `(width,height)` descriptors plus an array of cell-buffer pointers, then allocates/copies one row-major byte buffer per nonempty layer.

Mobile MAP headers use little-endian `u32` fields. The console loader at `0x82239190` uses the same layer representation but reads the corresponding integers big-endian.

### Runtime update

`calcMap` processes two map-state banks and three layer channels. For active layers it:

- adds the per-layer X/Y velocity to fixed-point X/Y position;
- retains the loaded cell pointer and dimensions;
- derives clamped visible-column and visible-row ranges from the fixed-point position and map dimensions.

That makes `calcMap` a high-confidence ancestor of the console MAP runtime update routine at `0x82239608`, previously recovered as the scrolling/visible-range step.

### Tile encoding

`drawMap2` independently proves the mobile renderer uses the same logical cell encoding later recovered on console:

- `cell & 0x3F` = one-based tile code;
- zero = empty;
- subtract one and accept indices `0..48` = 49 tile variants;
- `0x40` = horizontal reflection;
- `0x80` = vertical reflection.

The console implementation preserves that logical model while replacing the platform-specific drawing path.

## Script timing: the ancestral 30 Hz model

The 30 Hz logical authoring model is now proven on both sides.

### iOS authored DAT load

For each command's first word, `Invinf_LoadScript` performs the equivalent of:

```text
runtime_delta = authored_delta * runtime_fps / 30
```

Thus a 30 Hz runtime retains authored ticks unchanged, while a 60 Hz runtime doubles the number of update ticks.

### iOS MAP speed

`setMapLayerSpeed` performs the inverse normalization:

```text
runtime_speed = authored_speed * 30 / runtime_fps
```

At 60 Hz the per-update scroll displacement is halved, preserving real-time displacement.

### Console evolution

Retail PS3 independently proves:

```text
runtime_updates        = authored_ticks * frame_multiplier
runtime_velocity       = authored_velocity / frame_multiplier
runtime_updates_per_sec = 30 * frame_multiplier
```

The invariant is the same. The architectural change is that mobile has separate primary `analyzeScript` and `analyzeScript_FPS60` enemy dispatchers, while the console code centralizes more of the 30/60 behavior through its runtime multiplier.

## Opcode-language expansion

A prior shorthand that the iOS script language ended at `0x83` was incomplete. The accurate split is:

- primary `analyzeScript`: serialized opcodes `0x02..0x83`;
- primary `analyzeScript_FPS60`: the same range;
- secondary `analyzeScript2`: `0x6E..0x8D`;
- therefore the effective mobile dispatcher frontier is **`0x8D`**;
- the June console table extends through **`0xCE`**.

The major console-only upper-range families in actual June data are:

- `0x96..0xAB`: expanded enemies and console/3D bosses;
- `0xB4..0xBE`: 3D background/wall/camera/field commands;
- `0xC8..0xCE`: Visualizer controls.

Across the supplied mobile authored+generator corpus, 87 opcode IDs are active. The June console table has 113 active IDs, with 73 active in both corpora. See `IOS_CONSOLE_OPCODE_FRONTIER_DEV18.csv`.

## Generator ancestry

The mobile generator is now concrete at code level.

`stageGenerateMapInit` creates exactly three generated output layers. Each receives **6,144 bytes**, with the allocation arithmetic reducing to:

```text
6144 = 24 blocks * 8 columns * 32 rows
```

`stageGenerateMap` advances a block counter until 24 pieces have been assembled and uses the familiar `a_%03d.map` through `j_%03d.map` resource families.

The console generator retains the same high-level architecture: `0x8226CD30` selects 24 named generator blocks and `0x8226CB28` appends their layers.

The resource corpus provides a second independent lineage marker:

| | iOS | Console |
|---|---:|---:|
| generator MAP files | 330 | 330 |
| nonempty layers | 645 | 645 |
| total stored cells | 121,472 | 242,944 |
| nonzero cells | 38,253 | 62,223 |

Console stored capacity is exactly twice iOS, but populated cells are not doubled. Therefore the console generator resources were expanded/transformed rather than simply duplicated byte-for-byte. The exact transformation remains unresolved.

## Authored-stage evolution

To avoid confusing engine ancestry with identical game content, `IOS_CONSOLE_STAGE_DELTA_DEV18.csv` compares the 18 shared normal stages 1-1 through 3-6.

Totals:

- iOS: **3,302 commands**;
- console: **3,166 commands**;
- opcode-sequence LCS: **3,028**, or **0.917020** of the larger aggregate stream;
- 10/18 stages retain an exactly identical opcode sequence length/order while still commonly changing arguments/timing;
- stage 3-6 is a major rewrite: 213 iOS commands versus 31 console commands.

Examples demonstrate why the relationship should be described as **shared engine + retuned/re-authored content**, not a direct file copy. Stage 1-1 has the same four-opcode sequence and same final frame but no complete record is byte/field-identical after decoding; several background, speed, and placement parameters changed. Stage 2-1 retains all 358 opcodes in the same order and overall duration, yet only 29 aligned command records are otherwise identical.

## Current boundary

High-confidence code ancestry is established for the 2D MAP loader/runtime/renderer, shared scroll commands, 30 Hz timing model, generator MAP assembly, and overall DAT execution architecture.

Still unresolved:

- exact Xbox address of the ordinary authored-DAT loader;
- exact console counterpart of `stageGenerateMapInit`;
- instruction-level old-vs-new handler matching for the majority of individual low-range enemy opcodes;
- exact reason the console generator MAP corpus has 2x mobile stored cell capacity;
- when, during console development, each new opcode family was introduced (prototype build diff is the next useful layer).
