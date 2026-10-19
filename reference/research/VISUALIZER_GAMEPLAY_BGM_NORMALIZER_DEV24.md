# Visualizer normal-gameplay BGM normalizer — dev24 WIP167

Status: **recovered and simulator-backed** for the game-side post-meter path. WIP174 additionally closes the upstream Xbox 360 XAudio2 meter window at one 5 1/3 ms / 256-sample processing quantum at 48 kHz; only browser/native phase alignment remains bounded.

## Why this pass exists

Project-owner real-hardware recordings of the June 10 build's stages **4-2, 4-4 and 4-5** expose the Visualizer debug lines while native BGM response is working. Those recordings distinguish normal stage playback from the dedicated Visualizer Check Mode path and make the adaptive volume state directly observable.

The relevant debug strings in the June 10 executable are:

- `AVE RAW:%0.4f SCALE:%0.4f` at `0x82017EB4`
- `VOL SCALE:%0.4f` at `0x82017ED0`
- `VOL:%0.4f MIN:%0.4f MAX:%0.4f` at `0x82017EE0`
- `SEQ=%d PARAM=%d` at `0x82017F00`

## Recovered state machine

### Raw input

`Function_82177648` reads `FUN_82495360()` and stores the result at VisualizerScript `+0x40` (`VOL`). Earlier dev24 work proved this value is the arithmetic mean of the left/right XAudio2 **peak** levels, in linear 0..1 amplitude space.

The dedicated Visualizer **Check Mode** (`Function_82183B20`) passes this raw value directly into `FUN_82174E40`. Check Mode therefore remains a raw-meter path.

Normal scripted stage playback is different.

### Adaptive MIN/MAX window

`Function_82177510` constructs an adaptive float buffer at `+0x44` with a default length of **300** and initializes:

- MIN (`+0x5C`) = 0
- MAX (`+0x60`) = 1
- VOL SCALE (`+0x64`) = 1

`Function_82177300` replaces that buffer length with an authored frame count, clamped to a minimum of 5. Opcode `0xCE`, whose debug/source name is `VL_VOLUME_SCALE` / `ScriptVOLUME_SCALE`, calls this function. The executable's own assertion text calls the argument `frame`.

The three new reference stages all author the same override at visualizer start:

| Script | Sequence | `0xCE` authored value | Runtime meaning |
|---|---:|---:|---|
| `level4_stage2.dat` | 4 | 180 | adaptive volume window = 180 Visualizer update frames |
| `level4_stage4.dat` | 8 | 180 | adaptive volume window = 180 Visualizer update frames |
| `level4_stage5.dat` | 12 | 180 | adaptive volume window = 180 Visualizer update frames |

Thus **300 is the constructor default, not the value used by these three stages**.

On each active update, `Function_82177648` clamps the raw meter value to [0,1], writes it to the current adaptive-buffer slot, advances the write index, and calls `Function_821773F0`. MIN/MAX are recomputed only when that write index wraps to zero.

### Exact VOL SCALE mapping

`Function_821773F0` sorts the completed adaptive window and takes its first/last values as MIN/MAX. If `abs(MAX-MIN) < 0.001`, it expands the range to at least 0.001. It then computes:

- `VOL < MIN` -> `VOL SCALE = 0`
- `VOL > MAX` -> `VOL SCALE = 1`
- otherwise -> `VOL SCALE = (VOL - MIN) / max(abs(MAX - MIN), 0.001)`

The resulting float is stored at `+0x64` and passed to the normal Visualizer parameter interpolator. **Normal stage parameter interpolation therefore uses VOL SCALE, not raw VOL.**

### Real-hardware cross-check

The footage numerically agrees with the recovered equation. Representative examples read from the hardware overlay include:

- stage 4-2: `VOL=0.4625`, `MIN=0.0486`, `MAX=0.7312` -> predicted `0.6063`, displayed `VOL SCALE=0.6064`
- stage 4-5: `VOL=0.2467`, `MIN=0.0751`, `MAX=0.4167` -> predicted `0.5023`, displayed `VOL SCALE=0.5022`
- stage 4-5: `VOL=0.4562`, `MIN=0.3206`, `MAX=0.7757` -> predicted `0.2980`, displayed `VOL SCALE=0.2979`

The small last-digit differences are consistent with the overlay rounding its underlying floats to four decimals before we read them from video.

## 180-frame diagnostic histories

The constructor separately allocates three 180-float histories at `+0x6C`, `+0x7C` and `+0x8C`. `Function_82177648` writes raw VOL to `+0x6C` and normalized VOL SCALE to `+0x8C` using a shared 180-entry ring index at `+0x68`.

`Function_82175FA8` refreshes the displayed diagnostic averages when that ring wraps. The printed values are:

- `AVE RAW` from the raw history (`+0x6C` -> `+0x9C`)
- `AVE SCALE` from the normalized history (`+0x8C` -> `+0xA4`)

The function accumulates onto the previous displayed average before multiplying by `1/180`; the simulator preserves that tiny previous-average carry rather than silently simplifying it to an ideal moving mean.

## Simulator behavior

Visualizer dataset **v18** retains the two distinct BGM-response models:

1. **Check Mode · raw peak mean** — preserves `Function_82183B20` semantics.
2. **Stage playback · adaptive VOL SCALE** — reproduces `Function_82177510`, `Function_82177300`, `Function_821773F0`, `Function_82177648`, and the visible portions of `Function_82175FA8`.

Applying/selecting a decoded stage Visualizer event switches to BGM + stage mode and applies the latest authored `VL_VOLUME_SCALE` window at or before the selected script frame. With no authored override, the recovered constructor default is 300 frames.

The simulator also displays hardware-style `VOL / MIN / MAX / VOL SCALE / AVE RAW / AVE SCALE` diagnostics to permit direct comparison with captured hardware footage.

## Remaining boundary

This still does **not** make the browser audio frontend cycle-equivalent to XAudio2. WIP174 resolves the native meter window to one **256-sample / 5 1/3 ms** Xbox 360 XAudio2 quantum at 48 kHz and the simulator mirrors that window size. The remaining approximation is when the browser's analyser snapshot lands relative to native XAudio2 quantum boundaries and media-element scheduling. The recovered game-side adaptive normalizer continues to consume the current stereo peak mean once per logical 60 Hz simulator step.
