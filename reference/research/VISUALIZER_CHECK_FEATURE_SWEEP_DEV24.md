# Visualizer Check Mode hardware feature sweep — dev24 WIP177

## Scope

Ten project-owner Xbox 360 June 10 Visualizer Check Mode segments (1920×1080, 60 fps MKV) were inspected as a controlled parameter sweep. The capture media remains external/user-owned and is not bundled in the toolkit. This checkpoint uses the on-screen control text/value as the authoritative description of the edited parameter and the rendered Visualizer response as independent hardware evidence.

WIP177 does **not** replace executable-backed semantics with footage inference. Where a clip is ambiguous because recursive feedback preserves earlier frames, the executable remains canonical and the ambiguity is recorded.

## Segment map

| Segment | Primary feature | Hardware observation | Toolkit conclusion |
|---|---|---|---|
| 1 | Magnify A / baseline | Magnify A endpoint edits change feedback persistence while VolumeSet and SHAPE are varied | Corroborates volume-endpoint alpha interpolation already recovered; WIP176 native range guard remains |
| 2 | Position Free | Sweeping X/Y moves the effect across all quadrants | Confirms centered game coordinates: +X right, +Y up; Free X/Y is the raw Position Fix 0 path |
| 3 | Rotation Base / Add Rotation with Fix Rotation active | Large Base/Add edits produce no corresponding rotational change while Fix Rotation stays at 360° | Confirms any nonzero Fix Rotation overrides the accumulated Base + Add×volume path |
| 4 | Position Fix | Raw nonzero Position Fix values switch among distinct fixed anchors; raw 0 returns to Free | Corroborates separate fixed-anchor path. Exact 3×3 coordinates remain executable-backed because recursive history makes rapid transitions visually ambiguous |
| 5 | SHAPE RGBA min/max | R/G/B/A endpoint changes alter source tint/opacity in the expected direction | Confirms these are VolumeSet interpolation endpoints, not random ranges |
| 6 | BG RGBA | BG R/G/B directly change the feedback clear color; BG A is independently sweepable 0..255 | Confirms BG controls are direct single clear values, not VolumeSet endpoint pairs. Exact native alpha storage/final composite remains bounded |
| 7 | Magnify Scale X/Y maxima | Values above 1 expand/stretch the recursive image independently by axis | Confirms feedback-surface magnification and volume endpoint interpolation |
| 8 | Magnify Scale X/Y minima | Values below 1 contract the recursive image toward the anchor | Confirms the same endpoint interpolation works below unity; X/Y remain independent |
| 9 | SHAPE resource sweep | Distinct silhouettes match the recovered 10-resource order | Corroborates the existing SHAPE resource mapping; no remap needed |
| 10 | ordinary Scale X/Y | X/Y endpoint edits change the dimensions of newly injected SHAPE stamps before they accumulate | Confirms ordinary Scale X/Y targets the source stamp, not the previous feedback surface; unlike Magnify X/Y its setter has no max>=min assertion |

## Confirmed control relationships

For Magnify X/Y/A, ordinary source Scale X/Y, and SHAPE RGBA, the hardware behavior is consistent with the recovered VolumeSet interpolation:

`effective = min + (max - min) * volume`

The important distinction is **what receives that interpolated value**:

- ordinary `Scale X/Y` scales the newly injected 128×128 SHAPE source;
- `Magnify Scale X/Y` scales the previous feedback surface before additive recurrence;
- SHAPE RGBA tints the newly injected source stamp;
- `Magnify A` supplies the recursive feedback pass alpha.

The June 10 executable remains authoritative for range validity: Magnify X/Y/A and SHAPE RGBA assert on inverted min/max, while ordinary source Scale X/Y stores all four values without that sibling ordering assertion.

## Override / inactive-control behavior

The hardware sweep makes two native precedence relationships visually explicit:

1. `Position Fix = 0` uses Position Free X/Y. Any nonzero Position Fix selects the fixed-anchor table and ignores the free coordinates.
2. `Fix Rotation = 0` uses the accumulated `Rotation Base + Add Rotation × volume` path. Any nonzero Fix Rotation supplies the source angle directly and bypasses Base/Add accumulation.

WIP177 makes these inactive states visible in the browser UI instead of leaving controls looking live when the native path is ignoring them.

## Background alpha boundary intentionally retained

The BG:A clip proves that the June 10 Check Mode exposes and updates an independent 0..255 background-alpha control. It does **not** by itself establish exact Xenos render-target alpha storage or the final screen-composite equation: recursive feedback contains prior frames, and the recovered EffectBlur pass already has its own alpha/blend behavior.

The simulator therefore continues to reproduce the instruction-backed RGB recurrence on opaque browser working canvases and exposes BG:A as a native control while explicitly labeling alpha storage/final-composite equivalence as unresolved. No speculative Canvas alpha feedback was introduced.

## WIP177 implementation

Visualizer dataset advances from v19 to **v20**. Renderer math is unchanged. The simulator now:

- labels Magnify and source-tint min/max values as VolumeSet endpoints;
- explicitly separates source Scale X/Y from recursive Magnify X/Y;
- visibly marks Position Free inactive while Position Fix is nonzero;
- visibly marks Rotation Base/Add inactive while Fix Rotation is nonzero;
- labels BG RGBA as direct clear controls and keeps the exact BG:A/Xenos-alpha boundary visible;
- reports effective source scale and effective SHAPE tint in the live status line for hardware comparison.

## Boundaries retained

- exact Xenos render-target alpha storage/final-composite equivalence;
- browser/Web Audio snapshot phase and scheduling relative to native Xbox 360 XAudio2 256-sample quantum boundaries.
