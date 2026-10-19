"""Executable-backed SIIG 3D route resampling helpers.

This module reproduces the retail PS3 route segment code paths traced at
0x00158790 (linear), 0x00158A28 (Hermite), 0x00158D38 (curve setup),
0x00159298 (straight/curve classifier), and 0x0015A338/0x00159560
(initialization/advance).

The constant-spacing helper remains available for deterministic analysis.
RouteRuntimeState additionally reproduces the position/source-index portion of
the retail runtime advance path, including loop wrapping and linear mid-segment
spacing rebuilds. DAT timeline coupling is kept explicit rather than hidden.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import struct
from typing import Iterable, Sequence

Vec3 = tuple[float, float, float]

Mat3 = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]


def mat3_identity() -> Mat3:
    return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def mat3_mul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> Mat3:
    """3x3 matrix multiply for the retail row-vector transform convention."""
    return tuple(
        tuple(_f32(sum(_f32(float(a[r][k]) * float(b[k][c])) for k in range(3))) for c in range(3))
        for r in range(3)
    )  # type: ignore[return-value]


def transform_row_vec3(vector: Sequence[float], matrix: Sequence[Sequence[float]]) -> Vec3:
    """Transform a row vector as v' = v * M."""
    v = _vec3(vector)
    return tuple(
        _f32(sum(_f32(v[k] * float(matrix[k][c])) for k in range(3)))
        for c in range(3)
    )  # type: ignore[return-value]


def _rotation_x_row(angle: float) -> Mat3:
    c, s = _f32(math.cos(angle)), _f32(math.sin(angle))
    return ((1.0, 0.0, 0.0), (0.0, c, s), (0.0, _f32(-s), c))


def _rotation_y_row(angle: float) -> Mat3:
    c, s = _f32(math.cos(angle)), _f32(math.sin(angle))
    return ((c, 0.0, _f32(-s)), (0.0, 1.0, 0.0), (s, 0.0, c))


def _rotation_z_row(angle: float) -> Mat3:
    c, s = _f32(math.cos(angle)), _f32(math.sin(angle))
    return ((c, s, 0.0), (_f32(-s), c, 0.0), (0.0, 0.0, 1.0))


def route_orientation_matrix(
    pitch: float,
    yaw: float,
    roll: float,
    *,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    offset_z: float = 0.0,
) -> Mat3:
    """Build the retail procedural route orientation matrix.

    Retail PS3 composes row-vector rotation matrices in the order
    Rz(roll+offset_z) * Rx(pitch+offset_x) * Ry(yaw+offset_y).
    """
    rz = _rotation_z_row(_f32(roll + offset_z))
    rx = _rotation_x_row(_f32(pitch + offset_x))
    ry = _rotation_y_row(_f32(yaw + offset_y))
    return mat3_mul(mat3_mul(rz, rx), ry)

DIRECTION_NAMES = {
    0: "-Z",
    1: "+Z",
    2: "+X",
    3: "-X",
    4: "+Y",
    5: "-Y",
}

# The executable initializes duplicate 1.5-magnitude axis vectors for the
# two signs of each axis. The sign comes from the segment delta itself.
_DIRECTION_AXIS_VECTORS: dict[int, Vec3] = {
    0: (0.0, 0.0, 1.5),
    1: (0.0, 0.0, 1.5),
    2: (1.5, 0.0, 0.0),
    3: (1.5, 0.0, 0.0),
    4: (0.0, 1.5, 0.0),
    5: (0.0, 1.5, 0.0),
}


def _f32(value: float) -> float:
    return struct.unpack(">f", struct.pack(">f", float(value)))[0]


def _vec3(value: Sequence[float]) -> Vec3:
    if len(value) != 3:
        raise ValueError("route point must contain exactly three components")
    return (_f32(value[0]), _f32(value[1]), _f32(value[2]))


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (_f32(a[0] - b[0]), _f32(a[1] - b[1]), _f32(a[2] - b[2]))


def _distance(a: Vec3, b: Vec3) -> float:
    # Retail helper computes a normal Euclidean length. Keep the final value
    # at float precision because its consumer uses single-precision division.
    dx, dy, dz = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return _f32(math.sqrt(dx * dx + dy * dy + dz * dz))


