# GLUTTONY runtime 0x9C DAT reconstruction — dev24

Status: development research for the unsealed `2.10.0-dev24` branch. Sealed `2.10.0-dev23` remains unchanged.

## Controller ownership

Retail `Function_821489F8` dispatches enemy visual controllers through `runtime_type + 1`. Runtime `0x9C` therefore selects switch case `0x9D`, which constructs `Function_82103878`. This is the GLUTTONY controller and agrees with the previously recovered `emy_050.gmx` body plus two `emy_050a.gmx` helpers.

The GLUTTONY vtable includes setup `Function_82102F68`, configuration/setup `Function_82103A88`, route/update `Function_821034D0`, route initialization `Function_82103380`, and a raw PPC copy stub at `0x82102F58`.

## Exact 25-word DAT layout

The generic enemy initializer `Function_820E7CE0` consumes the common prefix. The raw PPC at vtable +0x5C (`0x82102F58`) then copies exactly `0x28` bytes from the DAT-tail pointer into controller `+0x1C8`: 20 signed 16-bit words, exactly arguments 5..24.

| Arg | dev24 semantic | Runtime evidence |
|---:|---|---|
| 0 | `spawn_condition` | common conditional-spawn gate |
| 1 | `body_hp` | written to root element 0 of both +0xF0 baseline/max and +0x100 current HP arrays |
| 2 | `travel_speed_raw512` | stored as `arg2 / 512.0` at +0x1AC and consumed by route update |
| 3 | `path0_x` | common X at +0x1A0; route point 0 X |
| 4 | `path0_z` | common Z at +0x1A8; route point 0 Z |
| 5..22 | `path1_x/z` .. `path9_x/z` | copied to +0x1C8 and consumed as up to nine additional X/Z pairs |
| 23 | `path_point_count` | copied to +0x1EC; total route point count, 1..10 |
| 24 | `helper_hp` | copied to +0x1EE; written to helper HP slots 1 and 2 for both `emy_050a` helpers |

`Function_82103380` builds the route with point 0 from args3/4 and then reads `point_count - 1` additional X/Z pairs from args5..22 before handing the path to `Function_820FE160`. `Function_821034D0` advances along that route using the common `arg2 / 512` speed.

The final word is **not a timer**. `Function_82103380` writes arg24 into helper indices 1 and 2 of both HP arrays, and `Function_821031A0` later tests current-HP entries 1 and 2 to decide when neither helper remains alive. This also strengthens arg1 as root/body HP: the common initializer writes arg1 into element 0 of the same HP arrays, while generic damage code decrements +0x100 current HP.

## Seven retail records

All seven available retail opcode-`0x9C` records now decode with the same schema:

| Stage | Body HP | Speed | Point count | Authored X/Z route | Helper HP |
|---|---:|---:|---:|---|---:|
| `level5_stage4.dat` | 3000 | 2.0 | 6 | `(335,320) -> (335,-160) -> (335,240) -> (335,140) -> (40,0) -> (40,-300)` | 500 |
| `level5_stage4.dat` | 3000 | 2.0 | 3 | `(95,320) -> (95,140) -> (-209,0)` | 500 |
| `level5_stage4.dat` | 3000 | 2.0 | 4 | `(-100,220) -> (213,80) -> (213,-120) -> (213,540)` | 500 |
| `level5_stage5.dat` | 500 | 1.5 | 4 | `(-120,120) -> (106,120) -> (106,0) -> (-1000,0)` | 100 |
| `level5_stage5.dat` | 500 | 1.5 | 4 | `(547,120) -> (320,120) -> (320,0) -> (1427,0)` | 100 |
| `extra1_stage7.dat` | 3000 | 0.5 | 10 | `(47,-80) -> (47,71) -> (47,167) -> (379,167) -> (379,71) -> (213,71) -> (213,100) -> (213,100) -> (213,100) -> (213,100)` | 500 |
| `extra3_stage2.dat` | 3000 | 1.0 | 8 | `(213,-100) -> (213,200) -> (387,40) -> (387,200) -> (40,40) -> (40,200) -> (213,80) -> (213,-121)` | 500 |

Repeated route points in the 10-point bonus record are authored data and are intentionally preserved instead of normalized away.

## Toolkit consequence

`decode_dat_semantics(0x9C, ...)` is now high-confidence and names all 25 arguments. `_gluttony_path_points_from_args()` reproduces all seven retail routes. The `gluttony_complete` assembly metadata records the factory, config-copy boundary, DAT argument layout, route setup/update, and existing live helper-aim boundary.

A dedicated dev24 regression covers all seven retail records, including route order, point counts, body/helper HP, and raw/512 speed conversion. The branch remains WIP/unsealed.
