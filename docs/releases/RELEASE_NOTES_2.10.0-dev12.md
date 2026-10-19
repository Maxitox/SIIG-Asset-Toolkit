# SIIG Asset Toolkit 2.10.0-dev12

Dev12 resolves UNKNOWN's flashing appearance as an executable-driven **internal-form selector inside one `bos_006.gmx`**, not a multipart boss assembly.

## UNKNOWN forms

- Added exact catalogs `unknown_form_01` through `unknown_form_14`; each exports one native `ukXX` subtree from the original GMX.
- Added `unknown_all_forms` for one-scene research/Outliner inspection.
- Fresh retail GMX validation proves 14 named branches but only **13 unique visuals**: `uk08` is an exact visual duplicate of `uk01`.
- The normal console cycle uses only `uk01..uk12`; because of the duplicate, this is 12 named selections / 11 unique visuals.
- `uk13` and `uk14` remain valid renderer-registered branches but are outside the normal 12-tick console gameplay cycle traced here.

## Runtime cadence

Retail Xbox draw `0x821302E8` and move `0x82240DD0`, June 10 draw `0x8214B4C0` / move `0x822682A0`, and retail PS3 draw `0x001D5148` / move `0x001039EC` preserve the same selector/counter architecture. Normal form changes occur at the normalized 30 Hz logic rate, so one twelve-selection loop is about 0.4 seconds. State 0 explicitly forces `uk01`; state 23 freezes the selector.

No fake native GMX animation is synthesized: `bos_006.gmx` contains no MOTN/ANIM tracks. GUI 0.23.0-dev12 instead exposes exact manual form selection in Simple and Advanced modes and marks `uk08` as the duplicate of `uk01`.

No proprietary game files or generated retail glTF files are bundled.
