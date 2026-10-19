# Direct STFS and PS3 PKG input

`rip-game` accepts extracted directories, ZIP archives, Xbox 360 `CON `/`LIVE`/`PIRS` STFS packages, and PS3 type-1 PKGs. Detection uses file headers rather than filename extensions.

## One-click use

```bat
python siig_toolkit.py rip-game "C:\Games\SIIG_X360_STFS" -o "C:\Rips\SIIG_X360" --resume
python siig_toolkit.py rip-game "C:\Games\SIIG_PS3.pkg" -o "C:\Rips\SIIG_PS3" --resume
```

With `--resume`, package/ZIP staging is cached beside the output in a content-addressed hidden directory. The cache is reused only when the complete input SHA-256 matches. Use `--no-outer-cache` to force re-extraction. The cache is deliberately outside the rip tree so it is not indexed by the Asset Viewer or output manifest.

The desktop GUI exposes this as **Source-package cache**. It reports cache presence/size, remembers whether caching should remain enabled, and maps a disabled preference to `--no-outer-cache`. **Clear cache…** requires explicit confirmation and warns that the rip/Mod Workspaces are preserved but later resume may be slower because the original source package must be unpacked again.

## Xbox 360 STFS

The clean-room reader handles the volume descriptor, file table, hierarchy, consecutive/chained files, active hash-table copies, level-0/1/2 layouts, and `CON` transactional layout initialization. It extracts but does not authenticate/sign packages. SVOD is rejected rather than guessed.

The supplied original retail SIIG `LIVE` package was validated end to end: 94 outer files / 179,475,695 extracted bytes, 23 BBX archives, 2,593 resources, zero BBX hash mismatches, and zero archive failures.

## PlayStation 3 PKG and SDAT

The clean-room type-1 PKG reader supports finalized and debug/non-finalized streams. Finalized AES-CTR extraction may use an installed OpenSSL executable for acceleration; the locally written Python AES-CTR backend remains the fallback and is equivalence-tested. OpenSSL is not bundled.

SIIG's six `NPD\0` SDAT resources are decrypted internally with block authentication. On the supplied retail package, all six decrypt successfully with 18 authenticated HMAC-SHA1 blocks and zero fallbacks. Pre-decrypted `*.bin.gz.dat` files passed through `--ps3-sdat-dir` remain a compatibility fallback.

## Extraction safety

Outer members are treated as untrusted: traversal/absolute paths, ZIP symlinks/encryption, duplicate/case-colliding outputs, declared-size violations, and configured file/byte limits are rejected. Writes use `.siig-part` temporaries and atomic renames.

## Outer-container-only extraction

```bat
python siig_toolkit.py unpack-container "C:\Games\SIIG.pkg" -o "C:\Rips\SIIG_PKG_Files" --clean
```

This writes `SIIG_CONTAINER_MANIFEST.json`.

## Provenance

STFS, PKG, AES/debug-stream handling, SDAT handling, and safety wrappers are locally authored clean-room implementations. FIPS-197 is used as the AES algorithm/known-answer reference. OpenSSL is an optional external acceleration executable only. See `reference/provenance/` and `docs/project/THIRD_PARTY_NOTICES.md`.
