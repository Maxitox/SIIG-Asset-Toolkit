#!/usr/bin/env python3
"""Offline SIIG visualizer simulator.

The dev24 renderer keeps recovered data and approximated rendering separate:

* DAT timing/state is decoded from the game.
* The 29-value ParameterSet row, 57 SequenceSet slots and exact ten-SHAPE
  resource order are recovered facts.
* June 10 Visualizer Check Mode code now grounds the debug control surface:
  VolumeSet 0=from BGM / 1=from Stick, X clears the feedback surface, Y toggles
  debug text, and all numeric control ranges/defaults are recovered from the
  executable's 30-row menu table.
* Fix Rotation is a signed angle override, not a boolean.  Zero leaves the
  normal accumulated SHAPE rotation path active; a non-zero value supplies the
  fixed angle used by the source-image transform.
* May 11/June-era executable tracing recovers the 1280x720 feedback target,
  128x128 source-image footprint, SHAPE-first draw order, feedback-only
  magnification, and exact Position Fix table.  WIP170 corrected the browser bridge to the
  game's center-origin, +Y-up position convention; WIP171 then recovered the
  runtime-patched 3x3 fixed-position grid without aliasing raw presets. WIP191 temporarily applied a 1.5x logical-to-target hypothesis. WIP195
  supersedes that scale after the project owner's stage 4-5 hardware capture
  proved authored Y=+360 must still inject the 128x128 source at the top edge.
  Position values therefore map directly to target pixels again. WIP197 closes
  that global scale independently in June 10 `Function_82177DF0`, which passes
  X/640 and Y/360 into the 1280x720 render path. A research-only anchor/source
  bounds overlay is provided for measuring any remaining capture/pivot mismatch
  without changing native coordinates.
* June 10 VisualizerScript tracing also closes `VL_CHANGETIME`: it stores a
  SequenceSet change-threshold range, rolls `[min,max)` with the game's CRT RNG,
  advances only after `threshold < counter`, wraps on `-1`, and applies the newly
  armed ParameterSet on the following active update.
* June 10 audio tracing recovers VolumeSet/BGM as the arithmetic mean of the
  two XAudio2 volume-meter peak levels.  Microsoft documents Xbox 360 XAudio2
  graph processing as 5 1/3 ms per quantum; at SIIG's 48 kHz BGM rate that is
  exactly 256 samples, and pPeakLevels is the maximum absolute level during one
  processing pass.  Dedicated Visualizer Check Mode feeds that raw linear float
  directly into the parameter interpolator.  Normal stage playback instead
  applies the recovered VisualizerScript adaptive normalizer: a 300-update
  min/max window produces VOL SCALE, while 180-update RAW/SCALE histories feed
  the on-hardware diagnostic averages.
* ParameterSet.nut and SequenceSet.nut are parsed from a supplied rip when
  available.  Their proprietary rows are never bundled into the source-only
  toolkit.

Proprietary SHAPE pixels can now be consumed from a user-supplied full rip but
are never bundled.  Their serialized Xbox TEX headers also prove point-filtered
sampling with repeat addressing, matching the generic SIIG TEX fetch-constant
decoder.  The ordinary ScreenSprite source shader is also recovered as sampled
SHAPE RGBA multiplied by runtime float4 tint RGBA with SrcAlpha/OneMinusSrcAlpha
source-over blending, while EffectBlur RGB sample/blend math is independently
closed.  The Xbox 360 XAudio2 meter window is now fixed at one 256-sample /
5 1/3 ms processing quantum at 48 kHz.  Remaining browser boundaries are the
absolute phase of browser playback-time lookup relative to native quantum boundaries and
bit-exact Xenos render-target alpha storage/compositing.
"""
from __future__ import annotations

import base64
import concurrent.futures
import json
import re
import shutil
import subprocess
from pathlib import Path

import siig_toolkit as toolkit

VISUALIZER_SIMULATOR_VERSION = 24

VISUALIZER_OPCODES = set(range(0xC8, 0xCF))
MAX_SCRIPT_BYTES = 8 * 1024 * 1024
MAX_NUT_BYTES = 2 * 1024 * 1024

# Exact resource order recovered from visualizer.bin.
SHAPE_RESOURCES = (
    "WhiteCircle",
    "line",
    "3line",
    "square",
    "triangle",
    "WhiteCircle2",
    "line2",
    "3line2",
    "square2",
    "triangle2",
)

# VisualizerMain constructs a 1280x720 render target; each of the ten source
# images is instantiated as 128x128.  The fixed-position table is read by the
# feedback/source renderer when Position Fix is non-zero.
RENDER_TARGET_SIZE = (1280, 720)
SHAPE_TEXTURE_SIZE = (128, 128)
# WIP195 restored direct target-pixel positioning after stage 4-5 disproved
# WIP191's extra 1.5x multiplier. WIP197 strengthens this from regression
# evidence to an executable-backed contract: June 10 Function_82177DF0 feeds
# X * 1/640 and Y * 1/360 to the 1280x720 renderer, i.e. each authored
# position unit is one target pixel around the center-origin half-extents.
POSITION_LOGICAL_TO_TARGET_SCALE = 1.0
BGM_PREVIEW_CACHE_VERSION = 1
DISPLAY_RESOLVE_SIZE = (640, 360)
# The executable image contains the horizontal columns immediately, while a
# startup initializer patches the upper/lower Y rows into the writable table.
# C39A0000 is -308.0: the initializer writes +308 to raw 1..3 and -308 to
# raw 7..9.  Raw 4..6 remain Y=0.  Raw 0 is special in VisualizerMain: it
# selects Position Free X/Y instead of the fixed table, although the table's
# default entry itself is (0,0).
POSITION_FIX_COORDS = (
    (0.0, 0.0),
    (-448.0, 308.0),
    (0.0, 308.0),
    (448.0, 308.0),
    (-448.0, 0.0),
    (0.0, 0.0),
    (448.0, 0.0),
    (-448.0, -308.0),
    (0.0, -308.0),
    (448.0, -308.0),
)

# WIP170 incorrectly treated the zero-filled pre-constructor Y words as final
# data and collapsed rows into aliases.  Preserve this compatibility symbol as
# an identity map so existing callers keep working, but never collapse raw
# Position Fix values: all 1..9 are distinct runtime presets.
POSITION_FIX_CANONICAL_INDICES = tuple(range(10))
POSITION_FIX_CHOICES = (
    {"canonical_index": 0, "raw_indices": (0,), "label": "Free X/Y", "coord": (0.0, 0.0)},
    {"canonical_index": 1, "raw_indices": (1,), "label": "Upper left", "coord": (-448.0, 308.0)},
    {"canonical_index": 2, "raw_indices": (2,), "label": "Upper center", "coord": (0.0, 308.0)},
    {"canonical_index": 3, "raw_indices": (3,), "label": "Upper right", "coord": (448.0, 308.0)},
    {"canonical_index": 4, "raw_indices": (4,), "label": "Middle left", "coord": (-448.0, 0.0)},
    {"canonical_index": 5, "raw_indices": (5,), "label": "Fixed center", "coord": (0.0, 0.0)},
    {"canonical_index": 6, "raw_indices": (6,), "label": "Middle right", "coord": (448.0, 0.0)},
    {"canonical_index": 7, "raw_indices": (7,), "label": "Lower left", "coord": (-448.0, -308.0)},
    {"canonical_index": 8, "raw_indices": (8,), "label": "Lower center", "coord": (0.0, -308.0)},
    {"canonical_index": 9, "raw_indices": (9,), "label": "Lower right", "coord": (448.0, -308.0)},
)


def canonical_position_fix_index(raw_index: int | float) -> int:
    """Clamp Position Fix to the native raw 0..9 range without aliasing."""
    return max(0, min(9, int(round(float(raw_index)))))


def visualizer_canvas_position(
    x: float,
    y: float,
    *,
    width: int = RENDER_TARGET_SIZE[0],
    height: int = RENDER_TARGET_SIZE[1],
) -> tuple[float, float]:
    """Map SIIG logical Visualizer coordinates to the 1280x720 Canvas target.

    Coordinates are center-origin with +X right / +Y up and are target-pixel
    offsets at the native 1280x720 surface. For alternate output sizes they
    scale only with the output height. WIP195 restores this direct mapping after
    stage 4-5 hardware disproved WIP191's extra 1.5x multiplier.
    """
    scale = POSITION_LOGICAL_TO_TARGET_SCALE * (float(height) / float(RENDER_TARGET_SIZE[1]))
    return (float(width) * 0.5 + float(x) * scale, float(height) * 0.5 - float(y) * scale)

# June 10 VisualizerScript constructor/update path:
# Function_82177510 creates a 300-float adaptive range window and 180-float
# diagnostic RAW/SCALE histories. Function_821773F0 refreshes extrema only
# when the 300-sample write index wraps, guards a sub-0.001 span, and maps the
# current raw stereo-peak mean to VOL SCALE. Function_82175FA8 refreshes the
# diagnostic 180-sample averages when their ring wraps.
GAMEPLAY_VOLUME_WINDOW = 300
GAMEPLAY_DIAGNOSTIC_HISTORY = 180
GAMEPLAY_VOLUME_MIN_SPAN = 0.001

# Public XAudio2 documentation fixes the Xbox 360 audio-graph quantum at
# 5 1/3 ms. SIIG browser previews are normalized to 48 kHz, therefore one
# native processing pass is exactly 256 samples. XAUDIO2FX_VOLUMEMETER_LEVELS
# defines pPeakLevels as the maximum absolute level during a processing pass.
# The remaining browser approximation is query phase/scheduling, not window size.
XBOX360_XAUDIO2_SAMPLE_RATE = 48000
XBOX360_XAUDIO2_QUANTUM_MS = 16.0 / 3.0
XBOX360_XAUDIO2_QUANTUM_SAMPLES = 256

# Exact June 10 VisualizerScript SequenceSet change-timing contract.
# Constructor defaults both bounds to 18000.  VL_CHANGETIME (0xCD) replaces
# the inclusive lower / exclusive upper threshold range, and the current
# threshold is re-rolled immediately.  When both bounds are equal the fixed
# value is used.  The game RNG is the Xbox CRT LCG: state = state*0x343FD +
# 0x269EC3 (mod 2^32), rand15=(state>>16)&0x7FFF.  Visualizer change timing
# calls the wrapper that concatenates two rand15 results into one 30-bit value.
VISUALIZER_CHANGE_TIME_DEFAULT = 18000
VISUALIZER_RNG_MULTIPLIER = 0x343FD
VISUALIZER_RNG_INCREMENT = 0x269EC3

def visualizer_rng30_step(state: int) -> tuple[int, int]:
    """Advance SIIG's CRT RNG twice and return its 30-bit Visualizer value."""
    state = (int(state) * VISUALIZER_RNG_MULTIPLIER + VISUALIZER_RNG_INCREMENT) & 0xFFFFFFFF
    high = (state >> 16) & 0x7FFF
    state = (state * VISUALIZER_RNG_MULTIPLIER + VISUALIZER_RNG_INCREMENT) & 0xFFFFFFFF
    low = (state >> 16) & 0x7FFF
    return state, low | (high << 15)

def visualizer_change_time_pick(state: int, minimum: int, maximum: int) -> tuple[int, int]:
    """Return the native change threshold and updated RNG state.

    Function_82175CC0 uses ``minimum + random % (maximum-minimum)`` when
    the span is non-zero, so the upper bound is exclusive.  Equal bounds use
    the fixed lower value and consume no RNG call.
    """
    minimum = int(minimum)
    maximum = int(maximum)
    if maximum < minimum:
        raise ValueError('Visualizer change-time maximum must be >= minimum')
    span = maximum - minimum
    if span == 0:
        return int(state) & 0xFFFFFFFF, minimum
    state, value = visualizer_rng30_step(state)
    return state, minimum + (value % span)

def visualizer_sequence_parameter_trace(sequence, update_count: int, *, minimum: int = VISUALIZER_CHANGE_TIME_DEFAULT, maximum: int = VISUALIZER_CHANGE_TIME_DEFAULT, seed: int = 1) -> list[int | None]:
    """Reference SequenceSet stepping for active Visualizer update ticks.

    This mirrors Function_82177648: the current row is applied when the dirty
    flag is set, then the per-sequence counter is compared with the selected
    threshold.  A row change is armed once ``threshold < counter``; the next
    parameter is applied on the following active update.  ``-1`` terminates the
    authored list and wraps to entry zero.
    """
    row = [int(v) for v in sequence]
    if not row:
        return [None] * max(0, int(update_count))
    state = int(seed) & 0xFFFFFFFF
    state, threshold = visualizer_change_time_pick(state, minimum, maximum)
    index = 0
    counter = 0
    dirty = True
    current = None
    out = []
    for _ in range(max(0, int(update_count))):
        if dirty:
            dirty = False
            value = row[index] if index < len(row) else -1
            if value < 0:
                index = 0
                value = row[0] if row else -1
            current = value if value >= 0 else None
        if threshold < counter:
            index += 1
            if index >= len(row) or row[index] == -1:
                index = 0
            counter = 0
            dirty = True
            state, threshold = visualizer_change_time_pick(state, minimum, maximum)
        else:
            counter += 1
        out.append(current)
    return out


def gameplay_volume_normalizer_trace(
    samples: list[float] | tuple[float, ...],
    *,
    window_samples: int = GAMEPLAY_VOLUME_WINDOW,
) -> list[dict]:
    """Reference the recovered June-10 normal-stage BGM normalizer.

    This intentionally models the game-side post-meter logic only.  ``samples``
    are the already-recovered linear stereo peak averages returned by the XAudio2
    meter bridge.  Exact upstream XAudio2 meter window/cadence remains external.
    """
    window_samples = max(5, int(window_samples))
    window = [0.0] * window_samples
    raw_hist = [0.0] * GAMEPLAY_DIAGNOSTIC_HISTORY
    scale_hist = [0.0] * GAMEPLAY_DIAGNOSTIC_HISTORY
    wi = 0
    hi = 0
    minimum = 0.0
    maximum = 1.0
    scale = 1.0
    ave_raw = 0.0
    ave_scale = 0.0
    out: list[dict] = []
    for value in samples:
        raw = float(value)
        raw_hist[hi] = raw
        clamped = min(1.0, max(0.0, raw))
        window[wi] = clamped
        wi += 1
        if wi >= window_samples:
            wi = 0
        if wi == 0:
            ordered = sorted(window)
            minimum = ordered[0]
            maximum = ordered[-1]
            if abs(maximum - minimum) < GAMEPLAY_VOLUME_MIN_SPAN:
                if maximum < GAMEPLAY_VOLUME_MIN_SPAN or minimum <= 0.999:
                    maximum = minimum + GAMEPLAY_VOLUME_MIN_SPAN
                else:
                    minimum = maximum - GAMEPLAY_VOLUME_MIN_SPAN
        if raw < minimum:
            scale = 0.0
        elif raw > maximum:
            scale = 1.0
        else:
            span = max(abs(maximum - minimum), GAMEPLAY_VOLUME_MIN_SPAN)
            scale = (raw - minimum) / span
        scale_hist[hi] = scale
        hi += 1
        if hi >= GAMEPLAY_DIAGNOSTIC_HISTORY:
            hi = 0
            # Function_82175FA8 does not clear the prior display average before
            # accumulating, so preserve its tiny 1/180 carry exactly.
            ave_raw = (ave_raw + sum(raw_hist)) / GAMEPLAY_DIAGNOSTIC_HISTORY
            ave_scale = (ave_scale + sum(scale_hist)) / GAMEPLAY_DIAGNOSTIC_HISTORY
        out.append({
            "raw": raw,
            "minimum": minimum,
            "maximum": maximum,
            "scale": scale,
            "average_raw": ave_raw,
            "average_scale": ave_scale,
            "window_index": wi,
            "history_index": hi,
        })
    return out

