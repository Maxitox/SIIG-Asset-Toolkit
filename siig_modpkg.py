"""Shareable SIIG mod-package delta helpers.

The package format intentionally stores only binary deltas plus metadata. Original
resource/BBX bytes are addressed by SHA-256 and reconstructed from the user's own
verified rip when a package is applied.
"""
from __future__ import annotations

import difflib
import hashlib
import io
import json
import stat
import zipfile
from pathlib import Path
from typing import Mapping

PATCH_FORMAT = "SIIG_BINARY_PATCH_V1"
PACKAGE_FORMAT = "SIIG_MOD_PACKAGE_V1"
MAX_SEQUENCE_DIFF_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_FILES = 10000
MAX_PACKAGE_UNCOMPRESSED = 256 * 1024 * 1024
MAX_PACKAGE_MEMBER = 64 * 1024 * 1024


class ModPackageError(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def create_binary_patch(source: bytes, target: bytes, *, max_sequence_bytes: int = MAX_SEQUENCE_DIFF_BYTES) -> tuple[dict, bytes]:
    """Create a baseline-dependent patch without embedding unchanged source bytes.

    Equal-sized files use sparse replacement runs and scale to very large assets.
    Unequal-sized files use an exact SequenceMatcher copy/data stream, bounded to
    modest resources so package creation cannot accidentally become quadratic on
    giant archives. Large length-changing edits should be staged at a smaller
    resource boundary rather than as a whole-archive override.
    """
    source = bytes(source)
    target = bytes(target)
    common = {
        "format": PATCH_FORMAT,
        "source_size": len(source),
        "target_size": len(target),
        "source_sha256": _sha(source),
        "target_sha256": _sha(target),
    }
    if source == target:
        patch = {**common, "mode": "identity", "payload_size": 0, "payload_sha256": _sha(b""), "segments": []}
        return patch, b""

    payload = bytearray()
    if len(source) == len(target):
        segments: list[dict] = []
        i = 0
        size = len(source)
        while i < size:
            if source[i] == target[i]:
                i += 1
                continue
            start = i
            i += 1
            while i < size and source[i] != target[i]:
                i += 1
            chunk = target[start:i]
            data_offset = len(payload)
            payload.extend(chunk)
            segments.append({"offset": start, "length": len(chunk), "data_offset": data_offset})
        patch = {
            **common,
            "mode": "sparse_equal",
            "segments": segments,
            "payload_size": len(payload),
            "payload_sha256": _sha(payload),
        }
        return patch, bytes(payload)

    if max(len(source), len(target)) > int(max_sequence_bytes):
        raise ModPackageError(
            "length-changing binary delta exceeds safe SequenceMatcher limit; "
            "stage the changed inner resource instead of a large whole-archive override"
        )

    matcher = difflib.SequenceMatcher(None, source, target, autojunk=False)
    ops: list[dict] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            if i2 > i1:
                ops.append({"op": "copy", "source_offset": i1, "length": i2 - i1})
        elif tag in ("replace", "insert"):
            if j2 > j1:
                data_offset = len(payload)
                chunk = target[j1:j2]
                payload.extend(chunk)
                ops.append({"op": "data", "data_offset": data_offset, "length": len(chunk)})
        elif tag == "delete":
            continue
        else:  # pragma: no cover - defensive
            raise ModPackageError(f"unsupported diff opcode: {tag}")
    patch = {
        **common,
        "mode": "copy_data",
        "ops": ops,
        "payload_size": len(payload),
        "payload_sha256": _sha(payload),
    }
    return patch, bytes(payload)


def apply_binary_patch(source: bytes, patch: Mapping, payload: bytes) -> bytes:
    source = bytes(source)
    payload = bytes(payload)
    if patch.get("format") != PATCH_FORMAT:
        raise ModPackageError("unsupported SIIG binary patch format")
    if len(source) != int(patch.get("source_size", -1)) or _sha(source) != str(patch.get("source_sha256", "")):
        raise ModPackageError("binary patch source does not match the required baseline")
    if len(payload) != int(patch.get("payload_size", -1)) or _sha(payload) != str(patch.get("payload_sha256", "")):
        raise ModPackageError("binary patch payload is corrupt or incomplete")

    mode = patch.get("mode")
    if mode == "identity":
        result = source
    elif mode == "sparse_equal":
        out = bytearray(source)
        last_end = -1
        for segment in patch.get("segments", []):
            offset = int(segment["offset"])
            length = int(segment["length"])
            data_offset = int(segment["data_offset"])
            if offset < 0 or length < 0 or data_offset < 0 or offset + length > len(out) or data_offset + length > len(payload):
                raise ModPackageError("binary patch segment is out of bounds")
            if offset < last_end:
                raise ModPackageError("binary patch segments overlap or are unsorted")
            out[offset:offset + length] = payload[data_offset:data_offset + length]
            last_end = offset + length
        result = bytes(out)
    elif mode == "copy_data":
        out = bytearray()
        for op in patch.get("ops", []):
            kind = op.get("op")
            length = int(op.get("length", -1))
            if length < 0:
                raise ModPackageError("binary patch operation has invalid length")
            if kind == "copy":
                offset = int(op.get("source_offset", -1))
                if offset < 0 or offset + length > len(source):
                    raise ModPackageError("binary patch copy is out of bounds")
                out.extend(source[offset:offset + length])
            elif kind == "data":
                offset = int(op.get("data_offset", -1))
                if offset < 0 or offset + length > len(payload):
                    raise ModPackageError("binary patch data is out of bounds")
                out.extend(payload[offset:offset + length])
            else:
                raise ModPackageError(f"unknown binary patch operation: {kind!r}")
        result = bytes(out)
    else:
        raise ModPackageError(f"unknown binary patch mode: {mode!r}")

    if len(result) != int(patch.get("target_size", -1)) or _sha(result) != str(patch.get("target_sha256", "")):
        raise ModPackageError("binary patch output failed target verification")
    return result


def deterministic_zip_bytes(files: Mapping[str, bytes]) -> bytes:
    """Build a deterministic source-style ZIP from a mapping of safe relative names."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(files):
            normalized = str(name).replace("\\", "/").strip("/")
            path = Path(normalized)
            if not normalized or path.is_absolute() or ".." in path.parts:
                raise ModPackageError(f"unsafe package member path: {name!r}")
            info = zipfile.ZipInfo(normalized, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, bytes(files[name]))
    return buffer.getvalue()


def read_mod_package(path: Path) -> tuple[dict, dict[str, bytes]]:
    """Read and validate a SIIG mod package without extracting it to disk."""
    package_path = Path(path)
    try:
        archive = zipfile.ZipFile(package_path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise ModPackageError(f"could not open mod package: {exc}") from exc
    members: dict[str, bytes] = {}
    seen: set[str] = set()
    total = 0
    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_PACKAGE_FILES:
            raise ModPackageError("mod package has too many members")
        for info in infos:
            name = info.filename.replace("\\", "/")
            member = Path(name)
            if info.is_dir():
                continue
            if member.is_absolute() or not member.parts or ".." in member.parts:
                raise ModPackageError(f"unsafe mod package member: {info.filename}")
            key = member.as_posix().casefold()
            if key in seen:
                raise ModPackageError(f"duplicate/colliding mod package member: {info.filename}")
            seen.add(key)
            if info.file_size > MAX_PACKAGE_MEMBER:
                raise ModPackageError(f"mod package member exceeds size limit: {info.filename}")
            total += info.file_size
            if total > MAX_PACKAGE_UNCOMPRESSED:
                raise ModPackageError("mod package exceeds uncompressed size limit")
            members[member.as_posix()] = archive.read(info)
    raw_manifest = members.get("manifest.json")
    if raw_manifest is None:
        raise ModPackageError("mod package is missing manifest.json")
    try:
        manifest = json.loads(raw_manifest.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModPackageError(f"invalid mod package manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("format") != PACKAGE_FORMAT:
        raise ModPackageError("unsupported SIIG mod package manifest")
    return manifest, members
