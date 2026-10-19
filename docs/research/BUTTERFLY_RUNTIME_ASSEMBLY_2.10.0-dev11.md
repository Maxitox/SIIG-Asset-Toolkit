# BUTTERFLY four-phase runtime assembly — 2.10.0-dev11

## Result

BUTTERFLY's four retail forms are now reconstructed as exact executable-backed assembly catalogs rather than visual approximations:

- `butterfly_phase_1`
- `butterfly_phase_2`
- `butterfly_phase_3`
- `butterfly_phase_4`

The three small GMXs `bos_011d/e/f.gmx` are **wing modules**, not additional boss phases. The project owner's gameplay screenshots supplied during dev11 independently corroborate the resulting layouts, but the preset counts and placement come from executable loader records and native `lt_*` locator hierarchy.

## Exact retail loader table

Retail Xbox function `0x82111F48` iterates ten 16-byte records at `0x82009560..0x820095FC`. Each record supplies a phase/group index, a model-table index, an instance count, and a starting index into a 48-entry locator pointer table. The seven model-table entries at `0x82009750..0x82009768` resolve to A4/C4-C9 (`bos_011` through `bos_011f`).

| Phase | Body | Wing modules |
|---|---|---|
| 1 | 1× A4 `bos_011.gmx` | none |
| 2 | 1× C4 `bos_011a.gmx` | 4× C7 `bos_011d.gmx` on `lt_001..lt_004` |
| 3 | 1× C5 `bos_011b.gmx` | 8× C7 `d` on `lt_001..lt_008`; 10× C8 `bos_011e.gmx` on `lt_009..lt_018` |
| 4 | 1× C6 `bos_011c.gmx` | 8× C7 `d` on `lt_001..lt_008`; 32× C8 `e` on `lt_009..lt_040`; 8× C9 `bos_011f.gmx` on `lt_041..lt_048` |

`PTR_DAT_82543150` resolves locator indices 0..47 to `lt_001..lt_048` in order. The exporter therefore parents every module under its exact named node instead of baking a screenshot-derived position.

## June 10 cross-check

June independently retains the same ten-record scheme in `Function_8212B490`:

- record table `0x8200F1A0..0x8200F23C`;
- model-index table `0x8200F720..0x8200F738` = A4/C4/C5/C6/C7/C8/C9;
- locator pointer table `PTR_DAT_82573D00`;
- all ten `(phase, model-index, count, locator-start)` values match retail Xbox exactly.

Retail PS3 independently maps the same runtime identities A4/C4-C9 to `bos_011`/`a`/`b`/`c`/`d`/`e`/`f` in the recovered entity registry. Dev11 does not invent an unproven PS3 loader address where one was not needed.

## Real retail GMX evidence

The re-uploaded original Xbox retail package was unpacked through the toolkit, then `enemy.bin` was extracted and scanned directly.

- `bos_011.gmx`: 2 meshes, 3 bones, no native motions, and no wing `lt_*` locators.
- `bos_011a.gmx`: 6 meshes, 11 bones, three native motions, exactly `lt_001..lt_004`.
- `bos_011b.gmx`: 6 meshes, 25 bones, three native motions, exactly `lt_001..lt_018`.
- `bos_011c.gmx`: 6 meshes, 55 bones, three native motions, exactly `lt_001..lt_048`.
- `bos_011d.gmx`: 3 meshes; large square module.
- `bos_011e.gmx`: 3 meshes; small square module.
- `bos_011f.gmx`: 3 meshes; elongated rectangular module.

The module-role names are supported by their actual GMX geometry and independently match the supplied gameplay captures.

## Real assembly export validation

All four catalogs were exported against the real retail files:

| Phase | Instances | glTF meshes | glTF nodes | Native animations retained |
|---|---:|---:|---:|---:|
| 1 | 1 | 2 | 4 | 0 |
| 2 | 5 | 18 | 32 | 3 |
| 3 | 19 | 60 | 116 | 3 |
| 4 | 49 | 150 | 296 | 3 |

Each export has one root node named `body`. Phase-2/3/4 modules are nested under the requested body `lt_*` nodes, so they follow wing animation naturally in Blender. No arbitrary world-space module positions or rotations are introduced.

## Gameplay screenshots

The project owner supplied captures showing phases 2–4. They visually match the executable-backed result: four large squares in phase 2, the large/small-square combination in phase 3, and the large/small/rectangular combination in phase 4. These images are retained as **corroborating observational evidence only**; they are not the source of the counts or locator assignments and are not bundled in the source-only release.

## Evidence boundary

The catalogs reconstruct the model composition and native hierarchy for each form. They preserve native body animation rather than choosing one arbitrary pose frame. They do not claim that every attack-specific transient effect or projectile belongs to the persistent boss assembly.
