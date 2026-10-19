# SG_GIGANTIC_UFO runtime 0x9E DAT reconstruction — dev24

Status: development research for unsealed `2.10.0-dev24`.

## Ownership and opcode dispatch

Retail runtime `0x9E` is the existing `SG_GIGANTIC_UFO` / `bos_003.gmx` family. `Function_821489F8(runtime_type + 1)` selects case `0x9F`, allocates a `0x228`-byte controller, and constructs **`Function_8211B560`**.

The enemy-opcode dispatcher `Function_820E8940` indexes handlers by `opcode - 0x96`; opcode `0x9E` therefore selects **`Function_820E82C0`**. That handler calls the common enemy initializer through `Function_820E7F68`, passes `FUN_8211AA28()` as the component count, then allocates auxiliary pools `0x42 x36` and `0x43 x60`.

`FUN_8211AA28()` sums the three renderer-group counts `1 + 3 + 36 = 40`: one `0x9E` root, three `0xB4` helper/control slots, and thirty-six `0xB5` / `bos_003a.gmx` weapon modules. This matches the already reconstructed 37-model visible hierarchy, where the three `0xB4` slots are deliberately not exported as models.

## Exact 10-argument DAT layout

The common initializer `Function_820E7CE0` consumes arguments 0..4. Retail vtable `PTR_Function_8211B718_82009C18` has raw PPC **`0x8211A8B8`** at +`0x5C`. That stub loops exactly five times and copies five signed 16-bit values from the DAT-tail pointer into controller offsets `+0x1DC..+0x1E4`. Since `Function_820E7F68` passes `record + 0x0E` to that vtable slot, the copied values are exactly arguments 5..9.

| Arg | Semantic | Retail evidence |
|---:|---|---|
| 0 | `spawn_condition` | common conditional-spawn gate |
| 1 | `body_hp` | `Function_820E7CE0` writes root element 0 of both baseline/max and current HP arrays |
| 2 | `travel_speed_raw512` | common initializer stores `arg2 / 512` at `+0x1AC`; `Function_8211AB80` uses it to scale waypoint movement |
| 3 | `start_x` | common initial X at `+0x1A0` |
| 4 | `start_z` | common initial Z at `+0x1A8` |
| 5 | `child_hp` | copied to `+0x1DC`; `Function_8211AAD0` writes it into every non-root HP slot |
| 6 | `waypoint0_x` | copied to `+0x1DE`; `Function_8211AB80` reads it as waypoint 0 X |
| 7 | `waypoint0_z` | copied to `+0x1E0`; `Function_8211AB80` reads it as waypoint 0 Z |
| 8 | `waypoint1_x` | copied to `+0x1E2`; `Function_8211AB80` reads it as waypoint 1 X |
| 9 | `waypoint1_z` | copied to `+0x1E4`; `Function_8211AB80` reads it as waypoint 1 Z |

`Function_8211AB80` constructs each target as `(x, 0, z)`, normalizes the vector from the current root position, scales it by the common speed field, snaps when within one update, advances from waypoint 0 to waypoint 1, then enters the later movement state. Therefore these are authored route coordinates rather than generic variant/timing values.

`child_hp` applies to the controller's complete non-root HP array: the three `0xB4` helper/control slots and all thirty-six `0xB5` weapon modules. The visible GMX export still contains only the root plus 36 `bos_003a` models because the `0xB4` entries are not model assets.

## June 10 cross-check

June 10 independently preserves the same schema despite a controller-layout shift:

- opcode `0x9E` handler: `Function_820FAC48`;
- runtime+1 case `0x9F`: `Function_82135360`, object size `0x22C`;
- vtable +`0x5C`: raw PPC `0x821344E0`, again copying exactly five signed shorts;
- copied tail offsets: `+0x1E0..+0x1E8` (four bytes later than retail);
- child-HP initializer: `Function_821346F8`;
- two-waypoint route update: `Function_821347A8`.

The bundled June-10 opcode census records 13 commands for `0x9E`, while the current retail semantic corpus contains 12. The code-level five-common-plus-five-tail contract is the same in both builds; their occurrence counts are therefore kept distinct rather than merged.

## Retail corpus

The current retail Stage Explorer corpus exposes 12 records, all exactly 10 arguments long:

- `level4_stage3.dat` @ 61743: `[0, 5000, 256, 737, 100, 100, 737, 100, -310, 0]`
- `level4_stage3.dat` @ 89043: `[0, 5000, 256, -310, 100, 100, -310, 100, 737, 0]`
- `level4_stage3.dat` @ 532123: `[0, 2500, 256, 737, 80, 100, 377, 0, 377, 361]`
- `level4_stage3.dat` @ 547053: `[0, 2500, 256, -310, 80, 100, 50, 0, 50, 361]`
- `level4_stage3.dat` @ 567653: `[0, 5000, 256, 737, 360, 100, -120, 120, 737, -120]`
- `level4_stage3.dat` @ 571253: `[0, 5000, 256, -310, -120, 100, 547, 120, -310, 360]`
- `level4_stage3.dat` @ 640313: `[0, 5000, 256, 213, -500, 100, 213, -500, 213, 50]`
- `level4_stage5.dat` @ 64767: `[0, 2500, 256, 737, 120, 100, 737, 120, 213, 50]`
- `level5_stage1.dat` @ 97339: `[1, 500, 2560, 737, 100, 100, 737, 100, -600, 0]`
- `extra1_stage9.dat` @ 21: `[0, 2000, 256, 900, 200, 1000, -400, 0, 213, 0]`
- `extra5_stage1.dat` @ 23092: `[0, 3000, 256, 213, -200, 100, 213, -200, 213, 0]`
- `trial_level5_stage1.dat` @ 97339: `[1, 500, 2560, 737, 100, 100, 737, 100, -600, 0]`


Observed ranges in this corpus:

- `body_hp`: 500, 2000, 2500, 3000, or 5000;
- `travel_speed_raw512`: 256 (0.5 native) or 2560 (5.0 native);
- `child_hp`: normally 100, with the Extra 1-9 encounter using 1000;
- route coordinates include both long off-screen traversals and short local two-point routes.

The `level5_stage1.dat` and `trial_level5_stage1.dat` records are byte-identical at this command and are retained as two authored stage occurrences, not deduplicated.

## Toolkit integration

`decode_dat_semantics(0x9E, ...)` is now high-confidence and names all ten fields. `gigantic_ufo_complete` runtime metadata records the controller factory, opcode handler, five-short tail-copy boundary, child-HP initializer, two-waypoint route update, auxiliary pools, and the June 10 cross-build confirmation.

A dedicated dev24 regression protects all 12 retail records, the raw/512 speed conversion, body/child HP separation, waypoint ordering, and the existing 1 + 3 + 36 runtime hierarchy. No proprietary DAT/XEX payload is bundled.
