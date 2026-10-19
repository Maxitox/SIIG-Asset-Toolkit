# Visualizer BGM meter — dev24

## Result

The June 10 Xbox 360 Visualizer Check Mode does **not** apply a dB or RMS transfer curve after its audio meter. `Function_82495500` copies a 12-byte XAudio2 volume-meter result, dereferences the first pointer field, averages exactly two floats, and stores that value in the audio singleton. `FUN_824956C0` latches it and `FUN_82495360` returns the float directly. `Function_82183B20` selects that BGM value when `VolumeSet == 0` and passes it directly into the Visualizer parameter path. This direct transfer is specific to dedicated Visualizer Check Mode. WIP167 recovers the normal scripted-stage downstream path separately: `Function_82177648` feeds the same raw meter value through an adaptive MIN/MAX normalizer before parameter interpolation; see `VISUALIZER_GAMEPLAY_BGM_NORMALIZER_DEV24.md`.

Microsoft's public `XAUDIO2FX_VOLUMEMETER_LEVELS` definition identifies the first field as `pPeakLevels`, followed by `pRMSLevels` and `ChannelCount`. Therefore the game's BGM control value is the arithmetic mean of the **left/right peak levels**, in the linear 0..1 amplitude domain.

## Browser simulator bridge

The source-only simulator now splits browser playback into left/right channels, samples each channel's time-domain maximum absolute value, and averages those two peaks. Mono files use the single channel. Files with more than two channels use the first two channels because the recovered game path is explicitly a two-float average.

WIP174 closes the native processing-window size. Microsoft's XAudio2 Audio Graph documentation specifies a **5 1/3 ms** processing quantum on Xbox 360, and the volume-meter API defines `pPeakLevels` as the maximum absolute level during one processing pass. At SIIG's 48 kHz BGM rate, that is exactly **256 samples**. Dataset v18 therefore requests a 48 kHz `AudioContext` and uses a 256-sample channel-separated peak window. The remaining browser approximation is snapshot **phase/scheduling** relative to native XAudio2 quantum boundaries, not the window duration itself. See `VISUALIZER_BGM_QUANTUM_DEV24.md`.

## Evidence

- June 10 `Function_82495500`: 12-byte meter structure; averages exactly two floats from first pointer field.
- June 10 `FUN_824956C0`: latches the computed meter value into the field read by Check Mode.
- June 10 `FUN_82495360`: returns the stored float directly.
- June 10 `Function_82183B20`: `VolumeSet == 0` selects the BGM float; `VolumeSet == 1` selects stick magnitude.
- Microsoft Learn `XAUDIO2FX_VOLUMEMETER_LEVELS`: first structure field is `pPeakLevels`; second is `pRMSLevels`; third is `ChannelCount`, and peak values are maxima over one processing pass.
- Microsoft Learn `XAudio2 Audio Graph`: Xbox 360 processing quantum is 5 1/3 ms (256 samples at 48 kHz).

No Microsoft implementation code is copied or bundled; the public API documentation is used only to identify the structure fields.
