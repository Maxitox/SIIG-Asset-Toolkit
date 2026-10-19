#!/usr/bin/env python3
"""Minimal, dependency-free NPDRM SDAT support for Space Invaders Infinity Gene.

This module intentionally implements only the SDAT subset observed in the retail
PS3 release.  It is a clean local implementation derived from format behaviour
validated against the supplied game files; no third-party source code is
vendored here.
"""
from __future__ import annotations

import hashlib
import hmac
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from siig_containers import _AES128

NPD_MAGIC = b"NPD\x00"
SDAT_KEY = bytes.fromhex("0D655EF8E674A98AB8505CFA7D012933")
EDAT_KEY_0 = bytes.fromhex("BE959CA8308DEFA2E5E180C63712A9AE")
EDAT_KEY_1 = bytes.fromhex("4CA9C14B01C95309969BEC68AA0BC081")
SDAT_FLAG = 0x01000000
FLAG_COMPRESSED = 0x00000001
FLAG_NO_CRYPT = 0x00000002
FLAG_KEY_ENCRYPTED = 0x00000008
FLAG_HASH_HMAC = 0x00000010
FLAG_HASH_20 = 0x00000020


class SdatError(Exception):
    """Raised when an SDAT is malformed, unsupported, or fails authentication."""


@dataclass(frozen=True)
class SdatInfo:
    version: int
    license: int
    type: int
    content_id: str
    digest: bytes
    title_hash: bytes
    dev_hash: bytes
    flags: int
    block_size: int
    file_size: int

    @property
    def block_count(self) -> int:
        return (self.file_size + self.block_size - 1) // self.block_size


def _xor16(a: bytes, b: bytes) -> bytes:
    if len(a) != 16 or len(b) != 16:
        raise ValueError("xor16 requires 16-byte inputs")
    return bytes(x ^ y for x, y in zip(a, b))


def _read_exact(handle: BinaryIO, offset: int, size: int) -> bytes:
    handle.seek(offset)
    data = handle.read(size)
    if len(data) != size:
        raise SdatError(f"truncated SDAT at 0x{offset:X} (+0x{size:X})")
    return data


def parse_sdat_header(path: Path) -> SdatInfo:
    path = Path(path)
    with path.open("rb") as handle:
        header = _read_exact(handle, 0, 0x100)
    if header[:4] != NPD_MAGIC:
        raise SdatError("not an NPD/SDAT file")
    version, license_value, type_value = struct.unpack_from(">III", header, 4)
    content_raw = header[0x10:0x40]
    content_id = content_raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")
    digest = header[0x40:0x50]
    title_hash = header[0x50:0x60]
    dev_hash = header[0x60:0x70]
    flags, block_size = struct.unpack_from(">II", header, 0x80)
    file_size = struct.unpack_from(">Q", header, 0x88)[0]
    if not (flags & SDAT_FLAG):
        raise SdatError(f"NPD file is not marked as SDAT (flags=0x{flags:08X})")
    if block_size <= 0 or block_size > 64 * 1024 * 1024:
        raise SdatError(f"invalid SDAT block size 0x{block_size:X}")
    if file_size < 0:
        raise SdatError("invalid SDAT file size")
    return SdatInfo(
        version=version,
        license=license_value,
        type=type_value,
        content_id=content_id,
        digest=digest,
        title_hash=title_hash,
        dev_hash=dev_hash,
        flags=flags,
        block_size=block_size,
        file_size=file_size,
    )


def _cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(ciphertext) % 16:
        raise SdatError("AES-CBC ciphertext is not block-aligned")
    if len(iv) != 16:
        raise SdatError("AES-CBC IV must be 16 bytes")
    aes = _AES128(key)
    out = bytearray()
    previous = iv
    for pos in range(0, len(ciphertext), 16):
        block = ciphertext[pos:pos + 16]
        decoded = aes.decrypt_block(block)
        out.extend(x ^ y for x, y in zip(decoded, previous))
        previous = block
    return bytes(out)


def _block_keys(info: SdatInfo, block_index: int) -> tuple[bytes, bytes]:
    # NPD v2+ uses dev_hash[0:12] || BE32(block_index) as the per-block seed.
    if info.version <= 1:
        block_seed = b"\x00" * 12 + struct.pack(">I", block_index)
    else:
        block_seed = info.dev_hash[:12] + struct.pack(">I", block_index)
    sdat_root_key = _xor16(info.dev_hash, SDAT_KEY)
    root_aes = _AES128(sdat_root_key)
    crypt_key = root_aes.encrypt_block(block_seed)
    hash_key = root_aes.encrypt_block(crypt_key) if (info.flags & FLAG_HASH_HMAC) else crypt_key
    return crypt_key, hash_key


