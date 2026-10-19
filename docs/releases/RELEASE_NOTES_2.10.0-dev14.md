# SIIG Asset Toolkit 2.10.0-dev14

Dev14 resolves CENTIPEDE's canonical initial-combat assembly and the topology rules behind its later combat splits without inventing randomized poses.

## Initial combat ring

`centipede_initial_combat_ring` exports exactly **32 visible links**: two A0 / `bos_007.gmx` endpoint forms and thirty BE / `bos_007a.gmx` body forms. Link positions are generated at radius 80 with 11.25° spacing beginning at -90°, and each link receives the executable-backed Y orientation. The ring is a real doubly linked chain: link 1 is head, links 2–31 are body, and link 32 is tail.

## Role-driven form swapping

The constructor preallocates both A0 and BE handles per link, but the runtime role switch makes only one form active: head/tail roles select A0; body role selects BE. This matches project-owner gameplay observation and the supplied screenshot, but the release preset is grounded in the executable behavior rather than visual reconstruction.

Destroying a body link severs its neighbor links and promotes the newly exposed ends to endpoint roles, which swaps those pieces to A0. Destroying an existing endpoint enters the separate reform path.

## Final phase boundary

Retail, June 10 and PS3 all use the same threshold: when fewer than six pieces remain (**five or fewer survivors**), live pieces are unlinked and become independent A0 movers. Their subsequent destinations are runtime-randomized, so dev14 deliberately provides no fake static final-phase assembly.

## Real-asset validation

Fresh retail export validates the canonical ring as **32 instances / 64 meshes / 128 nodes**, with native bounds approximately `X/Z ±102.3733`, `Y ±2.88236`. No retail GMX, screenshot or generated retail glTF is bundled.

GUI **0.25.0-dev14** adds CENTIPEDE manifest and one-click assembly actions in both Simple and Advanced modes. The dependency-free regression suite is **96/96** through development gating.