def classify_curve(delta: Sequence[float]) -> bool:
    """Return True when retail FUN_00159298 chooses Hermite interpolation."""
    x, y, z = _vec3(delta)
    # atan2 results are converted to degrees as float and then truncated toward
    # zero to int before each modulo-90 test.
    angles = (
        int(_f32(_f32(math.atan2(y, x)) * _f32(180.0)) / _f32(math.pi)),
        int(_f32(_f32(math.atan2(y, z)) * _f32(180.0)) / _f32(math.pi)),
        int(_f32(_f32(math.atan2(z, x)) * _f32(180.0)) / _f32(math.pi)),
    )
    return not all(angle % 90 == 0 for angle in angles)


def update_direction_state(state: int, delta: Sequence[float]) -> int:
    """Reproduce the six-state tangent-axis transition logic."""
    if state not in DIRECTION_NAMES:
        raise ValueError(f"invalid route direction state: {state}")
    x, y, z = _vec3(delta)
    if state in (0, 1):
        if x < 0.0:
            return 3
        if x > 0.0:
            return 2
        if y < 0.0:
            return 5
        if y > 0.0:
            return 4
    elif state in (2, 3):
        if z < 0.0:
            return 0
        if z > 0.0:
            return 1
        if y < 0.0:
            return 5
        if y > 0.0:
            return 4
    else:  # 4 / 5
        if z < 0.0:
            return 0
        if z > 0.0:
            return 1
        if x < 0.0:
            return 3
        if x > 0.0:
            return 2
    return state


def _base_sample_count(p0: Vec3, p1: Vec3, spacing: float) -> int:
    spacing = _f32(spacing)
    if spacing <= 0.0:
        return 0
    count = int(_f32(_distance(p0, p1) / spacing))
    return count if count != 0 else 1


def resample_linear_segment(p0: Sequence[float], p1: Sequence[float], spacing: float) -> list[Vec3]:
    """Reproduce retail FUN_00158790 for one fixed-spacing segment.

    The game advances by delta/count *before* writing each sample, so P0 is not
    included. P1 is explicitly written into the final sample slot.
    """
    a, b = _vec3(p0), _vec3(p1)
    count = _base_sample_count(a, b, spacing)
    if count == 0:
        return []
    delta = _sub(b, a)
    inv = _f32(1.0 / float(count))
    step = (_f32(delta[0] * inv), _f32(delta[1] * inv), _f32(delta[2] * inv))
    cur = list(a)
    out: list[Vec3] = []
    for _ in range(count):
        cur[0] = _f32(cur[0] + step[0])
        cur[1] = _f32(cur[1] + step[1])
        cur[2] = _f32(cur[2] + step[2])
        out.append((cur[0], cur[1], cur[2]))
    out[-1] = b
    return out


def resample_curve_segment(
    p0: Sequence[float],
    p1: Sequence[float],
    p2: Sequence[float],
    spacing: float,
    direction_state: int,
) -> tuple[list[Vec3], int, Vec3, Vec3]:
    """Reproduce curve setup + cubic Hermite evaluation for one segment."""
    a, b, c = _vec3(p0), _vec3(p1), _vec3(p2)
    base = _base_sample_count(a, b, spacing)
    count = int(_f32(float(base) * _f32(1.3)))
    old_state = direction_state
    d01 = _sub(b, a)
    new_state = update_direction_state(old_state, d01)
    d12 = _sub(c, b)
    old_axis = _DIRECTION_AXIS_VECTORS[old_state]
    new_axis = _DIRECTION_AXIS_VECTORS[new_state]
    m0 = tuple(_f32(d01[i] * old_axis[i]) for i in range(3))
    m1 = tuple(_f32(d12[i] * new_axis[i]) for i in range(3))
    if count < 2:
        # Retail FUN_00158A28 logs and writes no points when sample count < 2.
        return [], new_state, m0, m1
    denom = float(count - 1)
    out: list[Vec3] = []
    for i in range(count):
        t = _f32(float(i) / denom)
        t2 = _f32(t * t)
        t3 = _f32(t2 * t)
        h00 = _f32(_f32(2.0 * t3) - _f32(3.0 * t2) + 1.0)
        h10 = _f32(t3 - _f32(2.0 * t2) + t)
        h01 = _f32(_f32(-2.0 * t3) + _f32(3.0 * t2))
        h11 = _f32(t3 - t2)
        point = tuple(
            _f32(_f32(_f32(a[k] * h00) + _f32(m0[k] * h10)) +
                 _f32(_f32(b[k] * h01) + _f32(m1[k] * h11)))
            for k in range(3)
        )
        out.append(point)
    return out, new_state, m0, m1


