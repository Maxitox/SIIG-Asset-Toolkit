# Security notes

SIIG Asset Toolkit processes complex, potentially hostile binary containers. It is a research extractor, not a sandbox. Run it as an ordinary user, keep source packages read-only, and avoid processing untrusted files on a sensitive machine.

## Implemented protections

### Paths

- Absolute paths, drive-qualified paths, and `..` traversal are rejected or sanitized.
- ZIP symlinks are rejected.
- Windows reserved names are rewritten safely.
- Excessively deep paths are bounded.
- Duplicate and case-insensitive-colliding output paths are rejected or disambiguated where appropriate.

### Resource limits

Outer-container extraction uses configurable limits for:

- member count;
- total expanded bytes;
- one member's expanded size;
- ZIP expansion ratio.

Additional internal limits cover:

- offline asset-viewer text/model sampling, thumbnail dimensions, and payload-shard counts;
- glTF wireframe sample counts and referenced-buffer sizes;
- gzip expanded output;
- nested BBX recursion depth;
- total BBX resource entries;
- MAP atlas dimensions and embedded data size.

Defaults are chosen to accommodate SIIG's known data, not arbitrary game archives.

### Atomic output

Container members and generated metadata are written to `.siig-part` temporary files and renamed after completion. This reduces the chance that an interrupted write is mistaken for a valid file. `verify-output` reports leftover partial files.

### Format validation

Parsers check magic values, offsets, sizes, counts, arithmetic overflow/range conditions, declared-versus-available data, and unsupported variants before allocating or writing where practical.

### Privacy

Generated reports and manifests use archive-relative paths. Known absolute local paths are scrubbed from metadata. `verify-output` performs a privacy check over report/manifest content.

## Configuring limits

`rip-game` and `unpack-container` expose:

```text
--max-files
--max-total-bytes
--max-file-bytes
--max-zip-ratio
```

Example with stricter limits:

```bat
python siig_toolkit.py rip-game unknown.zip -o output ^
  --max-files 10000 ^
  --max-total-bytes 8589934592 ^
  --max-file-bytes 2147483648 ^
  --max-zip-ratio 200
```

Do not raise a limit merely because a suspicious package fails. Confirm the package's expected structure and expanded sizes first.

## Trust boundaries and limitations

- STFS signatures/content hashes are not authenticated as proof that a package is trusted.
- The tool does not verify publisher identity, console signatures, or package entitlement.
- The PS3 reader removes the outer PKG layer only; inner SELF/EDAT/SDAT cryptography is outside its scope.
- FFmpeg and other optional tools run as separate external processes and have their own security surface.
- Generated HTML is offline and dynamic strings are escaped. Linked thumbnails and preview payloads are still derived content and should be handled privately; keep the HTML beside its generated `viewer_assets` directory.
- `serve` binds to `127.0.0.1`; changing the code to bind externally creates a different security boundary.
- `repack-bbx` validates structure, paths, and payload equality, but cannot determine whether a semantic game-data modification is safe or accepted by the executable. It does not update STFS/PKG metadata or signatures.
- Python's memory usage can still be significant for very large legitimate assets despite extraction limits.
- No parser can guarantee safety against every malformed input. Use OS isolation for unknown files.

## Recommended workflow

1. Copy the package to a dedicated working directory.
2. Run `selftest` and `doctor`.
3. Use conservative limits for unknown containers.
4. Extract to a new empty output directory.
5. Review `RIP_REPORT.txt` and run `verify-output`.
6. Preserve the original package hash separately.
7. Do not run extracted executables or scripts.
8. Do not redistribute game-derived output.
9. For repacking, work from a copy and preserve the original archive hash.
10. Treat generated HTML viewers as private if they embed copyrighted previews.

## Reporting a security issue

Until a public project repository/contact is selected, document the smallest reproducible input description, command, Python version, platform, stack trace, and expected versus observed behavior. Do not attach copyrighted game packages publicly. A minimized synthetic reproducer is preferred.
