# CENTIPEDE runtime assembly — dev14

## Result

CENTIPEDE is a fixed 32-link runtime chain. The constructor preallocates both A0 (`bos_007.gmx`) and BE (`bos_007a.gmx`) handles for every segment, but these are **alternate per-link display states**, not simultaneous layers.

The exact initial-combat ring is:

- link 1: role 1 / head / A0 (`bos_007.gmx`)
- links 2–31: role 2 / body / BE (`bos_007a.gmx`)
- link 32: role 3 / tail / A0 (`bos_007.gmx`)

Therefore the visible ring is **2 A0 + 30 BE = 32 models**. The separately allocated record-0 A0 object is a controller/parent record and is not part of the linked visible ring preset.

## Exact ring transform

For link `i=1..32`:

`angle = -90° + (i-1)*11.25°`

`X = cos(angle)*80`  
`Y = 0`  
`Z = sin(angle)*80`  
`Ry = -angle`

Retail Xbox implements this in `0x821133A0`; June 10 independently retains it at `0x8212CA90`; retail PS3 retains the same construction at `0x001A16D8`.

## Why both GMXs are allocated

Retail `0x82115028` dispatches each live segment by role into `0x82113148`:

- role 1 or 3 -> A0 on, BE off
- role 2 -> A0 off, BE on

This directly matches the supplied gameplay capture: normal body pieces are BE, while the two chain ends are A0.

## Splitting

When a role-2 body segment is destroyed, `0x82115140` severs its previous/next links. The adjacent surviving links enter endpoint transition states; those handlers assign role 1 on one side and role 3 on the other. The ordinary role-display dispatcher then promotes both new exposed ends to A0 automatically.

Because the cut index is player-dependent, there is no single canonical split-chain assembly.

## Endpoint destruction and reformation

Destroying a segment already carrying role 1 or 3 takes the alternate branch in `0x82115140` and calls `0x82113F48`, which clears/reinitializes the surviving chain state before the later reform states rebuild the boss. Gameplay observation identifies this interval as the invulnerable random-reposition/reform mechanic.

## Final phase

Retail `0x821154A0` checks `32 - destroyed < 6`; therefore the independent-piece phase begins once **five or fewer links survive**. The final-state path detaches surviving links and promotes them to role 1/A0 before independent randomized movement. June `0x8212ECE8` and PS3 `0x001A58D0` retain the same `<6` threshold.

A static final-phase pose is intentionally **not** provided because its positions are runtime-randomized.

## Real retail validation

The `centipede_initial_combat_ring` catalog was exported from the freshly retained retail Xbox assets:

- 32 GMX instances
- 64 glTF meshes
- 128 glTF nodes
- 0 native animations
- bounds approximately X/Z ±102.3733, Y ±2.88236

No retail GMX or screenshot is bundled in the source-only toolkit.
