# Visualizer position coordinates and runtime Position Fix grid — dev24 WIP171

> **Current bridge note (WIP197):** WIP171 remains authoritative for the runtime-patched ±448/±308 Position Fix table and +X-right/+Y-up axes. WIP191's later 1.5× scale hypothesis was superseded by WIP195's stage 4-5 regression and is now independently closed by June 10 `Function_82177DF0`: it passes X×1/640 and Y×1/360 into the 1280×720 render path. The direct one-debug-unit = one-target-pixel bridge below is therefore current again. See `VISUALIZER_POSITION_AUDIO_CACHE_DEV24_WIP197.md`.

## Why WIP170 needed another correction

WIP170 correctly fixed the browser's vertical coordinate mirror, but its
Position Fix interpretation stopped one initialization step too early.  The
static executable image shows the Position Fix float2 table with the horizontal
columns populated and the upper/lower Y words still zero.  That is **not** the
final runtime table.

The project-owner June 10 Visualizer Check capture (Misc segment 3, roughly
1:34–2:22) makes the discrepancy visible: raw values 1..9 occupy a full 3×3
upper/middle/lower grid rather than three repeated horizontal positions.
Re-reading the June 10 startup code resolves the apparent contradiction.

## Runtime table construction

The June 10 fixed-position setter at `0x82177DB0` stores the raw Position Fix
index, multiplies it by eight, and reads a float2 from the writable table at
`0x82574250 + index*8`.

In the file image the X words already contain the three columns:

- left = `-448.0`
- center = `0.0`
- right = `+448.0`

The Y words appear zero in the raw listing.  A startup initializer at
`0x82564470` then loads `0xC39A0000` (`-308.0`) from `0x82574248`, negates it to
`+308.0`, and patches the table in place:

- Y slots for raw 1, 2, 3 receive `+308.0`;
- Y slots for raw 7, 8, 9 receive `-308.0`;
- raw 4, 5, 6 remain `0.0`.

The May 11 lineage performs the same patch at its corresponding startup
initializer, and retail Xbox 360 repeats the same six stores around its own
Position Fix table.  The zero-Y rows seen in the static image are therefore
**pre-constructor data**, not aliases.

The final runtime Position Fix contract is:

| Raw | Native X | Native Y | Meaning |
|---:|---:|---:|---|
| 0 | 0 | 0 | Free X/Y path (default free 0,0 appears centered) |
| 1 | -448 | +308 | Upper left |
| 2 | 0 | +308 | Upper center |
| 3 | +448 | +308 | Upper right |
| 4 | -448 | 0 | Middle left |
| 5 | 0 | 0 | Fixed center |
| 6 | +448 | 0 | Middle right |
| 7 | -448 | -308 | Lower left |
| 8 | 0 | -308 | Lower center |
| 9 | +448 | -308 | Lower right |

Raw 0 and raw 5 can look identical while Position Free is `(0,0)`, but they are
not semantic aliases.  Raw 0 makes VisualizerMain call the free-position setter
and therefore follows Position Free X/Y.  Raw 5 selects the fixed table entry
`(0,0)` and ignores Position Free X/Y.

## Coordinate bridge

The WIP170 axis correction remains valid.  SIIG's Visualizer coordinates are
center-origin with **+X right and +Y up**, while Canvas uses +Y downward:

- `canvas_x = 640 + game_x`
- `canvas_y = 360 - game_y`

On the 1280×720 target, the fixed table therefore maps to the following anchor
centers:

| Raw | Canvas X | Canvas Y |
|---:|---:|---:|
| 1 | 192 | 52 |
| 2 | 640 | 52 |
| 3 | 1088 | 52 |
| 4 | 192 | 360 |
| 5 | 640 | 360 |
| 6 | 1088 | 360 |
| 7 | 192 | 668 |
| 8 | 640 | 668 |
| 9 | 1088 | 668 |

The 128×128 SHAPE and the magnified recursive feedback are both transformed
around this same anchor, so edge presets naturally place a substantial part of
the visible effect outside the target.

The retained `SEQUENCE_4 -> PARAM_3` cross-check is still useful for the free
path: PARAM_3 uses Position Fix 0 with free `(10,+360)`, which maps to
`(650,0)`, not `(650,720)`.

## Simulator correction

Visualizer dataset **v16** restores all ten raw Position Fix choices.  There is
no alias canonicalization.  ParameterSet imports preserve their exact 0..9
value, and the UI exposes the nine fixed grid points plus raw 0 Free X/Y.

WIP170's four-choice alias interpretation is superseded by this runtime-
initializer trace.  The WIP170 package itself remains immutable as a historical
checkpoint; this current research note records the correction for WIP171 and
later work.

## Boundaries

This correction changes only the Position Fix runtime table interpretation and
its simulator UI/application.  It does not alter the recovered point-filtered
SHAPE/feedback samplers, EffectBlur blend/shader equation, adaptive BGM
normalizer, or host-only final softness/intensity calibration.  Exact upstream
XAudio2 meter cadence and exact Xenos render-target alpha storage remain
separate documented boundaries.  Proprietary captures and executable bytes are
validation inputs only and are not bundled in the source package.
