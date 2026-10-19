# SIIG Asset Toolkit 2.9.0-dev7

## Headline: evidence-bounded rigid glTF skin compatibility

Dev7 resolves the planned skinning investigation without inventing an unsupported native format. The supplied retail GMX evidence shows rigid scene-node attachment rather than per-vertex skin weights. An external dev7 cross-check of `player.bin` and `enemy.bin` covers 150 GMXs / 901 MESH records: all use `MESH.skin_index = 0xFFFF`, and all mesh declarations contain only POSITION, NORMAL, UV, COLOR and the index array. This agrees with the earlier 486-GMX finding that per-vertex skin weights are absent. Proprietary corpus inputs are not bundled.

The new `--sync-rigid-skins` compatibility path accepts glTF `skins`, `JOINTS_0`, and `WEIGHTS_0` only when every vertex resolves to the same single joint with weight 1.0. The compiler then maps that skin to the proven SIIG representation by synthesizing/resolving the joint BONE hierarchy and attaching the whole MESH/MTRL to the selected BONE. Non-bone armature/container nodes may sit between native joint nodes. `gltf2gmx-new` and Mod Workspace enable this safe path automatically.

A new regression proves a two-joint glTF skin rigidly bound to the child becomes two BONEs plus one child-attached MESH, preserves `skin_index=0xFFFF`, emits no invented weight arrays, and exports faithfully as a rigid native scene. A 50/50 blended vertex is rejected. The dependency-free suite is **81/81**.

## Boundaries

- True blended/multi-joint vertex skinning is not claimed or encoded; no native per-vertex weight representation is confirmed.
- `JOINTS_1`/`WEIGHTS_1` are rejected.
- A selected non-identity inverse-bind matrix is rejected in dev7; geometry rebaking through inverse-bind matrices is future work.
- `MESH.skin_index` remains semantically unresolved beyond the observed `0xFFFF` no-skin value and is not repurposed as a glTF skin index.
- Runtime acceptance of fully original template-free scenes remains an emulator/hardware validation gate.
- Platform shader microcode compilation remains unresolved.
- Audio rebuilding remains deferred.

Under the project's versioning policy, dev7 is the last planned 2.9 feature checkpoint before the mandatory minor-version review. A new substantial capability track should begin at 2.10.0 rather than extending another long dev-suffix chain.
