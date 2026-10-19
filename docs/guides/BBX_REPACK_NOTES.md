# BBX repacker notes

## Status

`repack-bbx` is a verified **research/modding** feature. On the supplied retail Xbox 360 `map.bin`, extract → repack produced a byte-for-byte identical archive. Synthetic named, unnamed, seeded-hash, sorted-index, alignment, and deterministic-gzip cases are included in `selftest`.

A byte-identical unchanged round trip proves the serializer matches that archive's layout. It does **not** prove that every modified archive will be accepted by every game build. Keep originals read-only and test modifications on copies.

## Canonical layout

```text
+0x00  char[4]  01 42 42 58
+0x04  be u32   entry count
+0x08  be u32   mode
+0x0C  be u32   filename-hash seed
+0x10  byte[16] preserved reserved header bytes
+0x20  entry table, count × 0x10
        be u32 payload offset
        be u32 payload size
        be u32 NUL-terminated name offset, or zero
        be u32 identifier/hash
        optional sorted {identifier,index} table for modes 0 and 1
        NUL-terminated names
        16-byte-aligned payloads
```

The repacker recomputes identifiers for named entries by default. Unnamed entries retain the manifest identifier because no filename exists to hash. `--preserve-identifiers` retains all manifest identifiers, including intentional mismatches.

## Basic workflow

```bat
python siig_toolkit.py extract map.bin -o work
python siig_toolkit.py repack-bbx work\map -o map_modified.bin
```

Edit only files referenced by `manifest.json`. The manifest preserves entry order, internal names, mode, seed, reserved header bytes, payload hashes, and original archive hash.

Useful options:

```text
--include-extra          append unlisted files using their relative paths as names
--preserve-identifiers  retain named identifiers instead of recomputing hashes
--mode / --hash-seed    explicit format overrides
--gzip                   deterministic gzip wrapper with timestamp zero
```

Every output is parsed again and compared with the requested names and payloads. A `.repack.json` report records hashes, sizes, settings, and verification results.

## Safety boundaries

- The source extraction directory is never modified.
- Manifest paths must remain inside the extraction directory.
- Missing files, duplicate/case-colliding paths, malformed identifiers, and NUL-containing names are rejected.
- Output is written atomically.
- Repacking cannot update executable tables, signatures, package metadata, or checksums outside the BBX file.
