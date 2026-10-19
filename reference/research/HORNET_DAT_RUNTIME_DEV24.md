# HORNET retail DAT/runtime mapping — dev24

Status: executable-backed, high confidence. This note covers retail Xbox runtime `0xA1` / script opcode `0xA1` (internal opcode label `HONET`) and the June 10 prototype cross-check.

## Factory and opcode ownership

- Runtime+1 dispatch case `0xA2` constructs retail `Function_8211E1C0` (object size `0x290`).
- Script opcode `0xA1` dispatches to retail `Function_820E8390`.
- `Function_820E8390` uses common `Function_820E7F68` / `Function_820E7CE0` and allocates auxiliary runtime type `0x48` x180.
- Retail controller vtable is `PTR_Function_8211E6C8_8200A0D8`.

## Exact DAT tail width

Retail vtable slot `+0x5C` is raw PPC stub `0x821245D8`:

- copy DAT arg5 to controller `+0x1C8`
- copy DAT arg6 to controller `+0x1CA`
- return

Therefore retail HORNET has exactly two controller-specific signed 16-bit arguments after the five common enemy arguments: seven DAT arguments total.

June 10 independently retains the same two-short contract. Runtime+1 case `0xA2` constructs `Function_82138358` (object size `0x294`), opcode handler is `Function_820FAD18`, and vtable `+0x5C` is `Function_82135708`, which copies the same two words to `+0x1CC/+0x1CE`. The four-byte shift is a controller-layout change, not a DAT-schema change.

Most importantly, the June 10 build still contains debug labels for those two copied values:

- first tail value: `break_hp`
- second tail value: `bit_hp`

These labels remove the ambiguity left by the optimized retail build.

## Seven retail arguments

| arg | semantic | evidence |
|---:|---|---|
| 0 | `spawn_condition` | common conditional-spawn path |
| 1 | `core_hp` | common handler initializes root HP slot 0; A1 / `bos_008.gmx` is the HORNET core/root |
| 2 | `common_speed_raw512` | common initializer stores `arg2 / 512` at `+0x1AC`; no narrower HORNET-only motion meaning is asserted |
| 3 | `position_x` | common controller X at `+0x1A0` |
| 4 | `position_z` | common controller Z at `+0x1A8` |
| 5 | `break_hp` | retail tail copies to `+0x1C8`; `Function_8211D648` seeds the break accumulator/threshold from it; damage callback `Function_8211C7C0` subtracts incoming damage, activates the next armor bit when exhausted, and reloads it; June debug label is literally `break_hp` |
| 6 | `bit_hp` | retail tail copies to `+0x1CA`; `Function_8211C7C0` assigns it to newly activated bits and `Function_8211D990` restores it across the owned secondary records; June debug label is literally `bit_hp` |

The apparent countdown-looking operation in retail is therefore damage-driven, not time-driven. The cross-build debug labels are the decisive correction: arg5 is a break-HP threshold, not a reveal interval.

## Six retail records

| stage | frame | args |
|---|---:|---|
| `level4_stage2.dat` | 340983 | `[0,10000,256,213,120,40,40]` |
| `level5_stage2.dat` | 431109 | `[0,3000,256,213,120,40,40]` |
| `level5_stage5.dat` | 87230 | `[0,3000,256,213,120,40,40]` |
| `extra2_stage7.dat` | 66 | `[0,10000,256,213,100,10,100]` |
| `extra4_stage4.dat` | 762115 | `[0,10000,256,213,120,40,40]` |
| `extra4_stage6.dat` | 20416 | `[0,10000,256,213,120,40,40]` |

All retail records use raw common scalar 256 (`0.5` after `/512`). The bonus `extra2_stage7` encounter independently varies both tail fields (`break_hp=10`, `bit_hp=100`) while the standard records use `break_hp=40`, demonstrating that the two authored values are distinct controls.

## June 10 corpus cross-check

`DAT_OPCODE_TABLE.csv` reports opcode `0xA1` with seven June 10 occurrences and observed word count 9. Since a record contains delta-frame + opcode + arguments, word count 9 independently confirms the same seven-argument DAT shape.

## Claim boundary

The names `break_hp` and `bit_hp` are retained executable debug strings, not inferred labels. `common_speed_raw512` deliberately stays generic because the `/512` common storage is proven while no unique HORNET-only consumer justifies a narrower motion label.
