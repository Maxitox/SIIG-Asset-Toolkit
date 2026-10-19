# SIIG Asset Toolkit 2.8.0-dev3 release notes

Dev3 focuses on executable-backed route construction and camera-preset structure.

## Route resampling

- Added `siig_route.py` and the `route-resample` command.
- Reproduces the retail PS3 non-loop fixed-spacing segment builder: linear write-after-step sampling, straight/curve classification, six-state tangent selection, cubic Hermite interpolation, exact initial source-index choice, and final look-ahead behavior.
- Exports JSON, CSV, and OBJ.
- Runtime SCROLL_02 spacing changes and loop wrapping are explicitly not modeled.
- Real-corpus gate at 100-unit analysis spacing: 46 resampleable files, one empty route skipped, 19,471 segments, 155,690 samples, 62 Hermite segments, zero conversion failures.

## Camera preset structure

- Retains the untouched 32 × 30 raw preset table.
- Adds a runtime table after applying all 160 executable initializer writes.
- Adds a 30-word schema identifying two vec3 blocks, three `{2 scalars + vec4}` groups, transition behavior, and consumer addresses.
- Ambiguous gameplay semantics remain unnamed.

## Validation

- Built-in self-test suite expands to 26 tests.
- Source-only release policy remains unchanged.
- Project-owner license selection remains open.
