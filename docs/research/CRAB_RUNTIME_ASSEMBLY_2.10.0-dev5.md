# CRAB landed runtime assembly — 2.10.0-dev5

## Why dev5 changes the beginner preset

Dev4 correctly reconstructed an executable-defined **first-visible** CRAB snapshot at native root sample 167. Project-owner Blender validation then exposed an important presentation fact: that state occurs while CRAB is still airborne during its entrance. It is evidence-correct, but inconvenient as the default editable assembly because the visible boss sits hundreds of native units above the ground plane.

Dev5 therefore **preserves** the original `crab_first_visible` catalog unchanged for provenance and changes the ordinary beginner-facing `crab` catalog to the first deterministic **landed/combat-ready** pose.

No arbitrary recentering or visual guess was applied.

## Landed formation

After the intro animation finishes, the executable returns A7 to its looping `bos_013` segment `1→60`. The first sample of that loop, native sample **1**, is therefore a deterministic landed state. The visible root geometry at sample 1 spans approximately Y `-0.126642` to `207.863`, placing the feet essentially on the native ground plane.

The resulting nine-object dev5 `crab` catalog is:

| index | runtime | model | role | native pose sample | translation | outer rotation |
|---:|---|---|---|---:|---|---|
| 0 | `0xA7` | `bos_013.gmx` | leg/root assembly | 1 | `(0,0,0)` | `(0,180,0)` |
| 1 | `0xCD` | `bos_013b.gmx` | body shell | 0 | `(0,214.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 2 | `0xCC` | `bos_013a.gmx` | central cannon | — | `(0,214.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 3 | `0xCE` | `bos_013c.gmx` | propodus | — | `(81,214.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 4 | `0xCE` | `bos_013c.gmx` | propodus | — | `(-81,214.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 5 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(81,237.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 6 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(81,191.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 7 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(-81,237.9811019897461,-3.018549919128418)` | `(0,0,0)` |
| 8 | `0xCF` | `bos_013d.gmx` | dactyl | — | `(-81,191.9811019897461,-3.018549919128418)` | `(0,0,0)` |

At native sample 1 the A7 root translation is approximately `(0,168.994,3.01855)` and the root animation carries its native 180° Y orientation. `lt_000` contributes local Y≈`45.9871`; the runtime outer 180° root transform yields the attachment center above while preserving the game's coordinate convention.

The actual assembled landed scene was checked against the retail GMXs outside the release and has approximate bounds `(-89.3984,-0.126642,-103.5331)` to `(89.3984,255.7224,103.5391)`.

## Preserved first-visible preset

`crab_first_visible` remains available and retains the dev4 sample-167 airborne reconstruction with attachment center Y `422.0840835571289`. The dev4 research/table/validation files are intentionally not rewritten.

## Evidence boundary

The change in default is a choice between **two recovered runtime states**, not a correction to the dev4 math. Both remain valid snapshots. The beginner GUI uses the landed state because it is more useful for viewing/editing in Blender and corresponds to the stable combat loop rather than the descent animation.