def _expected_hash(metadata: bytes, flags: int) -> bytes:
    if len(metadata) != 0x20:
        raise SdatError("unsupported SDAT metadata record length")
    # For the 0x20-byte interleaved metadata form used by SIIG, bytes 0..15
    # are XOR-folded with bytes 16..31.  In 20-byte HMAC mode the final four
    # digest bytes remain the first four bytes of the second half.
    folded = bytearray(metadata[:20])
    for i in range(16):
        folded[i] ^= metadata[16 + i]
    return bytes(folded[:20] if (flags & FLAG_HASH_20) else folded[:16])


def decrypt_sdat_bytes(path: Path) -> tuple[bytes, dict]:
    """Decrypt and authenticate the SIIG SDAT at *path*.

    Returns plaintext and a privacy-safe report.  Unsupported NPDRM variants
    fail closed rather than being guessed.
    """
    path = Path(path)
    info = parse_sdat_header(path)
    flags = info.flags
    if flags & FLAG_COMPRESSED:
        raise SdatError("compressed-section SDAT metadata is not supported by the SIIG subset")
    if not (flags & FLAG_HASH_HMAC) or not (flags & FLAG_HASH_20):
        raise SdatError(
            f"unsupported SDAT authentication flags 0x{flags:08X}; expected HMAC-SHA1/20-byte metadata"
        )

    file_bytes = path.stat().st_size
    cursor = 0x100
    plaintext = bytearray()
    blocks: list[dict] = []
    with path.open("rb") as handle:
        for block_index in range(info.block_count):
            remaining = info.file_size - block_index * info.block_size
            clear_len = min(info.block_size, remaining)
            crypt_len = (clear_len + 15) & ~15
            if cursor + 0x20 + crypt_len > file_bytes:
                raise SdatError(f"block {block_index} extends past end of SDAT")
            metadata = _read_exact(handle, cursor, 0x20)
            data_offset = cursor + 0x20
            ciphertext = _read_exact(handle, data_offset, crypt_len)
            crypt_key, hash_key = _block_keys(info, block_index)
            if flags & FLAG_KEY_ENCRYPTED:
                # NPDRM's encrypted-key mode wraps both generated keys once in
                # AES-CBC using the version-family EDAT key and a zero IV. For
                # one 16-byte block CBC reduces to one AES decrypt operation.
                edat_key = EDAT_KEY_1 if info.version == 4 else EDAT_KEY_0
                wrapper = _AES128(edat_key)
                crypt_key = wrapper.decrypt_block(crypt_key)
                hash_key = wrapper.decrypt_block(hash_key)
            expected = _expected_hash(metadata, flags)
            actual = hmac.new(hash_key, ciphertext, hashlib.sha1).digest()
            if not hmac.compare_digest(actual[:len(expected)], expected):
                raise SdatError(f"SDAT block {block_index} HMAC-SHA1 authentication failed")
            if flags & FLAG_NO_CRYPT:
                clear_padded = ciphertext
            else:
                clear_padded = _cbc_decrypt(ciphertext, crypt_key, info.digest)
            plaintext.extend(clear_padded[:clear_len])
            blocks.append({
                "index": block_index,
                "plaintext_bytes": clear_len,
                "ciphertext_bytes": crypt_len,
                "authenticated": True,
            })
            cursor = data_offset + crypt_len

    if len(plaintext) != info.file_size:
        raise SdatError(f"decrypted size mismatch ({len(plaintext)} != {info.file_size})")
    report = {
        "format": "SIIG_SDAT_DECRYPT",
        "npd_version": info.version,
        "flags": f"0x{info.flags:08X}",
        "block_size": info.block_size,
        "block_count": info.block_count,
        "plaintext_bytes": len(plaintext),
        "authenticated_blocks": len(blocks),
        "blocks": blocks,
    }
    return bytes(plaintext), report


def decrypt_sdat_file(input_path: Path, output_path: Path) -> dict:
    plaintext, report = decrypt_sdat_bytes(Path(input_path))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_name(output_path.name + ".siig-part")
    try:
        temp.write_bytes(plaintext)
        temp.replace(output_path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    return report
