# Stage Explorer proof-of-concept boundary — dev24 WIP172

## Trigger

Project-owner hands-on testing of the generated Stage Explorer showed three user-visible problems that matter more than the amount of decoded data already present:

1. atlas/sprite presentation can still look visibly jittery or otherwise unlike the game;
2. the motion control does not reproduce the complete stage sequence;
3. the combined browser UI feels janky enough that describing it as an accurate map viewer overstates its maturity.

WIP172 therefore changes the product claim rather than hiding those limitations behind additional fidelity language.

## What remains evidence-backed

The following data/decoding work remains useful and is not rolled back:

- June 10 runtime script/map slot pairing by table index;
- MAP layer dimensions and exact cell bytes;
- cell semantics: 0 empty, lower six bits one-based tile ID 1..49, 0x40 X reflection, 0x80 Y reflection;
- verified fence atlas resource mapping and 7x7 / 144-pixel-pitch / 96x96 source-rectangle layout;
- decoded DAT command records and semantic fields where executable evidence exists;
- SCROLL_01/02/03 layer velocity events and their recovered logical authoring timebase;
- level 4/5 route and 0x118 placement records;
- GMX root AABBs and recovered `S * Rz(z) * Rx(x) * Ry(y) * T` placement transform.

These are research/inspection capabilities. They do not by themselves prove that the browser reproduces the native stage renderer.

## Reclassification

Stage Explorer dataset v8 now reports:

- `maturity = proof_of_concept`
- `fidelity = research_inspector_not_gameplay_renderer`

The generated HTML repeats that boundary visibly. Exact static MAP-layer inspection and decoded DAT records are presented before the experimental motion/3D panels.

## Motion-preview boundary

The old wording "runtime playback" was too strong for the browser control. The panel integrates recovered SCROLL_01/02/03 X/Y velocities against a chosen frame. It does not execute the remaining DAT command stream, entity lifecycles, collision, all camera/3D controls, renderer state, or other gameplay systems. WIP172 labels it **Experimental SCROLL preview**.

The full decoded DAT timeline remains visible alongside it, but the timeline is evidence for commands, not proof that the browser has executed them.

## Sprite/presentation boundary

The browser renders converted atlas PNGs through Canvas. Therefore appearance depends on the current TEX conversion, atlas extraction, CSS scaling, and host browser sampling. A sprite that looks jittery/incorrect in the generated explorer is not treated as evidence that native SIIG rendered it that way. No new native-pixel-equivalence claim is made in WIP172.

## UX correction

Timeline search and category filtering formerly called the full `render()` path. That rebuilt the map canvases and reset the motion frame on every filter change, contributing directly to the janky feel. WIP172 updates only the timeline table for those filters. Stage changes and map-presentation changes still rebuild panels when needed.

## Continuation rule

Future Stage Explorer changes should improve decoded-data inspection first. Stronger terms such as "faithful", "accurate gameplay viewer", or "frame-accurate playback" should only return after the corresponding native behavior has been demonstrated and regression-tested rather than approximated.
