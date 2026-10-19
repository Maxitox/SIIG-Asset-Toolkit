# WRATH runtime 0x9B reconstruction — dev24

Status: **retail executable-backed body approach and state-1 behavior metadata**.

## Ownership and the adjacent-case trap

`Function_821489F8` switches on `runtime_type + 1`. Consequently runtime `0x9B` / `emy_049.gmx` selects switch case `0x9C` and constructs **`Function_8210CFE8`**. Switch case `0x9B` / `Function_82106378` belongs to neighboring runtime `0x9A`; dev24 has a regression specifically preventing that off-by-one attribution.

WRATH configuration uses `Function_8210CF78`, initial state setup uses `Function_8210D0C0`, and the main update is `Function_8210D468`. The four-point attack is `Function_8210D1F8`; the separate two-locator attack is `Function_8210D340`.

## Level 4-4 DAT record

Retail `level4_stage4.dat`, decoded command index 406 / frame 654354 carries opcode decimal 155 (`0x9B`) with arguments:

`[0, 3500, 2560, 213, 80, 0, 30]`

Decoded fields are spawn condition, common entity parameter, travel speed raw `/512`, anchor X, anchor Z, four-point-attack suppress flag, and attack interval in authored 30 Hz ticks.

The anchor is `(213, 0, 80)`. `Function_8210D0C0` starts the visible body at `(anchorX, anchorY - 500, anchorZ + 200)`, giving **`(213, -500, 280)`**. Raw speed `2560/512 = 5`; with the normal runtime frame multiplier 1 and 60/30 conversion, state 0 advances 10 native units per update along the anchor vector.

## Exact normal-timing approach

The rendered state-0 sequence contains **55 positions**: initial spawn plus 54 updates. The penultimate position is approximately `(213, -7.907353985, 83.162941594)`. The following update crosses the anchor-Y plane, and retail snaps the body exactly to `(213, 0, 80)` rather than rendering an overshoot.

Catalog `wrath_retail_level4_4_approach` exports this as a 55-sample translation action at 60 Hz. The action is controller-derived; `emy_049.gmx` itself contributes no native action to this retail export.

## State 1 and attacks

After arrival, `Function_8210D468` keeps Y at the anchor. X follows live player X with a normal-timing clamp of **±0.15 native units/update**. Z oscillates at **±0.3 units/update**, reversing each 60-runtime-tick band. Because player X is live, dev24 retains this behavior as metadata rather than baking a fake deterministic state-1 path.

DAT arg6=30 is scaled from authored 30 Hz to **60 normal runtime ticks** for the four-point attack. Arg5=0 permits that path; nonzero suppresses it. A separate fixed 240-runtime-tick path calls `Function_8210D340`, which uses the WRATH object's `lt_005` and `lt_006` locator positions to feed linked auxiliary controllers. Those linked allocations are now classified directly from their factories as transient attack/effect pools, not permanent WRATH GMX parts. Type `0x39` allocates 40 slots through `Function_8213CBC0`; `Function_8210D1F8` takes free slots through `Function_820FD738` and writes lifetime 100. Type `0x38` allocates two slots through `Function_8213D708`; `Function_8210D340` initializes them with `Function_8213D270`, feeds the `lt_005`/`lt_006` transforms through `FUN_8213d230`, and sets their active bytes with `FUN_8213d258`. `Function_8213D890` updates procedural four-corner geometry via `FUN_8246cd20`, with no auxiliary GMX ownership lookup in this attack path.

## Evidence boundary

The visible body ownership, Level 4-4 spawn, 55-sample approach, exact anchor snap, state-1 rates, timer scaling, locator identities, and transient auxiliary-pool classification are executable-backed. State-1 player-dependent X motion is intentionally not synthesized; procedural attack effects remain metadata rather than being misrepresented as permanent GMX body members.
