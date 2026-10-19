# PROGRESSIVE UFO barrier direction — dev23 correction

## Problem

The `progressive_ufo_classic` catalog carried a dev16 presentation override that reversed the two C3 / `bos_009b.gmx` Z-rotation signs. That override was not part of the executable pose table and contradicted the dev16 research note's own rule that no screenshot-derived orientation correction should be applied. Project-owner Blender feedback later observed that the barriers appeared to point backwards.

## Retail Xbox table

`Function_82536720` initializes the recurring table at `0x82568180`. The C3 records are written exactly as:

- runtime part 3: position `(115, 0, 3)`, Euler `(0, 0, +1.7453292608261108)`
- runtime part 4: position `(-115, 0, 3)`, Euler `(0, 0, -1.7453292608261108)`

`Function_82127018` applies this table in major states 5 and 8. The existing SIIG transform path remains `Rz * Rx * Ry * T` with the recovered runtime Y-sign convention.

## dev23 change

The toolkit now emits those two executable signs literally. No additional visual/outward-facing sign swap is applied. `bos_009b.gmx`'s authored internal approximately 190.794-degree face/edge bind tilt remains untouched; this correction concerns only the outer C3 runtime record.

The original `progressive_ufo` first-formation catalog remains unchanged because its recovered C3 outer rotation is zero.
