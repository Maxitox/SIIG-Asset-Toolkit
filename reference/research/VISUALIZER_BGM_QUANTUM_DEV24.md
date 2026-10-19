# Visualizer Xbox 360 BGM processing quantum — dev24 WIP174

Status: **native processing-window duration/size recovered; browser phase remains bounded**.

## Result

Microsoft's public XAudio2 audio-graph documentation states that the Xbox 360 graph is processed once every **5 1/3 milliseconds**. SIIG's browser-safe BGM previews are normalized to **48,000 Hz**, so one Xbox 360 processing pass corresponds to exactly:

`48000 * (16/3 ms) / 1000 = 256 samples`

Microsoft's `XAUDIO2FX_VOLUMEMETER_LEVELS` documentation defines `pPeakLevels` as the **maximum absolute level for each channel during a processing pass**. Earlier executable tracing already established that SIIG averages the first two peak values and that dedicated Visualizer Check Mode consumes that stereo peak mean directly.

Therefore the native upstream meter window is no longer an unknown: for SIIG's 48 kHz path it is a **256-sample, 5.333333... ms peak window per XAudio2 processing pass**.

## Executable-side polling

June 10 `FUN_824956C0`/`FUN_82495360` latch/read the already-produced XAudio2 meter value from the game update path. Normal VisualizerScript processing continues once per active logical update and then applies the separately recovered adaptive VOL SCALE normalizer. This does not imply that a 60 Hz game update creates the meter window; XAudio2 updates its effect state on the faster audio-graph quantum.

## Browser bridge

Visualizer Simulator dataset **v18** now:

- requests an `AudioContext` at **48 kHz**;
- falls back to the browser's default rate only if the requested rate is rejected;
- uses one **256-sample** `AnalyserNode` time-domain window per channel;
- disables analyser smoothing;
- takes the maximum absolute value of those 256 samples;
- averages left/right peaks exactly as the game does;
- displays the actual host sample rate and resulting analysis-window duration.

When the browser provides 48 kHz, the bridge has the native **window size and duration**. What remains approximate is the **phase/scheduling** of each browser analyser snapshot relative to Xbox 360 XAudio2 processing-pass boundaries. Browser media-element scheduling and Web Audio callbacks are not claimed sample-phase equivalent to the console.

## Private hardware-capture cross-check

The project owner's real-hardware June 10 stage footage was used only as private validation and is not bundled. For the first supplied hardware recording, nine manually read overlay `VOL` samples between 8.0 and 12.0 seconds were compared with the recording's decoded 48 kHz stereo audio. After allowing a single capture-path gain and A/V alignment offset, a 256-sample rolling peak window produced approximately **0.9967 correlation** and **0.0080 RMSE** against the displayed values. Neighboring window sizes were worse in that capture.

This empirical result is corroboration, not the source of the native constant: the 256-sample window follows independently from Microsoft's documented Xbox 360 XAudio2 quantum and 48 kHz rate.

## Sources / provenance

- Microsoft Learn, **XAudio2 Audio Graph** — Xbox 360 graph quantum: 5 1/3 ms.
  https://learn.microsoft.com/en-us/windows/win32/xaudio2/xaudio2-audio-graph
- Microsoft Learn, **XAUDIO2FX_VOLUMEMETER_LEVELS** — `pPeakLevels` is maximum absolute level per channel during a processing pass.
  https://learn.microsoft.com/en-us/windows/win32/api/xaudio2fx/ns-xaudio2fx-xaudio2fx_volumemeter_levels
- June 10 Xbox 360 executable tracing — SIIG's two-channel peak averaging, latch/read path and Visualizer consumption.
- Project-owner real-hardware captures — private cross-check only, not redistributed.

No Microsoft implementation code or project-owner footage/audio is included in the source-only toolkit.

## Remaining boundary

`VISUALIZER_BGM_PROCESSING_CADENCE` is narrowed rather than silently deleted: **quantum duration/window size is resolved; browser/native phase alignment is not**. Exact Xenos render-target alpha behavior remains a separate Visualizer boundary.
