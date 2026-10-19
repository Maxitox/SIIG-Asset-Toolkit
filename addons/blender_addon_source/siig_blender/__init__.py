from __future__ import annotations

bl_info = {
    "name": "SIIG Asset Toolkit",
    "author": "SIIG Asset Toolkit project",
    "version": (0, 4, 0),
    "blender": (3, 6, 0),
    "location": "File > Import and 3D View > Sidebar > SIIG",
    "description": "Import SIIG GMX models/assemblies with editing-first solid-pass defaults and Blender 5 compositor compatibility",
    "category": "Import-Export",
}

import importlib.util
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import AddonPreferences, Operator, OperatorFileListElement, Panel
from bpy_extras.io_utils import ImportHelper

_MODULE_NAME = "_siig_toolkit_blender_runtime"


_VISUAL_PASS_ITEMS = (
    ("solid", "Solid only (recommended for editing)", "Import the native _F face/solid pass and omit paired _E edge geometry"),
    ("separate", "Native solid + outline", "Preserve separate native _F solid and _E edge/outline passes"),
    ("outline", "Outline only", "Import only the native _E edge/outline pass when a paired pass exists"),
    ("combined", "Combined solid + outline", "Keep both native passes with the toolkits combined-animation export mode"),
)


def _preferences(context):
    addon = context.preferences.addons.get(__package__)
    return addon.preferences if addon else None


def _candidate_toolkits(context) -> Iterable[Path]:
    prefs = _preferences(context)
    if prefs and prefs.toolkit_path:
        selected = Path(bpy.path.abspath(prefs.toolkit_path))
        yield selected / "siig_toolkit.py" if selected.is_dir() else selected
    env = os.environ.get("SIIG_TOOLKIT_HOME")
    if env:
        selected = Path(env)
        yield selected / "siig_toolkit.py" if selected.is_dir() else selected
    here = Path(__file__).resolve()
    # When the readable source copy is used directly from an unpacked toolkit,
    # __file__ lives below addons/blender_addon_source/siig_blender/.  Walk
    # upward instead of assuming a fixed parent depth so both the source-tree
    # layout and future packaging layouts can discover the adjacent toolkit.
    for parent in here.parents:
        yield parent / "siig_toolkit.py"
    yield Path.cwd() / "siig_toolkit.py"


def _find_toolkit(context) -> Path:
    checked = []
    for candidate in _candidate_toolkits(context):
        checked.append(str(candidate))
        if candidate.is_file():
            return candidate.resolve()
    raise RuntimeError(
        "siig_toolkit.py was not found. Set the toolkit folder in Edit > Preferences > Add-ons > SIIG Asset Toolkit. "
        + "Checked: " + "; ".join(checked)
    )


