"""Executable-backed SIIG retail camera-preset helpers.

The 32 x 30 preset table is preserved separately as raw executable data. This
module operates on the runtime-initialized semantic table whose names are only
assigned where downstream retail-PS3 consumers prove their role.

Key evidence:
- 0x0015B524: preset copy/activation
- 0x0015BBA8: preset transition/interpolation
- 0x00155300: projection, uniform scale, scene/view translation, view matrix
- 0x00157A10: camera-eye offset transformed through active stage/route frame
- 0x00157540: dynamic eye/target horizontal response
- 0x0015B910 -> 0x0020D69C/0x0020E984 plus Xbox material/shader path: face bias
- 0x0020E984 plus renderer paths 0x003756AC/0x003756E8: fog color/range

Word 11 is now identified as `face_bias`. Xbox retail closes the former
ambiguity: the material virtual +0x18 setter stores it at wrapper +0x60; that
value is uploaded for the `collada_face1` material and the embedded vertex
shader names the corresponding c9 uniform `faceBias`, applying
`pos - Normal * faceBias.x`.
"""
from __future__ import annotations

import csv
import math
import struct
from pathlib import Path
from typing import Mapping, Sequence

from siig_route import transform_row_vec3


def _f32(value: float) -> float:
    return struct.unpack(">f", struct.pack(">f", float(value)))[0]


def _vec3(values: Sequence[float]) -> tuple[float, float, float]:
    if len(values) != 3:
        raise ValueError("expected exactly three components")
    return (_f32(values[0]), _f32(values[1]), _f32(values[2]))


def gmx_serialized_affine_to_runtime_row(matrix: Sequence[float]) -> tuple[tuple[float, ...], ...]:
    """Convert one serialized GMX affine matrix to SIIG's runtime row-vector form.

    SIIG GMX ANIM matrices are serialized as conventional row-major matrices for
    column-vector use: translation is stored at flat indices 3/7/11.  The PS3
    runtime camera/math path instead consumes row-vector matrices whose
    translation occupies the final row.  The SgModel node-matrix getter bridges
    those representations before the camera copies/uses the matrix, so the
    conversion is a 4x4 transpose.

    Evidence boundary: GMX serialization is demonstrated by real cam01/fld015
    ANIM matrices; runtime layout is demonstrated by PS3 0x0036A154,
    0x00369BE4 and the 0x00157A10 camera path.  This helper models the resulting
    representation change directly rather than the internal SgModel getter.
    """
    if len(matrix) != 16:
        raise ValueError("GMX affine matrix must contain 16 values")
    return tuple(
        tuple(_f32(float(matrix[c * 4 + r])) for c in range(4))
        for r in range(4)
    )


def field_state_from_gmx_matrix(matrix: Sequence[float]) -> dict:
    """Return FieldPos/orientation from one serialized GMX matrix sample."""
    runtime = gmx_serialized_affine_to_runtime_row(matrix)
    field_position = (runtime[3][0], runtime[3][1], runtime[3][2])
    orientation = tuple(tuple(runtime[r][c] for c in range(3)) for r in range(3))
    return {
        "field_position": list(field_position),
        "orientation_matrix_row_vector": [list(row) for row in orientation],
        "runtime_matrix_row_vector": [list(row) for row in runtime],
        "serialized_translation_indices": [3, 7, 11],
        "runtime_translation_row": 3,
        "conversion": "transpose_4x4",
    }


def _default_table_path() -> Path:
    return Path(__file__).resolve().parent / "reference" / "tables" / "CAMERA_PRESETS_RUNTIME_SEMANTIC.csv"


def load_camera_presets(path: str | Path | None = None) -> list[dict]:
    table = Path(path) if path is not None else _default_table_path()
    with table.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 32:
        raise ValueError(f"camera preset table must contain 32 rows; found {len(rows)}")
    return rows


def _float(row: Mapping[str, str], key: str) -> float:
    return _f32(float(row[key]))


