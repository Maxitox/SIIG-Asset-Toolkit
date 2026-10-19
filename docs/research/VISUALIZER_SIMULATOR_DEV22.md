# Visualizer simulator — dev22 evidence boundary

## Primary source and recovered data

The **June 10 Visualizer Check Mode footage is the primary visual reference** for dev22. May 9 and May 11 remain useful secondary prototype references, but they no longer define the rendering model.

Recovered game data used by the simulator:

- `visualizerSet.bin.gz.sdat` extracts successfully.
- `ParameterSet.nut` contains **49 parameter presets**.
- `SequenceSet.nut` contains **57 sequences**.
- Every recovered parameter row contains **29 values**, matching the 29 controls exposed by Visualizer Check Mode.
- Exact SHAPE resource order from `visualizer.bin`: `WhiteCircle`, `line`, `3line`, `square`, `triangle`, `WhiteCircle2`, `line2`, `3line2`, `square2`, `triangle2`.
- Retail/console stage DAT files contain real `VL_*` timeline commands. The project corpus has recovered **30 timelines / 243 Visualizer commands**; a simulator build supplied with a compatible full rip decodes the timelines directly instead of baking those corpus totals into the renderer.

The recovered 29-value parameter-row order is:

1. `magnify_scale_x_min`
2. `magnify_scale_x_max`
3. `magnify_scale_y_min`
4. `magnify_scale_y_max`
5. `magnify_a_min`
6. `magnify_a_max`
7. `bg_r`
8. `bg_g`
9. `bg_b`
10. `bg_a`
11. `shape`
12. `position_fix`
13. `position_free_x`
14. `position_free_y`
15. `rotation_base`
16. `add_rotation`
17. `fix_rotation`
18. `scale_x_min`
19. `scale_x_max`
20. `scale_y_min`
21. `scale_y_max`
22. `rgb_r_min`
23. `rgb_r_max`
24. `rgb_g_min`
25. `rgb_g_max`
26. `rgb_b_min`
27. `rgb_b_max`
28. `rgb_a_min`
29. `rgb_a_max`

## June 10 rendering observation

The June 10 footage does **not** look like a procedural collection of independently drawn nested rings. A much stronger match is a feedback/trailing-copy renderer:

1. Start with the previously rendered Visualizer image.
2. Magnify it around the active spawn/feedback center using the X/Y magnify controls.
3. Rotate the prior image by the current rotation increment.
4. Apply the feedback alpha (`Magnify A`).
5. Inject a fresh SHAPE sprite/stamp at the spawn point.
6. Repeat, producing transparent copies that expand outward and eventually fill much of the screen.

This interpretation directly explains the footage where `Magnify Scale X/Y = 1.030`: each earlier copy grows by about three percent per update, creating expanding tunnels/rings. Raising Rotation Base turns the same feedback into spirals and star-like square tunnels without requiring separate hard-coded visual families.

The simulator therefore uses a two-buffer (ping-pong) feedback canvas at a fixed logical update cadence rather than the old static procedural-ring renderer.

## Evidence boundary

The following are treated as **recovered facts** and are represented explicitly rather than guessed:

- the 49/57 preset and sequence counts;
- the 29-value parameter width/order;
- the ten-resource SHAPE order;
- decoded `VL_START`, `VL_END`, `VL_DISP_ON`, `VL_DISP_OFF`, `VL_SEQUENCESET`, `VL_CHANGETIME`, and `VL_VOLUME_SCALE` stage commands;
- the June 10 observation that visible copies grow outward and accumulate translucently.

The following remain **visual/behavioral approximations** until executable/render-path tracing proves them:

- exact pixel content, dimensions, filtering and blend mode of the ten SHAPE sprites;
- exact renderer update/compositing order;
- final code-level semantics and valid range of `Position Fix`;
- final code-level semantics of `Fix Rotation`;
- any mapping from a recovered sequence to behavior not directly decoded from the corresponding recovered data.

`siig_visualizer.py` labels this boundary in the generated HTML. The objective is to make the simulator look and behave like the June 10 Visualizer while keeping recovered timing/data distinct from still-unresolved renderer details.
