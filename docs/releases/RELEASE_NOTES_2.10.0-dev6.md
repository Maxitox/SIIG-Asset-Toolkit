# SIIG Asset Toolkit 2.10.0-dev6

## Main result

Dev6 resolves HORNET's later C0 prism-wall attack as an evidence-backed **13-variant runtime family** across June Xbox, retail Xbox and retail PS3. The game chooses one of 13 exact 5×9 grid records for A1; that subordinate C0 is hidden and A1 occupies the cell, while 44 C0 prisms occupy every other cell.

Built-in catalogs are `hornet_prism_wall_00`, `_02`, `_06`, `_08`, `_18`, `_20`, `_22`, `_24`, `_26`, `_36`, `_38`, `_42`, and `_44`. An unqualified `hornet_prism_wall` request is intentionally rejected rather than silently selecting a random retail outcome.

A1's own native loop is preserved instead of baking an arbitrary internal animation sample. The settled outer wall transforms are identity rotation/unit scale.

## GUI

GUI `0.17.0-dev6` keeps the deterministic HORNET full-armor button in Simple mode. Advanced mode adds an exact runtime slot selector plus prism-wall manifest/assembly actions.

## Validation

- dependency-free regression suite: **88/88**;
- representative synthetic prism-wall export verifies all 45 cells, A1 substitution, missing selected C0 and retained A1 animation;
- external real-retail slot-22 export: **45 instances / 90 meshes / 180 nodes**, A1 at `(213.5,0,120)`;
- source release continues to exclude proprietary GMXs, executables, Ghidra exports and ANM files.

## Remaining boundary

HORNET state 6 uses a separate neighborhood/propagation attack over the 45-record system. It is not equivalent to the recovered prism wall and remains unresolved.
