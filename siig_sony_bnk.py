#!/usr/bin/env python3
"""Minimal Sony 989SND/SCREAM SBlk v3 reader used by SIIG's PS3 sound bank.

This module is intentionally narrow and dependency-free.  The container/table
layout and field meanings were cross-checked against the public vgmstream Sony
BNK implementation (src/meta/bnk_sony.c) and Sony PS-ADPCM behavior.  The code
below is an independent Python implementation for the exact format subset found
in Space Invaders Infinity Gene; no vgmstream source is vendored.
"""

from __future__ import annotations

from array import array
from dataclasses import asdict, dataclass
import csv
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import wave


class SonyBnkError(ValueError):
    """Raised for unsupported, malformed, or inconsistent Sony SBlk banks."""


def _u16be(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise SonyBnkError(f"u16 read outside bank at 0x{offset:X}")
    return struct.unpack_from(">H", data, offset)[0]


def _u32be(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise SonyBnkError(f"u32 read outside bank at 0x{offset:X}")
    return struct.unpack_from(">I", data, offset)[0]


def _cstring(data: bytes, offset: int, maximum: int = 0x100) -> str:
    if offset < 0 or offset >= len(data):
        return ""
    end = min(len(data), offset + maximum)
    nul = data.find(b"\0", offset, end)
    if nul >= 0:
        end = nul
    return data[offset:end].decode("ascii", "replace")


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return cleaned or "stream"


def _sample_rate_from_center(center_note: int, center_fine: int) -> int:
    """Convert SCREAM's PS2 center-note/fine encoding to its SPU sample rate.

    SIIG's bank uses the PS2/48 kHz form (high bit set).  This formulation uses
    the equivalent pitch-register relationship directly rather than copying an
    SDK lookup table.  Integer truncation matches the register/sample-rate path.
    """
    ps2_mode = bool(center_note & 0x80)
    center = (0x100 - center_note) if ps2_mode else center_note
    semitones = (60 - center) + (center_fine / 128.0)
    pitch = int(4096.0 * math.pow(2.0, semitones / 12.0))
    pitch = max(0, min(0x4000, pitch))
    if not ps2_mode:
        pitch = (pitch * 44100) // 48000
    return max(1, (48000 * pitch) // 4096)


@dataclass(frozen=True)
class SonySblkStream:
    index: int
    name: str
    name_resolved: bool
    center_note: int
    center_fine: int
    flags: int
    codec: str
    sample_rate: int
    channels: int
    header_offset: int
    stream_offset: int
    stream_size: int
    absolute_offset: int
    num_samples: int
    loop_flag: bool


@dataclass(frozen=True)
class SonySblkBank:
    outer_version: int
    sections: int
    sblk_version: int
    sblk_offset: int
    data_offset: int
    data_size: int
    sounds_entries: int
    grains_entries: int
    stream_entries: int
    streams: tuple[SonySblkStream, ...]
    covered_audio_bytes: int
    coverage_complete: bool


def _resolve_v3_name(
    data: bytes,
    table1: int,
    table4: int,
    sounds_entries: int,
    table2_entry_offset: int,
) -> tuple[str, bool]:
    section_id = None
    for i in range(sounds_entries):
        base = table1 + i * 0x0C
        if base + 0x0C > len(data):
            raise SonyBnkError("SBlk sound table exceeds bank")
        entry_count = data[base + 0x04]
        entry_offset = _u32be(data, base + 0x08)
        if entry_offset <= table2_entry_offset < entry_offset + entry_count * 0x08:
            section_id = i
            break
    if section_id is None:
        return "", False

    if table4 <= 0 or table4 + 0x58 > len(data):
        return "", False
    names_base = table4 + _u32be(data, table4 + 0x08)
    chunks = [_u16be(data, table4 + 0x18 + i * 2) for i in range(32)]
    for bucket, first_record in enumerate(chunks):
        offset = names_base + first_record * 0x14
        # Bound the walk so malformed chunk indices cannot spin into arbitrary data.
        for _ in range(sounds_entries + 1):
            if offset + 0x14 > len(data) or data[offset] == 0:
                break
            if ((data[offset] + data[offset + 4] + data[offset + 8] + data[offset + 12]) & 0x1F) != bucket:
                raise SonyBnkError("SBlk v3 name-bucket checksum mismatch")
            if _u16be(data, offset + 0x10) == section_id:
                name = _cstring(data, offset, 0x10)
                return name, bool(name)
            offset += 0x14
    return "", False


def parse_sony_sblk_v3(data: bytes) -> SonySblkBank:
    """Parse the big-endian SBlk v3 subset used by SIIG's PS3 sound bank."""
    if len(data) < 0x60:
        raise SonyBnkError("Sony bank is too small")
    outer_version = _u32be(data, 0x00)
    sections = _u32be(data, 0x04)
    if outer_version != 3:
        raise SonyBnkError(f"unsupported Sony bank outer version {outer_version}; expected 3")
    if sections not in (2, 3):
        raise SonyBnkError(f"unsupported Sony bank section count {sections}")

    sblk = _u32be(data, 0x08)
    sblk_size = _u32be(data, 0x0C)
    data_offset = _u32be(data, 0x10)
    data_size = _u32be(data, 0x14)
    if sblk > 0x20 or sblk + 0x40 > len(data):
        raise SonyBnkError("invalid SBlk offset")
    if data[sblk:sblk + 4] != b"klBS":
        raise SonyBnkError("missing big-endian SBlk marker")
    sblk_version = _u32be(data, sblk + 0x04)
    if sblk_version != 3:
        raise SonyBnkError(f"unsupported SBlk version {sblk_version}; SIIG uses v3")
    if sblk_size and sblk + sblk_size > data_offset:
        # A few banks align after SBlk; overlap is never expected.
        raise SonyBnkError("SBlk section overlaps audio data")
    if data_offset + data_size > len(data):
        raise SonyBnkError("Sony bank audio section exceeds file")

    sounds_entries = _u16be(data, sblk + 0x16)
    grains_entries = _u16be(data, sblk + 0x18)
    stream_entries = _u16be(data, sblk + 0x1A)
    if not (sounds_entries and grains_entries and stream_entries):
        raise SonyBnkError("Sony bank contains no SBlk sound entries")
    if max(sounds_entries, grains_entries, stream_entries) > 100_000:
        raise SonyBnkError("unreasonable SBlk entry count")

    table1 = sblk + _u32be(data, sblk + 0x1C)
    table2 = sblk + _u32be(data, sblk + 0x20)
    table3 = sblk + _u32be(data, sblk + 0x34)
    table4 = sblk + _u32be(data, sblk + 0x38)
    for label, offset in (("sound", table1), ("grain", table2), ("wave", table3), ("name", table4)):
        if offset < sblk or offset >= data_offset:
            raise SonyBnkError(f"SBlk {label} table offset is outside header section")

    streams: list[SonySblkStream] = []
    for grain_index in range(grains_entries):
        grain_offset = table2 + grain_index * 0x08
        if grain_offset + 0x08 > len(data):
            raise SonyBnkError("SBlk grain table exceeds bank")
        value = _u32be(data, grain_offset)
        subtype = (value >> 16) & 0xFFFF
        wave_suboffset = value & 0xFFFF
        if subtype != 0x0100:
            continue
        header = table3 + wave_suboffset
        if header < table3 or header + 0x18 > data_offset:
            raise SonyBnkError("SBlk wave header is outside header section")

        center_note = data[header + 0x02]
        center_fine = data[header + 0x03]
        flags = _u16be(data, header + 0x0E)
        stream_offset = _u32be(data, header + 0x10)
        stream_size = _u32be(data, header + 0x14)
        if stream_offset > data_size or stream_size > data_size - stream_offset:
            raise SonyBnkError("SBlk stream range exceeds audio section")

        if flags & 0x1000:
            codec = "MPEG"
        elif flags & 0x0080:
            codec = "PCM16BE"
        else:
            codec = "PSX_ADPCM"
        if codec == "PSX_ADPCM" and stream_size % 0x10:
            raise SonyBnkError("PSX ADPCM stream size is not 16-byte-frame aligned")

        resolved, name_ok = _resolve_v3_name(data, table1, table4, sounds_entries, grain_index * 0x08)
        name = resolved or f"stream_{len(streams) + 1:03d}.vag"
        channels = 1
        if codec == "PSX_ADPCM":
            num_samples = (stream_size // 0x10) * 28
        elif codec == "PCM16BE":
            num_samples = stream_size // 2
        else:
            num_samples = 0
        streams.append(SonySblkStream(
            index=len(streams),
            name=name,
            name_resolved=name_ok,
            center_note=center_note,
            center_fine=center_fine,
            flags=flags,
            codec=codec,
            sample_rate=_sample_rate_from_center(center_note, center_fine),
            channels=channels,
            header_offset=header,
            stream_offset=stream_offset,
            stream_size=stream_size,
            absolute_offset=data_offset + stream_offset,
            num_samples=num_samples,
            loop_flag=bool(flags & 0x0040),
        ))

    if not streams:
        raise SonyBnkError("SBlk grain table contains no waveform entries")
    if len(streams) != stream_entries:
        raise SonyBnkError(
            f"SBlk waveform count mismatch: parsed {len(streams)}, header says {stream_entries}"
        )

    ordered = sorted((s.stream_offset, s.stream_offset + s.stream_size) for s in streams)
    covered = 0
    cursor = 0
    complete = True
    for start, end in ordered:
        if start != cursor:
            complete = False
        if start < cursor:
            raise SonyBnkError("overlapping SBlk audio stream ranges")
        covered += end - start
        cursor = end
    complete = complete and cursor == data_size

    return SonySblkBank(
        outer_version=outer_version,
        sections=sections,
        sblk_version=sblk_version,
        sblk_offset=sblk,
        data_offset=data_offset,
        data_size=data_size,
        sounds_entries=sounds_entries,
        grains_entries=grains_entries,
        stream_entries=stream_entries,
        streams=tuple(streams),
        covered_audio_bytes=covered,
        coverage_complete=complete,
    )


_PSX_COEFS = ((0, 0), (60, 0), (115, -52), (98, -55), (122, -60))


def decode_psx_adpcm_mono(raw: bytes) -> bytes:
    """Decode standard 16-byte Sony PS-ADPCM frames to little-endian PCM16."""
    if len(raw) % 0x10:
        raise SonyBnkError("PSX ADPCM data is not frame aligned")
    hist1 = 0
    hist2 = 0
    samples = array("h")
    for frame_offset in range(0, len(raw), 0x10):
        frame = raw[frame_offset:frame_offset + 0x10]
        coef_index = (frame[0] >> 4) & 0x0F
        shift_factor = frame[0] & 0x0F
        flag = frame[1]
        if coef_index > 4:
            coef_index = 0
        if shift_factor > 12:
            shift_factor = 9
        coef0, coef1 = _PSX_COEFS[coef_index]
        scale_shift = 20 - shift_factor
        for i in range(28):
            sample = 0
            # 0x07 is an explicit silent/end frame. Unknown high flag values in
            # trailing padding are likewise rendered silent, matching the normal
            # console decoder behavior instead of interpreting garbage nibbles.
            if flag < 0x07:
                packed = frame[0x02 + i // 2]
                nibble = ((packed >> 4) & 0x0F) if (i & 1) else (packed & 0x0F)
                if nibble & 0x08:
                    nibble -= 0x10
                sample = nibble << scale_shift
                # The standard filter coefficients are rational values /64;
                # multiplying by 256 here keeps the whole predictor path exact.
                sample += (coef0 * hist1 + coef1 * hist2) * 4
                sample >>= 8
            clipped = max(-32768, min(32767, sample))
            samples.append(clipped)
            hist2, hist1 = hist1, sample
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()


def encode_psx_adpcm_mono(pcm_le: bytes, frame_flags: tuple[int, ...] | list[int] | None = None) -> bytes:
    """Encode little-endian PCM16 mono into standard 16-byte Sony PS-ADPCM frames.

    The encoder is intentionally conservative for template-preserving bank edits:
    callers may supply the original frame-control bytes so loop/end markers stay
    byte-for-byte in their original frame positions.  Frames with control values
    >= 0x07 decode as silence in the supported SIIG path, so non-zero replacement
    samples in such a frame are rejected instead of being silently discarded.
    """
    if len(pcm_le) % (28 * 2):
        raise SonyBnkError("PCM16 replacement length must be an exact multiple of 28 mono samples")
    sample_count = len(pcm_le) // 2
    frame_count = sample_count // 28
    if frame_flags is None:
        flags = [0] * frame_count
    else:
        flags = [int(value) & 0xFF for value in frame_flags]
        if len(flags) != frame_count:
            raise SonyBnkError("PSX ADPCM frame-control count does not match PCM frame count")
    samples = struct.unpack(f"<{sample_count}h", pcm_le) if sample_count else ()
    output = bytearray()
    hist1 = 0
    hist2 = 0

    for frame_index in range(frame_count):
        target = samples[frame_index * 28:(frame_index + 1) * 28]
        control = flags[frame_index]
        if control >= 0x07:
            if any(target):
                raise SonyBnkError(
                    f"replacement frame {frame_index} contains audio but template control 0x{control:02X} renders it silent"
                )
            output.extend(bytes((0x00, control)) + (b"\x00" * 14))
            hist1 = 0
            hist2 = 0
            continue

        # Select the predictor whose source-domain residual has the smallest
        # peak (then energy).  This is a clean-room search over the five
        # standard decoder coefficient pairs already used by the reader.
        best_filter = 0
        best_key: tuple[int, int, int] | None = None
        for filter_index, (coef0, coef1) in enumerate(_PSX_COEFS):
            source_hist1 = hist1
            source_hist2 = hist2
            peak = 0
            energy = 0
            for wanted in target:
                predicted = ((coef0 * source_hist1 + coef1 * source_hist2) * 4) >> 8
                residual = int(wanted) - predicted
                peak = max(peak, abs(residual))
                energy += residual * residual
                source_hist2, source_hist1 = source_hist1, int(wanted)
            key = (peak, energy, filter_index)
            if best_key is None or key < best_key:
                best_key = key
                best_filter = filter_index

        assert best_key is not None
        peak = best_key[0]
        shift_factor = 12
        quant_step = 1
        # Signed nibbles hold -8..+7.  Use +7 as the conservative symmetric
        # bound and choose the finest step that fits the frame residual peak.
        while shift_factor > 0 and peak > 7 * quant_step:
            shift_factor -= 1
            quant_step <<= 1

        coef0, coef1 = _PSX_COEFS[best_filter]
        nibbles: list[int] = []
        for wanted in target:
            predicted = ((coef0 * hist1 + coef1 * hist2) * 4) >> 8
            residual = int(wanted) - predicted
            if residual >= 0:
                quantized = (residual + quant_step // 2) // quant_step
            else:
                quantized = -((-residual + quant_step // 2) // quant_step)
            quantized = max(-8, min(7, quantized))
            reconstructed = predicted + quantized * quant_step
            nibbles.append(quantized & 0x0F)
            hist2, hist1 = hist1, reconstructed

        packed = bytearray(14)
        for index in range(14):
            packed[index] = nibbles[index * 2] | (nibbles[index * 2 + 1] << 4)
        output.extend(bytes(((best_filter << 4) | shift_factor, control)) + packed)

    return bytes(output)


@lru_cache(maxsize=512)
def _center_from_sample_rate(sample_rate: int) -> tuple[int, int, int]:
    """Return the closest PS2 SCREAM center-note/fine pair for a target rate.

    SIIG's SBlk v3 wave headers do not store a literal Hz value.  They store the
    same center-note/fine pitch pair consumed by the PS2-style SCREAM runtime.
    Searching the finite high-bit/PS2 representation is cheap, deterministic,
    and avoids baking in an approximate inverse of the integer pitch path.
    """
    target = int(sample_rate)
    if target <= 0:
        raise SonyBnkError("replacement sample rate must be positive")
    best: tuple[int, int, int, int] | None = None
    for center_note in range(0x80, 0x100):
        for center_fine in range(0x80):
            actual = _sample_rate_from_center(center_note, center_fine)
            key = (abs(actual - target), abs(center_fine), center_note, actual)
            if best is None or key < best:
                best = key
    assert best is not None
    _error, center_fine_abs, center_note, actual = best
    # center_fine_abs is the actual fine value because the search domain is >=0.
    return center_note, center_fine_abs, actual


def _downmix_pcm16_le_to_mono(pcm_le: bytes, channels: int) -> tuple[bytes, int]:
    """Downmix interleaved PCM16 to mono with a simple equal-weight average."""
    channels = int(channels)
    if not (1 <= channels <= 64):
        raise SonyBnkError(f"unsupported replacement channel count {channels}")
    frame_bytes = channels * 2
    if len(pcm_le) % frame_bytes:
        raise SonyBnkError("replacement PCM16 payload is not frame aligned")
    frames = len(pcm_le) // frame_bytes
    if channels == 1:
        return bytes(pcm_le), frames
    samples = array("h")
    samples.frombytes(pcm_le)
    if sys.byteorder != "little":
        samples.byteswap()
    mono = array("h")
    for frame in range(frames):
        start = frame * channels
        total = sum(int(samples[start + ch]) for ch in range(channels))
        # Truncate toward zero so positive/negative mixes are symmetric.
        mixed = int(total / channels)
        mono.append(max(-32768, min(32767, mixed)))
    if sys.byteorder != "little":
        mono.byteswap()
    return mono.tobytes(), frames


def _sblk_replacement_frame_flags(original_raw: bytes, audio_frames: int, loop_flag: bool) -> list[int]:
    """Generate SIIG-compatible PS-ADPCM control bytes for a resized stream.

    Retail one-shots conventionally end with an audio frame flagged 0x01 and a
    silent 0x07 pad frame.  Retail looping SIIG streams use 0x06 at loop start,
    0x02 through the loop body, 0x03 at loop end and a final 0xFF pad frame.
    When duration changes, preserve the original loop-start *fraction* of the
    playable stream instead of pinning it to a stale absolute frame index.
    """
    if audio_frames <= 0:
        audio_frames = 1
    old_flags = [original_raw[offset + 1] for offset in range(0, len(original_raw), 0x10)]
    old_playable = len(old_flags)
    while old_playable and old_flags[old_playable - 1] >= 0x07:
        old_playable -= 1
    old_playable = max(1, old_playable)

    if not loop_flag:
        flags = [0] * audio_frames
        flags[-1] = 0x01
        return flags + [0x07]

    # A looping stream needs distinct start/end blocks.  Extend very tiny input
    # with one silent audio block rather than producing an impossible 0x07 block
    # that would both carry audio and act as loop start+end.
    audio_frames = max(2, audio_frames)
    old_start = next((i for i, flag in enumerate(old_flags[:old_playable]) if flag & 0x04), 0)
    if old_playable <= 1:
        new_start = 0
    else:
        new_start = round(old_start * (audio_frames - 1) / (old_playable - 1))
    new_start = max(0, min(audio_frames - 2, new_start))
    flags = [0] * audio_frames
    for i in range(new_start + 1, audio_frames - 1):
        flags[i] = 0x02
    flags[new_start] = 0x06
    flags[-1] = 0x03
    return flags + [0xFF]


def _select_sblk_stream(bank: SonySblkBank, selector: str | int) -> SonySblkStream:
    token = str(selector).strip()
    if token.isdigit():
        index = int(token) - 1
        if 0 <= index < len(bank.streams):
            return bank.streams[index]
        raise SonyBnkError(f"SBlk stream index {token} is outside 1..{len(bank.streams)}")
    folded = token.casefold()
    matches = [
        stream for stream in bank.streams
        if stream.name.casefold() == folded or Path(stream.name).stem.casefold() == folded
    ]
    if not matches:
        raise SonyBnkError(f"SBlk stream {token!r} was not found; use a 1-based index or exact stream name")
    if len(matches) != 1:
        raise SonyBnkError(f"SBlk stream selector {token!r} is ambiguous")
    return matches[0]


def replace_sony_sblk_stream_pcm16(
    data: bytes,
    selector: str | int,
    pcm_le: bytes,
    sample_rate: int,
) -> tuple[bytes, dict]:
    """Replace one SIIG PS3 SBlk PS-ADPCM slot without changing bank layout.

    The source bank is the structural template.  Stream offset, byte capacity,
    loop/end frame-control bytes, tables, names, and all bytes outside the target
    payload are preserved.  The replacement therefore must have the same PCM
    sample count/rate as the selected slot; arbitrary bank topology is outside
    this safe path.
    """
    bank = parse_sony_sblk_v3(data)
    stream = _select_sblk_stream(bank, selector)
    if stream.codec != "PSX_ADPCM":
        raise SonyBnkError(f"stream {stream.index + 1} uses unsupported replacement codec {stream.codec}")
    if stream.channels != 1:
        raise SonyBnkError("template-preserving SBlk replacement currently requires mono streams")
    if int(sample_rate) != stream.sample_rate:
        raise SonyBnkError(
            f"replacement sample rate {sample_rate} does not match slot rate {stream.sample_rate}; resample first"
        )
    expected_pcm_bytes = stream.num_samples * 2
    if len(pcm_le) != expected_pcm_bytes:
        raise SonyBnkError(
            f"replacement has {len(pcm_le) // 2} PCM sample(s); slot requires exactly {stream.num_samples}"
        )

    original_raw = data[stream.absolute_offset:stream.absolute_offset + stream.stream_size]
    if len(original_raw) != stream.stream_size or stream.stream_size % 0x10:
        raise SonyBnkError("selected PSX ADPCM slot is truncated or not frame aligned")
    frame_flags = tuple(original_raw[offset + 1] for offset in range(0, len(original_raw), 0x10))
    encoded = encode_psx_adpcm_mono(pcm_le, frame_flags)
    if len(encoded) != stream.stream_size:
        raise SonyBnkError("encoded replacement no longer fits the fixed SBlk stream slot")

    rebuilt = bytearray(data)
    rebuilt[stream.absolute_offset:stream.absolute_offset + stream.stream_size] = encoded
    rebuilt_bytes = bytes(rebuilt)
    check_bank = parse_sony_sblk_v3(rebuilt_bytes)
    check_stream = check_bank.streams[stream.index]
    if check_stream != stream or len(rebuilt_bytes) != len(data):
        raise SonyBnkError("template-preserving SBlk replacement changed structural bank metadata")

    decoded = decode_psx_adpcm_mono(encoded)
    wanted = struct.unpack(f"<{stream.num_samples}h", pcm_le)
    got = struct.unpack(f"<{stream.num_samples}h", decoded)
    squared_error = 0
    max_error = 0
    for left, right in zip(wanted, got):
        delta = int(left) - int(right)
        squared_error += delta * delta
        max_error = max(max_error, abs(delta))
    rms_error = math.sqrt(squared_error / stream.num_samples) if stream.num_samples else 0.0

    report = {
        "format": "SIIG_SONY_SBLK_SLOT_REPLACEMENT",
        "stream_index": stream.index + 1,
        "stream_name": stream.name,
        "codec": stream.codec,
        "sample_rate": stream.sample_rate,
        "channels": stream.channels,
        "pcm_samples": stream.num_samples,
        "stream_bytes": stream.stream_size,
        "frame_count": stream.stream_size // 0x10,
        "frame_controls_preserved": True,
        "bank_layout_preserved": True,
        "bank_size_unchanged": True,
        "max_pcm_error": max_error,
        "rms_pcm_error": rms_error,
        "original_stream_sha256": hashlib.sha256(original_raw).hexdigest(),
        "replacement_stream_sha256": hashlib.sha256(encoded).hexdigest(),
        "rebuilt_bank_sha256": hashlib.sha256(rebuilt_bytes).hexdigest(),
        "runtime_validation": "not claimed; structurally validated template-preserving replacement",
    }
    return rebuilt_bytes, report


def replace_sony_sblk_stream_pcm16_flexible(
    data: bytes,
    selector: str | int,
    pcm_le: bytes,
    sample_rate: int,
    channels: int = 1,
) -> tuple[bytes, dict]:
    """Rebuild one SIIG SBlk v3 PS-ADPCM stream from arbitrary PCM16 timing.

    Unlike the original fixed-slot path, this function repacks the complete
    contiguous SBlk audio data section and updates every affected stream offset
    plus the selected stream's size and center-note/fine pitch fields.  SIIG's
    v3 bank stores PS-ADPCM waves as mono voices, so multichannel input is
    accepted and downmixed to mono instead of pretending the format has an
    in-slot channel-count field.
    """
    bank = parse_sony_sblk_v3(data)
    if not bank.coverage_complete:
        raise SonyBnkError(
            "variable-size SBlk rebuilding requires complete contiguous audio coverage"
        )
    stream = _select_sblk_stream(bank, selector)
    if stream.codec != "PSX_ADPCM":
        raise SonyBnkError(f"stream {stream.index + 1} uses unsupported replacement codec {stream.codec}")

    mono_pcm, input_frames = _downmix_pcm16_le_to_mono(pcm_le, channels)
    if input_frames <= 0:
        raise SonyBnkError("replacement WAV contains no PCM frames")
    center_note, center_fine, actual_rate = _center_from_sample_rate(int(sample_rate))

    # PS-ADPCM encodes 28 mono samples per frame.  Pad only the final partial
    # frame, then add the same terminal control/pad frame style used by retail.
    audio_frames = max(1, (input_frames + 27) // 28)
    if stream.loop_flag:
        audio_frames = max(2, audio_frames)
    padded_samples = audio_frames * 28
    padded_pcm = mono_pcm + (b"\x00\x00" * (padded_samples - input_frames))
    original_raw = data[stream.absolute_offset:stream.absolute_offset + stream.stream_size]
    frame_flags = _sblk_replacement_frame_flags(original_raw, audio_frames, stream.loop_flag)
    encoded_pcm = padded_pcm + (b"\x00\x00" * 28)
    encoded = encode_psx_adpcm_mono(encoded_pcm, frame_flags)

    # Repack in original physical order.  Every raw stream remains byte-identical
    # except the selected one; only header offsets after a resized stream move.
    rebuilt_header = bytearray(data[:bank.data_offset])
    ordered = sorted(bank.streams, key=lambda item: item.stream_offset)
    data_blob = bytearray()
    changed_offsets = 0
    original_target_sha = hashlib.sha256(original_raw).hexdigest()
    for item in ordered:
        raw = (
            encoded
            if item.index == stream.index
            else data[item.absolute_offset:item.absolute_offset + item.stream_size]
        )
        new_offset = len(data_blob)
        if new_offset != item.stream_offset:
            changed_offsets += 1
        if item.index == stream.index:
            rebuilt_header[item.header_offset + 0x02] = center_note
            rebuilt_header[item.header_offset + 0x03] = center_fine
        struct.pack_into(
            ">II",
            rebuilt_header,
            item.header_offset + 0x10,
            new_offset,
            len(raw),
        )
        data_blob.extend(raw)

    struct.pack_into(">I", rebuilt_header, 0x14, len(data_blob))
    tail = data[bank.data_offset + bank.data_size:]
    rebuilt_bytes = bytes(rebuilt_header) + bytes(data_blob) + bytes(tail)
    check_bank = parse_sony_sblk_v3(rebuilt_bytes)
    if len(check_bank.streams) != len(bank.streams) or not check_bank.coverage_complete:
        raise SonyBnkError("variable-size SBlk rebuild changed stream topology or lost data coverage")
    check_stream = check_bank.streams[stream.index]
    if check_stream.stream_size != len(encoded):
        raise SonyBnkError("variable-size SBlk rebuild did not preserve the replacement stream size")
    if check_stream.sample_rate != actual_rate:
        raise SonyBnkError("variable-size SBlk rebuild did not preserve the replacement sample rate metadata")
    # Confirm untouched stream payloads survive repacking byte-for-byte.
    for item in bank.streams:
        if item.index == stream.index:
            continue
        old_raw = data[item.absolute_offset:item.absolute_offset + item.stream_size]
        new_item = check_bank.streams[item.index]
        new_raw = rebuilt_bytes[new_item.absolute_offset:new_item.absolute_offset + new_item.stream_size]
        if old_raw != new_raw:
            raise SonyBnkError(f"variable-size SBlk rebuild altered untouched stream {item.index + 1}")

    decoded = decode_psx_adpcm_mono(encoded)
    report = {
        "format": "SIIG_SONY_SBLK_VARIABLE_REPLACEMENT",
        "stream_index": stream.index + 1,
        "stream_name": stream.name,
        "codec": stream.codec,
        "input_sample_rate": int(sample_rate),
        "native_sample_rate": actual_rate,
        "sample_rate_error_hz": actual_rate - int(sample_rate),
        "input_channels": int(channels),
        "native_channels": 1,
        "channel_policy": "equal-weight PCM16 downmix to mono" if int(channels) != 1 else "mono passthrough",
        "input_pcm_frames": input_frames,
        "encoded_pcm_frames": len(encoded) // 0x10 * 28,
        "audio_frames_before_terminal_pad": audio_frames,
        "terminal_control_frame_added": True,
        "loop_flag_preserved": stream.loop_flag,
        "loop_control_policy": "proportional loop-start remap" if stream.loop_flag else "retail one-shot end/pad controls",
        "original_stream_bytes": stream.stream_size,
        "replacement_stream_bytes": len(encoded),
        "bank_audio_bytes_before": bank.data_size,
        "bank_audio_bytes_after": len(data_blob),
        "bank_size_before": len(data),
        "bank_size_after": len(rebuilt_bytes),
        "stream_offsets_changed": changed_offsets,
        "original_stream_sha256": original_target_sha,
        "replacement_stream_sha256": hashlib.sha256(encoded).hexdigest(),
        "decoded_replacement_sha256": hashlib.sha256(decoded).hexdigest(),
        "rebuilt_bank_sha256": hashlib.sha256(rebuilt_bytes).hexdigest(),
        "runtime_validation": "structurally validated variable-size SBlk v3 rebuild; retail-runtime acceptance pending project-owner test",
    }
    return rebuilt_bytes, report


def replace_sony_sblk_wav_file(
    input_path: Path,
    selector: str | int,
    wav_path: Path,
    output_path: Path,
) -> dict:
    """Replace one SBlk PS-ADPCM stream from an arbitrary-size/rate PCM16 WAV."""
    try:
        with wave.open(str(wav_path), "rb") as wav:
            if wav.getsampwidth() != 2:
                raise SonyBnkError("replacement WAV must be PCM16")
            if wav.getcomptype() != "NONE":
                raise SonyBnkError("replacement WAV must be uncompressed PCM")
            channels = wav.getnchannels()
            sample_rate = wav.getframerate()
            frame_count = wav.getnframes()
            pcm = wav.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise SonyBnkError(f"invalid replacement WAV: {exc}") from exc

    rebuilt, report = replace_sony_sblk_stream_pcm16_flexible(
        input_path.read_bytes(), selector, pcm, sample_rate, channels
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(rebuilt)
    report.update({
        "source_bank": input_path.name,
        "replacement_wav": wav_path.name,
        "output_bank": output_path.name,
    })
    return report


def decode_sblk_stream(data: bytes, stream: SonySblkStream) -> bytes:
    raw = data[stream.absolute_offset:stream.absolute_offset + stream.stream_size]
    if len(raw) != stream.stream_size:
        raise SonyBnkError("truncated SBlk stream")
    if stream.codec == "PSX_ADPCM":
        return decode_psx_adpcm_mono(raw)
    if stream.codec == "PCM16BE":
        samples = array("h")
        samples.frombytes(raw)
        # Input bytes are big-endian while WAV PCM16 is little-endian.
        # array.frombytes interprets native endian, so one byte swap is needed
        # on either host endian before serialising the WAV payload.
        samples.byteswap()
        return samples.tobytes()
    raise SonyBnkError(f"built-in Sony bank decoder does not support {stream.codec}")


def export_sony_sblk_wav_bytes(data: bytes, output_dir: Path, source_label: str = "sound.bnk") -> dict:
    """Export every supported SBlk v3 stream to PCM16 WAV plus CSV/JSON manifests."""
    bank = parse_sony_sblk_v3(data)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    used_names: set[str] = set()
    decode_failures = 0

    for stream in bank.streams:
        base = Path(stream.name).stem
        stem = _safe_name(base)
        key = stem.casefold()
        if key in used_names:
            stem = f"{stream.index + 1:03d}_{stem}"
            key = stem.casefold()
        used_names.add(key)
        wav_name = stem + ".wav"
        wav_path = output_dir / wav_name
        error = ""
        decoded = False
        pcm = b""
        try:
            pcm = decode_sblk_stream(data, stream)
            with wave.open(str(wav_path), "wb") as wav:
                wav.setnchannels(stream.channels)
                wav.setsampwidth(2)
                wav.setframerate(stream.sample_rate)
                wav.writeframes(pcm)
            decoded = True
        except Exception as exc:
            decode_failures += 1
            error = str(exc)
            wav_path.unlink(missing_ok=True)

        row = asdict(stream)
        row.update({
            "flags_hex": f"0x{stream.flags:04X}",
            "wav_file": wav_name if decoded else "",
            "decoded": decoded,
            "pcm_sha256": hashlib.sha256(pcm).hexdigest() if decoded else "",
            "error": error,
        })
        rows.append(row)

    manifest = {
        "source": Path(source_label).name,
        "format": "Sony 989SND/SCREAM SBlk v3",
        "outer_version": bank.outer_version,
        "sblk_version": bank.sblk_version,
        "stream_count": len(bank.streams),
        "decoded_wav": len(bank.streams) - decode_failures,
        "decode_failures": decode_failures,
        "audio_data_size": bank.data_size,
        "covered_audio_bytes": bank.covered_audio_bytes,
        "coverage_complete": bank.coverage_complete,
        "entries": rows,
    }
    (output_dir / "sblk_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if rows:
        csv_rows = []
        for row in rows:
            flat = dict(row)
            # bools/ints are already CSV-friendly; keep stable scalar columns.
            csv_rows.append(flat)
        with (output_dir / "sblk_manifest.csv").open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)
    return manifest


def export_sony_sblk_wav_file(input_path: Path, output_dir: Path) -> dict:
    return export_sony_sblk_wav_bytes(input_path.read_bytes(), output_dir, input_path.name)
