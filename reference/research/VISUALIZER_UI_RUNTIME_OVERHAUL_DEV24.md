# Visualizer Simulator UI/runtime overhaul — dev24 WIP191

> **Historical/superseded position note (WIP197):** This file preserves the WIP191 reasoning as a historical checkpoint. Its 1.5× logical-to-target Position inference is **not current**. WIP195 showed it can move authored sources completely off-target, and WIP197 independently isolates June 10 `Function_82177DF0` using X/640 and Y/360, restoring the direct target-pixel mapping. The viewport UI and display-only resolve described here remain current.


WIP191 is a usability and hardware-alignment pass over the offline Visualizer
Simulator. It does not replace the recovered recursive renderer with a new
artistic approximation. The recovered 1280x720 ping-pong surfaces, SHAPE-first
draw order, point-filtered feedback sampler, EffectBlur source-alpha/additive
blend, source-only rotation, ParameterSet/SequenceSet logic and stage BGM
normalizer remain intact.

## UI overhaul

The old document flow placed every control in a long left column while the
1280x720 canvas sat in a separate column. Selecting a stage/boss preset near the
bottom therefore required scrolling away from the canvas and then scrolling
back to inspect the result.

WIP191 changes the simulator into a viewport-first control surface inspired by
the June 10 `VISUALIZER CHECK MODE` screen:

- the Visualizer canvas owns the viewport and never moves away during normal
  control changes;
- a translucent in-canvas menu is grouped into **PRESETS**, **CHECK MODE** and
  **ADVANCED** tabs;
- Stage/boss authored events are available in the always-visible top bar and
  apply immediately on selection, resetting accumulated feedback so the chosen
  preset can be watched from a clean state;
- the detailed ParameterSet/SequenceSet, BGM controls, recovered 29-value Check
  Mode controls, schema and decoded DAT timeline remain available rather than
  being removed;
- `M` hides/shows the menu, `X` resets feedback and `Y` toggles runtime debug
  text, preserving the recovered Check Mode button semantics for X/Y;
- `F` and the **Fullscreen** button use the browser Fullscreen API. Esc exits
  fullscreen normally.

The generated simulator remains a standalone local HTML file and does not need
an HTTP server.

## Hardware-derived logical-to-target position scale

WIP170/WIP171 correctly established the coordinate axes and runtime Position
Fix table, but the browser bridge then treated Check Mode position numbers as
literal 1280x720 target pixels. New cross-checks against the retained project-
owner June 10 hardware recordings show that this scale is wrong.

Two independent observations converge on a **1.5x logical-to-target scale**:

1. Retail-hardware stage 4-4 uses `PARAM_4`, whose free position is `(0,+256)`.
   Fitting the concentric blue feedback arcs in the 1920x1080 capture places
   their center approximately at/above the top of the 1280x720-equivalent
   frame. A 1.5x bridge predicts target Y `360 - 256*1.5 = -24`; the old direct
   bridge predicts Y `104`, visibly too far inside the screen.
2. In the dedicated June 10 Position Free sweep, the debug menu visibly reports
   values including `(345,+195)` while the triangle source is clipped against
   the top-right of the screen. The 1.5x bridge predicts a 1280x720 anchor of
   about `(1157.5,67.5)` (1920x1080 capture position about `(1736,101)`), which
   matches that edge-clipped behavior. The old direct bridge predicts a much
   more central position.

The corrected bridge is therefore:

- `target_x = 640 + logical_x * 1.5`
- `target_y = 360 - logical_y * 1.5`

The factor is also exactly `720 / 480`, consistent with a 480-line logical
control space feeding the 720-line Visualizer target. That relationship is a
strong hardware-derived model, but WIP191 deliberately does **not** claim the
exact upstream executable conversion call has been isolated yet.

Applying the same scale to the runtime-patched Position Fix grid is important
because free and fixed positions feed the same renderer transform. The nine
fixed centers become:

| Raw | Logical X/Y | 1280x720 target center |
|---:|---:|---:|
| 1 | -448,+308 | -32,-102 |
| 2 | 0,+308 | 640,-102 |
| 3 | +448,+308 | 1312,-102 |
| 4 | -448,0 | -32,360 |
| 5 | 0,0 | 640,360 |
| 6 | +448,0 | 1312,360 |
| 7 | -448,-308 | -32,822 |
| 8 | 0,-308 | 640,822 |
| 9 | +448,-308 | 1312,822 |

This naturally puts edge/corner feedback centers just outside the visible
screen, matching the behavior called out by the project owner. Raw 0 remains
Position Free and may move farther outside because its native bounds are X
`[-560,+560]`, Y `[-360,+360]`.

## Chunky feedback and display resolve

The blockiness cannot honestly be fixed by switching the recursive feedback
sampler to bilinear filtering: executable/TEX evidence says the native feedback
sampler is point-filtered. WIP191 therefore leaves the recursive ping-pong
working surfaces unchanged.

Instead the **default final browser presentation only** now performs a high-
quality resolve through a 640x360 intermediate surface and scales that resolved
image back to 1280x720 before the existing base/bloom presentation. This
reduces the huge host-visible square blocks produced by repeated point-sampled
magnification without feeding smoothing back into the next Visualizer frame.

The Check Mode panel exposes two presentation modes:

- **Hardware-like smooth resolve** — default WIP191 host presentation;
- **Raw recovered RGB** — bypasses the resolve, softness and bloom and displays
  the recursive RGB surface directly for research comparison.

The resolve is explicitly a browser presentation model, not a claimed Xenos
render-target sampler state.

## Evidence and retained boundaries

Private project-owner recordings used for this correction are validation inputs
only and are not distributed with the toolkit. The WIP191 generated HTML was
also syntax-checked with Node against a retail-derived, user-owned dataset
containing all 49 ParameterSets, 57 SequenceSets, 30 timelines / 243 commands,
39 authored Visualizer events and all ten recovered SHAPE images.

Still open:

- exact upstream executable location responsible for the 480-line logical ->
  720-line Visualizer target position conversion;
- exact Xenos final-composite / render-target alpha behavior;
- exact browser playback-time query phase relative to the native XAudio2 meter
  quantum;
- a final capture-matched browser post-process is not claimed bit-exact.
