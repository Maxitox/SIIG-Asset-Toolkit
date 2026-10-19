# Testing and validation

This release includes a dependency-free regression suite and reproducible end-to-end checks. Validation is intended to catch parser regressions, unsafe extraction behavior, stale resume output, and accidental privacy leaks; it is not a substitute for testing every possible third-party package variant.

## Built-in self-test

```bat
python siig_toolkit.py selftest
```

The current 22-test suite covers:

1. AES-128 encrypt/decrypt known-answer vectors.
2. PKG AES-CTR chunk equivalence and round-trip behavior.
3. STFS `CON` transactional-layout initialization.
4. Authenticated NPDRM SDAT decrypt and tamper rejection.
5. Sony PS-ADPCM frame decoding.
6. DAT and MAP parsing.
7. BBX extraction/hash and canonical repacking.
8. ANM, wall/generator, Bmap/Xmap, and Xenos shader structures.
9. Bounded gzip, PNG/atlas rendering, and ZIP traversal safety.
10. Content-addressed outer-package resume caching and invalidation.
11. Privacy scrubbing.
12. Linked-data Asset Viewer generation.
13. Organized release-layout checks.
14. Output-manifest generation and tamper detection.

A successful run exits with code 0 and reports all tests as passed.

## Environment/input diagnostics

```bat
python siig_toolkit.py doctor
python siig_toolkit.py doctor "C:\path\to\input"
```

`doctor` checks:

- supported Python version;
- required standard-library cryptographic primitives and bundled modules;
- bundled CSV/JSON lookup files;
- optional FFmpeg availability;
- recognizable package/game input indicators when a path is supplied.

Warnings may describe optional functionality, such as missing FFmpeg. Errors indicate that the requested workflow is not ready.

## Verify a full rip

```bat
python siig_toolkit.py verify-output "C:\path\to\SIIG_Ripped"
```

Full mode checks every manifest SHA-256. Quick mode checks structure, sizes, privacy, and partial files without hashing:

```bat
python siig_toolkit.py verify-output "C:\path\to\SIIG_Ripped" --quick
```

A machine-readable report may be written with:

```bat
python siig_toolkit.py verify-output "C:\path\to\SIIG_Ripped" ^
  --json-output verification_result.json
```

## 2.3.0 release validation

The release candidate is tested with:

- Python bytecode compilation for all bundled Python modules and Blender add-on source;
- the complete 11-case built-in self-test;
- byte-identical extraction/repacking of the supplied retail `map.bin`;
- deterministic gzip repack verification;
- canonical repack verification of larger supplied BBX archives;
- offline asset-viewer generation on real extracted output;
- JavaScript syntax validation of generated Stage Explorer and Asset Viewer files;
- an end-to-end SIIG subset containing the original `default.xex`, `map.bin`, `script.bin`, and `texture_map.bin` resources;
- automatic BBX extraction, DAT/MAP conversion, both HTML viewers, manifest generation, and output verification;
- deterministic release ZIP reconstruction and source-only content scanning.

Blender itself was unavailable in the build environment. Add-on syntax, packaging, toolkit discovery logic, and exporter calls are validated outside Blender; final operator/UI behavior remains an explicit in-Blender test item.

The end-to-end subset produced:

```text
3 BBX archives processed
146 resources extracted
76 DAT files decoded
64 MAP files decoded
92 Stage Explorer entries
17,335 stage DAT commands
573,984 stage MAP cells
4 MAP atlases embedded
423 output files hashed and verified
0 verification errors
```

These counts are test evidence, not promised output for every platform/input combination.

## Container-reader coverage

The STFS/PKG implementations have synthetic tests for consecutive/chained STFS files, level-0/1/2 boundaries, finalized/debug PKG streams, AES, malformed metadata, extraction limits, and unsafe paths. Supplied extracted retail releases were also processed end to end.

The supplied original retail Xbox 360 LIVE STFS and PS3 type-1 PKG have now been exercised directly. Current retail regressions reach 2,593 BBX resources with zero archive failures/hash mismatches on both platforms; Xbox audio decodes 86/86 XACT streams, while PS3 internally authenticates all six SDATs (18 blocks) and decodes 84/84 Sony bank streams.

## Adding a regression case

A new parser or security fix should include a minimal deterministic synthetic case in `selftest` when feasible. Tests must not include copyrighted game assets, machine-specific absolute paths, secrets, or nondeterministic timestamps.

For corpus-only findings that cannot be reduced to a synthetic fixture, record:

- input class and build;
- relevant counts/hashes without redistributing content;
- expected behavior;
- observed failure before the fix;
- observed success after the fix;
- any unresolved ambiguity.

## 2.4.0 regression additions

The built-in suite now includes synthetic tests for:

- corrected ANM grouping, start/end frames, and loop flags;
- wall repeat counts, the runtime clamp to 16, and generator enable flags;
- 0x118-byte stage path cells, 800-unit centers, placements, and sentinels;
- Xenos shader stage bits, bounded microcode ranges, and metadata strings.

Real-corpus results are in `validation/RESEARCH_VALIDATION_2.4.json`.

## 2.5.0 Asset Viewer validation

The real-corpus viewer regression uses the 1,759-file structured research rip. It checks:

- all 1,016 previewable assets receive a thumbnail;
- the main HTML remains below 64 KiB;
- no base64 media is embedded;
- all original-file, thumbnail, preview, and payload URLs resolve;
- every payload key exists in one of at most 32 shards;
- all generated JavaScript files pass Node.js syntax checking;
- rebuilding inside the indexed tree does not recursively include the prior viewer output.

See `validation/ASSET_VIEWER_VALIDATION_2.5.json`. Interactive testing in a normal desktop browser remains recommended because headless browser automation was unavailable in the release environment.

## Dev4 route-runtime coverage

The built-in suite now includes 28 checks. Dev4 adds explicit coverage for signed SCROLL_02 spacing conversion, non-loop route termination, modulo loop wrapping, linear mid-segment spacing rebuilds, Hermite non-rebuild behavior, and authored-DAT-frame to runtime-update coupling.

The targeted real-corpus gate additionally smoke-steps all 46 resampleable retail stage3d routes in non-loop and loop modes; the route-empty `Xmap4_1.bin` is skipped.
