# SIIG Asset Toolkit 2.8.0-dev12 release notes

Dev12 turns the May 9 Ultimate UFO debug HUD into executable-backed phase semantics, separates normal 5-3 from Bonus 5-6, corrects dev11's prototype registry interpretation, and closes the Mframe-to-field/camera chain far enough to classify the normal late route as rear-follow geometry.

- Corrected May 9/May 11 runtime ID `0xD9` to `bos_015k.gmx`; June/retail/PS3 use `0xD8` for the same model. Dev11's May=`bos_015l` conclusion is superseded.
- Recovered May 9 `Mframe`, `Sframe`, `state`, `L2:SKIP`, and Umb/Tow/Fan/Ring debug-HUD mechanics.
- Named all eight Ultimate UFO phase bytes as Umb/Tow/Fan/Ring `col`/`dis` pairs while retaining the raw flags in the Python API for compatibility.
- Proved `L2:SKIP` input mask `0x400` sets Sframe to zero and that Mframe advances only when its advance flag is enabled and Sframe has expired.
- Added direct Mframe -> `fld015.gmx` route-frame setter evidence for May 9, May 11, June 10, Xbox retail, and PS3 retail.
- Added explicit normal 5-3 and DLC Bonus 5-6 behavior profiles.
- Proved the Bonus 5-6 fast-destruction branch independently in retail Xbox and PS3: core destruction is immediately mirrored to the main body and pending late destruction state is cleared.
- Reconstructed the PA camera lifecycle: temporary `cam01_op1.gmx` animated eye/target, then automatic procedural-camera fallback transformed by the active `fld015` orientation/FieldPos.
- Rejected the earlier preset-4-as-HP-zero-switch hypothesis.
- Evaluated real late `fld015` matrices with preset 4 and classified the normal 5-3 late camera as rear-follow geometry: local `(0,40,60)` -> late world-relative `(0,-60,+40)`.
- Expanded self-tests from 39 to 43 checks.
- Audited all five direct retail-PS3 callers of camera preset setter `0x0015B524`; none belongs to Ultimate UFO, while the sole boss-specific direct caller cross-maps to Vertebrate.
