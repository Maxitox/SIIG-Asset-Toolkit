#!/usr/bin/env python3
"""Mobile SIIG package helpers (iOS IPA/TZIP and Android APK).

Standard-library only. This module deliberately separates the mobile MAP
little-endian header variant from the shared big-endian DAT format handled by
siig_toolkit.py.
"""
from __future__ import annotations

import base64
import hashlib
import io
import os
import plistlib
import re
import struct
import zipfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

MOBILE_MAP_MAGIC = b"MAP\x00"
DEX_MAGIC_PREFIX = b"dex\n"
UTF8_FLAG = 0x00000100
NO_INDEX = 0xFFFFFFFF

class MobileFormatError(ValueError):
    pass


def _bounded_zlib(data: bytes, max_output: int = 512 * 1024 * 1024) -> bytes:
    d = zlib.decompressobj()
    out = d.decompress(data, max_output + 1)
    if len(out) > max_output:
        raise MobileFormatError("TZIP expansion exceeds configured limit")
    out += d.flush(max_output + 1 - len(out))
    if len(out) > max_output:
        raise MobileFormatError("TZIP expansion exceeds configured limit")
    if d.unused_data:
        raise MobileFormatError("unexpected trailing data after TZIP zlib stream")
    return out


def parse_tzip_bytes(data: bytes, *, max_output: int = 512 * 1024 * 1024, max_entries: int = 100_000) -> dict[str, bytes]:
    try:
        decoded = _bounded_zlib(data, max_output=max_output)
        obj = plistlib.loads(decoded)
    except (zlib.error, plistlib.InvalidFileException, ValueError) as exc:
        raise MobileFormatError(f"invalid SIIG TZIP: {exc}") from exc
    if not isinstance(obj, dict):
        raise MobileFormatError("TZIP plist root is not a dictionary")
    if len(obj) > max_entries:
        raise MobileFormatError("TZIP entry count exceeds configured limit")
    result: dict[str, bytes] = {}
    for name, payload in obj.items():
        if not isinstance(name, str) or not isinstance(payload, (bytes, bytearray)):
            raise MobileFormatError("TZIP entries must map string names to data blobs")
        pp = PurePosixPath(name.replace("\\", "/"))
        if pp.is_absolute() or ".." in pp.parts or not pp.parts:
            raise MobileFormatError(f"unsafe TZIP member path: {name!r}")
        clean = pp.as_posix()
        if clean in result:
            raise MobileFormatError(f"duplicate TZIP member: {clean}")
        result[clean] = bytes(payload)
    return result


