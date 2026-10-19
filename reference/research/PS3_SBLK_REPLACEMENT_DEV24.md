# PS3 SBlk fixed-slot replacement — dev24 WIP161

## Scope

WIP161 adds the first native audio replacement path without claiming a general Sony bank compiler. The existing SIIG PS3 reader already proves the retail bank's 84 waveform entries, mono Sony PS-ADPCM payloads, sample-rate metadata, stream offsets/sizes, names, and complete audio-region coverage. The new path deliberately reuses an **original SBlk as the structural template**.

For one selected PS-ADPCM stream, the input WAV must be mono uncompressed PCM16 with exactly the slot's decoded sample count and sample rate. The builder then:

1. reads the original PS-ADPCM frame-control byte from every 16-byte frame;
2. encodes each 28-sample PCM block with the five standard decoder predictors and a deterministic residual/quantization search;
3. preserves each original frame-control byte in the same frame position;
4. rejects non-zero replacement samples in a template frame whose control value renders that frame silent;
5. replaces only the existing audio payload range; and
6. reparses the rebuilt bank and requires the selected stream metadata and overall bank size to remain unchanged.

No stream offset, byte capacity, table, name, loop/end control position, sample-rate field, or unrelated payload is rewritten.

## Regression evidence

The source-only regression creates a synthetic one-stream big-endian SBlk v3 fixture with a 48 kHz two-frame PS-ADPCM slot. A generated 440 Hz PCM16 test tone encodes to two native frames, decodes with a maximum absolute error of 61 sample units in the fixture, and replaces the slot without changing the bank header/table bytes or stream metadata. No proprietary audio is bundled.

The retail project bank was previously validated for **84/84 decode** and complete audio-region accounting. WIP161 does not claim an edited-retail runtime test because the retained Library search did not surface the proprietary bank as a directly reusable validation input in this checkpoint, and source-only regression is not a substitute for console/emulator acceptance.

## Remaining boundary

This closes only fixed-capacity **same-slot PS3 SBlk replacement**. It does not yet provide:

- variable-duration SBlk stream resizing/offset-table rebuilding;
- insertion/removal/reordering of sounds/grains/waves/names;
- newly authored loop/end marker policy;
- runtime acceptance evidence for modified PS3 banks; or
- Xbox 360 XACT/XMA2 native replacement-bank construction.