# 29 serialized ParameterSet values.  Position Free is one debug-menu row but
# serializes as two numbers, which is why the menu has 28 parameter rows while
# the NUT row width is 29.
PARAMETER_FIELDS = (
    "magnify_scale_x_min",
    "magnify_scale_x_max",
    "magnify_scale_y_min",
    "magnify_scale_y_max",
    "magnify_a_min",
    "magnify_a_max",
    "bg_r",
    "bg_g",
    "bg_b",
    "bg_a",
    "shape",
    "position_fix",
    "position_free_x",
    "position_free_y",
    "rotation_base",
    "add_rotation",
    "fix_rotation",
    "scale_x_min",
    "scale_x_max",
    "scale_y_min",
    "scale_y_max",
    "rgb_r_min",
    "rgb_r_max",
    "rgb_g_min",
    "rgb_g_max",
    "rgb_b_min",
    "rgb_b_max",
    "rgb_a_min",
    "rgb_a_max",
)

# June 10 executable VisualizerCheckMode menu table at 0x82574550.  Integer
# storage scaling is normalized here to the values printed by the game's own
# format strings.  The free-position bounds come from Function_821839B8.
VISUALIZER_CHECK_CONTROLS = {
    "volume_source": {"default": 1, "min": 0, "max": 1, "options": ["from BGM", "from Stick"]},
    "bgm_index": {"default": 0, "min": 0, "max": 50, "step": 1},
    "magnify_scale_x_min": {"default": 1.03, "min": 0.8, "max": 2.0, "step": 0.001},
    "magnify_scale_x_max": {"default": 1.03, "min": 0.8, "max": 2.0, "step": 0.001},
    "magnify_scale_y_min": {"default": 1.03, "min": 0.8, "max": 2.0, "step": 0.001},
    "magnify_scale_y_max": {"default": 1.03, "min": 0.8, "max": 2.0, "step": 0.001},
    "magnify_a_min": {"default": 1.0, "min": 0.7, "max": 1.0, "step": 0.001},
    "magnify_a_max": {"default": 1.0, "min": 0.7, "max": 1.0, "step": 0.001},
    "bg_r": {"default": 0, "min": 0, "max": 255, "step": 1},
    "bg_g": {"default": 0, "min": 0, "max": 255, "step": 1},
    "bg_b": {"default": 0, "min": 0, "max": 255, "step": 1},
    "bg_a": {"default": 0, "min": 0, "max": 255, "step": 1},
    "shape": {"default": 0, "min": 0, "max": 9, "step": 1},
    "position_fix": {"default": 0, "min": 0, "max": 9, "step": 1},
    "position_free_x": {"default": 0, "min": -560, "max": 560, "step": 1},
    "position_free_y": {"default": 0, "min": -360, "max": 360, "step": 1},
    "rotation_base": {"default": 0.1, "min": -365.0, "max": 365.0, "step": 0.1},
    "add_rotation": {"default": 0.0, "min": -730.0, "max": 730.0, "step": 0.1},
    "fix_rotation": {"default": 0.0, "min": -365.0, "max": 365.0, "step": 0.1},
    "scale_x_min": {"default": 1.0, "min": 0.01, "max": 4.0, "step": 0.001},
    "scale_x_max": {"default": 1.0, "min": 0.01, "max": 4.0, "step": 0.001},
    "scale_y_min": {"default": 1.0, "min": 0.01, "max": 4.0, "step": 0.001},
    "scale_y_max": {"default": 1.0, "min": 0.01, "max": 4.0, "step": 0.001},
    "rgb_r_min": {"default": 128, "min": 0, "max": 255, "step": 1},
    "rgb_r_max": {"default": 255, "min": 0, "max": 255, "step": 1},
    "rgb_g_min": {"default": 0, "min": 0, "max": 255, "step": 1},
    "rgb_g_max": {"default": 0, "min": 0, "max": 255, "step": 1},
    "rgb_b_min": {"default": 0, "min": 0, "max": 255, "step": 1},
    "rgb_b_max": {"default": 0, "min": 0, "max": 255, "step": 1},
    "rgb_a_min": {"default": 255, "min": 0, "max": 255, "step": 1},
    "rgb_a_max": {"default": 255, "min": 0, "max": 255, "step": 1},
}


def _find_media(input_path: Path) -> Path | None:
    candidates = (
        input_path / "assets" / "Media",
        input_path / "Media",
        input_path / "assets" / "USRDIR",
        input_path / "USRDIR",
        input_path,
    )
    for candidate in candidates:
        if (candidate / "script").is_dir():
            return candidate
    return None


def _visualizer_timelines(input_path: Path | None) -> list[dict]:
    if input_path is None:
        return []
    media = _find_media(input_path)
    if media is None:
        return []
    result: list[dict] = []
    for path in sorted((media / "script").glob("*.dat"), key=lambda p: p.name.lower()):
        try:
            if path.stat().st_size > MAX_SCRIPT_BYTES:
                continue
            parsed = toolkit.parse_dat_bytes(path.read_bytes())
        except Exception:
            continue
        events = []
        for record in parsed["records"]:
            if record["opcode"] not in VISUALIZER_OPCODES:
                continue
            events.append({
                "frame": record["absolute_frame"],
                "opcode": record["opcode_name"],
                "args": record["args_signed"],
                "fields": record["semantic"]["fields"],
            })
        if events:
            result.append({
                "script": path.name,
                "duration_frames": parsed["duration_frames"],
                "events": events,
            })
    return result


def _find_visualizer_set_file(input_path: Path | None, name: str) -> Path | None:
    if input_path is None or not input_path.exists():
        return None
    candidates = (
        input_path / name,
        input_path / "visualizerSet" / name,
        input_path / "assets" / "visualizerSet" / name,
        input_path / "assets" / "Media" / "visualizerSet" / name,
        input_path / "Media" / "visualizerSet" / name,
        input_path / "converted_assets" / "visualizerSet" / name,
    )
    for path in candidates:
        if path.is_file() and path.stat().st_size <= MAX_NUT_BYTES:
            return path
    try:
        for path in input_path.rglob(name):
            if path.is_file() and path.stat().st_size <= MAX_NUT_BYTES:
                return path
    except OSError:
        return None
    return None


def _parse_nut_number(token: str) -> int | float:
    token = token.strip()
    if not token:
        raise ValueError("empty NUT number")
    value = float(token)
    if not any(ch in token.lower() for ch in (".", "e")) and value.is_integer():
        return int(value)
    return value


def _parse_nut_rows(text: str, prefix: str) -> list[list[int | float]]:
    pattern = re.compile(rf"\b{re.escape(prefix)}_(\d+)\s*<-\s*\[([^\]]*)\]", re.MULTILINE)
    rows: dict[int, list[int | float]] = {}
    for match in pattern.finditer(text):
        index = int(match.group(1))
        values = [_parse_nut_number(token) for token in match.group(2).split(",") if token.strip()]
        rows[index] = values
    if not rows:
        return []
    maximum = max(rows)
    return [rows.get(i, []) for i in range(maximum + 1)]


def _visualizer_sets(input_path: Path | None) -> dict:
    parameter_path = _find_visualizer_set_file(input_path, "ParameterSet.nut")
    sequence_path = _find_visualizer_set_file(input_path, "SequenceSet.nut")
    parameter_rows: list[list[int | float]] = []
    sequence_rows: list[list[int | float]] = []
    try:
        if parameter_path is not None:
            parameter_rows = _parse_nut_rows(parameter_path.read_text(encoding="utf-8", errors="replace"), "PARAM")
    except (OSError, ValueError):
        parameter_rows = []
    try:
        if sequence_path is not None:
            sequence_rows = _parse_nut_rows(sequence_path.read_text(encoding="utf-8", errors="replace"), "SEQUENCE")
    except (OSError, ValueError):
        sequence_rows = []
    parameter_sets = []
    for index, values in enumerate(parameter_rows):
        if len(values) != len(PARAMETER_FIELDS):
            continue
        parameter_sets.append({"id": index, "values": values})
    sequence_sets = []
    for index, values in enumerate(sequence_rows):
        if not values:
            continue
        sequence_sets.append({"id": index, "parameter_ids": [int(value) for value in values]})
    return {
        "parameter_sets": parameter_sets,
        "sequence_sets": sequence_sets,
        "source_files": [name for name, path in (("ParameterSet.nut", parameter_path), ("SequenceSet.nut", sequence_path)) if path is not None],
    }


def _timeline_presets(timelines: list[dict], sequence_sets: list[dict]) -> list[dict]:
    sequence_map = {item["id"]: [value for value in item["parameter_ids"] if value >= 0] for item in sequence_sets}
    presets: list[dict] = []
    for timeline in timelines:
        for event in timeline.get("events", []):
            if event.get("opcode") != "VL_SEQUENCESET" or not event.get("args"):
                continue
            sequence_id = int(event["args"][0])
            presets.append({
                "script": timeline["script"],
                "frame": int(event["frame"]),
                "sequence_id": sequence_id,
                "parameter_ids": sequence_map.get(sequence_id, []),
            })
    return presets


def _shape_image_payloads(input_path: Path | None) -> dict[str, str]:
    """Find converted retail Visualizer SHAPE PNGs in a user-supplied rip.

    Proprietary pixels are never part of the source package.  When the user
    builds the simulator from a full rip, the already-converted PNGs can be
    embedded into that *local generated HTML* so the source-image morphology
    is exact.
    """
    if input_path is None or not input_path.exists():
        return {}
    roots = [input_path] if input_path.is_dir() else [input_path.parent]
    candidates: dict[str, Path] = {}
    for scan_root in roots:
        for path in scan_root.rglob("*.png"):
            if path.stem not in SHAPE_RESOURCES:
                continue
            # Avoid same-named unrelated resources outside the Visualizer
            # extraction tree.
            if "visualizer" not in {part.lower() for part in path.parts}:
                continue
            candidates.setdefault(path.stem, path)
    payloads: dict[str, str] = {}
    for name in SHAPE_RESOURCES:
        path = candidates.get(name)
        if path is None:
            continue
        data = path.read_bytes()
        # Minimal PNG identity + recovered 128x128 source contract.
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            continue
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        if (width, height) != SHAPE_TEXTURE_SIZE:
            continue
        payloads[name] = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
    return payloads



NATIVE_BGM_EXTENSIONS = {
    ".wma": "Xbox 360 WMA",
    ".at3": "PS3 AT3/ATRAC3+",
}


def _bgm_roots(input_path: Path | None) -> list[Path]:
    if input_path is None or not input_path.exists():
        return []
    candidates = (
        input_path / "ready_files" / "Media" / "BGM",
        input_path / "ready_files" / "USRDIR" / "BGM",
        input_path / "assets" / "Media" / "BGM",
        input_path / "assets" / "USRDIR" / "BGM",
        input_path / "Media" / "BGM",
        input_path / "USRDIR" / "BGM",
        input_path / "BGM",
    )
    result: list[Path] = []
    seen: set[str] = set()
    for root in candidates:
        try:
            if not root.is_dir():
                continue
            key = str(root.resolve())
        except OSError:
            continue
        if key in seen:
            continue
        seen.add(key)
        result.append(root)
    return result


