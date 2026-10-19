# Five-boss primary controller audit — dev22

> **Dev24 follow-up:** this file preserves the dev22 controller-audit boundary. Later retail DAT/controller evidence promotes OCTOPUS, WATER STRIDER and NO_NAME to exact **gameplay-pose reconstruction** while keeping their multipart ownership gates intact; LADYBUG is now a deep runtime reconstruction. THE MOON remains native-inspection-only. Dev24 also corrects the old THE MOON “scale” interpretation: the 0.4/0.9/0..1 values are fourth-component/material-alpha writes, while slot 0 separately receives 36-degree-step Z rotation. See `reference/research/CONSERVATIVE_BOSS_GAMEPLAY_POSES_DEV24.md` and `reference/research/THE_MOON_VISUAL_CONTROLLER_DEV24.md`.


Dev22 revisits the five conservative console boss families directly from the retained **Xbox 360 retail Ghidra export**, with PS3 retail used as a parity check where noted. The result is deliberately not five new static assemblies. Instead, each family now has enough primary-controller evidence to explain **why its canonical export remains native/timed** and what evidence would be required before promoting it.

This supersedes the preliminary dev21 five-boss audit where the newer trace is more specific. The corrected visual-controller factory rule remains `switch(runtime_type + 1)`.

## THE MOON (`0x46` / `bos_001.gmx`)

Factory case `0x47` constructs `Function_8212B638`. Setup/update are `Function_8212B6F8` and `Function_8212B760`.

The update operates on THE MOON's own visual-slot/material state. **Dev24 correction:** the values previously described here as dynamic scale are not scale writes. `Function_8212B760` preserves RGB and changes the fourth/material-alpha component of the `collada_edge1`, `collada_face1`, and `collada_face2` vectors through `Function_8214D9B0`; slot 0 separately receives periodic 36-degree-step Z rotation. Nonzero slots use alpha 0.4. The traced visual-controller path contains **no auxiliary GMX registry lookup**.

**Current interpretation:** the native animated `bos_001.gmx` remains the canonical representation. The controller state can now be sampled exactly, but a material-animated gameplay export still requires mapping controller visual slots/materials to exact exported GMX render nodes/materials; there is no evidence for inventing a separate outer world transform or multipart static scene.

## LADYBUG (`0x49` / `bos_004.gmx`)

Factory case `0x4A` constructs `Function_8211EA18`. `Function_8211EB88` resolves runtime `0xB6` (`bos_004a.gmx`) and creates exactly four helper objects.

The important dev22 correction comes from the helper update path. `Function_8211E9D0` dispatches non-root helper updates through `Function_8211E8A8`; that routine derives the helper transforms from **live field-coordinate arrays**, rather than rigidly multiplying one of the `bos_004.gmx` `lt_001..lt_004` locator matrices. `Function_8211E780` also controls helper visibility by runtime state.

**Dev22 interpretation:** the four B6 models are positively owned by LADYBUG, but they are **controller-owned dynamic field-space helpers**, not proven static body attachments. They stay out of the canonical static body assembly until a relevant field/controller state can be replayed or captured.

## OCTOPUS (`0xA3` / `bos_010.gmx`)

Factory case `0xA4` constructs `Function_82123E18`. `Function_82121228` loads runtime `0xA3` / `bos_010.gmx`, while `Function_821216F0` explicitly resolves native locator `lt_000`. The large state machine is driven by `Function_82124170`.

A scan of the local setup/move state-table helpers assigned by this controller found **no second entity-registry model lookup**. A nearby function containing an A2/C2/C3 model-ID table is not in the OCTOPUS vtable/state table and is therefore not attributed to OCTOPUS merely because it is adjacent in the executable.

**Dev22 interpretation:** no auxiliary GMX membership is promoted. The native articulated `bos_010.gmx` and its animation/state inspection remain the evidence-backed representation unless a distinct externally owned model path is later proven.

## WATER STRIDER (`0xA6` / `bos_014.gmx`)

Factory case `0xA7` constructs `Function_821368E8`. `Function_82136810` owns the route/controller clock and wraps after `0x5A0`, confirming the recovered **1441-frame `0..1440` loop** belongs to WATER STRIDER's controller.

`Function_821362C0` binds exactly seven native locators, in this order:

1. `lt_001`
2. `lt_002`
3. `lt_003`
4. `lzr_001`
5. `lzr_002`
6. `lzr_003`
7. `lzr_004`

PS3 retail routine `0x001E0300` independently repeats the same seven-locator binding pattern, providing cross-platform parity evidence.

**Dev22 interpretation:** WATER STRIDER has a **timed route/locator reconstruction**, not one canonical static route transform. A deeper export should therefore be a user-selected route/controller-time snapshot rather than a guessed static assembly.

## NAMELESS / internal `NO_NAME` (`0xAB` / `bos_018a.gmx`)

Factory case `0xAC` constructs `Function_82120B50`. Setup `Function_82120CA0` directly creates runtime `0xAB` / `bos_018a.gmx`, initializes large helper pools, and `Function_821208F8` advances the local state machine through controller helpers including `Function_8211F370` and `Function_8211FBD8`.

The controller-local path contains **no ownership lookup for retail `0xE5` / `bos_018.gmx`**. That model remains separately registered; its existence in the registry is not evidence that it should be stacked into NAMELESS. Earlier prototype research likewise showed May-only `bos_018b/c` assets disappearing by June 10, without surviving gameplay/debug wiring that would justify adding them to the retail scene.

**Dev22 interpretation:** canonical NAMELESS remains `bos_018a.gmx`. `bos_018.gmx` or discarded May assets require a direct ownership/spawn/attachment path before they can be added.

## Machine-readable status

`boss-matrix` now exposes four dev22 fields for these five families:

- `controller_research_grade`
- `controller_research_finding`
- `controller_promotion_gate`
- `controller_evidence_functions`

The top-level report also records `native_controller_traced_families = 5`. This means **native inspection only is no longer synonymous with unresearched**: all five controller paths are traced far enough to preserve a positive evidence boundary, while the toolkit still refuses to fabricate a static gameplay assembly.

## Promotion rule

A family should only move beyond this boundary when the missing gameplay representation is backed by a direct native/executable path for the relevant **membership, transform/attachment, and state/time/visibility behavior**. Screenshots, adjacency in the executable, registry presence by itself, or visually plausible locator matching are not sufficient.
