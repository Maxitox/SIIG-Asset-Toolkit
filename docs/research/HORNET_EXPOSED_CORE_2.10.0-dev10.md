# HORNET exposed-core state — 2.10.0-dev10

## Result

HORNET has a real executable-backed **A1-only exposed-core state**. It is not a presentation-only convenience preset.

The toolkit catalog key is:

`hornet_exposed_core`

The preset is the deterministic **high-level state-3 entry snapshot**:

- 1 × `bos_008.gmx` / runtime `0xA1`;
- native motion 0 at sample 0;
- identity outer transform in boss-local coordinates;
- no visible BF armor instances;
- no visible C0 prism instances;
- C1 remains an invisible animation/formation rig and is not exported as geometry.

## Retail Xbox proof

Retail HORNET high-level dispatcher: `0x8211E3D0`.

Relevant flow:

- state 2: `0x8211BE88`;
- if it returns 1, dispatcher advances to **state 3**;
- state 3: `0x8211CF98`;
- every high-level state transition runs `0x8211D840`;
- `0x8211D840` calls common reset `0x8211D648`.

`0x8211D648` establishes the state-entry presentation before state 3 runs:

1. clears the A1 transparency flag at parent `+0x1CC`;
2. calls the per-record reset/disable path for all 125 records;
3. writes record state `-1` for all 125 records, so the normal BF/C0 model-selection branches are inactive;
4. re-enables the root/A1 part;
5. selects A1 native motion 0 via `0x8214C020(..., 0)`;
6. sets A1 to sample 0 via `0x8214BDA0(..., 0)`;
7. resets the meshless C1 rig to sample 0 separately.

The ordinary placement/update function `0x8211CAB8` only chooses visible BF for record states 0..2 and visible C0 for states 3..4. State `-1` therefore leaves those subordinate pools out of the visible state-3 entry assembly.

State 3 itself (`0x8211CF98`) performs the exposed-core attack behavior and does not rebuild a BF or C0 formation before firing its timed attacks.

## June 10 Xbox cross-check

June independently preserves the same architecture:

- dispatcher: `0x82138568`;
- state 3: `0x82136FD0`;
- transition reset: `0x82137820`;
- common pool/root reset: `0x82137628`;
- placement/update: `0x82136AA8`.

`0x82137628` repeats the same key operations: A1 transparency reset, 125 record states set to `-1`, root re-enable, A1 motion 0/sample 0, and C1 sample-0 reset.

## Retail PS3 cross-check

Retail PS3 reproduces the state graph independently:

- state 3: `_opd_FUN_001b25b8`;
- transition reset: `_opd_FUN_001b02f8`;
- common reset: `_opd_FUN_001affd8`;
- placement/update: `_opd_FUN_001afa08`.

`_opd_FUN_001affd8` likewise clears the A1 transparency byte, resets all 125 records to `-1`, re-enables the root, and resets A1/C1 animation state to sample 0.

## Re-uploaded real-retail asset validation

The project owner re-supplied the original retail Xbox package. `Media/3ddata/enemy.bin.gz` was extracted directly from the STFS package and yielded the original HORNET files.

Hashes exactly match the previously recorded dev5 corpus:

- `bos_008.gmx`: `0d73ffe9744fdd635c6480836734576f715b3037d2aa90737682912ab88cd516`
- `bos_008a.gmx`: `7d9d44813cd5327c91218e477e8be8e8d71915425d4067b01729078d37edfd55`
- `bos_008b.gmx`: `e4be18e2da142cc65504456c16d5464cb9064636a621c78d57878f144b8b47e5`
- `bos_008c.gmx`: `7e0601f6048a38ce49fe4a6ebc6319619ae99037ba3c0bf93ba643ac03041ad1`
- `enemy.anm`: `c3100a85d279af220e3f2b1f8b51650acf2e3c536ecac1f918d5174f88570cb4`

Native structure check:

- A1 / `bos_008.gmx`: 2 visible meshes, 3 bones, 2 animation tracks;
- BF / `bos_008a.gmx`: 2 meshes, no native animation tracks;
- C0 / `bos_008b.gmx`: 2 meshes, no native animation tracks;
- C1 / `bos_008c.gmx`: 0 meshes, 128 bones, 126 animation tracks.

A real `hornet_exposed_core` glTF export from the re-uploaded retail A1 produced:

- 1 GMX instance;
- 2 meshes;
- 4 glTF nodes;
- 0 retained glTF animations because sample 0 is deliberately baked for the static state-entry snapshot;
- local bounds approximately `(-13.8054,-13.8054,-13.8054)` to `(13.8054,13.8054,13.8054)`.

## Evidence boundary

This preset is the **state-3 entry snapshot**, not a claim that A1 remains frozen at sample 0 throughout the whole state. Runtime state 3 continues normal boss movement/attack logic after entry. The static assembly deliberately captures the deterministic state boundary rather than choosing an arbitrary later attack frame.

The full-armor, prism-wall and state-6 propagation assemblies remain separate presets/families and are not merged into this one.
