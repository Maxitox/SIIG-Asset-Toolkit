# `est_012` shared target-cube identification — dev24 WIP181

WIP181 promotes `est_012.gmx` from an unidentified cube-shaped `est_*` resource to a **project-owner-confirmed shared interactive target cube**, with independent executable ownership corroboration for JOLYNE and UNKNOWN. The semantic/gameplay description comes from the project owner's direct game observation; the resource ownership comes from retained executable analysis. No proprietary executable or model bytes are bundled.

## Project-owner gameplay identification

- **JOLYNE:** the boss unravels an orthogonal fuse/line that turns only at right angles. A transparent shootable cube appears at the endpoint. Shooting that target progresses/returns the fuse toward JOLYNE until the encounter can be finished.
- **UNKNOWN:** during the first phase, the boss creates multiple transparent shootable cubes in changing patterns. Destroying/progressing through that phase eventually removes the cube system and advances the fight.

These observations identify the *visible gameplay role*. They are not represented as recovered internal class or resource names.

## Executable corroboration

### JOLYNE

The May 11 executable labels the relevant class/source as `Jolyne::Init` / `Jolyne.cpp`. `Function_82119D68` initializes ten helper objects, then loads runtime resource `0xE7`; the May prototype runtime registry maps `0xE7` to `est_012.gmx`. Its following update path (`Function_82119F20`) drives the ten segment helpers and the separate endpoint model.

The Xbox retail lineage has the same distinctive setup/update structure: the corresponding setup creates ten helpers and loads runtime `0xE6`; retail maps `0xE6` to `est_012.gmx`.

### UNKNOWN

The Xbox retail boss factory maps UNKNOWN runtime `0x4B` to visual-controller constructor `Function_821300A8`. The controller's setup path `Function_82130190` directly loads runtime `0xE6`, therefore `est_012.gmx`, and provisions up to 120 helper objects. After that pool it also requests runtime `0xBD`, which is a separate retail primitive resource (texture resource ID 13), not another GMX. This cleanly supports a model-cube plus separate primitive/pattern presentation architecture.

### UNKNOWN prototype lineage

The initially ambiguous May 11 `Function_82144298` attribution is now resolved by the boss visual-controller factory: factory case `0x4C` (the recovered `runtime_type + 1` convention for UNKNOWN runtime `0x4B`) constructs `Function_821441B0`, whose setup path is `Function_82144298`. That setup repeats retail UNKNOWN's structure: it loads prototype runtime `0xE7 -> est_012.gmx`, provisions up to 120 helpers, then loads prototype runtime `0xBC`, which the May registry identifies as the same primitive texture-resource-13 slot that moved to `0xBD` in retail.

Therefore the two confirmed gameplay owners are **JOLYNE and UNKNOWN**, each corroborated in retail/prototype lineage. WIP181 does **not** claim a third VERTEBRATE owner; nearby Vertebrate strings were adjacency, not ownership evidence. The game's original internal symbolic name for `est_012` remains unresolved.

## Result

`est_012` is no longer part of the speculative `est_*` identity set. The current effect-identity split is now:

- confirmed effect usages: `est_012`, `est_013`, `est_015`;
- speculative/unidentified: `est_011`, `est_014`, `est_016`, `est_017`, `est_018`, `est_019`, `est_020`, `est_021`.

This identification does not change the global dev24 unresolved-boundary count because that registry did not contain a dedicated `est_012` boundary.
