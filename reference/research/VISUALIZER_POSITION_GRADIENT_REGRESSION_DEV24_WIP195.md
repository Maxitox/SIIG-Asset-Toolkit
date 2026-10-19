# Visualizer Position / gradient regression — dev24 WIP195

WIP191 introduced a 1.5× Position multiplier while overhauling the Visualizer Simulator UI. Project-owner testing later exposed a stage-dependent failure: many authored presets rendered as full-screen gradients, while examples such as level4_stage1, level4_stage4 and level5_stage3 retained visible SHAPE feedback.

Retail stage 4-5 provides a decisive constraint. Its authored visualizer is `SEQUENCE_12 -> PARAM_7`; `PARAM_7` uses `WhiteCircle2`, Position Fix 0, free position `(10,+360)`, source scale 1×1 and BG `(0,1,1,0)`. With WIP191's extra 1.5× multiplier, the 128×128 source center becomes `(655,-180)` and its Y extent is `-244..-116`, wholly outside the 1280×720 target. Because the source never intersects the target, it cannot seed structured feedback; only the tiny nonzero BG RGB clear survives and magnifies into the observed gradient.

The project owner's retail Xbox 360 stage 4-5 capture visibly reports `SEQ:12 PARAM:7` while structured teal feedback remains present. Therefore the authored source must intersect the render target. Direct target-pixel mapping places the center at `(650,0)` with Y extent `-64..64`, satisfying the hardware observation and the earlier WIP170/WIP183 `+Y up` cross-check.

WIP195 restores direct target-pixel Position mapping (`x=640+X`, `y=360-Y`). The WIP191 viewport-first menu, stage selector, fullscreen controls and display-only 640×360 smooth resolve remain. The WIP191 validation file is retained as historical evidence, but its inferred 1.5× Position multiplier is superseded by this regression result.

The project-owner video is validation input only and is not bundled.