@dataclass
class RouteSegmentResult:
    segment_index: int
    source_endpoint_index: int
    lookahead_index: int
    interpolation: str
    direction_before: int
    direction_after: int
    sample_start: int
    sample_count: int
    start: Vec3
    end: Vec3
    lookahead: Vec3
    tangent_start: Vec3 | None = None
    tangent_end: Vec3 | None = None


def resample_route_constant_spacing(
    control_points: Iterable[Sequence[float]],
    initial_field_position: Sequence[float],
    spacing: float,
) -> dict:
    """Reproduce the retail non-loop route builder for a constant spacing.

    The game's real spacing is mutable and is driven by SCROLL_02. This helper
    intentionally freezes it to the supplied value so segment construction can
    be inspected deterministically.
    """
    controls = [_vec3(p) for p in control_points]
    initial = _vec3(initial_field_position)
    spacing = _f32(spacing)
    if spacing <= 0.0:
        raise ValueError("route spacing must be greater than zero")
    if len(controls) < 3:
        raise ValueError("retail route setup requires at least three source control points")

    # FUN_0015A338: direction state starts at -Z. If FieldPos equals source[0],
    # source indices begin 1/2/3; otherwise 0/1/2.
    direction = 0
    current_index = 1 if initial == controls[0] else 0
    next_index = current_index + 1
    lookahead_index = current_index + 2
    current_position = initial
    points: list[Vec3] = []
    segments: list[RouteSegmentResult] = []

    def append_segment(endpoint_index: int, tangent_lookahead_index: int) -> None:
        nonlocal current_position, direction
        endpoint = controls[endpoint_index]
        lookahead = controls[tangent_lookahead_index]
        delta = _sub(endpoint, current_position)
        before = direction
        start_offset = len(points)
        if classify_curve(delta):
            samples, direction_after, m0, m1 = resample_curve_segment(
                current_position, endpoint, lookahead, spacing, direction
            )
            kind = "cubic_hermite"
            direction = direction_after
        else:
            samples = resample_linear_segment(current_position, endpoint, spacing)
            m0 = m1 = None
            kind = "linear_equal_distance"
            # Straight segments do not execute the direction-state transition.
        points.extend(samples)
        segments.append(RouteSegmentResult(
            segment_index=len(segments), source_endpoint_index=endpoint_index,
            lookahead_index=tangent_lookahead_index, interpolation=kind,
            direction_before=before, direction_after=direction,
            sample_start=start_offset, sample_count=len(samples),
            start=current_position, end=endpoint, lookahead=lookahead,
            tangent_start=m0, tangent_end=m1,
        ))
        current_position = endpoint

    append_segment(current_index, next_index)

    # FUN_00159560: on non-loop routes, build another segment while the
    # consumed/source-current index is < source_count - 2. The final source
    # point therefore remains look-ahead context.
    consumed_index = current_index
    endpoint_index = next_index
    tangent_lookahead_index = lookahead_index
    while consumed_index < len(controls) - 2:
        append_segment(endpoint_index, tangent_lookahead_index)
        consumed_index += 1
        endpoint_index += 1
        tangent_lookahead_index += 1
        if tangent_lookahead_index >= len(controls):
            break

    return {
        "algorithm": "SIIG_RETAIL_ROUTE_CONSTANT_SPACING",
        "scope": "non_loop_constant_spacing",
        "spacing": spacing,
        "initial_field_position": list(initial),
        "initial_direction_state": 0,
        "initial_direction_name": DIRECTION_NAMES[0],
        "source_point_count": len(controls),
        "resampled_point_count": len(points),
        "source_points": [list(p) for p in controls],
        "points": [list(p) for p in points],
        "segments": [
            {
                **s.__dict__,
                "direction_before_name": DIRECTION_NAMES[s.direction_before],
                "direction_after_name": DIRECTION_NAMES[s.direction_after],
                "start": list(s.start), "end": list(s.end), "lookahead": list(s.lookahead),
                "tangent_start": list(s.tangent_start) if s.tangent_start is not None else None,
                "tangent_end": list(s.tangent_end) if s.tangent_end is not None else None,
            }
            for s in segments
        ],
        "untraversed_tail_source_points": [list(p) for p in controls[(segments[-1].source_endpoint_index + 1):]] if segments else [list(p) for p in controls],
        "limitations": [
            "Runtime SCROLL_02 can change spacing while the route is active; this export keeps spacing constant.",
            "Looping-route wrap behavior is intentionally not modeled by this helper.",
        ],
    }


