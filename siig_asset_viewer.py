#!/usr/bin/env python3
"""Offline linked-data asset browser for SIIG toolkit outputs.

The generated viewer makes no network requests. Its main HTML remains small because
inventory data, text/model payloads, and thumbnails are written as sibling files and
loaded only when needed. Relative file links continue to work under ``file://``;
``serve`` remains available for browsers with stricter local-file policies.
"""
from __future__ import annotations

import colorsys
import csv
import fnmatch
import hashlib
import html
import json
import math
import mimetypes
import os
import re
import struct
import sys
import wave
import webbrowser
from collections import defaultdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import parse_qs, quote, urlparse

VIEWER_VERSION = "2.2.1"
TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".ini", ".cfg", ".log",
    ".obj", ".mtl", ".fnt", ".glsl", ".hlsl", ".bat", ".ps1",
    ".nut", ".py", ".pyw", ".c", ".h", ".cpp", ".hpp", ".cc", ".hh",
    ".js", ".mjs", ".css", ".html", ".htm", ".yaml", ".yml", ".toml",
    ".sh", ".cmd", ".cmake", ".properties",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
MODEL_EXTENSIONS = {".gltf", ".glb", ".obj", ".gmx"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".wma", ".xma", ".at3"}
BROWSER_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
ARCHIVE_EXTENSIONS = {".zip", ".gz", ".pkg", ".bin", ".bbx", ".sdat"}
DATA_EXTENSIONS = {".map", ".dat", ".col", ".anm", ".tex", ".crp", ".xwb", ".xsb", ".bnk"}
PREVIEW_SUFFIX_RE = re.compile(
    r"(?:\.atlas)?\.(?:composite|layer\d+)$|_atlas$|_preview$|_thumbnail$",
    re.IGNORECASE,
)

ENTITY_IDENTITY_TABLE = Path(__file__).resolve().parent / "reference" / "tables" / "ENTITY_MODEL_IDENTITIES_DEV24.csv"
_ENTITY_IDENTITY_CACHE: Optional[list[dict[str, str]]] = None


def _entity_identity_catalog() -> list[dict[str, str]]:
    """Load project-owner-friendly GMX identities without treating them as internal names.

    The table deliberately carries evidence/status fields.  In particular, speculative
    ``est_*`` effect guesses remain searchable but are never silently promoted to hard
    runtime ownership.  Keeping this in a source table also lets researchers correct a
    label without editing browser JavaScript.
    """
    global _ENTITY_IDENTITY_CACHE
    if _ENTITY_IDENTITY_CACHE is not None:
        return _ENTITY_IDENTITY_CACHE
    rows: list[dict[str, str]] = []
    try:
        with ENTITY_IDENTITY_TABLE.open(newline="", encoding="utf-8-sig") as handle:
            for raw in csv.DictReader(handle):
                pattern = str(raw.get("model_stem_pattern") or "").strip().lower()
                label = str(raw.get("display_name") or "").strip()
                if not pattern or not label:
                    continue
                row = {str(k): str(v or "").strip() for k, v in raw.items() if k is not None}
                row["model_stem_pattern"] = pattern
                rows.append(row)
    except (OSError, csv.Error):
        rows = []
    _ENTITY_IDENTITY_CACHE = rows
    return rows


def _entity_identity(path: Path) -> Optional[dict[str, str]]:
    if path.suffix.lower() not in {".gmx", ".gltf", ".glb", ".obj"}:
        return None
    stem = path.stem.lower()
    # More specific literal patterns should win over wildcard family rows if the
    # table ever grows an exception.  Current rows are non-overlapping by design.
    rows = sorted(_entity_identity_catalog(), key=lambda row: ("*" in row["model_stem_pattern"], -len(row["model_stem_pattern"])))
    for row in rows:
        if fnmatch.fnmatchcase(stem, row["model_stem_pattern"]):
            return dict(row)
    return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _stable_id(relative: str) -> str:
    return hashlib.sha1(relative.encode("utf-8", errors="surrogatepass")).hexdigest()[:20]


def _kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in MODEL_EXTENSIONS:
        return "model"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in DATA_EXTENSIONS:
        return "data"
    if ext in ARCHIVE_EXTENSIONS:
        return "archive"
    return "other"


def _png_size(data: bytes) -> Optional[tuple[int, int]]:
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return struct.unpack_from(">II", data, 16)
    return None


def _jpeg_size(data: bytes) -> Optional[tuple[int, int]]:
    if not data.startswith(b"\xFF\xD8"):
        return None
    offset = 2
    while offset + 9 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in (0xD8, 0xD9):
            continue
        if offset + 2 > len(data):
            break
        length = int.from_bytes(data[offset:offset + 2], "big")
        if length < 2 or offset + length > len(data):
            break
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if length >= 7:
                return int.from_bytes(data[offset + 3:offset + 5], "big"), int.from_bytes(data[offset + 5:offset + 7], "big")
            break
        offset += length
    return None


