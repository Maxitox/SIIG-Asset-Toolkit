# Camera preset word 11 — face bias (dev24)

## Result

Retail camera preset word 11 is **`face_bias`**, not an unresolved generic material scalar. All 32 retained retail presets author `0.2`.

## Closure chain

1. The retail camera transition path interpolates preset word 11 like the other scalar preset fields.
2. PS3 tracing had already proven that the resulting scalar is forwarded into the `collada_edge1` / `collada_face1` / `collada_face2` material subsystem, but the virtual setter meaning was previously unknown.
3. Xbox `Function_8214E120` calls material virtual slot `+0x18` with the shared scalar.
4. Raw PPC at **0x82475590** stores that float at material-wrapper offset **+0x60**.
5. The material constructor classifies `collada_edge1`, `collada_face1`, `collada_face2`; `Function_824745F0` uploads the `+0x60..+0x6C` vector only for material type 1 (`collada_face1`).
6. The embedded vertex shader at **0x8208D408** explicitly declares `float4 faceBias : register(c9)` and computes `pos = pos - (In.Normal * faceBias.x)` before WVP projection.

This identifies both the semantic name and the geometric effect. No observational guess is required.
