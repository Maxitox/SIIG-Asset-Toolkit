# SIIG Asset Toolkit 2.8.0-dev18

**iOS -> console code-lineage checkpoint**

- Branched from sealed dev17; all earlier checkpoints remain frozen.
- Added `siig_lineage.py` and `ios-console-lineage-info`, a source-only executable-lineage reference for mobile/console MAP, DAT timing, generator, and dispatcher evolution.
- Matched iOS `Invinf_LoadMap`, `calcMap`, and `drawMap2` to the recovered console MAP loader/update/renderer family.
- Proved the same 49-tile + X/Y reflection logical cell renderer on iOS and console.
- Proved the iOS 30 Hz timing equations: command deltas scale by `runtime_fps/30`, while map speeds scale by `30/runtime_fps`; related these directly to the independently recovered console frame-multiplier model.
- Corrected the mobile command frontier: primary analyzers end at `0x83`, but `analyzeScript2` handles `0x6E..0x8D`; console expands through `0xCE`.
- Matched iOS `stageGenerateMap` to console's 24-block generator selection/append path and decoded the iOS generated-layer capacity as `6144 = 24*8*32` bytes per layer.
- Added source-only function-lineage, opcode-frontier, generator-lineage, and 18-stage content-delta tables.
- Compared shared normal stages 1-1..3-6: aggregate opcode-sequence similarity is 0.917020, while parameters and some stage structures are substantially retuned; stage 3-6 is a major rewrite.
- Expanded the dependency-free regression suite from 53 to 54 tests.

## Evidence boundary

The iOS executable is from the supplied modified-distribution 4.1.0 research IPA. Findings about executable code and ordinary hashed resources remain usable for lineage, but no claim is made that the package wrapper is an untouched App Store artifact. Exact Xbox addresses are left unresolved where the retained source-only console references do not support them. No game executable, IPA/APK, DAT/MAP payload, or third-party footage is bundled.
