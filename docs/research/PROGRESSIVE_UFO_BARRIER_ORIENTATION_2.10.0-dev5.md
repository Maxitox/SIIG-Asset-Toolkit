# PROGRESSIVE UFO barrier orientation addendum — 2.10.0-dev5

Project-owner Blender validation of the dev3 PROGRESSIVE UFO assembly noticed that the two `bos_009b.gmx` barrier machines are slightly rotated relative to the other front-facing pieces.

This is **intentional native asset data**, not an error in the recovered assembly matrices.

The executable-backed C3 outer runtime rotation in the dev3 assembly remains exactly zero for both barriers. Inside retail `bos_009b.gmx`, however, the two barrier mesh bones (`p3_E1` and `p3_F1`) carry the same native bind quaternion, approximately:

`(x=0, y=0, z=0.99557, w=-0.09406)`

which corresponds to a Z rotation of approximately **190.794265°** (equivalently **−169.205735°**), around **10.794265° away from a perfect 180° flip**.

The retail `bos_009b.gmx` input used for this check has SHA-256:

`173f0ca1236405bb8d7b5b7123041a344ed1872f3ff2a264951b9c6ff1d006c6`

The exporter preserves the GMX's internal bone transform, so the visible barrier tilt survives correctly in Blender. Dev5 therefore does **not** "straighten" the barriers or alter the evidence-backed outer C3 matrices.

This finding is an orientation clarification only; `progressive_ufo` retains the dev3 placement values and provenance unchanged.
