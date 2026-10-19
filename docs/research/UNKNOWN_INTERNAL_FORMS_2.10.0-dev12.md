# UNKNOWN internal-form reconstruction — 2.10.0-dev12

UNKNOWN is not a multipart GMX assembly. Retail runtime type `0x4B` uses one `bos_006.gmx` whose scene graph contains fourteen named top-level form branches, `uk01` through `uk14`. The retail file has 48 BONE records, 33 MESH records, and no native MOTN/ANIM tracks, so the rapid form change is driven by executable visibility selection rather than a baked GMX animation.

## Runtime selector

Retail Xbox draw `0x821302E8` owns a fourteen-name table at `0x8200B068`. Outside the state-0 override it selects `floor(counter / timing_scale) % 14`. Retail move `0x82240DD0` increments the counter in states other than 0/23 and wraps it at `(timing_scale * 0x168) / 0x1E`, i.e. twelve timing units. With the normalized timing scale this produces the named sequence `uk01..uk12` at 30 selections/second, repeating every 0.4 seconds.

State 0 is special: the draw path explicitly enables the first branch and disables the remaining thirteen, so the countdown does **not** expose `uk13` or `uk14`. State 23 freezes the counter; the renderer therefore keeps the selector corresponding to the frozen value.

June 10 independently preserves the same architecture at draw `0x8214B4C0`, move `0x822682A0`, table `0x820122B8`. Retail PS3 independently preserves it at draw `0x001D5148`, move `0x001039EC`, table `0x004BBB84`.

## Fourteen names, thirteen unique visuals

Fresh extraction of the project owner's retail Xbox `bos_006.gmx` proves that `uk08` is an exact visual duplicate of `uk01`. After each branch's native hierarchy transform is applied, canonical payloads including world-space POSITION/NORMAL, UVs, indices, and material state hash identically. No other pair among the fourteen branches matches.

Therefore:

- named native branches: **14**;
- unique 3D visual forms: **13**;
- normal console cycle: **12 named selections** (`uk01..uk12`);
- unique visuals inside that normal cycle: **11**, because `uk08 == uk01`;
- `uk13` and `uk14` are valid registered branches but are outside the normal twelve-tick cycle traced here.

The project owner independently notes that UNKNOWN's 2D counterpart also duplicates its first form. That observation is retained as corroboration only; the 3D duplicate relation above is independently proven from the retail GMX.

## Toolkit representation

Dev12 exposes `unknown_form_01` through `unknown_form_14`. Each catalog keeps one native `bos_006.gmx` instance and restricts the exported glTF scene to the exact requested `ukXX` subtree; it does not create fourteen GMX copies or invent transforms. `unknown_all_forms` retains the full single-GMX scene graph for Outliner/research inspection. Form 08 is labeled as the visual duplicate of form 01, while remaining separately selectable because the executable retains a distinct `uk08` branch name.

The runtime reference records the exact normal cycle and its evidence boundary. A synthetic visibility animation is intentionally not presented as a native GMX animation: the source GMX has no MOTN/ANIM, and glTF has no direct node-visibility channel. Manual form selection provides an exact representation without substituting scale-to-zero tricks for SIIG's real runtime visibility toggle.

## Real-retail validation

Retail `bos_006.gmx`:

- size: 661,760 bytes;
- SHA-256: `9ec3de255073c7871ef35dce3f27de6305ae9e3b8c1177bcfaeef4a04befbecf`;
- 48 bones / 33 meshes / 0 native animations;
- all fourteen form-subtree exports succeed;
- `unknown_all_forms`: 1 GMX instance / 33 meshes / 49 glTF nodes / 0 animations.

See `validation/UNKNOWN_INTERNAL_FORMS_2.10.0-dev12.json`, `reference/tables/UNKNOWN_INTERNAL_FORMS_DEV12.csv`, and `reference/tables/UNKNOWN_RUNTIME_CYCLE_DEV12.csv` for the machine-readable evidence.
