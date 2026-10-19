# SIIG Asset Toolkit 2.8.0-dev4 release notes

Dev4 extends the executable-backed route analysis from fixed-spacing geometry into the retail runtime position/source-index state machine.

## Dynamic route runtime

- Added `RouteRuntimeState` reproducing PS3 retail initialization/advance behavior from `0x0015A338` and `0x00159560`.
- Added non-loop tail termination and modulo loop wrapping.
- Reproduced one generated sample consumed per runtime update.
- Reproduced linear mid-segment spacing changes: remaining samples are discarded and rebuilt from current `FieldPos` to the same endpoint.
- Active Hermite segments deliberately do not rebuild on a spacing change.
- Added signed SCROLL_02 Y → per-update spacing conversion from `0x0014E408`, including PPC truncation toward zero and signed-16 narrowing.

## DAT coupling

New `route-playback` accepts one stage3d route table and one DAT script. It maps authored DAT frames to runtime updates using an explicit frame multiplier and applies SCROLL_02 events before each route update.

The tool does not guess route↔DAT filename pairing or route-object creation time. `--start-frame` is explicit; the most recent SCROLL_02 at or before that frame initializes spacing. `--loop`, `--end-frame`, and `--max-updates` make the remaining runtime assumptions visible and bounded.

## Validation

- 28/28 dependency-free self-tests pass.
- All 46 resampleable retail stage3d route tables pass dynamic non-loop and loop smoke stepping; `Xmap4_1.bin` is route-empty and remains skipped.
- Explicit filename-correspondence validation candidates:
  - `Xmap2_1.bin + level2_stage1.dat`: 100,000 runtime updates, route finished.
  - `Xmap3_1.bin + level3_stage1.dat`: 265,020 updates, seven applied SCROLL_02 events and seven linear spacing rebuilds, route finished.

These examples validate the route/DAT coupling code but are not presented as a solved global pairing table.

## Remaining boundaries

- Authoritative route-object activation and complete route↔DAT pairing remain unresolved.
- Orientation, field-model animation, camera matrices/presets, and route position are not yet combined into one scene playback model.
- Several camera-preset semantics remain intentionally unnamed.
- RSX/Xenos shader instruction-level analysis remains future work.
- Original toolkit code still requires an owner-selected publication license.
