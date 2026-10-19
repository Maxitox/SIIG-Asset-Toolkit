# SIIG 3D stage tables

## Path and placement records

`Bmap*.bin`, `Xmap*.bin`, and the same-layout `map4_*.bin` / `map5_*.bin` resources contain fixed `0x118`-byte records. These are separate from the 2D `MAP\0` tile resources.

```text
record +0x00  placement[0] (0x34 bytes)
       +0x34  placement[1]
       +0x68  placement[2]
       +0x9C  placement[3]
       +0xD0  be f32 cell_step[3]
       +0xDC  be f32 auxiliary_points[5][3]
```

Each placement is:

```text
+0x00  char[16] model name (`notuse` is empty)
+0x10  be f32 position[3]
+0x1C  be f32 stored_scale[3] (runtime multiplies each component by 5.0)
+0x28  be f32 rotation_degrees[3] (runtime converts to radians)
```

The executable preloads each used placement as `<name>.gmx`. It accumulates `cell_step` into an 800-unit path and constructs an 800×800×800 lookup box around each path-cell center. A zero step marks the end when it occurs before file capacity. The five trailing vectors are homogeneous optional route-point slots: the runtime scans all five and concatenates every nonzero point, in slot and record order, into the route source used to build the spline. If record 0 contributes no point, the runtime inserts an origin before continuing. Across the supplied 47-file corpus, only slot 2 is used (19,562 nonzero points across 19,563 active records). Slots 0, 1, 3, and 4 are supported but unused, so no separate role should be assigned to them.

The placement transform is also recovered. Retail Xbox 360 and PS3 consume each placement with the same row-vector order `S * Rz(z) * Rx(x) * Ry(y) * T`: the stored scale is first multiplied by 5, the three stored degree values become the Z/X/Y rotations in that multiplication order, and translation is the placement origin. Stage Explorer uses this exact order when transforming GMX root-AABB corners; it no longer leaves proxy boxes axis-aligned. See `reference/research/STAGE_PLACEMENT_TRANSFORM_DEV24.md`.

Record 0 slot 2 supplies the initial `FieldPos`. If it is zero, the runtime falls back to record 0 placement slot 0's stored position; this occurs only in `Bmap16.bin`. The JSON export records both `initial_field_position` and `initial_field_position_source`.

`stage3dmap` writes lossless JSON, path CSV, placement CSV, an OBJ polyline of cell centers, and the executable-ordered runtime route-source control points as `.route_source.csv` / `.route_source.obj`. The latter are source/control points, not the engine-resampled spline.

`route-resample` goes one step further and applies the retail non-loop segment algorithm to those control points at a constant user-supplied spacing. It reproduces the linear write-after-step sampler (`0x00158790`), cubic Hermite evaluator (`0x00158A28`), tangent-axis state machine (`0x00158D38`), straight/curve classifier (`0x00159298`), source-index advancement (`0x00159560`), and initial FieldPos/source-index selection (`0x0015A338`). The final source point remains look-ahead/tangent context rather than being automatically traversed.

`route-resample` remains a deterministic fixed-spacing analysis exporter. Dev4 added `route-playback`, which couples a stage3d table and DAT script through the executable-backed SCROLL_02 spacing timeline. WIP160 additionally resolves the deterministic normal-stage filename correspondence: `XmapW_S.bin` and `map4_/map5_` resources may omit the DAT argument (or use `auto`) and the CLI selects `levelW_stageS.dat`, cross-checking the resulting stage number against `reference/tables/STAGE_PAIRING.csv`. Explicit DAT arguments remain supported. Playback reproduces modulo loop wrapping, non-loop termination, one-sample-per-runtime-update advancement, and the linear mid-segment spacing-change rebuild from current `FieldPos`. Active Hermite segments intentionally do not take that rebuild path. Automatic inference is limited to deterministic normal-stage names. `Bmap13`/`Bmap15` retain the stronger `WARNING[12]`/`WARNING[14]` special-reload evidence. WIP164 cross-checks an explicitly supplied DAT against those WARNING requests and reports the authored request frame(s), competing special requests, and the recovered reload-chain normalized frame 130. That still proves request compatibility rather than a unique DAT owner or route-object initialization frame, so special/boss DAT selection and `--start-frame` remain explicit.

Automatic filename inference is intentionally limited to the deterministic normal-stage `XmapW_S` / `map4_/map5_` namespace. It does **not** guess one owning DAT for `Bmap` boss/special routes, and it does not infer the gameplay frame at which any route object is instantiated. `Bmap13`/`Bmap15` have direct `WARNING [12]` / `WARNING [14]` special-reload evidence, but that proves the resource transition rather than a unique DAT owner or creation frame. `--start-frame` therefore remains explicit, and the latest SCROLL_02 at/before that authored frame becomes the initial spacing. Main retail gameplay scene `0x02` uses frame multiplier 2; `--frame-multiplier 1` remains available for 30-update scenes. Orientation, camera transforms, field-model animation, and scenegraph side effects remain outside the playback model.

Examples:

```text
python siig_toolkit.py route-resample Bmap01.bin -o route_debug --spacing 100
python siig_toolkit.py route-playback Xmap3_1.bin -o route_runtime --frame-multiplier 2
```

Validation found 47 same-layout files, 19,563 active path records, 23,830 used placements, and 77 unique referenced model names. Every model reference resolves to a supplied GMX file. All 77 path/wall/generator stage files compared between the June 10 prototype and retail are byte-identical.

## Wall strips and generator candidates

`wall*.bin`, `Xwall*.bin`, and `stage_generate.bin` use 20-byte records:

```text
+0x00  char[16] name
+0x10  be u32 value
```

For wall tables, `value` is a repeat count. The executable clamps values above 16, then expands each named strip element that many times. `notuse` creates an empty segment. For `stage_generate.bin`, nonzero values mark the 53 names eligible for runtime selection.

`stagewall` exports both forms to CSV and JSON without discarding raw values.

### XEX evidence

Key June 10 functions include:

- `0x82101850`: scans `0x118` records and preloads four GMX names
- `0x82102610`: accumulates steps and constructs 800-unit cell boxes
- `0x82102120`: exposes up to five reserved route-point vector slots
- `0x82101AD0`: loads `wall` / `Xwall` data
- `0x82105D50`: copies 20-byte wall records and clamps counts to 16
- `0x82106478`: expands the wall strip according to each count
- `0x82101C40`: selects enabled entries from `stage_generate.bin`


## Native table rebuilding (dev22)

`stage3dmap` now writes `*.stage3d.edit.json`. Every active `0x118` record is fully described by its four placement records, cell-step vector, and five route-point vectors, so `stage3d-build` can synthesize those records deterministically:

```bat
python siig_toolkit.py stage3dmap Bmap15.bin -o stage3d_edit
python siig_toolkit.py stage3d-build stage3d_edit\Bmap15.bin.stage3d.edit.json -o Bmap15_mod.bin
```

Supply `--template Bmap15.bin` to preserve inactive records or tail bytes exactly. Active records must be contiguous and may not use an all-zero cell-step because that is the native end sentinel.

The same dev22 release also adds `stagewall-build` for the fixed 20-byte wall/Xwall/stage-generator records (`char name[16]` + big-endian `u32 value`). Its input can be the exporter CSV or `*.stagewall.edit.json`.
