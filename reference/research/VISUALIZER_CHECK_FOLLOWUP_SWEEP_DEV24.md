# Visualizer Check Mode follow-up controlled sweep — dev24 WIP178

## Scope

A second set of ten project-owner Xbox 360 June 10 Visualizer Check Mode segments (`18-35-14`, 1920×1080/60 fps MKV) was inspected after the WIP177 feature sweep. The footage remains external/user-owned and is not bundled.

This pass is primarily a **cross-check and boundary-tightening pass**. It does not replace executable-backed renderer semantics with visual inference, and it does not change Visualizer dataset v20 or the recovered RGB recurrence.

## Segment map

| Segment | Controlled focus | Follow-up hardware observation | Result |
| --- | --- | --- | --- |
| 1 | SHAPE RGBA endpoints | large R/G endpoint edits visibly retint the injected source while the same SHAPE/feedback context is retained | independently corroborates source-tint VolumeSet endpoints rather than random min/max ranges |
| 2 | combined Magnify Scale X/Y + Magnify A | independent X/Y expansion/contraction combines with persistence changes as A endpoints are edited | corroborates feedback-surface scaling and feedback-alpha interpolation together |
| 3 | BG RGBA, especially BG:A | `BG:R=255, G=B=0, BG:A=0` still presents a bright red clear/background around the recursive image; later A/R combinations remain independently editable | **new constraint:** BG RGB must not be premultiplied away merely because BG:A is zero; exact Xenos stored alpha/final presentation still remains unresolved |
| 4 | Rotation Base / Add Rotation | Base/Add edits visibly change the normal accumulated-angle path when Fix Rotation is no longer forcing the source angle | complements WIP177's override test and confirms the active non-fixed path |
| 5 | SHAPE resource sweep | silhouettes again traverse the recovered ten-resource order | second independent hardware corroboration of resource order |
| 6 | extreme Magnify X/Y | asymmetric extremes produce correspondingly asymmetric recursive stretch | reinforces independent feedback X/Y axes |
| 7 | ordinary source Scale X/Y | near-flat Y and enlarged X values create thin/wide newly injected shapes while recursive magnification remains a separate control | reinforces source-stamp/feedback-scale separation |
| 8 | Stick VolumeSet + Add Rotation | Stick volume can drive the effect from zero/blank through a rotating recursive pattern with Add Rotation active | corroborates Check Mode Stick as the direct VolumeSet input and Add Rotation's volume dependency |
| 9 | BGM VolumeSet + Position Free | BGM-driven volume changes coexist with free-position movement; debug overlay visibility can be toggled without stopping the effect | corroborates that diagnostic display state is separate from the Visualizer simulation state |
| 10 | Stick VolumeSet + color/alpha controls | source intensity/tint responds while Stick volume is swept; zero Stick volume can suppress the injected result while the debug menu remains active | further corroboration of endpoint-driven source controls; does not isolate final render-target alpha storage |

## BG:A constraint added by this sweep

The strongest new evidence is segment 3. A native frame explicitly shows a saturated red screen with:

- `BG:R = 255`
- `BG:G = 0`
- `BG:B = 0`
- `BG:A = 0`

That rules out a browser approximation in which the clear RGB is simply multiplied by BG:A before entering the recovered RGB recurrence. The current simulator already behaves correctly for this observation: its feedback working canvases preserve the selected clear RGB independently of BG:A because the recovered EffectBlur pixel path samples RGB independently from sampled alpha.

What the frame **does not** prove is the exact alpha value retained in the native Xenos render target after clear/SHAPE/feedback blending, nor how that alpha is treated by the final presentation path. Recursive history and later blend/copy stages prevent the capture from isolating that internal quantity. `VISUALIZER_RT_ALPHA_STORAGE` therefore remains open.

## BGM timing boundary retained

Segments 9/10 provide useful real-hardware cross-checks of BGM/Stick switching and displayed volume values, but they do not provide a phase-locked measurement of when the menu samples the XAudio2 meter relative to each native 256-sample processing quantum. WIP174's executable-backed **256 samples / 5.333 ms at 48 kHz** bridge remains unchanged, and browser/native snapshot phase/scheduling remains bounded.

## WIP178 implementation consequence

No Visualizer renderer-math or dataset-version change is justified. Instead WIP178:

- records the second sweep as a separate validation artifact;
- regression-locks the new `BG RGB survives BG:A=0` constraint against the existing browser implementation;
- preserves the two narrow open boundaries: exact native render-target alpha/final presentation and browser/native XAudio2 snapshot phase.
