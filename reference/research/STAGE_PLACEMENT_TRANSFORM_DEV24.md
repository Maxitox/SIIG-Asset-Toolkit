# Stage placement native transform — dev24 WIP159

## Result

The former Stage Explorer placement-Euler boundary is closed. Retail Xbox 360 and retail PS3 use the same model-transform convention for the fixed `0x118` stage placement records:

```text
row-vector local point * S * Rz(z) * Rx(x) * Ry(y) * T
```

The record stores `position[3]`, `stored_scale[3]`, and `rotation_degrees[3]`. Runtime scale is `stored_scale * 5.0`; the stored rotations are converted from degrees and consumed in **Z, X, Y multiplication order**, followed by translation. This is the same SIIG model-matrix convention already recovered independently in the GMX/boss transform work, now tied to the stage-placement consumer rather than inferred from appearance.

## Evidence boundary

- Xbox 360: retained retail/June PPC analysis reaches the stage placement consumer and the common model transform path used by the loaded `<name>.gmx` instance. The common model path composes the scale/rotation/translation matrices in the order above.
- PS3: the project-owner retail EBOOT Ghidra export independently preserves the same placement-to-model transform sequence.
- No screenshot-fit correction or guessed axis swap is introduced.
- This result closes **Euler multiplication/order** for placement rendering. It does not resolve route↔DAT ownership/activation, collision, arbitrary scene-control side effects, or claim a byte-identical gameplay camera.

## Stage Explorer implementation

`siig_stageviz.py` transforms all eight corners of each available GMX root geometry AABB with the native placement transform. Orbit, top-down, and POV views render those same transformed corners as a wire box. If the GMX AABB is unavailable, the pre-existing small fallback proxy remains an inspection marker.

The built-in Stage Explorer regression uses a deliberately non-symmetric AABB, runtime scale `(5, 10, 15)`, stored rotation `(0°, 90°, 0°)`, and preview origin `(10, 20, -370)`. Under the recovered transform the first two corners become `(-35, 0, -365)` and `(-35, 0, -390)`, which prevents a return to the former axis-aligned approximation or a different Euler order.
