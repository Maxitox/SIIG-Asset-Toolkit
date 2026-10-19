# LINE_INVADER runtime 0x9A procedural path reconstruction — dev24

Status: **retail executable-backed procedural entity; intentionally not a GMX Workbench family**.

## Ownership

Retail `Function_821489F8` switches on `runtime_type + 1`, so runtime `0x9A` selects switch case `0x9B` and constructs `Function_82106378`. Its vtable uses `Function_82105A10` for the opcode-specific configuration block, `Function_82105CF0` for initial path/resource setup, and `Function_821061C8` for the main state update.

The extracted retail enemy model corpus contains `emy_045.gmx`, `emy_046.gmx`, then `emy_049.gmx`; there is no `emy_047.gmx` or `emy_048.gmx`. This is consistent with the 0x9A controller constructing its own render/path resources in `Function_821065D8` instead of owning a missing GMX body. dev24 therefore does **not** invent an `emy_048` assembly.

## DAT layout

`Function_820E7CE0` consumes the common first five arguments. `Function_820E7F68` then passes `record + 0x0E` to vtable +0x5C, and `Function_82105A10` copies exactly `0x2C` bytes: the 22 signed shorts corresponding to args5..26.

The high-confidence 0x9A layout is:

- arg0: spawn condition;
- arg1: common entity parameter;
- arg2: travel speed, raw `/512`;
- args3/4: polyline point 0 X/Z;
- args5..22: up to nine additional X/Z point pairs;
- arg23: total point count, 1..10, including point 0;
- arg24: path/render resource mode;
- arg25: active moving-member count;
- arg26: member-spawn interval in authored 30 Hz ticks. `Function_82105A10` scales it by 60/30 for the controller timeline.

`Function_82105CF0` explicitly starts from the common object position and reads `point_count - 1` coordinate pairs from the copied block. `Function_82105B60` grows active members until arg25 is reached. `Function_82105EE0` advances active members through the path using the common travel speed and the runtime frame multiplier.

## Retail examples

The first Level 5-1 0x9A record (decoded index 405 / frame 752372) is:

`[1,10,2048,-31,62,24,55,79,50,132,47,186,46,241,46,295,47,349,50,403,55,456,62,10,2,50,5]`

It defines a ten-point path:

`(-31,62) -> (24,55) -> (79,50) -> (132,47) -> (186,46) -> (241,46) -> (295,47) -> (349,50) -> (403,55) -> (456,62)`

Travel speed is `2048/512 = 4`; active member count is 50; spawn interval 5 authored ticks becomes 10 normal runtime ticks.

A Level 5-3 record (decoded index 78 / frame 83165) uses only three points:

`(47,270) -> (47,20) -> (548,20)`

with active member count 8 and spawn interval 4 authored ticks -> 8 normal runtime ticks.

## Rendering boundary

`Function_821065D8` creates the LINE_INVADER render/path resources directly, including a `0xC1C1C1` render color and a small separately allocated resource object. The controller feeds path positions through `Function_82155CD0`; it is not represented by a retained `emy_048.gmx`. The toolkit exposes the DAT/path semantics for analysis and Stage tooling, but does not add a fake GMX assembler entry.
