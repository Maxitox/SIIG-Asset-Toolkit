# Runtime 0x9D / emy_051 reconstruction — dev24

Status: development research for unsealed `2.10.0-dev24`. **WIP179 follow-up:** the project-owner model catalog now resolves the player-facing identity as **LUST** (`emy_051`), while the executable-internal script/debug token remains unproven. This note keeps `runtime 0x9D / emy_051` in executable-facing descriptions so provenance stays explicit; it no longer treats the gameplay identity itself as unknown.

## Ownership

The retail entity registry maps runtime `0x9D` to `emy_051.gmx`. Retail `Function_821489F8` dispatches enemy controllers with `runtime_type + 1`, so runtime `0x9D` selects switch case `0x9E`, which allocates a `0x20C`-byte controller and constructs **`Function_82106F78`**.

This is separate from GLUTTONY: runtime `0x9C` selects case `0x9D` / `Function_82103878`.

## DAT handler and the important negative result

The opcode-`0x9D` callback is `Function_820E8268`. It calls the common enemy handler `Function_820E7F68`, then allocates a type-`0x3E` auxiliary pool with count `0x28` through `Function_820E7DC0`.

The `Function_82106F78` vtable at `0x82008910` uses the common handler entries and, critically, its +0x5C DAT-tail slot is `0x824DBC78` (no-op). Therefore there is **no runtime-0x9D-specific copied parameter tail** after the common five arguments.

This agrees with the retail Stage Explorer corpus: all **80** available runtime-`0x9D` commands contain exactly five signed arguments.

## High-confidence five-argument schema

`Function_820E7CE0`, reached through the common handler, gives the exact storage semantics:

| Arg | Semantic | Evidence |
|---:|---|---|
| 0 | `spawn_condition` | common conditional-spawn gate |
| 1 | `body_hp` | root element 0 of both +0xF0 baseline/max and +0x100 current HP arrays |
| 2 | `travel_speed_raw512` | stored as `arg2 / 512.0` at common field +0x1AC |
| 3 | `position_x` | common X at +0x1A0 |
| 4 | `position_z` | common Z at +0x1A8 |

The current evidence proves the scaling/storage of arg2 and supports the established common movement-speed interpretation. dev24 does not claim a more specific state-dependent role for it until the `Function_82106F78` movement state machine is traced further.

## Retail corpus profile

The 80 current retail records are distributed as follows:

- `level4_stage6.dat`: 21 records
- `level5_stage2.dat`: 22 records
- `extra1_stage7.dat`: 1 record
- `extra3_stage2.dat`: 36 records

All use `body_hp = 300`. Raw speed is either `256` (0.5 native) or `512` (1.0 native). Z is `-20` in the normal groups and `-10` in the single Extra 1-7 record. Authored X spans many positions (36 distinct values in the recovered retail corpus), consistent with a positioned encounter family rather than a hidden extra parameter block.

Representative records include:

- `[0, 300, 256, 213, -20]`
- `[0, 300, 512, 52, -20]`
- `[0, 300, 256, 213, -10]`
- `[0, 300, 512, 416, -20]`

## Assembly boundary

`emy_051.gmx` is now cataloged as **LUST** from project-owner visual/model identification. The type-`0x3E` auxiliary pool is still unconfigured in the current retail model registry, so dev24 does **not** invent multipart ownership or attach unproven helper models merely because the friendly identity is known. The controller/DAT semantics remain independently executable-backed.

A dedicated regression protects the five-field mapping and representative retail values. Further work may trace the `Function_82106F78` state machine if it produces useful behavior/visualization evidence; it is no longer needed merely to obtain a player-facing name.