def camera_preset_info(index: int, *, table_path: str | Path | None = None) -> dict:
    rows = load_camera_presets(table_path)
    if not 0 <= int(index) < len(rows):
        raise ValueError(f"camera preset index out of range: {index}")
    row = rows[int(index)]
    fog = []
    for profile in range(3):
        prefix = f"fog{profile}_"
        fog.append({
            "profile_index": profile,
            "start": _float(row, prefix + "start"),
            "end": _float(row, prefix + "end"),
            "color_rgba": [
                _float(row, prefix + "color_r"),
                _float(row, prefix + "color_g"),
                _float(row, prefix + "color_b"),
                _float(row, prefix + "color_a"),
            ],
        })
    return {
        "preset_index": int(index),
        "fov_degrees": _float(row, "fov_degrees"),
        "fov_radians": _f32(_float(row, "fov_degrees") * _f32(math.pi) / _f32(180.0)),
        "uniform_scene_view_scale": _float(row, "uniform_scene_view_scale"),
        "camera_eye_offset": [
            _float(row, "camera_eye_offset_x"),
            _float(row, "camera_eye_offset_y"),
            _float(row, "camera_eye_offset_z"),
        ],
        "scene_view_translation": [
            _float(row, "scene_view_translation_x"),
            _float(row, "scene_view_translation_y"),
            _float(row, "scene_view_translation_z"),
        ],
        "dynamic_horizontal_response": {
            "gain": _float(row, "dynamic_horizontal_response_gain"),
            "target_local_x_scale": _float(row, "dynamic_target_local_x_scale"),
            "eye_local_x_scale": _float(row, "dynamic_eye_local_x_scale"),
        },
        "face_bias": _float(row, "face_bias"),
        "fog_profiles": fog,
        "evidence": {
            "preset_activation": "retail PS3 0x0015B524",
            "preset_interpolation": "retail PS3 0x0015BBA8",
            "projection_and_scene_transform": "retail PS3 0x00155300",
            "eye_offset_transform": "retail PS3 0x00157A10",
            "dynamic_response": "retail PS3 0x00157540",
            "face_bias_forwarding": "retail PS3 0x0015B910 -> 0x0020D69C/0x0020E984; Xbox 0x8214E120 -> virtual +0x18 (0x82475590) -> material +0x60 -> faceBias c9",
            "fog_uniforms": "retail PS3 0x003756AC vFogColor; 0x003756E8 fogRange",
        },
    }


def dynamic_horizontal_offsets(
    preset: Mapping[str, object] | int,
    runtime_x: float,
    runtime_y: float,
    *,
    table_path: str | Path | None = None,
) -> dict:
    """Evaluate the pre-transform local-X dynamic camera response.

    Retail 0x00157540 normalizes runtime coordinates as (x-213)/213 and
    (y-5)/228. Word 8 becomes max(0, gain/uniform_scale). Words 9 and 10
    separately scale target and eye local-X translations. The resulting local
    translations are subsequently transformed through the active stage/route
    frame by the game; this helper intentionally stops before that transform.
    """
    info = camera_preset_info(int(preset), table_path=table_path) if isinstance(preset, int) else dict(preset)
    scale = _f32(float(info["uniform_scene_view_scale"]))
    if scale == 0.0:
        raise ValueError("uniform scene/view scale is zero; retail gain division is undefined")
    dyn = info["dynamic_horizontal_response"]
    assert isinstance(dyn, Mapping)
    gain = _f32(float(dyn["gain"]))
    target_scale = _f32(float(dyn["target_local_x_scale"]))
    eye_scale = _f32(float(dyn["eye_local_x_scale"]))
    nx = _f32(_f32(float(runtime_x) - _f32(213.0)) / _f32(213.0))
    ny = _f32(_f32(float(runtime_y) - _f32(5.0)) / _f32(228.0))
    normalized_gain = _f32(gain / scale)
    if normalized_gain < 0.0:
        normalized_gain = 0.0
    common = _f32(_f32(nx * normalized_gain) * ny)
    target = _f32(common * target_scale)
    eye = _f32(common * eye_scale)
    return {
        "runtime_x": _f32(runtime_x),
        "runtime_y": _f32(runtime_y),
        "normalized_x": nx,
        "normalized_y": ny,
        "gain_over_uniform_scale_clamped": normalized_gain,
        "target_local_x": target,
        "eye_local_x": eye,
        "scope": "pre_stage_route_transform_local_x_response",
        "evidence": "retail PS3 0x00157540",
    }



