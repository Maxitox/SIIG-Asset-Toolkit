# Offline Stage Explorer v8 — proof of concept

Run after extraction:

> **Maturity: proof of concept / research inspector.** This tool is useful for inspecting decoded MAP cells, DAT commands, runtime pairings, and recovered route/placement metadata. It is **not** a faithful or frame-accurate recreation of the in-game stage renderer or stage playback. The experimental motion preview executes only recovered SCROLL vectors, and the browser presentation can still differ visibly from native output.


```text
python siig_toolkit.py stageviz <SIIG_Ripped> -o stage_explorer
```

The generated HTML is self-contained and makes no network requests. The locator accepts the Xbox `Media/script` + `Media/map` layout and the PS3 `USRDIR/script` + `USRDIR/map` layout directly; platform-native folders do not need to be renamed.

## MAP rendering

Verified resource mapping: 6 → `fence1_512.png`, 7 → `fence2_512.png`, 8 → `fence6_512a.png`, 9 → `fence3_512.png`. Tiles use the confirmed 7×7 atlas, 144-pixel pitch, 96×96 source rectangles, one-based IDs 1–49, and 0x40/0x80 X/Y reflections.

## Experimental SCROLL preview

Explorer v8 carries decoded SCROLL events into the dataset for inspection:

- `SCROLL_01` → MAP layer 0 X/Y velocity
- `SCROLL_02` → MAP layer 1 X/Y velocity
- `SCROLL_03` → MAP layer 2 X/Y velocity

The experimental viewport integrates the signed 8.8 velocities at the logical 30 Hz authoring timebase established by executable analysis. Across the retained retail explorer corpus there are 92 entries, 78 runtime pairings, and 468 scroll events. Its controls preview only this recovered scroll state; they do **not** execute the other stage DAT commands or reproduce native gameplay sequencing.

## Limits

The individual decoded MAP layers are the primary inspection surface. The zero-scroll composite and motion/3D panels are secondary previews. Converted TEX/atlas pixels, browser scaling/sampling, native camera composition, full DAT execution, entity simulation, collision, and other stage behavior remain outside a faithful-renderer claim.

## Experimental level 4/5 route / placement inspection

For main level 4/5 stage entries, the explorer also reads the fixed `0x118` stage-placement table. The route line is derived from the executable-backed 800-unit cell steps and each used placement is located at `cell_center + stored placement position`.

When the corresponding extracted `<name>.gmx` is available anywhere in the rip's asset tree, the explorer reads only the proven GMX-root geometry AABB and applies the recovered stage-placement transform to its eight corners. The native row-vector order is `S × Rz(z) × Rx(x) × Ry(y) × T`: scale uses the recovered runtime value (`stored_scale × 5`), the stored degree rotations are converted to radians, then the recovered placement origin is applied. Orbit, top-down, and POV views all draw that transformed wire box. Clicking a placement reports the model name, record/slot, local and preview positions, runtime scale, stored rotation degrees, and native AABB.

This closes the former Euler-order approximation for placement metadata, but does **not** elevate Stage Explorer beyond proof-of-concept status. Route-follow cameras, entity/gameplay simulation, collision, and other unmodeled 3D-control side effects retain their documented boundaries. See `reference/research/STAGE_PLACEMENT_TRANSFORM_DEV24.md`.
