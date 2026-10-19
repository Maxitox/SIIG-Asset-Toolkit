# Ultimate UFO late owned object — dev11

> **Historical correction (dev12):** the May 9/May 11 `0xD9` entry is `bos_015k.gmx`, not `bos_015l.gmx`. This document is retained as the dev11 historical record; use the dev12 research notes for the corrected interpretation.


Dev11 follows the post-HP-zero / late-route object accessed by Ultimate UFO rather than assigning a gameplay label from appearance alone.

## Retail and June 10: model `bos_015k.gmx`

Xbox 360 retail setup `0x8212FC80` loads model-registry entry `0xD8` through `0x820FAAB8`, materializes it, and stores the resulting owned object at UFO `+0x25C` (word `0x97`). The retail registry entry names `0xD8` as `bos_015k.gmx`. `UltimateUfo::MoveMain` equivalent `0x8212EC50` later reads that exact field: phase 11 (trigger 5902) starts child animation/state index 0 when inactive; phase 13 (trigger 6200) disables the object through `0x820F2CF8(object,0)`.

June 10 preserves the same identity with shifted layout. Setup `0x8214AE58` loads registry entry `0xD8` through `0x82111918`, stores the object at `+0x260` (word `0x98`), and MoveMain `0x82149DF8` uses that exact field in phases 11 and 13. The June registry likewise names `0xD8` as `bos_015k.gmx`.

This closes the previously opaque “owned object” identity for the later builds.

## May 9 / May 11 predecessor: model `bos_015l.gmx`

The prototypes use a different late object. May 9 setup code at `0x82142F5C` loads registry entry `0xD9` and stores it at UFO `+0x1DC` (word `0x77`); May 11 code at `0x821440C4` does the same at `+0x1E8` (word `0x7A`). Their old phase-11/final-phase-12 paths consume those corresponding fields.

Thus the late route evolved from prototype model `bos_015l.gmx` (`0xD9`) to retail/June model `bos_015k.gmx` (`0xD8`), at the same time the 12-phase prototype route became the later 13-phase form with a new phase 12 at frame 6030 and the former frame-6200 ending moved to phase 13.

## Airlock interpretation

The project owner's independent model observation identifies `bos_015k.gmx` as the sliding airlock-door component and `bos_015l.gmx` as the giant-laser/weak-spot assembly. That observation makes the retail switch highly consistent with the observed airlock escape sequence. It is deliberately kept separate from the executable fact: the executable proves `bos_015k.gmx` is animated in phase 11 and disabled in phase 13, but contains no recovered semantic string saying “airlock” or “door.”

## Camera boundary

Both known retail DAT encounters author a `3D Camera Change 01 [4,0]` immediately after the `ULTIMATE_UFO` record. This is useful script evidence, but dev11 does not equate that event with an internal PA-route phase or the final rear-view shot until the boss/script clock gate or camera consumer is proven. Retail PA-route setup still has a proven activation of `cam01_op1.gmx`; a proven activation caller for `cam02_op1.gmx` remains unresolved.
