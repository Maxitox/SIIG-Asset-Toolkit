# SIIG Asset Toolkit 2.8.0-dev13 release notes

Dev13 turns the Ultimate UFO late-camera research into an executable-backed reconstruction command and refines the ending/transition lifecycle.

- Added `field-camera` to reconstruct procedural camera eye/target directly from `fld014.gmx` / `fld015.gmx` for an explicit camera preset and frame range.
- Added explicit GMX serialized column-vector affine → SIIG runtime row-vector affine conversion, modeled as a 4×4 transpose and regression-tested.
- Validated every real normal-5-3 late `fld015` sample from Mframe 5897..6300: 404/404 frames are rear-follow for preset 4.
- Measured late rear distance at 59.859..72.111 route units (mean 63.665).
- Stress-tested preset-4 dynamic horizontal response at extreme constant runtime X values; 404/404 frames remain rear-follow.
- Decoded retail camera-controller `+0x11C` as the timed-preset-transition acceptance gate and proved Ultimate UFO's normal part-0/state-0 reset clears it on retail Xbox and PS3.
- Recovered the May 9/May 11 phase-12 Mframe-6200 direct `UltimateUfo::Vanish(part 0)` call and documented the later June/retail 6030/6200 ending split.
- Confirmed the retail `DEL_LV5_BOSS` opcode is not authored in either 5-3 or Bonus 5-6, so it is not used as the fight-ending trigger.
- Added machine-readable camera-transition, final-Vanish, and GMX/runtime matrix-convention reference tables.
- Expanded dependency-free self-tests from 43 to 45 checks.
