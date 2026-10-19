# SIIG audio notes

## Xbox 360 — XACT3/XMA2

`sound.bin` contains nested XSB/XWB banks. The retail Xbox corpus resolves 86 named streams: 83 SE cues plus `BGM007`, `BGM008_MIX_C`, and `BGM_XACT_SE33`. The toolkit writes RIFF/XMA2 wrappers and invokes FFmpeg when available for PCM WAV output; FFmpeg is not bundled.

```bat
python siig_toolkit.py xact2wav sound.bin -o audio
```

The supplied retail Xbox regression decodes 86/86 streams with zero failures when FFmpeg is available. Ready WMA media is copied unchanged.

### Mod Workspace Xbox replacement (dev24 WIP187)

The Simple Mod Workspace exports `sound.bin` as editable named WAVs and rebuilds changed slots without requiring the original duration, rate, or channel count. The builder rewrites each edited XWB entry's duration, mini-wave format and play region, repacks the wave-data segment, and proportionally remaps any existing loop begin/length to the replacement sample count. PCM16 input with 1–6 channels remains 1–6 channels in the native XWB; 7–64-channel input is accepted and downmixed to stereo. Since FFmpeg does not provide an XMA2 encoder, untouched XMA2 streams remain byte-identical and edited slots become XACT-supported PCM16. Xbox big-endian 16-bit PCM is byte-swapped during authoring.

The supplied retail bank was structurally exercised by changing one looped XMA2 slot to 3-channel, 32 kHz, 12,345-sample PCM16; the nested XWB/BBX reparsed with the rewritten format, duration, play region and loop region. This does not replace emulator/hardware runtime testing. Native XMA2 encoding remains future work.

## PlayStation 3 — Sony 989SND/SCREAM SBlk v3

The retail PS3 bank is a big-endian Sony SBlk v3/989SND bank. The current narrow parser resolves all 84 sound/grain/wave entries and names, and the full 4,200,384-byte audio region is accounted for by the 84 streams. SIIG uses mono Sony PS-ADPCM for these entries.

```bat
python siig_toolkit.py sblk2wav sound.bnk -o ps3_audio
```

The built-in decoder exports 84/84 PCM WAV files with zero failures on the supplied retail bank and retains the source `.bnk`. vgmstream remains a recommended general-purpose fallback for unrelated Sony bank variants.

### Flexible PS3 replacement (dev24 WIP187)

`mod-export` / `mod-build` and `sblk-replace` now accept PCM16 WAV replacements with arbitrary duration and sample rate. The builder downmixes multichannel input to mono, because the SIIG SBlk v3 stream form is mono; it does not fabricate an unsupported per-stream channel-count field. It PS-ADPCM-encodes the new stream, regenerates loop/end control flags, repacks the complete contiguous bank data section, rewrites all affected stream offsets/sizes, and rewrites the selected stream's center-note/fine pitch to the nearest representable SCREAM playback rate.

A supplied retail 84-stream bank was structurally exercised with a stereo 32 kHz, 10,003-frame input. It rebuilt as native mono at the nearest representable ~32 kHz rate, resized the target payload, shifted all later offsets, preserved untouched stream bytes, and retained complete contiguous coverage. True multichannel SBlk topology synthesis and runtime acceptance remain separate boundaries.

### Fixed-slot PS3 replacement (dev24 WIP161)

A conservative native replacement path is now available for the SIIG SBlk subset:

```bat
python siig_toolkit.py sblk-replace sound.bnk 12 edited.wav -o sound_mod.bnk
python siig_toolkit.py sblk-replace sound.bnk SE_PLAYER_SHOT edited.wav -o sound_mod.bnk
```

The selector is a 1-based stream index or exact stream name. The WAV must be **mono, uncompressed PCM16**, with the **same sample rate and exact PCM sample count** as the selected slot. The builder encodes Sony PS-ADPCM independently, then replaces only that slot's existing audio bytes. It preserves the original stream offset/byte capacity, all SBlk tables/names, and every original per-frame control byte (including loop/end markers). Frames whose original control byte renders them silent must remain silent in the replacement.

This is intentionally not a variable-duration bank compiler: it will not resize streams, move later payloads, invent loop metadata, or rewrite bank topology. The rebuilt bank is reparsed structurally and its unchanged layout is regression-checked. Runtime acceptance of edited banks still requires PS3 emulator/hardware validation.

## Provenance

The SIIG-specific Python parser/decoder is locally authored from the supplied retail bank and synthetic tests. Table/field behavior was cross-checked against vgmstream's public `src/meta/bnk_sony.c`, and PS-ADPCM behavior was cross-checked against `src/coding/psx_decoder.c`. No vgmstream source is vendored or copied into the package; see `docs/project/THIRD_PARTY_NOTICES.md`.
