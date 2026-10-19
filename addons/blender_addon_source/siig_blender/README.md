# SIIG Blender Add-on 0.4.0

This add-on imports extracted SIIG `.gmx` models through the verified GMX → glTF exporter in `siig_toolkit.py`. It also imports toolkit-generated assembled `.gltf`/`.glb` scenes, organizes logical SIIG components into hideable Blender collections, and provides an optional **SIIG Style Preview**. It does not contain game assets and does not contact the network.

## Install

1. In Blender, open **Edit → Preferences → Add-ons**.
2. Choose **Install from Disk** and select `addons/SIIG_Blender_Addon_v0.4.0.zip`.
3. Enable **SIIG Asset Toolkit**.
4. Open the add-on preferences and select the folder containing `siig_toolkit.py`.

Blender 3.6 and newer remain the supported baseline. Add-on 0.4.0 also migrates the compositor integration to Blender 5's `Scene.compositing_node_group` API while retaining the older `Scene.node_tree` path for Blender 3.6/4.x.

## Editing-first import behavior

0.4.0 changes the defaults so a normal model import is useful for editing rather than automatically styled like an in-game preview.

- Raw GMX import defaults to **Solid only**, so the native `_E` edge pass is not brought in unless you request it.
- **Native solid + outline**, **Outline only**, and **Combined solid + outline** remain available from the Visual pass selector.
- Assembled glTF/GLB files can still contain preserved `_E` objects; the add-on hides those objects after import by default instead of deleting them.
- The SIIG sidebar provides **Hide Native _E Outlines** and **Show Native _E Outlines** for non-destructive control.
- Automatic SIIG Style Preview is **off by default** in 0.4.0. White preview outlines and scanlines are opt-in presentation helpers.

This keeps native outline data recoverable without forcing black edge meshes over every imported model in Blender's normal viewport/material display.

## Import and assembly controls

- **File → Import → Space Invaders Infinity Gene (.gmx)** imports one or several raw GMX files.
- **File → Import → SIIG Assembled Model (.gltf/.glb)** imports a Boss/Entity Assembler result.
- The **SIIG** sidebar exposes **Organize SIIG Part Collections** for an assembly imported previously with Blender's normal glTF importer.
- Hide/show a generated `SIIG_PART_*` collection in the Outliner to toggle one logical game part, including its preserved solid/face (`_F`) and edge/outline (`_E`) descendants when both were exported.
- Recursive raw-GMX folder import, optional V flip, and an external texture root remain available.

## SIIG Style Preview

The preview is deliberately host-side and non-destructive. It does not rewrite GMX, textures, animations, or the game renderer.

### Optional white native outlines

When native `_E` geometry is present, the add-on can build thin white emissive **curve copies** from those edges. The original edge meshes remain untouched.

- Turn on **White native outlines**.
- **Outline thickness (%)** scales the curve radius relative to each native outline object's local bounds.
- **Apply / Refresh SIIG Style Preview** rebuilds only the generated preview curves.
- **Remove SIIG Style Preview** deletes the generated curves and leaves the imported model unchanged.

### Optional post-process scanlines

Scanlines are applied after the existing compositor image source rather than being inserted into every material. The add-on creates a one-pixel-wide horizontal pattern, scales it to the render dimensions, and multiplies it over the final image.

- Turn on **Post-process scanlines**.
- Adjust spacing, thickness, and strength in the SIIG sidebar.
- If render resolution changes, press **Apply / Refresh SIIG Style Preview** so pixel spacing is regenerated for the new output height.
- Removing the preview restores the compositor image link that existed before the SIIG overlay was inserted.

Blender 5 removed `Scene.node_tree` and the old Composite node. 0.4.0 therefore uses the scene's compositor node group and Group Output in Blender 5 while retaining the legacy path for older supported Blender versions.

## Fidelity boundary

The outline source geometry is native SIIG `_E` data, but Blender curve radius is a host presentation choice. The scanline overlay is also a Blender post-process approximation. Neither feature is presented as an exact reconstruction of Xenos/RSX rasterization, native line width, antialiasing, scanout, or final-composite behavior.

Source syntax, packaging, metadata/grouping contracts, compatibility branches, and exporter integration are regression-tested outside Blender. A real Blender executable is not bundled with the toolkit, so final visual/UI behavior still benefits from in-Blender testing.
