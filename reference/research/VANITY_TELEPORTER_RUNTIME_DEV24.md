# VANITY / TELEPORTER runtime reconstruction — v2.10.0-dev24

Status: development research for the unsealed `2.10.0-dev24` branch.  Sealed `2.10.0-dev23` remains unchanged.

This note supersedes only the VANITY/TELEPORTER *WIP interpretations made after dev23 was sealed*.  The dev23 ownership research remains valid.  In particular, the early dev24 label `TELEPORTER state 2 tick 152` was disproven by raw PPC timer arithmetic and has been removed rather than preserved as if it were a reachable gameplay state.

## TELEPORTER (`0x0B`, `sbs_003*`)

### DAT -> runtime state

Retail DAT opcode `0x0B` dispatches directly to `Function_821AE858`.

For the retail World 5-4 pair:

| DAT | absolute frame | X | Z | mirror anchor X | width |
| --- | ---: | ---: | ---: | ---: | ---: |
| `level5_stage4.dat` | 603275 | 142 | 70 | 284 | 142 |
| `level5_stage4.dat` | 606305 | 284 | 70 | 142 | 142 |

`Function_821AE858` initializes:

- state = 0;
- normal initial timer = `(step * 600) / 30` = 20 at normal `step=1`;
- helper modes `table[0..8] = -1`;
- `table[9] = 426 - X` in 8.8 fixed point;
- `table[10] = abs(table[9] - X) >> 8`.

The X/Z arguments are therefore native coordinates.  The older generic `variant/position_x` interpretation was incorrect for this opcode.

### State machine timing

Retail update: `Function_82235D50`.

Raw PPC at `0x82235DE0..0x82235E00` and `0x82235E70..0x82235E8C` is decisive for state 2: the timer is reset to `(step * 30) / 30`, not to 30 updates.  `Function_820E0000` initializes the normal step field to 1, so a new negative helper slot is activated every normal update.

One deterministic transfer, stopping before the next randomized state-0 X selection, therefore has these renderer-visible samples:

| State | Samples | Action ticks | Visual |
| --- | ---: | --- | --- |
| 0 | 20 | 0..19 | two split roots converge from X±20 toward the DAT X |
| 1 | 30 | 20..49 | center root at source X |
| 2 | 14 | 50..63 | nine-helper transfer burst |
| 3 | 30 | 64..93 | center root at mirror anchor X |
| 4 | 20 | 94..113 | two split roots diverge from the anchor |

Total deterministic action: **114 samples** at the established 30 Hz logic cadence.  Tick 113 is state 4 / timer 1.  The next update re-enters state 0 and chooses a new random X, so dev24 intentionally stops there instead of inventing a loop.

### Reachable state-2 tables

The fourteen state-2 renderer snapshots are exactly:

```text
0  [-1,-1,-1,-1,-1,-1,-1,-1,-1]
1  [ 5,-1,-1,-1,-1,-1,-1,-1,-1]
2  [ 4, 5,-1,-1,-1,-1,-1,-1,-1]
3  [ 3, 4, 5,-1,-1,-1,-1,-1,-1]
4  [ 2, 3, 4, 5,-1,-1,-1,-1,-1]
5  [ 1, 2, 3, 4, 5,-1,-1,-1,-1]
6  [ 0, 1, 2, 3, 4, 5,-1,-1,-1]
7  [ 0, 0, 1, 2, 3, 4, 5,-1,-1]
8  [ 0, 0, 0, 1, 2, 3, 4, 5,-1]
9  [ 0, 0, 0, 0, 1, 2, 3, 4, 5]
10 [ 0, 0, 0, 0, 0, 1, 2, 3, 4]
11 [ 0, 0, 0, 0, 0, 0, 1, 2, 3]
12 [ 0, 0, 0, 0, 0, 0, 0, 1, 2]
13 [ 0, 0, 0, 0, 0, 0, 0, 0, 1]
```

On the next update slot 8 becomes zero and the controller immediately changes to state 3; a state-2 visual tick 14 does not exist.

