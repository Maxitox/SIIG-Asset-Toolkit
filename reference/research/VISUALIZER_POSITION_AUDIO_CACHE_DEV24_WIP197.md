# Visualizer direct Position scale, audio-step timing and rebuild cache — dev24 WIP197

## Why this pass exists

Project-owner testing of WIP196 established three separate observations:

1. all authored Visualizers render again after the WIP195 gradient fix, but some source/feedback placement still looks offset from the game;
2. normal stage playback can appear to speed up or slow down abruptly even when the song does not sound correspondingly loud or quiet;
3. rebuilding only the Visualizer Simulator can take disproportionately long compared with the amount of HTML/data being regenerated.

These are deliberately handled as separate problems. WIP197 does not tune one global number until the screenshot "looks right".

## Global Position scale is now executable-backed

WIP191 inferred an extra 1.5× logical-to-target Position scale from capture fitting. WIP195 disproved that globally: retail stage 4-5 `SEQUENCE_12 -> PARAM_7` uses free Y `+360` with a 128×128 source. At 1.5× its complete source is above the 1280×720 target and cannot seed the structured hardware recurrence.

WIP197 closes the scale independently in the June 10 executable. `Function_82177DF0` calls the downstream render object with:

- X multiplied by `0.0015625` = **1 / 640**;
- Y multiplied by `0.0027777778` = **1 / 360**.

Those denominators are exactly the half-width and half-height of the recovered 1280×720 target. The host bridge therefore remains:

- `target_x = 640 + X`
- `target_y = 360 - Y`

with only the Y sign flipped for Canvas coordinates. There is no evidence in this path for the WIP191 extra 1.5 factor.

The simulator now provides an optional **Native anchor overlay** in Advanced. It draws the current executable-backed anchor and the browser's current source bounds without touching either recursive feedback surface. That is a diagnostic aid for measuring any remaining hardware difference. Remaining mismatch should be investigated as source pivot/transform/final-composite/capture alignment rather than hidden by another guessed global Position multiplier.

## Why stage response is not proportional to absolute loudness

The recovered game has two different BGM response paths:

- dedicated Visualizer Check Mode uses the raw arithmetic mean of the left/right XAudio2 peak levels;
- normal authored stage playback passes that raw peak mean through VisualizerScript's adaptive minimum/maximum window and interpolates parameters with **VOL SCALE = (raw - min) / (max - min)**.

The constructor uses a 300-update range window; `VL_VOLUME_SCALE` can change the window (the stage 4-2/4-4/4-5 examples author 180). Because this is a relative adaptive range, a quiet musical section can still produce a high VOL SCALE when it is near the recent local maximum, and a louder section can produce a lower value after the adaptive maximum moves. That non-monotonic relation to perceived absolute loudness is therefore intentional game behavior.

## Browser catch-up jitter fixed

WIP196 sampled `HTMLMediaElement.currentTime` once per browser `requestAnimationFrame`. If the browser delivered a delayed frame, the simulator then executed several fixed 60 Hz `logicalStep()` calls to catch up, but every one of those steps reused the same audio-meter sample. The result could be a visible burst/freeze pattern that did **not** exist in the intended fixed-step model.

WIP197 samples the precomputed native-quantum envelope at the corresponding playback time for each catch-up logical step. The displayed meter is still refreshed at the actual media time after the catch-up loop. This does not claim exact phase identity with the Xbox 360 audio thread; it only removes an avoidable host scheduling artifact while preserving the recovered adaptive normalizer.

## Why rebuilding was slow

Generated WMA/AT3 browser previews were already content-addressed, so an unchanged encoded preview often did not need to be transcoded again. However, the simulator still called FFmpeg for every native BGM on every rebuild to decode the entire track and recreate its 256-sample stereo peak envelope. On a full SIIG BGM set, that audio decode dominates the simulator build time.

WIP197 writes `visualizer_simulator/bgm_preview/BGM_PREVIEW_CACHE.json`. Each row uses a privacy-safe rip-relative key and stores:

- source size and nanosecond mtime;
- previously verified source SHA-256;
- generated preview relative path/codec;
- the compact 256-sample-quantum peak envelope.

An unchanged size+mtime row can reuse the verified hash and envelope without rereading/decoding the source. If stat metadata changes, the source is SHA-256 checked and the old envelope can still be reused when content is identical. Retained-source Update Rip seeds the prior BGM preview directory into staging so a Visualizer-only migration can take this fast path. A cached browser preview also remains usable if FFmpeg is temporarily unavailable.

A synthetic two-second WMA smoke measured roughly 0.30 s on the first build versus 0.07 s on the cached second build in the checkpoint environment; the important contract is the operation count, not that machine-specific ratio: second build = zero source hashes, zero preview transcodes and zero envelope decodes for the unchanged track.

## Resume-version correction

One fresh-rip resume predicate still compared the generated Visualizer manifest against a hard-coded historical dataset version. WIP197 replaces that literal with `VISUALIZER_SIMULATOR_VERSION`, so a current simulator is reusable instead of being silently marked stale by an obsolete number.

## Boundaries retained

- Exact browser playback-time query phase versus the native Xbox 360 XAudio2 256-sample processing pass remains bounded.
- Exact Xenos render-target alpha storage/final composite remains bounded.
- The project-owner's residual position concern is retained as a live comparison boundary; WIP197 closes the **global scale** but does not invent a per-shape or per-stage correction without executable/hardware evidence.
- Project-owner videos, original BGM and executable bytes are validation/research inputs only and are not bundled.
