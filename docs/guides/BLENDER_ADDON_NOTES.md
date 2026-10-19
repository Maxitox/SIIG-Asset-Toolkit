# Blender add-on

The current `addons/SIIG_Blender_Addon_v0.4.0.zip` supports Blender 3.6 or newer.

The add-on deliberately does **not** implement a second GMX parser. Raw GMX import loads the selected toolkit installation, runs the verified GMX → glTF exporter in Blender's Python process, and hands the temporary glTF to Blender's built-in importer. This keeps Blender results aligned with command-line conversion fixes.

## Installation

1. Open **Edit → Preferences → Add-ons** in Blender.
2. Choose **Install from Disk** and select `addons/SIIG_Blender_Addon_v0.4.0.zip`.
3. Enable **SIIG Asset Toolkit**.
4. In the add-on preferences, choose the folder containing `siig_toolkit.py`.

An alternative is to set the `SIIG_TOOLKIT_HOME` environment variable to the toolkit folder. Add-on 0.4.0 retains the upward source-tree discovery fix, so the readable source copy inside an unpacked toolkit can find the adjacent `siig_toolkit.py` without accidentally stopping at `addons/`.

## 0.4.0 editing defaults

The 0.3.0 preview defaults could make an otherwise correct import look as though Blender had baked black outlines into the model. In reality the toolkit was preserving SIIG's separate native `_E` edge pass, and the optional host preview could also be applied automatically.

0.4.0 makes those layers explicit:

- Raw GMX **Visual pass** defaults to **Solid only (recommended for editing)**.
- **Native solid + outline**, **Outline only**, and **Combined solid + outline** remain selectable when the native edge pass is wanted.
- Toolkit-generated assemblies may already contain `_E` objects. Those are hidden after import by default, not deleted.
- **Hide Native _E Outlines** / **Show Native _E Outlines** in the SIIG sidebar control them later.
- **Auto-apply SIIG Style Preview after import** is a new opt-in setting and defaults off, so old 0.3.0 saved preview preferences cannot silently force the presentation layer back on.

## Raw GMX features

- File → Import → **Space Invaders Infinity Gene (.gmx)**.
- Multi-file selection and recursive folder import.
- Selectable visual pass with editing-first solid default.
- Optional V-coordinate flip and configurable texture-search root.
- Optional collection per raw GMX.
- Source filename and toolkit version stored as Blender custom properties.
- Missing textures reported without discarding geometry.

## Assembled-model visibility

Toolkit Boss/Entity assemblies can preserve native face/solid (`_F`) and edge/outline (`_E`) meshes as separate Blender objects. Hiding only one mesh object therefore leaves its overlapping sibling visible.

- **Import SIIG Assembly (.gltf/.glb)** imports an assembled toolkit output and automatically builds logical part collections.
- **Organize SIIG Part Collections** can post-process an already imported toolkit assembly.
- `_E` objects are hidden after SIIG assembly import by default; this is reversible from the sidebar.

Each toolkit `siigAssemblyModel` master becomes one `SIIG_PART_*` collection containing that master and its native descendants, stopping at nested child-part masters. Use the collection eye/monitor controls in Blender's Outliner to hide/show a whole logical part while native transform parenting and animations stay intact.

## SIIG Style Preview (optional)

The sidebar retains the **SIIG Style Preview** box, but it is now opt-in.

### White native outlines

When native `_E` geometry is available, the preview can create thin white emissive curve objects from those edge segments. Generated objects are marked `siig_style_preview_outline`, parented to the original `_E` objects, and use a dedicated `SIIG_Preview_Outline_White` material. Refreshing first removes only those generated preview objects.

### Compositor scanline overlay and Blender 5

Blender 5 removed `Scene.node_tree`, removed the old Composite node, and moved scene compositing to `Scene.compositing_node_group` with a Group Output node. Add-on 0.4.0 isolates that compatibility boundary:

- Blender 3.6/4.x uses the legacy scene node tree.
- Blender 5.x uses `compositing_node_group` and Group Output.
- Nodes removed by Blender 5's compositor unification use their supported Shader-node counterpart where needed.
- Existing upstream image links are recorded/restored when the SIIG scanline layer is removed.

The scanline overlay remains a host-side preview, not native game rendering.

## Validation boundary

The release regression validates Python syntax, package/source identity, expected operators, solid-only default selection, reversible native-outline hiding, logical-master metadata handling, Blender 3.6/4.x vs 5.x compositor source contracts, source-tree discovery, and non-destructive hierarchy/link-restoration rules.

Blender itself is not available in the release-build environment. The `_E` geometry source is native/recovered, but generated curve width and scanline appearance are host presentation controls and are **not** claimed to reproduce exact Xenos/RSX line rasterization, antialiasing, or final scanout. Final visual/UI behavior remains an in-Blender runtime gate.