Retail renderer `Function_8210B888` maps positive modes to widths `1/3, 2/3, 3/3, 2/3, 1/3` of the source-to-anchor distance and scales the helper in X by `width / 35`.  Its second pass also implements the unusual visibility rule where the newest zero-mode helper is hidden while older completed helpers are stacked at the destination.  The first `-1` causes that helper and all later not-yet-transferred helpers to remain visible in a source stack.

Dev24 exports:

- `teleporter_retail_5_4_left_transfer_cycle`
- `teleporter_retail_5_4_right_transfer_cycle`
- `teleporter_retail_5_4_left_state2_tick7`
- `teleporter_retail_5_4_right_state2_tick7`
- `teleporter_owned_visual_set` (identity inspection, retained)

The two full-cycle catalogs retain all 3 root visuals + 9 helpers and add one 114-sample STEP action.  Visibility is represented at the assembly-container level with zero/nonzero scale so native GMX subtrees and native animations are not flattened.

### Other retail encounters

The corrected DAT schema also exposes centered encounters at X=213 in `level2_stage5.dat` and `level3_stage5.dat`, plus several bonus-stage variants.  For X=213, mirror anchor X is also 213 and transfer width is zero; the same state machine runs but there is no lateral span to reconstruct.

## VANITY (`0x38`, `sbs_002` + 2×`sbs_002a`)

### DAT -> three visual coordinate records

Retail opcode `0x38` dispatches to `Function_821AF5A0`.

The handler initializes the primary X/Z record from DAT start coordinates and two B1 helper records at:

- helper 1 X = primary X − `0x4A00 / 256` = **primary X − 74**;
- helper 2 X = primary X + **74**;
- helper Z values = primary Z.

The state-0 update in `Function_822395D0` moves all three coordinate records and reasserts the ±74 helper offsets when the primary reaches its target.  `Function_820FA770` is the common visual positioner that writes those records to the registered visuals.

Main-game retail rows recovered in dev24 use start `(213,-24)` and target `(213,32)`:

| DAT | absolute frame | primary parameter | helper/timing args vary |
| --- | ---: | ---: | --- |
| `level2_stage6.dat` | 3802 | 15000 | yes |
| `level3_stage5.dat` | 764764 | 5000 | yes |
| `level5_stage4.dat` | 42604 | 1500 | yes |

So `vanity_main_game_arrival` is exactly:

- primary `(213,0,32)`;
- helper 1 `(139,0,32)`;
- helper 2 `(287,0,32)`.

Bonus-stage rows can use different X (for example 120); dev24 does not generalize the 213 formation to every authored encounter.

### State 2 local-Y descent

`Function_822395D0` state 2 decrements `table[2]` by 10 per update from the handler-seeded 1000 toward a floor of 500.  The visual controller `Function_8210CAB8` passes that counter to:

```text
FUN_820fa5b8(counter, 1000, 1)
```

Recovered formula:

```text
ratio = counter / 1000
phase = ratio - 1                  when ratio >= 1
phase = -(1 - ratio)               otherwise
Y = phase * 200
```

For the state-2 range this produces an exact local Y progression:

- tick 0: counter 1000 -> Y 0;
- tick 1: 990 -> Y -2;
- ...
- tick 49: 510 -> Y -98;
- tick 50: 500 -> Y -100.

At counter 510 the mover also executes a separate gameplay event path (`FUN_821d7dc0` / `FUN_821b8f58`); dev24 records the timing but does not assign an unsupported semantic label to that event.

State-2 X/Z continue using live steering velocities, and B1 helpers retain independent activity/last-state coordinates.  Therefore `vanity_state2_primary_descent_local` intentionally exports **one primary model only**, anchored at inspection X/Z=0, with an exact 51-sample local-Y action.  It is not presented as a complete gameplay trajectory.

## Validation boundary

All transforms/timing above come from retail DAT + retail Xbox PPC/model behavior.  No gameplay screenshot measurement is used for these VANITY/TELEPORTER transforms.  The dev24 branch remains unsealed until its normal release gates are run.
