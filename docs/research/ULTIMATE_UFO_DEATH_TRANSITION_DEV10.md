# Ultimate UFO death / late-transition trace — dev10

The user gameplay observation that the final sequence starts immediately after Ultimate UFO reaches zero HP was used only as a search anchor. The statements integrated here come from the executables.

## HP-zero dispatch

Xbox retail `0x820FBD30` is the common tracked-health damage path. When subtraction leaves a health slot below 1, it dispatches the object's vtable `+0x3C(part, state=1)` and then `+0x44(part)`. Ultimate UFO supplies its own part-state handler at retail `0x8212DCB0`.

For part index 1, that override stores the state in byte `+0x1EE` and performs UFO-specific coupled part handling. This gives an instruction-level bridge from zero health into the UFO destruction state machine.

## Prototype symbol confirmation

The May prototypes preserve the debug name `UltimateUfo::Vanish`:

- May 9: `0x821410A8`
- May 11: `0x821423B8`

The May 11 body treats part 1 specially, validates/locates the owned part, emits the vanish/destruction effect at that part's position, then calls the part-state handler. This identifies the semantic role of the prototype vtable slot without forcing the same name onto later retail code where the implementation evolved.

The script command `AnalyzeDelLv5Boss` also survives across the prototype/PS3 evidence and selects entity type IDs `0xA6..0xAB`, which includes Water Strider `0xA6` and Ultimate UFO `0xA8`, before invoking the per-part vtable `+0x48` operation.

## Retail late phases

Ultimate UFO retail `MoveMain` (`0x8212EC50`) proves these late actions:

- phase 9, trigger 5897: route advancement can halt while an owned event/object remains incomplete, then resumes;
- phase 11, trigger 5902: an owned object is acted on and effect `0xA9` is emitted;
- phase 12, trigger 6030: part-1 state is propagated to part 0; when `+0x1EE` is nonzero the part-0 destruction operation is called and flag `+0x1EC` enables recurring randomized explosion effects;
- phase 13, trigger 6200: the owned object referenced by the UFO is disabled.

These establish a post-destruction late-route sequence. They do **not** by themselves identify the player's observed “airlock escape” or “rear camera” with a particular camera resource or camera preset. No such human label is emitted until a specific camera consumer/callsite is recovered.
