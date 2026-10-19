# GREED runtime 0x99 reconstruction — dev24

Status: **retail executable-backed runtime semantics with conservative snapshots**.

## Ownership

The retained registry maps runtime `0x99` to `emy_046.gmx` and the retained lineage identifies the entity as **GREED**.

`Function_821489F8` switches on `runtime_type + 1`, so runtime `0x99` selects switch case `0x9A`, which allocates `Function_82103C58`.

Opcode `0x99` is routed by `Function_820E8940` through its handler table to `Function_820E80E0`. The latter uses the common spawn/configuration path and also creates the linked auxiliary object used by this enemy family.

## DAT field mapping

Common initializer `Function_820E7CE0` consumes:

- arg0: spawn condition;
- arg1: common entity parameter;
- arg2: travel speed, stored as `arg2 / 512`;
- arg3: start X;
- arg4: start Z.

The GREED vtable `+0x5C` routine is raw-PPC label `0x82103C10`. It copies five signed shorts from DAT args 5..9 into controller offsets `+0x1E0..+0x1E8`, then multiplies the final two timing values by `60/30`:

- arg5: target X;
- arg6: target Z;
- arg7: post-hover negative-Z motion input, fixed 8.8 before runtime frame compensation;
- arg8: radial-burst interval in authored 30 Hz ticks; stored as `arg8 * 2` normal runtime ticks;
- arg9: hover duration in authored 30 Hz ticks; stored as `arg9 * 2` runtime ticks.

`Function_820E8940` additionally treats opcode `0x99` specially: it reads arg10 and writes `(0,0,arg10)` through `FUN_820F9C70`. `Function_82103E18` converts its sign into the full-turn approach rotation direction. A positive input therefore selects the negative Z rotation sign; a negative input selects the positive sign; zero supplies no Z spin component.

## State machine

`Function_82103E18` initializes the body at `(start_x, -1000, start_z)`, computes a velocity toward `(target_x, -1000, target_z)`, configures the approach rotation, and enters state 0.

`Function_82104020` then implements:

- **state 0 — approach:** moves toward the DAT target and transitions when the target is reached;
- **state 1 — hover/attack:** `Function_820F99F8` seeds the controller at the DAT target. `Function_820F9AA8` then moves X toward the live player X at 1 native unit/update under normal timing, clamps the 100-unit-wide footprint so its center stays within X=50..377, and moves Z at 0.2 units/update with direction reversing every 60 elapsed runtime ticks. At the configured interval, `Function_82103B50` emits an eight-way radial burst. Once elapsed time exceeds the scaled arg9 duration, state 2 begins;
- **state 2 — exit:** Z decreases by `(arg7 / 256) * 60 / (runtime_frame_multiplier * 30)` per update until the common out-of-bounds test removes the object.

Because state-1 X explicitly depends on live player position, dev24 does not bake a guessed full hover trajectory. The deterministic X-rate/clamp and Z triangle-wave rules are retained as runtime metadata.

## Concrete Level 4-1 encounter

`level4_stage1.dat`, command 24 / frame 711:

`[0, 2000, 20480, 213, 360, 213, 80, 5120, 10, 150, 1]`

This means:

- common travel speed `20480 / 512 = 40`;
- exact spawn X/Z `(213,360)` at native Y `-1000`;
- exact first hover-entry target `(213,80)` at the same Y;
- post-hover Z-motion raw value `5120`;
- shot interval `10` authored ticks -> `20` normal runtime ticks;
- hover duration `150` authored ticks -> `300` runtime ticks;
- positive approach-spin input.

Dev24 exposes two exact snapshots: `greed_retail_level4_1_spawn`, `greed_retail_level4_1_approach_trace`, and `greed_retail_level4_1_hover_entry`. The five-copy approach trace is an inspection trail of exact normal-timing state-0 positions, not simultaneous gameplay duplicates; the hover-entry catalog represents the exact controller seed/target anchor rather than asserting a rendered body pose.

## Retail script coverage

The retained retail DAT corpus contains seven opcode `0x99` records. Six carry arg10 explicitly and one shorter Extra-stage record carries only args0..9. The core args0..9 state machine is therefore encoded independently of the optional/following spin-sign word; the toolkit does not invent a missing arg10 for the shorter record.
