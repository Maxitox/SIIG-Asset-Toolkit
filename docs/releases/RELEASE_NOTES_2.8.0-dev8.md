# SIIG Asset Toolkit 2.8.0-dev8 release notes

Dev8 is a cross-build PA-route activation research checkpoint built on validated dev7 animation timing.

## New

- Added `pa-route-info`, an executable-backed inspector for the special `Route::SetPaRoute` system.
- Added five-build activation-gate comparison across PS3 retail, Xbox 360 retail, June 10, May 11, and May 9.
- Added machine-readable PA-route function, gate, camera-selection, and boss/field correlation tables.
- Recovered prototype debug name `Route::SetPaRoute` and mapped it to stripped retail/PS3 equivalents.
- Proved the known retail stage setup selects camera index 0 (`cam01_op1.gmx`); index 1 (`cam02_op1.gmx`) is accepted by `SetPaRoute` but lacks a proven retail activation callsite.
- Documented the retail/June gate `stage_category == 0 && state(+0x218)==4 && state(+0x21C)==1`, the earlier May 11 state-only gate, and the absence of the corresponding May 9 activation branch.
- Added conservative boss/field correlations: Water Strider <-> `fld014` / Bmap13 / parameter 0x0C; Ultimate UFO <-> `fld015` / Bmap15 / parameter 0x0E.
- `pa-route-info DAT` scans real DAT command streams for `WATER_STRIDER` / `ULTIMATE_UFO` while explicitly warning that boss opcode presence alone is not an activation trigger.

## Validation

- Dependency-free suite expanded from 34 to **35 tests**.
- Real retail PS3 script archive: 76 DAT files scanned; six Water Strider / Ultimate UFO occurrences identified with zero parse failures.
- Existing dev7 package/animation/route/camera validation remains inherited and unchanged.

## Deliberate limits

- Dev8 does not automatically switch procedural stage playback into PA-route mode yet.
- The final boss-stage transition/write is still unresolved.
- No proven retail callsite selecting cam02 has been found.
- Boss-to-field mapping is labeled strong correlation where the complete single direct call chain has not yet been recovered.
