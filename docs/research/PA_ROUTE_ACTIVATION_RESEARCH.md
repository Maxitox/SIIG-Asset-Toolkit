# PA-route / special-route activation research

This note records the cross-build evidence begun in **2.8.0-dev8** and extended through **2.8.0-dev10**. `PA` is retained exactly as the prototype debug identifier (`Route::SetPaRoute`); its expansion is unknown and is intentionally not guessed.

## Why both PS3 and Xbox 360 executables matter

The retail PS3 EBOOT has cleaner direct resource/call relationships in several route/camera paths, while the Xbox 360 prototypes retain debug/source strings that supply original class and method names. The current model therefore treats neither platform as universally authoritative: behavior is matched by function shape, state layout, resources, vtable role, and cross-build comparison.

## Route::SetPaRoute correspondence

| Build | SetPaRoute | activation wrapper | stage/setup routine | gate |
|---|---:|---:|---:|---:|
| PS3 retail | `0x0015AEBC` | `0x001580DC` | `0x00161134` | `0x000EA2E0` |
| Xbox 360 retail | `0x820EAFC8` | `0x820EABE8` | `0x820EFA98` | `0x8221CBE0` |
| Xbox 360 June 10 | `0x820FDE88` | `0x820FDAE0` | `0x82104860` | `0x82243F78` |
| Xbox 360 May 11 | `0x820FCD50` | `0x820FC9A8` | `0x82101C90` | `0x82238A18` |
| Xbox 360 May 9 | `0x820FCB28` | `0x820FC718` | corresponding setup does not activate this branch | not observed in corresponding setup |

June 10, May 11, and May 9 retain the literal debug string `Route::SetPaRoute`, which is used to name the stripped retail/PS3 equivalents by structural correspondence.

`Route::SetPaRoute` accepts indices 0 and 1 and formats `cam%02d_op1.gmx` using `index + 1`:

- index 0 -> `cam01_op1.gmx`
- index 1 -> `cam02_op1.gmx`

The known retail PS3/Xbox stage-setup path invokes the route vtable `+0x08` slot with **index 0**. No retail activation callsite selecting index 1 has yet been proven. Therefore dev8 reports cam02 as supported by `SetPaRoute`, not as proven stage-activated.

## Dev10: literal special-stage request recovered

The former boss→field “strong correlation” is now a direct script/executable chain. Retail opcode `0x78` (`WARNING`) writes its first argument to the reload parameter and resets the transition timer. Real retail scripts use `WARNING [12]` before Water Strider and `WARNING [14]` before Ultimate UFO; the retail reload routine maps 12 to Bmap13/descriptor 1/fld014 and 14 to Bmap15/descriptor 0/fld015. See `SPECIAL_STAGE_RELOAD_CHAIN_DEV10.md`. Boss spawn presence remains insufficient by itself to trigger the reload.


## Gate evolution

The retail stage/category helper classifies stage IDs as:

- `< 0x1F` -> category 0
- `0x1F..0x27` -> 1
- `0x28..0x30` -> 2
- `0x31..0x39` -> 3
- `0x3A..0x42` -> 4
- `0x43..0x4B` -> 5
- `0x4C..0xAE` -> 6
- `9999` -> 7
- otherwise -> 0

The activation gate changes across builds:

- **PS3 retail / Xbox retail / June 10:** category must be 0 and runtime state fields `+0x218 == 4`, `+0x21C == 1`.
- **May 11:** only `+0x218 == 4`, `+0x21C == 1`; the later category filter is absent.
- **May 9:** `Route::SetPaRoute` exists, but the corresponding setup path does not invoke the PA-route activation branch.

This is evidence of prototype evolution, not a platform difference between the final retail builds.

## Special boss-stage reload and field models

PS3 `0x00161A88` is a boss-stage reload path. It requests `Bmap%02d.bin` using `parameter + 1`, then selects the field descriptor passed to `0x00161134`:

- reload parameter `0x0C` -> descriptor index 1 -> `Bmap13.bin`
- reload parameter `0x0E` -> descriptor index 0 -> `Bmap15.bin`

The two runtime field descriptors are already decoded:

- descriptor 0 -> `fld015.gmx`, 0..6300, non-loop
- descriptor 1 -> `fld014.gmx`, 0..1440, loop

Cross-build prototype debug information identifies one external field-frame driver as `UltimateUfo::MoveMain`; the corresponding Water Strider class/vtable path drives the other timeline. Their frame behavior matches the descriptors exactly:

- **Water Strider** wraps at 1440 -> `fld014` / descriptor 1 / special parameter 0x0C / Bmap13.
- **Ultimate UFO** drives a long non-wrapping counter into the 6000s -> `fld015` / descriptor 0 / special parameter 0x0E / Bmap15.

The boss-to-field/model mapping is classified as **strong correlation**, not a single recovered literal boss->reload-parameter callsite. The toolkit keeps that distinction in `PA_ROUTE_BOSS_MAPPING.csv`.

## DAT evidence

Retail DAT opcodes:

- `0xA6` = `WATER_STRIDER`
- `0xA8` = `ULTIMATE_UFO`

Across the 76 supplied retail PS3 DAT files, the dev8 real-corpus scan finds six such occurrences:

- `extra2_stage8.dat`: WATER_STRIDER
- `extra5_stage6.dat`: WATER_STRIDER and ULTIMATE_UFO
- `level5_stage1.dat`: WATER_STRIDER
- `level5_stage3.dat`: ULTIMATE_UFO
- `trial_level5_stage1.dat`: WATER_STRIDER

Boss opcode presence alone does **not** prove PA-route activation at that DAT frame. Extra scripts can spawn these bosses outside the normal special encounter transition. `pa-route-info` therefore reports the correlation and an explicit warning instead of automatically switching playback modes.

## Machine-readable references

- `reference/tables/PA_ROUTE_BUILD_GATES.csv`
- `reference/tables/PA_ROUTE_FUNCTIONS.csv`
- `reference/tables/PA_ROUTE_CAMERA_SELECTIONS.csv`
- `reference/tables/PA_ROUTE_BOSS_MAPPING.csv`

## Remaining activation work

1. Recover the exact write/transition that supplies the boss-stage reload parameter to the global special-stage state.
2. Determine whether any retail path actually selects `Route::SetPaRoute(1)` / cam02.
3. Prove the exact transition time from normal procedural route to special field/camera mode.
4. Only after those points are resolved should automatic stage playback switch modes without caller input.
