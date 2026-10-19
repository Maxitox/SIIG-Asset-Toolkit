# THE SUN runtime assembly — 2.10.0-dev19

## Scope

Dev19 resolves THE SUN's extended-arm body motion and the previously unidentified `bos_002b.gmx` component without merging evidence that the executable does not directly synchronize.

## Native body and extended arms

Retail runtime type `0x47` maps to `bos_002.gmx`. The retail asset is 78,016 bytes with 8 meshes, 9 bones and six native matrix-animation tracks targeting `c1_E`, `d1_E`, `d2_E`, `c1_F`, `d1_F`, and `d2_F`. Each track contains 41 logical samples on the toolkit's established 30 Hz runtime clock.

Sample 0 has `c1_E/c1_F` X scale approximately `0.077`; the paired `d1/d2` endpoints are near `+148.683/-148.686`. At sample 40, `c1_E/c1_F` reaches X scale `1.0` and the paired endpoints have crossed to approximately `-34.058/+34.056`. Retail visual controller `0x47` (`Function_8212B638`, update `Function_8212B760`) manipulates the relevant internal model nodes directly. No external arm GMXs are required.

Dev19 therefore adds:

- `the_sun_native_body` — identity outer transform with all six native tracks retained;
- `the_sun_extended_arms` — the same body with native logical sample 40 baked as a static inspection pose.

## `bos_002b.gmx` / runtime `0xB3`

The neighboring `0x48` visual controller owns allocation of the auxiliary pools. `Function_8212BB58` allocates `0xB2` as a group of 8 and up to 48 `0xB3` objects. Its update path (`0x8212BD80` -> `Function_8212BBF0`) consumes four fixed-point wave groups from shared stage state.

For each wave group, active `0xB3` count is `max(length,0) >> 9`. Active instances are placed at:

- `X = (x0 + span/2) / 256`
- `Y = 0`
- `Z = start/256 + 2*segment_index`

Unused `0xB3` instances are disabled.

Retail THE SUN constructor `Function_821B22C0` initializes four groups:

| group | `x0` | `start` | `span` | `length` |
|---:|---:|---:|---:|---:|
| 0 | `0x3900` | `0xC800` | `0x1800` | `0` |
| 1 | `0x9900` | `0xC800` | `0x1800` | `0` |
| 2 | `0xF900` | `0xC800` | `0x1800` | `0` |
| 3 | `0x15900` | `0xC800` | `0x1800` | `0` |

Retail `moveTheSun` (`Function_8223AEC0`) subtracts 512 from `start` while adding 512 to `length` until `length=0x1800`. At the full ramp:

- `start = 0xB000 = 176.0`
- `length = 0x1800 = 24.0`
- `length >> 9 = 12` segments per group
- total active `0xB3` instances = `4 * 12 = 48`

The exact full-ramp segment centers are therefore X `69, 165, 261, 357`, each paired with Z `176,178,...,198`.

Fresh retail `bos_002b.gmx` is 4,992 bytes, contains 2 meshes / 3 bones, has no native animation tracks, and is a thin static tile/slab. Dev19 adds `the_sun_long_wave`, an exact 48-instance static inspection field using these executable-derived transforms.

## Evidence boundary

The executable evidence proves the body animation samples and the B3 maximum-wave field independently. It does **not** prove that `bos_002.gmx` sample 40 occurs at the exact same frame as the 48-segment full-ramp state. Dev19 therefore deliberately keeps the extended-arm body and long-wave field as separate presets rather than manufacturing a synchronized composite.

## Independent cross-check

June 10 preserves the same `0xB2` count 8, `0xB3` capacity 48, four-group update formula, `length >> 9` segment count and `0x1800` limit. The iOS 4.1.0 binary retains the ancestral `_setTheSun` / `_moveTheSunWaveShot` four-group concept, but console coordinates are used for dev19.
