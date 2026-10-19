# Ultimate UFO final reset and camera-gate audit — dev14

Dev14 narrows the June/retail ending question by separating three events that are easy to conflate: destruction state, visible owned-object shutdown, and the part-0/state-0 reset that clears the retail camera transition gate.

## Result

Retail Xbox does **not** clear camera controller `+0x11C` at Mframe 6030 or 6200.

- At Mframe 6030, `Ultimate UFO MoveMain` (`0x8212EC50`) invokes vtable `+0x3C(part 0, state +0x1EE)`. In an ordinary defeated-boss path `+0x1EE` is state 1, not state 0. It then invokes part destruction through vtable `+0x44` and enables the recurring explosion flag.
- At Mframe 6200, the same function only calls `Function_820F2CF8` on the owned `bos_015k` object with enable state 0.
- The tail of `MoveMain` updates owned objects/camera behavior, emits recurring explosions when enabled, advances Mframe, and writes the route frame. It has no later part-0 `+0x48` reset.

The proven Xbox clear is the byte store at `0x8212DD20` inside `0x8212DCB0`, and it is conditional on **part 0, state 0**, outside the Extra/Bonus 5-6 exception. The generic vtable `+0x48` implementation at `0x820FBEE8` is the bridge: it calls vtable `+0x3C(part, state 0)`. Therefore the camera gate is cleared only when a later caller actually invokes part-0 `+0x48`; it is not cleared merely because the visible model vanishes or the entity is destroyed.

The PS3 equivalents remain `0x001D3380` for the UFO part-state handler and `0x0015B524` for the preset setter.

## Gate lifecycle

Retail Xbox camera-controller construction at `0x820ECFD8` initializes `+0x11C` to 1. Accepted preset changes in `0x820ECDF0` also leave the gate at 1 (`0x820ECF04`). Retail PS3 camera-controller construction at `0x0015C6C8` and accepted preset changes at `0x0015B524` have the same set-to-1 behavior.

This means a later camera-controller reconstruction is not evidence that the UFO clear ran: reconstruction initializes the new controller to 1, while the UFO reset writes 0 to the existing controller.

## Caller exclusions

The retail caller audit excludes the following as the ordinary Normal 5-3 final reset:

- `DEL_ZAKO` dispatches group 0, entity types `0x96..0x9E`, and therefore excludes Ultimate UFO type `0xA8`.
- `level5_stage3.dat` has no authored `DEL_ALL_ENEMY` or `DEL_LV5_BOSS` after the Ultimate UFO spawn.
- Manager removal `0x82148748 -> 0x8214A368` invokes the entity destructor and clears its manager slot; it does not first dispatch the entity's vtable `+0x48`.
- Generic lifetime method `0x820FB280` can dispatch `+0x48` for every part, but its Ultimate UFO threshold is 25,200 timer units. With the retail default timer scale (`0x820E0200` / `0x820E0248` return two units per main update), that is approximately 12,600 updates and is a watchdog rather than the normal route-end event.

The complete decompiler export contains other vtable `+0x48` calls, but they belong to specific entity implementations acting on their own parts. No post-6200 Ultimate UFO self-call was found.

## Final static closure

The ordinary Normal 5-3 ending has **no proven post-6200 `+0x48` caller** in the retained static evidence. This is stronger and more precise than assuming that a later reset must exist: the retail part-0/state-0 handler proves what *would* happen if that reset is dispatched, but it does not prove that Normal 5-3 actually dispatches it during its ordinary ending.

Static evidence therefore permits two implementation outcomes:

1. a higher-level transition invokes the generic `+0x48` reset before teardown, which would clear `+0x11C` through `0x8212DD20`; or
2. stage/entity teardown reaches the destructor-only manager removal without `+0x48`; in that case the old controller gate need not be cleared because later camera-controller construction initializes a new controller to 1.

No available static caller, Normal 5-3 DAT command, phase-table action, or normal-route lifetime expiry proves outcome 1. Conversely, the manager-removal routine proves that outcome 2 is mechanically possible but does not by itself prove that it is the exact ordinary 5-3 call path. The correct dev14 conclusion is therefore **static closure with a runtime-only branch unresolved**, not “a hidden reset definitely happens later.”

## June 10 footage boundary

Project-owner June 10 Normal-mode footage supplies a precise observational boundary. In `SIIG June 10 Normal mode-01.15.00.000-01.30.00.000-seg6.mp4`, the `ULTIMATE_UFO HP = 0 / 10000` debug registration remains visible through approximately 427.367 seconds and is absent by approximately 427.400 seconds, as the white-out leading into the Stage 5-3 results transition begins. The general development/debug overlay remains present.

This strongly associates the *visible entity-registration removal* with the higher-level stage-completion transition rather than with Mframe 6030 or the Mframe-6200 `bos_015k` shutdown. It is still gameplay observation, not executable proof of either `+0x48` or destructor dispatch. The frame boundary is recorded in `reference/tables/ULTIMATE_UFO_VISIBLE_REMOVAL_DEV14.csv`.

A runtime watchpoint on the retail camera-controller `+0x11C` byte, or a recovered higher-level transition callsite from a complete executable trace, is the remaining way to distinguish the two implementation outcomes. Until then, toolkit semantics must not assign an exact normal-ending camera-gate clear time or claim that the clear definitely executes.

## Evidence boundary

All addresses, conditions, opcode exclusions, timer arithmetic, and manager behavior above are executable or retail-DAT evidence. User prototype footage remains gameplay observation and is not used to promote the unresolved caller to executable fact. Retail videos remain third-party gameplay observation.
