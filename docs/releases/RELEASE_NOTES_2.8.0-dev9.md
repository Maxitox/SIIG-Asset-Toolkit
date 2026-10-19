# SIIG Asset Toolkit 2.8.0-dev9 release notes

Dev9 is an executable-backed boss-route timeline checkpoint built from the frozen 2.8.0-dev8 source tree.

## New

- Added literal Water Strider 17-segment PA-route course table and a helper that reproduces the retail 1441-frame wrap.
- Added Ultimate UFO retail/June/PS3 13-phase route table plus May 9/May 11 12-phase prototype table.
- Cross-mapped stripped retail/PS3 boss route functions to prototype debug-named `UltimateUfo::MoveMain` and `WaterStrider::updateAct`.
- Documented the executable phase-9 Ultimate UFO hold/resume gate and the finite-vs-looping route distinction.
- Added three machine-readable tables and exposed the timelines through `pa-route-info`'s reference snapshot.
- Kept camera-angle semantics conservative: no vertical/escape/rear-shot label is promoted without a recovered camera consumer.

## Validation

- Built-in suite expanded from 35 to **36 tests**.
- Retail Xbox 360 and PS3 boss tables were independently matched byte-for-byte against the June 10 tables from the retained Ghidra listing corpus.
- May 9/May 11 timing differences are preserved and regression-tested.
- Existing dev8 real-DAT gate (76 retail PS3 DAT files, zero parse failures) remains inherited.

## Deliberate limits

- The literal boss-to-special-stage reload-parameter callsite remains unresolved.
- `cam02_op1.gmx` still lacks a proven retail activation caller.
- Exact semantic names for several phase/segment flag bytes remain unresolved.
