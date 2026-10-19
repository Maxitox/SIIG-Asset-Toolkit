# ULTIMATE UFO runtime assembly — 2.10.0-dev9

## Scope

This checkpoint reconstructs ULTIMATE UFO as a **complete 126-instance allocated GMX hierarchy** plus state-specific controller-activity subsets. The complete catalog is a constructor-baseline allocation/hierarchy view, not a claim that every phase-gated member is simultaneously rendered or gameplay-active. The exporter uses exact named GMX locator nodes and preserves the parent/child hierarchy so native parent animation can drive attached children.

## Evidence boundary

The retail Xbox executable is authoritative for pool sizes, controller grouping, phase visibility, locator ranges, and parent rotation behavior. June 10 independently preserves the same component grouping and locator-number ranges. Project-owner footage/model inspection supplies friendly gameplay labels (Umb/Tow/Fan/Ring and the visible roles of several assets), but those observations are kept distinct from executable proof.

No retail `bos_015*.gmx` binaries are bundled. They were not present in the persistent research Library during this checkpoint, so dev9 does **not** claim a fresh real-retail glTF export. The implementation instead resolves named locators at export time from the user's own extracted GMXs; missing or ambiguous locator nodes are hard errors.

## Runtime inventory

The retail parent setup constructs the A8 body plus subordinate model pools: D0×1, D1×1, D2×1, D3×1, D4×21, D5×2, D6×32, D7×64, D8×1 and D9×1. Together with A8 this is **126 allocated model instances**. Allocation does not mean all 126 are simultaneously visible.

Retail model identities used by the assembly catalogs:

- A8 → `bos_015.gmx` main body
- D0 → `bos_015a.gmx` FAN parent A
- D1 → `bos_015b.gmx` FAN parent B
- D2 → `bos_015c.gmx` RING parent A
- D3 → `bos_015d.gmx` RING parent B
- D4 → `bos_015g.gmx` TOW child family
- D5 → `bos_015h.gmx` UMB child family
- D6 → `bos_015i.gmx` FAN attached children
- D7 → `bos_015j.gmx` RING attached children
- D8 → `bos_015k.gmx` late airlock object
- D9 → `bos_015l.gmx` state-9 core/weak-spot assembly

`bos_015e.gmx` and `bos_015f.gmx` are not present in the recovered registry.

## Exact named-locator hierarchy

The retail string/data table contains the format `lt_%03d`. Controller constructors generate exact attachment records and update children through those parent locator matrices:

- D5×2 attach directly to A8 `lt_002..lt_003`.
- D4×21 attach directly to A8 `lt_004..lt_024`.
- FAN parent A (D0) owns D6 children at `lt_226..lt_241`; FAN parent B (D1) owns `lt_242..lt_257`.
- RING parent A (D2) owns D7 children at `lt_258..lt_289`; RING parent B (D3) owns `lt_290..lt_321`.

The D0/D1 and D2/D3 parents are runtime rotating GMXs. At their activation boundary 0° and 360° are equivalent identity orientations, while the controller metadata records opposite Y-axis steps: D0 +0.5, D1 −0.5, D2 −1.0, D3 +1.0. The exporter preserves the GMXs' native animations and locator hierarchy; it does not bake guessed child XYZ positions.

Useful child-local named sets recovered alongside the hierarchy include D4 `hit_009..hit_012`, D5 `hit_013..hit_016`, D6 `hit_002..hit_008`, late controller `hit_017..hit_019`, and D9 `hit_020..hit_022`. These are documented semantics, not substituted for the outer `lt_###` placement hierarchy.

## Complete hierarchy and retail activity subsets

The retail MoveMain phase table writes Umb/Tow/Fan/Ring **collision/destructibility controller flags**. Those bytes do not prove render visibility. Dev9 therefore exposes `ultimate_ufo_complete` for the entire 126-instance allocation hierarchy and eight activity-focused subsets for inspecting the families controlled at specific states:

| Catalog | Mframe | Activity-focused model family | Instances |
|---|---:|---|---:|
| `ultimate_ufo_state_02` | 1750 | A8 + 2×D5 / UMB | 3 |
| `ultimate_ufo_state_03` | 2250 | A8 + 21×D4 / TOW | 22 |
| `ultimate_ufo_state_06` | 4450 | A8 + FAN + RING | 101 |
| `ultimate_ufo_state_07` | 5100 | A8 + FAN + RING | 101 |
| `ultimate_ufo_state_08` | 5300 | A8 + RING | 67 |
| `ultimate_ufo_state_09` | 5897 | A8 + D9 core | 2 |
| `ultimate_ufo_state_11` | 5902 | A8 + D8 airlock | 2 |
| `ultimate_ufo_state_12` | 6030 | A8 + D8 late | 2 |

States 1/4/5/10/13 do not get separate activity-subset catalogs because they add no distinct model-family activity useful for assembly inspection. This is not a statement that the persistent D4–D7 geometry disappears when its col/dis flags are zero.

## GUI

GUI 0.20.0-dev9 adds an ULTIMATE UFO selector in both Simple and Advanced GMX Workbench modes. Simple mode defaults to **COMPLETE — 126 allocated hierarchy**. The numbered choices are explicitly activity-focused subsets; Advanced mode additionally writes the selected manifest.

## Validation

The regression verifies all eight catalog counts/Mframes, exact D4/D5/D6/D7 locator ranges, D6/D7 parent splits, rotating-parent metadata, D9/D8 late-state identities, and state-8 FAN exclusion. The existing assembly-export regression independently proves that `attach_to {instance,node}` reparents children to exact named source nodes, preserves provenance, rejects missing locators, and rejects attachment cycles.

See:

- `reference/tables/ULTIMATE_UFO_RUNTIME_ATTACHMENT_MAP_2.10.0-dev9.csv`
- `reference/tables/ULTIMATE_UFO_PHASE_ACTIVITY_2.10.0-dev9.csv`
- `validation/ULTIMATE_UFO_RUNTIME_ASSEMBLY_2.10.0-dev9.json`
