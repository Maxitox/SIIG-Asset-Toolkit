# CENTIPEDE retail DAT/runtime mapping — dev24

Status: executable-backed, high confidence. This note covers retail Xbox runtime `0xA0` / script opcode `0xA0` (`CENTIPEDE`) and the June 10 prototype cross-check.

## Factory and opcode ownership

- Runtime+1 dispatch case `0xA1` constructs retail `Function_82116478` (object size `0x210`).
- Script opcode `0xA0` dispatches to retail `Function_820E8330`.
- `Function_820E8330` uses common `Function_820E7F68` / `Function_820E7CE0` and allocates auxiliary runtime type `0x44` x60.
- Retail controller vtable is `PTR_Function_82116640_82009810`.

## Exact DAT tail width

Retail vtable slot `+0x5C` is raw PPC stub `0x82112080`:

- `lhz r11,0(r4)`
- `sth r11,0x1DC(r3)`
- return

Therefore retail CENTIPEDE has exactly one controller-specific signed 16-bit argument after the five common enemy arguments: DAT arg5.

June 10 independently retains the same contract. Its runtime+1 case `0xA1` constructs `Function_8212FD50` (object size `0x214`), opcode handler is `Function_820FACB8`, and vtable `+0x5C` is `Function_8212B620`, which copies exactly one short to `+0x1E0`. The four-byte offset shift is a controller-layout change, not a DAT-schema change. `DAT_OPCODE_TABLE.csv` reports June 10 word count 8, which is exactly delta-frame + opcode + the same six arguments.

## Six retail arguments

The high-confidence retail schema is:

| arg | semantic | evidence |
|---:|---|---|
| 0 | `spawn_condition` | common conditional-spawn path |
| 1 | `a0_form_hp` | `Function_820E7CE0` initializes root HP slot 0; `Function_821132A8` copies that HP to each link record's `+0x78` A0 counterpart |
| 2 | `common_speed_raw512` | common initializer stores `arg2 * 0.00390625 * 0.5 = arg2 / 512` at `+0x1AC`; no narrower CENTIPEDE-only interpretation is asserted |
| 3 | `ring_center_x` | common X `+0x1A0`; applied before ring construction |
| 4 | `ring_center_z` | common Z `+0x1A8`; applied before ring construction |
| 5 | `be_form_hp` | `0x82112080` copies it to `+0x1DC`; `Function_821132A8` writes it to every link record's `+0x7C` BE counterpart HP slot |

The A0/BE naming follows the executable's paired visual/runtime ownership. Retail `Function_82116690` constructs a fixed 32-link chain with paired A0 and BE handles. `Function_82115028` + `Function_82113148` select the A0 counterpart for role 1/3 endpoints and the BE counterpart for role 2 body links. This is why arg1 and arg5 are not two arbitrary HP values: they are the HP values for the two switchable forms.

## Ring center and geometry

`Function_821132A8` invokes the common transform setup before the ring enters its first state. `Function_821133A0` then constructs all 32 links around the controller position with:

- radius: `80.0`
- angular spacing: `11.25` degrees
- first angle: `-90` degrees

Thus args3/4 are more specifically the authored ring-center X/Z coordinates, not generic `variant/position_x` words.

## Seven retail records

The available retail stage corpus contains seven `0xA0` commands, all with six arguments:

| stage | frame | args |
|---|---:|---|
| `level4_stage1.dat` | 234095 | `[0,400,256,213,120,160]` |
| `level5_stage1.dat` | 201920 | `[0,150,256,213,120,20]` |
| `level5_stage5.dat` | 14892 | `[0,150,256,213,120,20]` |
| `extra2_stage7.dat` | 41 | `[0,500,256,213,100,100]` |
| `extra4_stage3.dat` | 298194 | `[0,400,256,213,120,160]` |
| `extra4_stage6.dat` | 8752 | `[0,400,256,213,120,160]` |
| `trial_level5_stage1.dat` | 201920 | `[1,150,256,213,120,20]` |

All retail records use raw common speed 256 (`0.5` after `/512`). The repeated normal/trial Level 5-1 payload differs only in spawn condition, which is preserved exactly.

## Boundary of the claim

The project intentionally calls arg2 `common_speed_raw512`, not `travel_speed`, because the common initializer conversion is proven while a unique CENTIPEDE-only consumer that would justify a narrower motion label has not been isolated. The HP-form and ring-center semantics above are directly controller-backed.