def camera_world_state(
    preset: Mapping[str, object] | int,
    field_position: Sequence[float],
    orientation_matrix: Sequence[Sequence[float]],
    *,
    runtime_x: float | None = None,
    runtime_y: float | None = None,
    table_path: str | Path | None = None,
) -> dict:
    """Evaluate the proven procedural camera eye/target state in world space.

    This models the normal procedural-camera path only. Animated camera GMX
    mode (`cam1`/`int1`) bypasses the word-8/9/10 response and is intentionally
    outside this helper's scope.
    """
    info = camera_preset_info(int(preset), table_path=table_path) if isinstance(preset, int) else dict(preset)
    field = _vec3(field_position)
    eye_offset = _vec3(info["camera_eye_offset"])
    transformed_eye_offset = transform_row_vec3(eye_offset, orientation_matrix)
    base_eye = tuple(_f32(field[i] + transformed_eye_offset[i]) for i in range(3))
    base_target = field

    dynamic = None
    eye_dynamic_world = (0.0, 0.0, 0.0)
    target_dynamic_world = (0.0, 0.0, 0.0)
    if (runtime_x is None) != (runtime_y is None):
        raise ValueError("runtime_x and runtime_y must be supplied together")
    if runtime_x is not None:
        dynamic = dynamic_horizontal_offsets(info, runtime_x, runtime_y)
        scale = _f32(float(info["uniform_scene_view_scale"]))
        eye_local_scaled = (_f32(float(dynamic["eye_local_x"]) * scale), 0.0, 0.0)
        target_local_scaled = (_f32(float(dynamic["target_local_x"]) * scale), 0.0, 0.0)
        eye_dynamic_world = transform_row_vec3(eye_local_scaled, orientation_matrix)
        target_dynamic_world = transform_row_vec3(target_local_scaled, orientation_matrix)

    eye = tuple(_f32(base_eye[i] + eye_dynamic_world[i]) for i in range(3))
    target = tuple(_f32(base_target[i] + target_dynamic_world[i]) for i in range(3))
    return {
        "scope": "retail_procedural_camera_world_state",
        "preset_index": info.get("preset_index"),
        "field_position": list(field),
        "orientation_matrix_row_vector": [[_f32(float(v)) for v in row] for row in orientation_matrix],
        "base_eye": list(base_eye),
        "base_target": list(base_target),
        "eye_dynamic_world": list(eye_dynamic_world),
        "target_dynamic_world": list(target_dynamic_world),
        "eye": list(eye),
        "target": list(target),
        "fov_degrees": info["fov_degrees"],
        "fov_radians": info["fov_radians"],
        "uniform_scene_view_scale": info["uniform_scene_view_scale"],
        "scene_view_translation": info["scene_view_translation"],
        "fog_profiles": info["fog_profiles"],
        "face_bias": info["face_bias"],
        "dynamic_horizontal_response": dynamic,
        "evidence": {
            "eye_offset_transform": "retail PS3 0x00157A10",
            "dynamic_response": "retail PS3 0x00157540",
            "view_matrix_eye_target": "retail PS3 look-at consumer traced from 0x00155300",
        },
        "limitations": [
            "Animated camera GMX mode is not modeled; cam1/int1 replace procedural eye/target in that path.",
            "Camera preset activation timing is caller-supplied rather than inferred.",
            "Fog-profile selection timing is not modeled by this helper.",
        ],
    }
