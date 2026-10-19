# ENVY runtime 0x98 reconstruction — dev24

Status: **retail executable-backed runtime ownership and chain geometry**.

## Corrected ownership

Retail `Function_821489F8` switches on `runtime_type + 1`. Runtime `0x98` therefore selects switch case `0x99`, which constructs **`Function_82102898`** for `emy_045.gmx`. The adjacent mapping is intentionally regression-guarded: runtime `0x97 -> Function_820FF9A8`, `0x98 -> Function_82102898`, `0x99 -> Function_82103C58`, `0x9A -> Function_82106378`, and `0x9B -> Function_8210CFE8`.

An early dev24 WIP briefly attributed the neighboring `Function_820FF9A8` lattice controller to ENVY. Raw PPC disproved that interpretation before release; the lattice forms and semantics are not part of the current ENVY implementation.

## Retail controller

`Function_82102898` owns the ENVY visual/controller family. Its configuration path is `Function_82101960`; growth uses `Function_82102480 -> Function_82102058`; member facing uses `FUN_82101810`; the later transition uses `Function_82102510 -> Function_82101E20`.

`Function_82102058` places active members along one of four cardinal vectors. Member ordinal `i` is displaced `i * 10` units along the configured cardinal direction, with an alternating perpendicular offset of magnitude 2. `FUN_82101810` applies alternating −30°/+30° yaw around the corresponding cardinal-facing base.

The normalized member transform is therefore executable-backed, while the chain's absolute base position remains encounter-driven and is deliberately normalized away in Workbench assembly forms.

## DAT semantics

For opcode `0x98`, dev24 exposes the high-confidence fields:

1. spawn condition;
2. common entity parameter;
3. travel speed, raw `/512`;
4. start X;
5. start Z;
6. target X;
7. target Z;
8. member count;
9. growth interval in authored 30 Hz ticks;
10. later/fly-away tracking duration in authored 30 Hz ticks;
11. cardinal heading index;
12. later/fly-away motion, fixed 8.8.

`Function_82101960` scales the two authored-duration fields from 30 Hz to the 60 Hz controller timeline. Count and heading are encounter parameters rather than model constants.

## Exact Level 4-2 form

`level4_stage2.dat`, command 56 / frame 5057 contains:

`[0, 10, 256, 20, -10, 20, 361, 20, 5, 0, 3, 1280]`

Therefore the exact normalized growth-complete inspection form has **20 members** and heading index **3**. For this heading the cardinal direction is +X and the alternating perpendicular displacement is along Z. Travel speed is `256/512 = 0.5` native units/update; growth interval 5 authored ticks becomes 10 normal 60 Hz controller ticks.

Catalog `envy_retail_level4_2_growth_complete` exports this exact relative formation. Catalog `envy_zigzag_preview_06` uses the same proven geometry with count 6 / heading 0 solely as a compact inspection convenience and is not a claimed retail encounter.

## Evidence boundary

The relative chain geometry, DAT count/heading fields, speed conversion, growth timing conversion, and controller ownership are executable-backed. The moving absolute chain base and later live fly-away behavior are retained as runtime metadata rather than collapsed into an invented fixed pose.