def extract_tzip_file(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> dict[str, Any]:
    src = Path(source)
    root = Path(destination)
    entries = parse_tzip_bytes(src.read_bytes())
    root.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, payload in sorted(entries.items()):
        out = root.joinpath(*PurePosixPath(name).parts)
        resolved_root = root.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        if resolved_root not in out.resolve().parents and out.resolve() != resolved_root:
            raise MobileFormatError(f"unsafe output path: {name!r}")
        out.write_bytes(payload)
        total += len(payload)
    return {"format": "SIIG_TZIP", "source": src.name, "entries": len(entries), "payload_bytes": total}


def parse_mobile_map_bytes(data: bytes, *, max_layers: int = 4096, max_cells: int = 200_000_000) -> dict[str, Any]:
    if len(data) < 8 or data[:4] != MOBILE_MAP_MAGIC:
        raise MobileFormatError("not a mobile SIIG MAP file")
    layer_count = struct.unpack_from("<I", data, 4)[0]
    if layer_count > max_layers:
        raise MobileFormatError("mobile MAP layer count is unreasonable")
    pos = 8
    layers = []
    total_cells = 0
    for index in range(layer_count):
        if pos + 8 > len(data):
            raise MobileFormatError(f"truncated mobile MAP layer {index} header")
        width, height = struct.unpack_from("<II", data, pos)
        pos += 8
        cells = width * height
        total_cells += cells
        if cells > max_cells or total_cells > max_cells:
            raise MobileFormatError("mobile MAP cell count exceeds configured limit")
        if pos + cells > len(data):
            raise MobileFormatError(f"truncated mobile MAP layer {index} cells")
        blob = data[pos:pos + cells]
        pos += cells
        base_ids = [b & 0x3F for b in blob if (b & 0x3F)]
        layers.append({
            "index": index,
            "width": width,
            "height": height,
            "cell_count": cells,
            "nonzero_cells": sum(1 for b in blob if b),
            "max_base_tile_id": max(base_ids, default=0),
            "x_flip_cells": sum(1 for b in blob if b & 0x40),
            "y_flip_cells": sum(1 for b in blob if b & 0x80),
        })
    if pos != len(data):
        raise MobileFormatError(f"mobile MAP has {len(data)-pos} trailing bytes")
    return {
        "format": "SIIG_MOBILE_MAP",
        "endianness": "little",
        "layer_count": layer_count,
        "layers": layers,
        "total_cells": total_cells,
        "nonempty_layers": sum(1 for x in layers if x["cell_count"]),
    }


def parse_dex_header_bytes(data: bytes) -> dict[str, Any]:
    if len(data) < 0x70 or data[:4] != DEX_MAGIC_PREFIX or data[7] != 0:
        raise MobileFormatError("not a DEX file")
    version = data[4:7].decode("ascii", "replace")
    checksum = struct.unpack_from("<I", data, 8)[0]
    signature = data[12:32]
    file_size, header_size, endian_tag = struct.unpack_from("<III", data, 32)
    if file_size > len(data) or header_size < 0x70:
        raise MobileFormatError("invalid DEX size/header")
    sha1_actual = hashlib.sha1(data[32:file_size]).digest()
    adler_actual = zlib.adler32(data[12:file_size]) & 0xFFFFFFFF
    return {
        "format": "DEX",
        "version": version,
        "file_size": file_size,
        "header_size": header_size,
        "endian_tag": f"0x{endian_tag:08X}",
        "stored_sha1": signature.hex(),
        "computed_sha1": sha1_actual.hex(),
        "sha1_ok": signature == sha1_actual,
        "stored_adler32": f"0x{checksum:08X}",
        "computed_adler32": f"0x{adler_actual:08X}",
        "adler32_ok": checksum == adler_actual,
    }


def _u8len(data: bytes, off: int) -> tuple[int, int]:
    a = data[off]; off += 1
    if a & 0x80:
        a = ((a & 0x7F) << 8) | data[off]; off += 1
    return a, off


def _u16len(data: bytes, off: int) -> tuple[int, int]:
    a = struct.unpack_from("<H", data, off)[0]; off += 2
    if a & 0x8000:
        b = struct.unpack_from("<H", data, off)[0]; off += 2
        a = ((a & 0x7FFF) << 16) | b
    return a, off


def _parse_string_pool(data: bytes, off: int) -> tuple[list[str], int]:
    typ, header_size, size = struct.unpack_from("<HHI", data, off)
    if typ != 0x0001 or header_size < 28 or off + size > len(data):
        raise MobileFormatError("invalid Android string pool")
    count, style_count, flags, strings_start, styles_start = struct.unpack_from("<IIIII", data, off + 8)
    offsets_base = off + header_size
    strings_base = off + strings_start
    strings = []
    utf8 = bool(flags & UTF8_FLAG)
    for i in range(count):
        rel = struct.unpack_from("<I", data, offsets_base + i * 4)[0]
        p = strings_base + rel
        if utf8:
            _, p = _u8len(data, p)  # UTF-16 length
            n, p = _u8len(data, p)
            s = data[p:p+n].decode("utf-8", "replace")
        else:
            n, p = _u16len(data, p)
            s = data[p:p+n*2].decode("utf-16le", "replace")
        strings.append(s)
    return strings, off + size


def parse_android_manifest_bytes(data: bytes) -> dict[str, Any]:
    if len(data) < 16:
        raise MobileFormatError("AndroidManifest.xml is too short")
    typ, header_size, size = struct.unpack_from("<HHI", data, 0)
    if typ != 0x0003 or size > len(data):
        raise MobileFormatError("AndroidManifest.xml is not binary AXML")
    strings: list[str] | None = None
    off = header_size
    result: dict[str, Any] = {}
    while off + 8 <= size:
        ctype, chead, csize = struct.unpack_from("<HHI", data, off)
        if csize < 8 or off + csize > size:
            raise MobileFormatError("invalid Android XML chunk")
        if ctype == 0x0001:
            strings, _ = _parse_string_pool(data, off)
        elif ctype == 0x0102 and strings is not None:
            if chead < 16 or off + 36 > len(data):
                raise MobileFormatError("truncated Android start-element")
            ns, name_idx = struct.unpack_from("<II", data, off + 16)
            attr_start, attr_size, attr_count = struct.unpack_from("<HHH", data, off + 24)
            tag = strings[name_idx] if name_idx < len(strings) else f"#{name_idx}"
            attrs = {}
            ap = off + 16 + attr_start
            for _ in range(attr_count):
                if ap + 20 > off + csize:
                    raise MobileFormatError("truncated Android XML attribute")
                ans, aname, raw = struct.unpack_from("<III", data, ap)
                vsize, vres0, vtype, vdata = struct.unpack_from("<HBBI", data, ap + 12)
                key = strings[aname] if aname < len(strings) else f"#{aname}"
                if raw != NO_INDEX and raw < len(strings):
                    value: Any = strings[raw]
                elif vtype == 0x03 and vdata < len(strings):
                    value = strings[vdata]
                elif vtype == 0x12:
                    value = bool(vdata)
                elif vtype in (0x10, 0x11):
                    value = int(vdata)
                else:
                    value = int(vdata)
                attrs[key] = value
                ap += attr_size
            if tag == "manifest":
                result.update({k: attrs.get(k) for k in ("package", "versionCode", "versionName") if k in attrs})
            elif tag == "application" and "debuggable" in attrs:
                result["debuggable"] = attrs["debuggable"]
        off += csize
    result["format"] = "ANDROID_BINARY_XML"
    return result


def _parse_manifest_mf(data: bytes) -> dict[str, str]:
    text = data.decode("utf-8", "replace").replace("\r\n", "\n")
    # unfold continuation lines
    text = re.sub(r"\n ([^\n]*)", r"\1", text)
    result = {}
    for section in text.split("\n\n"):
        fields = {}
        for line in section.splitlines():
            if ": " in line:
                k, v = line.split(": ", 1); fields[k] = v
        if "Name" in fields and "SHA1-Digest" in fields:
            result[fields["Name"]] = fields["SHA1-Digest"]
    return result


def verify_apk_manifest_hashes(zf: zipfile.ZipFile) -> dict[str, Any]:
    if "META-INF/MANIFEST.MF" not in zf.namelist():
        return {"covered_files": 0, "matches": 0, "mismatches": [], "status": "absent"}
    expected = _parse_manifest_mf(zf.read("META-INF/MANIFEST.MF"))
    mismatches = []
    matches = 0
    names = set(zf.namelist())
    for name, digest in expected.items():
        if name not in names:
            mismatches.append(name); continue
        actual = base64.b64encode(hashlib.sha1(zf.read(name)).digest()).decode("ascii")
        if actual == digest: matches += 1
        else: mismatches.append(name)
    return {"covered_files": len(expected), "matches": matches, "mismatches": mismatches, "status": "pass" if not mismatches else "fail"}


def verify_ios_coderesources(zf: zipfile.ZipFile, app_prefix: str) -> dict[str, Any]:
    path = app_prefix + "_CodeSignature/CodeResources"
    if path not in zf.namelist():
        return {"covered_files": 0, "matches": 0, "mismatches": [], "status": "absent"}
    obj = plistlib.loads(zf.read(path))
    files = obj.get("files", {}) if isinstance(obj, dict) else {}
    matches = 0; mismatches = []
    names = set(zf.namelist())
    for rel, spec in files.items():
        expected = spec if isinstance(spec, (bytes, bytearray)) else spec.get("hash") if isinstance(spec, dict) else None
        if not isinstance(expected, (bytes, bytearray)):
            continue
        full = app_prefix + rel
        if full in names and hashlib.sha1(zf.read(full)).digest() == bytes(expected): matches += 1
        else: mismatches.append(rel)
    return {"covered_files": matches + len(mismatches), "matches": matches, "mismatches": mismatches, "status": "pass" if not mismatches else "fail"}


def _macho_info(data: bytes) -> dict[str, Any]:
    if len(data) < 28:
        raise MobileFormatError("Mach-O slice too short")
    magic = data[:4]
    if magic == b"\xCE\xFA\xED\xFE": endian = "<"; is64 = False
    elif magic == b"\xCF\xFA\xED\xFE": endian = "<"; is64 = True
    elif magic == b"\xFE\xED\xFA\xCE": endian = ">"; is64 = False
    elif magic == b"\xFE\xED\xFA\xCF": endian = ">"; is64 = True
    else: raise MobileFormatError("not a Mach-O slice")
    hsize = 32 if is64 else 28
    cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags = struct.unpack_from(endian+"6I", data, 4)
    pos = hsize; cryptids=[]; symtab=None
    for _ in range(ncmds):
        if pos + 8 > len(data): break
        cmd, cmdsize = struct.unpack_from(endian+"II", data, pos)
        if cmdsize < 8 or pos + cmdsize > len(data): break
        basecmd = cmd & 0x7FFFFFFF
        if basecmd in (0x21, 0x2C) and cmdsize >= 20:
            cryptids.append(struct.unpack_from(endian+"I", data, pos+16)[0])
        elif basecmd == 0x2 and cmdsize >= 24:
            symtab = struct.unpack_from(endian+"IIII", data, pos+8)
        pos += cmdsize
    symbols=[]
    if symtab:
        symoff,nsyms,stroff,strsize=symtab; entsz=16 if is64 else 12
        if stroff+strsize <= len(data) and symoff+nsyms*entsz <= len(data):
            stab=data[stroff:stroff+strsize]
            for i in range(nsyms):
                so=struct.unpack_from(endian+"I",data,symoff+i*entsz)[0]
                if 0 < so < len(stab):
                    end=stab.find(b"\0",so)
                    if end>so:
                        s=stab[so:end].decode("utf-8","replace")
                        if s: symbols.append(s)
    return {"cputype":cputype,"cpusubtype":cpusubtype,"is64":is64,"cryptids":cryptids,"encrypted":any(x != 0 for x in cryptids),"symbols":symbols}


def parse_fat_macho(data: bytes) -> dict[str, Any]:
    if data[:4] == b"\xCA\xFE\xBA\xBE":
        n = struct.unpack_from(">I", data, 4)[0]
        slices=[]
        for i in range(n):
            cputype,subtype,off,size,align=struct.unpack_from(">IIIII",data,8+i*20)
            info=_macho_info(data[off:off+size]); info.update({"offset":off,"size":size}); slices.append(info)
    else:
        slices=[_macho_info(data)]
    return {"format":"Mach-O","fat":len(slices)>1,"slices":slices,"all_cryptids":[x for s in slices for x in s["cryptids"]],"all_decrypted":all(not s["encrypted"] for s in slices)}


def inventory_ipa(path: str | os.PathLike[str]) -> dict[str, Any]:
    p=Path(path)
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
        infos=[n for n in names if n.startswith("Payload/") and n.endswith(".app/Info.plist")]
        if len(infos)!=1: raise MobileFormatError("IPA does not contain exactly one app Info.plist")
        info_path=infos[0]; app_prefix=info_path.rsplit("Info.plist",1)[0]
        pl=plistlib.loads(z.read(info_path)); exe_name=pl.get("CFBundleExecutable"); exe_path=app_prefix+str(exe_name)
        macho=parse_fat_macho(z.read(exe_path)) if exe_path in names else None
        tzips=[]
        for n in names:
            if n.startswith(app_prefix) and n.endswith(".tzip"):
                ent=parse_tzip_bytes(z.read(n)); tzips.append({"name":n[len(app_prefix):],"entries":len(ent),"payload_bytes":sum(map(len,ent.values()))})
        return {
            "format":"SIIG_MOBILE_PACKAGE_INVENTORY","platform":"ios","archive":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "bundle_identifier":pl.get("CFBundleIdentifier"),"version":pl.get("CFBundleShortVersionString"),"build":pl.get("CFBundleVersion"),"executable":exe_name,
            "zip_entries":len(names),"tzip_archives":tzips,"macho":macho,"has_overdrive_dylib":app_prefix+"overdrive.dylib" in names,"has_sf_info":any(n.startswith(app_prefix+"SF_Info/") for n in names),
            "code_resources":verify_ios_coderesources(z,app_prefix),
        }



def _der_tlv(data: bytes, off: int) -> tuple[int, int, int, int]:
    if off >= len(data):
        raise MobileFormatError("truncated DER")
    start = off
    tag = data[off]; off += 1
    if off >= len(data): raise MobileFormatError("truncated DER length")
    b = data[off]; off += 1
    if b & 0x80:
        n = b & 0x7F
        if n == 0 or n > 4 or off + n > len(data): raise MobileFormatError("unsupported DER length")
        length = int.from_bytes(data[off:off+n], "big"); off += n
    else:
        length = b
    end = off + length
    if end > len(data): raise MobileFormatError("truncated DER value")
    return tag, off, end, start


def extract_pkcs7_certificates(data: bytes) -> list[bytes]:
    """Extract DER X.509 certificate blobs from the simple APK v1 PKCS#7 SignedData form."""
    try:
        tag, ro, re, _ = _der_tlv(data, 0)
        if tag != 0x30: return []
        # ContentInfo: OID, [0] EXPLICIT SignedData
        p = ro
        _, _, e1, _ = _der_tlv(data, p); p = e1
        t2, o2, e2, _ = _der_tlv(data, p)
        if t2 != 0xA0: return []
        ts, osd, esd, _ = _der_tlv(data, o2)
        if ts != 0x30: return []
        # SignedData children; locate context [0] certificates.
        p = osd
        cert_container = None
        while p < esd:
            t, o, e, st = _der_tlv(data, p)
            if t == 0xA0:
                cert_container = (o, e); break
            p = e
        if not cert_container: return []
        p, end = cert_container
        certs=[]
        while p < end:
            t,o,e,st = _der_tlv(data,p)
            if t == 0x30:
                certs.append(data[st:e])
            p=e
        return certs
    except MobileFormatError:
        return []

def inventory_apk(path: str | os.PathLike[str]) -> dict[str, Any]:
    p=Path(path)
    with zipfile.ZipFile(p) as z:
        names=z.namelist(); manifest=parse_android_manifest_bytes(z.read("AndroidManifest.xml")); dex=parse_dex_header_bytes(z.read("classes.dex")) if "classes.dex" in names else None
        sigs=[n for n in names if n.upper().startswith("META-INF/") and n.upper().endswith((".RSA",".DSA",".EC"))]
        certs=[]
        for sig in sigs:
            for cert in extract_pkcs7_certificates(z.read(sig)):
                certs.append({"signature_block":sig,"sha1":hashlib.sha1(cert).hexdigest(),"sha256":hashlib.sha256(cert).hexdigest(),"bytes":len(cert)})
        return {
            "format":"SIIG_MOBILE_PACKAGE_INVENTORY","platform":"android","archive":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"zip_entries":len(names),
            "package":manifest.get("package"),"version":manifest.get("versionName"),"version_code":manifest.get("versionCode"),"debuggable":manifest.get("debuggable"),
            "dex":dex,"native_libraries":[n for n in names if n.startswith("lib/") and n.endswith(".so")],"signature_blocks":sigs,
            "signature_block_sha1":{n:hashlib.sha1(z.read(n)).hexdigest() for n in sigs},"certificates":certs,"manifest_hashes":verify_apk_manifest_hashes(z),
        }


def inventory_mobile_package(path: str | os.PathLike[str]) -> dict[str, Any]:
    p=Path(path)
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
        if "AndroidManifest.xml" in names: return inventory_apk(p)
        if any(n.startswith("Payload/") and n.endswith(".app/Info.plist") for n in names): return inventory_ipa(p)
    raise MobileFormatError("archive is neither an IPA nor an APK")


def _ipa_stage_resources(path: str | os.PathLike[str]) -> dict[str, bytes]:
    out={}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.endswith("/script.tzip") or n.endswith("/map.tzip"):
                out.update(parse_tzip_bytes(z.read(n)))
    return {k:v for k,v in out.items() if k.lower().endswith((".dat",".map"))}


def _apk_stage_resources(path: str | os.PathLike[str]) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as z:
        return {n[len("assets/"):]:z.read(n) for n in z.namelist() if n.startswith("assets/") and n.lower().endswith((".dat",".map"))}


def compare_mobile_stage_resources(ipa: str | os.PathLike[str], apk: str | os.PathLike[str]) -> dict[str, Any]:
    ios=_ipa_stage_resources(ipa); android=_apk_stage_resources(apk); common=sorted(set(ios)&set(android)); identical=[]; different=[]
    for n in common:
        if ios[n]==android[n]: identical.append(n)
        else: different.append({"name":n,"ios_bytes":len(ios[n]),"android_bytes":len(android[n]),"ios_sha256":hashlib.sha256(ios[n]).hexdigest(),"android_sha256":hashlib.sha256(android[n]).hexdigest()})
    return {"format":"SIIG_MOBILE_STAGE_COMPARE","ios_resources":len(ios),"android_resources":len(android),"common":len(common),"identical":len(identical),"different":len(different),"different_files":different,"ios_only":sorted(set(ios)-set(android)),"android_only":sorted(set(android)-set(ios))}

# Executable-backed mobile-exclusive reference data. These are descriptive
# metadata only; no proprietary resource payloads are embedded.
_SURVIVAL_CHIMERA_SUBSTITUTIONS = (
    {
        "requested_stage_id": 49, "extra": 31, "chimera_stage": "C-1A", "mission": "CAPTAIN NEO",
        "evolution_node": 30, "evolution_title": "EXTRA 31", "unlock_source": "crossover purchase",
        "paired_purchase_node": 88, "paired_purchase_title": "SILVER HAWK",
        "fallback_stage_id": 31, "fallback_extra": 13, "fallback_mission": "PROOF-READING REPAIR",
    },
    {
        "requested_stage_id": 50, "extra": 32, "chimera_stage": "C-2A", "mission": "URBAN TRAIL",
        "evolution_node": 31, "evolution_title": "EXTRA 32", "unlock_source": "crossover purchase",
        "paired_purchase_node": 89, "paired_purchase_title": "INTER GRAY",
        "fallback_stage_id": 40, "fallback_extra": 22, "fallback_mission": "TELEOMORPH",
    },
    {
        "requested_stage_id": 51, "extra": 33, "chimera_stage": "C-3A", "mission": "BORN TO BE FREE",
        "evolution_node": 32, "evolution_title": "EXTRA 33", "unlock_source": "crossover purchase",
        "paired_purchase_node": 90, "paired_purchase_title": "BLACK FLY",
        "fallback_stage_id": 36, "fallback_extra": 18, "fallback_mission": "GENETIC DRIFT",
    },
    {
        "requested_stage_id": 52, "extra": 34, "chimera_stage": "C-1B", "mission": "I CAN NOT APE",
        "evolution_node": 33, "evolution_title": "EXTRA 34", "unlock_source": "clear C-1A / stage 49",
        "paired_purchase_node": None, "paired_purchase_title": None,
        "fallback_stage_id": 27, "fallback_extra": 9, "fallback_mission": "REPLICATION FORK",
    },
    {
        "requested_stage_id": 53, "extra": 35, "chimera_stage": "C-2B", "mission": "BURN ALT AIR",
        "evolution_node": 34, "evolution_title": "EXTRA 35", "unlock_source": "clear C-2A / stage 50",
        "paired_purchase_node": None, "paired_purchase_title": None,
        "fallback_stage_id": 46, "fallback_extra": 28, "fallback_mission": "CHROMOSOMAL DELETION",
    },
    {
        "requested_stage_id": 54, "extra": 36, "chimera_stage": "C-3B", "mission": "BEFORE TEN ORB",
        "evolution_node": 35, "evolution_title": "EXTRA 36", "unlock_source": "clear C-3A / stage 51",
        "paired_purchase_node": None, "paired_purchase_title": None,
        "fallback_stage_id": 30, "fallback_extra": 12, "fallback_mission": "ALLELE",
    },
)

_SURVIVAL_ENDINGS = (
    (28, 37, 1, "LINK", 52, "SURVIVAL_01_CLEAR"),
    (29, 46, 2, "CIRCLE", 53, "SURVIVAL_02_CLEAR"),
    (30, 52, 3, "VIRTUAL", 54, "SURVIVAL_03_CLEAR"),
    (31, 48, 4, "ETERNITY", 55, "SURVIVAL_04_CLEAR"),
    (32, 53, 5, "CUT OFF", 56, "SURVIVAL_05_CLEAR"),
    (33, 38, 6, "IMMORTALITY", 57, "SURVIVAL_06_CLEAR"),
    (34, 54, 7, "PHANTASM", 58, "SURVIVAL_07_CLEAR"),
    (35, 47, 8, "PARALLEL", 59, "SURVIVAL_08_CLEAR"),
)

_V2_BEHAVIOR_BRANCHES = (
    {
        "boss": "THE_MOON", "original_type": 70, "v2_type": 100,
        "shared_mover": "moveTheMoon", "mover_type_branch": False,
        "proven_difference": "V2 constructor uses a different helper family/capacity and adds random initialization.",
    },
    {
        "boss": "THE_SUN", "original_type": 71, "v2_type": 101,
        "shared_mover": "moveTheSun", "mover_type_branch": True,
        "proven_difference": "Original type 71 alone executes a four-pair +/-512 ramp toward 6144; V2 type 101 bypasses that original-only branch.",
    },
    {
        "boss": "GIGANTIC_UFO", "original_type": 72, "v2_type": 102,
        "shared_mover": "moveGiganticUfo", "mover_type_branch": True,
        "proven_difference": "Type-dependent coordinate branches use +4096 versus +18432 in one path; a traceOption path uses multiplier 2 for V2 versus 1 otherwise, shifting the internal offset by 92 additional units.",
    },
    {
        "boss": "LADYBUG", "original_type": 73, "v2_type": 103,
        "shared_mover": "moveLadybug", "mover_type_branch": False,
        "proven_difference": "V2 constructor expands/replaces helper pools, adds one extra ES_Init2 pool, and performs two random initializations.",
    },
    {
        "boss": "MANDALA", "original_type": 74, "v2_type": 104,
        "shared_mover": "moveMandala", "mover_type_branch": False,
        "proven_difference": "V2 constructor replaces helper families/capacities; no direct 74/104 branch was found in the shared mover.",
    },
    {
        "boss": "UNKNOWN", "original_type": 75, "v2_type": 105,
        "shared_mover": "moveUnknown", "mover_type_branch": True,
        "proven_difference": "V2 doubles helper +0x14 values in two phases, doubles helper +0x28 in another phase, and calls setVer2Destroy on defeat.",
    },
)


_V2_ATTACK_POOLS = (
    ("THE_MOON", "original", 36, 20, "dischargeTheMoonShot"),
    ("THE_MOON", "v2", 55, 80, "dischargeTheMoonSearchLaser"),
    ("THE_SUN", "original", 37, 8, "dischargeTheSunLaserShot"),
    ("THE_SUN", "original", 38, 36, "dischargeTheSunWaveShot"),
    ("THE_SUN", "original", 39, 20, "dischargeTheSunLightBallShot"),
    ("THE_SUN", "original", 46, 4, "dischargeLadybugAddSpeedShot"),
    ("THE_SUN", "v2", 56, 8, "dischargeTheSunGammaLaserShot"),
    ("THE_SUN", "v2", 59, 36, "dischargeTheSunRollingLaserShot"),
    ("THE_SUN", "v2", 57, 60, "dischargeTheSunSubSpeedShot"),
    ("THE_SUN", "v2", 46, 4, "dischargeLadybugAddSpeedShot"),
    ("GIGANTIC_UFO", "original", 40, 20, "dischargeGiganticUfoHomingShot"),
    ("GIGANTIC_UFO", "original", 41, 20, "dischargeGiganticUfoLightBallShot"),
    ("GIGANTIC_UFO", "original", 42, 4, "dischargeGiganticUfoLaser01Shot"),
    ("GIGANTIC_UFO", "original", 43, 2, "dischargeGiganticUfoLaser02Shot"),
    ("GIGANTIC_UFO", "original", 44, 2, "dischargeGiganticUfoLaser03Shot"),
    ("GIGANTIC_UFO", "v2", 63, 20, "dischargeGiganticUfoSubSpeedShot"),
    ("GIGANTIC_UFO", "v2", 60, 40, "dischargeGiganticUfoShortLaserShot"),
    ("GIGANTIC_UFO", "v2", 61, 4, "dischargeGiganticUfoLargeLaserShot"),
    ("GIGANTIC_UFO", "v2", 62, 80, "dischargeGiganticUfoSearchLaserShot"),
    ("LADYBUG", "original", 45, 40, "dischargeLadybugHomingShot"),
    ("LADYBUG", "original", 46, 20, "dischargeLadybugAddSpeedShot"),
    ("LADYBUG", "original", 47, 4, "dischargeLadybugLaserShot"),
    ("LADYBUG", "v2", 66, 40, "dischargeLadybugLightBallShot"),
    ("LADYBUG", "v2", 65, 48, "dischargeLadybugSubSpeedShot"),
    ("LADYBUG", "v2", 64, 40, "dischargeLadybugLaserShot2"),
    ("LADYBUG", "v2", 67, 80, "dischargeLadybugSubSpeedShot2"),
    ("MANDALA", "original", 48, 100, "dischargeMandalaBeamShot"),
    ("MANDALA", "original", 49, 10, "dischargeMandalaLightBallShot"),
    ("MANDALA", "original", 50, 40, "dischargeMandalaShotLShot"),
    ("MANDALA", "v2", 68, 80, "dischargeMandalaTwinShot"),
    ("MANDALA", "v2", 49, 10, "dischargeMandalaLightBallShot"),
    ("MANDALA", "v2", 71, 40, "dischargeMandalaLaserShot"),
    ("UNKNOWN", "original", 51, 30, "dischargeUnknownShotS"),
    ("UNKNOWN", "original", 52, 30, "dischargeUnknownLightBall"),
    ("UNKNOWN", "original", 53, 80, "dischargeUnknownSubSpeedShot"),
    ("UNKNOWN", "v2", 72, 80, "dischargeUnknownAddSpeedShot"),
    ("UNKNOWN", "v2", 73, 40, "dischargeUnknownHomingShot"),
    ("UNKNOWN", "v2", 74, 80, "dischargeUnknownAddSpeedShot2"),
)


def mobile_exclusives_reference() -> dict[str, Any]:
    """Return static executable-backed reference data for mobile-exclusive systems."""
    substitutions = [dict(x) for x in _SURVIVAL_CHIMERA_SUBSTITUTIONS]
    endings = [
        {
            "terminal_node": node, "stage_id": stage_id, "ending_number": number,
            "ending_name": name, "achievement_index": achievement_index,
            "achievement_key": achievement_key,
        }
        for node, stage_id, number, name, achievement_index, achievement_key in _SURVIVAL_ENDINGS
    ]
    return {
        "format": "SIIG_MOBILE_EXCLUSIVES_REFERENCE",
        "evidence": "iOS 4.1.0 executable/resource-table reverse engineering; descriptive metadata only",
        "survival_chimera_policy": "Use the requested Chimera stage only when its Evolution Tree stage node status equals 1; otherwise substitute the listed fallback stage.",
        "survival_chimera_substitutions": substitutions,
        "survival_endings": endings,
        "v2_behavior_branches": [dict(x) for x in _V2_BEHAVIOR_BRANCHES],
        "v2_attack_pools": [
            {"boss": boss, "variant": variant, "type_id": type_id, "capacity": capacity, "discharge_handler": handler}
            for boss, variant, type_id, capacity, handler in _V2_ATTACK_POOLS
        ],
    }
