# PROGRESSIVE UFO runtime assembly — 2.10.0-dev3

## Result

The first executable-backed PROGRESSIVE UFO formation is now recovered as five runtime objects in this exact order:

| index | runtime | model | local translation | local rotation |
|---:|---|---|---|---|
| 0 | `0xA2` | `bos_009.gmx` | `(0, 0, 0)` | `(0, 0, 0)` |
| 1 | `0xC2` | `bos_009a.gmx` | `(-90, 0, -10)` | `(0, 0, 0)` |
| 2 | `0xC2` | `bos_009a.gmx` | `(90, 0, -10)` | `(0, 0, 0)` |
| 3 | `0xC3` | `bos_009b.gmx` | `(-160, 0, -50)` | `(0, 0, 0)` |
| 4 | `0xC3` | `bos_009b.gmx` | `(160, 0, -50)` | `(0, 0, 0)` |

Scale is identity. These values are not screenshot measurements or symmetry guesses.

## June 10 Xbox evidence

The June executable retains `ProgressiveUfo.cpp` debug/source strings, making the class boundary unusually strong.

- `ProgressiveUfo::SetScriptData` is anchored at `0x8214A280`.
- The adjacent five-word runtime type table at `0x82010F2C` is exactly `A2, C2, C2, C3, C3`.
- The creation loop at `0x8214A328` walks those five words, resolves the entity registry, creates each object and appends the object in table order.
- The class keeps five `0x60`-byte motion records, one per object.
- `0x8214C820` copies one five-record pose table from `0x825D9538` and schedules those targets over 60 frames. A conditional branch can exchange pose records 3 and 4; both are `C3` objects, so the assembled geometry set is unchanged.
- Startup initializer `0x82576808` fills the five 24-byte pose records as two `vec3`s each: translation followed by rotation. It writes the exact values listed above; every rotation component is zero.

The adjacent runtime pose tables used by later states are intentionally not promoted into the built-in static assembly preset. Dev3 represents the first recovered formation consumed by the boss state machine, not every later animation/phase pose.

## Retail Xbox cross-check

The stripped retail executable preserves the same implementation after address relocation/refactoring:

- type table: `0x8200A4EC`, again `A2, C2, C2, C3, C3`;
- creation-loop mnemonic fingerprint: `0x821327F0`, uniquely matching June `0x8214A328` and loading the retail table above;
- formation apply routine: `0x82134900`, uniquely matching June `0x8214C820`, including the five-record loop, optional record-3/4 swap and duration 60;
- formation table: `0x82568108`;
- formation initializer: `0x82549418`, uniquely matching the June initializer and resolving to the same `-90`, `90`, `-10`, `-160`, `160`, `-50` constants with zero rotations.

## Retail PS3 cross-check

The retained project-owner Ghidra export `SIIGPS3GHIDRA.zip` has SHA-256
`e7af0cd5940268c4697470ca58d55010b45a50706dfc10ead552d4ee4ce55d6d`, matching the input recorded by the earlier PS3 research report.

In that stripped EBOOT analysis, initializer `0x001C51E8` writes the same five translation/rotation pairs into `DAT_0054B598` onward. The first five translations decode exactly to `0`, `-90/-10`, `90/-10`, `-160/-50`, `160/-50`, with a zero-rotation vector after each translation. This independently corroborates the console formation on a second architecture/platform.

## glTF assembly convention

The toolkit's GMX exporter preserves native POSITION XYZ values and units when producing glTF; it does not permute axes. The assembly wrapper therefore uses the recovered game-local XYZ offsets directly. Standard glTF column-major matrices place translation in elements 12–14:

```text
[1,0,0,0, 0,1,0,0, 0,0,1,0, tx,ty,tz,1]
```

This is an outer instance transform. Each GMX retains its own internal BONE/MESH hierarchy and native-to-glTF matrix handling.

## Evidence boundary

- This result proves the first five-part runtime formation and its zero local rotations.
- It does not claim the game stores one merged native GMX; it instantiates five separate runtime model entities.
- Later Progressive UFO movement/state formations remain dynamic and should be represented separately if recovered.
- No executable bytes, decompiled proprietary code, GMX assets or screenshots are bundled in the source-only release. Only derived addresses, constants, fingerprints and matrices are retained.