def _ffmpeg_preview_codec(ffmpeg: str) -> tuple[str, str, list[str]]:
    """Return (extension, label, encoder args) for a browser-safe preview."""
    try:
        proc = subprocess.run(
            [ffmpeg, "-nostdin", "-hide_banner", "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
            check=False,
        )
        if "libmp3lame" in (proc.stdout or ""):
            return ".mp3", "MP3", ["-c:a", "libmp3lame", "-q:a", "5"]
    except (OSError, subprocess.SubprocessError):
        pass
    # FFmpeg's native AAC encoder is present in normal builds and gives us a
    # dependency-light fallback when libmp3lame is unavailable.
    return ".m4a", "AAC/M4A", ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"]


def _ffmpeg_peak_envelope(ffmpeg: str, source: Path) -> dict | None:
    """Decode one user-owned track to the native 48 kHz stereo meter domain.

    The browser simulator runs at 60 Hz, but the recovered Xbox meter is one
    256-sample XAudio2 processing quantum.  Store one unsigned byte per
    channel per native quantum (187.5 Hz) and select the latest quantum by
    HTMLMediaElement.currentTime.  This avoids routing local file:// media
    through MediaElementAudioSourceNode, which can become silent under browser
    origin/CORS rules.  The 8-bit envelope is presentation/meter support only;
    original game audio bytes remain untouched.
    """
    command = [
        ffmpeg,
        "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(source), "-map", "0:a:0", "-vn",
        "-ac", "2", "-ar", str(XBOX360_XAUDIO2_SAMPLE_RATE),
        "-f", "s16le", "-acodec", "pcm_s16le", "-",
    ]
    proc = None
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        assert proc.stdout is not None
        quantum_bytes = XBOX360_XAUDIO2_QUANTUM_SAMPLES * 2 * 2
        envelope = bytearray()
        pending = bytearray()
        while True:
            chunk = proc.stdout.read(64 * 1024)
            if not chunk:
                break
            pending.extend(chunk)
            while len(pending) >= quantum_bytes:
                block = pending[:quantum_bytes]
                del pending[:quantum_bytes]
                peak_l = 0
                peak_r = 0
                for off in range(0, quantum_bytes, 4):
                    left = int.from_bytes(block[off:off+2], "little", signed=True)
                    right = int.from_bytes(block[off+2:off+4], "little", signed=True)
                    peak_l = max(peak_l, abs(left))
                    peak_r = max(peak_r, abs(right))
                envelope.append(min(255, round(peak_l * 255 / 32768)))
                envelope.append(min(255, round(peak_r * 255 / 32768)))
        if pending:
            pending.extend(b"\x00" * (quantum_bytes - len(pending)))
            peak_l = 0
            peak_r = 0
            for off in range(0, quantum_bytes, 4):
                left = int.from_bytes(pending[off:off+2], "little", signed=True)
                right = int.from_bytes(pending[off+2:off+4], "little", signed=True)
                peak_l = max(peak_l, abs(left))
                peak_r = max(peak_r, abs(right))
            envelope.append(min(255, round(peak_l * 255 / 32768)))
            envelope.append(min(255, round(peak_r * 255 / 32768)))
        code = proc.wait(timeout=30)
        if code != 0 or not envelope:
            return None
        return {
            "encoding": "u8_stereo_peak_b64",
            "sample_rate_hz": XBOX360_XAUDIO2_SAMPLE_RATE,
            "quantum_samples": XBOX360_XAUDIO2_QUANTUM_SAMPLES,
            "channels": 2,
            "quantum_count": len(envelope) // 2,
            "data_b64": base64.b64encode(envelope).decode("ascii"),
        }
    except (OSError, subprocess.SubprocessError):
        if proc is not None:
            try:
                proc.kill()
            except OSError:
                pass
        return None


def _bgm_cache_source_key(path: Path, input_path: Path | None) -> str:
    """Return a privacy-safe, rip-relative cache key when possible."""
    if input_path is not None:
        try:
            return path.resolve().relative_to(Path(input_path).resolve()).as_posix()
        except (OSError, ValueError):
            pass
    return path.name


def _valid_meter_envelope(value) -> bool:
    return bool(
        isinstance(value, dict)
        and value.get("encoding") == "u8_stereo_peak_b64"
        and isinstance(value.get("data_b64"), str)
        and value.get("data_b64")
        and int(value.get("quantum_samples", 0) or 0) > 0
        and int(value.get("sample_rate_hz", 0) or 0) > 0
    )


def _prepare_bgm_previews(input_path: Path | None, output: Path, ffmpeg_path: str | None = None) -> dict:
    """Discover console-native BGM and make/cache browser-safe previews.

    WIP197 adds a persistent stat/content-bound cache for both the browser
    preview and the 256-sample stereo peak envelope. Older builds already used
    content-addressed preview filenames, but still decoded every complete BGM
    track with FFmpeg on every Visualizer rebuild merely to recreate the same
    peak envelope. A matching size+mtime fingerprint now reuses the previously
    verified source SHA/envelope without reading/decoding the track again.
    """
    sources: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for root in _bgm_roots(input_path):
        try:
            children = sorted(root.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            continue
        for path in children:
            if not path.is_file() or path.suffix.lower() not in NATIVE_BGM_EXTENSIONS:
                continue
            try:
                identity = str(path.resolve())
            except OSError:
                identity = str(path)
            if identity in seen:
                continue
            seen.add(identity)
            sources.append((path, _bgm_cache_source_key(path, input_path)))

    preview_root = output / "bgm_preview"
    cache_path = preview_root / "BGM_PREVIEW_CACHE.json"
    cached_rows: dict[str, dict] = {}
    try:
        cached_doc = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached_doc.get("format") == "SIIG_VISUALIZER_BGM_CACHE" and int(cached_doc.get("version", -1)) == BGM_PREVIEW_CACHE_VERSION:
            cached_rows = {str(k): v for k, v in (cached_doc.get("tracks") or {}).items() if isinstance(v, dict)}
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        cached_rows = {}

    ffmpeg = ffmpeg_path or shutil.which("ffmpeg")
    if ffmpeg_path and not Path(ffmpeg_path).exists():
        ffmpeg = shutil.which(ffmpeg_path)
    if sources:
        preview_root.mkdir(parents=True, exist_ok=True)

    codec_ext, codec_label, codec_args = ("", "", [])
    if ffmpeg:
        codec_ext, codec_label, codec_args = _ffmpeg_preview_codec(ffmpeg)

    entries: list[dict] = []
    jobs: list[tuple[int, Path, Path, dict | None, bool]] = []
    cache_hits = 0
    envelope_cache_hits = 0
    hashes_read = 0
    for path, cache_key in sources:
        try:
            st = path.stat()
            size, mtime_ns = int(st.st_size), int(st.st_mtime_ns)
        except OSError:
            size, mtime_ns = -1, -1
        cached = cached_rows.get(cache_key, {})
        stat_match = bool(
            cached
            and int(cached.get("size", -2)) == size
            and int(cached.get("mtime_ns", -2)) == mtime_ns
            and isinstance(cached.get("source_sha256"), str)
            and len(str(cached.get("source_sha256"))) == 64
        )
        if stat_match:
            digest = str(cached["source_sha256"])
            cache_hits += 1
        else:
            try:
                digest = toolkit.sha256_file(path)
                hashes_read += 1
            except OSError:
                digest = "unreadable"
        same_content = digest != "unreadable" and str(cached.get("source_sha256") or "") == digest
        cached_envelope = cached.get("meter_envelope") if same_content and _valid_meter_envelope(cached.get("meter_envelope")) else None
        if cached_envelope:
            envelope_cache_hits += 1

        safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem).strip("._") or "bgm"
        preview_name = f"{safe_stem}-{digest[:12]}{codec_ext}" if ffmpeg and digest != "unreadable" else None
        preview_codec = codec_label if preview_name else None
        # A previously generated preview remains usable even when FFmpeg is not
        # currently installed; the cache records only rip-relative filenames.
        if not preview_name and same_content:
            cached_preview = str(cached.get("preview") or "")
            candidate = output / cached_preview if cached_preview else None
            if candidate is not None and candidate.is_file() and candidate.stat().st_size > 0:
                preview_name = Path(cached_preview).name
                preview_codec = cached.get("preview_codec")

        destination = preview_root / preview_name if preview_name else None
        preview_ready = bool(destination is not None and destination.is_file() and destination.stat().st_size > 0)
        entry = {
            "name": path.name,
            "native_format": NATIVE_BGM_EXTENSIONS[path.suffix.lower()],
            "source_sha256": digest if digest != "unreadable" else None,
            "preview": f"bgm_preview/{preview_name}" if preview_name else None,
            "preview_codec": preview_codec if preview_name else None,
            "status": "ready" if preview_ready else ("pending" if preview_name and ffmpeg else "ffmpeg_unavailable"),
            "_cache_key": cache_key,
            "_size": size,
            "_mtime_ns": mtime_ns,
        }
        if cached_envelope:
            entry["meter_envelope"] = cached_envelope
        entries.append(entry)
        if preview_name and (not preview_ready or not cached_envelope) and ffmpeg:
            jobs.append((len(entries) - 1, path, destination, cached_envelope, not preview_ready))

    def transcode(job: tuple[int, Path, Path, dict | None, bool]) -> tuple[int, bool, dict | None, bool, bool]:
        index, source, destination, cached_envelope, needs_preview = job
        temp = destination.with_suffix(destination.suffix + ".partial")
        transcoded = False
        decoded = False
        try:
            ok = destination.is_file() and destination.stat().st_size > 0
            if needs_preview or not ok:
                temp.unlink(missing_ok=True)
                command = [
                    ffmpeg,
                    "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source), "-map", "0:a:0", "-vn",
                    "-ac", "2", "-ar", "48000",
                    *codec_args,
                    str(temp),
                ]
                if destination.suffix.lower() == ".mp3":
                    command[-1:-1] = ["-f", "mp3"]
                else:
                    command[-1:-1] = ["-f", "mp4"]
                proc = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300, check=False)
                ok = proc.returncode == 0 and temp.is_file() and temp.stat().st_size > 0
                if ok:
                    temp.replace(destination)
                    transcoded = True
                else:
                    temp.unlink(missing_ok=True)
            envelope = cached_envelope
            if ok and not _valid_meter_envelope(envelope):
                envelope = _ffmpeg_peak_envelope(ffmpeg, source)
                decoded = envelope is not None
            return index, ok, envelope, transcoded, decoded
        except (OSError, subprocess.SubprocessError):
            temp.unlink(missing_ok=True)
            return index, False, cached_envelope, transcoded, decoded

    transcoded_previews = 0
    decoded_envelopes = 0
    if ffmpeg and jobs:
        workers = min(4, len(jobs))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for index, ok, envelope, transcoded, decoded in pool.map(transcode, jobs):
                entries[index]["status"] = "ready" if ok else "transcode_failed"
                if envelope:
                    entries[index]["meter_envelope"] = envelope
                if transcoded:
                    transcoded_previews += 1
                if decoded:
                    decoded_envelopes += 1
                if not ok:
                    entries[index]["preview"] = None
                    entries[index]["preview_codec"] = None

    cache_tracks: dict[str, dict] = {}
    for entry in entries:
        cache_key = str(entry.pop("_cache_key"))
        size = int(entry.pop("_size"))
        mtime_ns = int(entry.pop("_mtime_ns"))
        if entry.get("source_sha256"):
            cache_tracks[cache_key] = {
                "name": entry.get("name"),
                "size": size,
                "mtime_ns": mtime_ns,
                "source_sha256": entry.get("source_sha256"),
                "preview": entry.get("preview"),
                "preview_codec": entry.get("preview_codec"),
                "meter_envelope": entry.get("meter_envelope"),
            }
    if sources:
        toolkit.write_json_private(cache_path, {
            "format": "SIIG_VISUALIZER_BGM_CACHE",
            "version": BGM_PREVIEW_CACHE_VERSION,
            "tracks": cache_tracks,
        }, ensure_ascii=False)

    ready = sum(1 for item in entries if item["status"] == "ready")
    return {
        "tracks": entries,
        "native_track_count": len(entries),
        "preview_count": ready,
        "ffmpeg_available": bool(ffmpeg),
        "preview_codec": codec_label or next((item.get("preview_codec") for item in entries if item.get("preview_codec")), None),
        "cache_hits": cache_hits,
        "envelope_cache_hits": envelope_cache_hits,
        "hashes_read": hashes_read,
        "transcoded_previews": transcoded_previews,
        "decoded_envelopes": decoded_envelopes,
    }


