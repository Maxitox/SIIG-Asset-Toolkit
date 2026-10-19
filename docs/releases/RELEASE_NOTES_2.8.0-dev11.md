# SIIG Asset Toolkit 2.8.0-dev11 release notes

> **Historical correction (dev12):** the May 9/May 11 `0xD9` entry is `bos_015k.gmx`, not `bos_015l.gmx`. This document is retained as the dev11 historical record; use the dev12 research notes for the corrected interpretation.


Dev11 resolves the concrete model object controlled by Ultimate UFO's late route and documents a cross-build ending-sequence change.

- Xbox retail and June 10 construct model-registry ID `0xD8`, `bos_015k.gmx`, in the exact owned field consumed by late phase 11 and the frame-6200 final-disable phase.
- May 9 and May 11 instead use ID `0xD9`, `bos_015l.gmx`, in the corresponding owned field of their earlier 12-phase route.
- The phase-11 action is conservatively recorded as starting child animation/state index 0 when inactive; the final action disables the same owned object.
- Human observation identifying `bos_015k.gmx` as sliding airlock doors is documented as corroboration, not converted into an executable-only fact.
- The known post-`ULTIMATE_UFO` script camera preset-4 records are documented without assigning them to the final rear-camera shot; camera synchronization remains open.
- Self-test coverage adds a cross-build late-owned-model identity check.
