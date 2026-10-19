# Visualizer Simulator proof-of-concept polish — dev24 WIP183

## Scope

WIP183 deliberately reclassifies the browser Visualizer Simulator as a **polished proof of concept**. It remains useful for recovered controls, ParameterSet/SequenceSet exploration, DAT timeline playback, SHAPE inspection, and qualitative feedback behavior, but it is not presented as a bit-exact Xbox 360/Xenos final-output emulator.

This pass responds to project-owner testing of WIP182: recursive feedback still looked too blocky, colors were visibly too dark, and generated game-BGM previews produced no audible sound in the browser.

## Presentation-only polish

The executable-backed recursive working surfaces remain unchanged:

- 1280x720 ping-pong feedback surfaces;
- current SHAPE drawn first;
- previous feedback drawn second;
- recovered point-filtered feedback sampling;
- recovered additive EffectBlur RGB recurrence;
- source-only rotation and recovered position/scale semantics.

WIP182's host presentation multiplied the entire final canvas by a default `0.32` alpha and applied a `5.5 px` blur. That made the browser output substantially darker and did not adequately hide the block-like point-sampling presentation.

WIP183 replaces that final-only bridge with:

- base softness: **1.4 px**;
- base intensity: **0.88**;
- separate host-only **screen/bloom** layer: **0.52**;
- bloom uses a broader blur plus mild saturation/brightness;
- raw recovered RGB is still available at softness `0`, intensity `1`, bloom `0`.

The bloom/softness pass never feeds back into the recovered recursive surfaces. It is explicitly a browser presentation approximation.

## BGM audibility / meter redesign

The previous browser path created a `MediaElementAudioSourceNode` around the `<audio>` element to obtain a live analyser. Local `file://` media can be treated as an opaque/cross-origin source by browser Web Audio implementations; once wrapped, that source can produce silence even though the native media element itself can decode the file.

WIP183 removes `createMediaElementSource()` entirely.

For toolkit-generated Xbox WMA / PS3 AT3 previews:

1. FFmpeg still creates a browser-safe stereo 48 kHz MP3 or AAC/M4A preview.
2. FFmpeg separately decodes the user-owned source to stereo 48 kHz PCM.
3. The toolkit computes one left/right peak pair for every recovered **256-sample XAudio2 quantum**.
4. Peaks are quantized to unsigned 8-bit values and embedded compactly in the locally generated simulator dataset.
5. The HTML `<audio>` element plays the preview directly, with no Web Audio routing.
6. Meter playback indexes the precomputed quantum envelope using `HTMLMediaElement.currentTime`.

For user-selected browser-decodable host audio, Web Audio is used only to decode the file to an `AudioBuffer` and build the same peak envelope. It is never connected to the playing media element.

This design removes the known local-media muting failure mode while preserving the recovered meter value semantics. Exact browser `currentTime` scheduling/phase relative to Xbox 360 XAudio2 processing boundaries remains approximate.

## Boundary retained

WIP183 does **not** claim to solve:

- exact Xenos render-target alpha storage;
- exact final game composite/post-processing;
- exact host/XAudio2 meter-query phase;
- exact hardware blur/AA/display filtering;
- bit-perfect visual output.

The simulator should be described as a polished PoC, similar in status to Stage Explorer but with an intentionally richer interactive control surface and room for future evidence-backed presentation improvements.
