# Visualizer Simulator — dev23 Check Mode reconstruction

This dev23 pass separates the June 10 prototype Visualizer Check Mode controls that are directly supported by executable evidence from host-side conveniences used by the offline simulator. No proprietary `ParameterSet.nut` or `SequenceSet.nut` rows are bundled; they are parsed from a user-supplied rip at runtime.

## June 10 executable evidence

- Main Check Mode update: `Function_82183B20`.
- **X / input mask `0x40`** calls the feedback-surface reset path (`FUN_821756F8`). This matches the project-owner June 10 footage where X visibly clears accumulated feedback.
- **Y / input bit `0x80`** is returned by `Function_82183398` and feeds the generic toggle control used for debug-info visibility. This matches the footage where Y hides/shows the overlay text.
- **VolumeSet** is a two-way selector: `0 = from BGM`, `1 = from Stick`; the June 10 default is `1`. When zero, the loop consumes the BGM meter float returned through `FUN_82495360`; otherwise it consumes the absolute controller/stick magnitude path. The original upstream BGM meter transfer curve is still unresolved.
- The Check Mode descriptor table at `0x82574550` contains 30 rows: VolumeSet, BGM, and 28 displayed parameter controls. `Position Free` carries two values, producing the recovered 29-number ParameterSet row schema.
- **Fix Rotation** is a signed numeric angle, not a Boolean. `FUN_821750D8` stores the float and `Function_82178788` uses zero for the normal accumulated-rotation path or a nonzero fixed angle converted to radians.

## Recovered UI ranges/defaults

- VolumeSet: 0..1, default 1.
- BGM: 0..50, default 0.
- Magnify X/Y min/max: 0.8..2.0, default 1.03.
- Magnify alpha min/max: 0.7..1.0, default 1.0.
- Background RGBA: 0..255, default 0.
- Shape: 0..9, default 0.
- Position Fix: 0..9, default 0.
- Position Free: X -560..560, Y -360..360.
- Rotation Base: -365..365, default 0.1, step 0.1.
- Add Rotation: -730..730, default 0.0, step 0.1.
- Fix Rotation: -365..365, default 0.0, step 0.1.
- Scale X/Y min/max: 0.01..4.0, default 1.0.
- Color channels: 0..255; recovered defaults R 128..255, G 0..0, B 0..0, A 255..255.

## External preset loading

Retail `visualizerSet/ParameterSet.nut` exposes 49 ParameterSet rows and `SequenceSet.nut` exposes 57 SequenceSet rows. The simulator parses these files only when present in a supplied rip. The real-retail validation input loaded all 49/57 rows.

Decoded script DAT timelines are also inspected for `VL_SEQUENCESET` commands. Retail validation found 39 such authored events across the 30 decoded Visualizer timelines, and the simulator exposes them as quick jump/apply entries. The event data remains external to the source-only toolkit.

## Host-side BGM approximation

The browser simulator can load a local audio file and estimate level with the Web Audio analyser. It maps approximately -60..0 dBFS to 0..1 for interactive preview. This is intentionally labelled a host approximation because the executable trace has not yet recovered the game's full upstream music-meter transfer curve.

## Still unresolved

- Exact fixed coordinates for Position Fix indices 1..9. The executable proves index 0 uses free X/Y and nonzero indices use a fixed-position method, but the final coordinate table/path is not yet fully reconstructed.
- Exact original audio-meter transfer curve before `FUN_82495360`.
- Any visual/compositing details not already constrained by the June 10 footage and decoded data.


## dev24 WIP166 presentation/audio bridge

The recovered Xenos feedback and SHAPE samplers remain point-filtered. To reflect the visibly softer final presentation in the game/reference capture without rewriting those recovered semantics, dataset v12 applies an optional display-only Canvas blur after the feedback result; default 0.65 px, range 0..2 px, with 0 disabling it. This does not feed back into the recursive surface.

For host BGM, static browsers do not reliably decode Xbox WMA or PS3 AT3/ATRAC3+. When the simulator is generated from a user rip and FFmpeg is available, the toolkit discovers those native BGM files and creates browser-safe local MP3 previews (AAC/M4A fallback), keyed by source SHA-256. The native files are not modified. Retail cross-check: 53/53 Xbox WMA and 56/56 PS3 AT3 tracks produced previews; both retain 30 decoded Visualizer timelines / 243 commands.
