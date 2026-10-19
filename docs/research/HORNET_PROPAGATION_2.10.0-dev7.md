# HORNET state-6 propagation family — 2.10.0-dev7

## Result

HORNET's state-6 attack is now recovered as a deterministic **13-seed propagation family** over the same 45-record 5×9 grid used by the preceding prism wall. It is not another static wall.

The seed is **not randomized again**. State 6 inherits the exact A1 cell chosen by state 4 from the already recovered 13-entry table:

`0, 2, 6, 8, 18, 20, 22, 24, 26, 36, 38, 42, 44`.

Immediately before propagation, state 5 clears the relevant selection/display flags across all 45 records and hides A1. Therefore damage or transient state from the preceding wall does not prune the propagation graph: each of the 13 seeds produces one deterministic expansion sequence.

State 6 starts with the inherited seed only, then alternates:

1. **orthogonal** neighbors (left/right/up/down),
2. **diagonal** neighbors,
3. orthogonal,
4. diagonal,
5. and so on until all 45 cells are reached.

Each candidate must be inside the 9×5 grid, must not already be selected, and must not carry the unavailable/selected guard byte. State 5 zeroes that guard before state 6 begins, so the resulting family is deterministic.

The visible runtime object in these activation snapshots is **C0 / `bos_008b.gmx` only**. State 5 hides A1, state 6 does not restore it, and reached records re-enable their existing C0 model assignment. Unreached records remain hidden.

## Snapshot convention

The toolkit represents each wave at the **activation instant** immediately after the new reached set is enabled:

- reached C0 prisms are visible;
- A1 is hidden;
- C0 grid transforms use the inherited exact 5×9 positions;
- extra runtime Y rotation is zero at activation;
- laser/beam/effect objects are intentionally omitted.

After activation the runtime briefly rotates the selected set toward **π/4 (45°)** over about five updates, holds/fires the four-way beam pattern, then advances to the next expansion. The catalog snapshots deliberately do not freeze an arbitrary intermediate rotation.

Catalog keys are procedural rather than pre-enumerated:

```text
hornet_propagation_SS_wave_WW
```

`SS` must be one of the 13 runtime-valid seeds. `WW` must be within that seed's actual wave range; requesting a wave after complete 45-cell coverage is a hard error. There is deliberately no unqualified `hornet_propagation` default.

## Exact wave counts

| seed | visible C0 count by activation wave | final wave |
|---:|---|---:|
| 0 | 1 → 3 → 6 → 11 → 20 → 26 → 32 → 37 → 43 → 45 | 9 |
| 2 | 1 → 4 → 10 → 18 → 29 → 36 → 42 → 45 | 7 |
| 6 | 1 → 4 → 10 → 18 → 29 → 36 → 42 → 45 | 7 |
| 8 | 1 → 3 → 6 → 11 → 20 → 26 → 32 → 37 → 43 → 45 | 9 |
| 18 | 1 → 4 → 10 → 17 → 23 → 28 → 32 → 37 → 43 → 45 | 9 |
| 20 | 1 → 5 → 17 → 27 → 33 → 38 → 42 → 45 | 7 |
| 22 | 1 → 5 → 17 → 29 → 41 → 45 | 5 |
| 24 | 1 → 5 → 17 → 27 → 33 → 38 → 42 → 45 | 7 |
| 26 | 1 → 4 → 10 → 17 → 23 → 28 → 32 → 37 → 43 → 45 | 9 |
| 36 | 1 → 3 → 6 → 11 → 20 → 26 → 32 → 37 → 43 → 45 | 9 |
| 38 | 1 → 4 → 10 → 18 → 29 → 36 → 42 → 45 | 7 |
| 42 | 1 → 4 → 10 → 18 → 29 → 36 → 42 → 45 | 7 |
| 44 | 1 → 3 → 6 → 11 → 20 → 26 → 32 → 37 → 43 → 45 | 9 |

## Grid geometry

The state inherits the exact dev6 5×9 prism grid:

- `X = (index mod 9) * 46 + 29.5`
- `Y = 0`
- `Z = (index div 9) * 46 + 28`
- indices `0..44`.

No visual approximation, recentering, or unit conversion is used.

## June 10 Xbox evidence

Retained June Ghidra export SHA-256: `987cf607e4164dde06b980718a6169791d81e064d4b5e46ecb35f45176076f66`.

Key anchors:

- `0x82136468` — state-5 reset. Clears the 45-record selection/display flags before propagation and hides the A1 boss object.
- `0x821378A0` — state-6 grid-neighbor helper. Enforces 9×5 bounds, duplicate rejection and the per-record guard.
- `0x82137DE0` — state-6 controller. Inserts the inherited seed when the selected vector is empty; then alternates orthogonal and diagonal expansions, activates reached C0 records, drives the 0→π/4 turn and beam timing, and completes after all 45 records are selected.
- `0x82138568` — high-level HORNET state dispatcher.

The inherited seed field is the same state-4 selected A1 slot recovered in dev6; no second random selection occurs.

## Retail Xbox cross-check

Retained retail Ghidra export SHA-256: `444ea2b9cf85f201cd160f935ea890bc473b6d541cb9d8cecb849ae462c53499`.

The stripped retail equivalents reproduce the same logic:

- state-5 reset: `0x8211C4B8`;
- neighborhood helper: `0x8211D8C0`;
- state-6 controller: `0x8211DCC0`.

The same inherited 13-way seed family, 45-record reset, orthogonal/diagonal alternation, A1-hidden behavior and C0 activation semantics are present.

## Retail PS3 cross-check

Retained PS3 Ghidra export SHA-256: `e7af0cd5940268c4697470ca58d55010b45a50706dfc10ead552d4ee4ce55d6d`.

The retail PS3 EBOOT mirrors the algorithm at:

- state-5 reset: `_opd_FUN_001b1e6c`;
- neighborhood helper: `_opd_FUN_001b1318`;
- state-6 controller: `_opd_FUN_001b1458`.

This independently corroborates that the propagation attack is not a June-only prototype artifact.

## Representative real-retail export

Outside the source-only package, `hornet_propagation_22_wave_03` was exported using the retained retail `bos_008b.gmx`:

- **29** visible C0 GMX instances;
- **58** meshes;
- **116** nodes;
- **0** glTF animations in the activation snapshot;
- **29** unique assembly roots;
- bounds approximately `(75.5, 0, 28)` through `(351.5, 0, 212)`;
- C0 retail source SHA-256 `e4be18e2da142cc65504456c16d5464cb9064636a621c78d57878f144b8b47e5`.

Proprietary validation inputs and generated real-asset output are not bundled.

## Evidence boundary

This reconstruction represents the **activation instant** of each propagation wave. It does not attempt to bake transient beam effects or choose an arbitrary frame from the subsequent 0→45° prism turn. Those temporal effects remain runtime behavior rather than static assembly geometry.
