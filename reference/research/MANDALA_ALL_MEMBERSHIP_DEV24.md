# MANDALA complete-membership inspection — dev24

Status: executable-backed Workbench fidelity correction for unsealed `2.10.0-dev24`.

## What changed

MANDALA allocates 72 visual/runtime members: slots 0..19 are B7 / `bos_005a.gmx`, slots 20..27 are the B8-BB quartet repeated twice, slots 28..59 are BC / `bos_005f.gmx`, and slots 60..71 are structural 4A / `bos_005.gmx` members.

The older `mandala_initial_combat` catalog intentionally showed only the 40 members active/reference-visible at the state-7 activation boundary. That made a generic “fully assembled” inspection look as if the 32 small center circles were missing.

Retail Xbox `Function_82240190` resolves the distinction. Its geometry update runs whenever controller state is 7, 8, or 9 and writes the four eight-member BC rings at position-array offsets `0x70`, `0x90`, `0xB0`, and `0xD0`. The later state-7 -> state-8 branch separately copies slots 28..59 from the authored/config array into the active/damage-state array. Therefore the BC geometry exists and is recoverable before its gameplay activation gate.

## New Workbench preset

`mandala_all_members_phase0` contains all **72 allocated members** in exact relative geometry with the shared phase accumulator normalized to zero:

- 20 × B7 / `bos_005a.gmx`
- 2 × each B8/B9/BA/BB / `bos_005b`..`bos_005e.gmx`
- 32 × BC / `bos_005f.gmx`, arranged as four radius-20 eight-member rings whose centers lie on the four radius-20 cardinal points
- 12 × structural 4A / `bos_005.gmx`

This preset is an **inspection composite**, not a claim that all 72 members are simultaneously damage-active. Each BC instance records `activation_state = 8` and `gameplay_active_in_state7 = false`.

The complete preset is now MANDALA's canonical Workbench assembly so a normal full-model inspection includes the center circles. The older state-7 and state-8 gameplay/reference presets remain available separately.