def scroll02_spacing_from_script_y(script_y: int, frame_multiplier: int) -> float:
    """Convert the signed SCROLL_02 Y argument to route spacing per runtime update.

    Retail PS3 AnalyzeScroll02 (0x0014E408) computes signed integer
    ``(script_y * 30) / (frame_multiplier * 30)``, truncating toward zero,
    narrows the result to signed 16-bit, then multiplies by 1/256.
    """
    if frame_multiplier == 0:
        raise ValueError("frame multiplier must not be zero")
    y = int(script_y)
    # PPC divw truncates toward zero, unlike Python // for negative values.
    q = abs(y) // abs(int(frame_multiplier))
    if (y < 0) != (frame_multiplier < 0):
        q = -q
    q &= 0xFFFF
    if q & 0x8000:
        q -= 0x10000
    return _f32(float(q) * _f32(1.0 / 256.0))


@dataclass
class RuntimeRouteBuild:
    endpoint_counter: int
    endpoint_index: int
    lookahead_counter: int | None
    lookahead_index: int | None
    interpolation: str
    sample_count: int
    start: Vec3
    end: Vec3
    spacing: float
    direction_before: int
    direction_after: int
    reason: str


class RouteRuntimeState:
    """Position-only reproduction of the retail route runtime state machine.

    Evidence-backed scope:
    - initialization: retail PS3 0x0015A338
    - per-update advance/rebuild/loop behavior: 0x00159560
    - segment generation: 0x00158790 / 0x00158D38

    Orientation/scenegraph side effects at +0x38..+0x4C/+0x88 are intentionally
    not modeled here. This class reproduces route position sampling and source
    index/spacing state only.
    """

    def __init__(
        self,
        control_points: Iterable[Sequence[float]],
        initial_field_position: Sequence[float],
        spacing: float,
        *,
        loop: bool = False,
    ) -> None:
        self.controls = [_vec3(p) for p in control_points]
        if len(self.controls) < 3:
            raise ValueError("retail route runtime requires at least three source control points")
        self.current_position = _vec3(initial_field_position)
        self.spacing = _f32(spacing)
        self.previous_spacing = self.spacing
        self.loop = bool(loop)
        self.direction_state = 0
        # Procedural route orientation state. Retail initializes these to zero
        # and the matrix to identity; orientation is updated from movement
        # samples produced by Hermite segments before any next-segment build.
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.orientation_offset_x = 0.0
        self.orientation_offset_y = 0.0
        self.orientation_offset_z = 0.0
        self.pitch_locked = False
        self.orientation_matrix: Mat3 = mat3_identity()
        self.previous_position = self.current_position
        self.last_consumed_interpolation = "none"
        self.orientation_update_count = 0

        equal_first = self.current_position == self.controls[0]
        self.current_counter = 1 if equal_first else 0  # object +0x24
        self.next_counter = self.current_counter + 1      # object +0x28
        self.lookahead_counter = self.current_counter + 2 # object +0x2C

        self.generated_samples: list[Vec3] = []
        self.sample_index = 0
        self.interpolation = "none"
        self.finished = False
        self.update_count = 0
        self.builds: list[RuntimeRouteBuild] = []
        self.linear_spacing_rebuilds = 0

        # Initialization only builds when spacing != 0; the advance routine
        # itself rejects <=0. Match the observed init branch literally.
        if self.spacing != 0.0:
            self._build_initial_segment()

    def _source(self, counter: int) -> tuple[int, Vec3]:
        index = counter % len(self.controls) if self.loop else counter
        if index < 0 or index >= len(self.controls):
            raise IndexError(f"route source counter {counter} is outside non-loop source range")
        return index, self.controls[index]

    def _generate_segment(
        self,
        start: Vec3,
        endpoint_counter: int,
        lookahead_counter: int | None,
        *,
        reason: str,
        allow_curve: bool = True,
    ) -> None:
        endpoint_index, endpoint = self._source(endpoint_counter)
        before = self.direction_state
        delta = _sub(endpoint, start)
        is_curve = classify_curve(delta)
        lookahead_index: int | None = None
        lookahead: Vec3 | None = None
        if is_curve and allow_curve:
            if lookahead_counter is None:
                raise ValueError("Hermite route segment requires a look-ahead source point")
            lookahead_index, lookahead = self._source(lookahead_counter)
            samples, after, _m0, _m1 = resample_curve_segment(
                start, endpoint, lookahead, self.spacing, self.direction_state
            )
            self.direction_state = after
            interpolation = "cubic_hermite"
        else:
            samples = resample_linear_segment(start, endpoint, self.spacing)
            interpolation = "linear_equal_distance"
        self.generated_samples = samples
        self.sample_index = 0
        self.interpolation = interpolation
        self.builds.append(RuntimeRouteBuild(
            endpoint_counter=endpoint_counter,
            endpoint_index=endpoint_index,
            lookahead_counter=lookahead_counter if interpolation == "cubic_hermite" else lookahead_counter,
            lookahead_index=lookahead_index,
            interpolation=interpolation,
            sample_count=len(samples),
            start=start,
            end=endpoint,
            spacing=self.spacing,
            direction_before=before,
            direction_after=self.direction_state,
            reason=reason,
        ))

    def _build_initial_segment(self) -> None:
        # Init uses +0x24 as endpoint and +0x28 as Hermite look-ahead.
        self._generate_segment(
            self.current_position,
            self.current_counter,
            self.next_counter,
            reason="initialization",
        )

    def _can_build_next(self) -> bool:
        if self.loop:
            return True
        # Retail reduces +0x24 modulo source_count and compares it with
        # source_count - 2. In normal non-loop state +0x24 stays in range.
        current_index = self.current_counter % len(self.controls)
        return current_index < len(self.controls) - 2

    def _build_next_segment(self) -> bool:
        if not self._can_build_next():
            self.finished = True
            return False
        # Advance uses +0x28 endpoint and +0x2C look-ahead, modulo source count
        # in loop mode. It increments all three counters after generation.
        self._generate_segment(
            self.current_position,
            self.next_counter,
            self.lookahead_counter,
            reason="segment_advance",
        )
        self.current_counter += 1
        self.next_counter += 1
        self.lookahead_counter += 1
        return True

    def set_orientation_offsets(self, x: float, y: float, z: float) -> None:
        self.orientation_offset_x = _f32(x)
        self.orientation_offset_y = _f32(y)
        self.orientation_offset_z = _f32(z)
        self.orientation_matrix = route_orientation_matrix(
            self.pitch, self.yaw, self.roll,
            offset_x=self.orientation_offset_x,
            offset_y=self.orientation_offset_y,
            offset_z=self.orientation_offset_z,
        )

    def set_pitch_locked(self, locked: bool) -> None:
        self.pitch_locked = bool(locked)

    def _update_orientation_from_consumed_sample(self, interpolation: str) -> None:
        current = self.current_position
        previous = self.previous_position
        changed = current != previous
        if changed and interpolation == "cubic_hermite":
            dx = _f32(current[0] - previous[0])
            dy = _f32(current[1] - previous[1])
            dz = _f32(current[2] - previous[2])
            if dx != 0.0:
                self.yaw = _f32(math.atan2(_f32(-dz), dx) - _f32(math.pi / 2.0))
            if dz != 0.0 and not self.pitch_locked:
                self.pitch = _f32(math.atan2(dy, _f32(-dz)))
            self.orientation_matrix = route_orientation_matrix(
                self.pitch, self.yaw, self.roll,
                offset_x=self.orientation_offset_x,
                offset_y=self.orientation_offset_y,
                offset_z=self.orientation_offset_z,
            )
            self.orientation_update_count += 1
        # Retail tracks the previously consumed runtime position even when a
        # straight segment leaves the procedural angles unchanged.
        if changed:
            self.previous_position = current

    def set_spacing(self, spacing: float) -> None:
        self.spacing = _f32(spacing)

    def step(self, spacing: float | None = None) -> Vec3:
        """Advance one retail runtime update and return current FieldPos.

        A supplied ``spacing`` is applied before the update, matching a
        SCROLL_02 update having already written object +0x6C for that frame.
        """
        if spacing is not None:
            self.set_spacing(spacing)
        self.update_count += 1

        # 0x00159620..0x00159634: route position processing exits for <=0.
        if self.spacing <= 0.0:
            return self.current_position

        # Consume at most one generated position per runtime update. Capture
        # the interpolation type *before* any same-update next-segment build;
        # the orientation update belongs to the segment that produced the
        # consumed sample, not the newly prepared segment.
        produced_interpolation = self.interpolation
        consumed_sample = False
        if self.sample_index < len(self.generated_samples):
            self.current_position = self.generated_samples[self.sample_index]
            self.sample_index += 1
            consumed_sample = True
            self.last_consumed_interpolation = produced_interpolation
            self._update_orientation_from_consumed_sample(produced_interpolation)

        exhausted = self.sample_index >= len(self.generated_samples)
        if exhausted:
            # The same update that consumes the final point can prepare the
            # next segment, but does not consume its first point until the next
            # runtime update.
            self._build_next_segment()
        elif self.spacing != self.previous_spacing and self.interpolation == "linear_equal_distance":
            # Mid-segment spacing changes rebuild the remaining *linear* path
            # from current FieldPos to the same endpoint (+0x24). Curves skip
            # this branch entirely.
            endpoint_counter = self.current_counter
            self._generate_segment(
                self.current_position,
                endpoint_counter,
                None,
                reason="linear_spacing_change",
                allow_curve=False,
            )
            self.linear_spacing_rebuilds += 1

        # 0x00159D0C: previous spacing is updated only while current segment
        # is classified linear. For curves it deliberately remains unchanged.
        if self.interpolation == "linear_equal_distance":
            self.previous_spacing = self.spacing
        return self.current_position

    def snapshot(self) -> dict:
        return {
            "current_position": list(self.current_position),
            "spacing": self.spacing,
            "previous_spacing": self.previous_spacing,
            "loop": self.loop,
            "direction_state": self.direction_state,
            "direction_name": DIRECTION_NAMES[self.direction_state],
            "source_counters": {
                "current_0x24": self.current_counter,
                "next_0x28": self.next_counter,
                "lookahead_0x2c": self.lookahead_counter,
            },
            "generated_sample_count": len(self.generated_samples),
            "generated_sample_index": self.sample_index,
            "interpolation": self.interpolation,
            "finished": self.finished,
            "update_count": self.update_count,
            "linear_spacing_rebuilds": self.linear_spacing_rebuilds,
            "build_count": len(self.builds),
            "last_consumed_interpolation": self.last_consumed_interpolation,
            "orientation": {
                "pitch_radians": self.pitch,
                "yaw_radians": self.yaw,
                "roll_radians": self.roll,
                "offset_x_radians": self.orientation_offset_x,
                "offset_y_radians": self.orientation_offset_y,
                "offset_z_radians": self.orientation_offset_z,
                "pitch_locked": self.pitch_locked,
                "matrix_row_vector": [list(row) for row in self.orientation_matrix],
                "previous_position": list(self.previous_position),
                "update_count": self.orientation_update_count,
            },
        }
