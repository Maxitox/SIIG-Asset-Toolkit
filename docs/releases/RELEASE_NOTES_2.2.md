# SIIG Asset Toolkit 2.2.0 release notes

Version 2.2.0 consolidates the MAP research into the main toolkit and strengthens the complete extraction pipeline.

## MAP and stage visualization

The runtime tile-set mapping is resolved for resource IDs 6–9. `stageviz` now embeds the matching `fence` atlases, renders actual tile imagery with confirmed X/Y reflections, creates a zero-scroll composite, and exposes clicked-cell metadata. `map2png` can use a supplied verified atlas for the same rendering path.

The release does not claim that the three layer roles or their frame-by-frame scroll trajectories are solved. Those remain clearly labeled limitations.

## Reliability and safety

The package-input path now has configurable file-count/byte/ratio limits, path and collision checks, symlink rejection, bounded gzip output, BBX recursion/resource budgets, and atomic writes. Resume profiles include toolkit version.

## Reproducibility

Every normal full rip now writes deterministic output manifests unless disabled. `verify-output` checks structure, privacy, sizes, hashes, and interrupted partial files. `doctor` provides preflight diagnostics; `selftest` exercises parsers, rendering, extraction safety, privacy, and tamper detection.

## Compatibility

The command-line interface remains compatible with earlier workflows. New behavior is automatic Stage Explorer and manifest generation; use `--no-stageviz` or `--no-output-manifest` to opt out.

## Known limitations

- Exact original retail SIIG STFS/PKG outer-container validation remains unavailable.
- PS3 inner SDAT decryption remains an external user step.
- MAP composites are zero-scroll visualizations, not complete gameplay playback.
- Full 3D stage reconstruction remains separate work.
- The project owner has not yet selected a license for original toolkit code.
