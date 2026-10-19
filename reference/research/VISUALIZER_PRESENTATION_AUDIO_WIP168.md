# Visualizer real-hardware presentation + browser-audio correction — dev24 WIP168

## Scope

WIP168 responds to project-owner testing of the WIP167 offline Visualizer Simulator. Two screenshots of the same June-10 stage context were compared: the browser simulator was structurally close but much harder/brighter than the real-hardware output, and the generated WMA browser previews could advance normally while producing no audible output.

The comparison image itself remains external/user-owned and is **not bundled** in the toolkit.

## Presentation calibration

The recovered recursive renderer remains unchanged: SHAPE and feedback sampling stay point-filtered, EffectBlur remains the recovered Add(SrcAlpha, One) RGB recurrence, and the real 29-value ParameterSet rows remain the source of render parameters.

The mismatch is handled only in the final host presentation pass:

- `Display softness` now defaults to **5.5 px** and is adjustable over **0..12 px**.
- `Display intensity` is a new host-only multiplier, default **0.32** and adjustable over **0.10..1.00**.
- softness/intensity are applied only when the completed feedback surface is copied to the visible browser canvas; neither value is written into either recursive feedback surface.
- setting softness **0** and intensity **1** exposes the raw recovered RGB recurrence.

A pixel-gradient comparison of the supplied screenshots put the closest simple Gaussian host blur in roughly the 5–6 px range at the simulator's displayed size. The intensity default is an empirical presentation calibration, **not** a newly claimed Xenos blend or shader constant.

## Stage sequence synchronization

The screenshots also exposed an important usability/fidelity problem: the real game debug overlay identifies the active `SEQ` and `PARAM`, while the simulator could show a stage timeline without automatically applying the sequence's parameter row as the authored frame changed.

WIP168 therefore:

- shows `SEQ` and `PARAM` in the simulator status line;
- synchronizes decoded `VL_SEQUENCESET` events to their recovered SequenceSet row and active ParameterSet row;
- advances the selected authored DAT frame at the simulator's 60 Hz logical step when **Advance authored stage frame** is enabled;
- keeps this synchronization separate from the still-bounded exact `VL_CHANGETIME` interpolation behavior.

Retail `SEQUENCE_4` maps to `PARAM_3`, matching the project-owner hardware screenshot's `SEQ=4 PARAM=3` overlay.

## WMA/AT3 mute diagnosis and fix

The previous browser code called `createMediaElementSource()` as soon as a track was selected. That immediately reroutes an HTML `<audio>` element through Web Audio. Browsers are allowed to keep a newly created `AudioContext` suspended until a user gesture; in that state the media element can visibly advance while the rerouted output is silent.

WIP168 changes the bridge so:

1. selecting a track leaves native HTML audio routing intact;
2. a direct pointer/keyboard interaction with the audio controls creates/resumes the `AudioContext`;
3. the media element is connected to analysers/destination **only after** the context is confirmed `running`;
4. if Web Audio cannot be unlocked, native audio remains audible and only live meter analysis is unavailable;
5. FFmpeg browser previews are normalized to **stereo 48 kHz** before MP3/AAC encoding for consistent playback/analyser input.

The source-only selftest now synthesizes non-zero stereo audio and, when FFmpeg is available, decodes the generated preview and rejects a silent result. This replaces the former all-zero test fixture that could not detect mute-preview regressions.

## Evidence boundary

WIP168 does not reinterpret the recovered Xenos sampler, shader, or fixed-function blend semantics. The new visual defaults are explicitly host presentation calibration. Exact final Xenos render-target alpha storage/compositing and the browser-vs-XAudio2 upstream analysis-window cadence remain bounded.