def _load_toolkit(context):
    script = _find_toolkit(context)
    existing = sys.modules.get(_MODULE_NAME)
    if existing is not None and Path(getattr(existing, "__file__", "")).resolve() == script:
        return existing
    root = str(script.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load SIIG toolkit from {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


def _new_objects(before: set[bpy.types.Object]) -> list[bpy.types.Object]:
    return [obj for obj in bpy.data.objects if obj not in before]


def _move_to_collection(objects: Iterable[bpy.types.Object], collection: bpy.types.Collection) -> None:
    """Move objects exclusively into collection.

    Exclusive membership is intentional: if a mesh remains linked to the scene/import
    collection as well as its SIIG part collection, hiding the part collection in Blender
    does not reliably hide that mesh through every remaining collection path.
    Parenting is independent of collection membership and remains untouched.
    """
    for obj in objects:
        if collection not in obj.users_collection:
            collection.objects.link(obj)
        for old in list(obj.users_collection):
            if old != collection:
                old.objects.unlink(obj)


def _custom_prop(obj: bpy.types.Object, key: str):
    try:
        return obj.get(key)
    except Exception:
        return None


_STYLE_OUTLINE_OBJECT_PREFIX = "SIIG_PREVIEW_OUTLINE_"
_STYLE_OUTLINE_MATERIAL = "SIIG_Preview_Outline_White"
_STYLE_SCANLINE_IMAGE = "SIIG_Preview_Scanlines"
_STYLE_SCANLINE_IMAGE_NODE = "SIIG Scanline Image"
_STYLE_SCANLINE_SCALE_NODE = "SIIG Scanline Scale"
_STYLE_SCANLINE_MIX_NODE = "SIIG Scanline Overlay"
_STYLE_SCANLINE_MARKER = "siig_style_scanline_node"
_OUTLINE_NAME_RE = re.compile(r"(?:^|_)E\d*(?:\.\d+)?$", re.IGNORECASE)


def _is_native_outline_object(obj) -> bool:
    """Recognize the native GMX edge/outline pass without touching ordinary scene meshes."""
    if obj is None or getattr(obj, "type", None) != "MESH":
        return False
    if _custom_prop(obj, "siig_style_preview_outline"):
        return False
    name = str(getattr(obj, "name", ""))
    if _OUTLINE_NAME_RE.search(name):
        return True
    data = getattr(obj, "data", None)
    materials = getattr(data, "materials", ()) if data is not None else ()
    for material in materials:
        material_name = str(getattr(material, "name", "")).lower()
        if "collada_edge" in material_name or "edge" in material_name:
            return True
    # Toolkit GMX imports retain source markers on every created object.  A line-only
    # mesh from one of those imports is the conservative fallback for native _E data.
    if _custom_prop(obj, "siig_source_gmx") or _custom_prop(obj, "siig_source_assembly"):
        polygons = getattr(data, "polygons", ()) if data is not None else ()
        edges = getattr(data, "edges", ()) if data is not None else ()
        return len(polygons) == 0 and len(edges) > 0
    return False


def _outline_scale(obj) -> float:
    data = getattr(obj, "data", None)
    vertices = list(getattr(data, "vertices", ())) if data is not None else []
    if not vertices:
        return 1.0
    xs = [float(v.co.x) for v in vertices]
    ys = [float(v.co.y) for v in vertices]
    zs = [float(v.co.z) for v in vertices]
    dx, dy, dz = max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)
    diagonal = (dx*dx + dy*dy + dz*dz) ** 0.5
    return diagonal if diagonal > 1e-8 else 1.0


def _ensure_outline_material():
    material = bpy.data.materials.get(_STYLE_OUTLINE_MATERIAL)
    if material is None:
        material = bpy.data.materials.new(_STYLE_OUTLINE_MATERIAL)
    material.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    material.use_nodes = True
    tree = material.node_tree
    if tree is not None:
        tree.nodes.clear()
        output = tree.nodes.new("ShaderNodeOutputMaterial")
        emission = tree.nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        emission.inputs["Strength"].default_value = 1.0
        tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def _remove_outline_previews() -> int:
    removed = 0
    for obj in list(bpy.data.objects):
        if not _custom_prop(obj, "siig_style_preview_outline"):
            continue
        data = getattr(obj, "data", None)
        bpy.data.objects.remove(obj, do_unlink=True)
        if data is not None and getattr(data, "users", 1) == 0:
            try:
                bpy.data.curves.remove(data)
            except Exception:
                pass
        removed += 1
    return removed


def _create_outline_preview(context, source, thickness_percent: float):
    data = getattr(source, "data", None)
    vertices = getattr(data, "vertices", ()) if data is not None else ()
    edges = getattr(data, "edges", ()) if data is not None else ()
    if not vertices or not edges:
        return None
    curve_data = bpy.data.curves.new(_STYLE_OUTLINE_OBJECT_PREFIX + source.name, "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 1
    curve_data.bevel_resolution = 0
    curve_data.resolution_v = 0
    curve_data.bevel_depth = max(1e-6, _outline_scale(source) * max(0.001, float(thickness_percent)) / 100.0)
    curve_data.resolution_v = 0
    for edge in edges:
        indices = tuple(int(v) for v in edge.vertices)
        if len(indices) != 2 or indices[0] >= len(vertices) or indices[1] >= len(vertices):
            continue
        spline = curve_data.splines.new("POLY")
        spline.points.add(1)
        a = vertices[indices[0]].co
        b = vertices[indices[1]].co
        spline.points[0].co = (float(a.x), float(a.y), float(a.z), 1.0)
        spline.points[1].co = (float(b.x), float(b.y), float(b.z), 1.0)
    if not curve_data.splines:
        bpy.data.curves.remove(curve_data)
        return None
    preview = bpy.data.objects.new(_STYLE_OUTLINE_OBJECT_PREFIX + source.name, curve_data)
    preview.parent = source
    preview.matrix_parent_inverse.identity()
    preview.color = (1.0, 1.0, 1.0, 1.0)
    preview.hide_select = True
    preview["siig_style_preview_outline"] = True
    preview["siig_style_preview_source"] = source.name
    curve_data.materials.append(_ensure_outline_material())
    collections = list(getattr(source, "users_collection", ()))
    if collections:
        collections[0].objects.link(preview)
    else:
        context.scene.collection.objects.link(preview)
    return preview


def _refresh_outline_previews(context, thickness_percent: float) -> int:
    _remove_outline_previews()
    sources = [obj for obj in list(context.scene.objects) if _is_native_outline_object(obj)]
    created = 0
    for source in sources:
        if _create_outline_preview(context, source, thickness_percent) is not None:
            created += 1
    return created


def _set_native_outline_visibility(objects, visible: bool) -> int:
    changed = 0
    for obj in list(objects):
        if not _is_native_outline_object(obj):
            continue
        try:
            obj.hide_set(not visible)
        except Exception:
            pass
        if hasattr(obj, "hide_render"):
            obj.hide_render = not visible
        obj["siig_native_outline_hidden"] = not visible
        changed += 1
    return changed


def _scanline_image(height: int, spacing: int, thickness: int, opacity: float):
    height = max(1, int(height))
    spacing = max(2, int(spacing))
    thickness = max(1, min(int(thickness), spacing - 1))
    opacity = max(0.0, min(float(opacity), 0.95))
    image = bpy.data.images.get(_STYLE_SCANLINE_IMAGE)
    if image is None:
        image = bpy.data.images.new(_STYLE_SCANLINE_IMAGE, width=1, height=height, alpha=True, float_buffer=False)
    elif tuple(image.size) != (1, height):
        image.scale(1, height)
    pixels = []
    dark = 1.0 - opacity
    for y in range(height):
        value = dark if (y % spacing) < thickness else 1.0
        pixels.extend((value, value, value, 1.0))
    image.pixels.foreach_set(pixels)
    try:
        image.colorspace_settings.name = "Non-Color"
    except Exception:
        pass
    image.update()
    return image


def _scene_compositor_tree(scene, *, create: bool):
    """Return the scene compositor tree across Blender 3.6/4.x and 5.x.

    Blender 5 removed Scene.node_tree and moved scene compositing to the
    compositing_node_group data block.  Keep the compatibility boundary here so
    the rest of the add-on never assumes one Blender compositor generation.
    """
    if hasattr(scene, "compositing_node_group"):
        tree = getattr(scene, "compositing_node_group", None)
        if tree is None and create:
            tree = bpy.data.node_groups.new("SIIG Compositor Preview", "CompositorNodeTree")
            tree["siig_style_created_tree"] = True
            scene.compositing_node_group = tree
        return tree
    if create and not bool(getattr(scene, "use_nodes", False)):
        scene["siig_style_nodes_were_enabled"] = False
        scene.use_nodes = True
    return getattr(scene, "node_tree", None)


def _group_output_node(tree):
    outputs = [node for node in tree.nodes if getattr(node, "bl_idname", "") == "NodeGroupOutput" or getattr(node, "type", "") == "GROUP_OUTPUT"]
    output = outputs[0] if outputs else tree.nodes.new("NodeGroupOutput")
    image_input = output.inputs.get("Image")
    if image_input is None:
        interface = getattr(tree, "interface", None)
        if interface is None or not hasattr(interface, "new_socket"):
            raise RuntimeError("Blender compositor group output has no Image socket")
        interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        image_input = output.inputs.get("Image")
    if image_input is None:
        raise RuntimeError("Blender compositor group output could not expose an Image socket")
    return output


def _active_composite_node(scene, tree):
    if hasattr(scene, "compositing_node_group"):
        return _group_output_node(tree)
    composites = [node for node in tree.nodes if getattr(node, "type", "") == "COMPOSITE"]
    if composites:
        return next((node for node in composites if getattr(node, "is_active_output", False)), composites[0])
    node = tree.nodes.new("CompositorNodeComposite")
    node.name = "Composite"
    return node


def _image_input(node):
    socket = node.inputs.get("Image")
    if socket is not None:
        return socket
    return node.inputs[0] if len(node.inputs) else None


def _image_output(node):
    for name in ("Image", "Color", "Result"):
        socket = node.outputs.get(name)
        if socket is not None:
            return socket
    return node.outputs[0] if len(node.outputs) else None


def _new_multiply_node(tree):
    try:
        node = tree.nodes.new("CompositorNodeMixRGB")
    except Exception:
        # Blender 5 compositor unification removes several legacy CompositorNode*
        # color nodes.  ShaderNodeMixRGB is valid in the unified compositor.
        node = tree.nodes.new("ShaderNodeMixRGB")
    node.blend_type = "MULTIPLY"
    if len(node.inputs):
        factor = node.inputs.get("Fac") or node.inputs.get("Factor") or node.inputs[0]
        try:
            factor.default_value = 1.0
        except Exception:
            pass
    return node


def _mix_color_inputs(node):
    # Old MixRGB exposes [Fac, Image, Image]; the unified ShaderNodeMixRGB uses
    # [Fac, Color1, Color2].  Prefer names and retain positional fallback.
    left = node.inputs.get("Color1") or node.inputs.get("A")
    right = node.inputs.get("Color2") or node.inputs.get("B")
    if left is None and len(node.inputs) > 1:
        left = node.inputs[1]
    if right is None and len(node.inputs) > 2:
        right = node.inputs[2]
    return left, right


def _restore_scanline_link(scene, *, restore_use_nodes: bool) -> int:
    tree = _scene_compositor_tree(scene, create=False)
    if tree is None:
        return 0
    mix = tree.nodes.get(_STYLE_SCANLINE_MIX_NODE)
    composite = _active_composite_node(scene, tree) if mix is not None else None
    if mix is not None and composite is not None:
        image_input = _image_input(composite)
        if image_input is not None:
            for link in list(image_input.links):
                tree.links.remove(link)
            if bool(mix.get("siig_had_upstream_link", False)):
                source_node = tree.nodes.get(str(mix.get("siig_upstream_node", "")))
                source_index = int(mix.get("siig_upstream_socket_index", -1))
                if source_node is not None and 0 <= source_index < len(source_node.outputs):
                    tree.links.new(source_node.outputs[source_index], image_input)
    removed = 0
    for name in (_STYLE_SCANLINE_MIX_NODE, _STYLE_SCANLINE_SCALE_NODE, _STYLE_SCANLINE_IMAGE_NODE):
        node = tree.nodes.get(name)
        if node is not None and bool(node.get(_STYLE_SCANLINE_MARKER, False)):
            tree.nodes.remove(node)
            removed += 1
    # Blender 3.6/4.x can restore the old use_nodes state. Blender 5 removed
    # use_nodes; a compositor group created by SIIG is left as a harmless empty
    # data block rather than deleting a tree the user may have edited meanwhile.
    if restore_use_nodes and hasattr(scene, "use_nodes") and "siig_style_nodes_were_enabled" in scene:
        was_enabled = bool(scene["siig_style_nodes_were_enabled"])
        if not was_enabled:
            try:
                scene.use_nodes = False
            except Exception:
                pass
        del scene["siig_style_nodes_were_enabled"]
    return removed


def _install_scanline_overlay(scene, *, spacing: int, thickness: int, opacity: float) -> None:
    legacy_use_nodes = bool(getattr(scene, "use_nodes", True))
    original_nodes_enabled = bool(scene.get("siig_style_nodes_were_enabled", legacy_use_nodes))
    tree = _scene_compositor_tree(scene, create=True)
    if tree is None:
        raise RuntimeError("Blender compositor is unavailable")
    _restore_scanline_link(scene, restore_use_nodes=False)
    if hasattr(scene, "use_nodes"):
        scene["siig_style_nodes_were_enabled"] = original_nodes_enabled
    tree = _scene_compositor_tree(scene, create=True)
    composite = _active_composite_node(scene, tree)
    image_input = _image_input(composite)
    if image_input is None:
        raise RuntimeError("Blender compositor output has no Image input")
    upstream = image_input.links[0].from_socket if image_input.links else None
    if upstream is None:
        render_layers = next((node for node in tree.nodes if getattr(node, "type", "") == "R_LAYERS"), None)
        if render_layers is None:
            render_layers = tree.nodes.new("CompositorNodeRLayers")
            render_layers.name = "Render Layers"
        upstream = _image_output(render_layers)
    for link in list(image_input.links):
        tree.links.remove(link)

    height = max(1, round(scene.render.resolution_y * scene.render.resolution_percentage / 100.0))
    scan_image = _scanline_image(height, spacing, thickness, opacity)
    image_node = tree.nodes.new("CompositorNodeImage")
    image_node.name = _STYLE_SCANLINE_IMAGE_NODE
    image_node.label = "SIIG scanline pattern"
    image_node.image = scan_image
    image_node[_STYLE_SCANLINE_MARKER] = True

    scale = tree.nodes.new("CompositorNodeScale")
    scale.name = _STYLE_SCANLINE_SCALE_NODE
    scale.label = "SIIG scanlines to render size"
    scale[_STYLE_SCANLINE_MARKER] = True
    if hasattr(scale, "space"):
        scale.space = "RENDER_SIZE"
    if hasattr(scale, "frame_method"):
        scale.frame_method = "STRETCH"

    mix = _new_multiply_node(tree)
    mix.name = _STYLE_SCANLINE_MIX_NODE
    mix.label = "SIIG post-process scanline overlay"
    mix[_STYLE_SCANLINE_MARKER] = True
    left, right = _mix_color_inputs(mix)
    if left is None or right is None:
        raise RuntimeError("Blender multiply node does not expose two color inputs")
    if upstream is not None:
        mix["siig_had_upstream_link"] = True
        mix["siig_upstream_node"] = upstream.node.name
        mix["siig_upstream_socket_index"] = list(upstream.node.outputs).index(upstream)
        tree.links.new(upstream, left)
    else:
        mix["siig_had_upstream_link"] = False
    image_out = _image_output(image_node)
    scale_in = _image_input(scale)
    scale_out = _image_output(scale)
    mix_out = _image_output(mix)
    if any(socket is None for socket in (image_out, scale_in, scale_out, mix_out)):
        raise RuntimeError("Blender compositor scanline nodes expose an unexpected socket layout")
    tree.links.new(image_out, scale_in)
    tree.links.new(scale_out, right)
    tree.links.new(mix_out, image_input)

    image_node.location = (composite.location.x - 520, composite.location.y - 180)
    scale.location = (composite.location.x - 330, composite.location.y - 180)
    mix.location = (composite.location.x - 160, composite.location.y)


def _apply_style_preview(context) -> dict:
    prefs = _preferences(context)
    if prefs is None:
        raise RuntimeError("SIIG add-on preferences are unavailable")
    if prefs.style_outline_enabled:
        outlines = _refresh_outline_previews(context, prefs.style_outline_thickness_percent)
    else:
        outlines = 0
        _remove_outline_previews()
    if prefs.style_scanlines_enabled:
        _install_scanline_overlay(
            context.scene,
            spacing=prefs.style_scanline_spacing,
            thickness=prefs.style_scanline_thickness,
            opacity=prefs.style_scanline_opacity,
        )
        scanlines = True
    else:
        _restore_scanline_link(context.scene, restore_use_nodes=True)
        scanlines = False
    return {"outlines": outlines, "scanlines": scanlines}


def _remove_style_preview(context) -> dict:
    outlines = _remove_outline_previews()
    nodes = _restore_scanline_link(context.scene, restore_use_nodes=True)
    return {"outlines": outlines, "nodes": nodes}


def _is_siig_assembly_master(obj: bpy.types.Object, candidates: set[bpy.types.Object] | None = None) -> bool:
    # Blender's glTF importer normally preserves node extras as custom properties.
    # This is the authoritative path for toolkit-generated assembled glTFs.
    if _custom_prop(obj, "siigAssemblyModel") is not None:
        return True
    if _custom_prop(obj, "siigAssemblyRole") is not None:
        return True

    # Fallback for Blender builds/import settings that do not preserve extras.  The
    # toolkit names each logical master "part" and its native GMX root/meshes
    # "part:...".  Restrict the fallback to Empty nodes with a matching child so an
    # ordinary native mesh is never mistaken for a part master merely because of its name.
    if getattr(obj, "type", None) != "EMPTY" or ":" in obj.name:
        return False
    allowed = candidates if candidates is not None else set(bpy.data.objects)
    prefix = obj.name + ":"
    return any(child in allowed and child.name.startswith(prefix) for child in obj.children)


def _part_members(master: bpy.types.Object, masters: set[bpy.types.Object], allowed: set[bpy.types.Object]) -> list[bpy.types.Object]:
    """Return one logical part without crossing into an attached child-part master."""
    members: list[bpy.types.Object] = []
    stack = [master]
    seen: set[bpy.types.Object] = set()
    while stack:
        obj = stack.pop()
        if obj in seen or obj not in allowed:
            continue
        seen.add(obj)
        members.append(obj)
        for child in obj.children:
            if child not in allowed:
                continue
            if child in masters and child is not master:
                continue
            stack.append(child)
    return members


def _collection_label(text: str, prefix: str = "SIIG_PART_") -> str:
    safe = "".join(ch if ch.isalnum() or ch in " _-." else "_" for ch in text).strip()
    if not safe:
        safe = "part"
    # Blender datablock names are friendlier when kept compact; duplicate names are
    # automatically disambiguated by Blender (.001, .002, ...).
    return (prefix + safe)[:63]


def _organize_siig_parts(
    context,
    objects: Iterable[bpy.types.Object],
    *,
    root_name: str = "SIIG_Assembly",
) -> dict:
    """Create one Blender collection per logical assembled-GMX part.

    The toolkit intentionally preserves native solid/face (_F) and outline/edge (_E)
    objects as separate meshes.  A Blender object eye therefore cannot represent the
    whole logical part.  Part collections solve that UI mismatch: hiding the collection
    hides its master, solid pass, outline pass and internal transform nodes together.
    """
    candidates = {obj for obj in objects if obj is not None}
    if not candidates:
        return {"masters": 0, "collections": 0, "objects": 0, "unassigned": 0}

    masters = {obj for obj in candidates if _is_siig_assembly_master(obj, candidates)}
    if not masters:
        return {"masters": 0, "collections": 0, "objects": 0, "unassigned": len(candidates)}

    root = bpy.data.collections.new(_collection_label(root_name, "SIIG_"))
    context.scene.collection.children.link(root)
    assigned: set[bpy.types.Object] = set()
    created_collections = 0

    # Stable order makes the Outliner predictable even when Blender's object datablock
    # iteration order differs across versions.
    for master in sorted(masters, key=lambda obj: obj.name.lower()):
        collection = bpy.data.collections.new(_collection_label(master.name))
        root.children.link(collection)
        members = _part_members(master, masters, candidates)
        _move_to_collection(members, collection)
        assigned.update(members)
        collection["siig_logical_part"] = master.name
        model = _custom_prop(master, "siigAssemblyModel")
        role = _custom_prop(master, "siigAssemblyRole")
        if model is not None:
            collection["siig_assembly_model"] = str(model)
        if role is not None:
            collection["siig_assembly_role"] = str(role)
        created_collections += 1

    leftovers = sorted(candidates - assigned, key=lambda obj: obj.name.lower())
    if leftovers:
        misc = bpy.data.collections.new(_collection_label("MISC"))
        root.children.link(misc)
        _move_to_collection(leftovers, misc)
        misc["siig_logical_part"] = "unassigned"
        created_collections += 1

    root["siig_part_collection_root"] = True
    root["siig_part_count"] = len(masters)
    return {
        "masters": len(masters),
        "collections": created_collections,
        "objects": len(candidates),
        "unassigned": len(leftovers),
        "root": root.name,
    }


def _import_gltf_assembly(context, source: Path, organize_parts: bool = True) -> tuple[int, dict]:
    before = set(bpy.data.objects)
    result = bpy.ops.import_scene.gltf(filepath=str(source))
    if "FINISHED" not in result:
        raise RuntimeError(f"Blender glTF importer returned {result}")
    created = _new_objects(before)
    info = {"masters": 0, "collections": 0, "objects": len(created), "unassigned": len(created)}
    if organize_parts and created:
        info = _organize_siig_parts(context, created, root_name=source.stem)
    for obj in created:
        obj["siig_source_assembly"] = str(source)
    prefs = _preferences(context)
    if created and prefs and prefs.hide_native_outlines_after_import:
        _set_native_outline_visibility(created, False)
    return len(created), info


def _import_one(context, source: Path, flip_v: bool, texture_root: str, group_collection: bool, visual_pass: str = "solid") -> tuple[int, dict]:
    toolkit = _load_toolkit(context)
    roots = [source.parent]
    if texture_root:
        roots.append(Path(bpy.path.abspath(texture_root)))
    before = set(bpy.data.objects)
    with tempfile.TemporaryDirectory(prefix="siig_blender_") as temp_dir:
        output = Path(temp_dir)
        metadata = toolkit.export_gmx_gltf_file(
            source,
            output,
            flip_v=flip_v,
            texture_roots=tuple(roots),
            visual_pass=visual_pass,
        )
        gltf = output / f"{source.stem}.gltf"
        if not gltf.is_file():
            raise RuntimeError(f"SIIG exporter did not create {gltf.name}")
        result = bpy.ops.import_scene.gltf(filepath=str(gltf))
        if "FINISHED" not in result:
            raise RuntimeError(f"Blender glTF importer returned {result}")
    created = _new_objects(before)
    if group_collection and created:
        collection = bpy.data.collections.new(f"SIIG_{source.stem}")
        context.scene.collection.children.link(collection)
        _move_to_collection(created, collection)
    for obj in created:
        obj["siig_source_gmx"] = str(source)
        obj["siig_toolkit_version"] = str(getattr(toolkit, "TOOLKIT_VERSION", "unknown"))
    prefs = _preferences(context)
    if created and prefs and prefs.hide_native_outlines_after_import:
        _set_native_outline_visibility(created, False)
    return len(created), metadata


class SIIGAddonPreferences(AddonPreferences):
    bl_idname = __package__

    toolkit_path: StringProperty(
        name="Toolkit folder",
        description="Folder containing siig_toolkit.py, or the script itself",
        subtype="DIR_PATH",
    )
    default_texture_root: StringProperty(
        name="Default texture root",
        description="Optional folder searched recursively for textures referenced by GMX files",
        subtype="DIR_PATH",
    )
    default_visual_pass: EnumProperty(
        name="Raw GMX visual pass",
        description="Solid-only is the editing-first default; choose Native solid + outline when you need the preserved _E edge pass",
        items=_VISUAL_PASS_ITEMS,
        default="solid",
    )
    hide_native_outlines_after_import: BoolProperty(
        name="Hide native _E outlines after assembly import",
        description="Hide imported native edge-pass objects by default so assembled models do not appear with black viewport outlines; the objects remain recoverable",
        default=True,
    )
    style_auto_apply_after_import: BoolProperty(
        name="Auto-apply SIIG Style Preview after import",
        description="Refresh optional white outline curves and scanlines after SIIG imports",
        default=False,
    )
    style_outline_enabled: BoolProperty(
        name="White native outlines",
        description="Render native GMX _E line meshes as non-destructive white emissive curve previews",
        default=False,
    )
    style_outline_thickness_percent: FloatProperty(
        name="Outline thickness (%)",
        description="Curve radius as a percentage of each native outline object's local bounding-box diagonal",
        default=0.18, min=0.01, max=5.0, precision=3,
    )
    style_scanlines_enabled: BoolProperty(
        name="Post-process scanlines",
        description="Multiply a horizontal scanline pattern over the compositor final image; supports legacy Scene.node_tree and Blender 5 compositing_node_group",
        default=False,
    )
    style_scanline_spacing: IntProperty(
        name="Scanline spacing",
        description="Distance between scanline starts in output pixels",
        default=4, min=2, max=64,
    )
    style_scanline_thickness: IntProperty(
        name="Scanline thickness",
        description="Darkened rows per scanline; values are clamped below the spacing",
        default=1, min=1, max=32,
    )
    style_scanline_opacity: FloatProperty(
        name="Scanline strength",
        description="Amount that scanline rows darken the final compositor image",
        default=0.22, min=0.0, max=0.95, subtype="FACTOR",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "toolkit_path")
        layout.prop(self, "default_texture_root")
        layout.separator()
        layout.prop(self, "default_visual_pass")
        layout.prop(self, "hide_native_outlines_after_import")
        layout.prop(self, "style_auto_apply_after_import")
        layout.prop(self, "style_outline_enabled")
        layout.prop(self, "style_outline_thickness_percent")
        layout.prop(self, "style_scanlines_enabled")
        layout.prop(self, "style_scanline_spacing")
        layout.prop(self, "style_scanline_thickness")
        layout.prop(self, "style_scanline_opacity")
        layout.label(text="The add-on calls the toolkit's verified GMX to glTF exporter locally.")


class SIIG_OT_import_gmx(Operator, ImportHelper):
    bl_idname = "import_scene.siig_gmx"
    bl_label = "Import SIIG GMX"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".gmx"
    filter_glob: StringProperty(default="*.gmx;*.GMX", options={"HIDDEN"})
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")
    flip_v: BoolProperty(name="Flip texture V", default=False)
    group_collection: BoolProperty(name="Collection per GMX", default=True)
    visual_pass: EnumProperty(name="Visual pass", items=_VISUAL_PASS_ITEMS, default="solid")
    texture_root: StringProperty(name="Texture root", subtype="DIR_PATH")

    def invoke(self, context, event):
        prefs = _preferences(context)
        if prefs and prefs.default_texture_root and not self.texture_root:
            self.texture_root = prefs.default_texture_root
        if prefs:
            self.visual_pass = prefs.default_visual_pass
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        paths = [Path(self.directory) / item.name for item in self.files] if self.files else [Path(self.filepath)]
        imported_objects = 0
        failures = []
        for path in paths:
            try:
                count, metadata = _import_one(context, path.resolve(), self.flip_v, self.texture_root, self.group_collection, self.visual_pass)
                imported_objects += count
                missing = metadata.get("missing_textures", []) if isinstance(metadata, dict) else []
                if missing:
                    self.report({"WARNING"}, f"{path.name}: {len(missing)} referenced texture(s) not found")
            except Exception as exc:
                failures.append(f"{path.name}: {exc}")
        prefs = _preferences(context)
        if imported_objects and prefs and prefs.style_auto_apply_after_import:
            try:
                _apply_style_preview(context)
            except Exception as exc:
                self.report({"WARNING"}, f"Imported models, but SIIG Style Preview could not refresh: {exc}")
        if failures:
            self.report({"ERROR"}, " | ".join(failures[:4]))
            return {"CANCELLED"} if imported_objects == 0 else {"FINISHED"}
        self.report({"INFO"}, f"Imported {len(paths)} GMX file(s), {imported_objects} Blender object(s)")
        return {"FINISHED"}


class SIIG_OT_import_gmx_folder(Operator):
    bl_idname = "import_scene.siig_gmx_folder"
    bl_label = "Import GMX Folder"
    bl_options = {"REGISTER", "UNDO"}

    directory: StringProperty(name="Folder", subtype="DIR_PATH")
    recursive: BoolProperty(name="Recursive", default=True)
    flip_v: BoolProperty(name="Flip texture V", default=False)
    group_collection: BoolProperty(name="Collection per GMX", default=True)
    visual_pass: EnumProperty(name="Visual pass", items=_VISUAL_PASS_ITEMS, default="solid")
    texture_root: StringProperty(name="Texture root", subtype="DIR_PATH")
    max_files: IntProperty(name="Maximum files", default=256, min=1, max=10000)

    def invoke(self, context, event):
        prefs = _preferences(context)
        if prefs and prefs.default_texture_root and not self.texture_root:
            self.texture_root = prefs.default_texture_root
        if prefs:
            self.visual_pass = prefs.default_visual_pass
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        root = Path(bpy.path.abspath(self.directory))
        iterator = root.rglob("*.gmx") if self.recursive else root.glob("*.gmx")
        paths = sorted(iterator, key=lambda p: p.as_posix().lower())
        if not paths:
            self.report({"ERROR"}, "No .gmx files were found")
            return {"CANCELLED"}
        if len(paths) > self.max_files:
            self.report({"ERROR"}, f"Found {len(paths)} GMX files; raise Maximum files to continue")
            return {"CANCELLED"}
        imported = 0
        failures = []
        for path in paths:
            try:
                count, _metadata = _import_one(context, path, self.flip_v, self.texture_root, self.group_collection, self.visual_pass)
                imported += count
            except Exception as exc:
                failures.append(f"{path.name}: {exc}")
        prefs = _preferences(context)
        if imported and prefs and prefs.style_auto_apply_after_import:
            try:
                _apply_style_preview(context)
            except Exception as exc:
                self.report({"WARNING"}, f"Imported models, but SIIG Style Preview could not refresh: {exc}")
        if failures:
            self.report({"WARNING"}, f"Imported {len(paths)-len(failures)}/{len(paths)} files; first error: {failures[0]}")
        else:
            self.report({"INFO"}, f"Imported {len(paths)} files, {imported} objects")
        return {"FINISHED"} if imported else {"CANCELLED"}


class SIIG_OT_import_assembly(Operator, ImportHelper):
    bl_idname = "import_scene.siig_assembly"
    bl_label = "Import SIIG Assembly"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".gltf"
    filter_glob: StringProperty(default="*.gltf;*.glb;*.GLTF;*.GLB", options={"HIDDEN"})
    organize_parts: BoolProperty(
        name="Logical part collections",
        description="Put each SIIG assembly master and its native solid/outline descendants in one hideable Blender collection",
        default=True,
    )

    def execute(self, context):
        source = Path(self.filepath).resolve()
        if source.suffix.lower() not in {".gltf", ".glb"}:
            self.report({"ERROR"}, "Choose a .gltf or .glb SIIG assembly")
            return {"CANCELLED"}
        try:
            count, info = _import_gltf_assembly(context, source, self.organize_parts)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        prefs = _preferences(context)
        if count and prefs and prefs.style_auto_apply_after_import:
            try:
                _apply_style_preview(context)
            except Exception as exc:
                self.report({"WARNING"}, f"Imported assembly, but SIIG Style Preview could not refresh: {exc}")
        if self.organize_parts and not info.get("masters"):
            self.report({"WARNING"}, f"Imported {count} object(s), but no SIIG logical assembly masters were detected")
        else:
            self.report({"INFO"}, f"Imported {count} object(s); organized {info.get('masters', 0)} logical SIIG part(s)")
        return {"FINISHED"}


class SIIG_OT_organize_parts(Operator):
    bl_idname = "object.siig_organize_parts"
    bl_label = "Organize SIIG Part Collections"
    bl_description = "Group each assembled SIIG logical part so the Outliner collection eye hides its solid and outline objects together"
    bl_options = {"REGISTER", "UNDO"}

    selected_only: BoolProperty(
        name="Selected objects only",
        description="Organize only selected objects; disable to scan the current scene",
        default=False,
    )

    def execute(self, context):
        objects = list(context.selected_objects) if self.selected_only else list(context.scene.objects)
        info = _organize_siig_parts(context, objects, root_name="Organized_Parts")
        if not info.get("masters"):
            self.report({"WARNING"}, "No SIIG logical assembly masters were found. Import a toolkit-generated assembled glTF first.")
            return {"CANCELLED"}
        self.report({"INFO"}, f"Organized {info['masters']} SIIG logical part(s) into {info['collections']} collection(s)")
        return {"FINISHED"}


class SIIG_OT_hide_native_outlines(Operator):
    bl_idname = "object.siig_hide_native_outlines"
    bl_label = "Hide Native _E Outlines"
    bl_description = "Hide preserved native SIIG edge-pass objects without deleting them"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        count = _set_native_outline_visibility(context.scene.objects, False)
        self.report({"INFO"}, f"Hidden {count} native SIIG outline object(s)")
        return {"FINISHED"}


class SIIG_OT_show_native_outlines(Operator):
    bl_idname = "object.siig_show_native_outlines"
    bl_label = "Show Native _E Outlines"
    bl_description = "Show preserved native SIIG edge-pass objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        count = _set_native_outline_visibility(context.scene.objects, True)
        self.report({"INFO"}, f"Shown {count} native SIIG outline object(s)")
        return {"FINISHED"}


class SIIG_OT_apply_style_preview(Operator):
    bl_idname = "scene.siig_apply_style_preview"
    bl_label = "Apply / Refresh SIIG Style Preview"
    bl_description = "Refresh white native outline previews and the compositor scanline overlay using the current add-on settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            info = _apply_style_preview(context)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        scanline_text = "scanlines on" if info.get("scanlines") else "scanlines off"
        self.report({"INFO"}, f"SIIG Style Preview: {info.get('outlines', 0)} outline object(s), {scanline_text}")
        return {"FINISHED"}


class SIIG_OT_remove_style_preview(Operator):
    bl_idname = "scene.siig_remove_style_preview"
    bl_label = "Remove SIIG Style Preview"
    bl_description = "Remove generated outline preview curves and restore the compositor link that existed before the SIIG scanline overlay"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            info = _remove_style_preview(context)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Removed {info.get('outlines', 0)} SIIG outline preview object(s)")
        return {"FINISHED"}


class SIIG_PT_tools(Panel):
    bl_label = "SIIG Asset Toolkit"
    bl_idname = "SIIG_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SIIG"

    def draw(self, context):
        layout = self.layout
        layout.operator(SIIG_OT_import_gmx.bl_idname, icon="IMPORT")
        layout.operator(SIIG_OT_import_gmx_folder.bl_idname, icon="FILE_FOLDER")
        layout.separator()
        layout.operator(SIIG_OT_import_assembly.bl_idname, icon="OUTLINER_COLLECTION")
        layout.operator(SIIG_OT_organize_parts.bl_idname, icon="GROUP")
        box = layout.box()
        box.label(text="Native outline visibility")
        row = box.row(align=True)
        row.operator(SIIG_OT_hide_native_outlines.bl_idname, icon="HIDE_ON")
        row.operator(SIIG_OT_show_native_outlines.bl_idname, icon="HIDE_OFF")
        box.label(text="Raw GMX defaults to Solid only for editing.")
        box.label(text="Native _E geometry is preserved when requested.")
        prefs = _preferences(context)
        style = layout.box()
        style.label(text="SIIG Style Preview")
        if prefs is not None:
            style.prop(prefs, "default_visual_pass")
            style.prop(prefs, "hide_native_outlines_after_import")
            style.prop(prefs, "style_outline_enabled")
            if prefs.style_outline_enabled:
                style.prop(prefs, "style_outline_thickness_percent")
            style.prop(prefs, "style_scanlines_enabled")
            if prefs.style_scanlines_enabled:
                row = style.row(align=True)
                row.prop(prefs, "style_scanline_spacing")
                row.prop(prefs, "style_scanline_thickness")
                style.prop(prefs, "style_scanline_opacity")
            style.prop(prefs, "style_auto_apply_after_import")
            style.operator(SIIG_OT_apply_style_preview.bl_idname, icon="FILE_REFRESH")
            style.operator(SIIG_OT_remove_style_preview.bl_idname, icon="TRASH")
            style.label(text="Scanlines are a final compositor overlay.")
            style.label(text="Refresh after changing render resolution.")
        else:
            style.label(text="Enable the add-on to configure style preview.", icon="ERROR")
        try:
            path = _find_toolkit(context)
            layout.label(text=f"Toolkit: {path.parent.name}", icon="CHECKMARK")
        except Exception:
            layout.label(text="Set toolkit path in Add-on Preferences", icon="ERROR")


def _menu_import(self, context):
    self.layout.operator(SIIG_OT_import_gmx.bl_idname, text="Space Invaders Infinity Gene (.gmx)")
    self.layout.operator(SIIG_OT_import_assembly.bl_idname, text="SIIG Assembled Model (.gltf/.glb)")


_CLASSES = (
    SIIGAddonPreferences,
    SIIG_OT_import_gmx,
    SIIG_OT_import_gmx_folder,
    SIIG_OT_import_assembly,
    SIIG_OT_organize_parts,
    SIIG_OT_hide_native_outlines,
    SIIG_OT_show_native_outlines,
    SIIG_OT_apply_style_preview,
    SIIG_OT_remove_style_preview,
    SIIG_PT_tools,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(_menu_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(_menu_import)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
