# Route/DAT filename pairing boundary — dev24 WIP164

## Result

The normal-stage filename part of the former route↔DAT boundary is now deterministic. For the recovered stage3d resource namespaces:

```text
XmapW_S.bin  -> levelW_stageS.dat
map4_S.bin   -> level4_stageS.dat
map5_S.bin   -> level5_stageS.dat
```

where `W` is 1..5 and `S` is 1..6. The corresponding runtime stage number is `(W - 1) * 6 + S`. The toolkit cross-checks that number and DAT name against `reference/tables/STAGE_PAIRING.csv`, whose first 30 runtime-stage rows come from the executable-backed stage/script registry. This is a filename/resource correspondence only; it is not a claim about the gameplay frame at which a route object is created.

`route-playback` and `route-camera-playback` therefore accept the historical explicit DAT argument unchanged, but may now omit it (or pass `auto`) for those deterministic normal-stage names. The resolver searches the nearby extracted layout, including an ancestor `script/` directory, and fails closed if the inferred DAT is absent.

## Boss/special boundary

`Bmap` resources are intentionally excluded from automatic one-DAT ownership. Two special transitions are stronger than an arbitrary guess but still do not prove a unique owning DAT:

- `WARNING [12]` directly drives the recovered reload chain to `Bmap13.bin` + `fld014.gmx` (descriptor 1).
- `WARNING [14]` directly drives the recovered reload chain to `Bmap15.bin` + `fld015.gmx` (descriptor 0).

Those chains prove which special route/field resources are requested by those transition values. They do **not** by themselves identify one canonical DAT file that owns the route object, nor the exact authored frame at which the object is instantiated. Other `Bmap` ownership is likewise not inferred.

## Explicit Bmap DAT request cross-check (WIP164)

When `route-playback` / `route-camera-playback` is given an **explicit** DAT for `Bmap13.bin` or `Bmap15.bin`, the report now emits a `special_reload_validation` block instead of treating that pairing as opaque. It scans authored `WARNING` (`0x78`) records and cross-checks the direct reload evidence:

- `Bmap13.bin` expects `WARNING [12]`, which requests `fld014.gmx` descriptor 1.
- `Bmap15.bin` expects `WARNING [14]`, which requests `fld015.gmx` descriptor 0.

The report records every matching authored WARNING frame, any competing special WARNING requests present in the same DAT, and the recovered reload-chain normalized transition frame (`130`). This is a compatibility check for the caller-supplied DAT; it does **not** turn Bmap resources into automatic one-DAT mappings.

Most importantly, an authored WARNING request frame is not relabeled as a route-object creation frame. The report therefore keeps `unique_dat_owner_inferred=false` and `route_initialization_frame_inferred=false`; `--start-frame` remains an explicit caller choice.

## Remaining boundary

`--start-frame` remains explicit for every route playback because exact route-object creation/activation timing is state-dependent and has not been recovered globally. Closing the remaining `ROUTE_DAT_PAIRING_AND_ACTIVATION` item therefore requires evidence for a canonical/scene-level Bmap owner plus the exact route-object initialization timing. Explicit DAT compatibility with the known WARNING request chain is now checked; it is no longer part of the unknown.
