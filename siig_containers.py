#!/usr/bin/env python3
"""Dependency-free Xbox 360 STFS and PlayStation 3 PKG extraction helpers.

This module only removes the outer package layer. It does not decrypt PS3 SELF,
EDAT, or SDAT payloads found inside a PKG.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Callable, Iterable, Optional


class ContainerError(Exception):
    """Raised when an outer game container is malformed or unsupported."""


STFS_MAGICS = {b"CON ", b"LIVE", b"PIRS"}
PKG_MAGIC = b"\x7fPKG"
ZIP_MAGICS = {b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"}
BLOCK_SIZE = 0x1000


@dataclass(frozen=True)
class ExtractionLimits:
    """Resource limits for untrusted outer-container extraction."""

    max_files: int = 200_000
    max_total_bytes: int = 16 * 1024 * 1024 * 1024
    max_file_bytes: int = 4 * 1024 * 1024 * 1024

    def validate(self) -> "ExtractionLimits":
        if self.max_files < 1:
            raise ContainerError("max_files must be at least 1")
        if self.max_total_bytes < 1:
            raise ContainerError("max_total_bytes must be at least 1")
        if self.max_file_bytes < 1:
            raise ContainerError("max_file_bytes must be at least 1")
        if self.max_file_bytes > self.max_total_bytes:
            raise ContainerError("max_file_bytes cannot exceed max_total_bytes")
        return self


DEFAULT_EXTRACTION_LIMITS = ExtractionLimits()


def _validate_extraction_plan(
    members: Iterable[tuple[str, int]],
    limits: ExtractionLimits,
) -> tuple[int, int]:
    limits = limits.validate()
    count = 0
    total = 0
    for name, size in members:
        if size < 0:
            raise ContainerError(f"negative member size for {name}")
        count += 1
        if count > limits.max_files:
            raise ContainerError(
                f"container exceeds file-count limit ({count} > {limits.max_files})"
            )
        if size > limits.max_file_bytes:
            raise ContainerError(
                f"container member {name} exceeds per-file limit "
                f"({size} > {limits.max_file_bytes} bytes)"
            )
        total += size
        if total > limits.max_total_bytes:
            raise ContainerError(
                f"container exceeds total extraction limit "
                f"({total} > {limits.max_total_bytes} bytes)"
            )
    return count, total


def _atomic_replace(temp: Path, target: Path) -> None:
    try:
        os.replace(temp, target)
    except Exception:
        try:
            temp.unlink(missing_ok=True)
        finally:
            raise


def detect_container_kind(path: Path) -> Optional[str]:
    """Return directory, zip, stfs, ps3_pkg, or None from content rather than suffix."""
    path = Path(path)
    if path.is_dir():
        return "directory"
    if not path.is_file():
        return None
    with path.open("rb") as handle:
        magic = handle.read(4)
    if magic in ZIP_MAGICS:
        return "zip"
    if magic in STFS_MAGICS:
        return "stfs"
    if magic == PKG_MAGIC:
        return "ps3_pkg"
    return None


def _safe_relative_path(raw_name: str) -> Path:
    name = raw_name.replace("\\", "/").replace("\x00", "")
    posix = PurePosixPath(name)
    if posix.is_absolute() or any(part in ("", ".", "..") for part in posix.parts):
        raise ContainerError(f"unsafe package path: {raw_name!r}")
    # Device/reserved punctuation is not expected in SIIG, but replacing it makes
    # extraction portable to Windows without changing directory separators.
    safe_parts = []
    for part in posix.parts:
        cleaned = "".join("_" if ch in '<>:"|?*' else ch for ch in part).rstrip(" .")
        if not cleaned:
            raise ContainerError(f"unsafe empty package path component: {raw_name!r}")
        safe_parts.append(cleaned)
    return Path(*safe_parts)


def _target_for(destination: Path, relative: Path) -> Path:
    root = destination.resolve()
    target = (destination / relative).resolve()
    if target != root and root not in target.parents:
        raise ContainerError(f"package member escapes output: {relative.as_posix()}")
    return target


def _u24_le(data: bytes) -> int:
    if len(data) != 3:
        raise ValueError("u24 requires three bytes")
    return data[0] | (data[1] << 8) | (data[2] << 16)


def _u24_be(data: bytes) -> int:
    if len(data) != 3:
        raise ValueError("u24 requires three bytes")
    return (data[0] << 16) | (data[1] << 8) | data[2]


def _read_exact(handle: BinaryIO, offset: int, size: int, file_size: int) -> bytes:
    if offset < 0 or size < 0 or offset + size > file_size:
        raise ContainerError(f"read outside package at 0x{offset:X} (+0x{size:X})")
    handle.seek(offset)
    data = handle.read(size)
    if len(data) != size:
        raise ContainerError(f"short package read at 0x{offset:X}")
    return data


@dataclass
class _StfsEntry:
    index: int
    name: str
    flags: int
    block_count: int
    start_block: int
    parent_index: int
    file_size: int

    @property
    def is_directory(self) -> bool:
        return bool(self.flags & 0x02)

    @property
    def is_consecutive(self) -> bool:
        return bool(self.flags & 0x01)


class _StfsReader:
    def __init__(self, package_path: Path):
        self.path = Path(package_path)
        self.file_size = self.path.stat().st_size
        self.handle = self.path.open("rb")
        try:
            self.magic = _read_exact(self.handle, 0, 4, self.file_size)
            if self.magic not in STFS_MAGICS:
                raise ContainerError("not an STFS CON/LIVE/PIRS package")
            if self.file_size < 0x3AA:
                raise ContainerError("truncated STFS header")
            self.header_size = struct.unpack(">I", _read_exact(self.handle, 0x340, 4, self.file_size))[0]
            if self.header_size < 0x344 or self.header_size > self.file_size:
                raise ContainerError(f"invalid STFS header size 0x{self.header_size:X}")
            self.file_system = struct.unpack(">I", _read_exact(self.handle, 0x3A9, 4, self.file_size))[0]
            if self.file_system != 0:
                raise ContainerError("SVOD/Game-on-Demand filesystem is not STFS and is not supported")
            volume = _read_exact(self.handle, 0x379, 0x24, self.file_size)
            if volume[0] != 0x24:
                raise ContainerError(f"unexpected STFS volume descriptor size 0x{volume[0]:02X}")
            self.block_separation = volume[2]
            self.first_hash_table_address = (self.header_size + 0xFFF) & ~0xFFF
            # LIVE/PIRS packages have one hash-table copy. CON packages can use
            # paired transactional tables; their layout is also implied by a
            # 0xB000 first hash-table address in older packages.  Compute the
            # first table address before consulting it (v2.5.1 did this in the
            # opposite order, which broke CON initialization).
            if self.magic == b"CON ":
                self.package_sex = 1 if self.first_hash_table_address == 0xB000 else ((~self.block_separation) & 1)
            else:
                self.package_sex = 0
            self.file_table_block_count = struct.unpack_from("<H", volume, 3)[0]
            self.file_table_start_block = _u24_le(volume[5:8])
            self.allocated_blocks = struct.unpack_from(">I", volume, 0x1C)[0]
            self.unallocated_blocks = struct.unpack_from(">I", volume, 0x20)[0]
            if not self.file_table_block_count:
                raise ContainerError("STFS package has no file-table blocks")
            if not self.allocated_blocks:
                raise ContainerError("STFS package reports zero allocated blocks")
            if self.file_table_start_block >= self.allocated_blocks:
                raise ContainerError("STFS file-table start block is outside allocation")
            self.block_step0 = 0xAB if self.package_sex == 0 else 0xAC
            self.block_step1 = 0x718F if self.package_sex == 0 else 0x723A
            if self.allocated_blocks <= 0xAA:
                self.top_level = 0
            elif self.allocated_blocks <= 0x70E4:
                self.top_level = 1
            else:
                self.top_level = 2
        except Exception:
            self.handle.close()
            raise

    def close(self) -> None:
        self.handle.close()

    def __enter__(self) -> "_StfsReader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _read(self, offset: int, size: int) -> bytes:
        return _read_exact(self.handle, offset, size, self.file_size)

    def _backing_data_block_number(self, block_num: int) -> int:
        if block_num < 0 or block_num >= self.allocated_blocks:
            raise ContainerError(f"STFS block {block_num} outside allocation")
        sex = self.package_sex
        result = block_num + (((block_num + 0xAA) // 0xAA) << sex)
        if block_num < 0xAA:
            return result
        result += ((block_num + 0x70E4) // 0x70E4) << sex
        if block_num >= 0x70E4:
            result += 1 << sex
        return result

    def block_address(self, block_num: int) -> int:
        address = self.first_hash_table_address + self._backing_data_block_number(block_num) * BLOCK_SIZE
        if address + BLOCK_SIZE > self.file_size:
            raise ContainerError(f"STFS block {block_num} maps outside package")
        return address

    def read_block(self, block_num: int) -> bytes:
        return self._read(self.block_address(block_num), BLOCK_SIZE)

    def _level0_hash_block(self, block_num: int) -> int:
        group = block_num // 0xAA
        result = group * self.block_step0
        if group == 0:
            return result
        level1_group = block_num // 0x70E4
        result += (level1_group + 1) << self.package_sex
        if level1_group:
            result += 1 << self.package_sex
        return result

    def _level1_hash_block(self, block_num: int) -> int:
        group = block_num // 0x70E4
        if group == 0:
            return self.block_step0
        return group * self.block_step1 + (1 << self.package_sex)

    def _level2_hash_block(self) -> int:
        return self.block_step1

    def _hash_table_address(self, backing_block: int, copy_offset: int = 0) -> int:
        address = self.first_hash_table_address + backing_block * BLOCK_SIZE + copy_offset
        if address + BLOCK_SIZE > self.file_size:
            raise ContainerError("STFS hash table maps outside package")
        return address

    def _hash_status(self, table_address: int, index: int) -> int:
        if index < 0 or index >= 0xAA:
            raise ContainerError(f"invalid STFS hash index {index}")
        return self._read(table_address + index * 0x18 + 0x14, 1)[0]

    def _level0_table_address(self, block_num: int) -> int:
        base = self._level0_hash_block(block_num)
        if self.top_level == 0:
            copy_offset = (self.block_separation & 2) << 11
            return self._hash_table_address(base, copy_offset)
        if self.top_level == 1:
            top_copy = (self.block_separation & 2) << 11
            level1 = self._hash_table_address(self._level1_hash_block(block_num), top_copy)
            status = self._hash_status(level1, (block_num // 0xAA) % 0xAA)
            return self._hash_table_address(base, (status & 0x40) << 6)
        top_copy = (self.block_separation & 2) << 11
        level2 = self._hash_table_address(self._level2_hash_block(), top_copy)
        level2_status = self._hash_status(level2, block_num // 0x70E4)
        level1 = self._hash_table_address(self._level1_hash_block(block_num), (level2_status & 0x40) << 6)
        level1_status = self._hash_status(level1, (block_num % 0x70E4) // 0xAA)
        return self._hash_table_address(base, (level1_status & 0x40) << 6)

    def next_block(self, block_num: int) -> int:
        table = self._level0_table_address(block_num)
        entry = self._read(table + (block_num % 0xAA) * 0x18, 0x18)
        return _u24_be(entry[0x15:0x18])

    def _file_table_blocks(self) -> list[int]:
        blocks: list[int] = []
        current = self.file_table_start_block
        seen: set[int] = set()
        for ordinal in range(self.file_table_block_count):
            if current in seen:
                raise ContainerError("cycle in STFS file-table block chain")
            if current >= self.allocated_blocks:
                raise ContainerError("STFS file-table chain leaves allocation")
            seen.add(current)
            blocks.append(current)
            if ordinal + 1 == self.file_table_block_count:
                break
            try:
                next_block = self.next_block(current)
            except ContainerError:
                next_block = 0xFFFFFF
            if next_block == 0xFFFFFF or next_block >= self.allocated_blocks:
                # Read-only marketplace packages commonly allocate the table in
                # logical sequence; this also keeps damaged hash metadata from
                # making otherwise recoverable packages unusable.
                next_block = current + 1
            current = next_block
        return blocks

    def entries(self) -> list[_StfsEntry]:
        result: list[_StfsEntry] = []
        for table_ordinal, block_num in enumerate(self._file_table_blocks()):
            block = self.read_block(block_num)
            for slot in range(0x40):
                offset = slot * 0x40
                record = block[offset:offset + 0x40]
                name_flags = record[0x28]
                name_length = name_flags & 0x3F
                if not name_length:
                    continue
                if name_length > 0x28:
                    raise ContainerError("invalid STFS filename length")
                raw_name = record[:name_length]
                try:
                    name = raw_name.decode("utf-8")
                except UnicodeDecodeError:
                    name = raw_name.decode("latin-1")
                name = name.rstrip("\x00")
                if not name or "/" in name or "\\" in name:
                    raise ContainerError(f"invalid STFS filename {name!r}")
                result.append(_StfsEntry(
                    index=table_ordinal * 0x40 + slot,
                    name=name,
                    flags=name_flags >> 6,
                    block_count=_u24_le(record[0x29:0x2C]),
                    start_block=_u24_le(record[0x2F:0x32]),
                    parent_index=struct.unpack_from(">H", record, 0x32)[0],
                    file_size=struct.unpack_from(">I", record, 0x34)[0],
                ))
        return result

    def _entry_relative_path(self, entry: _StfsEntry, by_index: dict[int, _StfsEntry]) -> Path:
        parts = [entry.name]
        parent = entry.parent_index
        seen = {entry.index}
        while parent != 0xFFFF:
            if parent in seen:
                raise ContainerError("cycle in STFS directory tree")
            seen.add(parent)
            parent_entry = by_index.get(parent)
            if parent_entry is None:
                raise ContainerError(f"missing STFS parent entry {parent}")
            if not parent_entry.is_directory:
                raise ContainerError(f"STFS parent entry {parent} is not a directory")
            parts.append(parent_entry.name)
            parent = parent_entry.parent_index
        parts.reverse()
        return _safe_relative_path("/".join(parts))

    def extract(
        self,
        destination: Path,
        limits: ExtractionLimits = DEFAULT_EXTRACTION_LIMITS,
    ) -> dict:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        entries = self.entries()
        by_index = {entry.index: entry for entry in entries}
        directories = [entry for entry in entries if entry.is_directory]
        files = [entry for entry in entries if not entry.is_directory]

        resolved_paths: dict[int, Path] = {}
        path_kinds: dict[str, str] = {}
        for entry in entries:
            relative = self._entry_relative_path(entry, by_index)
            key = relative.as_posix().casefold()
            kind = "directory" if entry.is_directory else "file"
            previous = path_kinds.get(key)
            if previous is not None:
                raise ContainerError(
                    f"duplicate or colliding STFS path {relative.as_posix()} "
                    f"({previous} versus {kind})"
                )
            path_kinds[key] = kind
            resolved_paths[entry.index] = relative
            if not entry.is_directory and entry.file_size > entry.block_count * BLOCK_SIZE:
                raise ContainerError(
                    f"STFS entry {relative.as_posix()} declares {entry.file_size} bytes "
                    f"but only {entry.block_count} data block(s)"
                )

        planned_files, planned_bytes = _validate_extraction_plan(
            ((resolved_paths[entry.index].as_posix(), entry.file_size) for entry in files),
            limits,
        )
        extracted_files: list[dict] = []

        for entry in sorted(directories, key=lambda item: item.index):
            relative = resolved_paths[entry.index]
            _target_for(destination, relative).mkdir(parents=True, exist_ok=True)

        for entry in sorted(files, key=lambda item: item.index):
            relative = resolved_paths[entry.index]
            target = _target_for(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + ".siig-part")
            temp.unlink(missing_ok=True)
            remaining = entry.file_size
            current = entry.start_block
            seen: set[int] = set()
            try:
                with temp.open("wb") as output:
                    for ordinal in range(entry.block_count):
                        if remaining <= 0:
                            break
                        if current in seen:
                            raise ContainerError(f"cycle in block chain for {relative.as_posix()}")
                        seen.add(current)
                        if current >= self.allocated_blocks:
                            raise ContainerError(f"file block outside allocation for {relative.as_posix()}")
                        payload = self.read_block(current)
                        take = min(remaining, BLOCK_SIZE)
                        output.write(payload[:take])
                        remaining -= take
                        if remaining <= 0:
                            break
                        if entry.is_consecutive:
                            current = entry.start_block + ordinal + 1
                        else:
                            current = self.next_block(current)
                            if current == 0xFFFFFF:
                                raise ContainerError(f"premature end of block chain for {relative.as_posix()}")
                if remaining:
                    raise ContainerError(
                        f"STFS entry {relative.as_posix()} ended {remaining} byte(s) early "
                        f"({entry.block_count} blocks declared)"
                    )
                _atomic_replace(temp, target)
            except Exception:
                temp.unlink(missing_ok=True)
                raise
            extracted_files.append({"path": relative.as_posix(), "size": entry.file_size})

        return {
            "format": "STFS",
            "magic": self.magic.decode("ascii").rstrip(),
            "header_size": self.header_size,
            "file_system": "STFS",
            "allocated_blocks": self.allocated_blocks,
            "file_table_blocks": self.file_table_block_count,
            "hash_level": self.top_level,
            "directories": len(directories),
            "files": len(extracted_files),
            "bytes_extracted": sum(item["size"] for item in extracted_files),
            "planned_files": planned_files,
            "planned_bytes": planned_bytes,
            "limits": {
                "max_files": limits.max_files,
                "max_total_bytes": limits.max_total_bytes,
                "max_file_bytes": limits.max_file_bytes,
            },
            "members": extracted_files,
            "signature_verification": "not_performed",
        }


def extract_stfs(
    package_path: Path,
    destination: Path,
    limits: ExtractionLimits = DEFAULT_EXTRACTION_LIMITS,
) -> dict:
    with _StfsReader(Path(package_path)) as reader:
        return reader.extract(Path(destination), limits=limits)


# AES-128 implementation used solely for PS3 PKG CTR decryption. The round
# functions follow FIPS-197 and avoid a third-party runtime dependency.
_AES_SBOX = (
    0x63,0x7C,0x77,0x7B,0xF2,0x6B,0x6F,0xC5,0x30,0x01,0x67,0x2B,0xFE,0xD7,0xAB,0x76,
    0xCA,0x82,0xC9,0x7D,0xFA,0x59,0x47,0xF0,0xAD,0xD4,0xA2,0xAF,0x9C,0xA4,0x72,0xC0,
    0xB7,0xFD,0x93,0x26,0x36,0x3F,0xF7,0xCC,0x34,0xA5,0xE5,0xF1,0x71,0xD8,0x31,0x15,
    0x04,0xC7,0x23,0xC3,0x18,0x96,0x05,0x9A,0x07,0x12,0x80,0xE2,0xEB,0x27,0xB2,0x75,
    0x09,0x83,0x2C,0x1A,0x1B,0x6E,0x5A,0xA0,0x52,0x3B,0xD6,0xB3,0x29,0xE3,0x2F,0x84,
    0x53,0xD1,0x00,0xED,0x20,0xFC,0xB1,0x5B,0x6A,0xCB,0xBE,0x39,0x4A,0x4C,0x58,0xCF,
    0xD0,0xEF,0xAA,0xFB,0x43,0x4D,0x33,0x85,0x45,0xF9,0x02,0x7F,0x50,0x3C,0x9F,0xA8,
    0x51,0xA3,0x40,0x8F,0x92,0x9D,0x38,0xF5,0xBC,0xB6,0xDA,0x21,0x10,0xFF,0xF3,0xD2,
    0xCD,0x0C,0x13,0xEC,0x5F,0x97,0x44,0x17,0xC4,0xA7,0x7E,0x3D,0x64,0x5D,0x19,0x73,
    0x60,0x81,0x4F,0xDC,0x22,0x2A,0x90,0x88,0x46,0xEE,0xB8,0x14,0xDE,0x5E,0x0B,0xDB,
    0xE0,0x32,0x3A,0x0A,0x49,0x06,0x24,0x5C,0xC2,0xD3,0xAC,0x62,0x91,0x95,0xE4,0x79,
    0xE7,0xC8,0x37,0x6D,0x8D,0xD5,0x4E,0xA9,0x6C,0x56,0xF4,0xEA,0x65,0x7A,0xAE,0x08,
    0xBA,0x78,0x25,0x2E,0x1C,0xA6,0xB4,0xC6,0xE8,0xDD,0x74,0x1F,0x4B,0xBD,0x8B,0x8A,
    0x70,0x3E,0xB5,0x66,0x48,0x03,0xF6,0x0E,0x61,0x35,0x57,0xB9,0x86,0xC1,0x1D,0x9E,
    0xE1,0xF8,0x98,0x11,0x69,0xD9,0x8E,0x94,0x9B,0x1E,0x87,0xE9,0xCE,0x55,0x28,0xDF,
    0x8C,0xA1,0x89,0x0D,0xBF,0xE6,0x42,0x68,0x41,0x99,0x2D,0x0F,0xB0,0x54,0xBB,0x16,
)


def _xtime(value: int) -> int:
    return ((value << 1) ^ (0x11B if value & 0x80 else 0)) & 0xFF


_AES_INV_SBOX = tuple(_AES_SBOX.index(value) for value in range(256))


def _gf_mul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a = _xtime(a)
        b >>= 1
    return result & 0xFF


class _AES128:
    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("AES-128 key must be 16 bytes")
        expanded = list(key)
        rcon = 1
        while len(expanded) < 176:
            temp = expanded[-4:]
            if len(expanded) % 16 == 0:
                temp = temp[1:] + temp[:1]
                temp = [_AES_SBOX[value] for value in temp]
                temp[0] ^= rcon
                rcon = _xtime(rcon)
            for value in temp:
                expanded.append(expanded[-16] ^ value)
        self.round_keys = bytes(expanded)

    def encrypt_block(self, block: bytes) -> bytes:
        if len(block) != 16:
            raise ValueError("AES block must be 16 bytes")
        state = [value ^ self.round_keys[index] for index, value in enumerate(block)]
        for round_index in range(1, 10):
            state = [_AES_SBOX[value] for value in state]
            state = [
                state[0], state[5], state[10], state[15],
                state[4], state[9], state[14], state[3],
                state[8], state[13], state[2], state[7],
                state[12], state[1], state[6], state[11],
            ]
            for column in range(4):
                index = column * 4
                a, b, c, d = state[index:index + 4]
                mix = a ^ b ^ c ^ d
                first = a
                state[index] = a ^ mix ^ _xtime(a ^ b)
                state[index + 1] = b ^ mix ^ _xtime(b ^ c)
                state[index + 2] = c ^ mix ^ _xtime(c ^ d)
                state[index + 3] = d ^ mix ^ _xtime(d ^ first)
            key_offset = round_index * 16
            state = [value ^ self.round_keys[key_offset + index] for index, value in enumerate(state)]
        state = [_AES_SBOX[value] for value in state]
        state = [
            state[0], state[5], state[10], state[15],
            state[4], state[9], state[14], state[3],
            state[8], state[13], state[2], state[7],
            state[12], state[1], state[6], state[11],
        ]
        key_offset = 160
        return bytes(value ^ self.round_keys[key_offset + index] for index, value in enumerate(state))

    def decrypt_block(self, block: bytes) -> bytes:
        """Decrypt one AES-128 block (FIPS-197 inverse cipher)."""
        if len(block) != 16:
            raise ValueError("AES block must be 16 bytes")
        state = [value ^ self.round_keys[160 + index] for index, value in enumerate(block)]
        for round_index in range(9, 0, -1):
            # Inverse ShiftRows for the column-major state representation.
            state = [
                state[0], state[13], state[10], state[7],
                state[4], state[1], state[14], state[11],
                state[8], state[5], state[2], state[15],
                state[12], state[9], state[6], state[3],
            ]
            state = [_AES_INV_SBOX[value] for value in state]
            key_offset = round_index * 16
            state = [value ^ self.round_keys[key_offset + index] for index, value in enumerate(state)]
            for column in range(4):
                index = column * 4
                a, b, c, d = state[index:index + 4]
                state[index] = _gf_mul(a, 14) ^ _gf_mul(b, 11) ^ _gf_mul(c, 13) ^ _gf_mul(d, 9)
                state[index + 1] = _gf_mul(a, 9) ^ _gf_mul(b, 14) ^ _gf_mul(c, 11) ^ _gf_mul(d, 13)
                state[index + 2] = _gf_mul(a, 13) ^ _gf_mul(b, 9) ^ _gf_mul(c, 14) ^ _gf_mul(d, 11)
                state[index + 3] = _gf_mul(a, 11) ^ _gf_mul(b, 13) ^ _gf_mul(c, 9) ^ _gf_mul(d, 14)
        state = [
            state[0], state[13], state[10], state[7],
            state[4], state[1], state[14], state[11],
            state[8], state[5], state[2], state[15],
            state[12], state[9], state[6], state[3],
        ]
        state = [_AES_INV_SBOX[value] for value in state]
        return bytes(value ^ self.round_keys[index] for index, value in enumerate(state))


# Public PS3 package content key used by the installed-content PKG format.
_PS3_PKG_KEY = bytes.fromhex("2E7B71D7C9C9A14EA3221F188828B8F8")


class _PkgDecryptor:
    def __init__(self, finalized: bool, digest: bytes, riv: bytes, debug_arcade: bool = False):
        self.finalized = finalized
        if finalized:
            self.aes = _AES128(_PS3_PKG_KEY)
            self.counter_base = int.from_bytes(riv, "big")
            self.debug_seed = None
        else:
            self.aes = None
            seed = bytearray(0x40)
            seed[0:8] = digest[0:8]
            seed[8:16] = digest[0:8]
            if debug_arcade:
                seed[16:24] = digest[0:8]
                seed[24:32] = digest[8:16]
                seed[32:56] = b"\xA0" * 0x18
            else:
                seed[16:24] = digest[8:16]
                seed[24:32] = digest[8:16]
            self.debug_seed = int.from_bytes(seed, "big")
            self.counter_base = 0

    def keystream_block(self, block_index: int) -> bytes:
        if self.finalized:
            counter = (self.counter_base + block_index) & ((1 << 128) - 1)
            return self.aes.encrypt_block(counter.to_bytes(16, "big"))  # type: ignore[union-attr]
        counter = (self.debug_seed + block_index) & ((1 << 512) - 1)  # type: ignore[operator]
        return hashlib.sha1(counter.to_bytes(0x40, "big")).digest()[:16]

    def crypt(self, offset: int, data: bytes) -> bytes:
        if not data:
            return b""
        output = bytearray(len(data))
        position = 0
        block_index = offset // 16
        skip = offset % 16
        while position < len(data):
            stream = self.keystream_block(block_index)
            take = min(16 - skip, len(data) - position)
            for index in range(take):
                output[position + index] = data[position + index] ^ stream[skip + index]
            position += take
            block_index += 1
            skip = 0
        return bytes(output)


@dataclass
class _PkgItem:
    index: int
    name_offset: int
    name_size: int
    data_offset: int
    data_size: int
    flags: int
    name: str = ""

    @property
    def is_directory(self) -> bool:
        return (self.flags & 0xFF) in (0x04, 0x12)

    @property
    def key_index(self) -> int:
        return (self.flags >> 28) & 0x07


class _PkgReader:
    def __init__(self, package_path: Path):
        self.path = Path(package_path)
        self.file_size = self.path.stat().st_size
        self.handle = self.path.open("rb")
        try:
            header = _read_exact(self.handle, 0, 0x80, self.file_size)
            if header[:4] != PKG_MAGIC:
                raise ContainerError("not a PlayStation 3 PKG")
            (
                _magic,
                self.revision,
                self.package_type,
                self.metadata_offset,
                self.metadata_count,
                self.metadata_size,
                self.item_count,
                self.total_size,
                self.data_offset,
                self.data_size,
            ) = struct.unpack_from(">4sHHIIIIQQQ", header, 0)
            self.content_id = header[0x30:0x60].rstrip(b"\x00").decode("ascii", errors="replace")
            self.digest = header[0x60:0x70]
            self.data_riv = header[0x70:0x80]
            if self.package_type != 1:
                raise ContainerError(f"PKG type {self.package_type} is not a PS3 package")
            if not self.item_count or self.item_count > 1_000_000:
                raise ContainerError(f"invalid PKG item count {self.item_count}")
            if self.data_offset < 0x80 or self.data_offset + self.data_size > self.file_size:
                raise ContainerError("PKG encrypted data region is outside the file")
            if self.total_size and self.total_size > self.file_size:
                raise ContainerError("PKG declared total size exceeds the file")
            self.finalized = bool(self.revision & 0x8000)
            self.decryptor, self.table_offset = self._select_decryptor_and_table()
            self._fast_handle = None
            self._fast_path = None
            self.decrypt_backend = "python"
        except Exception:
            self.handle.close()
            raise

    def close(self) -> None:
        if getattr(self, "_fast_handle", None) is not None:
            self._fast_handle.close()
            self._fast_handle = None
        if getattr(self, "_fast_path", None) is not None:
            try:
                Path(self._fast_path).unlink(missing_ok=True)
            finally:
                self._fast_path = None
        self.handle.close()

    def __enter__(self) -> "_PkgReader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _encrypted_read(self, relative_offset: int, size: int) -> bytes:
        if relative_offset < 0 or size < 0 or relative_offset + size > self.data_size:
            raise ContainerError("PKG item read is outside encrypted data region")
        return _read_exact(self.handle, self.data_offset + relative_offset, size, self.file_size)

    def _decrypted_read_with(self, decryptor: _PkgDecryptor, relative_offset: int, size: int) -> bytes:
        return decryptor.crypt(relative_offset, self._encrypted_read(relative_offset, size))

    def decrypted_read(self, relative_offset: int, size: int) -> bytes:
        if self._fast_handle is not None:
            return _read_exact(self._fast_handle, relative_offset, size, self.data_size)
        return self._decrypted_read_with(self.decryptor, relative_offset, size)

    def _prepare_fast_decrypt(self) -> bool:
        """Materialize the encrypted data region through OpenSSL when available.

        PKG extraction remains dependency-free: failure or absence of OpenSSL
        simply leaves the established Python CTR implementation in use.
        """
        if not self.finalized or self._fast_handle is not None:
            return self._fast_handle is not None
        executable = shutil.which("openssl")
        if not executable:
            return False
        iv = self.decryptor.counter_base.to_bytes(16, "big").hex()
        temp = tempfile.NamedTemporaryFile(prefix="siig_pkg_", suffix=".dec", delete=False)
        temp_path = Path(temp.name)
        temp.close()
        try:
            with temp_path.open("wb") as output:
                process = subprocess.Popen(
                    [
                        executable, "enc", "-d", "-aes-128-ctr", "-nopad",
                        "-K", _PS3_PKG_KEY.hex(), "-iv", iv,
                    ],
                    stdin=subprocess.PIPE, stdout=output, stderr=subprocess.PIPE,
                )
                assert process.stdin is not None
                self.handle.seek(self.data_offset)
                remaining = self.data_size
                try:
                    while remaining:
                        chunk = self.handle.read(min(4 * 1024 * 1024, remaining))
                        if not chunk:
                            raise ContainerError("short read while feeding OpenSSL PKG decryptor")
                        process.stdin.write(chunk)
                        remaining -= len(chunk)
                    process.stdin.close()
                    stderr = process.stderr.read() if process.stderr is not None else b""
                    return_code = process.wait()
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
                    raise
            if return_code != 0 or temp_path.stat().st_size != self.data_size:
                temp_path.unlink(missing_ok=True)
                return False
            self._fast_path = temp_path
            self._fast_handle = temp_path.open("rb")
            self.decrypt_backend = "openssl"
            return True
        except (OSError, subprocess.SubprocessError, BrokenPipeError, ContainerError):
            temp_path.unlink(missing_ok=True)
            return False

    def _parse_item_records(self, decryptor: _PkgDecryptor, table_offset: int, limited: bool = False) -> list[_PkgItem]:
        count = min(self.item_count, 8) if limited else self.item_count
        table_size = count * 0x20
        if table_offset + table_size > self.data_size:
            raise ContainerError("PKG item table exceeds encrypted data region")
        raw = self._decrypted_read_with(decryptor, table_offset, table_size)
        result: list[_PkgItem] = []
        for index in range(count):
            name_offset, name_size, data_offset, data_size, flags, _padding = struct.unpack_from(">IIQQI4s", raw, index * 0x20)
            if name_size == 0 or name_size > 0x10000:
                raise ContainerError("implausible PKG item name size")
            if name_offset + name_size > self.data_size:
                raise ContainerError("PKG item name is outside encrypted data")
            if data_offset > self.data_size or data_size > self.data_size - data_offset:
                raise ContainerError("PKG item payload is outside encrypted data")
            result.append(_PkgItem(index, name_offset, name_size, data_offset, data_size, flags))
        return result

    def _candidate_is_plausible(self, decryptor: _PkgDecryptor, table_offset: int) -> bool:
        try:
            items = self._parse_item_records(decryptor, table_offset, limited=True)
            for item in items:
                raw_name = self._decrypted_read_with(decryptor, item.name_offset, item.name_size)
                name = raw_name.split(b"\x00", 1)[0].decode("utf-8")
                _safe_relative_path(name)
            return True
        except (ContainerError, UnicodeDecodeError, ValueError):
            return False

    def _select_decryptor_and_table(self) -> tuple[_PkgDecryptor, int]:
        if self.finalized:
            decryptors = [_PkgDecryptor(True, self.digest, self.data_riv, False)]
            if self.digest != self.data_riv:
                # Some documentation/tooling names the 0x60 field as the CTR
                # seed. Trying it second is harmless because the item table has
                # strong structural validation before extraction begins.
                decryptors.append(_PkgDecryptor(True, self.digest, self.digest, False))
        else:
            decryptors = [
                _PkgDecryptor(False, self.digest, self.data_riv, False),
                _PkgDecryptor(False, self.digest, self.data_riv, True),
            ]
        for decryptor in decryptors:
            if self._candidate_is_plausible(decryptor, 0):
                return decryptor, 0
            # Nonstandard/debug builders can place the item table after a small
            # encrypted preamble. Search a bounded aligned range rather than
            # making assumptions from the filename or revision alone.
            search_limit = min(self.data_size, 0x10000)
            for table_offset in range(0x10, search_limit, 0x10):
                if self._candidate_is_plausible(decryptor, table_offset):
                    return decryptor, table_offset
        raise ContainerError("could not decrypt or locate the PS3 PKG item table")

    def items(self) -> list[_PkgItem]:
        items = self._parse_item_records(self.decryptor, self.table_offset, limited=False)
        for item in items:
            raw_name = self.decrypted_read(item.name_offset, item.name_size)
            try:
                item.name = raw_name.split(b"\x00", 1)[0].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ContainerError(f"invalid UTF-8 in PKG item {item.index}") from exc
            _safe_relative_path(item.name)
            if item.key_index != 0:
                raise ContainerError(
                    f"PS3 PKG item {item.index} requests unsupported key index {item.key_index}"
                )
        return items

    def extract(
        self,
        destination: Path,
        limits: ExtractionLimits = DEFAULT_EXTRACTION_LIMITS,
    ) -> dict:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        self._prepare_fast_decrypt()
        items = self.items()
        resolved_paths: dict[int, Path] = {}
        path_kinds: dict[str, str] = {}
        for item in items:
            relative = _safe_relative_path(item.name)
            key = relative.as_posix().casefold()
            kind = "directory" if item.is_directory else "file"
            previous = path_kinds.get(key)
            if previous is not None:
                raise ContainerError(
                    f"duplicate or colliding PKG path {relative.as_posix()} "
                    f"({previous} versus {kind})"
                )
            path_kinds[key] = kind
            resolved_paths[item.index] = relative

        files = [item for item in items if not item.is_directory]
        planned_files, planned_bytes = _validate_extraction_plan(
            ((resolved_paths[item.index].as_posix(), item.data_size) for item in files),
            limits,
        )
        extracted_files: list[dict] = []
        directories = 0
        for item in items:
            relative = resolved_paths[item.index]
            target = _target_for(destination, relative)
            if item.is_directory:
                target.mkdir(parents=True, exist_ok=True)
                directories += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + ".siig-part")
            temp.unlink(missing_ok=True)
            remaining = item.data_size
            relative_offset = item.data_offset
            try:
                with temp.open("wb") as output:
                    while remaining:
                        take = min(1024 * 1024, remaining)
                        output.write(self.decrypted_read(relative_offset, take))
                        relative_offset += take
                        remaining -= take
                _atomic_replace(temp, target)
            except Exception:
                temp.unlink(missing_ok=True)
                raise
            extracted_files.append({"path": relative.as_posix(), "size": item.data_size})
        return {
            "format": "PS3_PKG",
            "revision": f"0x{self.revision:04X}",
            "finalized": self.finalized,
            "content_id": self.content_id,
            "metadata_size": self.metadata_size,
            "data_offset": self.data_offset,
            "data_size": self.data_size,
            "item_table_offset": self.table_offset,
            "decrypt_backend": self.decrypt_backend,
            "directories": directories,
            "files": len(extracted_files),
            "bytes_extracted": sum(item["size"] for item in extracted_files),
            "planned_files": planned_files,
            "planned_bytes": planned_bytes,
            "limits": {
                "max_files": limits.max_files,
                "max_total_bytes": limits.max_total_bytes,
                "max_file_bytes": limits.max_file_bytes,
            },
            "members": extracted_files,
            "signature_verification": "not_performed",
            "inner_npdrm_note": "SELF/EDAT/SDAT payloads are preserved; this removes only the PKG layer",
        }


def extract_ps3_pkg(
    package_path: Path,
    destination: Path,
    limits: ExtractionLimits = DEFAULT_EXTRACTION_LIMITS,
) -> dict:
    with _PkgReader(Path(package_path)) as reader:
        return reader.extract(Path(destination), limits=limits)


def unpack_outer_container(
    package_path: Path,
    destination: Path,
    limits: ExtractionLimits = DEFAULT_EXTRACTION_LIMITS,
) -> dict:
    kind = detect_container_kind(Path(package_path))
    if kind == "stfs":
        return extract_stfs(Path(package_path), Path(destination), limits=limits)
    if kind == "ps3_pkg":
        return extract_ps3_pkg(Path(package_path), Path(destination), limits=limits)
    raise ContainerError("input is not an Xbox 360 STFS package or PlayStation 3 PKG")


def aes_self_test() -> bool:
    key = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
    plain = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    expected = bytes.fromhex("69C4E0D86A7B0430D8CDB78070B4C55A")
    return _AES128(key).encrypt_block(plain) == expected
