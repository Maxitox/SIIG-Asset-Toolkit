# SIIG Asset Toolkit 2.8.0-dev23

Dev23 adds the first project-level modding workflow above the native builders introduced in dev21/dev22, and upgrades GMX/localization round-trip evidence from synthetic fixtures to real retail Xbox corpus validation.

## Mod workspace

New commands:

- `mod-init` — index a clean `rip-game` output and record immutable BBX baselines.
- `mod-list` — list archive keys and native resource paths without manual filesystem guessing.
- `mod-export` — export one supported BBX resource to its proven editable representation and track the edit baseline.
- `mod-export-archive` — export whole `text.bin` / `message.bin` localization archives for editing.
- `mod-stage` / `mod-stage-archive` — accept already-native resource or whole-BBX replacements.
- `mod-build` — rebuild changed editable files, overlay native replacements, rebuild only affected BBX archives, and emit a machine-readable build report.
- `mod-verify` — verify source baselines, built BBX hashes/parseability, and gzip patch payload identity.

Xbox `.gz` BBX resources can now be emitted as deterministic game-relative gzip patch files. Raw BBX files are emitted directly. PS3 NPDRM/SDAT re-encryption remains explicitly unsupported; those builds retain the verified decompressed BBX output.

## Retail corpus round-trip gate

Using the user-supplied retail Xbox files as external test inputs only:

- all **13/13** GMX resources from `player.bin` survived `gmx-edit-export` -> unchanged `gmx-build` byte-identically;
- retail `text.bin` rebuilt byte-identically from the readable 542-string export;
- retail `message.bin` rebuilt byte-identically from six readable scripts covering 284 groups / 1295 strings per language.

Only derived hashes/counts are included in the release. Proprietary inputs and rebuilt test assets are not bundled. Byte identity proves lossless no-op reconstruction on these samples; arbitrary modified-asset runtime acceptance remains a separate test boundary.

## Validation

- Dependency-free self-test suite: **68/68**.
- New mod-workspace regression exercises editable DAT -> native DAT -> rebuilt BBX -> deterministic gzip patch -> verification.
- Existing dev22 11/14 native-build asset-family coverage remains unchanged; dev23 integrates those builders into one project workflow rather than claiming three new format compilers.
