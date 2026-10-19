# SQUID runtime assembly — 2.10.0-dev17

## Result

SQUID is a two-phase locator-driven multipart entity rather than a single static mesh. The modeled runtime pool contains one animated body and eight identical static leg GMXs:

- Runtime record 0: `0xA9`, `bos_016.gmx`, animated body/root.
- Runtime records 1–8: `0xDA`, eight `bos_016a.gmx` legs.
- Runtime records 9–13: non-GMX helper/control objects; deliberately excluded from model assembly.
- Phase-1 attachment locators: `lt_000` through `lt_007`, in strict record order.

`bos_016.gmx` independently contains exactly those eight locator bones and eight native animation clips. `bos_016a.gmx` is a static two-mesh leg. The toolkit therefore parents each leg under its exact body locator using `attach_to` and leaves the leg-local matrix as identity. The preserved body animation drives the leg hierarchy without baking approximate world transforms.

## Runtime evidence

Retail `Function_82127B38` allocates fourteen SQUID records, but only records 0–8 are model records. The retail per-frame update uses records 1–8 with the pointer table at `0x8200A5D4..0x8200A5F0`; the eight entries resolve exactly to `lt_000..lt_007`.

The legless phase is also executable-proven. Retail state 8 enters through `Function_8212AE30`, which loops records 1–8 and invokes virtual `+0x54`. That call resolves to `Function_820FC270`, disabling the corresponding part/model. Record 0 is left active. June 10 independently performs the same eight-record disable loop in `Function_82145E68`.

## Catalogs

- `squid_phase1_legs` — one animated body plus eight locator-attached legs.
- `squid_phase2_body` — animated body only, representing state 8 and later after the eight leg records are disabled.

These are modeled-state snapshots, not an attempt to serialize non-GMX helper/control objects into glTF.

## Fresh retail validation

The retained retail Xbox package was freshly unpacked with dev17 before validation.

- `bos_016.gmx`: 44,544 bytes; SHA-256 `5e51d90192593d2d87cb81471532e32f2f78b63b490d91a117875ef913591b30`.
- `bos_016a.gmx`: 7,024 bytes; SHA-256 `e345016de566897e275aff9fed3d62b9aecdddaab35aacd47ac308ae6381ddea`.

Phase 1 export: 9 GMX instances, 18 meshes, 44 nodes, 8 preserved animations. Bounds are X/Y `-19.1398129463..19.1398129463`, Z `-19.5..88.875`.

Phase 2 export: 1 GMX instance, 2 meshes, 12 nodes, 8 preserved animations. Bounds are X/Y `-11.0865747929..11.0865747929`, Z `-19.5..20.25`.

The phase-1 glTF contains `body:lt_000` through `body:lt_007`, and its eight preserved animations are the body locator tracks `motion_000_lt_000` through `motion_007_lt_007`.

## Distribution boundary

No proprietary GMX files or generated retail glTFs are bundled in the source-only toolkit release.