def _image_meta(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = handle.read(512 * 1024)
    except OSError:
        return {}
    size = _png_size(data) or _jpeg_size(data)
    return {"width": size[0], "height": size[1]} if size else {}


def _text_preview(path: Path, limit: int) -> str:
    if limit <= 0:
        return ""
    try:
        with path.open("rb") as handle:
            raw = handle.read(limit)
    except OSError:
        return ""
    if b"\x00" in raw[:2048]:
        return ""
    return raw.decode("utf-8", errors="replace")


def _wav_meta(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate()
            return {
                "channels": handle.getnchannels(),
                "sample_rate": rate,
                "sample_width_bits": handle.getsampwidth() * 8,
                "frames": frames,
                "duration_seconds": round(frames / rate, 4) if rate else 0,
            }
    except (OSError, wave.Error):
        return {}


def _safe_child(root: Path, candidate: Path) -> Optional[Path]:
    try:
        resolved_root = root.resolve()
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
        return resolved
    except (OSError, ValueError):
        return None


def _gltf_summary(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, {}
    meshes = document.get("meshes", []) if isinstance(document, dict) else []
    nodes = document.get("nodes", []) if isinstance(document, dict) else []
    materials = document.get("materials", []) if isinstance(document, dict) else []
    animations = document.get("animations", []) if isinstance(document, dict) else []
    primitives = sum(len(mesh.get("primitives", [])) for mesh in meshes if isinstance(mesh, dict))
    metadata = {
        "meshes": len(meshes),
        "primitives": primitives,
        "nodes": len(nodes),
        "materials": len(materials),
        "animations": len(animations),
    }
    return metadata, _gltf_wireframe(path, document)


def _component_format(component_type: int) -> Optional[tuple[str, int]]:
    return {
        5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
        5125: ("I", 4), 5126: ("f", 4),
    }.get(component_type)


def _type_components(value: str) -> int:
    return {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}.get(value, 0)


def _load_gltf_buffer(path: Path, document: dict[str, Any], index: int) -> Optional[bytes]:
    buffers = document.get("buffers", [])
    if not isinstance(buffers, list) or index < 0 or index >= len(buffers) or not isinstance(buffers[index], dict):
        return None
    uri = buffers[index].get("uri")
    if not isinstance(uri, str):
        return None
    if uri.startswith("data:"):
        try:
            import base64
            return base64.b64decode(uri.split(",", 1)[1], validate=True)
        except Exception:
            return None
    target = _safe_child(path.parent, path.parent / uri)
    if target is None or not target.is_file() or target.stat().st_size > 128 * 1024 * 1024:
        return None
    try:
        return target.read_bytes()
    except OSError:
        return None


def _read_accessor(path: Path, document: dict[str, Any], accessor_index: int, max_items: int) -> list[tuple[float, ...]]:
    accessors = document.get("accessors", [])
    views = document.get("bufferViews", [])
    if not isinstance(accessors, list) or accessor_index < 0 or accessor_index >= len(accessors):
        return []
    accessor = accessors[accessor_index]
    if not isinstance(accessor, dict) or "sparse" in accessor:
        return []
    view_index = accessor.get("bufferView")
    if not isinstance(view_index, int) or not isinstance(views, list) or view_index < 0 or view_index >= len(views):
        return []
    view = views[view_index]
    if not isinstance(view, dict):
        return []
    component = _component_format(int(accessor.get("componentType", 0)))
    components = _type_components(str(accessor.get("type", "")))
    count = min(int(accessor.get("count", 0)), max_items)
    if component is None or components < 1 or count < 1:
        return []
    fmt, component_size = component
    payload = _load_gltf_buffer(path, document, int(view.get("buffer", -1)))
    if payload is None:
        return []
    element_size = component_size * components
    stride = int(view.get("byteStride", element_size))
    if stride < element_size:
        return []
    offset = int(view.get("byteOffset", 0)) + int(accessor.get("byteOffset", 0))
    output: list[tuple[float, ...]] = []
    unpack = struct.Struct("<" + fmt * components)
    for index in range(count):
        position = offset + index * stride
        if position < 0 or position + element_size > len(payload):
            break
        output.append(tuple(float(value) for value in unpack.unpack_from(payload, position)))
    return output


def _gltf_wireframe(path: Path, document: dict[str, Any]) -> dict[str, Any]:
    meshes = document.get("meshes", [])
    if not isinstance(meshes, list):
        return {}
    points: list[list[float]] = []
    edges: list[list[int]] = []
    max_points = 3000
    max_edges = 6000
    for mesh in meshes:
        if not isinstance(mesh, dict):
            continue
        for primitive in mesh.get("primitives", []):
            if not isinstance(primitive, dict):
                continue
            attributes = primitive.get("attributes", {})
            position_accessor = attributes.get("POSITION") if isinstance(attributes, dict) else None
            if not isinstance(position_accessor, int):
                continue
            local = _read_accessor(path, document, position_accessor, max_points - len(points))
            if not local:
                continue
            base = len(points)
            for value in local:
                if len(value) >= 3:
                    points.append([round(value[0], 6), round(value[1], 6), round(value[2], 6)])
            indices_accessor = primitive.get("indices")
            if isinstance(indices_accessor, int):
                raw_indices = _read_accessor(path, document, indices_accessor, max_edges * 3)
                indices = [int(item[0]) for item in raw_indices if item]
            else:
                indices = list(range(len(local)))
            mode = int(primitive.get("mode", 4))
            if mode == 4:
                for i in range(0, len(indices) - 2, 3):
                    tri = indices[i:i + 3]
                    if max(tri, default=-1) >= len(local) or min(tri, default=0) < 0:
                        continue
                    edges.extend([[base + tri[0], base + tri[1]], [base + tri[1], base + tri[2]], [base + tri[2], base + tri[0]]])
                    if len(edges) >= max_edges:
                        break
            elif mode == 1:
                for i in range(0, len(indices) - 1, 2):
                    a, b = indices[i], indices[i + 1]
                    if 0 <= a < len(local) and 0 <= b < len(local):
                        edges.append([base + a, base + b])
                    if len(edges) >= max_edges:
                        break
            if len(points) >= max_points or len(edges) >= max_edges:
                break
        if len(points) >= max_points or len(edges) >= max_edges:
            break
    if not points:
        return {}
    mins = [min(point[i] for point in points) for i in range(3)]
    maxs = [max(point[i] for point in points) for i in range(3)]
    return {"points": points, "edges": edges[:max_edges], "min": mins, "max": maxs}



def _toolkit_core() -> Any:
    candidate = sys.modules.get("siig_toolkit")
    if candidate is not None and hasattr(candidate, "parse_gmx_chunks"):
        return candidate
    main = sys.modules.get("__main__")
    if main is not None and hasattr(main, "parse_gmx_chunks"):
        return main
    try:
        import siig_toolkit as core
        return core
    except Exception:
        return None


def _gmx_summary(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    core = _toolkit_core()
    if core is None:
        return {}, {}
    try:
        chunks = core.parse_gmx_chunks(path.read_bytes())
        arrays = {item.array_index: item for item in (core.parse_gmx_array(chunk) for chunk in chunks if chunk.tag == "ARRY")}
        meshes = [core.parse_gmx_mesh(chunk) for chunk in chunks if chunk.tag == "MESH"]
    except Exception:
        return {}, {}
    metadata = {
        "meshes": len(meshes),
        "primitives": len(meshes),
        "nodes": sum(1 for chunk in chunks if chunk.tag == "BONE"),
        "materials": sum(1 for chunk in chunks if chunk.tag == "MTRL"),
        "animations": sum(1 for chunk in chunks if chunk.tag == "ANIM"),
    }
    points: list[list[float]] = []
    edges: list[list[int]] = []
    max_points = 2200
    max_edges = 4400
    for mesh in meshes:
        referenced = [arrays[index] for index in mesh.array_refs if index in arrays]
        position = next((item for item in referenced if item.semantic == "IN.position"), None)
        indices = next((item for item in referenced if item.gl_type == 0x1403 and item.components == 1), None)
        if position is None or indices is None:
            continue
        room = max_points - len(points)
        if room <= 0:
            break
        local_values = position.values[:room]
        base = len(points)
        for value in local_values:
            if len(value) >= 3:
                points.append([round(float(value[0]), 6), round(float(value[1]), 6), round(float(value[2]), 6)])
        raw_indices = [int(value[0]) for value in indices.values]
        if mesh.primitive_mode == 4:
            for index in range(0, len(raw_indices) - 2, 3):
                triangle = raw_indices[index:index + 3]
                if min(triangle) < 0 or max(triangle) >= len(local_values):
                    continue
                edges.extend([[base + triangle[0], base + triangle[1]], [base + triangle[1], base + triangle[2]], [base + triangle[2], base + triangle[0]]])
                if len(edges) >= max_edges:
                    break
        elif mesh.primitive_mode == 1:
            for index in range(0, len(raw_indices) - 1, 2):
                a, b = raw_indices[index:index + 2]
                if 0 <= a < len(local_values) and 0 <= b < len(local_values):
                    edges.append([base + a, base + b])
                if len(edges) >= max_edges:
                    break
        if len(edges) >= max_edges:
            break
    if not points:
        return metadata, {}
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return metadata, {"points": points, "edges": edges[:max_edges], "min": mins, "max": maxs}


def _obj_summary(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    points: list[list[float]] = []
    edges: list[list[int]] = []
    face_count = 0
    line_count = 0
    max_points = 3000
    max_edges = 6000
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if line.startswith("v ") and len(points) < max_points:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            points.append([float(parts[1]), float(parts[2]), float(parts[3])])
                        except ValueError:
                            pass
                elif line.startswith("f "):
                    face_count += 1
                    refs: list[int] = []
                    for token in line.split()[1:]:
                        try:
                            value = int(token.split("/", 1)[0])
                            refs.append(value - 1 if value > 0 else len(points) + value)
                        except ValueError:
                            pass
                    for index in range(len(refs)):
                        a, b = refs[index], refs[(index + 1) % len(refs)]
                        if 0 <= a < len(points) and 0 <= b < len(points):
                            edges.append([a, b])
                            if len(edges) >= max_edges:
                                break
                elif line.startswith("l "):
                    line_count += 1
                    refs = []
                    for token in line.split()[1:]:
                        try:
                            value = int(token.split("/", 1)[0])
                            refs.append(value - 1 if value > 0 else len(points) + value)
                        except ValueError:
                            pass
                    for a, b in zip(refs, refs[1:]):
                        if 0 <= a < len(points) and 0 <= b < len(points):
                            edges.append([a, b])
                            if len(edges) >= max_edges:
                                break
                if len(edges) >= max_edges and len(points) >= max_points:
                    break
    except OSError:
        return {}, {}
    metadata = {"vertices": len(points), "faces": face_count, "lines": line_count}
    if not points:
        return metadata, {}
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return metadata, {"points": points, "edges": edges[:max_edges], "min": mins, "max": maxs}


def _model_summary(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    extension = path.suffix.lower()
    if extension == ".gltf":
        return _gltf_summary(path)
    if extension == ".gmx":
        return _gmx_summary(path)
    if extension == ".obj":
        return _obj_summary(path)
    return {}, {}

def _human_bytes(value: int) -> str:
    number = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if number < 1024 or unit == "TiB":
            return f"{number:.0f} {unit}" if unit == "B" else f"{number:.1f} {unit}"
        number /= 1024
    return str(value)


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except (OSError, ValueError):
        return False


def _walk_files(root: Path, excluded_files: set[Path], excluded_dirs: set[Path]) -> Iterable[Path]:
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not path.is_file():
            continue
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in excluded_files or any(_is_within(resolved, directory) for directory in excluded_dirs):
            continue
        if any(part in {".git", "__pycache__"} for part in path.parts):
            continue
        if path.name.endswith(".siig-part"):
            continue
        yield path


def _relative_url(path: Path, html_path: Path) -> str:
    return quote(os.path.relpath(path, html_path.parent).replace(os.sep, "/"), safe="/._-")


def _preview_keys(path: Path) -> set[str]:
    name = path.name.lower()
    base = name
    if path.suffix.lower() in IMAGE_EXTENSIONS:
        base = name[:-len(path.suffix)]
    keys = {base, Path(base).stem.lower(), path.stem.lower(), name}
    current = base
    while True:
        stripped = PREVIEW_SUFFIX_RE.sub("", current)
        if stripped == current:
            break
        keys.add(stripped)
        keys.add(Path(stripped).stem.lower())
        current = stripped
    if current.endswith(".tex") or current.endswith(".map") or current.endswith(".col"):
        keys.add(Path(current).stem.lower())
    return {key for key in keys if key}


def _candidate_score(path: Path) -> tuple[int, int, str]:
    name = path.name.lower()
    preferred = 0
    if "composite" in name:
        preferred -= 40
    if "atlas" in name:
        preferred -= 20
    if "layer0" in name:
        preferred -= 10
    return preferred, path.stat().st_size, name


def _build_image_lookup(images: list[Path], root: Path) -> tuple[dict[tuple[str, str], list[Path]], dict[str, list[Path]]]:
    local: dict[tuple[str, str], list[Path]] = defaultdict(list)
    global_lookup: dict[str, list[Path]] = defaultdict(list)
    for path in images:
        parent = path.parent.relative_to(root).as_posix().lower()
        for key in _preview_keys(path):
            local[(parent, key)].append(path)
            global_lookup[key].append(path)
    return local, global_lookup


def _find_related(path: Path, root: Path, local: dict[tuple[str, str], list[Path]], global_lookup: dict[str, list[Path]]) -> Optional[Path]:
    parent = path.parent.relative_to(root).as_posix().lower()
    candidates: list[Path] = []
    for key in _preview_keys(path):
        candidates.extend(local.get((parent, key), []))
    unique = {candidate.resolve(): candidate for candidate in candidates if candidate != path}
    if unique:
        return sorted(unique.values(), key=_candidate_score)[0]
    global_candidates: dict[Path, Path] = {}
    for key in _preview_keys(path):
        values = global_lookup.get(key, [])
        if len(values) == 1 and values[0] != path:
            global_candidates[values[0].resolve()] = values[0]
    if global_candidates:
        return sorted(global_candidates.values(), key=_candidate_score)[0]
    return None


def _write_payload_shard(path: Path, payloads: dict[str, dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payloads, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    text = (
        "window.SIIG_VIEWER_PAYLOADS=window.SIIG_VIEWER_PAYLOADS||{};"
        f"Object.assign(window.SIIG_VIEWER_PAYLOADS,{encoded});\n"
    )
    path.write_text(text, encoding="utf-8", newline="\n")
    return path.stat().st_size


def _project_wireframe(wireframe: dict[str, Any], width: int = 320, height: int = 180) -> tuple[list[tuple[float, float]], list[list[int]]]:
    points = wireframe.get("points", [])
    edges = wireframe.get("edges", [])
    if not points:
        return [], []
    mins = wireframe.get("min", [min(p[i] for p in points) for i in range(3)])
    maxs = wireframe.get("max", [max(p[i] for p in points) for i in range(3)])
    center = [(mins[i] + maxs[i]) / 2 for i in range(3)]
    extent = max(maxs[i] - mins[i] for i in range(3)) or 1.0
    ax, ay = -0.35, 0.55
    sx, cx, sy, cy = math.sin(ax), math.cos(ax), math.sin(ay), math.cos(ay)
    scale = min(width, height) * 0.72 / extent
    projected: list[tuple[float, float]] = []
    for point in points:
        x, y, z = point[0] - center[0], point[1] - center[1], point[2] - center[2]
        x1 = x * cy + z * sy
        z1 = -x * sy + z * cy
        y1 = y * cx - z1 * sx
        projected.append((width / 2 + x1 * scale, height / 2 - y1 * scale))
    return projected, edges


def _write_wireframe_svg(path: Path, wireframe: dict[str, Any], max_edges: int = 500) -> bool:
    projected, edges = _project_wireframe(wireframe)
    if not projected:
        return False
    if edges:
        step = max(1, math.ceil(len(edges) / max_edges))
        selected = edges[::step][:max_edges]
        commands: list[str] = []
        for edge in selected:
            if len(edge) != 2 or not (0 <= edge[0] < len(projected) and 0 <= edge[1] < len(projected)):
                continue
            a, b = projected[edge[0]], projected[edge[1]]
            commands.append(f"M{a[0]:.1f},{a[1]:.1f}L{b[0]:.1f},{b[1]:.1f}")
        geometry = f'<path d="{"".join(commands)}" fill="none" stroke="#78baff" stroke-width="0.8" opacity="0.78"/>'
    else:
        step = max(1, math.ceil(len(projected) / 700))
        geometry = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.8" fill="#78baff"/>' for x, y in projected[::step])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        '<rect width="320" height="180" fill="#070a0f"/>' + geometry + "</svg>\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")
    return True


def _pcm_peak(sample: bytes, width: int) -> float:
    if width == 1:
        return abs(sample[0] - 128) / 128.0
    if width == 2:
        value = int.from_bytes(sample, "little", signed=True)
        return abs(value) / 32768.0
    if width == 3:
        raw = int.from_bytes(sample, "little", signed=False)
        if raw & 0x800000:
            raw -= 1 << 24
        return abs(raw) / float(1 << 23)
    if width == 4:
        value = int.from_bytes(sample, "little", signed=True)
        return abs(value) / float(1 << 31)
    return 0.0


def _write_waveform_svg(path: Path, wav_path: Path, bins: int = 150) -> bool:
    try:
        with wave.open(str(wav_path), "rb") as handle:
            frames = handle.getnframes()
            channels = handle.getnchannels()
            width = handle.getsampwidth()
            if frames <= 0 or channels <= 0 or width not in {1, 2, 3, 4}:
                return False
            values: list[float] = []
            for index in range(bins):
                position = min(frames - 1, int(index * frames / bins))
                handle.setpos(position)
                raw = handle.readframes(min(256, frames - position))
                frame_size = channels * width
                peak = 0.0
                for offset in range(0, len(raw) - frame_size + 1, frame_size):
                    for channel in range(channels):
                        start = offset + channel * width
                        peak = max(peak, _pcm_peak(raw[start:start + width], width))
                values.append(min(1.0, peak))
    except (OSError, wave.Error):
        return False
    lines = []
    for index, value in enumerate(values):
        x = 8 + index * (304 / max(1, bins - 1))
        half = max(1.0, value * 70)
        lines.append(f"M{x:.1f},{90-half:.1f}V{90+half:.1f}")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        '<rect width="320" height="180" fill="#070a0f"/>'
        '<path d="' + "".join(lines) + '" fill="none" stroke="#8ed4a8" stroke-width="1.2" opacity="0.86"/>'
        '<line x1="8" y1="90" x2="312" y2="90" stroke="#2d3b47" stroke-width="1"/>'
        '</svg>\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")
    return True



def _write_rgba_png(path: Path, width: int, height: int, rgba: bytes) -> bool:
    if width <= 0 or height <= 0 or len(rgba) != width * height * 4:
        return False
    import zlib
    signature = b"\x89PNG\r\n\x1a\n"
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    rows = bytearray()
    stride = width * 4
    for y in range(height):
        rows.append(0)
        rows.extend(rgba[y * stride:(y + 1) * stride])
    data = signature + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def _tile_color(value: int) -> tuple[int, int, int, int]:
    base = value & 0x3F
    if base == 0:
        return (8, 11, 16, 255)
    hue = ((base * 0.61803398875) % 1.0)
    saturation = 0.55 + ((base % 5) * 0.06)
    brightness = 0.62 + ((base % 3) * 0.10)
    r, g, b = colorsys.hsv_to_rgb(hue, min(0.92, saturation), min(0.96, brightness))
    factor = 1.0 - 0.10 * ((value >> 6) & 0x03)
    return (int(r * 255 * factor), int(g * 255 * factor), int(b * 255 * factor), 255)


def _parse_map_layers(path: Path) -> list[tuple[int, int, bytes]]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if len(data) < 8 or data[:4] != b"MAP\x00":
        return []
    count = struct.unpack_from(">I", data, 4)[0]
    if count < 1 or count > 16:
        return []
    offset = 8
    layers: list[tuple[int, int, bytes]] = []
    for _ in range(count):
        if offset + 8 > len(data):
            return []
        width, height = struct.unpack_from(">II", data, offset)
        offset += 8
        cells = width * height
        if width > 65536 or height > 65536 or cells > 64 * 1024 * 1024 or offset + cells > len(data):
            return []
        layers.append((width, height, data[offset:offset + cells]))
        offset += cells
    return layers


def _write_map_thumbnail(path: Path, output: Path, width: int = 320, height: int = 180) -> bool:
    layers = _parse_map_layers(path)
    nonempty = [layer for layer in layers if layer[0] and layer[1]]
    if not layers:
        return False
    rgba = bytearray((8, 11, 16, 255) * (width * height))
    if not nonempty:
        for index in range(min(width, height)):
            for x, y in ((index, index), (width - 1 - index, index)):
                position = (y * width + x) * 4
                rgba[position:position + 4] = bytes((49, 62, 82, 255))
        return _write_rgba_png(output, width, height, bytes(rgba))
    margin = 6
    gap = 4
    panel_count = len(nonempty)
    panel_width = max(1, (width - margin * 2 - gap * (panel_count - 1)) // panel_count)
    panel_height = height - margin * 2
    for panel_index, (source_width, source_height, cells) in enumerate(nonempty):
        x0 = margin + panel_index * (panel_width + gap)
        scale = min(panel_width / source_width, panel_height / source_height)
        draw_width = max(1, int(source_width * scale))
        draw_height = max(1, int(source_height * scale))
        ox = x0 + (panel_width - draw_width) // 2
        oy = margin + (panel_height - draw_height) // 2
        for y in range(draw_height):
            sy = min(source_height - 1, int(y * source_height / draw_height))
            for x in range(draw_width):
                sx = min(source_width - 1, int(x * source_width / draw_width))
                color = _tile_color(cells[sy * source_width + sx])
                position = ((oy + y) * width + ox + x) * 4
                rgba[position:position + 4] = bytes(color)
    return _write_rgba_png(output, width, height, bytes(rgba))


def _parse_dat_frames(path: Path) -> list[int]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if len(data) < 3 or data[0] != 1:
        return []
    count = struct.unpack_from(">H", data, 1)[0]
    offset = 3
    absolute = 0
    frames: list[int] = []
    for _ in range(count):
        if offset + 5 > len(data):
            return []
        words = data[offset]
        if words < 2:
            return []
        record_size = 1 + words * 2
        if offset + record_size > len(data):
            return []
        delta = struct.unpack_from(">h", data, offset + 1)[0]
        absolute += delta
        frames.append(absolute)
        offset += record_size
    return frames


def _write_dat_thumbnail(path: Path, output: Path, width: int = 320, height: int = 180) -> bool:
    frames = _parse_dat_frames(path)
    if not frames:
        return False
    bins = 150
    maximum = max(frames) or 1
    counts = [0] * bins
    for frame in frames:
        index = max(0, min(bins - 1, int(frame * (bins - 1) / maximum)))
        counts[index] += 1
    peak = max(counts) or 1
    rgba = bytearray((8, 11, 16, 255) * (width * height))
    baseline = height - 16
    for index, count in enumerate(counts):
        x0 = 8 + int(index * 304 / bins)
        x1 = 8 + int((index + 1) * 304 / bins)
        bar_height = max(1, int((count / peak) ** 0.55 * (height - 28))) if count else 0
        for y in range(baseline - bar_height, baseline):
            for x in range(x0, max(x0 + 1, x1)):
                pos = (y * width + x) * 4
                rgba[pos:pos + 4] = bytes((118, 185, 255, 255))
    return _write_rgba_png(output, width, height, bytes(rgba))


def _parse_anm_ranges(path: Path) -> list[tuple[str, float, float, int]]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if len(data) < 28 or len(data) % 28:
        return []
    records: list[tuple[str, float, float, int]] = []
    for offset in range(0, len(data), 28):
        raw_name = data[offset:offset + 16].split(b"\x00", 1)[0]
        if not raw_name:
            return []
        try:
            name = raw_name.decode("ascii")
        except UnicodeDecodeError:
            return []
        start, end = struct.unpack_from(">ff", data, offset + 16)
        loop = struct.unpack_from(">I", data, offset + 24)[0]
        if not (math.isfinite(start) and math.isfinite(end)):
            return []
        records.append((name, start, end, loop))
    return records


def _write_anm_thumbnail(path: Path, output: Path, width: int = 320, height: int = 180) -> bool:
    records = _parse_anm_ranges(path)
    if not records:
        return False
    maximum = max(end for _, _, end, _ in records) or 1.0
    rows = min(18, len(records))
    rgba = bytearray((8, 11, 16, 255) * (width * height))
    for row, (_, start, end, loop) in enumerate(records[:rows]):
        y0 = 8 + row * max(1, (height - 16) // rows)
        y1 = min(height - 8, y0 + max(2, (height - 16) // rows - 2))
        x0 = 8 + int(max(0.0, start) / maximum * 304)
        x1 = 8 + int(max(start, end) / maximum * 304)
        color = (244, 211, 124, 255) if loop else (142, 230, 168, 255)
        for y in range(y0, y1):
            for x in range(max(8, x0), min(width - 8, max(x0 + 1, x1))):
                pos = (y * width + x) * 4
                rgba[pos:pos + 4] = bytes(color)
    return _write_rgba_png(output, width, height, bytes(rgba))



def _write_tex_thumbnail(path: Path, output: Path, width: int = 320, height: int = 180) -> bool:
    core = _toolkit_core()
    if core is None:
        return False
    try:
        info, source = core.decode_tex_rgba(path.read_bytes())
        source_width, source_height = int(info.width), int(info.height)
    except Exception:
        return False
    if source_width <= 0 or source_height <= 0 or len(source) != source_width * source_height * 4:
        return False
    target = bytearray((8, 11, 16, 255) * (width * height))
    scale = min(width / source_width, height / source_height)
    draw_width = max(1, int(source_width * scale))
    draw_height = max(1, int(source_height * scale))
    ox = (width - draw_width) // 2
    oy = (height - draw_height) // 2
    for y in range(draw_height):
        sy = min(source_height - 1, int(y * source_height / draw_height))
        for x in range(draw_width):
            sx = min(source_width - 1, int(x * source_width / draw_width))
            src = (sy * source_width + sx) * 4
            dst = ((oy + y) * width + ox + x) * 4
            target[dst:dst + 4] = source[src:src + 4]
    return _write_rgba_png(output, width, height, bytes(target))

def _write_structured_thumbnail(path: Path, output: Path) -> Optional[str]:
    extension = path.suffix.lower()
    if extension == ".map" and _write_map_thumbnail(path, output):
        return "generated MAP layer overview"
    if extension == ".dat" and _write_dat_thumbnail(path, output):
        return "generated DAT command-density timeline"
    if extension == ".anm" and _write_anm_thumbnail(path, output):
        return "generated ANM frame-range timeline"
    if extension == ".tex" and _write_tex_thumbnail(path, output):
        return "decoded TEX thumbnail"
    return None


def _write_text_thumbnail_svg(path: Path, source: Path, preview: str) -> bool:
    """Write a cheap deterministic code/text card from already-read preview text."""
    suffix = source.suffix.lower().lstrip(".").upper() or "TEXT"
    lines: list[str] = []
    for raw in preview.splitlines():
        cleaned = "".join(ch if 0x20 <= ord(ch) < 0x7F else " " for ch in raw).strip()
        if cleaned:
            lines.append(cleaned[:52])
        if len(lines) >= 6:
            break
    if not lines:
        lines = ["(empty text file)"]
    rows = "".join(
        f'<text x="18" y="{54 + i * 18}" fill="#9fb0c8" font-family="ui-monospace,Consolas,monospace" font-size="11">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        '<rect width="320" height="180" fill="#070a0f"/>'
        '<rect x="10" y="10" width="300" height="160" rx="8" fill="#0d121b" stroke="#263247"/>'
        f'<text x="18" y="32" fill="#76b9ff" font-family="system-ui,sans-serif" font-size="13" font-weight="700">{html.escape(suffix)}</text>'
        + rows +
        '</svg>\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")
    return True


def _write_dat_thumbnail_svg(path: Path, output: Path, width: int = 320, height: int = 180) -> bool:
    """Fast SVG equivalent of the DAT density thumbnail (avoids 57k-pixel raster loops/file)."""
    frames = _parse_dat_frames(path)
    if not frames:
        return False
    bins = 96
    maximum = max(frames) or 1
    counts = [0] * bins
    for frame in frames:
        index = max(0, min(bins - 1, int(frame * (bins - 1) / maximum)))
        counts[index] += 1
    peak = max(counts) or 1
    baseline = height - 16
    bars: list[str] = []
    span = width - 16
    for index, count in enumerate(counts):
        if not count:
            continue
        x0 = 8 + index * span / bins
        x1 = 8 + (index + 1) * span / bins
        bar_height = max(1.0, (count / peak) ** 0.55 * (height - 28))
        bars.append(f'<rect x="{x0:.2f}" y="{baseline-bar_height:.2f}" width="{max(1.0, x1-x0):.2f}" height="{bar_height:.2f}" fill="#76b9ff"/>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="#080b10"/>'
        + "".join(bars) +
        f'<text x="8" y="12" fill="#718097" font-family="system-ui,sans-serif" font-size="9">{len(frames)} commands · frame {maximum}</text>'
        '</svg>\n'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8", newline="\n")
    return True


def _write_generic_placeholder_svg(path: Path, source: Path, category: str) -> bool:
    """Write a deterministic thumbnail for supported inventory items without a native renderer.

    This is deliberately a placeholder, not a fabricated media preview. It keeps the
    viewer visually complete for retained console-native assets such as WMA/XMA/AT3
    audio and XACT XWB/XSB data while clearly labelling the underlying file type.
    """
    label = html.escape(source.suffix.lower().lstrip(".").upper() or category.upper())
    title = html.escape(category.title())
    size = _human_bytes(source.stat().st_size) if source.is_file() else ""
    detail = html.escape(f"{title} · {size}" if size else title)
    icon = (
        '<path d="M102 68H138L164 47V133L138 112H102Z" fill="none" stroke="#6f9f80" stroke-width="4"/>'
        '<path d="M184 70Q210 90 184 110M199 57Q237 90 199 123" fill="none" stroke="#6f9f80" stroke-width="4"/>'
        if category == "audio" else
        '<path d="M108 47H190L212 69V133H108ZM190 47V70H212" fill="none" stroke="#7089a8" stroke-width="4"/>'
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        '<rect width="320" height="180" fill="#070a0f"/>'
        + icon +
        f'<text x="160" y="148" text-anchor="middle" fill="#aab8cc" font-family="system-ui,sans-serif" font-size="15">{label}</text>'
        f'<text x="160" y="165" text-anchor="middle" fill="#718097" font-family="system-ui,sans-serif" font-size="10">{detail}</text>'
        '</svg>\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")
    return True


def _write_model_placeholder_svg(path: Path, source: Path, metadata: dict[str, Any]) -> bool:
    label = html.escape(source.suffix.lower().lstrip(".").upper() or "MODEL")
    details = []
    for key in ("meshes", "nodes", "animations", "vertices", "lines"):
        if key in metadata:
            details.append(f"{key}: {metadata[key]}")
    detail = html.escape(" · ".join(details[:3]) or "No drawable geometry")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        '<rect width="320" height="180" fill="#070a0f"/>'
        '<path d="M110 120L160 40L210 120ZM130 120L160 72L190 120Z" fill="none" stroke="#687a96" stroke-width="4"/>'
        f'<text x="160" y="145" text-anchor="middle" fill="#aab8cc" font-family="system-ui,sans-serif" font-size="15">{label}</text>'
        f'<text x="160" y="164" text-anchor="middle" fill="#718097" font-family="system-ui,sans-serif" font-size="10">{detail}</text>'
        '</svg>\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")
    return True

def build_asset_viewer(
    input_path: Path,
    output: Path,
    *,
    title: str = "SIIG Asset Viewer",
    hash_files: bool = True,
    max_embed_bytes: int = 0,
    max_single_preview_bytes: int = 0,
    max_text_preview_bytes: int = 48 * 1024,
    page_size: int = 96,
    incremental: bool = False,
) -> dict[str, Any]:
    """Build a linked-data viewer.

    ``max_embed_bytes`` and ``max_single_preview_bytes`` are retained for command-line
    compatibility but no longer cause media to be base64-embedded. Direct relative
    URLs and lazy loading provide complete thumbnail coverage without inflating HTML.
    """
    root = input_path.resolve()
    if not root.is_dir():
        raise ValueError(f"asset-viewer input must be a directory: {input_path}")
    if output.suffix.lower() == ".html":
        html_path = output.resolve()
        output_dir = html_path.parent
        assets_dir = output_dir / f"{html_path.stem}_assets"
    else:
        output_dir = output.resolve()
        html_path = output_dir / "SIIG_Asset_Viewer.html"
        assets_dir = output_dir / "viewer_assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "ASSET_VIEWER_REPORT.json"
    data_path = assets_dir / "viewer_data.js"
    payload_dir = assets_dir / "payloads"
    thumbnail_dir = assets_dir / "thumbnails"
    if assets_dir.exists() and not incremental:
        import shutil
        shutil.rmtree(assets_dir)
    payload_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_dir.mkdir(parents=True, exist_ok=True)

    excluded_files = {html_path.resolve(), report_path.resolve()}
    excluded_dirs: set[Path] = {assets_dir.resolve()}
    if output_dir != root and _is_within(output_dir, root):
        excluded_dirs.add(output_dir.resolve())

    # When the viewer is rebuilt through update-rip it is staged beside the
    # existing canonical viewer (asset_viewer.siig-update-part).  Older builds
    # accidentally walked root/asset_viewer while generating that staged copy,
    # causing the viewer to index its own previous HTML/data/thumbnails.  Each
    # update could therefore make the next rebuild progressively slower and more
    # bloated.  The viewer is a browser *for* rip assets, never an asset itself.
    canonical_viewer = root / "asset_viewer"
    if canonical_viewer.is_dir() and canonical_viewer.resolve() != output_dir:
        excluded_dirs.add(canonical_viewer.resolve())

    paths = list(_walk_files(root, excluded_files, excluded_dirs))
    images = [path for path in paths if _kind(path) == "image"]
    gltfs = [path for path in paths if path.suffix.lower() == ".gltf"]
    wavs = [path for path in paths if path.suffix.lower() == ".wav"]
    image_local, image_global = _build_image_lookup(images, root)
    gltf_local, gltf_global = _build_image_lookup(gltfs, root)
    wav_local, wav_global = _build_image_lookup(wavs, root)

    # A converted glTF is already used as the interactive preview for its native GMX.
    # Keep both files indexed/openable, but mark the generated glTF as a default-hidden
    # duplicate so the normal browser view does not show two cards for one model.
    converted_gltf_sources: dict[Path, str] = {}
    for native_model in (path for path in paths if path.suffix.lower() == ".gmx"):
        related = _find_related(native_model, root, gltf_local, gltf_global)
        if related is not None and related.suffix.lower() == ".gltf":
            converted_gltf_sources[related.resolve()] = native_model.relative_to(root).as_posix()

    model_cache: dict[Path, tuple[dict[str, Any], dict[str, Any], Optional[Path], Optional[Path], str]] = {}
    wav_thumb_cache: dict[Path, Optional[Path]] = {}
    entries: list[dict[str, Any]] = []
    kind_counts: dict[str, int] = {}
    total_bytes = 0
    payload_bytes = 0
    payload_shards: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
    payload_shard_count = 32
    thumbnail_bytes = 0
    direct_thumbnails = 0
    derived_thumbnails = 0
    model_payloads = 0
    text_payloads = 0

    def register_payload(asset_id: str, payload: dict[str, Any]) -> Path:
        shard = int(asset_id[:8], 16) % payload_shard_count
        payload_shards[shard][asset_id] = payload
        return payload_dir / f"payload_{shard:02d}.js"

    def prepare_model(path: Path) -> tuple[dict[str, Any], dict[str, Any], Optional[Path], Optional[Path], str]:
        nonlocal thumbnail_bytes, model_payloads
        resolved = path.resolve()
        cached = model_cache.get(resolved)
        if cached is not None:
            return cached
        relative = path.relative_to(root).as_posix()
        asset_id = _stable_id(relative)
        metadata, wireframe = _model_summary(path)
        payload_path: Optional[Path] = None
        thumb_path: Optional[Path] = None
        candidate = thumbnail_dir / f"{asset_id}.svg"
        if wireframe:
            payload_path = register_payload(asset_id, {"wireframe": wireframe})
            model_payloads += 1
            if (incremental and candidate.is_file()) or _write_wireframe_svg(candidate, wireframe):
                thumb_path = candidate
                thumbnail_bytes += candidate.stat().st_size
        elif (incremental and candidate.is_file()) or _write_model_placeholder_svg(candidate, path, metadata):
            thumb_path = candidate
            thumbnail_bytes += candidate.stat().st_size
        cached = (metadata, wireframe, payload_path, thumb_path, asset_id)
        model_cache[resolved] = cached
        return cached

    def prepare_wav_thumb(path: Path) -> Optional[Path]:
        nonlocal thumbnail_bytes
        resolved = path.resolve()
        if resolved in wav_thumb_cache:
            return wav_thumb_cache[resolved]
        asset_id = _stable_id(path.relative_to(root).as_posix())
        candidate = thumbnail_dir / f"audio_{asset_id}.svg"
        result = candidate if ((incremental and candidate.is_file()) or _write_waveform_svg(candidate, path)) else None
        if result is not None:
            thumbnail_bytes += result.stat().st_size
        wav_thumb_cache[resolved] = result
        return result

    for path in paths:
        relative = path.relative_to(root).as_posix()
        asset_id = _stable_id(relative)
        stat_result = path.stat()
        kind = _kind(path)
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        total_bytes += stat_result.st_size
        folder = relative.rsplit("/", 1)[0] if "/" in relative else ""
        entry: dict[str, Any] = {
            "id": asset_id,
            "path": relative,
            "folder": folder,
            "name": path.name,
            "extension": path.suffix.lower(),
            "kind": kind,
            "size": stat_result.st_size,
            "size_human": _human_bytes(stat_result.st_size),
            "modified_ns": stat_result.st_mtime_ns,
            "url": _relative_url(path, html_path),
        }
        native_source = converted_gltf_sources.get(path.resolve())
        if native_source is not None:
            entry["default_hidden_duplicate"] = True
            entry["native_model_source"] = native_source
        if hash_files:
            entry["sha256"] = _sha256(path)
        identity = _entity_identity(path) if kind == "model" else None
        if identity is not None:
            entry["entity_identity"] = identity

        if kind == "image":
            entry["metadata"] = _image_meta(path)
            entry["thumbnail_url"] = entry["url"]
            entry["preview_url"] = entry["url"]
            entry["thumbnail_source"] = "original image"
            direct_thumbnails += 1
        elif path.suffix.lower() == ".gltf":
            metadata, _, payload_path, thumb_path, payload_key = prepare_model(path)
            entry["metadata"] = metadata
            if payload_path is not None:
                entry["payload_url"] = _relative_url(payload_path, html_path)
                entry["payload_key"] = payload_key
            if thumb_path is not None:
                entry["thumbnail_url"] = _relative_url(thumb_path, html_path)
                entry["thumbnail_source"] = "generated glTF wireframe"
                derived_thumbnails += 1
        elif kind == "model":
            related_gltf = _find_related(path, root, gltf_local, gltf_global)
            preview_model = related_gltf if related_gltf is not None else path
            metadata, _, payload_path, thumb_path, payload_key = prepare_model(preview_model)
            entry["metadata"] = dict(metadata)
            if related_gltf is not None:
                entry["preview_source"] = related_gltf.relative_to(root).as_posix()
            if payload_path is not None:
                entry["payload_url"] = _relative_url(payload_path, html_path)
                entry["payload_key"] = payload_key
            if thumb_path is not None:
                entry["thumbnail_url"] = _relative_url(thumb_path, html_path)
                entry["thumbnail_source"] = "related glTF wireframe" if related_gltf is not None else "generated model wireframe"
                derived_thumbnails += 1
        elif kind == "audio":
            wav_path = path if path.suffix.lower() == ".wav" else _find_related(path, root, wav_local, wav_global)
            if wav_path is not None:
                entry["metadata"] = _wav_meta(wav_path)
                entry["preview_url"] = _relative_url(wav_path, html_path)
                if wav_path != path:
                    entry["preview_source"] = wav_path.relative_to(root).as_posix()
                thumb_path = prepare_wav_thumb(wav_path)
                if thumb_path is not None:
                    entry["thumbnail_url"] = _relative_url(thumb_path, html_path)
                    entry["thumbnail_source"] = "generated WAV waveform"
                    derived_thumbnails += 1
            else:
                entry["metadata"] = {}
                if path.suffix.lower() in BROWSER_AUDIO_EXTENSIONS:
                    entry["preview_url"] = entry["url"]
        elif kind == "text":
            preview = _text_preview(path, max_text_preview_bytes)
            if preview:
                payload_path = register_payload(asset_id, {"text": preview})
                entry["payload_url"] = _relative_url(payload_path, html_path)
                entry["payload_key"] = asset_id
                text_payloads += 1
            text_thumb = thumbnail_dir / f"text_{asset_id}.svg"
            if (incremental and text_thumb.is_file()) or _write_text_thumbnail_svg(text_thumb, path, preview):
                entry["thumbnail_url"] = _relative_url(text_thumb, html_path)
                entry["thumbnail_source"] = "generated text/code thumbnail"
                thumbnail_bytes += text_thumb.stat().st_size
                derived_thumbnails += 1
            if path.suffix.lower() == ".json":
                try:
                    value = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(value, dict):
                        entry["metadata"] = {"top_level_keys": list(value)[:40]}
                    elif isinstance(value, list):
                        entry["metadata"] = {"items": len(value)}
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    pass

        if "thumbnail_url" not in entry and kind == "data":
            if path.suffix.lower() == ".dat":
                structured_path = thumbnail_dir / f"data_{asset_id}.svg"
                structured_source = "generated DAT command-density timeline" if ((incremental and structured_path.is_file()) or _write_dat_thumbnail_svg(path, structured_path)) else None
            else:
                structured_path = thumbnail_dir / f"data_{asset_id}.png"
                structured_source = ("reused generated structured thumbnail" if incremental and structured_path.is_file() else _write_structured_thumbnail(path, structured_path))
            if structured_source:
                entry["thumbnail_url"] = _relative_url(structured_path, html_path)
                entry["thumbnail_source"] = structured_source
                thumbnail_bytes += structured_path.stat().st_size
                derived_thumbnails += 1

        if "thumbnail_url" not in entry and kind not in {"text", "archive", "other"}:
            related_image = _find_related(path, root, image_local, image_global)
            if related_image is not None:
                entry["thumbnail_url"] = _relative_url(related_image, html_path)
                entry["thumbnail_source"] = "related converted image"
                entry.setdefault("preview_url", _relative_url(related_image, html_path))
                entry["preview_source"] = related_image.relative_to(root).as_posix()
                derived_thumbnails += 1

        if "thumbnail_url" not in entry and kind in {"audio", "data"}:
            placeholder = thumbnail_dir / f"placeholder_{asset_id}.svg"
            if (incremental and placeholder.is_file()) or _write_generic_placeholder_svg(placeholder, path, kind):
                entry["thumbnail_url"] = _relative_url(placeholder, html_path)
                entry["thumbnail_source"] = f"{kind} placeholder (no native preview)"
                thumbnail_bytes += placeholder.stat().st_size
                derived_thumbnails += 1
        entries.append(entry)

    for shard, payloads in sorted(payload_shards.items()):
        payload_bytes += _write_payload_shard(payload_dir / f"payload_{shard:02d}.js", payloads)

    thumbnail_count = sum(1 for entry in entries if entry.get("thumbnail_url"))
    previewable_count = sum(1 for entry in entries if entry["kind"] in {"image", "model", "audio", "data", "text"})
    missing_previewable = sum(1 for entry in entries if entry["kind"] in {"image", "model", "audio", "data", "text"} and not entry.get("thumbnail_url"))
    converted_duplicate_count = sum(1 for entry in entries if entry.get("default_hidden_duplicate"))
    identified_model_file_count = sum(1 for entry in entries if entry.get("entity_identity"))
    identity_catalog_rows = len(_entity_identity_catalog())
    database = {
        "viewer_version": VIEWER_VERSION,
        "title": title,
        "root_name": root.name,
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "total_bytes_human": _human_bytes(total_bytes),
        "kind_counts": kind_counts,
        "thumbnail_count": thumbnail_count,
        "previewable_count": previewable_count,
        "missing_previewable_thumbnails": missing_previewable,
        "converted_model_duplicate_count": converted_duplicate_count,
        "identified_model_file_count": identified_model_file_count,
        "entity_identity_catalog_rows": identity_catalog_rows,
        "entity_identity_source": "project-owner identifications with explicit speculative-status preservation",
        "default_hide_converted_model_duplicates": True,
        "folder_navigation": True,
        "page_size": max(24, min(500, int(page_size))),
        "files": entries,
    }
    data_json = json.dumps(database, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    data_path.write_text(f"window.SIIG_VIEWER_DB={data_json};\n", encoding="utf-8", newline="\n")
    html_path.write_text(_viewer_html(title, _relative_url(data_path, html_path)), encoding="utf-8", newline="\n")

    viewer_files = [html_path, data_path]
    viewer_files.extend(path for path in payload_dir.glob("*.js"))
    viewer_files.extend(path for path in thumbnail_dir.iterdir() if path.is_file())
    viewer_total_bytes = sum(path.stat().st_size for path in viewer_files if path.is_file())
    report = {
        key: value for key, value in database.items() if key != "files"
    }
    report.update({
        "html_file": html_path.name,
        "data_file": _relative_url(data_path, html_path),
        "report_file": report_path.name,
        "hashes_included": hash_files,
        "linked_data_mode": True,
        "base64_media_embedded": False,
        "legacy_max_embed_bytes_ignored": max_embed_bytes,
        "legacy_max_single_preview_bytes_ignored": max_single_preview_bytes,
        "html_bytes": html_path.stat().st_size,
        "data_bytes": data_path.stat().st_size,
        "payload_bytes": payload_bytes,
        "thumbnail_bytes": thumbnail_bytes,
        "viewer_total_bytes": viewer_total_bytes,
        "direct_thumbnails": direct_thumbnails,
        "derived_thumbnails": derived_thumbnails,
        "model_payloads": model_payloads,
        "text_payloads": text_payloads,
        "payload_shards": len(payload_shards),
        "max_text_preview_bytes": max_text_preview_bytes,
        "output_assets_directory": assets_dir.name,
    })
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _viewer_html(title: str, data_url: str) -> str:
    safe_title = html.escape(title)
    safe_data_url = html.escape(data_url, quote=True)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title}</title>
<style>
:root{{color-scheme:dark;--bg:#0b0e14;--panel:#121722;--panel2:#171e2b;--line:#2a3446;--text:#edf2ff;--muted:#9ba8bd;--accent:#76b9ff;font:14px system-ui,sans-serif}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text)}}header{{position:sticky;top:0;z-index:4;background:#0e131dee;border-bottom:1px solid var(--line);backdrop-filter:blur(8px);padding:12px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}h1{{font-size:18px;margin:0 16px 0 0}}input,select,button{{background:var(--panel2);color:var(--text);border:1px solid #39475f;border-radius:7px;padding:7px 9px}}input[type=search]{{min-width:min(340px,75vw)}}label.check{{display:inline-flex;align-items:center;gap:6px;color:var(--muted);white-space:nowrap}}label.check input{{min-width:0}}button{{cursor:pointer}}button:disabled{{opacity:.45;cursor:default}}main{{padding:14px}}.folderbar{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:9px 10px;margin-bottom:8px}}.crumbs{{display:flex;gap:3px;align-items:center;flex-wrap:wrap;flex:1;min-width:220px}}.crumbs button{{padding:4px 7px}}.folderlist{{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 12px}}.folderchip{{background:#141c29;border:1px solid #34445e;border-radius:8px;padding:7px 10px}}.folderchip b{{color:#dce9ff}}.stats{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}.stat{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 11px}}.stat b{{font-size:17px}}.toolbar{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 12px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:10px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;min-height:180px}}.thumb{{height:150px;background:#080a0f;display:flex;align-items:center;justify-content:center;overflow:hidden;border-bottom:1px solid var(--line)}}.thumb img{{width:100%;height:100%;object-fit:contain;image-rendering:auto}}.thumb canvas{{width:100%;height:100%}}.icon{{font-size:44px;color:#596780}}.body{{padding:10px;min-width:0}}.name{{font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:5px}}.identity{{font-size:12px;color:#cfe1ff;margin-top:4px;overflow-wrap:anywhere}}.identity.speculative{{color:#ffd7a3}}.path{{font-size:12px;color:var(--muted);overflow-wrap:anywhere;margin-top:4px}}.meta{{font-size:12px;color:#bdc8da;margin-top:7px}}.actions{{margin-top:auto;padding:0 10px 10px;display:flex;gap:6px;align-items:center}}a{{color:var(--accent)}}.pill{{display:inline-block;background:#273348;border-radius:999px;padding:2px 7px;font-size:11px;margin-right:4px}}dialog{{width:min(1100px,94vw);height:min(820px,90vh);background:var(--panel);color:var(--text);border:1px solid #48566e;border-radius:12px;padding:0}}dialog::backdrop{{background:#000b}}.modal-head{{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line)}}.modal-content{{height:calc(100% - 52px);overflow:auto;padding:14px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#090c12;border:1px solid var(--line);padding:12px;border-radius:8px}}.large-preview{{max-width:100%;max-height:62vh;display:block;margin:auto}}.model{{height:62vh;width:100%;background:#070a0f;border-radius:8px}}.empty,.loading{{padding:40px;text-align:center;color:var(--muted)}}.error{{color:#ffaaa4}}.page{{font-variant-numeric:tabular-nums;color:var(--muted)}}
</style></head><body>
<header><h1>{safe_title}</h1><input type="search" id="search" placeholder="Search current folder"><select id="kind"><option value="">All types</option></select><select id="sort"><option value="path">Path</option><option value="name">Name</option><option value="size-desc">Largest</option><option value="size-asc">Smallest</option></select><label class="check"><input type="checkbox" id="showDuplicates">Show converted model duplicates</label><span id="shown"></span></header>
<main><div class="stats" id="stats"><div class="loading">Loading local inventory…</div></div><div class="folderbar"><button id="folderUp">Up</button><div class="crumbs" id="crumbs"></div><label class="check"><input type="checkbox" id="recursiveFolder">Include subfolders</label></div><div class="folderlist" id="folderList"></div><div class="toolbar"><button id="prev">Previous</button><span class="page" id="page"></span><button id="next">Next</button><select id="pageSize"><option>48</option><option selected>96</option><option>192</option><option>384</option></select></div><div class="grid" id="grid"><div class="loading">Loading…</div></div></main>
<dialog id="modal"><div class="modal-head"><b id="modalTitle"></b><button onclick="modal.close()">Close</button></div><div class="modal-content" id="modalContent"></div></dialog>
<script src="{safe_data_url}"></script>
<script>
const DB=window.SIIG_VIEWER_DB,grid=document.getElementById('grid'),search=document.getElementById('search'),kind=document.getElementById('kind'),sort=document.getElementById('sort'),showDuplicates=document.getElementById('showDuplicates'),shown=document.getElementById('shown'),modal=document.getElementById('modal'),modalTitle=document.getElementById('modalTitle'),modalContent=document.getElementById('modalContent'),prev=document.getElementById('prev'),next=document.getElementById('next'),pageLabel=document.getElementById('page'),pageSize=document.getElementById('pageSize'),folderUp=document.getElementById('folderUp'),crumbs=document.getElementById('crumbs'),folderList=document.getElementById('folderList'),recursiveFolder=document.getElementById('recursiveFolder');
if(!DB){{grid.innerHTML='<div class="empty error">Viewer inventory could not be loaded. Keep the viewer HTML beside its assets folder, or open it through the toolkit serve command.</div>';throw new Error('missing SIIG_VIEWER_DB')}}
let currentPage=0,filtered=[],currentFolder='';pageSize.value=String(DB.page_size||96);showDuplicates.checked=false;recursiveFolder.checked=false;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
for(const key of Object.keys(DB.kind_counts).sort()){{const o=document.createElement('option');o.value=key;o.textContent=`${{key}} (${{DB.kind_counts[key]}})`;kind.appendChild(o)}}
stats.innerHTML=`<div class=stat><b>${{DB.file_count}}</b><br>indexed files</div><div class=stat><b>${{DB.total_bytes_human}}</b><br>source data</div><div class=stat><b>${{DB.thumbnail_count}}/${{DB.previewable_count}}</b><br>previewable thumbnails</div><div class=stat><b>${{DB.identified_model_file_count||0}}</b><br>friendly model identities</div><div class=stat><b>${{DB.converted_model_duplicate_count||0}}</b><br>converted model duplicates hidden by default</div><div class=stat><b>${{DB.missing_previewable_thumbnails}}</b><br>without derived preview</div>`+Object.entries(DB.kind_counts).sort().map(([k,v])=>`<div class=stat><b>${{v}}</b><br>${{esc(k)}}</div>`).join('');
function icon(k){{return {{image:'▧',model:'◇',audio:'♫',text:'≡',data:'⌗',archive:'▣',other:'·'}}[k]||'·'}}
function meta(f){{const m=f.metadata||{{}},parts=[f.size_human];if(m.width)parts.push(`${{m.width}}×${{m.height}}`);if(m.meshes!==undefined)parts.push(`${{m.meshes}} meshes`,`${{m.animations}} animations`);if(m.duration_seconds!==undefined)parts.push(`${{m.duration_seconds}} s`,`${{m.sample_rate}} Hz`);return parts.join(' · ')}}
function identityLine(f){{const i=f.entity_identity;if(!i)return '';const scope=[i.dimension_scope,i.platform_note].filter(Boolean).join(' · '),spec=String(i.identity_status||'').includes('speculative');return `<div class="identity${{spec?' speculative':''}}"><b>${{esc(i.display_name)}}</b>${{scope?` · ${{esc(scope)}}`:''}}${{spec?' · speculative':''}}</div>`}}
function thumb(f){{return f.thumbnail_url?`<img class=lazy loading=lazy decoding=async alt="" data-src="${{f.thumbnail_url}}">`:`<div class=icon>${{icon(f.kind)}}</div>`}}
const imageObserver='IntersectionObserver' in window?new IntersectionObserver((items,observer)=>{{for(const item of items)if(item.isIntersecting){{const img=item.target;img.src=img.dataset.src;img.removeAttribute('data-src');observer.unobserve(img)}}}},{{rootMargin:'300px'}}):null;
function activateImages(){{for(const img of grid.querySelectorAll('img[data-src]')){{if(imageObserver)imageObserver.observe(img);else img.src=img.dataset.src}}}}
function folderParent(path){{const i=path.lastIndexOf('/');return i<0?'':path.slice(0,i)}}
function childFolders(base){{const counts=new Map();for(const f of DB.files){{const folder=f.folder||'';let rest='';if(base){{if(!folder.startsWith(base+'/'))continue;rest=folder.slice(base.length+1)}}else rest=folder;if(!rest)continue;const head=rest.split('/')[0],full=base?`${{base}}/${{head}}`:head;counts.set(full,(counts.get(full)||0)+1)}}return [...counts.entries()].sort((a,b)=>a[0].localeCompare(b[0]))}}
function renderFolderNav(){{folderUp.disabled=!currentFolder;const parts=currentFolder?currentFolder.split('/'):[];let built='';const crumbsHtml=[`<button data-folder="">${{esc(DB.root_name||'Root')}}</button>`];for(const part of parts){{built=built?`${{built}}/${{part}}`:part;crumbsHtml.push('<span>/</span>',`<button data-folder="${{esc(built)}}">${{esc(part)}}</button>`)}}crumbs.innerHTML=crumbsHtml.join('');for(const b of crumbs.querySelectorAll('[data-folder]'))b.onclick=()=>setFolder(b.dataset.folder);const children=childFolders(currentFolder);folderList.innerHTML=children.map(([path,count])=>{{const name=path.split('/').pop();return `<button class=folderchip data-folder="${{esc(path)}}">📁 <b>${{esc(name)}}</b> · ${{count}} file${{count===1?'':'s'}}</button>`}}).join('');for(const b of folderList.querySelectorAll('[data-folder]'))b.onclick=()=>setFolder(b.dataset.folder)}}
function setFolder(path){{currentFolder=path||'';search.value='';currentPage=0;renderFolderNav();updateFilter(true)}}
function updateFilter(reset=true){{const q=search.value.trim().toLowerCase(),k=kind.value,recursive=recursiveFolder.checked;filtered=DB.files.filter(f=>{{const folder=f.folder||'',folderOk=recursive?(currentFolder===''||folder===currentFolder||folder.startsWith(currentFolder+'/')):folder===currentFolder,duplicateOk=showDuplicates.checked||!f.default_hidden_duplicate;const i=f.entity_identity||{{}};return folderOk&&duplicateOk&&(!k||f.kind===k)&&(!q||`${{f.path}} ${{f.sha256||''}} ${{f.extension}} ${{i.display_name||''}} ${{i.entity_kind||''}} ${{i.dimension_scope||''}} ${{i.platform_note||''}} ${{i.identity_status||''}}`.toLowerCase().includes(q))}});filtered.sort((a,b)=>sort.value==='name'?a.name.localeCompare(b.name):sort.value==='size-desc'?b.size-a.size:sort.value==='size-asc'?a.size-b.size:a.path.localeCompare(b.path));if(reset)currentPage=0;renderPage()}}
function renderPage(){{const amount=Number(pageSize.value)||96,pages=Math.max(1,Math.ceil(filtered.length/amount));currentPage=Math.max(0,Math.min(currentPage,pages-1));const start=currentPage*amount,files=filtered.slice(start,start+amount);shown.textContent=`${{filtered.length}} visible · ${{DB.file_count}} indexed`;pageLabel.textContent=`Page ${{currentPage+1}} of ${{pages}}`;prev.disabled=currentPage===0;next.disabled=currentPage>=pages-1;grid.innerHTML=files.map(f=>`<article class=card><div class=thumb>${{thumb(f)}}</div><div class=body><div><span class=pill>${{esc(f.kind)}}</span><span class=pill>${{esc(f.extension||'no ext')}}</span></div><div class=name title="${{esc(f.name)}}">${{esc(f.name)}}</div>${{identityLine(f)}}<div class=path>${{esc(f.path)}}</div><div class=meta>${{esc(meta(f))}}</div></div><div class=actions><button data-open="${{f.id}}">Inspect</button><button data-native="${{f.id}}" title="Uses the OS-default application when viewed through the toolkit localhost server; otherwise falls back to the browser">Open file</button></div></article>`).join('')||'<div class=empty>No matching assets in this folder.</div>';for(const b of grid.querySelectorAll('[data-open]'))b.onclick=()=>openFile(DB.files.find(f=>f.id===b.dataset.open));for(const b of grid.querySelectorAll('[data-native]'))b.onclick=()=>openNative(DB.files.find(f=>f.id===b.dataset.native),b);activateImages();window.scrollTo({{top:0,behavior:'instant'}})}}
const loadedPayloadScripts=new Map();function loadPayload(f){{window.SIIG_VIEWER_PAYLOADS=window.SIIG_VIEWER_PAYLOADS||{{}};const key=f.payload_key||f.id;if(window.SIIG_VIEWER_PAYLOADS[key])return Promise.resolve(window.SIIG_VIEWER_PAYLOADS[key]);if(!f.payload_url)return Promise.resolve({{}});if(!loadedPayloadScripts.has(f.payload_url))loadedPayloadScripts.set(f.payload_url,new Promise(resolve=>{{const script=document.createElement('script');script.src=f.payload_url;script.onload=()=>resolve(true);script.onerror=()=>resolve(false);document.head.appendChild(script)}}));return loadedPayloadScripts.get(f.payload_url).then(ok=>ok?(window.SIIG_VIEWER_PAYLOADS[key]||{{}}):{{error:'Local preview payload could not be loaded.'}})}}
async function openNative(f,button){{if(!f)return;const original=button?.textContent||'Open file';if(location.protocol==='http:'||location.protocol==='https:'){{try{{const r=await fetch(`/__siig_open__?path=${{encodeURIComponent(f.path)}}`,{{method:'POST',headers:{{'X-SIIG-Open':'1'}}}});if(r.ok){{if(button){{button.textContent='Opened';setTimeout(()=>button.textContent=original,900)}}return}}}}catch(_e){{}}}}window.open(f.url,'_blank')}}
async function openFile(f){{modalTitle.textContent=f.path;modalContent.innerHTML='<div class=loading>Loading preview…</div>';modal.showModal();const payload=await loadPayload(f);const ident=f.entity_identity;let body=`<p><b>Type:</b> ${{esc(f.kind)}} · <b>Size:</b> ${{esc(f.size_human)}}${{ident?`<br><b>Friendly identity:</b> ${{esc(ident.display_name)}} · ${{esc(ident.entity_kind||'')}}${{ident.dimension_scope?` · ${{esc(ident.dimension_scope)}}`:''}}${{ident.platform_note?` · ${{esc(ident.platform_note)}}`:''}}<br><b>Identity evidence:</b> ${{esc(ident.identity_status||'')}}${{ident.notes?` — ${{esc(ident.notes)}}`:''}}`:''}}${{f.sha256?`<br><b>SHA-256:</b> <code>${{esc(f.sha256)}}</code>`:''}}${{f.preview_source?`<br><b>Preview source:</b> ${{esc(f.preview_source)}}`:''}}</p>`;if(f.kind==='image'||(f.preview_url&&f.kind==='data'))body+=`<img class=large-preview src="${{f.preview_url||f.url}}">`;else if(f.kind==='audio'&&f.preview_url)body+=`<audio controls preload=metadata style="width:100%" src="${{f.preview_url}}"></audio>`;else if(payload.wireframe?.points?.length)body+=`<canvas class=model id=modalModel></canvas><p class=path>Local mesh-space wireframe preview. Node transforms, materials, and animation behavior are summarized rather than fully rendered.</p>`;else if(payload.text!==undefined)body+=`<pre>${{esc(payload.text)}}</pre>`;else body+=`<pre>${{esc(JSON.stringify(f.metadata||{{}},null,2))}}</pre>`;if(payload.error)body+=`<p class=error>${{esc(payload.error)}}</p>`;modalContent.innerHTML=body;if(document.getElementById('modalModel'))startModel(document.getElementById('modalModel'),payload.wireframe,true)}}
function startModel(canvas,w,interactive){{if(!w?.points?.length)return;const ctx=canvas.getContext('2d'),pts=w.points,edges=w.edges||[];let ax=-.35,ay=.55,zoom=1,drag=false,lx=0,ly=0;function draw(){{const rect=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1,ww=Math.max(10,Math.floor(rect.width*dpr)),hh=Math.max(10,Math.floor(rect.height*dpr));if(canvas.width!==ww||canvas.height!==hh){{canvas.width=ww;canvas.height=hh}}ctx.fillStyle='#070a0f';ctx.fillRect(0,0,ww,hh);const sx=Math.sin(ax),cx=Math.cos(ax),sy=Math.sin(ay),cy=Math.cos(ay),center=[(w.min[0]+w.max[0])/2,(w.min[1]+w.max[1])/2,(w.min[2]+w.max[2])/2],extent=Math.max(w.max[0]-w.min[0],w.max[1]-w.min[1],w.max[2]-w.min[2],1e-5),scale=Math.min(ww,hh)*.72/extent*zoom;const pp=pts.map(p=>{{let x=p[0]-center[0],y=p[1]-center[1],z=p[2]-center[2];const x1=x*cy+z*sy,z1=-x*sy+z*cy,y1=y*cx-z1*sx;return [ww/2+x1*scale,hh/2-y1*scale,z1]}});ctx.strokeStyle='#78baff';ctx.globalAlpha=.72;ctx.lineWidth=Math.max(1,dpr*.6);ctx.beginPath();for(const e of edges){{const a=pp[e[0]],b=pp[e[1]];if(!a||!b)continue;ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1])}}ctx.stroke();if(!edges.length){{ctx.fillStyle='#78baff';for(const p of pp)ctx.fillRect(p[0],p[1],2*dpr,2*dpr)}}ctx.globalAlpha=1}}draw();if(interactive){{canvas.onpointerdown=e=>{{drag=true;lx=e.clientX;ly=e.clientY;canvas.setPointerCapture(e.pointerId)}};canvas.onpointermove=e=>{{if(!drag)return;ay+=(e.clientX-lx)*.008;ax+=(e.clientY-ly)*.008;lx=e.clientX;ly=e.clientY;draw()}};canvas.onpointerup=()=>drag=false;canvas.onwheel=e=>{{e.preventDefault();zoom=Math.max(.2,Math.min(8,zoom*Math.exp(-e.deltaY*.001)));draw()}}}}}}
search.oninput=()=>updateFilter(true);kind.onchange=()=>updateFilter(true);sort.onchange=()=>updateFilter(true);showDuplicates.onchange=()=>updateFilter(true);recursiveFolder.onchange=()=>updateFilter(true);folderUp.onclick=()=>setFolder(folderParent(currentFolder));pageSize.onchange=()=>{{currentPage=0;renderPage()}};prev.onclick=()=>{{currentPage--;renderPage()}};next.onclick=()=>{{currentPage++;renderPage()}};renderFolderNav();updateFilter(true);
</script></body></html>'''


def _open_os_default(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        import subprocess
        subprocess.Popen(["open", str(path)])
    else:
        import subprocess
        subprocess.Popen(["xdg-open", str(path)])


def serve_directory(
    root: Path, *, port: int = 8765, open_browser: bool = True, open_relative: str = ""
) -> None:
    directory = root.resolve()
    if not directory.is_dir():
        raise ValueError(f"serve root is not a directory: {root}")

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, fmt: str, *args: Any) -> None:
            print("viewer:", fmt % args)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            parsed = urlparse(self.path)
            if parsed.path != "/__siig_open__" or self.headers.get("X-SIIG-Open") != "1":
                self.send_error(404)
                return
            raw_path = parse_qs(parsed.query).get("path", [""])[0]
            candidate = _safe_child(directory, directory / raw_path)
            if candidate is None or not candidate.is_file():
                self.send_error(404, "File is outside the served tree or does not exist")
                return
            try:
                _open_os_default(candidate)
            except Exception as exc:
                self.send_error(500, f"Could not open file: {exc}")
                return
            self.send_response(204)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    suffix = "/" + quote(open_relative.replace("\\", "/").lstrip("/"), safe="/") if open_relative else "/"
    url = f"http://127.0.0.1:{server.server_port}{suffix}"
    print(f"serving {directory} at {url}")
    print("press Ctrl+C to stop")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping server")
    finally:
        server.server_close()