def _html(dataset: dict) -> str:
    payload = json.dumps(dataset, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SIIG Visualizer Simulator</title>
<style>
:root{color-scheme:dark;--hud:rgba(3,7,12,.82);--line:rgba(205,226,255,.25);--text:#f4f7fb;--muted:#a9b5c6;--accent:#d8edff;--good:#bfe9cb;background:#000;color:var(--text);font:14px ui-monospace,SFMono-Regular,Consolas,monospace}*{box-sizing:border-box}html,body{width:100%;height:100%;margin:0;overflow:hidden;background:#000}body{user-select:none}header{height:58px;padding:8px 12px;background:linear-gradient(#101823f2,#080d15ee);border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:center;position:fixed;inset:0 0 auto 0;z-index:30;box-shadow:0 4px 18px #0008}h1{font:700 15px ui-monospace,monospace;letter-spacing:.08em;margin:0 6px 0 0;white-space:nowrap;color:#fff}button,select,input,audio{background:#0b111b;color:#f4f7fb;border:1px solid #526075;border-radius:2px;padding:5px 7px;font:12px ui-monospace,monospace}button{cursor:pointer}button:hover,select:hover,input:hover{border-color:#a7c5e8}button:focus-visible,select:focus-visible,input:focus-visible{outline:1px solid #d8edff;outline-offset:1px}.quick-preset{display:flex;gap:6px;align-items:center;min-width:0;flex:1}.quick-preset span{font-size:11px;color:#cbd8e8;white-space:nowrap}.quick-preset select{width:min(620px,100%);min-width:170px}.top-spacer{flex:1}main{position:fixed;inset:58px 0 0 0;overflow:hidden;background:#000}#stageView{position:absolute;inset:0;padding:0;display:grid;place-items:center;min-width:0;background:#000}.canvas-wrap{position:absolute;inset:0;display:grid;place-items:center;background:#000;overflow:hidden}.canvas-wrap canvas{display:block;width:min(100%,calc((100vh - 58px)*16/9));height:auto;max-height:100%;aspect-ratio:16/9;background:#000;object-fit:contain;image-rendering:auto}#debugInfo{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);max-width:min(94vw,1180px);z-index:8;pointer-events:none;background:#02060aa8;border:1px solid #ffffff22;padding:5px 8px;text-shadow:0 1px 2px #000}.status{color:#d6e1ef;font:11px ui-monospace,monospace}.hidden{display:none!important}#controlDock{position:absolute;z-index:20;top:12px;left:12px;bottom:12px;width:min(470px,calc(100vw - 24px));overflow:auto;background:var(--hud);border:1px solid #8394aa55;box-shadow:0 10px 40px #000b;backdrop-filter:blur(5px);transition:transform .18s ease,opacity .18s ease;padding:0 10px 10px}#controlDock.panel-hidden{transform:translateX(calc(-100% - 20px));opacity:0;pointer-events:none}.check-title{position:sticky;top:0;z-index:4;margin:0 -10px;padding:10px 12px 7px;background:#03070cf2;color:#fff;font-weight:700;letter-spacing:.12em;border-bottom:1px solid #ffffff29}.check-title .sub{display:block;margin-top:3px;color:#9eabbc;font-size:10px;font-weight:400;letter-spacing:.02em}.tabbar{position:sticky;top:48px;z-index:4;display:grid;grid-template-columns:repeat(3,1fr);gap:1px;margin:0 -10px 10px;background:#65728455;border-bottom:1px solid #ffffff26}.tabbar button{border:0;border-radius:0;background:#0a111bf5;padding:8px 4px;color:#9eabbc}.tabbar button.active{background:#182331;color:#fff;box-shadow:inset 0 -2px 0 #e8f4ff}.tab-page{display:none}.tab-page.active{display:block}fieldset{border:0;border-top:1px solid #8394aa55;border-radius:0;margin:0;padding:8px 2px 10px}fieldset:first-child{border-top:0}legend{color:#fff;padding:0 4px 0 0;text-transform:uppercase;font-weight:700;letter-spacing:.06em;font-size:11px}.row{display:grid;grid-template-columns:minmax(150px,1fr) minmax(120px,175px);gap:8px;align-items:center;margin:4px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:4px}.quad{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}.muted{color:var(--muted)}.small{font-size:10px;line-height:1.35}.notice{padding:8px;border-left:2px solid #a78746;background:#18140dc4;color:#e8d49f;margin:8px 0;font-size:10px;line-height:1.35}.good{border-color:#5fa476;background:#0c1a12c4;color:#ccebd4}.wide{width:100%}.meter{font-size:10px;color:var(--good)}.schema{max-height:170px;overflow:auto;margin-top:7px;border:1px solid #ffffff20;padding:6px}.schema code{display:block;color:#bcc9da;padding:1px 0}.timeline{margin:8px 0;border:1px solid #ffffff25;overflow:auto;max-height:34vh;background:#03070c}table{width:100%;border-collapse:collapse;font-size:10px}th,td{padding:4px 5px;border-bottom:1px solid #ffffff14;text-align:left}th{position:sticky;top:0;background:#111925}.mono{font-family:ui-monospace,monospace}.inactive-native{opacity:.55}.inactive-native input{border-color:#775e35}.hint-live{color:#f0d99d}.primary-action{border-color:#8caed5;background:#15283d}.preset-summary{padding:6px 7px;margin-bottom:6px;border:1px solid #ffffff20;background:#06101b;color:#d8edff;font-size:10px}.presentation-note{color:#9fb1c6;font-size:10px}.panel-footer{color:#8290a2;font-size:9px;padding:6px 0}.fullscreen-only{display:none}:fullscreen .fullscreen-only{display:inline}:fullscreen header{height:52px}:fullscreen main{inset:52px 0 0}:fullscreen .canvas-wrap canvas{width:min(100%,calc((100vh - 52px)*16/9))}@media(max-width:800px){header h1{display:none}.quick-preset span{display:none}header{height:54px;padding:6px}.quick-preset select{min-width:110px}main{inset:54px 0 0}#controlDock{top:8px;left:8px;bottom:8px;width:min(440px,calc(100vw - 16px))}.canvas-wrap canvas{width:min(100%,calc((100vh - 54px)*16/9))}}
</style></head><body>
<header id="topbar"><h1>SIIG VISUALIZER</h1><label class="quick-preset"><span>STAGE / BOSS</span><select id="quickTimelinePreset"><option value="">— choose authored visualizer —</option></select></label><button id="play" type="button">Pause</button><button id="reset" type="button">Reset (X)</button><button id="fullscreen" type="button">Fullscreen (F)</button><button id="togglePanel" type="button">Hide menu (M)</button><button id="toggleDebug" type="button">Info (Y)</button><label class="small">SHAPE <select id="shape"></select></label></header>
<main id="simulatorShell"><aside id="controlDock"><div class="check-title">VISUALIZER CHECK MODE<span class="sub">June 10-inspired simulator control surface · canvas remains live behind this menu</span></div><div class="tabbar"><button type="button" class="tab active" data-tab="tabPresets">PRESETS</button><button type="button" class="tab" data-tab="tabCheck">CHECK MODE</button><button type="button" class="tab" data-tab="tabAdvanced">ADVANCED</button></div><div id="tabPresets" class="tab-page active"></div><div id="tabCheck" class="tab-page"></div><div id="tabAdvanced" class="tab-page"></div>
<div class="notice good"><b>June 10 executable-backed controls.</b> X clears the feedback surface, Y toggles Visualizer info, VolumeSet 0 reads the BGM meter and 1 reads stick magnitude, and the original debug-menu ranges/defaults are reproduced below. Real-hardware stage 4-2/4-4/4-5 footage now also anchors the normal gameplay VOL/MIN/MAX/VOL SCALE diagnostics.</div>
<div class="notice small">Recovered facts are kept separate from approximation. <b>The runtime pipeline is executable-backed:</b> 1280×720 feedback target, 128×128 SHAPE source, SHAPE-first draw order, feedback magnification without framebuffer rotation, signed Fix Rotation, and the exact Position Fix coordinate table. Position coordinates use the game's centered convention: <b>+X right, +Y up</b>. WIP195 restores <b>direct target-pixel Position mapping</b>. The WIP191 1.5× hypothesis was contradicted by retail stage 4-5: PARAM_7's authored Y=+360 must seed its 128×128 source at the top edge; at 1.5× the source was fully off-screen and the simulator collapsed into BG-color gradients. Startup code patches the writable fixed-position table into a full 3×3 grid: raw 1..3 upper, 4..6 middle, and 7..9 lower; raw 0 remains the Free X/Y path. When built from a full rip, the simulator embeds the user's real ten Visualizer SHAPE PNGs; otherwise it falls back to procedural stand-ins. Recursive GPU sampler/blend/shader semantics are executable-backed; only final host presentation and exact render-target alpha storage remain browser-side approximations.</div>
<fieldset><legend>VolumeSet / input</legend>
<div class="row"><label>VolumeSet</label><select id="volumeSource"><option value="0">0 · from BGM</option><option value="1" selected>1 · from Stick</option></select></div>
<div class="row"><label>BGM response model</label><select id="bgmResponseModel"><option value="check" selected>Check Mode · raw peak mean</option><option value="gameplay">Stage playback · adaptive VOL SCALE</option></select></div>
<div class="row"><label>Left Stick magnitude</label><input id="stickVolume" type="range" min="0" max="1" step="0.001" value="0"></div>
<div class="muted small">Arrow keys or WASD temporarily drive the simulated stick to 1.0. The original code takes the absolute stick value.</div>
<div class="row"><label>Extracted game BGM</label><select id="bgmPreset"><option value="">— choose generated preview —</option></select></div>
<div id="bgmPreviewStatus" class="muted small">No console-native BGM previews were generated.</div>
<div class="row"><label>Host BGM audio</label><input id="bgmFile" type="file" accept=".wma,.at3,.wav,.mp3,.m4a,.aac,.ogg,.flac,audio/*"></div>
<audio id="bgmAudio" class="wide" controls></audio><div id="bgmMeter" class="meter small">BGM meter: peak L 0.000 · peak R 0.000 · raw mean 0.000</div>
<div id="bgmQuantumStatus" class="muted small">Xbox 360 meter quantum: 256 samples @ 48 kHz = 5.333 ms. Generated previews use a precomputed peak envelope so local audio remains directly audible.</div>
<div id="bgmGameplayMeter" class="meter small">Stage meter: VOL 0.0000 · MIN 0.0000 · MAX 1.0000 · VOL SCALE 1.0000 · AVE RAW 0.0000 · AVE SCALE 0.0000</div>
<div class="muted small">Executable-backed semantics: the game averages the left/right XAudio2 volume-meter <b>peak</b> levels. Check Mode consumes that raw linear 0..1 mean directly. Normal stage playback writes it through a 300-sample adaptive min/max window and drives parameter interpolation with normalized <b>VOL SCALE</b>; the hardware AVE RAW/SCALE diagnostics use 180-sample histories. The simulator executes that recovered post-meter state once per logical 60 Hz simulation step. Xbox 360 XAudio2 processes one 5 1/3 ms quantum at a time; at the 48 kHz preview rate that is exactly 256 samples, and the volume meter reports each channel's maximum absolute level for one processing pass. Generated game-BGM previews now keep the HTML audio element on its native audible path and use an FFmpeg-precomputed 256-sample peak envelope indexed by playback time; this avoids file:// MediaElementAudioSource muting/CORS problems. User-loaded browser audio is decoded only for metering and remains natively audible through the media element. Exact host query phase/scheduling relative to native XAudio2 quantum boundaries remains approximate. Xbox WMA and PS3 AT3/ATRAC3+ are converted by the toolkit to browser-safe local previews when FFmpeg is available; originals remain untouched.</div>
<button id="resetBgmNormalizer" type="button">Reset stage BGM normalizer</button>
</fieldset>
<fieldset><legend>Feedback / magnify</legend>
<div class="row"><label>Magnify Scale X min/max</label><div class="pair"><input id="magxmin" type="number" min="0.8" max="2" step="0.001" value="1.030"><input id="magxmax" type="number" min="0.8" max="2" step="0.001" value="1.030"></div></div>
<div class="row"><label>Magnify Scale Y min/max</label><div class="pair"><input id="magymin" type="number" min="0.8" max="2" step="0.001" value="1.030"><input id="magymax" type="number" min="0.8" max="2" step="0.001" value="1.030"></div></div>
<div class="row"><label>Magnify A min/max</label><div class="pair"><input id="magamin" type="number" min="0.7" max="1" step="0.001" value="1.000"><input id="magamax" type="number" min="0.7" max="1" step="0.001" value="1.000"></div></div>
<div id="nativeRangeStatus" class="muted small">Native range contract: Magnify X/Y/A and SHAPE RGBA require max ≥ min. The browser keeps those pairs valid instead of reproducing the June 10 assertion.</div>
<div class="muted small"><b>Hardware-sweep clarification:</b> min/max are the VolumeSet endpoints: effective value = min + (max − min) × volume. Values below 1 contract feedback; values above 1 expand it. X and Y remain independent.</div>
<div class="row"><label>Presentation resolve</label><select id="displayResolve"><option value="hardware" selected>Hardware-like smooth resolve</option><option value="raw">Raw recovered RGB</option></select></div>
<div class="row"><label>Display softness (host-only px)</label><input id="displaySoftness" type="range" min="0" max="8" step="0.1" value="0.8"></div>
<div class="row"><label>Base intensity (host-only)</label><input id="displayIntensity" type="range" min="0.1" max="1" step="0.01" value="0.90"></div>
<div class="row"><label>Soft bloom (host-only)</label><input id="displayBloom" type="range" min="0" max="1" step="0.01" value="0.46"></div>
<div class="muted small">Presentation-only polish after the recovered point-filtered feedback pass. Hardware-like resolve first performs a high-quality 640×360 display resolve and then scales back to 1280×720 before the soft base/bloom presentation. It never feeds back into the recursive surfaces. Choose Raw recovered RGB to inspect the un-resolved recurrence directly.</div>
<div class="row" id="rotationBaseRow"><label>Rotation Base (deg/update)</label><input id="rotbase" type="number" min="-365" max="365" step="0.1" value="0.1"></div>
<div class="row" id="rotationAddRow"><label>Add Rotation (deg/update × volume)</label><input id="rotadd" type="number" min="-730" max="730" step="0.1" value="0.0"></div>
<div class="row"><label>Fix Rotation (deg)</label><input id="rotfix" type="number" min="-365" max="365" step="0.1" value="0.0"></div>
<div id="rotationOverrideHint" class="muted small">Fix Rotation = 0 keeps accumulated rotation active. Any non-zero value overrides Rotation Base + Add Rotation × volume; the June 10 hardware sweep visibly confirms those two controls are ignored while the override is active.</div>
</fieldset>
<fieldset><legend>Stamp / position</legend>
<div class="row"><label>Position Fix</label><select id="positionFix"></select></div>
<div class="row" id="positionFreeRow"><label>Position Free X/Y</label><div class="pair"><input id="posx" type="number" min="-560" max="560" step="1" value="0"><input id="posy" type="number" min="-360" max="360" step="1" value="0"></div></div><div id="positionFreeHint" class="muted small">Centered target coordinates: +X right, +Y up. Authored Position values map directly to 1280×720 target-pixel offsets; +360 therefore places the source center on the top edge. Position Free is used only when Position Fix = 0.</div>
<div class="row"><label>Scale X min/max</label><div class="pair"><input id="sxmin" type="number" min="0.01" max="4" step="0.001" value="1"><input id="sxmax" type="number" min="0.01" max="4" step="0.001" value="1"></div></div>
<div class="row"><label>Scale Y min/max</label><div class="pair"><input id="symin" type="number" min="0.01" max="4" step="0.001" value="1"><input id="symax" type="number" min="0.01" max="4" step="0.001" value="1"></div></div>
<div class="muted small"><b>Source-stamp scale:</b> these X/Y pairs are also VolumeSet endpoints, but they scale only the newly injected SHAPE before recursive feedback. Unlike Magnify X/Y, the June 10 setter does not assert max ≥ min, so inverted source-scale endpoints remain allowed.</div>
</fieldset>
<fieldset><legend>Position diagnostics</legend>
<div class="row"><label>Native anchor overlay</label><input id="showAnchorOverlay" type="checkbox"></div>
<div class="muted small">Research-only overlay. Draws the executable-backed target anchor and the browser's current 128×128 source bounds after source scale. It does not alter the feedback surfaces. Use it when comparing a simulator preset against hardware footage; remaining capture/pivot differences should be measured here instead of introducing another guessed global Position multiplier.</div>
</fieldset>
<fieldset><legend>Background RGBA</legend>
<div class="quad"><input id="bgr" aria-label="BG R" type="number" min="0" max="255" value="0"><input id="bgg" aria-label="BG G" type="number" min="0" max="255" value="0"><input id="bgb" aria-label="BG B" type="number" min="0" max="255" value="0"><input id="bga" aria-label="BG A" type="number" min="0" max="255" value="0"></div>
<div class="muted small"><b>Direct clear values:</b> June 10 hardware sweeps confirm BG R/G/B/A are single controls, not VolumeSet min/max endpoints. RGB is reproduced directly in the recovered feedback clear. BG A remains visible here as a native control, but exact Xenos render-target alpha storage/final-composite equivalence is still bounded rather than guessed by the browser bridge.</div>
</fieldset>
<fieldset><legend>Stamp RGBA min/max</legend>
<div class="row"><label>R min/max</label><div class="pair"><input id="rmin" type="number" min="0" max="255" value="128"><input id="rmax" type="number" min="0" max="255" value="255"></div></div>
<div class="row"><label>G min/max</label><div class="pair"><input id="gmin" type="number" min="0" max="255" value="0"><input id="gmax" type="number" min="0" max="255" value="0"></div></div>
<div class="row"><label>B min/max</label><div class="pair"><input id="bmin" type="number" min="0" max="255" value="0"><input id="bmax" type="number" min="0" max="255" value="0"></div></div>
<div class="row"><label>A min/max</label><div class="pair"><input id="amin" type="number" min="0" max="255" value="255"><input id="amax" type="number" min="0" max="255" value="255"></div></div>
<div class="muted small"><b>Source tint endpoints:</b> R/G/B/A interpolate as min + (max − min) × VolumeSet before the new SHAPE stamp is drawn. The hardware sweep visibly confirms endpoint interpolation; these are not random ranges.</div>
</fieldset>
<fieldset><legend>Recovered game presets</legend>
<div id="presetSummary" class="preset-summary">Choose a Stage / boss event here or from the always-visible top bar. Selection applies immediately and resets feedback.</div>
<div id="setStatus" class="muted small">No ParameterSet.nut / SequenceSet.nut loaded. Build the simulator from a full rip to enable exact game rows.</div>
<div class="row"><label>ParameterSet</label><select id="parameterPreset"></select></div><button id="applyParameter" type="button">Apply parameter row</button>
<div class="row"><label>SequenceSet</label><select id="sequencePreset"></select></div><button id="applySequence" type="button">Apply active parameter row</button>
<div class="row"><label>Stage / boss event</label><select id="timelinePreset"></select></div><button id="applyTimelinePreset" class="primary-action" type="button">Restart selected authored visualizer</button>
<div class="muted small">SequenceSet preserves all 16 authored entries. Retail rows currently contain one active parameter id each. Stage/boss events come directly from decoded <code>VL_SEQUENCESET</code> commands, and the timeline now synchronizes the active parameter automatically.</div>
</fieldset>
<fieldset><legend>Recovered parameter schema</legend><div class="muted small">29 values / ParameterSet row · 49 retail rows · 57 retail sequences</div><div id="schema" class="schema mono"></div></fieldset>
<fieldset><legend>Decoded stage / boss visualizer timeline</legend><div class="row"><label>Script</label><select id="script"></select></div><div class="row"><label>Authored frame</label><input id="frame" type="range" min="0" max="0" value="0"></div><label class="small"><input id="timelineFollow" type="checkbox" checked> Advance authored stage frame with the 60 Hz simulator</label><div class="row"><label>Sequence RNG seed (sim-only)</label><input id="timelineSeed" type="number" min="0" max="4294967295" step="1" value="1"></div><button id="rerollTimelineSeed" type="button">Reroll sequence timing</button><div class="muted small"><code>VL_CHANGETIME</code> is not an interpolation command: the executable stores a minimum/maximum SequenceSet change threshold, rolls <code>[min,max)</code> with the game's CRT RNG, and advances to the next ParameterSet when its active-update counter passes that threshold. Equal bounds are fixed and consume no RNG. Hardware seeds the CRT RNG from a timer, so the seed above is intentionally simulator-controlled for reproducible playback.</div><div class="status" id="scriptStatus">No DAT timeline loaded.</div></fieldset>
</aside><section id="stageView"><div class="canvas-wrap"><canvas id="canvas" width="1280" height="720"></canvas></div><div id="debugInfo"><div class="status" id="status"></div></div><div class="timeline"><table><thead><tr><th>Frame</th><th>Opcode</th><th>Arguments</th></tr></thead><tbody id="events"></tbody></table></div></section></main>
<script id="data" type="application/json">__DATA__</script><script>
const DB=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id),can=$('canvas'),ctx=can.getContext('2d',{alpha:true});
const W=can.width,H=can.height,feedback=[document.createElement('canvas'),document.createElement('canvas')],feedbackCtx=[];for(const c of feedback){c.width=W;c.height=H;feedbackCtx.push(c.getContext('2d',{alpha:false}))}const resolveCanvas=document.createElement('canvas'),resolveSize=(DB.evidence.presentation_softness&&DB.evidence.presentation_softness.resolve_size)||[640,360];resolveCanvas.width=resolveSize[0];resolveCanvas.height=resolveSize[1];const resolveCtx=resolveCanvas.getContext('2d',{alpha:false});let front=0,running=true,last=performance.now(),accum=0,logicalFrames=0,rotationAccum=0,showDebugInfo=true,bgmLevel=0,bgmPeakL=0,bgmPeakR=0,bgmChannels=2;const STEP=1/60,FIXED_POS=DB.evidence.position_fix_coords,FIXED_CHOICES=DB.evidence.position_fix_choices,FIXED_CANON=DB.evidence.position_fix_canonical_indices,POS_SCALE=Number(DB.evidence.position_coordinate_system.logical_to_target_scale)||1,GAME_VOL_WINDOW=300,GAME_AVG_HISTORY=180,GAME_MIN_SPAN=0.001,DEFAULT_CHANGE_TIME=18000,XBOX_AUDIO_RATE=DB.evidence.bgm_meter.xbox360_sample_rate_hz||48000,XBOX_AUDIO_QUANTUM=DB.evidence.bgm_meter.xbox360_quantum_samples||256;
const stageBgm={windowLength:GAME_VOL_WINDOW,window:new Float32Array(GAME_VOL_WINDOW),rawHistory:new Float32Array(GAME_AVG_HISTORY),scaleHistory:new Float32Array(GAME_AVG_HISTORY),windowIndex:0,historyIndex:0,min:0,max:1,scale:1,averageRaw:0,averageScale:0};
const clamp=(v,a,b)=>Math.max(a,Math.min(b,Number(v)||0)),num=id=>Number($(id).value)||0,mix=(a,b,t)=>a+(b-a)*t,rad=d=>d*Math.PI/180;
function setupControlDock(){const dock=$('controlDock'),pages={preset:$('tabPresets'),check:$('tabCheck'),advanced:$('tabAdvanced')},sets=[...dock.querySelectorAll(':scope > fieldset')],notices=[...dock.querySelectorAll(':scope > .notice')];const byLegend=name=>sets.find(f=>(f.querySelector('legend')?.textContent||'').trim()===name);for(const name of ['Recovered game presets','VolumeSet / input']){const f=byLegend(name);if(f)pages.preset.appendChild(f)}for(const name of ['Feedback / magnify','Stamp / position','Background RGBA','Stamp RGBA min/max']){const f=byLegend(name);if(f)pages.check.appendChild(f)}for(const name of ['Position diagnostics','Recovered parameter schema','Decoded stage / boss visualizer timeline']){const f=byLegend(name);if(f)pages.advanced.appendChild(f)}for(const n of notices)pages.advanced.appendChild(n);const timeline=document.querySelector('#stageView > .timeline');if(timeline)pages.advanced.appendChild(timeline);for(const b of document.querySelectorAll('.tabbar .tab'))b.onclick=()=>{for(const x of document.querySelectorAll('.tabbar .tab'))x.classList.toggle('active',x===b);for(const p of document.querySelectorAll('.tab-page'))p.classList.toggle('active',p.id===b.dataset.tab)}}
setupControlDock();
function togglePanel(){const hidden=$('controlDock').classList.toggle('panel-hidden');$('togglePanel').textContent=hidden?'Show menu (M)':'Hide menu (M)'}
async function toggleFullscreen(){try{if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen()}catch(_){}}
function updateFullscreenButton(){$('fullscreen').textContent=document.fullscreenElement?'Exit fullscreen (F)':'Fullscreen (F)'}
document.addEventListener('fullscreenchange',updateFullscreenButton);
const NATIVE_RANGE_PAIRS=[['magxmin','magxmax','Magnify Scale X'],['magymin','magymax','Magnify Scale Y'],['magamin','magamax','Magnify A'],['rmin','rmax','SHAPE R'],['gmin','gmax','SHAPE G'],['bmin','bmax','SHAPE B'],['amin','amax','SHAPE A']];
let nativeRangeGuard=false;function normalizeNativeRanges(changedId=null){if(nativeRangeGuard)return;nativeRangeGuard=true;let adjusted='';for(const [loId,hiId,label] of NATIVE_RANGE_PAIRS){const lo=$(loId),hi=$(hiId),a=Number(lo.value),b=Number(hi.value);if(!Number.isFinite(a)||!Number.isFinite(b)||a<=b)continue;if(changedId===hiId)lo.value=hi.value;else hi.value=lo.value;adjusted=label}nativeRangeGuard=false;const out=$('nativeRangeStatus');if(out)out.textContent=adjusted?`Native range contract: ${adjusted} was clamped so max ≥ min (the June 10 build asserts on an inverted pair).`:'Native range contract: Magnify X/Y/A and SHAPE RGBA require max ≥ min. The browser keeps those pairs valid instead of reproducing the June 10 assertion.';}
const shapeImages={},shapePixels={},shapeTint=document.createElement('canvas');shapeTint.width=128;shapeTint.height=128;for(const [name,src] of Object.entries(DB.shape_images||{})){const img=new Image();img.src=src;shapeImages[name]=img}
function exactShapePixels(name){if(shapePixels[name])return shapePixels[name];const img=shapeImages[name];if(!img||!img.complete||!img.naturalWidth)return null;const c=document.createElement('canvas');c.width=128;c.height=128;const cg=c.getContext('2d',{willReadFrequently:true});cg.imageSmoothingEnabled=false;cg.clearRect(0,0,128,128);cg.drawImage(img,0,0,128,128);const pixels=new Uint8ClampedArray(cg.getImageData(0,0,128,128).data);shapePixels[name]=pixels;return pixels}
const stickKeys=new Set(),stickVolume=()=>clamp(Math.max(num('stickVolume'),stickKeys.size?1:0),0,1);
function resetGameplayBgmNormalizer(){stageBgm.window.fill(0);stageBgm.rawHistory.fill(0);stageBgm.scaleHistory.fill(0);stageBgm.windowIndex=0;stageBgm.historyIndex=0;stageBgm.min=0;stageBgm.max=1;stageBgm.scale=1;stageBgm.averageRaw=0;stageBgm.averageScale=0;updateGameplayMeter()}
function configureGameplayBgmWindow(samples){const n=Math.max(5,Math.round(Number(samples)||GAME_VOL_WINDOW));if(n===stageBgm.windowLength)return;stageBgm.windowLength=n;stageBgm.window=new Float32Array(n);resetGameplayBgmNormalizer()}
function updateGameplayBgmNormalizer(raw){stageBgm.rawHistory[stageBgm.historyIndex]=raw;stageBgm.window[stageBgm.windowIndex]=clamp(raw,0,1);stageBgm.windowIndex++;if(stageBgm.windowIndex>=stageBgm.windowLength)stageBgm.windowIndex=0;if(stageBgm.windowIndex===0){let lo=1,hi=0;for(const v of stageBgm.window){if(v<lo)lo=v;if(v>hi)hi=v}stageBgm.min=lo;stageBgm.max=hi;if(Math.abs(stageBgm.max-stageBgm.min)<GAME_MIN_SPAN){if(stageBgm.max<GAME_MIN_SPAN||stageBgm.min<=0.999)stageBgm.max=stageBgm.min+GAME_MIN_SPAN;else stageBgm.min=stageBgm.max-GAME_MIN_SPAN}}if(raw<stageBgm.min)stageBgm.scale=0;else if(raw>stageBgm.max)stageBgm.scale=1;else stageBgm.scale=(raw-stageBgm.min)/Math.max(Math.abs(stageBgm.max-stageBgm.min),GAME_MIN_SPAN);stageBgm.scaleHistory[stageBgm.historyIndex]=stageBgm.scale;stageBgm.historyIndex++;if(stageBgm.historyIndex>=GAME_AVG_HISTORY){stageBgm.historyIndex=0;let rawSum=stageBgm.averageRaw,scaleSum=stageBgm.averageScale;for(let i=0;i<GAME_AVG_HISTORY;i++){rawSum+=stageBgm.rawHistory[i];scaleSum+=stageBgm.scaleHistory[i]}stageBgm.averageRaw=rawSum/GAME_AVG_HISTORY;stageBgm.averageScale=scaleSum/GAME_AVG_HISTORY}updateGameplayMeter()}
const bgmDrive=()=>$('bgmResponseModel').value==='gameplay'?stageBgm.scale:bgmLevel,volume=()=>$('volumeSource').value==='0'?bgmDrive():stickVolume(),mixControl=(a,b)=>mix(num(a),num(b),volume());
function updateGameplayMeter(){$('bgmGameplayMeter').textContent=`Stage meter: VOL ${bgmLevel.toFixed(4)} · MIN ${stageBgm.min.toFixed(4)} · MAX ${stageBgm.max.toFixed(4)} · VOL SCALE ${stageBgm.scale.toFixed(4)} · AVE RAW ${stageBgm.averageRaw.toFixed(4)} · AVE SCALE ${stageBgm.averageScale.toFixed(4)} · window ${stageBgm.windowLength}f`}
function colorNow(){const v=volume();return [clamp(mix(num('rmin'),num('rmax'),v),0,255),clamp(mix(num('gmin'),num('gmax'),v),0,255),clamp(mix(num('bmin'),num('bmax'),v),0,255),clamp(mix(num('amin'),num('amax'),v),0,255)]}
function resetFeedback(){for(const c of feedback)c.getContext('2d').clearRect(0,0,W,H);front=0;logicalFrames=0;rotationAccum=0;drawDisplay()}
function toggleDebug(){showDebugInfo=!showDebugInfo;$('debugInfo').classList.toggle('hidden',!showDebugInfo);$('toggleDebug').textContent=showDebugInfo?'Hide debug text (Y)':'Show debug text (Y)'}
function shapeStamp(g,name,cx,cy,sx,sy,rgba,stampAngle){const pixels=exactShapePixels(name);if(pixels){const tg=shapeTint.getContext('2d',{willReadFrequently:true}),out=tg.createImageData(128,128),tr=clamp(rgba[0],0,255)/255,tgMul=clamp(rgba[1],0,255)/255,tb=clamp(rgba[2],0,255)/255,ta=clamp(rgba[3],0,255)/255;for(let i=0;i<pixels.length;i+=4){out.data[i]=Math.round(pixels[i]*tr);out.data[i+1]=Math.round(pixels[i+1]*tgMul);out.data[i+2]=Math.round(pixels[i+2]*tb);out.data[i+3]=Math.round(pixels[i+3]*ta)}tg.putImageData(out,0,0);g.save();g.translate(cx,cy);g.rotate(stampAngle);g.scale(sx,sy);g.globalCompositeOperation='source-over';const shapeSmooth=g.imageSmoothingEnabled;g.imageSmoothingEnabled=false;g.drawImage(shapeTint,-64,-64,128,128);g.imageSmoothingEnabled=shapeSmooth;g.restore();return}g.save();g.translate(cx,cy);g.rotate(stampAngle);g.scale(sx,sy);g.globalCompositeOperation='source-over';g.strokeStyle=`rgba(${rgba[0]|0},${rgba[1]|0},${rgba[2]|0},${rgba[3]/255})`;g.fillStyle=g.strokeStyle;g.lineCap='round';g.lineJoin='round';const r=42;switch(name){case 'WhiteCircle':g.lineWidth=8;g.beginPath();g.arc(0,0,r,0,Math.PI*2);g.stroke();break;case 'line':g.lineWidth=8;g.beginPath();g.moveTo(-64,0);g.lineTo(64,0);g.stroke();break;case '3line':g.lineWidth=7;for(const y of [-17,0,17]){g.beginPath();g.moveTo(-58,y);g.lineTo(58,y);g.stroke()}break;case 'square':g.lineWidth=8;g.strokeRect(-42,-42,84,84);break;case 'triangle':g.lineWidth=8;g.beginPath();g.moveTo(0,-52);g.lineTo(48,36);g.lineTo(-48,36);g.closePath();g.stroke();break;case 'WhiteCircle2':g.beginPath();g.arc(0,0,r,0,Math.PI*2);g.fill();break;case 'line2':g.lineWidth=18;g.beginPath();g.moveTo(-64,0);g.lineTo(64,0);g.stroke();break;case '3line2':g.lineWidth=15;for(const y of [-21,0,21]){g.beginPath();g.moveTo(-58,y);g.lineTo(58,y);g.stroke()}break;case 'square2':g.fillRect(-42,-42,84,84);break;case 'triangle2':g.beginPath();g.moveTo(0,-52);g.lineTo(48,36);g.lineTo(-48,36);g.closePath();g.fill();break}g.restore()}
function logicalStep(){updateGameplayBgmNormalizer(bgmLevel);const src=feedback[front],dst=feedback[1-front],g=feedbackCtx[1-front];g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='copy';const br=clamp(num('bgr'),0,255)|0,bg=clamp(num('bgg'),0,255)|0,bb=clamp(num('bgb'),0,255)|0,ba=clamp(num('bga'),0,255)/255;/* EffectBlurPS samples previous RGB but discards sampled alpha, replacing W with the uniform Alpha parameter. Keep feedback working canvases opaque and always preserve clear RGB so Canvas source alpha cannot attenuate the recovered RGB recurrence. */g.fillStyle=`rgb(${br},${bg},${bb})`;g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';const v=volume(),mx=Math.max(0.001,mixControl('magxmin','magxmax')),my=Math.max(0.001,mixControl('magymin','magymax')),ma=clamp(mixControl('magamin','magamax'),0,1);const rotStep=num('rotbase')+num('rotadd')*v,fix=Math.max(0,Math.min(9,Math.round(num('positionFix')))),freeX=num('posx'),freeY=num('posy'),fixed=(FIXED_CHOICES.find(x=>x.canonical_index===fix)||{coord:[0,0]}).coord,px=fix?fixed[0]:freeX,py=fix?fixed[1]:freeY,cx=W/2+px*POS_SCALE,cy=H/2-py*POS_SCALE;const fixRot=num('rotfix');if(Math.abs(fixRot)<1e-9)rotationAccum+=rotStep;const stampAngle=rad(Math.abs(fixRot)<1e-9?rotationAccum:fixRot),rgba=colorNow(),sx=mixControl('sxmin','sxmax'),sy=mixControl('symin','symax');/* Runtime order: clear target -> draw current SHAPE -> draw magnified previous feedback -> swap. Rotation is source-image only. */shapeStamp(g,$('shape').value,cx,cy,sx,sy,rgba,stampAngle);g.save();g.globalAlpha=ma;g.globalCompositeOperation='lighter';const prevSmooth=g.imageSmoothingEnabled;g.imageSmoothingEnabled=false;g.translate(cx,cy);g.scale(mx,my);g.translate(-cx,-cy);g.drawImage(src,0,0);g.imageSmoothingEnabled=prevSmooth;g.globalCompositeOperation='source-over';g.restore();front=1-front;logicalFrames++;advanceTimelineFrame()}
function updateNativeInactiveHints(){const fix=Math.max(0,Math.min(9,Math.round(num('positionFix')))),fixRot=num('rotfix'),posRow=$('positionFreeRow'),posHint=$('positionFreeHint'),rotHint=$('rotationOverrideHint'),rotBaseRow=$('rotationBaseRow'),rotAddRow=$('rotationAddRow');if(posRow)posRow.classList.toggle('inactive-native',fix!==0);if(rotBaseRow)rotBaseRow.classList.toggle('inactive-native',Math.abs(fixRot)>=1e-9);if(rotAddRow)rotAddRow.classList.toggle('inactive-native',Math.abs(fixRot)>=1e-9);if(posHint){posHint.classList.toggle('hint-live',fix!==0);posHint.textContent=fix===0?`Centered target coordinates: +X right / +Y up · ${POS_SCALE.toFixed(2)}× native position scale. Position Free is active.`:`Position Free is currently ignored: Position Fix ${fix} selects a native fixed anchor.`}if(rotHint){rotHint.classList.toggle('hint-live',Math.abs(fixRot)>=1e-9);rotHint.textContent=Math.abs(fixRot)<1e-9?'Fix Rotation = 0: Rotation Base + Add Rotation × volume is accumulated normally.':`Fix Rotation ${fixRot.toFixed(1)}° is active: Rotation Base and Add Rotation are currently ignored by the native path.`}}
function displaySource(){if($('displayResolve').value==='raw')return feedback[front];resolveCtx.setTransform(1,0,0,1,0,0);resolveCtx.globalAlpha=1;resolveCtx.globalCompositeOperation='copy';resolveCtx.imageSmoothingEnabled=true;resolveCtx.imageSmoothingQuality='high';resolveCtx.drawImage(feedback[front],0,0,W,H,0,0,resolveCanvas.width,resolveCanvas.height);resolveCtx.globalCompositeOperation='source-over';return resolveCanvas}
function drawDisplay(){updateNativeInactiveHints();ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,W,H);ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);const mode=$('displayResolve').value,softness=clamp(num('displaySoftness'),0,8),intensity=clamp(num('displayIntensity'),0.1,1),bloom=clamp(num('displayBloom'),0,1),source=displaySource(),raw=mode==='raw';ctx.save();ctx.globalCompositeOperation='source-over';ctx.globalAlpha=raw?1:intensity;ctx.imageSmoothingEnabled=!raw;ctx.imageSmoothingQuality='high';ctx.filter=!raw&&softness>0?`blur(${Math.min(softness,2.0).toFixed(2)}px)`:'none';ctx.drawImage(source,0,0,source.width,source.height,0,0,W,H);ctx.restore();if(!raw&&bloom>0){ctx.save();ctx.globalCompositeOperation='screen';ctx.globalAlpha=bloom;ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.filter=`blur(${Math.max(1.0,softness*2.0).toFixed(2)}px) saturate(1.08) brightness(1.15)`;ctx.drawImage(source,0,0,source.width,source.height,0,0,W,H);ctx.restore()}ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';ctx.filter='none';const v=volume(),name=$('shape').value;const mx=mixControl('magxmin','magxmax'),my=mixControl('magymin','magymax'),ma=mixControl('magamin','magamax'),sx=mixControl('sxmin','sxmax'),sy=mixControl('symin','symax'),rgba=colorNow(),fixRot=num('rotfix'),fix=Math.max(0,Math.min(9,Math.round(num('positionFix')))),freeX=num('posx'),freeY=num('posy'),fixed=(FIXED_CHOICES.find(x=>x.canonical_index===fix)||{coord:[0,0]}).coord,px=fix?fixed[0]:freeX,py=fix?fixed[1]:freeY,cx=W/2+px*POS_SCALE,cy=H/2-py*POS_SCALE;if($('showAnchorOverlay')&&$('showAnchorOverlay').checked){ctx.save();ctx.globalCompositeOperation='source-over';ctx.globalAlpha=.92;ctx.imageSmoothingEnabled=false;ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.setLineDash([6,4]);ctx.strokeRect(cx-64*Math.abs(sx),cy-64*Math.abs(sy),128*Math.abs(sx),128*Math.abs(sy));ctx.setLineDash([]);ctx.beginPath();ctx.moveTo(cx-10,cy);ctx.lineTo(cx+10,cy);ctx.moveTo(cx,cy-10);ctx.lineTo(cx,cy+10);ctx.stroke();ctx.restore()}const seqText=activeTimelineSequence===null?'—':activeTimelineSequence,paramText=activeTimelineParameter===null?'—':activeTimelineParameter;$('status').textContent=`SEQ ${seqText} · PARAM ${paramText} · ${name} · VolumeSet ${$('volumeSource').value==='0'?'BGM '+($('bgmResponseModel').value==='gameplay'?'VOL SCALE':'raw'):'Stick'} ${v.toFixed(3)} · anchor ${cx.toFixed(0)},${cy.toFixed(0)}${(cx<0||cx>W||cy<0||cy>H)?' OFF-SCREEN':''} · source ${sx.toFixed(2)}×${sy.toFixed(2)} · feedback ${mx.toFixed(3)}×${my.toFixed(3)} / A ${ma.toFixed(3)} · ${raw?'RAW RGB':`smooth resolve ${source.width}×${source.height}`} · rotation ${Math.abs(fixRot)<1e-9?'accum '+rotationAccum.toFixed(1)+'°':'fixed '+fixRot.toFixed(1)+'°'} · ${logicalFrames}f`;}
let decodeCtx=null,lastAudioUrl=null,activePeakBytes=null,activePeakChannels=2,activePeakRate=XBOX_AUDIO_RATE,activePeakQuantum=XBOX_AUDIO_QUANTUM,activeBgmTrack=null;const bgmAudio=$('bgmAudio'),bgmTracks=DB.bgm_tracks||[],bgmPreset=$('bgmPreset'),bgmPreviewStatus=$('bgmPreviewStatus');
function setBgmStatus(text,bad=false){bgmPreviewStatus.textContent=text;bgmPreviewStatus.style.color=bad?'#f0b7b7':''}
function decodePeakEnvelopeB64(track){const env=track&&track.meter_envelope;if(!env||!env.data_b64)return null;try{const raw=atob(env.data_b64),out=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)out[i]=raw.charCodeAt(i)&255;return out}catch(_){return null}}
function setPeakEnvelope(bytes,channels=2,sampleRate=XBOX_AUDIO_RATE,quantum=XBOX_AUDIO_QUANTUM){activePeakBytes=bytes;activePeakChannels=Math.max(1,channels|0);activePeakRate=Math.max(1,Number(sampleRate)||XBOX_AUDIO_RATE);activePeakQuantum=Math.max(1,Number(quantum)||XBOX_AUDIO_QUANTUM);updateAudioQuantumStatus()}
function updateAudioQuantumStatus(){const el=$('bgmQuantumStatus');if(!el)return;const ms=1000*activePeakQuantum/activePeakRate;if(activePeakBytes){const source=activeBgmTrack?'FFmpeg-precomputed game-BGM envelope':'decoded host-audio envelope';el.textContent=`BGM analysis: ${activePeakQuantum}-sample peak quantum @ ${activePeakRate} Hz = ${ms.toFixed(3)} ms · ${source} · audio stays on native media-element output`;el.style.color='#bde6c6'}else{el.textContent=`Xbox 360 meter quantum: ${XBOX_AUDIO_QUANTUM} samples @ ${XBOX_AUDIO_RATE/1000} kHz = ${(1000*XBOX_AUDIO_QUANTUM/XBOX_AUDIO_RATE).toFixed(3)} ms. Meter envelope unavailable; audio can still play directly.`;el.style.color='#f0d99d'}}
function ensureDecodeContext(){if(decodeCtx)return decodeCtx;const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return null;try{decodeCtx=new AC({sampleRate:XBOX_AUDIO_RATE})}catch(_){try{decodeCtx=new AC()}catch(__){decodeCtx=null}}return decodeCtx}
function peakEnvelopeFromBuffer(buffer){const channels=Math.max(1,Math.min(2,buffer.numberOfChannels||1)),rate=Number(buffer.sampleRate)||XBOX_AUDIO_RATE,quantum=Math.max(1,Math.round(rate*XBOX_AUDIO_QUANTUM/XBOX_AUDIO_RATE)),frames=buffer.length||0,count=Math.ceil(frames/quantum),bytes=new Uint8Array(count*channels),left=buffer.getChannelData(0),right=channels>1?buffer.getChannelData(1):left;for(let q=0;q<count;q++){const start=q*quantum,end=Math.min(frames,start+quantum);let pl=0,pr=0;for(let i=start;i<end;i++){pl=Math.max(pl,Math.abs(left[i]||0));pr=Math.max(pr,Math.abs(right[i]||0))}bytes[q*channels]=Math.min(255,Math.round(clamp(pl,0,1)*255));if(channels>1)bytes[q*channels+1]=Math.min(255,Math.round(clamp(pr,0,1)*255))}return{bytes,channels,rate,quantum}}
function sampleBgmMeterAt(timeSeconds,updateText=true){if(!activePeakBytes||bgmAudio.paused){bgmLevel=0;bgmPeakL=0;bgmPeakR=0}else{const q=Math.max(0,Math.floor(Math.max(0,Number(timeSeconds)||0)*activePeakRate/activePeakQuantum)),count=Math.floor(activePeakBytes.length/activePeakChannels),idx=Math.min(Math.max(0,count-1),q)*activePeakChannels;bgmPeakL=(activePeakBytes[idx]||0)/255;bgmPeakR=activePeakChannels===1?bgmPeakL:(activePeakBytes[idx+1]||0)/255;bgmLevel=activePeakChannels===1?bgmPeakL:(bgmPeakL+bgmPeakR)*0.5}if(updateText){const detail=activePeakChannels===1?`peak ${bgmPeakL.toFixed(3)} · raw mean ${bgmLevel.toFixed(3)}`:`peak L ${bgmPeakL.toFixed(3)} · peak R ${bgmPeakR.toFixed(3)} · raw mean ${bgmLevel.toFixed(3)}`;$('bgmMeter').textContent=`BGM meter: ${detail}`}}
function updateBgmMeter(){sampleBgmMeterAt(Number(bgmAudio.currentTime)||0,true)}
function loadPreviewTrack(track){if(!track||!track.preview){setBgmStatus(track?`${track.name}: native ${track.native_format} found, but no browser preview is available. Install FFmpeg and rebuild the simulator.`:'No BGM selected.',true);return false}if(lastAudioUrl){URL.revokeObjectURL(lastAudioUrl);lastAudioUrl=null}activeBgmTrack=track;bgmChannels=2;setPeakEnvelope(decodePeakEnvelopeB64(track),Number(track.meter_envelope&&track.meter_envelope.channels)||2,Number(track.meter_envelope&&track.meter_envelope.sample_rate_hz)||XBOX_AUDIO_RATE,Number(track.meter_envelope&&track.meter_envelope.quantum_samples)||XBOX_AUDIO_QUANTUM);resetGameplayBgmNormalizer();bgmAudio.src=track.preview;bgmAudio.load();setBgmStatus(`${track.name} · ${track.native_format} → ${track.preview_codec} browser preview · direct audible playback${activePeakBytes?' + native-quantum peak envelope':' · meter envelope unavailable'}`);return true}
for(const [i,track] of bgmTracks.entries()){const o=document.createElement('option');o.value=String(i);o.textContent=`${track.name} · ${track.native_format}${track.preview?'':' · preview unavailable'}`;bgmPreset.appendChild(o)}if(bgmTracks.length){const ready=bgmTracks.filter(x=>x.preview).length,metered=bgmTracks.filter(x=>x.meter_envelope&&x.meter_envelope.data_b64).length;setBgmStatus(`${bgmTracks.length} console-native BGM track(s) found · ${ready} browser preview(s) ready · ${metered} peak envelope(s).`)}else{bgmPreset.disabled=true}
bgmPreset.onchange=()=>{if(bgmPreset.value==='')return;loadPreviewTrack(bgmTracks[Number(bgmPreset.value)])};
$('bgmFile').onchange=async()=>{const file=$('bgmFile').files&&$('bgmFile').files[0];if(!file)return;const ext=(file.name.split('.').pop()||'').toLowerCase();if(ext==='wma'||ext==='at3'){const matchIndex=bgmTracks.findIndex(t=>t.name.toLowerCase()===file.name.toLowerCase()&&t.preview);if(matchIndex>=0){bgmPreset.value=String(matchIndex);loadPreviewTrack(bgmTracks[matchIndex]);return}setBgmStatus(`${file.name}: browsers do not natively decode ${ext.toUpperCase()}. Rebuild this simulator from the rip with FFmpeg so the toolkit can create a local browser-safe preview.`,true);return}activeBgmTrack=null;setPeakEnvelope(null,2,XBOX_AUDIO_RATE,XBOX_AUDIO_QUANTUM);let meterOk=false;const ac=ensureDecodeContext();if(ac){try{const decoded=await ac.decodeAudioData(await file.arrayBuffer());bgmChannels=Math.max(1,decoded.numberOfChannels||2);const env=peakEnvelopeFromBuffer(decoded);setPeakEnvelope(env.bytes,env.channels,env.rate,env.quantum);meterOk=true}catch(_){bgmChannels=2}}if(lastAudioUrl)URL.revokeObjectURL(lastAudioUrl);lastAudioUrl=URL.createObjectURL(file);resetGameplayBgmNormalizer();bgmAudio.src=lastAudioUrl;bgmAudio.load();setBgmStatus(`${file.name} · browser-loaded host audio · direct audible playback${meterOk?' + decoded peak envelope':' · meter unavailable'}`,!meterOk)};bgmAudio.addEventListener('error',()=>setBgmStatus('The browser could not decode this audio source. For WMA/AT3 use a toolkit-generated preview.',true));
function tick(now){let dt=Math.min(0.1,(now-last)/1000);last=now;if(running){accum+=dt;const mediaNow=Number(bgmAudio.currentTime)||0;while(accum>=STEP){const logicalAudioTime=Math.max(0,mediaNow-(accum-STEP));sampleBgmMeterAt(logicalAudioTime,false);logicalStep();accum-=STEP}sampleBgmMeterAt(mediaNow,true);drawDisplay()}else updateBgmMeter();requestAnimationFrame(tick)}
for(const name of DB.evidence.shape_resources){const o=document.createElement('option');o.value=name;o.textContent=`${DB.evidence.shape_resources.indexOf(name)} · ${name}`;$('shape').appendChild(o)}$('shape').value=DB.evidence.shape_resources[DB.evidence.check_mode_controls.shape.default]||'WhiteCircle';
for(const choice of FIXED_CHOICES){const o=document.createElement('option');o.value=String(choice.canonical_index);o.textContent=choice.canonical_index===0?'0 · Free X/Y (default 0,0 = center)':`${choice.canonical_index} · ${choice.label} · X ${choice.coord[0]} / Y ${choice.coord[1]}`;$('positionFix').appendChild(o)}
$('schema').innerHTML=DB.evidence.parameter_fields.map((x,i)=>`<code>${String(i).padStart(2,'0')} · ${x}</code>`).join('');
$('play').onclick=()=>{running=!running;$('play').textContent=running?'Pause':'Play';last=performance.now()};$('reset').onclick=resetFeedback;$('toggleDebug').onclick=toggleDebug;$('fullscreen').onclick=toggleFullscreen;$('togglePanel').onclick=togglePanel;$('resetBgmNormalizer').onclick=resetGameplayBgmNormalizer;$('bgmResponseModel').onchange=()=>{resetGameplayBgmNormalizer();if(!running)drawDisplay()};
const ignoredTypingTarget=e=>['INPUT','SELECT','TEXTAREA'].includes((e.target&&e.target.tagName)||'');document.addEventListener('keydown',e=>{const k=e.key.toLowerCase();if(!ignoredTypingTarget(e)&&k==='x'&&!e.repeat){resetFeedback();e.preventDefault();return}if(!ignoredTypingTarget(e)&&k==='y'&&!e.repeat){toggleDebug();e.preventDefault();return}if(!ignoredTypingTarget(e)&&k==='f'&&!e.repeat){toggleFullscreen();e.preventDefault();return}if(!ignoredTypingTarget(e)&&k==='m'&&!e.repeat){togglePanel();e.preventDefault();return}if(!ignoredTypingTarget(e)&&['arrowup','arrowdown','arrowleft','arrowright','w','a','s','d'].includes(k)){stickKeys.add(k);e.preventDefault()}});document.addEventListener('keyup',e=>stickKeys.delete(e.key.toLowerCase()));window.addEventListener('blur',()=>stickKeys.clear());
for(const el of document.querySelectorAll('input,select')){if(['script','frame','bgmFile'].includes(el.id))continue;el.addEventListener('input',()=>{normalizeNativeRanges(el.id);if(!running)drawDisplay()})}
const paramSets=DB.parameter_sets||[],seqSets=DB.sequence_sets||[],timelinePresets=DB.timeline_presets||[],paramSel=$('parameterPreset'),seqSel=$('sequencePreset'),timelinePresetSel=$('timelinePreset'),quickTimelinePreset=$('quickTimelinePreset');let activeTimelineSequence=null,activeTimelineParameter=null;
if(paramSets.length){$('setStatus').textContent=`Loaded ${paramSets.length} ParameterSet rows and ${seqSets.length} SequenceSet rows from the supplied rip.`;for(const p of paramSets){const o=document.createElement('option');o.value=String(p.id);o.textContent=`PARAM_${p.id}`;paramSel.appendChild(o)}}else{paramSel.disabled=true;$('applyParameter').disabled=true}
if(seqSets.length){for(const s of seqSets){const active=s.parameter_ids.filter(x=>x>=0);const o=document.createElement('option');o.value=String(s.id);o.textContent=`SEQUENCE_${s.id} → ${active.length?active.map(x=>'PARAM_'+x).join(', '):'empty'}`;seqSel.appendChild(o)}}else{seqSel.disabled=true;$('applySequence').disabled=true}
if(timelinePresets.length){timelinePresets.forEach((p,i)=>{const label=`${p.script} @ ${p.frame} → SEQUENCE_${p.sequence_id}${p.parameter_ids.length?' / '+p.parameter_ids.map(x=>'PARAM_'+x).join(', '):''}`;for(const target of [timelinePresetSel,quickTimelinePreset]){const o=document.createElement('option');o.value=String(i);o.textContent=label;target.appendChild(o)}})}else{timelinePresetSel.disabled=true;quickTimelinePreset.disabled=true;$('applyTimelinePreset').disabled=true}
const fieldTargets=['magxmin','magxmax','magymin','magymax','magamin','magamax','bgr','bgg','bgb','bga',null,'positionFix','posx','posy','rotbase','rotadd','rotfix','sxmin','sxmax','symin','symax','rmin','rmax','gmin','gmax','bmin','bmax','amin','amax'];
function applyParameter(id,resetRotation=true){const p=paramSets.find(x=>x.id===Number(id));if(!p||p.values.length!==fieldTargets.length)return false;for(let i=0;i<p.values.length;i++){if(i===10){const idx=Math.max(0,Math.min(DB.evidence.shape_resources.length-1,Math.round(Number(p.values[i])||0)));$('shape').value=DB.evidence.shape_resources[idx];continue}const target=fieldTargets[i];if(target){if(i===11){const rawFix=Math.max(0,Math.min(9,Math.round(Number(p.values[i])||0)));$(target).value=String(FIXED_CANON[rawFix]??0)}else $(target).value=String(p.values[i])}}normalizeNativeRanges();activeTimelineParameter=Number(id);if(resetRotation)rotationAccum=0;if(!running)drawDisplay();return true}
$('applyParameter').onclick=()=>applyParameter(paramSel.value);$('applySequence').onclick=()=>{const s=seqSets.find(x=>x.id===Number(seqSel.value));if(!s)return;activeTimelineSequence=s.id;const first=s.parameter_ids.find(x=>x>=0);if(first!==undefined){paramSel.value=String(first);applyParameter(first)}};
const sel=$('script'),frame=$('frame'),events=$('events'),scriptStatus=$('scriptStatus'),timelines=DB.timelines||[];if(timelines.length){for(const t of timelines){const o=document.createElement('option');o.value=t.script;o.textContent=t.script;sel.appendChild(o)}}else{const o=document.createElement('option');o.textContent='No decoded DAT timeline';o.value='';sel.appendChild(o);sel.disabled=true;frame.disabled=true;$('timelineSeed').disabled=true;$('rerollTimelineSeed').disabled=true}
const timelineRuntime={active:false,display:false,sequenceId:null,sequenceIndex:0,changeCounter:0,changeMin:DEFAULT_CHANGE_TIME,changeMax:DEFAULT_CHANGE_TIME,changeThreshold:DEFAULT_CHANGE_TIME,dirty:false,currentParameter:null,volumeWindow:GAME_VOL_WINDOW,rngState:1,processedFrame:-1};
function seedValue(){const n=Number($('timelineSeed').value);return Number.isFinite(n)?(Math.trunc(n)>>>0):1}
function crtRand15(){timelineRuntime.rngState=(Math.imul(timelineRuntime.rngState,0x343fd)+0x269ec3)>>>0;return (timelineRuntime.rngState>>>16)&0x7fff}
function visualizerRandom30(){const high=crtRand15(),low=crtRand15();return (low+(high*0x8000))>>>0}
function rollChangeThreshold(){const lo=Math.trunc(timelineRuntime.changeMin),hi=Math.trunc(timelineRuntime.changeMax),span=hi-lo;if(span<=0){timelineRuntime.changeThreshold=lo;return lo}timelineRuntime.changeThreshold=lo+(visualizerRandom30()%span);return timelineRuntime.changeThreshold}
function resetTimelineRuntime(){timelineRuntime.active=false;timelineRuntime.display=false;timelineRuntime.sequenceId=null;timelineRuntime.sequenceIndex=0;timelineRuntime.changeCounter=0;timelineRuntime.changeMin=DEFAULT_CHANGE_TIME;timelineRuntime.changeMax=DEFAULT_CHANGE_TIME;timelineRuntime.changeThreshold=DEFAULT_CHANGE_TIME;timelineRuntime.dirty=false;timelineRuntime.currentParameter=null;timelineRuntime.volumeWindow=GAME_VOL_WINDOW;timelineRuntime.rngState=seedValue();timelineRuntime.processedFrame=-1;activeTimelineSequence=null;activeTimelineParameter=null}
function setRuntimeSequence(id){const seq=seqSets.find(x=>x.id===Number(id));timelineRuntime.sequenceId=seq?Number(id):null;timelineRuntime.sequenceIndex=0;timelineRuntime.changeCounter=0;timelineRuntime.dirty=!!seq;timelineRuntime.currentParameter=null;activeTimelineSequence=timelineRuntime.sequenceId;if(seq)seqSel.value=String(seq.id)}
function setRuntimeChangeTime(args){const lo=Math.trunc(Number(args&&args[0])||0),rawHi=args&&args.length>1?Math.trunc(Number(args[1])||0):lo,hi=Math.max(lo,rawHi);timelineRuntime.changeMin=lo;timelineRuntime.changeMax=hi;rollChangeThreshold()}
function processTimelineEventsAtFrame(t,f){for(const e of t.events){if(Number(e.frame)!==f)continue;if(e.opcode==='VL_START')timelineRuntime.active=true;else if(e.opcode==='VL_END')timelineRuntime.active=false;else if(e.opcode==='VL_DISP_ON')timelineRuntime.display=true;else if(e.opcode==='VL_DISP_OFF')timelineRuntime.display=false;else if(e.opcode==='VL_SEQUENCESET')setRuntimeSequence(e.args[0]);else if(e.opcode==='VL_CHANGETIME')setRuntimeChangeTime(e.args);else if(e.opcode==='VL_VOLUME_SCALE'){timelineRuntime.volumeWindow=Math.max(5,Math.trunc(Number(e.args[0])||GAME_VOL_WINDOW));configureGameplayBgmWindow(timelineRuntime.volumeWindow)}}}
function tickRuntimeSequence(applyUi=true){if(!timelineRuntime.active||timelineRuntime.sequenceId===null)return;const seq=seqSets.find(x=>x.id===timelineRuntime.sequenceId);if(!seq||!seq.parameter_ids.length)return;if(timelineRuntime.dirty){timelineRuntime.dirty=false;let id=Number(seq.parameter_ids[timelineRuntime.sequenceIndex]);if(id<0){timelineRuntime.sequenceIndex=0;id=Number(seq.parameter_ids[0])}timelineRuntime.currentParameter=id>=0?id:null;activeTimelineParameter=timelineRuntime.currentParameter;if(applyUi&&timelineRuntime.currentParameter!==null){paramSel.value=String(timelineRuntime.currentParameter);applyParameter(timelineRuntime.currentParameter,false)}}if(timelineRuntime.changeThreshold<timelineRuntime.changeCounter){timelineRuntime.sequenceIndex++;if(timelineRuntime.sequenceIndex>=seq.parameter_ids.length||Number(seq.parameter_ids[timelineRuntime.sequenceIndex])===-1)timelineRuntime.sequenceIndex=0;timelineRuntime.changeCounter=0;timelineRuntime.dirty=true;rollChangeThreshold()}else timelineRuntime.changeCounter++}
function stepTimelineRuntime(t,f,applyUi=true){processTimelineEventsAtFrame(t,f);tickRuntimeSequence(applyUi);timelineRuntime.processedFrame=f}
function rebuildTimelineRuntime(t,target,applyUi=true){resetTimelineRuntime();const end=Math.max(0,Math.trunc(Number(target)||0));for(let f=0;f<=end;f++)stepTimelineRuntime(t,f,false);configureGameplayBgmWindow(timelineRuntime.volumeWindow);activeTimelineSequence=timelineRuntime.sequenceId;activeTimelineParameter=timelineRuntime.currentParameter;if(activeTimelineSequence!==null)seqSel.value=String(activeTimelineSequence);if(applyUi&&activeTimelineParameter!==null){paramSel.value=String(activeTimelineParameter);applyParameter(activeTimelineParameter,false)}}
function timelineStatusText(f){const range=timelineRuntime.changeMin===timelineRuntime.changeMax?String(timelineRuntime.changeMin):`[${timelineRuntime.changeMin},${timelineRuntime.changeMax})`;return `frame ${f} · active ${timelineRuntime.active?'yes':'no'} · display ${timelineRuntime.display?'on':'off'} · sequence ${timelineRuntime.sequenceId??'—'} · parameter ${timelineRuntime.currentParameter??'—'} · sequence slot ${timelineRuntime.sequenceIndex} · change range ${range} · threshold ${timelineRuntime.changeThreshold} · counter ${timelineRuntime.changeCounter} · RNG 0x${timelineRuntime.rngState.toString(16).padStart(8,'0')} · adaptive volume window ${timelineRuntime.volumeWindow} frames`}
function renderTimeline(rebuildRows=true,rebuildRuntime=true){const t=timelines.find(x=>x.script===sel.value);if(rebuildRows)events.innerHTML='';if(!t){scriptStatus.textContent='No DAT timeline loaded.';configureGameplayBgmWindow(GAME_VOL_WINDOW);resetTimelineRuntime();return}frame.max=t.duration_frames||0;const f=Math.max(0,Math.min(Number(t.duration_frames)||0,Math.trunc(Number(frame.value)||0)));if(rebuildRows){for(const e of t.events){const tr=document.createElement('tr');const args=e.opcode==='VL_CHANGETIME'&&e.args.length>=2?`${e.args[0]} .. ${e.args[1]} (upper exclusive)`:e.args.join(' ');tr.innerHTML=`<td>${e.frame}</td><td>${e.opcode}</td><td class="mono">${args||'—'}</td>`;events.appendChild(tr)}}if(rebuildRuntime)rebuildTimelineRuntime(t,f,true);scriptStatus.textContent=timelineStatusText(f)}
function advanceTimelineFrame(){if(!$('timelineFollow').checked||!timelines.length||!sel.value)return;const t=timelines.find(x=>x.script===sel.value);if(!t)return;const end=Number(t.duration_frames)||0,current=Number(frame.value)||0;if(current<end){const next=current+1;frame.value=String(next);stepTimelineRuntime(t,next,true);scriptStatus.textContent=timelineStatusText(next)}}
function applyTimelinePresetIndex(index){const i=Number(index),p=timelinePresets[i];if(!p)return;timelinePresetSel.value=String(i);quickTimelinePreset.value=String(i);$('volumeSource').value='0';$('bgmResponseModel').value='gameplay';resetGameplayBgmNormalizer();sel.value=p.script;frame.value=String(p.frame);renderTimeline(true,true);resetFeedback();$('presetSummary').textContent=`${p.script} · authored frame ${p.frame} · SEQUENCE_${p.sequence_id}${p.parameter_ids.length?' · '+p.parameter_ids.map(x=>'PARAM_'+x).join(', '):''}`};
$('applyTimelinePreset').onclick=()=>applyTimelinePresetIndex(timelinePresetSel.value);timelinePresetSel.onchange=()=>applyTimelinePresetIndex(timelinePresetSel.value);quickTimelinePreset.onchange=()=>{if(quickTimelinePreset.value!=='')applyTimelinePresetIndex(quickTimelinePreset.value)};
sel.onchange=()=>{$('volumeSource').value='0';$('bgmResponseModel').value='gameplay';frame.value='0';renderTimeline(true,true);resetGameplayBgmNormalizer();resetFeedback()};frame.oninput=()=>{renderTimeline(false,true)};$('timelineSeed').onchange=()=>renderTimeline(false,true);$('rerollTimelineSeed').onclick=()=>{$('timelineSeed').value=String(Date.now()>>>0);renderTimeline(false,true)};$('timelineFollow').onchange=()=>{if($('timelineFollow').checked){$('volumeSource').value='0';$('bgmResponseModel').value='gameplay';renderTimeline(false,true)}};renderTimeline(true,true);resetGameplayBgmNormalizer();resetFeedback();requestAnimationFrame(tick);
</script></body></html>'''
    return template.replace("__DATA__", payload)


def build_visualizer_simulator(input_path: Path | None, output: Path, ffmpeg_path: str | None = None) -> dict:
    timelines = _visualizer_timelines(input_path)
    sets = _visualizer_sets(input_path)
    bgm = _prepare_bgm_previews(input_path, output, ffmpeg_path=ffmpeg_path)
    dataset = {
        "format": "SIIG_VISUALIZER_SIMULATOR",
        "version": VISUALIZER_SIMULATOR_VERSION,
        "timelines": timelines,
        "bgm_tracks": bgm["tracks"],
        "parameter_sets": sets["parameter_sets"],
        "sequence_sets": sets["sequence_sets"],
        "timeline_presets": _timeline_presets(timelines, sets["sequence_sets"]),
        "shape_images": _shape_image_payloads(input_path),
        "evidence": {
            "primary_visual_reference": "June 10 Visualizer Check Mode footage",
            "runtime_assets": ["visualizerSet.bin.gz.sdat", "ParameterSet.nut", "SequenceSet.nut"],
            "parameter_preset_count": 49,
            "sequence_count": 57,
            "parameter_width": 29,
            "parameter_fields": list(PARAMETER_FIELDS),
            "shape_resources": list(SHAPE_RESOURCES),
            "check_mode_control_rows": 30,
            "check_mode_controls": VISUALIZER_CHECK_CONTROLS,
            "check_mode_input": {
                "volume_source_0": "from BGM",
                "volume_source_1": "from Stick",
                "reset_button": "X / input mask 0x40",
                "toggle_info_button": "Y / input mask 0x80",
                "position_free_bounds": {"x": [-560, 560], "y": [-360, 360]},
            },
            "native_range_contract": {
                "magnify_scale_x": "max >= min; June10 Function_821750F8 assertion",
                "magnify_scale_y": "max >= min; June10 Function_821750F8 assertion",
                "magnify_alpha": "max >= min; June10 Function_821751B0 assertion; independently observed on real hardware 2026-09-20",
                "shape_rgba": "each channel max >= min; June10 Function_82174E88 assertions",
                "shape_scale_xy": "not generalized: June10 FUN_821750E0 stores four scale floats without the same range-order assertion",
                "simulator_policy": "clamp the edited endpoint to preserve max >= min instead of reproducing the native debug assertion",
            },
            "loaded_set_files": sets["source_files"],
            "bgm_meter": {
                "value_semantics": "arithmetic mean of the two XAudio2 per-channel peak levels",
                "range": [0.0, 1.0],
                "game_channels": 2,
                "check_mode_transfer_after_meter": "none; Visualizer Check Mode consumes the returned linear float directly",
                "normal_stage_transfer_after_meter": "300-sample adaptive min/max normalizer -> VOL SCALE; parameter interpolation consumes VOL SCALE",
                "xbox360_processing_quantum_ms": XBOX360_XAUDIO2_QUANTUM_MS,
                "xbox360_sample_rate_hz": XBOX360_XAUDIO2_SAMPLE_RATE,
                "xbox360_quantum_samples": XBOX360_XAUDIO2_QUANTUM_SAMPLES,
                "native_peak_window": "maximum absolute level per channel during one XAudio2 processing pass",
                "browser_bridge": "generated game-BGM previews use an FFmpeg-precomputed stereo peak envelope at one byte/channel per native 256-sample 48 kHz quantum; each 60 Hz logical simulation step samples its own playback-time point, including browser catch-up steps; HTML audio stays directly audible; user-loaded browser audio is decoded only to build the same meter envelope",
                "browser_phase_boundary": "absolute HTMLMediaElement.currentTime remains host-scheduled and is not claimed phase-aligned to Xbox 360 XAudio2 processing-pass boundaries",
                "logical_step_meter_resampling": True,
            },
            "gameplay_volume_normalizer": {
                "constructor": "June10 Function_82177510",
                "configure": "June10 Function_82177300",
                "normalize": "June10 Function_821773F0",
                "update": "June10 Function_82177648",
                "debug_average": "June10 Function_82175FA8",
                "constructor_default_window_samples": GAMEPLAY_VOLUME_WINDOW,
                "dat_override": "VL_VOLUME_SCALE / opcode 0xCE calls Function_82177300 and replaces the adaptive window length in Visualizer update frames (minimum 5)",
                "reference_stage_window_frames": {"level4_stage2.dat": 180, "level4_stage4.dat": 180, "level4_stage5.dat": 180},
                "diagnostic_history_samples": GAMEPLAY_DIAGNOSTIC_HISTORY,
                "minimum_span": GAMEPLAY_VOLUME_MIN_SPAN,
                "initial_min": 0.0,
                "initial_max": 1.0,
                "initial_scale": 1.0,
                "formula": "clamp by MIN/MAX; otherwise (VOL-MIN)/max(abs(MAX-MIN),0.001)",
                "real_hardware_reference": "project-owner June 10 build recordings of stages 4-2, 4-4 and 4-5 on Xbox 360 hardware (2026-09-19)",
                "simulator_update": "post-meter adaptive state updates once per logical 60 Hz simulator step; upstream meter window is one 256-sample / 5 1/3 ms Xbox 360 XAudio2 quantum at 48 kHz; browser query phase remains approximate",
            },
            "presentation_softness": {
                "default_px": 0.8,
                "range_px": [0.0, 8.0],
                "default_intensity": 0.90,
                "intensity_range": [0.1, 1.0],
                "default_bloom": 0.46,
                "bloom_range": [0.0, 1.0],
                "default_resolve": "hardware-like",
                "resolve_size": list(DISPLAY_RESOLVE_SIZE),
                "scope": "display-only high-quality half-resolution resolve + base/screen-bloom post-pass after the recovered feedback recurrence",
                "runtime_sampler_unchanged": True,
                "calibration": "WIP191 presentation overhaul after project-owner feedback that recursive point-sampled feedback still presented as large chunky blocks",
                "reason": "smooth only the host-visible final composite while retaining the recovered point-filtered recursive feedback buffers; Raw recovered RGB remains selectable",
            },
            "native_bgm_preview": {
                "native_extensions": [".wma", ".at3"],
                "xbox360": "WMA",
                "ps3": "AT3/ATRAC3+",
                "ffmpeg_available": bgm["ffmpeg_available"],
                "preview_codec": bgm["preview_codec"],
                "native_track_count": bgm["native_track_count"],
                "preview_count": bgm["preview_count"],
                "policy": "original native BGM is untouched; browser-safe previews are generated only beside the user's local simulator",
                "preview_pcm_layout": "FFmpeg output normalized to stereo 48 kHz before browser-safe encoding",
                "browser_audio_policy": "native HTML audio is never routed through MediaElementAudioSourceNode; generated previews use build-time FFmpeg meter envelopes and user-loaded browser audio is decoded only for a local envelope, avoiding file:// analyser/CORS muting",
            },
            "dat_opcodes": ["VL_START", "VL_END", "VL_DISP_ON", "VL_DISP_OFF", "VL_SEQUENCESET", "VL_CHANGETIME", "VL_VOLUME_SCALE"],
            "sequence_change_timing": {
                "set_sequence": "June10 Function_82175C10 resets sequence slot=0, counter=0 and sets a dirty/apply flag",
                "set_change_time": "June10 Function_82175DB0 stores min/max and immediately rolls the current threshold",
                "pick_threshold": "June10 Function_82175CC0: min + random % (max-min), so max is exclusive; equal bounds use min without RNG",
                "update": "June10 Function_82177648 applies a dirty slot, then advances when threshold < counter; next slot applies on the following active update",
                "default_bounds": [VISUALIZER_CHANGE_TIME_DEFAULT, VISUALIZER_CHANGE_TIME_DEFAULT],
                "sequence_terminator": -1,
                "rng_wrapper": "June10 Function_8249A9D8 concatenates two CRT rand15 calls into one 30-bit value",
                "rng_lcg": "state = state*0x343FD + 0x269EC3 mod 2^32; rand15=(state>>16)&0x7FFF",
                "runtime_seed": "Function_8249A9B0 seeds CRT state from Function_82495800 timer-derived value; exact run seed is not authored in DAT",
                "browser_seed_policy": "user-controlled deterministic 32-bit simulator seed for reproducible stage playback",
            },
            "render_target_size": list(RENDER_TARGET_SIZE),
            "shape_texture_size": list(SHAPE_TEXTURE_SIZE),
            "position_fix_coords": [list(item) for item in POSITION_FIX_COORDS],
            "position_fix_canonical_indices": list(POSITION_FIX_CANONICAL_INDICES),
            "position_fix_choices": [
                {
                    "canonical_index": item["canonical_index"],
                    "raw_indices": list(item["raw_indices"]),
                    "label": item["label"],
                    "coord": list(item["coord"]),
                }
                for item in POSITION_FIX_CHOICES
            ],
            "position_coordinate_system": {
                "origin": "center of 1280x720 feedback target",
                "x_axis": "+X right",
                "y_axis": "+Y up",
                "logical_to_target_scale": POSITION_LOGICAL_TO_TARGET_SCALE,
                "canvas_bridge": "canvas_x = 640 + position_x; canvas_y = 360 - position_y",
                "hardware_evidence": "project-owner retail-hardware stage 4-5: PARAM_7 free Y=+360 still seeds structured feedback at the top edge; WIP191 1.5x moved the complete source off-target",
                "executable_evidence": "June10 Function_82177DF0 passes X * 0.0015625 (1/640) and Y * 0.0027777778 (1/360) into the 1280x720 renderer; direct target-pixel mapping follows exactly",
                "evidence_grade": "executable-backed direct mapping plus independent hardware regression cross-check",
            },
            "render_pipeline": [
                "clear destination feedback target with SHAPE clear color",
                "draw current 128x128 SHAPE source at free/fixed position with source scale/color/rotation",
                "draw previous feedback target through magnify scale/alpha around the same position without framebuffer rotation",
                "swap ping-pong feedback targets",
            ],
            "runtime_functions": {
                "visualizer_main_ctor": "May11 Function_8216B168",
                "parameter_apply": "May11 Function_8216B4F8 / Function_8216B660",
                "feedback_render": "May11 Function_8216D830 / Function_8216DC18",
                "source_transform": "May11 Function_8216E380",
                "fixed_position": "May11 LAB_8216D8F8 + DAT_825624C8",
                "bgm_meter_capture": "June10 Function_82495500 + FUN_82496828(+0x400)",
                "bgm_meter_latch": "June10 FUN_824956C0 / FUN_82495360",
                "check_mode_volume_select": "June10 Function_82183B20",
                "sequence_set": "June10 Function_82175C10",
                "sequence_change_range": "June10 Function_82175DB0",
                "sequence_change_pick": "June10 Function_82175CC0",
                "sequence_update": "June10 Function_82177648",
                "sequence_rng30": "June10 Function_8249A9D8 / Function_824A9E88",
            },
            "render_model": "executable-backed ping-pong feedback pipeline; uses real user-rip SHAPE PNG morphology when available, otherwise procedural stand-ins",
            "shape_image_policy": "proprietary PNGs are embedded only into locally generated simulator HTML from a user-supplied rip; never bundled in source",
            "feedback_sampler": {
                "fetch_constant_dword3": "0x00001414",
                "addressing": "repeat on X/Y/Z",
                "mag_filter": "point",
                "min_filter": "point",
                "mip_filter": "point (no mip chain used by the feedback target)",
                "anisotropy": "disabled",
                "browser_bridge": "imageSmoothingEnabled=false for the recursive previous-feedback draw",
                "evidence": "May11 Function_821AA630 -> Function_8226F240 -> Function_8226EA98 -> Function_8226F5C0; xe_gpu_texture_fetch_t field layout cross-checked against Xenia xenos.h",
            },
            "effectblur_shader": {
                "retail_microcode_sha256": "550328d21de6af38fde4a0814bd71aa68352667c826b0d7b1f172796c3db8116",
                "microcode_size_bytes": 72,
                "control_flow": "one 2D texture fetch, then two ALU instructions, then end",
                "texture_fetch": "sample TextureSampler into r0.xyz while keeping r0.w",
                "alpha_write": "r0.w = Alpha.w",
                "export": "color0 = r0",
                "rgb_equation": "shader source RGB = sampled previous-feedback RGB; sampled texture alpha is ignored",
                "alpha_equation": "shader source alpha = uniform feedback Alpha.w",
                "ps3_cross_check": "retail PS3 EffectBlurPS exposes only TextureSampler and Alpha; draw uploads (0,0,0,alpha)",
                "browser_bridge": "feedback working canvases are opaque RGB surfaces so Canvas lighter does not re-multiply sampled feedback RGB by browser source alpha",
                "evidence": "private retail EffectBlurPS microcode decoded against public Xenia ucode.h instruction layouts; proprietary shader bytes are not bundled",
            },
            "effectblur_blend": {
                "setup": "retail Function_821595F0 immediately before Function_82159CB8",
                "blend_enable": True,
                "packed_rb_blendcontrol": "0x01060106",
                "rgb_src_factor": "SrcAlpha (6)",
                "rgb_dst_factor": "One (1)",
                "rgb_operation": "Add",
                "alpha_src_factor": "SrcAlpha (6)",
                "alpha_dst_factor": "One (1)",
                "alpha_operation": "Add",
                "browser_bridge": "Canvas lighter on opaque feedback working canvases; globalAlpha carries recovered magnify alpha",
                "evidence": "Function_821595F0 -> FUN_8224B188(enable) + FUN_8224B2A8(6) + FUN_8224B338(1); packed state expands to 0x01060106; Xenos BlendFactor values cross-checked against Xenia xenos.h",
            },
            "shape_shader": {
                "shader": "ScreenSpritePS variant 0",
                "microcode_size_bytes": 60,
                "control_flow": "one 2D texture fetch followed by one vector multiply and color export",
                "pixel_equation": "output.rgba = sampled_shape.rgba * runtime_tint.rgba",
                "runtime_tint": "four-component float RGBA propagated by the ScreenSprite vertex path",
                "blend": "Add(SrcAlpha, OneMinusSrcAlpha) for the source SHAPE pass",
                "browser_bridge": "CPU-multiply user-rip PNG RGBA by runtime tint RGBA, then point-sampled Canvas source-over draw",
                "source_only": "shader bytes and proprietary texture pixels are not bundled",
            },
            "shape_sampler": {
                "serialized_tex_fetch_dword3": "0x00000C14",
                "addressing": "repeat on X/Y/Z",
                "mag_filter": "point",
                "min_filter": "point",
                "mip_filter": "point",
                "anisotropy": "disabled",
                "browser_bridge": "when real user-rip SHAPE PNGs are present, imageSmoothingEnabled=false only for their transformed draw",
                "evidence": "retail visualizer TEX 0x34-byte resource header copied by Function_8248BEB0; all ten headers are byte-identical and bind through Function_821AB320 -> Function_821AB6D8 -> Function_8226F5C0; fetch layout cross-checked against Xenia xenos.h",
            },
            "unresolved": [
                "exact browser playback-time meter lookup phase versus the XAudio2 processing-pass cadence",
                "exact Canvas alpha-channel equivalence to Xenos is not claimed; recovered Visualizer feedback RGB recurrence is modeled independently of sampled texture alpha",
            ],
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    path = output / "SIIG_Visualizer_Simulator.html"
    toolkit.write_text_atomic(path, _html(dataset), encoding="utf-8")
    report = {
        "format": dataset["format"],
        "version": dataset["version"],
        "timeline_count": len(timelines),
        "event_count": sum(len(item["events"]) for item in timelines),
        "parameter_preset_count": 49,
        "sequence_count": 57,
        "loaded_parameter_preset_count": len(sets["parameter_sets"]),
        "loaded_sequence_count": len(sets["sequence_sets"]),
        "timeline_preset_count": len(dataset["timeline_presets"]),
        "check_mode_control_rows": 30,
        "shape_count": len(SHAPE_RESOURCES),
        "embedded_shape_image_count": len(dataset["shape_images"]),
        "native_bgm_track_count": bgm["native_track_count"],
        "bgm_preview_count": bgm["preview_count"],
        "bgm_meter_envelope_count": sum(1 for track in bgm["tracks"] if track.get("meter_envelope", {}).get("data_b64")),
        "bgm_preview_codec": bgm["preview_codec"],
        "bgm_cache_hits": bgm.get("cache_hits", 0),
        "bgm_envelope_cache_hits": bgm.get("envelope_cache_hits", 0),
        "bgm_hashes_read": bgm.get("hashes_read", 0),
        "bgm_previews_transcoded": bgm.get("transcoded_previews", 0),
        "bgm_envelopes_decoded": bgm.get("decoded_envelopes", 0),
        "ffmpeg_available": bgm["ffmpeg_available"],
        "html": path.name,
    }
    toolkit.write_json_private(output / "VISUALIZER_SIMULATOR_MANIFEST.json", report, ensure_ascii=False)
    return report
